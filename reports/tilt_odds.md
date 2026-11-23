# When to go heavier into certain stocks: decision odds, 2026-11-23

Rules written in tilt_odds.py before the run. Base = the live book (inverse-vol, fully invested).

|                                                                  |   P(arm grows faster) |   CAGR arm |   CAGR base |   Sharpe arm |   Sharpe base |   MaxDD arm |   MaxDD base |   P 1st half |   P 2nd half |
|:-----------------------------------------------------------------|----------------------:|-----------:|------------:|-------------:|--------------:|------------:|-------------:|-------------:|-------------:|
| ew: heavier in the volatile names | end-2014 list (decides)      |                 0.220 |      0.198 |       0.206 |        0.908 |         0.971 |      -0.369 |       -0.335 |        0.621 |        0.190 |
| trend: heavier in what has been rising | end-2014 list (decides) |                 0.840 |      0.220 |       0.206 |        1.015 |         0.971 |      -0.341 |       -0.335 |        0.761 |        0.782 |
| dip: heavier in what just fell | end-2014 list (decides)         |                 0.001 |      0.152 |       0.206 |        0.752 |         0.971 |      -0.379 |       -0.335 |        0.119 |        0.000 |
| ew: heavier in the volatile names | shipped list (reported)      |                 0.995 |      0.361 |       0.326 |        1.249 |         1.229 |      -0.443 |       -0.417 |        1.000 |        0.671 |
| trend: heavier in what has been rising | shipped list (reported) |                 0.501 |      0.326 |       0.326 |        1.204 |         1.229 |      -0.410 |       -0.417 |        0.550 |        0.434 |
| dip: heavier in what just fell | shipped list (reported)         |                 0.003 |      0.281 |       0.326 |        1.083 |         1.229 |      -0.445 |       -0.417 |        0.024 |        0.030 |

- Decision: move the live book to **trend: heavier in what has been rising**
