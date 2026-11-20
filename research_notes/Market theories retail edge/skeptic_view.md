# Skeptic / Replication View: Why Most Claimed Market Edges Fail, and What Survives

Format: simulated multi-turn expert interview. Each thread is a series of Q (interviewer) and A (sourced answer), with each follow-up sharper than the last. Every figure carries an inline source. Figures I could not verify are in Gaps.

---

## Thread 1: Data mining and p-hacking. How much of the published "edge" is real?

### Takeaway
Under multiple testing, the usual t > 2 significance bar is far too low (Harvey-Liu-Zhu argue for t > 3). Backtests with more than a few dozen tried variants are probably overfit (Bailey/López de Prado). Published anomaly returns fall about 26% out-of-sample and about 58% after publication (McLean-Pontiff). After realistic trading costs, the average anomaly nets only about 4 bps/month (Chen-Velikov). The counterpoint (Jensen-Kelly-Pedersen) is that most factors do replicate as statistical effects. "Real" is not the same as "tradeable at a profit by you after costs".

### Interview

**Round 1. Q: How large is the "factor zoo", and what significance bar should a new finding clear?**
- Harvey, Liu and Zhu build a multiple-testing framework that allows for correlated tests and missing data. They conclude that a newly discovered factor needs a t-ratio above 3.0, not the conventional 2.0, and that "most claimed research findings in financial economics are likely false" — [NBER w20592](https://nber.org/papers/w20592); published RFS 2016, 29(1):5-68 — [RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.)
- Their dataset contains about 316 factors, as cited by a Federal Reserve paper — [FEDS 2019-016](https://www.federalreserve.gov/econres/feds/files/2019016pap.pdf). Other papers cite 314, so the count depends on the version.
- The framework produces a time series of significance cutoffs from 1967 onward. The bar rises as more factors get tested — [NBER w20592](https://nber.org/papers/w20592)

**Round 2. Q (sharper): That covers academics. What about an individual who backtests 200 parameter variants on their own laptop?**
- Bailey, Borwein, López de Prado and Zhu (Notices of the AMS, 2014): "the higher the number of configurations tried, the greater is the probability that the backtest is overfit." With only 5 years of daily data, trying as few as 45 configurations can mislead you. At least one will show a good in-sample Sharpe and a poor out-of-sample Sharpe — [EurekAlert AMS release](https://www.eurekalert.org/news-releases/817304); [paper record](https://scholarworks.wmich.edu/math_pubs/40/); [Bailey & López de Prado slides 2022](https://cdar.berkeley.edu/sites/default/files/dhb-risk-2022.pdf)
- "Financial analysts rarely report the number of configurations tried," so investors cannot judge how overfit a backtest is — [paper record](https://scholarworks.wmich.edu/math_pubs/40/)
- The Probability of Backtest Overfitting (PBO) is estimated with combinatorially symmetric cross-validation (CSCV). It is the probability that the in-sample-best configuration ranks below the median out-of-sample — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253); definition as summarized in [UW course paper](https://sites.math.washington.edu/~morrow/336_18/papers17/akshay.pdf)
- The Deflated Sharpe Ratio (Bailey & López de Prado, JPM 2014) corrects the observed Sharpe for selection bias under multiple testing and for non-normal returns (skew and kurtosis). It builds on the Probabilistic Sharpe Ratio — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)

**Round 3. Q (sharper): Suppose an anomaly is genuinely real in-sample. How much of it survives once it is public?**
- McLean & Pontiff (JF 2016, 71(1):5-32) study 97 published predictors. Returns are 26% lower out-of-sample but before publication, and 58% lower after publication. They treat the 26% as an upper bound on data mining and attribute the remaining ~32% (58 − 26) to publication-informed trading, i.e. arbitrage — [search summary of paper](https://econpapers.repec.org/RePEc:bla:jfinan:v:71:y:2016:i:1:p:5-32); [CFA digest](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary)
  - Note: the brief's "~32% post-publication decay" is the publication-specific component. The total post-publication decline is 58%.

**Round 4. Q (sharper): Add trading costs on top of decay. What is left for the average anomaly?**
- Chen & Velikov (JFQA 2023, 58(3):968-1004): the average anomaly earns 68 bps/month gross in-sample, which falls to 44 bps after cost mitigation. After both trading costs and post-publication decay, the average anomaly's expected return is "a measly 4 bps per month". The strongest net at best about 10 bps after controlling for data mining, and combining anomalies gets to about 20 bps. Costs use effective spreads from ISSM/TAQ high-frequency data — [Cambridge/JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225). The 2020 working paper reported 8 bps — [FEDS 2020-039](https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf)

**Round 5. Q (counterpoint): Isn't finance in a "replication crisis", then?**
- Jensen, Kelly & Pedersen (JF 2023, 78(5):2465-2518) use a global dataset of 153 factors across 93 countries. They find "the majority of factors do replicate, do survive joint modeling of all factors, do hold up out-of-sample", although "a non-trivial minority" fail. Under their Bayesian approach the replication rate is about 82%, versus the 35% reported by Hou-Xue-Zhang (2020) — [NBER w28432](https://www.nber.org/papers/w28432); [Alpha Architect summary](https://alphaarchitect.com/factors-are-global-respectable-and-repeatable/)
- Separately, Andrew Chen estimates that at least 82% of claimed findings on value-weighted CAPM alphas are true. This is a different 82% and should not be conflated with the JKP figure — [Chen paper](https://www.anderson.ucla.edu/sites/default/files/document/2024-05/5.24.24%20Paper%20Andrew%20Checn%20Fed%20Reserve%20Board.pdf)

### Inferences
- The two camps can be reconciled. JKP show that factor signs and significance replicate. McLean-Pontiff and Chen-Velikov show that the magnitude available to a new trader is small after decay and costs. "It replicates" does not mean "I can harvest it net".
- For a retail quant, the practical bar is: count every variant tried, deflate the Sharpe accordingly, and expect at least ~half of the backtested edge to vanish live before costs. This fits this repo's own record: several pre-registered Kalshi/Polymarket rules failed out-of-sample, per recent commits.

### Gaps
- I did not extract the exact Deflated Sharpe Ratio formula or the MinBTL closed form from the primary papers; only the abstracts and press summaries were read.
- I did not verify a precise PBO estimate for typical retail strategies. No such population estimate was found.

---

## Thread 2: Costs and implementation shortfall that kill paper edges for retail

### Takeaway
Turnover is the main killer. Active retail traders lag by about 5-7 pp/yr. Anomalies with more than about 50% monthly turnover rarely survive costs. Over 97% of persistent day traders lose money. Fund investors lose another ~1.1-1.2 pp/yr to bad timing (behavioral abandonment). Taxes on short-term gains add a further, separate drag.

### Interview

**Round 1. Q: What does high trading actually cost real retail accounts?**
- Barber & Odean (JF 2000), covering 66,465 households (described as "over 60,000") from 1991-96. Average turnover was over 80%/yr. The average household's gross return of 17.7% roughly matched the market's 17.1%, but net of costs it fell to 15.3%. The most active 20% (≥9.6% monthly turnover) netted 10.0% vs the market's 17.1%, roughly −7 pp/yr — [Barber & Odean abstract](https://faculty.haas.berkeley.edu/odean/papers/returns/Returns.html)
- Critique: Bonaparte & Cooper argue that how "hazardous" trading actually is remains open. An SEC comment letter notes the ~78,000-account sample from one broker is not representative — [NBER w16022](https://www.nber.org/papers/w16022.pdf); [SEC comment](https://sec.gov/comments/s7-12-23/s71223-281699-688282.pdf)

**Round 2. Q (sharper): Are there any skilled day traders? Maybe the average hides a profitable tail.**
- Taiwan, 1992-2006, using complete transaction data: fewer than 1% of day traders predictably earn positive abnormal returns net of fees. The top-500 prior-year traders earn 61.3 bps/day before fees and 37.9 bps after. The bottom-ranked earn −11.5 bps before fees and −28.9 bps after — [Barber, Lee, Liu, Odean, J. Financial Markets 2014](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html); [working paper](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf). A companion version estimates that 97% of day traders can expect to lose money — [same PDF set](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/day%20trading%20and%20learning%20110217.pdf)
- Brazil equity futures, 2013-15 entrants: of those who persisted 300+ days, 97% lost money, only 1.1% earned more than the minimum wage, and only about 0.4-0.5% earned more than a bank teller's starting salary (~US$54/day). There was no evidence of learning — [Chague, De-Losso, Giovannetti, IDEAS](https://ideas.repec.org/p/spa/wpaper/2019wpecon47.html)

**Round 3. Q (sharper): For a systematic, not discretionary, retail strategy, what turnover is survivable?**
- Novy-Marx & Velikov (RFS 2016, 29(1):104-147): most anomalies with one-sided monthly turnover below 50% keep significant net spreads when designed to mitigate costs, while "few with higher turnover do". The most effective mitigation is a buy/hold spread, with stricter rules to enter a position than to keep it — [NBER w20721](https://www.nber.org/papers/w20721)
- Combined with Chen-Velikov (Thread 1): even mitigated, the average anomaly nets about 4 bps/month after decay — [JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225)

**Round 4. Q (sharper): Taxes and wash sales. How do they hit a taxable retail trader specifically?**
- In the US, short-term gains (holding ≤1 year) are taxed at ordinary income rates of up to 37%. Long-term gains are taxed at 0/15/20% — [IRS Topic 409](https://www.irs.gov/taxtopics/tc409) (not fetched this session; standard IRS reference)
- The wash-sale rule disallows a loss if a substantially identical security is bought within 30 days before or after the sale — [IRS Pub 550](https://www.irs.gov/publications/p550) (not fetched this session)
- Quantified wash-sale bite: in a simulation of monthly harvesting, tax alpha falls from 1.10%/yr to 0.85%/yr (working paper), or from 1.08% to 0.82% (published FAJ 2020) — [Chaudhuri, Burnham, Lo, MIT DSpace](https://dspace.mit.edu/bitstream/handle/1721.1/135992/SSRN-id3351382.pdf); [CFA](https://rpc.cfainstitute.org/research/financial-analysts-journal/2020/empirical-evaluation-tax-loss-harvesting-alpha)
- After-tax active fund results are worse than pre-tax. S&P publishes a separate after-tax SPIVA scorecard — [SPIVA After-Tax YE2024](https://www.spglobal.com/spdji/en/documents/spiva/spiva-after-tax-scorecard-year-end-2024.pdf) (I did not extract figures)

**Round 5. Q (sharper): Behavioral abandonment. Even if the strategy works, do people capture it?**
- Morningstar Mind the Gap 2024, covering the 10 years to end-2023: the dollar-weighted investor return was 6.3%/yr vs 7.3% for the funds, a gap of about 1.1 pp. That is roughly 15% of total return. Investors lagged in every one of the 10 calendar years — [Mind the Gap 2024 PDF](https://marketing.morningstar.com/content/cs-assets/v3/assets/blt9415ea4cc4157833/blt5d1d34a59bd78a2c/680a4bd8c4d2e877fdb4b354/Mind_the_Gap_2024.pdf); [Fortune](https://dc.fortune.com/2024/08/21/investors-pulled-nearly-0-5-trillion-in-2020s-market-turbulence-then-missed-the-rally)
- The next edition (10 years to end-2024) showed 7.0% vs 8.2%, a gap of about 1.2 pp — [Morningstar AU](https://morningstar.com.au/insights/special-reports/253580/why-investors-missed-out-on-15-of-total-fund-returns). Morningstar also reports that "the more investors traded, the worse they performed" — [Morningstar](https://global.morningstar.com/en-gb/personal-finance/more-investors-traded-worse-they-performed)
- AQR lists as a "fiction" the belief that you know when you are in a drawdown or recovery and when to cut or add risk — [AQR Fact, Fiction, and Factor Investing 2023](https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/AQRJPMQuant23FactFictionandFactorInvesting.pdf)

### Inferences
- The shortfall stack for a taxable, high-turnover retail strategy is roughly: about 5-7 pp/yr cost drag (Barber-Odean top quintile), plus a short-term tax rate of up to 37% on any gains, plus about 1 pp/yr of timing loss. A paper edge of a few percent per year rarely survives all three.
- Turnover below 50%/month and buy/hold bands are the cheapest defenses. Holding positions more than a year converts the tax rate.

### Gaps
- No primary source fetched for current retail bid-ask/PFOF price-improvement magnitudes (e.g., SEC Rule 605 data) in 2024-26.
- The exact Barber-Odean household count (66,465) comes from my background knowledge. The fetched abstract says "over 60,000".
- After-tax SPIVA numbers were not extracted.

---

## Thread 3: The arithmetic of active management, and what skeptics concede works

### Takeaway
Sharpe's (1991) arithmetic says active management is zero-sum before costs and negative-sum after. SPIVA confirms that over 15 years no category of active managers has a majority beating its benchmark. Pedersen (2018) shows the arithmetic is not strictly exact. What skeptics do concede are modest but real "edges" that come from cost, tax and behavior rather than prediction: low cost, tax-loss harvesting (~0.8-1.1%/yr in simulation, front-loaded), asset location (0-75 bps), rebalancing (12-42 bps, by Vanguard edition), avoiding the behavior gap (~1-2%/yr), and factor premia, but only with decade-plus patience.

### Interview

**Round 1. Q: What is the core arithmetic?**
- Sharpe (FAJ 1991): "before costs, the return on the average actively managed dollar will equal the return on the average passively managed dollar", and "after costs, the return on the average actively managed dollar will be less". This holds because the market is the value-weighted sum of active and passive holdings — [Sharpe, Stanford](https://web.stanford.edu/~wfsharpe/art/active/active.htm)

**Round 2. Q (sharper): Is the arithmetic airtight?**
- Pedersen (2018, "Sharpening the Arithmetic of Active Management") argues that Sharpe implicitly assumes the market portfolio never changes. IPOs, index changes and buybacks force passive investors to trade, so whether active adds value in aggregate is an empirical question — [AQR](https://www.aqr.com/insights/research/journal-article/sharpening-the-arithmetic-of-active-management); [CFA blog](https://rpc.cfainstitute.org/blogs/enterprising-investor/2025/from-sharpe-to-pedersen-why-active-management-isnt-zero-sum-after-all)
- Another working paper argues that in multi-period settings, Sharpe's first statement may give too much credit to active managers: the median active fund lags even before costs — [Lozada, Utah](https://content.csbs.utah.edu/~lozada/Research/ActiveVDrag7.pdf)

**Round 3. Q (sharper): Empirically, how do professionals do?**
- SPIVA U.S. YE2024: 65% of active large-cap funds underperformed the S&P 500 in 2024, up from 60% in 2023. Over 15 years there was no category, among all equity and fixed-income categories, where a majority of active managers outperformed — [SPIVA US YE2024](https://spglobal.com/spdji/en/spiva/article/spiva-us-year-end-2024). A secondary source gives about 84% of large-cap funds underperforming at the longest horizon, but the column mapping is unverified — [Institutional Investor](https://institutionalinvestor.com/article/2ei0q73dr49zygyfxzu2o/portfolio/active-continue-to-struggle-especially-when-measured-over-long-time-periods)

**Round 4. Q (sharper): So what DO skeptics concede works for individuals, and by how much?**
- Vanguard Advisor's Alpha (2022 edition) puts the total at "about 3%", and warns that modules are not additive and that this is not an annual add-on. Module values: behavioral coaching up to 200+ bps, rebalancing 12 bps, asset location 0-45 bps — [Vanguard 2022 PDF](https://corporate.vanguard.com/content/dam/corp/articles/pdf/putting_value_on_your_value_quantifying_vanguard_advisors_alpha.pdf). An earlier handout gave rebalancing 35 bps, asset location 0-75 bps, behavioral 150 bps — [Vanguard handout](https://assets.contentstack.io/v3/assets/blt4eb669caa7dc65b2/blt6e6801f2660ef0ab/64f88a95b8c6d623fb0e3abc/150_basis_points.pdf). The Canada 2018 edition gave behavioral 150 bps, rebalancing 42 bps, location 0-42 bps — [Vanguard Canada](https://vanguard.ca/content/dam/intl/americas/canada/en/documents/gas/advisors-alpha-infographic.pdf)
- The 2025 (25th-anniversary) edition adds tax-loss harvesting as a module at "up to 150 bps or more", asset location at 0-60 bps, and behavioral at up to 200 bps — [Financial Planning](https://financial-planning.com/news/vanguard-advisors-alpha-study-cites-tax-loss-harvesting)
- Independent TLH estimate: 1.08%/yr from 1926-2018, falling to 0.82% with the wash-sale constraint and to about 0.95% after transaction costs. The figure is regime-dependent: 2.13%/yr in 1926-49 but 0.51% in 1949-72 — [Chaudhuri, Burnham, Lo, CFA/FAJ](https://rpc.cfainstitute.org/research/financial-analysts-journal/2020/empirical-evaluation-tax-loss-harvesting-alpha); [MIT DSpace](https://dspace.mit.edu/bitstream/handle/1721.1/135992/SSRN-id3351382.pdf)
- Behavior gap avoided: about 1.1-1.2 pp/yr (Morningstar, Thread 2) — [Mind the Gap 2024](https://marketing.morningstar.com/content/cs-assets/v3/assets/blt9415ea4cc4157833/blt5d1d34a59bd78a2c/680a4bd8c4d2e877fdb4b354/Mind_the_Gap_2024.pdf)

**Round 5. Q (sharper): And factor premia, given that JKP says they replicate. Can an individual just hold value?**
- AQR (Asness, Frazzini, Israel, Moskowitz, "Fact, Fiction, and Value Investing", 2015): the value premium appears in 87 years of US data, more than 30 years of out-of-sample evidence, and 40 other countries — [AQR](https://www.aqr.com/insights/research/journal-article/fact-fiction-and-value-investing)
- But patience is the price. AQR itself describes a "10+ year" value drawdown and argues that realized long-run averages can mislead — [AQR "The Long Run Is Lying to You"](https://www.aqr.com:443/-/media/AQR/Documents/Perspectives/The-Long-Run-Is-Lying-to-You.pdf?sc_lang=en); Asness describes the "long but shallower" 2010-2017 value drawdown — [AQR "A Gut Punch"](https://aqr.com/Research-Archive/Perspectives/A-Gut-Punch)
- After costs and publication decay, the expected net premium is much smaller than the backtest: about 4-20 bps/month per Chen-Velikov (Thread 1).

### Inferences
- The surviving "edges" share one feature: they come from not losing (fees, taxes, timing errors), not from forecasting. They are about 0.5-3%/yr combined, not additive, and front-loaded in the case of TLH, since harvestable losses shrink as the basis ratchets down.
- Factor premia are the one predictive edge skeptics partly concede. They require low-turnover implementation and a horizon long enough to sit through decade-long drawdowns. A retail trader who abandons the strategy in a drawdown turns the factor premium into a behavior-gap loss.
- Relevance to this repo: the project's frozen-model, change-controlled approach (per memory) is the practical defense against overfitting and abandonment that this literature recommends.

### Gaps
- I could not fetch the official SPIVA YE2024 page (HTTP 403), so the 10/15/20-year large-cap percentages and survivorship rates are unconfirmed beyond the "no category majority at 15 years" headline.
- No independent (non-Vanguard) verification was found for the rebalancing-bonus magnitudes. Vanguard's own figures vary from 12 to 42 bps by edition.
- I did not find the exact quoted passage on value's historical frequency of 10-year underperformance in the 2015 AQR paper.
