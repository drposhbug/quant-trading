"""
Train the NBA match-outcome model
================================================================================
The basketball analogue of train_club_model.py. Two differences from the
soccer club model:

  * It's a BINARY market (home win / away win) — the NBA has no draws, overtime
    settles every game — so this is a 2-class logistic regression, not the
    3-way home/draw/away multinomial.
  * The strength signals come from nba_features.py (NBA-tuned Elo, rolling net
    rating, form, rest / back-to-backs) instead of club_features.py.

Same evaluation discipline as the rest of the repo: hold out the most recent
complete seasons, train strictly on earlier games, report held-out accuracy and
log loss against the base-rate baseline — then refit on ALL history so the saved
production weights use the freshest data. The held-out numbers are the honest
estimate of live performance; the refit just feeds the deployed model more data.

There's no ROI/CLV number here because nba_api carries no betting odds — ROI is
measured live via the paper-trade log (analyze_prices.py --paper-log), same as
the soccer models once they went live.

Usage:
    py train_nba_model.py
"""

import json
import os

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

from ingest_nba import fetch_all_games
from nba_features import FEATURE_NAMES, compute_features

WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "nba_model_weights.json"
)


if __name__ == "__main__":
    games = fetch_all_games()
    rows, final_state = compute_features(games)
    feats = pd.DataFrame(rows)

    seasons = sorted(feats["season"].unique())
    # Hold out the last two *complete* seasons; exclude the newest season from
    # the eval-training set entirely (it's chronologically after the test window
    # — and may be a partial in-progress season if this is run mid-year — so
    # training on it would leak the post-test era into the held-out scores).
    # Same guard as train_club_model.py.
    test_seasons = seasons[-3:-1]
    newest_season = seasons[-1]
    train = feats[~feats["season"].isin(test_seasons + [newest_season])]
    test = feats[feats["season"].isin(test_seasons)]
    print(f"Seasons: {seasons[0]} .. {seasons[-1]} ({len(seasons)} total)")
    print(f"Train: {len(train)} games (before {test_seasons}; newest {newest_season} excluded from eval)")
    print(f"Test:  {len(test)} games (seasons {test_seasons}, held out)")

    X_train, y_train = train[FEATURE_NAMES].astype(float), train["result"]
    X_test, y_test = test[FEATURE_NAMES].astype(float), test["result"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)
    preds = model.classes_[probs.argmax(axis=1)]

    print("\n=== Held-out test set (most recent complete seasons) ===")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}")
    print(f"Log loss: {log_loss(y_test, probs, labels=model.classes_):.3f}")

    base_rates = y_train.value_counts(normalize=True).reindex(model.classes_).values
    baseline = [base_rates] * len(test)
    print(f"Baseline log loss (always predict home/away base rate): "
          f"{log_loss(y_test, baseline, labels=model.classes_):.3f}")
    home_rate = (y_test == "H").mean()
    print(f"(Home team won {home_rate:.3f} of held-out games; "
          f"picking the model favorite got {accuracy_score(y_test, preds):.3f}.)")

    # Evaluation done — refit on everything (incl. held-out + newest season) so
    # production weights use all available history.
    final_model = LogisticRegression(max_iter=1000)
    final_model.fit(feats[FEATURE_NAMES].astype(float), feats["result"])

    # Binary sklearn stores ONE coef row — the log-odds of the positive class,
    # which is classes_[1] ('H'). A positive coef pushes probability toward a
    # home win. (net_rating_diff / elo_diff / rest_diff / b2b_diff read with the
    # expected sign; form_diff comes out slightly negative because, once Elo and
    # net rating already capture strength, a team on a hot win-streak relative to
    # its efficiency tends to regress — not a bug.)
    print(f"\nClass order: {list(final_model.classes_)} (coef row is log-odds of "
          f"'{final_model.classes_[1]}', a home win)")
    print(f"Feature order: {FEATURE_NAMES}")
    print(f"  coefs={dict(zip(FEATURE_NAMES, final_model.coef_[0].round(4)))}, "
          f"intercept={final_model.intercept_[0]:.4f}")

    weights = {
        "league": "NBA",
        "classes": list(final_model.classes_),
        "feature_names": FEATURE_NAMES,
        "coef": final_model.coef_.tolist(),
        "intercept": final_model.intercept_.tolist(),
        "final_state": final_state,
        "trained_on_games": len(feats),
        "test_seasons": test_seasons,
    }
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2)
    print(f"\nSaved to {WEIGHTS_PATH}")
