# When buying options pays for a retail investor in US mega-cap tech (calls, LEAPS, PMCC, protective puts, collars)

Scope: long-only retail, TSLA/NVDA/AAPL/MSFT/GOOGL/AMZN/META/AVGO/TSM/AMD/ORCL. Evidence as of Nov 2026. Research budget was limited (about 15 tool calls). Several primary pages (IBKR, Alpha Architect, Advisor Perspectives) returned HTTP 403, so some figures come from search-engine summaries of those pages. Those figures are flagged.

## Q1. Effective financing rate in deep-ITM (~0.80 delta) LEAPS vs 2026 margin rates; cost of extrinsic; leverage, decay, liquidity, rolling

### Takeaway
By put-call parity, a deep-ITM call's extrinsic value splits into (a) interest on the strike, charged at roughly the risk-free/box rate (about 3.9% in late 2026), plus (b) an embedded put that works as downside insurance. The pure financing part is cheaper than retail margin at Schwab or Fidelity (about 11.6%) and roughly equal to or cheaper than IBKR or Robinhood (about 5.3–5.4%). The *total* extrinsic is much higher for high-IV names, though: about 13% per year per dollar financed for an NVDA-like stock vs about 6–7% for an MSFT-like one. The investor pays for insurance whether they want it or not. LEAPS make most sense when you want both the leverage and the capped loss. If you only want leverage, cheap margin (IBKR-class) is the cleaner instrument.

### Cited Findings
- 2026 margin rates (search summary of IBKR's comparison table, as of 21 Sep 2026; primary page returned 403): IBKR Pro 5.38% at $25K, falling to 4.72% at $3.5M, blended by tier. Schwab and Fidelity were both 11.58% at $25K and 10.33% at the next tier. A separate review gives Fidelity's base rate as 10.825% (effective 18 Sep 2026). — [IBKR margin page (via search)](https://www.interactivebrokers.com.sg/en/trading/margin.php); [Social Life Magazine aggregator](https://sociallifemagazine.com/finance/your-broker-may-be-charging-you-double-to-borrow/)
- Third-party October 2026 comparison: Public 5.15%, Robinhood 5.25%, IBKR Pro 5.38%, IBKR Lite 6.38% at $25K. Earlier 2026 snapshots differ (March 2026: IBKR Pro 5.14%, Schwab 12.33%, Fidelity 11.33%). — [tradingcosts aggregator](https://tradingcosts.labs.searchatlas.com/margin-interest-rates-brokers-2026/); [Westmount](https://westmount-fundamentals.pages.dev/broker-fees); [Public.com](https://public.com/learn/lowest-margin-rates-compared)
- Policy rate: the FOMC held at 3.75–4.00% on 28 Oct 2026 (10–2 vote, two dissents favoring a hike). Other sources report a 3.50–3.75% range in mid-2026, so the series conflicts and should be checked against federalreserve.gov. — [Advisor Perspectives, Oct 28 2026](https://www.advisorperspectives.com/dshort/updates/2026/10/28/feds-interest-rate-decision-october-28-2026); [Mondo Visione, Jul 29 2026 statement](https://mondovisione.com/news/federal-reserve-issues-fomc-statement-2026729/)
- Box spreads expose an implied financing rate that can be compared directly with T-bills and margin rates. CME notes the implied-rate math is that of any fixed-income instrument and is especially relevant for deep-ITM strikes. — [CME Group](https://www.cmegroup.com/articles/2024/index-options-box-spreads-as-financing-tool.html); [Schwab](https://www.schwab.com/learn/story/what-are-box-spreads)
- Poor man's covered call (PMCC) = deep-ITM LEAPS used instead of long stock, with short near-term calls sold against it. — [box-spread / PMCC explainer (via search)](https://boxspread-site.pages.dev/articles/the-four-leg-structure)
- Early-assignment risk on short calls rises around large dividends when the call is ITM. This matters for the short leg of a PMCC on dividend payers (MSFT, AAPL, AVGO, ORCL, TSM). — [Option Strategist](https://optionstrategist.com/node/6671)

**Worked example (my own Black-Scholes calculation, not market quotes).** Inputs: S = 100 (normalized), r = 3.9%, IV 45% with ~0 dividend for "NVDA-like"; IV 24% with 0.8% dividend yield for "MSFT-like". Strike chosen for delta of about 0.80. These IVs are typical-regime assumptions. Check live chains before use.

| Case | Tenor | Strike | Call | Leverage (Δ·S/C) | Extrinsic | of which interest K(1−e^−rT) | of which embedded put | Extrinsic per $ financed per yr | Theta, 1st month |
|---|---|---|---|---|---|---|---|---|---|
| NVDA-like | 1.0y | 79 | 30.41 | 2.6x | 9.41 (9.4% of S) | 3.02 | 6.42 | 13.5% | 0.70 |
| NVDA-like | 1.5y | 78 | 34.77 | 2.3x | 12.77 | 4.43 | 8.39 | 13.1% | 0.58 |
| MSFT-like | 1.0y | 86.5 | 18.94 | 4.2x | 5.44 | 3.31 | 2.93 (+0.8 dividends forgone) | 6.7% | 0.42 |
| MSFT-like | 1.5y | 85 | 22.28 | 3.6x | 7.28 | 4.83 | 3.65 (+1.2 dividends forgone) | 6.2% | 0.36 |

- Decay profile (NVDA-like, 2-year, K = 77.5, spot held flat): extrinsic is 15.8 at 2.0y, 12.6 at 1.5y, 8.9 at 1.0y, 6.8 at 0.75y, 4.4 at 0.5y, 1.9 at 0.25y, and 0.5 at 0.1y. Decay accelerates in the last ~6 months. This is the mechanical basis for the "roll at 6–9 months remaining" rule.
- Comparison: a 1-year ATM NVDA-like call costs about 19.4 (delta 0.62), and almost all of that is extrinsic.

### Inferences
- The financing component of a LEAPS is the market's box/risk-free rate plus the bid-ask spread. It is about 4% in late 2026, which beats Schwab/Fidelity margin (~11.6%) by about 7 points per year and ties IBKR/Robinhood. Stating that LEAPS have a "13% financing rate" is wrong. The excess over r is insurance (the embedded put), and high-IV names like NVDA, TSLA and AMD make that insurance expensive.
- At equal delta exposure, LEAPS lose to IBKR margin unless (i) implied vol is below the vol you expect to realize, or (ii) you put real value on the capped loss (no margin call, no forced liquidation during a 50% drawdown). For low-IV names (MSFT, AAPL, GOOGL), the insurance part is small and LEAPS are a reasonable margin substitute. For TSLA/NVDA/AMD it is costly.
- Dividend payers: the LEAPS holder does not receive dividends (about 0.8–1.2% of S over the life of an MSFT-like LEAPS).
- Bid-ask on 1–2 year LEAPS is a direct financing cost. A $0.50 round-trip spread on a $30 option is about 1.7% of premium per round trip, so rolling often wipes out the margin advantage. That number is an assumption: I found no published 2026 spread statistics for mega-cap LEAPS.
- Rolling: the "roll with 6–9 months left, back to ~0.80 delta" rule matches the computed decay curve and is mechanically sensible. The specific delta and DTE numbers are practitioner convention and have no tested-edge evidence behind them. Treat them as folklore with a rational basis.
- Leverage of 2.3–4.2x on a single high-vol name means a 30–40% drawdown, which is common for NVDA, TSLA or AMD, can take 70–100% of the LEAPS premium. LEAPS cap the dollar loss but do not reduce the percentage loss on the capital in the trade.

### Gaps
- No live 2026 NVDA/MSFT LEAPS chains were retrieved, so the example is model-based. To fill this, pull Jan-2028 chains and compute (C − (S − K·e^−rT)) directly; market-implied r usually comes out slightly above T-bills.
- No primary-source data was found on bid-ask spreads or open interest for 1–2 year expiries on these names.
- I found no peer-reviewed study of PMCC/diagonal returns. Evidence on PMCC comes only from education material (folklore tier).

## Q2. Does systematic put protection or collaring improve long-run returns, or only reduce drawdowns at a cost?

### Takeaway
Mainly the second. Monthly 5% OTM index puts (PPUT) lower volatility and reduce the number of bad months. But Israelov finds that holding less equity achieves the same average return with *better* drawdowns and a higher Sharpe ratio, because puts embed the volatility risk premium. Collars (CLL) are cheaper because the investor gives up upside. AQR prefers trend-following to puts as a tail hedge. Universa's large crash returns come from tiny, specific allocations and are disputed. They are not evidence that retail put-buying is positive-EV.

### Cited Findings
- PPUT method: S&P 500 plus a monthly 5% OTM SPX put. CLL: S&P 500, sells a monthly 110% call, buys a quarterly 95% put. CLLZ: buys a monthly 2.5–5% put spread funded by a short OTM call. — [Cboe](https://www.cboe.com/insights/posts/benchmark-indices-series-hedging-downside-exposure-with-pput-cll-and-cllz-indices)
- Cboe (Jun 1986–Jun 2021): all three indices had beta below 0.75. PPUT had 18 monthly declines of 6% or more vs 35 for the S&P 500. In 2008 and 2020, PPUT beat other stock indices by more than 10 percentage points. Max drawdown −38.91% (PPUT) vs −50.95% (S&P 500). Cboe notes fewer >4% up-months and "a cost to buying put options." — [Cboe benchmark post](https://www.cboe.com/insights/posts/benchmark-indices-series-hedging-downside-exposure-with-pput-cll-and-cllz-indices); [Cboe Portfolio Protection](https://cboe.com/us/index_protection/)
- Independent analysis, Jul 1986–May 2016 (search summary): PPUT annualized vol 13.5%, beta 0.74. A static index-plus-cash mix with the same beta matched returns with lower vol. One quoted figure gives PPUT drawdown −32.1% vs −20.9% for the comparison mix. Methods and periods differ from Cboe's. — [CXO Advisory](https://www.cxoadvisory.com/equity-options/do-protective-equity-index-puts-work-well/)
- Israelov, "Pathetic Protection" (J. Alternative Investments, 2019): put-protected portfolios have worse peak-to-trough drawdowns per unit of expected return than statically de-risked portfolios. Sized to the same average return, divesting has lower drawdowns, lower vol, lower beta and a higher Sharpe. Puts win only when a large crash happens within the option's life. Effectiveness depends on matching option maturity to drawdown length, which cannot be known in advance. Main cause: the volatility risk premium. — [Alpha Architect (via search, page 403)](https://alphaarchitect.com/pathetic-protection/); [Advisor Perspectives (via search)](https://www.advisorperspectives.com/articles/2019/08/22/are-puts-efficient-at-protecting-downside-risk); [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/pathetic-protection-via-protective-puts/)
- Hedge Fund Alpha summary: divesting beat protection in 97% of very short horizons and 100% of longer horizons in the simulations, which are hypothetical. — [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/pathetic-protection-via-protective-puts/)
- AQR (Ilmanen, Thapar, Tummala, Villalon, J. Systematic Investing 2021), "Tail Risk Hedging: Contrasting Put and Trend Strategies": the view that puts are costly but more reliable "has some merit but misses the full picture." The authors prefer trend-following as a tail hedge because of its long-run cost. — [AQR](https://aqr.com/Insights/Research/White-Papers/Tail-Risk-Hedging-Contrasting-Put-and-Trend-Strategies)
- Universa vs AQR: Universa reported a 3,612% Q1-2020 return on its tail fund. Taleb (Universa adviser) said AQR did not test the tail-hedged portfolio construction Universa uses. A FactorResearch analysis found tail-risk funds and cash had similar risk/return and drawdowns over 2007–2020. — [Advisor Perspectives](https://www.advisorperspectives.com/articles/2020/05/06/an-aqr-warning-and-a-3-612-return-fire-up-the-black-swan-debate); [Advisor Perspectives, empirical support](https://www.advisorperspectives.com/articles/2020/07/13/empirical-support-for-tail-risk-strategies)

### Inferences
- For a concentrated mega-cap tech basket, rolling single-name puts on each stock costs more than one index put (QQQ/NDX/SPX) because single-name IVs are higher. Index puts leave basis risk: an idiosyncratic −40% move in one stock is not covered. Cheapest robust option: size down (Israelov's "divest") and use index puts or a collar only for a known, dated risk window.
- Collars turn the cost into forgone upside. For momentum mega-caps, the forgone right tail may be the main source of return, so a 110% call cap is expensive in opportunity cost even when the premium nets to zero.
- Universa's numbers do not carry over to a retail investor buying 5% OTM monthly puts. They rely on far-OTM, crash-convex positions sized at a few percent of capital, with institutional execution.

### Gaps
- Primary PPUT/CLL annualized return, standard deviation and Sharpe for 1986–2026 were not retrieved (Cboe gives them only in charts). Fetch from Cboe index data.
- No retrieved study quantifies single-name put costs for these 11 stocks against index-put basis risk.

## Q3. Documented retail option-buyer outcomes; conditions where buying is positive-EV

### Takeaway
Retail option buyers lose money systematically, mostly through spreads, buying expensive implied vol, and holding too long. The only academically supported "buy" signal is cross-sectional: buy options where implied vol is low *relative to historical/realized* vol (Goyal–Saretto). Even that edge is sensitive to bid-ask costs and is a delta-hedged, long-short institutional strategy, not a retail directional call purchase. Buying ahead of earnings is the worst-documented retail pattern.

### Cited Findings
- Bryzgalova, Pavlova, Sikorskaya, "Retail Trading in Options and the Rise of the Big Three Wholesalers" (J. Finance 2023): retail lost about $1.14B on options from Nov 2019 to Jun 2021 (10-day holding assumption). Dollar options volume rose 143%. Retail favors cheap, short-dated, lottery-like contracts. Losses are driven largely by bid-ask/round-trip costs. Payment for order flow from wholesalers supported the growth. — [LBS](https://www.london.edu/faculty-and-research/academic-research/r/retail-trading-in-options-and-the-rise-of-the-big-three-wholesalers); [FA Mag](https://www.fa-mag.com/news/mom-and-pop-investors-took-a-billion-dollar-bath-trading-options-during-the-pandemic-67571.html?section=43); [Wealth Advisor](https://www.thewealthadvisor.com/article/mom-and-pop-investors-took-billion-dollar-bath-trading-options-during-pandemic)
- Beckmeyer, Branger, Gayda, "Retail Traders Love 0DTE Options… But Should They?" (SSRN 2023; secondary-coverage figures): average retail loss of $184K/day (Feb 2021–Feb 2023), rising to $358K/day after daily expiries began in May 2022. Total losses over $70M, of which over $50M was transaction costs. About 75% of retail S&P 500 option trades were 0DTE. The authors attribute the motive to gambling/entertainment. A 2025 Cboe analysis disputes the retail-discipline picture. — [CFR Cologne WP](https://www.cfr-cologne.de/download/workingpaper/cfr-25-09.pdf); [BNN Bloomberg](https://www.bnnbloomberg.ca/day-traders-lose-358-000-per-day-gambling-on-zero-day-options-1.1910634); [Cboe](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact)
- de Silva, Smith, So, "Losing is Optional: Retail Option Trading and Expected Announcement Volatility" (Review of Finance 2025): retail concentrates purchases before earnings with high expected volatility and loses 5–9% on average, or 10–14% for high-expected-vol announcements. Three drivers: overpaying relative to realized vol, wide spreads, and slow exits (buy about a week before, exit about two weeks after). Sample: 2010–Feb 2021, 32,791 announcements. — [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/publications/losing-optional-retail-option-trading-expected-announcement); [Quantpedia](https://quantpedia.com/how-retail-losses-money-in-option-trading/); [MIT Sloan](https://mitsloan.mit.edu/ideas-made-to-matter/retail-investors-lose-big-options-markets-research-shows)
- Goyal and Saretto (JFE 2009): sorting on historical minus ATM implied vol, long low-IV-vs-HV / short high-IV-vs-HV straddles and delta-hedged options earned significant monthly returns (1996–2006), robust to risk factors. Bid-ask costs materially erode profitability, and one replication finds the edge disappears with alternative real-time IV estimates. — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:94:y:2009:i:2:p:310-326); [NUS RMI](https://rmi.nus.edu.sg/wp-content/uploads/2020/11/30.-Guanglian-Hu.pdf)

### Inferences
- "Buy when IV rank is low" is a loose version of Goyal–Saretto. The research supports IV *relative to realized/historical vol* in the cross-section, not IV rank against the stock's own 52-week range. IV-rank rules as sold by retail platforms are folklore unless backtested.
- No retrieved peer-reviewed evidence shows pre-earnings options are systematically *under*-priced for mega-caps. The evidence points the other way (de Silva et al.). This matches this repo's own earnings work (the earnings iron-fly experiment sells, not buys, event vol).
- Retail conditions closest to non-negative EV: long-dated, deep-ITM, liquid contracts held for exposure (low spread as a share of premium, little extrinsic), bought with limit orders at mid. This minimizes the documented loss channels: spread, vol premium and lottery strikes. It reduces costs. It is not a source of positive alpha.

### Gaps
- No study was retrieved specifically on retail LEAPS-buyer outcomes. The documented losses are concentrated in short-dated contracts.
- Exact figures for Beckmeyer et al. come from secondary coverage; the SSRN PDF was not read.

## Q4. Practical rules (DTE, delta, roll/exit): evidence-based vs folklore

### Takeaway
Rules backed by evidence or arithmetic: use limit orders and liquid strikes (spreads drive most retail losses); avoid short-dated OTM and pre-earnings long vol (documented losses); compare total extrinsic per year against your actual margin rate; size down rather than buy puts for permanent protection. Folklore (plausible arithmetic, no tested edge): "0.80 delta," "roll at 90/180 DTE," "buy when IV rank < 30," "PMCC short call at 0.30 delta."

### Cited Findings
- Transaction costs account for most retail options losses: over $50M of $70M in 0DTE, and bid-ask is the main driver in BPS. — [BNN Bloomberg](https://www.bnnbloomberg.ca/day-traders-lose-358-000-per-day-gambling-on-zero-day-options-1.1910634); [Wealth Advisor](https://www.thewealthadvisor.com/article/mom-and-pop-investors-took-billion-dollar-bath-trading-options-during-pandemic)
- Holding through and after the event is a measurable loss driver around earnings. — [Quantpedia](https://quantpedia.com/how-retail-losses-money-in-option-trading/)
- Put protection is inefficient compared with divesting, except when hedge maturity matches the crash. — [Hedge Fund Alpha](https://hedgefundalpha.com/strategies/pathetic-protection-via-protective-puts/)
- Volatility-mispricing edge is cross-sectional (HV vs IV), not timing on IV rank, and is cost-sensitive. — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:94:y:2009:i:2:p:310-326)

### Inferences
- Rules ranked by support:
  1. **Arithmetic or evidence:** LEAPS vs margin decision = extrinsic/(S − C)/T against your broker's rate (about 5.4% IBKR, about 11.6% Schwab/Fidelity). Prefer LEAPS on low-IV names or when you value the stop-loss. Prefer cheap margin (or plain stock) on high-IV names.
  2. **Arithmetic:** a deeper ITM strike means less extrinsic per unit of delta and less vol-premium exposure, but less leverage. 0.80 is a compromise, not an optimum.
  3. **Arithmetic:** decay accelerates within about 6 months, so roll before then. The exact trigger is folklore.
  4. **Folklore:** IV-rank entry thresholds, PMCC short-call delta targets, "buy calls instead of stock to limit risk." Buying calls caps the dollar loss but raises the probability of total loss, and the premium carries the vol risk premium.
- Calls vs stock (unlevered comparison): holding stock plus cash equal to the strike's present value replicates a call minus the embedded put. The call buyer is therefore long stock plus long a put, i.e. a protective-put investor, and Israelov's cost critique applies to all call buying.

### Gaps
- No controlled study on optimal LEAPS strike or roll timing for retail was found.
- No 2026 data on LEAPS liquidity by name. Mega-caps (NVDA, TSLA, AAPL, MSFT, AMZN, META) are generally assumed to have the deepest long-dated chains, and TSM/ORCL/AVGO thinner, but this was not verified.
