# Decision odds, 2026-11-22

Rules written in growth_odds.py before the run.

## A. 90% book + 10% gold (arm) against 100% book

|                                    |   years |   P(arm grows faster) |   P(arm Sharpe higher) |   CAGR arm |   CAGR base |   Sharpe arm |   Sharpe base |   MaxDD arm |   MaxDD base |
|:-----------------------------------|--------:|----------------------:|-----------------------:|-----------:|------------:|-------------:|--------------:|------------:|-------------:|
| QQQ 2005-2026 (decides)            |  21.698 |                 0.414 |                  0.991 |      0.145 |       0.146 |        0.784 |         0.736 |      -0.494 |       -0.534 |
| end-2014 list, live book (decides) |  11.623 |                 0.201 |                  0.970 |      0.198 |       0.206 |        1.016 |         0.971 |      -0.312 |       -0.335 |
| shipped list, live book (reported) |  11.623 |                 0.031 |                  0.964 |      0.306 |       0.326 |        1.265 |         1.229 |      -0.388 |       -0.417 |

- Decision: **no gold sleeve**

## B. Fully invested (arm) against the frozen engine with T-bills on idle cash

|                          |   years |   P(arm grows faster) |   P(arm Sharpe higher) |   CAGR arm |   CAGR base |   Sharpe arm |   Sharpe base |   MaxDD arm |   MaxDD base |
|:-------------------------|--------:|----------------------:|-----------------------:|-----------:|------------:|-------------:|--------------:|------------:|-------------:|
| ^NDX 1986-2026 (decides) |  40.131 |                 0.722 |                  0.017 |      0.138 |       0.125 |        0.628 |         0.819 |      -0.829 |       -0.345 |
| end-2014 list (decides)  |  11.623 |                 0.972 |                  0.454 |      0.206 |       0.156 |        0.971 |         0.988 |      -0.335 |       -0.222 |
| shipped list (reported)  |  11.623 |                 0.990 |                  0.380 |      0.326 |       0.237 |        1.229 |         1.279 |      -0.417 |       -0.218 |

- Decision: **keep the fully invested override**
