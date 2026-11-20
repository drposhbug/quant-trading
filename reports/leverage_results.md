# Leverage study: is a leveraged risk engine more reliable than buy & hold?

## Pre-registration (written 2026-11-20, before any run of leverage_study.py)

Study only: the live model is frozen (MATH.md change control); this result goes to the 2027-11-19 scheduled review.

- **Variants:** frozen engine (model.target_weights: inverse-vol + 20% vol target + 200d regime, all P frozen) run on a
  single index (the index's own 200d MA as the regime), final weights multiplied by L ∈ {1.0, 1.25, 1.5, 2.0}.
  So L scales both the vol target (20%·L) and the max gross (L).
- **Benchmarks:** buy & hold 1x; naive constant 1.5x and 2x, rebalanced daily.
- **Markets:** ^GSPC (1950+), ^NDX (1985+), ^N225 (1965+), ^GDAXI (1988+), ^FTSE (1985+), ^HSI (1987+). Evaluation
  starts 252 trading days after each start (regime/vol warm-up); all arms over the same days.
- **Returns:** weights at close t earn t→t+1 (model.backtest_returns). Borrowed exposure (gross > 1) pays T-bill +
  spread; idle cash (gross < 1) earns the T-bill (live holds SGOV). T-bill = ^IRX, backfilled before 1960 with FRED
  TB3MS (monthly). Non-US markets: same US T-bill + spread, local-currency index returns, FX not modelled.
- **Dividends:** primary run adds an approximate constant dividend yield × exposure (long-run averages, crude):
  ^GSPC 3.0%, ^NDX 0.8%, ^N225 1.3%, ^FTSE 3.8%, ^HSI 3.3%, ^GDAXI 0% (it is already a total-return index).
  The pass decision is also reported price-only (both arms identical inputs).
- **Base case:** financing T-bill + 1.5%, cost 5 bp per unit turnover. **Stress:** T-bill + 3%, 10 bp.
- **Pass for a given L requires ALL of:**
  - (a) CAGR > buy&hold AND MaxDD better than buy&hold on ≥ 5 of the 6 indices, the Nikkei being one of the passes;
  - (b) pooled paired stationary bootstrap (L_block = 20, B = 2000, per market, engine and hold on the same index
    paths; Sharpe on T-bill excess returns; pooled = mean across the 6 markets of the per-draw Sharpe difference):
    P(Sharpe_engine ≤ Sharpe_hold) < 0.05;
  - (c) worst rolling 10-year CAGR ≥ buy&hold's on both the Nikkei and the S&P 500;
  - (d) (a)–(c) all still pass under the stress case.
- **Report only (not in the decision):** real 2x ETFs (QLD, SSO) vs synthetic 2x; the shipped 12-name universe at
  L = 1.0/1.5; drawdown durations and recoveries (2000, 2008, 2022, Nikkei 1990); 10-year forward paths by bootstrap
  (mean block 250 days, so 1-year trends survive resampling); sensitivity (regime 1 day late, vol window 20/60/120);
  PBO across the variants.

## Decision (pre-registered criteria)

| L | (a) wins of 6 (CAGR>hold AND MaxDD better) | Nikkei win | (b) pooled P(Sharpe ≤ hold) | (c) worst 10y ≥ hold on N225 & GSPC | base pass | (d) stress: a / b (P) / c | **PASS** | price-only (a/b/c) |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 1 (^N225) | yes | 0.011 | yes | no | no / yes (0.049) / yes | **FAIL** | no/no/yes |
| 1.25 | 4 (^GSPC, ^NDX, ^N225, ^HSI) | yes | 0.044 | yes | no | no / no (0.254) / yes | **FAIL** | no/no/yes |
| 1.5 | 5 (^GSPC, ^NDX, ^N225, ^GDAXI, ^HSI) | yes | 0.095 | yes | no | no / no (0.550) / yes | **FAIL** | yes/no/yes |
| 2.0 | 2 (^NDX, ^GDAXI) | no | 0.228 | no | no | no / no (0.861) / no | **FAIL** | no/no/no |

## Per-market results (base: T-bill + 1.5%, 5 bp, approx. dividends)

### ^GSPC (1951-01-05 → 2026-11-19, dividend 3.0%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 11.3%  | 15.8% |                 0.5  | -54.9%  |                      5.5 | -3.3%            | 1.2%                       |
| Naive 1.5x    | 13.0%  | 23.6% |                 0.46 | -72.6%  |                      7.6 | -8.8%            | 7.4%                       |
| Naive 2x      | 14.0%  | 31.5% |                 0.45 | -85.6%  |                     13.6 | -15.0%           | 14.9%                      |
| Engine L=1.0  | 10.9%  | 11.3% |                 0.62 | -29.5%  |                      4.7 | 0.4%             | 0.0%                       |
| Engine L=1.25 | 12.2%  | 14.1% |                 0.6  | -37.2%  |                      5.7 | -0.7%            | 0.1%                       |
| Engine L=1.5  | 13.3%  | 16.9% |                 0.58 | -44.4%  |                      6.8 | -1.8%            | 0.7%                       |
| Engine L=2.0  | 15.3%  | 22.5% |                 0.57 | -57.8%  |                      7.6 | -4.3%            | 1.6%                       |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 11.3%, MaxDD -54.9%; Engine L=1.0: CAGR 10.8%, MaxDD -29.9%; Engine L=1.25: CAGR 11.6%, MaxDD -37.7%; Engine L=1.5: CAGR 12.4%, MaxDD -45.5%; Engine L=2.0: CAGR 13.7%, MaxDD -59.2%

### ^NDX (1986-09-30 → 2026-11-19, dividend 0.8%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 14.9%  | 26.1% |                 0.55 | -82.5%  |                     14.6 | -7.7%            | 7.3%                       |
| Naive 1.5x    | 17.3%  | 39.1% |                 0.53 | -94.8%  |                     17.9 | -17.0%           | 9.5%                       |
| Naive 2x      | 17.5%  | 52.1% |                 0.51 | -98.8%  |                     20.7 | -27.7%           | 17.1%                      |
| Engine L=1.0  | 13.2%  | 15.9% |                 0.67 | -34.1%  |                      6.6 | 2.4%             | 0.0%                       |
| Engine L=1.25 | 15.2%  | 19.9% |                 0.66 | -42.4%  |                      7.1 | 1.9%             | 0.0%                       |
| Engine L=1.5  | 17.0%  | 23.8% |                 0.65 | -49.8%  |                      7.3 | 1.1%             | 0.0%                       |
| Engine L=2.0  | 20.0%  | 31.8% |                 0.64 | -62.2%  |                      7.6 | -0.7%            | 0.2%                       |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 14.9%, MaxDD -82.5%; Engine L=1.0: CAGR 13.0%, MaxDD -34.4%; Engine L=1.25: CAGR 14.7%, MaxDD -42.8%; Engine L=1.5: CAGR 16.1%, MaxDD -50.2%; Engine L=2.0: CAGR 18.3%, MaxDD -62.6%

### ^N225 (1966-01-18 → 2026-11-20, dividend 1.3%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 7.8%   | 20.5% |                 0.25 | -76.9%  |                     30.9 | -8.3%            | 27.9%                      |
| Naive 1.5x    | 6.8%   | 30.8% |                 0.22 | -95.8%  |                     36.4 | -16.3%           | 35.1%                      |
| Naive 2x      | 4.7%   | 41.0% |                 0.21 | -99.4%  |                     36.9 | -24.8%           | 41.7%                      |
| Engine L=1.0  | 7.9%   | 13.6% |                 0.3  | -41.8%  |                     15.9 | -2.7%            | 8.2%                       |
| Engine L=1.25 | 8.2%   | 16.9% |                 0.29 | -58.1%  |                     23.4 | -4.7%            | 16.5%                      |
| Engine L=1.5  | 8.4%   | 20.3% |                 0.28 | -70.4%  |                     25.4 | -6.9%            | 22.5%                      |
| Engine L=2.0  | 8.3%   | 27.1% |                 0.27 | -85.8%  |                     34.5 | -11.3%           | 29.1%                      |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 7.8%, MaxDD -76.9%; Engine L=1.0: CAGR 7.7%, MaxDD -43.2%; Engine L=1.25: CAGR 7.8%, MaxDD -59.9%; Engine L=1.5: CAGR 7.6%, MaxDD -72.3%; Engine L=2.0: CAGR 6.8%, MaxDD -88.0%

### ^GDAXI (1989-01-03 → 2026-11-19, dividend 0.0%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 8.0%   | 21.7% |                 0.33 | -72.7%  |                      7.3 | -3.3%            | 6.1%                       |
| Naive 1.5x    | 7.8%   | 32.5% |                 0.31 | -88.3%  |                     15   | -9.4%            | 14.8%                      |
| Naive 2x      | 6.3%   | 43.3% |                 0.29 | -95.4%  |                     25.3 | -16.7%           | 20.9%                      |
| Engine L=1.0  | 7.3%   | 14.4% |                 0.36 | -39.9%  |                      5.7 | 2.6%             | 0.0%                       |
| Engine L=1.25 | 7.9%   | 18.0% |                 0.35 | -48.9%  |                      5.9 | 2.2%             | 0.0%                       |
| Engine L=1.5  | 8.2%   | 21.6% |                 0.34 | -56.6%  |                      6   | 1.5%             | 0.0%                       |
| Engine L=2.0  | 8.4%   | 28.8% |                 0.33 | -69.1%  |                      8.9 | -0.2%            | 0.1%                       |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 8.0%, MaxDD -72.7%; Engine L=1.0: CAGR 7.1%, MaxDD -40.1%; Engine L=1.25: CAGR 7.4%, MaxDD -49.1%; Engine L=1.5: CAGR 7.4%, MaxDD -57.0%; Engine L=2.0: CAGR 6.9%, MaxDD -69.6%

### ^FTSE (1985-12-31 → 2026-11-19, dividend 3.8%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 9.1%   | 17.1% |                 0.41 | -46.8%  |                      5.3 | -1.8%            | 1.1%                       |
| Naive 1.5x    | 10.0%  | 25.6% |                 0.38 | -66.2%  |                      7   | -6.6%            | 6.1%                       |
| Naive 2x      | 10.1%  | 34.2% |                 0.36 | -79.6%  |                     14.7 | -12.2%           | 11.0%                      |
| Engine L=1.0  | 7.1%   | 11.8% |                 0.38 | -34.7%  |                      5.6 | -0.5%            | 0.2%                       |
| Engine L=1.25 | 7.6%   | 14.7% |                 0.36 | -43.3%  |                      6   | -1.8%            | 1.5%                       |
| Engine L=1.5  | 8.0%   | 17.6% |                 0.35 | -51.0%  |                      6.1 | -3.1%            | 3.6%                       |
| Engine L=2.0  | 8.5%   | 23.5% |                 0.33 | -64.2%  |                      8.8 | -5.9%            | 8.1%                       |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 9.1%, MaxDD -46.8%; Engine L=1.0: CAGR 6.8%, MaxDD -35.5%; Engine L=1.25: CAGR 7.0%, MaxDD -44.3%; Engine L=1.5: CAGR 7.0%, MaxDD -52.1%; Engine L=2.0: CAGR 6.7%, MaxDD -66.3%

### ^HSI (1988-01-12 → 2026-11-20, dividend 3.3%)

|               | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:--------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| Hold 1x       | 9.5%   | 24.8% |                 0.37 | -64.1%  |                      7.4 | -1.1%            | 1.3%                       |
| Naive 1.5x    | 9.4%   | 37.2% |                 0.35 | -80.4%  |                     10   | -4.6%            | 7.2%                       |
| Naive 2x      | 7.5%   | 49.5% |                 0.34 | -90.2%  |                     19.1 | -9.0%            | 20.7%                      |
| Engine L=1.0  | 9.1%   | 15.0% |                 0.46 | -36.0%  |                      4.5 | -0.4%            | 0.4%                       |
| Engine L=1.25 | 10.0%  | 18.8% |                 0.45 | -45.3%  |                      7.7 | -1.4%            | 1.7%                       |
| Engine L=1.5  | 10.8%  | 22.6% |                 0.44 | -53.8%  |                      8.8 | -2.4%            | 3.2%                       |
| Engine L=2.0  | 11.9%  | 30.1% |                 0.43 | -67.7%  |                      8.8 | -4.8%            | 6.2%                       |

Stress (T-bill + 3%, 10 bp): Hold 1x: CAGR 9.5%, MaxDD -64.1%; Engine L=1.0: CAGR 8.8%, MaxDD -36.5%; Engine L=1.25: CAGR 9.6%, MaxDD -46.5%; Engine L=1.5: CAGR 10.1%, MaxDD -55.2%; Engine L=2.0: CAGR 10.5%, MaxDD -69.4%

## Recovery time after each crash (years from the pre-crash peak back to it; depth in brackets)

| Market | Event | Hold 1x | Naive 1.5x | Naive 2x | Engine L=1.0 | Engine L=1.25 | Engine L=1.5 | Engine L=2.0 |
|---|---|---|---|---|---|---|---|---|
| ^GSPC | 2000 | 5.5 (-46%) | 6.9 (-64%) | 13.6 (-86%) | 4.7 (-29%) | 5.7 (-37%) | 6.8 (-44%) | 7.6 (-58%) |
| ^GSPC | 2008 | 4.4 (-55%) | 5.3 (-73%) | 5.8 (-84%) | 2.7 (-26%) | 2.7 (-32%) | 2.7 (-38%) | 2.8 (-49%) |
| ^GSPC | 2022 | 1.6 (-24%) | 2.0 (-35%) | 2.1 (-46%) | 1.9 (-18%) | 2.0 (-22%) | 2.0 (-26%) | 2.1 (-34%) |
| ^NDX | 2000 | 14.6 (-83%) | 17.9 (-95%) | 20.7 (-99%) | 6.6 (-34%) | 7.1 (-42%) | 7.3 (-50%) | 7.6 (-62%) |
| ^NDX | 2008 | 3.0 (-53%) | 3.7 (-71%) | 4.4 (-83%) | 2.2 (-28%) | 2.2 (-35%) | 2.4 (-41%) | 2.4 (-51%) |
| ^NDX | 2022 | 2.0 (-35%) | 2.2 (-51%) | 2.5 (-64%) | 1.5 (-22%) | 1.6 (-27%) | 1.6 (-32%) | 1.6 (-41%) |
| ^N225 | Nikkei 1990 | 30.9 (-77%) | 36.4 (-96%) | not yet (-99%) | 15.9 (-42%) | 23.4 (-58%) | 25.4 (-70%) | 34.5 (-86%) |
| ^GDAXI | 2000 | 7.3 (-73%) | 15.0 (-88%) | 25.3 (-95%) | 5.7 (-40%) | 5.9 (-49%) | 6.0 (-57%) | 6.8 (-69%) |
| ^GDAXI | 2008 | 5.8 (-55%) | 6.5 (-72%) | 7.7 (-84%) | 3.4 (-26%) | 3.5 (-33%) | 3.6 (-39%) | 5.9 (-50%) |
| ^GDAXI | 2022 | 1.4 (-26%) | 2.3 (-39%) | 2.3 (-50%) | 1.4 (-19%) | 1.5 (-24%) | 1.5 (-28%) | 2.2 (-36%) |
| ^FTSE | 2000 | 5.3 (-47%) | 7.0 (-66%) | 14.7 (-80%) | 5.6 (-35%) | 6.0 (-43%) | 6.1 (-51%) | 6.3 (-64%) |
| ^FTSE | 2008 | 3.1 (-45%) | 5.3 (-63%) | 5.9 (-76%) | 2.7 (-28%) | 2.8 (-34%) | 2.8 (-41%) | 5.7 (-52%) |
| ^FTSE | 2022 | 0.2 (-9%) | 0.2 (-14%) | 0.9 (-20%) | 2.2 (-13%) | 3.0 (-17%) | 3.0 (-20%) | 3.5 (-28%) |
| ^HSI | 2000 | 5.4 (-49%) | 6.4 (-69%) | 6.7 (-82%) | 3.8 (-33%) | 3.8 (-41%) | 3.9 (-49%) | 5.3 (-61%) |
| ^HSI | 2008 | 7.4 (-64%) | 10.0 (-80%) | not yet (-90%) | 3.0 (-30%) | 3.0 (-37%) | 3.0 (-43%) | 7.5 (-54%) |
| ^HSI | 2022 | 4.1 (-46%) | not yet (-62%) | not yet (-75%) | 3.6 (-30%) | 3.7 (-38%) | 3.7 (-45%) | 4.3 (-57%) |

## 10-year forward paths (stationary bootstrap, mean block 250 d, 2,000 paths per market, paired; pooled = all 6 markets equally weighted)

| Arm | median terminal wealth | 5th pct | 95th pct | P(lose money over 10y) | P(beat hold on same path) |
|---|---|---|---|---|---|
| Hold 1x | 2.62x | 0.84x | 7.98x | 7.6% | — |
| Naive 2x | 2.76x | 0.22x | 23.25x | 22.9% | 52.4% |
| Engine L=1.0 | 2.40x | 1.09x | 5.50x | 3.4% | 34.4% |
| Engine L=1.25 | 2.61x | 0.99x | 7.22x | 5.2% | 47.7% |
| Engine L=1.5 | 2.79x | 0.88x | 9.36x | 7.3% | 59.2% |
| Engine L=2.0 | 3.09x | 0.67x | 15.05x | 11.4% | 65.4% |

Per market, P(lose money over 10y) bootstrap (hold / L=1 / L=1.5 / L=2 / naive 2x): 
- ^GSPC: 1.1% / 0.2% / 0.9% / 2.1% / 9.9%
- ^NDX: 5.6% / 0.2% / 0.8% / 1.8% / 17.0%
- ^N225: 14.1% / 6.5% / 13.8% / 20.0% / 35.5%
- ^GDAXI: 12.2% / 6.1% / 13.0% / 18.9% / 31.1%
- ^FTSE: 3.0% / 2.9% / 7.4% / 13.1% / 15.1%
- ^HSI: 9.5% / 4.2% / 8.1% / 12.7% / 28.8%

## Sensitivity (report only): CAGR / MaxDD, base costs

| Market | Variant | Hold | L=1.0 | L=1.5 | L=2.0 |
|---|---|---|---|---|---|
| ^GSPC | frozen (vol 60, regime same day) | 11.3% / -54.9% | 10.9% / -29.5% | 13.3% / -44.4% | 15.3% / -57.8% |
| ^GSPC | regime 1 day late | 11.3% / -54.9% | 11.0% / -27.5% | 13.3% / -43.3% | 15.3% / -56.6% |
| ^GSPC | vol window 20 | 11.3% / -54.9% | 11.1% / -31.4% | 13.5% / -47.9% | 15.6% / -61.3% |
| ^GSPC | vol window 120 | 11.3% / -54.9% | 10.8% / -30.1% | 13.1% / -44.9% | 15.1% / -57.6% |
| ^NDX | frozen (vol 60, regime same day) | 14.9% / -82.5% | 13.2% / -34.1% | 17.0% / -49.8% | 20.0% / -62.2% |
| ^NDX | regime 1 day late | 14.9% / -82.5% | 13.1% / -31.4% | 16.7% / -46.5% | 19.5% / -58.7% |
| ^NDX | vol window 20 | 14.9% / -82.5% | 13.5% / -38.0% | 17.3% / -54.3% | 20.5% / -66.7% |
| ^NDX | vol window 120 | 14.9% / -82.5% | 12.7% / -33.0% | 16.2% / -48.4% | 18.8% / -60.8% |
| ^N225 | frozen (vol 60, regime same day) | 7.8% / -76.9% | 7.9% / -41.8% | 8.4% / -70.4% | 8.3% / -85.8% |
| ^N225 | regime 1 day late | 7.8% / -76.9% | 7.7% / -41.1% | 8.0% / -68.0% | 7.7% / -85.1% |
| ^N225 | vol window 20 | 7.8% / -76.9% | 7.5% / -46.3% | 7.8% / -73.8% | 7.5% / -87.9% |
| ^N225 | vol window 120 | 7.8% / -76.9% | 8.0% / -40.4% | 8.5% / -69.2% | 8.4% / -85.1% |
| ^GDAXI | frozen (vol 60, regime same day) | 8.0% / -72.7% | 7.3% / -39.9% | 8.2% / -56.6% | 8.4% / -69.1% |
| ^GDAXI | regime 1 day late | 8.0% / -72.7% | 7.2% / -41.4% | 7.9% / -58.2% | 8.1% / -70.6% |
| ^GDAXI | vol window 20 | 8.0% / -72.7% | 7.6% / -41.1% | 8.7% / -57.9% | 9.1% / -70.4% |
| ^GDAXI | vol window 120 | 8.0% / -72.7% | 7.5% / -38.5% | 8.5% / -55.1% | 8.8% / -67.6% |
| ^FTSE | frozen (vol 60, regime same day) | 9.1% / -46.8% | 7.1% / -34.7% | 8.0% / -51.0% | 8.5% / -64.2% |
| ^FTSE | regime 1 day late | 9.1% / -46.8% | 6.9% / -29.9% | 7.6% / -48.2% | 7.9% / -62.6% |
| ^FTSE | vol window 20 | 9.1% / -46.8% | 7.1% / -36.7% | 8.0% / -53.2% | 8.4% / -65.8% |
| ^FTSE | vol window 120 | 9.1% / -46.8% | 7.1% / -33.7% | 8.0% / -50.0% | 8.4% / -63.4% |
| ^HSI | frozen (vol 60, regime same day) | 9.5% / -64.1% | 9.1% / -36.0% | 10.8% / -53.8% | 11.9% / -67.7% |
| ^HSI | regime 1 day late | 9.5% / -64.1% | 8.9% / -37.8% | 10.6% / -56.1% | 11.6% / -69.8% |
| ^HSI | vol window 20 | 9.5% / -64.1% | 8.7% / -36.9% | 10.3% / -55.0% | 11.2% / -68.8% |
| ^HSI | vol window 120 | 9.5% / -64.1% | 9.2% / -32.9% | 11.0% / -49.0% | 12.1% / -63.2% |

PBO (CSCV, S = 16) over the 16 engine variants (4 L × 4 settings) per market, excess returns: ^GSPC 0.05, ^NDX 0.25, ^N225 0.17, ^GDAXI 0.09, ^FTSE 0.23, ^HSI 0.43. L mostly rescales the same bet, so this mainly says whether the choice among near-identical variants is stable.

## Real 2x ETFs vs the synthetic leverage used above (report only)

### QLD vs synthetic 2x QQQ (2007-06-22 → 2026-11-19)

|                                                     | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:----------------------------------------------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| QLD hold                                            | 22.7%  | 44.6% |                 0.65 | -83.1%  |                      4.4 | 16.8%            | 0.0%                       |
| Synthetic 2x QQQ (T-bill+1.5%, study model)         | 22.5%  | 44.8% |                 0.64 | -82.6%  |                      4.4 | 16.6%            | 0.0%                       |
| Synthetic 2x QQQ (T-bill + 0.95% fee)               | 23.1%  | 44.8% |                 0.66 | -82.5%  |                      4.4 | 17.2%            | 0.0%                       |
| QQQ hold                                            | 15.3%  | 22.4% |                 0.68 | -53.4%  |                      3.1 | 11.6%            | 0.0%                       |
| QLD inside engine (vol target 30%, max 1 unit = 2x) | 18.0%  | 27.0% |                 0.7  | -43.8%  |                      2.4 | 16.1%            | 0.0%                       |
| Engine L=1.5 on QQQ, synthetic financing            | 16.6%  | 23.3% |                 0.71 | -41.7%  |                      2.4 | 13.8%            | 0.0%                       |
| QLD inside engine (vol target 40%, max 1 unit = 2x) | 20.3%  | 31.0% |                 0.71 | -53.9%  |                      2.4 | 17.3%            | 0.0%                       |
| Engine L=2.0 on QQQ, synthetic financing            | 20.1%  | 31.1% |                 0.7  | -52.3%  |                      2.4 | 17.0%            | 0.0%                       |

- QLD minus Synthetic 2x QQQ (T-bill+1.5%, study model): tracking difference +0.21%/yr, tracking error 3.90%/yr

- QLD minus Synthetic 2x QQQ (T-bill + 0.95% fee): tracking difference -0.47%/yr, tracking error 3.90%/yr

### SSO vs synthetic 2x SPY (2007-06-22 → 2026-11-19)

|                                                     | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:----------------------------------------------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| SSO hold                                            | 13.6%  | 38.7% |                 0.49 | -84.7%  |                      6   | 7.3%             | 0.0%                       |
| Synthetic 2x SPY (T-bill+1.5%, study model)         | 13.5%  | 39.4% |                 0.48 | -84.4%  |                      6.1 | 7.0%             | 0.0%                       |
| Synthetic 2x SPY (T-bill + 0.95% fee)               | 14.1%  | 39.4% |                 0.49 | -84.3%  |                      6   | 7.6%             | 0.0%                       |
| SPY hold                                            | 10.4%  | 19.7% |                 0.52 | -55.2%  |                      4.9 | 6.8%             | 0.0%                       |
| SSO inside engine (vol target 30%, max 1 unit = 2x) | 13.4%  | 23.4% |                 0.59 | -46.5%  |                      3.6 | 10.7%            | 0.0%                       |
| Engine L=1.5 on SPY, synthetic financing            | 11.7%  | 19.1% |                 0.6  | -40.9%  |                      2.7 | 9.4%             | 0.0%                       |
| SSO inside engine (vol target 40%, max 1 unit = 2x) | 14.0%  | 25.3% |                 0.59 | -53.4%  |                      3.6 | 11.2%            | 0.0%                       |
| Engine L=2.0 on SPY, synthetic financing            | 13.9%  | 25.5% |                 0.58 | -51.7%  |                      3.5 | 11.2%            | 0.0%                       |

- SSO minus Synthetic 2x SPY (T-bill+1.5%, study model): tracking difference +0.17%/yr, tracking error 3.64%/yr

- SSO minus Synthetic 2x SPY (T-bill + 0.95% fee): tracking difference -0.45%/yr, tracking error 3.64%/yr

## Shipped 12-name universe (2015-03-31 → 2026-11-19, frozen P incl. 25% caps; T-bill on idle cash, T-bill + spread on borrowing)

|                            | CAGR   | Vol   |   Sharpe (ex T-bill) | MaxDD   |   Longest underwater (y) | Worst 10y CAGR   | Share of 10y windows < 0   |
|:---------------------------|:-------|:------|---------------------:|:--------|-------------------------:|:-----------------|:---------------------------|
| QQQ hold                   | 17.7%  | 22.1% |                 0.75 | -35.1%  |                      2   | 15.5%            | 0.0%                       |
| Frozen model L=1.0         | 23.8%  | 17.9% |                 1.16 | -21.8%  |                      1.4 | 23.7%            | 0.0%                       |
| Frozen model L=1.0, stress | 23.4%  | 17.9% |                 1.15 | -22.0%  |                      1.4 | 23.3%            | 0.0%                       |
| Frozen model L=1.5         | 34.1%  | 26.9% |                 1.15 | -31.7%  |                      1.4 | 34.0%            | 0.0%                       |
| Frozen model L=1.5, stress | 32.8%  | 26.9% |                 1.11 | -32.0%  |                      1.4 | 32.8%            | 0.0%                       |

Paired bootstrap: P(Sharpe L=1.5 ≤ L=1.0) = 1.000; P(MaxDD L=1.5 worse than QQQ) = 0.745. Selection bias (MATH.md §7) inflates both levels; only the L comparison is meaningful.


## Verdict (written after the 2026-11-20 run; numbers above are deterministic, seeded)

**No L passes.** L = 1.5 comes closest: under base assumptions it beats buy & hold on both CAGR and MaxDD in 5 of 6
markets including the Nikkei (fails the FTSE), and its worst 10-year CAGR is better than holding on the Nikkei and the
S&P. But the pooled Sharpe test fails (P = 0.095), and under stress financing (T-bill + 3%) and 10 bp it wins in only
3 markets (S&P, Nasdaq, Hang Seng; on the Nikkei its CAGR drops below holding, 7.6% vs 7.8%). L = 1.25 fails (a)
(4 of 6) and passes (b) only in base (P = 0.044; 0.25 under stress).
L = 2.0 fails everything that involves the Nikkei: −86% MaxDD vs −77% for holding, 34 years underwater.
L = 1.0 has the best risk-adjusted numbers (pooled P = 0.011) and the smallest drawdowns everywhere, but lower CAGR
than holding in 5 of 6 markets: it is a safer way to hold, not a higher-return one.

What is robust: the engine's drawdown control is real at every L ≤ 1.5 across six markets and five decades
(and survives a 1-day regime lag and vol windows 20/120). What is not: turning that into *more return than holding*
needs leverage whose financing cost eats the gain outside a strong uptrend; the Nasdaq result is the best case.
