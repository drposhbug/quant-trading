"""Do prediction-market odds changes PREDICT next-day / next-week stock returns? Writes reports/pm_results.md.
Run: python pm_study.py [--refresh]      (history cached in data/pm_hist.pkl; data/ is gitignored)

Data (free, no key): Kalshi /historical + live candlesticks (hourly), Polymarket gamma (discovery) + CLOB prices-history
(hourly, fetched in 14-day startTs/endTs windows because interval=max at hourly fidelity only covers ~30 days).

Timing: odds are read at the US cash close of day t (16:00 New York, 13:00 on half days) from the last hourly point at or
before it. Δp_t = p(close t) - p(close t-1) on ONE contract (never across a rollover). Predictive targets: return close
t -> close t+1, and close t -> close t+5 on non-overlapping 5-day blocks with Δp over the prior 5 days. Contemporaneous
(close t-1 -> close t on the same Δp_t) is reported separately to show co-movement vs prediction.
"""
import datetime as dt
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests

from correlations import holm, pval
from model import BENCH, UNIVERSE, load_prices

UA = {"User-Agent": "quant-research"}
GAMMA, CLOB = "https://gamma-api.polymarket.com", "https://clob.polymarket.com"
KX = "https://api.elections.kalshi.com/trade-api/v2"
CACHE = "data/pm_hist.pkl"  # written by this script only, so read_pickle is safe
NAMES = [c for c in UNIVERSE if c != "ANT"] + [BENCH]  # ANT has no prices
UTC = dt.timezone.utc


def get(url, **params):
    for i in range(7):
        r = requests.get(url, params=params, headers=UA, timeout=60)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(2 ** i, 30))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def ts(s):
    return pd.Timestamp(s).tz_convert("UTC") if pd.Timestamp(s).tzinfo else pd.Timestamp(s, tz="UTC")


# ---------------- Polymarket ----------------
def pm_events(queries, slug_re):
    slugs = set()
    for q in queries:
        d = get(f"{GAMMA}/public-search", q=q, limit_per_type=100, events_status="all", keep_closed_markets=1)
        slugs |= {e["slug"] for e in d.get("events", []) if re.search(slug_re, e["slug"])}
    return [get(f"{GAMMA}/events/slug/{s}") for s in sorted(slugs)]


def pm_contracts(events, pick=lambda m: True):
    out = []
    for e in events:
        for m in e.get("markets", []):
            if not m.get("clobTokenIds") or not pick(m):
                continue
            end = min(ts(x) for x in (m.get("endDate"), m.get("closedTime")) if x)
            start = ts(m.get("startDate") or m.get("createdAt") or e["startDate"])
            out.append(dict(id=m["slug"], src="polymarket", token=json.loads(m["clobTokenIds"])[0], start=start, end=end))
    return out


def pm_hist(c):
    a, b = int(c["start"].timestamp()), int(min(c["end"], pd.Timestamp.now(tz="UTC")).timestamp())
    pts = []
    for s in range(a, b, 14 * 86400):
        pts += get(f"{CLOB}/prices-history", market=c["token"], startTs=s, endTs=min(s + 14 * 86400, b),
                   fidelity=60).get("history", [])
    s = pd.Series({pd.Timestamp(p["t"], unit="s", tz="UTC"): float(p["p"]) for p in pts}, dtype=float)
    return s[~s.index.duplicated()].sort_index()


# ---------------- Kalshi ----------------
def kx_events(series):
    evs, cur = [], None
    for st in ("settled", "closed", "open"):
        while True:
            d = get(f"{KX}/events", series_ticker=series, status=st, limit=200, **({"cursor": cur} if cur else {}))
            evs += [e["event_ticker"] for e in d.get("events", [])]
            cur = d.get("cursor")
            if not cur:
                break
    return sorted(set(evs))


def kx_markets(series, event):
    hist = get(f"{KX}/historical/markets", event_ticker=event).get("markets", [])
    ms = [(m, True) for m in hist] or [(m, False) for m in get(f"{KX}/markets", event_ticker=event).get("markets", [])]
    return [dict(id=m["ticker"], src="kalshi", series=series, hist=h, sub=m.get("yes_sub_title") or "",
                 vol=float(m.get("volume_fp") or m.get("volume") or 0),
                 start=ts(m["open_time"]), end=ts(m["close_time"])) for m, h in ms]


def kx_hist(c):
    path = (f"/historical/markets/{c['id']}/candlesticks" if c["hist"]
            else f"/series/{c['series']}/markets/{c['id']}/candlesticks")
    a, b = int(c["start"].timestamp()), int(min(c["end"], pd.Timestamp.now(tz="UTC")).timestamp())
    rows = {}
    for s in range(a, b, 150 * 86400):  # ponytail: sparse candles (hours with activity); assumes < 5000 per 150d window
        for k in get(KX + path, start_ts=s, end_ts=min(s + 150 * 86400, b), period_interval=60).get("candlesticks", []):
            f = lambda d, x: float((k.get(d) or {}).get(x) or (k.get(d) or {}).get(x + "_dollars") or "nan")  # live API: *_dollars
            bid, ask, last = f("yes_bid", "close"), f("yes_ask", "close"), f("price", "close")
            last = last if last == last else f("price", "previous")
            if bid > 1 or ask > 1:  # older payloads in cents
                bid, ask, last = bid / 100, ask / 100, last / 100
            mid = (bid + ask) / 2 if 0 < bid <= ask < 1 else np.nan
            rows[pd.Timestamp(k["end_period_ts"], unit="s", tz="UTC")] = mid if mid == mid else last
    return pd.Series(rows, dtype=float).sort_index().ffill()


# ---------------- building series ----------------
def fetch_all(contracts):
    cache = pd.read_pickle(CACHE) if os.path.exists(CACHE) and "--refresh" not in sys.argv else {}
    todo = [c for c in contracts if c["id"] not in cache]
    os.makedirs("data", exist_ok=True)
    try:
        with ThreadPoolExecutor(3) as ex:  # Kalshi rate-limits at ~10 req/s
            for c, s in zip(todo, ex.map(lambda c: (pm_hist if c["src"] == "polymarket" else kx_hist)(c), todo)):
                cache[c["id"]] = s
    finally:
        pd.to_pickle(cache, CACHE)  # keep partial progress
    return cache


def close_times(days):
    """16:00 New York on each trading day; 13:00 on NYSE half days (Jul 3, day after Thanksgiving, Dec 24)."""
    out = []
    for d in days:
        thanksgiving_fri = d.month == 11 and d.weekday() == 4 and 22 <= d.day - 1 <= 28
        half = thanksgiving_fri or (d.month, d.day) in ((7, 3), (12, 24))
        out.append(pd.Timestamp(dt.datetime(d.year, d.month, d.day, 13 if half else 16)).tz_localize("America/New_York"))
    return pd.DatetimeIndex(out).tz_convert("UTC")


def chain(contracts, hist, closes, days):
    """For each day t pick the live contract with the earliest sel_end after close t that has prices at t and t-1.
    Returns level, Δ1 (t-1 -> t) and Δ5 (t-5 -> t), each measured on that single contract, plus the chosen id."""
    A = {}
    for c in contracts:
        s = hist.get(c["id"])
        if s is None or s.dropna().empty:
            continue
        s = s.dropna()
        v = pd.Series(s.reindex(s.index.union(closes)).ffill().reindex(closes).values, index=days)
        ok = (closes >= s.index[0]) & (closes <= c["end"])
        A[c["id"]] = v.where(ok)
    A = pd.DataFrame(A)
    sel_end = pd.Series({c["id"]: c.get("sel_end", c["end"]) for c in contracts}).reindex(A.columns)
    out = pd.DataFrame(index=days, columns=["level", "d1", "d5", "id"], dtype=object)
    for i in range(1, len(days)):
        cand = [k for k in A.columns if sel_end[k] > closes[i] and A[k].iat[i] == A[k].iat[i] and A[k].iat[i - 1] == A[k].iat[i - 1]]
        if not cand:
            continue
        k = min(cand, key=lambda k: sel_end[k])
        out.iloc[i] = [A[k].iat[i], A[k].iat[i] - A[k].iat[i - 1], A[k].iat[i] - A[k].iat[i - 5] if i >= 5 else np.nan, k]
    return out.astype({"level": float, "d1": float, "d5": float})


def build(days, closes):
    """Each theme: (contracts, tickers, story). Rollover rules are documented in the report (RULES)."""
    themes = {}

    # Fed: Kalshi FEDDECISION / KXFEDDECISION, one event per FOMC meeting. Contract value = sum of 'Cut ...' markets.
    fed = []
    for ev in kx_events("KXFEDDECISION"):
        ms = kx_markets("KXFEDDECISION", ev)
        cuts = [m for m in ms if m["sub"].lower().startswith("cut")]
        if cuts:
            fed.append(dict(id=ev, legs=cuts, end=min(m["end"] for m in ms), main=max(cuts, key=lambda m: m["vol"])["id"]))
    themes["FED_CUT"] = (fed, NAMES, "P(cut at next FOMC), Kalshi")

    # Recession: Kalshi RECSSNBER-yy, one per calendar year. Selected only during its own calendar year.
    rec = []
    for ev in kx_events("KXRECSSNBER"):
        y = 2000 + int(ev[-2:])
        for m in kx_markets("KXRECSSNBER", ev):
            rec.append(m | dict(sel_end=pd.Timestamp(f"{y + 1}-01-01", tz="UTC")))
    themes["RECESSION"] = (rec, NAMES, "P(US recession in current calendar year), Kalshi")

    # Shutdown: Kalshi GOVSHUT-<date> 'shut down on <date>?' markets; nearest deadline.
    shut = [m for ev in kx_events("KXGOVSHUT") for m in kx_markets("KXGOVSHUT", ev)]
    themes["SHUTDOWN"] = (shut, NAMES, "P(gov shut down on next funding deadline), Kalshi")

    # China de-escalation: Polymarket 'Trump lowers tariffs on China by D' / 'US-China tariff agreement by D'.
    china = pm_contracts(pm_events(["lower tariffs on china", "china tariff agreement"],
                                   r"^(will-trump-lower-tariffs-on-china-(in-april|by)|us-(x-)?china-tariff-agreement)"))
    themes["CHINA_DEAL"] = (china, NAMES, "P(US-China tariff cut/agreement by nearest deadline), Polymarket")

    # AI race: Polymarket 'Which company has best AI model end of <month>' -> Google leg.
    ai = pm_contracts(pm_events(["best AI model end of", "best ai model on"], r"^which-company-has-(the-)?best-ai-model-"),
                      lambda m: re.search(r"google", (m.get("groupItemTitle") or m["question"]), re.I))
    themes["AI_GOOGLE_BEST"] = (ai, ["GOOGL", BENCH], "P(Google has best AI model at month end), Polymarket")

    # NVIDIA largest company at month end (resolves on market cap, so expect it to lag the stock, not lead it).
    lg = pm_contracts(pm_events(["largest company end of", "largest company eoy"], r"^largest-company-(end|eoy)"),
                      lambda m: re.search(r"nvidia", (m.get("groupItemTitle") or m["question"]), re.I))
    themes["NVDA_LARGEST"] = (lg, ["NVDA", BENCH], "P(NVIDIA largest company at month end), Polymarket")

    # Tesla: SpaceX merger announced by D; driverless robotaxi service launched by D.
    tm = pm_contracts(pm_events(["tesla spacex merger"], r"^tesla-and-spacex-merger"))
    themes["TSLA_SPACEX_MERGER"] = (tm, ["TSLA", "SPCX", BENCH], "P(Tesla-SpaceX merger announced by nearest deadline), Polymarket")
    rt = pm_contracts(pm_events(["tesla driverless robotaxi"], r"^will-tesla-launch-a-driverless-rob.?taxi-service"))
    themes["TSLA_ROBOTAXI"] = (rt, ["TSLA", BENCH], "P(Tesla driverless robotaxi launch by nearest deadline), Polymarket")

    flat = [m for f in fed for m in f["legs"]] + [c for k, (cs, _, _) in themes.items() if k != "FED_CUT" for c in cs]
    hist = fetch_all(flat)
    for f in fed:  # sum cut legs; start when the most-traded cut leg has its first print (thin tail legs default to 0)
        legs = pd.DataFrame({m["id"]: hist.get(m["id"]) for m in f["legs"]}).sort_index().ffill()
        first = hist[f["main"]].dropna().index[0] if f["main"] in hist and hist[f["main"]].notna().any() else None
        hist[f["id"]] = legs.fillna(0).sum(axis=1).loc[first:] if first is not None else pd.Series(dtype=float)
    return {k: (chain(cs, hist, closes, days), tk, story, len(cs)) for k, (cs, tk, story) in themes.items()}


# ---------------- tests ----------------
def ols_hac(y, x, lags):
    """OLS y = a + b x, Newey-West SE. Returns b, t(b)."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ beta
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for l in range(1, lags + 1):
        G = Xu[l:].T @ Xu[:-l]
        S += (1 - l / (lags + 1)) * (G + G.T)
    XtX_inv = np.linalg.inv(X.T @ X)
    return beta[1], beta[1] / np.sqrt((XtX_inv @ S @ XtX_inv)[1, 1])


def run_test(x, y, lags):
    d = pd.concat([x, y], axis=1, keys=["x", "y"]).dropna()
    d = d[d.x.abs() > 0] if (d.x != 0).sum() < 30 else d
    n = len(d)
    if n < 30 or d.x.std() == 0:
        return dict(n=n)
    b, t = ols_hac(d.y.values, d.x.values, lags)
    h = n // 2
    b1 = ols_hac(d.y.values[:h], d.x.values[:h], lags)[0]
    b2 = ols_hac(d.y.values[h:], d.x.values[h:], lags)[0]
    trim = d.drop(d.x.abs().nlargest(5).index)  # robustness only (not in the pass rule): is it a handful of days?
    t_trim = ols_hac(trim.y.values, trim.x.values, lags)[1] if trim.x.std() > 0 else np.nan
    return dict(n=n, start=d.index[0].date(), end=d.index[-1].date(), beta_bp_per_10pp=b * 1e4 * 0.10,
                corr=d.x.corr(d.y), t=t, p=pval(t), b_1st=b1, b_2nd=b2, nonzero_dp=int((d.x != 0).sum()), t_ex_top5=t_trim,
                top3="; ".join(f"{i.date()} Δp {100 * d.x[i]:+.1f}pp → {100 * d.y[i]:+.1f}%" for i in d.x.abs().nlargest(3).index))


def main():
    px = load_prices(start="2021-06-01")[NAMES]
    days = px.index
    closes = close_times(days)
    r = px.pct_change(fill_method=None)
    fwd1 = r.shift(-1)
    fwd5 = (px.shift(-5) / px - 1)
    series = build(days, closes)

    rows, desc = [], []
    for name, (s, tickers, story, ncon) in series.items():
        v = s.dropna(subset=["level"])
        desc.append(dict(Series=name, Definition=story, Contracts=ncon, Used=v["id"].nunique(),
                         First=v.index.min().date() if len(v) else None, Last=v.index.max().date() if len(v) else None,
                         Days=len(v), **{"Days Δp≠0": int((s.d1.fillna(0) != 0).sum()),
                                         "mean |Δp| (pp)": 100 * s.d1.abs().mean(), "sd Δp (pp)": 100 * s.d1.std()}))
        blocks = s.index[::5]
        for tk in tickers:
            for kind, x, y, lags in (("same-day", s.d1, r[tk], 5), ("next 1d", s.d1, fwd1[tk], 5),
                                     ("next 5d (non-overlap)", s.d5.loc[blocks], fwd5[tk].loc[blocks], 2)):
                rows.append(dict(Series=name, Ticker=tk, Test=kind, **run_test(x, y, lags)))
    res = pd.DataFrame(rows)
    ran = res[res.t.notna()].copy()
    m = len(ran)
    ran["Holm p"] = holm(ran.p).values
    ran["same sign both halves"] = np.sign(ran.b_1st) == np.sign(ran.b_2nd)
    ran["Pass"] = (ran.Test != "same-day") & (ran["Holm p"] < 0.05) & ran["same sign both halves"]
    ran["Robust"] = ran.Pass & (ran.t_ex_top5.map(pval) * m < 0.05)  # still Bonferroni-significant without its 5 biggest Δp days
    z = NormalDist().inv_cdf
    ran["MDE |corr| (80% power, Holm)"] = (z(1 - 0.05 / (2 * m)) + z(0.8)) / np.sqrt(ran.n)
    ran["MDE |corr| (80%, unadjusted)"] = (z(0.975) + z(0.8)) / np.sqrt(ran.n)
    skipped = res[res.t.isna()][["Series", "Ticker", "Test", "n"]]
    write_report(pd.DataFrame(desc), ran, skipped, m, days[-1])


RULES = """\
- **FED_CUT** (Kalshi `FEDDECISION-*` / `KXFEDDECISION-*`, one event per FOMC meeting). Contract value = sum of the "Cut 25bps"
  and "Cut >25bps" legs (hourly mid of yes bid/ask; last trade when the book is one-sided; thin tail legs count as 0 until
  their first print; the series starts at the first print of the most-traded cut leg). On day t the chosen contract is the
  meeting with the earliest close time after close t, so the series always means "cut at the NEXT meeting". Kalshi closes
  each meeting's markets at ~19:00 UTC on decision day, before the 16:00 ET read, so the decision day already reads the
  following meeting.
- **RECESSION** (Kalshi `RECSSNBER-yy`, "recession in 20yy?"). Day t uses the contract for t's calendar year only
  (Jan 1 roll), even though each contract trades on until NBER/GDP data resolves it.
- **SHUTDOWN** (Kalshi `GOVSHUT-*` / `KXGOVSHUT-*`, "government shut down on <deadline>?"). Nearest deadline after close t.
  Undefined between funding fights.
- **CHINA_DEAL** (Polymarket: "Will Trump lower tariffs on China in April / by <date>", "US-China tariff agreement before
  90-day deadline / by <date>"). Nearest deadline after close t. Treated as one de-escalation series.
- **AI_GOOGLE_BEST** (Polymarket "Which company has (the) best AI model end of <month/year>", Google leg). Nearest month end.
- **NVDA_LARGEST** (Polymarket "Largest company end of <month>", NVIDIA leg). Nearest month end. Resolves on market cap,
  so it should follow NVDA, not lead it (a built-in placebo).
- **TSLA_SPACEX_MERGER**, **TSLA_ROBOTAXI** (Polymarket deadline ladders). Nearest deadline after close t.
- **Universal rule (no splicing):** Δp is always taken on ONE contract: Δ1 = p_k(close t) − p_k(close t−1) and
  Δ5 = p_k(close t) − p_k(close t−5) where k is the contract chosen on day t (Δ5 is missing if k did not trade at t−5).
  A roll never creates a jump. The contract must have a print at or before both closes and must not have closed/resolved
  (deadline = min(endDate, closedTime) on Polymarket, close_time on Kalshi). Weekend/holiday odds moves fall into the next
  trading day's Δp, which is correct: they happen before that day's close.
"""


def write_report(desc, ran, skipped, m, last):
    pred = ran[ran.Test != "same-day"]
    same = ran[ran.Test == "same-day"]
    cols = ["Series", "Ticker", "Test", "n", "start", "end", "beta_bp_per_10pp", "corr", "t", "p", "Holm p",
            "b_1st", "b_2nd", "t_ex_top5", "Pass", "MDE |corr| (80% power, Holm)"]
    passed = pred[pred.Pass]
    raw5 = pred[pred.p < 0.05]
    fmt = dict(index=False, floatfmt=".4f")
    out = [
        "# Prediction-market odds vs stock returns: lead or just co-move?\n",
        f"Generated by pm_study.py on {dt.date.today()} (prices through {last.date()}). Holm correction across all {m} tests run "
        f"({len(same)} same-day + {len(pred)} predictive). **Pass** = predictive test, Holm p < 0.05, and the slope has the "
        "same sign in both halves of that test's sample.\n",
        "## Verdict\n",
        (f"**{len(passed)} of {len(pred)} predictive tests pass the formal rule; {int(passed.Robust.sum())} survive dropping their "
         f"5 largest odds moves** (Bonferroni over all {m} tests on the trimmed t). {len(raw5)} predictive tests have an "
         f"unadjusted p < 0.05 vs {0.05 * len(pred):.1f} expected by chance.\n\n"
         + passed[cols + ["Robust"]].to_markdown(**fmt)
         + "\n\nWhat drives each pass (3 largest |Δp| observations: odds move → following return):\n\n"
         + passed[["Series", "Ticker", "Test", "top3"]].to_markdown(index=False)
         + ("\n\n**Reading:** every pass rests on a handful of days, not a steady relationship, and none survives removing "
            "its 5 biggest odds moves. Treat them as anecdotes, not a signal; none is fit to trade. Overall: no robust "
            "evidence that prediction-market odds changes lead these stocks.\n" if passed.Robust.sum() == 0 else "\n"))
        if len(passed) else
        f"**No predictive test passes.** 0 of {len(pred)} survive Holm. {len(raw5)} have an unadjusted p < 0.05, about the "
        f"{0.05 * len(pred):.1f} expected by chance alone. Prediction-market odds changes, measured at the US close, do not "
        "forecast next-day or next-week returns of QQQ or the names in this sample.\n",
        f"\nSame-day co-movement: {int((same['Holm p'] < 0.05).sum())} of {len(same)} same-day tests are Holm-significant "
        "(section 4). Odds and stocks move together on the same day far more reliably than odds move first.\n",
        "## 1. Data obtained\n",
        "Verified live on the run date: Kalshi `GET /historical/markets`, `/historical/markets/{ticker}/candlesticks` "
        "(settled before the historical cutoff) and `/series/{s}/markets/{ticker}/candlesticks` (newer) return hourly candles "
        "with no key, back to 2021 for some series. Polymarket gamma `/public-search` (with `events_status=all`, "
        "`keep_closed_markets=1`) finds closed events, and CLOB `/prices-history` returns HOURLY history for resolved markets "
        "back to 2024 when called in ≤14-day `startTs/endTs` windows with `fidelity=60` (`interval=max&fidelity=1440` gives "
        "only one point per day stamped 00:00 UTC, which is useless for a 16:00 ET read). Kalshi candles are sparse (only hours "
        "with activity) and are forward-filled.\n",
        desc.to_markdown(index=False, floatfmt=".2f"),
        "\nNot used: Polymarket Fed markets (start Aug 2024; Kalshi covers 2023 on and the two track each other); tariff-rate "
        "and per-country tariff ladders (multi-outcome, no clean single probability); earnings-beat and price-level markets "
        "(the latter are derivatives of the stock itself).\n",
        "## 2. Method\n",
        "- Odds at close t = last hourly print at or before 16:00 America/New_York (13:00 on Jul 3, Black Friday, Dec 24). "
        "Polymarket points are stamped at HH:00:02, so the read is the 15:00 ET point: up to 1 hour stale, never later than "
        "the close. Staleness can only weaken a lead, not create one.\n",
        "- Predictive: r(close t → close t+1) on Δ1_t; r(close t → close t+5) on Δ5_t, sampled every 5th trading day so "
        "windows do not overlap. Same-day: r(close t−1 → close t) on Δ1_t (co-movement, not tradable).\n",
        "- OLS with Newey-West t-stats (5 lags daily, 2 lags for 5-day blocks). Effect = return in bp per +10pp move in odds. "
        "Tests with < 30 usable observations are not run (listed in section 5). For very sparse series, if fewer than 30 "
        "days have Δp ≠ 0, only those days are used.\n",
        "- SPCX trades only since 2026-06, so its tests are short. ANT has no prices.\n",
        "- `t_ex_top5` = the same regression after dropping the 5 days with the largest |Δp| (robustness only, not part of "
        "the pass rule). `Robust` = a pass whose trimmed t is still significant at 0.05 / (number of tests).\n",
        "### Chaining / rollover rules\n", RULES,
        "## 3. Predictive results (all tests, sorted by p)\n",
        "`MDE` = smallest |corr| the test could detect with 80% power at the Holm-adjusted level. If the MDE is far above any "
        "plausible effect (daily return predictability is usually |corr| < 0.05), the test has no power, whatever its p.\n",
        pred.sort_values("p")[cols].to_markdown(**fmt),
        "\n## 4. Same-day co-movement (descriptive)\n",
        same.sort_values("p")[["Series", "Ticker", "n", "beta_bp_per_10pp", "corr", "t", "Holm p"]].to_markdown(**fmt),
        "\n## 5. Tests not run (too little data)\n",
        skipped.to_markdown(index=False) if len(skipped) else "None.",
        "\n## 6. Caveats\n",
        "- **Power is the binding constraint.** The longest series (Fed, recession) give ~800-1,100 daily observations; "
        "Polymarket thematic series give 60-470. At the Holm level the smallest detectable |corr| is ~0.15 at n = 900 and "
        "~0.36 at n = 150 (see the MDE column), far above the ~0.02-0.05 that real daily predictors usually have. A null here "
        "rules out only LARGE leads, not small ones.\n",
        "- Most daily Δp are tiny or zero outside news days (see 'Days Δp≠0'); the information is concentrated in a few days "
        "per contract, so effective sample sizes are smaller than n.\n",
        "- Deadline ladders (China deal, robotaxi, Tesla-SpaceX, shutdown) decay toward 0 as a deadline nears without the "
        "event; part of Δp is that mechanical drift, not news.\n",
        "- Tests are not independent: each series is tested against 13 highly correlated stocks, so one lucky stretch "
        "lights up many rows at once. The raw count of p < 0.05 hits overstates the evidence; Holm handles this conservatively.\n",
        "- SHUTDOWN ends 2026-01-30: later funding fights are not listed under Kalshi KXGOVSHUT. Each funding fight gives only "
        "a few informative weeks, so its 88 five-day blocks hold only a handful of independent episodes.\n",
        "- Kalshi hourly candles exist only for hours with activity; forward-filled mids can be stale for thin markets.\n",
        "- Polymarket prices-history is the CLOB's sampled price (no bid/ask); thin markets can jump on single trades.\n",
        "- Series were chosen a priori from the themes in research_notes, not by looking at results; nothing was tuned.\n",
        "- No transaction costs: the question is only whether any lead exists.\n",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/pm_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[:5]))


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:  # lookahead + HAC sanity
        days = pd.bdate_range("2025-11-24", periods=5)
        ct = close_times(days)
        assert ct[4].hour == 18 and ct[0].hour == 21, ct  # Fri after Thanksgiving 13:00 ET = 18:00 UTC; EST close 21:00
        h = pd.Series([0.1, 0.2, 0.9], index=[ct[1] - pd.Timedelta("2h"), ct[1] + pd.Timedelta("1s"), ct[2]])
        ch = chain([dict(id="a", end=ct[-1] + pd.Timedelta("1D"))], {"a": h}, ct, days)
        assert ch.level.iat[2] == 0.9 and np.isnan(ch.d1.iat[1])
        assert abs(ch.d1.iat[2] - 0.8) < 1e-12  # uses 0.1 (before close t-1), not 0.2 printed 1s after it
        rng = np.random.default_rng(0)
        x = rng.normal(size=5000)
        assert abs(ols_hac(0.3 * x + rng.normal(size=5000), x, 5)[0] - 0.3) < 0.05
        print("selfcheck ok")
    else:
        main()
