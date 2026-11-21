# Stock proof battery: backtest.py, track.py, MATH.md §0, §6 and Change control

Audit note, 2026-11-21. Read-only review. Scratch scripts are outside the repo.

## Purpose

`backtest.py` re-runs the frozen stock model and eleven comparison series over 2015–2026, applies a fixed set of statistical tests and writes `reports/backtest_results.md`. MATH.md §0 turns those numbers into pass/fail claims. `track.py` compares the paper account's logged equity with what the model earned over the same days. `scorecard.py` uses that comparison for the pre-registered execution test of the paper year.

## Data flow

1. `prices()` (backtest.py:22-30) reads `data/prices.csv`: yfinance adjusted closes for 12 names and QQQ from 2014-01-02. It downloads again only if the file is missing, the column list changed or `--refresh` is passed. It does not check dates or missing values.
2. `model.target_weights` gives weights at each close. `model.backtest_returns` (model.py:124-136) earns the next day's return and charges 5 bp on the trade from drifted weights. Cash earns 0.
3. `main()` drops the first 312 rows (backtest.py:117) and builds the series (:120-149): shipped model, 10 bp cost, one day late, signal model, HRP, old 8-name model, no risk engine, equal weight on every listed name, equal weight × 0.64 (a constant chosen with hindsight), equal weight vol-targeted on its own trailing 60-day volatility, QQQ, and the same engine on the end-2014 top-10 tech list. Four extra tickers and the T-bill series (^IRX/100/252) are downloaded at every run and not cached.
4. The tests run (:165-199) and the report is written (:242).
5. `track.compare` (track.py:21-32) downloads prices from 500 days before the first log row, recomputes the model, compounds its daily returns over each interval between logged dates and subtracts that from the change in logged equity. Tracking error is the standard deviation of those gaps × √252. The equity is read at about 15:30 ET, before that day's orders (monitor.py:62, 236).

On a normal day nothing here trades. `backtest.py` runs only by hand. `track.compare` runs inside the daily scorecard from 15:23 UTC.

## Decision rules and parameters

- Stationary bootstrap: mean block 20 days, 2,000 resamples, seed 7, the same index paths for every series (backtest.py:19, 43-50, 165-166). Pass bars: lower CI bound above 0, P < 0.05 (:207-217).
- Drawdown tests: share of resamples in which the model's worst drawdown is at or below the benchmark's (:168-181).
- Alpha: OLS on T-bill-excess returns, Newey-West with 5 lags, bar t > 3 (:57-69, 184-186).
- Deflated Sharpe: 60 grid variants (vol target 10/15/20/25%, regime scale 0/0.5/1, vol window 20/60/120, regime average 100/200, less 12 duplicates), bar 0.95 (:72-82, 188-193).
- PBO: 16 blocks, 12,870 splits, bar 0.30 (:85-106).
- Rank IC: daily Spearman of score against next-day and non-overlapping 5-day returns, bar t > 2 (:109-112, 196-199).
- Change control (MATH.md:53-59): frozen 2026-11-19. A change needs one pre-registered paired bootstrap with P < 0.05 on the shipped universe and on the end-2014 list, decided at a scheduled review.
- Paper year (MATH.md:74-79, 89; scorecard.py:65, 151): tracking error ≤ 3%/yr, at most 5 missed sessions, mean fill shortfall ≤ 10 bp, no stray positions, minimum 250 logged sessions. `track.py` needs two log rows (:37).

## What was verified

- An offline rebuild from the cache reproduces every number in the report exactly. The end-2014 row matches to 0.004 Sharpe using a different local price file.
- Independent re-implementations match the bootstrap (mean block 20.1), `hac_alpha`, `rank_ic`, `pbo_cscv` and `deflated_sharpe` to six decimals. The formulas are coded correctly.
- Alpha t against QQQ is stable from 0 to 120 lags (3.15 to 3.81). Sharpe comparisons do not move with block length.
- `track.compare` aligns model and live returns correctly, compounds across missing log rows correctly, and its 500-day warm-up gives the same weights as full history. A zero-error account snapshotted at the close shows 0.09% tracking error.
- The equal-weight challenger numbers and the Nasdaq-100 vol-target numbers in MATH.md reproduce, although no committed script produces them.

## Assumptions the code makes

- Trades fill at the close the weights were computed from, at a flat 5 bp.
- Idle cash earns 0, yet the full T-bill rate is subtracted for every "ex T-bill" figure. Live, idle cash is in SGOV.
- A missing close equals the previous close, with no warning.
- Twenty-day blocks are long enough for a drawdown test of rules that act over 60 and 200 days.
- The 60 grid variants are the only trials. The report says universe, sizing and signal choices are outside the count.
- `track.py`: every change in logged equity is investment return, every logged date has a price row, a 15:30 snapshot is comparable to a close, and the paper account receives the dividends that adjusted closes include.

## Tests

`test_model.py` passes in 4 seconds. It covers no-lookahead on three dates, weight limits, the HRP path, PBO on noise and on a planted edge, deflated Sharpe on noise, one missing close and the cost on drifted weights. It does not cover the bootstrap, the alpha regression, rank IC, any benchmark construction, `sizing="ew"`, the agreement of MATH.md with the report, or anything in `track.py`. `test_scorecard.py` replaces `track.compare` with a stub.

## Current state

- Report: generated 2026-11-19 23:36 ET, period 2015-03-31 to 2026-11-19, 2,929 days. MATH.md quotes the 2,928-day run of 11-18. About 22 figures differ and no verdict changes.
- Cache: 3,241 rows. The last row has no close for META or SPCX.
- `signals/equity_log.csv`: one row (2026-11-20, $95,083.54, target gross 34.0%, risk-off). `track.py` cannot run until a second row exists.
- `state.json` (working copy): rebalanced 2026-11-20, missed 2026-11-19, peak equity 100,000 (committed value 95,083.54). `monitor.py`, `test_monitor.py` and `state.json` have uncommitted edits.
- Open positions were not read. This audit made no API calls.

## Defects found (detail in the structured result)

1. The 15:30 snapshot alone produces about 5%/yr of measured tracking error at normal exposure and 2.5% in risk-off. The 3% bar fails with perfect execution.
2. A paper-account reset would be read as a one-day gain of 5.2% and fail the year's test.
3. "No persistent drift" is pre-registered but never computed. The live rules and uncredited dividends build in roughly −0.8%/yr.
4. The one alpha pass (against QQQ) exists only on the hindsight universe. On the end-2014 list t = 1.34.
5. Drawdown p-values move with block length. The QQQ row flips; the vol-matched rows do not.
6. MATH.md and the report disagree on about 22 figures.
7. Missing closes are forward-filled silently in the cache and in `track.compare`.
8. Ex-T-bill Sharpe and alpha penalise the model's idle cash; the gap to equal weight is overstated about threefold.
