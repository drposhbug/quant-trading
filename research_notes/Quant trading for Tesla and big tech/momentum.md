# Momentum and Trend-Following on Single Mega-Cap Stocks (TSLA, NVDA, AAPL, MSFT, GOOGL, AMZN, META)

Scope note: no peer-reviewed study I found tests momentum or trend rules on this exact 7-8 stock mega-cap universe. Almost all the evidence comes from broad stock universes, futures, or index ETFs, so applying it to these names is inference. Any "it works on TSLA/NVDA" claim from blogs or social media should be treated as anecdotal, because those names were picked after the fact (survivorship and selection bias).

## 1. Time-series vs cross-sectional momentum; lookbacks; volatility-scaled trend

### Takeaway
Two kinds of momentum are well documented. Time-series momentum (TSMOM) trades each asset on its own past 12-month return. Cross-sectional momentum (XSMOM) ranks stocks against each other, usually on the 12-1 month return. TSMOM also shows up in individual US stocks over about 90 years. A large share of the headline TSMOM performance in futures comes from volatility scaling, though, and volatility-managing momentum is the most robust improvement found.

### Cited Findings
- Moskowitz, Ooi and Pedersen (MOP) define TSMOM as an asset's own past 12-month excess return predicting its future return. They test 58 futures and forwards: equity indices, currencies, commodities and sovereign bonds. The effect persists for about a year, then partly reverses over longer horizons. They report it as robust across sub-samples, lookbacks and holding periods, using more than 25 years of data. — [AQR: Time Series Momentum](https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum)
- A diversified TSMOM portfolio across 58 markets is cited at a Sharpe of roughly 1.0. The same blog notes that applying it to individual stocks adds friction that can erode the edge. This is a secondary source. — [Menon Lab blog](https://themenonlab.blog/blog/time-series-momentum-hedge-fund-strategy-explained)
- **Critique (Kim, Tse and Wald 2016, J. Financial Markets):** MOP's results are "largely driven by volatility-scaling." Without vol scaling, TSMOM and buy-and-hold give similar cumulative returns with alphas that are not significantly different. Across 55 futures in 1985-2013, the monthly TSMOM alpha falls from 1.27% (vol-scaled) to 0.41% (unscaled). Outperformance vanishes in 2009-2013. — [Quantpedia summary](https://quantpedia.com/deconstructing-the-time-series-momentum-strategy/); [RePEc](https://econpapers.repec.org/RePEc:eee:finmar:v:30:y:2016:i:c:p:103-124)
- **Counterpoint:** Jo and Kim (2019) find a significant TSMOM anomaly regardless of the vol-scaling method. Huang, Li, Wang and Zhou argue TSMOM is weak, especially across a large cross-section of assets, and that pooled-regression methods bias it upward. — [Quantpedia summary](https://quantpedia.com/deconstructing-the-time-series-momentum-strategy/); [Alpha Architect](https://alphaarchitect.com/2016/12/time-series-momentum-volatility-scaling-and-crisis-alpha/)
- **TSMOM in individual stocks (Lim, Wang and Yao 2018, J. Banking & Finance):** Strong TSMOM in individual US stocks over 1927-2017. They report it is "not confined to particular sub-periods, firm sizes, formation and holding-period lengths" and that it survives standard risk factors. It depends on market state, information discreteness and sentiment. "Dual momentum" (TSMOM combined with XSMOM) earns more than TSMOM alone. — [Lancaster eprints](https://eprints.lancs.ac.uk/id/eprint/128366); [RePEc](https://econpapers.repec.org/RePEc:eee:jbfina:v:97:y:2018:i:c:p:283-296)
- A European stock study (1992-2019, master's thesis, lower authority) finds that single-stock TSMOM is largely explained by the cross-sectional momentum premium and is also exposed to momentum crashes. — [CBS thesis](https://research-api.cbs.dk/ws/portalfiles/portal/60699508/815971_Masters_thesis_final_Magnus_Bojesen.pdf)
- **Volatility-managed XSMOM (Barroso and Santa-Clara 2015, JFE):** They scale momentum by realized variance of daily returns over the prior 6 months, targeting constant risk. This "virtually eliminates crashes" and nearly doubles the Sharpe ratio over 1927-2011. One secondary summary puts it at 0.53 to 0.97. Turnover is about the same as plain momentum. — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:116:y:2015:i:1:p:111-120); [CFA Institute blog](https://blogs.cfainstitute.org/blog/2018/01/17/timing-the-market-momentum-and-beyond); [Swedroe/ETF.com](https://www.etf.com/node/94292.md)
- Barroso also reports that momentum's Sharpe is about 1.7 after low-risk months but only about 0.28 after high-risk months. — [CFA Institute blog](https://blogs.cfainstitute.org/blog/2018/01/17/timing-the-market-momentum-and-beyond)
- **Residual (idiosyncratic) momentum:** Ranking on firm-specific residual returns rather than raw returns gave a monthly Sharpe of 0.48, versus 0.25 for conventional momentum, over Dec 1925-Dec 2015. This is cross-sectional. — [CXO Advisory guide](https://www.cxoadvisory.com/guides/trend-momentum/)

### Inferences
- For one mega-cap, a "trend" rule is TSMOM on a single asset. With no diversification across assets, most of the risk-adjusted benefit MOP report (which comes from about 58 low-correlation markets plus vol scaling) is missing. Expect a single-stock trend rule's Sharpe to be far below the about 1.0 portfolio figure.
- Vol scaling is the most robust ingredient to carry over: size each stock to a target volatility, using something like 6-month realized vol as in Barroso and Santa-Clara. This matters a lot for TSLA and NVDA, whose volatility varies widely over time.
- Standard parameters from the literature: a 12-month lookback, often skipping the most recent month (12-1) for XSMOM, monthly rebalancing, and a 6-month realized-variance or EWMA vol estimate for scaling.

### Gaps
- I could not confirm from the fetched page MOP's exact per-instrument vol target or vol estimator. From memory these are about 40% annualized and an EWMA estimator, so verify against the paper's PDF.
- I found no peer-reviewed Sharpe or drawdown figures for TSMOM on any single named mega-cap stock.

## 2. Cross-sectional momentum in a tiny universe (~8 mega caps); momentum crashes

### Takeaway
Momentum profits do not disappear in large caps, unlike value. Momentum in a universe of only about 8 highly correlated tech names is untested in the academic literature, though. Small concentrated momentum portfolios show very large drawdowns, and momentum is prone to forecastable crashes in sharp market rebounds.

### Cited Findings
- **Israel and Moskowitz (2013, JFE):** Momentum profits "exhibit no reliable relation with size," unlike value, which is weak among the largest stocks. Long positions supply about half of momentum profits. Trading costs and institutional ownership barely explain the time variation. The sample is 86 years of US data plus international markets. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/The-Role-of-Shorting-Firm-Size-and-Time-on-Market-Anomalies); [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:108:y:2013:i:2:p:275-301)
- **Small-portfolio momentum (Siganos, UK 1988-2006, via Quantpedia):** 10 long and 10 short positions on a 12-month lookback with yearly rebalancing earned about 32% a year net of commissions, stamp duty, borrow costs and spreads. Max drawdown was **-88%**. Quantpedia's own out-of-sample backtest is slightly negative, and it rates its confidence "moderate." — [Quantpedia](https://quantpedia.com/strategies/momentum-effect-in-stocks-in-small-portfolios)
- **Momentum crashes (Daniel and Moskowitz 2016, JFE, 1927-2013):** Crashes are infrequent but persistent and partly forecastable. They happen in "panic states" after market declines when the market rebounds, because the short-loser leg behaves like a short call. Their dynamic strategy scales by forecast mean and variance, which roughly doubles the alpha and Sharpe of static momentum across equities, bonds, commodities and FX. — [NBER w20439](https://www.nber.org/papers/w20439); [Chicago Booth Review](https://www.chicagobooth.edu/review/understanding-momentum-crashes)
- Original momentum suffered extreme monthly losses of about 77%, which risk-managed versions sharply reduce (Dierkes and Krupski). — [Alpha Architect](https://alphaarchitect.com/risk-of-momentum-crashes/)
- From 1994-2024, the momentum factor averaged **-0.73% a month** in or right after volatility-spike months, versus +0.54% in other months. — [Alpha Architect](https://alphaarchitect.com/momentum-investing-struggling/)
- **Recent regime:** Momentum was the top US factor in 2024. Since 1990, in 7 of 11 prior years when momentum led, its excess return the next year was negative. — [SSGA](https://ssga.com/us/en/individual/insights/what-drove-momentums-strong-2024-and-what-it-could-mean-for-2025). Momentum returned 0.77% in Q4 2025 versus 8.34% for value. — [Morningstar](https://global.morningstar.com/en-ca/markets/are-we-due-us-stock-market-rotation). After a crash (the worst 5% of rolling 3-month returns), momentum rebounded over the next 12 months, though it usually did not recoup its losses fully. — [SSGA March 2025](https://www.ssga.com/us/en/individual/insights/systematic-active-monthly-march-2025)
- Quantpedia notes the "Magnificent Seven" episode of concentration and says capturing such gains systematically "has proven challenging." Its tech-leadership timing study makes money mainly while a tech bubble is inflating or bursting. — [Quantpedia: Tech sector leadership](https://quantpedia.com/can-technology-sector-leadership-be-systematically-exploited/?a=6080); [Quantpedia Mag-7 tag](https://quantpedia.com/tag/magnificent-7/)
- In a QuantConnect forum backtest of a dollar-volume filter concentrated in mega caps (Sep 2021-Sep 2026), the Sharpe was 0.525. This is a community post, so it is anecdotal. — [QuantConnect forum](https://www.quantconnect.com/forum/discussion/21382)

### Inferences
- With about 8 names, "top-k minus bottom-k" momentum is really a sector-internal relative bet between highly correlated stocks. It has little diversification and its results will hinge on a handful of episodes (for example NVDA in 2023-24, or META in 2022). Any backtest has very few independent bets and is heavily exposed to selection bias, since these 7 were chosen because they won.
- A long-only, rank-and-tilt or TSMOM-gated version (hold a name only if its own 12-1 return is above zero) is more defensible than long/short. It keeps the "long leg is about half the profit" finding and avoids the short-call crash mechanics of shorting losers.
- Crash protection is worth adding: volatility scaling, or cutting exposure after a market drawdown or volatility spike, per Daniel and Moskowitz and Barroso and Santa-Clara.

### Gaps
- I found no peer-reviewed or reputable practitioner study of XSMOM restricted to about 8 mega caps. An S&P 100 momentum report turned up (k-dense.ai, July 2026) that reportedly finds insignificant CAPM alpha and emphasizes survivorship bias. Its PDF could not be parsed and it looks AI-generated, so I did not use it.

## 3. Intraday / short-term momentum and post-earnings drift (PEAD) on mega caps

### Takeaway
Intraday momentum (the first half-hour return predicting the last half-hour) is documented robustly at the market or ETF level. At the single-stock level the evidence is mixed: recent work finds cross-sectional end-of-day reversal. PEAD has essentially disappeared for large stocks since the mid-2000s, so it is unlikely to be exploitable on mega caps.

### Cited Findings
- **Gao, Han, Li and Zhou (2018, JFE):** For SPY in 1993-2013, the first half-hour return predicts the last half-hour return with an R² of 1.6%, or 2.6% when the 12th half-hour is added and 1.2% out of sample. The effect is stronger in high volatility, high volume and recessions, and holds for 10 other liquid ETFs. — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414); [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)
- **Zarattini, Aziz and Barbon (2024, SFI WP):** A "Noise Area" intraday breakout on SPY uses a band from the open based on the average intraday move over the past 14 days, with trades only at HH:00 and HH:30. They report a 19.6% annual return and a **Sharpe of 1.33 net of costs** over 2007-early 2024. — [SFI](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy). CXO Advisory notes a -25% max drawdown and that the result is in-sample. — [CXO Advisory](https://www.cxoadvisory.com/?p=45565). An independent QuantConnect replication got a **Sharpe of 0.60**, a 13.4% CAGR and a 25.5% drawdown. — [QuantConnect backtest](https://quantconnect.com/terminal/cache/embedded_backtest_32f62726550888da5f2a06694ac37930.html)
- **Single stocks:** An April 2025 working paper finds early-day returns of individual stocks *negatively* predict their last-half-hour return in the cross-section ("end-of-day reversal"). This is unlike market-level momentum. — [Notre Dame, Da et al. WP](https://www3.nd.edu/~zda/EOD.pdf). Beckmeyer and Moerke (EFMA 2021) argue stock-level intraday momentum is mostly a common market component, linked to hedging by option market makers. — [EFMA 2021 paper](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2021-Leeds/papers/EFMA%202021_stage-2049_question-Full%20Paper_id-237.pdf). Heston, Korajczyk and Sadka (2008) find return continuation at half-hour intervals is strongest in the first and last half-hours. — [NBER conf. paper](https://conference.nber.org/confer/2008/mms08/korajczyk.pdf)
- **PEAD (Martineau 2022, Critical Finance Review, "Rest in Peace PEAD"):** Prices now fully reflect earnings surprises on the announcement day. Drift is effectively nonexistent for large stocks since about 2006 and has only recently disappeared in microcaps. — [Now Publishers](https://nowpublishers.com/article/Details/CFR-0122); [IDEAS](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html). Other work attributes the decline to arbitrage and liquidity or to falling earnings persistence (Zhao 2022 WP). — [Columbia CEASA PDF](https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf)

### Inferences
- The case for intraday trend is strongest at the index level (SPY or QQQ, or using SPY's first half-hour as a market signal) rather than on single mega-cap stocks. For TSLA or NVDA alone, the cross-sectional evidence points toward reversal near the close. Any single-stock intraday trend edge would have to be validated out of sample by the user.
- Classic SUE-based PEAD on mega caps should be treated as dead. Whatever earnings-related edge remains is more likely in event volatility (options) than in drift.

### Gaps
- I found no study of intraday momentum or PEAD specifically on the 7 named mega caps.
- I did not verify a secondary claim that the Zarattini strategy reaches a Sharpe of 3.5 when VIX is above 40.

## 4. Reported Sharpe ratios and drawdowns, after costs

### Takeaway
Momentum survives trading costs for large, patient institutions, and costs on mega caps are tiny. Realistic Sharpe ratios for well-built momentum are about 0.5-1.0 for diversified portfolios. Concentrated or single-name versions carry very large drawdowns, -25% to -88% in the cases found, and in-sample Sharpes should be roughly halved when replicated.

### Cited Findings
- **Frazzini, Israel and Moskowitz (AQR live-trade data):** Momentum is "robust, implementable, and sizeable" after costs, with about 4.34% a year net at a $3.7B fund size and a break-even size of about $52B. The 2018 follow-up uses $1.7T of executions and finds real costs an order of magnitude below earlier estimates, with S&P 500 trading costs of about 4.81 bps a year. — [Alpha Architect](https://alphaarchitect.com/surprise-the-size-value-and-momentum-anomalies-survive-after-trading-costs/); [Alpha Architect, 2018 paper](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/)
- **Contrary:** Lesmond, Schill and Zhou (2004) find no net momentum return using TAQ data. Patton and Weller (2018) find typical mutual funds earn no momentum returns after implementation costs. Korajczyk and Sadka put momentum capacity at about $5B. — [Alpha Architect summary](https://alphaarchitect.com/the-best-research-paper-ever-written-on-trading-costs/); [Swedroe/ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-trading-cost-truths)
- **Summary of reported figures:**
  - Plain XSMOM Sharpe is about 0.53, versus about 0.97 with vol management, over 1927-2011, gross of costs. — [Swedroe/ETF.com](https://www.etf.com/node/94292.md)
  - Daniel and Moskowitz's dynamic momentum roughly doubles the Sharpe. — [NBER](https://www.nber.org/papers/w20439)
  - Diversified futures TSMOM Sharpe is about 1.0 (secondary source). — [Menon Lab](https://themenonlab.blog/blog/time-series-momentum-hedge-fund-strategy-explained)
  - Factor TSMOM Sharpe is 0.84, across 65 factors. — [AQR Factor Momentum Everywhere](https://www.Aqr.Com/-/media/AQR/Documents/Insights/Journal-Article/Factor-Momentum-Everywhere-JPM-Quant-19.pdf?sc_lang=en)
  - SPY intraday momentum: Sharpe 1.33 in-sample net, versus 0.60 in independent replication, with drawdowns of about -25%. — [SFI](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy); [QuantConnect](https://quantconnect.com/terminal/cache/embedded_backtest_32f62726550888da5f2a06694ac37930.html)
  - Small 20-stock momentum portfolio: -88% max drawdown. — [Quantpedia](https://quantpedia.com/strategies/momentum-effect-in-stocks-in-small-portfolios)
  - Unmanaged momentum's worst month was about -77%. — [Alpha Architect](https://alphaarchitect.com/risk-of-momentum-crashes/)

### Inferences
- For monthly-rebalanced trend or momentum on mega caps, commissions and spreads are negligible (a few bps per trade). The real "costs" are taxes on short-term gains, borrow costs if short, and slippage around gaps (overnight earnings moves in TSLA, NVDA and META).
- A defensible prior for a single-name or 8-name vol-scaled trend strategy is a Sharpe in the 0.3-0.7 range, with drawdowns of 30-50% possible. This is an inference only, from diversification loss versus the figures above; no study confirms it for this universe.

### Gaps
- I found no after-cost Sharpe or drawdown figures for momentum or trend on the named mega caps from any reputable source.
- I could not read the AQR Factor Momentum and Lim-Wang-Yao full texts, so per-stock TSMOM Sharpe figures for individual stocks are missing.
