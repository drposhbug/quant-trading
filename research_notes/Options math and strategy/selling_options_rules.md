# Option-Selling Strategies and Management Rules: Evidence vs Folklore (US mega-cap tech and indices, as of Nov 2026)

Scope note: 17 tool calls; many primary PDFs (Cboe factsheets, Bondarenko 2016/2019, the Cboe 2016 options-selling white paper) could not be parsed directly, so several numbers come from secondary summaries (CXO Advisory, Cboe press releases, Cboe Insights). Where a number is secondhand it is flagged.

## Q1. Earnings short-vol on single stocks (straddles, iron flies, iron condors): measured returns after costs, implied vs realized moves, tail-loss frequency

### Takeaway
The best peer-reviewed evidence points the *opposite* way from the "IV crush is free money" folklore: long ATM straddles bought ~3 days before earnings earn significantly positive returns (Gao, Xing & Zhang, JFQA 2018), i.e. on average the short side of the pre-earnings window loses. No peer-reviewed, cost-inclusive study of *short* earnings straddles/iron flies on mega-caps was found. Mega-cap-specific practitioner data (NVDA) show implied moves exceed realized moves most of the time, but the average implied and average realized move are nearly equal, so the high win rate is paid for by infrequent large losses.

### Cited Findings
- Gao, Xing & Zhang (2018), "Anticipating Uncertainty: Straddles around Earnings Announcements," JFQA 53(6): average ATM straddles held from 3 days before the earnings announcement to the announcement date return a highly significant +3.34%; authors conclude the market underestimates earnings-day uncertainty and the returns are unlikely to be compensation for market-volatility or jump risk factors. — [Cambridge/JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/anticipating-uncertainty-straddles-around-earnings-announcements/7B34877AD5E06304BA3C55FBA3219FDD); [RePEc](https://econpapers.repec.org/RePEc:cup:jfinqa:v:53:y:2018:i:06:p:2587-2617_00)
- Same paper: straddle returns are larger for smaller firms, higher-volatility/higher-kurtosis firms, firms with more volatile past surprises, and those with lower volume / higher transaction costs; straddles outside the event window earn significantly negative returns (the usual volatility risk premium). — [Tsinghua PBCSF working-paper PDF](https://www.pbcsf.tsinghua.edu.cn/__local/B/7B/EF/9C90E5DE82928B64858EFBA685C_E7B3C45C_4183B.pdf?e=.pdf); [BSIC summary](https://bsic.it/straddling-outside-and-into-earnings/)
- BSIC replication/summary: GXZ straddles used 10-60 DTE options (avg ~38 DTE), filters stock >$5 and option >$0.125, no explicit bid-ask cost modelling; the effect is weakest for very liquid, heavily covered names like Apple, and liquidity limits capacity. — [BSIC](https://bsic.it/straddling-outside-and-into-earnings/)
- Background on the non-earnings volatility risk premium cited in the same summary: Coval & Shumway (2001) ATM SPX straddles lose ~3.15%/week; Cremers, Halling & Weinbaum (2015, JF) estimate annualized jump-risk premium ~-40.89% and volatility premium ~-9.56% for long straddles. — [BSIC](https://bsic.it/straddling-outside-and-into-earnings/)
- NVDA (ORATS, Feb 24 2026): implied earnings move 5.6% vs a 12-quarter average implied move of 7.6%; realized post-earnings moves "clustered near" the 7.6% level. An earlier ORATS piece (Aug 2025): 12-quarter average implied 7.7% vs average actual 7.6% — "remarkably accurate on average." No strategy backtest published in either. — [ORATS 2026](https://orats.com/blog/is-nvda-earnings-volatility-underpriced); [ORATS](https://orats.com/blog/nvidia-earnings-options-market-expectations-vs-reality)
- NVDA beat rate: implied move exceeded actual in 14 of the last 20 reports (attributed to Cboe LiveVol, but only found on mirror/spam domains — UNVERIFIED). Earnings Watcher: NVDA actual beat implied ~25% of the time; in a ~16-report sample only 5 beats, but beats averaged ~7.1 points *over* the implied move. AAPL beat its implied move 7 of 16 times (44%), with ~±4.9% average 10-year earnings-day move. — [Earnings Watcher wiki](https://earnings-watcher.com/wiki/earnings-expected-moves); [Earnings Watcher on Medium](https://medium.com/@EarningsWatcher/how-were-framing-nvda-earnings-long-vol-lottos-vs-defined-risk-short-vol-b948394b0fea); [mirror of LiveVol claim, low quality](https://bvwd.ca.gov/expert-time/Nvidia-PostEarnings-Volatility-Options-Pricing-Overestimated-Swings-in-14-of-Last-20-Quarters-19-1570)
- Practitioner illustration of the tail mechanics: if a TSLA straddle prices a $15 move and the stock gaps $40, crush saves ~$5 but the directional loss costs ~$25. Multi-leg structures carry substantial commissions/spread costs. — [Moomoo education](https://www.moomoo.com/us/learn/options-earnings-series-3-exploring-common-two-legged-option-strategies-for-earnings-season); [TD Ameritrade Ticker Tape](https://tickertape.tdameritrade.com/trading/option-straddle-strategy-earnings-announcements-15528)

### Inferences
- "Implied > realized most of the time" (win rate ~55-75% for mega-caps) and "short earnings vol has positive expectancy" are different claims. NVDA data (avg implied ≈ avg realized, beats ~7 pts over implied) suggest near-zero gross edge for a short straddle; after 4-leg iron-fly spreads/commissions, expectancy is plausibly negative.
- The GXZ result is entry-timing-specific (long from T-3 to announcement captures the pre-announcement IV *rise*). A short entered the afternoon before the report captures only the crush-vs-gap; GXZ does not directly measure that window, so it argues against but does not refute it.
- The GXZ effect is weakest in the most liquid names (Apple), which is exactly the mega-cap universe — consistent with mega-cap earnings options being roughly fairly priced, i.e. no robust edge either way.
- Tail frequency for mega-caps, roughly: actual > implied in ~25-45% of reports; when it happens the overshoot can be ~1x the implied move (NVDA), so an iron fly's max loss is hit in a meaningful minority of events.

### Gaps
- No peer-reviewed or independently audited, cost-inclusive backtest of *short* pre-announcement straddles / iron flies on mega-caps was found. ORATS/OptionAlpha/tastylive earnings backtest numbers were not retrieved (none appeared with stats in searches).
- Euan Sinclair's specific published numbers on earnings vol (e.g., in "Positional Option Trading") were not located online in this session.
- Systematic implied-vs-actual tables for AAPL/MSFT/AMZN/GOOGL/META/TSLA from a primary data vendor (Cboe LiveVol, ORATS) were not retrieved; the 14/20 NVDA figure could not be traced to Cboe directly.

## Q2. Cboe benchmark indices (PUT, BXM, BXMD, CNDR, BFLY) vs S&P 500, incl. 2008, 2020, 2022, 2025-26

### Takeaway
Over long samples, index put-writing (PUT) roughly matched the S&P 500 return with ~2/3 the volatility (Sharpe ~0.67 vs ~0.47, 1986-2015, gross), and shallower but still large drawdowns (~-33% vs ~-51%). Over the bull-heavy 2006-2015 and later periods, PUT/BXM lagged the index in raw return; BXM returned 8.9% in 2025 (S&P 500 TR ~18% — not verified in this session). All index figures are gross of costs and investable ETFs tracking them have underperformed the indices.

### Cited Findings
- Bondarenko (2016), PUT vs S&P 500 TR: 1986-2015 annual compound return PUT 10.1% vs index 9.8%; volatility 10.1% vs 15.3%; Sharpe 0.67 vs 0.47. 2006-2015: PUT 6.6%, WPUT 5.6%, index 7.1%; vol 11.5% / 9.8% / 15.1%; Sharpe 0.52 / 0.50 / 0.46; max drawdown -33% / -24% / -51%. All gross; pre-2007 PUT history is back-constructed. — [CXO Advisory summary](https://www.cxoadvisory.com/equity-options/performance-of-cboe-putwrite-indexes); [Cboe Insights on the white paper](https://www.cboe.com/insights/posts/white-paper-shows-volatility-risk-premium-facilitated-higher-risk-adjusted-returns-for-put-index); [Indexology blog](https://www.indexologyblog.com/2016/02/18/paper-by-professor-bondarenko-has-intriguing-new-analysis-of-put-and-wput-indexes/)
- Bondarenko (2019) "Historical Performance of Put-Writing Strategies" extends to mid-1986; a summary reports PUT max drawdown -32.7% vs -38.9% for the S&P 500 (period unclear — UNVERIFIED secondhand). — [Elite Trader thread](https://www.elitetrader.com/et/threads/historical-performance-of-put-writing-strategies.374547)
- CXO: ETPs tracking BXM substantially underperform BXM; put-write ETFs underperformed SPY. — [CXO Advisory](https://www.cxoadvisory.com/equity-options/performance-of-cboe-putwrite-indexes)
- BXM calendar returns: 2025 +8.91%, 2024 +20.12%, 2022 -11.37% (YCharts). — [YCharts BXM](https://ycharts.com/indices/^BXM)
- Cboe 2016 study (BXM, PUT, BFLY, BXMD, CMBO, CNDR): CNDR had the lowest annualized std dev (7.23%), PUT 10.16%; months with losses worse than -6%: CNDR 10, BFLY 2, PUT 15. — [Cboe IR press release](https://ir.cboe.com/news/news-details/2016/Study-Analyzes-Performance-of-CBOE-SP-500-SPX-Options-Selling-Indexes-02-23-2016/default.aspx); [Hedgeweek](https://www.hedgeweek.com/new-study-analyses-performance-cboe-sp-500-options-selling-indexes/)
- Cboe (2021, ~35 years): worst peak-to-trough drawdown CNDR -19%, BFLY -47.1%, S&P 500 -51%; CNDR returned 0-2% in 59% of months; neither had a ±10% month. Construction: CNDR sells ~0.20-delta SPX put and call, buys ~0.05-delta wings, monthly roll, T-bill collateral; BFLY sells ATM put+call and buys 5% OTM wings. — [Cboe Insights](https://www.cboe.com/insights/posts/benchmark-indices-series-volatility-management-with-cboes-bfly-and-cndr-indices/)
- Note: CNDR construction is described elsewhere as ~0.15 delta shorts (2015 launch release) — conflicting with the 0.20 above; check methodology doc. — [Cboe 2015 launch release](https://ir.cboe.com/news/news-details/2015/CBOE-Introduces-10-Options-Based-Strategy-Performance-Benchmark-Indexes-07-29-2015/default.aspx)
- BFLY was up 7.14% in December 2024, one of the only options-strategy indices to gain that month. — [S&P DJI dashboard Dec 2024](https://spglobal.com/spdji/en/documents/performance-reports/dashboard-sp-500-options-strategy-indices-2024-12.pdf)
- October 2026: S&P 500 -0.9% for the month, +10.7% YTD; BXM -0.2%, PUT +0.4%; VIX rose 16.34 → 19.42. — [Cboe Index Insights Oct 2026](https://www.cboe.com/insights/posts/index-insights-october-2026/)

### Inferences
- PUT's long-run "equal return, lower vol" result is driven largely by the 1986-2002 era and by T-bill collateral yield; in bull-dominated periods (2009-2021, 2023-2025) it lags materially. Its drawdown (-33%) is still ~2/3 of equity, so it is not a hedge.
- CNDR's low drawdown comes with low return; BFLY's -47% drawdown shows short-ATM structures with 5% wings can lose nearly as much as equities in crashes.
- For a stock/ETF trader, costs matter: index results are gross, and the real-world tracking-ETF gap is the best available estimate of the cost drag.

### Gaps
- Calendar-year 2008, 2020, 2022 and 2025 returns for PUT, BXMD, CNDR, BFLY were not retrieved (Cboe factsheet PDF could not be parsed). Recommend pulling Cboe's dashboard data directly (https://www.cboe.com/us/indices/dashboard/PUT/).
- 2026 YTD for the option indices beyond October monthly figures not found.
- S&P 500 2025 total return not confirmed in this session.

## Q3. Which management rules (30-45 DTE, 16/30-delta, 50% profit, 21 DTE, 2x stop, rolling, high IV rank) have independent out-of-sample support?

### Takeaway
Essentially none have independent, out-of-sample, cost-inclusive support. The 45-DTE / 50%-profit / 21-DTE package originates in tastytrade/tastylive in-house studies (SPY, ~2005-2017, mostly gross, reporting metrics like win rate and P&L per day that favour early exits). The one independent replication found (SteadyOptions, SPX 2001-2020, no costs) found the managed 45-DTE/50%/21-DTE strangle did *worse* (Sharpe 0.52) than a simple unmanaged 30-DTE/5-DTE-exit strangle (Sharpe 0.67). No rigorous evidence was found that an IV-rank entry filter or a 2x-credit stop improves risk-adjusted returns.

### Cited Findings
- tastylive's base studies: SPY ~1-SD (16-delta) strangles at ~45 DTE, compared hold-to-expiration vs manage at 50% max profit vs exit at 21 DTE; tastylive reports 50% management increases win rate and profit per day; managing at 50% returns more than holding but "does not control volatility as effectively as exiting at 21 DTE"; samples ~2005-2015/2017. — [tastylive Market Measures 2015](https://www.tastylive.com/shows/market-measures/episodes/managing-winners-varying-profit-targets-12-04-2015); [tastylive 2016](https://tastylive.com/shows/market-measures/episodes/managing-strangles-performance-08-05-2016); [tastylive 21 DTE](https://www.tastylive.com/shows/best-practices/episodes/managing-21-days-early-02-25-2020); [tastylive short put management 2018](https://www.tastylive.com/shows/market-measures/episodes/short-put-management-performance-09-12-2018)
- Independent test (SteadyOptions, SPX EOD 2001-May 2020, 16-delta strangles, 1x notional, no commissions/slippage): managed 45 DTE → 50% or 21 DTE: CAGR 4.44%, vol 8.62%, Sharpe 0.52. Unmanaged 30 DTE → exit 5 DTE: CAGR 5.46%, vol 8.19%, Sharpe 0.67. 25-delta put / 16-delta call unmanaged: CAGR 6.30%, vol 9.93%, Sharpe 0.63. Author: unclear whether active management adds value; warns backtests are hard to replicate. Caveat: tests change entry DTE and exit rule simultaneously. — [SteadyOptions](https://steadyoptions.com/articles/does-%E2%80%9Cmanaging-winners%E2%80%9D-add-value-to-short-strangles-r618)
- Spintwig (independent backtester, via secondary review): ~45 DTE found near-optimal with diminishing returns beyond; 75% take-profit and hold-to-expiry both had good win rates; reviewer notes implied vol typically overstates realized so delta ≠ true probability. — [the7circles review](https://the7circles.uk/?p=34924); [ERN guest post](https://earlyretirementnow.com/2020/06/17/passive-income-through-option-writing-part-5)
- IV rank: ORATS backtester material shows how to set an IV≥50 entry filter but publishes no result; claims that IV-filtered iron condors win more often (mid-to-high 50s% vs high 40s%) appear only on unsourced education sites. — [ORATS blog](https://orats.com/blog/backtester-upgrade-signals-stats); [options-force (unsourced)](https://options-force.pages.dev/p/iv-rank-entry-timing)
- AQR (Israelov & Nielsen, FAJ 2015) show covered-call short-delta exposure is an uncompensated timing bet — relevant to "rolling" rules that change delta exposure without being priced. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/Covered-Calls-Uncovered)

### Inferences
- "Profit per day" and "win rate" (tastylive's headline metrics) are not risk-adjusted return on capital; early profit-taking raises win rate mechanically by truncating the payoff while keeping full exposure to the tail when you re-enter. The independent test suggests the net effect is neutral-to-negative.
- 21-DTE exit has the most plausible mechanism (cutting gamma exposure near expiry), and tastylive's own data say its benefit is volatility reduction, not return.
- Vendor bias: tastytrade/tastylive is a broker-owned media platform that benefits from turnover; OptionAlpha and ORATS sell backtesting/automation. No sample-split / out-of-sample validation was found in any vendor study.
- 2x-credit stops on short premium are path-dependent and convert vol spikes (which often mean-revert) into realized losses; no independent study supporting them was found.

### Gaps
- No academic paper testing 50%/21-DTE/2x-stop rules was found.
- Raw tastylive result tables (returns, drawdowns) were not retrievable; secondhand summaries only.
- No independent test of IV-rank entry filters; Sinclair's views not located in this session.
- Delta choice (16 vs 30): only indirect evidence (SteadyOptions 25-delta put raised CAGR; PUT index uses ATM puts and earns ~equity-like return) — more delta = more equity beta, not more "edge."

## Q4. Covered calls (and the wheel) on high-growth stocks: underperformance in strong uptrends

### Takeaway
Strong, consistent evidence: covered calls on fast-rising stocks lag the underlying, and the short-call leg embeds an uncompensated "equity reversal" timing bet (AQR). Live single-stock covered-call ETFs on NVDA/TSLA (YieldMax) have trailed their underlyings on total return. The wheel is economically a put-write followed by a covered call, so it inherits both critiques; no rigorous independent study of "the wheel" itself was found.

### Cited Findings
- Israelov & Nielsen, "Covered Calls Uncovered" (FAJ 2015): covered-call returns decompose into passive equity, equity market timing (short delta that grows when markets rally), and short volatility; the timing component is material, uncompensated, may contribute >3x the risk of the short-vol component and nearly half the risk of the passive equity exposure. Delta-hedging the timing exposure raised Sharpe from 0.37 to 0.52 and cut vol 11.4% → 9.2%. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/Covered-Calls-Uncovered); [Quantpedia](https://quantpedia.com/covered-calls-uncovered/); [CFA Institute](https://rpc.cfainstitute.org/research/financial-analysts-journal/2015/covered-calls-uncovered)
- Israelov, Klein & Tummala, "Covering the World" (Journal of Risk): across 11 global indices the equity-timing component is on average uncompensated yet adds significant risk. — [Risk.net](https://risk.net/journal-of-risk/5943741/covering-the-world-global-evidence-on-covered-calls)
- AQR also published "Covered Call Strategies: One Fact and Eight Myths" (FAJ) and "Covered Calls and Their Unintended Reversal Bet." — [AQR PDF](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/FAJ-Covered-Call-Strategies-One-Fact-and-Eight-Myths.pdf); [AQR white paper](https://www.aqr.com/Insights/Research/White-Papers/Covered-Calls-and-Their-Unintended-Reversal-Bet)
- NVDY vs NVDA: one trailing year NVDA +62% vs NVDY +56% total return with distributions reinvested; NVDY "misses about half" of NVDA's strong-month moves; NVDY fell 21% Aug-Dec 2025 with full downside participation; distributions partly return of capital. — [Yahoo Finance](https://finance.yahoo.com/markets/options/articles/why-nvdy-shareholders-miss-half-174004944.html); [24/7 Wall St Dec 2025](https://247wallst.com/investing/2025/12/13/nvdy-offers-58-yield-on-nvidia-exposure-but-investors-are-getting-their-own-capital-back/)
- TSLY vs TSLA: since-inception TSLY +55.36% vs TSLA +86.21% (Kalkine); 2026: TSLY -39.3% YTD and -41.6% over one year (24/7 Wall St, Aug 2026). — [Kalkine](https://kalkine.com/news/etfs/yieldmax-tsla-etf-misses-about-30-of-teslas-rally-on-call-strategy); [24/7 Wall St Aug 2026](https://247wallst.com/investing/etf/2026/08/21/tsly-pays-more-each-week-than-nvdy-but-holders-are-losing-money-faster/)
- Morningstar: YieldMax shifted away from synthetic structures for at least one fund in early 2025, so structures are not uniform. — [Morningstar](https://www.morningstar.com/funds/this-etf-paid-out-big-its-total-returns-tell-another-story)

### Inferences
- On high-momentum mega-caps (NVDA, TSLA), the short call removes exactly the right-tail months that generate most of the long-run return; the premium does not compensate for that given those stocks' positively skewed returns.
- YieldMax funds are imperfect evidence (synthetic structures, fees, high distributions, short histories, newsletter sources), but they are live, after-cost outcomes, which vendor backtests are not.
- The wheel: the put-write leg earns roughly equity-like returns with VRP (PUT index evidence); the covered-call leg adds the AQR timing drag; assignment-driven switching makes delta exposure path-dependent with no evidence of compensation.

### Gaps
- No academic study specifically on "the wheel" found.
- No peer-reviewed study of covered calls restricted to high-growth single stocks found; evidence is index-level (AQR) plus ETF track records (secondary press with inconsistent windows).
