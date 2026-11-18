# Mean Reversion & Statistical Arbitrage / Pairs Trading in Mega-Cap Tech and TSLA

Scope note: The published academic evidence is almost all broad-universe (S&P 500, CRSP large caps). I found no peer-reviewed study that tests mega-cap tech pairs like MSFT/GOOGL, NVDA/AMD or TSLA/EV peers specifically. The mega-cap conclusions below are inferences from large-cap results.

## 1. Does short-horizon (1-5 day) reversal work on mega caps after costs? (RSI/Bollinger-style vs academic evidence)

### Takeaway
Raw 1-week and 1-month reversal on large caps is marginal to negative after realistic costs, and the classic effect has largely faded since the 2000s. Residualized versions (reversal measured after stripping out factor or industry moves) hold up better, including among large caps. Retail RSI(2)-style index rules have only blog-grade evidence, and that evidence is mixed on post-2010 decay.

### Cited Findings
- Groot, Huij & Zhou (1990–2009): costs mostly destroy reversal profits because of small-cap trading. "Limiting the stock universe to large cap stocks significantly reduces trading costs." — [Quantpedia: Short-term reversal](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Universe size matters a lot in the Quantpedia replication (Nomura cost model, weekly/5-day rebalance):
  - 100 largest US stocks: +29.0 bp/week net, about 16% annual return, about 15% volatility, Sharpe about 1.09.
  - 500 stocks: +10.6 bp/week.
  - 1,500 stocks: −31.4 bp/week.
  - The sample ends in 2009. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Blitz, van der Grient & Honarvar: the classic reversal effect has weakened and "largely disappeared in most regions." A version that neutralizes industry and factor momentum has worked again. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Blitz, Huij, Lansdorp & Verbeek, "Short-term residual reversal" (J. Financial Markets 16(3), 2013): residual reversal is statistically and economically significant net of trading costs, even restricted to large caps after 1990. — [EconPapers](https://econpapers.repec.org/RePEc:eee:finmar:v:16:y:2013:i:3:p:477-504); [Robeco summary](https://robeco.com/en-int/insights/2011/11/short-term-residual-reversal)
- A commentary on the 2011 working paper gives the large-cap sample as 1990–2008 and a breakeven round-trip friction of about 0.56% for the full-sample monthly strategy. These are working-paper numbers, not the published ones. — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/purified-short-term-stock-reversal/)
- Frazzini, Israel & Moskowitz (live institutional trade data, 1998–2011): short-term reversal is the factor most constrained by trading costs. It does not survive costs at fund sizes above about $9B in the US. — [NBER paper](https://conference.nber.org/conf_papers/f68262/f68262.pdf); [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Medhat & Schmeling: short-term reversal comes from low-turnover stocks. Among large caps, plain reversal earned about 0.84%/month gross, while the strategy's estimated costs were about 1.94%/month (search-summary figures, not verified against the paper). — [Alpha Architect](https://alphaarchitect.com/short-term-momentum/)
- Nagel ("Evaporating Liquidity"): reversal returns are payment for providing liquidity. They can be predicted from VIX and spike during market stress. Reversal behaves like a short-volatility trade. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Miwa: intraday returns reverse the following week but overnight returns do not. The effect is stronger in illiquid names and volatile markets. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Practitioner RSI(2) evidence (not peer-reviewed, rule variants differ, mostly without costs):
  - SPY rules (buy below 10, sell above 80): about 9% CAGR while invested about 28% of the time, 1993 onward, max drawdown 34% (Quantified Strategies, as summarized in search results). — [Quantified Strategies substack](https://quantifiedstrategies.substack.com/p/larry-connors-r3-strategy-it-still-ebb)
  - QQQ variant: 10.7% CAGR since 2000. — same source
  - One S&P 500 backtest (1990–2024) says the edge continued after the book was published. — [backtest.substack](https://backtest.substack.com/p/the-2-period-rsi-a-simple-system)
  - A forum user reports a "spectacular" drop-off after about 2010 for a stock-level RSI(2) variant that adds a new-lows filter. — [thechartist forum](https://thechartist.com.au/forums/topic/trading-system-broken/page/2)

### Inferences
- Mega caps are the cheapest stocks to trade, so if reversal survives costs anywhere, it is in the top-100 bucket. The top-100 net result ends in 2009, though, and later work says the raw effect has faded.
- For single names like TSLA and NVDA, a raw price-reversal signal mixes idiosyncratic noise with factor and sector momentum. That momentum hurts plain reversal and is exactly what residual reversal removes. Measure reversal on residuals versus QQQ or XLK, not on raw returns.
- Reversal pays most after volatility spikes. Expect clustered P&L and large drawdowns in crashes, so it needs a VIX or volatility-aware sizing rule.
- RSI and Bollinger rules on the index ETF (QQQ) are better documented than RSI rules on individual mega caps. None of that evidence reports a clean before-and-after-2010 split with costs.

### Gaps
- No peer-reviewed study of 1–5 day reversal restricted to the roughly 10 mega-cap tech names or TSLA after 2010.
- No cost-inclusive, out-of-sample RSI(2) or Bollinger study on individual mega caps. Blog backtests vary by rule and usually ignore slippage.
- The Medhat & Schmeling large-cap net figure was not confirmed against the original paper.

## 2. Cointegration tests, Kalman hedge ratios, half-life: how stable are mega-cap pairs?

### Takeaway
Cointegration between individual US large-cap stocks is not persistent. Pairs that test cointegrated in one window seldom test cointegrated again later. Distance and cointegration pairs profits have decayed sharply and are largely gone after costs. A Kalman-filter hedge ratio and half-life filters are standard practitioner tools, but they do not fix the underlying non-persistence.

### Cited Findings
- Clegg (2014): previously cointegrated S&P 500 pairs re-cointegrated only 4.5–7.2% of the time (2002–2012, across multiple tests). The evidence does not support cointegration pairs trading on liquid US stocks. ETFs or other markets may work better. — [CXO Advisory summary](https://www.cxoadvisory.com/technical-trading/essential-assumption-of-pairs-trading-wrong)
- Clegg & Krauss, "Pairs trading with partial cointegration": equity spreads are hit by a steady stream of permanent shocks. Classical distance and cointegration variants disappoint on a survivor-bias-free S&P 500 sample, and partial cointegration does better. — [FAU working paper](https://www.iwf.rw.fau.de/files/2016/05/05-2016.pdf)
- Palomar (textbook): pair spreads are "typically affected by a steady stream of permanent shocks" that erode cointegration. — [Portfolio Optimization book, 15.4](https://bookdown.org/palomar/portfoliooptimizationbook/15.4-discovering-pairs.html)
- Farago & Hjalmarsson: cointegration is "not a likely explanation" for the profitability of pairs trading on ordinary stock pairs. — [Quantpedia](https://quantpedia.com/is-equity-pairs-trading-profitable-due-to-cointegration/)
- Do & Faff (2010), distance method 1962–2009: mean monthly excess return fell from about 1.24% (1962–88) to about 0.33% (2003–09). They attribute this mainly to more pairs that never converge. — [Quantpedia](https://quantpedia.com/?p=585)
- Do & Faff (2012): once commissions, market impact and short fees are included, the Gatev et al. baseline becomes largely unprofitable. — [arXiv 2010.01157 lit review](https://arxiv.org/pdf/2010.01157)
- Krauss (2017, J. Economic Surveys 31(2)) survey: the distance baseline is largely unprofitable after costs. — [EconPapers](https://econpapers.repec.org/RePEc:bla:jecsur:v:31:y:2017:i:2:p:513-545); [WP version](https://www.iwf.rw.fau.de/files/2016/03/09-2015.pdf)
- Contrary view: Rad, Low & Faff (2016) found the distance, cointegration and copula methods all profitable over 1962–2014, with distance slightly best after costs. Profits were much smaller in recent years. — [search summary of the review literature](https://arxiv.org/pdf/2010.01157)
- Engle-Granger pitfalls:
  - Use EG critical values (5% about −3.34 for two series), not standard ADF tables. Standard ADF tables over-reject and "find" false cointegration. — [QuantVault](https://quantvault.org/problem-1724-cointegration-engle-granger-procedure-and-error-correction.html)
  - EG assumes a single cointegrating vector. Johansen is preferred for 3 or more series (for example TSLA vs a basket of EV peers). It returns the vectors plus trace and eigenvalue statistics. — [Hudson & Thames ArbitrageLab docs](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/cointegration_approach/cointegration_tests.html)
- Half-life:
  - Under an OU process (Ornstein-Uhlenbeck, the standard mean-reversion model), half-life = ln(2)/κ, where κ is the speed at which the spread pulls back. — [LuxAlgo](https://www.luxalgo.com/library/concept/pairs-trading-stack.md)
  - A λ near zero means a very long half-life, and the trade becomes unprofitable. — [Hudson & Thames intro to cointegration](https://hudsonthames.org/an-introduction-to-cointegration/)
  - Practitioner rule of thumb: a 5–60 day half-life is tradable. At about 200 days, costs and margin eat the edge. — [LuxAlgo](https://www.luxalgo.com/library/concept/pairs-trading-stack.md)
- Kalman filter:
  - ArbitrageLab's KalmanFilterStrategy follows Chan's *Algorithmic Trading* (2013). The hedge ratio is a hidden state updated at each observation. Defaults: observation covariance 0.001, transition covariance 0.0001, entry and exit set on forecast-error standard deviations. — [ArbitrageLab Kalman docs](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/other_approaches/kalman_filter.html)
  - A static OLS hedge ratio over- or under-hedges when the relationship drifts. Chan's examples are ETF pairs such as EWA/EWC and Treasury ETFs, not single stocks. — [Letian Wang blog](https://letianzj.github.io/kalman-filter-pairs-trading.html); [QuantStart](https://www.quantstart.com/articles/kalman-filter-based-pairs-trading-strategy-in-qstrader)
  - Recommended practice is rolling-window re-testing plus ranking candidates by half-life, spread volatility and test stability. — [LuxAlgo](https://www.luxalgo.com/library/concept/pairs-trading-stack.md)

### Inferences
- Mega-cap tech pairs are a worst case for cointegration. Each name is driven by distinct, very large idiosyncratic narratives (cloud vs search ads for MSFT/GOOGL, datacenter AI for NVDA/AMD, a single CEO and EV/robotaxi story for TSLA). Those narratives produce exactly the permanent shocks that break cointegration.
- A Kalman hedge ratio makes the spread look stationary in-sample by continuously absorbing drift. That can hide a broken relationship. Monitor the filtered beta's path: a trending beta is a red flag, not a feature.
- A small universe of about 10 names means few candidate pairs. Fewer pairs means less of the diversification the academic portfolios (top-20 pairs from about 500 stocks) relied on.
- Multiple testing: screening every mega-cap pair combination and keeping the one that passes will over-select false cointegration, especially with ADF instead of EG critical values.

### Gaps
- No published Engle-Granger or Johansen results, half-life estimates or Kalman studies for MSFT/GOOGL, NVDA/AMD, AAPL/MSFT, or TSLA vs EV peers or QQQ. A pairtradinglab page runs Engle-Granger on TSLA/SPY but is just a no-cost backtest tool. — [pairtradinglab](https://www.pairtradinglab.com/analyses/Z6E-1X6Qic2rWmu2)
- TSLA vs EV peers (NIO, RIVN): only opinion pieces (fundamental long-TSLA/short-RIVN or NIO theses), no statistical tests. — [Seeking Alpha](https://seekingalpha.com/article/4679405-why-long-tesla-and-short-rivian-makes-sense); [TradingView idea](https://in.tradingview.com/chart/TSLA/Pjo93Soq-Pair-trade-Long-TSLA-short-NIO)
- Formal structural-break cointegration tests (Gregory-Hansen, Bai-Perron) applied to these pairs were not found. The project would need to run them itself.

## 3. Avellaneda-Lee style residual stat arb vs ETF (QQQ/XLK); decay of returns over time

### Takeaway
Avellaneda & Lee (2010) model each stock's residual versus sector ETFs (or PCA factors) as an OU process and trade s-score deviations. Sharpe ratios were about 1.1–1.44 over 1997–2007, but performance clearly degraded after about 2002. Adding volume information partly restored it. Modern deep-learning residual stat arb reports high Sharpe ratios, but at large, diversified scale, not on a handful of tech names.

### Cited Findings
- Setup: residuals after removing systematic factors are modeled as mean-reverting (OU), producing contrarian signals. Factors come either from PCA or from regression on sector ETFs. Published in Quantitative Finance 10(7):761–782 (2010). — [IDEAS/RePEc](https://ideas.repec.org/a/taf/quantf/v10y2010i7p761-782.html); [NYU abstract](https://cims.nyu.edu/ams/abstracts/avellaneda.html)
- Performance and decay:
  - ETF-based strategies: Sharpe 1.1 over 1997–2007, with degradation since 2002.
  - PCA strategies: Sharpe only 0.9 over 2003–2007, much weaker than before 2003.
  - ETF strategies using trading-time volume information reached Sharpe 1.51 over 2003–2007.
  - The paper ties strategy performance to the market cycle.
  - (Search-summarized from the abstract.) — [Avellaneda & Lee PDF](https://www.math.nyu.edu/faculty/avellane/AvellanedaLeeStatArb20090616.pdf); [IDEAS](https://ideas.repec.org/a/taf/quantf/v10y2010i7p761-782.html)
- Guijarro-Ordonez, Pelger & Zanotti, "Deep Learning Statistical Arbitrage" (arXiv 2106.04028, rev. Oct 2022): residuals from conditional latent factors, signals from a convolutional transformer, and a constrained risk-adjusted policy. They report consistently high out-of-sample Sharpe ratios that beat benchmarks, including Avellaneda-Lee-type ones, and say the results survive trading frictions. Slides cite about 20% annual return at under 6% volatility. — [arXiv](https://arxiv.org/abs/2106.04028v2); [CDAR slides](https://cdar.berkeley.edu/sites/default/files/slides_deep_learning_statistical_arbitrage.pdf)
- Residual (factor-neutralized) reversal survives costs among large caps, where raw reversal does not. This supports the residual-versus-ETF approach over raw price mean reversion. — [EconPapers, Blitz et al. 2013](https://econpapers.repec.org/RePEc:eee:finmar:v:16:y:2013:i:3:p:477-504)

### Inferences
- Applying Avellaneda-Lee to TSLA or NVDA versus QQQ or XLK has a structural problem. These names are a large share of QQQ and XLK (NVDA, MSFT and AAPL dominate XLK). Regressing a stock on an ETF that the stock itself drives shrinks the residual and biases beta. Consider excluding the stock from the benchmark, or using an equal-weight or ex-mega-cap tech basket.
- The paper's edge came from diversifying across hundreds of residuals. A strategy on about 10 names loses most of that, and the Sharpe ratio should be expected to be far lower. Each name's residual carries large earnings and news jumps.
- The decay after 2002 is consistent with crowding (which also showed in the August 2007 quant unwind) and with the reversal and pairs decay in sections 1–2. A reasonable prior for a simple 2026 version is a much lower Sharpe ratio than the published figures.

### Gaps
- I could not extract Avellaneda-Lee's exact parameters (s-score entry and exit thresholds, κ or half-life filter, 60-day window, cost assumption, ETF list) because PDF text extraction failed in this environment. From memory, the paper uses a 60-day estimation window, entry near |s| > 1.25, a fast-mean-reversion filter (half-life under about half the window), and a 5 bp one-way cost. These are unverified and must be checked against the PDF before use.
- No published out-of-sample replication of Avellaneda-Lee after 2010 was found in this pass, and none specific to QQQ or XLK residuals.
- I did not get the exact Sharpe tables or post-2016 subperiod results from the deep-learning stat-arb paper.

## 4. Pitfalls: regime breaks (e.g., the NVDA AI boom breaking pairs)

### Takeaway
The biggest risk for mega-cap pairs and residual strategies is a permanent, story-driven divergence. NVDA vs AMD in 2023 is the canonical example. The literature's finding of non-persistent cointegration and growing non-convergence matches it directly. Reversal and stat-arb strategies also lose money in liquidity crises and pay off afterward.

### Cited Findings
- NVDA rose 214% in 2023 (to late July) vs AMD's 72%. — [Motley Fool, Jul 2023](https://www.fool.com/investing/2023/07/29/better-ai-chip-stock-amd-vs-nvidia)
- That divergence was attributed to AMD being "late to the AI party." — [Benzinga, Oct 2023](https://benzinga.com/markets/equities/23/10/35161048/in-nvda-vs-amd-one-stock-has-emerged-clear-winner-but-what-can-you-expect-next-in-chipmakers-ai-)
- More recently, AMD and NVDA moved in opposite directions within a single week. This shows the AI-chip complex does not move in lockstep (anecdotal, one week). — [Gotrade](https://www.heygotrade.com/en/news/ai-chip-semiconductor-stocks-divergence-amd-nvidia-broadcom/)
- Do & Faff attribute the decay in pairs profits mainly to a rising share of pairs that never converge. — [search summary](https://arxiv.org/pdf/2010.01157); [Quantpedia](https://quantpedia.com/?p=585)
- Clegg: only 4.5–7.2% of previously cointegrated S&P 500 pairs re-cointegrate (2002–2012). — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/essential-assumption-of-pairs-trading-wrong)
- Spreads are hit by a steady stream of permanent shocks. — [Palomar](https://bookdown.org/palomar/portfoliooptimizationbook/15.4-discovering-pairs.html); [Clegg & Krauss](https://www.iwf.rw.fau.de/files/2016/05/05-2016.pdf)
- Reversal returns are predictable from VIX and spike in turmoil. They behave like short volatility and need strict risk control in volatile periods. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Avellaneda-Lee performance is linked to the market cycle. — [IDEAS](https://ideas.repec.org/a/taf/quantf/v10y2010i7p761-782.html)
- Pairs and distance strategies did well in turbulent markets (Do & Faff 2012), but that is before costs. — [arXiv 2010.01157](https://arxiv.org/pdf/2010.01157)

### Inferences
- A fixed-hedge NVDA/AMD spread traded from early 2023 would have kept signaling "short NVDA, long AMD" as the spread widened. That is unbounded loss without a stop. Concrete guards:
  - a time stop of about 2–3× the half-life;
  - a z-score stop-loss;
  - a rolling re-test that drops the pair when the EG or Johansen p-value deteriorates or the half-life lengthens;
  - a ban on holding through earnings.
- TSLA is a special case. Its idiosyncratic volatility, single-CEO news flow and the lack of a clean EV peer (NIO and RIVN are far smaller and have different fundamentals) make TSLA/peer cointegration implausible. TSLA residual versus QQQ is more tractable but jump-prone.
- Earnings, index rebalances (QQQ and XLK capping rules) and AI capex news create the jumps that dominate residuals. Filter or flatten around those dates.
- Backtests on today's mega caps carry survivorship and look-ahead bias, because you are choosing names known to have become mega caps.

### Gaps
- No formal study documenting a cointegration or structural break date for NVDA/AMD, MSFT/GOOGL or TSLA/peers. This has to be tested in-house (rolling EG or Johansen, CUSUM or Gregory-Hansen).
- No quantified loss figures from real stat-arb funds tied to the 2023–2024 AI rally were found.
