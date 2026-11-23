# A neural network that refits every month: decision odds, 2026-11-23

Rules written in mlp_odds.py before the run. 'live' = the current book (long-trend tilt).

|                                                                      |   P vs live |   P 1st half |   P 2nd half |   P vs untilted |   CAGR arm |   CAGR live |   MaxDD arm |   MaxDD live |   rank IC |   IC t | from       |
|:---------------------------------------------------------------------|------------:|-------------:|-------------:|----------------:|-----------:|------------:|------------:|-------------:|----------:|-------:|:-----------|
| mlp: a neural network refitted every month | end-2014 list (decides) |       0.066 |        0.411 |        0.037 |           0.091 |      0.208 |       0.238 |      -0.375 |       -0.341 |    -0.023 | -0.758 | 2016-01-28 |
| mlp: a neural network refitted every month | shipped list (reported) |       0.938 |        0.972 |        0.623 |           0.954 |      0.378 |       0.342 |      -0.435 |       -0.410 |     0.048 |  1.492 | 2016-01-28 |

- Decision: **the live tilt stays**: the network does not clear the bar
