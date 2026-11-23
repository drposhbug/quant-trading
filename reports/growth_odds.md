# Decision odds, 2026-11-22

Rules written in growth_odds.py before the run.

## A. 90% book + 10% gold (arm) against 100% book

|                                    |   years |   P(arm grows faster) |   P(arm Sharpe higher) |   CAGR arm |   CAGR base |   Sharpe arm |   Sharpe base |   MaxDD arm |   MaxDD base |
|:-----------------------------------|--------:|----------------------:|-----------------------:|-----------:|------------:|-------------:|--------------:|------------:|-------------:|
| QQQ 2005-2026 (decides)            |  21.702 |                 0.394 |                  0.995 |      0.148 |       0.150 |        0.797 |         0.749 |      -0.494 |       -0.534 |
| end-2014 list, live book (decides) |  11.623 |                 0.197 |                  0.969 |      0.198 |       0.206 |        1.016 |         0.971 |      -0.312 |       -0.335 |
| shipped list, live book (reported) |  11.623 |                 0.029 |                  0.955 |      0.306 |       0.326 |        1.265 |         1.229 |      -0.388 |       -0.417 |

- Decision: **no gold sleeve**

## B. Fully invested (arm) against the frozen engine with T-bills on idle cash

|                          |   years |   P(arm grows faster) |   P(arm Sharpe higher) |   CAGR arm |   CAGR base |   Sharpe arm |   Sharpe base |   MaxDD arm |   MaxDD base |
|:-------------------------|--------:|----------------------:|-----------------------:|-----------:|------------:|-------------:|--------------:|------------:|-------------:|
| ^NDX 1986-2026 (decides) |  40.135 |                 0.746 |                  0.009 |      0.140 |       0.125 |        0.634 |         0.823 |      -0.829 |       -0.345 |
| end-2014 list (decides)  |  11.623 |                 0.982 |                  0.455 |      0.206 |       0.156 |        0.971 |         0.988 |      -0.335 |       -0.222 |
| shipped list (reported)  |  11.623 |                 0.987 |                  0.373 |      0.326 |       0.237 |        1.229 |         1.279 |      -0.417 |       -0.218 |

- Decision: **keep the fully invested override**
