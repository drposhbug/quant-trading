# Daily calls: what the machine predicted and what came true

Updated after the close on 2026-11-23. Rules "v2 2026-11-23", written in daily_calls.py before the first call. It never trades.

Each day after the close the machine ranks about 500 stocks for three horizons. The top third is *favoured*, the bottom third *avoided*. When the horizon has passed, a call is **right** if favoured did better than avoided (before trading costs). There are three entries. **Sure**: only patterns whose record beats what the best of 345 reaches by luck; if there is none it says "no view". **Best guess**: every pattern that stands out one at a time, so some of its voters are luck. **Trend ranking**: a plain 12-month trend, the yardstick. Every call carries a probability, and the probabilities are checked too (last section). Being right more often than a coin is not yet a profit: trading costs come off, most of all on the next-session calls.

## The fast answer: its record on the past

Every fifth session since 2019 each entry's call was rebuilt with only what was known that day, then checked against what followed. Only calls that do not overlap are counted. "A coin gets" is the range pure luck lands in 19 times out of 20. An entry **passes** if it was right more often than a coin would be 19 times in 20 and its average gap is clearly above zero (t of 2 or more). Two cautions: the list is today's surviving companies, which flatters every entry a little, and several entries are tested, so a single narrow pass can be luck.

| Board | Horizon | Who | Calls | Right | A coin gets | Favoured minus avoided | t | Past test |
|---|---|---|---|---|---|---|---|---|
| market | next 21 sessions (official) | machine, sure | 4 | 2 (50%) | 0 to 4 | -1.12% | -0.7 | no better than a coin |
| market | next 21 sessions (official) | machine, best guess | 73 | 31 (42%) | 28 to 45 | -0.44% | -1.0 | no better than a coin |
| market | next 21 sessions (official) | trend ranking | 73 | 39 (53%) | 28 to 45 | -0.23% | -0.5 | yardstick |
| market | next 5 sessions (side board) | machine, sure | 26 | 8 (31%) | 8 to 18 | -0.45% | -1.5 | no better than a coin |
| market | next 5 sessions (side board) | machine, best guess | 366 | 180 (49%) | 164 to 202 | -0.06% | -0.8 | no better than a coin |
| market | next 5 sessions (side board) | trend ranking | 366 | 192 (52%) | 164 to 202 | -0.02% | -0.1 | yardstick |
| market | next session (side board) | machine, sure | 124 | 76 (61%) | 51 to 73 | +0.14% | +1.5 | right more often than a coin, but its gain is not clearly above zero: fails |
| market | next session (side board) | machine, best guess | 367 | 197 (54%) | 165 to 202 | +0.04% | +0.8 | no better than a coin |
| market | next session (side board) | trend ranking | 367 | 194 (53%) | 165 to 202 | -0.02% | -0.3 | yardstick |
| book | next 21 sessions (official) | machine, sure | 4 | 0 (0%) | 0 to 4 | -5.90% | -1.6 | no better than a coin |
| book | next 21 sessions (official) | machine, best guess | 73 | 31 (42%) | 28 to 45 | -1.24% | -1.2 | no better than a coin |
| book | next 21 sessions (official) | trend ranking | 73 | 44 (60%) | 28 to 45 | +0.70% | +0.8 | yardstick |
| book | next 5 sessions (side board) | machine, sure | 26 | 7 (27%) | 8 to 18 | -1.08% | -2.0 | no better than a coin |
| book | next 5 sessions (side board) | machine, best guess | 366 | 179 (49%) | 164 to 202 | -0.26% | -1.3 | no better than a coin |
| book | next 5 sessions (side board) | trend ranking | 366 | 179 (49%) | 164 to 202 | +0.17% | +0.8 | yardstick |
| book | next session (side board) | machine, sure | 124 | 68 (55%) | 51 to 73 | +0.40% | +1.7 | no better than a coin |
| book | next session (side board) | machine, best guess | 367 | 193 (53%) | 165 to 202 | +0.04% | +0.5 | no better than a coin |
| book | next session (side board) | trend ranking | 367 | 196 (53%) | 165 to 202 | +0.07% | +0.7 | yardstick |

## The tally on new days

New days confirm or contradict the past. Only calls that do not overlap are counted, and an entry is checked at 20, 40, 60... calls.

| Board | Horizon | Who | Calls counted | Right | A coin gets | Favoured minus avoided | Rank IC | All calls, overlapping | Says |
|---|---|---|---|---|---|---|---|---|---|
| market | next 21 sessions (official) | machine, sure | 0 | | | | | | nothing has come due yet |
| market | next 21 sessions (official) | machine, best guess | 0 | | | | | | nothing has come due yet |
| market | next 21 sessions (official) | trend ranking | 0 | | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | machine, sure | 0 | | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | machine, best guess | 0 | | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | trend ranking | 0 | | | | | | nothing has come due yet |
| market | next session (side board) | machine, sure | 0 | | | | | | nothing has come due yet |
| market | next session (side board) | machine, best guess | 0 | | | | | | nothing has come due yet |
| market | next session (side board) | trend ranking | 0 | | | | | | nothing has come due yet |
| book | next 21 sessions (official) | machine, sure | 0 | | | | | | nothing has come due yet |
| book | next 21 sessions (official) | machine, best guess | 0 | | | | | | nothing has come due yet |
| book | next 21 sessions (official) | trend ranking | 0 | | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | machine, sure | 0 | | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | machine, best guess | 0 | | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | trend ranking | 0 | | | | | | nothing has come due yet |
| book | next session (side board) | machine, sure | 0 | | | | | | nothing has come due yet |
| book | next session (side board) | machine, best guess | 0 | | | | | | nothing has come due yet |
| book | next session (side board) | trend ranking | 0 | | | | | | nothing has come due yet |

Days logged: 1. Days the sure entry had no view: next 21 sessions (official) 1, next 5 sessions (side board) 1, next session (side board) 0.

## The calls made after the close on 2026-11-23

### The next 21 sessions (official)

- Patterns that stand out one at a time: **10** of 345. Luck alone usually gives about 9 and rarely more than 46. About what luck gives.
- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.48).
- **The machine, best guess** (from 7 patterns that stand out one at a time; some of them are luck), market: favours most MRNA, NEM, PYPL, LULU, LII, COIN, AXON, RDDT, COO, EXPE; avoids most L, TRGP, OKE, HUM, CBOE, CVX, AFL, EOG, EG, NI. **44% that favoured beats avoided**, 56% that it does not.
  In the book: favours SPCX, TSLA, ORCL, AMD; avoids MSFT, META, AVGO, NVDA. **44% that favoured beats avoided**, 56% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **53% that favoured beats avoided**, 47% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **58% that favoured beats avoided**, 42% that it does not.

### The next 5 sessions (side board)

- Patterns that stand out one at a time: **24** of 345. Luck alone usually gives about 8 and rarely more than 60. About what luck gives.
- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.57).
- **The machine, best guess** (from 24 patterns that stand out one at a time; some of them are luck), market: favours most UNH, ELV, CNC, HUM, WSM, MPC, MO, CRM, VLO, LYB; avoids most PNR, TJX, WYNN, NRG, DPZ, LVS, BSX, MLM, GNRC, MKC. **49% that favoured beats avoided**, 51% that it does not.
  In the book: favours SPCX, AMD, MSFT, AAPL; avoids TSLA, ORCL, NVDA, AMZN. **49% that favoured beats avoided**, 51% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **52% that favoured beats avoided**, 48% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **49% that favoured beats avoided**, 51% that it does not.

### The next session (side board)

- Patterns that stand out one at a time: **75** of 345. Luck alone usually gives about 8 and rarely more than 43. More than luck: something real is in there, even where no single pattern proves it.
- **The machine, sure**, market: favours most MRNA, VTRS, AES, TGT, TECH, MU, PSX, MPC, SNDK, HST; avoids most LVS, BSX, PODD, PNR, ROL, NKE, WYNN, NFLX, TSCO, CSGP. **60% that favoured beats avoided**, 40% that it does not.
  In the book: favours AMD, AAPL, TSM; avoids ORCL, TSLA, AVGO. **54% that favoured beats avoided**, 46% that it does not.
- **The machine, best guess** (from 75 patterns that stand out one at a time; some of them are luck), market: favours most MRNA, TECH, MPC, PSX, VLO, VTRS, TRV, AES, WST, HST; avoids most LVS, PNR, ROL, BSX, WYNN, NFLX, APTV, PODD, NRG, ALB. **53% that favoured beats avoided**, 47% that it does not.
  In the book: favours AAPL, AMD, MSFT, TSM; avoids ORCL, TSLA, AVGO, GOOGL. **52% that favoured beats avoided**, 48% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **53% that favoured beats avoided**, 47% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **53% that favoured beats avoided**, 47% that it does not.
- What the machine is sure of (13 patterns cleared the bar of 3.49; strongest first):
  - return beyond what small US stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 4.2)
  - return beyond what 7-10 year Treasuries explains, 252 sessions, leaving out the latest 21: higher is better (strength 4.0)
  - return beyond what junk bonds explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.9)
  - return beyond what energy stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what banks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what oil explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what long Treasury bonds explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what US stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)

## The chance that each of the bot's stocks beats the typical stock

"Beats the typical stock" means it does better than the middle stock of the market list over that horizon, so 50% is a coin. The columns are the horizon in sessions and the entry. These numbers stay close to 50% because that is what the record supports.

| Stock | 21: sure | 21: best guess | 21: trend | 5: sure | 5: best guess | 5: trend | 1: sure | 1: best guess | 1: trend |
|---|---|---|---|---|---|---|---|---|---|
| AAPL | no view | 50.0% | 49.1% | no view | 50.0% | 50.2% | 52.8% | 50.3% | 50.9% |
| AMD | no view | 50.3% | 49.9% | no view | 50.0% | 50.8% | 52.8% | 52.0% | 50.7% |
| AMZN | no view | 50.3% | 49.6% | no view | 50.2% | 49.8% | 49.6% | 49.5% | 49.5% |
| AVGO | no view | 50.8% | 49.8% | no view | 49.5% | 49.2% | 47.1% | 48.9% | 49.5% |
| GOOGL | no view | 50.3% | 49.7% | no view | 50.2% | 49.0% | 48.0% | 49.3% | 49.4% |
| META | no view | 50.8% | 49.7% | no view | 49.5% | 49.0% | 48.0% | 49.5% | 49.4% |
| MSFT | no view | 50.8% | 49.6% | no view | 50.0% | 49.8% | 49.6% | 50.6% | 49.5% |
| NVDA | no view | 50.8% | 49.7% | no view | 50.2% | 49.0% | 48.0% | 49.3% | 49.4% |
| ORCL | no view | 50.3% | 49.4% | no view | 50.2% | 48.8% | 47.1% | 47.8% | 49.0% |
| SPCX | no view | 48.6% | no view | no view | 49.9% | no view | no view | 48.9% | no view |
| TSLA | no view | 50.3% | 49.8% | no view | 50.6% | 49.2% | 47.1% | 47.8% | 49.5% |
| TSM | no view | 50.3% | 50.5% | no view | 50.0% | 50.1% | 50.8% | 50.6% | 49.8% |

## Where the probabilities come from

Each starts from the entry's record on old days: every fifth session since 2019 the call was rebuilt with only what was known that day, and checked against what followed. That record is pulled toward 50% and counts for at most 100 calls; every real result since is added on top, so the probabilities learn from what comes true. The old-days record is on companies that still exist today, which flatters it a little.

| Entry | Horizon | Board | Its record on old days | Real results since | Chance today |
|---|---|---|---|---|---|
| machine, best guess | next 21 sessions (official) | market | right in 42% of 73 calls | 0 of 0 | 44% |
| machine, best guess | next 21 sessions (official) | book | right in 42% of 73 calls | 0 of 0 | 44% |
| trend ranking | next 21 sessions (official) | market | right in 53% of 73 calls | 0 of 0 | 53% |
| trend ranking | next 21 sessions (official) | book | right in 60% of 73 calls | 0 of 0 | 58% |
| machine, best guess | next 5 sessions (side board) | market | right in 49% of 366 calls | 0 of 0 | 49% |
| machine, best guess | next 5 sessions (side board) | book | right in 49% of 366 calls | 0 of 0 | 49% |
| trend ranking | next 5 sessions (side board) | market | right in 52% of 366 calls | 0 of 0 | 52% |
| trend ranking | next 5 sessions (side board) | book | right in 49% of 366 calls | 0 of 0 | 49% |
| machine, sure | next session (side board) | market | right in 61% of 124 calls | 0 of 0 | 60% |
| machine, sure | next session (side board) | book | right in 55% of 124 calls | 0 of 0 | 54% |
| machine, best guess | next session (side board) | market | right in 54% of 367 calls | 0 of 0 | 53% |
| machine, best guess | next session (side board) | book | right in 53% of 367 calls | 0 of 0 | 52% |
| trend ranking | next session (side board) | market | right in 53% of 367 calls | 0 of 0 | 53% |
| trend ranking | next session (side board) | book | right in 53% of 367 calls | 0 of 0 | 53% |

## Were the probabilities honest?

Nothing has come due yet. When it has: the Brier score (a coin that always says 50% scores 0.250, lower is better), and how often each band of stated chance came true.

## What came due most recently

| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |
|---|---|---|---|---|---|---|---|
