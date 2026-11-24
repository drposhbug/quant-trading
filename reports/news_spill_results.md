# When one stock gets a shock, do its sector's other stocks drift?

Rules written in news_spill_study.py before the run. 11093 shocks on 1994 days, 2017-08-04 to 2026-11-12, index members by date, dead companies included. Sizes are hundredths of a percent a peer, market and sector taken out, from the next open.

| What | Next session | t | Next 5 sessions | t |
|---|---|---|---|---|
| All peers (1994 days) | +0.0 | +0.0 | +0.1 | +0.1 |
| All peers, first half of the days (997 days) | +0.1 | +0.4 | +0.5 | +0.8 |
| All peers, second half (997 days) | -0.1 | -0.4 | -0.4 | -0.6 |
| After up-shocks (1568 days) | +0.2 | +0.9 | -0.0 | -0.0 |
| After down-shocks (1722 days) | -0.3 | -1.9 | -0.2 | -0.3 |
| Peers closest to the shocked stock (1994 days) | +1.1 | +1.7 | -0.1 | -0.0 |
| The other peers (1994 days) | -0.5 | -1.4 | +0.1 | +0.1 |

- Verdict: **no pattern**: the peers do not follow or oppose the shocked stock reliably (bar: |t| of 3 or more and the same sign in both halves).
