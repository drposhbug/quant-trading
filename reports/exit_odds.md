# Selling rules: decision odds, 2026-11-23

Rules written in exit_odds.py before the run. 'live' = the current book.

|                                         |   P vs live |   P 1st half |   P 2nd half |   CAGR arm |   CAGR live |   MaxDD arm |   MaxDD live |   Sharpe arm |   Sharpe live |   avg invested |
|:----------------------------------------|------------:|-------------:|-------------:|-----------:|------------:|------------:|-------------:|-------------:|--------------:|---------------:|
| stop 20% | end-2014 list (decides)      |       0.009 |        0.000 |        0.190 |      0.165 |       0.220 |      -0.293 |       -0.341 |        0.950 |         1.015 |          0.895 |
| stop 10% | end-2014 list (decides)      |       0.003 |        0.001 |        0.215 |      0.127 |       0.220 |      -0.166 |       -0.341 |        0.937 |         1.015 |          0.709 |
| stretch trim | end-2014 list (decides)  |       0.114 |        0.292 |        0.128 |      0.209 |       0.220 |      -0.336 |       -0.341 |        1.011 |         1.015 |          0.945 |
| jump trim | end-2014 list (decides)     |       0.064 |        0.088 |        0.213 |      0.216 |       0.220 |      -0.341 |       -0.341 |        1.007 |         1.015 |          0.994 |
| new-high trim | end-2014 list (decides) |       0.017 |        0.052 |        0.067 |      0.189 |       0.220 |      -0.308 |       -0.341 |        0.970 |         1.015 |          0.804 |
| stop 20% | shipped list (reported)      |       0.002 |        0.001 |        0.054 |      0.226 |       0.326 |      -0.320 |       -0.410 |        1.097 |         1.204 |          0.878 |
| stop 10% | shipped list (reported)      |       0.001 |        0.000 |        0.086 |      0.164 |       0.326 |      -0.201 |       -0.410 |        1.046 |         1.204 |          0.692 |
| stretch trim | shipped list (reported)  |       0.012 |        0.018 |        0.173 |      0.284 |       0.326 |      -0.397 |       -0.410 |        1.173 |         1.204 |          0.894 |
| jump trim | shipped list (reported)     |       0.019 |        0.074 |        0.064 |      0.317 |       0.326 |      -0.409 |       -0.410 |        1.191 |         1.204 |          0.991 |
| new-high trim | shipped list (reported) |       0.004 |        0.004 |        0.112 |      0.275 |       0.326 |      -0.397 |       -0.410 |        1.133 |         1.204 |          0.808 |

- Decision: **no selling rule is added**: none clears the bar

## This dip, shipped list (reported)

|               |   6 Oct to 20 Nov (the fall) |   6 Oct to 23 Nov (with the rebound) |   invested on 20 Nov |
|:--------------|-----------------------------:|-------------------------------------:|---------------------:|
| live book     |                       -0.196 |                               -0.152 |                0.987 |
| stop 20%      |                       -0.155 |                               -0.146 |                0.533 |
| stop 10%      |                       -0.069 |                               -0.065 |                0.250 |
| stretch trim  |                       -0.181 |                               -0.137 |                0.987 |
| jump trim     |                       -0.196 |                               -0.152 |                0.987 |
| new-high trim |                       -0.180 |                               -0.135 |                0.987 |
