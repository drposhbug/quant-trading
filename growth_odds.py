"""Decision calc for the two open choices, by probability. Writes reports/growth_odds.md. Run: python growth_odds.py

The owner's instruction (2026-11-22): "do whatever is statistically best probability wise". The stated aim is the
account's P&L, so the criterion is compound growth: which arm is more likely to end with more money. Sharpe and
drawdown are reported beside it. These are decision odds, not significance tests.

Written 2026-11-22, before the first run:
  A. Gold. Arm = 90% book + 10% GLD, rebalanced daily, against 100% book. Add the sleeve to the live book only if
     P(arm grows faster) > 0.5 on BOTH QQQ 2005-03..2026 (no stock picking in it) and the end-2014 list's live book.
     The shipped list is reported; its window is the one that suggested gold.
  B. Exposure. Arm = fully invested (the 2026-11-21 override) against the frozen engine with T-bills on idle cash.
     Keep the override only if P(fully invested grows faster) > 0.5 on BOTH ^NDX 1986-10..2026 and the end-2014 list;
     otherwise set monitor.LIVE = P.
  P = share of 2000 paired stationary-bootstrap histories (L=20) in which the arm's mean log return is higher.
  Not modelled: the few bp a year it costs to rebalance a 90/10 mix; taxes.
"""
import numpy as np
import pandas as pd
import yfinance as yf

from backtest import prices, sharpe_rows, stats
from model import BENCH, P, backtest_returns, target_weights
from universe_study import TECH10_2014, load_extra

LIVE = {**P, "vol_target": float("inf"), "regime_scale": 1.0}
rng = np.random.default_rng(7)


def boot_idx(T, B=2000, L=20):
    idx = np.empty((B, T), dtype=np.int64)
    idx[:, 0] = rng.integers(0, T, B)
    for t in range(1, T):
        idx[:, t] = np.where(rng.random(B) < 1 / L, rng.integers(0, T, B), (idx[:, t - 1] + 1) % T)
    return idx


def odds(arm, base):
    arm, base = arm.align(base, join="inner")
    idx = boot_idx(len(arm))
    la, lb = np.log1p(arm.values)[idx].mean(1), np.log1p(base.values)[idx].mean(1)
    sa, sb = stats(arm), stats(base)
    return {"years": len(arm) / 252, "P(arm grows faster)": (la > lb).mean(),
            "P(arm Sharpe higher)": (sharpe_rows(arm.values[idx]) > sharpe_rows(base.values[idx])).mean(),
            "CAGR arm": sa["CAGR"], "CAGR base": sb["CAGR"], "Sharpe arm": sa["Sharpe"], "Sharpe base": sb["Sharpe"],
            "MaxDD arm": sa["MaxDD"], "MaxDD base": sb["MaxDD"]}


def engine_vs_full(px, rf):
    """(fully invested, frozen engine with T-bills on idle cash) daily returns."""
    w = target_weights(px)
    eng = backtest_returns(px, w) + (1 - w.sum(axis=1)).shift(1).fillna(0) * rf.reindex(px.index).fillna(0)
    return backtest_returns(px, target_weights(px, LIVE)), eng


def main():
    px = prices()
    start = px.index[P["trend_long"] + P["vol_win"]]
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    long = yf.download(["^NDX", "QQQ", "GLD", "^IRX"], start="1985-01-01", auto_adjust=True, progress=False,
                       threads=False)["Close"].dropna(subset=["^NDX"])
    rf = (long["^IRX"].ffill() / 100 / 252).fillna(0)
    gld = long["GLD"].pct_change()

    a = {}
    qqq = long["QQQ"].pct_change().loc["2005-03-01":]
    a["QQQ 2005-2026 (decides)"] = odds(0.9 * qqq + 0.1 * gld.reindex(qqq.index).fillna(0), qqq)
    for name, data in {"end-2014 list, live book (decides)": px14, "shipped list, live book (reported)": px}.items():
        book = backtest_returns(data, target_weights(data, LIVE)).loc[start:]
        a[name] = odds(0.9 * book + 0.1 * gld.reindex(book.index).fillna(0), book)

    b = {}
    ndx = pd.DataFrame({f"N{i:02d}": long["^NDX"] for i in range(12)}).assign(**{BENCH: long["^NDX"]})
    full, eng = engine_vs_full(ndx, rf)
    b["^NDX 1986-2026 (decides)"] = odds(full.loc["1986-10-01":], eng.loc["1986-10-01":])
    for name, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        full, eng = engine_vs_full(data, rf)
        b[name] = odds(full.loc[start:], eng.loc[start:])

    ta, tb = pd.DataFrame(a).T, pd.DataFrame(b).T
    gold = bool((ta[ta.index.str.contains("decides")]["P(arm grows faster)"] > 0.5).all())
    keep = bool((tb[tb.index.str.contains("decides")]["P(arm grows faster)"] > 0.5).all())
    out = ["# Decision odds, 2026-11-22\n", "Rules written in growth_odds.py before the run.\n",
           "## A. 90% book + 10% gold (arm) against 100% book\n", ta.to_markdown(floatfmt=".3f"),
           f"\n- Decision: **{'add a 10% gold sleeve' if gold else 'no gold sleeve'}**\n",
           "## B. Fully invested (arm) against the frozen engine with T-bills on idle cash\n", tb.to_markdown(floatfmt=".3f"),
           f"\n- Decision: **{'keep the fully invested override' if keep else 'revert to the engine (LIVE = P)'}**"]
    with open("reports/growth_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return ta, tb


if __name__ == "__main__":
    main()
