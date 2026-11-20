"""
Is there any signal here at all? -- the gate that must pass before ROI matters
================================================================================
nba_backtest.py answers "did this rule make money in the backtest". That is the
wrong FIRST question, because with ~700 bets a season a rule can post +8% ROI
for a year on noise alone (2016-17 did; 2023-24 posted -12%). This script asks
the question that actually decides whether any betting rule can work:

    Does the model predict games better than the closing line already does?

If it doesn't, no threshold, no staking plan and no bet filter can produce a
positive expectation -- you would be paying 3.8% vig to place a worse estimate
against a better one. Sweeping thresholds until one looks profitable is just
picking the luckiest cell. This is the same discipline train_market_model.py
applies to soccer, ported to the NBA's 2-way market.

Four checks, walk-forward (train strictly on earlier seasons, price the next):

  1. THE BAR. Log loss / Brier / accuracy of the stats model vs the de-vigged
     closing line on identical games.
  2. DISAGREEMENT DECOMPOSITION. The decisive one. Bucket games by how far the
     model departs from the market, then compare each bucket's actual home-win
     rate against both estimates. Real information means `actual` tracks the
     MODEL in the outer buckets. If it tracks the MARKET instead, every
     disagreement is model error -- and since a bet is placed precisely when the
     model disagrees, every bet is then negative-expectation by construction.
  3. CALIBRATION. Whether the model's stated confidence is honest. An
     overconfident model manufactures edge out of nothing: it pushes
     probabilities away from the base rate, which is exactly what an edge
     threshold is looking for.
  4. SEGMENT SCAN. Whether some niche (early season, playoffs, big dogs, rest
     mismatches) bucks the overall verdict and is worth betting alone.

Findings as of the 2025-26 data (2013-14 onward, 15,226 games priced):

  * The stats model loses to the closing line in 13 of 13 seasons, by a
    remarkably steady ~0.020 nats of log loss.
  * In every disagreement bucket, the actual result tracks the market, not the
    model. The biggest disagreements are the biggest model errors.
  * The model is overconfident throughout (predicts 0.845, wins 0.804).
  * No segment escapes: the ~0.020 gap holds across early/late season,
    playoffs, favorites, underdogs and rest mismatches alike.

Feature work that was tried against this gate and did NOT close it -- recorded
so it isn't repeated: standardizing the features, opponent-adjusted ridge/SRS
team ratings refit weekly, multi-window rolling margin (5/25/season-to-date),
schedule density (games in the last 7 days), and gradient boosting over all of
the above. Best case closed 0.0005 of the 0.0200 gap -- 3%. The missing 0.020 is
not an architecture or tuning problem; it is information the closing line has
and a box score does not: injuries, load management, and lineup news. That is
what nba_injuries.py collects (structured, per player, snapshotted daily) and
what external_factors_agent.py researches qualitatively, and improving THOSE is
the only path that moves this number. Note that nba_injuries.py cannot help
retroactively -- ESPN publishes no archive, so its history starts the day it
first runs; re-run this diagnostic with injury features once a season's worth
of snapshots exists.

Usage:
    py nba_diagnose.py
    py nba_diagnose.py --start-season 2018-19
"""

import argparse

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from db import fetch_nba_games
from nba_backtest import join_odds
from nba_features import FEATURE_NAMES
from nba_odds import american_to_decimal, devig_power

# Buckets for check 2. Deliberately wider than any sane edge threshold at the
# edges so the outer cells hold the bets the backtest would actually place.
DISAGREEMENT_EDGES = [-1.0, -0.12, -0.06, -0.02, 0.02, 0.06, 0.12, 1.0]


def log_loss_binary(p, y):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(p, y):
    return float(np.mean((np.asarray(p, dtype=float) - np.asarray(y, dtype=float)) ** 2))


def load_priced_games():
    """Every game that joined to a closing moneyline, with fair market probs."""
    games = fetch_nba_games(include_playoffs=True)
    if not games:
        raise SystemExit("No NBA games in the DB -- run ingest_nba.py first.")
    joined, n_total, n_joined = join_odds(games)
    df = pd.DataFrame(joined).sort_values(["date", "game_id"]).reset_index(drop=True)
    df["d_home"] = df["ml_home"].map(american_to_decimal)
    df["d_away"] = df["ml_away"].map(american_to_decimal)
    df["mkt_p"] = [devig_power(h, a) for h, a in zip(df["d_home"], df["d_away"])]
    df["overround"] = 1.0 / df["d_home"] + 1.0 / df["d_away"]
    df["y"] = (df["result"] == "H").astype(int)
    df["season_game_no"] = df.groupby("season").cumcount()
    return df, n_total, n_joined


def walk_forward_predict(df, start_season):
    """
    Expanding window: for each season >= start_season, fit on all earlier
    seasons and price that season. Returns the priced test rows with p_model.
    """
    parts = []
    for season in sorted(df["season"].unique()):
        if season < start_season:
            continue
        train = df[df["season"] < season]
        test = df[df["season"] == season]
        if len(train) < 500 or test.empty:
            continue
        model = LogisticRegression(max_iter=1000)
        model.fit(train[FEATURE_NAMES].astype(float), train["y"])
        test = test.copy()
        test["p_model"] = model.predict_proba(test[FEATURE_NAMES].astype(float))[:, 1]
        parts.append(test)
    if not parts:
        raise SystemExit("No season had enough training history -- lower --start-season.")
    return pd.concat(parts, ignore_index=True)


def check_the_bar(R):
    print("=== 1. The bar: model vs the closing line on the same games ===")
    print(f"{'estimator':>22} {'log loss':>10} {'Brier':>9} {'accuracy':>10}")
    for label, col in (("stats model", "p_model"), ("closing line (de-vigged)", "mkt_p")):
        p, y = R[col].values, R["y"].values
        print(f"{label:>22} {log_loss_binary(p, y):>10.4f} {brier(p, y):>9.4f} "
              f"{np.mean((p >= 0.5) == (y == 1)):>10.4f}")

    per_season = R.groupby("season").apply(
        lambda x: pd.Series({"model": log_loss_binary(x["p_model"], x["y"]),
                             "market": log_loss_binary(x["mkt_p"], x["y"])}),
        include_groups=False)
    wins = int((per_season["model"] < per_season["market"]).sum())
    gap = float((per_season["model"] - per_season["market"]).mean())
    print(f"\nModel beat the market in {wins}/{len(per_season)} seasons "
          f"(mean log-loss gap {gap:+.4f}).")
    return wins, len(per_season), gap


def check_disagreement(R):
    print("\n=== 2. Where the model disagrees with the market, who is right? ===")
    R = R.assign(disagreement=R["p_model"] - R["mkt_p"])
    R["bucket"] = pd.cut(R["disagreement"], DISAGREEMENT_EDGES)
    table = R.groupby("bucket", observed=True).apply(
        lambda x: pd.Series({"n": len(x),
                             "market_says": x["mkt_p"].mean(),
                             "model_says": x["p_model"].mean(),
                             "actually_won": x["y"].mean()}),
        include_groups=False)
    table["closer"] = np.where(
        (table["actually_won"] - table["model_says"]).abs()
        < (table["actually_won"] - table["market_says"]).abs(), "model", "MARKET")
    print(table.round(4).to_string())

    outer = table[table.index.map(lambda b: b.left <= -0.12 or b.right >= 0.12)]
    model_right = (outer["closer"] == "model").all()
    print("\nOuter buckets are the games the backtest actually bets. "
          f"{'Model' if model_right else 'MARKET'} is closer there"
          f"{'' if model_right else ' -- those disagreements are model error, so'}"
          f"{'' if model_right else ' every such bet is -EV before vig is even paid.'}")
    return model_right


def check_calibration(R):
    print("\n=== 3. Is the model's confidence honest? ===")
    R = R.assign(band=pd.cut(R["p_model"], np.arange(0, 1.01, 0.1)))
    table = R.groupby("band", observed=True).apply(
        lambda x: pd.Series({"n": len(x), "predicted": x["p_model"].mean(),
                             "actual": x["y"].mean(), "market": x["mkt_p"].mean()}),
        include_groups=False)
    print(table.round(4).to_string())
    confident = table[table["n"] >= 200]
    drift = (confident["predicted"] - confident["actual"]).abs().mean()
    over = ((confident["predicted"] - 0.5).abs()
            > (confident["actual"] - 0.5).abs()).mean()
    print(f"\nMean |predicted - actual| in populated bands: {drift:.4f}; "
          f"model sits further from the base rate than the truth in "
          f"{over:.0%} of them.")
    if over >= 0.6:
        print("Overconfident: it manufactures edge by pushing probabilities out, "
              "which is exactly\nwhat an edge threshold mistakes for signal.")


def check_segments(R):
    print("\n=== 4. Does any segment buck the verdict? ===")
    segments = [
        ("first 150 games of season", R["season_game_no"] < 150),
        ("games 150-400", R["season_game_no"].between(150, 399)),
        ("after game 400", R["season_game_no"] >= 400),
        ("playoffs", R["season_type"] == "Playoffs"),
        ("regular season", R["season_type"] == "Regular Season"),
        ("close lines (mkt .40-.60)", R["mkt_p"].between(0.40, 0.60)),
        ("big favorites (mkt > .75)", R["mkt_p"] > 0.75),
        ("big underdogs (mkt < .25)", R["mkt_p"] < 0.25),
        ("rest mismatch (|b2b| = 1)", R["b2b_diff"].abs() == 1),
        ("both sides rested", R["b2b_diff"] == 0),
    ]
    print(f"{'segment':>28} {'n':>6} {'model LL':>9} {'market LL':>10} {'gap':>8}")
    any_win = False
    for label, mask in segments:
        seg = R[mask]
        if len(seg) < 100:
            continue
        lm = log_loss_binary(seg["p_model"], seg["y"])
        lk = log_loss_binary(seg["mkt_p"], seg["y"])
        any_win = any_win or lm < lk
        print(f"{label:>28} {len(seg):>6} {lm:>9.4f} {lk:>10.4f} {lm - lk:>+8.4f}"
              f"{'   <-- model wins' if lm < lk else ''}")
    return any_win


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Check whether the NBA stats model carries any signal the closing line lacks.")
    ap.add_argument("--start-season", default="2013-14",
                    help="first season to evaluate (earlier seasons are training-only burn-in)")
    args = ap.parse_args()

    df, n_total, n_joined = load_priced_games()
    print(f"Games in DB: {n_total}; joined to closing moneylines: {n_joined} "
          f"({n_joined / n_total:.1%})")
    hold = (df["overround"].mean() - 1) / df["overround"].mean()
    print(f"Mean overround {df['overround'].mean():.4f} -> the book holds {hold:.2%}. "
          f"That is the hurdle any\nedge has to clear before it is worth a cent.\n")

    R = walk_forward_predict(df, args.start_season)
    print(f"{len(R)} games priced walk-forward from {args.start_season} onward.\n")

    wins, n_seasons, gap = check_the_bar(R)
    model_right_on_disagreement = check_disagreement(R)
    check_calibration(R)
    segment_win = check_segments(R)

    print("\n" + "=" * 78)
    if wins == 0 and not model_right_on_disagreement and not segment_win:
        print("VERDICT: no signal. The model is beaten by the closing line in every season,\n"
              "every disagreement bucket and every segment tested. Any positive ROI that\n"
              "nba_backtest.py reports at some threshold is variance -- do not bet it.\n\n"
              "The gap is information, not architecture (see the module docstring for the\n"
              "feature work already ruled out). The routes that can actually move it:\n"
              "  * Better injury / load-management input -- the bulk of what the closing\n"
              "    line knows and the box score does not. nba_injuries.py snapshots ESPN's\n"
              "    report daily; it builds forward from first run, so the sooner it is\n"
              "    scheduled, the sooner this gap can be tested against real data.\n"
              "  * Stop trying to beat the close. Price against Polymarket instead, using\n"
              "    the de-vigged sharp book as fair value -- that is what log_prices.py and\n"
              "    analyze_prices.py already measure, and NBA is already in DEFAULT_SPORTS.\n"
              "  * Judge any future change by CLV, not ROI. It converges far faster.")
    elif wins < n_seasons / 2:
        print(f"VERDICT: weak. The model beat the market in only {wins}/{n_seasons} seasons\n"
              f"(mean gap {gap:+.4f}). Treat backtest ROI as unproven until this improves.")
    else:
        print(f"VERDICT: a residual signal may exist -- the model beat the market in\n"
              f"{wins}/{n_seasons} seasons (mean gap {gap:+.4f}). NOW nba_backtest.py's\n"
              f"ROI numbers are worth reading.")
    print("=" * 78)
