# Astra 6.2: first principles (2026-11-23)

Asked with the full results table (close-to-close outcomes, before rules v3). Unedited. The question is in `8 the question put to Astra and Grok.md`.

---

**My reading is that the project has found one candidate signal, slow momentum, and has weak evidence that it can time when to use it.** Thirteen versions of the same trade clearing a threshold is interesting. The strongest economic result is 14 basis points gross on 124 selected days. Its standard error is about 9 basis points, and an after-close decision may miss part of that return. I would fix the universe and the execution clock before changing the learner.

## 1. Deciphering the record

| Observation | Mechanism | Check on the existing record |
|---|---|---|
| **61% right, mean t = 1.5** | Hit rate gives a one-basis-point win and a two-percent win equal weight. If \(p\) is the win rate and \(W,L\) are average win and loss magnitudes, mean spread is \(pW-(1-p)L\). At 76 wins and 48 losses, losses averaging 1.58 times wins erase the edge. Large moves of either sign can inflate the standard error. Negative skew is plausible but unproven. | Report \(W,L\), spread quantiles, the five largest contributions of each sign, and results by calendar year. |
| **12-month momentum clears the one-day bar only** | Signal lookback and holding period measure different things. If expected daily spread persists, cumulative signal grows roughly as \(h\), return noise as \(\sqrt h\), but independent dates fall roughly as \(1/h\). Significance can therefore stay roughly constant. A drop could reflect reversal, changing exposures, or noise. | Freeze each date’s ranks. Plot incremental spreads on days 1–21, splitting the first overnight from the first open-to-close return. Use the same signal dates throughout. |
| **21-day best guess wins 31/73** | Under independent fair calls this is only about 1.3 standard deviations below half. Selecting signs from weak historical ICs can also leave the portfolio exposed to a factor that subsequently reverses. | Attribute losses by year and sector, and compare with the frozen momentum spread on identical dates. Verify actual holding intervals because a five-session decision grid alone permits overlap. |
| **Luck typically gives 8 crossings but sometimes 60** | The count is a sum of indicators. Its variance includes twice the sum of pairwise covariances. A favourable random sign sequence can push an entire family across 2 together. The median count need not equal the mean. | Plot the permutation histogram and identify which families cross together in its upper tail. Repeat with longer blocks because adjacent blocks can share forward-return shocks. |
| **Trend looks better on 12 megacaps** | A concentrated universe changes the trade, and a few large winners can dominate its spread. The 21-day mean of +0.70% has a standard error near 0.88%. Historical selection of today’s giants can also favour past winners. | Compare the **paired difference** on the same 73 dates with sector- and size-matched baskets selected using information available on each date. Show leave-one-name-out results. |

The one-day count of 75 exceeds its reported 95th-percentile null count of 43. The other two counts are inside theirs. That supports a family-level investigation. The randomization controls only the searches included in it, and its validity requires approximate joint sign symmetry across independently flippable blocks. Five hundred draws give only about 25 observations in the upper 5% tail.

## 2. What the sample can resolve

Let \(\sigma\) be the date-to-date standard deviation of a daily cross-sectional rank IC and \(D=1+2\sum_{k\ge1}\rho_k\) its serial-dependence multiplier. Summing the covariances of the daily observations gives \(SE(\bar{IC})\simeq\sigma\sqrt{D/T}\). For nearly fixed ranks and overlapping sums of independent daily shocks, \(\rho_k\simeq1-k/h\) for \(k<h\), giving \(D\simeq h\). Estimate \(D\) per family from the data.

For \(K_{\rm eff}\) independent Gaussian tests the two-sided 5% maximum cutoff is \(c=\Phi^{-1}[(1+.95^{1/K_{\rm eff}})/2]\). Use the empirical \(c\simeq3.5\) provisionally. A true mean of \(c\,SE\) has about **50% power** to clear it. For 80% power use \((c+0.84)SE\).

Under independent random ranks, \(\sigma=1/\sqrt{N-1}=0.045\) at \(N=500\). Sector and style exposures can make realized IC substantially noisier. With \(T=2,300\):

| Assumed daily \(\sigma\) | 1 session | 5 sessions | 21 sessions |
|---|---:|---:|---:|
| 0.045, 50%-power IC | .0033 | .0073 | .0151 |
| 0.10, 50%-power IC | .0073 | .0163 | .0334 |
| 0.10, 80%-power IC | .0091 | .0202 | .0415 |

At \(\sigma=.10\), detecting IC **.01, .02, .03** at 50% power takes respectively **1,225h, 307h, 137h sessions**, rounded up in the coefficients. At fixed \(T=2,300\), the independent-rank calculation gives \(N\ge1+3.5^2h/(2300\,IC^2)\), or roughly \(1+(53.3,13.3,5.9)h\) independent names respectively. Adding correlated stocks may buy much less. No horizon is intrinsically hopeless. A prespecified signal avoids the 345-way hurdle, while sparse events diluted across 500 names can evade even a sound full-universe test.

## 3. A learner with an explicit objective

Use standardized cross-sectional **ranks** for predictors \(X\) and outcome \(y\). Then \(m=E[Xy]\) is the vector of population ICs and \(G=E[XX^\top]\) is the predictor correlation matrix. Expanding squared forecast error gives \(1-2w^\top m+w^\top Gw\). Given estimated ICs \(b\), minimizing posterior expected loss gives \(Gw=E[m\mid b]\). This distinguishes uncertainty about ICs from redundancy among predictors. The stored t-values alone identify neither matrix.

Use `b = B.mean(axis=1)` for equal blocks. For \(M\) approximately independent blocks, `V = np.cov(B)/M` estimates the sampling covariance of \(b\). With serial dependence use a block-lag covariance estimate or longer blocks. Re-signing centered block means jointly provides a null covariance check. The reported self-normalized statistic is only approximately a Gaussian z-score.

For \(b\mid m\sim N(m,V)\), differentiating the marginal density gives **Tweedie’s formula**, \(E[m\mid b]=b+V\nabla\log f(b)\). A practical marginal two-groups prior puts mass \(1-\pi\) at zero and mass \(\pi\) on \(N(0,\tau^2)\). Writing \(v_j=V_{jj}\) and \(\phi_v\) for a zero-mean normal density of variance \(v\),

\[
q_j=\frac{\pi\phi_{v_j+\tau^2}(b_j)}
{(1-\pi)\phi_{v_j}(b_j)+\pi\phi_{v_j+\tau^2}(b_j)},\qquad
\hat m_j=q_j\,\frac{\tau^2}{v_j+\tau^2}b_j .
\]

That conditions on one observation per coefficient. I would first collapse near-identical families, then fit \(\pi,\tau\) by marginal likelihood on development data. For a simple **joint** alternative with Gaussian family prior covariance \(A\), use `mhat = A @ np.linalg.solve(A + V, b)`, then `w = np.linalg.solve(G + lam*np.eye(len(b)), mhat)` with positive regularization. Estimate \(G\) from historical daily ranks. The second solve limits exposure to nearly duplicate bets.

Shrinkage would change weights and coverage. Its effect on net returns is unknown. Use the read history for development, freeze the learner, and compare its **paired net spread against trend on new dates**, counting abstention as cash.

## 4. Payoff, monitoring, and probabilities

- **Payoff.** At fixed gross exposure report mean net spread, average loss in the worst 5%, and mean \(\log(1+fR_{\rm net})\) for a prespecified capital fraction \(f\). Log growth prices loss magnitude directly. With 124 calls the worst 5% contains only about six observations.
- **Daily looks.** For one frozen rule and resolved nonoverlapping calls, let \(X_i=1\) for a win and count ties as losses. Start \(E_0=1\), multiply by 1.1 on wins and 0.9 on losses, and stop at \(E_n\ge20\). Under \(P(X_i=1\mid\text{past})\le.5\), expected multiplier is at most one, so the chance of ever crossing is at most 5%. Under iid true \(p\), log drift is \(d=p\log1.1+(1-p)\log.9\). The final overshoot is below \(\log1.1\), so expected calls lie between \(\log20/d\) and \(\log22/d\): **3,011–3,107 at 53%, 598–618 at 55%, and 199–206 at 60%**, approximately. The exact expectation is \(\sum_{n\ge0}P(\tau>n)\), computable by propagating binomial path mass and removing paths at first crossing. These are calls, not trading days. Use the sign of the paired net improvement if benchmark outperformance is the question. This tests win probability only.
- **Stock probabilities.** There is no distribution-free map. Spearman IC fixes one moment of two uniform ranks, while the desired probability depends on their conditional distribution. Under a Gaussian copula, \(r=2\sin(\pi IC/6)\) and \(P(\text{beat population median}\mid u)=\Phi[r\Phi^{-1}(u)/\sqrt{1-r^2}]\). At IC .02 the 90th-percentile stock has probability **51.1%**. Average over each decile for comparison. The reported 47–53% is compatible with weak ranking skill, but calibration fitted on those dates needs fresh validation.

## 5. Information worth one trial

These are **subjective priors** for a positive incremental population IC after controlling for price trend and sector. Ranges are my expected orders of magnitude **conditional on an effect**, for a full-universe 21-session ranking with neutral scores on unaffected names. They are not measured results.

| Rank | Point-in-time input and proposed score | Probability | IC if present |
|---|---|---:|---:|
| 1 | Earnings surprise against a frozen seasonal earnings forecast, from original release exhibits. [SEC Item 2.02 filings](https://www.sec.gov/answers/form8k.htm) | 60% | .005–.020 |
| 2 | Numerical guidance revisions versus management’s previous range, from original releases. [EDGAR filings](https://www.sec.gov/search-filings) | 55% | .004–.015 |
| 3 | Cash-flow versus earnings divergence, using originally filed quarter values. [SEC XBRL filings API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | 40% | .003–.012 |
| 4 | Clusters of disclosed insider open-market purchases. [SEC Form 4 data](https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets) | 35% | .002–.010 |
| 5 | Newly disclosed acquisition agreements, distinguishing acquirer and target. [SEC 8-K filings](https://www.sec.gov/files/form8-k.pdf) | 25% | .001–.008 |

Use first public dissemination before the decision cutoff. Earnings and guidance often arrive together, so measure guidance’s increment conditional on earnings. A quarterly bulk file can reconstruct original filings but cannot establish that the bulk file itself was available on the trade date. [SEC dissemination and index timing](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)

## 6. What I would build

Delete the random products, top-ten selection, duplicate residual voters, and daily full-library permutation runs. Cache rolling sufficient statistics and update family estimates when labels mature. The largest statistical costs are repeatedly selecting a winner, treating clones as supporting votes, and discarding most one-day test dates. Freeze one primary horizon and score every eligible new date.

**My prior is 20%** that a frozen learner built with this budget beats volatility-scaled trend in expected net spread on the same universe and exposure over the next five years. I would spend the first week rebuilding historical membership, checking terminal delisting payoffs, and repricing both strategies from the first executable price after each decision, including turnover, spread and borrow. The local closes and volume support the universe repair. Historical next-open fills require corresponding open data. Then I would run **one earnings-surprise increment against trend**. Establishing whether the observed 14 basis points survive the execution clock is worth more than finding a fourteenth version of momentum.