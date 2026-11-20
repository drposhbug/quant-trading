"""Prediction-market odds around SCHEDULED announcements (FOMC, CPI, mega-cap earnings, IPOs): do Kalshi/Polymarket odds
predict the announcement, and do they carry tradable information about the index/stock move? Study only (model frozen).
Writes reports/event_odds_results.md below its pre-registration block (section 0, written before any run).
Run: python event_odds_study.py [--refresh]        Self-check: python test_event_odds_study.py
Caches (data/ is gitignored, written only by this script): data/eo_*.pkl. Read-only reuse: data/pm_cal_kalshi.pkl
(Kalshi market lists, pm_calibration.py), data/pm_cal_ipo.pkl (Anthropic IPO legs), data/edgar_earnings.csv (8-K times).
"""
import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats as st

import pm_close_study as PC  # reused (not edited): Alpaca bars, CLOB history, at(), cached()
import pm_study as P
from correlations import holm
from events_study import FOMC
from pm_calibration import IPO_EVENTS, calib_table, logloss

P.UA = {"User-Agent": "quant-research-monitor"}
NY = "America/New_York"
REFRESH = "--refresh" in sys.argv
REPORT, MARK = "reports/event_odds_results.md", "<!-- RESULTS BELOW ARE WRITTEN BY event_odds_study.py"
START = pd.Timestamp("2023-01-01", tz="UTC")
HZ = {"1d": pd.Timedelta(days=1), "1h": pd.Timedelta(hours=1), "5m": pd.Timedelta(minutes=5)}
PCOLS = [f"p_{h}" for h in HZ]
STALE = pd.Timedelta(days=10)  # Kalshi candles only appear when the quote changes, so a standing quote can be days old
COST = 0.0002  # per side
TICKERS = ["tsla", "nvda", "aapl", "msft", "googl", "amzn", "meta", "avgo", "tsm", "amd", "orcl", "spcx"]
FOMC_D = {pd.Timestamp(d).date() for d in FOMC}
# 2025 shutdown: Sept CPI moved to 2025-10-24 after Kalshi closed trading on 10-15; October CPI was never published.
CPI_SKIP = ("-25SEP", "-25OCT")
MIN_DRIFT = {"FOMC": 0.5, "CPI": 0.005, "Earnings": 0.005}


def cached(path, fn):
    return PC.cached(path, fn)  # same convention as pm_close_study (pickle written only by this script)


# ---------------- leg parsing ----------------
def fed_bp(ticker):
    """Kalshi FEDDECISION leg suffix -> rate change in bp. H0 = hold, H25 = +25, C25 = -25, H26/C26/H>25 = beyond 25 (+-50)."""
    m = re.search(r"-([HC])(>?)(\d+)$", ticker)
    if not m:
        return np.nan
    n = int(m.group(3))
    n = 50 if (m.group(2) or n == 26) else n
    return n if m.group(1) == "H" else -n


def strike(ticker):
    m = re.search(r"-T(-?[\d.]+)$", ticker)
    return float(m.group(1)) if m else np.nan


# ---------------- inventory ----------------
def kalshi_legs():
    k = pd.read_pickle("data/pm_cal_kalshi.pkl")  # written by pm_calibration.py; read-only here
    k = k[k.series.isin(["KXFEDDECISION", "KXCPI", "KXCPIYOY"]) & (k.end >= START)].copy()
    k = k[~k.event.str.endswith(CPI_SKIP)]
    k["src"], k["type"] = "kalshi", k.series.map({"KXFEDDECISION": "FOMC", "KXCPI": "CPI", "KXCPIYOY": "CPI YoY"})
    day = k.end.dt.tz_convert(NY).dt.date
    k["T"] = [pd.Timestamp(dt.datetime.combine(d, dt.time(14) if t == "FOMC" else dt.time(8, 30)), tz=NY)
              for d, t in zip(day, k.type)]
    k = k[(k.type != "FOMC") | day.isin(FOMC_D)]
    k["x"] = [fed_bp(i) if t == "FOMC" else strike(i) for i, t in zip(k.id, k.type)]
    k["token"] = None
    return k[["src", "type", "event", "id", "token", "series", "hist", "y", "vol", "x", "T"]].reset_index(drop=True)


def search(queries, pat):
    out = set()
    for q in queries:
        for page in (1, 2, 3):
            d = P.get(f"{P.GAMMA}/public-search", q=q, limit_per_type=100, events_status="all", keep_closed_markets=1, page=page)
            out |= {e["slug"] for e in d.get("events", []) if re.search(pat, e["slug"])}
    return sorted(out)


def edgar():
    d = pd.read_csv("data/edgar_earnings.csv")  # events_study cache (8-K Item 2.02 acceptance times); read-only
    d["ts"] = pd.to_datetime(d.ts, utc=True).dt.tz_convert(NY)
    return d[~(d.ts.dt.month.isin([1, 4, 7, 10]) & (d.ts.dt.day <= 5))]  # drop Tesla delivery-number filings


def earnings_T(tk, day, ed):
    if tk == "TSM":  # 6-K filer, no 8-K: TSMC releases ~01:00-02:00 ET on the report date
        return pd.Timestamp(dt.datetime.combine(day, dt.time(0, 30)), tz=NY)
    g = ed[ed.name == tk]
    if g.empty:
        return pd.NaT
    gap = (g.ts.dt.date.map(lambda x: abs((x - day).days)))
    if gap.min() > 4:
        return pd.NaT
    t = g.ts.iloc[int(np.argmin(gap.values))]
    # The press release goes out at/after 16:00 and the 8-K follows minutes later (TSLA: up to 40 min); odds already
    # move in between, so an after-close filing is timed at 16:00 (T-5min = 15:55).
    close = t.normalize() + pd.Timedelta(hours=16)
    return close if close <= t < close + pd.Timedelta(hours=4) else t


def pm_legs(cpi_T):
    fed = search(["fed decision in", "fed interest rates", "fed rate decision", "fomc"], r"^(fed-decision-in-|fed-interest-rates-)")
    cpi = search(["inflation us monthly", "monthly inflation", "cpi"], r"inflation-us-monthly")
    ern = search([f"{t} quarterly earnings" for t in TICKERS] + [f"{t.upper()} earnings eps" for t in TICKERS],
                 rf"^({'|'.join(TICKERS)})-quarterly-earnings-")
    ed = edgar()
    fomc = np.array(sorted(FOMC_D))
    rows = []
    for typ, slugs in (("FOMC", fed), ("CPI", cpi), ("Earnings", ern)):
        for slug in slugs:
            e = PC.event(slug)
            for m in (e or {}).get("markets", []):
                try:
                    px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                    tok = json.loads(m["clobTokenIds"])[0]
                except (KeyError, ValueError, TypeError):
                    continue
                if len(px) != 2 or max(px) < 0.99 or not m.get("closed"):
                    continue  # unresolved / voided
                ref = P.ts(m.get("endDate") or m.get("closedTime").replace(" ", "T").replace("+00", "Z"))
                if typ == "FOMC":
                    d = fomc[np.argmin([abs((x - ref.date()).days) for x in fomc])]
                    T = pd.Timestamp(dt.datetime.combine(d, dt.time(14)), tz=NY) if abs((d - ref.date()).days) <= 10 else pd.NaT
                elif typ == "CPI":
                    c = [t for t in cpi_T if abs((t.date() - ref.date()).days) <= 7]
                    T = c[0] if c else pd.NaT
                else:
                    mm = re.match(r"^(\w+)-quarterly-earnings-(?:non)?gaap-eps-(\d\d)-(\d\d)-(\d{4})", slug)
                    T = earnings_T(mm.group(1).upper(), dt.date(int(mm.group(4)), int(mm.group(2)), int(mm.group(3))), ed) if mm else pd.NaT
                rows.append(dict(src="polymarket", type=typ, event=slug, id=tok, token=tok, series="", hist=False,
                                 y=int(px[0] > 0.99), vol=float(m.get("volumeNum") or 0), x=np.nan, T=T,
                                 tk=slug.split("-")[0].upper() if typ == "Earnings" else "",
                                 title=m.get("groupItemTitle") or m["question"]))
    d = pd.DataFrame(rows)
    return d[d["T"].notna() & (d["T"] >= START) & (d["T"] < pd.Timestamp.now(tz=NY))].reset_index(drop=True)


# ---------------- odds at horizons ----------------
def kx_min(r, a, b, period=1):
    path = (f"/historical/markets/{r['id']}/candlesticks" if r["hist"]
            else f"/series/{r['series']}/markets/{r['id']}/candlesticks")
    rows = {}
    for k in P.get(P.KX + path, start_ts=int(a.timestamp()), end_ts=int(b.timestamp()), period_interval=period).get("candlesticks", []):
        f = lambda d, x: float((k.get(d) or {}).get(x) or (k.get(d) or {}).get(x + "_dollars") or "nan")
        bid, ask, last = f("yes_bid", "close"), f("yes_ask", "close"), f("price", "close")
        last = last if last == last else f("price", "previous")
        if bid > 1 or ask > 1:  # older payloads in cents
            bid, ask, last = bid / 100, ask / 100, last / 100
        mid = (bid + ask) / 2 if 0 <= bid < ask <= 1 else np.nan  # bid 0 / ask 1c -> 0.5c: fine for a longshot leg
        rows[pd.Timestamp(k["end_period_ts"], unit="s", tz="UTC")] = mid if mid == mid else last
    return pd.Series(rows, dtype=float).sort_index()


def odds(legs):
    path = "data/eo_odds.pkl"
    cache = pd.read_pickle(path) if os.path.exists(path) and not REFRESH else {}
    # 1-min points over [T-26h, T] plus hourly points over [T-10d, T] (carries a quote that last changed days ago)
    todo = [(r, k) for r in legs.to_dict("records") for k in (r["id"], r["id"] + "|h") if k not in cache]

    def one(job):
        r, k = job
        hourly = k.endswith("|h")
        a, b = r["T"] - (pd.Timedelta(days=10) if hourly else pd.Timedelta(hours=26)), r["T"]
        try:
            return (kx_min(r, a, b, 60 if hourly else 1) if r["src"] == "kalshi"
                    else PC.history(r["token"], a, b, 60 if hourly else 1))
        except Exception as e:  # noqa: BLE001 - one bad market should not kill the run; logged
            print("  odds fail", k, type(e).__name__)
            return pd.Series(dtype=float)
    try:
        with ThreadPoolExecutor(4) as ex:
            for (r, k), s in zip(todo, ex.map(one, todo)):
                cache[k] = s
    finally:
        pd.to_pickle(cache, path)
    ser = {}
    for i in legs.id:
        parts = [x for x in (cache.get(i), cache.get(i + "|h")) if x is not None and len(x)]
        s = pd.concat(parts) if parts else pd.Series(dtype=float)
        ser[i] = s[~s.index.duplicated(keep="last")].sort_index() if len(s) else s
    out = legs.copy()
    for h, dl in HZ.items():
        out[f"p_{h}"] = [PC.at(ser[i], T - dl, STALE) if len(ser[i]) else np.nan
                          for i, T in zip(out.id, out["T"])]
    return out


# ---------------- per-event summary ----------------
def summarize(g):
    """One row per event: leg Brier/log loss per horizon, implied expectation E_h, actual, surprise S."""
    typ, src = g.type.iat[0], g.src.iat[0]
    r = dict(src=src, type=typ, event=g.event.iat[0], T=g["T"].iat[0], tk=g.tk.iat[0])
    excl = typ == "FOMC" or (src == "polymarket" and typ == "CPI")
    if excl:  # exclusive buckets: a leg with no quote in 10 days is a dead longshot -> 0, then renormalised below
        g = g.assign(**{c: g[c].fillna(0.0) for c in PCOLS})
        if (g[PCOLS].sum() < 0.5).any():
            g = g.iloc[:0]
    g = g.dropna(subset=PCOLS).sort_values("x")
    r["legs"] = len(g)
    if g.empty:
        return r
    y = g.y.to_numpy(float)
    for c in PCOLS:
        p = g[c].to_numpy()
        r[f"brier_{c[2:]}"] = float(np.mean((p - y) ** 2))
        r[f"ll_{c[2:]}"] = logloss(p, y)
        r[f"hit_{c[2:]}"] = float(np.mean((p > 0.5) == (y == 1)))
    r["brier_unif"] = float(np.mean(((1 / len(g) if excl else 0.5) - y) ** 2))
    if src != "kalshi" and typ != "Earnings":
        return r
    if typ == "FOMC":
        if y.sum() != 1 or g.x.isna().any():
            return r
        x = g.x.to_numpy()
        for c in PCOLS:
            q = g[c].to_numpy()
            r[f"E_{c[2:]}"] = float(x @ (q / q.sum()))
        r["actual"] = float(x[y == 1][0])
    elif typ in ("CPI", "CPI YoY"):
        x = g.x.to_numpy()
        w = np.append(np.diff(x), 0.1)
        for c in PCOLS:
            r[f"E_{c[2:]}"] = float(w @ g[c].to_numpy())  # relative to the lowest strike (offset cancels in differences)
        r["actual"] = float(w @ y)
        r["X"] = float(x[y == 0].min()) if (y == 0).any() else float(x.max() + 0.1)  # printed value (0.1 grid)
        r["strikes"] = tuple(x)
    else:
        r["E_1d"], r["E_1h"], r["E_5m"], r["actual"] = g.p_1d.iat[0], g.p_1h.iat[0], g.p_5m.iat[0], y[0]
    r["S"] = r["actual"] - r["E_5m"]
    return r


def naive_brier(ev, legs):
    """FOMC/CPI: persistence (previous event's outcome with probability 1). Earnings: leave-one-out pooled beat rate."""
    out = pd.Series(np.nan, index=ev.index)
    for typ in ("FOMC", "CPI"):
        e = ev[(ev.src == "kalshi") & (ev.type == typ) & ev.actual.notna()].sort_values("T")
        prev = None
        for i, r in e.iterrows():
            g = legs[(legs.event == r.event)].dropna(subset=PCOLS)
            if prev is not None:
                f = (g.x == prev).astype(float) if typ == "FOMC" else (prev > g.x).astype(float)
                out[i] = float(np.mean((f - g.y) ** 2))
            prev = r.actual if typ == "FOMC" else r.X
    e = ev[ev.type == "Earnings"]
    if len(e) > 1:
        yy = e.actual.astype(float)
        loo = (yy.sum() - yy) / (len(yy) - 1)
        out[e.index] = (loo - yy) ** 2
    return out


# ---------------- prices ----------------
def intraday(keys):
    path = "data/eo_bars.pkl"
    cache = pd.read_pickle(path) if os.path.exists(path) and not REFRESH else {}
    try:
        for sym, d in keys:
            if (sym, d) not in cache:
                cache[(sym, d)] = PC.abars(sym, "1Min", d - dt.timedelta(days=6), d, "all")
    finally:
        pd.to_pickle(cache, path)
    return cache


def px_at(b, t, stale=pd.Timedelta(minutes=30)):
    """Close of the last 1-min bar that started before t (bar [t-1m, t) closes at t), no older than `stale`."""
    if b is None or b.empty:
        return np.nan
    s = b[(b.ts <= t - pd.Timedelta(minutes=1)) & (b.ts > t - stale)]
    return float(s.close.iloc[-1]) if len(s) else np.nan


def prev_close(b, day):
    s = b[(b.ts.dt.date < day) & (b.ts.dt.strftime("%H:%M") < "16:00")]  # ponytail: half days (13:00 close) use 15:59 ext-hours
    return float(s.close.iloc[-1]) if len(s) else np.nan


def open930(b, day):
    s = b[(b.ts.dt.date == day) & (b.ts.dt.strftime("%H:%M") == "09:30")]
    return float(s.open.iloc[0]) if len(s) else np.nan


def macro_returns(ev, bars):
    """Intraday returns for Kalshi FOMC/CPI events. Primary: FOMC SPY 14:00->14:30, CPI SPY 08:30->10:00."""
    rows = []
    for i, r in ev.iterrows():
        T, day, o = r["T"], r["T"].date(), {}
        for sym in ("SPY", "QQQ", "SHY"):
            b = bars.get((sym, day))
            if b is None or b.empty:
                continue
            p0, pm5, pc = px_at(b, T), px_at(b, T - HZ["5m"]), prev_close(b, day)
            o[f"{sym}_drift"] = pm5 / pc - 1
            if r.type == "FOMC":
                for m in (5, 30, 60):
                    o[f"{sym}_{m}m"] = px_at(b, T + pd.Timedelta(minutes=m)) / p0 - 1
                o[f"{sym}_hold"] = px_at(b, T + pd.Timedelta(minutes=30)) / pm5 - 1
            else:
                op, t930 = open930(b, day), pd.Timestamp(dt.datetime.combine(day, dt.time(9, 30)), tz=NY)
                o[f"{sym}_5m"] = px_at(b, T + pd.Timedelta(minutes=5)) / p0 - 1
                o[f"{sym}_to1000"] = px_at(b, t930 + pd.Timedelta(minutes=30)) / p0 - 1
                for m in (5, 30, 60):
                    o[f"{sym}_open{m}m"] = px_at(b, t930 + pd.Timedelta(minutes=m)) / op - 1
                o[f"{sym}_hold"] = px_at(b, t930 + pd.Timedelta(minutes=30)) / pm5 - 1
        rows.append(pd.Series(o, name=i))
    return pd.DataFrame(rows)


def daily(syms):
    def one(s):
        d = PC.abars(s, "1Day", "2025-06-01", str(dt.date.today() - dt.timedelta(days=1)), "all")  # SIP: no data inside 15 min on this plan
        return d.assign(date=d.ts.dt.date).set_index("date")[["open", "close"]] if len(d) else d
    return {s: one(s) for s in syms}


def earnings_returns(ev, dly):
    """Reaction session = first session whose open is after T. Excess = stock minus QQQ over the same window."""
    q = dly["QQQ"]
    rows = []
    for i, r in ev.iterrows():
        d = dly.get(r.tk)
        if d is None or d.empty:
            continue
        days = list(d.index)
        T = r["T"]
        k = next((j for j, x in enumerate(days) if x > T.date() or (x == T.date() and T.time() < dt.time(9, 30))), None)
        if k is None or k < 2 or days[k] not in q.index or days[k - 1] not in q.index or days[k - 2] not in q.index:
            continue
        a, b, c = days[k - 2], days[k - 1], days[k]
        cc = lambda f, x, y: f.close[y] / f.close[x] - 1
        rows.append(pd.Series({"c2c": cc(d, b, c) - cc(q, b, c),
                               "o2c": (d.close[c] / d.open[c] - 1) - (q.close[c] / q.open[c] - 1),
                               "drift": cc(d, a, b) - cc(q, a, b),
                               "hold": cc(d, b, c) - cc(q, b, c)}, name=i))
    return pd.DataFrame(rows)


# ---------------- statistics ----------------
def ols(y, x):
    """Slope, HC1 t, two-sided p on n-2 df, n."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    m = np.isfinite(y) & np.isfinite(x)
    y, x = y[m], x[m]
    n = len(y)
    if n < 5 or np.std(x) == 0:
        return np.nan, np.nan, np.nan, n
    X = np.column_stack([np.ones(n), x])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - 2)
    t = b[1] / np.sqrt(V[1, 1])
    return float(b[1]), float(t), float(2 * st.t.sf(abs(t), n - 2)), n


def mean_t(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    n = len(v)
    if n < 3 or v.std(ddof=1) == 0:
        return (float(v.mean()) if n else np.nan), np.nan, np.nan, n
    t = v.mean() / (v.std(ddof=1) / np.sqrt(n))
    return float(v.mean()), float(t), float(2 * st.t.sf(abs(t), n - 1)), n


def halves(d, fn):
    d = d.sort_values("T")
    h = len(d) // 2
    return fn(d.iloc[:h])[0], fn(d.iloc[h:])[0]


def rule_returns(d, typ, hold, drift):
    """Pre-registered rule: s = +1 if the odds drift (1d -> 5m) is good for the asset; trade only when the asset's own
    pre-announcement drift has the opposite sign. Net of 2bp per side."""
    dE = d.E_5m - d.E_1d
    s = np.where(dE.abs() < MIN_DRIFT[typ], 0, np.sign(dE) * (1 if typ == "Earnings" else -1))
    take = (s != 0) & (np.sign(d[drift]) == -s)
    return pd.Series(np.where(take, s * d[hold] - 2 * COST, np.nan), index=d.index)


def tests(d, typ, prim, hold, drift):
    """The 5 pre-registered primary tests for one event type (d = one row per event)."""
    d = d.assign(dE_late=d.E_5m - d.E_1h, S1h=d.actual - d.E_1h, rule=rule_returns(d, typ, hold, drift),
                 bd=d.naive - d.brier_5m)
    spec = [("1 accuracy: naive Brier - market Brier (T-5m)", "bd", None, "Brier pts"),
            ("2a leak: (actual - E_1h) on (E_5m - E_1h)", "S1h", "dE_late", "slope"),
            (f"2b late odds move -> {prim}", prim, "dE_late", "slope"),
            (f"3 surprise -> {prim}", prim, "S", "slope"),
            (f"4 rule: net return, {hold} (trades only)", "rule", None, "mean")]
    rows = []
    for name, yc, xc, unit in spec:
        fn = (lambda z, yc=yc, xc=xc: ols(z[yc], z[xc])) if xc else (lambda z, yc=yc: mean_t(z[yc]))
        sub = d.dropna(subset=[yc] + ([xc] if xc else []))
        b, t, p, n = fn(sub)
        h1, h2 = halves(sub, fn) if n >= 8 else (np.nan, np.nan)
        rows.append(dict(type=typ, test=name, n=n, effect=b, unit=unit, t=t, p=p, h1=h1, h2=h2))
    return rows


def secondary(d, typ, cols):
    rows = []
    for c in cols:
        if c not in d:
            continue
        for xc in ("S", "dE_late"):
            b, t, p, n = ols(d[c], d[xc])
            rows.append(dict(type=typ, test=f"{c} on {xc}", n=n, effect=b, t=t, p=p))
    return rows


# ---------------- IPOs (descriptive) ----------------
def ipo_rows(dly):
    ant = pd.read_pickle("data/pm_cal_ipo.pkl").assign(issuer="ANT")  # pm_calibration.py cache, read-only
    out = [ant[["issuer", "event", "item", "y", "vol", "eve", "pre"]]]
    sp = dly.get("SPCX")
    if sp is not None and len(sp):
        day = sp.index[0]
        pre = pd.Timestamp(dt.datetime.combine(day, dt.time(9)), tz=NY)
        eve = pd.Timestamp(dt.datetime.combine(day - dt.timedelta(days=1 if day.weekday() else 3), dt.time(16)), tz=NY)
        rows = []
        for slug in ("spacex-ipo-closing-market-cap", "spacex-ipo-closing-market-cap-above"):
            for m in (PC.event(slug) or {}).get("markets", []):
                px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                if len(px) != 2 or max(px) < 0.99 or not m.get("clobTokenIds") or "not ipo" in m["question"].lower():
                    continue
                s = PC.history(json.loads(m["clobTokenIds"])[0], pre - pd.Timedelta(days=3), pre + pd.Timedelta(hours=1), 60)
                rows.append(dict(issuer="SPCX", event=slug, item=m.get("groupItemTitle") or m["question"], y=int(px[0] > 0.99),
                                 vol=float(m.get("volumeNum") or 0), eve=PC.at(s, eve, STALE), pre=PC.at(s, pre, STALE)))
        out.append(pd.DataFrame(rows))
    return pd.concat(out, ignore_index=True)


# ---------------- report ----------------
def fmt(df, **kw):
    return df.to_markdown(index=False, floatfmt=kw.get("floatfmt", ".4f"))


def main():
    kx = cached("data/eo_kx_legs.pkl", kalshi_legs)
    cpi_T = sorted(set(kx.loc[kx.type == "CPI", "T"]))
    pm = cached("data/eo_pm_legs.pkl", lambda: pm_legs(cpi_T))
    legs = pd.concat([kx.assign(tk=""), pm], ignore_index=True)
    legs = cached("data/eo_legs_odds.pkl", lambda: odds(legs))
    ev = pd.DataFrame([summarize(g) for _, g in legs.groupby(["src", "type", "event"])])
    ev["naive"] = naive_brier(ev, legs)

    km = ev[(ev.src == "kalshi") & ev.type.isin(["FOMC", "CPI"]) & ev.S.notna()]
    bars = intraday([(s, r["T"].date()) for _, r in km.iterrows() for s in ("SPY", "QQQ", "SHY")
                     if not (s == "SHY" and r.type == "CPI")])
    mr = macro_returns(km, bars)
    er_ev = ev[(ev.type == "Earnings") & ev.S.notna()]
    dly = cached("data/eo_daily.pkl", lambda: daily(sorted(set(er_ev.tk)) + ["QQQ"]))
    er = earnings_returns(er_ev, dly)

    fomc = km[km.type == "FOMC"].join(mr)
    cpi = km[km.type == "CPI"].join(mr)
    ern = er_ev.join(er)
    for d in (fomc, cpi, ern):
        d["dE_late"] = d.E_5m - d.E_1h
    prim = (tests(fomc, "FOMC", "SPY_30m", "SPY_hold", "SPY_drift") + tests(cpi, "CPI", "SPY_to1000", "SPY_hold", "SPY_drift")
            + tests(ern, "Earnings", "c2c", "hold", "drift"))
    pt = pd.DataFrame(prim)
    pt["holm_p"] = holm(pt.p.fillna(1)).values
    pt["pass"] = (pt.holm_p < 0.05) & (np.sign(pt.h1) == np.sign(pt.h2))
    sec = pd.DataFrame(secondary(fomc, "FOMC", ["SPY_5m", "SPY_60m", "QQQ_5m", "QQQ_30m", "QQQ_60m", "SHY_5m", "SHY_30m", "SHY_60m"])
                       + secondary(cpi, "CPI", ["SPY_5m", "SPY_open5m", "SPY_open30m", "SPY_open60m", "QQQ_5m", "QQQ_to1000",
                                                "QQQ_open5m", "QQQ_open30m", "QQQ_open60m"])
                       + secondary(ern, "Earnings", ["o2c"]))
    for typ, d, yc in (("FOMC", fomc, "SPY_30m"), ("CPI", cpi, "SPY_to1000"), ("Earnings", ern, "c2c")):
        k = d.S.abs().idxmax()
        b, t, p, n = ols(d.drop(k)[yc], d.drop(k).S)
        sec.loc[len(sec)] = dict(type=typ, test=f"robustness: test 3 without largest |S| ({d['T'][k]:%Y-%m-%d})", n=n, effect=b, t=t, p=p)

    # inventory
    inv = legs.groupby(["type", "src"]).agg(events=("event", "nunique"), legs=("id", "size"),
                                            first=("T", "min"), last=("T", "max")).reset_index()
    with5 = ev.dropna(subset=["brier_5m"]).groupby(["type", "src"]).event.nunique().rename("events with odds at T-1d/1h/5m")
    inv = inv.merge(with5, on=["type", "src"], how="left")
    inv["first"], inv["last"] = inv["first"].map(lambda x: f"{x:%Y-%m-%d}"), inv["last"].map(lambda x: f"{x:%Y-%m-%d}")
    ern_cnt = ev[ev.type == "Earnings"].dropna(subset=["brier_5m"]).groupby("tk").size()

    # accuracy
    acc = []
    for (typ, src), g in ev.dropna(subset=["brier_5m"]).groupby(["type", "src"]):
        for h in HZ:
            acc.append(dict(type=typ, src=src, horizon=f"T-{h}", events=len(g), brier=g[f"brier_{h}"].mean(),
                            naive=g.naive.mean() if g.naive.notna().any() else np.nan, uniform=g.brier_unif.mean(),
                            logloss=g[f"ll_{h}"].mean(), leg_hit=g[f"hit_{h}"].mean()))
    acc = pd.DataFrame(acc)
    L5 = legs.dropna(subset=PCOLS)

    ipo = ipo_rows(dly) if "SPCX" in dly else ipo_rows({})
    ipo_sum = []
    for iss, g in ipo.dropna(subset=["pre"]).groupby("issuer"):
        for c in ("eve", "pre"):
            ipo_sum.append(dict(issuer=iss, snapshot={"eve": "T-1d 16:00", "pre": "IPO day 09:00"}[c], legs=len(g),
                                brier=float(np.mean((g[c] - g.y) ** 2)), brier50=float(np.mean((0.5 - g.y) ** 2)),
                                mean_p_winners=g.loc[g.y == 1, c].mean(), mean_p_losers=g.loc[g.y == 0, c].mean()))

    L = [MARK + " on %s -->" % dt.date.today(), "",
         "## 1. Inventory (events x markets found, resolved, 2023-01 .. 2026-11)", "", fmt(inv), "",
         "Earnings events with odds at all three horizons, by ticker: " + ", ".join(f"{k} {v}" for k, v in ern_cnt.items()) +
         ". Kalshi lists no beat/EPS markets for these names (only earnings-call *mention* markets).",
         f"Excluded: Kalshi CPI {', '.join(CPI_SKIP)} (2025 shutdown: Sept CPI released 2025-10-24 after trading closed "
         "10-15; October CPI never published).", "",
         "## 2. Results: pre-registered primary tests (Holm across all 15)", "",
         fmt(pt[["type", "test", "n", "effect", "unit", "t", "p", "holm_p", "h1", "h2", "pass"]]), "",
         f"**{int(pt['pass'].sum())} of {len(pt)} pass.** Units: FOMC E/S in bp, CPI in pp of MoM CPI, earnings in probability; "
         "returns are fractions (0.001 = 10 bp). h1/h2 = same statistic in the earlier/later half of events.", "",
         "## 3. Accuracy (all sources and horizons; secondary except the Kalshi FOMC/CPI and Polymarket earnings T-5m rows "
         "tested above)", "",
         "Brier = mean over legs per event, then over events. naive = persistence (Kalshi FOMC/CPI) or leave-one-out beat "
         "rate (earnings). uniform = 1/K for exclusive buckets, 0.5 for ladders/binaries.", "", fmt(acc), "",
         "### Calibration, all legs pooled", "", "T-1d:", "", calib_table(L5.p_1d.to_numpy(), L5.y.to_numpy()), "",
         "T-5min:", "", calib_table(L5.p_5m.to_numpy(), L5.y.to_numpy()), "",
         "## 4. Secondary reaction regressions (not Holm-corrected; exploratory)", "", fmt(sec), "",
         "## 5. IPOs (descriptive, n = 2 issues)", "", fmt(pd.DataFrame(ipo_sum)) if ipo_sum else "no IPO data", ""]
    for name, d, cols in (("FOMC", fomc, ["T", "E_1d", "E_1h", "E_5m", "actual", "S", "SPY_drift", "SPY_30m", "SHY_30m"]),
                          ("CPI", cpi, ["T", "X", "E_1d", "E_1h", "E_5m", "S", "SPY_drift", "SPY_5m", "SPY_to1000"]),
                          ("Earnings", ern, ["T", "tk", "E_1d", "E_1h", "E_5m", "actual", "drift", "c2c"])):
        dd = d[[c for c in cols if c in d]].sort_values("T").copy()
        dd["T"] = dd["T"].map(lambda x: f"{x:%Y-%m-%d %H:%M}")
        L += [f"<details><summary>{name} event list ({len(dd)})</summary>", "", fmt(dd), "", "</details>", ""]
    body = "\n".join(L) + "\n" + VERDICT
    pre = open(REPORT, encoding="utf-8").read().split(MARK)[0]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(pre + body)
    print(body)
    pd.to_pickle(dict(ev=ev, fomc=fomc, cpi=cpi, ern=ern, pt=pt), "data/eo_results.pkl")


VERDICT = """## 6. Deviations from the pre-registration (found while checking data, before reading any test result)

- Earnings timing: the first run timed T at the 8-K acceptance. Minute odds showed the beat markets jumping to 0/1
  between 16:00 and the 8-K (press release goes out first; TSLA's 8-K lags by up to 40 min), so T-5min was partly
  post-release. After-close filings are now timed at 16:00 ET (T-5min = 15:55). This lowers measured accuracy.
- Kalshi 1-min candles only exist when a quote changes, so a 26h window missed standing quotes on quiet legs.
  Hourly points over T-10d were added and the staleness limit raised to 10 days; in exclusive buckets (FOMC) a leg with
  no quote at all in 10 days is set to 0 before renormalising.
- Polymarket legs now require `closed` (a 99.5c unresolved December-2026 Fed leg had slipped in).

## 7. Verdict (written after the final run, 2026-11-20)

**(a) Do the odds predict the announcement before it happens? Yes for FOMC and CPI; barely for earnings.**
- FOMC: Kalshi Brier 0.004-0.006 at T-1d/1h/5m vs 0.15 for "same as last meeting" (passes, Holm p = 0.02). Every
  meeting's favourite at T-1d was the actual decision (leg hit rate 100%); Polymarket is the same. The decision is
  known a day ahead, so there is nothing left for the announcement to reveal about the *decision* (statement, dots and
  press conference are not priced by these markets).
- CPI (headline MoM ladder): Brier 0.06 vs 0.24 persistence (passes, Holm p < 0.001), but the odds barely improve
  from T-1d to T-5min (0.061 -> 0.063): no late information arrives in the last day.
- Earnings beat (Polymarket, 46 reports 2025-10..2026-11): Brier 0.115 at T-5min vs 0.135 for the pooled beat rate;
  not significant (p = 0.51), first half worse than the naive rate. These markets are mostly a beat-rate prior.

**Late-move "leak" tests.** FOMC and CPI: no (Holm p 0.31 / 1.0). Earnings: formally passes (slope 1.8, Holm p =
0.03), but it is two events: AMZN 2026-10-29 (p fell 0.67 -> 0.28 between 15:00 and 15:55 ET, then missed) and
ORCL 2026-06-10 (0.23 -> 0.54, beat). Dropping those two: slope 1.46, p = 0.26. Treat it as two anecdotes worth
watching, not a signal.

**(b) Tradable information about the move? No.**
- Surprise -> reaction is there and has the expected sign (markets use the odds as the expectation): FOMC SPY
  -3 bp per bp of hawkish surprise over 30 min (passes, Holm p = 0.008), SHY and QQQ agree (secondary); CPI SPY
  -2.4% per pp of MoM surprise to 10:00 (p = 0.03, Holm 0.31), -3.6%/pp in the first 5 pre-market minutes
  (secondary, t = -6.5); earnings +5% excess per unit of beat surprise (p = 0.048, Holm 0.39). But the FOMC result is
  one meeting: without 2024-09-18 (the 50 bp cut, surprise -13 bp) the slope is 0.0 (p = 0.96). With odds at
  99% the day before, FOMC surprises are almost always ~0.
- None of this is tradable, because the surprise is only known after T. The pre-registered pre-announcement rules:
  FOMC 0 trades (odds never drifted >= 0.5 bp against SPY's own drift); CPI 11 trades, -42 bp mean net (t = -1.7);
  earnings 16 trades, -3.1% mean net excess (t = -2.0). All fail; signs are negative.
- Late odds moves -> returns (2b): none pass. The CPI secondary row (late E move vs open-anchored 09:30->10:00 SPY,
  t = -2.2) are exploratory among ~36 secondary regressions and would not survive correction.
- IPOs (n = 2, descriptive): ANT and SPCX buckets were informative (Brier 0.06-0.08 / 0.04-0.05 vs 0.25), winners
  priced 0.66-0.88 on average; nothing testable.

**Per type.** FOMC: accurate, untradable (no uncertainty left by T-1d). CPI: accurate vs naive, reaction follows the
surprise, no pre-release edge. Earnings: weak forecaster, reaction follows the surprise, rule loses. IPOs: too few.

**Power.** n = 26 FOMC / 44 CPI / 46 earnings / 2 IPOs. Fails are "no evidence", not proof of no effect; the FOMC pass
in test 3 and the earnings leak pass each hinge on one or two events.

## 8. What to log going forward (forward, out-of-sample)

- Every Polymarket earnings-beat market for the 12 names: p at T-1d, 15:00, 15:30, 15:55 and the press-release
  timestamp (wire time, not 8-K) -> re-run the leak test once n >= 100; flag any >= 20-point move in the final hour
  before the release (the AMZN 2026-10-29 pattern).
- Kalshi KXCPI / KXCPIYOY / core CPI ladders at 08:00, 08:25, plus SPY 08:30->08:35 and 09:30->10:00 -> track the
  CPI 2b exploratory row (late E move -> open-anchored return) as a fresh pre-registered test after 24 new releases.
- Kalshi KXFEDDECISION + Polymarket at T-1d/T-5min and SPY/SHY 14:00->14:30: only meetings with a live (5-95%)
  leg at T-1d carry information; expect few.
- New IPO-day markets (open/close/market-cap buckets) at T-1d 16:00 and 09:00 with first-trade time and price.
"""

if __name__ == "__main__":
    main()
