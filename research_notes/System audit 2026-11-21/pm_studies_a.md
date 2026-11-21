# pm_studies_a: calibration, close, favourites, sharp snapshot, maker simulation

Audit note, 2026-11-21. Five research scripts, no orders. "Re-run" means reproduced offline, read-only, from the caches in `data/`.

## Purpose

Each script asks whether Polymarket or Kalshi prices are accurate, useful for the stock book, or beatable by a simple rule, and writes one report. Two feed paper sleeves: `reports/pm_calibration.md` is the stated basis of `betting/any_favorites.py`, and `reports/fav_backtest_results.md` is the yardstick for the favourites tests.

## Data flow

- **pm_calibration.py.** Draws up to 300 closed markets a week in hash order, keeps 40,140 that settled 1 or 0, and samples 250 per category and volume tercile (5,250). It reads the hourly price 1, 7 and 30 days before a reference time T, then prints calibration tables and the return from buying the favourite when the cheap side costs 0.5 to 10 cents. Kalshi macro strikes get the same treatment.
- **pm_close_study.py.** Daily "Up or Down" markets for 10 tickers, plus monthly ladders. The 1-minute Polymarket price at 09:25, 10:00 and 15:00 ET is compared with a zero-drift baseline from Alpaca bars, and a rule goes long at the open when the 09:25 price exceeds 0.60 (`pm_close_study.py:335`). 71 tests, Holm-corrected.
- **fav_backtest.py.** Every resolved event under 52 Gamma tags and series since 2024 gives 175,680 candidate markets. A random 2,000 per group are priced once at a fixed decision time, and the side priced 0.85 to 0.97 is bought and held (9,418 bets).
- **sharp_snapshot_study.py.** A copy of the odds-snapshot database (134 usable snapshots, 10 September to 20 November). Buys when de-vigged Pinnacle exceeds the Polymarket ask by 3 points at the same snapshot.
- **maker_sim.py.** 1,636 resolved Kalshi markets (sports, weather, economics). Trade prints and 1-minute candles for the last 48 hours drive simulated two-sided quotes, refreshed every 5 minutes and held to settlement.

## Decision rules and parameters

| Rule | Value | Where |
|---|---|---|
| Calibration reference time | T = earlier of endDate and closedTime | `pm_calibration.py:85` |
| Calibration price | last hourly point at or before T − h, at most 2 days old | `:111-124` |
| Edge bucket, costs | cheap side 0.5–10c; 0, 0.5, 1, 2c | `:277-291` |
| Close snapshots, staleness | 09:25, 10:00, 15:00; 60 minutes | `pm_close_study.py:37`, `:271` |
| Close pass | Holm p < 0.05, same sign in both halves | `:363-365` |
| Favourite band, spread, volume | 0.85–0.97, plus 1c, at least $1,000 | `fav_backtest.py:39` |
| Fee | rate × p(1 − p): sports 0.03, then 0.05 from 2026-07-10; geopolitics 0; crypto 0.07; other 0.04 | `:86-95` |
| Decision time | sports start − 2h; golf, F1, boxing, UFC end − 3d; non-sports end − 7d | `:198-211` |
| Outcomes kept | clean 1 or 0 only | `:176-177` |
| Clusters | sports by decision day, non-sports by event | `:273` |
| ADD a group | ROI > 0 in first 70% and last 30%, interval floor > −1%, 30 bets; Holm unused | `:354-358` |
| Snapshot rule | first pre-game snapshot with fair − ask ≥ 3 points; fee 0.05·q(1 − q) | `sharp_snapshot_study.py:49-62` |
| Integrity filter, added after seeing the bets | Gamma start within 3h, full outcome set, asks sum ≥ 0.98 | `:152-153` |
| Maker quotes | mid ± 2c, 10 contracts, inventory ± 50 | `maker_sim.py:32`, `:265-267` |
| Maker fill; pass | only a print strictly through the quote, half its size; interval above 0, both halves, holdout | `:270-275`, `:426` |

## Assumptions the code makes

- The hourly Polymarket price, a mid or a last trade, can be bought 1c higher.
- Gamma's present end date, start time and lifetime volume were known at the decision.
- A market that resolves 50-50 costs nothing. It pays $0.50 a share, about −45% on a 0.90 favourite.
- Events are independent, including hundreds of races settled on one election night.
- A Gamma error means there are no more pages (`fav_backtest.py:117-118`).
- A resting quote never fills on a print at its own price.

## What the tests cover

`test_fav_backtest.py` (fee and payout, decision times, filters, grouping, cluster statistics), `test_sharp_snapshot.py` (de-vig, fee, first-edge choice, Gamma parsing, bootstrap) and `test_maker_sim.py` (book lookup, fills, post-only, fee, inventory cap, scoring) pass, as does the `pm_close_study.py` self-check. `pm_calibration.py` has two inline asserts. Nothing tests sampling, paging, the ADD rule, the integrity filter, the informed fair values or the hand-written verdicts.

## Current state

No ledger and no positions. All five reports are dated 2026-11-20. The favourite, snapshot and maker tables re-run exactly from the caches. Sleeves that lean on these studies: tennis 278 settled at a stored +0.5%; soccer, NBA and other 17 rows, 16 open; any-category 69 open.

## Audit evidence (re-run)

1. **US politics, the only ADD, is two election nights.** 180 of 571 bets were decided a week before the 2026 midterms (+3.2%) and 54 in October 2024 (+5.4%); the other 337 earned +0.06%. The holdout is 92% midterm bets. Clustered by decision day the interval is −1.1% to +3.4%, which fails the ADD rule. With no edge anywhere the rule still adds a group 43% to 94% of the time.
2. **50-50 markets are dropped.** 1,487 otherwise-eligible markets: ATP 1.8%, WTA 1.9%, CS2 6.4%, boxing 7%, cricket 3.7%. Paid at $0.50, the "existing" blend falls from +0.8% to between +0.2% and +0.5%. Four tennis ledger losses match this list.
3. **Calibration edge.** On the 460 trades timed from a scheduled end date the 7-day edge is +0.9% (t = 1.35), against +1.48% (t = 3.56) reported. Legs that closed over 7 days early add 82 trades and no wins. The cleaner favourite backtest gives +0.7% before costs and −0.55% after for non-sports at 0.90–0.97.
4. **Maker fill rule.** With a 25% share of prints at the quote, economics moves from +10.7% (−4% to +27%) to +13.1% (+0.3% to +25.8%) and meets every pass condition. Sports is about zero and weather stays negative. Economics is positive in each of three years, on roughly $2,000 of capital.
5. **Close-study verdict text is ten times too small.** Pooled slopes are 9.9 and 3.2 bp per 10 points at 10:00 and 15:00, not 1 and 0.3. Holm p is still 1.
6. **"Existing +0.8%" is not the forward rule.** 899 of 962 soccer bets are NO-side or draw-market bets the sleeve never takes. What the scored tests trade: +1.1% (−1.6% to +3.5%), 514 bets.
7. **Paging stops silently at about 2,100 events** in 57 tag-weeks (crypto 33, soccer 16, tennis 8).
8. **Calibration edge table** prints a trade-weighted mean beside an event-weighted t: Kalshi 7-day shows +1.18% with t = 0.00.

Checked and clean: close-study dates (outcomes match Alpaca closes over 99%), maker game start times and candles, and the snapshot study, whose ten as-registered bets were all game mismatches.
