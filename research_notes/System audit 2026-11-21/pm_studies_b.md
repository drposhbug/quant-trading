# pm_studies_b: event odds, post counts, parlays, weather

Audit note, 2026-11-21. "Re-run" means reproduced offline, read-only, from the caches in `data/`.

## Purpose

Five research scripts. Each asks "does X beat a prediction-market price after fees?" and writes one report. All five answered no. Nothing here feeds the scorecard, a paper sleeve or the stock model, and on a given day nothing runs unless someone starts a script by hand.

## Data flow

Every script caches public history in `data/`, builds one table, runs fixed tests and overwrites its report. `maker_sim.py` borrows the weather loaders.

- **event_odds_study.py.** Kalshi Fed-decision and CPI ladders plus Polymarket Fed, CPI and earnings-beat markets. Odds one day, one hour and five minutes before each announcement become an implied expectation E and a surprise S; SPY, QQQ or stock returns (Alpaca bars) are regressed on them.
- **count_markets.py.** Polymarket and Kalshi "how many posts this week" brackets plus the xtracker post export. A negative-binomial rate model forecasts the final count at 0, 25, 50 and 75% of each window; it is scored against bracket prices and a buy-the-underpriced-bracket rule is simulated.
- **combo_study.py.** Random 30-second samples of Kalshi parlays ("combos"): first fill price, settlement value, product of the legs' mid prices. Measures the return from buying NO.
- **combo_change_study.py.** Same sample. Splits the NO return into "pricing" and "luck" and fits a leg-correlation model.
- **weather_study.py.** Kalshi daily-high brackets in 7 cities, NWS model forecasts (IEM archive) and observed highs: calibration, model versus market, reaction to forecast updates, one betting rule.

## Decision rules and parameters

- **Event odds.** Announcement time: FOMC 14:00 ET, CPI 08:30 ET (`event_odds_study.py:68`); earnings 16:00 ET when the 8-K lands 16:00 to 20:00, TSM 00:30 ET (`:91-104`). Odds are the last point at or before the horizon, up to 10 days old (`:32`, `:188-190`). Kalshi price is the mid when 0 ≤ bid < ask ≤ 1, else last trade (`:155`). Trading rule: follow the odds drift from one day to five minutes before, only when the asset drifted the other way; minimum drift 0.5 bp or 0.005; 2 bp per side (`:33`, `:38`, `:379-385`). Pass: Holm p < 0.05 across 15 tests and the same sign in both halves (`:471`).
- **Counts.** Rate profile from the last 672 hours; dispersion from 30 to 60 past windows (`count_markets.py:43`, `:77-92`). Buy YES when model probability minus ask ≥ 0.08 and ask ≤ 0.98; Polymarket ask is the hourly price plus 1c; fee 0.05·p(1−p), Kalshi 0.07·p(1−p) (`:44`, `:313`, `:353-363`). Holdout is the last 30% of events (`:377-381`). Pass: Holm p < 0.05 across 12 tests and ROI above zero in both halves (`:598`).
- **Combos.** Three windows a day, up to 10 combos each, 2025-09-15 to 2026-11-15 (`combo_study.py:61-62`). Rule: buy NO at the first fill when price minus leg product ≥ 5 points (`:63`). Taker fee 0.07·q(1−q) rounded up per contract; maker fee 0.035·q(1−q) from 2026-08-20 (`:71-88`). Pass: holdout day-bootstrap interval above zero and both discovery halves positive (`:459`).
- **Combo change.** Calibration fitted before 2026-08-01; early is 2025-10 to 2026-07, late is 2026-10 to 2026-11; rule edge 4 points (`combo_change_study.py:31-34`, `:283-286`, `:460`).
- **Weather.** Decision times 15:00 the day before, 08:00 and 12:00 local; a forecast counts as available 2 hours (NBM) or 4 hours (GFS) after its run time (`weather_study.py:38-40`). Price is the mid when the spread is at most 10c, else last trade (`:248`). Forecast errors come from days D−365 to D−2 (`:313`). Bet when model minus ask ≥ 8 points, 100 contracts, fee rounded up to the cent (`:41`, `:228-230`, `:463-470`). Pass: Holm p < 0.05 across 13 tests plus p < 0.05 with the same sign on the last 30% of dates (`:505`).

## Assumptions the code makes

- A cached mark is a tradable price: Polymarket hourly marks become an ask by adding 1c, and a last trade stands in for a quote when the book is wide.
- Polymarket's hourly points are the price "at" the hour. They are stamped 3 to 59 seconds after it, so the last point before a decision on the hour is about 60 minutes old.
- The post export read today equals what a trader saw live.
- A parlay's fair value is the product of its legs; only the quoting maker gets the NO side at the opening price.
- NBM text runs are at 01/07/13/19Z. Since May 2026 the cache labels them 00/06/12/18Z; the 2-hour lag was not re-checked.

## What the tests cover

All five test files pass. They check the pure maths: fees, ladder and bracket parsing, bracket probabilities, that the rate model ignores future data, leg-price and minute-bar lookups, bootstraps, Holm, the logistic fit. They do not check how samples are built or how prices line up with decision times, where every defect below sits. One weather test asserts the last-trade fallback as correct.

## Current state

No ledger, no positions, no schedule. Reports and code committed 2026-11-20. Samples: 26 FOMC, 44 CPI and 46 earnings events; 667 count events (29,628 bracket rows); 9,450 combos, 2,497 with leg prices; 45,259 weather brackets over 7,545 city-days. Published results: event odds 4 of 15 tests pass, none tradable; counts 0 of 12; combo rule fails at −6.1%; weather 6 of 13, effects too small to trade.

## Defects found (re-run evidence)

None changes a pre-registered verdict.

1. **Combo change: "pricing unchanged, the flip was luck" is not supported.** The pricing term depends only on price, so a shrinking house margin is booked as luck. Measured without outcomes, price over leg product fell from a median 1.18 to 1.08 (p = 0.0003).
2. **Event odds: the "leak" test has the wrong null.** Efficient pricing gives a slope of 1, not 0. The earnings pass (1.80) is not different from 1 (t = 1.41).
3. **Weather: stale last trades used as prices** on 5 to 20% of rows. The noon "rich bracket" bias of −4.4 points becomes −0.9 on quoted rows.
4. **Counts: hour-old Polymarket prices** against a model that has seen the latest hour. Musk bet ROI falls from +22% to +9% with fresh prices.
5. **Event odds: the CPI shutdown filter also deletes two FOMC meetings** (September and October 2025).
6. **Combos: leg mids have no spread limit.** 47% of rule trades include a leg quoted wider than 10c; tight-quote trades do worse (−11%).
7. **Event odds: an empty Kalshi book counts as 0.50**, breaking 5 of 45 CPI ladders.
8. **Combos: sampling differs across the 2026-09-19 cutoff** (fills later than 90 seconds: 1% before, 28% after).

Ruled out: resting offers on cheap weather brackets (0 to −2% once a fill is required).
