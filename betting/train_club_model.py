"""
Train a club-level (Premier League) match outcome model
================================================================================
train_model.py uses FIFA ranking points as the strength signal for national
teams. Clubs have no equivalent external ranking, so this builds its own
statistical signals purely from match history (see club_features.py):
Elo rating, head-to-head record specifically for this home team hosting
this exact opponent, and each team's recent form. All computed as-of just
before each match — no leakage, same principle as everywhere else in this
repo.

Unlike the World Cup bracket (single elimination, no draws), league matches
have three real outcomes bettors actually wager on: home win / draw / away
win. This trains a multinomial classifier on that 3-way market, not a binary
win/lose model.

Data: football-data.co.uk's free per-season CSVs (Premier League = E0),
1993-94 season through the current one.

Usage:
    py train_club_model.py
"""

import io
import json
import os

import pandas as pd
import requests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

from club_features import FEATURE_NAMES, compute_features, feature_vector

LEAGUE_CODE = "E0"  # Premier League on football-data.co.uk
SEASON_CODES = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(1993, 2026)]  # 9394 .. 2526
BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "club_model_weights_premier_league.json"
)


def fetch_season(season):
    url = BASE_URL.format(season=season, league=LEAGUE_CODE)
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return None
    df = pd.read_csv(io.StringIO(r.text), on_bad_lines="skip", engine="python")
    df = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]].dropna()
    df["season"] = season
    return df


def fetch_all_seasons():
    frames = [df for s in SEASON_CODES if (df := fetch_season(s)) is not None and len(df)]
    all_matches = pd.concat(frames, ignore_index=True)
    all_matches["Date"] = pd.to_datetime(all_matches["Date"], dayfirst=True, format="mixed")
    all_matches = all_matches.sort_values("Date").reset_index(drop=True)
    print(f"Loaded {len(all_matches)} Premier League matches "
          f"({all_matches['Date'].min().date()} to {all_matches['Date'].max().date()}).")
    return all_matches


if __name__ == "__main__":
    matches_df = fetch_all_seasons()
    matches = [
        {"date": m["Date"], "season": m["season"], "home": m["HomeTeam"], "away": m["AwayTeam"],
         "home_score": m["FTHG"], "away_score": m["FTAG"]}
        for m in matches_df.to_dict("records")
    ]
    rows, final_state = compute_features(matches)
    feats = pd.DataFrame(rows)

    test_seasons = SEASON_CODES[-3:-1]  # last two *complete* seasons held out
    current_season = SEASON_CODES[-1]
    # The current partial season is chronologically AFTER the test window, so
    # it must be excluded from evaluation training — fitting on matches played
    # after the test period lets the model see the post-test era of the league
    # and inflates the held-out scores. It gets used again below, but only in
    # the final refit AFTER evaluation is done.
    train = feats[~feats["season"].isin(test_seasons + [current_season])]
    test = feats[feats["season"].isin(test_seasons)]
    print(f"Train: {len(train)} matches (strictly before {test_seasons}; "
          f"current season {current_season} excluded from eval)")
    print(f"Test:  {len(test)} matches (seasons {test_seasons}, held out)")

    X_train = train[FEATURE_NAMES].astype(float)
    y_train = train["result"]
    X_test = test[FEATURE_NAMES].astype(float)
    y_test = test["result"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)
    preds = model.classes_[probs.argmax(axis=1)]

    print("\n=== Held-out test set (most recent complete seasons) ===")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"Log loss: {log_loss(y_test, probs, labels=model.classes_):.3f}")

    base_rates = y_train.value_counts(normalize=True).reindex(model.classes_).values
    baseline_probs = [base_rates] * len(test)
    print(f"Baseline log loss (always predict historical H/D/A base rates): "
          f"{log_loss(y_test, baseline_probs, labels=model.classes_):.3f}")

    # Evaluation is done — now refit on EVERYTHING (test seasons + current
    # partial season included) so the saved production weights use all
    # available history. The held-out numbers above are the honest estimate
    # of how a model trained this way performs; the refit just gives the
    # deployed model the freshest data.
    final_model = LogisticRegression(max_iter=1000)
    final_model.fit(feats[FEATURE_NAMES].astype(float), feats["result"])

    print(f"\nClass order: {list(final_model.classes_)}")
    print(f"Feature order: {FEATURE_NAMES}")
    for cls, coefs, intercept in zip(final_model.classes_, final_model.coef_, final_model.intercept_):
        print(f"  {cls}: coefs={dict(zip(FEATURE_NAMES, coefs.round(4)))}, intercept={intercept:.4f}")

    weights = {
        "league": "Premier League",
        "classes": list(final_model.classes_),
        "feature_names": FEATURE_NAMES,
        "coef": final_model.coef_.tolist(),
        "intercept": final_model.intercept_.tolist(),
        "final_state": {
            "elo": {k: round(v, 1) for k, v in sorted(final_state["elo"].items())},
            "h2h": final_state["h2h"],
            "form": final_state["form"],
        },
        "trained_on_matches": len(feats),  # final refit uses all history
        "test_seasons": test_seasons,
    }
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2)
    print(f"\nSaved to {WEIGHTS_PATH}")
