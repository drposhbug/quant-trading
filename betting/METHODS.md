# Betting Methods — Full System Explanation

*Polymarket sports trading system, September 2026. Written for external review —
self-contained, all numbers from the repo's own backtests and live measurements.*

## The core finding everything is built on

We tested whether statistical models (Elo, xG, XGBoost, logistic regression on
rank/form/market features) can out-predict the sportsbook closing line. Three
sports, walk-forward validation, log loss against the de-vigged Pinnacle close:

| Sport | Sample | Result |
|---|---|---|
| Soccer (EPL) | 12,704 matches | Model log loss 0.977 vs market 0.959 — model loses |
| NBA | 23,074 games | Model loses in 13/13 seasons (gap +0.020) |
| Tennis (ATP+WTA) | 15,825 matches | Model loses in 3/3 years (gap +0.055) |

In every disagreement bucket, the market was closer to the truth than the model.
A model fed *only* the market's own probabilities also scored worse than the
market (tree quantization noise). **Conclusion: no predictive edge exists in
these features. All methods below are execution and market-structure edges,
not prediction.**

## Method 1 — Sharp-line convergence trading (primary, running dry)

**Thesis:** Polymarket normally tracks the sharp sportsbook line within ~1–3
cents (measured: divergence std 3¢, only 4% of quotes stray >3¢). When PM
strays further, the sharp line is the better estimate, and the stray is the
trade. Profit is the price move back to fair, not the game outcome.

**Fair value:** Pinnacle's moneyline, de-vigged with the power method (solves
for the exponent making both implied probabilities sum to 1 — removes the
favorite-longshot skew that proportional de-vig leaves). Fallback chain:
BetOnline, lowvig, Bovada, DK, FanDuel, MGM. A "sharp consensus" (average of
Pinnacle + Betfair exchange + lowvig + BetOnline de-vigs) is logged in parallel
to test whether an ensemble tracks the close better than Pinnacle alone.

**Entry rules (all must hold):**
- PM best ask ≥ 3¢ below fair (covers taker fee + spread)
- Price between 5¢ and 95¢ (rails have no room / are lottery tickets)
- Bid-ask spread ≤ 10¢ (gaping books are where stale-quote phantom edges live)
- Sharp line ≤ 90 minutes old (a stale fair value is not a fair value)
- Game not started and >20 minutes to kickoff (in-play PM price vs frozen
  pre-match book line produced a phantom +19.6% "edge" — hard guard)
- Sizing: fractional Kelly on the sharp-line edge, capped by resting book depth
- Portfolio: max 20 open positions, max 50% of bankroll deployed, one position
  per market token (in a 2-way market YES-on-home IS NO-on-away — same token)

**Exit rules (in priority order):**
1. Always flat 20 minutes before kickoff (never hold through the game)
2. Stop: sharp line moves 5¢ against entry (thesis was wrong — labeled honestly)
3. Converged: PM mid within 1¢ of fair (edge banked)
4. Take-profit: bid 6¢ above entry

**Fees:** Polymarket taker fee 0.03·p·(1−p) per share (charged since 2026-03);
makers pay zero — see Method 4.

**Status:** paper trading against the live order book (simulated fills at real
resting size). 16 open dry positions, first full round trip completed
(converged exit, −$0.25 after fees on a 1¢ move).

## Method 2 — Best-price execution / line shopping (the only validated +ROI)

**Thesis:** the same bet at a better price needs no prediction. Measured value
of taking the best available quote instead of an average one:

| Market | Shopping value per bet |
|---|---|
| Tennis (15,825 matches, 3 price levels quoted) | +2.88% vs sharp line; best-of-book overround 0.997 (below 1.0) |
| MLS (live snapshots) | +8.9% (all books) / +4.5% (US-only) |
| EPL (live snapshots) | +3.4% / +2.1% |

**The one strategy with a validated positive backtest ROI depends on this:**
EPL market-anchored bets at BEST price: **+6.0% ROI, 90% CI [+0.4%, +11.6%],
P(ROI>0)=96%, 2,165 pre-registered bets.** The same bets at average odds:
+0.9% (noise). The edge is entirely in paying less.

**Implementation:** 10-book snapshot per sport (flat API cost), rosters
tailored per sport — soccer keeps MLS-verified books, US sports carry lowvig
(near-Pinnacle prices, low margin) plus diverse soft retail books (espnbet,
hardrockbet, Bovada) where mispricings live.

## Method 3 — Tennis favorite-longshot bias (pre-registered forward test)

**Thesis:** Polymarket overprices tennis longshots and underprices heavy
favorites. Retro on all settled Wimbledon 2026 singles: favorites priced
0.80–0.95 won 97.4% (37/38) → **+11% ROI net of fees** held to resolution;
longshots priced ~12% won 2.6% (buying them: −85% ROI). Caveat honored: the
bucket was chosen after looking (p≈0.04, post-hoc), so the rule was frozen in
advance and is now forward-tested:

> Buy any PM singles favorite priced 0.80–0.95 pre-play, flat stakes, hold to
> resolution. No discretion, no exits.

**Guards learned live:** next-day matches only (guarantees pre-play entry);
the *market price* must be 0.80–0.95, not just any ask (fresh thin books
quote junk asks — the naive rule tried to buy both players of one match "at
0.87"); coherent two-sided quote required (spread ≤5¢, ask within 5¢ of price).

**Why hold to resolution:** measured — tennis mispricing pays at settlement.
Pre-match drift ("buy early, sell before play") is dead: −3.3%/trade as taker.

## Method 4 — Maker vs taker execution (measuring, not yet betting)

Takers pay the fee and cross the spread; makers pay nothing and earn the
spread — worth ~2–3%/trade IF fills come. The counterargument is adverse
selection: resting orders fill exactly when the price moves against you.
Every entry signal logs both hypothetical executions (taker at ask with fee;
maker resting at bid+1¢, filled only if the market trades through, cancelled
if fair falls to the quote). Scored against the last pre-kickoff mid.
Verdict rule: whichever nets more per signal after 30 scored signals becomes
the live execution mode.

The same ledger also settles the exit question: every signal is additionally
scored at RESOLUTION (token worth 1 or 0), so after 30 settled signals the
data picks between A (exit at the pre-kickoff close — take the move) and
B (hold the same entry to settlement — take the outcome). CLV per entry-edge
bucket (2–3¢ / 3–5¢ / ≥5¢) accumulates in parallel, so entry-threshold and
staleness tightening is decided out-of-sample rather than by fitting a grid
to history.

## Method 5 — Decision gates (how anything goes live)

- **CLV (closing line value) is the go-live metric**, not backtest ROI: does
  the entry price beat the last pre-kickoff price? Sustained beat-the-close
  >55–60% = real edge; ~50% = the divergences were noise.
- **Per-sport KEEP/CUT:** each sport needs 30+ scored paper entries; negative
  mean CLV cuts it from the tracked list.
- **Live trading is triple-locked** (flag + env var + key) and requires weeks
  of positive paper CLV first. Bet sizing refuses model-based stakes for any
  sport whose model failed its diagnostic (all of them, by design).

## Rejected on evidence (do not re-add)

- Stats/Elo/xG/ML models as betting signals — lose to the close in 3 sports
- EV-threshold betting rule (p·odds−1 > t) — tested, lost to the price-gap rule
- Model/market probability blending — validation weight ~0.2, only ties market
- Pre-match drift trading in tennis — −3.3%/trade as taker
- Buying longshots — −85% ROI measured
- In-play trading — a latency war against faster actors

## Current yearly ROI expectation (Monte Carlo, 20k sims)

From the validated EPL edge alone (~240 bets/yr): median +12%/yr at 1% stakes,
+21% at Kelly, with ~1-in-3 losing years. If paper CLV validates the scanner
across NFL/MLS/MLB/WNBA (~720 bets/yr): median +42%/+84%. With hourly line
refresh (~1,500 bets/yr): median +109%/+248%, losing-year odds fall to ~17%.
Oversizing (5%/bet) raises the *mean* to +121% but drops the *median* to +7.6%
with 48% losing years — volume scales ROI, stake size destroys it.

## Questions worth asking this system (suggested critique prompts)

1. Is the 90-minute fair-line staleness window too generous for a venue that
   reprices on news? What invalidation rule would be better?
2. Is scoring maker fills as "ask ≤ resting price" too generous (queue
   position, partial fills)?
3. Does exiting at convergence forfeit the settlement edge the tennis retro
   found? Should soccer positions also be held to resolution?
4. Is the favorites forward test's 0.80–0.95 band still justified once the
   post-hoc selection is acknowledged, or should the band be widened and
   bucketed at analysis time?
5. What does adverse selection look like on Polymarket specifically, where
   flow is retail-heavy rather than sharp?
