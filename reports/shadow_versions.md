# Candidate versions of the bot, in shadow

Updated after the close on 2026-11-25. Counting from 2026-11-24. Computed from the rules and daily prices, not from the account's fills. Nothing here trades.

**In shock mode today: yes.** The latest market shock was 2026-11-23 (+7.0%); the candidates hold less for 19 more sessions. The names that fall hardest when the market falls, as measured today: AVGO, TSM, AMD, ORCL.

| Version | Sessions | Return since the start | Against the live book | Worst fall | Worst session | Share invested today |
|---|---|---|---|---|---|---|
| B2.1 live book (trend tilt, fully invested) | 2 | -1.98% | +0.00% | -0.88% | -1.11% | 97% |
| B2.2 half after a shock | 2 | -0.97% | +1.01% | -0.43% | -0.55% | 49% |
| B2.3 trim amplifiers after a shock | 2 | -1.34% | +0.64% | -0.72% | -0.72% | 89% |
| B3.0 steady 1.25x (borrowing a quarter) | 2 | -2.49% | -0.51% | -1.12% | -1.39% | 122% |
| C1.0 the live book with 5% in Bitcoin (held) | 2 | -2.00% | -0.02% | -0.84% | -1.17% | 95% stocks, 5% Bitcoin |

A few weeks of this say almost nothing: the candidates differ from the live book only after shocks. Their record on the past is in VERSIONS.md.

## Sleeves in shadow: holding only overnight

Separate small books, not part of the bot. On the past, meme and crypto stocks made their gains between the close and the next open and lost during the day (reports/meme_crypto_results.md). The lists were chosen with hindsight, so only these new days count.

| Sleeve | Sessions | Return since the start | Worst session |
|---|---|---|---|
| S1.0 crypto stocks, nights only (after 10 bp a night) | 2 | -8.53% | -5.73% |
| S2.0 meme stocks, nights only (after 10 bp a night) | 2 | -3.89% | -2.81% |
| for comparison: crypto stocks held day and night | 2 | -6.96% | -7.54% |
| for comparison: meme stocks held day and night | 2 | +3.00% | -0.74% |

## How a candidate becomes the bot's rule

1. Growth: the monthly self-review (learn.py) re-tests it against the live book; three passes in a row flag it for switching on.
2. Risk: the owner may choose a candidate that loses less but grows slower. That is a preference, not something a test can decide.
Either way the change gets a version number and a line in VERSIONS.md, and the old version stays one switch away.
