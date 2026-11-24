# Options: cheap after a shock? Calls as leverage with a capped loss?

Rules written in options_study.py before the run. Index options priced from the volatility indexes; Nasdaq-100 from 2001-04-20, S&P 500 from 1990, to 2026-11-23.

## 1. Buying options after a shock

|                                                     |   trades |   average return on the money paid |       t |   1st half |   2nd half |   share that made money |   median |
|:----------------------------------------------------|---------:|-----------------------------------:|--------:|-----------:|-----------:|------------------------:|---------:|
| Nasdaq-100: straddle bought after a shock (decides) |   84.000 |                             -0.175 |  -2.615 |     -0.191 |     -0.158 |                   0.357 |   -0.306 |
| Nasdaq-100: straddle bought on any day              |  306.000 |                             -0.158 |  -4.353 |     -0.202 |     -0.114 |                   0.353 |   -0.248 |
| Nasdaq-100: call bought after a shock               |   84.000 |                             -0.036 |  -0.284 |     -0.120 |      0.049 |                   0.381 |   -0.643 |
| Nasdaq-100: call bought on any day                  |  306.000 |                              0.048 |   0.689 |     -0.069 |      0.164 |                   0.412 |   -0.471 |
| S&P 500: straddle bought after a shock              |  128.000 |                             -0.261 |  -5.304 |     -0.302 |     -0.221 |                   0.305 |   -0.405 |
| S&P 500: straddle bought on any day                 |  439.000 |                             -0.270 | -10.197 |     -0.317 |     -0.222 |                   0.262 |   -0.375 |
| S&P 500: call bought after a shock                  |  128.000 |                             -0.043 |  -0.475 |     -0.107 |      0.022 |                   0.422 |   -0.291 |
| S&P 500: call bought on any day                     |  439.000 |                             -0.096 |  -2.000 |     -0.164 |     -0.029 |                   0.394 |   -0.399 |

- Verdict: **no reliable mispricing after a shock**.

### The other side of the same trades (a reading added after the first run; no bar)

- Nasdaq-100: selling that straddle every 21 sessions kept 11% of the money received on average and won 60% of the time. Its three worst: 2008-09-26 -265%, 2026-04-10 -225%, 2024-07-08 -204%. A loss of -300% means paying out four times what was received.
- S&P 500: selling that straddle every 21 sessions kept 22% of the money received on average and won 71% of the time. Its three worst: 2008-09-25 -275%, 2018-09-28 -246%, 2001-08-17 -156%. A loss of -300% means paying out four times what was received.

## 2. Calls as leverage with a capped loss (Nasdaq-100, steps of 21 sessions)

|                                          |   P vs holding |   growth a year |   worst fall (21-session steps) |   worst 21 sessions |   best 21 sessions |
|:-----------------------------------------|---------------:|----------------:|--------------------------------:|--------------------:|-------------------:|
| hold the index                           |        nan     |           0.110 |                          -0.571 |              -0.300 |              0.199 |
| 99% index + 1% in calls each 21 sessions |          0.348 |           0.107 |                          -0.615 |              -0.307 |              0.219 |
| 98% index + 2% in calls                  |          0.303 |           0.102 |                          -0.667 |              -0.314 |              0.266 |
| borrow a quarter (B3.0)                  |          0.820 |           0.121 |                          -0.672 |              -0.376 |              0.249 |

- Verdict for 1% a month in calls: **does not clear its bar**.

## 3. "If we had bought options on Friday"

- The last one, bought at the close on 2026-11-20 with the Nasdaq-100's volatility index at 45%: the index moved +6.9% by Monday's close and the call was worth +59% more.
- The same purchase on each of the last 225 Fridays: on average +1.4% by Monday's close; it lost money on 49% of them; best +75%, worst -46%.
- The three best: 2026-09-18 +75%, 2025-05-09 +67%, 2026-11-20 +59%. The three worst: 2025-03-07 -46%, 2025-01-24 -45%, 2022-06-10 -38%.
