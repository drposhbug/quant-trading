"""A big move with a company announcement behind it, against a big move with none. Writes reports/news_filing_results.md.
Run: python news_filing_study.py

Why: every test of direction after a shock has shown nothing (0 our own numbers.md, news_spill_study.py,
news_gap_study.py). The published explanation is that two opposite things are mixed together: a move caused by
real news tends to continue, and a move with no news behind it tends to turn back (Chan 2003, Savor 2012; the
news researcher's first recommendation, research_notes/Smarter machine 2026-11-23/5). Now there is a free, timed
record of real news: SEC 8-K filings (filings_data.py, lab/filings_8k.csv). Written before the first run.
- Stocks: today's S&P 500 members (the filings file covers only these), on the days they were in the index.
- Shock: the stock's move, with market and sector taken out (daily_calls.strip), is more than 3 of its own normal
  daily moves (the 60 sessions before) on more than twice its normal volume. Up and down shocks both count; every
  return below is taken in the direction of the shock, so plus means "kept going" and minus means "turned back".
- With news: the company filed an 8-K (amendments left out) that became public after the previous close and no
  later than this close. Without news: no such filing. Read separately: filings that carry item 2.02 (results)
  and filings that do not.
- Trade: in at the next open, held 5 sessions, against the average index member. A basket holds every stock whose
  shock was in the last 5 sessions; each day's basket return is one observation.
- The verdict is on ONE number: the with-news basket minus the without-news basket, day by day, over the days both
  exist. Real if its t is 3 or more in size and it has the same sign in both halves of the days; a hint if 2 or
  more with the same sign in both halves; otherwise no pattern. The published direction is plus (news continues
  more than no-news); a minus that passes would also be reported as real.
- Readings, not verdicts: each basket on its own, results against other filings, and holds of 1 and 21 sessions.
Known limits: only companies still in the index today have filings here; half-days are not treated as early closes.
"""
import warnings

import numpy as np
import pandas as pd

import daily_calls as d

HOLD = 5


def held(sgn, rf, rl, hold):
    """Daily return, in the shock's direction, of the basket of stocks whose shock was in the last `hold` sessions.
    sgn: [day x stock] +1 or -1 on the shock day, empty otherwise. In at the next open (rf: that day open to close),
    then close to close (rl), both against the average member."""
    entry = sgn.shift(1)
    pos, first = (entry.ffill(limit=hold - 1) if hold > 1 else entry), entry.notna()
    later = ~first & pos.notna()
    num = (pos * rf).where(first).sum(axis=1) + (pos * rl).where(later).sum(axis=1)
    cnt = (first & rf.notna()).sum(axis=1) + (later & rl.notna()).sum(axis=1)
    return (num / cnt)[cnt > 0]


def stats(b):
    half = len(b) // 2
    return {"days": len(b), "daily mean, bp": b.mean() * 1e4, "t": b.mean() / (b.std() / np.sqrt(len(b))),
            "1st half, bp": b.iloc[:half].mean() * 1e4, "2nd half, bp": b.iloc[half:].mean() * 1e4}


def main():
    warnings.simplefilter("ignore")
    raw, member, uni, outside = d.panel()
    c, o = raw["c"].ffill(limit=21), raw["o"]
    m_all = member if member is not None else c.notna()
    beta, sec = d.groups(c, outside["SPY"].ffill(), outside[d.SECTORS].ffill())
    own = pd.DataFrame(d.strip(np.where(m_all.values, c.pct_change().values, np.nan), beta, sec), index=c.index, columns=c.columns)
    first, later = (c / o - 1).where(m_all), c.pct_change().where(m_all)
    rf, rl = first.sub(first.mean(axis=1), axis=0), later.sub(later.mean(axis=1), axis=0)

    f = pd.read_csv("lab/filings_8k.csv")
    f = f[(f["form"] == "8-K") & f["ticker"].isin(c.columns)]
    t = pd.to_datetime(f["accepted_ny"].astype(str).str.slice(0, 19))  # New York local time
    day = t.dt.normalize()
    pos = c.index.searchsorted(day)  # the first session on or after the filing's day
    ok = pos < len(c)
    same = np.zeros(len(f), dtype=bool)
    same[ok.values if hasattr(ok, "values") else ok] = c.index[pos[ok]] == day[ok].values
    pos = pos + (same & (t.dt.hour >= 16).values)  # public after the close: it belongs to the next session's move
    tick = sorted(set(f["ticker"]))
    col = {n: i for i, n in enumerate(tick)}
    news, results = np.zeros((len(c), len(tick)), dtype=bool), np.zeros((len(c), len(tick)), dtype=bool)
    for p, tk, items in zip(pos, f["ticker"], f["items"].astype(str)):
        if p < len(c):
            news[p, col[tk]] = True
            results[p, col[tk]] |= "2.02" in items
    news, results = pd.DataFrame(news, index=c.index, columns=tick), pd.DataFrame(results, index=c.index, columns=tick)

    ow, mm = own[tick], m_all[tick]
    shock = ((ow / ow.rolling(60).std().shift(1)).abs() > 3) & (raw["v"][tick] / raw["v"][tick].rolling(60).mean().shift(1) > 2) & mm
    shock.iloc[:d.WARM] = False
    sgn = np.sign(ow).where(shock)
    groups = {"with a company announcement": news, "  of which with results (item 2.02)": results, "  of which other announcements": news & ~results,
              "with no announcement": ~news}
    week = (c.shift(-HOLD) / o.shift(-1) - 1).where(m_all)
    week = week.sub(week.mean(axis=1), axis=0)[tick]
    rows, b = {}, {}
    for name, g in groups.items():
        s = sgn.where(g)
        b[name] = held(s, rf[tick], rl[tick], HOLD)
        per = (s * week).stack().dropna()
        rows[name] = {"shocks": int(s.notna().sum().sum()), **stats(b[name]), "5 sessions, per shock": per.mean(), "kept going": (per > 0).mean()}
    table = pd.DataFrame(rows).T
    diff = (b["with a company announcement"] - b["with no announcement"]).dropna()
    ds = stats(diff)
    same_sign = ds["1st half, bp"] * ds["2nd half, bp"] > 0
    verdict = "real" if abs(ds["t"]) >= 3 and same_sign else "a hint" if abs(ds["t"]) >= 2 and same_sign else "no pattern"
    other = []
    for hold in (1, 21):
        x = (held(sgn.where(news), rf[tick], rl[tick], hold) - held(sgn.where(~news), rf[tick], rl[tick], hold)).dropna()
        other.append(f"held {hold} session{'s' if hold > 1 else ''}: {x.mean() * 1e4:+.1f} bp a day, t {x.mean() / (x.std() / np.sqrt(len(x))):+.1f}")
    out = ["# A big move with a company announcement behind it, against a big move with none\n",
           f"Rules written in news_filing_study.py before the run. {int(shock.sum().sum())} shocks in {len(tick)} companies, {c.index[d.WARM].date()} to {c.index[-1].date()}. "
           "Every return is in the direction of the shock (plus = kept going), against the average index member, in at the next open, held 5 sessions.\n",
           table.to_markdown(floatfmt=".2f"),
           f"\n- **The one number that decides:** with-announcement minus no-announcement, {ds['daily mean, bp']:+.1f} bp a day over {ds['days']} days, t {ds['t']:+.1f} "
           f"(halves {ds['1st half, bp']:+.1f} and {ds['2nd half, bp']:+.1f}). Verdict: **{verdict}**.",
           "- Readings at other holding periods (same difference): " + "; ".join(other) + "."]
    with open("reports/news_filing_results.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
