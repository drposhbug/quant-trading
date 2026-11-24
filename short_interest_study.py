"""Do heavily shorted stocks do worse? Writes reports/short_interest_results.md.
Run: python short_interest_study.py

One of the few non-price facts that exists for every large company: how many shares are sold short, twice a month
(short_interest_data.py, lab/short_interest.csv, FINRA, from 2017-12-29). Ranked second by Grok for a real effect
here (0.28); the evidence review rated short interest in large companies as weak. Written before the first run.
- Stocks: today's S&P 500 members (the file covers only these), on the days they were in the index.
- Timing: a figure is used only from the day FINRA published it (7 trading days after it was measured), and then one
  further full session is skipped: the ranking known at a day's close earns the return from the next close to the
  one after. Nothing here can be traded on hindsight. A figure older than 15 sessions is dropped.
- The measure (chosen in advance, one): days to cover = shares short / average daily volume, as FINRA reports it.
  Share counts are not needed, and the published work on this measure (Hong and others, 2016) is the strongest.
  Each day it is scaled across the stocks and has market beta and sector taken out (daily_calls.strip), because
  whole sectors differ in how much they are shorted.
- The bet: the least-shorted third minus the most-shorted third, every day. Each day's difference is one observation.
- Verdict: real if the daily mean is positive with t of 3 or more and positive in both halves of the days; a hint
  if t is 2 or more and positive in both halves; otherwise no pattern. A clearly NEGATIVE result (t of -3 or lower,
  both halves) would be reported as real in the other direction.
- Reading, not verdict: the same bet on the CHANGE in shares short since the previous report (least increased
  minus most increased).
"""
import warnings

import numpy as np
import pandas as pd

import daily_calls as d
from discover_odds import z


def spread(score, ret, member):
    """Daily return of the lowest third minus the highest third by `score` (known at the close two days before)."""
    rk = score.where(member).rank(axis=1, pct=True).shift(2)
    return (ret.where(rk <= 1 / 3).mean(axis=1) - ret.where(rk > 2 / 3).mean(axis=1)).dropna()


def stats(b):
    half = len(b) // 2
    return {"days": len(b), "daily mean, bp": b.mean() * 1e4, "a year": b.mean() * 252, "t": b.mean() / (b.std() / np.sqrt(len(b))),
            "1st half, bp": b.iloc[:half].mean() * 1e4, "2nd half, bp": b.iloc[half:].mean() * 1e4, "share of days up": (b > 0).mean()}


def main():
    warnings.simplefilter("ignore")
    raw, member, uni, outside = d.panel()
    c = raw["c"].ffill(limit=21)
    m_all = member if member is not None else c.notna()
    beta, sec = d.groups(c, outside["SPY"].ffill(), outside[d.SECTORS].ffill())
    si = pd.read_csv("lab/short_interest.csv", parse_dates=["settlement_date", "published"])
    si = si[si["ticker"].isin(c.columns)].sort_values(["published", "ticker"])
    known = lambda col: si.pivot_table(index="published", columns="ticker", values=col, aggfunc="last")
    onto = lambda f: f.reindex(f.index.union(c.index)).ffill(limit=15).reindex(c.index).reindex(columns=c.columns)  # from the publication day, for 15 sessions
    dtc, chg = onto(known("days_to_cover")), onto(np.log(known("short_interest").where(lambda x: x > 0)).diff())
    clean = lambda f: pd.DataFrame(d.strip(np.where(m_all.values, z(f).values, np.nan), beta, sec), index=c.index, columns=c.columns)
    ret = c.pct_change().where(m_all)
    rows = {"days to cover: least shorted minus most shorted (decides)": stats(spread(clean(dtc), ret, m_all)),
            "change in shares short: least increased minus most increased (reading)": stats(spread(clean(chg), ret, m_all))}
    t = pd.DataFrame(rows).T
    r = t.iloc[0]
    up, down = r["1st half, bp"] > 0 and r["2nd half, bp"] > 0, r["1st half, bp"] < 0 and r["2nd half, bp"] < 0
    verdict = ("real" if r["t"] >= 3 and up else "a hint" if r["t"] >= 2 and up else "real, the other way round" if r["t"] <= -3 and down else "no pattern")
    covered = int((dtc.where(m_all).notna().sum(axis=1) > 0).sum())
    out = ["# Do heavily shorted stocks do worse?\n",
           f"Rules written in short_interest_study.py before the run. {si['ticker'].nunique()} companies, figures published {si['published'].min().date()} to {si['published'].max().date()}, "
           f"{covered} trading days with a ranking; about {int(dtc.where(m_all).notna().sum(axis=1).replace(0, np.nan).median())} stocks ranked on a typical day.\n",
           t.to_markdown(floatfmt=".2f"),
           f"\n- Verdict: **{verdict}** (real needs t of 3 or more and the same sign in both halves; a hint needs 2)."]
    with open("reports/short_interest_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
