"""
Train a club-level (MLS) match outcome model
================================================================================
Same approach as train_club_model.py (Premier League): statistical signals
built purely from match history (see club_features.py) — Elo rating,
head-to-head record for this home team hosting this exact opponent, and
each team's recent form — used to train a 3-way (home/draw/away)
multinomial classifier.

Data: American Soccer Analysis's free public API
(app.americansocceranalysis.com), no auth required. Covers MLS regular
season + playoffs from 2013 onward.

MLS Cup Playoffs are single-elimination knockout rounds (draws are resolved
by extra time/penalties), so — like the World Cup bracket predictors in this
repo — those games are used to keep Elo/H2H/form current but excluded from
the 3-way classifier's training rows, since "draw" isn't a real outcome in a
knockout match the way it is in a regular-season league game.

Usage:
    py train_mls_model.py
"""

import json
import os
from collections import Counter

import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

from club_features import FEATURE_NAMES, compute_features

GAMES_URL = "https://app.americansocceranalysis.com/api/v1/mls/games"
TEAMS_URL = "https://app.americansocceranalysis.com/api/v1/mls/teams"
SEASONS = [str(y) for y in range(2013, 2026)]
WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "club_model_weights_mls.json")


def fetch_team_names():
    r = requests.get(TEAMS_URL, timeout=20)
    r.raise_for_status()
    return {t["team_id"]: t["team_name"] for t in r.json()}


def fetch_all_games():
    games = []
    for season in SEASONS:
        r = requests.get(GAMES_URL, params={"season_name": season}, timeout=20)
        if r.status_code != 200:
            continue
        games.extend(r.json())
    games = [g for g in games if g.get("status") == "FullTime"
              and g.get("home_score") is not None and g.get("away_score") is not None]
    games.sort(key=lambda g: g["date_time_utc"])
    print(f"Loaded {len(games)} completed MLS games "
          f"({games[0]['date_time_utc'][:10]} to {games[-1]['date_time_utc'][:10]}).")
    return games


if __name__ == "__main__":
    team_names = fetch_team_names()
    games = fetch_all_games()
    matches = [
        {"date": g["date_time_utc"], "home": team_names.get(g["home_team_id"], g["home_team_id"]),
         "away": team_names.get(g["away_team_id"], g["away_team_id"]),
         "home_score": g["home_score"], "away_score": g["away_score"],
         "knockout": bool(g.get("knockout_game"))}
        for g in games
    ]
    rows, final_state = compute_features(matches)

    # Regular-season (non-knockout) games only for the 3-way classifier —
    # playoff knockout games can't end in a draw, so they'd distort the
    # "draw" class if included.
    league_rows = [r for r in rows if not r["knockout"]]
    n = len(league_rows)
    split = int(n * 0.85)  # chronological split — last ~15% held out
    train, test = league_rows[:split], league_rows[split:]
    print(f"Regular-season games usable for training: {n} "
          f"({len(rows) - n} playoff knockout games excluded from training, used only for Elo/H2H/form continuity)")
    print(f"Train: {len(train)} matches, Test: {len(test)} matches (chronologically held out)")

    X_train = [[r[name] for name in FEATURE_NAMES] for r in train]
    y_train = [r["result"] for r in train]
    X_test = [[r[name] for name in FEATURE_NAMES] for r in test]
    y_test = [r["result"] for r in test]

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)
    preds = model.classes_[probs.argmax(axis=1)]

    print("\n=== Held-out test set (most recent ~15% of regular-season games) ===")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"Log loss: {log_loss(y_test, probs, labels=model.classes_):.3f}")

    base_counts = Counter(y_train)
    base_rates = [base_counts[c] / len(y_train) for c in model.classes_]
    baseline_probs = [base_rates] * len(test)
    print(f"Baseline log loss (always predict historical H/D/A base rates): "
          f"{log_loss(y_test, baseline_probs, labels=model.classes_):.3f}")

    print(f"\nClass order: {list(model.classes_)}")
    print(f"Feature order: {FEATURE_NAMES}")
    for cls, coefs, intercept in zip(model.classes_, model.coef_, model.intercept_):
        print(f"  {cls}: coefs={dict(zip(FEATURE_NAMES, coefs.round(4)))}, intercept={intercept:.4f}")

    weights = {
        "league": "MLS",
        "classes": list(model.classes_),
        "feature_names": FEATURE_NAMES,
        "coef": model.coef_.tolist(),
        "intercept": model.intercept_.tolist(),
        "final_state": {
            "elo": {k: round(v, 1) for k, v in sorted(final_state["elo"].items())},
            "h2h": final_state["h2h"],
            "form": final_state["form"],
        },
        "trained_on_matches": len(train),
    }
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2)
    print(f"\nSaved to {WEIGHTS_PATH}")
