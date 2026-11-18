# Core quant math for sizing, correlation and risk (12–13 name long-only daily-rebalanced US mega-cap tech book)

Source note for the report writer: the search tools worked, but the two primary PDFs I downloaded (DSR paper, Gârleanu-Pedersen manuscript) were binary and no PDF parser was available, so I could not read their full text. Formulas marked **[std]** are standard published results that I wrote from the cited primary paper's known content. I did not re-read them from the full text this session. DOIs/SSRN IDs were written from memory unless a search result returned them. Worked numbers marked **[calc]** are my own arithmetic from the formulas.

## Q1. For each method: formula, assumptions, out-of-sample evidence, failure modes

### Takeaway
For a concentrated, highly correlated tech book, the methods that hold up out of sample are the ones that don't estimate expected returns: inverse vol, ERC, HRP and shrunk minimum variance. Use them together with volatility scaling and well under full-Kelly leverage. Mean-dependent optimizers (full Kelly Σ⁻¹μ, Markowitz) are dominated by estimation error at this sample size.

### Cited Findings

**Kelly criterion (single asset, continuous time)**
- In continuous time (GBM), growth is g(f) = r + f(μ − r) − f²σ²/2, which is maximized at f* = (μ − r)/σ². Discrete binary-bet Kelly is f* = p − q/b. — [Thorp, "The Kelly Criterion in Blackjack, Sports Betting and the Stock Market"](https://sites.oxy.edu/lengyel/M330/thorp/paper.htm); [Thorp 2006 (Handbook chapter)](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf)
- [std] At the optimum, g* = r + S²/2, where S = (μ − r)/σ. At fraction c of Kelly, excess growth is (c − c²/2)S² and portfolio volatility is c·f*·σ = c·S. So half Kelly gives 75% of the max growth at 50% of the volatility. Betting 2× Kelly gives zero excess growth, and anything above 2× Kelly gives negative growth. — [Thorp 2006](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf)
- [std] Drawdown law under GBM with fraction c of Kelly: P(wealth ever falls to fraction x of its starting value) = x^(2/c − 1). Full Kelly has a 50% chance of halving at some point. Half Kelly cuts that to 12.5%, and quarter Kelly to x^7, about 0.8%. — [Thorp 2006](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf); [MacLean, Thorp, Ziemba "Good and bad properties of the Kelly criterion"](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)
- Multi-asset continuous Kelly is f* = Σ⁻¹(μ − r·1), which is the unconstrained log-utility (γ = 1) Merton portfolio. [std] — [Thorp 2006](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf)
- MacLean-Thorp-Ziemba list Kelly's good properties: it maximizes asymptotic growth, minimizes the expected time to reach large goals, and leads the median outcome. Its bad property is that Arrow-Pratt risk aversion is very low, so the bets are very large and short-run risk is high. Fractional Kelly (Kelly blended with cash) smooths the wealth path at the cost of expected final wealth. — [Good_Bad_Kelly](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf); [Kelly/Ziemba chapter](https://www.maths.ed.ac.uk/mckinnon/blackouts/StochOptFinanceAndEnergySpringer/Chap1_KellyZiemba.pdf)
- [std] For lognormal assets, fractional Kelly with fraction c is equivalent to CRRA utility with relative risk aversion γ = 1/c. So half Kelly corresponds to γ = 2 (MacLean, Ziemba & Li). — [Good_Bad_Kelly](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)
- Practitioner sources say most users bet half Kelly or less, because Kelly assumes the true parameters are known. — [Kelly calculator page (secondary)](https://ryanoconnellfinance.com/calculators/kelly-criterion-calculator/)
- Errors in means cost far more than errors in variances or covariances. Chopra & Ziemba (1993) find mean errors about 10× as damaging as variance errors and about 20× as damaging as covariance errors (at risk tolerance 50). [std] — [Chopra & Ziemba 1993, JPM, doi:10.3905/jpm.1993.409440](https://doi.org/10.3905/jpm.1993.409440)
- Kan & Zhou (2007) show that with estimated parameters the optimal rule is a scaled-down version of the plug-in mean-variance (Kelly) portfolio, mixed with the estimated minimum-variance portfolio. [std] — [Kan & Zhou 2007, JFQA, doi:10.1017/S0022109000004129](https://doi.org/10.1017/S0022109000004129)

**Risk parity / equal risk contribution (ERC)**
- [std] Risk contribution is RC_i = w_i(Σw)_i / σ_p, and Σ RC_i = σ_p. ERC sets RC_i = σ_p/N for all i. The ERC portfolio's volatility lies between minimum variance and 1/N. With equal pairwise correlations, ERC reduces to inverse volatility, w_i ∝ 1/σ_i. — [Maillard, Roncalli & Teiletche 2010, SSRN 1271972](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1271972)
- [std] Solver: minimize ½ yᵀΣy − (1/N) Σ ln y_i with y > 0, then set w = y/Σy. This problem is convex with a unique solution (Spinu 2013). Off-the-shelf implementations are in riskfolio-lib and PyPortfolioOpt. — [Maillard et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1271972)

**Inverse volatility**
- w_i = (1/σ_i) / Σ_j (1/σ_j). This ignores correlations. One study found inverse-vol portfolios the most robust when covariance estimates are crude, ahead of ML-based portfolios. — [IISc study](https://eprints.iisc.ac.in/77367/1/ris_7-3_2019.pdf)

**Minimum variance**
- [std] Unconstrained: w = Σ⁻¹1 / (1ᵀΣ⁻¹1). Long-only requires a QP. Jagannathan & Ma (2003) show that imposing a no-short constraint is equivalent to shrinking the covariance matrix, which is why long-only min-var works better out of sample than unconstrained. — [Jagannathan & Ma 2003, JF, doi:10.1111/1540-6261.00580](https://doi.org/10.1111/1540-6261.00580)
- In the HRP walk-forward thesis, minimum variance had the lowest realized risk, beating HRP. — [CBS HRP thesis](https://research-api.cbs.dk/ws/portalfiles/portal/76452070/1332322_Master_Thesis_Hierarchical_Risk_Parity.pdf)
- Failure mode: the weights depend on Σ⁻¹, so they are driven by the smallest, noisiest eigenvalues, and the portfolio concentrates in the 2–4 lowest-vol, lowest-correlation names. — see RMT below; [Michaud 1989 "The Markowitz optimization enigma", FAJ](https://doi.org/10.2469/faj.v45.n1.31)

**1/N benchmark**
- [std] DeMiguel, Garlappi & Uppal (2009) found that none of 14 optimizers consistently beat 1/N out of sample. For 25 assets, sample-based mean-variance needed roughly 3000 months of data to beat it. — [DeMiguel et al. 2009, RFS, doi:10.1093/rfs/hhm075](https://doi.org/10.1093/rfs/hhm075). One summarized study found 1/N had the highest vol and max drawdown among risk-based methods, so whether 1/N wins depends on setup. — [Quantpedia HRP summary](https://quantpedia.com/hierarchical-risk-parity/)

**Hierarchical Risk Parity (HRP)**
- [std] López de Prado (2016) works in three steps: (1) tree clustering on the distance d_ij = √(½(1 − ρ_ij)); (2) quasi-diagonalization, which reorders Σ by the dendrogram; (3) recursive bisection. At each split, cluster variance is V = w̃ᵀΣw̃ with inverse-variance weights w̃ inside the cluster, and the allocation is α = 1 − V₁/(V₁ + V₂) to the left half and 1 − α to the right. The method needs no matrix inversion. — [López de Prado 2016, JPM, SSRN 2708678](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2708678); [Quantpedia](https://quantpedia.com/hierarchical-risk-parity/)
- Out-of-sample evidence is mixed. In Monte Carlo, HRP had lower OOS variance than MV, ERC, IVP and 1/N. In walk-forward tests it beat IVP, 1/N and ERC on risk measures but lost to MV. HRP also proved less robust to covariance misspecification than non-hierarchical methods. — [CBS thesis](https://research-api.cbs.dk/ws/portalfiles/portal/76452070/1332322_Master_Thesis_Hierarchical_Risk_Parity.pdf). A forum backtest favoured HRP OOS, but that result is anecdotal. — [Quantopian archive](https://quantopian-archive.netlify.app/forum/threads/hierarchical-risk-parity-comparing-various-portfolio-diversification-techniques)

**Factor models**
- [std] CAPM: E[r_i] − r_f = β_i(E[r_m] − r_f), with β_i = Cov(r_i, r_m)/Var(r_m). Fama-French 3-factor adds SMB and HML. The 5-factor model adds RMW and CMA. — [Fama & French 1993, JFE](https://doi.org/10.1016/0304-405X(93)90023-5); [Fama & French 2015, JFE](https://doi.org/10.1016/j.jfineco.2014.10.010)
- [std] Barra/fundamental: r = Bf + ε, which gives Σ = BFBᵀ + D, with exposures B known (industries and styles), factor covariance F estimated, and D diagonal specific variance. Statistical/PCA: Σ = VΛVᵀ, keeping the top k eigenvectors and putting the residual into D. — [Grinold & Kahn, *Active Portfolio Management* (book, not fetched)](https://www.mheducation.com/highered/product/active-portfolio-management-quantitative-approach-producing-superior-returns-controlling-risk-grinold-kahn/M9780070248823.html)
- Grinold-Kahn "fundamental law": IR ≈ IC·√BR. [std] — same book.
- The Ledoit-Wolf single-index and constant-correlation targets are themselves 1-factor structures. — [Ledoit-Wolf notes](https://reasonabledeviations.com/notes/papers/ledoit_wolf_covariance)

**Covariance estimation**
- [std] EWMA/RiskMetrics: σ²_t = λσ²_{t−1} + (1 − λ)r²_{t−1}, and Cov_t = λCov_{t−1} + (1 − λ)r_{t−1}r_{t−1}ᵀ. Recommended λ is 0.94 for daily data and 0.97 for monthly. Half-life = ln 0.5/ln λ, about 11 trading days at λ = 0.94. — J.P. Morgan/Reuters, *RiskMetrics Technical Document* (1996), 4th ed. (no URL fetched this session)
- Ledoit-Wolf (2004): Σ̂ = δF + (1 − δ)S, with F the constant-correlation target (sample variances on the diagonal, average sample correlation off it). δ is chosen to minimize expected Frobenius loss. [std] δ* ≈ max(0, min(1, κ/T)), κ = (π − ρ)/γ. — [Ledoit-Wolf notes](https://reasonabledeviations.com/notes/papers/ledoit_wolf_covariance); [fynance implementation](https://fynance.readthedocs.io/en/latest/generated/fynance.portfolio.covariance.ledoit_wolf.html)
- [std] Implementation trap: `sklearn.covariance.LedoitWolf` shrinks toward a scaled identity (the Ledoit-Wolf 2004 JMVA version), not toward constant correlation. PyPortfolioOpt's `CovarianceShrinkage(...).ledoit_wolf(shrinkage_target="constant_correlation")` and fynance (default `const_corr`) implement the 2004 JPM target. — [fynance](https://fynance.readthedocs.io/en/latest/generated/fynance.portfolio.covariance.ledoit_wolf.html)
- A comparison of nine covariance estimators for portfolio optimization found the benefit of better estimators depends on the N/T ratio and the objective. — [arXiv 1004.4272](https://arxiv.org/pdf/1004.4272)
- Random matrix theory. [std] For an N×T correlation matrix of pure noise, eigenvalues lie within the Marchenko-Pastur bounds λ± = (1 ± √q)², q = N/T. Eigenvalues inside that band are treated as noise, then replaced by their average (clipping) or shrunk. — [Laloux, Cizeau, Bouchaud, Potters 1999, PRL, doi:10.1103/PhysRevLett.83.1467](https://doi.org/10.1103/PhysRevLett.83.1467); López de Prado, *Machine Learning for Asset Managers* ch. 2 (book)
- DCC-GARCH. [std] Each asset follows a univariate GARCH(1,1), and the standardized residuals ε feed Q_t = (1 − a − b)Q̄ + a ε_{t−1}ε_{t−1}ᵀ + b Q_{t−1}, with R_t = diag(Q_t)^{−½} Q_t diag(Q_t)^{−½} and a + b < 1. — [Engle 2002, JBES, doi:10.1198/073500102288618487](https://doi.org/10.1198/073500102288618487)

**Tail dependence and copulas**
- [std] The upper tail-dependence coefficient is λ_U = lim_{u→1} P(U₂ > u | U₁ > u), and λ_L is defined analogously. The Gaussian copula has λ = 0 for ρ < 1, so it understates joint crashes. The Student-t copula has λ = 2·t_{ν+1}(−√((ν+1)(1−ρ)/(1+ρ))). The Clayton copula has λ_L = 2^(−1/θ) and λ_U = 0. — McNeil, Frey & Embrechts, *Quantitative Risk Management* (book, not fetched)
- [std] Equity correlations are asymmetric: they rise in down markets (Ang & Chen 2002), and exceedance correlation increases in bear markets rather than bull markets (Longin & Solnik 2001). — [Ang & Chen 2002, JFE](https://doi.org/10.1016/S0304-405X(02)00068-5); [Longin & Solnik 2001, JF](https://doi.org/10.1111/0022-1082.00340)

**Regime detection**
- [std] Hamilton (1989) Markov switching: r_t | s_t ~ N(μ_{s_t}, σ²_{s_t}), with s_t a K-state Markov chain with transition matrix P, estimated by EM/Hamilton filter. The filtered probability P(s_t = bear | info_t) is the usable real-time signal. Smoothed probabilities use future data and leak look-ahead. — [Hamilton 1989, Econometrica, doi:10.2307/1912559](https://doi.org/10.2307/1912559)
- [std] Trend filters: Faber's 10-month SMA rule (hold when price > 10-month SMA, else cash) reduced drawdowns across asset classes with similar returns. Time-series momentum (sign of the trailing 12-month return, vol-scaled) is documented across 58 futures. — [Faber 2007, SSRN 962461](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461); [Moskowitz, Ooi & Pedersen 2012, JFE](https://doi.org/10.1016/j.jfineco.2011.11.003)

**Drawdown control**
- CPPI: exposure E_t = m·(V_t − F_t), with multiplier m > 1 and floor F. The main failure mode is gap risk: a one-period drop larger than 1/m pushes value through the floor. [std] — [Black & Perold 1992, JEDC](https://doi.org/10.1016/0165-1889(92)90043-E)
- Grossman-Zhou (1993) impose the constraint W_t ≥ αM_t (M_t = running max, so the max drawdown is 1 − α). For CRRA, the optimal risky investment is proportional to the surplus W_t − αM_t, and the policy resembles CPPI with a ratcheting floor. — [Grossman & Zhou 1993, Math Finance](https://ideas.repec.org/a/bla/mathfi/v3y1993i3p241-276.html); [Cvitanić & Karatzas follow-up](https://www.cis.upenn.edu/~mkearns/finread/drawdown.pdf)
- [std, form not verified against full text] The usable rule is: dollar risky exposure = ((μ − r)/(γσ²)) · (W_t − αM_t). Equivalently, apply the Kelly/Merton fraction to the cushion above the drawdown floor rather than to total wealth. A related study says the Grossman-Zhou strategy is "not always optimal". — [Lund Univ.](https://www.lunduniversity.lu.se/lup/publication/37b108be-d2da-4ec8-a331-1b0c7cb46310)

**Volatility targeting**
- Moreira & Muir (2017): the managed factor is f^σ_t = (c/σ̂²_{t−1}) f_t, scaling by the inverse of last month's realized **variance**. It produced positive alphas and higher Sharpe in-sample. — [summary in Visser thesis](https://thesis.eur.nl/pub/49941/Visser_443480.pdf); [Moreira & Muir 2017, JF, doi:10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513)
- Cederburg, O'Doherty, Wang & Yan (JFE 2020) tested 103 strategies. Volatility-managed versions don't systematically beat unmanaged ones, and the spanning-regression alphas aren't implementable in real time. Implementable OOS versions earn lower Sharpe ratios and certainty equivalents, which the authors attribute to structural instability. — [JFE record](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117); [Alpha Architect](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/); [Lehigh WP](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
- DeMiguel, Martín-Utrera & Uppal (JF 2024) find a conditional multifactor vol-managed portfolio that beats its unconditional version OOS, net of costs. — [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:79:y:2024:i:6:p:3859-3891)
- [std] Man Group (Harvey et al. 2018) find vol targeting with a vol (not variance) scaler improves Sharpe and reduces left-tail events for equities and credit, but adds little for bonds, FX and commodities. The equity benefit comes from the leverage effect (vol rises when prices fall). — [Harvey et al. "The Impact of Volatility Targeting", SSRN 3175538](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175538)
- Standard implementation: w_t = min(L_max, σ_target/σ̂_t), with σ̂_t from EWMA.

**Transaction costs**
- Square-root impact: Δ(Q) = Y·σ_daily·√(Q/V), with V the daily volume and Y of order 1. The law has been confirmed for equities and options. Alternatives include a logarithmic form (Zarinelli et al.), and the mechanical-versus-information origin is still debated. — [Tóth et al. 2011, PRX](https://doaj.org/article/aa335a8de8954ff386b6bb094d176225); [Tóth, Eisler, Bouchaud 2016](https://arxiv.org/abs/1602.03043); [Maitrier et al. 2026, QF](https://econpapers.repec.org/RePEc:taf:quantf:v:26:y:2026:i:4:p:491-503)
- [std] Almgren-Chriss (2000): with linear temporary impact h(v) = ε·sgn(v) + ηv and permanent impact g(v) = γv, minimize E[cost] + λ·Var[cost]. The optimal holdings path is x(t) = X·sinh(κ(T − t))/sinh(κT), with κ ≈ √(λσ²/η). Low risk aversion gives linear (TWAP-like) execution. — [Almgren & Chriss 2000, J. Risk, doi:10.21314/JOR.2001.041](https://doi.org/10.21314/JOR.2001.041)
- Spread cost: ½ × quoted spread × |traded notional|, paid per trade. [std]

**Performance statistics**
- [std] Sharpe ratio: SR = mean(r − r_f)/sd(r − r_f), annualized with ×√252 for daily data (valid only if returns are IID). Lo (2002): with IID data, SE(ŜR) ≈ √((1 + ŜR²/2)/T) in per-period units. Autocorrelation biases the √q annualization. — [Lo 2002, FAJ, doi:10.2469/faj.v58.n4.2453](https://doi.org/10.2469/faj.v58.n4.2453)
- Deflated Sharpe ratio: it corrects for selection bias under multiple testing and for non-normality. Inputs are the candidate SR, number of trials, variance of the trial SRs, skew, kurtosis and sample length. — [Bailey & López de Prado 2014, SSRN 2460551](https://papers.ssrn.com/abstract=2460551); [quantstrat `SharpeRatio.deflated`](https://rdrr.io/github/braverock/quantstrat/man/SharpeRatio.deflated.html)
- [std] PSR(SR*) = Φ( (ŜR − SR*)·√(T − 1) / √(1 − γ̂₃ŜR + ((γ̂₄ − 1)/4)ŜR²) ), with non-annualized per-period SR, skew γ₃ and (non-excess) kurtosis γ₄. DSR = PSR evaluated at SR* = √V[{ŜR_n}] · ((1 − γ_e)Φ⁻¹(1 − 1/N) + γ_e·Φ⁻¹(1 − 1/(N·e))), with γ_e ≈ 0.5772 (Euler-Mascheroni) and N = number of independent trials. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- [std] PBO via combinatorially symmetric cross-validation (CSCV): split the T×N matrix of strategy returns into S blocks and form every half/half combination. Pick the in-sample best, find its out-of-sample relative rank ω̄, and compute the logit λ = ln(ω̄/(1 − ω̄)). PBO = fraction of combinations with λ ≤ 0. — [Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting", SSRN 2326253](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253); [CXO summary](https://www.cxoadvisory.com/big-ideas/backtest-overfitting-the-movies/)

### Inferences
- [calc] Estimation error kills full Kelly here. Annual vol of 30% for a mega-cap tech name and a 4-year sample give SE(μ̂) = 0.30/√4 = 15%/yr, as large as any plausible edge. The multi-asset Σ⁻¹μ with pairwise correlations around 0.5–0.7 amplifies those errors into extreme, unstable bets (Michaud's "error maximization").
- [calc, simple derivation] For a single asset with μ̂ ~ N(μ, σ²/T) and the plug-in f = c·μ̂/σ², expected excess growth is maximized at c* = S²/(S² + 1/T), with S the annual Sharpe and T in years. With S = 0.5: T = 1 gives c* = 0.20, T = 4 gives c* = 0.50, and T = 10 gives c* = 0.71. Half Kelly is therefore what the estimation error itself calls for with about 4 years of data, not only a matter of taste. This is consistent in direction with Kan & Zhou (2007).
- Inverse vol and ERC will be nearly identical for this book, because mega-cap tech correlations are fairly uniform. HRP adds most when there are distinct sub-clusters (e.g. semis vs. software/platforms vs. TSLA).
- Vol targeting on a concentrated equity book is the case where the Man Group evidence is most favourable (equity leverage effect). Cederburg et al. still argue against expecting alpha from inverse-variance timing. Its main value is risk control, not return enhancement.

### Gaps
- I could not retrieve the full texts of Grossman-Zhou, Gârleanu-Pedersen or the DSR paper to verify the exact closed forms marked [std]. Check them before coding.
- I found no source that directly benchmarks these methods on a 12–13-stock mega-cap tech universe.

## Q2. Which covariance/correlation estimators work best with ~13 assets and ~250–1000 days?

### Takeaway
With q = N/T ≈ 0.013–0.05, the sample matrix is well conditioned. The bigger problem is non-stationarity, not dimensionality. Use an EWMA (or blended EWMA + long-window) covariance, apply light Ledoit-Wolf constant-correlation shrinkage, and run min-var/Kelly through it with long-only constraints. Full DCC-GARCH and RMT clipping add little at this N.

### Cited Findings
- Shrinkage matters most when N is close to or exceeds T, where the sample matrix becomes singular. — [Ledoit-Wolf notes](https://reasonabledeviations.com/notes/papers/ledoit_wolf_covariance)
- The constant-correlation target keeps the sample variances and replaces each off-diagonal correlation with the average correlation. — [rdrr cov_estim_lwcc](https://rdrr.io/github/antshi/CovEstim/man/cov_estim_lwcc.html)
- How much better covariance estimators improve portfolios depends on N/T. — [arXiv 1004.4272](https://arxiv.org/pdf/1004.4272); [cross-validated estimators, arXiv 1910.13960](https://arxiv.org/pdf/1910.13960)
- Inverse vol is more robust than ML and optimizer approaches when covariance estimates are crude. — [IISc](https://eprints.iisc.ac.in/77367/1/ris_7-3_2019.pdf)
- A long-only constraint acts as implicit covariance shrinkage. — [Jagannathan & Ma 2003](https://doi.org/10.1111/1540-6261.00580)
- Correlations rise in down markets, so a full-sample average understates crash-time correlation. — [Longin & Solnik 2001](https://doi.org/10.1111/0022-1082.00340); [Ang & Chen 2002](https://doi.org/10.1016/S0304-405X(02)00068-5)
- DCC lets correlations vary over time. [std] — [Engle 2002](https://doi.org/10.1198/073500102288618487)

### Inferences
- [calc] Marchenko-Pastur noise band for N = 13: at T = 250, q = 0.052 and λ ∈ [0.60, 1.51]; at T = 1000, q = 0.013 and λ ∈ [0.79, 1.24]. In a tech correlation matrix the first eigenvalue (market/tech factor) will be roughly 6–8, far outside the band, with perhaps 1–2 sector eigenvalues above it and the rest inside. Clipping changes only those small eigenvalues. That matters for min-variance (which inverts them) but hardly at all for inverse vol or ERC.
- Recommended stack, in order of value:
  1. Volatilities from EWMA with a half-life of about 20–60 days. λ = 0.94 (11-day half-life) is noisy and causes turnover for a daily-rebalanced book.
  2. Correlations from a longer window (1–3 years, or EWMA with a half-life of about 120–250 days) and Ledoit-Wolf constant-correlation shrinkage. Expect a small δ at T ≥ 500.
  3. A stress overlay that raises correlations toward 0.8–0.9 for risk limits, given the downside correlation asymmetry.
- Mixing a short half-life for vols with a long half-life for correlations is common practitioner practice (e.g., RiskMetrics-style vs. Barra's separate half-lives). I found no fetched source quantifying it for this universe.
- DCC-GARCH is defensible but brittle. Fitting needs the R `rmgarch` package, Python `mgarch` or custom code (the `arch` package is univariate). Its gain over EWMA for daily rebalancing of 13 liquid names is likely small relative to model risk.

### Gaps
- I found no head-to-head OOS study of EWMA vs. LW vs. DCC at exactly N ≈ 13, T ≈ 250–1000 for equities. The recommendations above are inferences.

## Q3. How do top practitioners choose leverage / Kelly fraction and drawdown limits?

### Takeaway
Practitioners size from a volatility or risk budget and treat Kelly as an upper bound. In practice that means a half Kelly or smaller ceiling, often scaled on a drawdown-adjusted cushion (Grossman-Zhou/CPPI style), with the fraction chosen from an explicit tolerated probability of drawdown via x^(2/c − 1).

### Cited Findings
- Kelly's bets are very large because it implies very low risk aversion. Fractional Kelly is the standard fix and trades growth for smoothness. — [MacLean-Thorp-Ziemba](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)
- Thorp discusses applying fractional Kelly in practice and the drawdown probabilities above. — [Thorp 2006](https://www.Gwern.net/doc/statistics/decision/2006-thorp.pdf)
- Most practitioners use half Kelly or less because the parameters are unknown (secondary source). — [calculator page](https://ryanoconnellfinance.com/calculators/kelly-criterion-calculator/)
- Grossman-Zhou: a max-drawdown limit 1 − α implies risky exposure proportional to W − αM. — [Grossman & Zhou](https://ideas.repec.org/a/bla/mathfi/v3y1993i3p241-276.html)
- Vol targeting with a fixed target and a leverage cap is the industry implementation (Man Group). — [Harvey et al. 2018](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175538)

### Inferences
- [calc] Picking c from a drawdown tolerance: to keep P(ever −50%) ≤ 5%, solve 0.5^(2/c − 1) = 0.05, giving 2/c − 1 = 4.32 and c ≈ 0.38. To keep P(ever −30%) ≤ 10%, solve 0.7^(2/c − 1) = 0.10, giving 2/c − 1 = 6.46 and c ≈ 0.27. This assumes the true Sharpe is known, so with estimation error the fraction should be smaller still.
- [calc] Example: a basket with an honest OOS Sharpe of about 0.5 and 28% vol has a full Kelly (μ − r)/σ² ≈ 0.14/0.0784 ≈ 1.8× leverage. A quarter-to-half Kelly ceiling gives about 0.45–0.9× exposure. This supports "≤ 1× gross, with cash/T-bills as the remainder" for a long-only retail book, which matches the repo's recent SGOV idle-cash change.
- A practical drawdown rule from Grossman-Zhou: exposure_t = base_exposure × clip((W_t − αM_t)/((1 − α)M_t), 0, 1). With α = 0.8 (20% max-DD budget), exposure falls linearly to 0 as drawdown approaches 20%. Re-risking happens automatically as the cushion rebuilds, but M_t ratchets, so after a deep drawdown the strategy can stay under-invested (the CPPI "cash lock" failure).
- I found no fetched source with specific Kelly fractions used by named funds. Common practitioner lore puts vol targets around 10–15% for diversified CTAs and risk-parity funds, but that is unverified here.

### Gaps
- I found no primary source documenting specific funds' Kelly fractions or drawdown stop levels.

## Q4. What rebalancing band / no-trade region is optimal under proportional costs (Davis-Norman, Gârleanu-Pedersen)?

### Takeaway
Under proportional costs the optimal policy is a no-trade band around the target, with width proportional to (cost)^(1/3). When a weight leaves the band, trade only back to the band edge. Under quadratic/impact costs (Gârleanu-Pedersen), trade a fixed fraction of the way toward an "aim" portfolio each day. For mega-cap tech at retail size, costs are about 1–2 bp, so the bands are narrow but still cut turnover materially.

### Cited Findings
- Davis-Norman made the no-trade region rigorous as a free-boundary problem. Its width scales with the cube root of the proportional cost, and higher-order expansions exist. — [Gerhold, Muhle-Karbe, Schachermayer](https://ar5iv.labs.arxiv.org/html/1010.0627); [Choi 2013](https://www.arxiv.org/pdf/1309.3721)
- Rogers decomposes the utility loss into direct trading costs plus the cost of displacement from the frictionless optimum. Janeček-Shreve give first-order asymptotics. — [search summary of arXiv 1103.4934](https://www.arxiv.org/pdf/1103.4934); [Liu & Zheng](https://www.ma.ic.ac.uk/~hz/ime2015.pdf)
- [std] First-order half-width, single risky asset, CRRA γ, proportional cost ε: Δπ ≈ ( (3/(2γ)) · ε · π*²(1 − π*)² )^(1/3) around the Merton weight π*. — [Janeček & Shreve 2004, Finance & Stochastics, doi:10.1007/s00780-003-0118-4](https://doi.org/10.1007/s00780-003-0118-4)
- Gârleanu-Pedersen (JF 2013) set the optimal portfolio to "aim in front of the target and trade partially toward the current aim". The aim is a weighted average of current and expected future Markowitz portfolios, and slower-decaying signals get more weight. — [EconPapers JF 2013](https://econpapers.repec.org/RePEc:bla:jfinan:v:68:y:2013:i:6:p:2309-2340); [NYU archive](https://archive.nyu.edu/handle/2451/28346)
- [std, from paper, not re-read] Their rule is x_t = (1 − a/λ)x_{t−1} + (a/λ)·aim_t, with quadratic cost ½Δxᵀ(λΣ)Δx and a = [−(γ(1 − ρ) + λρ) + √((γ(1 − ρ) + λρ)² + 4γλ(1 − ρ)²)] / (2(1 − ρ)), where ρ is the discount rate and γ risk aversion. — [GP 2013](https://econpapers.repec.org/RePEc:bla:jfinan:v:68:y:2013:i:6:p:2309-2340)
- Impact under the square-root law is Y·σ·√(Q/V). — [Tóth et al.](https://doaj.org/article/aa335a8de8954ff386b6bb094d176225)

### Inferences
- [calc] Davis-Norman half-width for one name at a target of about 8% weight (1/12.5), γ = 2 and ε = 5 bp gives (0.75 × 0.0005 × 0.0064 × 0.846)^(1/3) ≈ (2.0e-6)^(1/3) ≈ 1.3 percentage points. So hold anywhere in roughly 6.7–9.3% and trade only to the edge. At ε = 1 bp the band is about ±0.75 pp. This is a single-asset approximation. Multi-asset regions are not rectangles, but per-name bands are the standard practical proxy.
- [calc] Impact is negligible at retail scale. A $10k AAPL order against ~$10B ADV gives Q/V ≈ 1e-6, √ ≈ 1e-3, and with σ_daily ≈ 1.5% the impact is about 0.15 bp × Y. The cost is dominated by half-spread (about 0.5–1 bp on mega-caps) plus any commission or PFOF slippage. So the Almgren-Chriss scheduling and Gârleanu-Pedersen quadratic machinery mostly don't bind. Their practical lesson that survives is partial adjustment toward the target for noisy, fast-decaying signals, e.g., trading 20–50% of the gap per day to avoid churning on signal noise.
- Daily rebalancing without bands creates turnover from EWMA vol noise alone. Bands (or a lower-turnover vol estimator) are the cheapest fix.
- Retail feasibility: all the methods above run on free daily close data (yfinance/Stooq) with numpy, PyPortfolioOpt (LW constant-correlation, HRPOpt, min-var) or riskfolio-lib (ERC/HRP/HERC). DCC needs R or extra Python packages. Intraday impact models can't be calibrated without tick data, but they don't matter at this size.

### Gaps
- I could not read the closed-form trade rate from the Gârleanu-Pedersen paper's text this session, so the formula above should be checked against eq. (13)–(15) of the JF article.
- I found no empirical study of optimal band widths specifically for daily-rebalanced mega-cap equity books.
