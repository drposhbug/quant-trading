# Risk Management and Position Sizing for a Concentrated TSLA + Mega-Cap Tech Quant Portfolio (US retail, as of Nov 2026)

## Q1. Volatility targeting, fractional Kelly, risk parity, HRP: which suit ~8 correlated stocks?

### Takeaway
Volatility targeting at the portfolio level, with inverse-volatility or HRP weights inside the book and a fractional (at most half) Kelly cap on total exposure, is the best-supported combination. Each method has a weakness. Vol targeting thins the left tail of equity returns, but its claimed alpha is fragile out of sample. Full Kelly is dangerous when means are estimated with error. HRP's evidence comes mostly from simulations. With only 8 assets, equal or inverse-vol weighting is a hard baseline to beat.

### Cited Findings
**Volatility targeting / vol-managed portfolios**
- Moreira & Muir (Journal of Finance, 72(4), 2017, pp. 1611-1644) scale each month's return by the inverse of the prior month's realized variance. They report that "managed portfolios that take less risk when volatility is high produce large alphas, increase Sharpe ratios, and produce large utility gains for mean-variance investors." — [NBER w22208](https://www.nber.org/papers/w22208); [published PDF](https://amoreira2.github.io/alan-moreira.github.io/VolPortfolios_published.pdf)
- Cederburg, O'Doherty, Wang & Yan (JFE 2020) find positive spanning-regression alphas, but the real-time, implementable versions earn lower certainty-equivalent returns and Sharpe ratios than the unmanaged portfolios. They blame structural instability in the regressions. Across 103 equity strategies, the managed versions won in 53 cases and lost in 50. — [EconPapers JFE 138(1)](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117); [Lehigh working paper](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
- Barroso & Detzel find vol-managed strategies do not survive transaction costs. DeMiguel, Martin-Utrera & Uppal (JF 2024) accept the single-factor failure but report that a conditional multifactor version beats the unconditional one out of sample and net of costs, with a Sharpe ratio about 13% higher. — [DeMiguel et al. JF 2024 PDF](https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:79:y:2024:i:6:p:3859-3891)
- Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert ("The Impact of Volatility Targeting", JPM 2018, Man Group):
  - For US equities, the Sharpe ratio rises from about 0.40 unscaled to 0.48-0.51 scaled, and the result is not sensitive to the vol estimator.
  - Vol-of-vol falls from 4.6% to 1.8%.
  - Left-tail events (for example monthly returns of -10% or worse) are less severe because volatility rises as prices fall, so scaling adds some momentum.
  - The effect is negligible for bonds, FX and commodities, so it matters most for risk assets.
  - Sources: [Duke PDF](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf); [Alpha Architect summary](https://alphaarchitect.com/volatility-targeting-improves-risk-adjusted-returns/). The figures come from secondary summaries and were not checked against the paper's tables.

**Fractional Kelly**
- MacLean, Thorp & Ziemba (Quantitative Finance 2010) find that fractional Kelly reduces the damage from estimation error. Kelly is very sensitive to parameter estimates, especially the means, "which makes the strategy dangerous to those whose estimates are in error." Full Kelly carries drawdowns "too large for the comfort of many investors." — [Good and Bad Properties of the Kelly Criterion](https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf)
- In the simple growth model, half Kelly keeps about 75% of the optimal growth rate. Betting twice Kelly drives growth to about zero, so overbetting costs much more than underbetting. — [Wikipedia: Kelly criterion](https://www.wikipedia.org/wiki/Kelly_criterion); [Downey simulations](https://matthewdowney.github.io/uncertainty-kelly-criterion-optimal-bet-size)
- In Ziemba-Hausch simulations, the chance of losing half of wealth was about 8.4% under full Kelly and about 1% under half Kelly. — [Ziemba slide deck via mathnet.ru](https://www.mathnet.ru/PresentFiles/7097/7097.pdf) (a secondary summary of the simulations)
- Rising & Wyner shrink the estimated mean toward the risk-free rate to avoid over-betting, which can otherwise lead to ruin. — [Hakobyan & Lototsky, arXiv 2503.17927](https://www.arxiv.org/pdf/2503.17927)

**HRP / risk parity**
- Lopez de Prado's HRP (2016) uses clustering, quasi-diagonalization and recursive bisection, so it never inverts the covariance matrix. In the author's own Monte Carlo, it had lower out-of-sample variance than Markowitz CLA (even though CLA's objective is minimum variance) and was less risky than traditional risk parity. — [SSRN 2708678](https://papers.ssrn.com/abstract=2708678)
- Independent evidence is mixed:
  - A CBS master's thesis confirmed lower out-of-sample variance but found HRP less robust to covariance misspecification than some non-hierarchical methods. — [CBS thesis](https://research-api.cbs.dk/ws/portalfiles/portal/76452070/1332322_Master_Thesis_Hierarchical_Risk_Parity.pdf)
  - An informal 20-ETF walk-forward test had HRP trail inverse-variance on return and minimum-variance on volatility. — [Quantopian archive](https://quantopian-archive.netlify.app/forum/threads/hierarchical-risk-parity-comparing-various-portfolio-diversification-techniques)
  - Naive 1/N often beats optimizers out of sample (DeMiguel et al. 2009, cited in the HRP paper). — [SSRN 2708678 PDF copy](https://www.smallake.kr/wp-content/uploads/2020/04/SSRN-id2708678.pdf)

### Inferences
- With N=8, a covariance matrix has only 36 entries, so estimation error is small enough that HRP's main advantage (avoiding inversion of an ill-conditioned matrix) is modest. HRP's clustering is still useful as a diagnostic: it will likely show TSLA as its own branch apart from a software/semis/platform cluster. Inverse-vol weighting is a strong, simple default. HRP vs inverse-vol vs 1/N should be backtested walk-forward rather than assumed.
- Recommended stack:
  1. Inside the book, use inverse-vol or HRP weights.
  2. Scale the whole book to a target volatility, with an exposure cap (for example at most 1.0-1.5x gross).
  3. Set the cap from a fractional Kelly estimate (0.25-0.5x) using shrunk expected returns.
- The Harvey et al. result applies to diversified equity indices. Single-stock vol targeting on TSLA will also cut exposure after the large up-moves typical of a high-vol, positively skewed stock, so expect a sacrifice of upside.
- Vol targeting pays off mainly in risk control (fewer deep left-tail months). The case for alpha is weak out of sample, so justify it as a risk tool, not a return source. Keep turnover low with banded rebalancing to avoid the cost drag that Barroso & Detzel document.

### Gaps
- No primary-source drawdown-probability tables for fractional Kelly on equity-like (fat-tailed) return distributions were retrieved.
- No study found tests HRP specifically on a universe of about 8 mega-cap tech stocks.
- The 13% Sharpe improvement in DeMiguel et al. and the Harvey et al. Sharpe figures come from summaries, not checked against the papers' tables.

## Q2. TSLA's extreme volatility and earnings gaps; stop-loss evidence; drawdown controls

### Takeaway
Earnings gaps can't be stopped out: a stop-loss order fills at the gap open, not at the stop level. TSLA's realized earnings moves have ranged from about 4% to 13% depending on period. Size around earnings explicitly by cutting exposure or defining risk with options. In theory, stop-losses only lower expected return if prices follow a random walk. They help only where returns show momentum or regime-switching. Portfolio-level drawdown rules are a better-supported control than tight per-stock stops.

### Cited Findings
- TSLA earnings-move history (methods differ: next-session vs peak intraday move):
  - ORATS: over the last six reports, the average realized move was about 4.3% against about 6.3% implied, down from a 12.9% average realized move across 2023-2024. — [ORATS](https://orats.com/blog/tesla-earnings-market-wild-card-went-quiet)
  - EarningsWatcher: the 10-year average peak intraday earnings-day move is about ±9.4% (median ±8.9%). Moves beat the implied move in about 69-71% of reports since 2022. Implied move for the Oct 2026 report: ±7.5%. — [EarningsWatcher](https://earnings-watcher.com/wiki/tsla-implied-move); [Oct 2026](https://earnings-watcher.com/wiki/tsla-earnings-october-2026)
  - Regards of Wall Street: average first-session move of ±10.2% for reports from Jul 2022 to Apr 2025. — [RoWS](https://www.regardsofwallstreet.com/tools/earnings-history/tsla)
  - 2023 MarketChameleon data: options overestimated the move 67% of the time over 12 quarters (realized about 5.9% vs implied about 8.2%). — [MarketChameleon](https://marketchameleon.com/articles/b/2023/7/19/tsla-s-earnings-comparing-implied-moves-with-historical-trends)
  - These sources conflict on whether implied over- or understates the move. The answer depends on the window and on the move definition.
- Kaminski & Lo, "When Do Stop-Loss Rules Stop Losses?" (Journal of Financial Markets, 2014):
  - Under a random walk, stop-loss rules "simply force the portfolio out of higher-yielding assets on occasion, thereby lowering the overall expected return without adding any benefits."
  - Under momentum or Markov regime-switching, stops can add value.
  - On monthly US equity data from 1950-2004, certain stop-loss rules added 50-100 bp/month during stop-out periods. This figure comes from the working-paper abstract.
  - Sources: [MIT DSpace PDF](https://dspace.mit.edu/bitstream/handle/1721.1/114876/Lo_When%20Do%20Stop-Loss.pdf); [EconPapers](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:234-254)
- Vol scaling makes left-tail months less severe because exposure is already lower when volatility spikes. — [Harvey et al. 2018](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf)

### Inferences
- **Earnings rule:** treat the earnings event as a known jump. Size the position so that a 1.5-2x implied-move gap (roughly 10-15% for TSLA) costs no more than a fixed fraction of equity (for example 1% of NAV). Alternatively, cut the position into the print, or hold it through a put spread or collar so the loss is defined.
- **Volatility estimator:** use one that reacts quickly (EWMA or intraday realized vol) and add the implied earnings variance for days that include an event. Otherwise vol targeting will underestimate risk heading into a print.
- **Stop-losses:** the evidence favors slow, time-series-momentum-like stops (for example monthly-frequency exits after a large drawdown). It does not favor tight intraday stops on a mean-reverting, high-noise stock. Tight stops on TSLA will trigger often on noise.
- **Drawdown controls:** a portfolio-level de-risking ladder (for example cut gross 25% at -10% from peak and 50% at -20%, then re-risk on recovery or after a time window) is a practitioner convention, not an academically tested rule. Backtest any thresholds you adopt.

### Gaps
- TSLA's 2026 realized/implied volatility and beta to QQQ were not retrieved. Compute them from your own data (recent 60d/252d realized vol, beta).
- No academic study found on stop-losses for single high-vol stocks specifically.
- No authoritative source found on optimal drawdown-control thresholds.

## Q3. Correlation clustering among mega caps; QQQ beta; hedging with QQQ, futures or options

### Takeaway
Eight mega-cap tech names act much like one or two factor bets: the market/Nasdaq factor plus a TSLA idiosyncratic factor. Measure risk in factor (QQQ-beta) terms, not by name count. Hedge the common beta cheaply with Micro Nasdaq-100 futures or a QQQ short, and use options only for event and tail risk.

### Cited Findings
- The Magnificent Seven made up 34.3% of the S&P 500 in Dec 2025, up from 12.3% in 2015. The group fell roughly twice as hard as the index in 2022. — [Motley Fool, Jan 2026](https://www.fool.com/investing/2026/01/05/should-investors-be-worried-that-the-magnificent-s)
- The S&P 500's 12-month rolling correlation with the Nasdaq-100 hit an all-time high of 0.98 in March 2026, while its correlation with the equal-weight index fell to about 0.8. — [CME Group via Institutional Investor](https://www.institutionalinvestor.com/article/sponsored-content/what-past-sector-concentrations-tell-us-about-todays-tech-heavy-sp-500)
- A lower-authority source reports that Mag-7 rolling correlation with the equal-weight S&P turned negative on Feb 23, 2026. Correlations shift by regime. Unverified. — [rallies.ai](https://rallies.ai/news/magnificent-seven-correlation-with-sp-500-turns-negative-valuations-under-25x)
- Micro E-mini Nasdaq-100 (MNQ) is $2 x the index, with a 0.25-point tick ($0.50), and is 1/10 the size of NQ ($20 x). — [CME contract specs](https://cmegroup.com/trading/equity-index/us-index/micro-e-mini-nasdaq-100_contractSpecs_futures.html)
- Index futures are Section 1256 contracts: 60% long-term / 40% short-term regardless of holding period, and secondary sources say wash-sale rules do not apply. — [Optimus Futures](https://optimusfutures.com/e-mini-nasdaq-futures.php); [CME equity futures](https://cmegroup.com/equityfutures)
- A 2x leveraged ETP carries 50% long maintenance margin vs 25% for unleveraged. — [FINRA Rule 4210 interpretations](https://www.finra.org/rules-guidance/guidance/interps-4210)

### Inferences
- **Hedge sizing:** hedge notional = sum of (position $ × beta_i to QQQ). MNQ notional ≈ $2 × NDX level. At an NDX near 25,000 (illustrative only, check the live level), one MNQ is about $50k notional, coarse for small accounts. A QQQ short or puts give finer granularity.
- **What the hedge removes:** a beta hedge strips out the common factor and leaves TSLA's idiosyncratic risk. Expect the hedged book's volatility to be dominated by TSLA, so cap TSLA's risk contribution (for example at most 30-40% of portfolio variance) rather than its dollar weight.
- **Correlation regimes:** correlations rise in sell-offs. Estimate the covariance matrix with stress weighting (EWMA, or the downside-period covariance) and check diversification under correlation set to 0.9.
- **Options:** protective puts or put spreads on QQQ for tail risk, and single-name collars on TSLA around earnings. These cost premium and carry skew. Futures are cheaper for pure beta management.

### Gaps
- No current (2026) measured pairwise correlation matrix or QQQ betas for the 8 names were retrieved. Compute from data.
- Options-hedge cost-benefit evidence (put-protection drag studies) was not retrieved in this session.

## Q4. Leverage, margin, PDT status in 2026, and taxes for US retail

### Takeaway
The PDT rule is gone. The SEC approved FINRA's replacement on April 14, 2026, effective June 4, 2026, with firm phase-in allowed through Oct 20, 2027. In its place is an intraday margin standard, so check your own broker's implementation date. Reg T 50% initial and FINRA 25% maintenance still apply, and brokers often set higher house requirements for volatile names like TSLA. For taxes, short-term gains are taxed as ordinary income, and wash sales can hit a frequently traded 8-stock universe, including trades made in your IRAs.

### Cited Findings
**PDT / intraday margin (2026)**
- The SEC approved amendments to FINRA Rule 4210 on April 14, 2026 (Exchange Act Rel. No. 105226, 91 Fed. Reg. 20731). FINRA Regulatory Notice 26-10 followed on Apr 20, 2026. Effective June 4, 2026, with an optional 18-month phase-in ending Oct 20, 2027. — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard)
- Removed: the PDT definition (4+ day trades in 5 business days), the $25,000 minimum equity, and 4x "day trading buying power." — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard)
- How the new standard works — [WilmerHale](https://www.wilmerhale.com/en/insights/client-alerts/20260423-sec-approves-amendments-to-finra-rule-4210-replacing-day-trading-margin-requirements-with-a-modernized-intraday-margin-standard):
  - Firms compute an "intraday margin deficit" on any day with a transaction that reduces the intraday margin level, whether or not the customer day trades.
  - Firms either block such trades in real time or issue an end-of-day margin call.
  - A deficit stays outstanding up to the close of the 15th business day.
  - Repeated failure to meet deficits triggers a 90-day credit freeze.
  - Good-faith (cash) and portfolio margin accounts are excluded.
  - Maintenance requirements in 4210(c) are unchanged.
- E*TRADE implemented the change on June 9, 2026. Other brokers' dates vary within the phase-in. — [E*TRADE](https://us.etrade.com/knowledge/library/margin/pattern-day-trading-rule-change)

**Margin**
- Reg T initial margin is 50% of current market value for margin equity securities. FINRA 4210(c) maintenance is 25% of current market value for longs. Firms may require more. — [FINRA Rule 4210](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210); [SEC investor bulletin](https://www.sec.gov/investor/alerts/ib_marginaccounts.pdf); [FINRA alert](https://finra.org/investors/alerts/investing-borrowed-funds-no-margin-error)

**Taxes**
- **Wash sales:**
  - The window is 61 days (30 before, the sale day, and 30 after).
  - Buying calls or other contracts to acquire the same stock can trigger it.
  - A repurchase in an IRA or Roth IRA triggers it, and the loss is permanently lost because the IRA basis is not increased (Rev. Rul. 2008-5).
  - Different companies' stock is ordinarily not substantially identical (Pub. 550).
  - Sources: [Kiplinger](https://www.kiplinger.com/taxes/604947/wash-sale-rule); [Fidelity](https://www.fidelity.com/learning-center/personal-finance/wash-sales-rules-tax)
- **Trader status / 475(f):** without a valid 475(f) election, a trader's securities gains and losses are capital, reported on Schedule D and Form 8949. Trader status is a facts-and-circumstances test. A late election generally means waiting a year. — [IRS Topic 429](https://www.irs.gov/taxtopics/tc429)
- **475(f) deadline:** generally the due date, without extensions, of the prior year's return (typically April 15 of the election year). — [Schulte Roth & Zabel](https://www.srz.com/print/v2/content/196095/reminder-deadline-to-make-a-section-475-f-election-for-most.pdf). The IRS has denied relief for late elections in private letter rulings. — [PLR 202048009](https://ezel.ai/irs-rulings/202048009)
- **What 475(f) changes:** gains and losses become ordinary, so losses can offset other income. — [PLR summary](https://ezel.ai/irs-rulings/202150001). Wash-sale exemption under 475(f) is claimed by secondary sources only. — [Beancount.io](https://beancount.io/blog/2026/05/11/trader-tax-status-section-475f-mark-to-market-election-wash-sale-rule-3000-capital-loss-cap-day-traders-guide)
- Section 1256 futures get 60/40 treatment (see Q3). This is a tax advantage of hedging with MNQ/NQ over QQQ shorts.

### Inferences
- **What the PDT change does and doesn't do:** it removes the $25k barrier to frequent intraday rebalancing in margin accounts. It does not increase overnight leverage: Reg T 2:1 initial and 25% maintenance still apply. An intraday strategy can now be blocked or margin-called on a deficit basis, so systems must track intraday margin usage.
- **Leverage:** for a book with roughly 30-50% annualized volatility (typical of concentrated mega-cap tech plus TSLA; verify from data), even 1.5x gross leverage implies 45-75% volatility and a real chance of a 50%+ drawdown. Combining vol-target sizing with an exposure cap keeps leverage implicit and bounded. Brokers' house maintenance for TSLA is often above 25%, so model margin calls at the house rate.
- **Taxes:**
  - A systematic strategy that re-enters the same 8 names within 30 days will trigger wash sales frequently. Track them across all accounts, including IRAs and a spouse's accounts if applicable.
  - Swapping into a correlated but different name (for example MSFT to GOOGL) for tax-loss harvesting is ordinarily not a wash sale, though it changes exposure.
  - High-turnover gains are short-term and taxed at ordinary rates. Compare after-tax Sharpe, not pre-tax.

### Gaps
- The exact text of FINRA Regulatory Notice 26-10 was not fetched directly. Whether any minimum-equity figure remains for margin accounts (the long-standing $2,000 minimum margin equity under 4210(b)) was not confirmed.
- No IRS primary text found confirming that 475(f) traders are exempt from wash sales. Verify with a tax professional.
- 2026 ordinary income and short-term capital gains brackets were not retrieved.
- Specific broker house margin rates for TSLA in 2026 were not retrieved.
