# Candidate versions of the bot, in shadow

Updated after the close on 2026-11-23. Counting from 2026-11-24. Computed from the rules and daily prices, not from the account's fills. Nothing here trades.

**In shock mode today: yes.** The latest market shock was 2026-11-23 (+7.0%); the candidates hold less for 21 more sessions. The names that fall hardest when the market falls, as measured today: AVGO, TSM, AMD, ORCL.

No session has been counted yet: the first is 2026-11-24.

## Sleeves in shadow: holding only overnight

Separate small books, not part of the bot. On the past, meme and crypto stocks made their gains between the close and the next open and lost during the day (reports/meme_crypto_results.md). The lists were chosen with hindsight, so only these new days count.

No session has been counted yet: the first is 2026-11-24.

## How a candidate becomes the bot's rule

1. Growth: the monthly self-review (learn.py) re-tests it against the live book; three passes in a row flag it for switching on.
2. Risk: the owner may choose a candidate that loses less but grows slower. That is a preference, not something a test can decide.
Either way the change gets a version number and a line in VERSIONS.md, and the old version stays one switch away.
