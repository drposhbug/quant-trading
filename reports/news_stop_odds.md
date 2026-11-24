# Seeing the news and closing out: does the book lose less?

Rules written in news_stop_odds.py before the run. 'live book' is what the bot holds now. Alpaca daily bars from 2016.

|                                            |   P vs live |   P 1st half |   P 2nd half |   growth a year |   worst fall |   worst session |   worst 21 sessions |   Sharpe |
|:-------------------------------------------|------------:|-------------:|-------------:|----------------:|-------------:|----------------:|--------------------:|---------:|
| live book | end-2014 list (decides)        |     nan     |      nan     |      nan     |           0.215 |       -0.356 |          -0.120 |              -0.274 |    0.936 |
| close stop | end-2014 list (decides)       |       0.605 |        0.845 |        0.130 |           0.224 |       -0.339 |          -0.069 |              -0.150 |    1.077 |
| half after shock | end-2014 list (decides) |       0.378 |        0.737 |        0.126 |           0.207 |       -0.250 |          -0.060 |              -0.150 |    1.095 |
| stock stop | end-2014 list (decides)       |       0.133 |        0.098 |        0.411 |           0.206 |       -0.350 |          -0.117 |              -0.272 |    0.922 |
| tilt off, shock | end-2014 list (decides)  |       0.086 |        0.368 |        0.064 |           0.203 |       -0.345 |          -0.120 |              -0.282 |    0.895 |
| tilt off, wild | end-2014 list (decides)   |       0.221 |        0.672 |        0.083 |           0.203 |       -0.361 |          -0.120 |              -0.274 |    0.896 |
| gap stop | end-2014 list (decides)         |       0.432 |        0.658 |        0.124 |           0.213 |       -0.356 |          -0.054 |              -0.163 |    1.013 |
| live book | shipped list (reported)        |     nan     |      nan     |      nan     |           0.317 |       -0.411 |          -0.136 |              -0.299 |    1.095 |
| close stop | shipped list (reported)       |       0.401 |        0.706 |        0.073 |           0.310 |       -0.408 |          -0.078 |              -0.179 |    1.178 |
| half after shock | shipped list (reported) |       0.388 |        0.686 |        0.159 |           0.308 |       -0.312 |          -0.068 |              -0.169 |    1.273 |
| stock stop | shipped list (reported)       |       0.025 |        0.005 |        0.162 |           0.296 |       -0.417 |          -0.132 |              -0.296 |    1.056 |
| tilt off, shock | shipped list (reported)  |       0.116 |        0.217 |        0.198 |           0.303 |       -0.410 |          -0.134 |              -0.287 |    1.066 |
| tilt off, wild | shipped list (reported)   |       0.459 |        0.381 |        0.527 |           0.315 |       -0.418 |          -0.134 |              -0.290 |    1.100 |
| gap stop | shipped list (reported)         |       0.348 |        0.611 |        0.117 |           0.303 |       -0.411 |          -0.078 |              -0.215 |    1.129 |

- **Does any rule belong in the live book?** **No.** None grows faster than the live book by the standing bar.
- **Which lose less, and at what price?** 
  - **close stop**: worst fall smaller by 1.6% (end-2014 list) and 0.3% (shipped list); growth a year higher by 0.9% and lower by 0.7%.
  - **half after shock**: worst fall smaller by 10.6% (end-2014 list) and 9.9% (shipped list); growth a year lower by 0.8% and lower by 0.8%.
  - **tilt off, shock**: worst fall smaller by 1.0% (end-2014 list) and 0.1% (shipped list); growth a year lower by 1.2% and lower by 1.4%.

## Why closing out on the news helps less than it feels like it should

- Market shock-down days since 2018-09-28: 37. On those days the market fell -4.2% on average; 51% of that had already happened at the open, before any stop could act.
- In the 5 sessions after a close stop fired, the market returned +0.29% on average and was up 67% of the time (any 5 sessions: +0.37%, up 59%).
- Gap-down opens: 22. From that open to the same day's close the market returned +0.01% on average and rose 55% of the time.
- Times each rule fired: close stop 37, gap stop 22, any-shock 61, stock stop 125 stock-days.
