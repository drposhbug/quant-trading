# Does a level that has held before hold again?

Rules written in support_study.py before the run. S&P 500 members without Tesla, 2010-01-19 to 2026-10-20.

|               |      dips |     days |   up a month later |   median return |   mean vs market |   median vs market |   fell 10%+ on the way |
|:--------------|----------:|---------:|-------------------:|----------------:|-----------------:|-------------------:|-----------------------:|
| held 0 times  | 48872.000 | 3982.000 |              0.580 |           0.017 |            0.001 |             -0.001 |                  0.185 |
| held 1 times  | 14115.000 | 3146.000 |              0.577 |           0.017 |            0.002 |             -0.000 |                  0.191 |
| held 2 times  |  3661.000 | 1736.000 |              0.550 |           0.011 |            0.001 |             -0.003 |                  0.224 |
| held 3+ times |   877.000 |  654.000 |              0.542 |           0.010 |           -0.006 |             -0.004 |                  0.237 |

- Levels that held twice or more against no history: -0.31% a month, t = -1.6. 2010-2018: -0.46% (t = -1.6); 2019-2026: -0.23% (t = -0.9).
- Verdict: **does not clear the bar**

## Tesla alone (the stock that suggested the idea)

|              |   dips |   days |   up a month later |   median return |   mean vs market |   median vs market |   fell 10%+ on the way |
|:-------------|-------:|-------:|-------------------:|----------------:|-----------------:|-------------------:|-----------------------:|
| held 0 times | 71.000 | 71.000 |              0.521 |           0.006 |            0.011 |             -0.007 |                  0.465 |
| held 1 times | 31.000 | 31.000 |              0.452 |          -0.024 |           -0.005 |             -0.029 |                  0.419 |
| held 2 times |  4.000 |  4.000 |              0.250 |          -0.120 |           -0.117 |             -0.191 |                  0.750 |
