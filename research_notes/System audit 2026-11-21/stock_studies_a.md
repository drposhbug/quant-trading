# Stock studies A: retail-edge slate and leverage study

## Purpose

Two offline studies. Neither trades, and no live or paper code imports them.

- `retail_edge_tests.py` tests eight single changes to the frozen stock model: H1 tax-aware execution, H2 muni cash, H3 month-end timing, H4 a ±2% band on the 200-day rule, H5 faster re-entry after VIX ≥ 40, H6 a semis cap, H9 a 52-week-high tilt, H12 net liquidity. Result: nothing passes.
- `leverage_study.py` asks whether the same risk engine at 1x to 2x leverage beats buy-and-hold on six stock indices. Result: no leverage level passes.

## Data flow

**Retail edge.** Inputs are `data/prices.csv` (12 names plus QQQ, 2014 to 2026-11-19) and `data/retail_edge.pkl` (extra 2014-era names, ETFs, T-bill rate, VIX from 1990, three Fed series). `weights()` rebuilds the frozen weights without the 200-day gate and asserts they equal `model.target_weights`. `lagged()` delays every weight one session. `sim()` turns weights into daily returns with the ±1 pp no-trade band, 5 bp cost and T-bill interest on idle cash. H1 instead runs a share-level tax ledger from $100,000. `boot_p` and `holm` judge; `write_report` prints the table.

**Leverage.** Input is `data/leverage_px.pkl` (six indices, two 2x ETFs, T-bill rates). `market()` builds buy-and-hold, naive 1.5x/2x and engine × L per index. `run()` adds financing, cash interest and dividends. `criteria()` applies the pass rules.

## Decision rules and parameters

Retail edge (`retail_edge_tests.py`):

- Shared: band 1 pp, cost 5 bp, 2,000 resamples (:103). Signal at close t, fill at close t+1 (:205). A name trades only if it is over 1 pp from target or must be exited (:198).
- Test: P is the share of paired block-bootstrap resamples (mean block 20 days) in which the challenger is no better (:511–518). A hypothesis takes its worst universe's P (:671). Holm runs across hypotheses that produced a P (:521, :844). Passing needs Holm P < 0.05 plus the extra conditions (:848).
- H1: rates 40.8% short-term and interest, 23.8% long-term, $3,000 loss offset (:105, :212–226). Short-term means held ≤ 365 days (:253). Wash sales 30 days either side (:261, :292). Challenger sells losses first, then long-term gains, then short-term gains (:309). Any lot at ≤ 90% of basis is harvested into QQQ or VGT (:382) with a 30-day no-buy window (:392), then swapped back unless that realises a short-term gain above 0.5% of NAV (:399). Sales realising short-term gains need a 5 pp gap (:443). Gain lots aged 335–365 days are protected, up to 3% of NAV (:415–419). Tax is paid at year-end (:467).
- H2: cash sleeve in SUB vs BIL vs SHY, taxed daily (:703–708).
- H3: z-score of 60/40 drift at T−5 over 36 months; ×0.8 if z ≥ 1, ×min(1.2, 1/exposure) if z ≤ −1, on signal days T−5 to T−3 (:544–555).
- H4: halve below 0.98 × the 200-day average, restore above 1.02 × (:143–146).
- H5: an episode starts when the 63-session VIX high is ≥ 40, VIX is ≤ 0.6 × that high, and no episode began in the prior 126 sessions (:564). The halving is then off for 126 sessions or until QQQ closes above its 200-day average (:581). Under 6 ^NDX episodes means "untested" (:800).
- H6: semis ≤ 40% of the sleeve (:171–174); moot if it binds on under 10% of days (:817).
- H9: monthly weight multiplier 0.5 to 1.5 by rank of price over 252-day high (:597–607).
- H12: halve when 4-week net liquidity (Fed assets minus Treasury account minus reverse repo) falls, usable two days after the Wednesday date (:615–619).

Leverage (`leverage_study.py`): L ∈ {1, 1.25, 1.5, 2} (:22). Financing T-bill + 1.5% and 5 bp; stress T-bill + 3% and 10 bp (:23). Constant dividend yields (:21). 252-day warm-up (:24). Name cap lifted to 100% for a one-asset engine (:26). Return formula (:74). Pass needs CAGR and drawdown both better than holding on ≥ 5 of 6 indices including the Nikkei (:169–171), pooled Sharpe P < 0.05 (:166, :172), worst 10-year CAGR ≥ holding on Nikkei and S&P (:173), and all three again under stress.

## Assumptions the code makes

- Fills at the close, adjusted prices, flat costs. The shipped list was picked with hindsight.
- One random seed for every bootstrap, so each P carries about ±0.005 of simulation noise.
- Days are the resampling unit, even for H5, whose gate differs on only 26 of 2,929 stock-window sessions.
- H1: top federal bracket, no state tax, QQQ and VGT never "substantially identical" to a single name.
- Leverage: US T-bill rates on yen, euro, sterling and Hong Kong indices; no currency effect; rough constant dividend yields; the six markets resampled independently.

## What the tests cover

`test_retail_edge.py` (passes) checks tax netting, both wash-sale directions, lot order, `sim` at zero band against the model's backtest, the decomposed weights against the frozen model, and one synthetic VIX episode. It does not run `run_ledger` end to end, `boot_p`, `holm`, or the H3/H5/H9/H12 signal builders.

`test_leverage_study.py` (passes) checks financing and dividend arithmetic, drawdown helpers and no lookahead in engine weights. It does not test `rf_daily`, `boot_sharpe_diff` or `criteria`.

## Current state

Studies only: no ledger, no positions. Last runs 2026-11-20 (leverage commit 1f585c9; retail edge 1e389fb). Windows: stocks 2015-03-31 to 2026-11-19, ^NDX from 1990.

Reproduced exactly from the caches: every P for H2 to H12, H1's returns, taxes and harvest counts, and the leverage decision table. Deleting future data changed no signal, so there is no lookahead. Holm is correct.

At the 2026-11-19 close QQQ was 5.4% below its 200-day average. The halving signal has been on since the 11-13 close, after three switches in seven sessions (11-05, 11-11, 11-13). Target exposure is 37%. The study's benchmark is 13.9% below its 6 October peak (worst in sample: 22.7%). VIX's 63-session high is about 32, so H5's trigger is not armed.

## What the audit found

- Leverage pooled P is too small. Resampling the six markets together moves L = 1.0 from 0.01 to 0.10 and L = 1.25 from 0.04 to 0.17. Every level still fails.
- H5's 0.054 is one event. 85–90% of the stock-window gain is 19 sessions in April–May 2025, other seeds give 0.056–0.067, and four of 11 episodes switch nothing.
- H1's verdict holds. Its pre-tax loss (1.0 pp a year) is time spent in QQQ/VGT after harvests. Two small ledger slips (:420, :292) change nothing.
- The test has little power: a planted +0.84 pp/yr edge at 2% tracking error is detected 42% of the time.
- MATH.md logs neither study, and both pre-registration texts enter git with their results.

Audit diagnostics, not trials of record: H3 without the band (still null), H5 block lengths and seeds, leverage joint resampling, H1 ledger corrections.
