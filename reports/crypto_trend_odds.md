# Trading crypto with the slow trend rule

Rules written in crypto_trend_odds.py before the run. Bitcoin 2015-04-05 and Ether 2018-05-28 to 2026-11-24. P = share of simulated histories in which the rule ends with more money than holding the coin.

|                                 |   P vs holding |   P 1st half |   P 2nd half |   growth a year |   worst fall |   share of days held |
|:--------------------------------|---------------:|-------------:|-------------:|----------------:|-------------:|---------------------:|
| BTC-USD: holding                |        nan     |      nan     |      nan     |           0.599 |       -0.834 |                1.000 |
| BTC-USD: 200-day rule (decides) |          0.395 |        0.340 |        0.520 |           0.556 |       -0.705 |                0.620 |
| BTC-USD: 100-day rule (reading) |          0.561 |      nan     |      nan     |           0.621 |       -0.624 |                0.602 |
| ETH-USD: holding                |        nan     |      nan     |      nan     |           0.136 |       -0.864 |                1.000 |
| ETH-USD: 200-day rule (decides) |          0.831 |        0.778 |        0.750 |           0.378 |       -0.717 |                0.519 |
| ETH-USD: 100-day rule (reading) |          0.741 |      nan     |      nan     |           0.296 |       -0.750 |                0.543 |

- Verdict: **the rule does not clear its bar** (needs P of 0.75 on Bitcoin, 0.5 on Ether, and a smaller worst fall on both).

## Readings

- Bitcoin against the Nasdaq-100 on market days since 2018: correlation 0.30. It is partly the same bet as technology shares, and it trades on weekends when the bot cannot react.
- Hindsight, not evidence: the bot's book since 2018-10 grew 31.9% a year with a worst fall of -41%. With 10% of it in rule-traded Bitcoin: 33.4% a year, worst fall -38%. Bitcoin's own rise over these years is the reason, and that rise is the thing no test can promise again.
