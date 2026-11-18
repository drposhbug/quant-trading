"""Correlation research: how the universe moves together beyond the market, and whether any of it predicts returns.
Writes reports/correlations_results.md.  Run: python correlations.py [--refresh]

Descriptive (no pass bar): residual / overnight / intraday correlation, crash vs rally tail dependence, random-matrix noise filter.
Predictive (pass = Holm p < 0.05 AND same sign in both halves): peer lead-lag, peer catch-up, overnight momentum,
intraday reversal, and every ordered pair "i today -> j tomorrow".
"""
import math
import os
import sys
from statistics import NormalDist

import numpy as np
import pandas as pd
import yfinance as yf

from backtest import rank_ic
from model import BENCH, UNIVERSE

CACHE = "data/ohlc.pkl"  # local cache this script writes itself (data/ is gitignored), so read_pickle is safe
N01 = NormalDist()


def load():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_pickle(CACHE)
    d = yf.download(UNIVERSE + [BENCH], start="2014-01-01", auto_adjust=True, progress=False, threads=False)
    d = d[["Open", "Close"]].dropna(axis=1, how="all")
    os.makedirs("data", exist_ok=True)
    d.to_pickle(CACHE)
    return d


def resid(r, win=60):
    """Return minus (beta known at t-1) x QQQ return."""
    b, s = r[BENCH], r.drop(columns=BENCH)
    beta = s.apply(lambda c: c.rolling(win).cov(b) / b.rolling(win).var())
    return s - beta.shift(1).mul(b, axis=0)


def holm(p):
    p = pd.Series(p)
    order = p.sort_values().index
    adj = (p[order] * np.arange(len(p), 0, -1)).cummax().clip(upper=1)
    return adj.reindex(p.index)


def pval(t):
    return 2 * (1 - N01.cdf(abs(t)))


def top_pairs(m, k=8, key=None):
    iu = np.triu_indices(len(m), 1)
    s = pd.Series(m.values[iu], index=[f"{m.index[i]}–{m.columns[j]}" for i, j in zip(*iu)]).dropna()
    return s.reindex((key(s) if key else s).sort_values(ascending=False).index).head(k)


def tail_dep(r, q=0.05, min_days=500):
    """P(j in its worst (best) q | i in its worst (best) q), quantiles taken over the days both traded. Independent ~= q.
    Pairs with < min_days shared days are NaN (SPCX would otherwise rest on ~6 tail days)."""
    names = r.columns
    L, U = (pd.DataFrame(np.nan, index=names, columns=names) for _ in range(2))
    for i in names:
        for j in names:
            x = r[[i, j]].dropna()
            if i == j or len(x) < min_days:
                continue
            lo, hi = x <= x.quantile(q), x >= x.quantile(1 - q)
            L.loc[i, j] = (lo[i] & lo[j]).sum() / lo[i].sum()
            U.loc[i, j] = (hi[i] & hi[j]).sum() / hi[i].sum()
    return (L + L.T) / 2, (U + U.T) / 2


def peer_mats(e, win=252):
    """Month-end peer weights from trailing residual correlation (positive part, no self, rows sum to 1)."""
    mats = {}
    for d in e.resample("ME").last().index:
        c = e.loc[:d].tail(win).corr(min_periods=120).fillna(0).clip(lower=0)
        c = c.mask(np.eye(len(c), dtype=bool), 0)
        mats[d] = c.div(c.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    return mats


def peer_signal(x, mats):
    """For each day t: peer-weighted average of x_t using the latest month-end matrix (data <= t)."""
    out = pd.DataFrame(np.nan, index=x.index, columns=x.columns)
    ends = sorted(mats)
    for a, b in zip(ends, ends[1:] + [x.index[-1] + pd.Timedelta(days=1)]):
        blk = x.loc[(x.index > a) & (x.index <= b)]
        out.loc[blk.index] = blk.fillna(0).values @ mats[a].values.T
    return out.where(x.notna())


def main():
    d = load()
    O, C = d["Open"], d["Close"]
    names = [c for c in C.columns if c != BENCH]
    full = C.pct_change(fill_method=None)
    night = O / C.shift(1) - 1
    day = C / O - 1
    e, en, ed = resid(full), resid(night), resid(day)

    # ---------- descriptive ----------
    recent = e.loc[e.index[-504]:]  # last 2 years
    corr_full, corr_n, corr_d = (x.loc[recent.index].corr(min_periods=250) for x in (e, en, ed))  # SPCX (~50 obs) -> NaN
    raw_corr = full.loc[recent.index, names].corr()

    L, U = tail_dep(full[names])
    asym = L - U

    rm = recent.dropna(axis=1, thresh=400).dropna()
    T_, N_ = rm.shape
    ev = np.sort(np.linalg.eigvalsh(np.corrcoef(rm.values.T)))[::-1]
    lam_max = (1 + math.sqrt(N_ / T_)) ** 2

    # ---------- predictive ----------
    fwd1 = full[names].shift(-1)
    fwd5 = full[names].rolling(5).sum().shift(-5)
    mats = peer_mats(e)
    e21 = e.rolling(21).sum()
    sigs = {
        "Peer lead-lag (peers' residual today → me tomorrow)": peer_signal(e, mats),
        "Peer catch-up (peers' 21d residual − mine)": peer_signal(e21, mats) - e21,
        "Overnight momentum (21d sum of overnight returns)": night[names].rolling(21).sum(),
        "Intraday reversal (−21d sum of intraday returns)": -day[names].rolling(21).sum(),
    }
    start = e.index[300]
    half = e.index[len(e) // 2 + 150]
    rows = []
    for nm, sg in sigs.items():
        for h, fwd, step in (("1d", fwd1, 1), ("5d", fwd5, 5)):
            f = lambda a, b: rank_ic(sg.loc[a:b].iloc[::step], fwd.loc[a:b].iloc[::step])
            ic, t, n = f(start, None)
            ic1, _, _ = f(start, half)
            ic2, _, _ = f(half, None)
            rows.append(dict(Signal=nm, Horizon=h, IC=ic, t=t, n=n, IC_1st_half=ic1, IC_2nd_half=ic2, p=pval(t)))
    sig_tab = pd.DataFrame(rows)
    sig_tab["Holm p"] = holm(sig_tab["p"]).values
    sig_tab["Pass"] = (sig_tab["Holm p"] < 0.05) & (np.sign(sig_tab.IC_1st_half) == np.sign(sig_tab.IC_2nd_half))

    ll = []
    for i in names:
        for j in names:
            if i == j:
                continue
            x = pd.concat([e[i], e[j].shift(-1)], axis=1).loc[start:].dropna()
            if len(x) < 250:
                continue
            c = x.corr("spearman").iloc[0, 1]  # rank: Pearson was fooled by back-to-back earnings days (META->AMZN)
            h = len(x) // 2
            c1, c2 = (x.iloc[sl].corr("spearman").iloc[0, 1] for sl in (slice(None, h), slice(h, None)))
            ll.append(dict(Leader=i, Follower=j, corr=c, n=len(x), t=c * math.sqrt(len(x)), c1=c1, c2=c2))
    ll = pd.DataFrame(ll)
    ll["p"] = ll.t.map(pval)
    ll["Holm p"] = holm(ll.p).values
    ll["Pass"] = (ll["Holm p"] < 0.05) & (np.sign(ll.c1) == np.sign(ll.c2))
    ll = ll.reindex(ll.t.abs().sort_values(ascending=False).index)

    fmt = lambda s: s.to_frame("value").to_markdown(floatfmt=".3f")
    out = [
        f"# Correlation research\n\nGenerated by correlations.py on {C.index[-1].date()}. Names: {', '.join(names)}"
        f" (ANT has no prices until it lists). Residual = return minus rolling 60d beta × QQQ.\n",
        "## 1. Raw vs residual correlation (last 2 years)\n",
        f"Average raw pairwise correlation **{raw_corr.values[np.triu_indices(len(names), 1)].mean():.2f}**, "
        f"residual **{np.nanmean(corr_full.values[np.triu_indices(len(names), 1)]):.2f}**. Most raw co-movement is the market.\n",
        "Strongest residual pairs (real shared exposure beyond QQQ):\n", fmt(top_pairs(corr_full)),
        "\n## 2. Overnight vs intraday residual correlation\n",
        "Overnight moves come from news and after-hours traders, intraday moves from institutions. Pairs where they differ most:\n",
        (lambda s: s.to_frame("overnight − intraday").assign(
            overnight=[corr_n.loc[k.split('–')[0], k.split('–')[1]] for k in s.index],
            intraday=[corr_d.loc[k.split('–')[0], k.split('–')[1]] for k in s.index]).to_markdown(floatfmt=".3f"))(
            top_pairs(corr_n - corr_d, 10, key=abs)),
        "\n## 3. Tail dependence: crash together vs rally together (2014–today)\n",
        "P(j is in its worst 5% of days | i is). Independent stocks score 0.05. Asymmetry = crash − rally co-occurrence.\n",
        "Highest crash dependence:\n", fmt(top_pairs(L)),
        "\nMost crash-heavy asymmetry (diversification fails exactly when needed):\n", fmt(top_pairs(asym)),
        f"\nAverage crash dependence {np.nanmean(L.values[np.triu_indices(len(names), 1)]):.3f} vs "
        f"rally {np.nanmean(U.values[np.triu_indices(len(names), 1)]):.3f}.\n",
        "## 4. Random-matrix filter (residual correlation, last 2 years)\n",
        f"{N_} names × {T_} days. Pure noise produces eigenvalues up to λ+ = {lam_max:.2f}. "
        f"Eigenvalues: {', '.join(f'{x:.2f}' for x in ev)}. "
        f"**{(ev > lam_max).sum()}** above the noise bound = real residual factors (e.g. an AI-semis cluster); the rest is noise.\n",
        "## 5. Do correlations predict returns? (cross-sectional rank IC)\n",
        "Pass = Holm-corrected p < 0.05 across all 8 tests AND the same sign in both halves of the sample.\n",
        sig_tab.to_markdown(index=False, floatfmt=".4f"),
        "\n## 6. Who moves first? Rank correlation of residual i today vs residual j tomorrow, all ordered pairs\n",
        f"{len(ll)} pairs, Holm-corrected. {int(ll.Pass.sum())} pass. Top 12 by |t|:\n",
        ll.head(12)[["Leader", "Follower", "corr", "t", "c1", "c2", "Holm p", "Pass"]]
        .rename(columns={"c1": "corr 1st half", "c2": "corr 2nd half"}).to_markdown(index=False, floatfmt=".4f"),
        "\n## Not tested here (need data yfinance doesn't have)\n",
        "- Customer-supplier links from 10-K filings, shared analyst coverage, 13F/ETF common ownership, patent/job-posting "
        "overlap, Google Trends co-search, options-implied correlation. Each needs a paid or scraped source.",
        "- Earnings spillover: yfinance's history of earnings dates is too short/unreliable for a 2014+ test.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/correlations_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
