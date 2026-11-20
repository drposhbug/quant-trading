"""
Market-anchored model: predicts the RESIDUAL, not the match from scratch
================================================================================
Every trainer so far builds probabilities from public stats (Elo, form,
H2H, xG) and then compares them to the bookmaker line. That framing asks
the model to independently out-predict a market that already prices in all
of those signals — which the backtests correctly showed it can't.

This flips the framing: the de-vigged market probabilities go IN as
features, alongside the stats. The model's job shrinks from "predict the
match" to "learn the small, systematic ways the closing line is off" —
e.g. draw pricing, or slow incorporation of shot/xG form. If nothing
systematic exists, the model converges to just echoing the market, edges
never exceed the threshold, and the backtest honestly places ~no bets.
That non-result is itself informative: it says the residual is flat, not
that the code failed.

Two evaluation fixes over train_xgboost_model.py, both about not fooling
ourselves:

  1. NO THRESHOLD SWEEPING ON THE TEST SET. Sweeping seven thresholds and
     quoting the best one is multiple testing — with ~250 bets per cell,
     one cell will look great by chance. Here the edge threshold for test
     season N is selected on season N-1 (the last training season), then
     applied to season N exactly once. What gets pooled and reported is
     only the pre-registered bets.
  2. WALK-FORWARD + BOOTSTRAP by default (same machinery as
     walk_forward_backtest.py), because a single chronological split is
     one lucky/unlucky window.

Also reported: log loss of the market itself on each test season. This is
the number to watch before any ROI — if the model (which SEES the market)
can't beat the market's own log loss, there is no residual signal and no
betting rule will save it.

Missing values (xG before 2014, shots before ~2000) are passed to XGBoost
as NaN — it routes missing values natively, so early-season rows still
contribute their Elo/form/market information instead of being dropped.

Run ingest_premier_league.py (updated to include shot stats) and
ingest_understat_xg.py first.

Usage:
    py train_market_model.py
    py train_market_model.py --min-train-seasons 5
"""

import argparse

import numpy as np
from xgboost import XGBClassifier

from club_features import FEATURE_NAMES
from db import fetch_matches
from train_xgboost_model import implied_probs

LEAGUE = "premier_league"
XG_FEATURES = ["xg_for_diff", "xg_against_diff", "xg_overperformance_diff"]
SHOT_FEATURES = ["shots_for_diff", "sot_for_diff", "sot_against_diff"]
MARKET_FEATURES = ["mkt_p_home", "mkt_p_draw", "mkt_p_away", "mkt_logit_home_away"]
STATS_FEATURES = FEATURE_NAMES + XG_FEATURES + SHOT_FEATURES
ALL_FEATURES = STATS_FEATURES + MARKET_FEATURES

CLASSES = ["A", "D", "H"]
CANDIDATE_THRESHOLDS = (0.02, 0.03, 0.04, 0.05, 0.08)
MIN_VALIDATION_BETS = 15   # below this, a threshold's validation ROI is noise — skip it
N_BOOTSTRAP = 10_000
CI_LEVEL = 0.90


def season_sort_key(season):
    """'9394' -> 1993, '0001' -> 2000 — plain string sort puts the 90s last."""
    y = int(str(season)[:2])
    return 1900 + y if y >= 93 else 2000 + y


def add_market_features(rows):
    for r in rows:
        p_h, p_d, p_a = implied_probs(r["odds_home"], r["odds_draw"], r["odds_away"])
        r["mkt_p_home"], r["mkt_p_draw"], r["mkt_p_away"] = p_h, p_d, p_a
        # log-odds of home vs away — gives the trees a scale where a move
        # from 0.80->0.85 counts for more than 0.50->0.55, matching how
        # odds actually behave
        r["mkt_logit_home_away"] = float(np.log(p_h / p_a))
    return rows


def feature_matrix(rows, feature_names):
    def val(r, f):
        v = r.get(f)
        return np.nan if v is None else float(v)
    return np.array([[val(r, f) for f in feature_names] for r in rows])


def fit_predict(train_rows, test_rows, feature_names):
    model = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05,
                          objective="multi:softprob", num_class=3, eval_metric="mlogloss")
    model.fit(feature_matrix(train_rows, feature_names),
              [CLASSES.index(r["result"]) for r in train_rows])
    return model, model.predict_proba(feature_matrix(test_rows, feature_names))


def log_loss_vs_market(rows, probs):
    """(model log loss, market log loss) on the same rows."""
    idx = [CLASSES.index(r["result"]) for r in rows]
    model_ll = -np.mean(np.log(np.clip(probs[np.arange(len(rows)), idx], 1e-12, 1.0)))
    mkt = {"H": "mkt_p_home", "D": "mkt_p_draw", "A": "mkt_p_away"}
    market_ll = -np.mean([np.log(max(r[mkt[r["result"]]], 1e-12)) for r in rows])
    return model_ll, market_ll


def collect_bet_returns(probs, rows, threshold, best_price=False):
    """
    Per-bet $1 flat-stake P/L for the 'bet when model - market > threshold'
    rule. Edge detection is always vs the de-vigged AVERAGE line (the
    market consensus); best_price=True pays winners at the best price any
    tracked book offered (odds_max_*, falling back to average when the
    column is missing) — the payout a line-shopping bettor actually gets.
    """
    max_key = {"H": "odds_max_home", "D": "odds_max_draw", "A": "odds_max_away"}
    returns = []
    for row, model_probs in zip(rows, probs):
        model_p = dict(zip(CLASSES, model_probs))
        market = {"H": row["mkt_p_home"], "D": row["mkt_p_draw"], "A": row["mkt_p_away"]}
        odds_map = {"H": row["odds_home"], "D": row["odds_draw"], "A": row["odds_away"]}
        for outcome in ("H", "D", "A"):
            if model_p[outcome] - market[outcome] > threshold:
                payout_odds = odds_map[outcome]
                if best_price and row.get(max_key[outcome]):
                    payout_odds = row[max_key[outcome]]
                returns.append(payout_odds - 1.0 if row["result"] == outcome else -1.0)
    return returns


def select_threshold(probs_valid, valid_rows):
    """
    Pick the threshold on the VALIDATION season (last training season) —
    never on the test season. Falls back to the most conservative candidate
    if nothing clears MIN_VALIDATION_BETS with positive ROI.
    """
    best_t, best_roi = None, 0.0
    for t in CANDIDATE_THRESHOLDS:
        rets = collect_bet_returns(probs_valid, valid_rows, t)
        if len(rets) < MIN_VALIDATION_BETS:
            continue
        roi = float(np.mean(rets))
        if roi > best_roi:
            best_t, best_roi = t, roi
    return best_t, best_roi  # best_t is None => validation says "don't bet this season"


def bootstrap_ci(returns, n=N_BOOTSTRAP, level=CI_LEVEL, seed=0):
    arr = np.asarray(returns, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array([arr[rng.integers(0, len(arr), len(arr))].mean() for _ in range(n)])
    lo, hi = np.percentile(means, [(1 - level) / 2 * 100, (1 + level) / 2 * 100])
    return lo, hi, float((means > 0).mean())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Walk-forward backtest of the market-anchored model.")
    parser.add_argument("--min-train-seasons", type=int, default=5)
    args = parser.parse_args()

    all_rows = fetch_matches(LEAGUE)
    rows = [r for r in all_rows if r["odds_home"] and r["odds_draw"] and r["odds_away"]]
    rows = add_market_features(rows)
    seasons = sorted({r["season"] for r in rows}, key=season_sort_key)
    print(f"{len(rows)}/{len(all_rows)} matches have bookmaker odds, "
          f"seasons {seasons[0]}..{seasons[-1]}")

    by_season = {s: [r for r in rows if r["season"] == s] for s in seasons}
    pooled_returns, pooled_best_price, pooled_stats_only = [], [], []
    ll_model_all, ll_market_all = [], []

    print(f"\n{'season':>7} | {'n':>4} | {'model LL':>8} | {'mkt LL':>7} | "
          f"{'thresh':>6} | {'bets':>4} | {'season ROI':>10}")
    print("-" * 68)

    for i, season in enumerate(seasons):
        if i < args.min_train_seasons:
            continue
        train_seasons = seasons[:i]
        valid_season = train_seasons[-1]
        fit_seasons = train_seasons[:-1]

        fit_rows = [r for s in fit_seasons for r in by_season[s]]
        valid_rows = by_season[valid_season]
        test_rows = by_season[season]
        if len(test_rows) < 30:
            print(f"{season:>7} | {len(test_rows):>4} | skipped (partial season)")
            continue

        # threshold selection: model fit WITHOUT the validation season, applied to it
        _, probs_valid = fit_predict(fit_rows, valid_rows, ALL_FEATURES)
        threshold, _ = select_threshold(probs_valid, valid_rows)

        # final model for this window: fit on ALL training seasons (incl. validation)
        _, probs_test = fit_predict(fit_rows + valid_rows, test_rows, ALL_FEATURES)
        ll_m, ll_k = log_loss_vs_market(test_rows, probs_test)
        ll_model_all.append(ll_m)
        ll_market_all.append(ll_k)

        # stats-only comparison line (the old framing), same windows
        _, probs_stats = fit_predict(fit_rows + valid_rows, test_rows, STATS_FEATURES)

        if threshold is None:
            print(f"{season:>7} | {len(test_rows):>4} | {ll_m:8.4f} | {ll_k:7.4f} | "
                  f"{'--':>6} |    0 |  no bet (validation ROI <= 0)")
            continue

        rets = collect_bet_returns(probs_test, test_rows, threshold)
        pooled_returns += rets
        pooled_best_price += collect_bet_returns(probs_test, test_rows, threshold, best_price=True)
        pooled_stats_only += collect_bet_returns(probs_stats, test_rows, threshold)
        roi_str = f"{np.mean(rets):+9.1%}" if rets else "   no bets"
        print(f"{season:>7} | {len(test_rows):>4} | {ll_m:8.4f} | {ll_k:7.4f} | "
              f"{threshold:>5.0%} | {len(rets):>4} | {roi_str}")

    print("\n=== The number that matters first: log loss vs the market ===")
    print(f"Model (sees market + stats): {np.mean(ll_model_all):.4f} avg across test seasons")
    print(f"Market alone:                {np.mean(ll_market_all):.4f}")
    if np.mean(ll_model_all) >= np.mean(ll_market_all):
        print("Model does NOT beat the market's own log loss -> no residual signal in these\n"
              "features. Any positive ROI below is variance; do not bet it. Add information\n"
              "(lineups/injuries, line movement) rather than architecture.")
    else:
        print("Model beats the market's log loss -> a residual signal exists. Now the ROI\n"
              "numbers below are worth reading.")

    print(f"\n=== Pooled pre-registered bets (thresholds chosen on validation only) ===")
    for label, rets in (("market-anchored (avg odds)", pooled_returns),
                         ("market-anchored (best price)", pooled_best_price),
                         ("stats-only (same thresholds)", pooled_stats_only)):
        if not rets:
            print(f"  {label}: no bets placed across all windows")
            continue
        lo, hi, p_pos = bootstrap_ci(rets)
        print(f"  {label:>28}: {len(rets):4d} bets, ROI {np.mean(rets):+.1%}, "
              f"{CI_LEVEL:.0%} CI [{lo:+.1%}, {hi:+.1%}], P(ROI>0) = {p_pos:.0%}")

    print(
        "\nReminder: these backtests use closing AVERAGE odds. Live, you'd bet earlier\n"
        "lines and shop for best-of-book, both of which help you — but you'd also pay\n"
        "limits and account restrictions, which hurt. CLV from the Polymarket price\n"
        "logger remains the faster, cleaner verdict on whether an edge is real."
    )
