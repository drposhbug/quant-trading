# Daily calls: what the machine predicted and what came true

Updated after the close on 2026-11-23. Rules "v2 2026-11-23", written in daily_calls.py before the first call. It never trades.

Each day after the close the machine ranks about 500 stocks for three horizons. The top third is *favoured*, the bottom third *avoided*. When the horizon has passed, a call is **right** if favoured did better than avoided (before trading costs). There are three entries. **Sure**: only patterns whose record beats what the best of 345 reaches by luck; if there is none it says "no view". **Best guess**: every pattern that stands out one at a time, so some of its voters are luck. **Trend ranking**: a plain 12-month trend, the yardstick. Being right more often than a coin is not yet a profit: trading costs come off, most of all on the next-session calls.

## The tally

Only calls that do not overlap are counted. "A coin gets" is the range pure luck lands in 19 times out of 20.

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

Days logged: 1. Days the machine had no view: next 21 sessions (official) 1, next 5 sessions (side board) 1, next session (side board) 0.

## The calls made after the close on 2026-11-23

### The next 21 sessions (official)

- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.48).
- **The machine, best guess** (from 7 patterns that stand out one at a time; some of them are luck), market: favours most MRNA, NEM, PYPL, LULU, LII, COIN, AXON, RDDT, COO, EXPE; avoids most L, TRGP, OKE, HUM, CBOE, CVX, AFL, EOG, EG, NI.
  In the book: favours SPCX, TSLA, ORCL, AMD; avoids MSFT, META, AVGO, NVDA.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA.

### The next 5 sessions (side board)

- **The machine, sure: no view.** No pattern stood out from luck (the bar was 3.57).
- **The machine, best guess** (from 24 patterns that stand out one at a time; some of them are luck), market: favours most UNH, ELV, CNC, HUM, WSM, MPC, MO, CRM, VLO, LYB; avoids most PNR, TJX, WYNN, NRG, DPZ, LVS, BSX, MLM, GNRC, MKC.
  In the book: favours SPCX, AMD, MSFT, AAPL; avoids TSLA, ORCL, NVDA, AMZN.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA.

### The next session (side board)

- **The machine, sure**, market: favours most MRNA, VTRS, AES, TGT, TECH, MU, PSX, MPC, SNDK, HST; avoids most LVS, BSX, PODD, PNR, ROL, NKE, WYNN, NFLX, TSCO, CSGP.
  In the book: favours AMD, AAPL, TSM; avoids ORCL, TSLA, AVGO.
- **The machine, best guess** (from 75 patterns that stand out one at a time; some of them are luck), market: favours most MRNA, TECH, MPC, PSX, VLO, VTRS, TRV, AES, WST, HST; avoids most LVS, PNR, ROL, BSX, WYNN, NFLX, APTV, PODD, NRG, ALB.
  In the book: favours AAPL, AMD, MSFT, TSM; avoids ORCL, TSLA, AVGO, GOOGL.
- **The trend ranking**, market: favours most AES, TECH, MRNA, VTRS, PSX, TGT, MPC, VLO, APA, HST; avoids most BSX, LVS, PODD, PNR, ROL, NFLX, NKE, WYNN, TSCO, INTU.
  In the book: favours AAPL, AMD, TSM; avoids ORCL, AVGO, TSLA.
- What the machine is sure of (13 patterns cleared the bar of 3.49; strongest first):
  - return beyond what small US stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 4.2)
  - return beyond what 7-10 year Treasuries explains, 252 sessions, leaving out the latest 21: higher is better (strength 4.0)
  - return beyond what junk bonds explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.9)
  - return beyond what energy stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what banks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what oil explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what long Treasury bonds explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)
  - return beyond what US stocks explains, 252 sessions, leaving out the latest 21: higher is better (strength 3.8)

## What came due most recently

| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |
|---|---|---|---|---|---|---|---|
