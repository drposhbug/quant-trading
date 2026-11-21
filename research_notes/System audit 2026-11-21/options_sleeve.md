# Options earnings iron-fly sleeve: logic note

Audit of 2026-11-21. Line numbers are `options_earnings.py` unless stated.

## Purpose

A paper experiment on the second Alpaca paper account. Late on the session before a universe company reports earnings, it sells an at-the-money call and put and buys a further-out call and put (an iron butterfly), then buys it back the next morning. It gains when the stock moves less than the options implied. The report expects zero to slightly negative after costs and treats the sleeve as a test of order plumbing. Real money needs 120 closed trades with mean P&L above zero and t above 2 (`MATH.md:90`, `scorecard.py:158-168`).

## Data flow

`loop_monitor.py:33` runs the script after `monitor.py` on every pass: every 5 minutes, every 2 in the last 45. State is `options_state.json`. Closed trades go to `signals/options_trades.csv`. The loop commits both. On each pass with the market open:

1. Refuse to run if the options keys reach the stock account (77-83, 398).
2. Read equity, update the peak, load sessions from 14 days back to 30 days ahead (110-113, 363-366).
3. Alert once on any option position no tracked spread owns (346-353).
4. Manage each tracked spread (275-311).
5. With 30 minutes or less to the close, scan the 12 names for entries (373, 314-343).

Inputs: Yahoo (through yfinance) for report date and time of day, Alpaca's free "indicative" option quotes, the IEX last trade, and Alpaca paper for orders and positions.

## Decision rules and parameters

| Rule | Value | Lines |
|---|---|---|
| Report date | earliest Yahoo calendar date on or after today | 90 |
| Timing | before-open only if Yahoo shows a time after 00:00 and before 09:30 ET; otherwise, or on any error, after-close | 93-100 |
| Entry session | last session before the reaction session | 104-107 |
| Expiry | nearest expiry on or after the reaction day, at most 7 days later | 45, 179-183 |
| Short strike | strike nearest the stock price | 135 |
| Wings | strikes nearest price ± the at-the-money straddle mid | 137-142 |
| Skip | a leg with open interest under 100 or bid-ask over 20% of mid | 146-149 |
| Entry order | one four-leg day limit at the natural credit (sell at bid, buy at ask) minus $0.05 | 151-155, 212-219 |
| Size | floor(0.5% of equity ÷ max loss), max loss = (wider wing − credit) × 100; skip below one contract | 45, 156-161 |
| Blocks | already holding the name, four spreads open, equity over 10% below its peak | 326-328 |
| Decided once | the first pass that reaches a decision marks the event done | 339 |
| Exit window | reaction day or later, 09:45-10:30 ET: two tries at mid, then at natural | 46, 122, 249 |
| Expiry rule | any time on the session before expiry | 120 |
| Backstop | on expiry day, at natural at once, with an alert | 307-309 |
| Partial fills | entry keeps what filled; a close is sized to positions held and its lots averaged | 278-279, 239-246, 296-301 |
| P&L | (entry credit − average closing debit) × 100 × contracts, from fill prices, no fees | 259 |

## Assumptions the code makes

- Yahoo's date and time are right. Nothing checks them against a second source.
- Indicative quotes are close enough to the real market for natural minus $0.05 to fill. Exits have no cushion.
- A negative limit price means a credit on Alpaca multi-leg orders. No live order has confirmed it.
- The loop is running at 09:45-10:30 and in the last 30 minutes. Git shows no monitor commit in market hours on 2026-11-19, and the first on 2026-11-20 at 15:30 ET.
- Every spread ends through the bot's own close order. One that ends by expiry, assignment, broker liquidation or by hand is dropped with one Discord line and no ledger row (240-243).
- Only option positions are read (233-234), so stock delivered by an assignment is never seen.
- The stock keys are present. Without them the same-account guard compares nothing (79-80).

## Tests

`test_options.py` passes against a fake Alpaca. It covers strike, wing and size arithmetic, liquidity skips, entry days, the 30-minute gate, order fields, the three blocks, fill detection, the exit window, the close before expiry, close pricing, the ledger row, dry run, same-account refusal, partial fills and the orphan alert.

It does not cover `earnings()` (always stubbed), a report date beyond the 30-day calendar, two names in one scan, the first pass after the open when the expiry is the reaction day or the day after, a failed lookup while a close is booked, uneven legs, a corrupt state file, or the guard without stock keys. For a vanished spread it asserts only that the spread is dropped.

## Current state

- `options_state.json`: no spreads, no decided events, peak equity $100,000, no orphans. Last changed 2026-11-20 15:30 ET.
- No `signals/options_trades.csv`. Closed trades: 0 of 120. No event has been decided, so no order has been sent.
- NVDA reported on 2026-11-17, a day before the script was committed. Broadcom and Oracle are due in December.

## What it will do now

1. **Most likely nothing.** Tesla is scanned first and is next due in late January. A date beyond the 30-day calendar raises `ValueError` at line 321, outside the `try`, and ends the scan with a Discord error on each late pass. Replaying the last four quarters, 7 to 10 of 42 events were reachable if Yahoo posts a next date within a week of a report.
2. **If that is fixed, size stops most names.** Estimated from 2026-11-19 prices and past earnings moves, one contract risks about $300 (NVDA), $340 (AAPL), $480 (AMZN), $500 (ORCL), $600-670 (GOOGL, SPCX) and $1,160-1,950 (TSLA, MSFT, AVGO, AMD, META) against a $500 budget. Higher volatility raises every figure. That is 12 to 16 trades a year, not 44.
3. **The 09:45-10:30 window rarely governs.** With Friday expiries, of 124 reports since November 2023 the reaction day was the expiry Friday for 28% (closed at natural on the first pass after the open) and the Thursday before it for 44% (mid tries start on the first pass). AAPL and AMZN are almost always Fridays.

Closed trades are 0, so a logged rule correction restarts nothing (`MATH.md:85`).

## Defects

Findings `options_sleeve-1` to `-8` in the audit output carry the detail. One is not visible above: a filled close is booked twice if the price lookup fails while it is being logged (296-302). Separately, the report's Monte Carlo omits the stock's ordinary move on the holding day, which flatters every row by about 0.04 of max loss: the fairly-priced row should read 0.00 gross and −0.20 net.
