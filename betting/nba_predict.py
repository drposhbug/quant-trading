"""
Predicts an NBA game, combining two layers (same philosophy as
club_match_predict.py, adapted to basketball's binary home/away market):

  1. The statistical base rate from train_nba_model.py's weights — NBA-tuned
     Elo, rolling net rating, recent form, and rest / back-to-back situation
     (see nba_features.py), all from game history.
  2. external_factors_agent.py — Grok (live web/X search) + Gemini research on
     what a box-score dataset structurally can't see: star injuries and
     load-management rest-outs (which swing NBA lines more than in any other
     sport), trades, and back-end-of-a-long-road-trip fatigue.

Because two teams meet several times a season (and up to seven times in a
playoff series), each game's research report is keyed by --as-of-date so one
night's report is never reused for a later meeting.

Unlike the 3-way soccer model, this is a 2-class logistic: sklearn stores a
single coefficient row for the log-odds of a home win, so probabilities come
from a sigmoid, not a 3-way softmax.

Usage:
    py nba_predict.py "Boston Celtics" "Los Angeles Lakers"
    py nba_predict.py "Boston Celtics" "Los Angeles Lakers" --home-rest 2 --away-rest 1
    py nba_predict.py "Boston Celtics" "Los Angeles Lakers" --research --as-of-date 2026-01-14
"""

import argparse
import json
import math
import os

from nba_features import predict_features

WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "nba_model_weights.json"
)
ADJUSTMENT_CAP = 0.15  # matches ADJUSTMENT_CAP_PCT/100 in external_factors_agent.py


def load_weights():
    if not os.path.exists(WEIGHTS_PATH):
        raise FileNotFoundError(
            f"{os.path.basename(WEIGHTS_PATH)} not found — run train_nba_model.py first."
        )
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def predict_match(home_team, away_team, weights=None, home_rest=None, away_rest=None):
    """
    Returns (probs, features) where probs = {'H': p_home_win, 'A': p_away_win}
    and features is the raw stat vector used, for seeing *why* it predicted
    what it did. home_rest/away_rest are optional days of rest from the
    schedule; omit them for a neutral (well-rested, no back-to-back) matchup.
    """
    w = weights or load_weights()
    ratings = w["final_state"]["elo"]
    unknown = [t for t in (home_team, away_team) if t not in ratings]
    if unknown:
        raise KeyError(
            f"No rating for: {unknown}. Check the exact team name against "
            f"final_state.elo in {os.path.basename(WEIGHTS_PATH)} "
            f"(nba_api uses full names like 'Los Angeles Lakers'), or retrain."
        )

    feats = predict_features(home_team, away_team, w["final_state"],
                             home_rest=home_rest, away_rest=away_rest)
    # binary logistic: the single coef row / intercept give the log-odds of the
    # positive class classes_[1] ('H', a home win)
    z = w["intercept"][0] + sum(c * f for c, f in zip(w["coef"][0], feats))
    p_home = 1.0 / (1.0 + math.exp(-z))
    probs = {"H": p_home, "A": 1.0 - p_home}
    return probs, dict(zip(w["feature_names"], feats))


def adjusted_predict(home_team, away_team, home_rest=None, away_rest=None,
                     context=None, as_of_date=None, research=True):
    """Base statistical prediction, optionally nudged by Grok/Gemini research."""
    probs, feats = predict_match(home_team, away_team,
                                 home_rest=home_rest, away_rest=away_rest)

    adj = 0.0
    if research:
        from external_factors_agent import get_matchup_report, has_report, load_adjustment
        if not has_report(home_team, away_team, fixture_id=as_of_date):
            print(f"  researching {home_team} vs {away_team} (NBA, as of {as_of_date})...")
            get_matchup_report(home_team, away_team, context=context or "NBA game",
                               as_of_date=as_of_date, fixture_id=as_of_date)
        adj = load_adjustment(home_team, away_team, fixture_id=as_of_date)

    if adj:
        adj = max(-ADJUSTMENT_CAP, min(ADJUSTMENT_CAP, adj))
        base = dict(probs)
        p_home = min(0.99, max(0.01, probs["H"] + adj))
        probs = {"H": p_home, "A": 1.0 - p_home}
        print(f"  [external factors] adjustment {adj:+.1%} applied "
              f"(base H/A: {base['H']:.1%}/{base['A']:.1%})")

    return probs, feats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict an NBA game using stats + optional research.")
    parser.add_argument("home_team")
    parser.add_argument("away_team")
    parser.add_argument("--home-rest", dest="home_rest", type=int, default=None,
                        help="home team's days of rest (1 = back-to-back). Optional.")
    parser.add_argument("--away-rest", dest="away_rest", type=int, default=None,
                        help="away team's days of rest (1 = back-to-back). Optional.")
    parser.add_argument("--context", default=None, help="e.g. 'NBA regular season, Jan 14'")
    parser.add_argument("--as-of-date", dest="as_of_date", default=None,
                        help="YYYY-MM-DD, day before tip-off. Required for --research to avoid "
                             "leaking a played result and to keep repeat meetings from colliding.")
    parser.add_argument("--research", dest="research", action="store_true",
                        help="Run the Grok/Gemini research pass (injuries, rest-outs). "
                             "Off by default — stats-only prediction.")
    args = parser.parse_args()

    if args.research and not args.as_of_date:
        parser.error("--as-of-date is required when --research is passed.")
    if args.research:
        for var in ("XAI_API_KEY", "GOOGLE_API_KEY"):
            if not os.getenv(var):
                raise SystemExit(f"Missing {var}. Copy .env.example to .env and fill it in, "
                                 f"or drop --research for a stats-only prediction.")

    probs, feats = adjusted_predict(args.home_team, args.away_team,
                                    home_rest=args.home_rest, away_rest=args.away_rest,
                                    context=args.context, as_of_date=args.as_of_date,
                                    research=args.research)

    print(f"\n[NBA] {args.home_team} (home) vs {args.away_team} (away):")
    print(f"  Home win: {probs['H']:.1%}")
    print(f"  Away win: {probs['A']:.1%}")
    print(f"\n  Base stats: elo_diff={feats['elo_diff']:.1f}, "
          f"net_rating_diff={feats['net_rating_diff']:+.1f} pts/100poss, "
          f"form_diff={feats['form_diff']:+.2f} win%, "
          f"rest_diff={feats['rest_diff']:+.0f}d, b2b_diff={feats['b2b_diff']:+.0f}")
