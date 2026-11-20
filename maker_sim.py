"""Can a retail MAKER (resting quotes around a fair value) profit on Kalshi? Writes reports/maker_sim_results.md.
Run: python maker_sim.py fetch | report        (caches in data/maker/, written only by this script)

Data: Kalshi public market list, trade prints (/markets/trades, /historical/trades) and 1-minute candlesticks for resolved
markets in sports game winners (NFL/NBA/MLB/NHL), daily high temperature (KXHIGH*, market list reused read-only from
weather_study's cache) and economics ladders (CPI, Fed funds, payrolls). Informed fair values: weather_study's NWS-forecast
bracket probability; de-vigged Pinnacle from the betting snapshot DB copy (Sep-Nov 2026 NFL/MLB only).
PAPER/STUDY ONLY: no orders, no accounts.
"""
import hashlib
import math
import os
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import weather_study as W  # reused: paced Kalshi GET, candle parser, MOS/CLI loaders, bracket model, fee, bootstraps

D = "data/maker"
SPORTS = {"NFL": "KXNFLGAME", "NBA": "KXNBAGAME", "MLB": "KXMLBGAME", "NHL": "KXNHLGAME"}
ECON = {"CPI": "KXCPI", "FED": "KXFED", "JOBS": "KXPAYROLLS"}
PIN_LEAGUE = {"NFL": "americanfootball_nfl", "MLB": "baseball_mlb"}
START, END = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-11-19", tz="UTC")
PIN_START = pd.Timestamp("2026-09-10", tz="UTC")
N_SPORT, N_WX_CITY, N_ECON, N_PIN, MIN_VOL = 100, 100, 150, 60, 1000
GAME_LEN = pd.Timedelta(hours=3)        # Kalshi expected_expiration_time = scheduled start + 3h (12/12 ESPN spot checks)
WINDOW, PULL, STEP = pd.Timedelta(hours=48), pd.Timedelta(minutes=15), 300
H, SIZE, MAXINV, SKEW, QUEUE = 0.02, 10, 50, 0.0005, 0.5  # skew 0.5c per 10 contracts
MAKER_RATE, TAKER_RATE, PIN_MAX_AGE, MAX_PAGES = 0.0175, 0.07, 12 * 3600, 150
SAMPLE, DATA = f"{D}/sample.pkl", f"{D}/data.pkl"

PREREG = """## Pre-registration (written 2026-11-20 before any simulation result; one parameter set, not changed after)

Question: can a retail trader profit as a **maker** on Kalshi (resting quotes around a fair value), and does a
fair-value edge help?

- **Sample** (deterministic: within each stratum, markets ordered by sha1(ticker); resolved yes/no; total volume ≥ 1,000
  contracts; resolution 2024-01-01 → 2026-11-19):
  sports game winners KXNFLGAME/KXNBAGAME/KXMLBGAME/KXNHLGAME, one market per game (lowest hash), 100 games per league;
  daily high temperature KXHIGH{NY,CHI,MIA,AUS,LAX,DEN,PHIL} (market list from weather_study's cache), 100 brackets per city;
  economics KXCPI/KXFED/KXPAYROLLS (incl. legacy CPI-/FED- tickers listed under them), 150 markets per series.
  Extra Pinnacle sample: NFL/MLB games resolving 2026-09-10 → 2026-11-19 that match a Pinnacle game in the snapshot DB,
  60 per league (union with the main sample; reported only as a paired baseline-vs-Pinnacle comparison).
- **Resolution time T**: sports = scheduled start = expected_expiration_time − 3h; weather and econ = close_time
  (econ markets close ~5 min before the 8:30 ET release / 2:00 pm ET Fed decision).
- **Quoting window**: [max(open, T − 48h), min(T − 15 min, close)]. Quotes refreshed every 5 minutes on a fixed grid.
- **Fair value** at refresh time t (data strictly at or before t):
  (1) baseline: the market's own mid, from the last 1-minute candle closed at or before t
      ((yes_bid + yes_ask)/2 when both sides exist and spread ≤ 10¢, else last trade);
  (2a) weather informed: weather_study's model, P(bracket) with high = latest NBM-text (else GFS MOS) forecast available
      at t (run + 2h / + 4h) + error drawn from that city's errors on D−365…D−2 (D−1 15:00 errors before the event day,
      D 08:00 errors on it), Gaussian kernel h = 1°F, ≥ 60 errors;
  (2b) sports informed: Pinnacle moneyline, multiplicative de-vig, latest snapshot at or before t, no older than 12 h
      (else no quote). Other informed sources: none available with timestamped history → skipped.
- **Quotes**: bid = fair − h − skew, ask = fair + h − skew, rounded away from fair to the 1¢ tick; h = 2¢ (primary),
  1¢ and 3¢ (sensitivity); skew = 0.5¢ per 10 contracts of YES inventory; 10 contracts per side; inventory capped at
  ±50 (side size shrinks so the cap cannot be breached); post-only (a side that would cross the last candle's
  opposite best quote is not posted); no quote below 1¢ or above 99¢.
- **Fill model** (conservative): a resting bid fills only on a later public trade printed STRICTLY below the bid
  (strictly above for an ask), at most 0.5 × the printed size, until the order's 10 contracts are used up; trades at the
  quote's own timestamp never fill it. Fill price = our quote.
- **Fees**: series with Kalshi fee_type `quadratic_with_maker_fees` pay a maker fee ceil(0.0175 × multiplier × C × P(1−P))
  per order (one order = one side of one 5-min quote); other series pay no maker fee. Current fee type applied to all
  history. Taker fee 0.07 × multiplier × P(1−P) shown for comparison.
- **Score**: hold to settlement. P&L per market ($) and ROI = Σ P&L / Σ capital, capital per market = the largest
  collateral the inventory ever needed (long: contracts × average YES cost; short: contracts × (1 − average sale price)).
  Decomposition per fill: spread earned = side × (mid at fill − price); adverse selection = side × (mid at +5 min / +60 min /
  settlement − mid at fill). Fill rate = filled / posted contracts.
- **Statistics**: 95% CI by resampling resolution days (B = 2000). Chronological halves; holdout = last 30% of each
  category's markets by T. **Pass** (per category and fair value, h = 2¢ only): ROI > 0 with CI lower bound > 0, ROI > 0
  in both halves and in the holdout. h = 1¢/3¢ never decide a pass.
"""


def h8(s):
    return hashlib.sha1(s.encode()).hexdigest()


def ts(s):
    return pd.Timestamp(s).tz_convert("UTC") if pd.Timestamp(s).tzinfo else pd.Timestamp(s, tz="UTC")


def settled(series):
    """Every resolved market in a series: historical endpoint first (hist=True), then live settled."""
    got = {m["ticker"]: (m, True) for m in W.paged("/historical/markets", "markets", series_ticker=series)}
    for m in W.paged("/markets", "markets", series_ticker=series, status="settled"):
        got.setdefault(m["ticker"], (m, False))
    return got.values()


def vol(m):
    return float(m.get("volume_fp") or m.get("volume") or 0)


def team_match(sub, full):
    """Kalshi yes_sub_title ('Los Angeles R', 'Chicago WS', "A's") vs Odds API full name."""
    return full.startswith(sub) or (sub == "A's" and "Athletics" in full) or \
        (sub.endswith(" WS") and full.startswith(sub[:-3] + " White Sox"))


def pinnacle():
    c = sqlite3.connect("file:data/sharp_snap_copy.sqlite3?mode=ro", uri=True)
    q = pd.read_sql("select snapshot_time, league, commence_time, home_team, away_team, outcome, price from price_snapshots "
                    "where venue='pinnacle' and league in ('americanfootball_nfl','baseball_mlb') and outcome in ('H','A')", c)
    q["snap"], q["commence"] = pd.to_datetime(q.snapshot_time, utc=True), pd.to_datetime(q.commence_time, utc=True)
    w = q.pivot_table(index=["league", "commence", "home_team", "away_team", "snap"], columns="outcome", values="price").dropna()
    w = w.reset_index()
    w["pH"] = w.H / (w.H + w.A)  # multiplicative de-vig
    return w[w.snap < w.commence]


def build_sample():
    if os.path.exists(SAMPLE):
        return pd.read_pickle(SAMPLE)
    rows = []
    fees = {}
    for s in list(SPORTS.values()) + list(ECON.values()) + [c[0] for c in W.CITIES.values()]:
        x = W.kx_get(f"/series/{s}").get("series", {})
        fees[s] = float(x.get("fee_multiplier") or 1) if x.get("fee_type") == "quadratic_with_maker_fees" else 0.0
    pin = pinnacle()
    for lg, s in SPORTS.items():
        evs = {}
        for m, hist in settled(s):
            if m.get("result") not in ("yes", "no") or not m.get("expected_expiration_time"):
                continue
            T = ts(m["expected_expiration_time"]) - GAME_LEN
            evs.setdefault(m["event_ticker"], []).append(dict(
                cat="sports", sub=lg, series=s, ticker=m["ticker"], event=m["event_ticker"], hist=hist, T=T,
                open=ts(m["open_time"]), close=ts(m["close_time"]), y=int(m["result"] == "yes"), vol=vol(m),
                team=m.get("yes_sub_title") or "", mult=fees[s]))
        games = [min(g, key=lambda r: h8(r["ticker"])) for g in evs.values()]
        games = sorted([g for g in games if START <= g["T"] <= END and g["vol"] >= MIN_VOL], key=lambda r: h8(r["ticker"]))
        main = games[:N_SPORT]
        for g in main:
            g["main"] = True
        extra = []
        if lg in PIN_LEAGUE:
            pl = pin[pin.league == PIN_LEAGUE[lg]]
            for g in games:
                if g["T"] < PIN_START:
                    continue
                other = [r["team"] for r in evs[g["event"]] if r["ticker"] != g["ticker"]]
                c = pl[(pl.commence - g["T"]).abs() <= pd.Timedelta(minutes=45)]
                for (hm, aw), _ in c.groupby(["home_team", "away_team"]):
                    if team_match(g["team"], hm) and (not other or team_match(other[0], aw)):
                        g["pin"] = (PIN_LEAGUE[lg], hm, aw, "H")
                    elif team_match(g["team"], aw) and (not other or team_match(other[0], hm)):
                        g["pin"] = (PIN_LEAGUE[lg], hm, aw, "A")
                if g.get("pin") and len(extra) < N_PIN:
                    extra.append(g)
        rows += main + [g for g in extra if not g.get("main")]
        print(lg, len(games), "eligible games;", len(main), "main;", len(extra), "Pinnacle-matched", flush=True)
    wx = pd.read_pickle(W.MKT_MKT)  # weather_study's cache (read-only)
    wx = wx[(wx.date >= START.tz_localize(None)) & (wx.vol >= MIN_VOL)]
    for city, g in wx.groupby("city"):
        g = g.assign(h=g.ticker.map(h8)).sort_values("h").head(N_WX_CITY)
        s = W.CITIES[city][0]
        rows += [dict(cat="weather", sub=city, series=s, ticker=r.ticker, event=r.event, hist=r.hist, T=r.close, open=r.open,
                      close=r.close, y=r.y, vol=r.vol, mult=fees[s], date=r.date, lo=r.lo, hi=r.hi, main=True)
                 for r in g.itertuples()]
    for name, s in ECON.items():
        ms = [(m, hist) for m, hist in settled(s) if m.get("result") in ("yes", "no") and vol(m) >= MIN_VOL
              and START <= ts(m["close_time"]) <= END]
        ms = sorted(ms, key=lambda x: h8(x[0]["ticker"]))[:N_ECON]
        rows += [dict(cat="econ", sub=name, series=s, ticker=m["ticker"], event=m["event_ticker"], hist=hist, T=ts(m["close_time"]),
                      open=ts(m["open_time"]), close=ts(m["close_time"]), y=int(m["result"] == "yes"), vol=vol(m),
                      mult=fees[s], main=True) for m, hist in ms]
        print(name, len(ms), "markets", flush=True)
    df = pd.DataFrame(rows)
    df["main"] = df["main"].fillna(False).astype(bool)
    df["t0"] = np.maximum(df.open, df["T"] - WINDOW)
    df["t1"] = np.minimum(df["T"] - PULL, df.close)
    df = df[df.t1 > df.t0].reset_index(drop=True)
    os.makedirs(D, exist_ok=True)
    df.to_pickle(SAMPLE)
    return df


# ---------------- fetch ----------------
def fetch_one(r):
    """(trades [ts, yes price, size] ascending, candles [ts, bid, ask, last, vol]) or None on API failure."""
    path = "/historical/trades" if r.hist else "/markets/trades"
    a, b = int(r.t0.timestamp()), int(r.t1.timestamp())
    out, cur, pages = [], None, 0
    while pages < MAX_PAGES:
        d = W.kx_get(path, ticker=r.ticker, min_ts=a, max_ts=b, limit=1000, **({"cursor": cur} if cur else {}))
        if d is None:
            return None
        tr = d.get("trades", [])
        for t in tr:
            p = t.get("yes_price_dollars")
            p = float(p) if p is not None else float(t.get("yes_price", np.nan)) / 100
            n = t.get("count_fp")
            out.append((ts(t["created_time"]).timestamp(), p, float(n if n is not None else t.get("count", 0))))
        pages += 1
        cur = d.get("cursor")
        if not cur or not tr:
            break
    trades = np.array(sorted(out), dtype=float).reshape(-1, 3)
    cpath = f"/historical/markets/{r.ticker}/candlesticks" if r.hist else f"/series/{r.series}/markets/{r.ticker}/candlesticks"
    d = W.kx_get(cpath, start_ts=a - 3600, end_ts=b + 15 * 60 + 4500, period_interval=1)
    if d is None:
        return None
    cand = np.array([W.parse_candle(k) for k in d.get("candlesticks", [])], dtype=float).reshape(-1, 5)
    return trades, cand, pages >= MAX_PAGES


def fetch(sample):
    cache = pd.read_pickle(DATA) if os.path.exists(DATA) else {}
    todo = [r for r in sample.itertuples() if r.ticker not in cache]
    print(len(todo), "markets to fetch", flush=True)
    for i in range(0, len(todo), 100):
        with ThreadPoolExecutor(4) as ex:
            for r, x in zip(todo[i:i + 100], ex.map(fetch_one, todo[i:i + 100])):
                if x is not None:
                    cache[r.ticker] = x
        pd.to_pickle(cache, DATA)
        print(i + 100, "done", len(cache), "cached", time.strftime("%H:%M"), flush=True)
    return cache


# ---------------- simulation (pure; tested in test_maker_sim.py) ----------------
def cent_floor(x):
    return math.floor(round(x * 100, 6)) / 100


def cent_ceil(x):
    return math.ceil(round(x * 100, 6)) / 100


def book(c, t):
    """(bid, ask, mid) from 1-minute candles c[:, ts, bid, ask, last, vol] closed at or before t (scalar or array).
    bid/ask NaN when that side is empty; mid = (bid+ask)/2 if spread <= 10c else last trade."""
    t = np.atleast_1d(np.asarray(t, float))
    if not len(c):
        n = np.full(len(t), np.nan)
        return n, n, n
    ff = pd.DataFrame(c[:, 1:4]).ffill().to_numpy()
    i = np.searchsorted(c[:, 0], t, "right") - 1
    ok = i >= 0
    bid, ask, last = (np.where(ok, ff[np.maximum(i, 0), j], np.nan) for j in range(3))
    bid = np.where(bid > 0, bid, np.nan)
    ask = np.where(ask < 1, ask, np.nan)
    mid = np.where((ask - bid <= .10 + 1e-9) & (bid <= ask), (bid + ask) / 2, last)
    return bid, ask, mid


def simulate(trades, cand, fair, t0, t1, h=H, fee_mult=0.0):
    """Fixed 5-min quote grid on [t0, t1). fair: array of fair values at each grid time (NaN = no quote).
    Returns fills array [t, side(+1 buy YES / -1 sell YES), qty, price, fee] and posted contracts."""
    grid = np.arange(t0, t1, STEP)
    fair = np.asarray(fair, float)
    mb, ma, _ = book(cand, grid)
    tt, tp, tsz = (trades[:, j] for j in range(3)) if len(trades) else (np.empty(0),) * 3
    inv, fills, posted = 0.0, [], 0.0
    for k, tq in enumerate(grid):
        f = fair[k]
        if f != f:
            continue
        sk = SKEW * inv
        bid, ask = cent_floor(f - h - sk), cent_ceil(f + h - sk)
        qb = min(SIZE, MAXINV - inv) if bid >= 0.01 and not (ma[k] == ma[k] and bid >= ma[k]) else 0
        qa = min(SIZE, MAXINV + inv) if ask <= 0.99 and not (mb[k] == mb[k] and ask <= mb[k]) else 0
        lo, hi = np.searchsorted(tt, tq, "right"), np.searchsorted(tt, min(tq + STEP, t1), "right")
        p, s, t = tp[lo:hi], tsz[lo:hi], tt[lo:hi]
        for side, q, px, hit in ((1, qb, bid, p < bid - 1e-9), (-1, qa, ask, p > ask + 1e-9)):
            if q <= 0:
                continue
            posted += q
            cum = np.cumsum(QUEUE * s[hit])
            got = np.diff(np.minimum(np.r_[0, cum], q))
            nz = got > 1e-12
            if not nz.any():
                continue
            tot = got[nz].sum()
            fee = cent_ceil(MAKER_RATE * fee_mult * tot * px * (1 - px)) if fee_mult else 0.0
            fills += [(ft, side, g, px, fee * g / tot) for ft, g in zip(t[hit][nz], got[nz])]
            inv += side * tot
    f = np.array(sorted(fills), dtype=float).reshape(-1, 5)
    return f, posted


def capital(f):
    """Largest collateral the position ever needed: long = qty x avg YES cost, short = qty x (1 - avg sale price)."""
    pos = avg = cap = 0.0
    for _, side, q, px, _ in f:
        d = side * q
        if pos == 0 or np.sign(pos) == np.sign(d):
            avg = (abs(pos) * avg + q * px) / (abs(pos) + q)
        elif abs(d) > abs(pos):
            avg = px
        pos += d
        if abs(pos) < 1e-9:
            pos = 0.0
        cap = max(cap, pos * avg if pos > 0 else -pos * (1 - avg))
    return cap


def score(f, cand, y, fee_mult):
    """Per-market totals: spread earned, adverse selection at 5/60 min and settlement, fees, P&L (settlement)."""
    if not len(f):
        return dict(n=0, qty=0.0, spread=0.0, as5=0.0, as60=0.0, asS=0.0, fees=0.0, pnl=0.0, cap=0.0, taker=0.0)
    t, side, q, px, fee = f.T
    m0, m5, m60 = (book(cand, t + d)[2] for d in (0, 300, 3600))
    m0 = np.where(np.isnan(m0), px, m0)  # no prior candle -> mid unknown, count no spread
    m5, m60 = np.where(np.isnan(m5), m0, m5), np.where(np.isnan(m60), m0, m60)
    return dict(n=len(f), qty=q.sum(), spread=(side * q * (m0 - px)).sum(), as5=(side * q * (m5 - m0)).sum(),
                as60=(side * q * (m60 - m0)).sum(), asS=(side * q * (y - m0)).sum(), fees=fee.sum(),
                pnl=(side * q * (y - px)).sum() - fee.sum(), cap=capital(f),
                taker=(TAKER_RATE * (fee_mult or 1.0) * q * px * (1 - px)).sum())


# ---------------- informed fair values ----------------
def weather_fair(sample):
    """ticker -> function(grid times) -> model P(bracket), from weather_study's NWS MOS/NBM data."""
    path = f"{D}/wx_err.pkl"
    if os.path.exists(path):
        errs = pd.read_pickle(path)
    else:
        errs = {}
        for city, (_, _, st, tz) in W.CITIES.items():
            mos, cli = W.load_mos(st), W.load_cli(st)
            for slot in ("T1 D-1 15:00", "T2 D 08:00"):
                e = {}
                for d in pd.date_range("2022-03-01", END.tz_localize(None)):
                    f, _ = W.forecast_at(mos, d, W.slot_time(d, tz, slot))
                    if d in cli.index and f == f:
                        e[d] = cli[d] - f
                errs[(city, slot)] = pd.Series(e)
            print(city, "forecast errors", flush=True)
        pd.to_pickle(errs, path)
    mos = {c: W.load_mos(v[2]) for c, v in W.CITIES.items()}
    out = {}
    for r in sample[sample.cat == "weather"].itertuples():
        tz = W.CITIES[r.sub][3]
        m = mos[r.sub][mos[r.sub].date == r.date]
        day0 = pd.Timestamp(r.date).tz_localize(tz).tz_convert("UTC").timestamp()
        e = {s: errs[(r.sub, s)][(errs[(r.sub, s)].index >= r.date - pd.Timedelta(days=W.WIN)) &
                                 (errs[(r.sub, s)].index <= r.date - pd.Timedelta(days=2))].to_numpy() for s in ("T1 D-1 15:00", "T2 D 08:00")}
        runs = {k: (g.avail.map(pd.Timestamp.timestamp).to_numpy(), g.f.to_numpy()) for k, g in m.groupby("model")}

        def fn(grid, runs=runs, e=e, day0=day0, lo=r.lo, hi=r.hi):
            res = np.full(len(grid), np.nan)
            for k, t in enumerate(grid):
                f = np.nan
                for model in ("NBS", "GFS"):
                    if model in runs:
                        a, v = runs[model]
                        i = np.searchsorted(a, t, "right") - 1
                        if i >= 0 and a[i] > t - 36 * 3600:
                            f = v[i]
                            break
                er = e["T1 D-1 15:00" if t < day0 else "T2 D 08:00"]
                if f == f and len(er) >= W.MIN_ERR:
                    res[k] = W.bracket_probs(f, er, [lo], [hi])[0]
            return res
        out[r.ticker] = fn
    return out


def pinnacle_fair(sample):
    pin = pinnacle()
    out = {}
    if "pin" not in sample:
        return out
    for r in sample[sample.pin.notna()].itertuples():
        lg, hm, aw, side = r.pin
        g = pin[(pin.league == lg) & (pin.home_team == hm) & (pin.away_team == aw) &
                ((pin.commence - r.T).abs() <= pd.Timedelta(minutes=45))].sort_values("snap")
        a = g.snap.map(pd.Timestamp.timestamp).to_numpy()
        v = (g.pH if side == "H" else 1 - g.pH).to_numpy()

        def fn(grid, a=a, v=v):
            i = np.searchsorted(a, grid, "right") - 1
            ok = (i >= 0) & (grid - a[np.maximum(i, 0)] <= PIN_MAX_AGE) if len(a) else np.zeros(len(grid), bool)
            return np.where(ok, v[np.maximum(i, 0)] if len(a) else np.nan, np.nan)
        out[r.ticker] = fn
    return out


# ---------------- report ----------------
def run(sample, data, informed, hs=(0.01, 0.02, 0.03)):
    rows = []
    for r in sample.itertuples():
        if r.ticker not in data:
            continue
        trades, cand, trunc = data[r.ticker]
        t0, t1 = r.t0.timestamp(), r.t1.timestamp()
        if trunc and len(trades):
            t0 = max(t0, trades[0, 0])  # page cap hit: start the window at the earliest fetched trade
        grid = np.arange(t0, t1, STEP)
        fairs = {"baseline": book(cand, grid)[2]}
        if r.ticker in informed:
            fairs["informed"] = informed[r.ticker](grid)
        for fv, fa in fairs.items():
            for h in hs:
                f, posted = simulate(trades, cand, fa, t0, t1, h, r.mult)
                rows.append(dict(ticker=r.ticker, cat=r.cat, sub=r.sub, main=r.main, T=r.T, day=r.T.date(), fv=fv, h=h,
                                 posted=posted, quoted=int(np.isfinite(fa).sum()), trades=len(trades), trunc=trunc,
                                 **score(f, cand, r.y, r.mult)))
    return pd.DataFrame(rows)


def roi_line(g):
    if g.cap.sum() <= 0:
        return dict(roi=np.nan, lo=np.nan, hi=np.nan)
    roi, lo, hi, _ = W.roi_boot(g.pnl.to_numpy(), g.cap.to_numpy(), g.day.astype(str).to_numpy())
    return dict(roi=roi, lo=lo, hi=hi)


def summarize(g):
    g = g.sort_values("T")
    n = len(g)
    half = g.iloc[: n // 2], g.iloc[n // 2:]
    hold = g.iloc[int(n * .7):]
    r = roi_line(g)
    sub = lambda x: x.pnl.sum() / x.cap.sum() if x.cap.sum() > 0 else np.nan
    out = dict(markets=n, filled=int((g.n > 0).sum()), fill_rate=g.qty.sum() / g.posted.sum() if g.posted.sum() else np.nan,
               qty=g.qty.sum(), spread=g.spread.sum(), as5=g.as5.sum(), as60=g.as60.sum(), asS=g.asS.sum(), fees=g.fees.sum(),
               pnl=g.pnl.sum(), per_mkt=g.pnl.mean(), cap=g.cap.sum(), **r, h1=sub(half[0]), h2=sub(half[1]), hold=sub(hold),
               taker=g.taker.sum())
    out["pass"] = bool(out["roi"] > 0 and out["lo"] > 0 and out["h1"] > 0 and out["h2"] > 0 and out["hold"] > 0)
    return out


def f2(x, f="{:+.1%}"):
    return "—" if x is None or x != x else f.format(x)


def table(res, keys, label):
    L = [f"| {label} | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, g in res.groupby(keys):
        s = summarize(g)
        k = " / ".join(map(str, k)) if isinstance(k, tuple) else k
        L.append(f"| {k} | {s['markets']} | {s['filled']} | {f2(s['fill_rate'], '{:.1%}')} | {s['qty']:,.0f} | {s['pnl']:+,.0f} | "
                 f"{s['per_mkt']:+.2f} | {s['cap']:,.0f} | {f2(s['roi'])} | [{f2(s['lo'])}, {f2(s['hi'])}] | {f2(s['h1'])} | "
                 f"{f2(s['h2'])} | {f2(s['hold'])} | {'PASS' if s['pass'] else 'fail'} |")
    return "\n".join(L)


def decomp(res, keys, label):
    L = [f"| {label} | contracts | spread earned ¢/ct | AS +5 min ¢/ct | AS +60 min ¢/ct | AS settlement ¢/ct | maker fee ¢/ct | "
         f"net ¢/ct | taker fee would be ¢/ct |", "|---|---|---|---|---|---|---|---|---|"]
    for k, g in res.groupby(keys):
        q = g.qty.sum()
        if q <= 0:
            continue
        c = lambda x: f"{100 * g[x].sum() / q:+.2f}"
        k = " / ".join(map(str, k)) if isinstance(k, tuple) else k
        L.append(f"| {k} | {q:,.0f} | {c('spread')} | {c('as5')} | {c('as60')} | {c('asS')} | {-100 * g.fees.sum() / q:+.2f} | "
                 f"{c('pnl')} | {100 * g.taker.sum() / q:.2f} |")
    return "\n".join(L)


def write_report(sample, data, res):
    S = sample[sample.ticker.isin(data)]
    cov = ["| category | sub | markets sampled | with data | first T | last T | trades fetched | page cap hit | maker-fee series |",
           "|---|---|---|---|---|---|---|---|---|"]
    for (c, s), g in sample.groupby(["cat", "sub"]):
        d = g[g.ticker.isin(data)]
        nt = sum(len(data[t][0]) for t in d.ticker)
        cov.append(f"| {c} | {s} | {len(g)} | {len(d)} | {g['T'].min():%Y-%m-%d} | {g['T'].max():%Y-%m-%d} | {nt:,} | "
                   f"{sum(data[t][2] for t in d.ticker)} | {'yes' if g.mult.iloc[0] else 'no'} (×{g.mult.iloc[0]:g}) |")
    main = res[res.main]
    m2 = main[main.h == H]
    allcat = m2.assign(cat="all")
    L = ["# Kalshi maker simulation: resting quotes around a fair value", "",
         f"Generated {pd.Timestamp.now():%Y-%m-%d %H:%M} by [maker_sim.py](../maker_sim.py). Paper study only: no orders, no accounts.", "",
         PREREG, "## Data coverage", "", "\n".join(cov), "",
         f"Pinnacle-matched games (extra sample, NFL/MLB 2026-09-10 → 11-19): {int(S.get('pin', pd.Series(dtype=object)).notna().sum())}. "
         "Kalshi trade prints are taker executions (price, size, time); there is no historical order book, so queue position "
         "and hidden size are unknown — the 0.5 queue share and the strict trade-through rule stand in for them.", "",
         "## Results, h = 2¢ (primary), main sample", "",
         "### Baseline fair value = the market's own mid (no edge)", "",
         table(pd.concat([m2[m2.fv == 'baseline'], allcat[allcat.fv == 'baseline']]), ["cat"], "category"), "",
         table(m2[m2.fv == "baseline"], ["cat", "sub"], "category / sub"), "",
         "### Informed fair value (weather: NWS forecast model)", "",
         table(m2[m2.fv == "informed"], ["cat"], "category"), "",
         table(m2[m2.fv == "informed"], ["cat", "sub"], "category / sub"), "",
         "### Sports: baseline vs Pinnacle on the same games (Pinnacle-matched sample, 2026-09-10 → 11-19)", "",
         table(res[(res.h == H) & res.ticker.isin(res[res.fv == 'informed'].ticker) & (res.cat == 'sports')], ["sub", "fv"], "league / fair"), "",
         "## Adverse-selection decomposition (h = 2¢; ¢ per filled contract)", "",
         "Spread earned = distance of the fill from the mid at fill time; AS = how far the mid then moves against the fill "
         "(negative = adverse). Net = spread + AS settlement − fee.", "",
         decomp(pd.concat([res[res.h == H], res[res.h == H].assign(cat="all")]), ["cat", "fv"], "category / fair"), "",
         decomp(res[res.h == H], ["cat", "sub", "fv"], "category / sub / fair"), "",
         "## Sensitivity: half-spread h (labelled sensitivity only, never decides a pass)", "",
         table(pd.concat([main, main.assign(cat="all")]), ["cat", "fv", "h"], "category / fair / h"), "",
         decomp(pd.concat([main, main.assign(cat="all")]), ["cat", "fv", "h"], "category / fair / h"), ""]
    open("reports/maker_sim_results.md", "w", encoding="utf-8").write("\n".join(L))


def main():
    sample = build_sample()
    if "fetch" in sys.argv:
        fetch(sample)
        return
    data = pd.read_pickle(DATA)
    informed = {**weather_fair(sample), **pinnacle_fair(sample)}
    res = run(sample, data, informed)
    res.to_pickle(f"{D}/results.pkl")
    write_report(sample, data, res)
    print(open("reports/maker_sim_results.md", encoding="utf-8").read()[-6000:])


if __name__ == "__main__":
    main()
