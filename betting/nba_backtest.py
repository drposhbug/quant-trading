"""
Walk-forward BETTING backtest for the NBA model — the "does it actually make
money" test, not just "does it predict winners" (that's the held-out accuracy
in train_nba_model.py).

Method, matching walk_forward_backtest.py's discipline for soccer:

  * Expanding window. For each test season S, the model is fit ONLY on games
    from seasons before S, then used to price every game in S. No game is ever
    bet with information from its own season or later — this is the honest
    simulation of trading the model in real time, season after season.
  * Real closing moneylines (nba_odds.py). A bet on a side is placed only when
    the model's probability beats that side's break-even probability (1/decimal
    odds) by more than the edge threshold. Stakes are flat 1 unit, so ROI =
    profit / number of bets is the plain, un-leveraged edge.
  * Bootstrap CI. ROI is resampled over bets to show whether a positive result
    clears zero or is within noise — a good ROI on 40 bets means nothing.

Beating the closing line's break-even is a high bar: closing moneylines are the
sharpest number the market produces, already vig-loaded. A model that clears it
after vig has genuine edge; one that only "wins" at 50-52% accuracy but loses to
the vig does not — and this backtest is designed to tell those two apart.

READ nba_diagnose.py FIRST. ROI over ~700 bets a season is noisy enough that
some threshold in the sweep below will look profitable whether or not any edge
exists (2016-17 prints +7.8%, 2023-24 prints -12.0%, from the same model). The
diagnostic asks the prior question — does the model predict better than the
closing line at all — and as of the 2025-26 data the answer is no, in 0 of 13
seasons. Until that flips, treat every positive cell here as variance.

Usage:
    py nba_backtest.py
    py nba_backtest.py --thresholds 0.02,0.03,0.05 --start-season 2013-14
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from db import fetch_nba_games
from nba_features import FEATURE_NAMES
from nba_odds import american_to_decimal, load_closing_ml, norm_team


def join_odds(games):
    """
    Attach (ml_home, ml_away) to each game dict. Joins on (date, home, away)
    with a +/-1 calendar-day fallback for late tip-offs that the odds archive
    filed under a different date. Returns (joined_games, n_total, n_joined).
    """
    seasons = sorted({g["season"] for g in games})
    ml = load_closing_ml(seasons)
    joined = []
    for g in games:
        nh, na = norm_team(g["home_team"]), norm_team(g["away_team"])
        d = g["date"][:10]
        hit = ml.get((d, nh, na))
        if hit is None:
            # try neighbouring dates
            day = np.datetime64(d)
            for delta in (-1, 1):
                alt = str(day + np.timedelta64(delta, "D"))
                hit = ml.get((alt, nh, na))
                if hit:
                    break
        if hit:
            g = {**g, "ml_home": hit[0], "ml_away": hit[1]}
            joined.append(g)
    return joined, len(games), len(joined)


def walk_forward_bets(df, seasons, start_season, thresholds):
    """
    For each season >= start_season, train on all earlier seasons and price the
    season's games. Returns a dict: threshold -> list of per-bet dicts
    {season, side, profit, won}. profit is flat-stake units (win = decimal-1,
    loss = -1). Also returns per-game model/market accuracy bookkeeping.
    """
    bets = {t: [] for t in thresholds}
    n_correct_model = n_correct_market = n_games = 0

    test_seasons = [s for s in seasons if s >= start_season]
    for S in test_seasons:
        train = df[df["season"] < S]
        test = df[df["season"] == S]
        if len(train) < 500 or test.empty:
            continue

        model = LogisticRegression(max_iter=1000)
        model.fit(train[FEATURE_NAMES].astype(float), train["result"])
        h_idx = list(model.classes_).index("H")
        p_home = model.predict_proba(test[FEATURE_NAMES].astype(float))[:, h_idx]

        for (_, row), p_h in zip(test.iterrows(), p_home):
            p_a = 1.0 - p_h
            d_home = american_to_decimal(row["ml_home"])
            d_away = american_to_decimal(row["ml_away"])
            home_won = row["result"] == "H"

            n_games += 1
            n_correct_model += int((p_h >= 0.5) == home_won)
            # market favorite = lower decimal odds
            n_correct_market += int((d_home < d_away) == home_won)

            for side, p_side, d_side, side_won in (
                    ("home", p_h, d_home, home_won),
                    ("away", p_a, d_away, not home_won)):
                edge = p_side - 1.0 / d_side  # model prob minus break-even prob
                for t in thresholds:
                    if edge > t:
                        profit = (d_side - 1.0) if side_won else -1.0
                        bets[t].append({"season": S, "side": side,
                                        "profit": profit, "won": side_won})
    return bets, (n_correct_model, n_correct_market, n_games)


def roi_ci(profits, n_boot=10000, seed=0):
    """Bootstrap 90% CI for ROI (mean profit per unit staked)."""
    if len(profits) == 0:
        return 0.0, 0.0, 0.0
    rng = np.random.default_rng(seed)
    arr = np.asarray(profits)
    means = arr[rng.integers(0, len(arr), size=(n_boot, len(arr)))].mean(axis=1)
    return arr.mean(), np.percentile(means, 5), np.percentile(means, 95)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Walk-forward betting backtest for the NBA model.")
    ap.add_argument("--thresholds", default="0.02,0.03,0.05,0.08",
                    help="comma-separated edge thresholds (model prob minus break-even)")
    ap.add_argument("--start-season", default="2013-14",
                    help="first season to bet (earlier seasons are training-only burn-in)")
    ap.add_argument("--report-threshold", type=float, default=0.03,
                    help="threshold used for the per-season breakdown")
    args = ap.parse_args()
    thresholds = [float(t) for t in args.thresholds.split(",")]

    games = fetch_nba_games(include_playoffs=True)
    if not games:
        raise SystemExit("No NBA games in the DB — run ingest_nba.py first.")
    joined, n_total, n_joined = join_odds(games)
    print(f"Games in DB: {n_total};  joined to closing moneylines: {n_joined} "
          f"({n_joined / n_total:.1%})")

    df = pd.DataFrame(joined).sort_values(["date"]).reset_index(drop=True)
    seasons = sorted(df["season"].unique())
    print(f"Seasons with odds: {seasons[0]} .. {seasons[-1]}; "
          f"betting from {args.start_season} onward.\n")

    bets, (nc_model, nc_market, n_games) = walk_forward_bets(
        df, seasons, args.start_season, thresholds)

    print("=== Out-of-sample game prediction (walk-forward) ===")
    print(f"{n_games} games priced. Model picked winner {nc_model / n_games:.3f}; "
          f"market favorite won {nc_market / n_games:.3f}.\n")

    # baselines: flat-bet every home team, and every market favorite
    for label, pick_home in (("bet every home team", True),):
        prof = []
        for _, r in df[df["season"] >= args.start_season].iterrows():
            d = american_to_decimal(r["ml_home"] if pick_home else r["ml_away"])
            won = (r["result"] == "H") if pick_home else (r["result"] == "A")
            prof.append((d - 1.0) if won else -1.0)
        print(f"Baseline ({label}): {len(prof)} bets, "
              f"ROI {np.mean(prof):+.3%} (flat stake)")

    print("\n=== Model betting ROI at the closing moneyline (flat 1u stakes) ===")
    print(f"{'edge>':>6} {'bets':>6} {'ROI':>9} {'90% CI':>20} {'units':>9}")
    for t in thresholds:
        profits = [b["profit"] for b in bets[t]]
        roi, lo, hi = roi_ci(profits)
        units = sum(profits)
        print(f"{t:>6.0%} {len(profits):>6d} {roi:>+9.2%} "
              f"[{lo:>+6.2%}, {hi:>+6.2%}]  {units:>+9.1f}")

    rt = args.report_threshold
    print(f"\n=== Per-season ROI at edge > {rt:.0%} ===")
    by_season = {}
    for b in bets.get(rt, []):
        by_season.setdefault(b["season"], []).append(b["profit"])
    for S in sorted(by_season):
        p = by_season[S]
        print(f"  {S}: {len(p):>4d} bets, ROI {np.mean(p):>+7.2%}, units {sum(p):>+6.1f}")
    if not by_season:
        print(f"  (no bets at {rt:.0%} — try a threshold from --thresholds)")
