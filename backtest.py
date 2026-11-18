"""Backtest + statistical proof battery. Writes reports/backtest_results.md. Math: see MATH.md.

Run: python backtest.py            (downloads prices, caches to data/prices.csv)
     python backtest.py --refresh  (force re-download)
"""
import itertools
import math
import os
import sys
from statistics import NormalDist

import numpy as np
import pandas as pd

from model import BENCH, P, UNIVERSE, backtest_returns, load_prices, scores, target_weights

N01 = NormalDist()
CACHE = "data/prices.csv"
rng = np.random.default_rng(7)


def prices():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_csv(CACHE, index_col=0, parse_dates=True)
    px = load_prices()
    os.makedirs("data", exist_ok=True)
    px.to_csv(CACHE)
    return px


def stats(r):
    eq = (1 + r).cumprod()
    return dict(
        CAGR=eq.iloc[-1] ** (252 / len(r)) - 1,
        Vol=r.std() * math.sqrt(252),
        Sharpe=r.mean() / r.std() * math.sqrt(252),
        MaxDD=(eq / eq.cummax() - 1).min(),
    )


def stationary_bootstrap_idx(T, B, L=20):
    """Politis-Romano stationary bootstrap indices (B x T), mean block length L."""
    idx = np.empty((B, T), dtype=np.int64)
    idx[:, 0] = rng.integers(0, T, B)
    for t in range(1, T):
        jump = rng.random(B) < 1 / L
        idx[:, t] = np.where(jump, rng.integers(0, T, B), (idx[:, t - 1] + 1) % T)
    return idx


def sharpe_rows(x):
    return x.mean(axis=1) / x.std(axis=1) * math.sqrt(252)


def hac_alpha(y, x, lags=5):
    """OLS y = a + b x with Newey-West standard errors. Returns annualised alpha, beta, t(alpha)."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ beta
    XtX_inv = np.linalg.inv(X.T @ X)
    S = (X * u[:, None]).T @ (X * u[:, None])
    for l in range(1, lags + 1):
        w = 1 - l / (lags + 1)
        G = (X[l:] * u[l:, None]).T @ (X[:-l] * u[:-l, None])
        S += w * (G + G.T)
    se = np.sqrt(np.diag(XtX_inv @ S @ XtX_inv))
    return beta[0] * 252, beta[1], beta[0] / se[0]


def deflated_sharpe(r, sr_trials):
    """Bailey & Lopez de Prado (2014). Daily (non-annualised) Sharpes throughout."""
    T, N = len(r), len(sr_trials)
    sr = r.mean() / r.std()
    g3, g4 = r.skew(), r.kurt() + 3  # pandas kurt is excess
    gamma = 0.5772156649
    sr0 = math.sqrt(np.var(sr_trials, ddof=1)) * (
        (1 - gamma) * N01.inv_cdf(1 - 1 / N) + gamma * N01.inv_cdf(1 - 1 / (N * math.e))
    )
    z = (sr - sr0) * math.sqrt(T - 1) / math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr**2)
    return N01.cdf(z), sr0 * math.sqrt(252)


def pbo_cscv(M, S=16):
    """Probability of backtest overfitting via combinatorially symmetric CV (Bailey et al. 2017). M: T x N returns."""
    T, N = M.shape
    blocks = np.array_split(np.arange(T), S)
    bsum = np.array([M[b].sum(0) for b in blocks])
    bsq = np.array([(M[b] ** 2).sum(0) for b in blocks])
    bn = np.array([len(b) for b in blocks], dtype=float)
    combos = np.array([[i in c for i in range(S)] for c in itertools.combinations(range(S), S // 2)], dtype=float)

    def sr(mask):
        n = mask @ bn
        m = (mask @ bsum) / n[:, None]
        v = (mask @ bsq) / n[:, None] - m**2
        return m / np.sqrt(v)

    is_sr, oos_sr = sr(combos), sr(1 - combos)
    best = is_sr.argmax(1)
    oos_best = oos_sr[np.arange(len(combos)), best]
    rank = (oos_sr < oos_best[:, None]).sum(1) + 1  # 1..N
    omega = rank / (N + 1)
    logit = np.log(omega / (1 - omega))
    return float((logit <= 0).mean())


def rank_ic(score, fwd):
    ics = score.rank(axis=1).corrwith(fwd.rank(axis=1), axis=1).dropna()
    return ics.mean(), ics.mean() / ics.std() * math.sqrt(len(ics)), len(ics)


def main():
    px = prices()
    start = px.index[P["trend_long"] + P["vol_win"]]  # first date with full signal history
    sl = lambda r: r.loc[start:]

    strat = sl(backtest_returns(px, target_weights(px)))  # shipped model: inv-vol basket + vol target + regime
    strat2x = sl(backtest_returns(px, target_weights(px), cost_bps=10))
    sig = sl(backtest_returns(px, target_weights(px, {**P, "use_signal": True})))  # trend+reversal signal model
    raw = sl(backtest_returns(px, target_weights(px, {**P, "vol_target": 9, "regime_scale": 1.0})))
    rets = (px / px.shift(1) - 1)
    ew = sl(rets[UNIVERSE].mean(axis=1, skipna=True).fillna(0))
    qqq = sl(rets[BENCH].fillna(0))

    table = pd.DataFrame({
        "Shipped model (5bp)": stats(strat), "Shipped model (10bp stress)": stats(strat2x),
        "Signal model (trend+reversal) — rejected": stats(sig), "Inv-vol basket, no risk engine": stats(raw),
        "Equal-weight buy&hold": stats(ew), "QQQ buy&hold": stats(qqq),
    }).T

    # --- Proof battery ---
    B = 2000
    idx = stationary_bootstrap_idx(len(strat), B)
    S_m, S_sig, S_ew = (sharpe_rows(x.values[idx]) for x in (strat, sig, ew))
    dd = lambda x: ((c := np.cumprod(1 + x, axis=1)) / np.maximum.accumulate(c, axis=1) - 1).min(axis=1)
    DD_m, DD_ew, DD_q = dd(strat.values[idx]), dd(ew.values[idx]), dd(qqq.values[idx])
    boot = {
        "Model Sharpe 95% CI": np.percentile(S_m, [2.5, 97.5]),
        "P(Model Sharpe <= 0)": (S_m <= 0).mean(),
        "P(signal model Sharpe >= shipped)": (S_sig - S_m >= 0).mean(),
        "P(Model Sharpe <= equal-weight)": (S_m - S_ew <= 0).mean(),
        "P(Model MaxDD worse than equal-weight)": (DD_m <= DD_ew).mean(),
        "P(Model MaxDD worse than QQQ)": (DD_m <= DD_q).mean(),
    }
    a_ew, b_ew, t_ew = hac_alpha(strat.values, ew.values)
    a_q, b_q, t_q = hac_alpha(strat.values, qqq.values)

    grid = [dict(vol_target=vt, regime_scale=rs, vol_win=vw, regime_ma=ma)
            for vt in (0.10, 0.15, 0.20, 0.25) for rs in (0.0, 0.5, 1.0) for vw in (20, 60, 120) for ma in (100, 200)]
    M = np.column_stack([sl(backtest_returns(px, target_weights(px, {**P, **g}))).values for g in grid])
    sr_trials = M.mean(0) / M.std(0)
    dsr, sr0_ann = deflated_sharpe(strat, sr_trials)
    pbo = pbo_cscv(M)

    sc = scores(px).loc[start:]
    lr = np.log(px[UNIVERSE]).diff()
    ic1 = rank_ic(sc, lr.shift(-1).loc[start:])
    ic5 = rank_ic(sc.iloc[::5], lr.rolling(5).sum().shift(-5).loc[start:].iloc[::5])

    out = [
        f"# Backtest results\n\nPeriod {strat.index[0].date()} to {strat.index[-1].date()} ({len(strat)} days). "
        f"Generated by backtest.py; parameters in model.py were fixed before this run.\n",
        "## Performance\n", table.to_markdown(floatfmt=".3f"), "\n",
        "## Statistical tests\n",
        "| Test | Result | Pass bar |", "|---|---|---|",
        f"| Bootstrap Sharpe 95% CI (stationary, L=20, B={B}) | [{boot['Model Sharpe 95% CI'][0]:.2f}, {boot['Model Sharpe 95% CI'][1]:.2f}] | lower bound > 0 |",
        f"| P(Sharpe <= 0) | {boot['P(Model Sharpe <= 0)']:.3f} | < 0.05 |",
        f"| P(signal model Sharpe >= shipped) — would adding the trend+reversal signal help? | {boot['P(signal model Sharpe >= shipped)']:.3f} | < 0.05 to justify adding it |",
        f"| P(Model Sharpe <= equal-weight buy&hold) | {boot['P(Model Sharpe <= equal-weight)']:.3f} | < 0.05 |",
        f"| P(Model max drawdown worse than equal-weight) | {boot['P(Model MaxDD worse than equal-weight)']:.3f} | < 0.05 |",
        f"| P(Model max drawdown worse than QQQ) | {boot['P(Model MaxDD worse than QQQ)']:.3f} | < 0.05 |",
        f"| Alpha vs equal-weight (HAC t) | {a_ew:.2%}/yr, beta {b_ew:.2f}, t = {t_ew:.2f} | t > 3.0 (Harvey-Liu-Zhu) |",
        f"| Alpha vs QQQ (HAC t) | {a_q:.2%}/yr, beta {b_q:.2f}, t = {t_q:.2f} | t > 3.0 |",
        f"| Deflated Sharpe ratio ({len(grid)} trials) | {dsr:.3f} (Sharpe hurdle {sr0_ann:.2f}) | > 0.95 |",
        f"| Probability of backtest overfitting (CSCV, S=16) | {pbo:.3f} | < 0.30 |",
        f"| Rank IC, next day | {ic1[0]:.4f} (t = {ic1[1]:.2f}, n = {ic1[2]}) | t > 2 |",
        f"| Rank IC, next 5 days (non-overlapping) | {ic5[0]:.4f} (t = {ic5[1]:.2f}, n = {ic5[2]}) | t > 2 |",
        "\n## Caveats\n",
        "- Selection bias: these 8 names were chosen *because* they won. Absolute returns are inflated; only the "
        "comparisons against equal-weight and the inv-vol basket (same names, same bias) are meaningful.",
        "- SPCX has ~110 days of history and enters only after 60 days; it barely affects these results.",
        "- Prices are yfinance adjusted closes; fills assumed at the close with flat bp costs.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/backtest_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
