# Options that like small moves, and selling at a target

Rules written in options_small_moves.py before the run. Model prices from the volatility indexes, 1990-01-02 to 2026-11-23. For the small-move trade the return is on the money at risk (the most it can lose); for the calls, on the money paid.

|                                                                                    |   trades |   average return |      t |   1st half |   2nd half |   share that made money |   worst |   best |
|:-----------------------------------------------------------------------------------|---------:|-----------------:|-------:|-----------:|-----------:|------------------------:|--------:|-------:|
| S&P 500: small-move trade, held to the end (decides)                               |  442.000 |            0.022 |  1.076 |      0.063 |     -0.019 |                   0.706 |  -1.000 |  0.751 |
| S&P 500: small-move trade, managed (half the money earned, or stopped at twice)    |  442.000 |           -0.009 | -0.530 |      0.027 |     -0.046 |                   0.762 |  -1.026 |  0.631 |
| S&P 500: call, sold at +50% or held                                                |  442.000 |           -0.092 | -2.511 |     -0.108 |     -0.077 |                   0.527 |  -1.000 |  1.583 |
| S&P 500: call, held to the end                                                     |  442.000 |            0.007 |  0.130 |     -0.052 |      0.066 |                   0.439 |  -1.000 |  4.160 |
| Nasdaq-100: small-move trade, held to the end                                      |  309.000 |           -0.112 | -3.600 |     -0.128 |     -0.096 |                   0.531 |  -1.000 |  0.755 |
| Nasdaq-100: small-move trade, managed (half the money earned, or stopped at twice) |  309.000 |           -0.121 | -4.334 |     -0.155 |     -0.088 |                   0.615 |  -1.041 |  0.588 |
| Nasdaq-100: call, sold at +50% or held                                             |  309.000 |            0.001 |  0.032 |     -0.047 |      0.049 |                   0.570 |  -1.000 |  1.318 |
| Nasdaq-100: call, held to the end                                                  |  309.000 |            0.128 |  1.735 |      0.004 |      0.250 |                   0.434 |  -1.000 |  4.424 |

- Verdict: **the small-move trade does not clear its bar** (needs an average above zero with t of 3 or more, above zero in both halves).
