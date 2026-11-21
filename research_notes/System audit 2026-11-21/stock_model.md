# Stock model: weights, volatility target, regime rule

Audit note, 2026-11-21. Scope: `model.py`, `test_model.py`, `MATH.md` §1–5 and §7. Callers read for context: `monitor.py`, `backtest.py`, `track.py`. All checks ran offline on `data/prices.csv` (closes to 2026-11-19). Nothing in the repo was changed.

## Purpose

`model.py` turns a table of daily closes into one row of long-only target weights per day for 12 stocks, and turns a weight table into backtest returns. `monitor.py` trades the last row once a day on the Alpaca paper account. `backtest.py` and `track.py` replay every row.

## Data flow

1. `load_prices` (model.py:38-40) downloads adjusted closes for the 12 names and QQQ from Yahoo. A name with no data stays as an empty column.
2. `target_weights` (model.py:88-121) fills gaps forward, takes daily log returns, and computes each name's 60-day volatility and the 60-day covariance matrix.
3. Base weight is 1/volatility for each eligible name, scaled to sum to 1, then clipped at the cap. Clipped weight is not handed to other names; it stays in cash.
4. The book's volatility is estimated from those weights and the covariance. Every weight is multiplied by min(1, 20% / estimate), then by 0.5 if QQQ is below its 200-day average.
5. Live, `monitor.py:227` takes the last row at about 15:30 ET, with the price at that moment standing in for the close. Whatever is not in stocks goes to SGOV.
6. `backtest_returns` (model.py:124-136): weights set at close t earn the return from t to t+1. Cost is 5 bp times the trade from yesterday's drifted weights to today's target, booked on day t.

## Decision rules and parameters

| Rule | Value | Where |
|---|---|---|
| Universe | 12 names, benchmark QQQ | model.py:8-15 |
| Volatility and covariance | 60 sessions of log returns, ×√252 | model.py:22, 94, 97 |
| Eligibility | 63 daily returns since listing (defect 4) | model.py:52-53, 61 |
| Sizing | inverse volatility, signals off | model.py:27-28, 109-110 |
| Caps | 25% per name, 5% for SPCX, excess to cash | model.py:16, 24, 111-112 |
| Volatility target | 20%, never above 100% invested | model.py:24, 115-116 |
| Regime | ×0.5 when QQQ's close is below its 200-day mean | model.py:29, 118-120 |
| Cost | 5 bp per unit of turnover | model.py:124, 134-136 |

Measured since 2015-03-31: 80% invested on average; the volatility target binds on 60% of days; risk-off on 17.7% of days; 61 regime switches, and 9 of 31 risk-off spells lasted two days or less. The 25% cap has never bound (largest weight 20.4%, MSFT). The SPCX cap bound on 19 days and left at most 1% in cash. Turnover is about 6 times the account a year, a third of it on switch days, costing about 0.3% a year.

## Behaviour when volatility changes

The window weights all 60 days equally, so a shock counts in full for 60 sessions and then disappears in one day. The three largest one-day rises in the volatility scale since 2015 (+20, +12 and +9.5 points) each came exactly 60 sessions after a shock day (2025-04-09, 2018-12-26, 2020-03-16).

In this episode the same effect raised exposure from 90% to 100% on 23–26 October, with QQQ 6–7% below its peak, as late-July moves left the window. The book took the 5 November fall (QQQ −6.5%) at 94%. The regime rule also whipsawed: 40% on 5 November, 78% on 11 and 12 November, 39% on 13 November, costing about 0.26% against staying halved. The post-mortem table samples every fifth session and shows neither.

Expect mechanical step-ups when the 5 and 20 November returns leave the window, on about 3 and 19 February 2027, whatever the news.

## Assumptions the code makes

- Yahoo closes are right and complete. Nothing checks for stale, missing or wrong prices, and gaps are filled forward without limit.
- The 15:30 price is close enough to the close, and orders fill near it.
- Missing QQQ data means risk-on, because a comparison with an empty value is false (model.py:119).
- Cash earns nothing in the backtest.
- SPCX's pre-listing days count as zero returns in the covariance. This is harmless: it enters only with a full window.

## Tests

`test_model.py` checks that weights at three dates do not change when later data is removed (repeated here on 52 dates: exact match); that weights are non-negative, sum to at most 1 and respect the caps; that one missing close does not zero a name; that costs are charged on drift and on entry; and that the overfitting statistics behave on noise.

Not covered: the regime switch and the volatility target. With the halving switched off, or the target set to 900%, every test still passes. Also untested: eligibility, stale or partial data, zero volatility, missing QQQ, the `ew` branch, and that weights earn the next day's return (checked by hand: correct). The tests read the cached price file, so they depend on the last download.

## Defects

1. **The regime rule fails open on missing QQQ data (medium).** `monitor.py:204` fills forward before the guard at `:216` looks, so the guard fires only when QQQ is entirely empty. Replaying 5 and 13 November with that day's QQQ bar missing gives 81% and 78% gross instead of 40% and 39%.
2. **Stale prices read as low volatility (medium, rare).** `model.py:90` has no limit, and the shipped branch (`:109`) lacks the zero-volatility guard the other two branches have (`:100`, `:107`). AAPL stale for 15 sessions: weight +38%. Stale for 60: every weight is 0 for two or three sessions (SPCX, ORCL, AAPL), or the book becomes the stale name alone (NVDA). The monitor's no-data check covers only a fully empty column.
3. **Tests cannot see a broken risk rule (low).** See above.
4. **Eligibility is 63 returns, not 60 (low).** `min_hist` does nothing at any value up to 63; the 63-day trend window decides. SPCX's first weight is on 2026-09-14, its 64th close.
5. **MATH.md is stale (low).** §1–2 still give ANT a 5% cap and a 60-day rule, though the code dropped it. The Sharpe of 1.259 is 1.254 in the regenerated report.
6. **The cache ends on a partial row (low).** META and SPCX have no close for 2026-11-19. The backtest books 0% for them, and nothing refreshes or flags it (`backtest.py:22-30`).

## Current state

Frozen 2026-11-19 at a 20% target. Target at the 19 November close (cache): 37.4% gross, risk-off. Live log (`signals/equity_log.csv`): one row, 2026-11-20, equity $95,083.54, target gross 34.0%, risk-off. `state.json`: rebalanced 2026-11-20, one missed session (2026-11-19). QQQ must rise about 12% to restore full weight.
