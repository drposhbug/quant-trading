"""Kalshi combos (KXMVE*, RFQ-priced parlays): is the NO side ("being the house") profitable after fees?
Writes reports/combo_results.md.   Run: python combo_study.py [--refresh]   (caches: data/combo/*.pkl, local only)

Sampling (by combo creation time): 3 seeded-random 30 s windows per day, 2025-09-15 .. 2026-11-15. Combos created in a
window come from GET /markets?mve_filter=only&min/max_created_ts (live; everything settled after the 2026-09-19
historical cutoff) plus, for windows before the cutoff, KXMVE tickers that traded in [t, t+90 s] on /historical/trades,
looked up on /historical/markets and kept if created in the window. Up to CAP per window are drawn at random (so each
window, roughly each day, carries similar weight); the window total is kept for volume estimates.
Price = the combo's first trade (the RFQ fill, seconds after creation). Outcome = settlement_value_dollars (YES payout,
product of leg values, so voided/fair-value legs give fractions). Fair = product of each leg's own mid (1-min candle
yes bid/ask, last candle ending <= t0, <= 60 min old; leg side "no" -> 1 - mid) at t0. Premium = price - fair.

PRE-REGISTERED RULE (fixed 2026-11-20 before any outcome was looked at): buy NO on every combo with premium >= 0.05 at
its first fill, at that fill's NO price (1 - p), hold to settlement, $1 flat stake. Primary fee: Kalshi taker
0.07*q*(1-q) rounded up to the cent per contract. Pass = holdout (chronologically last 30%) mean ROI > 0 with a
day-clustered bootstrap 95% CI above 0, and ROI > 0 in both halves of the discovery 70%. Also reported: per-order
rounding at the observed fill size, maker fee (combo maker = 0.035*q*(1-q) from 2026-08-20, 0 before), and no fee.
"""
import datetime as dt
import math
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import pm_study as P

import threading
import time

import requests

KX = P.KX
_lock, _last = threading.Lock(), [0.0]


def get(url, **params):
    """GET with a global throttle (~8 req/s across threads) and patient 429 backoff."""
    for i in range(12):
        with _lock:
            wait = _last[0] + 0.125 - time.time()
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        r = requests.get(url, params=params, headers={"User-Agent": "quant-research"}, timeout=60)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(2 ** i, 60))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()
REFRESH = "--refresh" in sys.argv
D = "data/combo"
WIN_CACHE, LEG_CACHE = f"{D}/windows.pkl", f"{D}/legs.pkl"  # written only by this script (data/ is local), so read_pickle is safe
CUTOFF = pd.Timestamp("2026-09-19", tz="UTC")       # GET /historical/cutoff (markets settled + trades before this)
MAKER_FEE_FROM = pd.Timestamp("2026-08-20 09:00", tz="UTC")
START, END = dt.date(2025, 9, 15), dt.date(2026, 11, 15)
W, PAD, PER_DAY, CAP = 30, 60, 3, 10
PREMIUM, HOLDOUT = 0.05, 0.30
HIST_LEGS = 1500

UTC = dt.timezone.utc
ts = lambda x: pd.Timestamp(x).tz_convert("UTC") if pd.Timestamp(x).tzinfo else pd.Timestamp(x, tz="UTC")


# ---------------- fees / maths (tested in test_combo_study.py) ----------------
def taker_fee_contract(q):
    """Kalshi taker fee 0.07*q*(1-q), rounded up to the cent per contract (conservative)."""
    return math.ceil(round(0.07 * q * (1 - q) * 100, 9)) / 100


def taker_fee_order(q, n):
    """Same fee rounded up once per order of n contracts, per contract."""
    n = max(n, 0.01)
    return math.ceil(round(0.07 * n * q * (1 - q) * 100, 9)) / 100 / n


def maker_fee(q, t):
    return 0.035 * q * (1 - q) if t >= MAKER_FEE_FROM else 0.0


def roi(q, payout_no, fee):
    """Return per $ staked buying NO at q (plus fee) with NO payout payout_no in [0, 1]."""
    return (payout_no - q - fee) / (q + fee)


def mid(c):
    """Mid from a candle dict (live *_dollars or historical plain keys; cents if > 1). NaN if no two-sided quote."""
    def f(side):
        d = c.get(side) or {}
        v = d.get("close_dollars", d.get("close"))
        return float(v) if v not in (None, "") else np.nan
    b, a = f("yes_bid"), f("yes_ask")
    if b > 1 or a > 1:
        b, a = b / 100, a / 100
    return (b + a) / 2 if 0 <= b < a <= 1 else np.nan


def leg_price(candles, t0, side, max_age=3600):
    cs = [c for c in candles if t0 - max_age <= c["end_period_ts"] <= t0]
    if not cs:
        return np.nan
    m = mid(max(cs, key=lambda c: c["end_period_ts"]))
    return m if side == "yes" else 1 - m


SPORTS = [("NFL", r"^KXNFL"), ("NCAAF", r"^KXNCAAF"), ("NBA", r"^KXNBA"), ("WNBA", r"^KXWNBA"),
          ("NCAAB", r"^KX(NCAAMB|NCAAB|NCAAWB|MARMAD)"), ("MLB", r"^KXMLB"), ("NHL", r"^KXNHL"),
          ("soccer", r"^KX(EPL|UCL|UEL|LALIGA|SERIEA|BUNDES|LIGUE|MLS|SOCCER|FIFA|WC|EFL|UECL|EREDIV|LIGAMX|BRASIL)"),
          ("tennis", r"^KX(ATP|WTA)"), ("golf", r"^KX(PGA|LIV|GOLF)"), ("MMA/boxing", r"^KX(UFC|MMA|BOX)"),
          ("crypto 15m", r"^KX\w+15M$"), ("crypto/fx other", r"^KX(BTC|ETH|SOL|XRP|DOGE|BNB|HYPE|EURUSD|USDJPY)")]


def leg_cat(event_ticker):
    s = event_ticker.split("-")[0]
    for name, pat in SPORTS:
        if re.search(pat, s):
            return name
    return "other"


def combo_cat(legs):
    cats = {leg_cat(l["event_ticker"]) for l in legs}
    return cats.pop() if len(cats) == 1 else "mixed"


def same_event(legs):
    """Any two legs on the same game/time slot (event suffix after the series), e.g. a same-game parlay."""
    suf = [l["event_ticker"].split("-", 1)[1] if "-" in l["event_ticker"] else l["event_ticker"] for l in legs]
    suf = [s.split("-")[0] for s in suf]  # KXNFLTEAMFIRSTTD-26NOV19INDHOU-HOU -> 26NOV19INDHOU
    return len(set(suf)) < len(suf)


def day_boot(r, day, B=2000, seed=0, w=None):
    """(Weighted) mean of r with a 95% CI from resampling whole days (clusters) with replacement."""
    r, day = np.asarray(r, float), np.asarray(day)
    w = np.ones(len(r)) if w is None else np.asarray(w, float)
    u, inv = np.unique(day, return_inverse=True)
    s, n = np.bincount(inv, r * w), np.bincount(inv, w)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), (B, len(u)))
    bs = s[idx].sum(1) / n[idx].sum(1)
    return s.sum() / n.sum(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def max_dd(pnl):
    c = np.cumsum(pnl)
    return float((c - np.maximum.accumulate(np.r_[0, c])[1:]).min()) if len(c) else 0.0


def worst_streak(lost):
    best = cur = 0
    for x in lost:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


# ---------------- data ----------------
def windows():
    rng, out, d = random.Random(20261120), [], START
    while d <= END:
        base = int(dt.datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp())
        out += [base + rng.randrange(0, 86400 - W) for _ in range(PER_DAY)]
        d += dt.timedelta(1)
    return out


def pages(url, n_max=50, **params):
    out, cur = [], None
    for _ in range(n_max):
        j = get(url, limit=1000, **params, **({"cursor": cur} if cur else {}))
        out += j.get("markets") or j.get("trades") or []
        cur = j.get("cursor")
        if not cur:
            break
    return out


def market_trades(m):
    tr = []
    if ts(m["created_time"]) < CUTOFF:
        tr += pages(f"{KX}/historical/trades", ticker=m["ticker"])
    if ts(m["close_time"]) >= CUTOFF:
        tr += pages(f"{KX}/markets/trades", ticker=m["ticker"])
    return sorted({t["trade_id"]: t for t in tr}.values(), key=lambda t: t["created_time"])


def one_window(t):
    a, b = t, t + W
    ms = {m["ticker"]: m for m in pages(f"{KX}/markets", 5, mve_filter="only", min_created_ts=a, max_created_ts=b)}
    if pd.Timestamp(a, unit="s", tz="UTC") < CUTOFF:
        cand = sorted({x["ticker"] for x in pages(f"{KX}/historical/trades", 30, min_ts=a, max_ts=b + PAD)
                       if x["ticker"].startswith("KXMVE")} - set(ms))
        for i in range(0, len(cand), 80):
            for m in get(f"{KX}/historical/markets", tickers=",".join(cand[i:i + 80]), limit=1000).get("markets", []):
                if a <= ts(m["created_time"]).timestamp() < b:
                    ms[m["ticker"]] = m
    total = len(ms)
    pick = random.Random(t).sample(sorted(ms), min(CAP, total))
    rows = []
    for k in pick:
        m = ms[k]
        if m.get("status") not in ("finalized", "settled") or m.get("settlement_value_dollars") in (None, ""):
            rows.append(dict(ticker=k, settled=False))
            continue
        tr = market_trades(m)
        rows.append(dict(ticker=k, settled=True, m=m, trades=tr))
    return dict(t=t, total=total, rows=rows)


def safe_window(t):
    try:
        return one_window(t)
    except Exception as e:  # skipped windows are retried on the next run (not cached)
        print(f"  window {t} failed: {e!s:.120}", flush=True)
        return None


def build_windows():
    cache = pd.read_pickle(WIN_CACHE) if os.path.exists(WIN_CACHE) and not REFRESH else {}
    todo = [t for t in windows() if t not in cache]
    os.makedirs(D, exist_ok=True)
    print(f"windows: {len(cache)} cached, {len(todo)} to fetch", flush=True)
    try:
        with ThreadPoolExecutor(4) as ex:
            for i, w in enumerate(ex.map(safe_window, todo)):
                if w is None:
                    continue
                cache[w["t"]] = w
                if i % 50 == 49:
                    pd.to_pickle(cache, WIN_CACHE)
                    print(f"  {i + 1}/{len(todo)}", flush=True)
    finally:
        pd.to_pickle(cache, WIN_CACHE)
    return cache


def flatten(cache):
    rows = []
    for w in cache.values():
        for r in w["rows"]:
            if not r["settled"] or not r["trades"]:
                continue
            m, tr = r["m"], r["trades"]
            f = tr[0]
            legs = m.get("mve_selected_legs") or []
            t0 = ts(f["created_time"])
            sec = tr[1:]
            rows.append(dict(
                ticker=m["ticker"], series=m["event_ticker"].split("-")[0], coll=m.get("mve_collection_ticker"),
                win=w["t"], win_total=w["total"], created=ts(m["created_time"]), close=ts(m["close_time"]), t0=t0,
                lag=(t0 - ts(m["created_time"])).total_seconds(), legs=legs, n_legs=len(legs), cat=combo_cat(legs),
                same=same_event(legs), p=float(f["yes_price_dollars"]), size=float(f["count_fp"]),
                first_taker=f["taker_side"], y=float(m["settlement_value_dollars"]), vol=float(m.get("volume_fp") or 0),
                n_sec=len(sec), sec_vol=sum(float(x["count_fp"]) for x in sec),
                sec_taker_yes=sum(float(x["count_fp"]) for x in sec if x["taker_side"] == "yes"),
                sec_pre2h=sum(float(x["count_fp"]) for x in sec if ts(x["created_time"]) <= ts(m["close_time"]) - pd.Timedelta(hours=5))))
    df = pd.DataFrame(rows).sort_values("t0").reset_index(drop=True)
    df["day"] = df.t0.dt.strftime("%Y-%m-%d")
    return df


def fetch_legs(c):
    """{leg ticker: candles} around t0: live batch endpoint first, per-market historical for the rest."""
    t0, tick = int(c["t0"].timestamp()), [l["market_ticker"] for l in c["legs"]]
    got = {}
    try:
        for x in get(f"{KX}/markets/candlesticks", market_tickers=",".join(tick), start_ts=t0 - 3600, end_ts=t0,
                     period_interval=1).get("markets", []):
            got[x["market_ticker"]] = x.get("candlesticks") or []
    except Exception:
        pass
    for k in tick:
        if not got.get(k):
            try:
                got[k] = get(f"{KX}/historical/markets/{k}/candlesticks", start_ts=t0 - 3600, end_ts=t0,
                             period_interval=1).get("candlesticks", [])
            except Exception:
                got[k] = []
    return got


def leg_sample(df):
    """Combos with <= 10 legs: all created after the cutoff (batch candles, cheap) + a seeded random HIST_LEGS of the
    earlier ones (per-leg historical candles, slow)."""
    e = df[df.n_legs <= 10]
    live = e.created >= CUTOFF
    return pd.concat([e[live], e[~live].sample(min(HIST_LEGS, (~live).sum()), random_state=1)]).sort_values("t0")


def build_legs(df):
    cache = pd.read_pickle(LEG_CACHE) if os.path.exists(LEG_CACHE) and not REFRESH else {}
    todo = [c for c in leg_sample(df).to_dict("records") if c["ticker"] not in cache]
    print(f"leg prices: {len(cache)} cached, {len(todo)} to fetch", flush=True)
    try:
        with ThreadPoolExecutor(4) as ex:
            for i, (c, g) in enumerate(zip(todo, ex.map(fetch_legs, todo))):
                cache[c["ticker"]] = g
                if i % 200 == 199:
                    pd.to_pickle(cache, LEG_CACHE)
                    print(f"  {i + 1}/{len(todo)}", flush=True)
    finally:
        pd.to_pickle(cache, LEG_CACHE)
    return cache


def fair_price(c, legc):
    g = legc.get(c["ticker"])
    if g is None:
        return np.nan
    t0 = int(c["t0"].timestamp())
    return float(np.prod([leg_price(g.get(l["market_ticker"], []), t0, l["side"]) for l in c["legs"]]))


# ---------------- report ----------------
PB = [(0, .01), (.01, .02), (.02, .05), (.05, .10), (.10, .20), (.20, .35), (.35, .50), (.50, 1.01)]
LB = [(2, 2), (3, 3), (4, 5), (6, 8), (9, 14), (15, 99)]


def lb(n):
    for a, b in LB:
        if a <= n <= b:
            return f"{a}" if a == b else f"{a}–{b if b < 99 else '+'}"
    return "1"


def calib(df, by):
    L = [f"| {by} | n | days | mean YES price | mean YES payout | payout / price | mean NO return (no fee) |",
         "|---|---|---|---|---|---|---|"]
    for k, g in df.groupby(by, sort=False):
        r = roi(1 - g.p, 1 - g.y, 0)
        L.append(f"| {k} | {len(g)} | {g.day.nunique()} | {g.p.mean():.4f} | {g.y.mean():.4f} | "
                 f"{g.y.mean() / g.p.mean():.2f} | {r.mean() * 100:+.2f}% |")
    return "\n".join(L)


def rule_line(name, g, col, w=None):
    if len(g) < 5:
        return f"| {name} | {len(g)} | – | – | – | – |"
    m, lo, hi = day_boot(g[col], g.day, w=w)
    return (f"| {name} | {len(g)} | {g.day.nunique()} | {m * 100:+.2f}% | [{lo * 100:+.2f}%, {hi * 100:+.2f}%] | "
            f"{(g.y > 0).mean():.3f} |")


RH = "| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |\n|---|---|---|---|---|---|"


def add_rois(d):
    q = 1 - d.p
    d["r_taker"] = [roi(a, 1 - y, taker_fee_contract(a)) for a, y in zip(q, d.y)]
    d["r_order"] = [roi(a, 1 - y, taker_fee_order(a, n)) for a, y, n in zip(q, d.y, d["size"])]
    d["r_maker"] = [roi(a, 1 - y, maker_fee(a, t)) for a, y, t in zip(q, d.y, d.t0)]
    d["r_nofee"] = roi(q, 1 - d.y, 0)
    return d


def block(L, title, d):
    L += [f"### {title}", "", RH]
    for col, nm in (("r_taker", "taker, fee ceil per contract (primary)"), ("r_order", "taker, fee ceil per order"),
                    ("r_maker", "maker (RFQ quoter) fee"), ("r_nofee", "no fee")):
        L.append(rule_line(nm, d, col))
    L.append(rule_line("maker fee, $-weighted by the fill's NO-side cost", d, "r_maker", d["size"] * (1 - d.p)))
    L.append("")


def main():
    cache = build_windows()
    df = flatten(cache)
    legc = build_legs(df)
    sel = set(leg_sample(df).ticker)
    df["fair"] = [fair_price(c, legc) if c["ticker"] in sel else np.nan for c in df.to_dict("records")]
    df["prem"] = df.p - df.fair
    df["pb"] = pd.cut(df.p, [a for a, _ in PB] + [1.01], right=False,
                      labels=[f"{a:.2f}–{min(b, 1):.2f}" for a, b in PB])
    df["lb"] = df.n_legs.map(lb)
    df = add_rois(df)
    df.to_pickle(f"{D}/combos.pkl")

    n_win = len(cache)
    unset = sum(1 for w in cache.values() for r in w["rows"] if not r["settled"])
    L = ["# Kalshi combos: is buying NO (being the house) profitable?",
         f"Generated {dt.date.today()} by `combo_study.py`. Pre-registered rule and sampling: see the script docstring.", ""]
    # inventory
    tot = pd.DataFrame([dict(t=pd.Timestamp(w["t"], unit="s", tz="UTC"), n=w["total"]) for w in cache.values()])
    tot["mo"] = tot.t.dt.strftime("%Y-%m")
    mon = tot.groupby("mo").n.mean() * 86400 / W
    df["mo"] = df.t0.dt.strftime("%Y-%m")
    gm = df.groupby("mo")
    L += ["## Inventory", "",
          f"{n_win} windows of {W}s ({PER_DAY}/day, {START}..{END}); {int(tot.n.sum()):,} combos created in them, "
          f"{len(df):,} sampled settled combos with a fill ({unset} sampled were unsettled/never filled, dropped). "
          f"Historical cutoff (GET /historical/cutoff): markets settled and trades before {CUTOFF.date()} live under "
          "/historical/*; /historical/markets has no time filter, so pre-cutoff combos are found through "
          "/historical/trades windows.", "",
          "| month | est. combos created / day | sampled | mean legs | median fill (contracts) | median fill $ (YES side) | "
          "median fill $ (NO side) | est. opening-fill NO-side $ / day | YES payout rate | NO ROI, maker fee | NO ROI, taker fee |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for mo, g in gm:
        L.append(f"| {mo} | {mon.get(mo, np.nan):,.0f} | {len(g)} | {g.n_legs.mean():.1f} | {g['size'].median():.0f} | "
                 f"{(g['size'] * g.p).median():.2f} | {(g['size'] * (1 - g.p)).median():.0f} | "
                 f"{mon.get(mo, np.nan) * (g['size'] * (1 - g.p)).mean() / 1e6:,.1f}M | {g.y.mean():.3f} | "
                 f"{g.r_maker.mean() * 100:+.1f}% | {g.r_taker.mean() * 100:+.1f}% |")
    L += ["", "Series: " + ", ".join(f"{k} {v}" for k, v in df.series.value_counts().items()),
          "", "Category (all legs same category, else mixed): " +
          ", ".join(f"{k} {v}" for k, v in df.cat.value_counts().items()),
          "", f"Same-event legs (same game / same 15-min slot): {df.same.mean():.0%}. Legs: median {df.n_legs.median():.0f},"
          f" max {df.n_legs.max()}. First fill seconds after creation: median {df.lag.median():.0f}. "
          f"Hours from fill to close: median {((df.close - df.t0).dt.total_seconds() / 3600).median():.1f}. "
          f"First fill taker side: YES {(df.first_taker == 'yes').mean():.0%}. Settlement values strictly between 0 and 1 "
          f"(voided/fair-value legs): {((df.y > 0) & (df.y < 1)).sum()} of {len(df)}.", ""]
    # calibration
    L += ["## Calibration of the first-fill YES price", "", "By price bucket:", "", calib(df.sort_values("p"), "pb"), "",
          "By number of legs:", "", calib(df.sort_values("n_legs"), "lb"), "",
          "By category:", "", calib(df, "cat"), "", "Same-event legs vs independent:", "", calib(df, "same"), ""]
    # premium
    f = df.dropna(subset=["fair"])
    f = f[f.fair > 0]
    L += ["## Parlay premium = first-fill YES price − product of leg mids at the same minute", "",
          f"Legs priced for {len(f):,} of {len(sel):,} attempted combos (≤10 legs: every one created after "
          f"{CUTOFF.date()} plus a random {HIST_LEGS} earlier; a leg needs a two-sided 1-min quote within 60 min before "
          "the fill).", "",
          "| slice | n | mean price | mean fair (product) | mean premium | median premium | premium / fair | mean payout | "
          "share premium ≥ 5pp |", "|---|---|---|---|---|---|---|---|---|"]
    for nm, g in [("all", f)] + [(f"legs {k}", g) for k, g in f.sort_values("n_legs").groupby("lb", sort=False)] + \
                 [(f"same-event={k}", g) for k, g in f.groupby("same")] + [(k, g) for k, g in f.groupby("cat") if len(g) >= 30]:
        L.append(f"| {nm} | {len(g)} | {g.p.mean():.4f} | {g.fair.mean():.4f} | {g.prem.mean() * 100:+.2f}pp | "
                 f"{g.prem.median() * 100:+.2f}pp | {(g.p.sum() / g.fair.sum() - 1) * 100:+.1f}% | {g.y.mean():.4f} | "
                 f"{(g.prem >= PREMIUM).mean():.1%} |")
    L += ["", "Does the product of legs forecast better than the combo price? (Brier, same combos)", "",
          f"combo price {np.mean((f.p - f.y) ** 2):.4f}, leg product {np.mean((f.fair.clip(0, 1) - f.y) ** 2):.4f}, "
          f"YES payout rate {f.y.mean():.4f}.", ""]
    # baseline: all combos NO
    L += ["## Results", ""]
    block(L, "Baseline: buy NO on every sampled combo at the first fill (= the RFQ maker's position)", df)
    # rule
    r = f[f.prem >= PREMIUM].sort_values("t0").reset_index(drop=True)
    cut = int(len(r) * (1 - HOLDOUT))
    disc, hold = r.iloc[:cut], r.iloc[cut:]
    h1, h2 = disc.iloc[:len(disc) // 2], disc.iloc[len(disc) // 2:]
    L += [f"### Pre-registered rule: premium ≥ {PREMIUM * 100:.0f}pp → buy NO (n = {len(r)})", "", RH]
    for nm, g in [("all", r), ("discovery first half", h1), ("discovery second half", h2),
                  (f"HOLDOUT last {HOLDOUT:.0%} ({hold.t0.min():%Y-%m-%d}..)" if len(hold) else "HOLDOUT", hold)]:
        L.append(rule_line(nm, g, "r_taker"))
    L += ["", "Same rule, other fee assumptions:", ""]
    block(L, "rule, all", r)
    block(L, "rule, holdout", hold)
    L += ["By legs / category / same-event (rule trades, primary fee):", "", RH]
    for k, g in r.sort_values("n_legs").groupby("lb", sort=False):
        L.append(rule_line(f"legs {k}", g, "r_taker"))
    for k, g in r.groupby("cat"):
        L.append(rule_line(k, g, "r_taker"))
    for k, g in r.groupby("same"):
        L.append(rule_line(f"same-event={k}", g, "r_taker"))
    ok = len(hold) >= 5 and day_boot(hold.r_taker, hold.day)[1] > 0 and h1.r_taker.mean() > 0 and h2.r_taker.mean() > 0
    L += ["", f"**Pre-registered verdict: {'PASS' if ok else 'FAIL'}** (holdout CI > 0 and both discovery halves > 0).", ""]
    # risk
    L += ["## Tail risk (flat $1 stakes, chronological)", "",
          "| book | n | total P&L $ | max drawdown $ | longest run of YES hits (NO losses) | worst day $ | largest single loss $ |",
          "|---|---|---|---|---|---|---|"]
    for nm, g in (("all combos, primary fee", df), ("rule, primary fee", r), ("rule, maker fee", r)):
        col = "r_maker" if "maker" in nm else "r_taker"
        pnl = g[col].to_numpy()
        L.append(f"| {nm} | {len(g)} | {pnl.sum():+.1f} | {max_dd(pnl):.1f} | {worst_streak(g.y.to_numpy() > 0)} | "
                 f"{g.groupby('day')[col].sum().min():+.1f} | {pnl.min():.1f} |")
    L += ["", "A NO stake at 0.99 makes +1% when the combo misses and −100% when it hits: about 1 hit per 100 such "
          "stakes erases the edge, so results hinge on a few hits.", ""]
    # capacity
    L += ["## Capacity", "",
          f"First fill size: median {df['size'].median():.0f} contracts, p90 {df['size'].quantile(.9):.0f}; NO-side $ "
          f"(size × (1−p)): median ${(df['size'] * (1 - df.p)).median():.0f}, p90 ${(df['size'] * (1 - df.p)).quantile(.9):,.0f}, "
          f"total in sample ${(df['size'] * (1 - df.p)).sum():,.0f}. Rule trades: median NO $ "
          f"{(r['size'] * (1 - r.p)).median() if len(r) else float('nan'):.0f}.",
          f"Secondary trading after the opening fill: {(df.n_sec > 0).mean():.0%} of combos have any; secondary volume = "
          f"{df.sec_vol.sum() / df['size'].sum():.0%} of opening-fill volume; share of secondary contracts where the taker "
          f"bought YES (i.e. a resting NO-side order was hit): {df.sec_taker_yes.sum() / max(df.sec_vol.sum(), 1):.0%}. "
          f"Secondary contracts traded ≥5h before close (a proxy for 'before the first leg starts'): "
          f"{df.sec_pre2h.sum() / df['size'].sum():.1%} of opening volume.",
          "Combo books show no standing quotes (yes bid 0 / ask 1) between trades: the only way to buy NO at the opening "
          "price is to be the RFQ quoter (maker, HVM 3 s confirm / 1 s execution timers, competing with ~5 combo makers "
          "answering in <300 ms).", ""]
    os.makedirs("reports", exist_ok=True)
    with open("reports/combo_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
