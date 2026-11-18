# Skeptic / Replication View of Return Predictors and Portfolio Construction for a Concentrated US Mega-Cap Tech Basket

## Q1. How often do published predictors fail out-of-sample, how much do they decay after publication, and what statistical hurdles are right?

### Takeaway
Most published anomalies are real in-sample (they reproduce), but they are much weaker than reported. The average predictor loses about a quarter of its return out-of-sample and more than half after publication. Most do not clear a multiple-testing-adjusted hurdle (t > 3) once microcaps are de-emphasised. Large-cap, after-cost survival is a minority outcome, mostly limited to low-turnover themes such as value, profitability and momentum. A home-grown backtest on 8-15 correlated stocks should be treated as presumptively overfit until it passes a deflated-Sharpe / PBO test.

### Cited Findings
- **McLean and Pontiff (JF 2016), 97 predictors:** portfolio returns are 26% lower out-of-sample and 58% lower post-publication. The 26% is read as an upper bound on statistical bias. That leaves roughly 32 percentage points attributable to investors trading on the publication. — [CXO Advisory / abstract copies](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation); [CFA Digest summary](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary); [JF DOI listing](https://law-journals-books.vlex.com/vid/does-academic-research-destroy-855658380)
  - A Fortune write-up of an earlier working-paper version reported about 35% post-publication decay. Cite the published 26%/58% figures. — [Fortune](https://fortune.com/2012/11/02/academics-academia-destroys-stock-picking-strategies/)
- **Harvey, Liu and Zhu (RFS 2016):** they catalogue about 316 factors and argue that, given this extensive data mining, a new factor needs a t-ratio above 3.0 rather than 2.0. — [NBER w20592](https://nber.org/papers/w20592); [CXO summary](https://www.cxoadvisory.com/big-ideas/taming-the-factor-zoo/)
- **Hou, Xue and Zhang, "Replicating Anomalies" (RFS):** they test 447 anomalies with NYSE breakpoints and value weighting to limit microcaps. 286 (64%) are insignificant at 5%, and 380 (85%) are insignificant at the t > 3 hurdle. Even among the survivors, magnitudes are often much smaller than originally reported. Microcaps are about 3% of market cap but about 60% of stocks, and the authors call microcap anomalies "more apparent than real" because of trading costs. — [NBER conference paper](https://conference.nber.org/conf_papers/f102921/f102921.pdf); [Alpha Architect](https://alphaarchitect.com/replicating-anomalies/)
- **Jensen, Kelly and Pedersen, "Is There a Replication Crisis in Finance?" (JF 2023, 78(5)):** a Bayesian analysis of 153 factors in 93 countries. Most factors replicate, survive joint modelling, and hold up out-of-sample. They cluster into 13 themes, most of which matter for the tangency portfolio. The replication rate exceeds 75% in 10 of the 13 themes. The exceptions are Seasonality, Leverage and Size. They rebut HXZ's roughly 35% replication rate. — [NBER w28432](https://nber.org/system/files/working_papers/w28432/w28432.pdf); [Alpha Architect](https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/); [CBS](https://research.cbs.dk/en/publications/is-there-a-replication-crisis-in-finance/)
- **Chen and Zimmermann:** nearly 100% of published predictability results can be reproduced with an open-source dataset. Publication-bias-adjusted returns are only about 13% smaller than in-sample returns, and the average shrinkage across three meta-studies is about 10%. Returns are 30-50% weaker in alternative portfolio tests. Publication bias is too small to explain post-publication decay. — [Open Source Cross-Sectional Asset Pricing](https://cfr.ivo-welch.info/published/papers/chen2021open.pdf); [Publication Bias in Asset Pricing Research (arXiv 2209.13623)](https://www.arxiv.org/pdf/2209.13623); [AEA 2018](https://aeaweb.org/conference/2018/preliminary/paper/ZKzBYziN)
- **Novy-Marx and Velikov (RFS 2016), trading costs:** most anomalies with turnover below 50% a month still earn significant net spreads when built to reduce costs; few higher-turnover anomalies do. A buy/hold spread (a stricter bar to enter a position than to keep it) is the single most effective simple cost mitigation. Costs always reduce profits, which raises data-snooping concerns. Size, value and profitability have the most capacity. — [NBER w20721](https://www.nber.org/papers/w20721); [Alpha Architect](https://alphaarchitect.com/2017/05/trading-costs-destroy-factor-investing/)
- **Bailey and López de Prado, overfitting statistics:**
  - The Deflated Sharpe Ratio corrects the Sharpe ratio for selection bias under multiple testing and for non-normal returns. It builds on the Probabilistic Sharpe Ratio. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
  - The Probability of Backtest Overfitting (PBO) is the probability that the in-sample-optimal configuration ranks below the median out-of-sample. — [Bailey et al. (PBO)](https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf)
  - Minimum Backtest Length example: trying more than 45 strategy configurations on 5 years of data almost guarantees finding one with an in-sample Sharpe of 1 but an expected out-of-sample Sharpe of 0. — [CXO summary](https://www.cxoadvisory.com/?p=23736); [Bailey, Borwein, López de Prado, Zhu](https://carmamaths.org/jon/BODT.pdf)
  - These derivations assume tame return distributions. — [CXO](https://www.cxoadvisory.com/?p=23736)

### Inferences
- The two camps disagree mostly about framing, not facts. JKP and Chen-Zimmermann show that predictors *reproduce*. McLean-Pontiff and HXZ show that their *magnitude* shrinks sharply out-of-sample, post-publication, and in value-weighted / large-cap / after-cost tests. For a mega-cap basket, the relevant expectation is the decayed, cost-adjusted number. As a rule of thumb, haircut any in-sample premium by at least 50% (McLean-Pontiff's 58% post-publication decay).
- Practical hurdles for this project:
  1. Require t > 3 (HLZ) for any signal found by search.
  2. Report the deflated Sharpe using the number of variants actually tried.
  3. Compute PBO with combinatorially symmetric cross-validation.
  4. Prefer low-turnover signals.
  5. Use a buy/hold band rather than raw daily rebalancing (Novy-Marx-Velikov).
- Cross-sectional anomalies with 8-15 stocks have little statistical power: long-short deciles are impossible and the breadth is tiny. So "factor" tilts inside the basket are mostly noise-dominated. This is my inference; I did not find a source that tests anomalies within a 10-stock mega-cap universe.

### Gaps
- I found no source giving the exact share of anomalies that survive *in large caps after costs*. HXZ (value-weighted, about 36% significant at 5%, about 15% at t > 3) and Novy-Marx-Velikov (the low-turnover subset) are the closest proxies.
- I could not retrieve the exact Minimum Backtest Length formula or the McLean-Pontiff large-versus-small-stock breakdown from full text (the PDF fetch failed).

## Q2. Which portfolio-construction choices reliably improve risk-adjusted returns for a small, highly correlated, long-only basket (8-15 tech mega-caps)?

### Takeaway
Estimation error dominates in small universes. 1/N or simple inverse-volatility weighting is a tough benchmark that optimised weights rarely beat out-of-sample. HRP and minimum-variance can trim volatility, but the evidence that they improve Sharpe is mixed and author-dependent. Volatility targeting (Moreira-Muir) does not reliably beat buy-and-hold out-of-sample once real-time implementation is enforced (Cederburg et al.). 200-day moving-average timing is substantially overstated after costs in independent tests. When names are highly correlated, the reliable risk lever is total exposure (the cash/T-bill fraction and diversifying assets), not the weights within the basket.

### Cited Findings
- **DeMiguel, Garlappi and Uppal (RFS 2009, 22(5)):**
  - None of 14 optimising models consistently beats 1/N on Sharpe, certainty-equivalent return or turnover across 7 datasets. — [RePEc](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html); [NBER SI draft](https://conference.nber.org/confer/2006/si2006/ap/uppal.pdf)
  - Sample mean-variance needs an estimation window of more than about 3,000 months to beat 1/N with 25 assets, and about 6,000 months with 50 assets. Practitioners typically use 120 months. — [NBER SI draft](https://conference.nber.org/confer/2006/si2006/ap/uppal.pdf)
  - A later JFQA paper on how to beat 1/N also treats the 3,000-month requirement as a serious concern. — [JFQA "Why naive 1/N diversification is not so naive"](https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/4969319F5B1F3E350FB7FC8A73BA9F65/S0022109023001175a.pdf/why-naive-dollar-1n-dollar-diversification-is-not-so-naive-and-how-to-beat-it.pdf)
- **HRP versus alternatives (mixed evidence):**
  - A CBS thesis found HRP had the lowest out-of-sample variance in Monte Carlo simulations, but it was less robust to a misspecified covariance matrix. In walk-forward tests it beat inverse-variance and equal weight on risk measures but lagged minimum-variance. — [CBS thesis](https://research-api.cbs.dk/ws/portalfiles/portal/76452070/1332322_Master_Thesis_Hierarchical_Risk_Parity.pdf)
  - On Brazilian equities, HRP was generally not the best out-of-sample. — [RBFin](https://periodicos.fgv.br/rbfin/article/download/89848/84802/201368)
  - The strongest pro-HRP results come from its originator or from blog-style tests. — [gmarti replication](https://gmarti.gitlab.io/qfin/2018/10/15/hierarchical-risk-parity-part-2.html)
  - Practitioner note: equal weight needs no forecasts, inverse-volatility needs only volatility forecasts, and minimum-variance and risk parity also need correlations. — [CXO / Hallerbach](https://www.cxoadvisory.com/strategic-allocation/practitioners-perspective-on-portfolio-risk-management-research/)
- **Moreira and Muir (JF 2017, 72(4)):** scaling factor exposure by inverse recent variance produces large alphas and higher Sharpe ratios. The working paper reports lifetime-utility gains of about 50-90% for a mean-variance investor. — [NBER w22208](https://www.nber.org/papers/w22208); [published PDF](https://amoreira2.github.io/alan-moreira.github.io/VolPortfolios_published.pdf)
- **Cederburg, O'Doherty, Wang and Yan (JFE 2020):**
  - Across 103 strategies, the volatility-managed version wins 53 and loses 50. Only 8 of the 53 wins are significant.
  - Real-time mean-variance implementations that include the volatility-managed option give *lower* Sharpe ratios for 72 of 103 strategies.
  - The authors attribute the failure to structural instability in the spanning regressions. Their results are gross of costs.
  - [Paper PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf); [Alpha Architect](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/); [CXO](https://www.cxoadvisory.com/volatility-effects/does-volatility-management-work-for-equity-factor-portfolios/)
  - Barroso and Detzel (2021) reportedly find no positive after-cost alphas. This is second-hand only. — [EUR thesis](https://thesis.eur.nl/pub/49941/Visser_443480.pdf)
- **200-day moving-average / Faber timing:**
  - Zakamulin's out-of-sample tests with realistic transaction costs conclude that the performance of moving-average and time-series-momentum timing is "highly overstated". He finds no significant outperformance in the second half of a 155-year sample. He attributes the deterioration to instability in the optimal moving-average length. — [Zakamulin, core.ac.uk](https://core.ac.uk/download/225890416.pdf); [SSRN 2677212](https://papers.ssrn.com/abstract=2677212)
  - Faber's own update reports the Sharpe ratio improving from 0.45 to 0.80, but he is not an independent tester. — [CFA Enterprising Investor](https://rpc.cfainstitute.org/blogs/enterprising-investor/2016/dumb-alpha-tactical-errors/)
  - A practitioner extension (2006-2025) finds about 220bp of CAGR difference between the best and worst monthly rebalance days ("timing luck") and whipsaw from frequent signal flips. This is an unverified blog. — [Concretum Substack](https://concretumgroup.substack.com/p/global-tactical-asset-allocation)

### Inferences
- **For a 10-name basket of correlated tech stocks:**
  - Use equal weight or inverse-volatility as the default.
  - Treat minimum-variance and HRP as risk-reduction tools that must beat 1/N in walk-forward tests.
  - Never use mean-variance with estimated means. With N of about 10 and only a few years of data, DGU-style estimation error is severe.
- When pairwise correlations are high, all risk-based schemes converge toward similar weights. That limits how much any weighting scheme can add.
- **Volatility targeting:**
  - Its realistic benefit is drawdown and risk control, not reliably higher Sharpe.
  - Daily rebalancing adds turnover that the Cederburg et al. results (gross of costs) do not even account for.
  - Use a deadband or buy/hold band (per Novy-Marx-Velikov) and slow-moving volatility estimates.
- **200-day moving-average filters:** evaluate them with the PBO / deflated-Sharpe hurdle from Q1. Their documented benefit is mainly avoiding deep drawdowns (for example 2022), at the cost of whipsaw and lower returns in V-shaped recoveries.
- **Fractional Kelly:** I found no source in this session. On theory alone (not cited here), half-Kelly or less is standard because estimated edges are biased upward. McLean-Pontiff's decay makes full Kelly on backtested means dangerous.

### Gaps
- I did not retrieve sources on fractional Kelly (for example MacLean, Thorp and Ziemba) because of tool-call limits. The claim above is uncited and the report writer should flag it.
- I found no peer-reviewed comparison of weighting schemes specifically for 8-15 highly correlated large-cap tech stocks.
- I found no independent 2020s out-of-sample study of 200-day moving-average timing on single tech stocks.

## Q3. Diversification: Treasuries, gold, trend-following / managed futures, T-bills; the stock-bond correlation regime since 2022

### Takeaway
Since 2022 the stock-bond correlation has been positive. That weakens Treasuries as an equity hedge, but AQR argues positive correlation is the historical norm, not a new crisis. Trend-following delivered strong crisis alpha in 2022 (+27%) but then suffered its second-worst drawdown on record (about -20%, May 2024 to May 2025), which shows it is a diversifier with long dry spells. Holding idle cash in T-bills is a no-cost improvement whenever a filter or volatility target leaves the basket under-invested.

### Cited Findings
- **AQR (Asness, Villalon, Ilmanen, 2026):** a positive stock-bond correlation "has been the historical norm". Since 2022, bond volatility has risen to 6.68% (versus 5.51% historically) and stock volatility has fallen to 16.73% (versus 18.35%). 60/40 portfolio volatility is 10.95%, versus 11.13% historically. AQR argues that a positive correlation is a terrible reason to add more equity risk. — [AQR](https://www.aqr.com/insights/perspectives/a-positive-stock-bond-correlation-is-a-terrible-reason-to-add-more-equity-risk-to-your-portfolio); [Alpha Architect summary](https://alphaarchitect.com/bonds-seem-to-not-diversify-anymore-now-what/)
- **Man Group:** the stock-bond correlation historically turns positive when US inflation runs above about 2.5%, so bonds cannot be relied on as a diversifier in those periods. Man favours equity-market-neutral strategies and trend as more durable diversifiers. — [Man, "Bonds bust equities"](https://www.man.com/insights/bonds-bust-equities); [Man, diversification](https://www.man.com/it/exclusive/diversify-approach-diversification)
- **SSGA:** the 36-month stock-bond correlation eased from a peak of 0.66 (December 2024) to 0.48 (September 2025). — [SSGA, October 2025](https://www.ssga.com/us/en/individual/insights/mind-on-the-market-03-october-2025)
- **PGIM:** in the positive-correlation era of 1965-2000, correlations of about +0.25 still left room for diversification. — [PGIM](https://www.pgim.com:443/research/negative-correlation-dead-long-live-6040-portfolio)
- **Trend-following (SG Trend Index):**
  - +27.4% in 2022, when MSCI ACWI fell 18.4% and US aggregate bonds fell about 13%. — [Cambridge Associates](https://www.cambridgeassociates.com/?p=48375); [AdvisorAnalyst](https://advisoranalyst.com/?p=167192)
  - Drew down 20.4% from May 2024 to May 2025, its second-largest drawdown since 2000. AlphaSimplex reports -18.7% for the 12 months to April 2025, the worst in the index's history. — [Cambridge Associates](https://www.cambridgeassociates.com/?p=48375); [AdvisorAnalyst](https://advisoranalyst.com/?p=167192)
  - Man frames 2022 as evidence that trend's crisis alpha does not depend on long-bond positions. — [Man](https://www.man.com/insights/why-patience-matters-during-market-stress)

### Inferences
- For a long-only retail account, the realistic diversifiers are ETFs: T-bills (SGOV/BIL), intermediate Treasuries, gold, and managed-futures ETFs.
- Given the positive stock-bond correlation, Treasuries should not be assumed to hedge a tech-equity drawdown in an inflationary shock (as in 2022). They are more likely to help in deflationary or growth-scare shocks.
- Earning T-bill yield on idle cash costs nothing and should be the default in any backtest that de-risks. A backtest that leaves cash at 0% understates de-risked returns. Conversely, a backtest from 2010-2021 that assumes about 0% cash rates is not representative of 2023-2026.

### Gaps
- I found no authoritative calendar-2025 return for the SG Trend Index.
- I did not retrieve 2022-2026 gold correlation data from a primary source.

## Q4. Concentration risk in AI / semiconductor names, 2024-2026; crash co-movement and what mitigates it

### Takeaway
US equity concentration is at record levels in 2026. A long-only tech mega-cap basket is effectively a single AI-capex factor bet whose names fall together in shocks (DeepSeek, January 2025; 2022). Within-basket weighting cannot diversify that. Only exposure sizing, cash or T-bills, and non-equity diversifiers can.

### Cited Findings
- **Concentration in 2026:**
  - NVIDIA, Apple and Microsoft together exceeded 21% of the S&P 500 in October 2026, the most ever for three stocks. The previous top-three record was about 13.4%, set in the mid-1980s. — [247wallst, October 2026](https://247wallst.com/investing/2026/10/07/three-stocks-are-now-21-of-the-sp-500-the-most-ever); [Benzinga / Creative Planning](https://www.benzinga.com/node/62200101)
  - Individual weights cited: NVDA about 8%, AAPL about 7%, MSFT about 5.7%. A January 2026 claim that NVDA weighed about 12.7% conflicts with this and is likely wrong. — [KuCoin flash (low quality)](https://www.kucoin.com/news/flash/nvidia-and-apple-hit-15-of-s-p-500-surpassing-1999-dot-com-peak)
  - IT sector weight of about 39%, above the March 2000 record of about 35%. This comes from secondary sources and should be verified with S&P DJI. — [Cryptobriefing](https://cryptobriefing.com/tech-stocks-surpass-50-percent-sp500/)
- **DeepSeek shock (27 January 2025):** the S&P 500 fell 1.5% and the Nasdaq 100 fell 3%. The Magnificent 7 were about one-third of the S&P 500 and about 45% of the Nasdaq 100. A strategist cited "correlated and crowded positioning in the AI theme". — [Reuters via The Star](https://www.thestar.com.my/tech/tech-news/2025/01/28/analysis-us-tech-stock-tumble-highlights-risk-of-market-reliance-on-megacaps--)
- **2022 drawdown:** the Magnificent 7 fell about 45% as a group, versus about 20% for the cap-weighted S&P 500 and about 13% for the equal-weighted S&P 500. An HDFC analysis puts AI names at about 58% of S&P 500 risk. Both figures are from a secondary site; treat them with caution. — [Cryptobriefing](https://cryptobriefing.com/sp500-ai-companies-58-percent-index-risk/)
- **Dispersion is possible:** the correlation between the Magnificent 7 and the equal-weighted S&P 500 turned negative in February 2025 (BofA's Hartnett), and the group's leadership reshuffled after DeepSeek. — [Tiger / BofA](https://www.itiger.com/news/1170135134); [Bloomberg Línea](https://www.bloomberglinea.com/mercados/a-seis-meses-del-shock-de-deepseek-asi-se-reacomodaron-las-7-magnificas/?outputType=amp)

### Inferences
- Correlations rise in sell-offs (tail dependence). As a result, the volatility-based weights in Q2 understate crash risk.
- Mitigations, roughly in order of reliability:
  1. Cap gross equity exposure, or set a portfolio-level volatility or drawdown budget.
  2. Hold the remainder in T-bills.
  3. Add assets with low crisis co-movement, such as trend/managed futures, gold and, in deflationary shocks, Treasuries.
  4. Apply per-name and per-sub-theme caps, for example limiting total semiconductor weight (NVDA, AVGO, AMD, TSM).
  5. Evaluate with stress tests on 2022 and January 2025 rather than full-sample covariance.
- A 2024-2026 backtest of an AI basket is dominated by a single regime (the AI capex boom). Its Sharpe ratio is very likely inflated relative to forward expectations. This links directly to the McLean-Pontiff and deflated-Sharpe haircuts in Q1.

### Gaps
- I found no peer-reviewed 2024-2026 measure of tail dependence (copula or downside correlation) among AI and semiconductor names.
- Concentration percentages differ by source and date. Verify them against S&P DJI or fund-holdings data.
- I found no primary data on how US mega-cap tech correlations behaved during the 2025 tariff sell-off. It was not searched because of the tool-call limit.
