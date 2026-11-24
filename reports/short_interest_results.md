# Do heavily shorted stocks do worse?

Rules written in short_interest_study.py before the run. 503 companies, figures published 2018-01-10 to 2026-11-10, 2230 trading days with a ranking; about 427 stocks ranked on a typical day.

|                                                                        |    days |   daily mean, bp |   a year |     t |   1st half, bp |   2nd half, bp |   share of days up |
|:-----------------------------------------------------------------------|--------:|-----------------:|---------:|------:|---------------:|---------------:|-------------------:|
| days to cover: least shorted minus most shorted (decides)              | 2228.00 |             0.49 |     0.01 |  0.80 |          -0.03 |           1.00 |               0.53 |
| change in shares short: least increased minus most increased (reading) | 2219.00 |            -0.06 |    -0.00 | -0.13 |          -0.27 |           0.16 |               0.50 |

- Verdict: **no pattern** (real needs t of 3 or more and the same sign in both halves; a hint needs 2).
