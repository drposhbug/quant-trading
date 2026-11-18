"""Do market-moving factors (VIX, term structure, rates, dollar, credit, oil, bitcoin) or "buy the dip" rules predict
QQQ / the universe? Writes reports/macro_results.md.  Run: python macro.py [--refresh]

Everything is known at the US close of day t; targets are close t -> t+1 and t -> t+5 (non-overlapping).
Pass = Holm p < 0.05 across all tests AND the same sign in both halves. Passing predictors are then tried as an
exposure overlay on the shipped model, which must beat it in a paired bootstrap (P < 0.05) to be adopted.
"""
import math
import os
import sys

import numpy as np
import pandas as pd
import yfinance as yf

from backtest import prices, sharpe_rows, stationary_bootstrap_idx, stats
from correlations import holm, pval
from model import BENCH, P, backtest_returns, names_of, target_weights

CACHE = "data/macro.csv"
TICKERS = ["^VIX", "^VIX3M", "^TNX", "DX-Y.NYB", "HYG", "IEF", "CL=F", "BTC-USD"]


def load():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_csv(CACHE, index_col=0, parse_dates=True)
    m = yf.download(TICKERS, start="2014-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    os.makedirs("data", exist_ok=True)
    m.to_csv(CACHE)
    return m


def hac_slope_t(y, x, lags):
    """OLS slope of y on x with Newey-West t-stat."""
    X = np.column_stack([np.ones_like(x), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ b
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for l in range(1, lags + 1):
        G = Xu[l:].T @ Xu[:-l]
        S += (1 - l / (lags + 1)) * (G + G.T)
    V = np.linalg.inv(X.T @ X) @ S @ np.linalg.inv(X.T @ X)
    return b[1], b[1] / math.sqrt(V[1, 1])


def predictors(px, m):
    q = px[BENCH]
    btc = m["BTC-USD"].dropna()
    btc_ret = (btc.pct_change().shift(1)).reindex(px.index, method="ffill")  # bar t closes 00:00 UTC t+1 > US close: lag 1
    z = lambda s, w=252: (s - s.rolling(w).mean()) / s.rolling(w).std()
    m = m.reindex(px.index).ffill(limit=3)  # holiday gaps only
    rsi2 = (lambda d: 100 - 100 / (1 + d.clip(lower=0).ewm(alpha=1 / 2).mean() / (-d.clip(upper=0)).ewm(alpha=1 / 2).mean()))(q.diff())
    return {
        "VIX level (1y z-score)": z(m["^VIX"]),
        "VIX term structure (VIX/VIX3M, >1 = stress)": m["^VIX"] / m["^VIX3M"],
        "VIX 5d change": m["^VIX"].pct_change(5, fill_method=None),
        "10y yield 5d change": m["^TNX"].diff(5),
        "Dollar index 5d change": m["DX-Y.NYB"].pct_change(5, fill_method=None),
        "Credit (HYG vs IEF, 21d)": m["HYG"].pct_change(21, fill_method=None) - m["IEF"].pct_change(21, fill_method=None),
        "Oil 5d change": m["CL=F"].pct_change(5, fill_method=None).clip(-0.5, 0.5),  # Apr-2020 negative print
        "Bitcoin prior-day return": btc_ret,
        "Dip: QQQ drawdown from 21d high": q / q.rolling(21).max() - 1,
        "Dip: QQQ 5d return": q.pct_change(5, fill_method=None),
        "Dip: QQQ RSI(2)": rsi2,
    }


def main():
    px = prices()
    m = load()
    names = [c for c in names_of(px) if px[c].notna().any()]
    rets = px.pct_change(fill_method=None)
    targets = {"QQQ": rets[BENCH], "Universe EW": rets[names].mean(axis=1)}
    preds = predictors(px, m)
    start = px.index[300]

    rows = []
    for pn, x in preds.items():
        for tn, r in targets.items():
            for h in (1, 5):
                fwd = r.rolling(h).sum().shift(-h)
                d = pd.concat([x, fwd], axis=1).loc[start:].dropna().iloc[::h]
                d = d[np.isfinite(d).all(axis=1)]
                xs = (d.iloc[:, 0] - d.iloc[:, 0].mean()) / d.iloc[:, 0].std()
                b, t = hac_slope_t(d.iloc[:, 1].values, xs.values, lags=5)
                half = len(d) // 2
                b1, _ = hac_slope_t(d.iloc[:half, 1].values, xs.iloc[:half].values, 5)
                b2, _ = hac_slope_t(d.iloc[half:, 1].values, xs.iloc[half:].values, 5)
                rows.append(dict(Predictor=pn, Target=tn, Horizon=f"{h}d", n=len(d),
                                 **{"bp per 1σ": b * 1e4, "t (HAC)": t, "bp 1st half": b1 * 1e4, "bp 2nd half": b2 * 1e4},
                                 p=pval(t)))
    tab = pd.DataFrame(rows)
    tab["Holm p"] = holm(tab.p).values
    tab["Pass"] = (tab["Holm p"] < 0.05) & (np.sign(tab["bp 1st half"]) == np.sign(tab["bp 2nd half"]))

    # Overlay test for every predictor that passed on any target: cut exposure to 50% on its worst-quintile days
    # (quintile from an expanding window, so no lookahead), compare with the shipped model.
    w = target_weights(px)
    s0 = start
    base = backtest_returns(px, w).loc[s0:]
    idx = stationary_bootstrap_idx(len(base), 2000)
    Sb = sharpe_rows(base.values[idx])
    ov = []
    for pn in tab.loc[tab.Pass, "Predictor"].unique():
        row = tab[(tab.Predictor == pn) & tab.Pass].iloc[0]
        x = preds[pn].reindex(px.index)
        sign = np.sign(row["bp per 1σ"])  # bad days = low x if slope > 0, high x if slope < 0
        bad_cut = (x * sign).expanding(252).quantile(0.2).shift(1)
        mult = np.where((x * sign) < bad_cut, 0.5, 1.0)
        r = backtest_returns(px, w.mul(mult, axis=0)).loc[s0:]
        ov.append(dict(Overlay=f"{pn}: half exposure on worst-quintile days", **stats(r),
                       **{"P(overlay Sharpe <= shipped)": (sharpe_rows(r.values[idx]) <= Sb).mean()}))
    ov_tab = pd.DataFrame([dict(Overlay="Shipped model", **stats(base), **{"P(overlay Sharpe <= shipped)": np.nan})] + ov)

    now = {pn: x.dropna().iloc[-1] for pn, x in preds.items() if x.notna().any()}
    out = [
        f"# Market-moving factors and dip rules\n\nGenerated by macro.py on {px.index[-1].date()}. "
        f"Targets: QQQ and the equal-weight universe ({len(names)} names). "
        f"{len(tab)} tests, Holm-corrected; pass also needs the same sign in both halves.\n",
        "## Predictive tests\n",
        tab.drop(columns="p").to_markdown(index=False, floatfmt=".3f"),
        f"\n**{int(tab.Pass.sum())} of {len(tab)} pass.**\n",
        "## Overlay test (only predictors that passed)\n",
        ov_tab.to_markdown(index=False, floatfmt=".3f") if ov else "None passed, so there is nothing to overlay.",
        "\n## Today's readings\n",
        pd.Series(now).to_frame("latest").to_markdown(floatfmt=".4f"),
        "\n## Caveats\n",
        "- Bitcoin is lagged one extra day because its daily bar closes after the US close.",
        "- VIX/VIX3M are index levels, not tradable; they are used only as signals.",
        "- Each predictor is tested in one pre-chosen form (no lookback tuning), to keep the test count honest.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/macro_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
