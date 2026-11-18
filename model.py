"""Signal + sizing model shared by backtest.py and monitor.py. Math: see MATH.md."""
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

CORE = ["TSLA", "SPCX", "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META"]
# AI compute chain, picked from supply links rather than past returns (correlations.py): TPUs/custom silicon (AVGO),
# foundry (TSM), GPUs (AMD), cloud capacity (ORCL). All sell into the same AI capex that drives NVDA/MSFT/GOOGL/AMZN.
AI_CHAIN = ["AVGO", "TSM", "AMD", "ORCL"]
# ANT = Anthropic (S-1 filed 2026-10-26 for Nasdaq "ANT"). No prices yet: it carries weight 0 until it has min_hist days.
UNIVERSE = CORE + AI_CHAIN + ["ANT"]
BENCH = "QQQ"
EVENT_CAPS = {"SPCX": 0.05, "ANT": 0.05}  # fresh IPOs: lockups, thin history, event risk (report §SPCX)

# Fixed a priori from the research (not tuned on this data). backtest.py measures how much a grid around them overfits.
P = dict(
    trend_long=252, trend_skip=21, trend_short=63,  # 12-1 month + 3 month time-series momentum
    rev_win=5, beta_win=60,                          # 1-week residual reversal vs QQQ
    vol_win=60,                                      # vol / covariance lookback
    w_trend=0.5,                                     # equal-weight signal combination (w_rev = 1 - w_trend)
    cap=0.25, vol_target=0.25,                       # per-name cap, portfolio vol target (annual). Raised from 0.15 on 2026-11-18
                                                     # for return: same Sharpe, CAGR 19%->26%, MaxDD -20%->-27%. Above 0.25 the
                                                     # no-leverage cap binds and adds ~nothing. ~1/5 Kelly (MATH.md §3).
    sizing="invvol",                                 # "invvol" or "hrp" (correlation-aware). HRP lost to inv-vol in backtest.py
    use_signal=False,                                # signals failed the bootstrap test vs the plain basket (reports/backtest_results.md); kept for research/alerts only
    regime_ma=200, regime_scale=0.5,                 # halve gross when QQQ < 200d MA
    min_hist=60,                                     # days of history before a name is tradable (SPCX IPO'd 2026-06)
)


def names_of(px):
    return [c for c in px.columns if c != BENCH]


def load_prices(start="2014-01-01"):
    px = yf.download(UNIVERSE + [BENCH], start=start, auto_adjust=True, progress=False, threads=False)["Close"]
    return px.reindex(columns=UNIVERSE + [BENCH]).dropna(how="all")  # reindex: not-yet-listed names (ANT) stay as NaN


def scores(px, p=P):
    """Combined score per name at each close t, using only data up to t."""
    names = names_of(px)
    lr = np.log(px).diff()
    s, b = lr[names], lr[BENCH]
    vol = s.rolling(p["vol_win"]).std()

    n_long = p["trend_long"] - p["trend_skip"]
    z_long = s.rolling(n_long).sum().shift(p["trend_skip"]) / (vol * np.sqrt(n_long))
    z_short = s.rolling(p["trend_short"]).sum() / (vol * np.sqrt(p["trend_short"]))
    trend = ((z_long.fillna(z_short) + z_short) / 2).clip(-3, 3)  # young names fall back to short trend

    beta = pd.DataFrame({c: s[c].rolling(p["beta_win"]).cov(b) / b.rolling(p["beta_win"]).var() for c in names})
    resid = s - beta.shift(1).mul(b, axis=0)
    rvol = resid.rolling(p["beta_win"]).std()
    rev = (-resid.rolling(p["rev_win"]).sum() / (rvol * np.sqrt(p["rev_win"]))).clip(-3, 3)

    score = p["w_trend"] * trend + (1 - p["w_trend"]) * rev.fillna(0)  # rev needs ~120d; young names (SPCX) use trend only
    return score.where(s.notna().cumsum() >= p["min_hist"])


def _cluster_var(cov, idx):
    sub = cov[np.ix_(idx, idx)]
    iv = 1 / np.diag(sub)
    iv /= iv.sum()
    return iv @ sub @ iv


def hrp(cov):
    """Hierarchical risk parity (Lopez de Prado 2016): cluster by correlation, split risk top-down between clusters.
    Unlike inverse-vol, two highly correlated names (NVDA/AMD) share one risk budget instead of getting two."""
    sd = np.sqrt(np.diag(cov))
    dist = np.sqrt(np.clip((1 - cov / np.outer(sd, sd)) / 2, 0, None))
    order = leaves_list(linkage(squareform(dist, checks=False), "single"))
    w = np.ones(len(cov))
    clusters = [order]
    while clusters:
        clusters = [c[sl] for c in clusters if len(c) > 1 for sl in (slice(0, len(c) // 2), slice(len(c) // 2, None))]
        for a, b in zip(clusters[::2], clusters[1::2]):
            va, vb = _cluster_var(cov, a), _cluster_var(cov, b)
            w[a] *= vb / (va + vb)
            w[b] *= va / (va + vb)
    return w


def target_weights(px, p=P):
    """Long-only weights at each close t: base sizing on eligible names, capped, vol-targeted, regime-scaled."""
    px = px.ffill()  # one missing close would blank that name's 60d vol for 60 days -> weight 0
    names = names_of(px)
    lr = np.log(px).diff()
    s = lr[names]
    vol_a = s.rolling(p["vol_win"]).std() * np.sqrt(252)
    sc = scores(px, p)
    n = len(names)
    cov = (s.fillna(0).rolling(p["vol_win"]).cov() * 252).values.reshape(len(s), n, n)

    if p["sizing"] == "hrp":
        ok = (sc.notna() & (vol_a > 0)).values
        base = np.zeros((len(s), n))
        for t in np.flatnonzero(ok.any(axis=1)):
            m = ok[t]
            base[t, m] = hrp(cov[t][np.ix_(m, m)]) if m.sum() > 1 else 1.0
        base = pd.DataFrame(base, index=s.index, columns=names)
    else:
        base = sc.notna().astype(float) / vol_a
    raw = base * (sc.clip(lower=0) if p["use_signal"] else 1)
    caps = pd.Series({c: EVENT_CAPS.get(c, p["cap"]) for c in names})
    w = raw.div(raw.sum(axis=1), axis=0).fillna(0).clip(upper=caps, axis=1)  # shortcut: capped excess sits in cash

    W = w.values
    pv = np.sqrt(np.clip(np.einsum("ti,tij,tj->t", W, np.nan_to_num(cov), W), 0, None))
    scale = pd.Series(np.where(pv > 0, np.minimum(1.0, p["vol_target"] / np.where(pv > 0, pv, 1)), 1.0), index=w.index)  # no leverage

    qqq = px[BENCH]
    risk_off = qqq < qqq.rolling(p["regime_ma"]).mean()
    scale = scale * np.where(risk_off, p["regime_scale"], 1.0)
    return w.mul(scale, axis=0)


def backtest_returns(px, w, cost_bps=5.0):
    """Daily net returns: weights set at close t earn close t -> t+1. Cost on turnover each side."""
    px = px.ffill()  # without this a hole books 0% twice and the move across it is lost
    names = names_of(px)
    r = (px[names] / px[names].shift(1) - 1).fillna(0)
    wl = w.shift(1).fillna(0)  # shortcut: ignores intraday drift of weights between rebalances; fine for daily rebalancing
    turnover = (w - w.shift(1)).abs().sum(axis=1).shift(1).fillna(0)
    return (wl * r).sum(axis=1) - turnover * cost_bps / 1e4
