# Daily calls: what the machine predicted and what came true

Updated after the close on 2026-11-23. Rules "v3 2026-11-23", written in daily_calls.py before the first call. It never trades.

Each day after the close the machine ranks about 500 stocks for three horizons. The top third is *favoured*, the bottom third *avoided*. Every result is measured from the next morning's open, the first price anyone could trade at after the call. When the horizon has passed, a call is **right** if favoured did better than avoided (before trading costs). There are three entries. **Sure**: only patterns whose record beats what the best of 332 reaches by luck; if there is none it says "no view". **Best guess**: every pattern that stands out one at a time, so some of its voters are luck. **Trend ranking**: a plain 12-month trend, the yardstick. Every call carries a probability, and the probabilities are checked too (last section). Being right more often than a coin is not yet a profit: trading costs come off, most of all on the next-session calls.

## The fast answer: its record on the past

Every fifth session since 2019 each entry's call was rebuilt with only what was known that day, then checked against what followed. Only calls that do not overlap are counted. "A coin gets" is the range pure luck lands in 19 times out of 20. An entry **passes** if it was right more often than a coin would be 19 times in 20 and its average gap is clearly above zero (t of 2 or more). Two cautions: the list is today's surviving companies, which flatters every entry a little, and several entries are tested, so a single narrow pass can be luck.

| Board | Horizon | Who | Calls | Right | A coin gets | Favoured minus avoided | t | Past test |
|---|---|---|---|---|---|---|---|---|
| market | next 21 sessions (official) | machine, sure | 3 | 2 (67%) | 0 to 3 | +0.39% | +0.5 | no better than a coin |
| market | next 21 sessions (official) | machine, best guess | 73 | 31 (42%) | 28 to 45 | -0.49% | -1.2 | no better than a coin |
| market | next 21 sessions (official) | trend ranking | 73 | 39 (53%) | 28 to 45 | -0.28% | -0.6 | yardstick |
| market | next 5 sessions (side board) | machine, sure | 4 | 0 (0%) | 0 to 4 | -2.19% | -2.1 | no better than a coin |
| market | next 5 sessions (side board) | machine, best guess | 363 | 157 (43%) | 163 to 200 | -0.08% | -1.0 | no better than a coin |
| market | next 5 sessions (side board) | trend ranking | 366 | 186 (51%) | 164 to 202 | -0.07% | -0.5 | yardstick |
| market | next session (side board) | machine, best guess | 367 | 175 (48%) | 165 to 202 | -0.07% | -2.0 | no better than a coin |
| market | next session (side board) | trend ranking | 367 | 176 (48%) | 165 to 202 | -0.07% | -1.6 | yardstick |
| book | next 21 sessions (official) | machine, sure | 3 | 0 (0%) | 0 to 3 | -7.53% | -1.5 | no better than a coin |
| book | next 21 sessions (official) | machine, best guess | 73 | 29 (40%) | 28 to 45 | -0.88% | -0.8 | no better than a coin |
| book | next 21 sessions (official) | trend ranking | 73 | 41 (56%) | 28 to 45 | +0.57% | +0.7 | yardstick |
| book | next 5 sessions (side board) | machine, sure | 4 | 1 (25%) | 0 to 4 | -0.63% | -0.3 | no better than a coin |
| book | next 5 sessions (side board) | machine, best guess | 363 | 173 (48%) | 163 to 200 | -0.14% | -0.7 | no better than a coin |
| book | next 5 sessions (side board) | trend ranking | 366 | 171 (47%) | 164 to 202 | +0.07% | +0.3 | yardstick |
| book | next session (side board) | machine, best guess | 367 | 189 (51%) | 165 to 202 | +0.01% | +0.2 | no better than a coin |
| book | next session (side board) | trend ranking | 367 | 181 (49%) | 165 to 202 | -0.02% | -0.3 | yardstick |

## The tally on new days

New days confirm or contradict the past. Only calls that do not overlap are counted. "Evidence" starts at 1 and 20 confirms; it can be read every day without fooling ourselves, because luck alone reaches 20 at most 1 time in 20.

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

Days logged: 1. Days the sure entry had no view: next 21 sessions (official) 1, next 5 sessions (side board) 1, next session (side board) 1.

## The calls made after the close on 2026-11-23

### The next 21 sessions (official)

- Patterns that stand out one at a time: **13** of 332. Luck alone usually gives about 9 and rarely more than 47. About what luck gives.
- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.49).
- **The machine, best guess** (from 9 patterns that stand out one at a time; some of them are luck), market: favours most MRNA, NEM, PYPL, COIN, LULU, FICO, LII, ALB, FCX, COO; avoids most L, HUM, AFL, CBOE, EG, OKE, REG, TRGP, NI, AMT. **44% that favoured beats avoided**, 56% that it does not.
  In the book: favours SPCX, ORCL, AMD, TSLA; avoids MSFT, META, AVGO, NVDA. **42% that favoured beats avoided**, 58% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **53% that favoured beats avoided**, 47% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **55% that favoured beats avoided**, 45% that it does not.

### The next 5 sessions (side board)

- Patterns that stand out one at a time: **12** of 332. Luck alone usually gives about 8 and rarely more than 56. About what luck gives.
- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.55).
- **The machine, best guess** (from 12 patterns that stand out one at a time; some of them are luck), market: favours most INTU, UNH, NKE, WSM, ELV, IP, CRM, CNC, CI, HUM; avoids most AES, TJX, OKTA, GNRC, PANW, FIX, TGT, ZBH, VRSN, COHR. **44% that favoured beats avoided**, 56% that it does not.
  In the book: favours SPCX, MSFT, AMD, AVGO; avoids NVDA, TSLA, GOOGL, AMZN. **48% that favoured beats avoided**, 52% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **51% that favoured beats avoided**, 49% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **47% that favoured beats avoided**, 53% that it does not.

### The next session (side board)

- Patterns that stand out one at a time: **9** of 332. Luck alone usually gives about 8 and rarely more than 48. About what luck gives.
- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.64).
- **The machine, best guess** (from 7 patterns that stand out one at a time; some of them are luck), market: favours most PYPL, MRNA, TMO, DGX, BDX, LIN, LH, AES, VRSN, FTNT; avoids most VICI, TDG, NI, EXE, ATO, LVS, PPL, CMS, TTWO, INVH. **48% that favoured beats avoided**, 52% that it does not.
  In the book: favours AAPL, AMD, SPCX, TSLA; avoids ORCL, AVGO, NVDA, META. **51% that favoured beats avoided**, 49% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU. **48% that favoured beats avoided**, 52% that it does not.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA. **49% that favoured beats avoided**, 51% that it does not.

## The chance that each of the bot's stocks beats the typical stock

"Beats the typical stock" means it does better than the middle stock of the market list over that horizon, so 50% is a coin. The columns are the horizon in sessions and the entry. These numbers stay close to 50% because that is what the record supports.

| Stock | 21: sure | 21: best guess | 21: trend | 5: sure | 5: best guess | 5: trend | 1: sure | 1: best guess | 1: trend |
|---|---|---|---|---|---|---|---|---|---|
| AAPL | no view | 50.1% | 48.8% | no view | 49.6% | 50.0% | no view | 48.6% | 50.2% |
| AMD | no view | 50.3% | 49.9% | no view | 50.2% | 50.4% | no view | 48.8% | 49.8% |
| AMZN | no view | 50.3% | 49.5% | no view | 49.9% | 49.9% | no view | 50.1% | 49.7% |
| AVGO | no view | 50.8% | 50.0% | no view | 50.2% | 49.4% | no view | 51.1% | 50.0% |
| GOOGL | no view | 50.3% | 49.9% | no view | 49.9% | 49.5% | no view | 50.0% | 49.9% |
| META | no view | 50.7% | 49.9% | no view | 50.4% | 49.5% | no view | 51.1% | 49.9% |
| MSFT | no view | 50.7% | 49.5% | no view | 49.9% | 49.9% | no view | 50.0% | 49.7% |
| NVDA | no view | 50.1% | 49.9% | no view | 51.3% | 49.5% | no view | 51.1% | 49.9% |
| ORCL | no view | 50.3% | 49.6% | no view | 49.6% | 49.4% | no view | 51.1% | 50.4% |
| SPCX | no view | 48.8% | no view | no view | 49.2% | no view | no view | 49.2% | no view |
| TSLA | no view | 50.3% | 50.0% | no view | 51.3% | 49.4% | no view | 49.9% | 50.0% |
| TSM | no view | 50.3% | 50.4% | no view | 49.6% | 49.8% | no view | 50.0% | 49.8% |

## Where the probabilities come from

Each starts from the entry's record on old days: every fifth session since 2019 the call was rebuilt with only what was known that day, and checked against what followed. That record is pulled toward 50% and counts for at most 100 calls; every real result since is added on top, so the probabilities learn from what comes true. The old-days record is on companies that still exist today, which flatters it a little.

| Entry | Horizon | Board | Its record on old days | Real results since | Chance today |
|---|---|---|---|---|---|
| machine, best guess | next 21 sessions (official) | market | right in 42% of 73 calls | 0 of 0 | 44% |
| machine, best guess | next 21 sessions (official) | book | right in 40% of 73 calls | 0 of 0 | 42% |
| trend ranking | next 21 sessions (official) | market | right in 53% of 73 calls | 0 of 0 | 53% |
| trend ranking | next 21 sessions (official) | book | right in 56% of 73 calls | 0 of 0 | 55% |
| machine, best guess | next 5 sessions (side board) | market | right in 43% of 363 calls | 0 of 0 | 44% |
| machine, best guess | next 5 sessions (side board) | book | right in 48% of 363 calls | 0 of 0 | 48% |
| trend ranking | next 5 sessions (side board) | market | right in 51% of 366 calls | 0 of 0 | 51% |
| trend ranking | next 5 sessions (side board) | book | right in 47% of 366 calls | 0 of 0 | 47% |
| machine, best guess | next session (side board) | market | right in 48% of 367 calls | 0 of 0 | 48% |
| machine, best guess | next session (side board) | book | right in 51% of 367 calls | 0 of 0 | 51% |
| trend ranking | next session (side board) | market | right in 48% of 367 calls | 0 of 0 | 48% |
| trend ranking | next session (side board) | book | right in 49% of 367 calls | 0 of 0 | 49% |

## Were the probabilities honest?

Nothing has come due yet. When it has: the Brier score (a coin that always says 50% scores 0.250, lower is better), and how often each band of stated chance came true.

## What came due most recently

| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |
|---|---|---|---|---|---|---|---|
