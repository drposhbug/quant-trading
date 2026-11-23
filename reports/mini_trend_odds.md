# Mini trends and a learning rule: decision odds, 2026-11-23

Rules written in mini_trend_odds.py before the run. 'live' = the current book (long-trend tilt).

|                                       |   P vs live |   P 1st half |   P 2nd half |   P last 3 yrs |   P vs untilted |   CAGR arm |   CAGR live |   MaxDD arm |   MaxDD live |   turnover/yr |
|:--------------------------------------|------------:|-------------:|-------------:|---------------:|----------------:|-----------:|------------:|------------:|-------------:|--------------:|
| mini 5-day | end-2014 list (decides)  |       0.004 |        0.002 |        0.251 |          0.263 |           0.013 |      0.169 |       0.220 |      -0.379 |       -0.341 |        32.756 |
| mini 10-day | end-2014 list (decides) |       0.013 |        0.042 |        0.071 |          0.064 |           0.034 |      0.179 |       0.220 |      -0.369 |       -0.341 |        23.600 |
| mini 21-day | end-2014 list (decides) |       0.070 |        0.136 |        0.127 |          0.177 |           0.222 |      0.195 |       0.220 |      -0.363 |       -0.341 |        16.869 |
| mini 63-day | end-2014 list (decides) |       0.017 |        0.229 |        0.006 |          0.170 |           0.183 |      0.192 |       0.220 |      -0.398 |       -0.341 |        11.001 |
| learn | end-2014 list (decides)       |       0.004 |        0.170 |        0.004 |          0.017 |           0.086 |      0.182 |       0.220 |      -0.377 |       -0.341 |        18.182 |
| mini 5-day | shipped list (reported)  |       0.001 |        0.001 |        0.060 |          0.019 |           0.000 |      0.260 |       0.326 |      -0.442 |       -0.410 |        33.513 |
| mini 10-day | shipped list (reported) |       0.035 |        0.030 |        0.170 |          0.060 |           0.020 |      0.290 |       0.326 |      -0.434 |       -0.410 |        24.542 |
| mini 21-day | shipped list (reported) |       0.059 |        0.179 |        0.090 |          0.160 |           0.049 |      0.297 |       0.326 |      -0.463 |       -0.410 |        18.026 |
| mini 63-day | shipped list (reported) |       0.279 |        0.774 |        0.110 |          0.279 |           0.292 |      0.318 |       0.326 |      -0.457 |       -0.410 |        11.502 |
| learn | shipped list (reported)       |       0.252 |        0.019 |        0.697 |          0.739 |           0.292 |      0.316 |       0.326 |      -0.443 |       -0.410 |        17.419 |

- Decision: **the live tilt stays**: no arm clears the bar
- Share of days the learning rule held each trend length: end-2014 list: long 36%, 21-day 25%, 5-day 21%, 63-day 18%; shipped list: long 34%, 63-day 33%, 5-day 18%, 21-day 14%
