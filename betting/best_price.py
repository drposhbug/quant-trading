"""
Best-price execution — the largest measured effect in this repo
================================================================================
Every diagnostic here reached the same verdict: the models do not beat the
closing line (NBA 0/13 seasons, tennis 0/3 years, and in both the model's
disagreements with the market were error rather than information). So profit
cannot come from prediction with these inputs. It has to come from paying less.

That is what this module does, and unlike a model edge it was measured, not
assumed:

    tennis, 15,826 matches with three price levels quoted per match
        market average .................. 5.20% hold
        Pinnacle (sharp book) ........... 2.62% hold
        best price across books ........ -0.26% hold   <-- below zero

    soccer, from this repo's own price_snapshots
        best vs average, US-accessible books ... +3.88% on the payout
        best vs average, all 27 books .......... +8.27%

Shopping is worth more than the entire vig in every market checked. The tennis
best-of-book overround coming out BELOW 1.0 means that, on average, the best
available prices on the two sides added to less than a guaranteed payout.

WHY THAT IS NOT FREE MONEY, and why this module reports depth and venue counts
rather than just a number: the two best prices sit at different books and were
not necessarily quoted at the same instant, top-of-market limits are small, and
an account that only ever takes the best price gets restricted. Treat the
overround as the honest cost of execution, not as an arbitrage ticket.

The functions are market-shape agnostic — they take whatever outcome tuple they
are given, so the 2-way (NBA, tennis) and 3-way (soccer) markets share one
implementation.

Usage:
    py best_price.py                  # measure shopping value in the local DB
    py best_price.py --tennis         # historical tennis price levels
    py best_price.py --snapshots      # live book quotes from price_snapshots
"""

import argparse
from collections import defaultdict


def overround(prices):
    """
    Sum of implied probabilities. 1.0 = no vig; above = the house's cut;
    below = the set of prices pays more than certainty.
    """
    prices = [p for p in prices if p and p > 1.0]
    if not prices:
        return None
    return sum(1.0 / p for p in prices)


def hold(prices):
    """Overround expressed as a share of stake -- the number that is 'the vig'."""
    o = overround(prices)
    if o is None or o <= 0:
        return None
    return (o - 1.0) / o


def best_quote(quotes_by_venue, outcome):
    """
    quotes_by_venue: {venue: {outcome: decimal_odds}}.
    -> (venue, odds) offering the most for `outcome`, or (None, None).
    """
    best_v, best_o = None, None
    for venue, odds in quotes_by_venue.items():
        o = odds.get(outcome)
        if o and o > 1.0 and (best_o is None or o > best_o):
            best_v, best_o = venue, o
    return best_v, best_o


def best_line(quotes_by_venue, outcomes, allowed_venues=None):
    """
    The synthetic best-of-book line: for each outcome, the venue paying most.

    allowed_venues restricts to books you can actually bet -- the headline
    shopping number is meaningless if half the winning quotes come from books
    that will not take your action.

    -> {outcome: {'venue', 'odds'}}, missing outcomes omitted.
    """
    if allowed_venues is not None:
        quotes_by_venue = {v: o for v, o in quotes_by_venue.items()
                           if v in allowed_venues}
    out = {}
    for outcome in outcomes:
        venue, odds = best_quote(quotes_by_venue, outcome)
        if venue is not None:
            out[outcome] = {"venue": venue, "odds": odds}
    return out


def shopping_gain(quotes_by_venue, outcomes, allowed_venues=None):
    """
    What shopping is worth on this market, versus taking an average book.

    Returns a dict with the best-of-book and average-book overrounds, the hold
    at each, and the gain in hold -- the per-bet saving, which is the number
    that actually compounds. Returns None when the market is not fully quoted
    by at least two venues (nothing to shop between).
    """
    if allowed_venues is not None:
        quotes_by_venue = {v: o for v, o in quotes_by_venue.items()
                           if v in allowed_venues}
    complete = {v: o for v, o in quotes_by_venue.items()
                if all(o.get(k) and o[k] > 1.0 for k in outcomes)}
    if len(complete) < 2:
        return None

    best = best_line(complete, outcomes)
    if len(best) != len(outcomes):
        return None
    best_prices = [best[k]["odds"] for k in outcomes]

    # the average book: mean decimal price per outcome across books quoting it
    avg_prices = []
    for k in outcomes:
        vals = [o[k] for o in complete.values()]
        avg_prices.append(sum(vals) / len(vals))

    h_best, h_avg = hold(best_prices), hold(avg_prices)
    if h_best is None or h_avg is None:
        return None
    return {
        "n_venues": len(complete),
        "best": best,
        "best_overround": overround(best_prices),
        "avg_overround": overround(avg_prices),
        "best_hold": h_best,
        "avg_hold": h_avg,
        "gain": h_avg - h_best,          # hold saved per bet by shopping
        "venues_used": sorted({b["venue"] for b in best.values()}),
    }


def payout_gain(quotes_by_venue, outcome, allowed_venues=None):
    """
    Best price vs the average price for ONE side -- the number to quote when you
    are betting a single outcome rather than making a two-way market.
    -> (venue, best_odds, avg_odds, fractional gain on the payout) or None.
    """
    if allowed_venues is not None:
        quotes_by_venue = {v: o for v, o in quotes_by_venue.items()
                           if v in allowed_venues}
    vals = [o[outcome] for o in quotes_by_venue.values()
            if o.get(outcome) and o[outcome] > 1.0]
    if len(vals) < 2:
        return None
    venue, best = best_quote(quotes_by_venue, outcome)
    avg = sum(vals) / len(vals)
    return venue, best, avg, (best / avg - 1.0)


# --------------------------------------------------------------------------
# reporting against the local DB
# --------------------------------------------------------------------------

# Books a US-based account can realistically use. The all-books number is
# inflated by exotics that will not take the action, so both are reported.
US_ACCESSIBLE = {"draftkings", "fanduel", "betmgm", "betrivers", "betonlineag",
                 "lowvig", "bovada", "espnbet", "hardrockbet", "betparx",
                 "fliff", "betus", "mybookieag", "pinnacle", "betanysports"}


def report_tennis():
    """Historical tennis, which ships with all three price levels per match."""
    from db import fetch_tennis_matches
    rows = fetch_tennis_matches()
    if not rows:
        print("No tennis matches -- run ingest_tennis.py first.")
        return
    levels = [("market average", "p1_avg", "p2_avg"),
              ("Pinnacle (sharp)", "p1_ps", "p2_ps"),
              ("best across books", "p1_max", "p2_max")]
    print(f"=== Tennis price levels ({len(rows)} matches) ===")
    print(f"{'level':>22} {'overround':>10} {'hold':>9} {'n':>7}")
    holds = {}
    for label, c1, c2 in levels:
        vals = [(r[c1], r[c2]) for r in rows
                if r.get(c1) and r.get(c2) and r[c1] > 1 and r[c2] > 1]
        if not vals:
            continue
        o = sum(overround(v) for v in vals) / len(vals)
        h = (o - 1.0) / o
        holds[label] = h
        print(f"{label:>22} {o:>10.4f} {h:>+9.2%} {len(vals):>7}")
    if "best across books" in holds and "Pinnacle (sharp)" in holds:
        print(f"\nShopping vs the sharp line: "
              f"{holds['Pinnacle (sharp)'] - holds['best across books']:+.2%} per bet")
        print(f"Shopping vs an average book: "
              f"{holds['market average'] - holds['best across books']:+.2%} per bet")


def report_snapshots():
    """Live book quotes this repo has logged, by league."""
    import sqlite3
    from db import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT snapshot_time, league, home_team, away_team, outcome, venue, "
        "decimal_odds FROM price_snapshots "
        "WHERE decimal_odds IS NOT NULL AND venue != 'polymarket'")]
    conn.close()
    if not rows:
        print("\nNo book quotes in price_snapshots -- is log_prices.py running?")
        return

    markets = defaultdict(dict)
    leagues = {}
    for r in rows:
        key = (r["snapshot_time"], r["home_team"], r["away_team"])
        markets[key].setdefault(r["venue"], {})[r["outcome"]] = r["decimal_odds"]
        leagues[key] = r["league"]

    print(f"\n=== Live snapshots: what shopping is worth ({len(markets)} markets) ===")
    print(f"{'league':>24} {'markets':>8} {'all books':>11} {'US-only':>9}")
    by_league = defaultdict(lambda: {"all": [], "us": []})
    for key, quotes in markets.items():
        league = leagues[key]
        outcomes = ("H", "A") if _two_way(league) else ("H", "D", "A")
        for label, allowed in (("all", None), ("us", US_ACCESSIBLE)):
            g = shopping_gain(quotes, outcomes, allowed_venues=allowed)
            if g:
                by_league[league][label].append(g["gain"])
    for league, d in sorted(by_league.items()):
        a = sum(d["all"]) / len(d["all"]) if d["all"] else None
        u = sum(d["us"]) / len(d["us"]) if d["us"] else None
        print(f"{league:>24} {len(d['all']):>8} "
              f"{(f'{a:+.2%}' if a is not None else '--'):>11} "
              f"{(f'{u:+.2%}' if u is not None else '--'):>9}")
    print("\nValues are hold SAVED per bet by taking the best quote instead of an\n"
          "average one. Positive means shopping pays.")


def _two_way(league):
    """Markets with no draw: basketball and tennis."""
    lg = (league or "").lower()
    return lg.startswith("basketball") or lg.startswith("tennis") or lg == "nba"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Measure and apply best-price execution.")
    ap.add_argument("--tennis", action="store_true", help="historical tennis price levels")
    ap.add_argument("--snapshots", action="store_true", help="live logged book quotes")
    args = ap.parse_args()

    if args.tennis or not args.snapshots:
        report_tennis()
    if args.snapshots or not args.tennis:
        report_snapshots()
