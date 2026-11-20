"""Is Polymarket (and Kalshi) well calibrated? Writes reports/pm_calibration.md.
Run: python pm_calibration.py [--refresh]      (caches: data/pm_cal_*.pkl; data/ is gitignored)

Sample: resolved binary Polymarket markets with endDate 2023-01..2026-11 (CLOB history starts ~late 2022), volume >= $500.
Per week, gamma /markets ordered by conditionId (a hash, so a pseudo-random draw w.r.t. topic and outcome), 300 per
week -> pool; classify by regex into categories; stratified random sample of <= PER_CELL per (category x volume tercile).
Reference time T = min(endDate, closedTime). YES price = last hourly CLOB point at or before T - h (h = 1, 7, 30 days),
no older than 2 days. Outcome = which outcome paid $1 (outcomePrices 1/0). "YES" = first outcome (team A for sports).
Kalshi: Fed / CPI / macro series via /historical + live markets, mid price from hourly candles, same horizons.
"""
import datetime as dt
import json
import math
import os
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

import pm_study as P

P.UA = {"User-Agent": "quant-research-monitor"}  # pm_study.get reads this global at call time
get, GAMMA, CLOB = P.get, P.GAMMA, P.CLOB
REFRESH = "--refresh" in sys.argv
# caches are written only by this script (data/ is local, gitignored), so read_pickle on them is safe
POOL, SAMPLE, KXC, IPO = (f"data/pm_cal_{x}.pkl" for x in ("pool", "sample", "kalshi", "ipo"))
H = (1, 7, 30)
PER_CELL = 250
CATS = [  # first match wins
    ("crypto", r"bitcoin|\bbtc\b|ethereum|\beth\b|solana|\bxrp\b|doge|crypto|token|airdrop|\bfdv\b|memecoin|binance|"
               r"coinbase|stablecoin|\bsol\b|up or down|pump\.fun|megaeth|hyperliquid"),
    ("econ/fed", r"\bfed\b|fomc|interest rate|\bbps\b|\bcpi\b|inflation|\bgdp\b|recession|unemployment|jobs report|"
                 r"payroll|tariff|s&p|nasdaq|treasury|yield|crude|oil price|gold|powell|rate cut|rate hike|stock market"),
    ("sports", r"\bvs\.?\b|nba|nfl|mlb|nhl|ufc|premier league|champions league|la liga|serie a|bundesliga|super bowl|"
               r"world series|stanley cup|grand prix|\bf1\b|tennis|golf|\bpga\b|\batp\b|\bwta\b|\bopen\b|fifa|world cup|"
               r"olympic|boxing|win on 20|mvp|playoffs|finals|championship|\bo/u\b|spread|counter-strike|league of legends|"
               r"dota|valorant|esports|cricket|ipl|wimbledon|heisman|draft"),
    ("politics", r"election|president|trump|biden|harris|senate|congress|governor|parliament|prime minister|minister|"
                 r"\bvote\b|nominee|primary|party|ukraine|russia|israel|gaza|hamas|iran|china|putin|zelensky|ceasefire|"
                 r"supreme court|mayor|democrat|republican|gop|white house|cabinet|pope|nato|war\b|military|strike on|"
                 r"invade|impeach|government shutdown|executive order|deport|maduro|netanyahu|xi jinping"),
    ("tech/companies", r"apple|google|openai|anthropic|tesla|nvidia|microsoft|\bmeta\b|amazon|\bai\b|gpt|gemini|grok|"
                       r"claude|\bipo\b|earnings|elon|musk|spacex|tiktok|starship|market cap|largest company|ceo|"
                       r"acquire|robotaxi|iphone|x\.com|twitter|neuralink|xai"),
    ("culture", r"movie|box office|album|song|spotify|oscar|grammy|emmy|taylor swift|tweet|youtube|mrbeast|netflix|"
                r"billboard|kardashian|person of the year|rotten tomatoes|eurovision|tv show|celebrity|kanye|drake|"
                r"time 100|super bowl halftime|wedding|baby|podcast|streamer|kick|twitch|mention|say "),
]


def category(m):
    text = f"{m['question']} {m['event']}".lower()
    for name, pat in CATS:
        if re.search(pat, text):
            return name
    if m["outcomes"] != ["Yes", "No"]:
        return "sports"  # team-vs-team style two-name outcomes
    return "other (weather etc.)"


# ---------------- Polymarket pool + sample ----------------
def week_pool(monday):
    out = []
    for off in (0, 100, 200):
        d = get(f"{GAMMA}/markets", closed="true", limit=100, offset=off, order="conditionId", ascending="true",
                end_date_min=f"{monday:%Y-%m-%d}T00:00:00Z", end_date_max=f"{monday + dt.timedelta(6):%Y-%m-%d}T23:59:59Z",
                volume_num_min=500)
        for m in d:
            try:
                outs, px = json.loads(m.get("outcomes") or "[]"), [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
                tok = json.loads(m.get("clobTokenIds") or "[]")
            except (ValueError, TypeError):
                continue
            if len(outs) != 2 or len(px) != 2 or len(tok) != 2 or not m.get("closedTime") or not m.get("endDate"):
                continue
            if not ((px[0] > 0.99 and px[1] < 0.01) or (px[1] > 0.99 and px[0] < 0.01)):
                continue  # unresolved, voided 50/50 or disputed
            ev = (m.get("events") or [{}])[0]
            out.append(dict(id=m["id"], question=m["question"], event=ev.get("title", ""), event_id=ev.get("id", m["id"]),
                            outcomes=outs, y=int(px[0] > 0.99), vol=float(m.get("volumeNum") or 0), token=tok[0],
                            start=P.ts(m.get("startDate") or m.get("createdAt")),
                            T=min(P.ts(m["endDate"]), P.ts(m["closedTime"].replace(" ", "T").replace("+00", "Z"))),
                            fees=bool(m.get("feesEnabled"))))
        if len(d) < 100:
            break
    return out


def build_pool():
    if os.path.exists(POOL) and not REFRESH:
        return pd.read_pickle(POOL)
    mondays = [dt.date(2023, 1, 2) + dt.timedelta(7 * i) for i in range(202)]
    with ThreadPoolExecutor(8) as ex:
        rows = [r for w in ex.map(week_pool, mondays) for r in w]
    df = pd.DataFrame(rows).drop_duplicates("id")
    df["cat"] = df.apply(category, axis=1)
    os.makedirs("data", exist_ok=True)
    df.to_pickle(POOL)
    return df


def window(token, a, b):
    pts = get(f"{CLOB}/prices-history", market=token, startTs=int(a.timestamp()), endTs=int(b.timestamp()),
              fidelity=60).get("history", [])
    return pd.Series({pd.Timestamp(p["t"], unit="s", tz="UTC"): float(p["p"]) for p in pts}, dtype=float).sort_index()


def at(s, t):
    if s.empty:
        return np.nan
    s = s[(s.index <= t) & (s.index > t - pd.Timedelta(days=2))]
    return float(s.iloc[-1]) if len(s) else np.nan


def horizons(r):
    T, d = r["T"], pd.Timedelta(days=1)
    try:
        s = pd.concat([window(r["token"], T - 9 * d, T - d), window(r["token"], T - 32 * d, T - 30 * d)])
    except Exception:
        return {f"p{h}": np.nan for h in H}
    return {f"p{h}": at(s, T - h * d) if T - h * d >= r["start"] else np.nan for h in H}


def build_sample(pool):
    if os.path.exists(SAMPLE) and not REFRESH:
        return pd.read_pickle(SAMPLE)
    pool = pool.copy()
    pool["vt"] = pool.groupby("cat")["vol"].transform(lambda v: pd.qcut(v.rank(method="first"), 3, labels=False))
    sm = pool.sample(frac=1, random_state=7).groupby(["cat", "vt"]).head(PER_CELL)
    with ThreadPoolExecutor(8) as ex:
        hz = list(ex.map(horizons, sm.to_dict("records")))
    sm = pd.concat([sm.reset_index(drop=True), pd.DataFrame(hz)], axis=1)
    sm.to_pickle(SAMPLE)
    return sm


# ---------------- Kalshi ----------------
KX_SERIES = ["KXFED", "KXFEDDECISION", "KXCPI", "KXCPIYOY", "KXGDP", "KXPAYROLLS", "KXU3"]


def kx_event_markets(series, ev):
    hist = get(f"{P.KX}/historical/markets", event_ticker=ev).get("markets", [])
    ms = [(m, True) for m in hist] or [(m, False) for m in get(f"{P.KX}/markets", event_ticker=ev).get("markets", [])]
    return [dict(id=m["ticker"], series=series, event=ev, hist=h, y=int(m["result"] == "yes"),
                 vol=float(m.get("volume_fp") or m.get("volume") or 0), start=P.ts(m["open_time"]), end=P.ts(m["close_time"]))
            for m, h in ms if m.get("result") in ("yes", "no")]


def kx_one(c):
    try:
        s = P.kx_hist(c)
    except Exception:
        s = pd.Series(dtype=float)
    return {**c, **{f"p{h}": at(s, c["end"] - pd.Timedelta(days=h)) if c["end"] - pd.Timedelta(days=h) >= c["start"]
                    else np.nan for h in H}}


def build_kalshi():
    if os.path.exists(KXC) and not REFRESH:
        return pd.read_pickle(KXC)
    cs = []
    for s in KX_SERIES:
        try:
            evs = P.kx_events(s)
        except Exception:
            continue
        with ThreadPoolExecutor(8) as ex:
            cs += [c for lst in ex.map(lambda e: kx_event_markets(s, e), evs) for c in lst]
    with ThreadPoolExecutor(8) as ex:
        df = pd.DataFrame(list(ex.map(kx_one, cs)))
    df.to_pickle(KXC)
    return df


# ---------------- Anthropic IPO day (2026-11-19) ----------------
IPO_EVENTS = ["anthropic-ipo-closing-price-above-ipo-price-on-first-day", "anthropic-ipo-open-price-above-ipo-price",
              "anthropic-ipo-first-day-pop-above", "anthropic-closing-share-price-on-ipo-day",
              "anthropic-opening-share-price-on-ipo-day", "how-much-will-anthropics-stock-move-on-ipo-day",
              "anthropic-ipo-closing-market-cap-above", "anthropic-ipo-closing-market-cap-higher-strikes",
              "anthropic-ipo-closing-market-cap-979", "anthropic-ipo-closing-market-cap-119"]
PRE = pd.Timestamp("2026-11-19 14:00", tz="UTC")  # 09:00 New York, before the cash open (IPO opens later still)
EVE = pd.Timestamp("2026-11-18 21:00", tz="UTC")  # 16:00 New York the day before


def build_ipo():
    if os.path.exists(IPO) and not REFRESH:
        return pd.read_pickle(IPO)
    rows = []
    for slug in IPO_EVENTS:
        try:
            e = get(f"{GAMMA}/events/slug/{slug}")
        except Exception:
            continue
        for m in e.get("markets", []):
            px = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            if len(px) != 2 or max(px) < 0.99 or not m.get("clobTokenIds") or "not ipo" in m["question"].lower():
                continue
            s = window(json.loads(m["clobTokenIds"])[0], PRE - pd.Timedelta(days=3), PRE + pd.Timedelta(hours=1))
            rows.append(dict(event=slug, q=m["question"], item=m.get("groupItemTitle") or "", y=int(px[0] > 0.99),
                             vol=float(m.get("volumeNum") or 0), eve=at(s, EVE), pre=at(s, PRE)))
    df = pd.DataFrame(rows)
    df.to_pickle(IPO)
    return df


# ---------------- stats ----------------
def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p, d = k / n, 1 + z * z / n
    c, w = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - w, c + w)


def brier(p, y):
    return float(np.mean((p - y) ** 2))


def logloss(p, y):
    p = np.clip(p, 0.005, 0.995)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def calib_table(p, y):
    b = np.minimum((p * 10).astype(int), 9)
    rows = []
    for i in range(10):
        k, n = int(y[b == i].sum()), int((b == i).sum())
        lo, hi = wilson(k, n)
        rows.append(f"| {i/10:.1f}–{(i+1)/10:.1f} | {n} | {p[b == i].mean() if n else np.nan:.3f} | "
                    f"{k/n if n else np.nan:.3f} | [{lo:.3f}, {hi:.3f}] |")
    return "| bin | n | mean price | YES freq | 95% CI |\n|---|---|---|---|---|\n" + "\n".join(rows)


def ece(p, y):
    b = np.minimum((p * 10).astype(int), 9)
    return float(sum(abs(p[b == i].mean() - y[b == i].mean()) * (b == i).sum() for i in range(10) if (b == i).any()) / len(p))


def scores(df, col, base_by=None):
    d = df.dropna(subset=[col])
    p, y = d[col].to_numpy(), d["y"].to_numpy()
    base = d.groupby(base_by)["y"].transform("mean").to_numpy() if base_by else np.full(len(y), y.mean())
    bm, b5, bb = brier(p, y), brier(np.full(len(y), .5), y), brier(base, y)
    return dict(n=len(d), events=d["event_id"].nunique() if "event_id" in d else d["event"].nunique(), yes=y.mean(),
                brier=bm, b50=b5, bbase=bb, bss=1 - bm / bb, ll=logloss(p, y), ll50=math.log(2), llbase=logloss(base, y),
                ece=ece(p, y), acc=float(((p > .5) == (y == 1))[p != .5].mean()))


def fold(df, col):
    """Cheap side of each market: q = min(p, 1-p), win = cheap side paid out."""
    d = df.dropna(subset=[col])
    q = np.minimum(d[col], 1 - d[col])
    win = np.where(d[col] <= .5, d["y"], 1 - d["y"])
    ev = d["event_id"] if "event_id" in d else d["event"]
    return pd.DataFrame(dict(q=q.to_numpy(), win=win, ev=ev.to_numpy()))[lambda x: x.q > 0.0005]


LS_BINS = [(0, .02), (.02, .05), (.05, .10), (.10, .20), (.20, .35), (.35, .501)]


def longshot_table(df, col):
    f = fold(df, col)
    out = ["| cheap-side price | n | mean price | won | 95% CI | won / priced |", "|---|---|---|---|---|---|"]
    for a, b in LS_BINS:
        g = f[(f.q >= a) & (f.q < b)]
        if len(g):
            lo, hi = wilson(int(g.win.sum()), len(g))
            out.append(f"| {a:.2f}–{min(b, .5):.2f} | {len(g)} | {g.q.mean():.3f} | {g.win.mean():.3f} | "
                       f"[{lo:.3f}, {hi:.3f}] | {g.win.mean() / g.q.mean():.2f} |")
    return "\n".join(out)


def edge(df, col, h, lo=.005, hi=.10, costs=(0, .005, .01, .02)):
    """Sell the longshot = buy the favourite at (1-q)+c, hold to resolution. Returns per $ staked; t-stat clusters by event."""
    f = fold(df, col)
    f = f[(f.q >= lo) & (f.q < hi)]
    if not len(f):
        return []
    rows = []
    for c in costs:
        for side, price, payoff in (("sell longshot (buy fav)", 1 - f.q + c, 1 - f.win), ("buy longshot", f.q + c, f.win)):
            r = (payoff - price) / price
            e = r.groupby(f.ev).mean()
            t = e.mean() / (e.std(ddof=1) / math.sqrt(len(e))) if len(e) > 2 else np.nan
            rows.append(f"| {h}d | {side} | {c*100:.1f}¢ | {len(f)} | {len(e)} | {r.mean()*100:+.2f}% | {t:+.2f} | "
                        f"{r.min()*100:.0f}% |")
    return rows


def score_line(name, s):
    return (f"| {name} | {s['n']} | {s['events']} | {s['yes']:.2f} | {s['brier']:.4f} | {s['b50']:.4f} | {s['bbase']:.4f} | "
            f"{s['bss']:+.2f} | {s['ll']:.3f} | {s['llbase']:.3f} | {s['ece']:.3f} | {s['acc']:.2f} |")


SC_HDR = ("| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | "
          "log loss base | ECE | hit rate |\n|---|---|---|---|---|---|---|---|---|---|---|---|")


LIT = """## Literature (brief)
- Wolfers & Zitzewitz (2004), "Prediction Markets", *J. Econ. Perspectives* 18(2): prices are good aggregate forecasts,
  usually at least as good as polls/experts; flags thin markets, longshot bias and manipulation attempts as limits.
- Berg, Nelson & Rietz (2008), "Prediction market accuracy in the long run", *Int. J. Forecasting* 24: Iowa Electronic
  Markets beat 964 polls 74% of the time across 1988–2004 US elections, more so far from election day.
- Snowberg & Wolfers (2010), *J. Political Economy* 118(4): the favourite–longshot bias in racetrack betting is driven by
  probability misperception (longshots overbet). Page & Clemen (2013), *Economic Journal* 123: Intrade-era prediction
  markets well calibrated near expiry, but a longshot bias appears for events far in the future (cost of locked capital).
- Rothschild & Sethi (2016), *J. Prediction Markets*: one Intrade trader spent ~$4M propping Romney in 2012; prices moved
  but reverted — manipulation is possible short-term and costly. Failures: markets favoured Remain (Brexit) and Clinton
  in 2016, roughly like polls.
- 2024 US election: Polymarket had Trump ~60%+ for weeks while poll averages were ~50/50; the outcome favoured the market,
  but a few whales (one ~$30M+ French trader) moved the headline price, so one election is weak evidence either way.
- Diercks, Katz & Wright (2026), "Kalshi and the Rise of Macro Markets", FEDS 2026-010 (Federal Reserve Board): Kalshi
  FOMC-decision markets had a perfect record the day before meetings and matched/beat fed funds futures on rate paths;
  CPI markets compared well with consensus surveys. (Our Kalshi KXFED/KXFEDDECISION skill of 0.95–0.99 at 1–7d agrees.)
- Resolution/integrity: Polymarket's March 2025 Ukraine minerals-deal market resolved YES via a UMA vote despite no
  signed deal (large UMA holder suspected); a Columbia SSRN paper (Nov 2025, "Network-Based Detection of Wash Trading")
  estimates ~25% of 2022–25 Polymarket volume was likely wash trading (~45% in sports at peaks) — volume ≠ liquidity.
- Recent Polymarket calibration replications (theses/preprints/GitHub, not peer reviewed) mostly find good calibration
  with a mild longshot overpricing that grows with horizon — consistent with the tables above."""


def main():
    pool = build_pool()
    sm = build_sample(pool)
    kx = build_kalshi()
    ipo = build_ipo()
    L = ["# Is Polymarket any good at predictions? Calibration on resolved markets",
         f"Generated {dt.date.today()} by `pm_calibration.py`. Pool: {len(pool):,} resolved binary Polymarket markets "
         f"(endDate 2023-01..2026-11, volume ≥ $500, pseudo-random 300/week). Stratified sample: {len(sm):,} markets "
         f"(≤{PER_CELL} per category × volume tercile). Price = last hourly CLOB point ≤ T−h, T = min(endDate, closedTime).",
         "", "Pool category mix (before stratification): " +
         ", ".join(f"{k} {v:.0%}" for k, v in pool["cat"].value_counts(normalize=True).items()), ""]
    for h in H:
        col = f"p{h}"
        d = sm.dropna(subset=[col])
        L += [f"## Horizon {h} day{'s' if h > 1 else ''} before resolution (n = {len(d):,})", "",
              calib_table(d[col].to_numpy(), d["y"].to_numpy()), "", SC_HDR,
              score_line("all (base = pooled YES rate)", scores(sm, col)),
              score_line("all (base = category YES rate)", scores(sm, col, "cat"))]
        for c in sorted(sm["cat"].unique()):
            if sm.loc[sm.cat == c, col].notna().sum() >= 30:
                L.append(score_line(c, scores(sm[sm.cat == c], col)))
        for v in range(3):
            if sm.loc[sm.vt == v, col].notna().sum() >= 30:
                L.append(score_line(f"volume tercile {v+1} (within category)", scores(sm[sm.vt == v], col)))
        L.append(f"\nShare of prices already ≤3¢ or ≥97¢ at this horizon: "
                 f"{((d[col] <= .03) | (d[col] >= .97)).mean():.0%}\n")
        L += ["Favourite–longshot (both sides folded: cheap side of every market)", "", longshot_table(sm, col), ""]
    L += ["## Is there a tradable edge? (hold to resolution, returns per $ staked)", "",
          "Rule: whenever the cheap side is priced 0.5–10¢ at the horizon, buy the favourite (= sell the longshot), or the "
          "reverse. Cost = half-spread + taker fee per share. t clusters by event (correlated legs of one event count once).",
          "", "| horizon | rule | cost | trades | events | mean return | t (event-clustered) | worst trade |",
          "|---|---|---|---|---|---|---|---|"]
    for h in H:
        L += edge(sm, f"p{h}", h)
    # Kalshi
    L += ["", "## Kalshi macro markets (Fed, CPI, GDP, payrolls, unemployment)", ""]
    if len(kx):
        kx["event_id"] = kx["event"]
        L += [f"{len(kx):,} settled strike markets, {kx['event'].nunique()} events; series: "
              + ", ".join(f"{s} {n}" for s, n in kx["series"].value_counts().items()), ""]
        for h in H:
            col = f"p{h}"
            d = kx.dropna(subset=[col])
            if len(d) < 30:
                continue
            L += [f"### Kalshi {h}d (n = {len(d):,})", "", calib_table(d[col].to_numpy(), d["y"].to_numpy()), "", SC_HDR,
                  score_line("all Kalshi macro", scores(kx, col))]
            for s in sorted(kx["series"].unique()):
                if kx.loc[kx.series == s, col].notna().sum() >= 30:
                    L.append(score_line(s, scores(kx[kx.series == s], col)))
            L += ["", longshot_table(kx, col), ""]
        L += ["Kalshi edge test (fee ≈ 0.07·p·(1−p) per contract ≈ 0.35–0.65¢ at 5–10¢, plus half-spread):", "",
              "| horizon | rule | cost | trades | events | mean return | t (event-clustered) | worst trade |",
              "|---|---|---|---|---|---|---|---|"]
        for h in H:
            L += edge(kx, f"p{h}", h, costs=(0, .01, .02))
    # IPO
    if len(ipo):
        L += ["", "## Worked example: Anthropic IPO day, 2026-11-19", "",
              f"Prices: day before at 16:00 NY ({EVE:%Y-%m-%d %H:%M} UTC) and pre-open 09:00 NY ({PRE:%H:%M} UTC). "
              "Outcome = how the market resolved that evening.", "",
              "| event | bucket / question | vol $ | p (eve) | p (pre-open) | outcome |", "|---|---|---|---|---|---|"]
        for r in ipo.sort_values(["event", "item"]).itertuples():
            L.append(f"| {r.event} | {r.item or r.q} | {r.vol:,.0f} | {r.eve:.3f} | {r.pre:.3f} | {'YES' if r.y else 'no'} |")
        d = ipo.dropna(subset=["pre"])
        if len(d):
            p, y = d["pre"].to_numpy(), d["y"].to_numpy()
            win = d[d.y == 1]
            L += ["", f"Pre-open Brier over {len(d)} contracts: {brier(p, y):.3f} (50%: 0.250). "
                  f"Mean pre-open price of the {len(win)} buckets that won: {win['pre'].mean():.2f}."]
    L += ["", LIT, "", "## Caveats",
          "- T = min(endDate, closedTime). Markets that resolve early (\"by date X\" that happen, awards announced) are timed "
          "from the resolution stamp, which lags the news by hours to days (UMA liveness) — so the 1-day horizon partly "
          "scores prices set after the outcome was public. The 'share already ≤3¢/≥97¢' line shows how much.",
          "- Only markets still listed by gamma with a 1/0 settlement; voided/50-50 and disputed-then-reversed markets are "
          "excluded, and delisted markets are invisible (survivorship).",
          "- CLOB history price is the hourly point Polymarket serves (mid/last), not an executable quote; thin markets "
          "can show stale or one-sided prices. Spreads on 1–5¢ longshots are often ≥1¢, i.e. 20–100% of the price.",
          "- Stratified sample: pooled numbers overweight small categories relative to Polymarket's actual mix (which is "
          "dominated by crypto up/down and sports). Category regexes are approximate.",
          "- Many markets in one event are mechanically correlated (e.g. 20 'Will X win the Open?' legs); t-stats cluster by "
          "event but CIs in calibration tables do not."]
    os.makedirs("reports", exist_ok=True)
    with open("reports/pm_calibration.md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    assert abs(wilson(5, 10)[0] - 0.2366) < 1e-3 and brier(np.array([1.]), np.array([1])) == 0
    t = pd.DataFrame(dict(p1=[.04, .96, .5], y=[0, 0, 1], event="e"))  # folded: cheap sides .04 (lost), .04 (won), .5
    assert list(fold(t, "p1").win) == [0, 1, 1]
    main()
