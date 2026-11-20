"""
Compares live Polymarket prices against DraftKings odds (and the trained
club model) for a Premier League fixture, then reports:

  1. best payout venue per outcome — where a winning bet on H/D/A returns
     the most per dollar
  2. model edge vs each venue's implied probability
  3. cross-venue 3-way arbitrage — whether buying the cheapest price on
     each of home/draw/away across venues locks in a risk-free profit,
     with exact stake splits

APIs used:
  - Polymarket Gamma (https://gamma-api.polymarket.com) — market discovery
    via public search; also provides fallback prices.
  - Polymarket CLOB (https://clob.polymarket.com) — live order book. The
    BEST ASK is used (what you would actually pay to buy YES right now),
    not the midpoint — arbitrage math on unfillable midpoints is fiction.
    The available size at that ask is reported too, since an arb you can
    only fill $12 of isn't an arb worth acting on.
  - DraftKings via The Odds API (https://the-odds-api.com) — DraftKings
    has no public API and its internal sportsbook endpoints are geo-fenced
    and break without notice, so the reliable route is The Odds API's free
    tier (500 requests/month). Put ODDS_API_KEY in .env.

Team names on the command line use football-data.co.uk short names (same
convention as the rest of this repo, e.g. "Man City"), mapped to full
names via FD_TO_FULL for matching against Polymarket/DraftKings.

Usage:
    py odds_compare.py "Liverpool" "Man City"
    py odds_compare.py "Liverpool" "Man City" --stake 100
    py odds_compare.py "Liverpool" "Man City" --bookmakers draftkings,fanduel
    py odds_compare.py "Liverpool" "Man City" --no-model
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"
ODDS_API_SPORT = "soccer_epl"
TIMEOUT = 20

# football-data.co.uk short name -> full name used by Polymarket / The Odds API
FD_TO_FULL = {
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest",
    "Tottenham": "Tottenham Hotspur",
    "West Ham": "West Ham United",
    "Wolves": "Wolverhampton Wanderers",
    "West Brom": "West Bromwich Albion",
    "Brighton": "Brighton and Hove Albion",
    "Leeds": "Leeds United",
    "Leicester": "Leicester City",
    "Luton": "Luton Town",
    "Ipswich": "Ipswich Town",
    "Sheffield United": "Sheffield United",
}

OUTCOMES = ("H", "D", "A")


def norm(name):
    """Normalize a team name for loose matching across venues."""
    s = re.sub(r"[^a-z0-9 ]", "", name.lower())
    s = re.sub(r"\b(fc|afc)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def teams_match(a, b):
    na, nb = norm(a), norm(b)
    return na == nb or na in nb or nb in na


# ---------------------------------------------------------------- Polymarket

def nickname(team_full):
    """
    The franchise name US titles are keyed on: 'Kansas City Chiefs' -> 'chiefs'.
    'Sox' alone is ambiguous (Red Sox / White Sox), so keep two words there.
    """
    words = norm(team_full).split()
    if len(words) >= 2 and words[-1] == "sox":
        return " ".join(words[-2:])
    return words[-1] if words else ""


def gamma_find_event(home_full, away_full, commence_time=None):
    """
    Find the active Polymarket event for this fixture via public search.
    Soccer events are titled with full team names; US sports (NFL/NBA, and
    older MLB) use nicknames ('Chiefs vs. Chargers'), so if the full-name
    query finds nothing, retry the search with nicknames.

    commence_time (kickoff, ISO UTC) anchors the DATE: teams that meet twice
    a season otherwise both match the sooner event, tagging the rematch with
    the wrong market. An event qualifies when it settles after kickoff but
    within ~9 days of it (PM game events end about a week after the game;
    season-series and futures markets end months later and are excluded).
    """
    lo, hi = None, None
    if commence_time:
        try:
            ko = datetime.fromisoformat(str(commence_time).replace("Z", "+00:00"))
            lo = ko.strftime("%Y-%m-%dT%H:%M:%SZ")
            hi = (ko + timedelta(days=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    queries = [f"{home_full} {away_full}",
               f"{nickname(home_full)} {nickname(away_full)}"]
    for q in queries:
        r = requests.get(f"{GAMMA_BASE}/public-search",
                         params={"q": q, "limit_per_type": 20},
                         timeout=TIMEOUT)
        r.raise_for_status()
        events = r.json().get("events") or []
        candidates = [ev for ev in events
                      if not ev.get("closed")
                      and teams_match_any(home_full, ev.get("title", ""))
                      and teams_match_any(away_full, ev.get("title", ""))
                      and (lo is None or lo <= (ev.get("endDate") or "") <= hi)]
        if candidates:
            # prefer the one ending soonest (the next meeting, not a distant
            # rematch; also outranks all-day novelty markets on the same teams)
            candidates.sort(key=lambda e: e.get("endDate") or "9999")
            return candidates[0]
    return None


def teams_match_any(team_full, text):
    """True if the title mentions this team by full name or by nickname."""
    if norm(team_full) in norm(text):
        return True
    nick = nickname(team_full)
    return bool(nick) and re.search(rf"\b{re.escape(nick)}\b", norm(text)) is not None


def parse_event_markets(event, home_full, away_full):
    """
    Map the event's markets to H/D/A. Two shapes exist:
      - soccer: three YES/NO markets grouped in one event (groupItemTitle =
        team name or "Draw"), one per outcome
      - US sports (NFL/NBA/MLB): ONE moneyline market whose two outcomes ARE
        the team names; the same event also carries spread/total/prop markets
        with team-name outcomes, which must be skipped (the moneyline is the
        one with no group label and no line in the question)
    Returns {outcome: {label, yes_token_id, gamma_price}}.
    """
    out = {}
    for m in event.get("markets", []):
        label = m.get("groupItemTitle") or m.get("question", "")
        outcomes = json.loads(m["outcomes"]) if isinstance(m.get("outcomes"), str) else m.get("outcomes", [])
        prices = json.loads(m["outcomePrices"]) if isinstance(m.get("outcomePrices"), str) else m.get("outcomePrices", [])
        tokens = json.loads(m["clobTokenIds"]) if isinstance(m.get("clobTokenIds"), str) else m.get("clobTokenIds", [])

        try:
            yes_idx = [o.lower() for o in outcomes].index("yes")
        except ValueError:
            yes_idx = None

        if yes_idx is not None:  # soccer-style binary market
            if "draw" in norm(label):
                key = "D"
            elif teams_match(home_full, label):
                key = "H"
            elif teams_match(away_full, label):
                key = "A"
            else:
                continue
            out[key] = {
                "label": label,
                "yes_token_id": tokens[yes_idx] if yes_idx < len(tokens) else None,
                "gamma_price": float(prices[yes_idx]) if yes_idx < len(prices) else None,
            }
            continue

        # US-style moneyline: both outcomes are the team names. Spread markets
        # share that shape, so require an unlabeled market (moneyline has no
        # groupItemTitle) whose question carries no handicap number.
        if len(outcomes) == 2 and not m.get("groupItemTitle") \
                and "spread" not in (m.get("question") or "").lower():
            for idx, o in enumerate(outcomes):
                if teams_match(home_full, o):
                    key = "H"
                elif teams_match(away_full, o):
                    key = "A"
                else:
                    continue
                out.setdefault(key, {
                    "label": o,
                    "yes_token_id": tokens[idx] if idx < len(tokens) else None,
                    "gamma_price": float(prices[idx]) if idx < len(prices) else None,
                })
    return out


def clob_best_ask(token_id):
    """Best ask (price you'd pay to buy YES now) and its available size."""
    try:
        r = requests.get(f"{CLOB_BASE}/book", params={"token_id": token_id}, timeout=TIMEOUT)
        r.raise_for_status()
        asks = [(float(a["price"]), float(a["size"]))
                for a in r.json().get("asks", []) if float(a.get("size", 0)) > 0]
        if asks:
            price, size = min(asks, key=lambda x: x[0])
            return price, size
    except requests.RequestException:
        pass
    try:  # fallback: midpoint (indicative only — flagged in output)
        r = requests.get(f"{CLOB_BASE}/midpoint", params={"token_id": token_id}, timeout=TIMEOUT)
        r.raise_for_status()
        return float(r.json()["mid"]), None
    except requests.RequestException:
        return None, None


def fetch_polymarket(home_full, away_full):
    """Returns {outcome: {price, size, source, label}} or None if not listed."""
    event = gamma_find_event(home_full, away_full)
    if event is None:
        return None, None
    markets = parse_event_markets(event, home_full, away_full)
    quotes = {}
    for key, m in markets.items():
        price, size = (None, None)
        if m["yes_token_id"]:
            price, size = clob_best_ask(m["yes_token_id"])
        source = "clob_ask" if price is not None and size is not None else \
                 ("clob_mid" if price is not None else "gamma")
        if price is None:
            price = m["gamma_price"]
        if price is not None:
            quotes[key] = {"price": price, "size": size, "source": source, "label": m["label"]}
    return quotes or None, event.get("title")


# --------------------------------------------------------------- DraftKings

def fetch_sportsbook_odds(home_full, away_full, bookmakers):
    """
    Decimal h2h odds via The Odds API. Returns
    {outcome: {book: decimal_odds}} for whichever requested books list it.
    """
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ODDS_API_KEY — get a free key at https://the-odds-api.com "
                         "and add it to .env")
    r = requests.get(f"{ODDS_API_BASE}/sports/{ODDS_API_SPORT}/odds",
                     params={"apiKey": api_key, "regions": "us,us2", "markets": "h2h",
                             "oddsFormat": "decimal", "bookmakers": ",".join(bookmakers)},
                     timeout=TIMEOUT)
    r.raise_for_status()
    remaining = r.headers.get("x-requests-remaining")
    for ev in r.json():
        if teams_match(home_full, ev["home_team"]) and teams_match(away_full, ev["away_team"]):
            odds = {k: {} for k in OUTCOMES}
            for bm in ev.get("bookmakers", []):
                for mkt in bm.get("markets", []):
                    if mkt["key"] != "h2h":
                        continue
                    for oc in mkt["outcomes"]:
                        if oc["name"].lower() == "draw":
                            key = "D"
                        elif teams_match(home_full, oc["name"]):
                            key = "H"
                        elif teams_match(away_full, oc["name"]):
                            key = "A"
                        else:
                            continue
                        odds[key][bm["key"]] = float(oc["price"])
            return odds, remaining
    return None, remaining


def devig(odds_by_outcome):
    """De-vig one book's decimal odds -> fair probabilities. Needs all 3 outcomes."""
    raw = {k: 1.0 / odds_by_outcome[k] for k in OUTCOMES}
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}, total


# --------------------------------------------------------------- comparison

def best_costs(pm_quotes, book_odds):
    """
    Cheapest cost per $1 of payout for each outcome across venues.
    Polymarket YES at price p costs $p per $1 payout; decimal odds o cost
    $1/o per $o... normalized: 1/o per $1 payout.
    """
    costs = {}
    for k in OUTCOMES:
        options = []
        if pm_quotes and k in pm_quotes:
            options.append(("Polymarket", pm_quotes[k]["price"]))
        if book_odds:
            for book, o in book_odds.get(k, {}).items():
                options.append((book, 1.0 / o))
        if options:
            costs[k] = min(options, key=lambda x: x[1])
    return costs


def find_arbitrage(costs, budget=100.0):
    """3-way arb check on the cheapest cross-venue costs."""
    if len(costs) < 3:
        return None
    total = sum(c for _, c in costs.values())
    if total >= 1.0:
        return {"total_cost": total, "profit": None}
    payout = budget / total
    stakes = {k: (venue, cost * payout) for k, (venue, cost) in costs.items()}
    return {"total_cost": total, "payout": payout, "stakes": stakes,
            "profit": payout - budget, "roi": payout / budget - 1.0}


def get_model_probs(fd_home, fd_away):
    try:
        from club_model import predict_match
        probs, _ = predict_match(fd_home, fd_away, league="premier_league")
        return probs
    except Exception as e:  # missing weights, unknown team, etc. — not fatal
        print(f"  (model probabilities unavailable: {e})")
        return None


if __name__ == "__main__":
    load_dotenv(override=True)  # .env should win over any stale/empty env var of the same name
    parser = argparse.ArgumentParser(description="Polymarket vs sportsbook odds comparison + arbitrage check.")
    parser.add_argument("home_team", help="football-data short name, e.g. 'Liverpool'")
    parser.add_argument("away_team", help="football-data short name, e.g. 'Man City'")
    parser.add_argument("--bookmakers", default="draftkings",
                        help="comma-separated Odds API bookmaker keys (default: draftkings)")
    parser.add_argument("--stake", type=float, default=100.0, help="arb budget to size stakes for")
    parser.add_argument("--no-model", dest="model", action="store_false",
                        help="skip the trained model's probabilities")
    args = parser.parse_args()

    fd_home, fd_away = args.home_team, args.away_team
    home_full = FD_TO_FULL.get(fd_home, fd_home)
    away_full = FD_TO_FULL.get(fd_away, fd_away)
    books = [b.strip() for b in args.bookmakers.split(",") if b.strip()]

    print(f"\n{home_full} (home) vs {away_full} (away)")

    pm_quotes, pm_title = fetch_polymarket(home_full, away_full)
    print(f"  Polymarket event: {pm_title or 'NOT FOUND — may not be listed yet'}")

    book_odds, remaining = fetch_sportsbook_odds(home_full, away_full, books)
    if book_odds is None:
        print(f"  Sportsbook: fixture not found on {books} (Odds API requests left: {remaining})")
    else:
        print(f"  Sportsbook odds fetched ({', '.join(books)}; Odds API requests left: {remaining})")

    model = get_model_probs(fd_home, fd_away) if args.model else None

    # de-vigged fair probs per book (only books quoting all three outcomes)
    fair = {}
    if book_odds:
        for book in books:
            per_book = {k: book_odds[k][book] for k in OUTCOMES if book in book_odds.get(k, {})}
            if len(per_book) == 3:
                fair[book], overround = devig(per_book)

    print(f"\n{'outcome':<22}{'model':>8}{'PM ask (payout)':>18}", end="")
    for book in books:
        print(f"{book + ' (fair prob)':>26}", end="")
    print()
    names = {"H": f"Home ({fd_home})", "D": "Draw", "A": f"Away ({fd_away})"}
    for k in OUTCOMES:
        line = f"{names[k]:<22}"
        line += f"{model[k]:>7.1%} " if model else f"{'—':>8}"
        if pm_quotes and k in pm_quotes:
            q = pm_quotes[k]
            note = "" if q["source"] == "clob_ask" else "*"
            line += f"{q['price']:>8.3f}{note} ({1/q['price']:>5.2f}x)"
        else:
            line += f"{'—':>18}"
        for book in books:
            o = book_odds.get(k, {}).get(book) if book_odds else None
            if o:
                fp = fair.get(book, {}).get(k)
                line += f"{o:>12.2f} ({fp:>5.1%})" if fp else f"{o:>12.2f}        "
            else:
                line += f"{'—':>26}"
        print(line)
    if pm_quotes and any(q["source"] != "clob_ask" for q in pm_quotes.values()):
        print("  * indicative price (midpoint/Gamma) — order book ask unavailable, don't trust for arb sizing")

    if model:
        print("\nModel edge (model prob - venue implied prob):")
        for k in OUTCOMES:
            parts = []
            if pm_quotes and k in pm_quotes:
                parts.append(f"vs Polymarket {model[k] - pm_quotes[k]['price']:+.1%}")
            for book, fp in fair.items():
                parts.append(f"vs {book} {model[k] - fp[k]:+.1%}")
            if parts:
                print(f"  {names[k]:<22}" + "   ".join(parts))

    costs = best_costs(pm_quotes, book_odds)
    arb = find_arbitrage(costs, budget=args.stake)
    print("\nCross-venue arbitrage check (cheapest price per outcome):")
    for k, (venue, cost) in costs.items():
        print(f"  {names[k]:<22}{venue:<14} ${cost:.3f} per $1 payout")
    if arb is None:
        print("  Incomplete quotes — need all three outcomes priced somewhere.")
    elif arb["profit"] is None:
        print(f"  Total cost of covering all outcomes: ${arb['total_cost']:.3f} per $1 payout — "
              f"no arb (needs < $1.000). "
              f"{'Close — worth re-checking near kickoff.' if arb['total_cost'] < 1.02 else ''}")
    else:
        print(f"  *** ARBITRAGE: total cost ${arb['total_cost']:.3f} per $1 payout ***")
        print(f"  For a ${args.stake:.2f} budget: guaranteed return ${arb['payout']:.2f} "
              f"(profit ${arb['profit']:.2f}, {arb['roi']:+.1%})")
        for k, (venue, stake) in arb["stakes"].items():
            print(f"    put ${stake:>7.2f} on {names[k]:<20} at {venue}")
        sizes = [pm_quotes[k]["size"] for k in OUTCOMES
                 if pm_quotes and k in pm_quotes and costs[k][0] == "Polymarket"]
        if any(s is not None for s in sizes):
            print(f"    (Polymarket ask depth caps fillable size: "
                  f"{', '.join(f'{s:.0f} shares' for s in sizes if s is not None)})")
        print("    Prices move — refetch immediately before placing both legs.")
