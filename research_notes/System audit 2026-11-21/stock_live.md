# Stock live path: monitor, loop, alerts, state

Audit note, 2026-11-21. Line numbers are for the working copy. The deployed `monitor.py` lacks lines 68-71, so later lines sit four lower there.

## Purpose

Once per trading day, about 30 minutes before the close, move the Alpaca paper account to the frozen model's weights and park the rest in SGOV. Send Discord alerts. Record state and equity in git so the next run knows what was done.

## Data flow

1. GitHub cron `17 12-20 * * 1-5` UTC starts a job each hour: 07:17-15:17 ET in winter, 08:17-16:17 in summer (`monitor.yml:7`). Jobs share one concurrency group: one runs, one waits, and a newer waiting job replaces an older one (`monitor.yml:16-18`).
2. `loop_monitor.py` reads Alpaca's clock and runs `monitor.py` every 5 minutes, every 2 minutes in the last 45, for at most 5 h 40 min (`loop_monitor.py:15,41-55`). After each pass it commits `state.json`, `signals/` and `options_state.json`, rebases with `-X theirs` and pushes. Failures of any step are ignored (`loop_monitor.py:18-28`).
3. Each `monitor.py` pass snapshots prediction markets and Trump posts (`monitor.py:186`), then stops if the market is closed, unless forced (`:189`). Once a day it flags earlier sessions with no completed rebalance (`:193-196`). It downloads 800 days of Yahoo adjusted closes for the 12 names and QQQ and forward-fills gaps (`:202-204`), then sends move alerts (|z| > 2.5, `:209-213`) and regime-flip alerts (`:221-224`).
4. Within 30 minutes of the close, or when forced, and if today is not yet done (`:226`): take the last row of `model.target_weights` (`:227`), send orders (`:231`), check the drawdown (`:233`), write the equity row (`:236`). The day is marked done only if no order line starts with FAILED or SKIPPED (`:240-241`).

## Decision rules and parameters

- Weights: inverse 60-day volatility, 25% cap (SPCX 5%), scaled to a 20% volatility target, halved when QQQ is below its 200-day average (`model.py:19-31,88-121`). Today's unfinished Yahoo bar stands in for the close.
- Window: Alpaca's `next_close` minus now is 30 minutes or less, so 15:30 ET, or 12:30 on half days (`monitor.py:47-53,188`).
- Cancel all open orders, then read equity and position values (`:61-63`).
- If a held name has no Yahoo data at all, skip the whole rebalance (`:64-65`).
- SGOV weight is 1 minus the stock weights (`:66`). Target dollars are weight × equity × 0.98, a 2% cash buffer (`:67`).
- No-trade band: a name is skipped if its trade is under max($50, 1% of equity) (`:75`). Uncommitted fix: the skipped stock amounts are netted out of the SGOV order (`:68-71`).
- Holdings with zero weight or outside the universe are closed in full (`:74,79`).
- Sells go first, largest first, with no wait for fills (`:73`). Orders are dollar-notional market day orders (`:83,90`). Non-fractionable names trade whole shares and are skipped below one share (`:84-89`).
- Drawdown alerts at −10% and −20% from peak, alert only, re-armed above −5% (`:127-129,159-170`). The peak starts at the first equity the code sees.
- Missed rebalance: any session in the last 10 days later than `state["rebalanced"]` (`:132-144`).
- Forced run (`FORCE=1`): skips the market-hours gate and trades at once. Outside the window it neither marks the day done nor logs equity (`:189,226,235,240`).

## Assumptions the code makes

- Yahoo's last row is today's and is correct. Nothing checks its date or compares it with Alpaca's prices.
- An accepted order is a filled order. Alpaca paper fills about 10% of orders partially and credits no dividends.
- Margin buying power covers buys sent before the sells fill.
- Some scheduled trigger starts a job that is still alive at 15:30. A job that starts before about 09:50 ET ends earlier.
- Every push succeeds, and "this run's version wins" is safe for files that only grow.
- Equity read at 15:30, before trading, can be compared with close-to-close model returns.

## Tests

`test_monitor.py` passes. It covers `rebalance()` against a fake Alpaca: closing zero-weight and outside holdings, the band, the SGOV size with the new netting, cancel-first, the no-data skip, whole-share orders, drawdown tiers, one equity row per day, and one missed-day case. The new test fails on the committed code, as it should.

Not covered: `run()` and its gates, the forced path, the FAILED/SKIPPED retry, `market_clock`, half days, `signals.py`, `loop_monitor.py` and every git step.

## Current state

- Deployed `state.json`: rebalanced 2026-11-20, missed [2026-11-19], risk-off, peak 95,083.54, tier 0. The 100,000 peak exists only in the local edit.
- `signals/equity_log.csv`: one row (2026-11-20, $95,083.54, target gross 34.0%).
- Positions are not stored in the repo. The post-mortem reports stocks about 39% against a 33.3% target, SGOV 64.7%, cash about −$3.6k.
- The snapshot file timestamps every pass: 23 so far. None fell in market hours on 11-19. On 11-20 the first was at 15:30:32 ET, then one every 2 minutes until 16:00:26.
- `signals/prediction_markets.csv`: 12,031 rows, 14.8 MB.

## What the offline checks showed

Scripts are in the session scratchpad. Nothing was run against Alpaca, Yahoo or GitHub.

- Local fix: in 20,000 random books cash never fell below +1% of equity. The committed code went negative in 30% of them, worst −5.1%. From the reported 11-20 book the committed code leaves cash at −3.7%, and −7.6% if the target falls to 30%; the fix restores +2.0%.
- Band, replayed on 2015-2026 prices: 0.83%/yr tracking error against the model and a gap of up to 7.2 points of equity. A 0.25% band gives 0.42% and 1.8 points for about 440 more small orders a year.
- Equity snapshot: on 5-minute bars for QQQ, NVDA and TSLA, a perfectly run account measured from 15:30 to 15:30 shows 4.8-5.9%/yr tracking error at the model's 17.9% volatility. Every 250-session window is above the 3% ceiling.
- Snapshot file: 97% of rows are Kalshi sports parlays matched by `ai\b` in "Shai". Each pass adds 0.76 MB. About 118 passes remain before GitHub's 100 MiB limit rejects every push.
- A queued job checks out the commit from its trigger time. Its first rebase deletes the rows the earlier job appended (reproduced in a scratch repository).
- A job started at 07:17 ET ends at 12:57. One failed `/clock` call at `loop_monitor.py:43` ends the job.
- An empty Yahoo frame crashes the pass before any alert. Data three days old still trades and marks the day done. A forced run with the market closed sends all 13 orders.
- The SGOV fix changes rebalance logic that MATH.md lists as frozen, so it needs a row in the change log.
