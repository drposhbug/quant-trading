"""
Backtests whether the external-factors layer (Grok live search + Gemini)
adds real edge over the market, on top of what the stats-only model already
gets you — on real historical matches with known odds and known outcomes.

For each sampled match:
  1. Compute the stats-only probability (club_model.py).
  2. Research it with the external-factors agent, using as_of_date = the day
     before the match, so Grok can't see the actual result — same
     no-leakage discipline as everywhere else in this repo.
  3. Compute the adjusted (stats + factors) probability.
  4. Compare both against the real bookmaker implied probability, and run
     the same edge-threshold ROI backtest as train_xgboost_model.py, so the
     two numbers are directly comparable: does adding live research turn a
     losing model into a winning one?

Uses ~2 paid API calls (Grok + Gemini) per match — costs real credits.

Usage:
    py backtest_external_factors.py --n 20
"""

import argparse

import numpy as np

from club_match_predict import adjusted_predict
from club_model import predict_match
from db import get_connection
from train_xgboost_model import implied_probs

LEAGUE = "premier_league"
EDGE_THRESHOLD = 0.05


def sample_matches(n, season="2425"):
    conn = get_connection()
    conn.row_factory = None
    rows = conn.execute(
        "SELECT date, home_team, away_team, result, odds_home, odds_draw, odds_away "
        "FROM matches WHERE league = ? AND season = ? AND odds_home IS NOT NULL ORDER BY date",
        (LEAGUE, season),
    ).fetchall()
    conn.close()
    step = max(1, len(rows) // n)
    return rows[::step][:n]


def roi_for_predictions(rows_with_probs, edge_threshold=EDGE_THRESHOLD):
    staked, returned, bets_placed = 0.0, 0.0, 0
    for row, probs in rows_with_probs:
        date, home, away, result, oh, od, oa = row
        market = dict(zip(["H", "D", "A"], implied_probs(oh, od, oa)))
        odds_map = {"H": oh, "D": od, "A": oa}
        for outcome in ("H", "D", "A"):
            edge = probs[outcome] - market[outcome]
            if edge > edge_threshold:
                staked += 1.0
                bets_placed += 1
                if result == outcome:
                    returned += odds_map[outcome]
    roi = (returned - staked) / staked if staked else None
    return {"bets_placed": bets_placed, "staked": staked, "returned": returned, "roi": roi}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--season", default="2425")
    args = parser.parse_args()

    rows = sample_matches(args.n, season=args.season)
    print(f"Sampled {len(rows)} matches from season {args.season}.\n")

    base_predictions, adjusted_predictions = [], []
    for row in rows:
        date, home, away, result, oh, od, oa = row
        match_date = str(date)[:10]

        base_probs, _ = predict_match(home, away, league=LEAGUE)
        print(f"{match_date}  {home} vs {away}  (actual: {result})")
        print(f"  base:     H={base_probs['H']:.1%} D={base_probs['D']:.1%} A={base_probs['A']:.1%}")

        adj_probs, _ = adjusted_predict(home, away, league=LEAGUE, context="Premier League",
                                         as_of_date=match_date, research=True)
        print(f"  adjusted: H={adj_probs['H']:.1%} D={adj_probs['D']:.1%} A={adj_probs['A']:.1%}")

        base_predictions.append((row, base_probs))
        adjusted_predictions.append((row, adj_probs))

    print(f"\n=== ROI comparison on these {len(rows)} matches (edge threshold = {EDGE_THRESHOLD:.0%}) ===")
    base_roi = roi_for_predictions(base_predictions)
    adj_roi = roi_for_predictions(adjusted_predictions)

    for label, result in (("Stats-only", base_roi), ("Stats + external factors", adj_roi)):
        roi_str = f"{result['roi']:+.1%}" if result["roi"] is not None else "n/a (no bets)"
        print(f"  {label:28s}: {result['bets_placed']:3d} bets, "
              f"staked ${result['staked']:.2f}, ROI {roi_str}")
