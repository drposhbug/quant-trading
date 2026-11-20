"""
Analyzes the price_snapshots table built by log_prices.py and answers the
four questions that determine whether trading Polymarket EPL markets is
worth it — before any real money moves:

  1. DIVERGENCE — how often, and by how much, does Polymarket's mid price
     differ from the de-vigged sharp-book line? Divergences larger than
     Polymarket's own bid/ask spread are the tradeable ones.
  2. ARBITRAGE — how often does buying the cheapest price per outcome
     across venues cost less than $1 per $1 of guaranteed payout?
  3. LEAD-LAG (coarse) — when the sharp line moves, does Polymarket move
     with it or one snapshot later? PM following = a speed edge exists.
     With snapshots hours apart this is a coarse signal; treat "PM lags"
     as reason to log faster near kickoff, not as a finished result.
  4. PAPER-TRADE CLV — for a simple rule ("trade toward the sharp line
     whenever the fair prob is outside PM's spread by EDGE_MARGIN"), did
     entries beat Polymarket's closing price? Closing line value converges
     on far fewer samples than ROI — consistently beating the close IS
     edge, before a single result settles.

Usage:
    py analyze_prices.py
    py analyze_prices.py --sharp-book pinnacle --edge-margin 0.02
"""

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np

from bet_sizer import suggest_stake
from nba_odds import devig_power
from db import get_connection, init_paper_trades, log_paper_trades
from odds_compare import FD_TO_FULL

MIN_SNAPSHOTS_FOR_LAG = 4  # per fixture-outcome series

# Odds API full names -> football-data short names (what the model was
# trained on). Names not in the map pass through unchanged ("Arsenal").
FULL_TO_FD = {full: short for short, full in FD_TO_FULL.items()}


def outcomes_for(league):
    """
    The tradeable outcomes for a market. The NBA (and any basketball market)
    is 2-way — overtime settles ties, so there's no draw — while soccer is the
    3-way home/draw/away. Everything downstream (de-vig, arb, the signal scan)
    iterates this instead of a hardcoded ('H','D','A'), so both market shapes
    flow through the same code.
    """
    lg = (league or "").lower()
    # Sport keys arrive as 'basketball_nba', 'tennis_atp_...', etc.; any
    # league that falls through to the 3-way branch has the scan invent a
    # draw the market does not price, corrupting every de-vig downstream —
    # this silently zeroed NFL and MLB when they were first added. Moneyline
    # NFL/MLB/NHL are 2-way (overtime/extra innings settle it; the rare NFL
    # tie is a push at the books and resolved per market rules on PM).
    two_way = (lg.startswith(("basketball", "tennis", "americanfootball",
                              "baseball", "icehockey")) or lg == "nba")
    return ("H", "A") if two_way else ("H", "D", "A")


def devig(odds_by_outcome, outcomes):
    """
    De-vig one book's decimal odds -> fair probabilities over `outcomes`.
    Generalizes odds_compare.devig (which is fixed to the 3-way soccer market)
    to the 2-way NBA market by normalizing over whatever outcome set is passed.
    """
    raw = {k: 1.0 / odds_by_outcome[k] for k in outcomes}
    total = sum(raw.values())
    if len(outcomes) == 2:
        # Proportional de-vig takes the same FRACTION off both sides, but books
        # load more vig on the longshot -- so it leaves a favourite-longshot
        # bias that reads as fake edge on underdogs. The power method solves
        # for the exponent that makes the two fair probabilities sum to 1.
        a, b = outcomes
        p_a = devig_power(odds_by_outcome[a], odds_by_outcome[b])
        return {a: p_a, b: 1.0 - p_a}, total
    return {k: v / total for k, v in raw.items()}, total


def load_snapshots():
    conn = get_connection()
    conn.row_factory = None
    cur = conn.execute(
        "SELECT snapshot_time, league, commence_time, home_team, away_team, outcome, venue, "
        "price, bid, ask_size, decimal_odds FROM price_snapshots ORDER BY snapshot_time")
    cols = ["snapshot_time", "league", "commence_time", "home_team", "away_team", "outcome",
            "venue", "price", "bid", "ask_size", "decimal_odds"]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def group_snapshots(rows):
    """
    -> (grouped, fixture_league) where
       grouped = {fixture_key: {snapshot_time: {"pm": {outcome: (bid, ask, size)},
                                                 "books": {book: {outcome: odds}}}}}
       fixture_league = {fixture_key: league}   (the Odds API sport key)
    fixture_key = (home, away, commence_time)
    """
    grouped = defaultdict(lambda: defaultdict(lambda: {"pm": {}, "books": defaultdict(dict)}))
    fixture_league = {}
    for r in rows:
        key = (r["home_team"], r["away_team"], r["commence_time"])
        fixture_league[key] = r["league"]
        snap = grouped[key][r["snapshot_time"]]
        if r["venue"] == "polymarket":
            snap["pm"][r["outcome"]] = (r["bid"], r["price"], r["ask_size"])
        else:
            snap["books"][r["venue"]][r["outcome"]] = r["decimal_odds"]
    return grouped, fixture_league


def sharp_fair(snap, outcomes, sharp_book, fallback_books):
    """De-vigged fair probs from the sharp book (or first fallback quoting every outcome)."""
    for book in [sharp_book] + fallback_books:
        odds = snap["books"].get(book, {})
        if all(k in odds and odds[k] for k in outcomes):
            fair, _ = devig(odds, outcomes)
            return fair, book
    return None, None


# The sharp set for the consensus line: Pinnacle plus the other references
# that price close to it — the Betfair exchange (an actual market), lowvig,
# and BetOnline. An average of several sharp de-vigs is usually a better
# close predictor than any single book (one book = one trader pool + update
# latency), but here that is MEASURED, not assumed: trader.py logs this next
# to the Pinnacle fair on every probe, and --report says which one tracked
# the close better. Switch the strategy's fair only when the data votes.
CONSENSUS_BOOKS = ("pinnacle", "betfair_ex_eu", "lowvig", "betonlineag")


def consensus_fair(snap, outcomes, books=CONSENSUS_BOOKS, min_books=2):
    """Average de-vigged fair across the sharp set; None below min_books."""
    fairs = []
    for book in books:
        odds = snap["books"].get(book, {})
        if all(k in odds and odds[k] for k in outcomes):
            fair, _ = devig(odds, outcomes)
            fairs.append(fair)
    if len(fairs) < min_books:
        return None, 0
    avg = {k: sum(f[k] for f in fairs) / len(fairs) for k in outcomes}
    return avg, len(fairs)


def pm_mid(snap, outcome):
    bid, ask, _ = snap["pm"].get(outcome, (None, None, None))
    if bid is not None and ask is not None:
        return (bid + ask) / 2.0
    return ask  # indicative-only rows have no bid


def _model_names(home_full, away_full, league):
    """
    The team names the model was trained on. Soccer models use football-data
    short names (mapped from Odds API full names); the NBA model uses full
    team names, which already match the Odds API's — so it's a passthrough.
    """
    if (league or "").startswith("basketball"):
        return home_full, away_full
    return FULL_TO_FD.get(home_full, home_full), FULL_TO_FD.get(away_full, away_full)


def model_probs_for(home_full, away_full, league):
    """
    Trained-model probabilities for a fixture named in Odds API full names,
    over that league's outcome set (H/D/A for soccer, H/A for the NBA).
    Returns None when the model or a team is unavailable (newly promoted club,
    a name mismatch, missing weights) — the scan degrades to sharp-line-only
    rather than failing.
    """
    home, away = _model_names(home_full, away_full, league)
    try:
        if (league or "").startswith("basketball"):
            from nba_predict import predict_match
            probs, _ = predict_match(home, away)
        else:
            from club_model import predict_match
            probs, _ = predict_match(home, away, league="premier_league")
        return probs
    except Exception:
        return None


def targeted_research(home_full, away_full, league, commence_time, model_p, fair):
    """
    Cost-targeted external research: only fires when the model ALREADY
    disagrees strongly with the sharp line — the spots where an injury, a star
    resting, or a lineup fact could actually flip a betting decision.
    Everything else skips the ~2 paid API calls. Returns the researched
    adjustment folded into the model's home-win probability, or the original
    probs if research isn't available/needed. The fold respects market shape:
    the NBA's 2-way (H +adj, A = rest) vs soccer's 3-way (H +adj, A -adj, D held).
    """
    from external_factors_agent import get_matchup_report, has_report, load_adjustment

    home, away = _model_names(home_full, away_full, league)
    context = "NBA game" if (league or "").startswith("basketball") else "Premier League"
    fixture_id = (commence_time or "")[:10] or None
    if not has_report(home, away, fixture_id=fixture_id):
        get_matchup_report(home, away, context=context,
                           as_of_date=fixture_id, fixture_id=fixture_id)
    adj = load_adjustment(home, away, fixture_id=fixture_id)
    if not adj or model_p is None:
        return model_p, adj
    if (league or "").startswith("basketball"):
        p_h = min(0.99, max(0.01, model_p["H"] + adj))
        return {"H": p_h, "A": 1.0 - p_h}, adj
    p_h = min(0.98, max(0.01, model_p["H"] + adj))
    p_a = min(0.98, max(0.01, model_p["A"] - adj))
    total = p_h + model_p["D"] + p_a
    return {"H": p_h / total, "D": model_p["D"] / total, "A": p_a / total}, adj


def scan_live_opportunities(grouped, fixture_league, sharp_book, fallbacks, edge_margin,
                            bankroll, research=False, research_threshold=0.05):
    """
    Looks ONLY at the most recent snapshot run and returns actionable
    signals: fixtures where Polymarket's executable price (ask for buys,
    bid for sells) is beyond the de-vigged sharp line by more than
    edge_margin. Each signal carries the model's view and a suggested
    stake from bet_sizer. Sizing uses the SHARP-LINE edge — that's the
    validated signal (+6% at best price); the model/research numbers are
    context, not the sizing input. Handles both 3-way soccer and 2-way NBA
    markets via each fixture's outcome set.
    """
    latest = max((t for snaps in grouped.values() for t in snaps), default=None)
    if latest is None:
        return [], None

    signals = []
    for fixture, snaps in grouped.items():
        snap = snaps.get(latest)
        if not snap or not snap["pm"]:
            continue
        league = fixture_league.get(fixture)
        outcomes = outcomes_for(league)
        fair, book = sharp_fair(snap, outcomes, sharp_book, fallbacks)
        if fair is None:
            continue
        home, away, commence = fixture
        # An in-play Polymarket price vs a pre-match sharp line is a phantom
        # edge (the book line stops updating at kickoff) — skip started games.
        if commence and commence <= latest:
            continue
        model_p = model_probs_for(home, away, league)
        adj = None
        if research and model_p is not None and any(
                abs(model_p[k] - fair[k]) > research_threshold for k in outcomes):
            model_p, adj = targeted_research(home, away, league, commence, model_p, fair)

        for k in outcomes:
            bid, ask, depth = snap["pm"].get(k, (None, None, None))
            if ask is not None and fair[k] > ask + edge_margin:
                side, entry, edge = "buy_yes", ask, fair[k] - ask
            elif bid is not None and fair[k] < bid - edge_margin:
                side, entry, edge = "sell_yes", bid, bid - fair[k]
            else:
                continue
            # selling YES = buying NO at (1 - bid); Kelly must see the price
            # of the position actually being opened
            kelly_price = entry if side == "buy_yes" else 1.0 - entry
            sizing = suggest_stake(edge, kelly_price, bankroll)
            signals.append({
                "logged_at": latest, "league": league,
                "commence_time": commence, "home_team": home, "away_team": away,
                "outcome": k, "side": side, "entry_price": entry, "depth": depth,
                "fair_prob": fair[k], "model_prob": model_p[k] if model_p else None,
                "edge": edge, "suggested_stake": sizing["stake"],
                "sharp_book": book, "research_adj": adj,
            })
    signals.sort(key=lambda s: s["edge"], reverse=True)
    return signals, latest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze logged Polymarket vs sportsbook prices.")
    parser.add_argument("--sharp-book", default="pinnacle",
                        help="book treated as the fair-line benchmark (default: pinnacle)")
    parser.add_argument("--edge-margin", type=float, default=0.02,
                        help="required gap beyond PM's bid/ask to count as tradeable (default: 0.02)")
    parser.add_argument("--alert", action="store_true",
                        help="live-signal mode: scan only the latest snapshot, print actionable "
                             "opportunities with stakes, skip the historical report")
    parser.add_argument("--bankroll", type=float, default=1000.0,
                        help="bankroll bet sizing is computed against (default: 1000)")
    parser.add_argument("--paper-log", action="store_true",
                        help="record live signals to the paper_trades table for later CLV scoring")
    parser.add_argument("--research", action="store_true",
                        help="run Grok/Gemini research, but ONLY on fixtures where the model "
                             "already disagrees with the sharp line by >5%% (costs ~2 API calls "
                             "per such fixture; needs XAI_API_KEY/GOOGLE_API_KEY)")
    args = parser.parse_args()

    rows = load_snapshots()
    if not rows:
        raise SystemExit("No snapshots yet — run log_prices.py first (and give it a few days).")
    grouped, fixture_league = group_snapshots(rows)
    all_books = sorted({r["venue"] for r in rows if r["venue"] != "polymarket"})
    fallbacks = [b for b in all_books if b != args.sharp_book]

    # ---- 0. live opportunity scan (latest snapshot only) ------------------
    signals, latest = scan_live_opportunities(
        grouped, fixture_league, args.sharp_book, fallbacks, args.edge_margin,
        args.bankroll, research=args.research)
    print(f"=== 0. Live signals (snapshot {latest}, edge > {args.edge_margin:.0%} "
          f"beyond PM's own price, sized for ${args.bankroll:,.0f}) ===")
    if signals:
        for s in signals:
            depth = f", depth {s['depth']:.0f} sh" if s["depth"] else ""
            model = f", model {s['model_prob']:.1%}" if s["model_prob"] is not None else ""
            adj = f", research adj {s['research_adj']:+.1%}" if s["research_adj"] else ""
            print(f"  {s['side'].upper():8s} {s['home_team']} vs {s['away_team']} [{s['outcome']}] "
                  f"@ {s['entry_price']:.3f} (fair {s['fair_prob']:.1%} per {s['sharp_book']}"
                  f"{model}{adj}) edge {s['edge']:+.1%} -> stake ${s['suggested_stake']:.2f}{depth}")
        if args.paper_log:
            init_paper_trades()
            n = log_paper_trades([{k: v for k, v in s.items()
                                   if k not in ("sharp_book", "research_adj")} for s in signals])
            print(f"  logged {n} paper trade(s) to paper_trades")
    else:
        print("  No live signals — Polymarket quotes absent or inside the sharp line "
              "by less than the margin.")

    # PM-native arb crumbs: every outcome of one fixture bought at ask for
    # less than $1 of guaranteed payout. Real but small and fast-decaying;
    # 0.99 leaves ~1c for the taker fee on each leg. Snapshot-cadence catch
    # only — anything still here after minutes was probably already taken.
    arbs = []
    if latest:
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        horizon = (now_dt + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for fixture, snaps in grouped.items():
            snap = snaps.get(latest)
            if not snap or not snap["pm"]:
                continue
            if fixture[2] and fixture[2] <= now_iso:
                continue                      # started: settlement, not arb
            if fixture[2] and fixture[2] > horizon:
                continue                      # months-out dust books: the "arb"
                                              # locks capital for pennies
            outcomes = outcomes_for(fixture_league.get(fixture))
            quotes = [snap["pm"].get(k, (None, None, None)) for k in outcomes]
            asks = [q[1] for q in quotes]
            sizes = [q[2] for q in quotes]
            # every leg needs a real ask with executable size -- dust quotes
            # on unwatched far-out books print fantasy margins
            if (all(a is not None for a in asks) and sum(asks) < 0.99
                    and all(s is not None and s >= 10 for s in sizes)):
                arbs.append((fixture, sum(asks)))
        if arbs:
            print(f"\n  PM-NATIVE ARB: {len(arbs)} fixture(s) with sum-of-asks < 0.99:")
            for (home, away, commence), tot in sorted(arbs, key=lambda x: x[1]):
                print(f"    {home} v {away} ({commence}): asks sum {tot:.3f} "
                      f"-> locked {1 - tot:.1%} before fees/slippage")
    if args.alert:
        raise SystemExit(0)

    n_snaps = len({r["snapshot_time"] for r in rows})
    pm_fixtures = {(r["home_team"], r["away_team"]) for r in rows if r["venue"] == "polymarket"}
    print(f"=== Coverage ===")
    print(f"{len(grouped)} fixtures, {n_snaps} snapshot runs, books: {all_books}")
    print(f"Polymarket listed {len(pm_fixtures)}/{len(grouped)} fixtures at least once")

    # ---- 1. divergence + tradeable signals -------------------------------
    divergences = []          # fair - pm_mid, per (snapshot, outcome)
    tradeable = []            # (fixture, time, outcome, side, entry_price, fair)
    for fixture, snaps in grouped.items():
        outcomes = outcomes_for(fixture_league.get(fixture))
        for t, snap in snaps.items():
            fair, _ = sharp_fair(snap, outcomes, args.sharp_book, fallbacks)
            if fair is None:
                continue
            for k in outcomes:
                bid, ask, _ = snap["pm"].get(k, (None, None, None))
                mid = pm_mid(snap, k)
                if mid is not None:
                    divergences.append(fair[k] - mid)
                if ask is not None and fair[k] > ask + args.edge_margin:
                    tradeable.append((fixture, t, k, "buy_yes", ask, fair[k]))
                elif bid is not None and fair[k] < bid - args.edge_margin:
                    tradeable.append((fixture, t, k, "sell_yes", bid, fair[k]))

    print(f"\n=== 1. Polymarket vs {args.sharp_book} fair line ===")
    if divergences:
        d = np.array(divergences)
        print(f"{len(d)} (snapshot, outcome) comparisons")
        print(f"divergence (fair - PM mid): mean {d.mean():+.3f}, std {d.std():.3f}, "
              f"P5 {np.percentile(d, 5):+.3f}, P95 {np.percentile(d, 95):+.3f}")
        print(f"|divergence| > 3c: {(abs(d) > 0.03).mean():.0%} of comparisons; "
              f"> 5c: {(abs(d) > 0.05).mean():.0%}")
        print(f"tradeable signals (fair beyond PM spread by >{args.edge_margin:.0%}): "
              f"{len(tradeable)}")
    else:
        print("No overlapping PM + sharp-book quotes yet — PM likely hasn't listed "
              "these fixtures. Re-run once fixtures are closer to kickoff.")

    # ---- 2. arbitrage frequency ------------------------------------------
    print(f"\n=== 2. Cross-venue arbitrage ===")
    arb_count, checked, best_margin = 0, 0, 0.0
    for fixture, snaps in grouped.items():
        outcomes = outcomes_for(fixture_league.get(fixture))
        for t, snap in snaps.items():
            costs = {}
            for k in outcomes:
                options = []
                _, ask, _ = snap["pm"].get(k, (None, None, None))
                if ask:
                    options.append(ask)
                options += [1.0 / o for o in
                            (snap["books"].get(b, {}).get(k) for b in all_books) if o]
                if options:
                    costs[k] = min(options)
            if len(costs) == len(outcomes):
                checked += 1
                total = sum(costs.values())
                if total < 1.0:
                    arb_count += 1
                    best_margin = max(best_margin, 1.0 - total)
    if checked:
        print(f"{arb_count}/{checked} fixture-snapshots had a full cross-venue arb "
              f"(best locked margin seen: {best_margin:.1%})")
    else:
        print("No fixture-snapshots with all three outcomes priced yet.")

    # ---- 3. coarse lead-lag ----------------------------------------------
    print(f"\n=== 3. Lead-lag (coarse, snapshot-resolution) ===")
    same_pairs, lag_pairs = [], []
    for fixture, snaps in grouped.items():
        outcomes = outcomes_for(fixture_league.get(fixture))
        times = sorted(snaps)
        for k in outcomes:
            series = []
            for t in times:
                fair, _ = sharp_fair(snaps[t], outcomes, args.sharp_book, fallbacks)
                mid = pm_mid(snaps[t], k)
                if fair is not None and mid is not None:
                    series.append((fair[k], mid))
            if len(series) < MIN_SNAPSHOTS_FOR_LAG:
                continue
            fair_d = np.diff([s[0] for s in series])
            pm_d = np.diff([s[1] for s in series])
            same_pairs += list(zip(fair_d, pm_d))            # book move t vs PM move t
            lag_pairs += list(zip(fair_d[:-1], pm_d[1:]))    # book move t vs PM move t+1
    if len(lag_pairs) >= 20:
        c_same = np.corrcoef(*zip(*same_pairs))[0, 1]
        c_lag = np.corrcoef(*zip(*lag_pairs))[0, 1]
        print(f"corr(book move, PM move same snapshot): {c_same:+.2f}  "
              f"| corr(book move, PM move NEXT snapshot): {c_lag:+.2f}")
        print("PM lagging the books (second number comparable to or above the first) "
              "= a speed edge worth logging faster to confirm."
              if c_lag > 0.5 * max(c_same, 0.01) else
              "No obvious lag at this snapshot resolution.")
    else:
        print(f"Not enough overlapping series yet ({len(lag_pairs)} delta pairs; need ~20+).")

    # ---- 4. paper-trade CLV ----------------------------------------------
    print(f"\n=== 4. Paper-trade CLV (rule: trade toward the sharp line) ===")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    clvs = []
    for fixture, snaps in grouped.items():
        commence = fixture[2]
        if not commence or commence > now:
            continue  # not kicked off yet — no closing price
        pre_ko = [t for t in sorted(snaps) if t < commence]
        if len(pre_ko) < 2:
            continue
        closing_t = pre_ko[-1]
        for (fx, t, k, side, entry, fair) in tradeable:
            if fx != fixture or t >= closing_t:
                continue
            close_mid = pm_mid(snaps[closing_t], k)
            if close_mid is None:
                continue
            clv = (close_mid - entry) if side == "buy_yes" else (entry - close_mid)
            entry_edge = (fair - entry) if side == "buy_yes" else (entry - fair)
            try:
                hours_out = (datetime.fromisoformat(commence.replace("Z", "+00:00"))
                             - datetime.fromisoformat(t.replace("Z", "+00:00"))
                             ).total_seconds() / 3600.0
            except (ValueError, AttributeError):
                hours_out = None
            pos_fair = fair if side == "buy_yes" else 1.0 - fair
            clvs.append((fixture_league.get(fixture) or "?", clv, entry_edge,
                         hours_out, pos_fair))
    if clvs:
        c = np.array([t[1] for t in clvs])
        print(f"{len(c)} paper entries with a closing price: "
              f"mean CLV {c.mean():+.3f} per $1 share, beat-the-close rate {(c > 0).mean():.0%}")
        print("Sustained beat-the-close >55-60% with positive mean CLV = real edge; "
              "~50% = the divergences were noise/spread, not mispricing.")
        # CLV by entry-edge size: does a bigger gap at entry actually predict a
        # better close, or is the 2-3c bucket noise dragging the mean? This is
        # the honest version of a threshold grid -- the answer accumulates out
        # of sample instead of being fit to history; raise ENTRY_MARGIN only
        # when a low bucket shows sustained negative CLV on a real sample.
        print(f"\n{'entry edge':>12} {'n':>5} {'mean CLV':>9} {'beat close':>11}")
        for lo, hi, lbl in ((0.02, 0.03, "2-3c"), (0.03, 0.05, "3-5c"),
                            (0.05, 1.00, ">=5c")):
            a = np.array([t[1] for t in clvs if lo <= t[2] < hi])
            if len(a):
                print(f"{lbl:>12} {len(a):>5} {a.mean():>+9.3f} {(a > 0).mean():>11.0%}")
        # entry timing: edge vs the books decays into kickoff, but so does the
        # staleness risk of an old sharp print -- this table says which
        # time-to-kickoff window actually pays, out of sample
        print(f"\n{'entry timing':>12} {'n':>5} {'mean CLV':>9} {'beat close':>11}")
        for lo, hi, lbl in ((48, 10_000, ">48h out"), (12, 48, "12-48h"),
                            (2, 12, "2-12h"), (0, 2, "<2h")):
            a = np.array([t[1] for t in clvs if t[3] is not None and lo <= t[3] < hi])
            if len(a):
                print(f"{lbl:>12} {len(a):>5} {a.mean():>+9.3f} {(a > 0).mean():>11.0%}")
        # price band of the position's FAIR value: longshot buys are where
        # the favorite-longshot bias works against us (tennis longshots ran
        # -85% at resolution), and a favorites-only book is the honest route
        # to a high win rate. If the low bands show sustained negative CLV,
        # gate entries with a fair floor -- one constant, decided by data.
        print(f"\n{'fair band':>12} {'n':>5} {'mean CLV':>9} {'beat close':>11}")
        for lo, hi, lbl in ((0.00, 0.35, "<0.35"), (0.35, 0.62, "0.35-0.62"),
                            (0.62, 1.01, ">=0.62")):
            a = np.array([t[1] for t in clvs if lo <= t[4] < hi])
            if len(a):
                print(f"{lbl:>12} {len(a):>5} {a.mean():>+9.3f} {(a > 0).mean():>11.0%}")
        # Per-sport verdict — the keep/cut table. Each sport costs one Odds
        # API credit per snapshot; it earns that credit with positive mean CLV
        # on a real sample. 30+ scored entries and negative CLV = cut it from
        # DEFAULT_SPORTS in log_prices.py; fewer entries = still collecting.
        print(f"\n{'league':>24} {'n':>5} {'mean CLV':>9} {'beat close':>11}  verdict")
        by_league = {}
        for t in clvs:
            by_league.setdefault(t[0], []).append(t[1])
        for lg, vals in sorted(by_league.items()):
            a = np.array(vals)
            if len(a) < 30:
                verdict = f"collecting ({len(a)}/30)"
            elif a.mean() > 0:
                verdict = "KEEP"
            else:
                verdict = "CUT from DEFAULT_SPORTS"
            print(f"{lg:>24} {len(a):>5} {a.mean():>+9.3f} {(a > 0).mean():>11.0%}  {verdict}")
    else:
        print("No completed fixtures with pre-kickoff signals yet — this section "
              "fills in as matches are played.")
