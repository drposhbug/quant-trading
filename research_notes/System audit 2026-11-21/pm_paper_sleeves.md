# Prediction-market paper sleeves: sports bets and favourites tests

Audit note, 2026-11-21. Read-only review. Nothing was run against the network. Ledger state is the last cloud commit (2026-11-21 00:08 UTC). Line numbers are `file:line`.

## Purpose

Four paper experiments on Polymarket, run by `.github/workflows/daily.yml` (cron `23 */3 * * *`, each sleeve step `continue-on-error`). None can place an order.

1. **Elo sports bets** (`sports.py`, ledger `signals/sports_ledger.csv`). A FiveThirtyEight-style Elo model for NFL and NBA bets against the market when the two disagree. Its backtest failed (ROI −6.5%); the forward ledger is kept as a calibration record.
2. **Tennis favourites** (`betting/tennis_favorites.py`).
3. **Soccer and NBA favourites**, plus an exploratory NFL/NHL/MLB group (`betting/sport_favorites.py`).
4. **Any-category favourites** (`betting/any_favorites.py`).

Experiments 2 to 4 test one idea: heavy favourites win slightly more often than their price implies. They write to `betting/paper_favorites.sqlite3` (path from `SPORTS_DB_PATH`, `betting/db.py:27`), which the workflow commits to git. `scorecard.py` judges each ledger against the table in `MATH.md:87-96`.

## Data flow

**Elo.** Each run rebuilds ratings from nflverse and ESPN results (`sports.py:106-161`), lists open game-winner markets from Polymarket's Gamma API (`:165-173`), and pairs each market with a game by the two team names and the date in the market's slug, its URL name (`:176-189`). For games starting within 48 hours it records Elo's home-win probability, the market mid and both asks (`:395-412`). There is one row per slug, written once and never revised (`:368-379`). A row settles once the game started more than 3 hours ago and Gamma shows the market closed and resolved (`:415-425`).

**Favourites.** Each run lists open events, picks the match-winner market, reads Gamma's price, then fetches the live order book (`betting/polymarket_exec.py:65-80`). If every condition holds it inserts one row keyed by token id, so a token is entered at most once. It then re-reads the market behind every open row and settles the closed ones.

## Decision rules and parameters

| Ledger | Rule | Where |
|---|---|---|
| Elo | Bet 1 unit on Elo's side when Elo and the mid differ by more than 0.05; pay the ask; no fee | `sports.py:43`, `:230-243` |
| Elo | K 20; home edge 48 (NFL), 100 (NBA); ratings pulled one third to the mean each season | `sports.py:41-42` |
| Tennis | ATP/WTA singles; price and ask 0.80–0.97; spread ≤ 0.05; ask within 0.05 of price | `tennis_favorites.py:39,48,149,162-164` |
| Tennis | Pre-play guard: the slug date must be later than today (UTC) | `:133` |
| Tennis | Scored test: ask 0.90–0.97, logged from 2026-11-20, 300 settled | `:45`, `scorecard.py:262-264` |
| Soccer | Team-to-win YES token, never the draw; 0.80–0.95; seven leagues | `sport_favorites.py:57-61,159-163` |
| NBA; NFL/NHL/MLB | Game-winner favourite 0.85–0.97 | `:61` |
| All sports | Start time known and at least 30 minutes away; 14-day lookahead | `:62-63,150-152` |
| Any-category | Side priced 0.90–0.97; spread ≤ 0.03; 7–30 days to the end date; volume ≥ $10k; no sports, crypto or price markets; "objective" resolution | `any_favorites.py:52-64,121-135,161-184` |
| Fee | rate × p × (1 − p) per share. Tennis and sports: fixed 0.05. Any-category: the rate the market publishes | `tennis_favorites.py:47`, `sport_favorites.py:65`, `any_favorites.py:114-118` |
| Payout | Win (1 − ask)/ask, loss −1, less fee/ask, per $1 | `tennis_favorites.py:211`, `sport_favorites.py:238`, `any_favorites.py:248` |
| Pass bar | Mean ROI > 0, bootstrap 95% interval above 0, both halves above 0; 300 settled (200 for any-category); re-checked daily | `sport_favorites.py:248-260`, `scorecard.py:246-256` |

## Assumptions the code makes

- **The slug date is the US Eastern date** (`sports.py:17`). Since August 2026 NFL slugs carry the UTC date, so 8 pm ET kickoffs never match: 32 of 151 regular-season markets in the cached data, every one a night game.
- **A 50-50 resolution returns the stake** (`sport_favorites.py:233`, `any_favorites.py:244`) **or is a total loss** (`tennis_favorites.py:206`). Polymarket pays $0.50 a share, so the true result at an ask of 0.90 is −44%. `sports.py` gets this right.
- **Sports fees are 0.05 everywhere.** Cached Gamma data shows 0.05 on NBA, 0.03 on NFL since October, and some zero-fee weeks. `sports.py` charges no fee at all, about 2.2% of stake on the 12 bets logged.
- **A tennis slug date after today means the match has not started.** Every market carries a start time; the slug date differs from it for a third of matches, and 37% of matches are listed too late to pass this guard.
- **$100 fills at the best ask.** The size at the ask is read and discarded (`tennis_favorites.py:156`).
- **Bets are independent.** Any-category buys both sides of one question, for example Republican YES and Democrat NO on the same House seat.
- **The job runs every 3 hours.** Ledger timestamps suggest two runs about 6 hours apart, each about 2.6 hours after its slot.

## Tests

- `test_sports.py`: Elo arithmetic, no lookahead, choice of pre-start price, the bet rule, ledger idempotence, settlement. Not covered: `match`, `open_candidates`, `home_payouts`, fees, slug-date conventions.
- `betting/test_sport_favorites.py`: league filter, price floors and caps, the 30-minute guard, unknown start, gaping book, draw exclusion, idempotence, win and loss settlement, pass bar. Not covered: 50-50 resolution, closed-but-unresolved prices, fee by market.
- `betting/test_any_favorites.py`: both sides, time and volume windows, exclusions, two skip reasons, wide spread, idempotence, settlement, closed-not-final. Not covered: 50-50 resolution, several legs of one event, loose "official" wording.
- `tennis_favorites.py` has no test file.

All three test files pass.

## Current state

| Ledger | Rows | Settled | Open |
|---|---|---|---|
| Elo sports | 30 (12 bets, 11 on the home team) | 0 | 30 |
| Tennis, all rows (2026-09-10 to 11-18) | 278 | 244 won, 34 lost | 0 |
| Tennis scored test (from 2026-11-20) | 0 | 0 | 0 |
| Soccer | 8 | 1 lost | 7 |
| NBA | 6 | 0 | 6 |
| NFL/NHL/MLB | 3 | 0 | 3 |
| Any-category | 69, plus 5 skipped | 0 | 69 |

The 278 tennis rows are the original 0.80–0.95 test: 87.8% won at a mean ask of 0.870, stored ROI +0.5%. At least six of the 34 losses were 50-50 resolutions booked as total losses, and every row carries the old 0.03 fee. Rescored at the true payout and a 0.05 fee, ROI is +1.5% with a 95% interval of −2.8% to +5.4%. Either way it is far from the +11% in the Wimbledon 2026 look-back that motivated the test.

Any-category will reach its minimum first: 49 of its 69 entries end by 1 December.
