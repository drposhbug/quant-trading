# Grok: first principles, the long answer (2026-11-23)

The same question as Astra (file 8), with the results as they stood before rules v3. It arrived about 55 minutes after it was asked, after the decision had been written. Unedited. What was taken from it afterwards: luck is now measured on blocks twice the horizon (its point that neighbouring blocks share outcomes). Not taken: its noise figure of 0.045 a day assumes independent stocks; the measured figure was 0.19.

---

The numbers describe one small, known effect sitting on the detection boundary, plus a library of copies of it. The rest is noise that the evaluation metrics misread.

## 1. What is going on

**(a)** A daily rank IC near 0.01 moves the average of about 167 favoured names above the average of 167 avoided names on roughly 60% of days, because that comparison averages idiosyncratic noise down by about \(\sqrt{167}\). The same IC is only a few basis points of spread, so the mean over about 124 calls stays inside sampling error. Negative skew (a handful of large down days, many small up days) pushes the mean down relative to the hit rate. Both readings are one fact.

Under a Gaussian copula, with \(s\) the cross-sectional z-score and \(\rho\) the rank IC,

\[
P(\text{top third beats bottom third}) \approx \Phi(19.9\,\rho)
\]

for \(N=500\). A 61% hit rate is \(\rho \approx 0.014\). The same \(\rho\) puts the top decile's probability of beating the median at

\[
\Phi\!\left(\frac{\rho \cdot 1.76}{\sqrt{1-\rho^2}}\right) \approx 0.51,
\]

inside the 47–53% band you measured. The per-stock calibration looks null because that is what an IC of this size looks like one stock at a time. (The 61% itself has a binomial z near 2.5 on 124 tries; the spread's t of 1.5 is the more relevant one, and it is weak.)

**(b)** Sampling noise of one day's rank IC is \(\sigma_1 \approx 1/\sqrt{N} = 0.045\) when the pairs \((s_i, r_i)\) are close to iid. Over \(T=2300\) days,

\[
\mathrm{se}(\overline{\mathrm{IC}}) \approx \sigma_1 \sqrt{h/T}.
\]

A true daily IC of 0.004 is a t near 4 at \(h=1\), which is exactly the 3.5–4.2 cluster you see, and it is one signal: 12-month return, raw and with a beta stripped. The same economic edge at horizon \(h\), if it accrues like a drift, is an IC larger by about \(\sqrt{h}\) and a t of the same size. Your 21-session t falls through the bar because a few violent months dominate \(\sum m_b^2\) in \(t=\sum m_b/\sqrt{\sum m_b^2}\), and because 0.004 is the edge of what \(T\) can support. This is a small momentum effect with crash kurtosis, not a one-day anomaly. Probability about 0.6. Probability about 0.3 that even the daily clearance is the maximum of a search whose 95th percentile is already 3.5.

**(c)** At 21 sessions the count of patterns with \(|t|>2\) (10, luck typically 9) matches the null. "Best guess" (bar at 2) therefore votes for noise. On 73 calls, 42% has binomial z near \(-1.3\). A rule that up-weights whatever just printed \(|t|>2\) also leans on one-month reversal, the main short-horizon cross-sectional fact. Probability 0.75 this path is noise; about 0.2 that the selection rule adds a real negative tilt.

**(d)** Under independence, \(345 \times P(|Z|>2) \approx 16\) with sd near 4, so a 95th percentile near 25, not 60. The observed width (typically 8, sometimes 40–60) is a herd: many of the 345 are transforms of one price history, so one latent factor drags dozens over the line together or none. The re-signing bar already says the same thing. The 95th percentile of the max \(|t|\) is 3.5; an independent calculation would put that percentile near 3.8 for 345 tests and near 3.5 for about 110. So \(K_{\mathrm{eff}} \approx 110\) for the extreme, and less than that for the bulky count. "75 patterns" at the 1-session horizon is one factor plus clones.

**(e)** On the 500, trend is a coin flip (t of \(-0.5\), \(-0.1\), \(-0.3\)). On 12 megacap tech names the same rule is 44 of 73, mean \(+0.70\%\), t \(0.8\). Those names are one correlated bull path, and a watchlist of today's winners built with hindsight over-represents names that trended. Probability about 0.75 that this is that path. It is not a second mechanism.

Two setup errors sit underneath all five. The universe is S&P members of a fixed date, so losers who left are missing; that manufactures momentum. A point-in-time list with dead names is the dataset. And independent re-signing of blocks is about 15% anti-conservative at \(h=5\) and \(h=21\): adjacent blocks of length \(h\) have correlation near 0.16 from overlapping forward windows, which random signs destroy, so the null used to build the bar is narrower than the null that generates the data. At \(h=1\) with a 5-day block the returns do not overlap and the bar is valid. The re-signing design itself — one sign per block, shared across patterns — is the right way to keep cross-pattern correlation.

## 2. The smallest IC you can see

\[
\mathrm{IC}_{\min}(h) = z \,\sigma_1 \sqrt{h/T}, \qquad \sigma_1 = 1/\sqrt{500} = 0.045, \quad T=2300.
\]

Sector-clustered signals plausibly push \(\sigma_1\) toward 0.06 (opinion, probability 0.5). Portfolio-breadth formulas do not apply here: a market factor that is constant across names cancels in a demeaned cross-section and does not inflate rank-IC noise.

| \(h\) | se | min IC, one pre-set test (\(z=2\)) | min IC after the search (\(z=3.5\)) |
|---|---|---|---|
| 1 | 0.00093 | 0.0019 | 0.0033 |
| 5 | 0.0021 | 0.0042 | 0.0073 |
| 21 | 0.0043 | 0.0086 | 0.015 |

No pattern in this library has a daily IC near 0.01, or its t would be near 11, and none is. So the machine can see only a persistent daily IC of a few thousandths, or a monthly IC above about 0.015 if you insist on searching and above about 0.009 if you pre-register one feature. Event signals die in the average: an IC of 0.10 on the 2% of names with news that day is an unconditional IC near 0.002, under the floor. Sparse information is invisible to a score that fires for every name every day.

Years required at \(N=500\), search bar \(z=3.5\): an IC of 0.01 needs \(T \approx 245\,h\) (about 22 years at \(h=21\)); 0.02 needs \(T \approx 61\,h\); 0.03 needs \(T \approx 27\,h\). At \(h=1\) you already have all three. Alternatively, at \(T=2300\), \(h=21\), \(z=3.5\), an IC of 0.01 needs about 1,100 names, 0.02 about 280, 0.03 about 125. A pre-registered test (\(z=2\)) at \(h=21\) sees an IC of 0.01 with the \(T\) you have.

## 3. Weights

\(w=\max(|t|-c, 0)\) hard-thresholds a correlated vector and then sums clones. The squared-error minimizer is the posterior mean of the true IC.

Univariate, if \(t\sim N(\mu,1)\) and the marginal density of the observed t's is \(f\), Tweedie's formula is

\[
\widehat\mu(t) = t + (\log f)'(t).
\]

Two groups, null probability \(\pi_0\), slab \(\mu\sim N(0,\tau^2)\):

\[
\mathrm{lfdr}(t)=\frac{\pi_0\,\phi(t)}{f(t)}, \qquad
\widehat\mu(t)=(1-\mathrm{lfdr}(t))\, t\, \frac{\tau^2}{1+\tau^2}.
\]

Estimate \(f\) and \(\pi_0\) from the 345 t's (central match \(\widehat\pi_0=\widehat f(0)/\phi(0)\), capped at 1). Estimate \(f_0\) from the stored re-signing draws. Where \(f\) matches \(f_0\), every weight is zero.

That univariate shrink still treats 13 momentum copies as 13 signals. The block matrix \(Y\) (\(345 \times B\)) is the cure. Numpy:

```python
m  = Y.mean(1)
Yc = Y - m[:, None]
U, S, _ = np.linalg.svd(Yc, full_matrices=False)
eig = S**2 / (Y.shape[1] - 1)
# keep components above the bulk; r will be small
scores = U[:, :r].T @ Y            # r x B
# shrink each row of `scores` by Tweedie / two-groups
mu = U[:, :r] @ scores.mean(1)     # back to pattern space
```

Cross-sectional blend, with \(R_x\) the average \(345\times 345\) correlation of the z-scores across names:

\[
w \propto R_x^{+} \,\widehat\mu.
\]

Clones then receive one shared weight. James–Stein, \(\widehat C=\mathrm{Cov}(Y)/B\), \(q=m^\top C^{+} m\), \(\widehat m=(1-(r-2)/q)_+ m\), is the linear version; with a spike at zero it shrinks the real factor too hard and the nulls too little. Prefer two-groups on the factors.

This would have changed the table in a way you can check without a second look at 2019–2026. At 5 and 21 sessions, \(f \approx f_0\) from the draws you stored, so the posterior is silent where "best guess" traded. At 1 session the posterior collapses to one momentum factor, which is the trend row already in the table. The gap between "sure" and trend was part of the look you have spent. Do not retune it on those years.

## 4. Yardstick, sequential test, IC map

**(i)** Decide on the daily rank IC, Fisher-transformed, \(z_t=\mathrm{artanh}(\mathrm{IC}_t)\), with a Newey–West standard error at lag \(h-1\). The correlation is bounded and close to symmetric. The dollar spread is the skewed object, so its t can sit near zero while most days are green. Hit rate bins a 5 bp win with a 200 bp win. Alongside, pre-commit a scale \(c\) and track \((1/n)\sum \log(1+x_i/c)\). That is the growth the skew actually leaves you.

**(ii)** Update only when a non-overlapping bet resolves (every session at \(h=1\), every \(h\) sessions otherwise). Peeking at a cumulative sum of overlapping bets on intermediate days does not add an increment. Wald SPRT of \(p=0.5\) against \(p=q\), \(\alpha=0.05\), \(\beta=0.20\): boundaries \(a=\ln 16=2.773\), \(b=\ln(0.2/0.95)=-1.558\). Drift \(\delta(p)=p\ln(2q)+(1-p)\ln(2(1-q))\). Expected length \((0.8a+0.2b)/\delta(q)\) under the alternative and \((0.05a+0.95b)/\delta(0.5)\) under the null, overshoot ignored:

| True hit rate | \(E[N]\) if real | \(E[N]\) under 50% |
|---|---|---|
| 53% | ~1060 | ~740 |
| 55% | ~380 | ~270 |
| 60% | ~95 | ~66 |

A 53% hit rate at a 21-session step is a lifetime. Test the Fisher-z IC instead. For a spread with mean 0.14% and sd 1%, the normal SPRT stops in about 200 independent bets if that mean is real, and in several times that if the truth is half the point estimate. Always-valid version, so you may look every completed bet forever: stitch a boundary with slices \(n_k=\lfloor 1.5^k\rfloor\), \(\alpha_k=\alpha\cdot 6/(\pi^2 k^2)\), and reject only when \(|S_n|\) exceeds \(\sigma\sqrt{2n\log(1/\alpha_{k(n)})}\).

**(iii)** Large \(N\), median near 0:

\[
P(r_i>\mathrm{median}\mid s_i)=\Phi\!\left(\frac{\rho\, s_i}{\sqrt{1-\rho^2}}\right),
\]

with Spearman \(\rho_s\) and Pearson \(\rho\) related by \(\rho=2\sin(\pi\rho_s/6)\); at these magnitudes they are the same number. Mean \(s\) of the top decile is 1.76, of the top third 1.09. Your decile band caps \(|\rho|\) at about 0.05, and the flatness you describe is what \(\rho\approx 0.01\) produces.

**(iv)** Gross tercile spread per day \(\approx \rho \cdot \sigma_{\mathrm{xs}} \cdot 2.18\). At \(\rho=0.005\) and cross-sectional dispersion 1.5% that is about 1.6 bp a day before costs, before you thin it by the "no voter, no bet" rule. That is the economic size of anything this sample can barely detect.

## 5. Information that is not a price transform

Ranked by probability of a real increment in this universe, at 1–21 sessions, after costs. Unconditional ICs are diluted by quiet names; the framework will miss them unless the feature is non-zero most days or you change the test to event days only.

| # | Data | Source | P(real here) | IC to expect |
|---|---|---|---|---|
| 1 | 8-K item codes at acceptance time (results, restatements, officer exits) | data.sec.gov submissions, `acceptanceDateTime` | 0.35 | ~0.005 unconditional; ~0.03 on filing days, over 5–21 sessions |
| 2 | Short-interest level and change, lagged to the FINRA release | FINRA equity short-interest files (publication is days after settlement; using the settlement date is look-ahead) | 0.28 | ~0.008 at 21 sessions, defined for every name |
| 3 | Form 4 open-market buys, code P, clustered, excluding 10b5-1 | EDGAR Form 4 XML | 0.25 | ~0.002 unconditional; ~0.02 conditional, 21 sessions |
| 4 | Seasonal-random-walk earnings surprise from XBRL | data.sec.gov companyfacts, filed timestamp | 0.22 | ~0.003 unconditional; ~0.015 on reporters. Weaker than analyst SUE, which is not free |
| 5 | Index addition and deletion announcements | S&P DJI press releases plus the point-in-time membership file you have | 0.20 | ~0.001 unconditional; a large IC on a handful of names, mostly eaten by the spread |

Options-implied skew would outrank all five and is not free. Anything that is a smooth function of the adjusted OHLC you already store will not clear the bar the price library failed.

## 6. What to delete

CPU is not the constraint; a few minutes can correlate 500 names. The multiple-testing bar is the constraint.

Delete the grid of 15 outside series. QQQ, XLK and SMH are one bet, and a beta residual of a 12-month return against SPY is almost the raw return. Keep one residual. Delete name-versus-name lead-lag: that is on the order of \(500^2\) correlated tests of nonsynchronous trading. Delete the bar-at-2 entry. Delete window clones of skew, maximum day, and up-day share; if you want the lottery effect, pre-register one. Delete hit rate as a stopping rule.

Stop throwing away four of every five sessions at the 1-session horizon. Those days are almost independent, and the thinning costs a factor of about \(\sqrt{5}\) in the only t-stat that had a chance. Keep the block matrix, the shared-sign null, and silence when no factor survives shrinkage.

## 7. Prior

Probability about **0.10** that anything built on this shelf beats plain 12-minus-1 momentum after costs on a fresh window. About 0.05 of that is "another price-volume variant." About 0.15 is "one pre-registered non-price feature, 8-K or short interest, adds a real increment," and the process as actually run — search, then lower the bar, then read the same years — pulls the joint probability back to 0.10. The walk-forward table has been read. It is spent.

I would use the same effort to switch on the point-in-time membership, freeze a single 12-minus-1 residual plus at most two non-price features, and run the always-valid IC test on new days only. Most days the output should be no bet. That is the machine being right.
