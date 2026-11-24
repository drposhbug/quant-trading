# Earnings as an event

Rules written in earnings_event_study.py before the run. 20098 announcements of 502 companies, 2016-04-15 to 2026-11-20. Returns are the stock's minus the average index member's.

|                                                                         |     events |   quarters |   average per event |   t over quarters |   1st half |   2nd half |   share above zero |
|:------------------------------------------------------------------------|-----------:|-----------:|--------------------:|------------------:|-----------:|-----------:|-------------------:|
| run-up: 5 sessions before | S&P 500                                     | 17523.0000 |    43.0000 |              0.0013 |            2.5199 |     0.0011 |     0.0014 |             0.5245 |
| holding through the announcement | S&P 500                              | 17523.0000 |    43.0000 |              0.0006 |            1.2148 |     0.0007 |     0.0005 |             0.5101 |
| drift: 21 sessions after, in the reaction's direction | S&P 500         | 17178.0000 |    43.0000 |              0.0005 |            1.0780 |     0.0013 |     0.0004 |             0.5068 |
| run-up: 5 sessions before | the bot's names                             |   403.0000 |    43.0000 |              0.0071 |            2.3262 |     0.0091 |     0.0045 |             0.5782 |
| holding through the announcement | the bot's names                      |   403.0000 |    43.0000 |              0.0058 |            1.4602 |     0.0065 |     0.0050 |             0.5012 |
| drift: 21 sessions after, in the reaction's direction | the bot's names |   397.0000 |    43.0000 |              0.0104 |            2.8598 |     0.0132 |     0.0097 |             0.5416 |

- **run-up: 5 sessions before**: a hint (+0.13% an event, t +2.5).
- **holding through the announcement**: no pattern (+0.06% an event, t +1.2).
- **drift: 21 sessions after, in the reaction's direction**: no pattern (+0.05% an event, t +1.1).

- Size of the reaction: on the reaction session a stock moved 2.2 times its normal daily move (typical event); one event in ten moved more than 6.6 times. The typical move was 2.9% against the average stock, up 51% of the time.
