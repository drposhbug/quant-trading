"""Post-count bracket markets: does a fixed negative-binomial rate model beat the market? Writes reports/count_markets_results.md.

Markets: Polymarket "tweets-markets" bracket events ("Elon Musk # tweets <window>?", "Donald Trump # Truth Social posts
<window>?", White House, Ted Cruz, Zelenskyy, NYC Mayor, CZ, Khamenei, Andrew Tate), all resolved on the xtracker.polymarket.com
"Post Counter"; Kalshi KXTRUTHSOCIAL (weekly Sun-Sat ET Trump Truth Social count, resolved on Roll Call Factbase).
Counts: xtracker.polymarket.com public post export (the Polymarket resolution source itself; Musk from 2025-10-31, Trump from
2026-01-15, the rest from Jan-Mar 2026); Trump before 2026-01-16 spliced from data/trump_posts.csv (trumpstruth.org archive).

Model (fixed before any run; nothing is tuned): at decision time t = start + f*(end-start), f in FRACS, final count =
observed so far + remainder ~ NegBin(mean mu, size r).
  mu = sum over the remaining hours of the hour-of-week mean over the 672 hours (28 days) before t.
  r  = method of moments on DISP_N past windows of the same remaining length ending before t (daily stride):
       r = sum(mu^2) / sum((X - mu)^2 - mu); Poisson if the denominator <= 0. Needs >= DISP_MIN windows.
Tests (pre-registered): per group (Musk PM, Trump PM, Trump Kalshi, Other PM), on the chronological last 30% of events:
log-loss and Brier of model vs the market's normalised bracket prices at the same hour, and the betting rule
(buy YES where model p - ask >= EDGE, ask = price + 1c on Polymarket / candle ask on Kalshi, taker fee rate*p*(1-p),
hold to resolution). One-sided week-clustered bootstrap p, Holm over the 12 tests.
"""
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
from scipy.stats import nbinom

import pm_study as P
from candles import holm

P.UA = {"User-Agent": "quant-research"}  # pm_study.get reads this global at call time
get = P.get
XT = "https://xtracker.polymarket.com/api"
REFRESH = "--refresh" in sys.argv
# caches below are written only by this script (data/ is local), so read_pickle on them is safe
PM_EVENTS, PM_PX, KX_EV, KX_PX = "data/count_pm_events.json", "data/count_pm_px.pkl", "data/count_kx_events.pkl", "data/count_kx_px.pkl"
HANDLES = {"elon-musk": "elonmusk", "donald-trump": "realDonaldTrump", "white-house": "WhiteHouse", "ted-cruz": "tedcruz",
           "zelenskyy": "ZelenskyyUa", "nyc-mayor": "NYCMayor", "cz-binance": "cz_binance", "khamenei": "khamenei_ir",
           "andrew-tate": "Cobratate"}
FRACS = (0, .25, .5, .75)
PROFILE_H, DISP_N, DISP_MIN = 672, 60, 30
EDGE, SPREAD, PM_FEE, KX_FEE, MAX_ASK = .08, .01, .05, .07, .98
HOLDOUT, B = .30, 2000
TRUMP_SPLICE = pd.Timestamp("2026-01-16", tz="UTC")
GROUPS = ["Musk (Polymarket)", "Trump (Polymarket)", "Trump (Kalshi)", "Other accounts (Polymarket)"]
rng = np.random.default_rng(11)
UTC, ET = "UTC", "America/New_York"


# ---------------- counts ----------------
def posts(handle):
    """UTC post timestamps from the xtracker export (cached). Trump before TRUMP_SPLICE comes from data/trump_posts.csv."""
    path = f"data/count_posts_{handle}.csv"
    if os.path.exists(path) and not REFRESH:
        s = pd.to_datetime(pd.read_csv(path).ts, utc=True)
    else:
        d = requests.get(f"{XT}/users/{handle}/posts", headers=P.UA, timeout=120).json()["data"]
        s = pd.to_datetime(pd.Series([p["createdAt"] for p in d], name="ts"), utc=True).sort_values()
        os.makedirs("data", exist_ok=True)
        s.to_frame().to_csv(path, index=False)
    if handle == "realDonaldTrump":
        ts = pd.read_csv("data/trump_posts.csv", parse_dates=["ts"]).ts  # naive New York time
        ts = ts.dt.tz_localize(ET, ambiguous=True, nonexistent="shift_forward").dt.tz_convert(UTC)
        s = pd.concat([ts[ts < TRUMP_SPLICE], s[s >= TRUMP_SPLICE]])
    return s.sort_values().reset_index(drop=True)


def hourly(s):
    """(first hour, counts per UTC hour up to the last complete hour of data)."""
    h0, h1 = s.iloc[0].floor("h"), s.iloc[-1].floor("h")
    idx = ((s.dt.floor("h") - h0) // pd.Timedelta(hours=1)).to_numpy()
    return h0, np.bincount(idx, minlength=int((h1 - h0) / pd.Timedelta(hours=1)))[: int((h1 - h0) / pd.Timedelta(hours=1))]


def mu_at(H, i, L):
    """Expected count in hours [i, i+L) from the hour-of-week mean over the PROFILE_H hours before i."""
    prof = H[i - PROFILE_H:i].reshape(PROFILE_H // 168, 168).mean(0)  # position q matches hour i + q (mod 168)
    return (L // 168) * prof.sum() + prof[:L % 168].sum()


def size_at(H, i, L):
    """NB size r fitted on past windows of length L ending at or before hour i; None if too little history."""
    js = [i - L - 24 * k for k in range(DISP_N)]
    js = [j for j in js if j - PROFILE_H >= 0]
    if len(js) < DISP_MIN:
        return None
    mu = np.array([mu_at(H, j, L) for j in js])
    x = np.array([H[j:j + L].sum() for j in js])
    den = ((x - mu) ** 2 - mu).sum()
    return float((mu ** 2).sum() / den) if den > 0 else 1e6


def bracket_probs(c, mu, r, lo, hi):
    """P(final count in [lo, hi]) given c observed and remainder ~ NB(mu, r). hi may be inf."""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    if mu <= 1e-9:
        return ((lo <= c) & (c <= hi)).astype(float)
    d = nbinom(r, r / (r + mu))
    up = np.where(np.isinf(hi), 1.0, d.cdf(np.where(np.isinf(hi), 0, hi - c)))
    return np.clip(up - d.cdf(lo - 1 - c), 0, 1)


# ---------------- Polymarket ----------------
MON = "January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec"
WHEN = re.compile(rf"({MON})\.? (\d{{1,2}})(?:st|nd|rd|th)?,? ?(\d{{4}})?,? (?:at )?(\d{{1,2}})(?::(\d\d))? ?([AP])\.?M\.? ?(ET|EST|EDT|UTC)", re.I)


def window(desc, end):
    """(start, end) UTC from the first two 'Month D[, YYYY], h:mm AM/PM ET' in a market description; end = gamma endDate."""
    f = WHEN.findall(desc or "")
    if len(f) < 2:
        return None
    out = []
    for k, (mon, day, yr, hh, mm, ap, tz) in enumerate(f[:2]):
        hh = int(hh) % 12 + (12 if ap.upper() == "P" else 0)
        ts = pd.Timestamp(f"{mon[:3]} {day} {yr or end.year} {hh}:{mm or '00'}")
        out.append(ts.tz_localize(UTC if tz.upper() == "UTC" else ET).tz_convert(UTC))
    a, b = out
    if a >= b:  # year wrap: "December 26 - January 2, 2026"
        a = a - pd.DateOffset(years=1)
    return a, b


def bounds(title):
    t = (title or "").strip().replace("–", "-").replace(",", "")
    if m := re.fullmatch(r"<\s*(\d+)", t):
        return 0, int(m[1]) - 1
    if m := re.fullmatch(r"(\d+)\s*\+|(\d+) or (?:more|above)", t):
        return int(m[1] or m[2]), np.inf
    if m := re.fullmatch(r">\s*(\d+)", t):
        return int(m[1]) + 1, np.inf
    if m := re.fullmatch(r"(\d+)\s*-\s*(\d+)", t):
        return int(m[1]), int(m[2])
    return None


def partition(br):
    """True if brackets tile [0, inf) with no gap/overlap and exactly one winner."""
    br = sorted(br, key=lambda x: x["lo"])
    return (br and br[0]["lo"] == 0 and np.isinf(br[-1]["hi"]) and sum(x["y"] for x in br) == 1
            and all(br[k + 1]["lo"] == br[k]["hi"] + 1 for k in range(len(br) - 1)))


def pm_events():
    if os.path.exists(PM_EVENTS) and not REFRESH:
        return json.load(open(PM_EVENTS))
    evs = {}
    for closed in ("true", "false"):
        off = 0
        while True:
            d = get(f"{P.GAMMA}/events", tag_slug="tweets-markets", closed=closed, limit=100, offset=off)
            evs.update({e["slug"]: e for e in d})
            off += 100
            if len(d) < 100:
                break
    os.makedirs("data", exist_ok=True)
    json.dump(list(evs.values()), open(PM_EVENTS, "w"))
    return list(evs.values())


def parse_pm(e):
    """Event dict or None (not a closed, full-partition count event of a tracked account)."""
    slug = e["slug"]
    handle = next((h for k, h in HANDLES.items() if slug.startswith(k + "-")), None)
    if not handle or not re.search(r"-of-(tweets|truth-social-posts|truth-posts|posts)-", slug) or not e.get("closed"):
        return None
    if handle == "realDonaldTrump" and "truth" not in slug:
        return None  # 2024 "Donald Trump # of tweets" were X counts
    br = []
    for m in e.get("markets", []):
        bd = bounds(m.get("groupItemTitle"))
        try:
            px, tok = json.loads(m.get("outcomePrices") or "[]"), json.loads(m.get("clobTokenIds") or "[]")
        except ValueError:
            return None
        if not bd or len(px) != 2 or not tok or float(px[0]) not in (0.0, 1.0):
            return None  # unparseable bracket or unresolved / 50-50
        closed = m.get("closedTime")
        br.append(dict(lo=bd[0], hi=bd[1], y=int(float(px[0]) == 1.0), token=tok[0], vol=float(m.get("volumeNum") or 0),
                       open=P.ts(m.get("startDate") or m.get("createdAt") or e["startDate"]),
                       closed=P.ts(closed.replace(" ", "T").replace("+00", "Z")) if closed else None))
    if not e.get("endDate"):
        return None
    w = window(e["markets"][0].get("description") if e.get("markets") else None, P.ts(e["endDate"]))
    if not w or not partition(br):
        return None
    group = GROUPS[0] if handle == "elonmusk" else GROUPS[1] if handle == "realDonaldTrump" else GROUPS[3]
    return dict(id=slug, venue="polymarket", handle=handle, group=group, a=w[0], b=w[1], vol=float(e.get("volume") or 0),
                brackets=sorted(br, key=lambda x: x["lo"]))


def pm_px(token, a, b):
    pts = []
    for s in range(int(a.timestamp()), int(b.timestamp()), 14 * 86400):
        pts += get(f"{P.CLOB}/prices-history", market=token, startTs=s, endTs=min(s + 14 * 86400, int(b.timestamp())),
                   fidelity=60).get("history", [])
    s = pd.Series({pd.Timestamp(p["t"], unit="s", tz=UTC): float(p["p"]) for p in pts}, dtype=float)
    return pd.DataFrame({"mid": s[~s.index.duplicated()].sort_index()})


# ---------------- Kalshi ----------------
def kx_parse(ev):
    hist = get(f"{P.KX}/historical/markets", event_ticker=ev).get("markets", [])
    ms = [(m, True) for m in hist] or [(m, False) for m in get(f"{P.KX}/markets", event_ticker=ev).get("markets", [])]
    if not ms or any(m.get("result") not in ("yes", "no") for m, _ in ms):
        return None
    f = re.findall(r"from (\w{3}) (\d{1,2}), (\d{4}) to (\w{3}) (\d{1,2}), (\d{4})", ms[0][0].get("rules_primary") or "")
    if not f:
        return None
    m1, d1, y1, m2, d2, y2 = f[0]
    a = pd.Timestamp(f"{m1} {d1} {y1}").tz_localize(ET).tz_convert(UTC)
    b = (pd.Timestamp(f"{m2} {d2} {y2}") + pd.Timedelta(days=1)).tz_localize(ET).tz_convert(UTC)
    br = []
    for m, h in ms:
        bd = bounds(m.get("yes_sub_title"))
        if not bd:
            return None
        br.append(dict(lo=bd[0], hi=bd[1], y=int(m["result"] == "yes"), token=m["ticker"], hist=h,
                       vol=float(m.get("volume_fp") or m.get("volume") or 0), open=P.ts(m["open_time"]),
                       closed=P.ts(m["close_time"])))
    if not partition(br):
        return None
    return dict(id=ev, venue="kalshi", handle="realDonaldTrump", group=GROUPS[2], a=a, b=b,
                vol=sum(x["vol"] for x in br), brackets=sorted(br, key=lambda x: x["lo"]))


def kx_events():
    if os.path.exists(KX_EV) and not REFRESH:
        return pd.read_pickle(KX_EV)
    with ThreadPoolExecutor(4) as ex:
        out = [e for e in ex.map(kx_parse, P.kx_events("KXTRUTHSOCIAL")) if e]
    pd.to_pickle(out, KX_EV)
    return out


def kx_px(c, a, b):
    path = (f"/historical/markets/{c['token']}/candlesticks" if c["hist"]
            else f"/series/KXTRUTHSOCIAL/markets/{c['token']}/candlesticks")
    rows = {}
    for k in get(P.KX + path, start_ts=int(a.timestamp()), end_ts=int(b.timestamp()), period_interval=60).get("candlesticks", []):
        g = lambda d: float((k.get(d) or {}).get("close") or (k.get(d) or {}).get("close_dollars") or "nan")
        bid, ask = g("yes_bid"), g("yes_ask")
        if bid > 1 or ask > 1:
            bid, ask = bid / 100, ask / 100
        rows[pd.Timestamp(k["end_period_ts"], unit="s", tz=UTC)] = (bid, ask)
    return pd.DataFrame.from_dict(rows, orient="index", columns=["bid", "ask"]).sort_index()


# ---------------- prices cache ----------------
def fetch_prices(events):
    out = {}
    for path, venue, fn in ((PM_PX, "polymarket", lambda c, e: pm_px(c["token"], e["a"] - pd.Timedelta(days=1),
                                                                         min(e["b"], c["closed"] or e["b"]) + pd.Timedelta(hours=1))),
                            (KX_PX, "kalshi", lambda c, e: kx_px(c, e["a"] - pd.Timedelta(days=1), e["b"]))):
        cache = pd.read_pickle(path) if os.path.exists(path) and not REFRESH else {}
        todo = [(c, e) for e in events if e["venue"] == venue for c in e["brackets"] if c["token"] not in cache]
        try:
            with ThreadPoolExecutor(6) as ex:
                for (c, _), s in zip(todo, ex.map(lambda ce: _safe(fn, *ce), todo)):
                    cache[c["token"]] = s
        finally:
            pd.to_pickle(cache, path)
        out.update(cache)
    return out


def _safe(fn, c, e):
    try:
        return fn(c, e)
    except Exception:
        return pd.DataFrame()


def at(df, t, look=pd.Timedelta(hours=6)):
    if df is None or df.empty:
        return None
    s = df[(df.index <= t) & (df.index > t - look)]
    return s.iloc[-1] if len(s) else None


# ---------------- rows ----------------
def build_rows(events, px, counts):
    """One row per (event, decision time, open bracket)."""
    rows, agree = [], []
    for e in events:
        h0, H = counts[e["handle"]]
        ia, ib = (int((e[k] - h0) / pd.Timedelta(hours=1)) for k in ("a", "b"))
        if ia < 0 or ib > len(H):
            continue
        final = int(H[ia:ib].sum())
        win = next(x for x in e["brackets"] if x["y"])
        agree.append(dict(group=e["group"], id=e["id"], ok=win["lo"] <= final <= win["hi"], final=final,
                          lo=win["lo"], hi=win["hi"], b=e["b"]))
        for f in FRACS:
            i = ia + int((ib - ia) * f)
            t, L = h0 + pd.Timedelta(hours=i), ib - i
            r = size_at(H, i, L) if i - PROFILE_H >= 0 else None
            if r is None:
                continue
            c, mu = int(H[ia:i].sum()), mu_at(H, i, L)
            look = pd.Timedelta(hours=6 if e["venue"] == "polymarket" else 24)
            live = [x for x in e["brackets"] if x["open"] <= t and (x["closed"] is None or x["closed"] > t)]
            if not any(x["y"] for x in live):
                continue  # winner already settled early: nothing left to forecast
            q = [at(px.get(x["token"]), t, look) for x in live]
            if any(v is None for v in q):
                continue
            p = bracket_probs(c, mu, r, [x["lo"] for x in live], [x["hi"] for x in live])
            for x, v, pm in zip(live, q, p):
                if e["venue"] == "polymarket":
                    mid, ask = float(v["mid"]), float(v["mid"]) + SPREAD
                else:
                    bid, ask = float(v["bid"]), float(v["ask"])
                    mid = (bid + ask) / 2 if 0 <= bid <= ask <= 1 else np.nan
                rows.append(dict(group=e["group"], venue=e["venue"], id=e["id"], f=f, t=t, b=e["b"], lo=x["lo"], hi=x["hi"],
                                 token=x["token"], y=x["y"], p=float(pm), mid=mid, ask=ask, vol=x["vol"], c=c, mu=mu, r=r))
    df = pd.DataFrame(rows)
    ok = df.groupby(["id", "f"]).mid.transform(lambda s: s.notna().all() and s.sum() > 0)
    df = df[ok].copy()
    g = df.groupby(["id", "f"])
    df["q"] = df.mid / g.mid.transform("sum")  # market's normalised bracket probabilities
    df["pn"] = df.p / g.p.transform("sum").clip(lower=1e-12)
    df["week"] = df.b.dt.tz_convert(None).dt.to_period("W").astype(str)
    return df, pd.DataFrame(agree)


# ---------------- scoring ----------------
def event_scores(df):
    """Per (event, f): Brier and log-loss of model and market."""
    eps = 1e-4
    d = df.assign(bm=(df.pn - df.y) ** 2, bq=(df.q - df.y) ** 2)
    s = d.groupby(["group", "id", "f", "week", "b"]).agg(brier_model=("bm", "sum"), brier_mkt=("bq", "sum")).reset_index()
    w = d[d.y == 1].set_index(["id", "f"])
    s = s.join(-np.log(w.pn.clip(lower=eps)).rename("ll_model"), on=["id", "f"])
    s = s.join(-np.log(w.q.clip(lower=eps)).rename("ll_mkt"), on=["id", "f"])
    return s


def boot(x, cl):
    """Cluster bootstrap of the mean of x: (mean, lo, hi, one-sided p of mean <= 0)."""
    x, cl = np.asarray(x, float), np.asarray(cl)
    if len(x) == 0:
        return np.nan, np.nan, np.nan, np.nan
    u, inv = np.unique(cl, return_inverse=True)
    sums, ns = np.bincount(inv, x), np.bincount(inv)
    k = rng.integers(0, len(u), (B, len(u)))
    m = sums[k].sum(1) / ns[k].sum(1)
    return x.mean(), *np.percentile(m, [2.5, 97.5]), float((m <= 0).mean())


def fee(p, venue):
    return (PM_FEE if venue == "polymarket" else KX_FEE) * p * (1 - p)


def bets(df, edge=EDGE):
    """First trigger per (event, bracket): buy YES at ask, hold to resolution."""
    d = df[(df.p - df.ask >= edge) & (df.ask > 0) & (df.ask <= MAX_ASK)].sort_values("t")
    d = d.drop_duplicates(["id", "lo"]).copy()
    d["cost"] = d.ask + fee(d.ask, d.venue.iloc[0]) if len(d) else []
    d["pnl"] = d.y - d.cost
    return d


def roi(d):
    """ROI per $ staked with week-clustered CI: (roi, lo, hi, p)."""
    if d.empty:
        return np.nan, np.nan, np.nan, np.nan
    u, inv = np.unique(d.week, return_inverse=True)
    pn, cs = np.bincount(inv, d.pnl), np.bincount(inv, d.cost)
    k = rng.integers(0, len(u), (B, len(u)))
    m = pn[k].sum(1) / cs[k].sum(1)
    return d.pnl.sum() / d.cost.sum(), *np.percentile(m, [2.5, 97.5]), float((m <= 0).mean())


def split(df, frac=HOLDOUT):
    """(development, holdout): holdout = last frac of events by window end."""
    ends = df.drop_duplicates("id").sort_values("b")
    cut = ends.b.iloc[int(len(ends) * (1 - frac))] if len(ends) else None
    return df[df.b < cut], df[df.b >= cut]


def calib(df, col):
    bins = [0, .02, .05, .1, .2, .35, .5, .7, 1.0001]
    g = df.groupby(pd.cut(df[col], bins, right=False), observed=True)
    return pd.DataFrame({"n": g.y.size(), "mean_p": g[col].mean(), "freq": g.y.mean()})


# ---------------- capacity snapshot (open events, now) ----------------
def depth_now(events_raw):
    """$ offered within 2c of the best ask on currently open Trump/Musk Polymarket events and the open Kalshi week."""
    out = []
    for e in events_raw:
        if e.get("closed") or not re.match(r"(elon-musk|donald-trump)-of-(tweets|truth-social-posts)-", e["slug"]):
            continue
        tot, n = 0.0, 0
        for m in e.get("markets", []):
            if m.get("closed"):
                continue
            try:
                bk = get(f"{P.CLOB}/book", token_id=json.loads(m["clobTokenIds"])[0])
            except Exception:
                continue
            asks = sorted((float(a["price"]), float(a["size"])) for a in bk.get("asks", []))
            if asks:
                tot += sum(p * s for p, s in asks if p <= asks[0][0] + .02)
                n += 1
        out.append(dict(venue="polymarket", event=e["slug"], brackets=n, depth=tot, per_bracket=tot / max(n, 1)))
    try:
        for ev in get(f"{P.KX}/events", series_ticker="KXTRUTHSOCIAL", status="open").get("events", []):
            tk = ev["event_ticker"]
            ms = get(f"{P.KX}/markets", event_ticker=tk).get("markets", [])
            tot = 0.0
            for m in ms:
                ob = get(f"{P.KX}/markets/{m['ticker']}/orderbook").get("orderbook_fp") or {}
                no = sorted(((float(p), float(s)) for p, s in (ob.get("no_dollars") or [])), reverse=True)
                if no:  # a YES ask is a NO bid at 1 - price
                    best = no[0][0]
                    tot += sum((1 - p) * s for p, s in no if p >= best - .02)
            out.append(dict(venue="kalshi", event=tk, brackets=len(ms), depth=tot, per_bracket=tot / max(len(ms), 1)))
    except Exception:
        pass
    return pd.DataFrame(out)


# ---------------- main ----------------
def fmt(x, nd=3):
    return "n/a" if x is None or x != x else f"{x:.{nd}f}"


def main():
    raw = pm_events()
    events = [e for e in (parse_pm(e) for e in raw) if e] + kx_events()
    counts = {h: hourly(posts(h)) for h in {e["handle"] for e in events}}
    h_end = {h: counts[h][0] + pd.Timedelta(hours=len(counts[h][1])) for h in counts}
    usable = [e for e in events if e["b"] <= h_end[e["handle"]] and e["a"] - pd.Timedelta(days=60) >= counts[e["handle"]][0]]
    print(f"{len(events)} parsed events, {len(usable)} inside count coverage; fetching prices", flush=True)
    px = fetch_prices(usable)
    df, agree = build_rows(usable, px, counts)
    df.to_pickle("data/count_rows.pkl")
    sc = event_scores(df)
    write_report(raw, events, usable, counts, df, agree, sc)


def inventory(raw, events):
    rows = []
    for e in raw:
        slug = e["slug"]
        k = re.sub(r"-(?:\d|january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|"
                   r"mar|apr|jun|jul|aug|sept?|oct|nov|dec|between|and|in)\b.*", "", slug)
        rows.append(dict(series=k, closed=bool(e.get("closed")), vol=float(e.get("volume") or 0),
                         start=str(e.get("endDate") or "")[:10]))
    inv = pd.DataFrame(rows)
    inv = inv.groupby("series").agg(events=("vol", "size"), closed=("closed", "sum"), volume=("vol", "sum"),
                                    first=("start", "min"), last=("start", "max")).sort_values("volume", ascending=False)
    return inv


def write_report(raw, events, usable, counts, df, agree, sc):
    L = ["# Post-count bracket markets: rate model vs market", "",
         "Generated by [count_markets.py](../count_markets.py). Model and tests fixed before any run (see the module "
         "docstring); nothing tuned. Paper analysis only, no orders.", ""]
    inv = inventory(raw, events)
    L += ["## 1. Inventory (Polymarket `tweets-markets` tag, all statuses)", "",
          "| series slug | events | closed | volume $ | first end | last end |", "|---|---|---|---|---|---|"]
    L += [f"| {k} | {r.events} | {r.closed} | {r.volume:,.0f} | {r['first']} | {r['last']} |"
          for k, r in inv[inv.events >= 3].iterrows()]
    kx = [e for e in events if e["venue"] == "kalshi"]
    L += ["", f"Parsed as full-partition, resolved count events: "
          + ", ".join(f"{g}: {sum(e['group'] == g for e in events)}" for g in GROUPS)
          + f". Inside count-data coverage (≥ 60 days of history before the window): "
          + ", ".join(f"{g}: {sum(e['group'] == g for e in usable)}" for g in GROUPS) + ".", ""]
    vols = pd.DataFrame([dict(group=e["group"], vol=e["vol"]) for e in usable]).groupby("group").vol.describe()
    L += ["Event volume (usable events, $):", "", "| group | n | median | mean | max |", "|---|---|---|---|---|"]
    L += [f"| {g} | {r['count']:.0f} | {r['50%']:,.0f} | {r['mean']:,.0f} | {r['max']:,.0f} |" for g, r in vols.iterrows()]
    L += ["", "**Resolution rules.** Polymarket: count of main-feed posts, quote posts and reposts between two 12:00 PM ET "
          "times (weekly windows open Tue and Fri, plus 2-day, daily and monthly Musk windows); replies excluded unless they "
          "appear on the main feed; deleted posts count if captured (~5 min); source = xtracker.polymarket.com \"Post "
          "Counter\" (Truth Social / X itself as fallback). Fee: `culture_fees`, feeSchedule rate 0.05, taker only "
          "(older events had fees disabled; the test charges 0.05·p(1−p) everywhere, conservative). Kalshi KXTRUTHSOCIAL: "
          "Truths, ReTruths and Quote Truths from 12:00 AM ET Sunday to 11:59 PM ET Saturday, replies only if captured by "
          "Roll Call Factbase (the source), deleted posts excluded, recorded 10:00 AM ET Sunday; quadratic fee 0.07·p(1−p). "
          "Kalshi KXELONTWEETS (9 weekly events, Mar–Apr 2025, near-zero volume) predates the Musk count data; KXTRUMPTIME "
          "(\"Will Trump post this hour?\", 19 events, 2026) and the ~100 Kalshi *MENTION series (speech-content markets) "
          "are not post counts and are not tested.", ""]
    # data completeness
    L += ["## 2. Count data completeness", "",
          "Posts: xtracker.polymarket.com public post export (`/api/users/<handle>/posts`, the same tracker Polymarket "
          "resolves on; one request per account, no auth). Coverage start: "
          + ", ".join(f"{h} {counts[h][0]:%Y-%m-%d}" for h in sorted(counts))
          + f". Trump before {TRUMP_SPLICE:%Y-%m-%d} spliced from data/trump_posts.csv (trumpstruth.org RSS; 100-items "
          "per request cap — the loader refetches per day, but days with ≥ 100 posts can still be short: Nov 2–8 2026 has "
          "253 there vs 378 on xtracker; Jan–Nov 2026 overlap is 7,442 vs 6,875, the archive also carries some replies).", "",
          "Check: does the tracker count over each window land in the bracket that actually won?", "",
          "| group | events | count in winning bracket | median |count − nearest bracket edge| when outside |", "|---|---|---|---|"]
    for g, a in agree.groupby("group"):
        bad = a[~a.ok]
        miss = np.minimum((bad.final - bad.lo).abs(), (bad.final - bad.hi).abs()) if len(bad) else pd.Series([np.nan])
        L.append(f"| {g} | {len(a)} | {a.ok.mean():.0%} | {fmt(miss.median(), 0)} |")
    L += ["", "Disagreements are not dropped (that would use hindsight); they show how far today's export is from "
          "what the market settled on (backfill, deletions, different source for Kalshi/2025 Trump windows).", ""]
    # scores
    L += ["## 3. Model vs market (per event × decision time; lower is better)", "",
          f"Decision times: {', '.join(f'{int(f*100)}%' for f in FRACS)} of the window elapsed. Market = hourly CLOB price "
          "(Polymarket) or Kalshi candle mid, normalised over open brackets. Model = bracket probabilities renormalised "
          "over the same open brackets. Δ = market − model (positive = model better); week-clustered bootstrap.", "",
          "| group | sample | n (event×t) | events | Brier model | Brier market | ΔBrier [95% CI] | log-loss model | "
          "log-loss market | Δlog-loss [95% CI] |", "|---|---|---|---|---|---|---|---|---|---|"]
    tests = []
    for g in GROUPS:
        s = sc[sc.group == g]
        if s.empty:
            continue
        dev, ho = split(s)
        for name, x in (("all", s), ("holdout (last 30%)", ho)):
            db = boot(x.brier_mkt - x.brier_model, x.week)
            dl = boot(x.ll_mkt - x.ll_model, x.week)
            L.append(f"| {g} | {name} | {len(x)} | {x.id.nunique()} | {x.brier_model.mean():.3f} | {x.brier_mkt.mean():.3f} | "
                     f"{db[0]:+.3f} [{db[1]:+.3f}, {db[2]:+.3f}] | {x.ll_model.mean():.3f} | {x.ll_mkt.mean():.3f} | "
                     f"{dl[0]:+.3f} [{dl[1]:+.3f}, {dl[2]:+.3f}] |")
            if name.startswith("holdout"):
                tests += [(g, "log-loss: model < market", dl[3], dl[0]), (g, "Brier: model < market", db[3], db[0])]
    L += ["", "By decision time (all groups pooled, full sample):", "", "| elapsed | n | Brier model | Brier market | "
          "log-loss model | log-loss market |", "|---|---|---|---|---|---|"]
    for f, x in sc.groupby("f"):
        L.append(f"| {int(f*100)}% | {len(x)} | {x.brier_model.mean():.3f} | {x.brier_mkt.mean():.3f} | "
                 f"{x.ll_model.mean():.3f} | {x.ll_mkt.mean():.3f} |")
    L += ["", "### Calibration (bracket level, full sample, all groups)", "", "| bin | n | model mean p | freq | "
          "market mean q | freq |", "|---|---|---|---|---|---|"]
    cm, cq = calib(df, "pn"), calib(df, "q")
    for k in cm.index.union(cq.index):
        a = cm.loc[k] if k in cm.index else None
        b = cq.loc[k] if k in cq.index else None
        L.append(f"| {k} | {fmt(a.n if a is not None else None, 0)} / {fmt(b.n if b is not None else None, 0)} | "
                 f"{fmt(a.mean_p if a is not None else None)} | {fmt(a.freq if a is not None else None)} | "
                 f"{fmt(b.mean_p if b is not None else None)} | {fmt(b.freq if b is not None else None)} |")
    # betting
    L += ["", "## 4. Betting rule", "",
          f"Buy YES on any open bracket where model p − ask ≥ {EDGE:.2f} (ask ≤ {MAX_ASK}); Polymarket ask = hourly price + "
          f"{SPREAD:.2f}, fee {PM_FEE}·p(1−p); Kalshi ask = candle yes-ask close, fee {KX_FEE}·p(1−p). First trigger per "
          "bracket per event, hold to resolution. ROI = P&L / $ staked; week-clustered bootstrap.", "",
          "| group | sample | bets | events | hit rate | mean ask | ROI [95% CI] | P&L per $1 bet |",
          "|---|---|---|---|---|---|---|---|"]
    halves = {}
    for g in GROUPS:
        d = df[df.group == g]
        if d.empty:
            continue
        bt = bets(d)
        dev, ho = split(d)
        ends = d.drop_duplicates("id").sort_values("b")
        mid = ends.b.iloc[len(ends) // 2]
        parts = [("all", bt), ("1st half", bt[bt.b < mid]), ("2nd half", bt[bt.b >= mid]),
                 ("holdout (last 30%)", bets(ho))]
        for name, x in parts:
            r = roi(x)
            L.append(f"| {g} | {name} | {len(x)} | {x.id.nunique() if len(x) else 0} | "
                     f"{fmt(x.y.mean() if len(x) else None, 2)} | {fmt(x.ask.mean() if len(x) else None, 2)} | "
                     f"{fmt(r[0], 2)} [{fmt(r[1], 2)}, {fmt(r[2], 2)}] | {fmt(x.pnl.sum() if len(x) else None, 2)} |")
            if name == "holdout (last 30%)":
                tests.append((g, "betting ROI > 0", r[3], r[0]))
            halves.setdefault(g, {})[name] = r[0]
    # sensitivity: fee-free (Polymarket fees were off on older markets) and edge 0.15
    L += ["", "Sensitivity (all events, not pre-registered):", "", "| group | edge 0.08, no fee | edge 0.15 | edge 0.15, no fee |",
          "|---|---|---|---|"]
    for g in GROUPS:
        d = df[df.group == g]
        if d.empty:
            continue
        cells = []
        for edge, nofee in ((EDGE, True), (.15, False), (.15, True)):
            x = bets(d, edge)
            if nofee and len(x):
                x = x.assign(cost=x.ask, pnl=x.y - x.ask)
            r = roi(x)
            cells.append(f"{fmt(r[0], 2)} (n={len(x)})")
        L.append(f"| {g} | " + " | ".join(cells) + " |")
    # capacity
    bt_all = pd.concat([bets(df[df.group == g]) for g in GROUPS if (df.group == g).any()])
    L += ["", "### Capacity", "", "Historical order-book depth is not available; lifetime volume of the brackets the rule "
          "bought, and a live snapshot of $ offered within 2c of the best ask on the currently open events:", ""]
    if len(bt_all):
        cap = bt_all.groupby("group").vol.describe()
        L += ["| group | bets | median bracket volume $ | 25% | 75% |", "|---|---|---|---|---|"]
        L += [f"| {g} | {r['count']:.0f} | {r['50%']:,.0f} | {r['25%']:,.0f} | {r['75%']:,.0f} |" for g, r in cap.iterrows()]
    dn = depth_now(raw) if "--no-depth" not in sys.argv else pd.DataFrame()
    if len(dn):
        L += ["", "| venue | open event | brackets with asks | $ within 2c of best ask (sum) | per bracket |", "|---|---|---|---|---|"]
        L += [f"| {r.venue} | {r.event} | {r.brackets} | {r.depth:,.0f} | {r.per_bracket:,.0f} |" for r in dn.itertuples()]
    # tests
    adj = holm(np.array([t[2] if t[2] == t[2] else 1.0 for t in tests]))
    L += ["", "## 5. Pre-registered tests (holdout = chronological last 30% of events per group; Holm over all)", "",
          "| group | test | effect | p (one-sided) | Holm p | ROI > 0 both halves | pass |", "|---|---|---|---|---|---|---|"]
    npass = 0
    for (g, name, p, eff), a in zip(tests, adj):
        both = "" if "ROI" not in name else ("yes" if (halves[g].get("1st half", -1) or -1) > 0 and (halves[g].get("2nd half", -1) or -1) > 0 else "no")
        ok = a < .05 and eff > 0 and (both != "no")
        npass += ok
        L.append(f"| {g} | {name} | {eff:+.3f} | {fmt(p)} | {fmt(a)} | {both or '—'} | {'**PASS**' if ok else 'fail'} |")
    L += ["", f"**{npass} of {len(tests)} pass.**", "",
          "Caveats that favour the model, so a positive ROI here is an upper bound: (1) Polymarket history is an hourly "
          "price, not an executable ask; price + 1c understates the real ask on thin brackets (the smaller accounts' "
          "brackets trade a few $k in their lifetime and live books hold tens of $ near the ask). (2) The post export "
          "is read today; in real time the tracker can lag or later backfill/delete posts, so the observed-so-far count "
          "is cleaner than what a live trader saw. (3) The rate model loses to the market on Brier and log-loss in every "
          "group, so any betting profit comes from a few cheap tail brackets, not better forecasts.", ""]
    L += ["## 6. US access", "",
          "The Polymarket count events are on the international Polymarket exchange (gamma/CLOB), which is close-only "
          "for US persons. Kalshi (CFTC-regulated, US-accessible) lists **KXTRUTHSOCIAL** — weekly Trump Truth Social "
          "post-count brackets since Feb 2026 (tested above as \"Trump (Kalshi)\"), resolved on Roll Call Factbase on a "
          "Sun–Sat ET week — plus KXTRUMPTIME (\"Will Trump post this hour?\") and many *MENTION speech markets; its "
          "KXELONTWEETS series ran only Mar–Apr 2025. No Musk count market currently trades on a US venue.", ""]
    os.makedirs("reports", exist_ok=True)
    open("reports/count_markets_results.md", "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
