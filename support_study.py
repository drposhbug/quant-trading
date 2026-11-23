"""Does a price level that has held before hold again? The owner's "buy Tesla at $340" idea, generalised.
Writes reports/support_results.md. Run: python support_study.py

Written 2026-11-23 before the first run. Tesla at $340 suggested the idea (dips there were up a month later 9 times of 9
since Aug 2025, 9 of 28 before that), so Tesla is left out of the judged sample and shown separately.
Data: point-in-time S&P 500 members, adjusted closes 2010-2026 (universe_data). Closes only, no intraday lows.
- Bounce point: a close that is the lowest of the 10 sessions either side of it and is followed by a rise of 10% or
  more within 21 sessions. It counts as known 21 sessions later, never sooner.
- Dip: the close is 5% or more below the highest close of the previous 10 sessions; one event per stock per 10 sessions.
- k = number of known bounce points in the previous 250 sessions priced within 3% of today's close
  ("this level has held k times in the past year").
- Outcome: return over the next 21 sessions minus the equal-weight S&P 500 over the same days (capped at +/-60% so one
  bad print cannot decide it); also the plain return and the worst close in between.
Claim: dips to a level that has held twice or more (k >= 2) do better than dips with no such history (k = 0).
Bar for taking it further (a portfolio backtest next, not a live change): mean relative return for k >= 2 at least
1.0 point above k = 0, t > 3 with one observation per date, and the same sign in 2010-2018 and 2019-2026.
"""
import numpy as np
import pandas as pd

import universe_data as U

LOOK, NEAR, FWD, HALF = 250, 0.03, 21, 10


def events(c, ok):
    """c: closes (NaN where no data). ok: member the day before. -> [(t, k)] for each dip day t."""
    s = pd.Series(c)
    low = s == s.rolling(2 * HALF + 1, center=True, min_periods=2 * HALF + 1).min()
    fmax = s[::-1].rolling(FWD, min_periods=1).max()[::-1].shift(-1)  # highest close over the next FWD sessions
    bp = np.flatnonzero((low & (fmax / s - 1 >= 0.10)).values)
    bp = bp[np.diff(bp, prepend=-99) > HALF]  # equal closes side by side (a filled gap) are one bounce, not two
    dip = (s <= 0.95 * s.shift(1).rolling(10).max()).values
    out, last = [], -99
    for t in np.flatnonzero(dip & ok):
        if t - last < 10:
            continue
        known = bp[(bp <= t - FWD) & (bp >= t - LOOK)]  # a bounce is only usable once its 21 sessions have passed
        out.append((t, int((np.abs(c[known] / c[t] - 1) <= NEAR).sum())))
        last = t
    return out


def _check():
    c = np.r_[np.linspace(120, 100, 30), np.linspace(100, 125, 30), np.linspace(125, 100.5, 30), np.linspace(100.5, 120, 30)]
    ev = dict(events(c, np.ones(len(c), bool)))
    assert max(ev.values()) == 1 and ev[max(ev)] == 1, ev      # the second fall to ~100 sees the first bounce there
    assert all(k == 0 for t, k in ev.items() if t < 29 + FWD), ev  # nothing is known before the first bounce is 21 sessions old


def table(e):
    g = e.groupby(e.k.clip(upper=3))
    t = pd.DataFrame({"dips": g.size(), "days": g.date.nunique(), "up a month later": g.fwd.apply(lambda x: (x > 0).mean()),
                      "median return": g.fwd.median(), "mean vs market": g.rel.mean(), "median vs market": g.rel.median(),
                      "fell 10%+ on the way": g.worst.apply(lambda x: (x <= -0.10).mean())})
    t.index = [f"held {k} times" if k < 3 else "held 3+ times" for k in t.index]
    return t


def gap(e):
    """(k>=2 mean minus k=0 mean of the relative return, t) with one observation per date and group."""
    a, b = (e[m].groupby("date").rel.mean() for m in (e.k >= 2, e.k == 0))
    return a.mean() - b.mean(), (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))


def main():
    _check()
    px, mem = U.load_universe(build_if_missing=False)
    px = px.ffill(limit=5)
    m = mem.reindex_like(px).fillna(False).astype(bool)
    M = (1 + px.pct_change(fill_method=None).where(m).mean(axis=1).fillna(0)).cumprod().values
    rows = []
    for sym in px.columns:
        c = px[sym].values
        for t, k in events(c, m[sym].shift(1, fill_value=False).values & ~np.isnan(c)):
            if t + FWD < len(c) and not np.isnan(c[t + FWD]):
                f = c[t + FWD] / c[t] - 1
                rows.append((px.index[t], sym, k, f, np.clip(f - (M[t + FWD] / M[t] - 1), -0.6, 0.6), np.nanmin(c[t + 1:t + FWD + 1]) / c[t] - 1))
    e = pd.DataFrame(rows, columns=["date", "sym", "k", "fwd", "rel", "worst"])
    tsla, e = e[e.sym == "TSLA"], e[e.sym != "TSLA"]
    d, t = gap(e)
    halves = [gap(e[e.date < "2019-01-01"]), gap(e[e.date >= "2019-01-01"])]
    ok = d >= 0.01 and t > 3 and halves[0][0] > 0 and halves[1][0] > 0
    out = ["# Does a level that has held before hold again?\n", "Rules written in support_study.py before the run. "
           f"S&P 500 members without Tesla, {e.date.min().date()} to {e.date.max().date()}.\n", table(e).to_markdown(floatfmt=".3f"),
           f"\n- Levels that held twice or more against no history: {d:+.2%} a month, t = {t:.1f}. "
           f"2010-2018: {halves[0][0]:+.2%} (t = {halves[0][1]:.1f}); 2019-2026: {halves[1][0]:+.2%} (t = {halves[1][1]:.1f}).",
           f"- Verdict: **{'clears the bar: worth a portfolio backtest' if ok else 'does not clear the bar'}**\n",
           "## Tesla alone (the stock that suggested the idea)\n", table(tsla).to_markdown(floatfmt=".3f")]
    with open("reports/support_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
