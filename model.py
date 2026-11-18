"""Signal + sizing model shared by backtest.py and monitor.py. Math: see MATH.md."""
import numpy as np
import pandas as pd
import yfinance as yf

UNIVERSE = ["TSLA", "SPCX", "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META"]
BENCH = "QQQ"

# Fixed a priori from the research (not tuned on this data). backtest.py measures how much a grid around them overfits.
P = dict(
    trend_long=252, trend_skip=21, trend_short=63,  # 12-1 month + 3 month time-series momentum
    rev_win=5, beta_win=60,                          # 1-week residual reversal vs QQQ
    vol_win=60,                                      # vol / covariance lookback
    w_trend=0.5,                                     # equal-weight signal combination (w_rev = 1 - w_trend)
    cap=0.25, vol_target=0.15,                       # per-name cap, portfolio vol target (annual)
    spcx_cap=0.05,                                   # SPCX: lockup 2026-12-08 + merger event risk (report §SPCX)
    use_signal=False,                                # signals failed the bootstrap test vs the plain basket (reports/backtest_results.md); kept for research/alerts only
    regime_ma=200, regime_scale=0.5,                 # halve gross when QQQ < 200d MA
    min_hist=60,                                     # days of history before a name is tradable (SPCX IPO'd 2026-06)
)


def load_prices(start="2014-01-01"):
    px = yf.download(UNIVERSE + [BENCH], start=start, auto_adjust=True, progress=False, threads=False)["Close"]
    return px[UNIVERSE + [BENCH]].dropna(how="all")


def scores(px, p=P):
    """Combined score per name at each close t, using only data up to t."""
    lr = np.log(px).diff()
    s, b = lr[UNIVERSE], lr[BENCH]
    vol = s.rolling(p["vol_win"]).std()

    n_long = p["trend_long"] - p["trend_skip"]
    z_long = s.rolling(n_long).sum().shift(p["trend_skip"]) / (vol * np.sqrt(n_long))
    z_short = s.rolling(p["trend_short"]).sum() / (vol * np.sqrt(p["trend_short"]))
    trend = ((z_long.fillna(z_short) + z_short) / 2).clip(-3, 3)  # young names fall back to short trend

    beta = pd.DataFrame({c: s[c].rolling(p["beta_win"]).cov(b) / b.rolling(p["beta_win"]).var() for c in UNIVERSE})
    resid = s - beta.shift(1).mul(b, axis=0)
    rvol = resid.rolling(p["beta_win"]).std()
    rev = (-resid.rolling(p["rev_win"]).sum() / (rvol * np.sqrt(p["rev_win"]))).clip(-3, 3)

    score = p["w_trend"] * trend + (1 - p["w_trend"]) * rev.fillna(0)  # rev needs ~120d; young names (SPCX) use trend only
    return score.where(s.notna().cumsum() >= p["min_hist"])


def target_weights(px, p=P):
    """Long-only weights at each close t: inverse-vol on positive scores, capped, vol-targeted, regime-scaled."""
    lr = np.log(px).diff()
    s = lr[UNIVERSE]
    vol_a = s.rolling(p["vol_win"]).std() * np.sqrt(252)
    sc = scores(px, p)
    raw = (sc.clip(lower=0) if p["use_signal"] else sc.notna().astype(float)) / vol_a
    caps = pd.Series(p["cap"], index=UNIVERSE).where(lambda c: c.index != "SPCX", p["spcx_cap"])
    w = raw.div(raw.sum(axis=1), axis=0).fillna(0).clip(upper=caps, axis=1)  # shortcut: capped excess sits in cash

    n = len(UNIVERSE)
    cov = (s.fillna(0).rolling(p["vol_win"]).cov() * 252).values.reshape(len(w), n, n)
    W = w.values
    pv = np.sqrt(np.clip(np.einsum("ti,tij,tj->t", W, np.nan_to_num(cov), W), 0, None))
    scale = pd.Series(np.where(pv > 0, np.minimum(1.0, p["vol_target"] / np.where(pv > 0, pv, 1)), 1.0), index=w.index)  # no leverage

    qqq = px[BENCH]
    risk_off = qqq < qqq.rolling(p["regime_ma"]).mean()
    scale = scale * np.where(risk_off, p["regime_scale"], 1.0)
    return w.mul(scale, axis=0)


def backtest_returns(px, w, cost_bps=5.0):
    """Daily net returns: weights set at close t earn close t -> t+1. Cost on turnover each side."""
    r = (px[UNIVERSE] / px[UNIVERSE].shift(1) - 1).fillna(0)
    wl = w.shift(1).fillna(0)  # shortcut: ignores intraday drift of weights between rebalances; fine for daily rebalancing
    turnover = (w - w.shift(1)).abs().sum(axis=1).shift(1).fillna(0)
    return (wl * r).sum(axis=1) - turnover * cost_bps / 1e4
