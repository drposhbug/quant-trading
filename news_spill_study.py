"""When one stock gets a shock, do the other stocks of its sector drift afterwards? Writes reports/news_spill_results.md.
Run: python news_spill_study.py

Grok's suggestion (2026-11-23, research_notes/Smarter machine 2026-11-23/7): the one news idea not yet tested here.
The owner's belief is that reactions to news "have to be a statistical pattern"; direction after a stock's own shock
and after market shocks showed nothing (0 our own numbers.md). This asks whether the news travels slowly to peers.
Written before the first run.
- Shock: a stock moves against its sector by more than 3 of its own normal daily moves (the 60 sessions before) on
  more than twice its normal volume. Up-shocks and down-shocks are both used; the sign of the shock is the bet.
- Peers: the other index members of the same sector that day (sector as in daily_calls.groups: the sector fund a
  stock has moved with most over the last 252 sessions), leaving out any peer that had a shock of its own that day.
- Outcome: the peers' average return over the next 1 and the next 5 sessions, from the next open, with the market
  and the sector taken out (daily_calls.strip), times the sign of the shock. Positive = peers follow the shocked
  stock; negative = they move the other way.
- Days are the unit: all shocks of a day are averaged first; for 5 sessions the t counts one day in five.
- Verdict: real if |t| >= 3 at either horizon (two readings), AND the same sign in the first and second half of the
  days. Anything less is "no pattern". Size is reported in hundredths of a percent a peer.
Also reported, not deciding: up-shocks and down-shocks separately, and the peer's own sensitivity (the peers that
have moved most closely with the shocked stock over the last 126 sessions against the rest).
"""
import warnings

import numpy as np
import pandas as pd

import daily_calls as d


def main():
    raw, member, uni, outside = d.panel()
    c = raw["c"].ffill(limit=21)
    keep = member.values if member is not None else np.ones(c.shape, dtype=bool)
    beta, sec = d.groups(c, outside["SPY"].ffill(), outside[d.SECTORS].ffill())
    r = c.pct_change().values
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        own = d.strip(np.where(keep, r, np.nan), beta, sec)  # today's move with market and sector taken out
        sd = pd.DataFrame(own).rolling(60).std().shift(1).values
        vn = (raw["v"] / raw["v"].rolling(60).mean().shift(1)).values
        shock = (np.abs(own / sd) > 3) & (vn > 2) & keep
        fwd = {h: d.strip(np.where(keep, d.ahead(c, raw["o"], h).values, np.nan), beta, sec) for h in (1, 5)}
        lr = pd.DataFrame(own)
        rows = []
        for t in np.where(shock.any(1))[0]:
            if t < d.WARM or t + 6 >= len(c):
                continue
            close = None
            for i in np.where(shock[t])[0]:
                peers = np.where((sec[t] == sec[t, i]) & ~shock[t] & keep[t])[0]
                if len(peers) < 5:
                    continue
                if close is None:
                    close = lr.iloc[t - 125:t + 1].corr().values  # how closely the stocks' own moves have gone together
                near = peers[np.argsort(-np.nan_to_num(close[i, peers]))[:max(2, len(peers) // 3)]]
                s = np.sign(own[t, i])
                rows.append({"day": t, "up": s > 0, **{f"all{h}": s * np.nanmean(fwd[h][t, peers]) for h in (1, 5)},
                             **{f"near{h}": s * np.nanmean(fwd[h][t, near]) for h in (1, 5)},
                             **{f"far{h}": s * np.nanmean(fwd[h][t, np.setdiff1d(peers, near)]) for h in (1, 5)}})
    e = pd.DataFrame(rows)
    days = e.groupby("day").mean(numeric_only=True)

    def line(col, h, frame):
        g = frame[col].dropna()
        return g.mean() * 1e4, g.mean() / (g.std() / np.sqrt(len(g) / h)), len(g)

    half = days.index[len(days) // 2]
    out = ["# When one stock gets a shock, do its sector's other stocks drift?\n",
           f"Rules written in news_spill_study.py before the run. {len(e)} shocks on {len(days)} days, {c.index[int(days.index[0])].date()} to {c.index[int(days.index[-1])].date()}, "
           f"{'index members by date, dead companies included' if member is not None else 'today members only'}. Sizes are hundredths of a percent a peer, market and sector taken out, from the next open.\n",
           "| What | Next session | t | Next 5 sessions | t |", "|---|---|---|---|---|"]
    verdict = []
    for name, col, frame in (("All peers", "all", days), ("All peers, first half of the days", "all", days[days.index < half]), ("All peers, second half", "all", days[days.index >= half]),
                             ("After up-shocks", "all", e[e["up"]].groupby("day").mean(numeric_only=True)), ("After down-shocks", "all", e[~e["up"]].groupby("day").mean(numeric_only=True)),
                             ("Peers closest to the shocked stock", "near", days), ("The other peers", "far", days)):
        (m1, t1, n1), (m5, t5, _) = line(col + "1", 1, frame), line(col + "5", 5, frame)
        out.append(f"| {name} ({n1} days) | {m1:+.1f} | {t1:+.1f} | {m5:+.1f} | {t5:+.1f} |")
        if name.startswith("All peers"):
            verdict.append((m1, t1, m5, t5))
    (m1, t1, m5, t5), a, b = verdict
    real = [h for h, t_, x, y in ((1, t1, a[0], b[0]), (5, t5, a[2], b[2])) if abs(t_) >= 3 and x * y > 0]
    out.append(f"\n- Verdict: {'**a real pattern at ' + ' and '.join(str(h) for h in real) + ' session(s)**' if real else '**no pattern**: the peers do not follow or oppose the shocked stock reliably'} "
               "(bar: |t| of 3 or more and the same sign in both halves).")
    with open("reports/news_spill_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
