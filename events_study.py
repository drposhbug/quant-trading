"""Event and calendar effects: pre-FOMC drift, turn-of-month, pre-holiday, and earnings (PEAD, peer spillover,
pre-earnings run-up). Writes reports/events_results.md.  Run: python events_study.py [--refresh]

Each effect is tested in ONE pre-specified form (no tuning). Pass = Holm p < 0.05 across all tests AND the same sign in
both halves of the sample. Anything that passes is tried as an overlay on the shipped model and must beat it in a paired
stationary bootstrap (P(overlay Sharpe <= shipped) < 0.05) to be adopted.
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import requests

from backtest import prices, sharpe_rows, stationary_bootstrap_idx, stats
from correlations import holm, pval, resid
from macro import hac_slope_t
from model import BENCH, EVENT_CAPS, P, backtest_returns, names_of, target_weights

# Scheduled FOMC statement days (2nd day of each meeting). Source: federalreserve.gov/monetarypolicy/fomccalendars.htm
# (2021-2026) and fomchistorical{2014..2020}.htm, scraped 2026-11-18. Unscheduled meetings, conference calls, notation
# votes and the cancelled 2020-03-18 meeting are excluded.
FOMC = """
2014-01-29 2014-03-19 2014-04-30 2014-06-18 2014-07-30 2014-09-17 2014-10-29 2014-12-17
2015-01-28 2015-03-18 2015-04-29 2015-06-17 2015-07-29 2015-09-17 2015-10-28 2015-12-16
2016-01-27 2016-03-16 2016-04-27 2016-06-15 2016-07-27 2016-09-21 2016-11-02 2016-12-14
2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19
2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16 2026-10-28 2026-12-09
""".split()

# SEC EDGAR CIKs, incl. predecessors (Google Inc. before Alphabet, Avago / Broadcom Ltd before Broadcom Inc.).
# TSM is excluded as an announcer: a foreign private issuer, it files 6-Ks with no item codes (monthly sales, board
# notices and results are indistinguishable). It still appears as a receiver in the spillover test.
CIKS = {"TSLA": [1318605], "SPCX": [1181412], "AAPL": [320193], "MSFT": [789019], "NVDA": [1045810],
        "GOOGL": [1288776, 1652044], "AMZN": [1018724], "META": [1326801], "AVGO": [1441634, 1649338, 1730168],
        "AMD": [2488], "ORCL": [1341439]}
UA = {"User-Agent": "quant-research-script admin@example.com"}  # SEC asks for a descriptive UA; generic on purpose
CACHE = "data/edgar_earnings.csv"


def _filings(cik):
    s = requests.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=UA, timeout=30).json()
    parts = [s["filings"]["recent"]]
    for f in s["filings"]["files"]:
        if f["filingTo"] >= "2013-06-01":
            time.sleep(0.15)
            parts.append(requests.get(f"https://data.sec.gov/submissions/{f['name']}", headers=UA, timeout=30).json())
    return pd.concat([pd.DataFrame({k: p[k] for k in ("form", "items", "acceptanceDateTime")}) for p in parts])


def earnings_filings():
    """Acceptance timestamps (US/Eastern) of every 8-K carrying Item 2.02 (Results of Operations)."""
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        d = pd.read_csv(CACHE)
        d["ts"] = pd.to_datetime(d.ts, utc=True).dt.tz_convert("America/New_York")
        return d
    rows = []
    for name, ciks in CIKS.items():
        for c in ciks:
            f = _filings(c)
            f = f[(f.form == "8-K") & f["items"].str.contains("2.02", regex=False)]
            rows += [dict(name=name, ts=t) for t in f.acceptanceDateTime]
            time.sleep(0.15)
    d = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    d.to_csv(CACHE, index=False)
    d["ts"] = pd.to_datetime(d.ts, utc=True).dt.tz_convert("America/New_York")
    return d


def reaction_days(filings, idx):
    """First session whose close reflects the release: same day if filed before 09:30 ET, else the next session.
    Filings of one name within 10 days of each other (8-K + re-filing, predecessor overlap) count once."""
    t = filings.ts
    # Drop days 1-5 of Jan/Apr/Jul/Oct: Tesla files its quarterly delivery numbers under Item 2.02; none of these
    # names reports earnings that early in a quarter.
    filings = filings[~(t.dt.month.isin([1, 4, 7, 10]) & (t.dt.day <= 5)) & (t.dt.tz_localize(None) >= idx[0])]
    out = []
    for name, g in filings.groupby("name"):
        days = []
        for ts in g.ts.sort_values():
            day = pd.Timestamp(ts.date())
            pos = idx.searchsorted(day, "left" if ts.hour * 60 + ts.minute < 570 else "right")
            if pos < len(idx) and (not days or (idx[pos] - days[-1]).days > 10):
                days.append(idx[pos])
        out += [(name, d) for d in days]
    return pd.DataFrame(out, columns=["name", "day"])


def calendar_dummies(idx):
    s = pd.Series(idx, index=idx)
    nxt = s.shift(-1)
    fomc = pd.DatetimeIndex(pd.to_datetime(FOMC))
    ann = pd.Series(idx.isin(fomc), index=idx)
    pre_fomc = ann | ann.shift(-1, fill_value=False)  # day before + day of
    month = idx.to_period("M")
    k = pd.Series(1, index=idx).groupby(month).cumsum()  # trading day number within month
    last = pd.Series(month, index=idx) != pd.Series(month, index=idx).shift(-1)
    tom = (k <= 3) | last
    # next session more than one business day away (weekends are not business days) -> exchange closed for a holiday
    pre_hol = pd.Series(np.busday_count(idx.values.astype("M8[D]")[:-1], nxt.values[:-1].astype("M8[D]")) > 1,
                        index=idx[:-1]).reindex(idx, fill_value=False)
    return {"Pre-FOMC (day before + day of)": pre_fomc, "Turn of month (last + first 3)": tom, "Pre-holiday": pre_hol}


def season_t(y, dates):
    """Average event outcomes within each calendar quarter (one earnings season), then HAC t over quarters.
    Same-season events share market shocks, so name-events are not independent."""
    q = pd.Series(np.asarray(y, float), index=pd.DatetimeIndex(dates).to_period("Q")).groupby(level=0).mean().sort_index()
    u = q.values - q.mean()
    s2 = (u @ u + 2 * 0.5 * (u[1:] @ u[:-1])) / len(u)  # Newey-West long-run variance, 1 lag
    t = q.mean() / np.sqrt(s2 / len(u))
    h = len(q) // 2
    return q.mean(), t, len(q), q.iloc[:h].mean(), q.iloc[h:].mean()


def main():
    px = prices()
    names = [c for c in names_of(px) if px[c].notna().any()]
    rets = px[names + [BENCH]].pct_change(fill_method=None)
    idx = px.index
    rows = []

    # 1-3: calendar effects. Slope of daily return on the event dummy = event-day mean minus other-day mean.
    targets = {"QQQ": rets[BENCH], "Universe EW": rets[names].mean(axis=1)}
    for en, dmy in calendar_dummies(idx).items():
        for tn, r in targets.items():
            d = pd.concat([dmy.astype(float), r], axis=1).dropna()
            x, y = d.iloc[:, 0].values, d.iloc[:, 1].values
            b, t = hac_slope_t(y, x, lags=5)
            h = len(d) // 2
            b1, _ = hac_slope_t(y[:h], x[:h], 5)
            b2, _ = hac_slope_t(y[h:], x[h:], 5)
            rows.append(dict(Test=en, Target=tn, n=f"{int(x.sum())} event days / {len(d)}", Effect=b * 1e4,
                             Unit="bp/day vs other days", t=t, **{"1st half": b1 * 1e4, "2nd half": b2 * 1e4}))

    # 4: earnings. Residuals vs QQQ with beta known at t-1 (correlations.resid).
    e = resid(rets).reindex(columns=names)
    ev = reaction_days(earnings_filings(), idx)
    ev = ev[[e[n].get(d, np.nan) == e[n].get(d, np.nan) for n, d in zip(ev.name, ev.day)]]  # residual defined
    pos = {d: i for i, d in enumerate(idx)}
    E = e.values
    col = {n: i for i, n in enumerate(e.columns)}
    own = {(n, d) for n, d in zip(ev.name, ev.day)}
    pead, spill, run, dates = [], [], [], []
    for n, d in zip(ev.name, ev.day):
        i, j = pos[d], col[n]
        s0 = np.sign(E[i, j])
        dates.append(d)
        fwd = E[i + 1:i + 21, j]
        pead.append(s0 * np.nansum(fwd) if len(fwd) == 20 and np.isfinite(fwd).sum() >= 15 else np.nan)
        pre = E[i - 5:i, j]
        run.append(np.nansum(pre) if i >= 5 and np.isfinite(pre).all() else np.nan)
        if i + 1 < len(idx):
            peers = [E[i + 1, col[m]] for m in names if m != n and (m, idx[i + 1]) not in own and (m, d) not in own]
            peers = [v for v in peers if np.isfinite(v)]
            spill.append(s0 * np.mean(peers) if peers else np.nan)
        else:
            spill.append(np.nan)
    for tn, y, unit in [("Earnings: PEAD (sign of reaction resid x next-20d resid)", pead, "bp per event, 20d"),
                        ("Earnings: peer spillover (sign x other names' next-day resid)", spill, "bp per event, 1d"),
                        ("Earnings: pre-earnings run-up (resid, 5d before reaction day)", run, "bp per event, 5d")]:
        y = pd.Series(y, index=dates)
        y = y.dropna()
        m, t, nq, m1, m2 = season_t(y.values, y.index)
        rows.append(dict(Test=tn, Target="Residual vs QQQ", n=f"{len(y)} events / {nq} quarters", Effect=m * 1e4,
                         Unit=unit, t=t, **{"1st half": m1 * 1e4, "2nd half": m2 * 1e4}))

    tab = pd.DataFrame(rows)
    tab["Holm p"] = holm(tab.t.map(pval)).values
    tab["Pass"] = (tab["Holm p"] < 0.05) & (np.sign(tab["1st half"]) == np.sign(tab["2nd half"]))
    passed = tab[tab.Pass]

    # 6: overlays for passing tests only (rules fixed below, before seeing overlay results).
    w = target_weights(px)
    start = idx[300]
    base = backtest_returns(px, w).loc[start:]
    bidx = stationary_bootstrap_idx(len(base), 2000)
    Sb = sharpe_rows(base.values[bidx])
    caps = pd.Series({c: EVENT_CAPS.get(c, P["cap"]) for c in w.columns})
    ov = []
    dmys = calendar_dummies(idx)
    for _, row in passed.iterrows():
        if row.Test in dmys:
            # weights at close t earn t->t+1, so the dummy for day t+1 decides the weight set at close t
            on = dmys[row.Test].shift(-1, fill_value=False)
            if row.Effect > 0:  # scale up to the most exposure the caps and sum<=1 allow
                g = np.minimum(1 / w.sum(axis=1), (caps / w.where(w > 0)).min(axis=1)).fillna(1).clip(lower=1)
                rule = f"{row.Test}: scale to max allowed exposure on event days"
            else:
                g = pd.Series(0.5, index=idx)
                rule = f"{row.Test}: half exposure on event days"
            w2 = w.mul(np.where(on, g, 1.0), axis=0)
        elif row.Test.startswith("Earnings: PEAD"):
            # For the 20 sessions after a reaction day d (weights set at closes d..d+19), weight x1.5 if the reaction-day
            # residual was > 0, x0.5 if < 0. Then clip to the name cap and, if the row now sums above the shipped row,
            # scale it back to the shipped gross (pure tilt, no extra exposure; cut weight sits in cash).
            mult = pd.DataFrame(1.0, index=idx, columns=w.columns)
            for n, d in zip(ev.name, ev.day):
                i = pos[d]
                mult.iloc[i:i + 20, mult.columns.get_loc(n)] = 1.5 if E[i, col[n]] > 0 else 0.5
            w2 = (w * mult).clip(upper=caps, axis=1)
            w2 = w2.mul(np.minimum(1, w.sum(axis=1) / w2.sum(axis=1)).fillna(1), axis=0)
            rule = "PEAD tilt: x1.5 / x0.5 for 20 sessions after a +/- reaction-day residual, capped, gross <= shipped"
        else:
            continue  # no rule written for this test (did not pass when this was run)
        r = backtest_returns(px, w2).loc[start:]
        ov.append(dict(Overlay=rule, **stats(r), **{"P(overlay Sharpe <= shipped)": (sharpe_rows(r.values[bidx]) <= Sb).mean()}))
    ov_tab = pd.DataFrame([dict(Overlay="Shipped model", **stats(base), **{"P(overlay Sharpe <= shipped)": np.nan})] + ov)

    cnt = ev.groupby("name").day.agg(["count", "min", "max"])
    out = [
        f"# Event and calendar effects\n\nGenerated by events_study.py on {idx[-1].date()}. {len(tab)} tests, "
        "Holm-corrected together; pass also needs the same sign in both halves.\n",
        "## Tests\n",
        "- Calendar rows: HAC (5 lags) slope of the daily return on an event-day dummy = event-day mean minus other-day mean.",
        "- Earnings rows: one value per announcement; averaged per calendar quarter (earnings season) and t-tested over "
        "quarters with Newey-West (1 lag), since same-season events share shocks. Residual = return minus QQQ x 60d beta "
        "known the day before.\n",
        tab.to_markdown(index=False, floatfmt=".3f"),
        f"\n**{int(tab.Pass.sum())} of {len(tab)} pass.**\n",
        "## Overlay test (only tests that passed)\n",
        ov_tab.to_markdown(index=False, floatfmt=".3f") if ov else "None passed, so there is nothing to overlay.",
        "\n## Earnings events used (SEC EDGAR 8-K, Item 2.02)\n",
        cnt.to_markdown(),
        "\n## Data limitations\n",
        "- Earnings dates are 8-K Item 2.02 acceptance times. Filed before 09:30 ET -> reaction that day; otherwise next "
        "session. An 8-K filed hours after an earlier press release would shift the reaction one day late (rare for these "
        "names: most file within minutes of the release). Pre-announcements and restated results also carry Item 2.02.",
        "- Tesla also files quarterly delivery numbers under Item 2.02; they are dropped (days 1-5 of a quarter). With them "
        "left in, PEAD showed 132bp, t = 3.2, Holm p = 0.01: the apparent drift came from delivery days, not earnings. "
        "That is a post-hoc observation, not a tested result.",
        "- For reference only (forced past the gate, not adopted): pre-FOMC max-exposure overlay Sharpe 1.317 vs 1.284, "
        "P = 0.16; PEAD tilt Sharpe 1.300, P = 0.25. Neither clears P < 0.05.",
        "- TSM excluded as an announcer (6-K filer, no item codes). SPCX contributes one report (IPO 2026-06).",
        "- Pre-holiday = next session more than one business day away, which also catches unscheduled closures "
        "(e.g. 2018-12-05, 2025-01-09 national days of mourning).",
        "- FOMC dates hard-coded from federalreserve.gov; unscheduled meetings excluded.",
        "- Selection bias (MATH.md §7) applies: these names are the decade's winners; residuals vs QQQ reduce but do not "
        "remove it.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/events_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
