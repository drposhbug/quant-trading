# Calculated risk: borrowing modestly, and more in calm times than after shocks

Rules written in managed_exposure_odds.py before the run. P = share of simulated histories in which the arm ends with more money than the current rule at 1x.

|                                                                       |   P base |   P 1st half |   P 2nd half |   P stress |   growth a year |   worst fall |
|:----------------------------------------------------------------------|---------:|-------------:|-------------:|-----------:|----------------:|-------------:|
| 1x (the current rule) | Nasdaq-100 since 1986 (decides)               |  nan     |      nan     |      nan     |    nan     |           0.136 |       -0.829 |
| steady 1.25x | Nasdaq-100 since 1986 (decides)                        |    0.837 |        0.498 |        0.956 |      0.716 |           0.148 |       -0.905 |
| steady 1.5x | Nasdaq-100 since 1986 (decides)                         |    0.788 |        0.432 |        0.941 |      0.646 |           0.154 |       -0.949 |
| 1.25x calm / 0.625x after a shock | Nasdaq-100 since 1986 (decides)   |    0.345 |        0.192 |        0.678 |      0.212 |           0.130 |       -0.897 |
| 1.5x calm / 0.75x after a shock | Nasdaq-100 since 1986 (decides)     |    0.562 |        0.240 |        0.923 |      0.384 |           0.139 |       -0.942 |
| 1x calm / 0.5x after a shock (B2.2) | Nasdaq-100 since 1986 (decides) |    0.107 |        0.179 |        0.159 |      0.089 |           0.118 |       -0.823 |
| 1x (the current rule) | end-2014 list (decides)                       |  nan     |      nan     |      nan     |    nan     |           0.220 |       -0.341 |
| steady 1.25x | end-2014 list (decides)                                |    0.986 |        0.976 |        0.891 |      0.970 |           0.261 |       -0.415 |
| steady 1.5x | end-2014 list (decides)                                 |    0.981 |        0.972 |        0.877 |      0.961 |           0.299 |       -0.483 |
| 1.25x calm / 0.625x after a shock | end-2014 list (decides)           |    0.697 |        0.624 |        0.664 |      0.617 |           0.231 |       -0.299 |
| 1.5x calm / 0.75x after a shock | end-2014 list (decides)             |    0.954 |        0.913 |        0.828 |      0.893 |           0.268 |       -0.354 |
| 1x calm / 0.5x after a shock (B2.2) | end-2014 list (decides)         |    0.141 |        0.152 |        0.309 |      0.132 |           0.193 |       -0.241 |
| 1x (the current rule) | shipped list (reported)                       |  nan     |      nan     |      nan     |    nan     |           0.326 |       -0.410 |
| steady 1.25x | shipped list (reported)                                |    0.998 |        0.998 |        0.877 |      0.996 |           0.394 |       -0.495 |
| steady 1.5x | shipped list (reported)                                 |    0.995 |        0.997 |        0.861 |      0.995 |           0.460 |       -0.571 |
| 1.25x calm / 0.625x after a shock | shipped list (reported)           |    0.852 |        0.732 |        0.785 |      0.789 |           0.356 |       -0.384 |
| 1.5x calm / 0.75x after a shock | shipped list (reported)             |    0.988 |        0.981 |        0.885 |      0.969 |           0.421 |       -0.451 |
| 1x calm / 0.5x after a shock (B2.2) | shipped list (reported)         |    0.141 |        0.098 |        0.406 |      0.132 |           0.291 |       -0.312 |

- **steady 1.25x**: **clears both bars: candidate B3.0**. Index since 1986: P 0.84 (stress 0.72), worst fall -90% against -83% at 1x. End-2014 list: P 0.99 (stress 0.97).
- **steady 1.5x**: grows faster, at a price (worst fall not bounded). Index since 1986: P 0.79 (stress 0.65), worst fall -95% against -83% at 1x. End-2014 list: P 0.98 (stress 0.96).
- **1.25x calm / 0.625x after a shock**: does not clear the growth bar. Index since 1986: P 0.34 (stress 0.21), worst fall -90% against -83% at 1x. End-2014 list: P 0.70 (stress 0.62).
- **1.5x calm / 0.75x after a shock**: does not clear the growth bar. Index since 1986: P 0.56 (stress 0.38), worst fall -94% against -83% at 1x. End-2014 list: P 0.95 (stress 0.89).
- **1x calm / 0.5x after a shock (B2.2)**: does not clear the growth bar. Index since 1986: P 0.11 (stress 0.09), worst fall -82% against -83% at 1x. End-2014 list: P 0.14 (stress 0.13).

## Reading: the steady multiple that would have grown fastest (base costs)

- Nasdaq-100 since 1986 (decides): 1.75x (15.6% a year). 0.50x 9.2%, 1.00x 13.6%, 1.25x 14.8%, 1.50x 15.4%, 2.00x 15.2%, 3.00x 9.0%
- end-2014 list (decides): 3.00x (45.3% a year). 0.50x 12.3%, 1.00x 22.0%, 1.25x 26.1%, 1.50x 29.9%, 2.00x 36.6%, 3.00x 45.3%
- shipped list (reported): 3.00x (74.6% a year). 0.50x 17.4%, 1.00x 32.6%, 1.25x 39.4%, 1.50x 46.0%, 2.00x 57.9%, 3.00x 74.6%

## What the bars do not show (written after the first run, 2026-11-23; no bar was changed)

- The calculated-risk bar counts points of worst fall. In the 2000-2002 crash the index at 1x fell 83% and at 1.25x 90%: 7 points, but that is 17 cents left of each dollar against 10 cents, about 40% less money at the bottom. Both are ruinous.
- On the index the advantage of 1.25x comes from the second half of the 40 years; in the first half it was a coin flip.
- The recent lists say the fastest growth was at 3x. That is a decade of unusually strong technology shares speaking, not a law: since 1986 the top is at about 1.75x, flat from 1.25x to 2x, and 3x did worse than 1x.
