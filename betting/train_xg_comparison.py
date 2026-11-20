"""
Head-to-head test: does adding Understat xG features actually improve ROI,
on the exact same held-out matches, holding everything else constant?

Understat only covers 2014-15 onward, so this restricts to that subset for
BOTH the baseline and the xG-enhanced model — an apples-to-apples
comparison, not a "different, larger dataset got better results" artifact.

Usage:
    py train_xg_comparison.py
"""

import numpy as np
from sklearn.metrics import accuracy_score, log_loss
from xgboost import XGBClassifier

from club_features import FEATURE_NAMES
from db import fetch_matches
from train_xgboost_model import EDGE_THRESHOLDS, backtest_roi

LEAGUE = "premier_league"
XG_FEATURES = ["xg_for_diff", "xg_against_diff", "xg_overperformance_diff"]
TEST_FRACTION = 0.15


def report(name, model, X_test, y_test, class_order, test_rows):
    probs = model.predict_proba(X_test)
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
    rows = [r for r in all_rows if r.get("xg_for_diff") is not None]
    print(f"{len(rows)} matches have xG data (Understat coverage: 2014-15 onward).")

    split = int(len(rows) * (1 - TEST_FRACTION))
    train, test = rows[:split], rows[split:]
    print(f"Train: {len(train)}, Test: {len(test)} (chronological)")

    y_train_raw = [r["result"] for r in train]
    y_test_raw = [r["result"] for r in test]
    class_order = sorted(set(y_train_raw))
    label_to_idx = {c: i for i, c in enumerate(class_order)}
    y_train = [label_to_idx[c] for c in y_train_raw]
    y_test = [label_to_idx[c] for c in y_test_raw]

    def make_model():
        return XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                              objective="multi:softprob", num_class=3, eval_metric="mlogloss")

    # baseline: same features as before, same subset of matches
    X_train_base = np.array([[r[f] for f in FEATURE_NAMES] for r in train])
    X_test_base = np.array([[r[f] for f in FEATURE_NAMES] for r in test])
    base_model = make_model()
    base_model.fit(X_train_base, y_train)
    report("Baseline (Elo/H2H/form only, 2014-25 subset)", base_model, X_test_base, y_test, class_order, test)

    # xG-enhanced: baseline features + xg_for_diff, xg_against_diff, xg_overperformance_diff
    xg_feature_names = FEATURE_NAMES + XG_FEATURES
    X_train_xg = np.array([[r[f] for f in xg_feature_names] for r in train])
    X_test_xg = np.array([[r[f] for f in xg_feature_names] for r in test])
    xg_model = make_model()
    xg_model.fit(X_train_xg, y_train)
    report("Baseline + xG features", xg_model, X_test_xg, y_test, class_order, test)

    importances = dict(zip(xg_feature_names, xg_model.feature_importances_.round(3)))
    print(f"\nFeature importances (xG-enhanced model): {importances}")
