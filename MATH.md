# The math, and what was actually proven

Code: [model.py](model.py) (model), [backtest.py](backtest.py) (tests), [candles.py](candles.py) (candlestick tests).
Results: [reports/backtest_results.md](reports/backtest_results.md), [reports/candles_results.md](reports/candles_results.md).
Research behind every choice: [reports/Quant trading for Tesla and big tech.md](reports/Quant%20trading%20for%20Tesla%20and%20big%20tech.md).

## 0. What "prove" can mean here

No backtest proves future profit. What we *can* do is state falsifiable claims, test them on 2015-2026 data with
methods that punish luck and overfitting, and only ship what survives. Every claim below has a test and a pass bar.

| Claim | Test | Result |
|---|---|---|
| The model has a positive Sharpe | stationary bootstrap, deflated Sharpe | **Pass** (CI 0.65–1.80, DSR 0.999) |
| The risk engine cuts drawdowns vs buy & hold | bootstrap P(MaxDD worse) | **Pass** (p = 0.003 vs equal-weight, 0.019 vs QQQ) |
| The parameter choice is not overfit | PBO via CSCV over 72 variants | **Pass, barely** (0.28 < 0.30) |
| Beats QQQ risk-adjusted | HAC alpha t-stat | **Borderline** (t = 3.02, bar 3.0; inflated by selection bias, §6) |
| Beats buying the same 8 stocks | bootstrap P(Sharpe ≤ EW), HAC alpha | **Fail** (p = 0.47, t = 1.2) — same Sharpe, half the drawdown |
| Trend + reversal signals predict returns | rank IC t-stat, bootstrap vs basket | **Fail** (IC t = 0.7; signal model worse) → removed |
| Candlestick patterns predict returns | 39 tests, Holm correction, split-sample | **1 of 39 passes** (bear marubozu, +0.50% next day) |

**Plain-English conclusion:** the edge is *risk control*, not *prediction*. You get roughly the same risk-adjusted
return as holding these stocks, with drawdowns cut from about −49% to about −22%. That is what the research predicted
(report §"what actually works").

## 1. Notation

Prices $P_{i,t}$ for names $i = 1..N$ ($N = 8$), log returns $r_{i,t} = \ln P_{i,t} - \ln P_{i,t-1}$, simple returns
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

Caps: $w_i \le 0.25$, and $w_{SPCX} \le 0.05$ (lockup on 2026-12-08, merger event risk, only ~110 days of history).
Anything over a cap sits in cash.

## 3. Volatility targeting

Portfolio vol estimate from the 60-day covariance $\hat\Sigma_t$ (annualised):

$$\hat\sigma_{p,t} = \sqrt{w_t^{0\top}\hat\Sigma_t w^0_t}, \qquad k_t = \min\!\left(1, \frac{\sigma^*}{\hat\sigma_{p,t}}\right), \quad \sigma^* = 15\%$$

**Why it is close to growth-optimal:** the Kelly fraction for an asset with drift $\mu$ and vol $\sigma$ is $f^* = \mu/\sigma^2$.
If the Sharpe ratio $S = \mu/\sigma$ is roughly stable while vol changes (the empirical regularity behind Moreira-Muir 2017),
then $f^* = S/\sigma$: **optimal exposure is inversely proportional to vol**, which is exactly $k_t \propto 1/\hat\sigma_{p,t}$.
$\sigma^* = 15\%$ is a fractional-Kelly choice. With realised Sharpe around 1.2, full Kelly would be about 120% vol, so 15% is roughly 1/8 Kelly.
Half-Kelly keeps about 75% of growth with far less ruin risk (Ziemba).

**Why it cuts drawdowns:** volatility clusters (GARCH). Crashes arrive in high-vol periods, when $k_t$ is already small.
The ablation confirms this: max drawdown falls from −47% without the engine to −22% with it, while Sharpe barely moves.

## 4. Regime overlay

$$g_t = \begin{cases} 1 & QQQ_t \ge MA_{200}(QQQ)_t \\ 0.5 & \text{otherwise}\end{cases}, \qquad w_t = g_t\, k_t\, w^0_t$$

Trend filters on an index are the best-supported regime signal for cutting drawdowns (report §regime).
The 0.5 is not tuned. The PBO grid tests 0, 0.5 and 1.0 and finds the choice is not what drives the result.

## 5. Costs

$$R^{net}_{p,t+1} = \sum_i w_{i,t} R_{i,t+1} - c \sum_i |w_{i,t} - w_{i,t-1}|, \quad c = 5\text{ bp (stress: 10 bp)}$$

Mega-cap spreads are about 1–2 bp (report §backtesting), so 5 bp is conservative. Doubling it barely changes Sharpe (1.21 → 1.19),
because inverse-vol weights move slowly.

## 6. The tests

**Stationary bootstrap (Politis-Romano 1994).** Returns are autocorrelated in volatility, so naive i.i.d. resampling understates
uncertainty. Each resample is built from blocks with geometric lengths (mean $L = 20$ days), drawing from a uniformly random start when a jump with probability $1/L$ occurs, and continuing the
current block otherwise. The same index paths are used for every strategy, so differences are *paired*.
2,000 resamples give a CI for the Sharpe, $P(\text{Sharpe}_A \le \text{Sharpe}_B)$ and $P(\text{MaxDD}_A \text{ worse})$.

**HAC alpha.** We regress $R_{p,t} = \alpha + \beta R_{b,t} + u_t$ by OLS with the Newey-West covariance

$$\hat V = (X^\top X)^{-1}\Big[\sum_t u_t^2 x_t x_t^\top + \sum_{l=1}^{5}\big(1-\tfrac{l}{6}\big)\sum_t u_t u_{t-l}(x_t x_{t-l}^\top + x_{t-l}x_t^\top)\Big](X^\top X)^{-1}$$

The pass bar is $t > 3.0$, not 2.0: Harvey-Liu-Zhu (2016) show that after hundreds of published factors, 2.0 lets in mostly false positives.

**Deflated Sharpe ratio (Bailey & López de Prado 2014).** We tried $K = 72$ variants. The best of $K$ noise strategies has an
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
$IR \approx IC\sqrt{\text{breadth}}$. With $IC = 0.006$ and breadth of 8 names × 252 days, $IR \approx 0.006\sqrt{2016} \approx 0.27$
*before* costs and estimation noise. Its t-stat (0.7) says even that is indistinguishable from zero. This is why the signals were removed:
with 8 correlated names, breadth is too small for a weak signal to matter (report §ML).

**Candlesticks (Holm-Bonferroni).** For each of 13 patterns × 3 horizons (39 tests), the excess forward return is

$$e = R_{t\to t+h} - \bar R_{h}$$

That is, the forward return minus the stock's own average $h$-day return, so a stock's general uptrend does not count as signal. We sort the p-values $p_{(1)}\le\dots\le p_{(m)}$,
set $\tilde p_{(k)} = \max_{j\le k}\min(1,(m-j+1)p_{(j)})$, and require two things:

- $\tilde p < 0.05$
- the same sign before and after 2021 (a discovery/holdout split)

Only the bear marubozu at $h = 1$ passes: +0.50% next day, 57% hit rate, holm-p = 0.03. Its t-stat treats events as independent;
for $h > 1$, overlapping windows inflate t, which makes the pass bar *easier* to clear. Even so, only 1 of 39 cleared it.

## 7. Known biases you should not ignore

1. **Selection bias.** These 8 names were picked because they became the biggest winners of the decade. Absolute returns
   (18% CAGR) are inflated. Only comparisons between strategies on the *same* names are fair, which is why equal-weight on the same names is the key benchmark.
2. **Short SPCX history.** About 110 days. It enters only after 60 days and is capped at 5%.
3. **Close fills.** The model assumes trades fill at the close. Live trading rebalances 0–30 min before the close, which adds tracking noise.
4. **Regime of the sample.** 2015–2026 was mostly a mega-cap bull market. A long sideways market would hurt the absolute numbers.
