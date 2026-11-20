"""
Loads the weights trained by train_model.py and exposes a drop-in win
probability function. Run train_model.py first to produce model_weights.json.
"""

import json
import math
import os

WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_weights.json")


def load_weights():
    if not os.path.exists(WEIGHTS_PATH):
        raise FileNotFoundError("model_weights.json not found — run train_model.py first.")
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def learned_win_probability(points_diff, neutral=True, weights=None):
    """
    Trained-model equivalent of pretournament_predictor.py's win_probability().
    points_diff = team_a's FIFA points minus team_b's. neutral=True for
    tournament matches at neutral venues (the World Cup default).
    """
    w = weights or load_weights()
    z = (
        w["coef_points_diff"] * points_diff
        + w["coef_neutral"] * (1.0 if neutral else 0.0)
        + w["intercept"]
    )
    return 1.0 / (1.0 + math.exp(-z))


if __name__ == "__main__":
    w = load_weights()
    print(f"Loaded weights (trained on {w['trained_on_matches']} matches, "
          f"test split at {w['train_test_split_date']}):")
    print(f"  coef_points_diff = {w['coef_points_diff']:.6f}")
    print(f"  coef_neutral     = {w['coef_neutral']:.4f}")
    print(f"  intercept        = {w['intercept']:.4f}")
    for diff in (0, 100, 300, 600):
        print(f"  points_diff={diff:4d}, neutral -> "
              f"p(team_a wins) = {learned_win_probability(diff, neutral=True, weights=w):.1%}")
