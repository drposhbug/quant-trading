"""
Two zero-cost stress-tests of the +9.4% xG backtest result — run these
BEFORE trusting it with money, because on 241 bets the standard error on
ROI is roughly +/-9-10%, meaning a single +9.4% window is ~1 sigma from
zero and entirely compatible with no edge.

1. Walk-forward validation — instead of one chronological split (one test
   window that could just be a lucky stretch of fixtures), roll season by
   season: train on every xG-covered match BEFORE season N, test on season
   N, for every season with enough prior history. A real edge shows up in
   most windows; a lucky one shows up in one window and vanishes in the
   rest.

2. Bootstrap confidence interval — pool the individual bet outcomes across
   all walk-forward windows and resample them 10,000 times to put an
   honest interval around the ROI instead of a single point estimate.

Run ingest_premier_league.py and ingest_understat_xg.py first.

Usage:
    py walk_forward_backtest.py
"""

import numpy as np
from xgboost import XGBClassifier

from club_features import FEATURE_NAMES
from db import fetch_matches
from train_xgboost_model import implied_probs

LEAGUE = "premier_league"
XG_FEATURES = ["xg_for_diff", "xg_against_diff", "xg_overperformance_diff"]
ALL_FEATURES = FEATURE_NAMES + XG_FEATURES
MIN_TRAIN_SEASONS = 3          # first test season needs this many prior xG seasons
EDGE_THRESHOLDS = (0.05, 0.08)  # the two thresholds worth watching from earlier runs
N_BOOTSTRAP = 10_000
CI_LEVEL = 0.90
CLASSES = ["A", "D", "H"]       # fixed label order


def make_model():
    # identical hyperparameters to train_xgboost_model.py / train_xg_comparison.py
    return XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                         objective="multi:softprob", num_class=3, eval_metric="mlogloss")


def fit_predict(train_rows, test_rows, feature_names):
    X_train = np.array([[r[f] for f in feature_names] for r in train_rows])
    y_train = [CLASSES.index(r["result"]) for r in train_rows]
    X_test = np.array([[r[f] for f in feature_names] for r in test_rows])
    model = make_model()
    model.fit(X_train, y_train)
    return model.predict_proba(X_test)


def collect_bet_returns(probs, rows, threshold):
    """
    Same betting rule as backtest_roi in train_xgboost_model.py, but returns
    the per-bet profit/loss list (flat $1 stakes) instead of just the
    aggregate — the bootstrap needs the individual outcomes.
    """
    returns = []
    for row, model_probs in zip(rows, probs):
        if not (row["odds_home"] and row["odds_draw"] and row["odds_away"]):
            continue
        market = dict(zip(["H", "D", "A"],
                          implied_probs(row["odds_home"], row["odds_draw"], row["odds_away"])))
        model_p = dict(zip(CLASSES, model_probs))
        odds_map = {"H": row["odds_home"], "D": row["odds_draw"], "A": row["odds_away"]}
        for outcome in ("H", "D", "A"):
            if model_p[outcome] - market[outcome] > threshold:
                won = row["result"] == outcome
                returns.append(odds_map[outcome] - 1.0 if won else -1.0)
    return returns


def bootstrap_ci(returns, n=N_BOOTSTRAP, level=CI_LEVEL, seed=0):
    arr = np.asarray(returns, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.empty(n)
    for i in range(n):
        means[i] = arr[rng.integers(0, len(arr), len(arr))].mean()
    lo, hi = np.percentile(means, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return lo, hi, (means > 0).mean()


if __name__ == "__main__":
    all_rows = fetch_matches(LEAGUE)
    rows = [r for r in all_rows if r.get("xg_for_diff") is not None]
    seasons = sorted({r["season"] for r in rows})
    print(f"{len(rows)} xG-covered matches across seasons {seasons[0]}..{seasons[-1]}")

    test_seasons = seasons[MIN_TRAIN_SEASONS:]
    pooled = {t: {"baseline": [], "xg": []} for t in EDGE_THRESHOLDS}
    window_roi = {t: {"baseline": [], "xg": []} for t in EDGE_THRESHOLDS}

    header = f"{'season':>7} | {'test n':>6} |"
    for t in EDGE_THRESHOLDS:
        header += f"  base@{t:.0%} (bets) |    xG@{t:.0%} (bets) |"
    print("\n" + header)
    print("-" * len(header))

    for season in test_seasons:
        train = [r for r in rows if r["season"] < season]
        test = [r for r in rows if r["season"] == season]
        if len(test) < 30:
            print(f"{season:>7} | {len(test):>6} | skipped (too few matches — partial season)")
            continue

        probs_base = fit_predict(train, test, FEATURE_NAMES)
        probs_xg = fit_predict(train, test, ALL_FEATURES)

        line = f"{season:>7} | {len(test):>6} |"
        for t in EDGE_THRESHOLDS:
            r_base = collect_bet_returns(probs_base, test, t)
            r_xg = collect_bet_returns(probs_xg, test, t)
            pooled[t]["baseline"] += r_base
            pooled[t]["xg"] += r_xg
            roi_b = np.mean(r_base) if r_base else float("nan")
            roi_x = np.mean(r_xg) if r_xg else float("nan")
            window_roi[t]["baseline"].append(roi_b)
            window_roi[t]["xg"].append(roi_x)
            line += f"  {roi_b:+8.1%} ({len(r_base):>3}) |  {roi_x:+8.1%} ({len(r_xg):>3}) |"
        print(line)

    print("\n=== Walk-forward summary ===")
    for t in EDGE_THRESHOLDS:
        rois = [r for r in window_roi[t]["xg"] if not np.isnan(r)]
        pos = sum(1 for r in rois if r > 0)
        print(f"\nedge > {t:.0%}: xG model positive in {pos}/{len(rois)} season windows")
        for label in ("baseline", "xg"):
            rets = pooled[t][label]
            if not rets:
                continue
            roi = np.mean(rets)
            lo, hi, p_pos = bootstrap_ci(rets)
            print(f"  {label:>8}: {len(rets):4d} pooled bets, ROI {roi:+.1%}, "
                  f"{CI_LEVEL:.0%} CI [{lo:+.1%}, {hi:+.1%}], "
                  f"P(ROI>0) = {p_pos:.0%}")

    print(
        "\nHow to read this:\n"
        "  - Real edge: xG positive in most windows AND the pooled CI mostly above 0\n"
        "    (P(ROI>0) >= ~90%). Then the external-factors spend is justified.\n"
        "  - Lucky window: one big positive season carrying everything, CI straddling\n"
        "    zero. Then the +9.4% was variance — don't bet it, keep improving features.\n"
        "  - In between: keep the bet log running on paper while you add shot-stat\n"
        "    features (HS/HST) and re-test."
    )
