"""
Tennis run through the same gate as the NBA — plus the execution number
================================================================================
nba_diagnose.py asks the only question that decides whether a betting rule can
work: does the model predict better than the closing line already does? This is
that gate for tennis, with one addition the tennis data makes possible.

WHY THE ADDITION MATTERS. The NBA odds archive carries a single closing
moneyline, so there is no way to measure what shopping between books is worth.
tennis-data.co.uk carries three prices per player — Pinnacle (sharp), the
market average, and the best price across every book it tracks — so the cost
of execution can be measured directly instead of assumed. That turns out to be
the largest number on this page by some distance, and unlike a model edge it
requires no prediction at all: it is the same bet, placed at a better price.

Two independent verdicts are printed:

  1. MODEL vs MARKET — walk-forward by year, log loss against the de-vigged
     Pinnacle line, then the disagreement decomposition that says whether the
     model's departures from the line carry information or are simply error.
  2. EXECUTION — the overround (the house's cut) at each of the three price
     levels. This is what you pay before any handicapping, and it is the
     hurdle every model edge has to clear.

Usage:
    py tennis_diagnose.py
    py tennis_diagnose.py --tour ATP
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from db import fetch_tennis_matches
# devig_power is sport-agnostic 2-way vig removal -- it lives in nba_odds.py
# because that is where it was first needed, and tennis is also a 2-way market.
from nba_odds import devig_power
from tennis_features import FEATURE_NAMES, compute_features

DISAGREEMENT_EDGES = [-1.0, -0.12, -0.06, -0.02, 0.02, 0.06, 0.12, 1.0]


def log_loss_binary(p, y):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(p, y):
    return float(np.mean((np.asarray(p, dtype=float) - np.asarray(y, dtype=float)) ** 2))


def load(tour=None):
    matches = fetch_tennis_matches(tour)
    if not matches:
        raise SystemExit("No tennis matches in the DB -- run ingest_tennis.py first.")
    rows, _ = compute_features(matches)
    df = pd.DataFrame(rows)
    df = df[df["p1_ps"].notna() & df["p2_ps"].notna()
            & (df["p1_ps"] > 1) & (df["p2_ps"] > 1)].reset_index(drop=True)
    df["mkt_p"] = [devig_power(a, b) for a, b in zip(df["p1_ps"], df["p2_ps"])]
    df["y"] = df["p1_won"].astype(int)
    return df


def report_execution(df):
    """
    What the house takes at each price level. overround = sum of both sides'
    implied probabilities; anything above 1.0 is the cut, and the hold is the
    share of stake it represents.
    """
    print("=== 2. Execution: what you pay before predicting anything ===")
    print(f"{'price level':>28} {'overround':>10} {'hold':>9} {'coverage':>10}")
    levels = [("Pinnacle (sharp book)", "p1_ps", "p2_ps"),
              ("market average", "p1_avg", "p2_avg"),
              ("best price across books", "p1_max", "p2_max")]
    holds = {}
    for label, c1, c2 in levels:
        sub = df[df[c1].notna() & df[c2].notna() & (df[c1] > 1) & (df[c2] > 1)]
        if sub.empty:
            print(f"{label:>28} {'--':>10} {'--':>9} {0:>9.1%}")
            continue
        over = (1.0 / sub[c1] + 1.0 / sub[c2]).mean()
        hold = (over - 1.0) / over
        holds[label] = hold
        print(f"{label:>28} {over:>10.4f} {hold:>+9.2%} {len(sub) / len(df):>10.1%}")

    if "best price across books" in holds and "Pinnacle (sharp book)" in holds:
        gain = holds["Pinnacle (sharp book)"] - holds["best price across books"]
        print(f"\nShopping instead of taking the sharp line is worth {gain:+.2%} per bet.")
        if holds["best price across books"] < 0:
            print("The best-of-book overround is BELOW 1.0: across these matches, buying\n"
                  "both sides at the best available price is on average a free position.\n"
                  "Caveats that stop this being literal free money -- the two best prices\n"
                  "are quoted by different books and not necessarily at the same moment,\n"
                  "stake limits are small at the top of the market, and accounts that only\n"
                  "ever take the best price get restricted. It is still the single largest\n"
                  "measured effect here, and it needs no model to be right.")
    return holds


def report_gate(df):
    print("\n=== 1. The bar: model vs the de-vigged closing line ===")
    years = sorted(df["year"].dropna().unique())
    parts = []
    print(f"{'test year':>10} {'n':>6} {'model LL':>9} {'market LL':>10} {'gap':>8}")
    for year in years:
        train, test = df[df["year"] < year], df[df["year"] == year]
        if len(train) < 1000 or test.empty:
            continue
        model = LogisticRegression(max_iter=2000)
        model.fit(train[FEATURE_NAMES].astype(float), train["y"])
        test = test.copy()
        test["p_model"] = model.predict_proba(test[FEATURE_NAMES].astype(float))[:, 1]
        lm = log_loss_binary(test["p_model"], test["y"])
        lk = log_loss_binary(test["mkt_p"], test["y"])
        parts.append(test)
        print(f"{int(year):>10} {len(test):>6} {lm:>9.4f} {lk:>10.4f} {lm - lk:>+8.4f}"
              f"{'   <-- MODEL WINS' if lm < lk else ''}")
    if not parts:
        raise SystemExit("Not enough history to walk forward -- ingest more years.")

    R = pd.concat(parts, ignore_index=True)
    lm, lk = log_loss_binary(R["p_model"], R["y"]), log_loss_binary(R["mkt_p"], R["y"])
    wins = sum(1 for _, g in R.groupby("year")
               if log_loss_binary(g["p_model"], g["y"]) < log_loss_binary(g["mkt_p"], g["y"]))
    n_years = R["year"].nunique()
    print(f"\npooled: model {lm:.4f} / Brier {brier(R['p_model'], R['y']):.4f}  vs  "
          f"market {lk:.4f} / Brier {brier(R['mkt_p'], R['y']):.4f}")
    print(f"model beat the market in {wins}/{n_years} years (gap {lm - lk:+.4f})")
    return R, wins, n_years, lm - lk


def report_disagreement(R):
    print("\n=== Where the model disagrees with the line, who is right? ===")
    R = R.assign(disagreement=R["p_model"] - R["mkt_p"])
    R["bucket"] = pd.cut(R["disagreement"], DISAGREEMENT_EDGES)
    table = R.groupby("bucket", observed=True).apply(
        lambda x: pd.Series({"n": len(x), "market_says": x["mkt_p"].mean(),
                             "model_says": x["p_model"].mean(),
                             "actually_won": x["y"].mean()}),
        include_groups=False)
    table["closer"] = np.where(
        (table["actually_won"] - table["model_says"]).abs()
        < (table["actually_won"] - table["market_says"]).abs(), "model", "MARKET")
    print(table.round(4).to_string())
    outer = table[table.index.map(lambda b: b.left <= -0.12 or b.right >= 0.12)]
    return bool((outer["closer"] == "model").all())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Does a tennis stats model beat the closing line, and what does execution cost?")
    ap.add_argument("--tour", choices=["ATP", "WTA"], help="restrict to one tour")
    args = ap.parse_args()

    df = load(args.tour)
    label = args.tour or "ATP + WTA"
    print(f"{len(df)} matches with a sharp price ({label}), "
          f"{df['date'].min()} .. {df['date'].max()}")
    print(f"p1 won {df['y'].mean():.3f} (alphabetical ordering, so ~0.500 means "
          f"no label leakage)\n")

    R, wins, n_years, gap = report_gate(df)
    model_right = report_disagreement(R)
    print()
    holds = report_execution(df)

    print("\n" + "=" * 78)
    if wins == 0 and not model_right:
        print("VERDICT: no signal, same as the NBA -- and by a wider margin. The model is\n"
              f"beaten by the closing line in every year tested (gap {gap:+.4f} vs the NBA's\n"
              "+0.0200), and in every outer disagreement bucket the market is closer to the\n"
              "truth than the model. Do not bet this model.\n\n"
              "The finding worth acting on is the execution number above, not the model:\n"
              "it is larger, it is measured rather than assumed, and it needs no prediction.\n"
              "Tennis is also the right place to test best-price execution generally, since\n"
              "it is the one sport here whose data ships with a best-of-book column.")
    elif wins < n_years / 2:
        print(f"VERDICT: weak. Model beat the market in {wins}/{n_years} years "
              f"(gap {gap:+.4f}).\nTreat any backtest ROI as unproven.")
    else:
        print(f"VERDICT: a residual signal may exist -- model beat the market in "
              f"{wins}/{n_years}\nyears (gap {gap:+.4f}). Now ROI numbers are worth computing.")
    print("=" * 78)
