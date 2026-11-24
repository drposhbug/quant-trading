# 3. Methods and math (the statistician's view)

Written 2026-11-23 for the STORM study "Smarter machine". Scope: how to learn from 345 weak, near-duplicate patterns ranking about 500 large caps over about 2,300 days, and how to judge the result quickly and honestly. All numbers marked "simulated" come from a small numpy simulation I ran in a scratch folder, not from the repository.

Notation used throughout:
- j = 1..P patterns (P = 345), h = horizon (1, 5, 21).
- IC_{j,t} = daily rank IC; B_{j,b} = block means (blocks of 21 or 5 sessions), b = 1..n_B.
- t_j = sum_b B_{j,b} / sqrt(sum_b B_{j,b}^2) (the self-normalised t the machine already uses).
- mu_hat = vector of mean ICs (P x 1); Sigma_hat = P x P covariance of the block ICs.
- Sigma_hat = Q Lambda Q' is its eigen-decomposition, with eigenvalues lambda_1 >= lambda_2 >= ...

---

## 1. Combining many weak, correlated signals

### 1a. Efron's two-groups model and local false discovery rate
**Idea.** Treat each pattern's t as drawn either from a null (no skill) or from a non-null distribution. The local fdr is the posterior probability that a given t is null. It replaces "is |t| above a bar?" with "how likely is this pattern to be noise?"

**Formula.** f(t) = pi0 f0(t) + (1 - pi0) f1(t); lfdr(t) = pi0 f0(t) / f(t). Estimate f by a smooth fit (Poisson regression on a histogram of the 345 t's, Lindsey's method) and f0 by the *empirical null*: centre and width fitted to the middle of the histogram (Efron 2004), or, better here, taken from the re-signing distribution which already carries the correlation. pi0 <= min over the central region of f(t)/f0(t).

**Correlation.** Efron (2007, "Correlation and large-scale simultaneous significance testing") shows that correlated tests leave each t's marginal null unchanged but make the *histogram* of t's wander: the count beyond 2 has variance inflated by roughly a factor 1 + (P - 1) A^2 times a constant, where A is the root-mean-square correlation among the t's. That is exactly why luck can give 43 exceedances at the 95th percentile when independence would predict about 17 +/- 4. The re-signing test is the correct fix and the machine already uses it.

**When it helps.** Large P, a modest fraction of real effects, and a well-estimated null. **When not.** When the "effects" are all one effect copied many times: lfdr then counts copies, not ideas. At h = 1 the 75 exceedances are probably a small number of underlying ideas (short-term reversal and its relatives).

**Change to the machine.** Report, per horizon, an estimate of 1 - pi0 and the expected number of real patterns among those with |t| > 2: E[#real] ~ #(|t|>2) - median luck count = 75 - 8 = 67 at h = 1, and about 0 at h = 5 and 21. Use lfdr only as a reporting device; use 1b/1d for the weights.

**References.** Efron, B. (2004) "Large-scale simultaneous hypothesis testing: the choice of a null hypothesis", JASA 99. Efron (2007) JASA 102:93-103. Efron (2010) *Large-Scale Inference*, Cambridge UP, chapters 5-8.

### 1b. Tweedie's formula and empirical Bayes shrinkage of each pattern's skill
**Idea.** If t_j ~ N(delta_j, 1), the best guess of the true delta_j given the observed t_j can be read off the shape of the histogram of all t's, without specifying a prior. It automatically pulls lucky winners back toward zero, more strongly when the histogram says big t's are mostly luck (the "winner's curse" correction).

**Formula (Tweedie).** E[delta | t] = t + d/dt log f(t), where f is the marginal density of the t's (Robbins 1956; Efron 2011, "Tweedie's formula and selection bias", JASA 106). With a normal prior delta ~ N(0, tau^2) this reduces to James-Stein: E[delta | t] = (1 - 1/(1 + tau^2)) t, with 1 + tau^2 estimated by the sample variance of the t's. James-Stein for P >= 3: delta_JS = (1 - (P - 2) / sum t_j^2) t (positive-part version clips at 0). Efron-Morris (1975) shrink toward the grand mean instead of 0: delta = t_bar + (1 - (P - 3)/sum (t_j - t_bar)^2)(t - t_bar).

**Correlation.** James-Stein's dominance proof assumes independent unit-variance errors. With correlated errors the right variance to subtract is not 1 but the null spread of the t's *as seen in the histogram*, which the re-signing gives: replace 1 by var_null = average over re-signings of the cross-sectional variance of t. Shrinkage factor: c = max(0, 1 - var_null / var(t_observed)). Note: with correlated noise the shrinkage estimate is itself noisy (effective P small), so be conservative.

**When it helps.** It turns a hard 0/1 threshold into a smooth, honest weight; a pattern with |t| = 3.4 is not worth zero while one with 3.6 is worth something. **When not.** It still treats patterns one at a time; it does not stop 40 near-copies voting 40 times.

**Change to the machine.** Replace the vote weight max(|t| - bar, 0) (bar about 3.5) and the looser max(|t| - 2, 0) with the posterior mean c * t_j, where c = 1 - var_null / var(t). At h = 5 and h = 21, where the counts are inside luck's range, c will be close to 0 and the horizon effectively switches itself off, which is correct. Combine with 1d so near-copies do not stack.

### 1c. "Shrinking the cross-section" (Kozak, Nagel, Santosh 2020)
**Idea.** Find the best linear combination of many characteristic-based portfolios with a prior that says high expected returns are unlikely to sit on low-variance (small-eigenvalue) directions. The resulting estimator is ridge regression of mean returns on the covariance, which shrinks most on the noisy, small principal components.

**Formula.** Prior mu ~ N(0, (kappa^2 / tau) Sigma^2). Posterior mean of the stochastic-discount-factor weights:
b_hat = (Sigma + gamma I)^{-1} mu_hat, gamma = tau / (kappa^2 T).
In principal-component coordinates: b_k = mu_k / (lambda_k + gamma), where mu_k = q_k' mu_hat. Large-eigenvalue PCs keep their weight; small-eigenvalue PCs (differences between near-copies) are crushed. They also allow an L1 term (elastic net) and find that sparsity in *characteristics* does not work, while sparsity in *principal components* does. gamma (equivalently kappa) is chosen by K-fold cross-validation over contiguous time blocks.

**When it helps.** Exactly our case: many near-duplicate signals, high correlation, P comparable to the number of independent blocks. **When not.** If the signal sits in a small-eigenvalue direction (for example "pattern A minus its near-copy B"), ridge will kill it. That is unlikely to be real alpha here.

**Change to the machine (the main recommendation).** Treat each pattern's daily IC as the return of a pattern portfolio. Per horizon, compute mu_hat (345) and Sigma_hat from the block ICs on the training window, compute b_hat = (Sigma_hat + gamma I)^{-1} mu_hat, choose gamma by leave-one-year-out CV of the out-of-sample IC of the combined score, and score stock i as s_i = sum_j b_j z_{ij}, where z_{ij} is pattern j's cross-sectional rank-normal score. One eigen-decomposition of a 345 x 345 matrix plus a 1-D grid search: well under a second.

**Reference.** Kozak, S., Nagel, S., Santosh, S. (2020) "Shrinking the cross-section", *Journal of Financial Economics* 135(2):271-292.

### 1d. Ridge vs lasso vs principal-components regression on the signals
**Idea.** All three are ways of regressing next-period returns on 345 collinear predictors. They differ in how they treat near-copies: ridge spreads weight across them, lasso picks one more or less at random, and PCR keeps the top K directions and drops the rest.

**Formulas.** Ridge: beta = (X'X + gamma I)^{-1} X'y, i.e. shrink PC k by lambda_k/(lambda_k + gamma). PCR: shrink factor 1 for k <= K and 0 for k > K. Lasso: min ||y - X beta||^2 + gamma ||beta||_1 (no closed form; coordinate descent). Elastic net adds both and has the "grouping effect" that keeps near-copies together (Zou and Hastie 2005).

**Which one here.** Ridge (equivalently KNS, 1c). Reasons: (i) the predictors come in clusters of near-copies, where lasso is unstable (selected set changes from year to year), (ii) ridge is the posterior mean under a Gaussian prior, which matches "many tiny effects", (iii) Hastie, Tibshirani and Friedman, *Elements of Statistical Learning* 3.4-3.6, and the comparison in Gu, Kelly, Xiu (2020) "Empirical asset pricing via machine learning", RFS 33, where linear penalised models are a strong baseline. PCR with K chosen by CV is a reasonable cross-check; lasso is not worth the instability.

**Pooled panel version.** Instead of working with ICs, one can run a pooled ridge of cross-sectionally ranked forward returns on the 345 rank-normal pattern scores, stacking 500 stocks x 2,300 days (about 1.1 million rows). X'X is 345 x 345, so it is computed once in seconds. This is mathematically close to 1c (the IC is the slope of a univariate cross-sectional regression on rank scores).

### 1e. The forecast-combination puzzle
**Idea.** In theory the optimal combination of forecasts uses the inverse covariance of their errors (Bates and Granger 1969). In practice the simple average usually wins, because estimating the optimal weights adds more error than it removes (Smith and Wallis 2009; Claeskens, Magnus, Vasnev, Wang 2016).

**Formula.** Optimal weights w* = Sigma_e^{-1} 1 / (1' Sigma_e^{-1} 1). Estimation error of w_hat is of order P / T, so with P = 345 and roughly 110 independent 21-day blocks the estimated w is pure noise; the simple average has zero estimation variance.

**When equal weights lose.** When some members are known to be useless or of the wrong sign (our case: most of the 345 have no skill and some have negative IC), or when members differ hugely in quality. **The middle road** is "shrink toward equal": w = alpha w_hat + (1 - alpha) (1/P), which in the ridge language above is a small-gamma vs large-gamma choice. Note that ridge with large gamma gives b proportional to mu_hat: the "IC-weighted average", which ignores correlation. That is the natural benchmark.

**Change to the machine.** Always carry three benchmarks in the past test: (A) equal-weight of all patterns with sign fixed by the training mean (sign(mu_hat_j)), (B) mu_hat-weighted (ridge, gamma -> infinity), (C) the CV-chosen ridge. If (C) does not beat (A) on new days, use (A) or (B).

### 1f. What changes when the noise in the signals is strongly correlated
- Equal weights stop diversifying: the variance of the average is approximately rho_bar sigma^2 for large P, so 345 near-copies behave like a handful of signals. The effective number (section 3g) is the right count.
- Sigma^{-1} mu takes big long-short positions between near-copies (it "bets on the difference"), which is mostly fitting noise; ridge/PCR damp exactly these directions.
- t's of correlated patterns are not independent evidence: "75 patterns beyond |t| = 2" is not 75 confirmations.
- The count test, the max-t bar and James-Stein all need the null spread from re-signing, not from independence. The machine already does this correctly.

---

## 2. The "virtue of complexity" debate, and whether a bigger model helps

**Idea.** Kelly, Malamud and Zhou (2024) show, in the ridge-less limit of random-feature regression, that out-of-sample R^2 and Sharpe ratios of market-timing strategies can *rise* as the number of random nonlinear features P grows past the number of observations T, provided the ridge penalty is chosen sensibly ("double descent"). Critics argue that this is not learning: with P >> T and short training windows, the forecast is a kernel-weighted average of recent returns, i.e. a volatility-scaled momentum rule.

**Formula (random-feature ridge).** Features S_t = [sin(gamma w_i' G_t), cos(gamma w_i' G_t)], w_i ~ N(0, I), i = 1..P/2. Ridge: beta = (S'S/T + z I)^{-1} S'R/T. As P/T -> infinity with fixed z, the prediction becomes R_hat(G) = sum_s k(G, G_s) R_s with Gaussian kernel k: a kernel ridge regression.

**Critics.** Nagel (2025, NBER w34104, "Seemingly virtuous complexity in return prediction") shows that with P >> T the RFF forecast is a similarity-weighted average of the training returns, that with short windows the weights mostly track recency, and that the method produces the same volatility-timed momentum strategy even in simulated data built to have reversals. Buncic (2024/25, "Simplified: a closer look at the virtue of (kernel) complexity") makes a related point that the gains come from the kernel and the penalty, not from complexity per se. Supporting side: Didisheim, Ke, Kelly, Malamud (2023) "Complexity in factor pricing models".

**When it helps.** Large panels with real nonlinear structure, lots of data (Gu, Kelly, Xiu use 30,000 stocks x 60 years; neural nets add little over penalised linear models for large caps). **When not.** Our case: 500 large caps, about 2,300 days, signal-to-noise around IC 0.01-0.03. The KMZ result is about the time series of the market with 12 predictors; for a cross-section the equivalent would be random features of the 345 patterns. With per-day cross-sectional IC of order 0.02, the per-observation R^2 is about 0.0004; nonlinear interactions have even smaller signal and need far more data to estimate.

**Change to the machine.** Do not build a bigger model now. If curiosity wins, the cheap test is: 1,000-2,000 random Fourier features of the (rank-normal) pattern scores, pooled cross-sectional ridge, gamma by time-block CV, compared on new days against the linear ridge of 1c. Expect it to match ridge at best. Kernel ridge with a linear kernel *is* ridge; so the question "does nonlinearity help" is the only one worth asking, and the answer for large-cap daily data in the literature is "barely".

**References.** Kelly, B., Malamud, S., Zhou, K. (2024) "The virtue of complexity in return prediction", *Journal of Finance* 79(1):459-503. Nagel, S. (2025) NBER WP 34104. Hastie, Montanari, Rosset, Tibshirani (2022) "Surprises in high-dimensional ridgeless least squares interpolation", *Annals of Statistics* 50. Rahimi and Recht (2007) "Random features for large-scale kernel machines", NIPS.

---

## 3. Multiple testing done properly for dependent tests

### 3a. White's reality check (2000) and Hansen's SPA (2005)
**Idea.** Test "the best of P strategies has no edge over the benchmark" by comparing the observed maximum performance to the bootstrap distribution of the maximum, with the bootstrap preserving the dependence across strategies and over time. Hansen's SPA studentises each strategy and removes very poor strategies from the null so they do not inflate the critical value.

**Formula.** RC statistic V = max_j sqrt(n) dbar_j; p-value from stationary-bootstrap draws V* = max_j sqrt(n)(dbar*_j - dbar_j). SPA: T = max_j max(sqrt(n) dbar_j / omega_j, 0), recentring dbar_j only when dbar_j > -sqrt(2 log log n) omega_j / sqrt(n) (the "consistent" version).

**Here.** The machine's block re-signing with common signs is a sign-flip version of the reality check with studentised statistics; it is valid if the null distribution of block means is symmetric and blocks are roughly independent. SPA's refinement (drop clearly bad patterns from the null) would lower the bar a little; small gain because P is fixed and most patterns sit near zero, not far below.

**References.** White, H. (2000) "A reality check for data snooping", *Econometrica* 68:1097-1126. Hansen, P. R. (2005) "A test for superior predictive ability", *JBES* 23:365-380.

### 3b. Romano-Wolf step-down
**Idea.** After rejecting the patterns whose t exceeds the max-t bar, remove them and recompute the bar using only the remaining patterns; repeat until no further rejection. Controls the family-wise error rate with more power than the single-step max-t, and respects dependence.

**Formula.** Order |t|(1) >= ... >= |t|(P). At step s, c_s = 95th percentile over re-signings of max_{j not yet rejected} |t*_j|. Reject all remaining with |t_j| > c_s. Stop when none is rejected.

**Change.** Cheap (reuses the 500 re-signings already drawn); bar falls slightly at each step. Use it for the "passes" list instead of a single bar. Optionally the k-FWER or FDP versions (Romano and Wolf 2007) which allow up to k false positives; these suit "many real but weak" better than strict FWER.

**References.** Romano, J. P., Wolf, M. (2005) "Stepwise multiple testing as formalized data snooping", *Econometrica* 73:1237-1282; Romano, Shaikh, Wolf (2008) "Formalized data snooping based on generalized error rates", *Econometric Theory* 24.

### 3c. Model confidence set
**Idea.** Instead of asking "is the best one better than nothing", keep a set of models that cannot be statistically separated from the best one at level alpha. Useful for choosing between a few combination methods (equal weight, IC weight, ridge, PCR), not for 345 patterns.

**Formula.** Iteratively test H0: all models in M have equal expected loss using T_max = max_{i in M} dbar_{i.}/se(dbar_{i.}); eliminate the worst model if rejected (bootstrap critical values).

**Change.** Use it at the end of the past test to compare the three to five candidate combinations; if all stay in the set, use the simplest.

**Reference.** Hansen, P. R., Lunde, A., Nason, J. M. (2011) "The model confidence set", *Econometrica* 79:453-497.

### 3d. Harvey-Liu-Zhu hurdle
**Idea.** Given the hundreds of factors tried in the literature, a new factor needs t > 3.0 (not 2.0) to be credible. It is a rule of thumb derived from Bonferroni/Holm/BHY adjustments on the published factor zoo.

**Here.** The machine's own re-signing bar (about 3.5) is the same idea calibrated to its own 345 tests; it is better than borrowing HLZ's 3.0. Mention for context only.

**Reference.** Harvey, C. R., Liu, Y., Zhu, H. (2016) "... and the cross-section of expected returns", *RFS* 29:5-68.

### 3e. Deflated Sharpe ratio
**Idea.** The best Sharpe ratio among N trials is biased upward; the DSR asks whether the observed Sharpe beats the expected *maximum* Sharpe of N zero-skill trials, while also correcting for non-normal returns.

**Formula.** Expected max under the null: SR0 = sqrt(V[SR_n]) ((1 - g) Phi^{-1}(1 - 1/N) + g Phi^{-1}(1 - 1/(N e))), g = 0.5772 (Euler-Mascheroni). DSR = Phi( (SR_hat - SR0) sqrt(T - 1) / sqrt(1 - gamma3 SR_hat + (gamma4 - 1)/4 SR_hat^2) ), with SR at the data frequency, gamma3 skew, gamma4 (non-excess) kurtosis. N should be the *effective* number of trials (3g), not 345.

**Change.** For each candidate "entry" in the daily calls report DSR with N = effective number of variants tried (patterns x horizons x weighting versions), computed on the daily spread series.

**Reference.** Bailey, D. H., Lopez de Prado, M. (2014) "The deflated Sharpe ratio", *Journal of Portfolio Management* 40(5):94-107.

### 3f. Probability of backtest overfitting (PBO, CSCV)
**Idea.** Split the history into S blocks, form all half/half combinations, pick the best configuration in-sample and see where it ranks out of sample. PBO is the fraction of splits where the in-sample winner falls below the out-of-sample median.

**Formula.** For each split c: lambda_c = logit(rank_oos(best_is)/(N + 1)); PBO = share of lambda_c <= 0. S = 16 gives C(16,8) = 12,870 splits, cheap with numpy.

**Change.** Good single-number check for the "versions" the machine compares (threshold, looser threshold, ridge variants). PBO above 0.5 means "choosing by backtest is worse than random".

**Reference.** Bailey, Borwein, Lopez de Prado, Zhu (2017) "The probability of backtest overfitting", *Journal of Computational Finance* 20(4).

### 3g. Effective number of tests from eigenvalues
**Formula.** With the correlation matrix R of the 345 IC series (or block ICs), eigenvalues lambda_k:
- Participation ratio: M_eff = (sum lambda_k)^2 / sum lambda_k^2 = P^2 / sum lambda_k^2.
- Nyholt (2004): M_eff = 1 + (P - 1)(1 - var(lambda)/P).
- Li and Ji (2005): M_eff = sum_k [I(lambda_k >= 1) + (lambda_k - floor(lambda_k))].
- Galwey (2009): M_eff = (sum sqrt(lambda_k))^2 / sum lambda_k.
**Use.** As N in the DSR, and as a sanity description ("345 patterns behave like about M_eff independent ones"). Not needed for the main test, because re-signing already handles dependence exactly.

---

## 4. Sequential testing: looking every day without inflating false positives

**Idea.** An e-process (test martingale) is a running "wealth" from betting against the null; under the null its expected value never exceeds 1, so by Ville's inequality P(it ever reaches 1/alpha) <= alpha. You can therefore check it every day and stop whenever you like; this is what the 20/40/60 check schedule tries to approximate.

**Ville's inequality.** If K_t is a non-negative supermartingale with K_0 = 1 under H0, then P(sup_t K_t >= 1/alpha) <= alpha.

### 4a. Procedure for "is this entry's hit rate above 50%?" (recommended)
One-sided beta-mixture e-value (a mixture SPRT, Robbins 1970; Wald 1945 for SPRT). With k hits in n calls:

E_n = [ integral_{1/2}^{1} p^k (1 - p)^{n - k} * 2 dp ] / (1/2)^n
    = 2^{n+1} * B(k + 1, n - k + 1) * I_{1/2}(n - k + 1, k + 1)

where B is the beta function and I_x the regularised incomplete beta (scipy.special.betaln and betainc; work in logs). Declare "hit rate above 50%" the first day E_n >= 1/alpha = 20. Valid under optional stopping and continuous monitoring. (The prior is uniform on [1/2, 1]; any prior works and keeps validity, only power changes.)

Equivalent betting form (Waudby-Smith and Ramdas 2023): K_n = prod_{i<=n} (1 + lambda_i (X_i - 1/2)), with lambda_i chosen from data before day i, e.g. lambda_i = clip(2(2 m_{i-1} - 1), 0, 1.9), m_{i-1} = (hits so far + 0.5)/(calls so far + 1). Reject at K_n >= 20.

**Simulated numbers (alpha = 0.05, 2,000 runs each, independent days):**

| true hit rate | beta-mixture: median days to stop | stopped within 250 / 1000 days | fixed-n test, 80% power, one look |
|---|---|---|---|
| 50% (null) | never (false stop rate 4% over 6,000 days) | 4% / 4% | n/a |
| 53% | about 2,400 | 9% / 22% | about 1,720 |
| 55% | about 810 | 19% / 60% | about 620 |
| 60% | about 160 | 69% / 100% | about 155 |

The betting version was within about 10% of these; a normal-mixture boundary (below) needed about 1,900 / 750 / 220 days. Rule of thumb: a valid always-on test needs roughly log(1/alpha) / KL(p || 1/2) observations, i.e. about 3.0 / (2 (p - 1/2)^2) (1,660 at 53%, 600 at 55%, 150 at 60%) plus a mixture overhead.

**Checks on the current schedule.** At 20, 40 or 60 calls nothing short of a true hit rate near 60%+ can be confirmed. The "nearest miss" (76 right of 124, 61%) gives E = 5.3, well short of 20: suggestive, not confirmed, consistent with the existing verdict. Note days are not independent for 5- and 21-session horizons (overlapping holding periods); use non-overlapping calls (every 5th or 21st day) for those, or divide the evidence by the overlap.

### 4b. Procedure for "is the mean daily spread above zero?"
Normal-mixture (Robbins) boundary for sub-Gaussian data, S_n = sum x_i, V_n = n sigma^2 (sigma from a pre-period, or a running estimate with a safety factor), rho a tuning constant (set rho sigma^2 equal to the variance expected at the time you most want power, e.g. 250 sigma^2):

reject when S_n >= sqrt( (V_n + rho) * log( (V_n + rho) / (rho * alpha^2) ) )

(This is the two-sided mixture boundary, used one-sided it is conservative; Howard, Ramdas, McAuliffe, Sekhon 2021, "Time-uniform, nonparametric, nonasymptotic confidence sequences", *Annals of Statistics* 49.) Daily spreads are fat-tailed and negatively skewed, so the sub-Gaussian assumption is shaky; the safe version is the betting confidence sequence for bounded data: clip the daily spread to [-c, c] (c = for example 4 daily standard deviations), rescale to [0, 1], and run the "hedged capital" or predictable plug-in empirical-Bernstein (PrPl-EB) process of Waudby-Smith and Ramdas (2023). Required days scale as about 2 log(1/alpha) / SR_daily^2 times a mixture overhead of 1.2-1.4: for a daily Sharpe of 0.10 (annualised 1.6), about 600-850 days; for 0.05, about 2,400-3,400.

### 4c. Alpha spending (the group-sequential alternative)
If you only look at fixed times (20, 40, 60, ...), a Lan-DeMets O'Brien-Fleming spending function alpha(t) = 2 - 2 Phi(z_{alpha/2} / sqrt(t)) (t = information fraction) gives nearly fixed-sample power. It requires a planned maximum sample size; e-values do not. Recommendation: use the e-value; it is simpler to explain and cannot be misused by looking more often.

### 4d. e-values across many entries
E-values multiply across independent evidence and average across any evidence: the average of the e-values of M entries is itself an e-value, and the e-BH procedure (Wang and Ramdas 2022, "False discovery rate control with e-values", JRSS-B 84) controls FDR at alpha under *arbitrary* dependence by rejecting the k largest e-values where k = max{k : e_(k) >= M/(alpha k)}. That fits the daily-calls table directly.

**References.** Ville (1939); Wald (1945) "Sequential tests of statistical hypotheses", Ann. Math. Statist. 16; Robbins (1970) "Statistical methods related to the law of the iterated logarithm", Ann. Math. Statist. 41; Waudby-Smith, I., Ramdas, A. (2023) "Estimating means of bounded random variables by betting", *JRSS-B* 86 (arXiv 2010.09686); Ramdas, Grünwald, Vovk, Shafer (2023) "Game-theoretic statistics and safe anytime-valid inference", *Statistical Science* 38; Lan, DeMets (1983) Biometrika 70.

---

## 5. Probabilities: calibration, scoring, conformal, and the IC-to-probability relation

### 5a. Exact rank-IC to probability relation (bivariate normal copula)
Assume the score and next return, each transformed to normal scores, are bivariate normal with Pearson correlation rho. Then:
- Spearman (rank) correlation: rho_S = (6/pi) arcsin(rho/2), so rho = 2 sin(pi rho_S / 6) (Pearson 1907; Kruskal 1958). For small values rho ~ 1.047 rho_S.
- Per stock with standardised score z (normal score of its rank): P(return > cross-sectional median | z) = Phi( rho z / sqrt(1 - rho^2) ).
- Average over the top fraction q (mean z = phi(Phi^{-1}(1 - q))/q, which is 1.755 for the top decile): approximately Phi(rho z_bar / sqrt(1 - rho^2)); exact would integrate over z, almost identical at these rho.
- Probability a stock is on the same side of the median for score and return (top half vs bottom half): 1/2 + arcsin(rho)/pi (Sheppard 1899).

| mean rank IC | rho | top-decile stock beats median | stock at z = 2 | same-side (halves) |
|---|---|---|---|---|
| 0.01 | 0.0105 | 50.7% | 50.8% | 50.3% |
| 0.02 | 0.0209 | 51.5% | 51.7% | 50.7% |
| 0.03 | 0.0314 | 52.2% | 52.5% | 51.0% |
| 0.05 | 0.0524 | 53.7% | 54.2% | 51.7% |
| 0.10 | 0.1047 | 57.3% | 58.3% | 53.3% |

Use the posterior-mean (shrunk) IC from section 1, not the in-sample IC. Caveat: daily IC varies a lot over time (market-wide moves make whole days good or bad), so the realised hit rate *of a whole day's call* is P(IC_t > 0) ~ Phi(mean IC / sd IC), a different and much more volatile quantity than the per-stock probability.

**Change to the machine.** Replace "past hit rate shrunk toward 50%" by this formula with the shrunk IC; it is smooth, has no per-entry overfitting, and gives honest numbers in the 50-54% range. Keep the empirical hit rate as a check of calibration (5b).

### 5b. Calibration
- **Platt scaling**: p = 1/(1 + exp(-(a s + b))), fitted by logistic regression of outcome on score (Platt 1999). Two parameters: the right choice when the signal is tiny and data are noisy.
- **Isotonic regression** (pool adjacent violators; Zadrozny and Elkan 2002): non-parametric, monotone. Overfits unless there are thousands of observations per bin; here it will produce staircase noise.
- **Beta calibration** (Kull, Silva Filho, Flach 2017, AISTATS): p = 1 / (1 + 1/(e^c s^a / (1 - s)^b)); a 3-parameter family that contains the identity, good when inputs are already probabilities.
**Recommendation.** Calibrate the IC-implied probability with Platt (logistic regression of "beat median" on logit(p_IC)); a fitted slope a well below 1 says the IC was overstated.

### 5c. Proper scoring rules and decomposition
- Brier score BS = mean (p_i - y_i)^2; Murphy (1973) decomposition with K bins: BS = REL - RES + UNC, REL = (1/n) sum_k n_k (p_k - ybar_k)^2, RES = (1/n) sum_k n_k (ybar_k - ybar)^2, UNC = ybar(1 - ybar).
- Log score LS = -mean[y log p + (1 - y) log(1 - p)].
- Skill vs coin: BSS = 1 - BS/0.25; LS skill = log 2 - LS. With p in 0.5 +/- 0.02 the maximum possible Brier skill is about 0.0016: tiny, so compare with a paired e-process on the per-day score differences (4b) rather than eyeballing.
**References.** Gneiting, Raftery (2007) "Strictly proper scoring rules, prediction, and estimation", JASA 102; Murphy (1973) J. Appl. Meteor. 12.

### 5d. Conformal prediction
**Idea.** Split conformal turns any point forecast into an interval with guaranteed marginal coverage under exchangeability: interval = forecast +/- the ceil((n+1)(1 - alpha))-th smallest absolute residual on a calibration set (Vovk, Gammerman, Shafer 2005; Angelopoulos and Bates 2023 tutorial; Lei et al. 2018 JASA). Under drift, adaptive conformal inference updates the level online: alpha_{t+1} = alpha_t + eta(alpha - err_t) (Gibbs and Candès 2021).
**Here.** The intervals for a single stock's 1-day return will be essentially the unconditional return distribution (the signal explains 0.04% of variance), so it adds little. Not worth building except as a demonstration of honest width.

---

## 6. Judging negatively skewed bets

The nearest-miss entry (61% right, mean not clearly above zero) is the classic signature of a short-volatility payoff: many small wins, a few large losses. Hit rate is the wrong statistic for it.

- **Probabilistic Sharpe ratio (Bailey and Lopez de Prado 2012, "The Sharpe ratio efficient frontier", J. Risk 15):** PSR(SR*) = Phi( (SR_hat - SR*) sqrt(n - 1) / sqrt(1 - gamma3 SR_hat + (gamma4 - 1)/4 SR_hat^2) ). Negative skew (gamma3 < 0) and fat tails (gamma4 > 3) widen the denominator and lower confidence. Minimum track record length: MinTRL = 1 + (1 - gamma3 SR_hat + (gamma4 - 1)/4 SR_hat^2) (Phi^{-1}(1 - alpha) / (SR_hat - SR*))^2.
- **Omega ratio (Keating and Shadwick 2002):** Omega(L) = integral_L^inf (1 - F(x)) dx / integral_-inf^L F(x) dx = E[(X - L)+] / E[(L - X)+]. At L = 0, Omega > 1 iff mean > 0; it uses the whole distribution and penalises large losses linearly.
- **Expected shortfall:** ES_q = E[X | X <= VaR_q]; report ES at 5% next to the mean; pair with the ratio mean / |ES_5%|.
- **Growth-optimal (Kelly) view:** maximise g(f) = E log(1 + f X). Third-order expansion: g(f) ~ f mu - f^2 (sigma^2 + mu^2)/2 + f^3 m3/3, where m3 = E[X^3]; negative skew reduces the optimal fraction and the achievable growth. A practical statistic: realised log growth at a fixed small fraction f (e.g. f = 1/2 of mu/sigma^2), and its e-process.
- **Testing the mean under skew.** The t of the mean has the wrong size with strong skew in small samples; use a stationary/block bootstrap of the mean or, for anytime validity, the betting CS of 4b on clipped spreads. Do not use the hit rate as the gate.

**Change to the machine.** Gate entries on the mean daily spread (with PSR at SR* = 0 and the anytime-valid mean test), report hit rate, skew, ES5% and Omega(0) alongside. An entry with high hit rate and Omega(0) near 1 is a short-volatility pattern, not an edge.

---

## 7. Online learning: prediction with expert advice

**Idea.** Hedge keeps a weight on each expert proportional to exp(-eta x cumulative loss), and guarantees that the combination's loss is within a regret term of the *best single expert in hindsight*, without any statistical assumptions. AdaHedge tunes eta automatically; FTRL is the general recipe (follow the leader plus a regulariser), of which Hedge is the entropic case; exponentiated gradient (EG) competes with the best fixed *mixture*.

**Formulas.** w_{i,t} proportional to exp(-eta L_{i,t-1}). For losses in [0, 1]: Regret_T <= sqrt((T/2) ln N) with eta = sqrt(8 ln N / T) (Freund and Schapire 1997; Cesa-Bianchi and Lugosi 2006, ch. 2). AdaHedge: eta_t = ln N / Delta_{t-1}, Delta = cumulative mixability gap (de Rooij, van Erven, Grünwald, Koolen 2014, JMLR 15). FTRL: w_t = argmin_w <w, L_{t-1}> + R(w)/eta.

**Does it make sense here?** Mostly no, as a pattern selector. With N = 345 and T = 2,300, the regret bound is sqrt(1150 x 5.84) ~ 82 loss units, i.e. about 0.036 per day on a [0, 1] loss scale, while the true differences in daily skill between patterns are of order 0.01 in IC: the guarantee is far weaker than the effects. When most experts are noise, Hedge with a tuned eta either stays near uniform (no gain) or chases the recent lucky leader (overfitting); the theory only protects you against being much worse than the best expert, which is a weak promise when the best expert is barely better than a coin. Where it can help: (i) combining a *few* (3-5) pre-built combinations (equal weight, ridge, PCR, per horizon) where the regret term ~ sqrt(T ln 5) is smaller and regime drift is plausible; (ii) as a slow, assumption-free robustness layer ("fixed-share" Hedge, Herbster and Warmuth 1998, to track a switching best).

**Change to the machine.** None for the 345 patterns. Optionally, AdaHedge over the 3-5 combination methods with the daily cross-sectional loss (1 - IC_t)/2, reported but not trusted until it passes the 4a/4b tests.

---

## Summary of recommendations

1. **Ridge (KNS) combination in PC space** instead of thresholded votes: b = (Sigma_hat + gamma I)^{-1} mu_hat, i.e. b_k = mu_k / (lambda_k + gamma) per principal component, gamma by time-block CV. Benchmark against sign-fixed equal weights and mu_hat-weights.
2. **Empirical-Bayes shrinkage of each pattern's t** with the null spread from re-signing: delta_hat_j = c t_j, c = max(0, 1 - var_null(t)/var_obs(t)) (or Tweedie t + (log f)'(t)); horizons whose counts are inside luck's range shrink to zero automatically.
3. **Anytime-valid confirmation** replacing the 20/40/60 checks: beta-mixture e-value E_n = 2^{n+1} B(k+1, n-k+1) I_{1/2}(n-k+1, k+1) >= 20 for hit rate; a betting/normal-mixture process on the daily spread for the mean, which should be the gate; e-BH across entries.
4. **Probabilities from the shrunk IC**: P = Phi(rho z / sqrt(1 - rho^2)), rho = 2 sin(pi IC / 6); Platt-calibrate; score with log/Brier skill.

Not worth the effort: random-feature "complex" models, isotonic calibration, conformal intervals for single-stock returns, Hedge over 345 patterns, lasso on near-copies, HLZ's 3.0 bar (the machine's own re-signing bar is better).
