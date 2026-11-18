# Candlestick pattern tests

Universe: TSLA, SPCX, AAPL, MSFT, NVDA, GOOGL, AMZN, META. Daily candles 2014 to today (yfinance, split/dividend adjusted). 39 tests (13 patterns × 3 horizons); Holm-corrected p-values.

excess_bp = average forward return after the pattern minus that stock's average return over the same horizon, in basis points (100 bp = 1%).

| Pattern                     |   h |    n |   excess_bp |   hit |     t |   pre2021_bp |   post2021_bp |   t_post |      p |   p_holm | same_sign_both_halves   | verdict              |
|:----------------------------|----:|-----:|------------:|------:|------:|-------------:|--------------:|---------:|-------:|---------:|:------------------------|:---------------------|
| Doji                        |   1 | 2353 |        -3.3 | 0.495 | -0.66 |         -2.2 |          -4.6 |    -0.62 | 0.5104 |   1      | True                    | noise                |
| Hammer (after down 5d)      |   1 |  325 |       -14.5 | 0.468 | -1.14 |        -14.4 |         -14.7 |    -0.63 | 0.2557 |   1      | True                    | noise                |
| Shooting star (after up 5d) |   1 |  309 |         5   | 0.518 |  0.4  |         15.7 |          -9.5 |    -0.52 | 0.6903 |   1      | False                   | noise                |
| Bullish engulfing           |   1 |  755 |        -5   | 0.464 | -0.59 |        -12.4 |           4.3 |     0.32 | 0.5574 |   1      | False                   | noise                |
| Bearish engulfing           |   1 |  927 |        19   | 0.506 |  2.2  |         11   |          28.8 |     2.07 | 0.0278 |   0.9722 | True                    | noise                |
| Bull marubozu               |   1 |  484 |         6.2 | 0.471 |  0.65 |         24   |         -16.9 |    -1.06 | 0.5184 |   1      | False                   | noise                |
| Bear marubozu               |   1 |  333 |        50.6 | 0.574 |  3.36 |         57.5 |          43   |     2.11 | 0.0008 |   0.0305 | True                    | SIGNIFICANT + stable |
| Three white soldiers        |   1 | 2048 |       -15   | 0.467 | -3.06 |         -8.4 |         -22.8 |    -2.8  | 0.0022 |   0.0835 | True                    | noise                |
| Three black crows           |   1 | 1502 |        11.1 | 0.527 |  1.62 |         21.6 |           0.8 |     0.08 | 0.1044 |   1      | True                    | noise                |
| Inside bar                  |   1 | 2694 |        -2.9 | 0.494 | -0.64 |         -3.2 |          -2.5 |    -0.35 | 0.524  |   1      | True                    | noise                |
| Outside bar                 |   1 | 1926 |         6.7 | 0.515 |  1.11 |          0.3 |          14.1 |     1.5  | 0.2654 |   1      | True                    | noise                |
| Gap up > 1%                 |   1 | 1052 |        -6.6 | 0.487 | -0.7  |         -1.8 |         -11.1 |    -0.81 | 0.4818 |   1      | True                    | noise                |
| Gap down > 1%               |   1 |  914 |         3.5 | 0.521 |  0.29 |         18.3 |          -8.1 |    -0.54 | 0.7702 |   1      | False                   | noise                |
| Doji                        |   5 | 2351 |       -10.1 | 0.491 | -0.92 |         -8.7 |         -11.7 |    -0.7  | 0.3571 |   1      | True                    | noise                |
| Hammer (after down 5d)      |   5 |  325 |        37.6 | 0.566 |  1.33 |         21.3 |          65.4 |     1.24 | 0.184  |   1      | True                    | noise                |
| Shooting star (after up 5d) |   5 |  307 |       -38.3 | 0.463 | -1.31 |        -54.4 |         -16   |    -0.34 | 0.1893 |   1      | True                    | noise                |
| Bullish engulfing           |   5 |  755 |        -4.5 | 0.502 | -0.26 |         -0.9 |          -9.1 |    -0.3  | 0.7939 |   1      | True                    | noise                |
| Bearish engulfing           |   5 |  926 |        46.3 | 0.526 |  2.67 |         44.7 |          48.3 |     1.74 | 0.0076 |   0.2796 | True                    | noise                |
| Bull marubozu               |   5 |  484 |       -39.6 | 0.494 | -1.94 |          9.3 |        -102.9 |    -2.99 | 0.052  |   1      | False                   | noise                |
| Bear marubozu               |   5 |  332 |        59   | 0.548 |  1.92 |        124.9 |         -13.7 |    -0.3  | 0.0547 |   1      | False                   | noise                |
| Three white soldiers        |   5 | 2047 |       -26.1 | 0.487 | -2.42 |        -22.1 |         -30.7 |    -1.68 | 0.0156 |   0.5599 | True                    | noise                |
| Three black crows           |   5 | 1498 |        26.6 | 0.497 |  1.71 |         45.1 |           8.3 |     0.36 | 0.0876 |   1      | True                    | noise                |
| Inside bar                  |   5 | 2692 |        -6.1 | 0.502 | -0.62 |          6   |         -21.6 |    -1.37 | 0.5349 |   1      | False                   | noise                |
| Outside bar                 |   5 | 1923 |        11.6 | 0.508 |  0.95 |          1.7 |          23.2 |     1.17 | 0.3437 |   1      | True                    | noise                |
| Gap up > 1%                 |   5 | 1051 |        29.9 | 0.526 |  1.49 |         50.1 |          10.6 |     0.38 | 0.1365 |   1      | True                    | noise                |
| Gap down > 1%               |   5 |  913 |        49.5 | 0.519 |  2.08 |         52.2 |          47.3 |     1.5  | 0.0377 |   1      | True                    | noise                |
| Doji                        |  10 | 2348 |        -9.8 | 0.493 | -0.64 |          1.2 |         -22.9 |    -0.95 | 0.5198 |   1      | False                   | noise                |
| Hammer (after down 5d)      |  10 |  325 |        30.4 | 0.554 |  0.72 |         55   |         -11.7 |    -0.15 | 0.4732 |   1      | False                   | noise                |
| Shooting star (after up 5d) |  10 |  306 |       -29   | 0.487 | -0.71 |        -34.9 |         -20.9 |    -0.3  | 0.4769 |   1      | True                    | noise                |
| Bullish engulfing           |  10 |  754 |        -9.5 | 0.499 | -0.36 |          8.3 |         -31.8 |    -0.68 | 0.7208 |   1      | False                   | noise                |
| Bearish engulfing           |  10 |  922 |        33.6 | 0.517 |  1.42 |         42.3 |          22.8 |     0.62 | 0.155  |   1      | True                    | noise                |
| Bull marubozu               |  10 |  482 |       -59.5 | 0.481 | -1.91 |        -53.8 |         -66.9 |    -1.26 | 0.0557 |   1      | True                    | noise                |
| Bear marubozu               |  10 |  331 |        80.5 | 0.541 |  1.89 |        111.7 |          46   |     0.68 | 0.0583 |   1      | True                    | noise                |
| Three white soldiers        |  10 | 2043 |       -30.8 | 0.475 | -1.99 |        -29   |         -33   |    -1.23 | 0.0468 |   1      | True                    | noise                |
| Three black crows           |  10 | 1497 |        11.5 | 0.502 |  0.52 |         57.4 |         -33.8 |    -1.01 | 0.5999 |   1      | False                   | noise                |
| Inside bar                  |  10 | 2686 |        -5.1 | 0.503 | -0.36 |          8.4 |         -22.3 |    -1    | 0.7178 |   1      | False                   | noise                |
| Outside bar                 |  10 | 1920 |        -6.8 | 0.491 | -0.41 |         12.6 |         -29.6 |    -1.1  | 0.6841 |   1      | False                   | noise                |
| Gap up > 1%                 |  10 | 1048 |        24.3 | 0.498 |  0.84 |         52.9 |          -3.1 |    -0.08 | 0.3992 |   1      | False                   | noise                |
| Gap down > 1%               |  10 |  909 |        25.8 | 0.521 |  0.81 |         31.5 |          21.4 |     0.5  | 0.4203 |   1      | True                    | noise                |

## Verdict

1 of 39 pattern/horizon combinations survive multiple-testing correction with a consistent sign in both halves of the sample.
