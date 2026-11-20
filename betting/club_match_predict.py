"""
Predicts a club match (Premier League or MLS), combining two layers:

  1. club_model.py — the statistical base rate: Elo, head-to-head record,
     recent form, all derived purely from match history.
  2. external_factors_agent.py — Grok (live web search) + Gemini research on
     things pure history can't see: injuries, suspensions, lineup news,
     travel/fixture congestion, manager changes, motivation (e.g. a mid-
     table team resting starters once safe from relegation).

Same two-layer philosophy as pretournament_predictor.py uses for the World
Cup: stats set the base rate, live research nudges it for information a
backward-looking dataset structurally cannot contain.

Because clubs play each other repeatedly (unlike a single-elimination
bracket), each fixture's research report is keyed by --as-of-date so a
Liverpool vs Man City report from August doesn't get reused for their
rematch in December.

Usage:
    py club_match_predict.py "Liverpool" "Man City" --league premier_league --as-of-date 2026-08-15
    py club_match_predict.py "Liverpool" "Man City" --league premier_league --as-of-date 2026-08-15 --no-research
"""

import argparse
import os

from club_model import load_weights, predict_match
from external_factors_agent import get_matchup_report, has_report, load_adjustment

ADJUSTMENT_CAP = 0.15  # matches ADJUSTMENT_CAP_PCT/100 in external_factors_agent.py


def adjusted_predict(home_team, away_team, league="premier_league", context=None,
                      as_of_date=None, research=True):
    probs, feats = predict_match(home_team, away_team, league=league)

    if research:
        if not has_report(home_team, away_team, fixture_id=as_of_date):
            print(f"  researching {home_team} vs {away_team} "
                  f"({league}, as of {as_of_date})...")
            get_matchup_report(home_team, away_team, context=context or league,
                                as_of_date=as_of_date, fixture_id=as_of_date)
        adj = load_adjustment(home_team, away_team, fixture_id=as_of_date)
    else:
        adj = 0.0

    if adj:
        base = dict(probs)
        p_home = min(0.98, max(0.01, probs["H"] + adj))
        p_away = min(0.98, max(0.01, probs["A"] - adj))
        p_draw = probs["D"]
        total = p_home + p_draw + p_away
        probs = {"H": p_home / total, "D": p_draw / total, "A": p_away / total}
        print(f"  [external factors] adjustment {adj:+.1%} applied "
              f"(base H/D/A: {base['H']:.1%}/{base['D']:.1%}/{base['A']:.1%})")

    return probs, feats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict a club match using stats + live research.")
    parser.add_argument("home_team")
    parser.add_argument("away_team")
    parser.add_argument("--league", choices=["premier_league", "mls"], default="premier_league")
    parser.add_argument("--context", default=None, help="e.g. 'Premier League matchday 3'")
    parser.add_argument("--as-of-date", dest="as_of_date", default=None,
                         help="YYYY-MM-DD, day before the match. Required for --research to avoid "
                              "leaking the actual result if this fixture has already been played, "
                              "and to keep repeat meetings between these clubs from colliding.")
    parser.add_argument("--no-research", dest="research", action="store_false",
                         help="Skip the Grok/Gemini research pass — stats-only prediction.")
    args = parser.parse_args()

    if args.research and not args.as_of_date:
        parser.error("--as-of-date is required unless --no-research is passed.")

    for var in ("XAI_API_KEY", "GOOGLE_API_KEY"):
        if args.research and not os.getenv(var):
            raise SystemExit(f"Missing {var}. Copy .env.example to .env and fill it in, "
                              f"or pass --no-research for a stats-only prediction.")

    probs, feats = adjusted_predict(args.home_team, args.away_team, league=args.league,
                                     context=args.context, as_of_date=args.as_of_date,
                                     research=args.research)

    print(f"\n[{args.league}] {args.home_team} (home) vs {args.away_team} (away):")
    print(f"  Home win: {probs['H']:.1%}")
    print(f"  Draw:     {probs['D']:.1%}")
    print(f"  Away win: {probs['A']:.1%}")
    print(f"\n  Base stats: elo_diff={feats['elo_diff']:.1f}, "
          f"h2h_home_win_rate={feats['h2h_home_win_rate']:.0%} "
          f"(over {feats['h2h_meetings']:.0f} prior meetings hosting this opponent), "
          f"recent_form_diff={feats['recent_form_diff']:+.2f} pts/game")
