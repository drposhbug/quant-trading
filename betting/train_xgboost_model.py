"""
Model upgrades pass: feature interactions (club_features.py), LightGBM +
an XGBoost/LightGBM/NN ensemble, isotonic probability calibration, and a
finer bet-threshold sweep — testing whether these techniques surface real
edge that the plain XGBoost model didn't find.

Worth being honest about going in: the earlier plain-XGBoost backtest
already showed reasonable calibration and no edge at any threshold, which
is the harder problem to fix with "a better algorithm." These techniques
squeeze more out of the SAME feature set — they don't invent new
information. If the underlying features genuinely don't contain
information the market hasn't priced in, no architecture change will
manufacture an edge. Still worth verifying properly rather than assuming.

Backtest methodology (against real historical bookmaker odds, de-vigged to
a fair implied probability):
  1. Split chronologically into train / calibration / test (three-way, not
     two — probability calibration needs its own held-out slice, or
     "calibrating" a model on data it was trained on just tells you it's
     confident, not that it's right).
  2. Fit XGBoost and LightGBM on train.
  3. Calibrate each with isotonic regression fit on the calibration slice.
  4. Build a simple average-probability ensemble of the two calibrated
     models, plus a small neural net (sklearn's MLPClassifier) trained
     directly for comparison.
  5. Backtest ROI for every model at edge thresholds from 3% to 20%.

Run ingest_premier_league.py first to populate the database.

Usage:
    py train_xgboost_model.py
"""

import json
import os

import numpy as np
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import accuracy_score, log_loss
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

from club_features import FEATURE_NAMES
from db import fetch_matches

LEAGUE = "premier_league"
TEST_FRACTION = 0.15
CALIB_FRACTION = 0.15
EDGE_THRESHOLDS = (0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20)
WEIGHTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xgboost_model_premier_league.json")


def implied_probs(odds_home, odds_draw, odds_away):
    raw = np.array([1.0 / odds_home, 1.0 / odds_draw, 1.0 / odds_away])
    overround = raw.sum()  # > 1.0 — the bookmaker's built-in edge
    return raw / overround  # normalized to a fair (no-edge) probability


def backtest_roi(probs_by_class, test_rows, class_order, edge_threshold):
    staked, returned, bets_placed = 0.0, 0.0, 0
    for row, model_probs in zip(test_rows, probs_by_class):
        if not (row["odds_home"] and row["odds_draw"] and row["odds_away"]):
            continue
        market = dict(zip(["H", "D", "A"], implied_probs(row["odds_home"], row["odds_draw"], row["odds_away"])))
        model_p = dict(zip(class_order, model_probs))
        odds_map = {"H": row["odds_home"], "D": row["odds_draw"], "A": row["odds_away"]}

        for outcome in ("H", "D", "A"):
            edge = model_p[outcome] - market[outcome]
            if edge > edge_threshold:
                staked += 1.0
                bets_placed += 1
                if row["result"] == outcome:
                    returned += odds_map[outcome]

    roi = (returned - staked) / staked if staked else None
    return {"bets_placed": bets_placed, "staked": staked, "returned": returned, "roi": roi}


def report_model(name, probs, y_test, class_order, test_rows):
    preds = probs.argmax(axis=1)
    print(f"\n--- {name} ---")
    print(f"Accuracy: {accuracy_score(y_test, preds):.3f}  |  "
          f"Log loss: {log_loss(y_test, probs, labels=list(range(3))):.3f}")
    for threshold in EDGE_THRESHOLDS:
        result = backtest_roi(probs, test_rows, class_order, threshold)
        roi_str = f"{result['roi']:+.1%}" if result["roi"] is not None else "n/a"
        print(f"  edge > {threshold:>4.0%}: {result['bets_placed']:4d} bets, "
              f"staked ${result['staked']:7.2f}, ROI {roi_str}")


if __name__ == "__main__":
    all_rows = fetch_matches(LEAGUE)
    print(f"Loaded {len(all_rows)} matches from the database.")

    n = len(all_rows)
    test_split = int(n * (1 - TEST_FRACTION))
    calib_split = int(test_split * (1 - CALIB_FRACTION))
    train, calib, test = all_rows[:calib_split], all_rows[calib_split:test_split], all_rows[test_split:]
    print(f"Train: {len(train)}, Calibration: {len(calib)}, Test: {len(test)} (all chronological, no shuffling)")

    def Xy(rows):
        X = np.array([[r[f] for f in FEATURE_NAMES] for r in rows])
        y_raw = [r["result"] for r in rows]
        return X, y_raw

    X_train, y_train_raw = Xy(train)
    X_calib, y_calib_raw = Xy(calib)
    X_test, y_test_raw = Xy(test)

    class_order = sorted(set(y_train_raw))
    label_to_idx = {c: i for i, c in enumerate(class_order)}
    y_train = [label_to_idx[c] for c in y_train_raw]
    y_calib = [label_to_idx[c] for c in y_calib_raw]
    y_test = [label_to_idx[c] for c in y_test_raw]

    xgb = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                         objective="multi:softprob", num_class=3, eval_metric="mlogloss")
    xgb.fit(X_train, y_train)

    lgbm = LGBMClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                           objective="multiclass", num_class=3, verbosity=-1)
    lgbm.fit(X_train, y_train)

    mlp = MLPClassifier(hidden_layer_sizes=(16,), max_iter=2000, random_state=0)
    mlp.fit(X_train, y_train)

    xgb_cal = CalibratedClassifierCV(FrozenEstimator(xgb), method="isotonic")
    xgb_cal.fit(X_calib, y_calib)

    lgbm_cal = CalibratedClassifierCV(FrozenEstimator(lgbm), method="isotonic")
    lgbm_cal.fit(X_calib, y_calib)

    probs_xgb = xgb.predict_proba(X_test)
    probs_lgbm = lgbm.predict_proba(X_test)
    probs_mlp = mlp.predict_proba(X_test)
    probs_xgb_cal = xgb_cal.predict_proba(X_test)
    probs_lgbm_cal = lgbm_cal.predict_proba(X_test)
    probs_ensemble = (probs_xgb_cal + probs_lgbm_cal) / 2.0

    report_model("XGBoost (uncalibrated)", probs_xgb, y_test, class_order, test)
    report_model("LightGBM (uncalibrated)", probs_lgbm, y_test, class_order, test)
    report_model("Neural net (sklearn MLP)", probs_mlp, y_test, class_order, test)
    report_model("XGBoost (isotonic-calibrated)", probs_xgb_cal, y_test, class_order, test)
    report_model("LightGBM (isotonic-calibrated)", probs_lgbm_cal, y_test, class_order, test)
    report_model("Ensemble (avg of calibrated XGBoost + LightGBM)", probs_ensemble, y_test, class_order, test)

    xgb.save_model(WEIGHTS_PATH)
    with open(WEIGHTS_PATH + ".meta.json", "w", encoding="utf-8") as f:
        json.dump({"feature_names": FEATURE_NAMES, "class_order": class_order}, f, indent=2)
    print(f"\nSaved base XGBoost model to {WEIGHTS_PATH} (the calibrated/ensemble variants are backtest-only here)")
