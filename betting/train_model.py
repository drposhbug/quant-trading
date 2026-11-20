"""
Train a real win-probability model
================================================================================
Every predictor in this repo (pretournament_predictor.py, blended_predictor.py,
etc.) uses a hand-picked Elo scale (ELO_SCALE = 400) nobody has ever validated
against real results. This script replaces that guess with weights *learned*
from actual history:

  1. Pull every international match since FIFA rankings started (1993) from a
     public results dataset, and the full FIFA ranking history (already used
     elsewhere in this repo).
  2. For each match, attach each team's FIFA points as of just before that
     match (an "as-of" join — never using points from after the match, same
     no-leakage principle as external_factors_agent.py's date cutoffs).
  3. Train a logistic regression: points_diff (+ neutral-venue flag) -> did
     the stronger-ranked team win? Only decisive (non-draw) matches are used,
     matching how the bracket simulators treat matches (no draws in a
     single-elimination bracket).
  4. Backtest on a held-out, chronologically later slice of matches (not a
     random split — you can't "peek" at future matches when betting on
     current ones) and compare against the old hardcoded ELO_SCALE=400
     baseline on the same test set.
  5. Save the learned weights to model_weights.json so trained_model.py can
     load them without retraining.

Usage:
    py train_model.py
"""

import io
import json
import os

import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss

RESULTS_CSV_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
FIFA_RANKING_CSV_URL = (
    "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/master/ranking_fifa_historical.csv"
)
TRAIN_TEST_SPLIT_DATE = "2022-01-01"  # train on everything before, test on everything after
WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_weights.json")


def fetch_historical_results():
    r = requests.get(RESULTS_CSV_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df["date"] = pd.to_datetime(df["date"])
    df["neutral"] = df["neutral"].astype(str).str.upper() == "TRUE"
    return df


def fetch_fifa_history():
    r = requests.get(FIFA_RANKING_CSV_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df["date"] = pd.to_datetime(df["date"])
    return df[["date", "team", "total_points"]].sort_values("date")


def attach_asof_points(results, fifa, team_col, points_col):
    """
    For each match, attach `team_col`'s FIFA points as of the most recent
    ranking snapshot strictly before (or on) the match date. Rows for teams
    with no ranking history before that date get NaN and are dropped later.
    """
    side = fifa.rename(columns={"team": team_col, "total_points": points_col})
    merged = pd.merge_asof(
        results.sort_values("date"),
        side.sort_values("date"),
        on="date",
        by=team_col,
        direction="backward",
    )
    return merged


def build_training_set():
    results = fetch_historical_results()
    fifa = fetch_fifa_history()

    results = results[results["date"] >= fifa["date"].min()]
    results = attach_asof_points(results, fifa, "home_team", "home_points")
    results = attach_asof_points(results, fifa, "away_team", "away_points")

    before = len(results)
    results = results.dropna(subset=["home_points", "away_points"])
    print(f"Matched FIFA points for {len(results)}/{before} matches "
          f"({len(results) / before:.0%}) — the rest are teams whose names "
          f"don't line up between the two datasets (renamed/historical "
          f"countries) and were dropped.")

    results["points_diff"] = results["home_points"] - results["away_points"]

    decisive = results[results["home_score"] != results["away_score"]].copy()
    decisive["home_win"] = (decisive["home_score"] > decisive["away_score"]).astype(int)
    print(f"{len(decisive)} decisive (non-draw) matches usable for training/testing.")
    return decisive


def elo_baseline_probability(points_diff, scale=400.0):
    return 1.0 / (1.0 + 10 ** (-points_diff / scale))


if __name__ == "__main__":
    data = build_training_set()

    train = data[data["date"] < TRAIN_TEST_SPLIT_DATE]
    test = data[data["date"] >= TRAIN_TEST_SPLIT_DATE]
    print(f"\nTrain: {len(train)} matches (before {TRAIN_TEST_SPLIT_DATE})")
    print(f"Test:  {len(test)} matches (on/after {TRAIN_TEST_SPLIT_DATE}, held out — never seen during training)")

    X_train = train[["points_diff", "neutral"]].astype(float)
    y_train = train["home_win"]
    X_test = test[["points_diff", "neutral"]].astype(float)
    y_test = test["home_win"]

    model = LogisticRegression()
    model.fit(X_train, y_train)

    learned_probs = model.predict_proba(X_test)[:, 1]
    baseline_probs = elo_baseline_probability(test["points_diff"].values)

    print("\n=== Held-out test set: learned model vs. hardcoded ELO_SCALE=400 ===")
    print(f"{'metric':20s} {'learned model':>15s} {'old ELO_SCALE=400':>20s}")
    print(f"{'accuracy':20s} {accuracy_score(y_test, learned_probs > 0.5):15.3f} "
          f"{accuracy_score(y_test, baseline_probs > 0.5):20.3f}")
    print(f"{'log loss (lower=better)':20s} {log_loss(y_test, learned_probs):15.3f} "
          f"{log_loss(y_test, baseline_probs):20.3f}")
    print(f"{'brier score (lower=better)':20s} {brier_score_loss(y_test, learned_probs):15.3f} "
          f"{brier_score_loss(y_test, baseline_probs):20.3f}")

    coef_points_diff, coef_neutral = model.coef_[0]
    intercept = model.intercept_[0]
    print(f"\nLearned weights: points_diff coef={coef_points_diff:.6f}, "
          f"neutral coef={coef_neutral:.4f}, intercept={intercept:.4f}")
    print(f"(For comparison, the old ELO_SCALE=400 hardcoded formula is "
          f"equivalent to a points_diff coef of {2.302585 / 400:.6f} with no "
          f"neutral-venue term and intercept=0.)")

    weights = {
        "coef_points_diff": coef_points_diff,
        "coef_neutral": coef_neutral,
        "intercept": intercept,
        "trained_on_matches": len(train),
        "train_test_split_date": TRAIN_TEST_SPLIT_DATE,
    }
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2)
    print(f"\nSaved weights to {WEIGHTS_PATH}")
