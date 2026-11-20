"""Which Polymarket groups should join the forward favourite paper tests? Writes reports/fav_backtest_results.md.
Run: python fav_backtest.py [--refresh] [--cap N]     (caches: data/fav_events_*.pkl, data/fav_prices.pkl; data/ is gitignored)

Rule (fixed before looking, same for every group): take the favourite side of each resolved binary market at a fixed
decision time and buy it if its price is 0.85-0.97; hold to resolution; flat stake.
  * sports games: decision = start - 2h (market gameStartTime, else event startTime, else slug date 00:00 UTC);
    last hourly CLOB point at or before it, no older than 2 days.
  * sports without a start time (golf / F1 / boxing / UFC cards): decision = scheduled endDate - 3 days.
  * non-sports: decision = scheduled endDate - 7 days (endDate is known in advance; closedTime would be lookahead).
  The market must be open at the decision (created before it, closed after it). Only clean 1/0 settlements count
  (voided / 50-50 / unresolved excluded). Volume >= $1,000 (lifetime volume: a mild lookahead, liquidity proxy only).
Cost: entry = price + 1c spread; fee per share = rate * p * (1-p) (sports 0.03 before 2026-07-10, 0.05 after;
  geopolitics 0; crypto 0.07; all other non-sports 0.04). pnl per $ = (won - c)/c - fee/c, as in betting/*.
Sample: all resolved events under each group's Gamma tags 2024-01..2026-11 (weekly endDate windows); per group a random
  sample of <= CAP candidate markets is priced. Bets/year = in-range rate in the sample x candidates in the last 12 months.
"""
import datetime as dt
import json
import math
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

import numpy as np
import pandas as pd

import pm_study as P
from correlations import holm
from pm_calibration import at, window

P.UA = {"User-Agent": "research-client"}
get, GAMMA = P.get, P.GAMMA
REFRESH = "--refresh" in sys.argv
CAP = int(sys.argv[sys.argv.index("--cap") + 1]) if "--cap" in sys.argv else 2000
START, END = pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-11-20", tz="UTC")
LO, HI, SPREAD, MIN_VOL = 0.85, 0.97, 0.01, 1000
FEE_SWITCH = pd.Timestamp("2026-07-10", tz="UTC")
PRICES = "data/fav_prices.pkl"  # all data/fav_* caches are written only by this script (local, gitignored): read_pickle is safe
H = pd.Timedelta(hours=1)
D = pd.Timedelta(days=1)

# umbrella tag ids queried (sports via /sports metadata, others via /tags/slug)
SPORT_TAGS = {"nba": 745, "wnba": 100254, "nfl": 450, "cfb": 100351, "cbb": 101178, "ncaab": 100149, "nhl": 899,
              "mlb": 100381, "soccer": 100350, "tennis": 864, "cricket": 517, "esports": 64, "ufc": 279,
              "boxing": 683, "f1": 435, "golf": 100219}
SPORT_SERIES = {"nba": (10345, "nba"), "wnba": (10105, "wnba"), "nfl": (12185, "nfl"), "cfb": (12756, "cfb"),
                "cbb": (10470, "cbb"), "nhl": (10346, "nhl"), "mlb": (3, "mlb"), "mls": (10189, "soccer"),
                "epl": (10188, "soccer"), "lal": (10193, "soccer"), "bun": (10194, "soccer"), "sea": (10203, "soccer"),
                "fl1": (10195, "soccer"), "ucl": (10204, "soccer"), "atp": (10365, "tennis"), "wta": (10366, "tennis"),
                "cs2": (10310, "esports"), "lol": (10311, "esports"), "dota2": (10309, "esports"),
                "val": (10369, "esports"), "ufc": (38, "ufc"), "ipl": (44, "cricket")}
OTHER_TAGS = {"politics": 2, "us-politics": 789, "elections": 144, "world-elections": 101206,
              "global-elections": 1597, "geopolitics": 100265, "economy": 100328, "fed": 159, "finance": 120,
              "pop-culture": 596, "tech": 1401, "business": 107, "weather": 84, "crypto": 21}
PREFIX = {"nba": "NBA", "wnba": "WNBA", "nfl": "NFL", "cfb": "NCAAF", "cbb": "NCAAB", "ncaab": "NCAAB", "nhl": "NHL",
          "mlb": "MLB", "mls": "MLS", "epl": "EPL", "lal": "La Liga", "bun": "Bundesliga", "sea": "Serie A",
          "fl1": "Ligue 1", "ucl": "UCL", "cs2": "CS2", "lol": "LoL", "dota2": "Dota", "val": "Valorant",
          "ufc": "MMA/UFC"}
UMBRELLA = {"soccer": "other soccer", "tennis": "other tennis", "cricket": "cricket", "esports": "esports other",
            "ufc": "MMA/UFC", "boxing": "boxing", "f1": "F1", "golf": "golf"}
NONSPORT_ORDER = [  # first match wins
    ("crypto", {21, 1312, 235, 102127}), ("weather", {84, 87}),
    ("economics/Fed", {100328, 159, 100196, 120, 101800}),
    ("tech/companies", {1401, 439, 101999, 1096, 1013, 600, 604, 107}),
    ("culture/awards", {596, 18, 53, 100}), ("geopolitics", {100265, 101970, 96, 154}),
    ("world elections", {101206, 1597}), ("US politics", {789, 2, 144, 126})]
EXISTING = {"ATP", "WTA", "EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "MLS", "UCL", "NBA"}
NOT_GAME = re.compile(r"spread|o/u|over/under|\bover\b|\bunder\b|total|handicap|\bmap \d|game \d|set \d|1st|first|"
                      r"half|quarter|period|inning|both teams|exact|correct score|points|rebounds|assists|yards|kills|"
                      r"tiebreak|\bby ko\b|method|round \d|go the distance|parlay", re.I)
SLUG_DATE = re.compile(r"-(\d{4}-\d{2}-\d{2})$")


def ts(s):
    if not s:
        return None
    try:
        return P.ts(s)
    except (ValueError, TypeError):
        return None


def fee_rate(group, sports, t):
    if sports:
        return 0.05 if t >= FEE_SWITCH else 0.03
    return {"geopolitics": 0.0, "crypto": 0.07}.get(group, 0.04)


def pnl(p, won, rate):
    """Profit per $1 staked buying the favourite at market price p (+1c spread), taker fee rate*p*(1-p) per share."""
    c = p + SPREAD
    return (won - c) / c - rate * p * (1 - p) / c


# ---------------- events ----------------
def slim(e):
    return dict(id=e["id"], slug=e.get("slug") or "", title=e.get("title") or "", start=e.get("startTime"),
                tags={int(t["id"]) for t in e.get("tags") or [] if str(t.get("id", "")).isdigit()},
                markets=[{k: m.get(k) for k in ("id", "question", "groupItemTitle", "outcomes", "outcomePrices",
                                                "clobTokenIds", "gameStartTime", "sportsMarketType", "startDate",
                                                "createdAt", "endDate", "closedTime", "volumeNum")}
                         for m in e.get("markets") or []])


def week_events(args):
    key, tag, monday, lag = args
    a, b = monday, monday + pd.Timedelta(days=7)
    out, off = [], 0
    extra = {"start_date_max": f"{b - lag:%Y-%m-%dT%H:%M:%SZ}"} if lag is not None else {}
    while off <= 5000:
        try:
            d = get(f"{GAMMA}/events", **{key: tag}, closed="true", limit=100, offset=off,
                    end_date_min=f"{a:%Y-%m-%dT%H:%M:%SZ}", end_date_max=f"{b:%Y-%m-%dT%H:%M:%SZ}", **extra)
        except Exception:
            break
        out += [slim(e) for e in d]
        if len(d) < 100:
            break
        off += 100
    return out


def fetch_tag(name, tag, lag, key="tag_id"):
    path = f"data/fav_events_{'s_' if key == 'series_id' else ''}{name}.pkl"
    if os.path.exists(path) and not REFRESH:
        return pd.read_pickle(path)
    mondays = list(pd.date_range(START - pd.Timedelta(days=7), END, freq="7D"))
    with ThreadPoolExecutor(8) as ex:
        evs = [e for w in ex.map(week_events, [(key, tag, m, lag) for m in mondays]) for e in w]
    os.makedirs("data", exist_ok=True)
    pd.to_pickle(evs, path)
    print(f"  {name}: {len(evs)} events", flush=True)
    return evs


def tennis_group(e):
    t = f"{e['title']} {e['slug']}".lower()
    if "doubles" in t:
        return None
    if re.search(r"challenger|\bitf\b|\b125\b|utr", t):
        return "other tennis"
    return {"atp": "ATP", "wta": "WTA"}.get(e["slug"].split("-")[0], "other tennis")


def sport_group(e, umbrella):
    pre = e["slug"].split("-")[0]
    if umbrella == "tennis":
        return tennis_group(e)
    if pre in PREFIX:
        return PREFIX[pre]
    if umbrella in UMBRELLA:
        return UMBRELLA[umbrella]
    return None  # league tag but not a game event (futures etc.)


def nonsport_group(e):
    if 1 in e["tags"] or 100639 in e["tags"]:
        return None
    for g, ids in NONSPORT_ORDER:
        if e["tags"] & ids:
            return g
    return None


def resolved(m):
    try:
        outs, px = json.loads(m["outcomes"] or "[]"), [float(x) for x in json.loads(m["outcomePrices"] or "[]")]
        tok = json.loads(m["clobTokenIds"] or "[]")
    except (ValueError, TypeError):
        return None
    if len(outs) != 2 or len(px) != 2 or len(tok) != 2:
        return None
    if not ((px[0] > 0.99 and px[1] < 0.01) or (px[1] > 0.99 and px[0] < 0.01)):
        return None  # voided, 50-50 or unresolved
    return outs, int(px[0] > 0.99), tok[0]


def candidates(e, group, sports):
    """One row per resolved binary market the rule could trade, with its decision time."""
    rows = []
    sm = SLUG_DATE.search(e["slug"])
    for m in e["markets"]:
        r = resolved(m)
        if r is None or float(m.get("volumeNum") or 0) < MIN_VOL:
            continue
        outs, y0, tok = r
        q = f"{m.get('question') or ''} {m.get('groupItemTitle') or ''}"
        opened, closed, end = ts(m.get("startDate") or m.get("createdAt")), ts(m.get("closedTime")), ts(m.get("endDate"))
        if not (opened and closed and end):
            continue
        kind = "yes" if outs == ["Yes", "No"] else "named"
        if sports:
            if m.get("sportsMarketType") not in (None, "moneyline") or NOT_GAME.search(q) or "/" in "".join(outs):
                continue
            st = ts(m.get("gameStartTime")) or ts(e["start"]) or (pd.Timestamp(sm.group(1), tz="UTC") if sm else None)
            if st is not None:
                dec, timing = st - 2 * H, "start-2h"
            elif group in ("golf", "F1", "boxing", "MMA/UFC"):
                dec, timing = end - 3 * D, "end-3d"
            else:
                continue
            if "draw" in q.lower():
                kind = "draw"
        else:
            if re.search(r"up or down", q, re.I):
                continue
            dec, timing = end - 7 * D, "end-7d"
        if not (START <= dec <= END and opened < dec < closed):
            continue
        rows.append(dict(mid=str(m["id"]), event=str(e["id"]), group=group, sports=sports, token=tok, y0=y0,
                         dec=dec, timing=timing, kind=kind, vol=float(m.get("volumeNum") or 0)))
    return rows


def build_candidates():
    rows, seen = [], set()
    for name, tag in SPORT_TAGS.items():
        for e in fetch_tag(name, tag, None):
            g = sport_group(e, name)
            if g and e["id"] not in seen:
                seen.add(e["id"])
                rows += candidates(e, g, True)
    for name, (sid, umbrella) in SPORT_SERIES.items():  # tags only cover ~2025-09 on; series reach further back
        for e in fetch_tag(name, sid, None, "series_id"):
            g = sport_group(e, umbrella)
            if g and e["id"] not in seen:
                seen.add(e["id"])
                rows += candidates(e, g, True)
    for name, tag in OTHER_TAGS.items():
        for e in fetch_tag(name, tag, 7 * D):
            g = nonsport_group(e)
            if g and e["id"] not in seen:
                seen.add(e["id"])
                rows += candidates(e, g, False)
    return pd.DataFrame(rows).drop_duplicates("mid")


# ---------------- prices ----------------
def price_at(r):
    try:
        s = window(r["token"], r["dec"] - 2 * D, r["dec"] + H)
    except Exception:
        return r["mid"], None  # None = fetch failed (retried next run); nan = no usable point
    return r["mid"], at(s, r["dec"])


def priced(cands):
    cache = pd.read_pickle(PRICES) if os.path.exists(PRICES) else {}
    sm = cands.sample(frac=1, random_state=11).groupby("group").head(CAP)
    todo = [r for r in sm.to_dict("records") if cache.get(r["mid"]) is None]
    print(f"pricing {len(todo)} of {len(sm)} sampled markets", flush=True)
    for i in range(0, len(todo), 2000):
        with ThreadPoolExecutor(12) as ex:
            cache.update(dict(ex.map(price_at, todo[i:i + 2000])))
        pd.to_pickle(cache, PRICES)
        print(f"  priced {min(i + 2000, len(todo))}/{len(todo)}", flush=True)
    sm = sm.copy()
    sm["p0"] = sm["mid"].map(lambda k: cache.get(k)).astype(float)
    return sm


def bets(sm):
    d = sm.dropna(subset=["p0"]).copy()
    d["p"] = np.maximum(d.p0, 1 - d.p0)
    d["won"] = np.where(d.p0 >= 0.5, d.y0, 1 - d.y0)
    d["fav_yes"] = np.where(d.p0 >= 0.5, d.kind == "yes", False)  # bought the YES side of a 'Will X win' market
    d = d[(d.p >= LO) & (d.p <= HI)].copy()
    d["rate"] = [fee_rate(g, s, t) for g, s, t in zip(d.group, d.sports, d.dec)]
    d["pnl"] = pnl(d.p, d.won, d.rate)
    d["cluster"] = np.where(d.sports, d.dec.dt.strftime("%Y-%m-%d"), d.event)
    return d.sort_values("dec")


# ---------------- stats ----------------
def cluster_stats(b, B=2000, seed=0):
    """ROI per $ (mean pnl over bets), cluster-bootstrap 95% CI, cluster-robust one-sided p for ROI > 0."""
    g = b.groupby("cluster")["pnl"].agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    roi = s.sum() / c.sum()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(s), (B, len(s)))
    boot = s[idx].sum(1) / c[idx].sum(1)
    k = len(s)
    if k > 2:
        u = s - roi * c  # ratio-estimator influence terms
        se = math.sqrt(k / (k - 1) * (u ** 2).sum()) / c.sum()
        p = 1 - NormalDist().cdf(roi / se) if se > 0 else np.nan
    else:
        p = 1.0
    return roi, np.percentile(boot, 2.5), np.percentile(boot, 97.5), p


def roi(b):
    return b.pnl.mean() if len(b) else np.nan


def pct(x):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x * 100:+.1f}%"


def summarize(b, cands, sm, name):
    n = len(b)
    if n == 0:
        return None
    rec = END - pd.Timedelta(days=365)
    sm_rec = sm[(sm.dec >= rec) & sm.p0.notna()]
    c_rec = (cands.dec >= rec).sum()
    per_year = (b.dec >= rec).sum() / len(sm_rec) * c_rec if len(sm_rec) else 0.0
    r, lo, hi, p = cluster_stats(b)
    cut = int(math.ceil(0.7 * n))
    half = n // 2
    sub = {k: roi(b[(b.p >= a) & (b.p < z)]) for k, (a, z) in
           {"85-90": (.85, .90), "90-95": (.90, .95), "95-97": (.95, .9701)}.items()}
    nsub = {k: int(((b.p >= a) & (b.p < z)).sum()) for k, (a, z) in
            {"85-90": (.85, .90), "90-95": (.90, .95), "95-97": (.95, .9701)}.items()}
    return dict(group=name, n=n, clusters=b.cluster.nunique(), cands=int(len(cands)), sampled=int(sm.p0.notna().sum()),
                per_year=per_year, win=b.won.mean(), price=b.p.mean(), roi=r, lo=lo, hi=hi, p=p,
                h1=roi(b.iloc[:half]), h2=roi(b.iloc[half:]), disc=roi(b.iloc[:cut]), hold=roi(b.iloc[cut:]),
                n_hold=n - cut, first=b.dec.min(), last=b.dec.max(), **{f"s{k}": v for k, v in sub.items()},
                **{f"n{k}": v for k, v in nsub.items()})


def combined(rows, bs, names):
    sel = [r for r in rows if r["group"] in names]
    if not sel:
        return 0, np.nan, (np.nan, np.nan)
    per_year = sum(r["per_year"] for r in sel)
    # expected ROI per bet weights each group by its forward bet rate, not its historical sample size
    w = np.array([r["per_year"] for r in sel])
    e = float(np.dot(w, [r["roi"] for r in sel]) / w.sum()) if w.sum() else np.nan
    allb = pd.concat([bs[r["group"]] for r in sel])
    _, lo, hi, _ = cluster_stats(allb.assign(cluster=allb.group + "|" + allb.cluster.astype(str)))
    return per_year, e, (lo, hi)


def main():
    cands = build_candidates()
    sm = priced(cands)
    allbets = bets(sm)
    rows, bs = [], {}
    for g in sorted(cands.group.unique()):
        b = allbets[allbets.group == g]
        s = summarize(b, cands[cands.group == g], sm[sm.group == g], g)
        if s:
            rows.append(s)
            bs[g] = b
    sy = allbets[(allbets.group.isin(["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "MLS", "UCL"])) & allbets.fav_yes]
    soccer_yes = summarize(sy, cands[cands.group.isin(["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "MLS", "UCL"])],
                           sm[sm.group.isin(["EPL", "La Liga", "Bundesliga", "Serie A", "Ligue 1", "MLS", "UCL"])],
                           "(top-7 soccer, team-win YES only)") if len(sy) else None
    adj = holm({r["group"]: r["p"] for r in rows if r["n"] >= 30})  # family = groups with >= 30 bets
    for r in rows:
        r["holm"] = adj.get(r["group"], np.nan)
        r["add"] = (r["group"] not in EXISTING and r["disc"] > 0 and r["hold"] > 0 and r["lo"] > -0.01
                    and r["n"] >= 30)
    write_report(rows, bs, cands, sm, allbets, soccer_yes)


def row_line(r):
    return (f"| {r['group']} | {r['n']} | {r['clusters']} | {r['per_year']:.0f} | {r['win']:.3f} | {r['price']:.3f} | "
            f"{pct(r['roi'])} | [{pct(r['lo'])}, {pct(r['hi'])}] | {r['p']:.3f} | {r.get('holm', np.nan):.3f} | "
            f"{pct(r['s85-90'])} ({r['n85-90']}) | {pct(r['s90-95'])} ({r['n90-95']}) | {pct(r['s95-97'])} ({r['n95-97']}) | "
            f"{pct(r['h1'])} / {pct(r['h2'])} | {pct(r['disc'])} | {pct(r['hold'])} ({r['n_hold']}) |")


HDR = ("| group | bets | clusters | bets/yr | win rate | avg price | ROI/$ | 95% CI (cluster boot) | p (ROI≤0) | Holm p | "
       "0.85–0.90 | 0.90–0.95 | 0.95–0.97 | halves | discovery 70% | holdout 30% (n) |\n"
       "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def write_report(rows, bs, cands, sm, allbets, soccer_yes):
    sports = [r for r in rows if bs[r["group"]].sports.iloc[0]]
    other = [r for r in rows if not bs[r["group"]].sports.iloc[0]]
    add = [r["group"] for r in rows if r["add"]]
    excl = [r["group"] for r in rows if not r["add"] and r["group"] not in EXISTING]
    exist_present = [g for g in EXISTING if g in bs]
    py_add, e_add, ci_add = combined(rows, bs, set(add))
    py_ex, e_ex, ci_ex = combined(rows, bs, set(exist_present))
    py_all, e_all, ci_all = combined(rows, bs, set(add) | set(exist_present))
    cov = cands.groupby([cands.group, cands.dec.dt.year]).size().unstack(fill_value=0)
    L = ["# Favourite backtest across Polymarket groups (which groups to add to the forward paper tests)",
         f"Generated {dt.date.today()} by `fav_backtest.py`. Window {START:%Y-%m-%d} → {END:%Y-%m-%d} (decision time).",
         "", "**Rule (fixed before looking, identical for all groups):** favourite side of each resolved binary market, "
         "price at the decision time (sports games: last hourly CLOB point ≥ 2h before start; sports without a start time "
         "— golf/F1/boxing/UFC cards — scheduled end − 3 days; non-sports: scheduled end − 7 days), buy if 0.85–0.97, hold "
         "to resolution. Entry = price + 1¢; fee = rate·p(1−p) per share (sports 0.03 → 0.05 from 2026-07-10, geopolitics "
         "0, crypto 0.07, other non-sports 0.04). Clean 1/0 settlements only; volume ≥ $1,000.", "",
         f"Candidates: {len(cands):,} markets; priced sample ≤ {CAP} per group ({int(sm.p0.notna().sum()):,} with a usable "
         f"price); bets (price in range): {len(allbets):,}. CI = bootstrap over clusters (sports: game day; non-sports: "
         "event). p = one-sided cluster-robust test of ROI > 0; Holm across all groups below. "
         "Bets/yr = in-range rate in the priced sample × candidates in the last 12 months.", "",
         "## Sports groups", "", HDR] + [row_line(r) for r in sports]
    if soccer_yes:
        L += [row_line({**soccer_yes, "holm": np.nan})]
    none = sorted(set(cands.group) - set(bs))
    if none:
        L += ["", "Groups with no favourite priced 0.85–0.97 at the decision time in the priced sample: "
              + ", ".join(f"{g} ({int(sm[(sm.group == g)].p0.notna().sum())} priced)" for g in none)
              + " — favourites in these sports are rarely that heavy before the game."]
    L += ["", "## Non-sports groups", "", HDR] + [row_line(r) for r in other]
    L += ["", "## Decision", "",
          "ADD = not already forward-tested, ROI > 0 in discovery (first 70%) AND holdout (last 30%), cluster-CI lower "
          "bound > −1%, ≥ 30 bets.", "",
          f"- **Add:** {', '.join(add) or 'none'}",
          f"- **Exclude:** {', '.join(excl) or 'none'}",
          f"- Existing forward groups present here: {', '.join(sorted(exist_present))}", "",
          "| set | bets/yr | expected ROI per bet (bets/yr-weighted) | pooled 95% CI |", "|---|---|---|---|",
          f"| existing (tennis ATP/WTA, top-7 soccer, NBA) | {py_ex:.0f} | {pct(e_ex)} | [{pct(ci_ex[0])}, {pct(ci_ex[1])}] |",
          f"| recommended additions | {py_add:.0f} | {pct(e_add)} | [{pct(ci_add[0])}, {pct(ci_add[1])}] |",
          f"| existing + additions | {py_all:.0f} | {pct(e_all)} | [{pct(ci_all[0])}, {pct(ci_all[1])}] |", "",
          "## Coverage (candidate markets by decision year)", "", cov.to_markdown(), "",
          "## Caveats", "",
          "- **Selection bias.** Groups are chosen *after* seeing these results (~30 groups). Even with Holm, the "
          "chosen set's backtest ROI is biased upward; the forward paper test is the verdict, not this table.",
          "- CLOB history price is an hourly mid/last, not an executable ask. The +1¢ spread is a flat assumption; "
          "thin markets (esports, small soccer leagues, challengers) often have wider books, which the forward rule's "
          "spread ≤ 0.05 / ask-within-0.05 filter will partly reject.",
          "- The fee schedule is applied retroactively (most of 2024–25 had no taker fees) so the ROI is what the rule "
          "would earn under today's fees.",
          "- Only markets Gamma still lists with a 1/0 settlement are seen (survivorship); voids are excluded rather "
          "than counted as 0 return. Tag coverage of 2024 is thin (Polymarket added per-game markets and sport tags "
          "mostly in 2025), so most of the evidence is 2025–26.",
          "- Multi-leg events (golf/F1 winners, elections, awards) mean many correlated bets per event; clustering by "
          "event handles that in the CI, but the number of independent outcomes is the cluster count, not the bet count.",
          "- Non-sports decision uses the endDate Gamma shows now; markets whose end date was extended or edited "
          "after creation are timed from the final date (a mild lookahead the forward test does not have).",
          "- Bets/yr for multi-leg groups (US politics, elections, culture, golf, F1) counts every leg; the number of "
          "independent outcomes per year is closer to the cluster share of that figure.",
          "- Bets/yr counts every in-range favourite at one decision time; the forward scripts poll repeatedly and enter "
          "at the first in-range observation, so live entry counts and prices will differ."]
    os.makedirs("reports", exist_ok=True)
    with open("reports/fav_backtest_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
