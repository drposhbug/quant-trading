"""Is there an exploitable minute-level lag between stocks and Polymarket daily "<TICKER> Up or Down" markets?
Appends results to reports/lag_results.md below its pre-registration block. Study only: model.py stays frozen.
Run: python lag_study.py [--refresh] | --selfcheck      (caches: data/lag_*.pkl; reuses data/pm_close_daily_*.pkl)
"""
import datetime as dt
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from scipy.stats import norm

import pm_close_study as PC  # reused (not edited): Alpaca/CLOB helpers, DK regression, caches
import pm_study as P
from correlations import holm

NY, UTC = "America/New_York", "UTC"
REPORT = "reports/lag_results.md"
MARK = "<!-- RESULTS BELOW ARE WRITTEN BY lag_study.py"
SYM = dict(PC.DAILY)  # prefix -> traded instrument (spx->SPY, ndx/qqq->QQQ)
ETF = {"SPY", "QQQ"}  # dividend-adjusted proxies for index markets
FIRST, LAST = "2025-08-01", "2026-11-19"
KS = (1, 5, 15)
COSTS = (0.01, 0.02, 0.03)
SNAPS = [30, 90, 150, 210, 270, 330, 360]  # 10:00, 11:00, ..., 15:00, 15:30
rng = np.random.default_rng(7)


# ---------------- pure pieces (tested) ----------------
def fair(S, R, sigma, T):
    """P(close > R) under a zero-drift random walk with daily vol sigma and T of 390 minutes left."""
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.log(S / R) / (sigma * np.sqrt(T / 390))
    return np.where(T > 0, norm.cdf(z), np.nan)


def runs(mask):
    """Lengths of consecutive True runs in a 1-D bool array."""
    x = np.diff(np.r_[0, mask.astype(int), 0])
    return np.flatnonzero(x == -1) - np.flatnonzero(x == 1)


def simulate(p, f, y, c, lat=1, min_T=30, thr=0.05, exit_thr=0.01):
    """Paper rule on one market. p, f: arrays for minutes m = 1..389 (index m-1). One trade max. None if no fill."""
    n = len(p)
    ask, bid = np.clip(p + c, .01, .99), np.clip(p - c, .01, .99)
    T = 390 - np.arange(1, n + 1)
    with np.errstate(invalid="ignore"):
        yes, no = (f - ask > thr) & (T >= min_T), (bid - f > thr) & (T >= min_T)
        close = np.abs(f - p) < exit_thr
    sig = np.flatnonzero(yes | no)
    if not len(sig):
        return None
    i = sig[0]
    side, e = (1 if yes[i] else -1), i + lat
    if e >= n or np.isnan(p[e]):
        return None
    price = ask[e] if side == 1 else 1 - bid[e]
    ex = np.flatnonzero(close[e + 1:])
    k = e + 1 + ex[0] + lat if len(ex) else n
    if k < n and not np.isnan(p[k]):
        out, exited = (bid[k] if side == 1 else 1 - ask[k]), True
    else:
        out, exited = (y if side == 1 else 1 - y), False
    return dict(m=e + 1, side=side, price=price, gap=(f[i] - p[i]), pnl=out / price - 1, exited=exited,
                hold=(k if exited else 390) - e)


def cluster_boot(x, g, B=2000):
    """Mean of x with a bootstrap over clusters g: (mean, lo, hi, two-sided p)."""
    x, g = np.asarray(x, float), np.asarray(g)
    u, inv = np.unique(g, return_inverse=True)
    s, n = np.bincount(inv, x, len(u)), np.bincount(inv, None, len(u))
    idx = rng.integers(0, len(u), (B, len(u)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return x.mean(), *np.percentile(m, [2.5, 97.5]), min(1.0, 2 * min((m <= 0).mean(), (m >= 0).mean()))


# ---------------- data ----------------
def tail_hist(inv):
    def one(r):
        d = r.date
        a = pd.Timestamp(dt.datetime(d.year, d.month, d.day, 14, 55), tz=NY).tz_convert(UTC)
        return PC.history(r.token, a, a + pd.Timedelta(minutes=66), 1)
    with ThreadPoolExecutor(8) as ex:
        return dict(zip(inv.token, ex.map(one, list(inv.itertuples()))))


def stocks():
    out = {}
    for sym in sorted(set(SYM.values())):
        adj = "all" if sym in ETF else "split"
        d = PC.abars(sym, "1Day", FIRST, LAST, adj)
        m = PC.abars(sym, "1Min", "2025-10-01", LAST, adj)
        if d.empty or m.empty:
            print("  no Alpaca data for", sym)
            continue
        d = d.assign(date=d.ts.dt.date).set_index("date")
        lr = np.log(d.close / d.close.shift())
        daily = pd.DataFrame({"R": d.close.shift(), "sigma": lr.rolling(20).std().shift()})
        hm = m.ts.dt.strftime("%H:%M")
        m = m[(hm >= "09:30") & (hm < "16:00")]
        out[sym] = (daily, pd.Series(m.close.values, index=(m.ts + pd.Timedelta(minutes=1)).dt.tz_convert(UTC)))
        print(f"  alpaca {sym}: {len(d)} days, {len(m)} regular minute bars")
    return out


def build(inv, hist, tail, stk, cal):
    """2-D arrays (markets x 390 minutes): p, S, f; plus a per-market frame."""
    rows, Ps, Ss, Fs = [], [], [], []
    for r in inv.itertuples():
        sym = SYM[r.inst]
        if sym not in stk or r.date not in cal.index or str(cal.loc[r.date, "close"]) != "16:00":
            continue
        daily, mins = stk[sym]
        if r.date not in daily.index or not (daily.loc[r.date, "sigma"] > 0):
            continue
        grid = pd.date_range(pd.Timestamp(f"{r.date} 09:31", tz=NY), periods=390, freq="min").tz_convert(UTC)
        h = pd.concat([hist.get(r.token, pd.Series(dtype=float)), tail.get(r.token, pd.Series(dtype=float))])
        h = h[~h.index.duplicated()].sort_index()
        if len(h) < 30:
            continue
        p = h.reindex(grid, method="ffill", tolerance=pd.Timedelta("5min")).to_numpy(copy=True)
        p[-1] = np.nan  # 16:00: PM prices used only up to 15:59
        day = mins[grid[0] - pd.Timedelta(minutes=1): grid[-1]]
        S = day.reindex(grid, method="ffill", tolerance=pd.Timedelta("15min")).values
        R, sig = daily.loc[r.date, "R"], daily.loc[r.date, "sigma"]
        f = fair(S, R, sig, 390 - np.arange(1, 391))
        rows.append(dict(inst=r.inst, sym=sym, date=r.date, y=r.y, vol=r.vol, token=r.token, sigma=sig))
        Ps.append(p), Ss.append(S), Fs.append(f)
    return pd.DataFrame(rows), np.array(Ps), np.array(Ss), np.array(Fs)


def lag(A, k):
    """A shifted so column j holds A[:, j + k] (NaN past the edge). k may be negative."""
    out = np.full_like(A, np.nan)
    if k >= 0:
        out[:, :A.shape[1] - k] = A[:, k:]
    else:
        out[:, -k:] = A[:, :k]
    return out


def trades_sample(mk, tr):
    """Public trades for up to 200 traded markets: notional near entry, to close, and minute coverage."""
    take = tr.drop_duplicates("token")
    take = take.sample(min(200, len(take)), random_state=1)

    def one(r):
        e = PC.event(PC.slug_day(r.inst, r.date))
        cond = e["markets"][0]["conditionId"]
        t0 = pd.Timestamp(f"{r.date} 09:30", tz=NY).timestamp()
        rows, cur = [], None
        for _ in range(60):
            j = P.get("https://data-api.polymarket.com/v2/trades", condition=cond, limit=1000,
                      **({"cursor": cur} if cur else {}))
            rows += j.get("data", [])
            cur = (j.get("pagination") or {}).get("next_cursor")
            if not (j.get("pagination") or {}).get("has_more") or not rows or rows[-1]["timestamp"] < t0:
                break
        return r.token, pd.DataFrame([dict(ts=x["timestamp"], size=float(x["size"]), price=float(x["price"])) for x in rows])
    with ThreadPoolExecutor(6) as ex:
        return dict(ex.map(one, list(take.itertuples())))


# ---------------- statistics ----------------
def reg(name, mk, Y, X, minn=30):
    """Pooled + per instrument DK regressions of Y on X (2-D arrays aligned with mk)."""
    ok = ~(np.isnan(Y) | np.isnan(X))
    r, c = np.nonzero(ok)
    d = pd.DataFrame(dict(y=Y[ok], x=X[ok], date=mk.date.values[r], inst=mk.inst.values[r]))
    out = []
    for g in ["POOLED"] + sorted(d.inst.unique()):
        x = d if g == "POOLED" else d[d.inst == g]
        out.append(dict(Test=name, Inst=g, **PC.test_row(x, "y", "x", minn=minn)))
    return out


def logit_slope(f, y):
    """Logistic regression y ~ a + b logit(f) by Newton; returns b."""
    f = np.clip(f, 1e-4, 1 - 1e-4)
    X = np.column_stack([np.ones(len(f)), np.log(f / (1 - f))])
    w = np.zeros(2)
    for _ in range(50):
        q = 1 / (1 + np.exp(-X @ w))
        w += np.linalg.solve(X.T @ (X * (q * (1 - q))[:, None]) + 1e-9 * np.eye(2), X.T @ (y - q))
    return w[1]


def main():
    cal = pd.read_pickle("data/pm_close_calendar.pkl")  # written by pm_close_study.py only
    inv = pd.read_pickle("data/pm_close_daily_inv.pkl")
    hist = pd.read_pickle("data/pm_close_daily_hist.pkl")
    inv = inv[(inv.rule == "prev close") & inv.y.isin([0.0, 1.0])].reset_index(drop=True)
    tail = PC.cached("data/lag_pm_tail.pkl", lambda: tail_hist(inv))
    stk = PC.cached("data/lag_stocks.pkl", stocks)
    mk, Pm, Sm, Fm = build(inv, hist, tail, stk, cal)
    print("markets in panel:", len(mk))
    y = mk.y.values
    G = Fm - Pm
    dP, dF = Pm - lag(Pm, -1), Fm - lag(Fm, -1)
    r1 = 1e4 * np.log(lag(Sm, 1) / Sm)
    T = 390 - np.arange(1, 391)[None, :].repeat(len(mk), 0)

    # ---- coverage ----
    cov = mk.assign(pm_min=np.isfinite(Pm[:, :389]).sum(1), stk_min=np.isfinite(Sm).sum(1),
                    both=(np.isfinite(Pm) & np.isfinite(Sm))[:, :389].sum(1),
                    moving=(np.abs(dP[:, :389]) > 0).sum(1))
    covt = cov.groupby("inst").agg(markets=("date", "size"), first=("date", "min"), last=("date", "max"),
                                   median_vol=("vol", "median"), market_minutes=("both", "sum"),
                                   pm_moves_per_day=("moving", "median")).reset_index()

    # ---- calibration ----
    cal_rows, pts = [], []
    for j in SNAPS:
        ok = np.isfinite(Fm[:, j - 1]) & np.isfinite(Pm[:, j - 1])
        f, p, yy = Fm[ok, j - 1], Pm[ok, j - 1], y[ok]
        hm = (dt.datetime(2000, 1, 1, 9, 30) + dt.timedelta(minutes=j)).strftime("%H:%M")
        cal_rows.append(dict(time=hm, n=ok.sum(), brier_fair=((f - yy) ** 2).mean(), brier_PM=((p - yy) ** 2).mean(),
                             logit_slope_fair=logit_slope(f, yy), logit_slope_PM=logit_slope(p, yy),
                             mean_abs_gap_pp=100 * np.abs(f - p).mean()))
        pts.append(pd.DataFrame(dict(f=f, p=p, y=yy)))
    pts = pd.concat(pts)
    bins = np.linspace(0, 1, 11)
    calt = pts.groupby(pd.cut(pts.f, bins, include_lowest=True), observed=True).agg(
        n=("y", "size"), mean_fair=("f", "mean"), mean_PM=("p", "mean"), freq_up=("y", "mean")).reset_index()

    # ---- lag tests ----
    tests = []
    for k in KS:
        tgt = lag(Pm, k) - Pm
        tests += reg(f"a PM lags: dp(t->t+{k}) on gap", mk, tgt, G)
        tests += reg(f"a' PM lags (bounce-robust): dp(t->t+{k}) on f_t-p_(t-1)", mk, tgt, Fm - lag(Pm, -1))
        rk = 1e4 * np.log(lag(Sm, k) / Sm)
        tests += reg(f"b1 PM leads: r(t->t+{k}) bp on (dp-df) per 10pp", mk, rk, 10 * (dP - dF))
        tests += reg(f"b2 PM leads: r(t->t+{k}) bp on (p-f) per 10pp", mk, rk, -10 * G)
    tests += reg("c1 PM lags: dp_t on sum df_(t-1..t-5)", mk, dP, sum(lag(dF, -L) for L in range(1, 6)))
    tests += reg("c2 PM leads: r(t->t+1) bp on (p_t-p_(t-5)) per 10pp", mk, r1, 10 * (Pm - lag(Pm, -5)))
    xc = []
    for L in range(-15, 16):
        row = dict(lag=L)
        for nm, B in (("corr(dp_t, df_(t-L))", dF), ("corr(dp_t, r_(t-L))", lag(r1, -1))):
            Bl = lag(B, -L)
            ok = np.isfinite(dP) & np.isfinite(Bl)
            row[nm] = np.corrcoef(dP[ok], Bl[ok])[0, 1]
            row["n"] = ok.sum()
        xc.append(row)
    xc = pd.DataFrame(xc)

    # ---- gaps ----
    absg = np.abs(G[:, :389])
    gap_rows = []
    for nm, sel in (("all minutes", np.ones_like(absg, bool)), ("T >= 30", T[:, :389] >= 30)):
        for thr in (0.05, 0.10):
            m = (absg > thr) & sel
            rl = np.concatenate([runs(row) for row in m])
            gap_rows.append(dict(sample=nm, threshold_pp=100 * thr, share_of_minutes=m.sum() / (np.isfinite(absg) & sel).sum(),
                                 markets_with_episode=float((m.any(1)).mean()), episodes=len(rl),
                                 mean_len=rl.mean() if len(rl) else np.nan,
                                 median_len=np.median(rl) if len(rl) else np.nan,
                                 p90_len=np.percentile(rl, 90) if len(rl) else np.nan))
    hl = []
    for nm, sel in (("all minutes", T[:, :388] >= 1), ("T >= 30", T[:, :388] >= 30)):
        a, b = G[:, :388], G[:, 1:389]
        ok = np.isfinite(a) & np.isfinite(b) & sel
        phi = np.polyfit(a[ok], b[ok], 1)[0]
        hl.append(dict(sample=nm, n=ok.sum(), phi=phi, half_life_min=math.log(0.5) / math.log(phi) if 0 < phi < 1 else np.nan))

    # ---- paper rule ----
    paper, trades_all = [], {}
    for c in COSTS:
        for lat in (1, 0):
            tr = [dict(i=i, **t) for i in range(len(mk))
                  if (t := simulate(Pm[i, :389], Fm[i, :389], y[i], c, lat=lat))]
            tr = pd.DataFrame(tr)
            tr = tr.join(mk[["inst", "date", "token", "vol"]], on="i")
            trades_all[(c, lat)] = tr
            mean, lo, hi, p = cluster_boot(tr.pnl, tr.date)
            cut = sorted(tr.date.unique())[tr.date.nunique() // 2]
            paper.append(dict(cost_c=100 * c, fill="next minute" if lat else "same minute (optimistic)", n=len(tr),
                              dates=tr.date.nunique(), up_side=float((tr.side == 1).mean()),
                              hit=float((tr.pnl > 0).mean()), mean_pnl_per_usd=mean, ci_lo=lo, ci_hi=hi, p=p,
                              h1=tr[tr.date < cut].pnl.mean(), h2=tr[tr.date >= cut].pnl.mean(),
                              exited_early=float(tr.exited.mean()), median_entry=tr.price.median(),
                              median_hold_min=tr.hold.median()))
    paper = pd.DataFrame(paper)
    prim = paper[(paper.cost_c == 2) & (paper.fill == "next minute")].iloc[0]
    tests.append(dict(Test="paper rule 2c next-minute: mean P&L per $", Inst="POOLED", n=int(prim.n),
                      effect=prim.mean_pnl_per_usd, t=np.nan, p=prim.p, h1=prim.h1, h2=prim.h2))
    tr2 = trades_all[(0.02, 1)]
    by_inst = tr2.groupby("inst").agg(n=("pnl", "size"), hit=("pnl", lambda s: (s > 0).mean()),
                                      mean_pnl=("pnl", "mean"), median_vol=("vol", "median")).reset_index()

    # ---- capacity (trades sample) ----
    trs = PC.cached("data/lag_trades.pkl", lambda: trades_sample(mk, tr2))
    capr = []
    for t in tr2[tr2.token.isin(trs)].itertuples():
        d = trs[t.token]
        if d.empty:
            continue
        t_e = pd.Timestamp(f"{t.date} 09:30", tz=NY).timestamp() + 60 * t.m
        t_c = pd.Timestamp(f"{t.date} 16:00", tz=NY).timestamp()
        day = d[(d.ts >= t_c - 390 * 60) & (d.ts < t_c)]
        notional = day["size"] * day.price
        near = (day.ts >= t_e - 300) & (day.ts <= t_e + 300)
        capr.append(dict(usd_pm5min=notional[near].sum(), usd_entry_to_close=notional[day.ts >= t_e].sum(),
                         usd_session=notional.sum(), median_trade_usd=notional.median() if len(day) else np.nan,
                         minutes_with_trade=day.ts.floordiv(60).nunique() / 390))
    capr = pd.DataFrame(capr)

    # ---- verdict ----
    res = pd.DataFrame(tests)
    ran = res[res.p.notna()].copy()
    ran["Holm p"] = holm(ran.p.reset_index(drop=True)).values
    ran["same sign halves"] = np.sign(ran.h1) == np.sign(ran.h2)
    ran["Pass"] = (ran["Holm p"] < 0.05) & ran["same sign halves"]
    write(covt, cov, cal_rows, calt, ran, res[res.p.isna()], xc, gap_rows, hl, paper, by_inst, capr)
    print(ran[ran.Inst == "POOLED"][["Test", "n", "effect", "t", "Holm p", "h1", "h2", "Pass"]].to_string())
    print(paper.to_string())


def write(covt, cov, cal_rows, calt, ran, skipped, xc, gap_rows, hl, paper, by_inst, capr):
    pre = open(REPORT, encoding="utf-8").read().split(MARK)[0]
    f = lambda d, ff=".4f": d.to_markdown(index=False, floatfmt=ff)
    show = ["Test", "Inst", "n", "effect", "t", "p", "Holm p", "h1", "h2", "same sign halves", "Pass"]
    pooled = ran[ran.Inst == "POOLED"]
    per = ran[ran.Inst != "POOLED"]
    cq = capr.describe(percentiles=[.25, .5, .75]).T[["count", "25%", "50%", "75%", "mean"]].reset_index() if len(capr) else pd.DataFrame()
    out = [pre.rstrip() + "\n", f"{MARK} on {dt.date.today()} -->\n",
           "## 1. Coverage\n",
           f"{len(cov)} resolved markets with a full session, sigma and >= 30 CLOB points; "
           f"{int(cov.both.sum()):,} market-minutes with both a PM price and a stock price (of {389 * len(cov):,}). "
           "`pm_moves_per_day` = median count of minutes in which the history price changed.\n", f(covt, ".1f"), "\n",
           "## 2. Fair-value calibration\n", f(pd.DataFrame(cal_rows)), "\n",
           "Pooled over the snapshots, by fair-value decile:\n", calt.to_markdown(index=False, floatfmt=".3f"), "\n",
           "## 3. Lag tests (Holm over all tests incl. per instrument and the paper rule)\n",
           f"**{int(ran.Pass.sum())} of {len(ran)} tests pass.** Pooled:\n", f(pooled[show]), "\n",
           "a/a' effect = share of the gap closed over k minutes; b/c effect = stock bp per 10pp; c1 = slope of dp on "
           "summed past df.\n",
           "Per instrument (only passing rows shown; full count above):\n",
           f(per[per.Pass][show]) if per.Pass.any() else "None pass.", "\n",
           "Per-instrument a'(5) slopes (descriptive):\n",
           f(per[per.Test.str.startswith("a' ") & per.Test.str.contains(r"t\+5\)")][["Inst", "n", "effect", "t", "Holm p", "Pass"]]), "\n",
           "Not run (n < 30): " + (", ".join(f"{r.Test}/{r.Inst}" for r in skipped.itertuples()) or "none") + "\n",
           "Cross-correlation of 1-minute changes (positive lag L: the stock/fair move happened L minutes BEFORE the PM move):\n",
           f(xc), "\n",
           "## 4. Gaps |fair - PM|\n", f(pd.DataFrame(gap_rows)), "\n", "AR(1) per minute:\n", f(pd.DataFrame(hl)), "\n",
           "## 5. Paper rule (one trade per market; |fair - ask/bid| > 5pp, T >= 30; exit at |gap| < 1pp or resolution)\n",
           f(paper), "\n", "By instrument (2c, next-minute fill):\n", f(by_inst), "\n",
           "Capacity, trades sample (public trades endpoint, USD notional = size x price, both outcomes):\n",
           f(cq, ".2f") if len(cq) else "No trades fetched.", "\n"]
    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def selfcheck():
    assert abs(fair(np.array([100.0]), 100.0, 0.02, np.array([195]))[0] - 0.5) < 1e-12
    assert np.isnan(fair(np.array([101.0]), 100.0, 0.02, np.array([0]))[0])
    assert list(runs(np.array([1, 1, 0, 1, 0, 0, 1, 1, 1], bool))) == [2, 1, 3]
    print("selfcheck ok")


if __name__ == "__main__":
    selfcheck() if "--selfcheck" in sys.argv else main()
