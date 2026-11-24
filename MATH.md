# The math, and what was actually proven

Code: [model.py](model.py) (model), [backtest.py](backtest.py) (tests), [candles.py](candles.py) (candlestick tests).
Results: [reports/backtest_results.md](reports/backtest_results.md), [reports/candles_results.md](reports/candles_results.md).
Research behind every choice: [reports/Quant trading for Tesla and big tech.md](reports/Quant%20trading%20for%20Tesla%20and%20big%20tech.md).

## 0. What "prove" can mean here

No backtest proves future profit. What we *can* do is state falsifiable claims, test them on 2015-2026 data with
methods that punish luck and overfitting, and only ship what survives. Every claim below has a test and a pass bar.

| Claim | Test | Result |
|---|---|---|
| The model has a positive Sharpe | stationary bootstrap, deflated Sharpe | **Pass** (CI 0.69–1.84, DSR 0.999). Raw 1.26; **1.14 after subtracting T-bills** (equal-weight: 1.18) |
| The risk engine cuts drawdowns vs buy & hold | bootstrap P(MaxDD worse) | **Pass vs full-exposure equal-weight** (p = 0.019, −22.5% vs −44%); **fail vs QQQ** (p = 0.08). Nasdaq-100 1985–2026: −39% vs −83% buy & hold |
| The drawdown cut is more than just holding less stock | bootstrap P(MaxDD worse) vs equal-weight scaled to the model's vol | **Fail.** Ex-post vol-matched EW (×0.64, hindsight): Sharpe 1.255, MaxDD −30%, p = 0.62. Ex-ante vol-targeted EW (20%/60d, no regime filter): Sharpe 1.30, MaxDD −29% at 20% vol, p = 0.28 |
| No sign of overfitting within the parameter grid | PBO via CSCV over 60 distinct variants | **Pass** (0.18 < 0.30). PBO and DSR cover only this grid, not the universe, sizing, signal or research choices made around it, so they cannot rule out overfitting from those |
| Beats QQQ risk-adjusted | HAC alpha t-stat, excess of T-bill | **Pass** (9.1%/yr, t = 3.29, bar 3.0; inflated by selection bias, §7) |
| Beats equal-weighting the same 12 stocks (daily rebalanced, same 5bp cost) | bootstrap P(Sharpe ≤ EW), HAC alpha | **Fail** (p = 0.50, excess-return alpha 1.6%/yr, t = 0.67) — same Sharpe; ex-T-bill Sharpe 1.14 vs EW 1.18 |
| Survives one day of execution delay | weights shifted one extra day | **Pass** (Sharpe 1.23, MaxDD −24%, CAGR 22.8%) |
| Works on names chosen without hindsight | same engine on the end-2014 top-10 US tech list ([universe_study.py](universe_study.py)) | **Much weaker:** CAGR 15%, Sharpe 0.98 (0.84 ex T-bill), MaxDD −22%. This, not 23%/1.26, is the honest forward expectation |
| Correlation-aware sizing (HRP) beats inverse-vol | paired bootstrap | **Fail** (P(HRP ≤ shipped) = 0.64; Sharpe 1.245 vs 1.259) → not used |
| Correlation structure predicts returns | rank IC + 110 lead-lag pairs, Holm | **Fail** (1 of 118 tests passes; too small to trade) — [correlations_results.md](reports/correlations_results.md) |
| Macro / cross-asset (VIX, rates, dollar, credit, oil, BTC) or buy-the-dip rules predict | HAC t, Holm, split halves | **Fail** (0 of 44) — [macro_results.md](reports/macro_results.md) |
| Earnings & calendar effects (pre-FOMC, turn-of-month, PEAD, peer spillover) | event study, Holm | **Fail** (0 of 9) — [events_results.md](reports/events_results.md) |
| Prediction-market odds (Kalshi/Polymarket) lead returns | HAC t, Holm, outlier trim | **Fail** (4 of 113 formal passes, all driven by 2-3 days) — [pm_results.md](reports/pm_results.md) |
| Trump posts predict returns | placebo-date test, Holm | **Fail** (0 of 295) — [trump_results.md](reports/trump_results.md) |
| Insider buying, short interest, TSMC monthly sales | event study / rank IC, Holm | **Fail** (0 of 23) — [altdata_results.md](reports/altdata_results.md) |
| Adding bonds/gold/other stocks beats the shipped universe | paired bootstrap, 12 variants | **Not significant** (best: GLD P = 0.024, IEF+GLD P = 0.029, vs bar 0.004); T-bills on idle cash adopted — [universe_results.md](reports/universe_results.md) |
| Per-stock 200-day exit beats the index-level filter | paired bootstrap | **Fail** (P(≤ shipped) = 0.83; lower CAGR and Sharpe) |
| Short QQQ (−25%) in risk-off instead of only halving | paired bootstrap, 5bp + 1%/yr borrow | **Fail** (Sharpe 1.23 vs 1.26, MaxDD worse −24% vs −22.5%, P(≤ model) = 0.80); risk-off only 18% of days, V-shaped recoveries whipsaw it |
| 20% Cboe S&P 500 PutWrite (PUT) sleeve | paired bootstrap vs 100% model | **Fail** (Sharpe 1.24, P = 0.72). PUT 2007–2026 alone: CAGR 7.1%, Sharpe 0.56 vs S&P TR 10.7%/0.62; −35% in 2008, −29% in Mar 2020: put-selling is lower-beta equity, not a free premium |
| Earnings-announcement premium across the point-in-time S&P 500 (2017–2026, 19,309 trades) | pre-registered, NW t, t > 3 bar; 80/20 mix bootstrap | **Fail** (−8.3%/yr vs EW S&P at 5bp, t = −1.43; ~−2%/yr before costs; mix Sharpe 1.15 vs 1.32, P = 0.98) — [earnings_premium_results.md](reports/earnings_premium_results.md) |
| Buy the post-earnings dip (reaction-day residual ≤ −5%, hold 10 days), point-in-time S&P 500 2016–2026 | per-date mean t, 10bp round trip | **Fail** (n = 3,224: −0.28% vs market, 47% win, t = −1.39; drops keep drifting). Reactions are 50/50 up/down, not "nearly always down" |
| Trend + reversal signals predict returns | rank IC t-stat, bootstrap vs basket | **Fail** (rank IC t = 1.66 next day, 1.36 over 5 days, bar 2; signal model worse, P = 0.98) → removed |
| Candlestick patterns predict returns | 39 tests, Holm correction, split-sample | **Fail** (0 of 39 pass) |

**Plain-English conclusion:** there is no proven edge, in prediction *or* in risk control. The model is a
long-only basket of these stocks run at about 64% of equal-weight's volatility (about 80% invested on average, tilted
to the calmer names). Its Sharpe (1.26 raw, 1.14 after T-bills) is
the same as equal-weighting the same names, and its drawdown (−22.5%) is about what you get by simply holding 64% of the
equal-weight basket and the rest in cash (−30% with hindsight scaling; the bootstrap cannot tell them apart, p = 0.62).
The value of the engine is holding a *fixed risk level* mechanically: on the Nasdaq-100 since 1985 it turned an −83% buy-and-hold
drawdown into −39% (2000–02: −77% → −41%) at a higher Sharpe (0.78 vs 0.63), though with lower CAGR (11.8% vs 14.1%).
The 23% CAGR comes from names picked knowing they won; the same engine on the end-2014 top-10 tech list earned
**about 15% a year at Sharpe ~1.0 with a −22% drawdown**, which is the realistic forward expectation (less if tech
lags). What the model does give is a disciplined, cheap, mechanical way to hold the basket at a fixed risk level.
The live monitor used to halve a name's weight before earnings; that rule was never backtested, so it was **removed
2026-11-18**: live now trades the backtested target weights (idle cash in T-bills, universe_results.md C1).

## Change control

The model (model.py `P`, universe, monitor rebalance logic) is **frozen as of 2026-11-19**. Paper-trade the frozen
model for 12 months (to 2027-11-19) and compare it with the backtest using `track.py`. A future change ships only if:

1. it beats the frozen model in **one pre-registered paired stationary-bootstrap test** (P < 0.05), written down
   (hypothesis, metric, data window) before the run, on the shipped universe **and** the end-2014 top-10 tech list;
2. it is decided at a **scheduled review**, never during a drawdown;
3. it is logged below with date and test result.

**Pre-registered challengers for the 2027-11-19 review** (written before any run):

1. **Equal base weights inside the frozen engine** (`P["sizing"] = "ew"`): identical to the frozen model in every way
   (eligibility, caps incl. SPCX/ANT, 20% vol target, QQQ 200d regime, costs) except equal instead of inverse-vol base
   weights, so the test isolates one change. (Redefined 2026-11-19 before the window opened, after Grok and GPT-6-Astra
   noted the ex-ante EW row changes four things at once.) Hypothesis: its Sharpe beats the frozen model's. Test: paired
   stationary bootstrap (L = 20, B = 2000), P(Sharpe_EW <= Sharpe_frozen) < 0.05 on the shipped universe **and** the
   end-2014 top-10 tech list, over the full backtest window extended by the 12 paper-trading months.
   Baseline today: shipped 1.306 vs 1.259 (P = 0.15); end-2014 list 0.895 vs 0.975 (P = 0.97). It must win on both.
   **Closed 2026-11-19: fails pre-registration** — it loses on the honest end-2014 universe, and 12 months of paper data
   cannot resolve a 0.05 Sharpe gap (≈ centuries of data for 80% power), so a shadow book would only add noise.

**What the 12-month paper year tests: execution, not skill** (thresholds set now, checked with `track.py` and the logs):
- tracking error, live vs backtest (compounded between logged days): ≤ 3%/yr annualised and no persistent drift;
- missed rebalance sessions (no equity_log row on a trading day): ≤ 5 over the year;
- fill shortfall (order fill price vs that day's close, from Alpaca order history): average ≤ 10 bp per trade,
  counting fills from the first logged rebalance onward (the one-time setup orders queued 2026-11-18 and filled at the
  2026-11-19 open are excluded — decided 2026-11-20 before any paper-year fill was scored);
- zero unexplained orders, positions or state errors.
Failing any of these means fixing the plumbing, not changing the model.

**Pre-registered promotion / stop rules for every paper sleeve** (2026-11-20, before any sleeve had data; encoded in
`scorecard.py`, which judges them daily and posts to Discord). Nothing is judged before its minimum n. A PASS only
sends a recommendation; **real money is never allocated automatically**, the user decides. A STOP is a recommendation
to end that experiment. Rules change only at a scheduled review, logged below, and a changed rule restarts its n.

| Experiment | Benchmark | Min n | Pass test (all must hold) | Stop |
|---|---|---|---|---|
| Stock model (Alpaca paper #1) | frozen-model backtest over the same days (QQQ for context) | 250 logged sessions | the four execution thresholds above (TE ≤ 3%/yr, missed ≤ 5, mean fill shortfall ≤ 10 bp, no positions outside universe + SGOV) | none automatic: −10%/−20% drawdown tiers alert; decide at the scheduled review |
| Options iron fly (Alpaca paper #2) | 0 (no trade) | 120 closed trades | mean P&L per trade > 0 with t > 2, at the logged worst-case fills (natural − $0.05) | account equity −10% from peak |
| Sports paper bets | market price (implied probability) | 200 settled bets | ROI bootstrap 95% CI > 0, and ROI > 0 in both chronological halves | ROI < −10% after ≥ 100 settled bets |
| Polymarket IPO brackets | naive IPO price × 1.15 | 30 resolved IPO events | bracket-implied CRPS lower than the naive baseline (paired sign test p < 0.05) | none (no money at risk) |
| Tennis favourites ([tennis_favorites.py](betting/tennis_favorites.py), heavy-favourite test) | Polymarket ask + taker fee 0.05·p(1−p) | 300 settled entries with ask 0.90–0.97 logged from 2026-11-20 | mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both chronological halves | none (paper only) |
| Soccer/NBA favourites ([sport_favorites.py](betting/sport_favorites.py)) | Polymarket ask + taker fee 0.05·p(1−p) | 300 settled per group | per group (soccer: favourite's win-YES, price and ask 0.80–0.95, EPL/La Liga/Bundesliga/Serie A/Ligue 1/MLS/UCL; NBA: moneyline favourite 0.85–0.97; entry ≥ 30 min before gameStartTime, hold to settlement): mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both halves | none (paper only) |
| Other-sports favourites, exploratory ([sport_favorites.py](betting/sport_favorites.py)) | Polymarket ask + taker fee 0.05·p(1−p) | 300 settled | NFL/NHL/MLB moneyline favourite 0.85–0.97, same rules and test; no historical basis, so a pass motivates a study, not money | none (paper only) |
| Any-category favourites ([any_favorites.py](betting/any_favorites.py)) | Polymarket ask + market's taker fee | 200 settled | non-sports, non-price markets; side priced and asked 0.90–0.97, spread ≤ 0.03, 7–30 days to end, volume ≥ $10k, objective resolution source: mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both halves | none (paper only) |

| Date | Change | Test | Result |
|---|---|---|---|
| 2026-11-18 | Earnings haircut removed from monitor.py (never backtested; live ≠ tested). | — | — |
| 2026-11-19 | vol_target 0.25 → 0.20, decided before the freeze. | Engine on ^NDX 1985–2026 (no hindsight universe, includes 2000–02 and 2008); rule set before the run: revert if MaxDD at 25% is worse than −45%. | NDX buy&hold: CAGR 14.1%, Sharpe 0.63, MaxDD −83%. Engine 15/20/25%: Sharpe 0.77/0.78/0.77, MaxDD −31/−39/−46.5%, CAGR 9.9/11.8/12.6%. 2000–02: NDX −77%, engine −41%. Bar tripped → 20%. |
| 2026-11-19 | Model frozen. | — | — |
| 2026-11-19 | ANT (Anthropic) removed from UNIVERSE before it listed (weight was 0, so no position change). | 10 large tech IPOs 2012–2024 vs QQQ: median −40% in year 1, −64% over 3 years; bought after this model's 60-day rule, median −33% over the next year; 7 of 10 lagged. Hand-picked famous IPOs (selection caveat). | Removed. SPCX (−8% since its June 2026 IPO, 5% cap) stays until the scheduled review. |
| 2026-11-19 | Measurement fixes (cost drift, rank IC, excess-return alpha); no trading-rule change. | Backtest re-run: costs on the trade from drifted weights incl. first entry; rank IC over names valid on both sides; HAC alpha on T-bill excess returns. | Model Sharpe 1.262 → 1.259, EW 1.261 → 1.255; QQQ alpha t 3.54 → 3.29; EW alpha t 1.03 → 0.67; PBO 0.187 → 0.182. No §0 verdict changes. |
| 2026-11-21 | Live plumbing fixes, no trading-rule change: the T-bill order nets out skipped small stock trims and never sells more T-bills than are held (on 2026-11-20 it had left stocks 5.7 pts over target and cash at −$3.6k); the QQQ freshness check now runs on the unfilled data (it could never fire); the drawdown anchor is the $100,000 start, not the 2026-11-20 snapshot. Set-up errors annotated: the first orders (queued 2026-11-18 17:17 ET, before the freeze at 20%) were sized at the 25% target, 46% invested vs 38%, and the 2026-11-19 rebalance never ran (GitHub cron). Together they cost about 1.6 pts of the account's −5.0% over 11-19/20 (model −3.4%). | test_monitor.py (three regression tests). Decision record: reports/Decision 2026-11-21.md, reviewed by Astra 6.2 and Grok. | Account kept, not reset. |
| 2026-11-21 | **Owner override, ends the frozen-model paper test.** At the owner's instruction the live book (monitor.py `LIVE`) drops the 20% vol target and the risk-off halving: same inverse-vol basket and caps, ~99% gross instead of 34%. Reason: the selloff post-mortem found every predictor null, and the fully invested basket made +15% to +38% in past rebounds vs about +6% for the halved model. The cost: a larger drawdown if the selloff continues (the engine's protection is off). From here equity_log no longer tracks the frozen backtest. Orders queued by a forced run on 2026-11-21 for the 2026-11-23 open. backtest.py and `P` are unchanged. | None, discretionary. | Revert with `LIVE = P`. |
| 2026-11-21 | Options iron fly: entry scan no longer crashes on a report beyond the 30-day calendar (audit options_sleeve-1); risk budget 0.5% -> 2% of equity per spread at the owner's request, since $500 was below one contract's max loss for most names. The sleeve's n restarts at 0 (it had no trades). | test_options.py regression check. | Next entries: AVGO 2026-12-09, ORCL 2026-12-14. |
| 2026-11-23 | **Live book: trend tilt added; no orders while the market is closed.** (1) Live weights x2 for the top third of names by the model's trend score, x0.5 for the bottom third, same gross and caps (`monitor.tilted`). (2) A forced run with the market closed no longer sends orders: queued orders filled at the next open, after the gap, on 11-19 and 11-23 (the latter bought $55,040 on average 8.1% above Friday's closes). Exposure unchanged: fully invested (2026-11-22 decision by odds). Trump posts keep zero weight in sizing (0 of 295, trump_results.md). | [tilt_odds.py](tilt_odds.py), rules written first, three arms; P = share of 2,000 paired bootstrap histories in which the arm grows faster than the live book. Bar: P >= 0.80 on the end-2014 list, > 0.5 in each half of it and on the shipped list. | Trend tilt passes: 0.84 on the end-2014 list (halves 0.76 / 0.78; CAGR 22.0% vs 20.6%, MaxDD −34.1% vs −33.5%); 0.501 on the shipped list, a coin flip (32.6% vs 32.6%). Equal weight 0.22 and 'heavier in what just fell' 0.001 (15.2% vs 20.6%) are rejected. Weak evidence (three arms, one clean universe): paper book only. [tilt_odds.md](reports/tilt_odds.md), [rebound case](reports/2026-11-23%20Huang%20rebound%20case.md) |
| 2026-11-23 | **Monthly self-review added (learn.py, learn.yml).** Early each month the bot re-runs growth_odds, tilt_odds, mini_trend_odds and exit_odds on fresh prices and writes signals/live_config.json, which `monitor.live_weights` reads. It may switch two settings on its own: fully invested <-> the original engine (fully invested stays while P > 0.5 on both deciding rows) and the trend tilt on <-> off (on while P >= 0.5 on the end-2014 list). A setting changes only after 3 reviews in a row ask for it. The 12 other rules tested on 2026-11-23 are re-tested against their own bars; one that passes 3 reviews in a row is flagged on Discord and is never switched on automatically. | Rules for each test written before its first run: [mini_trend_odds.py](mini_trend_odds.py) (four short trends and a performance-chasing rule), [exit_odds.py](exit_odds.py) (five selling rules), [support_study.py](support_study.py) (a level that held before). | First review 2026-11-23: fully invested ahead in 75% and 98% of histories, tilt ahead in 84%, no other rule passes (best short trend 0.07, best selling rule 0.11 against a 0.90 bar; held levels −0.31% a month, t = −1.6). No change to the book. |
| 2026-11-23 | **Neural-network challenger added to the monthly self-review, not to the book.** One hidden layer of 16 units in plain numpy, 14 inputs per stock per day, refitted every 21 sessions on every outcome known by then; its forecast replaces the trend score in the live tilt mechanics. | [mlp_odds.py](mlp_odds.py), rules written first; bar as for mini_trend_odds (P >= 0.90 against the live book on the end-2014 list, > 0.5 in each half, >= 0.5 on the shipped list). | **Fail.** End-2014 list: P = 0.07 (CAGR 20.8% vs 23.8%, 2016–2026), rank IC −0.02 (t = −0.8): it could not order names chosen without hindsight. Shipped list: P = 0.94 (37.8% vs 34.2%), rank IC +0.05 (t = 1.5), which is what a network trained on twelve known winners is expected to show. It is re-fitted and re-tested at every monthly review. [mlp_odds.md](reports/mlp_odds.md) |
| 2026-11-23 | **Network lab and lockbox (mlp_odds.py `--dev`), for a bounded Claude loop.** The loop may change the network's inputs, target and training, one change per experiment, at most 5 per session, scored on development years only (end-2014 list, to 2021-12-31). A change is kept only if its rank IC is 0.01 above the last kept variant, its growth odds against the live book do not fall, and the gain survives leaving out any one stock or year; otherwise the code is reverted. The kept variant then gets one lockbox verdict and is frozen. The network's official bar moves to the years from 2022 on (P >= 0.90 against the live book on the end-2014 list, > 0.5 in each half, >= 0.5 on the shipped list), because the earlier years are now used for tuning. The loop cannot touch the trading bot. | Rules in mlp_odds.py's docstring, written before the first experiment; shaped by Astra 6.2's review (`research_notes/mlp loop/ideas.md`). | Baseline before any experiment: development years rank IC +0.016 (t 0.4), growth odds 0.22; lockbox years 0.07 on the end-2014 list, 0.61 on the shipped list. Not live. |
| 2026-11-23 | **Network lab, rule 2; a forward record; a scheduled Claude task.** Replaces the lab rule in the row above, before any further experiment. The yardstick is now the live book, not the previous network. On the development years (end-2014 list; prices frozen in `lab/dev_prices.csv` and cut at 2021-12-31) a change is kept only if its growth odds against the live book are >= 0.90, above 0.5 in each half and with any one year left out, and its rank IC is above the live trend score's, also with any one stock or any one year left out. Budget: the four experiments written in `lab/queue.md`; the code refuses a fifth, and only the owner can raise it, with a row here. The network's official bar gains a floor: at least 252 sessions after a variant's own date. A forward record starts (`mlp_odds.py --log`, workflow `mlp-log`): one dated forecast per stock after each close, scored 21 sessions later, never rewritten. A scheduled Claude task (cloud routine "quant-trading network lab", weekly) runs the four experiments, then only checks and reports the forward record. It cannot touch the trading bot. | Second review by Astra 6.2 and Grok (`research_notes/mlp loop/round 2.md`), who agreed: a loop that keeps testing on the same six years mostly finds noise (Grok: 60% that the old +0.01 rule keeps a false winner); the old leave-one-out test compared a reduced sample with a full one; a December 2021 forecast was scored with January 2022 prices. Checks: the frozen file reproduces the logged baseline to the last digit with the network blocked; the official run gives the same numbers as the old code on the same prices. | Starting network under rule 2: growth odds 0.22 against the live book, rank IC +0.014 against the trend score's +0.006 over 71 months. What it adds once the trend score is taken out (partial rank IC): +0.091, s.e. 0.039, beaten by 1.3% of shuffled forecasts; one diagnostic, on years already seen. The reviewers' priors that anything here beats the live tilt on new days: about 10% and 5%. Not live. |
| 2026-11-23 | **Pattern-finder added as a shadow (discover_odds.py); lab budget 4 to 5.** The owner asked for a model that "looks for unique trends and makes its own correlations" instead of the textbook inputs. The machine builds 945 candidate patterns from each stock's open, high, low, close and volume and 15 outside series (stocks, bonds, gold, oil, the dollar, sectors, the VIX), and every 21 sessions keeps the 10 that pointed the same way in both halves of what it has seen, one equal vote each. Not live. It logs a dated forecast and the patterns behind it after every close (`signals/discover_*.csv`). | Lab rule 2, unchanged, one run, as the lab's fifth experiment. Definition and frozen data were committed before the run (8a55780). The choosing happens inside the walk-forward, so only forecasts for days it had not seen are scored. Self-checks: it finds two planted patterns among 40, pure noise scores as no skill, no pattern changes when later days are added. | **Reverted.** Growth odds 0.33 against the live book (bar 0.90; halves 0.28 and 0.40; 0.15 without 2019). Rank IC -0.011 against the trend score's +0.006; partial rank IC -0.028. Its patterns were stable (75% kept from one refit to the next) and had held in both halves of its training data, yet did not carry to months it had not seen: where it disagreed with the trend score about two stocks it was right 49% of the time. Four experiments remain for the scheduled task. |
| 2026-11-23 | **Daily calls (daily_calls.py): the pattern-finder rebuilt, judged only on days that have not happened.** The owner asked why the pattern-finder failed and for a machine that predicts every day so it can be seen what comes true. Changes: about 500 stocks (S&P 500 members of 2026-11-18, frozen in `lab/universe.csv`) instead of ten; the 345 patterns without the multiplied pairs; a noise bar in place of a top ten (a pattern votes only by how far its record exceeds what the best of 345 reaches by luck, and not if its latest 252 sessions disagree; nothing over the bar means NO VIEW); three horizons (21 sessions official; 5 and 1 as side boards). After each close it ranks the names, logs favoured and avoided thirds for the market and for the book beside a plain 12-month trend ranking, and scores each call when it comes due (`signals/calls*.csv`, `reports/daily_calls.md`). Not live; no order code. | No test on history: the 2016-2021 window is spent. Rules "v2 2026-11-23" fixed before the first call; a rule change starts a new tally. Verdict only after 20 non-overlapping official calls (about 20 months): worth a real test if at least 15 are right and its rank IC beats the trend ranking's, otherwise it stays a shadow. Why the first one failed, checked on its own run: its ten trusted patterns had rank IC +0.108 in their past and +0.003 in the next 21 sessions; on shuffled outcomes it found patterns that looked as good (0.214 against 0.228; 30% of shuffles looked better). Grok's review: `research_notes/mlp loop/round 3.md`. | No result yet by design. Grok's prior of real skill: about 20% at 21 sessions, 12% at 5, under 10% at 1, lower after costs. |
| 2026-11-23 | **Daily calls: the past test, a probability on every call, and the crowd count.** The owner asked why wait 20 months when the past is all there, asked for a probability on each outcome, and pointed out that many lucky-looking things at once can be one real thing nobody proved. The verdict now has two stages: A, each entry's record on old days (every 5th session from 2019, each call rebuilt with only what was known that day); B, new days confirm at 20, 40, 60... non-overlapping calls. Every call carries the chance that it comes true and each book name the chance that it beats the typical stock, from the old-days record pulled toward 50% and then updated by every real result; the probabilities are scored too (Brier score, bands). Each day the number of patterns that stand out one at a time is logged beside what luck alone gives. | Stage A's rule was committed (2bfb07e) before the past record was computed, and the call rules (22e460e) before that. Weak spots: the list is today's surviving companies, which flatters every entry; six machine results are read on the market board, so one narrow pass would have about a 1 in 4 chance of being luck. | **No entry passes the past test.** Market board, calls that do not overlap. 21 sessions: best guess right 31 of 73 (42%; a coin gets 28 to 45), trend ranking 39 of 73. 5 sessions: best guess 180 of 366 (49%), trend ranking 192. Next session: the sure entry 76 of 124 (61%; a coin gets 51 to 73), average gap +0.14% a day before costs with t = 1.5, short of the 2 required; best guess 197 of 367 (54%). The crowd on 2026-11-23: 75 standouts at 1 session where luck rarely gives more than 43 (real, and mostly the 12-month trend seen through many windows); 24 at 5 sessions and 10 at 21, both inside what luck gives. Stock probabilities all lie between 47% and 53%. |
| 2026-11-23 | **Daily calls, rules v3: the tradeable clock, and a running evidence score; a research round on how to make the machine smarter.** A call made after the close cannot be traded at that close, so learning, the past test and new days now use the return from the next session's open to the close h sessions after the call. New days are judged by a running evidence score, E = 2^(n+1) B(k+1, n-k+1) I_1/2(n-k+1, k+1) for k right of n, readable after every call and confirming at 20, in place of checks at 20, 40, 60 calls. The pattern count in daily_calls.py is 332, not 345 as the two rows above say (15 outside series, not 16). The v2 calls logged for 2026-11-23 are kept and never scored. Research: five Opus researchers, Astra 6.2 and Grok (`research_notes/Smarter machine 2026-11-23/`), decision in `reports/Making the machine smarter (2026-11-23).md`. | Rules committed (9cc1f96) before any call was scored and before the past test was re-run under them. Exploration, not tests (`0 our own numbers.md`): the 332 patterns are about 9 independent ideas; one day's rank IC wobbles by 0.19 where independent stocks would give 0.045, so 500 names carry the information of about 28; the smallest mean IC visible at 21 sessions is 0.025 for one idea chosen in advance and 0.043 for the best of the lot. | **Under v3 nothing stands out at any horizon** (standouts 13, 12 and 9, all inside luck's range; the sure entry has no view). Past test from the next open, market board: next session, best guess right 175 of 367 (48%), trend ranking 176 of 367 (48%, mean -0.07% a day, t -1.6); 5 sessions, best guess 157 of 363; 21 sessions, best guess 31 of 73, trend 39 of 73. Stock probabilities 48.6% to 51.3%. The trend's one-session edge was the overnight step: +2.8 bp a night (t 2.5) against -2.2 bp in the daytime; its worst 5% of days lose 310% and the other 95% make 323%. News shocks predict the size of later moves (1.9 times normal the next session after a stock's own shock; twice normal for a month after a market shock) and not their direction. Next builds, in order: a stock list with the dead companies; shared moves stripped out; nine families with shrinkage; crash control; then earnings, profitability, turnover-split reversal and headlines, one pre-registered test each. |
| 2026-11-23 | **Closing out on the news (news_stop_odds.py): no rule is added; one is a trade-off for the owner.** The owner asked whether the book can lose less by seeing the news and closing out. News is measured as the bot would see it: the market or a stock moving far more than its normal. Six rules on top of the live book: out for 5 sessions after a market shock-down close; out at a gap-down open; half the book for 21 sessions after any market shock; sell a stock after its own shock; drop the trend tilt after a shock; drop it while the tilt's bet is wild. | Rules and both bars committed (8cd0eb3) before the run. Alpaca daily bars, 2018-10 to 2026-11, 5 bp costs, idle money in T-bills. Bar 1, the standing one for any change to the live book: P(arm grows faster) >= 0.90 on the end-2014 list, > 0.5 in each half, >= 0.5 on the shipped list. Bar 2: "loses less" only if the worst fall is smaller on both lists; such an arm is the owner's choice, not added automatically. | **Bar 1: none passes** (best: out after a shock-down close, 0.61 on the end-2014 list, 0.85 and 0.13 in the halves, 0.40 on the shipped list). **Bar 2: half the book for 21 sessions after any market shock loses clearly less**: worst fall -25.0% against the live book's -35.6% on the end-2014 list and -31.2% against -41.1% on the shipped list, worst session -6.0% against -12.0%, worst 21 sessions -15.0% against -27.4%, for 0.8% a year less growth on both lists (P grows faster 0.38 and 0.39; 0.74 in the first half, 0.13 in the second). Closing out completely barely moves the worst fall. Why: of the market's average 4.2% fall on its 37 shock-down days, 51% had happened by the open; in the 5 sessions after such a day the market returned +0.29% and rose 67% of the time; after 22 gap-down opens the rest of the day returned +0.01%. Selling single stocks after their own shock, and dropping the tilt, do not help. Not wired into the bot: the owner decides whether 0.8% a year is worth about 10 points of worst fall. |
| 2026-11-23 | **Sector spillover after a stock's shock (news_spill_study.py): no pattern. The stock list by date, dead companies included (wide_universe.py).** Grok's untested news idea: when one stock gets a shock (more than 3 of its normal moves against its sector on double volume), do the other stocks of its sector drift in the same direction over the next 1 or 5 sessions? The list: every company that was in the S&P 500 on any day since 2016, rebuilt each day from Alpaca and two small committed files. | Spillover rules and bar committed (2ebaa53) before the run: a t of 3 or more in size at 1 or 5 sessions and the same sign in both halves; days are the unit; market and sector taken out; from the next open. The list was built by an Opus agent and checked against the local dataset. | **Spillover: no pattern.** 11,093 shocks on 1,994 days (2017-08 to 2026-11): peers' move in the shock's direction +0.0 hundredths of a percent next session (t 0.0), +0.1 over 5 sessions (t 0.1); halves +0.1 and -0.1; no sub-group reaches a t of 2 in size. With the earlier results this closes direction-after-news on daily data: a stock's own shock, a market shock, and now its sector peers all show nothing, while the size of later moves is strongly predictable. **The list:** 729 companies, 226 of which left the index; membership identical to the local dataset and 99.996% of daily returns within 0.1%. Known gaps: the three 2023 bank failures end at their last trade (down 48% to 75% in their last 21 sessions), not at their final loss; four acquired companies have no bars. |
| 2026-11-23 | **Daily calls, rules v4: the dated list, shared moves taken out, one learner, the calm trend, and information entries.** Built from the research round at the owner's request ("build everything"). The S&P 500 by date with dead companies (729); market and sector moves taken out of the patterns and of the outcomes they are learned on; one learner in place of "sure" and "best guess", which speaks only if the whole crowd of price patterns beats luck and then weights them by (S + gI)^-1 m; the trend standing aside when its own bet is wild; and one-idea entries judged on their own: busy/quiet month and profitability now, earnings surprise and about-to-report when the earnings file is complete. Profitability comes from SEC filings as first reported (`fundamentals_data.py`, 503 companies). | Rules committed (cc23c85) before the past test was run. One change after the first run had been read (8a0a1fb): luck is measured on blocks of twice the horizon, on Grok's point that shorter blocks share outcomes with their neighbours; it can only make the learner speak less. Ten machine results are read on the market board, so one narrow pass would be likely by luck. | **Nothing passes.** Market board, from the next open, calls that do not overlap: the learner never had a view at 21 or 5 sessions and was right 52 of 112 times at 1 session; trend ranking at 21 sessions 43 of 73 (59%), mean +0.07%, t 0.2; **trend on calm days 18 of 30 (60%), mean +0.65%, t 1.7, the nearest miss**, with its worst calls milder (-4.8% against -6.7%); busy/quiet month 26 of 73 (36%), t -2.3, the wrong way round; profitability 33 of 73, t 0.2. Taking out the market and the sectors cut the daily wobble of a ranking score from 0.19 to 0.116: the list now carries the information of about 74 independent stocks, up from about 28 (Grok had guessed about 100). On 2026-11-23: 6 market shock days in the last 21 sessions; the learner has a view only for the next session. |
| 2026-11-23 | **Bad-news gaps (news_gap_study.py): no pattern.** The owner said good news such as a chief executive's reinstatement "obviously" sends a stock up, and asked for a test of the opposite hint from a quick look: stocks that open more than 10% down seemed to lose a further 1.2% over five sessions. First event test in the project: only the stocks the event happened to, measured from the open against the average index member, on the dated list with dead companies. | Rules and bars committed (0c2f3dc) before the run. A basket holds every stock whose event was in the last 5 sessions; each day's basket return is one observation. Real needs t of -3 or lower and a negative mean in both halves; a hint needs -2. | **No pattern.** 1,209 events, 2017-08 to 2026-11: the basket lost 0.15% a day against the average member, t -1.5 (halves -0.21% and -0.09%); over the five sessions the average event lost about 1% more, but exactly half of the stocks fell further and half bounced. The average is a few disasters, not a tendency. Readings, not verdicts: opening more than 5% down, nothing (t +0.9); opening more than 10% UP (970 events), the stock then lagged the average member by 0.24% a day, t -3.3, strongest in the first half of the sample (-0.44% a day) and nearly gone in the second (-0.05%). The reinstatement case itself: Nvidia closed at 125.53 on 2026-11-20, opened at 167.03 on 2026-11-23 (+33%) and closed at 165.05, 1.2% below that open. |
| 2026-11-23 | **Two tests on information that is not prices: company announcements (news_filing_study.py) and short interest (short_interest_study.py). Neither shows a pattern.** Built at the owner's request to "seriously look at how to make this model smarter", from the two sources the research ranked highest. Announcements: 73,410 SEC 8-K filings with the second each became public (`filings_data.py`, `lab/filings_8k.csv`), used as a timed record of real news to split big moves into those with an announcement behind them and those without. Short interest: FINRA's twice-monthly figures used only from their publication dates (`short_interest_data.py`, `lab/short_interest.csv`), least-shorted third against most-shorted third by days to cover. Both data sets were built by Opus agents and checked (results dates match the earnings calendar; 9 of 10 short-interest spot checks match). | Rules and bars committed before each run (46d85a6, fb5835a): one deciding number each, real at a t of 3 or more in size with the same sign in both halves, a hint at 2. The announcement test crashed once before producing any number (a one-session holding period was not handled) and was re-run unchanged in its rules. Limits: both files cover only companies still in the index today. | **Announcements: no pattern.** 9,196 big moves since 2017-08, 5,476 with an 8-K behind them and 3,720 without: the with-announcement basket minus the without-announcement basket earned -0.02% a day over the next 5 sessions, t -0.8 (halves -0.05% and 0.00%). Neither group continued or reversed on its own (t 0.1 and 0.6). **Short interest: no pattern.** 2,228 days from 2018-01, about 427 stocks ranked a day: least shorted minus most shorted +0.005% a day, about 1% a year, t 0.8 (halves 0.00% and +0.01%); the change in shares short, t -0.1. With profitability (t 0.2) and busy/quiet month (t -2.3, the wrong way), four non-price or event ideas have now been tested on large companies and none adds anything. Earnings surprise and about-to-report remain, waiting on the earnings file. |

**Run the paper account as if it were real money** (adopted 2026-11-21, after the first drawdown; the paper year is
also a test of the operator):
- **No resets.** The account is never deleted, re-created or restarted because of its P&L. Losses are counted from
  the $100,000 start. Bad starts are annotated in the change log, not erased.
- **No manual trades.** Every order comes from monitor.py. Any manual action (a trade, a forced run, editing
  state.json or positions) is logged in the change log with date and reason, and counts against the paper year's
  "zero unexplained orders" threshold.
- **No decisions in a drawdown.** Between 2026-11-21 and the 2026-12-12 interim review only repairs are allowed. That
  review's agenda is fixed now: measurement (tracking error on end-of-day equity, a definition of drift), the defect
  list in `reports/Decision 2026-11-21.md`, the prediction-market sleeves. Stock parameters and the no-trade band are
  out of scope until 2027-11-19.
- **Real-money gate.** Before any real money follows this model: 250 logged sessions passing the execution thresholds
  above; at least one −10% drawdown sat through with no manual intervention; a written dollar loss limit; real money
  sized so that a −40% fall (the engine's 2000–02 case on ^NDX) is survivable without selling; and staged entry
  (one third at a time, at least a month apart), never sized on the 23% backtest.

## 1. Notation

Prices $P_{i,t}$ for names $i = 1..N$ ($N = 12$ plus ANT once it lists), log returns $r_{i,t} = \ln P_{i,t} - \ln P_{i,t-1}$, simple returns
$R_{i,t} = P_{i,t}/P_{i,t-1} - 1$. Everything at time $t$ uses data up to and including the close of $t$; positions set
at close $t$ earn $R_{t+1}$. `test_model.py` checks this mechanically by deleting future data and confirming the weights don't change.

## 2. Inverse-volatility weights

$\hat\sigma_{i,t}$ = 60-day standard deviation of $r_i$, annualised by $\sqrt{252}$.

$$w^{0}_{i,t} = \frac{1/\hat\sigma_{i,t}}{\sum_j 1/\hat\sigma_{j,t}}$$

**Why:** the risk contribution of name $i$ is $RC_i = w_i(\Sigma w)_i / \sigma_p$. If all pairwise correlations equal $\rho$,
then $(\Sigma w)_i = \sigma_i \sum_j \rho_{ij}\sigma_j w_j$, and with $w_j \propto 1/\sigma_j$ this is $\sigma_i \cdot c\,(1+(N-1)\rho)$ for a constant $c$,
so $RC_i = c\,(1+(N-1)\rho)/\sigma_p$, **the same for every name**. TSLA (~60% vol) gets about a third of AAPL's (~25%) weight,
so it can't dominate the book. Inverse-vol needs no expected-return estimates, which are the main source of error in
mean-variance and Kelly (MacLean-Thorp-Ziemba; report §risk).

Caps: $w_i \le 0.25$, and $w_{SPCX}, w_{ANT} \le 0.05$ (fresh IPOs: SPCX lockup on 2026-12-08, merger event risk, thin history; ANT trades only after 60 days of prices).
Anything over a cap sits in cash.

## 3. Volatility targeting

Portfolio vol estimate from the 60-day covariance $\hat\Sigma_t$ (annualised):

$$\hat\sigma_{p,t} = \sqrt{w_t^{0\top}\hat\Sigma_t w^0_t}, \qquad k_t = \min\!\left(1, \frac{\sigma^*}{\hat\sigma_{p,t}}\right), \quad \sigma^* = 20\%$$

**Why it is close to growth-optimal:** the Kelly fraction for an asset with drift $\mu$ and vol $\sigma$ is $f^* = \mu/\sigma^2$.
If the Sharpe ratio $S = \mu/\sigma$ is roughly stable while vol changes (the empirical regularity behind Moreira-Muir 2017),
then $f^* = S/\sigma$: **optimal exposure is inversely proportional to vol**, which is exactly $k_t \propto 1/\hat\sigma_{p,t}$.
$\sigma^* = 20\%$ (15% → 25% on 2026-11-18, → 20% on 2026-11-19; see the change log). With an honest forward Sharpe of 0.5–1.0, full Kelly is 50–100% vol, so 20% is roughly 1/5 to 2/5 Kelly. On the Nasdaq-100 since 1985, 20% had the best Sharpe of 15/20/25% and kept the dot-com drawdown to −39%.
Half-Kelly keeps about 75% of growth with far less ruin risk (Ziemba).

**Why it cuts drawdowns:** volatility clusters (GARCH). Crashes arrive in high-vol periods, when $k_t$ is already small.
The ablation shows max drawdown falling from −42% without the engine to −22.5% with it, while Sharpe barely moves. But
most of that is lower average exposure: equal-weight scaled to the same vol has a −30% drawdown and the bootstrap
cannot separate the two (p = 0.62, §0). Vol targeting here is a way to set risk, not a proven drawdown edge.

## 4. Regime overlay

$$g_t = \begin{cases} 1 & QQQ_t \ge MA_{200}(QQQ)_t \\ 0.5 & \text{otherwise}\end{cases}, \qquad w_t = g_t\, k_t\, w^0_t$$

Trend filters on an index are the best-supported regime signal for cutting drawdowns (report §regime).
The 0.5 is not tuned. The PBO grid tests 0, 0.5 and 1.0 and finds the choice is not what drives the result.

## 5. Costs

$$R^{net}_{p,t} = \sum_i w_{i,t-1} R_{i,t} - c \sum_i |w_{i,t} - \tilde w_{i,t}|, \quad \tilde w_{i,t} = \frac{w_{i,t-1}(1+R_{i,t})}{1+\sum_j w_{j,t-1}R_{j,t}}, \quad c = 5\text{ bp (stress: 10 bp)}$$

$\tilde w_t$ is yesterday's book after today's price moves, so the cost is on the trade actually made at close $t$; the first
entry from cash is charged. (Before 2026-11-19 the cost ignored drift; the fix moved Sharpe 1.262 → 1.259.)

Mega-cap spreads are about 1–2 bp (report §backtesting), so 5 bp is conservative. Doubling it barely changes Sharpe (1.26 → 1.24),
because inverse-vol weights move slowly.

## 6. The tests

**Stationary bootstrap (Politis-Romano 1994).** Returns are autocorrelated in volatility, so naive i.i.d. resampling understates
uncertainty. Each resample is built from blocks with geometric lengths (mean $L = 20$ days), drawing from a uniformly random start when a jump with probability $1/L$ occurs, and continuing the
current block otherwise. The same index paths are used for every strategy, so differences are *paired*.
2,000 resamples give a CI for the Sharpe, $P(\text{Sharpe}_A \le \text{Sharpe}_B)$ and $P(\text{MaxDD}_A \text{ worse})$.

**HAC alpha.** We regress excess returns, $R_{p,t} - r_{f,t} = \alpha + \beta (R_{b,t} - r_{f,t}) + u_t$ ($r_f$ = daily 13-week T-bill), by OLS with the Newey-West covariance

$$\hat V = (X^\top X)^{-1}\Big[\sum_t u_t^2 x_t x_t^\top + \sum_{l=1}^{5}\big(1-\tfrac{l}{6}\big)\sum_t u_t u_{t-l}(x_t x_{t-l}^\top + x_{t-l}x_t^\top)\Big](X^\top X)^{-1}$$

The pass bar is $t > 3.0$, not 2.0: Harvey-Liu-Zhu (2016) show that after hundreds of published factors, 2.0 lets in mostly false positives.

**Deflated Sharpe ratio (Bailey & López de Prado 2014).** We tried $K = 60$ distinct variants. The best of $K$ noise strategies has an
expected Sharpe of

$$SR_0 = \sqrt{V[\widehat{SR}_k]}\Big((1-\gamma)\,\Phi^{-1}(1-\tfrac1K) + \gamma\,\Phi^{-1}(1-\tfrac{1}{Ke})\Big), \quad \gamma \approx 0.5772$$

and

$$DSR = \Phi\!\left(\frac{(\widehat{SR}-SR_0)\sqrt{T-1}}{\sqrt{1-\hat\gamma_3\widehat{SR}+\frac{\hat\gamma_4-1}{4}\widehat{SR}^2}}\right)$$

This corrects for both the number of trials and the fat tails and skew of the returns ($\hat\gamma_3$ skew, $\hat\gamma_4$ kurtosis). Pass bar: 0.95.

**Probability of backtest overfitting via CSCV (Bailey, Borwein, López de Prado, Zhu 2017).** Split the $T\times K$ trial-return matrix into
$S = 16$ time blocks. For each of the $\binom{16}{8} = 12{,}870$ ways to pick half the blocks as in-sample:

1. Find the best trial in-sample.
2. Find its relative rank $\omega$ among all trials out of sample.
3. Compute $\lambda = \ln(\omega/(1-\omega))$.

$PBO = P(\lambda \le 0)$ is the probability that the in-sample winner is below the median out of sample. Pass bar: below 0.30.
`test_model.py` checks the implementation: PBO is above 0.3 on pure noise and below 0.1 on a planted edge.

**Information coefficient and the fundamental law.** $IC_t = \text{Spearman}(\text{score}_{\cdot,t}, r_{\cdot,t+1})$. Grinold's law gives
$IR \approx IC\sqrt{\text{breadth}}$. With $IC = 0.006$ and breadth of 8 names (original universe) × 252 days, $IR \approx 0.006\sqrt{2016} \approx 0.27$
*before* costs and estimation noise. Its t-stat (0.7) says even that is indistinguishable from zero. This is why the signals were removed:
with 8 correlated names, breadth is too small for a weak signal to matter (report §ML).

**Candlesticks (Holm-Bonferroni).** For each of 13 patterns × 3 horizons (39 tests), the excess forward return is

$$e = R_{t\to t+h} - \bar R_{h}$$

That is, the forward return minus the stock's own average $h$-day return, so a stock's general uptrend does not count as signal. We sort the p-values $p_{(1)}\le\dots\le p_{(m)}$,
set $\tilde p_{(k)} = \max_{j\le k}\min(1,(m-j+1)p_{(j)})$, and require two things:

- $\tilde p < 0.05$
- the same sign before and after 2021 (a discovery/holdout split)

None pass. The t-stat averages events per date first, because the same down-day hits many correlated names at once;
counting each name-day as independent had let the bear marubozu ($h = 1$) through (holm-p = 0.03), and it now fails (holm-p = 0.52).
For $h > 1$, overlapping windows still inflate t, which only makes the bar easier to clear.

## 7. Known biases you should not ignore

1. **Selection bias.** These names were picked because they became the biggest winners of the decade. Absolute returns
   (23% CAGR) are inflated. Only comparisons between strategies on the *same* names are fair, which is why equal-weight on the same names
   (also scaled to the model's vol) is the key benchmark. On the end-2014 top-10 tech list the same engine earns 15% CAGR, Sharpe 0.98.
2. **Short SPCX history.** About 110 days. It enters only after 60 days and is capped at 5%.
3. **Close fills.** The model assumes trades fill at the close. Live trading rebalances 0–30 min before the close, which adds tracking noise.
4. **Regime of the sample.** 2015–2026 was mostly a mega-cap bull market. A long sideways market would hurt the absolute numbers.
