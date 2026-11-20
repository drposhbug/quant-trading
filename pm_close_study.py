"""Can Polymarket predict a stock's CLOSE on the day (pre-open / intraday)? Appends results to reports/pm_close_results.md
below its pre-registration block (section 0, written before any data was loaded). Study only: model.py stays frozen.
Run: python pm_close_study.py [--refresh] | --selfcheck      (caches: data/pm_close_*.pkl; data/ is gitignored)

Data: Polymarket gamma /events/slug (daily "<tk>-up-or-down-on-<month>-<d>-<yyyy>", monthly "<tk>-above-in-<month>-<yyyy>"),
CLOB prices-history (1-min for daily markets, hourly for ladders, windows <= 14 days). Alpaca SIP bars, read-only.
"""
import datetime as dt
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests
from scipy.stats import chi2

import pm_study as P
from backtest import stationary_bootstrap_idx
from correlations import holm, pval

P.UA = {"User-Agent": "quant-research-monitor"}  # pm_study.get reads this global at call time
GAMMA, CLOB = P.GAMMA, P.CLOB
NY = "America/New_York"
REFRESH = "--refresh" in sys.argv
REPORT = "reports/pm_close_results.md"
MARK = "<!-- RESULTS BELOW ARE WRITTEN BY pm_close_study.py"
# Polymarket prefix -> traded instrument. No daily markets exist for AVGO, TSM, AMD, ORCL (checked via public-search).
DAILY = dict(tsla="TSLA", nvda="NVDA", aapl="AAPL", msft="MSFT", googl="GOOGL", amzn="AMZN", meta="META", spcx="SPCX",
             spx="SPY", ndx="QQQ", qqq="QQQ")
LADDER = ["tsla", "nvda", "aapl", "msft", "googl", "amzn", "meta", "avgo", "tsm", "amd", "orcl", "spcx", "spx", "ndx"]
SNAPS = {"09:25": 1.0, "10:00": 360 / 390, "15:00": 60 / 390}  # snapshot -> fraction of session still to come
FIRST, LAST = dt.date(2025, 6, 1), dt.date(2026, 11, 19)
COST = 0.0002  # per side
VOLMIN = 5000
N01 = NormalDist()
Phi = np.vectorize(N01.cdf)


def cached(path, fn):
    if os.path.exists(path) and not REFRESH:
        return pd.read_pickle(path)  # written only by this script
    out = fn()
    os.makedirs("data", exist_ok=True)
    pd.to_pickle(out, path)
    return out


def event(slug):
    try:
        return P.get(f"{GAMMA}/events/slug/{slug}")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def history(token, a, b, fid):
    pts = []
    for s in range(int(a.timestamp()), int(b.timestamp()), 14 * 86400):
        pts += P.get(f"{CLOB}/prices-history", market=token, startTs=s, endTs=min(s + 14 * 86400, int(b.timestamp())),
                     fidelity=fid).get("history", [])
    s = pd.Series({pd.Timestamp(p["t"], unit="s", tz="UTC"): float(p["p"]) for p in pts}, dtype=float)
    return s[~s.index.duplicated()].sort_index()


def at(s, t, stale):
    """Last point stamped at or before t (never after), no older than `stale`."""
    s = s[(s.index <= t) & (s.index > t - stale)]
    return float(s.iloc[-1]) if len(s) else np.nan


# ---------------- Alpaca (read-only historical bars) ----------------
def akeys():
    env = dict(os.environ)
    if os.path.exists(".env"):
        for line in open(".env"):
            k, _, v = line.strip().partition("=")
            env.setdefault(k, v.strip().strip("'\""))
    return {"APCA-API-KEY-ID": env["ALPACA_API_KEY"], "APCA-API-SECRET-KEY": env["ALPACA_SECRET_KEY"]}


def aget(url, params):
    for i in range(6):
        r = requests.get(url, params=params, headers=akeys(), timeout=60)
        if r.status_code == 429:
            time.sleep(2 ** i)
            continue
        if r.status_code != 200:
            raise SystemExit(f"Alpaca {r.status_code} on {url}")  # never echo headers (keys)
        time.sleep(0.35)
        return r.json()
    raise SystemExit("Alpaca rate limit")


def abars(sym, tf, start, end, adj):
    rows, tok = [], None
    while True:
        p = dict(timeframe=tf, start=f"{start}T00:00:00Z", end=f"{end}T23:59:00Z", feed="sip", adjustment=adj, limit=10000)
        if tok:
            p["page_token"] = tok
        j = aget(f"https://data.alpaca.markets/v2/stocks/{sym}/bars", p)
        rows += j.get("bars") or []
        tok = j.get("next_page_token")
        if not tok:
            break
    d = pd.DataFrame(rows)
    if d.empty:
        return d
    d["ts"] = pd.to_datetime(d["t"], utc=True).dt.tz_convert(NY)
    return d.rename(columns=dict(o="open", c="close"))[["ts", "open", "close"]]


def calendar():
    c = pd.DataFrame(aget("https://paper-api.alpaca.markets/v2/calendar", {"start": "2024-06-01", "end": str(LAST)}))
    return c.set_index(pd.to_datetime(c["date"]).dt.date)[["open", "close"]]


def intraday_points(m):
    """Per session date: last pre-market trade before 09:25, price at 10:00 and 15:00 (close of last bar starting before)."""
    m = m.assign(date=m.ts.dt.date, hm=m.ts.dt.strftime("%H:%M"))
    pre = m[(m.hm >= "04:00") & (m.hm < "09:25")].groupby("date").close.last()
    reg = m[m.hm >= "09:30"]
    return pd.DataFrame({"pre_0925": pre, "px_1000": reg[reg.hm < "10:00"].groupby("date").close.last(),
                         "px_1500": reg[reg.hm < "15:00"].groupby("date").close.last()})


def stock_data(syms, cal):
    def one(sym):
        d = abars(sym, "1Day", "2024-06-01", LAST, "split")
        d["date"] = d.ts.dt.date
        d = d.set_index("date")[["open", "close"]]
        d["prev_close"] = d.close.shift()
        d["sigma_oc"] = np.log(d.close / d.open).rolling(60, min_periods=20).std().shift()
        raw = abars(sym, "1Day", "2024-06-01", LAST, "raw").assign(date=lambda x: x.ts.dt.date).set_index("date").close
        d["raw_close"] = raw
        d["sigma_d"] = np.log(raw / raw.shift()).rolling(60, min_periods=20).std()  # through day t: known at its close
        pts = intraday_points(abars(sym, "1Min", "2025-09-01", LAST, "split"))
        print(f"  alpaca {sym}: {len(d)} days, {len(pts)} intraday days")
        return d.join(pts)
    return {s: one(s) for s in syms}


# ---------------- Polymarket inventory ----------------
def slug_day(prefix, d):
    return f"{prefix}-up-or-down-on-{d:%B}-{d.day}-{d.year}".lower()


def daily_inventory(days):
    keys = [(p, d) for p in DAILY for d in days]
    with ThreadPoolExecutor(8) as ex:
        evs = list(ex.map(lambda k: event(slug_day(*k)), keys))
    rows = []
    for (p, d), e in zip(keys, evs):
        if not e or not e.get("markets"):
            continue
        m = e["markets"][0]
        try:
            px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            outs, tok = json.loads(m["outcomes"]), json.loads(m["clobTokenIds"])
        except (KeyError, ValueError, TypeError):
            continue
        desc = m.get("description") or ""
        rule = ("prev close" if re.search(r"higher than the .*clos\w+ price .* on the most recent prior trading day", desc, re.S | re.I)
                else "open" if re.search(r"open", desc.split(".")[0], re.I) else "other")
        rows.append(dict(inst=p, date=d, token=tok[outs.index("Up")] if "Up" in outs else tok[0],
                         y=px[outs.index("Up")] if len(px) == 2 and "Up" in outs else np.nan,
                         resolved=m.get("umaResolutionStatus") == "resolved" or m.get("closed", False),
                         vol=float(m.get("volumeNum") or 0), start=P.ts(m.get("startDate") or e["startDate"]), rule=rule,
                         source=re.search(r"resolution source for this market (?:is|will be) (?:the )?([^,.]+)", desc).group(1)
                         if re.search(r"resolution source for this market (?:is|will be) (?:the )?([^,.]+)", desc) else ""))
    return pd.DataFrame(rows)


def daily_hist(inv):
    def one(r):
        d = r.date
        a = pd.Timestamp(dt.datetime(d.year, d.month, d.day, 8, 0), tz=NY).tz_convert("UTC")
        b = pd.Timestamp(dt.datetime(d.year, d.month, d.day, 15, 1), tz=NY).tz_convert("UTC")
        return history(r.token, max(a, r.start), b, 1)
    with ThreadPoolExecutor(8) as ex:
        return dict(zip(inv.token, ex.map(one, [r for r in inv.itertuples()])))


def ladder_inventory():
    months = pd.period_range("2025-01", "2026-10", freq="M")
    keys = [(p, mo) for p in LADDER for mo in months]
    with ThreadPoolExecutor(8) as ex:
        evs = list(ex.map(lambda k: event(f"{k[0]}-above-in-{k[1].strftime('%B').lower()}-{k[1].year}"), keys))
    rows = []
    for (p, mo), e in zip(keys, evs):
        for m in (e or {}).get("markets", []):
            try:
                px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                tok = json.loads(m["clobTokenIds"])
                K = float(re.sub(r"[^\d.]", "", m.get("groupItemTitle") or ""))
            except (KeyError, ValueError, TypeError):
                continue
            if len(px) != 2 or max(px) < 0.99:
                continue
            rows.append(dict(inst=p, month=str(mo), K=K, token=tok[0], y=px[0], vol=float(m.get("volumeNum") or 0),
                             start=P.ts(m.get("startDate") or e["startDate"]), end=P.ts(m["endDate"]),
                             rule_last_day=bool(re.search(r"final trading day of", m.get("description") or ""))))
    return pd.DataFrame(rows)


def ladder_hist(lad):
    def one(r):
        return history(r.token, max(r.start, r.end - pd.Timedelta(days=24)), r.end, 60)
    with ThreadPoolExecutor(8) as ex:
        return dict(zip(lad.token, ex.map(one, [r for r in lad.itertuples()])))


# ---------------- statistics ----------------
def dk(y, x, g, lags=5):
    """OLS y = a (+ b x) with Driscoll-Kraay SE (Newey-West on per-group score sums; groups = dates, sorted).
    Returns (coef, t) for b, or for a when x is None. One obs per group -> plain Newey-West."""
    y = np.asarray(y, float)
    X = np.ones((len(y), 1)) if x is None else np.column_stack([np.ones(len(y)), np.asarray(x, float)])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    sc = pd.DataFrame(X * (y - X @ beta)[:, None]).groupby(np.asarray(g)).sum().sort_index().values
    S = sc.T @ sc
    for l in range(1, min(lags, len(sc) - 1) + 1):
        G = sc[l:].T @ sc[:-l]
        S += (1 - l / (lags + 1)) * (G + G.T)
    inv = np.linalg.inv(X.T @ X)
    k = X.shape[1] - 1
    return beta[k], beta[k] / math.sqrt((inv @ S @ inv)[k, k])


def test_row(d, ycol, xcol, lags=5, gcol="date", minn=30):
    d = d.dropna(subset=[ycol] + ([xcol] if xcol else []))
    if len(d) < minn or (xcol and d[xcol].std() == 0):
        return dict(n=len(d))
    d = d.sort_values(gcol)
    b, t = dk(d[ycol], d[xcol] if xcol else None, d[gcol], lags)
    cut = d[gcol].iloc[len(d) // 2]
    h1, h2 = d[d[gcol] < cut], d[d[gcol] >= cut]
    halves = [dk(h[ycol], h[xcol] if xcol else None, h[gcol], lags)[0] if len(h) > 5 else np.nan for h in (h1, h2)]
    out = dict(n=len(d), start=d[gcol].iloc[0], end=d[gcol].iloc[-1], effect=b, t=t, p=pval(t), h1=halves[0], h2=halves[1])
    if xcol:
        out["rank_ic"] = d[xcol].rank().corr(d[ycol].rank())
    return out


def survival(K, p):
    """Ladder YES prices -> non-increasing P(close > K), clipped to [0, 1]."""
    o = np.argsort(K)
    return np.asarray(K)[o], np.clip(np.minimum.accumulate(np.asarray(p, float)[o]), 0, 1)


# ---------------- build panel ----------------
def panel(inv, hist, stocks, cal):
    rows = []
    for r in inv.itertuples():
        st = stocks[DAILY[r.inst]]
        if r.rule != "prev close":  # 2025-10-15 only: that first batch resolved close vs the SAME day's open
            continue
        if r.date not in st.index or str(cal.loc[r.date, "close"]) != "16:00":
            continue
        s = st.loc[r.date]
        h = hist.get(r.token, pd.Series(dtype=float))
        row = dict(inst=r.inst, sym=DAILY[r.inst], date=r.date, y=r.y, vol=r.vol)
        for T, f in SNAPS.items():
            t = pd.Timestamp(f"{r.date} {T}", tz=NY).tz_convert("UTC")
            row[f"p_{T}"] = at(h, t, pd.Timedelta(minutes=60)) if len(h) else np.nan
            ref = {"09:25": s.pre_0925, "10:00": s.px_1000, "15:00": s.px_1500}[T]
            sd = s.sigma_oc * math.sqrt(f)
            row[f"b_{T}"] = (0.5 if T == "09:25" else np.nan) if not (ref == ref and sd == sd and sd > 0) \
                else N01.cdf(math.log(ref / s.prev_close) / sd)
            row[f"r_{T}"] = s.close / {"09:25": s.open, "10:00": s.px_1000, "15:00": s.px_1500}[T] - 1
        rows.append(row)
    d = pd.DataFrame(rows)
    d = d[d.y.isin([0.0, 1.0])].copy()  # ties (50-50) and unresolved dropped
    for T in SNAPS:
        d[f"d_{T}"] = (d[f"b_{T}"] - d.y) ** 2 - (d[f"p_{T}"] - d.y) ** 2
        d[f"x_{T}"] = d[f"p_{T}"] - d[f"b_{T}"]
    return d


def ladder_panel(lad, lh, stocks, cal):
    tdays = [d for d in cal.index]
    sym = {p: DAILY.get(p, p.upper()) for p in LADDER}
    rows = []
    for (inst, month), g in lad.groupby(["inst", "month"]):
        last = g.end.max().tz_convert(NY).date()
        st = stocks.get(sym[inst]) if inst not in ("spx", "ndx") else None  # index-level strikes: no index bars here
        if st is None or last not in tdays or last not in st.index:
            continue
        i = tdays.index(last)
        C = st.loc[last, "raw_close"]
        for h in (1, 5, 10):
            sd = tdays[i - h]
            if sd not in st.index:
                continue
            t = pd.Timestamp(f"{sd} {cal.loc[sd, 'close']}", tz=NY).tz_convert("UTC")
            pr = np.array([at(lh.get(tok, pd.Series(dtype=float)), t, pd.Timedelta(days=2)) for tok in g.token])
            ok = ~np.isnan(pr)
            if ok.sum() < 4:
                continue
            K, S = survival(g.K.values[ok], pr[ok])
            y = g.y.values[ok][np.argsort(g.K.values[ok])]
            S0, sig = st.loc[sd, "raw_close"], st.loc[sd, "sigma_d"] * math.sqrt(h)
            Sb = Phi((np.log(S0 / K) - sig ** 2 / 2) / sig)
            rows.append(dict(inst=inst, month=month, h=h, n_strikes=len(K), vol=g.vol.sum(), close=C,
                             brier_pm=np.mean((S - y) ** 2), brier_base=np.mean((Sb - y) ** 2),
                             pit_pm=float(np.interp(C, K, 1 - S)), pit_base=N01.cdf((math.log(C / S0) + sig ** 2 / 2) / sig)))
    d = pd.DataFrame(rows)
    d["d"] = d.brier_base - d.brier_pm
    return d


# ---------------- tests ----------------
def run_tests(d, lp):
    rows = []
    insts = sorted(d.inst.unique())
    for T in SNAPS:
        for grp in insts + ["POOLED"]:
            x = d if grp == "POOLED" else d[d.inst == grp]
            rows.append(dict(Test=f"A Brier gain PM vs baseline @{T}", Inst=grp, **test_row(x, f"d_{T}", None)))
            rows.append(dict(Test=f"B (p_PM-p_base) -> r({T}->close)", Inst=grp, **test_row(x, f"r_{T}", f"x_{T}")))
    for h in (1, 5, 10):
        x = lp[lp.h == h].assign(date=lambda z: z.month)
        rows.append(dict(Test=f"D ladder Brier gain PM vs lognormal, h={h}d", Inst="POOLED", **test_row(x, "d", None, 1, minn=10)))
    return rows


def paper_rule(d):
    x = d.dropna(subset=["p_09:25", "r_09:25"]).copy()
    x["sig"] = (x["p_09:25"] > 0.60).astype(float)
    x["rule"] = x.sig * (x["r_09:25"] - 2 * COST)
    x["always"] = x["r_09:25"] - 2 * COST
    book = x.groupby("date")[["rule", "always"]].mean().sort_index()
    sh = lambda r: r.mean() / r.std() * math.sqrt(252) if r.std() > 0 else 0.0
    idx = stationary_bootstrap_idx(len(book), 2000, L=5)
    R, A = book.rule.values[idx], book.always.values[idx]
    sr = lambda M: M.mean(1) / M.std(1) * math.sqrt(252)
    sR, sA = sr(R), sr(A)
    P1, P2 = float((sR <= 0).mean()), float((sR - sA <= 0).mean())
    half = book.index[len(book) // 2]
    b1, b2 = book[book.index < half], book[book.index >= half]
    stats = dict(days=len(book), trades=int(x.sig.sum()), obs=len(x), hit=float((x[x.sig == 1]["r_09:25"] > 0).mean()),
                 sharpe_rule=sh(book.rule), sharpe_always=sh(book.always), sharpe_flat=0.0,
                 mean_rule_bp=book.rule.mean() * 1e4, mean_always_bp=book.always.mean() * 1e4,
                 cum_rule=float((1 + book.rule).prod() - 1), cum_always=float((1 + book.always).prod() - 1),
                 h1=(sh(b1.rule), sh(b1.always)), h2=(sh(b2.rule), sh(b2.always)), P1=P1, P2=P2)
    tests = [dict(Test="C rule Sharpe > 0 (bootstrap)", Inst="BOOK", n=len(book), effect=stats["sharpe_rule"], t=np.nan,
                  p=min(1, 2 * min(P1, 1 - P1)), h1=stats["h1"][0], h2=stats["h2"][0], start=book.index[0], end=book.index[-1]),
             dict(Test="C rule Sharpe - always-long Sharpe (paired bootstrap)", Inst="BOOK", n=len(book),
                  effect=stats["sharpe_rule"] - stats["sharpe_always"], t=np.nan, p=min(1, 2 * min(P2, 1 - P2)),
                  h1=stats["h1"][0] - stats["h1"][1], h2=stats["h2"][0] - stats["h2"][1], start=book.index[0], end=book.index[-1])]
    return stats, tests


def finalize(rows):
    res = pd.DataFrame(rows)
    ran = res[res.p.notna()].copy()
    ran["Holm p"] = holm(ran.p.reset_index(drop=True)).values
    ran["same sign halves"] = np.sign(ran.h1) == np.sign(ran.h2)
    ran["Pass"] = (ran["Holm p"] < 0.05) & ran["same sign halves"]
    return ran, res[res.p.isna()][["Test", "Inst", "n"]]


def calib_table(d, col):
    x = d.dropna(subset=[col])
    b = pd.cut(x[col], np.linspace(0, 1, 11), include_lowest=True)
    return x.groupby(b, observed=True).agg(n=("y", "size"), mean_p=(col, "mean"), freq_up=("y", "mean"))


# ---------------- report ----------------
VERDICT = """## 7. Verdict and caveats (written after the first run, 2026-11-20; numbers refer to the tables above)

**Polymarket is not a usable pre-open or intraday close predictor for these names. 0 of 71 tests pass.**

- **What the markets price.** Since 2025-10-16 every daily market resolves on close vs the PREVIOUS close. So the
  09:25 price is mostly the overnight gap: its correlation with the gap-only random-walk baseline is 0.94 at 09:25
  and 0.98 at 15:00. At 09:25 Polymarket is slightly WORSE than the baseline (pooled Brier 0.216 vs 0.213, gain t = −1.67).
  It is a little overconfident on "Up": the 0.5-0.6 bin resolves Up 50% of the time, and the 0.8-0.9 bin 78%.
  At 10:00 and 15:00 it ties the baseline (gain t = 1.19 and 0.32).
- **Tradable part.** (p_PM − p_base) at 09:25 does not predict open→close: pooled slope ≈ 0.1 bp per +10 pp
  (t = 0.14), rank IC 0.001. The 10:00 and 15:00 pooled slopes are small and positive (≈ 1 bp and 0.3 bp per
  +10 pp to the close, t ≈ 2.3 unadjusted, Holm 1.0), much less than a 4 bp round trip. Treat it as a weak
  hypothesis to watch, not a signal.
  The best single row (META 15:00, t = 3.3, Holm 0.07) is one of 71 tests.
- **Paper rule (long at the open iff p_0925 > 0.60).** Net Sharpe −0.57 vs −0.94 for always-long-at-open, over 272
  days. It loses less only because it is in the market less: open→close was a losing hold in this period
  (−6.5 bp/day after costs; the stocks' gains came overnight). Bootstrap P(rule ≤ always) = 0.29, and its edge flips
  sign between the halves. On markets with ≥ $5k volume the rule's Sharpe is −2.1.
- **Monthly ladders.** No better than a lognormal with trailing 60-day vol (Brier gain −0.017 / +0.004 / −0.006 at
  1 / 5 / 10 days, n = 81 ticker-months over 11 months, all p > 0.17). The h = 1 loss is concentrated in months
  whose last day follows an earnings release (Oct/Apr: AMZN, MSFT, GOOGL), where the ladder correctly widens but
  the realised close landed in the middle. PIT at 10 days is hump-shaped (chi-square p = 0.004): the ladders are too
  wide, i.e. underconfident, not sharp.
- **Caveats.** About 13 months, 2,421 market-days, roughly 270 per name. The MDE at the Holm level is |corr| ≈ 0.08
  pooled and ≈ 0.25 per name, so the test rules out large effects only. The volumes are tiny: median lifetime volume
  is $3.5-6k per single-stock market (SPX median $92k) and SPCX's is $464, so a few hundred dollars can move a
  price. Prices are the CLOB's sampled price (no bid/ask). The source moved from NASDAQ/WSJ to Pyth 1-minute
  candles on 2026-03-25. The 2025-10-15 batch (close vs the same day's OPEN) is excluded. There are no daily markets
  for AVGO, TSM, AMD or ORCL, and QQQ has only 23 days (not run). The baseline is deliberately simple. A fitted
  one would make Polymarket look worse, not better.

**What to log going forward (cheap, forward-only, no model change).** Every trading day, snapshot each daily
Up/Down market's best bid/ask/size and last price at 09:25, 10:00 and 15:00 ET, plus the stock's last pre-market or
intraday trade at the same second. Snapshot the monthly ladders once a day at 16:00 with bid/ask. Re-run this
script unchanged at 12 months of logs. Only the 10:00/15:00 pooled B tests are worth re-testing, and they should
be pre-registered then as the only two tests.
"""

def fmt(df, **kw):
    return df.to_markdown(index=False, floatfmt=".4f", **kw)


def write(inv, lad, d, lp, ran, skipped, C, sens):
    pre = open(REPORT, encoding="utf-8").read().split(MARK)[0]
    show = ["Test", "Inst", "n", "start", "end", "effect", "t", "p", "Holm p", "h1", "h2", "same sign halves", "Pass"]
    invt = inv.groupby("inst").agg(markets=("date", "size"), first=("date", "min"), last=("date", "max"),
                                   resolved_up_down=("y", lambda s: int(s.isin([0, 1]).sum())),
                                   median_vol=("vol", "median"), vol_ge_5k=("vol", lambda s: int((s >= VOLMIN).sum())),
                                   rule=("rule", lambda s: ", ".join(f"{k} {v}" for k, v in s.value_counts().items())),
                                   source=("source", lambda s: s.mode().iat[0] if len(s) else "")).reset_index()
    used = d.groupby("inst").agg(panel=("y", "size"), with_p0925=("p_09:25", "count"), up_rate=("y", "mean")).reset_index()
    invt = invt.merge(used, on="inst", how="left")
    ladt = lad.groupby("inst").agg(months=("month", "nunique"), first=("month", "min"), last=("month", "max"),
                                   strikes=("K", "size"), median_vol=("vol", "median"),
                                   last_day_rule=("rule_last_day", "mean")).reset_index() if len(lad) else pd.DataFrame()
    desc = []
    for T in SNAPS:
        x = d.dropna(subset=[f"p_{T}", f"b_{T}"])
        desc.append(dict(snapshot=T, n=len(x), brier_PM=((x[f"p_{T}"] - x.y) ** 2).mean(),
                         brier_base=((x[f"b_{T}"] - x.y) ** 2).mean(), brier_50=0.25,
                         corr_PM_base=x[f"p_{T}"].corr(x[f"b_{T}"]),
                         sd_resid_pp=100 * x[f"x_{T}"].std()))
    pits = []
    for h in (1, 5, 10):
        for c in ("pit_pm", "pit_base"):
            cnt = np.histogram(lp[lp.h == h][c].clip(0, 1), np.linspace(0, 1, 11))[0]
            e = cnt.sum() / 10
            pits.append(dict(h=h, forecast=c[4:], n=int(cnt.sum()), deciles=" ".join(map(str, cnt)),
                             chi2_p=float(1 - chi2.cdf(((cnt - e) ** 2 / e).sum(), 9)) if e > 0 else np.nan))
    lsum = lp.groupby("h").agg(n=("d", "size"), months=("month", "nunique"), brier_pm=("brier_pm", "mean"),
                               brier_base=("brier_base", "mean"), gain=("d", "mean")).reset_index()
    npass = int(ran.Pass.sum())
    out = [pre.rstrip() + "\n", MARK + " on " + str(dt.date.today()) + " -->\n",
           "## 1. Inventory\n",
           f"Daily Up/Down markets found by enumerating every trading day {FIRST}..{LAST} x prefix (gamma /events/slug). "
           "`rule` = what the resolution text compares against (parsed from the description). `panel` = resolved Up/Down "
           "rows with stock data on a full session; `with_p0925` = a CLOB point within 60 min before 09:25 ET.\n",
           fmt(invt), "\n",
           "Monthly ladders (\"close above $K end of <month>\", resolve on the official close of the last trading day of "
           "the month; source Yahoo Finance \"Close\").\n", fmt(ladt) if len(ladt) else "None found.", "\n",
           "## 2. Results (Holm over all tests run)\n",
           f"**{npass} of {len(ran)} tests pass** (Holm p < 0.05 and same sign in both chronological halves).\n",
           fmt(ran[show].sort_values("p")), "\n",
           "B `effect` = slope of the return on (p_PM − p_base) (return per 1.0 of probability; ×1e3 = bp per +10pp). "
           "A `effect` = mean Brier improvement of PM over the baseline (positive = PM better). D `effect` = mean Brier "
           "improvement of the ladder over the lognormal (positive = ladder better).\n",
           "Rank IC for B tests (descriptive):\n",
           fmt(ran[ran.Test.str.startswith("B")][["Test", "Inst", "n", "rank_ic"]].sort_values(["Test", "Inst"])), "\n",
           "Tests not run (too few observations): " + (", ".join(f"{r.Test}/{r.Inst} (n={r.n})" for r in skipped.itertuples()) or "none") + "\n",
           "## 3. How much does Polymarket know beyond the price at the snapshot? (descriptive)\n",
           fmt(pd.DataFrame(desc)), "\n",
           "Calibration of p_PM at 09:25 (pooled):\n", calib_table(d, "p_09:25").reset_index().to_markdown(index=False, floatfmt=".3f"), "\n",
           "Calibration of the gap-only baseline at 09:25 (pooled):\n", calib_table(d, "b_09:25").reset_index().to_markdown(index=False, floatfmt=".3f"), "\n",
           "## 4. Paper rule (fixed): long at the open iff p_PM(09:25) > 0.60, else flat; 2 bp per side\n",
           fmt(pd.DataFrame([{k: (f"{v[0]:.2f} / {v[1]:.2f}" if isinstance(v, tuple) else v) for k, v in C.items()}])),
           "\n`h1`/`h2` = (rule Sharpe / always-long Sharpe) in each half. P1 = bootstrap P(Sharpe_rule ≤ 0); "
           "P2 = P(Sharpe_rule ≤ Sharpe_always). Flat = 0 return, Sharpe 0.\n",
           "## 5. Monthly ladders\n", fmt(lsum), "\n",
           "PIT deciles (counts in 0-10%, ..., 90-100%; uniform if calibrated; chi-square, 9 df):\n", fmt(pd.DataFrame(pits)), "\n",
           f"## 6. Sensitivity: only markets with lifetime volume >= ${VOLMIN:,} (not in the pass rule)\n",
           fmt(sens[show[:8]]) if len(sens) else "Too few markets.", "\n",
           VERDICT]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def main():
    cal = cached("data/pm_close_calendar.pkl", calendar)
    days = [d for d in cal.index if FIRST <= d <= LAST]
    inv = cached("data/pm_close_daily_inv.pkl", lambda: daily_inventory(days))
    print("daily markets:", len(inv))
    lad = cached("data/pm_close_ladder_inv.pkl", ladder_inventory)
    print("ladder strikes:", len(lad))
    hist = cached("data/pm_close_daily_hist.pkl", lambda: daily_hist(inv))
    lh = cached("data/pm_close_ladder_hist.pkl", lambda: ladder_hist(lad))
    syms = sorted(set(DAILY.values()) | {p.upper() for p in LADDER if p not in DAILY})
    stocks = cached("data/pm_close_stocks.pkl", lambda: stock_data(syms, cal))
    d = panel(inv, hist, stocks, cal)
    lp = ladder_panel(lad, lh, stocks, cal)
    C, ctests = paper_rule(d)
    ran, skipped = finalize(run_tests(d, lp) + ctests)
    dv, lv = d[d.vol >= VOLMIN], lp[lp.vol >= VOLMIN]
    sens = pd.DataFrame([dict(Test=r["Test"], Inst=r["Inst"], **{k: v for k, v in r.items() if k not in ("Test", "Inst")})
                         for r in run_tests(dv, lv) if r["Inst"] == "POOLED"] + paper_rule(dv)[1])
    sens = sens[sens.p.notna()] if "p" in sens else sens
    write(inv, lad, d, lp, ran, skipped, C, sens)
    print(ran.sort_values("p")[["Test", "Inst", "n", "effect", "t", "p", "Holm p", "Pass"]].head(25).to_string())


def selfcheck():
    s = pd.Series([0.4, 0.9], index=pd.DatetimeIndex(["2026-01-21 14:24:59", "2026-01-21 14:25:01"], tz="UTC"))
    assert at(s, pd.Timestamp("2026-01-21 14:25", tz="UTC"), pd.Timedelta("1h")) == 0.4  # never after T
    assert np.isnan(at(s, pd.Timestamp("2026-01-21 16:00", tz="UTC"), pd.Timedelta("1h")))  # stale -> missing
    K, S = survival([20, 10, 30], [0.5, 0.4, 0.6])
    assert list(K) == [10, 20, 30] and list(S) == [0.4, 0.4, 0.4]  # non-increasing
    rng = np.random.default_rng(0)
    x = rng.normal(size=4000)
    b, t = dk(0.3 * x + rng.normal(size=4000), x, np.arange(4000))
    assert abs(b - 0.3) < 0.05 and t > 10
    assert slug_day("tsla", dt.date(2026, 2, 3)) == "tsla-up-or-down-on-february-3-2026"
    m = pd.DataFrame({"ts": pd.DatetimeIndex(["2026-02-03 09:24", "2026-02-03 09:25", "2026-02-03 09:59", "2026-02-03 10:00"], tz=NY),
                      "open": 1.0, "close": [1.0, 2.0, 3.0, 4.0]})
    p = intraday_points(m).iloc[0]
    assert p.pre_0925 == 1.0 and p.px_1000 == 3.0  # bar starting 09:25 excluded; 10:00 bar excluded
    print("selfcheck ok")


if __name__ == "__main__":
    selfcheck() if "--selfcheck" in sys.argv else main()
