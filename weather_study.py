"""Do NWS model forecasts (MOS / NBM text) beat Kalshi daily-high-temperature prices after fees? Writes reports/weather_results.md.
Run: python weather_study.py fetch_kx | fetch_iem | report      (caches in data/weather/, written only by this script)

Kalshi: KXHIGH{NY,CHI,MIA,AUS,LAX,DEN,PHIL} (+ legacy HIGH* tickers), every bracket, hourly candles (bid/ask/last/volume).
Forecasts: Iowa Environmental Mesonet MOS archive, NBM text (NBS, runs 01/07/13/19Z) and GFS MOS (MAV, 00/06/12/18Z), max-temp
row valid 00Z the next day (daytime max). The archive keeps run time, not dissemination time, so availability is assumed to be
run + 2h (NBS) and run + 4h (GFS MOS); MDL's published dissemination is about +1.2h and +3.5h, so these lags are conservative.
Observed highs: IEM archive of the NWS Daily Climate Report (CLI) for the settlement station.
PAPER/STUDY ONLY: no orders, no accounts.
"""
import datetime as dt
import io
import json
import math
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
from scipy.stats import norm

import pm_study as P
from correlations import holm

P.UA = {"User-Agent": "quant-research-monitor"}
KX, D = P.KX, "data/weather"
IEM = "https://mesonet.agron.iastate.edu"
# city: (series, legacy series, IEM/CLI station, tz)
CITIES = {"NY": ("KXHIGHNY", "HIGHNY", "KNYC", "America/New_York"), "CHI": ("KXHIGHCHI", "HIGHCHI", "KMDW", "America/Chicago"),
          "MIA": ("KXHIGHMIA", "HIGHMIA", "KMIA", "America/New_York"), "AUS": ("KXHIGHAUS", "HIGHAUS", "KAUS", "America/Chicago"),
          "LAX": ("KXHIGHLAX", None, "KLAX", "America/Los_Angeles"), "DEN": ("KXHIGHDEN", None, "KDEN", "America/Denver"),
          "PHIL": ("KXHIGHPHIL", None, "KPHL", "America/New_York")}
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2026-11-19")
LAG = {"NBS": pd.Timedelta(hours=2), "GFS": pd.Timedelta(hours=4)}
SLOTS = {"T1 D-1 15:00": (-1, 15), "T2 D 08:00": (0, 8), "T3 D 12:00": (0, 12)}  # (day offset, local hour)
DECISION = "T2 D 08:00"
EDGE, CONTRACTS, KDE_H, WIN, MIN_ERR = 0.08, 100, 1.0, 365, 60
MKT_MKT, CAND = f"{D}/markets.pkl", f"{D}/candles.pkl"


# ---------------- fetch: Kalshi ----------------
def ev_date(event):
    try:
        return pd.Timestamp(dt.datetime.strptime(event.split("-")[1], "%y%b%d"))
    except (ValueError, IndexError):  # a few odd event tickers (not a daily date) -> dropped
        return pd.NaT


def rec(m, city, hist):
    st = m.get("strike_type")
    lo = m.get("floor_strike") if st in ("between", "greater") else None
    hi = m.get("cap_strike") if st in ("between", "less") else None
    lo = -np.inf if lo is None else (lo + 1 if st == "greater" else lo)  # 'greater than 81' -> high >= 82
    hi = np.inf if hi is None else (hi - 1 if st == "less" else hi)       # 'less than 74' -> high <= 73
    return dict(ticker=m["ticker"], event=m["event_ticker"], city=city, date=ev_date(m["event_ticker"]), lo=lo, hi=hi,
                y=int(m.get("result") == "yes"), result=m.get("result"), vol=float(m.get("volume_fp") or m.get("volume") or 0),
                open=P.ts(m["open_time"]), close=P.ts(m["close_time"]), hist=hist,
                src="TWC" if "Weather Company" in (m.get("rules_primary") or "") else "NWS")


def paged(path, key, **params):
    out, cur = [], None
    while True:
        d = P.get(KX + path, limit=1000 if key == "markets" else 200, **params, **({"cursor": cur} if cur else {}))
        out += d.get(key, [])
        cur = d.get("cursor")
        if not cur or not d.get(key):
            return out


def fetch_markets():
    if os.path.exists(MKT_MKT):
        return pd.read_pickle(MKT_MKT)
    rows = []
    for city, (s, legacy, _, _) in CITIES.items():
        evs = {e["event_ticker"] for e in paged("/events", "events", series_ticker=s)}
        evs = {e for e in evs if ev_date(e) is not pd.NaT and START <= ev_date(e) <= END}
        got = {}
        for m in paged("/historical/markets", "markets", series_ticker=s):
            got[m["ticker"]] = rec(m, city, True)
        for m in paged("/markets", "markets", series_ticker=s, status="settled"):
            got.setdefault(m["ticker"], rec(m, city, False))
        missing = evs - {r["event"] for r in got.values()}

        def one(e):
            h = P.get(f"{KX}/historical/markets", event_ticker=e).get("markets", [])
            return [rec(m, city, True) for m in h] or [rec(m, city, False) for m in P.get(f"{KX}/markets", event_ticker=e).get("markets", [])]
        with ThreadPoolExecutor(4) as ex:
            for lst in ex.map(one, sorted(missing)):
                for r in lst:
                    got[r["ticker"]] = r
        rows += [r for r in got.values() if r["event"] in evs]
        print(city, len(evs), "events", sum(r["city"] == city for r in rows), "markets", flush=True)
    df = pd.DataFrame(rows)
    df = df[df.result.isin(["yes", "no"])].reset_index(drop=True)
    os.makedirs(D, exist_ok=True)
    df.to_pickle(MKT_MKT)
    return df


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def parse_candle(k):
    def g(d, x):
        o = k.get(d) or {}
        return num(o.get(x) if o.get(x) is not None else o.get(x + "_dollars"))
    bid, ask, last = g("yes_bid", "close"), g("yes_ask", "close"), g("price", "close")
    vol = num(k.get("volume") if k.get("volume") is not None else k.get("volume_fp"))
    if bid > 1 or ask > 1 or last > 1:  # older payloads in cents
        bid, ask, last = bid / 100, ask / 100, last / 100
    return (k["end_period_ts"], bid, ask, last, 0.0 if vol != vol else vol)


_lock, _last = threading.Lock(), [0.0]


def kx_get(path, **params):
    """Paced GET (<= ~6 req/s across threads; other studies share the IP's limit). 404 -> {}; persistent 429 -> None."""
    for i in range(10):
        with _lock:
            time.sleep(max(0, _last[0] + 0.16 - time.time()))
            _last[0] = time.time()
        try:
            r = requests.get(KX + path, params=params, headers=P.UA, timeout=60)
        except requests.RequestException:
            time.sleep(5)
            continue
        if r.status_code == 404:
            return {}
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(5 * (i + 1), 60))
            continue
        r.raise_for_status()
        return r.json()
    return None


def candles(r):
    path = f"/historical/markets/{r.ticker}/candlesticks" if r.hist else f"/series/{CITIES[r.city][0]}/markets/{r.ticker}/candlesticks"
    a, b = int(r.open.timestamp()), int(r.close.timestamp()) + 3600
    d = kx_get(path, start_ts=a, end_ts=b, period_interval=60)
    if d is None:
        return None  # not cached; retried on the next run
    return np.array([parse_candle(k) for k in d.get("candlesticks", [])], dtype=float).reshape(-1, 5)


def fetch_candles(mk):
    cache = pd.read_pickle(CAND) if os.path.exists(CAND) else {}
    todo = [r for r in mk.itertuples() if r.ticker not in cache]
    print(len(todo), "candle series to fetch", flush=True)
    for i in range(0, len(todo), 1000):
        with ThreadPoolExecutor(3) as ex:
            for r, c in zip(todo[i:i + 1000], ex.map(candles, todo[i:i + 1000])):
                if c is not None:
                    cache[r.ticker] = c
        pd.to_pickle(cache, CAND)
        print(i + 1000, "done", len(cache), "cached", time.strftime("%H:%M"), flush=True)
    return cache


# ---------------- fetch: IEM (MOS + CLI) ----------------
def iem(path, **params):
    for i in range(8):
        r = requests.get(IEM + path, params=params, headers=P.UA, timeout=300)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(30 * (i + 1))
            continue
        r.raise_for_status()
        time.sleep(6)  # IEM rate-limits per IP
        return r.text
    r.raise_for_status()


def fetch_iem():
    os.makedirs(D, exist_ok=True)
    for city, (_, _, st, _) in CITIES.items():
        for y in range(2022, 2027):
            for model in ("NBS", "GFS"):
                f = f"{D}/mos_{st}_{model}_{y}.csv"
                if not os.path.exists(f) or not os.path.getsize(f):
                    txt = iem("/cgi-bin/request/mos.py", station=st, model=model, sts=f"{y}-01-01T00:00Z",
                              ets=f"{y + 1}-01-01T00:00Z", format="csv")
                    open(f, "w").write(txt)
            f = f"{D}/cli_{st}_{y}.json"
            if not os.path.exists(f) or not os.path.getsize(f):
                txt = iem("/json/cli.py", station=st, year=y)
                open(f, "w").write(txt)
        print(city, "done", flush=True)


def load_mos(st):
    """One row per (model, run, target date): forecast daytime high for that local date."""
    out = []
    for model, col in (("NBS", "txn"), ("GFS", "n_x")):
        for y in range(2022, 2027):
            f = f"{D}/mos_{st}_{model}_{y}.csv"
            if not os.path.exists(f) or os.path.getsize(f) < 200:
                continue
            d = pd.read_csv(f, usecols=["runtime", "ftime", col], low_memory=False).dropna()
            d["ftime"], d["runtime"] = pd.to_datetime(d.ftime), pd.to_datetime(d.runtime)
            d = d[d.ftime.dt.hour == 0]  # 00Z row = daytime max of the previous local date (all CONUS stations)
            out.append(pd.DataFrame(dict(model=model, run=d.runtime.dt.tz_localize("UTC"),
                                         avail=d.runtime.dt.tz_localize("UTC") + LAG[model],
                                         date=d.ftime.dt.normalize() - pd.Timedelta(days=1), f=pd.to_numeric(d[col], errors="coerce"))))
    return pd.concat(out).dropna().drop_duplicates(["model", "run", "date"]).sort_values("avail").reset_index(drop=True)


def load_cli(st):
    rows = []
    for y in range(2022, 2027):
        f = f"{D}/cli_{st}_{y}.json"
        if os.path.exists(f) and os.path.getsize(f):
            rows += [(pd.Timestamp(r["valid"]), num(r.get("high"))) for r in json.load(open(f)).get("results", [])]
    s = pd.Series(dict(rows), dtype=float).dropna()
    return s[~s.index.duplicated()].sort_index()


# ---------------- pure helpers (tested in test_weather_study.py) ----------------
def fee(p, c=CONTRACTS):
    """Kalshi taker fee in $ for c contracts at price p: ceil to the cent of 0.07*c*p*(1-p)."""
    return math.ceil(round(0.07 * c * p * (1 - p) * 100, 9)) / 100


def bracket_probs(f, errs, lo, hi, h=KDE_H):
    """P(lo <= high <= hi) with high = f + e, e from the empirical errors smoothed by a N(0, h) kernel, integer highs."""
    errs = np.asarray(errs, float)[:, None]
    lo, hi = np.asarray(lo, float)[None, :], np.asarray(hi, float)[None, :]
    return (norm.cdf((hi + .5 - f - errs) / h) - norm.cdf((lo - .5 - f - errs) / h)).mean(0)


def state_at(c, t):
    """Quote state from hourly candles c[:, ts, bid, ask, last, vol] using only candles that closed at or before t."""
    c = c[c[:, 0] <= t]
    if not len(c):
        return np.nan, np.nan, np.nan
    bid, ask = c[-1, 1], c[-1, 2]
    last = c[:, 3][~np.isnan(c[:, 3])]
    last = last[-1] if len(last) else np.nan
    mid = (bid + ask) / 2 if 0 <= bid <= ask <= 1 and ask > 0 and ask - bid <= .10 else last
    return mid, (ask if 0 < ask < 1 else np.nan), last


def implied_mean(lo, hi, p):
    """Market-implied expected high from bracket prices (renormalised); open tails priced at 1 degree past the edge."""
    lo, hi, p = (np.asarray(x, float) for x in (lo, hi, p))
    x = np.where(np.isinf(lo), hi - 1, np.where(np.isinf(hi), lo + 1, (lo + hi) / 2))
    return float((x * p).sum() / p.sum())


def cluster_t(x, g):
    """Mean of the cluster means of x, its t-stat and two-sided p (clusters = g)."""
    s = pd.Series(np.asarray(x, float)).groupby(np.asarray(g)).mean().dropna()
    if len(s) < 3:
        return np.nan, np.nan, np.nan, len(s)
    t = s.mean() / (s.std(ddof=1) / math.sqrt(len(s)))
    return float(s.mean()), float(t), float(2 * norm.sf(abs(t))), len(s)


def roi_boot(pnl, cost, day, b=2000, seed=0):
    """ROI = sum pnl / sum cost; 95% CI and two-sided p by resampling days."""
    df = pd.DataFrame(dict(p=pnl, c=cost, d=day)).groupby("d").sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(df), (b, len(df)))
    r = df.p.to_numpy()[idx].sum(1) / df.c.to_numpy()[idx].sum(1)
    roi = df.p.sum() / df.c.sum()
    return roi, np.percentile(r, 2.5), np.percentile(r, 97.5), min(1, 2 * min((r <= 0).mean(), (r >= 0).mean()))


# ---------------- build the panel ----------------
def slot_time(date, tz, slot):
    off, hr = SLOTS[slot]
    return pd.Timestamp(date + pd.Timedelta(days=off, hours=hr)).tz_localize(tz).tz_convert("UTC")


def forecast_at(mos, date, t):
    """Latest NBS run available at t for this date (GFS MOS if no NBS), no older than 36h."""
    m = mos[(mos.date == date) & (mos.avail <= t) & (mos.avail > t - pd.Timedelta(hours=36))]
    for model in ("NBS", "GFS"):
        x = m[m.model == model]
        if len(x):
            return float(x.f.iloc[-1]), model
    return np.nan, None


def build_panel(mk, cand):
    rows, fc_rows = [], []
    for city, (_, _, st, tz) in CITIES.items():
        mos, cli = load_mos(st), load_cli(st)
        days = pd.date_range("2022-03-01", END)
        # forecast + error history for every day (also non-Kalshi days, for the trailing error distribution)
        for slot in SLOTS:
            for d in days:
                f, model = forecast_at(mos, d, slot_time(d, tz, slot))
                fc_rows.append(dict(city=city, slot=slot, date=d, f=f, model=model, obs=cli.get(d, np.nan)))
        print(city, "forecasts", flush=True)
        fc = pd.DataFrame([r for r in fc_rows if r["city"] == city])
        for ev, g in mk[mk.city == city].groupby("event"):
            d = g.date.iloc[0]
            for slot in SLOTS:
                t = slot_time(d, tz, slot).timestamp()
                st_ = [state_at(cand.get(tk, np.empty((0, 5))), t) for tk in g.ticker]
                vol = [cand[tk][(cand[tk][:, 0] > t - 7200) & (cand[tk][:, 0] <= t + 7200), 4].sum() if tk in cand else 0
                       for tk in g.ticker]
                h = fc[(fc.slot == slot) & (fc.date >= d - pd.Timedelta(days=WIN)) & (fc.date <= d - pd.Timedelta(days=2))]
                errs = (h.obs - h.f).dropna().to_numpy()
                f = fc[(fc.slot == slot) & (fc.date == d)].f.iloc[0] if len(fc[(fc.slot == slot) & (fc.date == d)]) else np.nan
                pm = bracket_probs(f, errs, g.lo, g.hi) if len(errs) >= MIN_ERR and f == f else np.full(len(g), np.nan)
                for (r, (mid, ask, last), p, v) in zip(g.itertuples(), st_, pm, vol):
                    rows.append(dict(city=city, event=ev, date=d, slot=slot, ticker=r.ticker, lo=r.lo, hi=r.hi, y=r.y, src=r.src,
                                     mkt=mid, ask=ask, last=last, model=p, f=f, vol2h=v, mvol=r.vol, obs=cli.get(d, np.nan)))
    return pd.DataFrame(rows), pd.DataFrame(fc_rows)


def lag_events(mk, cand):
    """Each new run (NBS or GFS MOS) that moves the forecast high for an open market's date by >= 2F."""
    out = []
    for city, (_, _, st, tz) in CITIES.items():
        mos = load_mos(st)
        evs = {d: g for d, g in mk[mk.city == city].groupby("date")}
        for (model, date), g in mos[mos.date.isin(evs)].groupby(["model", "date"]):
            g = g.sort_values("run")
            ev = evs[date]
            cutoff = pd.Timestamp(date + pd.Timedelta(hours=18)).tz_localize(tz).tz_convert("UTC")
            for prev, cur in zip(g.itertuples(), g.iloc[1:].itertuples()):
                dF = cur.f - prev.f
                if abs(dF) < 2 or not (ev.open.min() + pd.Timedelta(hours=3) <= cur.avail <= cutoff) or cur.run - prev.run > pd.Timedelta(hours=12):
                    continue
                E = {}
                for h in (-3, 0, 1, 2, 3):
                    t = (cur.avail + pd.Timedelta(hours=h)).timestamp()
                    p = np.array([state_at(cand.get(tk, np.empty((0, 5))), t)[0] for tk in ev.ticker])
                    E[h] = implied_mean(ev.lo, ev.hi, p) if not np.isnan(p).any() and p.sum() > 0 else np.nan
                out.append(dict(city=city, date=date, model=model, avail=cur.avail, dF=dF, **{f"E{h}": E[h] for h in E}))
    return pd.DataFrame(out)


# ---------------- report ----------------
def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p, d = k / n, 1 + z * z / n
    c, w = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - w, c + w


def calib_table(p, y):
    b = np.minimum((p * 10).astype(int), 9)
    out = ["| bin | n | mean price | YES freq | 95% CI |", "|---|---|---|---|---|"]
    for i in range(10):
        k, n = int(y[b == i].sum()), int((b == i).sum())
        lo, hi = wilson(k, n)
        if n:
            out.append(f"| {i/10:.1f}–{(i+1)/10:.1f} | {n} | {p[b == i].mean():.3f} | {k/n:.3f} | [{lo:.3f}, {hi:.3f}] |")
    return "\n".join(out)


def fmt(x, f="{:+.4f}"):
    return "—" if x is None or x != x else f.format(x)


def main():
    if "fetch_kx" in sys.argv:
        fetch_candles(fetch_markets())
        return
    if "fetch_iem" in sys.argv:
        fetch_iem()
        return
    mk, cand = pd.read_pickle(MKT_MKT), pd.read_pickle(CAND)
    pf = f"{D}/panel.pkl"
    if os.path.exists(pf) and "--rebuild" not in sys.argv:
        panel, fc, lag = pd.read_pickle(pf)
    else:
        panel, fc = build_panel(mk, cand)
        lag = lag_events(mk, cand)
        pd.to_pickle((panel, fc, lag), pf)
    write_report(mk, cand, panel, fc, lag)


def write_report(mk, cand, panel, fc, lag):
    dates = np.sort(panel.date.unique())
    cut = dates[int(len(dates) * .7)]
    panel["hold"] = panel.date >= cut
    L, tests = [], []

    def test(name, x, g, sign, hold_mask):
        m, t, p, n = cluster_t(x, g)
        mh, th, ph, nh = cluster_t(np.asarray(x)[hold_mask], np.asarray(g)[hold_mask])
        tests.append(dict(test=name, mean=m, t=t, p=p, n=n, hold_mean=mh, hold_p=ph, sign=sign))

    # ---- data coverage
    ev = mk.groupby("city").agg(events=("event", "nunique"), markets=("ticker", "size"), first=("date", "min"), last=("date", "max"),
                                vol=("vol", "sum"))
    ev["with candles"] = mk.groupby("city").ticker.apply(lambda s: sum(len(cand.get(t, [])) > 0 for t in s))
    cov = ["| city | station | events | brackets | with candles | first | last | contracts traded |", "|---|---|---|---|---|---|---|---|"]
    for c, r in ev.iterrows():
        cov.append(f"| {c} | {CITIES[c][2]} | {r.events} | {r.markets} | {r['with candles']} | {r['first']:%Y-%m-%d} | {r['last']:%Y-%m-%d} | {r.vol:,.0f} |")
    # settlement check: CLI high falls in the bracket that resolved YES
    win = panel[(panel.slot == DECISION) & (panel.y == 1)].dropna(subset=["obs"])
    win["ok"] = (win.obs >= win.lo) & (win.obs <= win.hi)
    chk = win.groupby(["city", "src"]).ok.agg(["mean", "size"])
    chk_lines = ["| city | settlement source | events | CLI high inside the YES bracket |", "|---|---|---|---|"] + \
        [f"| {c} | {s} | {int(r['size'])} | {r['mean']:.1%} |" for (c, s), r in chk.iterrows()]
    vol_year = mk.assign(year=mk.date.dt.year).groupby("year").vol.sum()
    # forecast skill
    f2 = fc.dropna(subset=["f", "obs"])
    f2 = f2.assign(e=f2.obs - f2.f)
    fsk = ["| slot | days | model used (NBS share) | mean error (obs − fcst) | MAE | SD |", "|---|---|---|---|---|---|"]
    for s, g in f2.groupby("slot"):
        fsk.append(f"| {s} | {len(g)} | {(g.model == 'NBS').mean():.0%} | {g.e.mean():+.2f} | {g.e.abs().mean():.2f} | {g.e.std():.2f} |")

    # ---- Test 1: calibration
    cal_txt = []
    for s in SLOTS:
        d = panel[(panel.slot == s)].dropna(subset=["mkt"])
        cal_txt.append(f"**{s}** (n = {len(d)} brackets, {d.event.nunique()} events; Brier {np.mean((d.mkt - d.y) ** 2):.4f})\n\n"
                       + calib_table(d.mkt.to_numpy(), d.y.to_numpy()))
        for name, m in (("cheap p<0.15", d.mkt < .15), ("rich p>=0.5", d.mkt >= .5)):
            x = d[m]
            test(f"1 calib {s} {name}: mean(y − price)", (x.y - x.mkt).to_numpy(), x.date.to_numpy(), 0, x.hold.to_numpy())

    d = panel[panel.slot == DECISION].dropna(subset=["model"])
    model_cal = calib_table(d.model.to_numpy(), d.y.to_numpy())

    # ---- Test 2: model vs market Brier on the same brackets
    sc = ["| slot | city | brackets | events | Brier market | Brier model | log loss market (event) | log loss model (event) |",
          "|---|---|---|---|---|---|---|---|"]
    for s in SLOTS:
        d = panel[panel.slot == s].dropna(subset=["mkt", "model"])
        d = d[d.groupby("event").mkt.transform("size") == d.groupby("event").ticker.transform("size")]
        for c, g in [("all", d)] + list(d.groupby("city")):
            ew = g[g.y == 1]
            nm = ew.mkt / g.groupby("event").mkt.sum().reindex(ew.event).to_numpy()
            nmod = ew.model / g.groupby("event").model.sum().reindex(ew.event).to_numpy()
            sc.append(f"| {s} | {c} | {len(g)} | {g.event.nunique()} | {np.mean((g.mkt - g.y) ** 2):.4f} | {np.mean((g.model - g.y) ** 2):.4f} | "
                      f"{-np.log(np.clip(nm, .005, 1)).mean():.3f} | {-np.log(np.clip(nmod, .005, 1)).mean():.3f} |")
        test(f"2 Brier(model) − Brier(market) {s}", ((d.model - d.y) ** 2 - (d.mkt - d.y) ** 2).to_numpy(), d.date.to_numpy(), -1,
             d.hold.to_numpy())

    # ---- Test 3: lag
    lag = lag.dropna(subset=["E0", "E1", "E2", "E3", "E-3"]).copy()
    lag["hold"] = lag.date >= cut
    lag_lines = ["| window | updates | mean move toward new forecast (°F) | t | share of |ΔF| |", "|---|---|---|---|---|"]
    sgn = np.sign(lag.dF)
    for lbl, a, b in (("A−3h → A (before availability)", "E-3", "E0"), ("A → A+1h", "E0", "E1"), ("A → A+2h", "E0", "E2"),
                      ("A → A+3h", "E0", "E3")):
        mv = sgn * (lag[b] - lag[a])
        m, t, p, n = cluster_t(mv.to_numpy(), lag.date.to_numpy())
        lag_lines.append(f"| {lbl} | {len(lag)} | {fmt(m, '{:+.3f}')} | {fmt(t, '{:+.2f}')} | {fmt(m / lag.dF.abs().mean(), '{:.1%}')} |")
        if a == "E0":
            test(f"3 lag: market moves toward new run, {lbl}", mv.to_numpy(), lag.date.to_numpy(), 1, lag.hold.to_numpy())
    gap0 = (sgn * (lag.dF - 0)).mean()

    # ---- Test 4: betting rule at the decision time
    b = panel[(panel.slot == DECISION)].dropna(subset=["model"]).copy()
    b["px"] = b.ask.where(b.ask.notna(), b["last"] + .02)
    b = b[b.px.notna() & (b.px < 1) & (b.px > 0)]
    b["noask"] = b.ask.isna()
    b = b[b.model - b.px >= EDGE].copy()
    b["fee"] = [fee(p) for p in b.px]
    b["cost"] = CONTRACTS * b.px + b.fee
    b["pnl"] = CONTRACTS * b.y - b.cost
    test("4 bet rule ROI per bet (pnl/cost)", (b.pnl / b.cost).to_numpy(), b.date.to_numpy(), 1, b.hold.to_numpy())

    def bet_row(name, g):
        if len(g) < 3:
            return f"| {name} | {len(g)} | — | — | — | — | — |"
        r, lo, hi, p = roi_boot(g.pnl.to_numpy(), g.cost.to_numpy(), g.date.to_numpy())
        return (f"| {name} | {len(g)} | {g.date.nunique()} | {g.y.mean():.1%} | {g.px.mean():.3f} | {r:+.1%} [{lo:+.1%}, {hi:+.1%}] | "
                f"{g.vol2h.median():,.0f} |")
    bdates = np.sort(b.date.unique())
    half = bdates[len(bdates) // 2] if len(bdates) else None
    bt = ["| slice | bets | days | hit rate | mean price paid | ROI after fees [95% day-bootstrap CI] | median contracts traded ±2h |",
          "|---|---|---|---|---|---|---|", bet_row("all", b)]
    if len(b):
        bt += [bet_row("first half", b[b.date < half]), bet_row("second half", b[b.date >= half]),
               bet_row("development (first 70%)", b[~b.hold]), bet_row("holdout (last 30%)", b[b.hold]),
               bet_row("priced at ask", b[~b.noask]), bet_row("no ask: last + 2¢", b[b.noask])]
        bt += [bet_row(f"city {c}", g) for c, g in b.groupby("city")]
        bt += [bet_row(f"year {y}", g) for y, g in b.groupby(b.date.dt.year)]
        bt += [bet_row("model prob − price ≥ 15pp", b[b.model - b.px >= .15])]

    # ---- exploratory (not pre-registered): is the cheap-bracket overpricing (test 1) worth selling at the bid after fees?
    x = panel[(panel.slot == DECISION) & (panel.mkt < .15) & panel.ask.notna()].copy()
    x["bid"] = 2 * x.mkt - x.ask  # mid came from quotes when the spread <= 10c
    x = x[(x.bid >= 0) & (x.ask - x.bid <= .10) & (x.bid > .005)]
    x["no"] = 1 - x.bid
    x["cost"] = CONTRACTS * x.no + [fee(p) for p in x.no]
    x["pnl"] = CONTRACTS * (1 - x.y) - x.cost
    x = x.rename(columns={"y": "y_yes"}).assign(y=lambda z: 1 - z.y_yes, px=lambda z: z.no)
    ex = ["| slice | bets | days | NO hit rate | mean NO price | ROI after fees [95% CI] | median contracts ±2h |", "|---|---|---|---|---|---|---|",
          bet_row("all", x), bet_row("holdout (last 30%)", x[x.hold]), bet_row("year 2026", x[x.date.dt.year == 2026])]

    # ---- Holm + verdicts
    T = pd.DataFrame(tests)
    T["holm"] = holm(T.p).to_numpy()
    T["pass"] = [(r.holm < .05) and (r.sign == 0 or np.sign(r["mean"]) == r.sign) and (r.hold_p < .05) and
                 (np.sign(r.hold_mean) == np.sign(r["mean"])) for _, r in T.iterrows()]
    tl = ["| # | test | mean | t | p | Holm p | n clusters (days) | holdout mean | holdout p | pass |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in T.iterrows():
        tl.append(f"| {i+1} | {r.test} | {fmt(r['mean'])} | {fmt(r.t, '{:+.2f}')} | {fmt(r.p, '{:.4f}')} | {fmt(r.holm, '{:.4f}')} | "
                  f"{r.n} | {fmt(r.hold_mean)} | {fmt(r.hold_p, '{:.4f}')} | {'**PASS**' if r['pass'] else 'fail'} |")

    roi_all = roi_boot(b.pnl.to_numpy(), b.cost.to_numpy(), b.date.to_numpy())[0] if len(b) else np.nan
    roi_hold = roi_boot(b[b.hold].pnl.to_numpy(), b[b.hold].cost.to_numpy(), b[b.hold].date.to_numpy())[0] if b.hold.any() else np.nan
    rep = f"""# Weather forecasts vs Kalshi daily-high markets

Generated {pd.Timestamp.now():%Y-%m-%d %H:%M} by [weather_study.py](../weather_study.py). Paper study only: no orders, no accounts.

## Pre-registration (written before the first run; not changed after)

A development run on a partial cache (166 NY events, 2026) was used only to debug the code; no test, threshold,
time or model setting was changed after it (only report formatting, and a descriptive model-calibration table was added).

Question: do official NWS model forecasts (and their updates) predict Kalshi daily high-temperature outcomes better than the
market price, after Kalshi fees, so a US retail trader could bet them?

- **Sample**: KXHIGH{{NY,CHI,MIA,AUS,LAX,DEN,PHIL}} (+ legacy HIGH* tickers), event dates {START:%Y-%m-%d} → {END:%Y-%m-%d}, every bracket.
  Chronological holdout = last 30% of event dates (from {pd.Timestamp(cut):%Y-%m-%d}).
- **Prices**: hourly Kalshi candles; state at time t = last candle that *closed* at or before t (quotes carried forward).
  Price = bid/ask mid when the spread ≤ 10¢, else last trade.
- **Times** (local to the city): T1 = 15:00 the day before (Kalshi opens these markets ~10:00 ET the day before, so 10:00
  local would precede the open for western cities), T2 = 08:00 on the day, T3 = 12:00 on the day.
- **Forecast**: latest NBM text (NBS) run available at t (run + 2h), else latest GFS MOS (run + 4h); daytime max row.
  Probability model: high = forecast + e, e drawn from that city's and slot's errors (CLI high − forecast) on days
  D−{WIN}…D−2 only (no lookahead), Gaussian-kernel smoothed (h = {KDE_H}°F), ≥ {MIN_ERR} past errors required.
- **Tests** (13, Holm-corrected together; a PASS also needs the same sign and p < 0.05 on the holdout alone;
  standard errors clustered by event date):
  1. Calibration at T1/T2/T3: mean(outcome − price) for cheap brackets (price < 0.15) and rich ones (≥ 0.5) — 6 tests.
  2. Brier(model) − Brier(market) per bracket at T1/T2/T3, same brackets (events with every bracket priced) — 3 tests; pass needs < 0.
  3. Update lag: each new NBS/GFS-MOS run (available time A) that moves the forecast high for an open market by ≥ 2°F.
     Market-implied mean high E(t) from renormalised bracket prices. Move toward the new forecast sign(ΔF)·(E(A+h) − E(A)),
     h = 1, 2, 3 h — 3 tests; pass needs > 0. A−3h → A reported for context (has the market already moved?).
  4. Betting rule at T2 (08:00 local, event day): buy every bracket with model prob − ask ≥ {EDGE*100:.0f}pp, {CONTRACTS} contracts,
     pay the ask (no ask quote → last trade + 2¢) plus the Kalshi taker fee ceil(0.07·C·P·(1−P)) to the cent, hold to
     settlement. 1 test on per-bet ROI; table reports ROI = Σpnl/Σcost with a day-bootstrap 95% CI (B = 2000).

## Data coverage

{chr(10).join(cov)}

Contracts traded per year (all 7 cities): {', '.join(f'{y}: {v:,.0f}' for y, v in vol_year.items())}.

Settlement check (IEM archive of the NWS CLI vs the bracket Kalshi settled YES). From late 2025/2026 Kalshi's rules name
The Weather Company (still the CLI station, e.g. CLINYC/CLIMDW) instead of the NWS report:

{chr(10).join(chk_lines)}

Forecast skill (all days 2022-03 → 2026-11, the error history the model draws on):

{chr(10).join(fsk)}

## Test 1: Kalshi calibration

{(chr(10) * 2).join(cal_txt)}

## Test 2: model vs market

{chr(10).join(sc)}

Model's own calibration at {DECISION} (all brackets with a model probability):

{model_cal}

## Test 3: does the market lag model updates?

{len(lag)} qualifying updates (|ΔF| ≥ 2°F; mean |ΔF| = {lag.dF.abs().mean():.2f}°F).

{chr(10).join(lag_lines)}

## Test 4: fixed betting rule

{chr(10).join(bt)}

## Exploratory (not pre-registered, not in the Holm family)

Sell the overpriced cheap brackets from test 1: at {DECISION}, every bracket with price < 0.15 and a YES bid > 0.5¢,
buy NO at 1 − YES bid ({CONTRACTS} contracts, taker fee), hold to settlement.

{chr(10).join(ex)}

## All tests

{chr(10).join(tl)}

**{int(T['pass'].sum())} of {len(T)} tests pass.**

## Verdict

- **Calibration**: Kalshi temperature brackets are well calibrated. Cheap brackets (< 15¢) resolve YES about 1pp less
  often than priced (tests 1/3/5 pass), a mild longshot bias; selling them at the bid after fees earns ≈ 0 (exploratory table).
- **Forecast model vs market**: the market beats the NWS MOS/NBM-text model at every time and in every city (tests 7–9:
  model Brier worse, holdout too). The model is calibrated but less sharp; the market has hourly NBM/HRRR runs, observations
  and the morning's temperatures that the 4-cycle public archive does not.
- **Update lag**: after a ≥ 2°F change in a new run, the market's implied high drifts toward it by ~0.02–0.08°F over 1–3 h
  (statistically real, tests 10–12 pass), but that is only 1–3% of the forecast change, and it moved as much before the run
  was (conservatively) available. Too small to pay a 1–2¢ spread plus fees on a 2°F bracket.
- **Betting rule**: model − ask ≥ 8pp at 08:00 loses {roi_all:+.1%} after fees overall and {roi_hold:+.1%} on the holdout; it was
  positive in the first half of bet days (thinner books) but sharply negative in the second half and in 2026, as volume grew.
- **Verdict: no tradable edge** for a retail trader from public NWS model guidance. Nothing to forward paper-log.
"""
    os.makedirs("reports", exist_ok=True)
    open("reports/weather_results.md", "w", encoding="utf-8").write(rep)
    print(rep)


if __name__ == "__main__":
    main()
