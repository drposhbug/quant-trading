# A neural network that refits every month: decision odds

Rules in mlp_odds.py. Variant: v1 baseline. Judged from 2022-01-01 on; 'live' = the current book (long-trend tilt).

|                             |   mlp: a neural network refitted every month | end-2014 list (decides) |   mlp: a neural network refitted every month | shipped list (reported) |
|:----------------------------|-----------------------------------------------------------------------:|-----------------------------------------------------------------------:|
| P vs live                   |                                                                  0.068 |                                                                  0.605 |
| P 1st half                  |                                                                  0.058 |                                                                  0.426 |
| P 2nd half                  |                                                                  0.203 |                                                                  0.722 |
| CAGR arm                    |                                                                  0.134 |                                                                  0.242 |
| CAGR live                   |                                                                  0.184 |                                                                  0.233 |
| MaxDD arm                   |                                                                 -0.376 |                                                                 -0.443 |
| MaxDD live                  |                                                                 -0.337 |                                                                 -0.407 |
| rank IC                     |                                                                 -0.047 |                                                                  0.038 |
| IC t                        |                                                                 -1.186 |                                                                  0.802 |
| whole window: P vs live     |                                                                  0.042 |                                                                  0.946 |
| whole window: P vs untilted |                                                                  0.045 |                                                                  0.949 |

- Decision: **the live tilt stays**: the network does not clear the bar
