# After a stock opens far below its last close, does it keep falling?

Rules written in news_gap_study.py before the run. S&P 500 members by date, dead companies included, 2017-08-04 to 2026-11-23. Returns are against the average index member, from the open of the event day.

| event                    |   events |   days held |   daily mean, bp |     t |   1st half, bp |   2nd half, bp |   5 sessions, per event |   fell further |
|:-------------------------|---------:|------------:|-----------------:|------:|---------------:|---------------:|------------------------:|---------------:|
| opens more than 10% down |  1209.00 |     1422.00 |           -15.01 | -1.53 |         -21.02 |          -9.00 |                   -0.01 |           0.50 |
| opens more than 5% down  |  6328.00 |     2207.00 |             3.79 |  0.95 |           0.39 |           7.19 |                    0.00 |           0.48 |
| opens more than 10% up   |   970.00 |     1458.00 |           -24.46 | -3.27 |         -44.41 |          -4.50 |                   -0.01 |           0.56 |

- Verdict for the 10%-down event: **no pattern** (real needs t of -3 or lower and a negative mean in both halves; a hint needs -2).
