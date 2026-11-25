# Daily calls: what the machine predicted and what came true

Updated after the close on 2026-11-24. Rules "v4 2026-11-23", written in daily_calls.py before the first call. It never trades.

Each day after the close the machine ranks the S&P 500 stocks for three horizons. The top third is *favoured*, the bottom third *avoided*. A call is **right** if favoured did better than avoided, measured from the next morning's open (the first price anyone could trade at) and before trading costs. Moves that the whole market or a whole sector made are taken out first, so a call is about what is particular to each stock.

**Shock watch:** 6 market-wide shock days in the last 21 sessions (latest 2026-11-23, +4.7%). After a shock the market's moves have run about twice their normal size for a month, in either direction, and the direction has not been predictable. Nothing here acts on it; reports/news_stop_odds.md shows what holding half the book after a shock would have done.

The entries:

- **The learner**: all the price patterns combined, with near-copies sharing one weight. It speaks only when the whole crowd of patterns beats luck; otherwise "no view".
- **The trend ranking**: a plain 12-month trend. The yardstick.
- **The trend on calm days**: the same trend, standing aside while its own bet has been wilder than usual.
- **Busy month, quiet month**: last month's winners keep going if they traded unusually heavily, and turn back if they were quiet.
- **Earnings surprise**: stocks that beat the earnings forecast at their latest report, for 63 sessions after it.
- **About to report**: stocks due to report earnings within about a week.
- **Profitability**: companies with more gross profit per dollar of assets, as first reported.

## The fast answer: each entry's record on the past

Every fifth session since 2019 each call was rebuilt with only what was known that day, among the companies that were in the index that day (dead ones included), then checked against what followed. Only calls that do not overlap are counted. "A coin gets" is the range pure luck lands in 19 times out of 20. An entry **passes** if it was right more often than a coin would be 19 times in 20 and its average gap is clearly above zero (t of 2 or more). Several entries are read here, so one narrow pass can be luck.

| Board | Horizon | Who | Calls | Right | A coin gets | Favoured minus avoided | t | Its worst 5% of calls | Past test |
|---|---|---|---|---|---|---|---|---|---|
| market | next 21 sessions (official) | learner | 0 | | | | | | never had a view |
| market | next 21 sessions (official) | trend ranking | 73 | 43 (59%) | 28 to 45 | +0.07% | +0.2 | -6.68% | yardstick |
| market | next 21 sessions (official) | trend, calm days | 30 | 18 (60%) | 10 to 20 | +0.65% | +1.7 | -4.80% | no better than a coin |
| market | next 21 sessions (official) | busy/quiet month | 73 | 26 (36%) | 28 to 45 | -0.29% | -2.3 | -2.50% | no better than a coin |
| market | next 21 sessions (official) | earnings surprise | 73 | 36 (49%) | 28 to 45 | -0.03% | -0.2 | -2.83% | no better than a coin |
| market | next 21 sessions (official) | profitability | 73 | 33 (45%) | 28 to 45 | +0.03% | +0.2 | -2.53% | no better than a coin |
| market | next 5 sessions (side board) | learner | 0 | | | | | | never had a view |
| market | next 5 sessions (side board) | trend ranking | 367 | 195 (53%) | 165 to 202 | +0.01% | +0.1 | -3.87% | yardstick |
| market | next 5 sessions (side board) | trend, calm days | 131 | 72 (55%) | 54 to 77 | +0.05% | +0.4 | -4.69% | no better than a coin |
| market | next 5 sessions (side board) | about to report | 354 | 193 (55%) | 159 to 195 | +0.06% | +0.8 | -3.03% | right more often than a coin, but its gain is not clearly above zero: fails |
| market | next session (side board) | learner | 112 | 52 (46%) | 46 to 66 | -0.00% | -0.2 | -0.74% | no better than a coin |
| market | next session (side board) | trend ranking | 367 | 182 (50%) | 165 to 202 | -0.01% | -0.5 | -1.32% | yardstick |
| market | next session (side board) | trend, calm days | 131 | 69 (53%) | 54 to 77 | +0.03% | +0.6 | -1.34% | no better than a coin |
| book | next 21 sessions (official) | learner | 0 | | | | | | never had a view |
| book | next 21 sessions (official) | trend ranking | 73 | 37 (51%) | 28 to 45 | +0.19% | +0.2 | -19.94% | yardstick |
| book | next 21 sessions (official) | trend, calm days | 30 | 14 (47%) | 10 to 20 | -0.78% | -0.6 | -14.92% | no better than a coin |
| book | next 5 sessions (side board) | learner | 0 | | | | | | never had a view |
| book | next 5 sessions (side board) | trend ranking | 367 | 190 (52%) | 165 to 202 | +0.05% | +0.2 | -8.72% | yardstick |
| book | next 5 sessions (side board) | trend, calm days | 131 | 66 (50%) | 54 to 77 | -0.23% | -0.7 | -9.08% | no better than a coin |
| book | next session (side board) | learner | 112 | 57 (51%) | 46 to 66 | -0.02% | -0.1 | -3.94% | no better than a coin |
| book | next session (side board) | trend ranking | 367 | 191 (52%) | 165 to 202 | +0.02% | +0.2 | -3.28% | yardstick |
| book | next session (side board) | trend, calm days | 131 | 74 (56%) | 54 to 77 | +0.14% | +1.2 | -2.73% | no better than a coin |

## The tally on new days

New days confirm or contradict the past. Only calls that do not overlap are counted. "Evidence" starts at 1 and 20 confirms; it can be read every day without fooling ourselves, because luck alone reaches 20 at most 1 time in 20.

| Board | Horizon | Who | Calls counted | Right | A coin gets | Favoured minus avoided | All calls, overlapping | Says |
|---|---|---|---|---|---|---|---|---|
| market | next 21 sessions (official) | learner | 0 | | | | | nothing has come due yet |
| market | next 21 sessions (official) | trend ranking | 0 | | | | | nothing has come due yet |
| market | next 21 sessions (official) | trend, calm days | 0 | | | | | nothing has come due yet |
| market | next 21 sessions (official) | busy/quiet month | 0 | | | | | nothing has come due yet |
| market | next 21 sessions (official) | earnings surprise | 0 | | | | | nothing has come due yet |
| market | next 21 sessions (official) | profitability | 0 | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | learner | 0 | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | trend ranking | 0 | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | trend, calm days | 0 | | | | | nothing has come due yet |
| market | next 5 sessions (side board) | about to report | 0 | | | | | nothing has come due yet |
| market | next session (side board) | learner | 1 | 1 | 0 to 1 | +0.12% | 1 of 1 | not yet: evidence 1.5 of the 20 needed (failed the past test) |
| market | next session (side board) | trend ranking | 1 | 0 | 0 to 1 | -0.65% | 0 of 1 | yardstick |
| market | next session (side board) | trend, calm days | 1 | 0 | 0 to 1 | -0.65% | 0 of 1 | not yet: evidence 0.5 of the 20 needed (failed the past test) |
| book | next 21 sessions (official) | learner | 0 | | | | | nothing has come due yet |
| book | next 21 sessions (official) | trend ranking | 0 | | | | | nothing has come due yet |
| book | next 21 sessions (official) | trend, calm days | 0 | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | learner | 0 | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | trend ranking | 0 | | | | | nothing has come due yet |
| book | next 5 sessions (side board) | trend, calm days | 0 | | | | | nothing has come due yet |
| book | next session (side board) | learner | 1 | 1 | 0 to 1 | +0.19% | 1 of 1 | not yet: evidence 1.5 of the 20 needed (failed the past test) |
| book | next session (side board) | trend ranking | 1 | 1 | 0 to 1 | +2.35% | 1 of 1 | yardstick |
| book | next session (side board) | trend, calm days | 1 | 1 | 0 to 1 | +2.35% | 1 of 1 | not yet: evidence 1.5 of the 20 needed (failed the past test) |

## The calls made after the close on 2026-11-24

### The next 21 sessions (official)

- Patterns that stand out one at a time: **14** of the learner's. Luck alone usually gives about 9 and rarely more than 59. About what luck gives.
- **The learner: no view.** The whole crowd of patterns is no better than luck here.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **57% that favoured beats avoided**, 43% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **51% that favoured beats avoided**, 49% that it does not.
- **The trend on calm days**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **56% that favoured beats avoided**, 44% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **48% that favoured beats avoided**, 52% that it does not.
- **Busy month, quiet month**, market: favours most NOW, PNR, RDDT, TER, SNDK, MU, COIN, CIEN, NTAP, CLX; avoids most APP, DELL, CMG, CHTR, ILMN, FFIV, DLTR, NVDA, BE, MPC. **39% that favoured beats avoided**, 61% that it does not.
- **Earnings surprise**, market: favours most DDOG, CHTR, WDAY, CRM, CNC, SKYD, COIN, XYZ, MRNA, WY; avoids most UBER, CRWD, MGM, BA, MOS, SPG, MAA, REG, AXON, GOOGL. **49% that favoured beats avoided**, 51% that it does not.
- **Profitability**, market: favours most TPR, FICO, SNDK, RL, DPZ, VRSN, GWW, FAST, IDXX, INCY; avoids most WY, TSN, CPT, MRNA, KHC, KDP, HRL, OMC, INTC, BA. **46% that favoured beats avoided**, 54% that it does not.

### The next 5 sessions (side board)

- Patterns that stand out one at a time: **36** of the learner's. Luck alone usually gives about 8 and rarely more than 59. About what luck gives.
- **The learner: no view.** The whole crowd of patterns is no better than luck here.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **53% that favoured beats avoided**, 47% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **52% that favoured beats avoided**, 48% that it does not.
- **The trend on calm days**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **54% that favoured beats avoided**, 46% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **50% that favoured beats avoided**, 50% that it does not.
- **About to report**, market: favours most MRVL, P, CRWD, OKTA, HOOD, COIN, MRNA, RDDT, IBKR, FIX; avoids most FTNT, FFIV, CSCO, PANW, DDOG, TWLO, AKAM, SNPS, ECHO, NTAP. **54% that favoured beats avoided**, 46% that it does not.

### The next session (side board)

- Patterns that stand out one at a time: **77** of the learner's. Luck alone usually gives about 8 and rarely more than 51. More than luck: something real is in there.
- **The learner**, market: favours most PYPL, MRNA, EIX, SWKS, PCG, ADI, LULU, WSM, JBHT, DVA; avoids most TTWO, LLY, TJX, TECH, F, GOOGL, WY, GOOG, VRTX, BLK. **47% that favoured beats avoided**, 53% that it does not.
  In the book: favours AMD, TSLA, AVGO; avoids GOOGL, NVDA, ORCL. **51% that favoured beats avoided**, 49% that it does not.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **49% that favoured beats avoided**, 51% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **52% that favoured beats avoided**, 48% that it does not.
- **The trend on calm days**, market: favours most AES, TECH, MRNA, VTRS, TRV, EBAY, TGT, STT, BNY, HST; avoids most PODD, BSX, PNR, ROL, EXE, LVS, TSCO, INTU, CSGP, ZTS. **52% that favoured beats avoided**, 48% that it does not.
  In the book: favours AAPL, MSFT, AMZN; avoids ORCL, AVGO, NVDA. **56% that favoured beats avoided**, 44% that it does not.
- What the learner leans on most:
  - overnight return over 5 sessions: lower is better (strength 4.0)
  - sensitivity to small US stocks times its move over 63 sessions: lower is better (strength 2.5)
  - where it closes in the day's range, average of 10 sessions: higher is better (strength 3.0)
  - sensitivity to small US stocks times its move over 126 sessions: lower is better (strength 2.0)
  - sensitivity to the Nasdaq 100 times its move over 63 sessions: lower is better (strength 2.1)
  - overnight return over 10 sessions: lower is better (strength 2.6)
  - sensitivity to energy stocks times its move over 21 sessions: higher is better (strength 1.1)
  - overnight return over 252 sessions: lower is better (strength 1.3)

## The chance that each of the bot's stocks beats the typical stock

"Beats the typical stock" means it does better than the middle stock of the index over that horizon, so 50% is a coin. The columns are the horizon in sessions and the entry. These numbers stay close to 50% because that is what the record supports.

| Stock | 21: trend ranking | 21: trend, calm days | 5: trend ranking | 5: trend, calm days | 1: learner | 1: trend ranking | 1: trend, calm days |
|---|---|---|---|---|---|---|---|
| AAPL | 50.2% | 50.8% | 50.4% | 49.9% | 49.7% | 50.9% | 50.5% |
| AMD | 50.0% | 50.3% | 49.9% | 50.5% | 49.1% | 49.1% | 49.6% |
| AMZN | 50.2% | 50.8% | 50.4% | 49.9% | 49.6% | 50.9% | 50.5% |
| AVGO | 49.4% | 47.7% | 49.3% | 49.0% | 50.2% | 49.8% | 49.3% |
| GOOGL | 50.0% | 50.3% | 49.9% | 50.5% | 49.7% | 49.1% | 49.6% |
| META | 50.0% | 50.3% | 49.9% | 50.5% | 49.6% | 49.1% | 49.6% |
| MSFT | 50.2% | 50.8% | 50.4% | 49.9% | 49.7% | 50.9% | 50.5% |
| NVDA | 49.1% | 48.8% | 49.4% | 49.5% | 49.7% | 49.3% | 49.1% |
| ORCL | 48.7% | 47.0% | 49.3% | 48.0% | 49.7% | 50.2% | 48.5% |
| TSLA | 50.0% | 50.3% | 49.9% | 50.5% | 49.5% | 49.1% | 49.6% |

## Where the probabilities come from

Each starts from the entry's record on old days (above), pulled toward 50% and counted for at most 100 calls; every real result since is added on top, so the probabilities learn from what comes true.

| Entry | Horizon | Board | Its record on old days | Real results since | Chance today |
|---|---|---|---|---|---|
| trend ranking | next 21 sessions (official) | market | right in 59% of 73 calls | 0 of 0 | 57% |
| trend ranking | next 21 sessions (official) | book | right in 51% of 73 calls | 0 of 0 | 51% |
| trend, calm days | next 21 sessions (official) | market | right in 60% of 30 calls | 0 of 0 | 56% |
| trend, calm days | next 21 sessions (official) | book | right in 47% of 30 calls | 0 of 0 | 48% |
| busy/quiet month | next 21 sessions (official) | market | right in 36% of 73 calls | 0 of 0 | 39% |
| earnings surprise | next 21 sessions (official) | market | right in 49% of 73 calls | 0 of 0 | 49% |
| profitability | next 21 sessions (official) | market | right in 45% of 73 calls | 0 of 0 | 46% |
| trend ranking | next 5 sessions (side board) | market | right in 53% of 367 calls | 0 of 0 | 53% |
| trend ranking | next 5 sessions (side board) | book | right in 52% of 367 calls | 0 of 0 | 52% |
| trend, calm days | next 5 sessions (side board) | market | right in 55% of 131 calls | 0 of 0 | 54% |
| trend, calm days | next 5 sessions (side board) | book | right in 50% of 131 calls | 0 of 0 | 50% |
| about to report | next 5 sessions (side board) | market | right in 55% of 354 calls | 0 of 0 | 54% |
| learner | next session (side board) | market | right in 46% of 112 calls | 1 of 1 | 47% |
| learner | next session (side board) | book | right in 51% of 112 calls | 1 of 1 | 51% |
| trend ranking | next session (side board) | market | right in 50% of 367 calls | 0 of 1 | 49% |
| trend ranking | next session (side board) | book | right in 52% of 367 calls | 1 of 1 | 52% |
| trend, calm days | next session (side board) | market | right in 53% of 131 calls | 0 of 1 | 52% |
| trend, calm days | next session (side board) | book | right in 56% of 131 calls | 1 of 1 | 56% |

## Were the probabilities honest?

**Calls**: 6 scored, Brier score 0.2452 against a coin's 0.2500.

| Stated chance | How many | Came true |
|---|---|---|
| under 48% | 1 | 100% |
| 48 to 50% | 1 | 0% |
| 50 to 52% | 2 | 100% |
| 52 to 55% | 1 | 0% |
| over 55% | 1 | 100% |

**Stocks**: 30 scored, Brier score 0.2471 against a coin's 0.2500.

| Stated chance | How many | Came true |
|---|---|---|
| 48 to 50% | 21 | 14% |
| 50 to 52% | 9 | 33% |


## What came due most recently

| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23 | 2026-11-24 | next session (side board) | market | trend, calm days | +0.69% | +1.34% | wrong |
| 2026-11-23 | 2026-11-24 | next session (side board) | market | learner | +1.06% | +0.94% | right |
| 2026-11-23 | 2026-11-24 | next session (side board) | market | trend ranking | +0.69% | +1.34% | wrong |
| 2026-11-23 | 2026-11-24 | next session (side board) | book | trend, calm days | +0.98% | -1.36% | right |
| 2026-11-23 | 2026-11-24 | next session (side board) | book | learner | -0.87% | -1.06% | right |
| 2026-11-23 | 2026-11-24 | next session (side board) | book | trend ranking | +0.98% | -1.36% | right |
