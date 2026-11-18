# Candlestick pattern tests

Universe: TSLA, SPCX, AAPL, MSFT, NVDA, GOOGL, AMZN, META, AVGO, TSM, AMD, ORCL, ANT. Daily candles 2014 to today (yfinance, split/dividend adjusted). 39 tests (13 patterns × 3 horizons); Holm-corrected p-values.

excess_bp = average forward return after the pattern minus that stock's average return over the same horizon, in basis points (100 bp = 1%).

| Pattern                     |   h |    n |   excess_bp |   hit |     t |   pre2021_bp |   post2021_bp |   t_post |      p |   p_holm | same_sign_both_halves   | verdict   |
|:----------------------------|----:|-----:|------------:|------:|------:|-------------:|--------------:|---------:|-------:|---------:|:------------------------|:----------|
| Doji                        |   1 | 3638 |         0.8 | 0.497 |  0.22 |          3.7 |          -2.7 |    -0.36 | 0.8258 |   1      | False                   | noise     |
| Hammer (after down 5d)      |   1 |  488 |       -21.7 | 0.469 | -0.48 |        -30.7 |          -9.1 |     0.25 | 0.6332 |   1      | True                    | noise     |
| Shooting star (after up 5d) |   1 |  506 |        -0.9 | 0.508 | -0.13 |         11.7 |         -17.5 |    -0.91 | 0.8984 |   1      | False                   | noise     |
| Bullish engulfing           |   1 | 1185 |        -7.7 | 0.472 |  0.22 |        -13.5 |          -0.4 |     1.21 | 0.8232 |   1      | True                    | noise     |
| Bearish engulfing           |   1 | 1464 |        20.6 | 0.518 |  2.07 |         10.3 |          34.1 |     1.81 | 0.0383 |   1      | True                    | noise     |
| Bull marubozu               |   1 |  702 |        -2.7 | 0.464 | -0.77 |          8.8 |         -18.3 |    -1.26 | 0.4438 |   1      | False                   | noise     |
| Bear marubozu               |   1 |  572 |        38.5 | 0.57  |  2.47 |         40.9 |          35.8 |     1.71 | 0.0133 |   0.5204 | True                    | noise     |
| Three white soldiers        |   1 | 3139 |       -14.2 | 0.469 | -1.4  |         -7.7 |         -21.9 |    -1.6  | 0.1622 |   1      | True                    | noise     |
| Three black crows           |   1 | 2362 |        10.9 | 0.524 |  0.38 |         20.2 |           2.1 |    -0.67 | 0.7027 |   1      | True                    | noise     |
| Inside bar                  |   1 | 4215 |        -3.4 | 0.488 | -0.39 |         -5.5 |          -0.8 |    -0.17 | 0.697  |   1      | True                    | noise     |
| Outside bar                 |   1 | 3019 |         0.6 | 0.503 |  0.56 |         -6.7 |           9   |     1.63 | 0.5731 |   1      | False                   | noise     |
| Gap up > 1%                 |   1 | 1815 |        -0.3 | 0.496 |  0.59 |          1.5 |          -1.8 |    -0.6  | 0.5574 |   1      | False                   | noise     |
| Gap down > 1%               |   1 | 1579 |         4   | 0.511 | -1.19 |         17.2 |          -6.8 |    -0.98 | 0.2346 |   1      | False                   | noise     |
| Doji                        |   5 | 3634 |         6.1 | 0.499 |  0.55 |          1.1 |          12.2 |     0.31 | 0.5793 |   1      | True                    | noise     |
| Hammer (after down 5d)      |   5 |  487 |         1.5 | 0.532 |  0.51 |         -0.8 |           4.6 |     0.31 | 0.6099 |   1      | False                   | noise     |
| Shooting star (after up 5d) |   5 |  503 |       -19.8 | 0.469 | -0.34 |        -33.5 |          -1.6 |     0.65 | 0.7358 |   1      | True                    | noise     |
| Bullish engulfing           |   5 | 1185 |         2.5 | 0.505 |  0.5  |         10.1 |          -7.3 |     0.37 | 0.619  |   1      | False                   | noise     |
| Bearish engulfing           |   5 | 1462 |        43.9 | 0.523 |  1.41 |         29.8 |          62.3 |     2.16 | 0.1592 |   1      | True                    | noise     |
| Bull marubozu               |   5 |  702 |       -36   | 0.489 | -1.51 |          5.9 |         -92.4 |    -2.02 | 0.1301 |   1      | False                   | noise     |
| Bear marubozu               |   5 |  571 |        34.9 | 0.515 |  0.75 |         76.7 |         -11.7 |    -0.65 | 0.4512 |   1      | False                   | noise     |
| Three white soldiers        |   5 | 3137 |       -24.9 | 0.481 | -2.28 |        -28.6 |         -20.5 |    -1.44 | 0.0225 |   0.8545 | True                    | noise     |
| Three black crows           |   5 | 2356 |        10.7 | 0.488 |  0.96 |         39.4 |         -16.9 |    -0.76 | 0.3362 |   1      | False                   | noise     |
| Inside bar                  |   5 | 4213 |        -6.5 | 0.497 | -0.67 |         -3.4 |         -10.4 |    -0.69 | 0.5002 |   1      | True                    | noise     |
| Outside bar                 |   5 | 3016 |         3.7 | 0.506 | -0.08 |         -6.6 |          15.9 |     0.77 | 0.9347 |   1      | False                   | noise     |
| Gap up > 1%                 |   5 | 1814 |         7.8 | 0.503 |  0.64 |         33.7 |         -14.8 |    -0.6  | 0.5219 |   1      | False                   | noise     |
| Gap down > 1%               |   5 | 1574 |        41.4 | 0.514 |  0.44 |         31.3 |          49.8 |     0.62 | 0.6605 |   1      | True                    | noise     |
| Doji                        |  10 | 3630 |        -1.5 | 0.496 |  0    |          3.4 |          -7.3 |    -0.45 | 0.9983 |   1      | False                   | noise     |
| Hammer (after down 5d)      |  10 |  486 |        20.3 | 0.537 |  0.33 |         56.1 |         -30.3 |    -0.55 | 0.7419 |   1      | False                   | noise     |
| Shooting star (after up 5d) |  10 |  502 |       -14   | 0.488 | -0.3  |        -31.5 |           9.3 |     0.8  | 0.7648 |   1      | False                   | noise     |
| Bullish engulfing           |  10 | 1184 |        -7.2 | 0.486 |  0.46 |         29.3 |         -54.2 |    -0.11 | 0.6432 |   1      | False                   | noise     |
| Bearish engulfing           |  10 | 1458 |        27.7 | 0.511 |  0.06 |         28.3 |          27   |     0.74 | 0.9549 |   1      | True                    | noise     |
| Bull marubozu               |  10 |  700 |       -39.1 | 0.493 | -1.12 |        -32   |         -48.7 |    -0.68 | 0.263  |   1      | True                    | noise     |
| Bear marubozu               |  10 |  569 |        40.6 | 0.511 |  0.37 |         63   |          15.4 |    -0.22 | 0.7123 |   1      | True                    | noise     |
| Three white soldiers        |  10 | 3131 |       -16   | 0.478 | -0.87 |        -42.9 |          16.4 |     0.74 | 0.3832 |   1      | False                   | noise     |
| Three black crows           |  10 | 2354 |        -1.1 | 0.489 | -0.27 |         46.3 |         -46.7 |    -1.41 | 0.7896 |   1      | False                   | noise     |
| Inside bar                  |  10 | 4205 |        -3.1 | 0.496 |  0.17 |          2.3 |         -10   |    -0.73 | 0.8647 |   1      | False                   | noise     |
| Outside bar                 |  10 | 3013 |        -6.7 | 0.491 | -0.27 |         -1.8 |         -12.4 |    -0.09 | 0.7865 |   1      | True                    | noise     |
| Gap up > 1%                 |  10 | 1807 |        27.9 | 0.499 |  1.26 |         51.8 |           6.9 |    -0.18 | 0.2069 |   1      | True                    | noise     |
| Gap down > 1%               |  10 | 1567 |        22.9 | 0.516 |  0.32 |         23.1 |          22.7 |     0.22 | 0.7465 |   1      | True                    | noise     |

## Verdict

0 of 39 pattern/horizon combinations survive multiple-testing correction with a consistent sign in both halves of the sample.
