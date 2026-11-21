# Sports betting methods under outside evidence (sports_execution)

Written 2026-11-21. Read-only review. [calc] is my own calculation from the data named; scripts are in the scratchpad under `storm/sports_execution/`. `stat_power.md` covers the power of each sleeve, so this note tests the three claims the sports side rests on. The shared web-search budget ran out before the last lookups (listed at the end).

## Findings

1. **"Polymarket strays from the sharp line and converges" is not supported.** The repo found no 3-point gap in 10,975 same-instant rows (`reports/sharp_snapshot_results.md`). Outside work points the same way: Polymarket NBA prices are "broadly well calibrated" and recalibration adds nothing ([arXiv 2604.20421](https://arxiv.org/abs/2604.20421)); Kalshi moneylines sit on the diagonal 30–240 minutes before expiry ([arXiv 2607.14430](https://arxiv.org/abs/2607.14430)); single-market arbitrage on Polymarket NBA lasts a median 3.6 seconds ([arXiv 2605.00864](https://arxiv.org/abs/2605.00864)). Method 1 does not survive.
2. **The July fee removed the venue discount.** The sports taker coefficient went from 0.03 to 0.05 on 2026-07-10 ([changelog](https://docs.polymarket.com/changelog)). Since then Polymarket asks plus fee sum to 1.032 on two-way games and 1.054 on soccer; Pinnacle's own prices sum to 1.032 and 1.046 [calc: 4,758 filtered pre-game snapshot-games, `price_snapshots`]. `METHODS.md` still says 0.03.
3. **The +6.0% EPL result is the average-to-best price gap.** Betting every outcome blindly returns −7.2% at average odds and −1.2% at maximum odds, a gain of 5.95 points from the price column alone; the repo's bets gain 5.1 (+0.9% to +6.0%) [calc: 7,980 matches, `matches`]. Its 90% interval becomes [−0.7%, +12.7%] at the 95% level the repo now requires [calc]. The odds are Friday-afternoon market maximums, not closing prices ([football-data notes](https://www.football-data.co.uk/notes.txt)).
4. **A US account cannot buy "best".** The best of the eight US-regulated books logged has a 1.041 overround on EPL, equal to the backtest's average column (1.041–1.058) and far from its maximum (0.993–1.023) [calc: 2,528 snapshot-games]. The attainable row is the +0.9% one.
5. **Line shopping pays briefly.** The same rule earned 3.5% on 56,435 backtest bets and 8.5% on 265 real $50 bets ($957.50) before the accounts were "severely" limited within months ([MIT Technology Review](https://www.technologyreview.com/2017/10/19/67760/the-secret-betting-strategy-that-beats-online-bookmakers/)). Massachusetts found 57.6% of limited accounts cut to 1–24% of the default stake, and bettors who beat the closing line were the ones more likely to be cut ([MGC, 30 Sep 2025](https://massgaming.com/wp-content/uploads/Meeting-Materials-9.30.25-OPEN.pdf)). In the repo's snapshots the best US-regulated price beat Pinnacle's fair value by over 2% on 104 game-outcomes in 4.4 months: about $360 at $100 a bet, before limits and before the 2026 [90% loss-deduction cap](https://www.kiplinger.com/taxes/new-gambling-loss-deduction-limit) [calc].
6. **Favourite bias exists against the de-vigged price, not the price paid.** The heavy-favourite test rests on "won 95.8–99.3% versus 92–96% priced", where priced means multiplicative fair value. Polymarket favourites are asked 1.8c above that [calc: 413 outcome-snapshots, fair ≥ 0.75]. Tennis favourites at 0.90–0.97, at Pinnacle's actual odds, returned +1.13% in the repo's table (2021 to February 2024, n = 648), +0.14% [−2.2%, +2.3%] from March 2024 to November 2025 (n = 374, specification written before download) and −0.67% at Betfair Exchange odds in 2026 (n = 258, descriptive). The 0.80–0.90 band lost 1.7% out of sample [calc: [tennis-data.co.uk](http://www.tennis-data.co.uk/alldata.php)]. On Kalshi, makers buying above 50c earned +2.6% with a 33% standard deviation before April 2025, mostly outside sports, and the bias was shrinking ([GWU WP 2026-001](https://www2.gwu.edu/~forcpgm/2026-001.pdf)). At a true edge of 0–1% a 300-bet gate passes 3–10% of the time [calc].
7. **The forward tennis test samples a different population.** Only 60 of its 278 settled entries are tour-level main-draw matches; 218 are Challenger, ITF or qualifying. For the 60, Polymarket ask plus fee equals the Betfair Exchange price to +0.09c (standard error 0.28c) [calc]. The repo's backtest lost 4.3% on "other tennis" (`reports/fav_backtest_results.md`).
8. **Closing-line value is sound, but measured badly here.** Against an efficient close, 50 bets can show a 2% edge where results need over 1,000 ([Buchdahl](https://www.sportstradingnetwork.com/article/using-the-closing-line-to-test-your-skill-in-betting/)). The probe ledger shows why a "55–60% beat rate" gate is unsafe: 58 signals beat the close 57% of the time by +3.3c, but 11 closes were stamped after kick-off and 14 more entries claimed edges above 10c. The clean 33 show +1.8c (standard error 0.9c) against a 1.06c fee. The dry trader also charges 1% of notional instead of the published fee: its −$76 becomes −$303 (−6.3%) [calc: `exec_probes`, `positions`].
9. **Maker execution has no subsidy at this size.** Polymarket pays no rebate below $200,000 of monthly maker volume ([docs](https://docs.polymarket.com/programs/maker-rebates)); Kalshi charges sports makers. The repo's simulation earned +1.85c of spread and lost 2.0c to adverse selection within five minutes (`reports/maker_sim_results.md`); one-sided flow predicts maker losses on Kalshi ([Bartlett and O'Hara](https://law.stanford.edu/press/adverse-selection-in-prediction-markets-evidence-from-kalshi/)).
10. **The owner cannot trade the venue being measured.** Polymarket.com blocks US residents. Polymarket US is a separate book charging about 0.07·p(1−p), closed in Nevada, with no new sports contracts in Michigan ([CryptoSlate, 10 Nov 2026](https://cryptoslate.com/prediction-markets/polymarket-us-review/)). Kalshi's sports contracts won in the Third Circuit and lost in the Sixth and Ninth; two Supreme Court petitions are pending ([Foley tracker, 10 Nov 2026](https://www.foley.com/?p=130779)).

**Verdict.** Stop Method 1 (dry convergence trader) and Method 4 (maker and taker probes) now. Withdraw the "validated +6%" label and the yearly return projections in `METHODS.md`. Close tennis Test 1 (0.80–0.95): 278 bets, +0.5%. Keep one pooled favourites ledger as `stat_power.md` proposes, and expect it to fail. Nothing on the sports side helps with the selloff.

## Evidence table

| Question | Evidence | Source |
|---|---|---|
| Polymarket NBA calibration, 2026 season | Brier 0.2034, calibration error 0.027, 1,136 markets | [arXiv 2604.20421](https://arxiv.org/abs/2604.20421) |
| Kalshi NBA, MLB, NHL moneylines, March to May 2026 | 23 million trades; calibrated 30–240 minutes out, distorted only in the final minutes | [arXiv 2607.14430](https://arxiv.org/abs/2607.14430) |
| Taker overround after fee | Polymarket 1.032 / 1.054; Pinnacle 1.032 / 1.046; the same asks at 0.07: 1.041 / 1.067 | [calc] |
| EPL blind bets, 2005–2026 | −7.17% average odds, −1.23% maximum odds | [calc] |
| EPL best of book | US-regulated 1.041; all logged books with Pinnacle and Betfair 1.019 | [calc] |
| Tennis 0.90–0.97 at the price paid | +1.13% (648), +0.14% (374), −0.67% (258) | [calc] |
| Tennis 0.80–0.97, Betfair Exchange 2026 | +1.2% gross, +0.55% [−2.0%, +3.0%] after a 0.05 fee, n = 919 | [calc] |
| Forward tennis ledger | 244 of 278 won at a 0.870 average ask: +0.48% [−4.1%, +4.8%] | [calc: `paper_favorites.sqlite3`] |
| Kalshi takers and makers, to April 2025 | −31.5% and −9.6% average return | [GWU WP 2026-001](https://www2.gwu.edu/~forcpgm/2026-001.pdf) |
| Accounts limited, Massachusetts | 0.64% of accounts; 12.7% of those to under 1% of the default stake | [MGC](https://massgaming.com/wp-content/uploads/Meeting-Materials-9.30.25-OPEN.pdf) |
| Kalshi market data | Public endpoints need no key | [Kalshi docs](https://docs.kalshi.com/getting_started/quick_start_market_data) |

## Ideas worth a pre-registered test (or why none)

No new signal is worth a trial. Two changes would make the surviving ledger informative:

1. **Score the price gap at a venue the owner can use.** For each entry store `ask_size` (returned by `public_book` and discarded), the same-instant best ask on Kalshi, and a reference price: Pinnacle from `price_snapshots`, or the Betfair Exchange price from tennis-data for tour tennis. Cost at 0.07·p(1−p). Pre-registered: mean of (reference raw price − ask − fee) above 0.5c with a 95% interval above zero over the first 150 matched entries per sport. The gap's standard deviation is about 2c, so this resolves in weeks. My estimate that it passes: 0.2.
2. **Label the population.** Add `tier` (tour main draw, qualifying, Challenger, ITF) to each tennis entry, parsed from the Gamma title. The pooled test's primary stratum is tour main draw plus the seven soccer leagues and NBA; lower tiers are reported separately.

A cheap low-prior study: soccer and NBA favourites at Pinnacle's raw closing price across football-data's full league set. Estimate 0.05.

## What I looked for and did not find

- A published same-instant Polymarket-versus-Pinnacle measurement for 2026; the repo's study is the best available.
- A sports-only split of maker and taker returns after the 2025–26 fee changes.
- The odds profile of the 2,165 EPL bets: `xgboost` is not in the venv and `betting/` code is off limits, so a matched blind baseline is not established.
- A primary Polymarket US fee schedule (0.0695 flat or tiers to 0.095), the status of the loss-cap repeal, and the tax treatment of event contracts.
- Integrity-alert data for lower-tier tennis, and current sportsbook sign-up offers, which are the one sports-side cash source with a high prior [memory]: the search budget ran out.
