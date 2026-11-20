"""
Loads weights trained by train_club_model.py (Premier League) or
train_mls_model.py (MLS) and predicts a 3-way (home win / draw / away win)
probability for any two clubs, using the model's own statistically-derived
features: Elo rating, head-to-head record for this exact home/away pairing,
and each team's recent form (see club_features.py).
"""

import json
import math
import os

from club_features import predict_features

WEIGHTS_PATHS = {
    "premier_league": os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "club_model_weights_premier_league.json"
    ),
    "mls": os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "club_model_weights_mls.json"
    ),
}


def load_weights(league="premier_league"):
    path = WEIGHTS_PATHS[league]
    if not os.path.exists(path):
        trainer = "train_club_model.py" if league == "premier_league" else "train_mls_model.py"
        raise FileNotFoundError(f"{os.path.basename(path)} not found — run {trainer} first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def predict_match(home_team, away_team, league="premier_league", weights=None):
    """
    Returns (probs, features) where probs = {'H': ..., 'D': ..., 'A': ...}
    and features is the raw stat vector used (elo_diff, h2h_home_win_rate,
    h2h_meetings, recent_form_diff) — handy for seeing *why* it predicted
    what it predicted.
    """
    w = weights or load_weights(league)
    ratings = w["final_state"]["elo"]
    if home_team not in ratings or away_team not in ratings:
        unknown = [t for t in (home_team, away_team) if t not in ratings]
        raise KeyError(f"No rating for: {unknown}. Check spelling against final_state.elo in "
                        f"{WEIGHTS_PATHS[league]}, or retrain if this is a newly added/promoted club.")

    feats = predict_features(home_team, away_team, w["final_state"])
    classes = w["classes"]
    scores = [
        intercept + sum(c * f for c, f in zip(coefs, feats))
        for coefs, intercept in zip(w["coef"], w["intercept"])
    ]
    exp_scores = [math.exp(s) for s in scores]
    total = sum(exp_scores)
    probs = {cls: score / total for cls, score in zip(classes, exp_scores)}
    return probs, dict(zip(w["feature_names"], feats))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Predict a club match outcome.")
    parser.add_argument("home_team")
    parser.add_argument("away_team")
    parser.add_argument("--league", choices=list(WEIGHTS_PATHS), default="premier_league")
    args = parser.parse_args()

    w = load_weights(args.league)
    probs, feats = predict_match(args.home_team, args.away_team, league=args.league, weights=w)
    print(f"[{args.league}] {args.home_team} (home) vs {args.away_team} (away):")
    print(f"  Home win: {probs['H']:.1%}")
    print(f"  Draw:     {probs['D']:.1%}")
    print(f"  Away win: {probs['A']:.1%}")
    print(f"\n  Based on: elo_diff={feats['elo_diff']:.1f}, "
          f"h2h_home_win_rate={feats['h2h_home_win_rate']:.0%} "
          f"(over {feats['h2h_meetings']:.0f} prior meetings hosting this opponent), "
          f"recent_form_diff={feats['recent_form_diff']:+.2f} pts/game")
