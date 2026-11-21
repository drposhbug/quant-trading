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
