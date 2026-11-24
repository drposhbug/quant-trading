# Holding less of the names that magnify selloffs

Rules written in downside_beta_odds.py before the run. Alpaca daily bars; the same days as news_stop_odds.py.

|                                                         |   P vs live |   P 1st half |   P 2nd half |   growth a year |   worst fall |   worst session |   worst 21 sessions |   Sharpe |   average invested |
|:--------------------------------------------------------|------------:|-------------:|-------------:|----------------:|-------------:|----------------:|--------------------:|---------:|-------------------:|
| live book | end-2014 list (decides)                     |     nan     |      nan     |      nan     |           0.215 |       -0.356 |          -0.120 |              -0.274 |    0.936 |              0.999 |
| trim amplifiers after a shock | end-2014 list (decides) |       0.480 |        0.742 |        0.250 |           0.215 |       -0.320 |          -0.083 |              -0.224 |    1.016 |              0.952 |
| trim amplifiers always | end-2014 list (decides)        |       0.044 |        0.181 |        0.076 |           0.182 |       -0.302 |          -0.083 |              -0.224 |    0.967 |              0.845 |
| half after shock | end-2014 list (decides)              |       0.378 |        0.737 |        0.126 |           0.207 |       -0.250 |          -0.060 |              -0.150 |    1.095 |              0.853 |
| live book | shipped list (reported)                     |     nan     |      nan     |      nan     |           0.317 |       -0.411 |          -0.136 |              -0.299 |    1.095 |              0.999 |
| trim amplifiers after a shock | shipped list (reported) |       0.128 |        0.384 |        0.046 |           0.299 |       -0.371 |          -0.105 |              -0.234 |    1.120 |              0.960 |
| trim amplifiers always | shipped list (reported)        |       0.000 |        0.054 |        0.003 |           0.243 |       -0.350 |          -0.105 |              -0.234 |    1.038 |              0.862 |
| half after shock | shipped list (reported)              |       0.388 |        0.686 |        0.159 |           0.308 |       -0.312 |          -0.068 |              -0.169 |    1.273 |              0.853 |

- **trim amplifiers after a shock**: live book by the standing bar: no. Loses less on both lists: yes (worst fall smaller by 3.6% and 4.0%; growth a year lower by -0.0% and 1.8%).
- **trim amplifiers always**: live book by the standing bar: no. Loses less on both lists: yes (worst fall smaller by 5.4% and 6.1%; growth a year lower by 3.4% and 7.4%).
- **half after shock**: live book by the standing bar: no. Loses less on both lists: yes (worst fall smaller by 10.6% and 9.9%; growth a year lower by 0.8% and 0.8%).
