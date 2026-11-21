# pm_trader: Polymarket sharp-line dry trader and execution

## Purpose

Buy a Polymarket (PM) sports token when its best ask is more than 3 cents below a "fair" probability taken from a sportsbook line, then sell when the price comes back or before kickoff. Paper ("dry") only: fills are simulated against the public order book. A never-traded "probe" ledger is meant to compare taker with maker execution and exit-at-close with hold-to-settlement.

## Data flow

1. `log_prices.py` (three runs a day) makes one Odds API call per sport, finds each fixture's PM event by team-name search (`odds_compare.gamma_find_event`) and reads the live book. Every row of a run carries the run's start time as `snapshot_time` (log_prices.py:200).
2. `trader.py --once` (every 10 minutes) calls `run_pass` (trader.py:485):
   - `latest_fair_lines` (241): newest snapshot per fixture. Fair = Pinnacle, else the first of BetOnline, lowvig, Bovada, DraftKings, FanDuel, BetMGM quoting every outcome (analyze_prices.py:117). De-vig is the power method for 2-way markets but plain proportional for 3-way soccer (analyze_prices.py:72-80); METHODS.md says power.
   - then `manage_exits` (263), `find_entries` (309), `manage_probes` (412), `settle_probes` (442).
3. Token ids come from `resolve_tokens` (183): Gamma search, cached for good under home|away|UTC date (196).
4. Orders go to `Executor` (polymarket_exec.py). Dry mode: a buy fills at the best ask, a sell at the best bid, each capped by the size at that one price level (189-215).
5. Output: tables `positions` and `exec_probes`; `--report` prints P&L.

## Decision rules and parameters

Entry, all must hold:
- fair - ask > 0.03 (trader.py:69, 128); ask between 0.05 and 0.95 (124); at least 5 shares at the ask (122).
- spread <= 0.10, checked only when a bid exists (70, 126).
- fair no older than `MAX_FAIR_AGE_MIN`: 10 in the repo (81, 335), 90 in the copy that actually runs.
- more than 20 minutes before the Odds API kickoff (80, 332).
- more than 12 hours out: also needs a consensus of two of Pinnacle, Betfair, lowvig, BetOnline, both gaps >= 0.05, half stake (74-76, 380-387).
- one position per fixture-outcome and per token (312-316); 20 positions and 50% of bankroll at most (71, 84, 321-326).
- The better of the YES and NO token is taken per outcome (347-357).

Sizing: stake = bankroll x min(0.25 x edge / (1 - ask), 0.05) (bet_sizer.py:61-62, 123-133, 164-166); shares = min(stake / ask, shares at the ask) (trader.py:388); 250 dollars per order at most (polymarket_exec.py:53, 186). Bankroll is fixed at 1,000 (trader.py:583).

Exit, first match wins (trader.py:132-166):
1. now >= kickoff - 20 min: `pre_kickoff` (153).
2. fair <= entry - 0.05: `stop` (79, 155).
3. fair within 1 cent of its entry value and mid <= entry - 0.02: `adverse` (72, 157-161). Not in METHODS.md.
4. mid >= fair - 0.01: `converged` (77, 162).
5. bid >= entry + 0.06: `take_profit` (78, 164).

The sale is at the bid; P&L = (exit - entry) x filled shares - fees (289-297).

Fees: price x shares x bps / 10,000 per side (polymarket_exec.py:110-112); bps is read from the CLOB or defaults to 100 (52, 83-94, 166-179).

Probes: one per signal per token (trader.py:367-374). Maker price = bid + 1 cent, at most ask - 1 cent (363). "Filled" when ask <= maker price, "cancelled" when fair - maker price <= 0.015, cancel tested first (436-439). Scored at the first pass after kickoff - 20 min (427-428); verdicts after 30 (543, 570).

Live lock: `Executor.from_env` returns dry unless `live=True`, `POLYMARKET_LIVE == "1"` and a key is set (polymarket_exec.py:142-150). Orders are sent only in `_live_order` (217-237), reached only in live mode. Nothing else builds a live executor, no scheduled job or workflow passes `--live`, and five lock combinations tested offline all came back dry: no path places a real order without all three. Weak point: the env flag and the key sit in the same `.env` that trader.py loads (trader.py:588-592), so once both are saved the flag alone arms it.

## Assumptions the code makes

- The PM event found by name search is the fixture's own game, so "fixture not started" means "token's game not started".
- A snapshot's Pinnacle price is as fresh as `snapshot_time` (the bookmaker's `last_update` is ignored).
- Any book in the fallback chain is "sharp".
- The best bid can absorb the whole position, and a failed exit will work later.
- The task runs every 10 minutes without gaps.
- The fee is proportional to notional (the repo's stated fee is 0.05 x p x (1 - p) per share).

## What the tests cover

`test_pipeline.py --offline`: 89 pass, 0 fail. Covered: 2-way de-vig, best-price helpers, Kelly cap and model gate, dry buy and sell on a synthetic book, the entry and exit pure functions, positions open/close, the lock with no env set.

Not covered: the adverse exit (no test passes `fair_at_entry`), spread and staleness guards, the early gate, everything in `run_pass` (exits, entries, probes, settlement), the report, token matching, the fee read, partial fills, missing bids, 3-way de-vig, the live order code.

## Current state (2026-11-21)

- The scheduled job is the Windows task "PolymarketTraderDry", every 10 minutes, running `C:\Users\tyler\OneDrive\Documents\Polymarket sports betting`, not `betting/`. That copy has the 90-minute rule, no game-matching fix and a crashing settlement step. Last run 00:49 local today.
- Ledger (identical in both copies): 249 dry positions, 2026-09-10 to 2026-11-08. 245 closed: -76.16 on 4,797.60 (-1.6%), fees 84.99. Exits: adverse 172 (-819), converged 32 (+514), take-profit 23 (+212), pre-kickoff 18 (+17), stop 0. Four still "open" since September; all four tokens settled at zero (-100 not booked).
- Of 218 positions whose token has a known game start, 205 held a different game's token and 161 were entered after that game began.
- 43 closes were partial fills; the unsold shares (cost 550.58) vanished from the ledger.
- Corrected P&L: about -264 with the four write-offs and the dropped shares at the exit bid; about -459 with the stated fee as well.
- Probes: 181 (119 open, 84 of them past kickoff; 0 settled).
- No entry or probe since 2026-11-09: MLB and WNBA ended; NFL, EPL and MLS are tracked, the NBA is not.
- Live trading: not possible today. No job passes `--live`, and `.env` is only 32 bytes longer than its template, so the wallet key is almost certainly blank (file not opened).
- Method 1: `reports/sharp_snapshot_results.md` found no PM ask 3 points below Pinnacle in 10,975 clean rows (largest 2.7). The ledger agrees: without other games' tokens at most 44 positions remain, and they lost money apart from three accidental in-play exits. With correct matching the rule has nothing to buy.
