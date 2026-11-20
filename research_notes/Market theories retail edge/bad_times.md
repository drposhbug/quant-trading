# How Stock Markets Behave in Bad Times: Crashes, Bear Markets, Crises, Recoveries

Scope: crisis dynamics and what is tradeable and robust for a long-only retail investor. Researched 2026-11-20. Caution throughout: there are only about 5-10 truly independent severe US crashes in a century, so almost every "after a crash" statistic rests on single-digit independent episodes.

## 1. Crisis mechanics: volatility clustering, leverage effect, correlation spikes, liquidity spirals, VIX term structure

### Takeaway
Volatility in bad times is persistent and asymmetric: it rises more after falls than after rises, and correlations rise in down markets, so diversification across stocks weakens when it is most needed. Liquidity spirals explain why declines speed up. These facts support volatility-aware sizing. They do not give a long-only investor a reliable directional edge.

### Cited Findings
- Leverage effect, meaning the negative correlation between current returns and future volatility, was first discussed by Black (1976) and Christie (1982) — [Bekaert & Wu, RFS 2000](https://www.bauer.uh.edu/wu/Papers/RFS2000_AsyVol.pdf)
- There are two competing explanations for asymmetric volatility. In the leverage story, return shocks raise future volatility. In the volatility-feedback story, higher expected volatility raises the risk premium and pushes prices down. Bekaert & Wu (Nikkei 225 data) reject the pure leverage model and support volatility feedback — [Bekaert & Wu, NBER W6022](https://www.nber.org/papers/W6022)
- Wu (2001), using a structural model estimated by simulated method of moments, finds that both leverage and volatility feedback matter — [Wu, RFS 2001](https://www.bauer.uh.edu/wu/Papers/RFS2001_DeterAsyVol.pdf)
- GJR-GARCH (Glosten, Jagannathan & Runkle 1993, JF) adds a term for negative lagged shocks only. This is the standard way to model the fact that down moves raise volatility more than up moves — [GJR 1993 PDF](https://faculty.washington.edu/ezivot/econ589/GJRJOF1993.pdf)
- Longin & Solnik (2001, JF) applied extreme value theory to monthly data for the 5 largest markets, 1958-1996. Correlation rises in bear markets but not in bull markets. Multivariate normality is rejected for the negative tail but not for the positive tail. Correlation depends on market trend rather than on volatility as such — [EconPapers JF 56(2)](https://econpapers.repec.org/RePEc:bla:jfinan:v:56:y:2001:i:2:p:649-676); [CEPR DP2538](https://repec.cepr.org/repec/cpr/ceprdp/Dp2538.pdf)
- Ang & Chen (2002): correlations between US stocks and the US market are much higher in declines than in rallies. They propose an "H statistic" to measure the asymmetry — [Ang & Chen PDF](https://drupalgsb-test.paas.cc.columbia.edu/sites/default/files-efs/pubfiles/1516/corr.pdf); critique of the test in [Hong, Tu & Zhou](https://hong.economics.cornell.edu/papers/Asymmetries%20in%20Stock%20Returns-%20Statistical%20Tests%20and%20Economic%20Evaluation.pdf)
- Campbell, Koedijk & Kofman (2002) find similar international results but warn that some of the conditional-correlation evidence may be biased. A rise in volatility mechanically inflates the measured correlation — [IDEAS FAJ 2002](https://ideas.repec.org/a/taf/ufajxx/v58y2002i1p87-94.html)
- Brunnermeier & Pedersen ("Market Liquidity and Funding Liquidity", NBER w12939 / RFS 2009) describe two spirals. In the margin spiral, illiquidity raises margins, which tightens funding, which reduces liquidity provision further. In the loss spiral, dealer losses on existing positions reduce their capacity to provide liquidity. The model has multiple equilibria, so liquidity can dry up suddenly. It also explains commonality in liquidity across assets and flight to liquidity. LTCM/1998 is the motivating example — [NBER w12939](https://www.nber.org/papers/w12939.pdf); [Princeton copy](https://www.princeton.edu/~markus/research/papers/Mkt_Fun_Liquidity.pdf)
- VIX futures backwardation (front month above later months) is "incredibly uncommon", per S&P DJI's 2020 COVID note — [S&P Global](https://www.spglobal.com/en/research-insights/articles/the-vix-futures-curve-is-in-backwardation)
- Cboe treats backwardation as a possible down-market sign and asks whether it actually predicts one. Its table of 30-day S&P returns after backwardation since 2018 could not be retrieved — [Cboe](https://www.cboe.com/insights/posts/inside-volatility-trading-is-vix-backwardation-necessarily-a-sign-of-a-future-down-market)
- In a VIX futures basis study, returns on VIX futures themselves were close to zero or positive in turbulent periods. Shorting VIX futures in contango and buying them in backwardation, hedged with S&P minis, was profitable. This is a volatility-trading result, not a signal for equity direction — [Quantpedia](https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures)
- A 2019 academic test of the VIX term structure as a contrarian equity-timing signal exists. Its findings were not retrieved — [JRFM 12(3):113](https://mdpi.com/1911-8074/12/3/113)

### Inferences
- Clustering is the most robust stylized fact. It supports sizing exposure by recent volatility (Section 4) more than it supports forecasting direction.
- Correlations rise in down markets, so a concentrated tech portfolio of 5-10 names behaves almost like one asset in a crash. Diversifying within equities gives the least protection exactly when it is needed.
- Liquidity spirals mostly affect leveraged players. For an unlevered retail investor the practical points are to avoid margin, which would put them inside the spiral, and to recognize that forced selling by others creates the overshoot behind post-crash rebounds (Section 5).

### Gaps
- No quantified, peer-reviewed evidence was retrieved on whether VIX term-structure inversion predicts S&P returns. Treat it as a regime indicator, not a validated signal.
- No numeric GARCH persistence estimates for the S&P (e.g. alpha+beta of about 0.98-0.99 in daily fits) were retrieved from a source. This is standard folklore but unsourced here.
- No fire-sale magnitudes (e.g. Coval-Stafford mutual-fund fire sales) or margin-call statistics for 2008/2020 were retrieved.

## 2. Historical bear markets: depth, duration, recovery (broad market and tech)

### Takeaway
The four "big" US bears were 1929-32 (about -86%), 1973-74 (about -48%), 2000-02 (about -49%) and 2007-09 (about -57%). Their price recoveries took from about 7 to more than 20 years, and inflation-adjusted recoveries took far longer. The average bear since 1929 is much shallower (-33.5%) and shorter (9.6 months). For tech, the Nasdaq-100 fell more than 80% in 2000-02 and about 34% in 2021-22.

### Cited Findings
- 1929-32: S&P about -86% (Fox -86.1%, Kiplinger -86.2%) over about 34 months. The prior peak was not regained until 1954. It is the only recovery cycle with negative real total return — [Fox Business](https://www.foxbusiness.com/markets/history-of-bear-markets-since-1929); [Kiplinger](https://kiplinger.com/article/investing/t041-c007-s001-how-bad-can-it-get.html); [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/the-four-totally-bad-bears). Note: Kiplinger uses a different break-even measure that gives Jan 1945, so sources conflict on 1929's recovery date.
- 1973-74: S&P -48% (Jan 1973 to Oct 1974; Plus500 -48.2% over 630 days; Kiplinger -43% to Sep 1974). Nominal recovery took about 90 months, the longest after WWII. The real recovery gain was only +20.2% versus +267.3% nominal — [Fox](https://www.foxbusiness.com/markets/history-of-bear-markets-since-1929); [Plus500](https://us.plus500.com/en/newsandmarketinsights/stock-market-corrections-since-1950); [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2025/10/06/bear-market-recoveries-q3-2025)
- 2000-02: S&P -49%. The prior closing peak was regained on 30 May 2007, about 86 months after the top. Dividends nearly doubled the recovery gain — [Fox](https://www.foxbusiness.com/markets/history-of-bear-markets-since-1929); [Plus500](https://us.plus500.com/en/newsandmarketinsights/stock-market-corrections-since-1950); [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2025/10/06/bear-market-recoveries-q3-2025)
- 2007-09: S&P -57% over 17 months (Oct 2007 to Mar 2009). The subsequent recovery was the strongest of the four big bears, +317.1% — [Fox](https://www.foxbusiness.com/markets/history-of-bear-markets-since-1929); [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2025/10/06/bear-market-recoveries-q3-2025)
- Since 1929 the average bear market fell 33.5% and lasted 9.6 months (Ned Davis Research) — [Kiplinger](https://www.kiplinger.com/slideshow/investing/t052-s001-8-facts-you-need-to-know-about-bear-markets/index.html)
- Frequency, 1975-2025: the S&P's intra-year max drawdown reached at least 20% in 14 of 50 years (about 1 in 3) and exceeded 30% five times — [Schwab](https://www.schwab.com/learn/story/ups-and-downs-stock-market-volatility)
- Nasdaq-100 2000-02: "declined by more than 80%" ([Nasdaq.com](https://www.nasdaq.com/articles/whats-in-store-for-q4-for-the-nasdaq-100)). Fortune gives -78% from Mar 2000 to Oct 2002 ([Fortune](https://fortune.com/2022/05/22/why-crypto-tech-stocks-crash-recession-dotcom-bubble/amp)). **The commonly quoted -83% was not confirmed by any retrieved source.** Sources conflict between -78% and -83%, depending on close versus intraday and the exact trough date.
- NDX calendar-year losses: 2000 -36.1%, 2001 -33.3%, 2002 -37.4%, 2008 -41.7%, 2022 -32.4%. That is three consecutive years worse than -30% after the dot-com peak. By comparison the S&P's worst recent year was 2008 at about -37%, with a max drawdown of -57% — [A Wealth of Common Sense](https://awealthofcommonsense.com/2025/12/the-nasdaq-100-booms-busts/)
- Nasdaq Composite price recovery after 2000 took until about Feb 2015. On total return, the drawdown was -74% and the new high came in Jun 2014 — [DQYDJ](https://dqydj.com/nasdaq-drawdown-history/); see also [MSCI "Seven Lean Years"](https://www.msci.com/research-and-insights/quick-take/seven-lean-years-and-other-lessons-from-the-last-tech-stock-correction)
- 2021-22: the NDX fell about 34% from its high, its worst stretch since 2007-08. The Composite fell -31% on total return from Nov 2021 to Oct 2022 — [Nasdaq.com](https://www.nasdaq.com/articles/whats-in-store-for-q4-for-the-nasdaq-100); [DQYDJ](https://dqydj.com/nasdaq-drawdown-history/)

### Inferences
- In 3 of the 4 major bears, a price-only buy-and-hold investor waited about 7-25 years to recover. Dividends and rebalancing shorten that a lot. The 2000 example shows dividends nearly doubling the recovery gain.
- Tech-specific tail risk is much larger than the broad market's: more than 80% versus about 49% in the same 2000-02 episode. Any tech-heavy long-only book should be sized assuming a drawdown worse than 50% is possible. That assumption should come from sizing, not from a timing signal.
- With 4 major bears and about 25 bears in total, estimates of average recovery time carry very wide error bands.

### Gaps
- 1987 (S&P about -34% peak-to-trough, with -20.5% on 19 Oct 1987), 2020 (about -34% in 23 trading days) and 2022 (S&P about -25%) are widely reported, but no source was fetched in this pass. The figures above are from memory and unverified.
- No NDX-specific total-return recovery date for the 2000 peak was found. The commonly cited ~2015/2016 date is for the Composite on a price basis.

## 3. Trend filters (200-day MA, time-series momentum), crisis alpha, whipsaw, decay, and "best days near worst days"

### Takeaway
Diversified time-series momentum, run on futures across many assets, has a century-long record of doing well in most large equity/bond crises: 8 of the 10 largest 60/40 drawdowns. Simple single-index 200-day rules mainly cut drawdowns and volatility. Since about 1990 they have usually lagged buy-and-hold on return because of whipsaws. The "you'll miss the best days" argument is roughly symmetric and mostly a scare statistic. Best and worst days cluster together in high-volatility regimes, so a trend filter that is out of the market in bear markets avoids both.

### Cited Findings
- Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing" (JPM 2017), with data since 1880: time-series momentum performed well in 8 of the 10 largest crisis periods, defined as the largest 60/40 drawdowns. The strategy itself still had drawdowns of up to about 25% over extended periods — [AQR](https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing?aqrPDF=1); [UCC working-paper copy](https://www.ucc.ie/en/media/research/centreforinvestmentresearch/wp/TrendFollowingFeb2014.pdf); [Alpha Architect summary](https://alphaarchitect.com/time-series-momentum-aka-trend-following-the-historical-evidence/) (the summary page returned 403 on fetch, so numbers come from the search snippet)
- Companion work on trend following and financial crises: after a financial crisis *begins*, trend-following returns average less than half of non-crisis returns for about 4 years. The authors say this is consistent with behavioral finance. Authorship was not confirmed on the source page — [Alpha Architect](https://alphaarchitect.com/?p=34042)
- 200-day rule whipsaw: the S&P crossed its 200-day MA about 180 times from Jan 1994 to Jan 2019, giving 90 bullish signals, many of them losers. Smoothing with a 5-day average cut this to 34 bullish signals in 25 years. Long-side signals worked but short signals lost money — [StockCharts, Arthur Hill](https://stockcharts.com/articles/arthurhill/2019/02/just-how-effective-is-the-200-day-moving-average.html); [StockCharts follow-up](https://d.stockcharts.com/articles/chartwatchers/2019/03/sp-500-clears-the-200-day-should-we-take-the-bait.html)
- Decay: Blake LeBaron's view (as cited) is that the MA rule worked across about six decades to the 1980s and stopped working around the early 1990s, when cheap trading and ETFs arrived. A 2002-2018 Dow ETF test of the 200-day rule lagged buy-and-hold on return but had lower risk — [White Coat Investor](https://www.whitecoatinvestor.com/?p=112284) (secondary source)
- Without a recession or sustained decline, a 200-day rule is unlikely to beat buy-and-hold because of whipsaws — [Quantified Strategies](https://quantifiedstrategies.substack.com/p/200-day-moving-average-trading-strategy-e52) (blog, lower quality)
- Asness/AQR, "So What If You Miss the Market's N Best Days": the effects are symmetric. S&P 1970-1996, baseline 12.3%/yr: missing the best 12 months gives 7.2% (-5.1pp) and missing the worst 12 gives 18.1% (+5.8pp). Out of sample, 1997-2024, baseline 9.3%: missing the best 12 months gives 5.0% (-4.3pp) and missing the worst 12 gives 14.9% (+5.6pp). Daily out of sample: missing the best 10 days gives 6.2% (-3.1pp) and missing the worst 10 gives 12.8% (+3.6pp); missing the best 30 days gives 2.4% and missing the worst 30 gives 17.4%. In a realistic 80/20 switching strategy, "great" versus "terrible" timing is only about ±1.6-1.8pp/yr. A normal-distribution simulation reproduces most of the effect (-4.7/+4.8 simulated vs -5.1/+5.8 actual), so it is mostly arithmetic, not a special property of markets — [AQR](https://www.aqr.com/insights/perspectives/so-what-if-you-miss-the-markets-n-best-days)
- Hartford Funds: about 78% of the S&P's best days in the last 20 years fell in a bear market (about 42%) or in the first 2 months of a bull market (about 36%). An earlier edition said 76%. Missing the 10 best days from 1996-2025 cut ending wealth from $192,167 to $85,490 (-56%) — [Hartford](https://www.hartfordfunds.com/practice-management/client-conversations/managing-volatility/timing-the-market-is-impossible.html); [Hartford bear markets](https://www.hartfordfunds.com/practice-management/client-conversations/managing-volatility/bear-markets.html)
- Wells Fargo: missing the best 30 days (Feb 1994 to Jan 2024) cut returns from 8.0%/yr to 1.8%/yr. Best days cluster in bear markets and recessions, and some worst days occur in bull markets — [Wells Fargo](https://www.wellsfargo.com/investment-institute/sr-perils-time-volatile-markets)
- Morningstar (via search snippet; the page returned 403): missing the 10 best days cost 2.40%/yr, while missing the 10 worst added 2.66%/yr, a net difference of only 26bp. The median gap between a top-10 worst day and a top-10 best day was 7 days — [Morningstar](https://www.morningstar.com/funds/you-can-beat-stock-market-by-avoiding-its-worst-days-you-wont)
- A critique calls the missing-best-days chart "wildly deceptive and misleading" — [TheStreet Pro](https://pro.thestreet.com/market-commentary/the-scariest-chart-on-wall-street-is-also-the-most-dishonest)

### Inferences
- Interaction with trend filters: best days happen mostly in bear markets, when volatility is high and price is below the 200-day MA. A filter that is out below the 200-day therefore misses many best days *and* many worst days. The net effect depends on whether the worst days outweigh the best, and on average they slightly do (Morningstar's 26bp, AQR's asymmetry). The real costs are whipsaws, late re-entry after V-shaped recoveries like 2020, and taxes in taxable accounts.
- What is plausibly robust for retail: a smoothed, long-only, monthly-checked trend rule (e.g. price vs 10-month MA) on a broad index. This is drawdown insurance with a probable small negative-to-flat return cost after about 1990, not alpha. Its value is behavioral and sizing-related (it lets you hold more equity), plus protection in slow bears (2000-02, 2008). It gives little protection in fast crashes (1987, 2020).
- Crisis alpha from diversified time-series momentum (long/short futures across asset classes) is not available to a long-only stock investor. Single-index long/flat rules capture only part of it.
- Sample-size warning: the "8 of 10 crises" result has n=10. Single-index 200-day studies effectively rest on about 5-8 major bear markets.

### Gaps
- Faber (2007) "A Quantitative Approach to Tactical Asset Allocation" and its out-of-sample update numbers were not retrieved.
- No net-of-cost, net-of-tax 200-day backtest from a peer-reviewed source was retrieved for the post-1990 period on NDX specifically.
- The Hurst-Ooi-Pedersen PDF could not be parsed (encrypted). Its gross/net returns, Sharpe and per-crisis table are not in these notes.

## 4. Volatility-managed portfolios (Moreira-Muir) and critiques

### Takeaway
Moreira & Muir (2017) show that scaling market exposure by the inverse of last month's realized variance raised the market Sharpe ratio by about 25% (alpha 4.9%). Cederburg et al. (2020, JFE) show that across 103 strategies, implementable real-time versions do not reliably beat unmanaged ones. Barroso & Detzel find that after transaction costs the alphas disappear. A 2024 multifactor rebuttal partly revives the idea. For a single equity index, volatility targeting is better seen as a risk-control tool than as a source of alpha.

### Cited Findings
- Moreira & Muir (JF 2017; NBER w22208) scale monthly returns by 1/(previous month's realized variance). For the market factor this gives alpha of 4.9%, an appraisal ratio of 0.33 and about a 25% increase in Sharpe ratio. The mechanism is that volatility changes are not offset by proportional changes in expected return — [NBER w22208](https://www.nber.org/papers/w22208)
- Cederburg, O'Doherty, Wang & Yan (JFE 2020, 138(1):95-117) test 103 equity strategies. The in-sample spanning-regression alphas need ex post optimal weights and cannot be implemented in real time. Realistic out-of-sample versions usually earn *lower* certainty-equivalent returns and Sharpe ratios than unscaled portfolios. The cause is instability in the spanning regressions. The volatility-managed version wins in 53 cases and the original in 50, a coin flip — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117); [Lehigh PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf); [Alpha Architect](https://alphaarchitect.com/?p=59058)
- Barroso & Detzel: after transaction costs, none of the volatility-managed portfolios studied have positive alpha, and most have significantly lower Sharpe ratios than unmanaged ones. This is cited via an Erasmus thesis, not read directly — [Erasmus thesis](https://thesis.eur.nl/pub/72898/thesis_ggianfranceschi_third_draft.pdf)
- DeMiguel, Martin-Utrera & Uppal (JF 2024): a conditional *multifactor* portfolio whose factor weights fall with market volatility beats the unconditional version out of sample and net of costs — [LBS PDF](https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf)

### Inferences
- For a long-only, unlevered retail investor, the inverse-variance weights in Moreira-Muir need leverage in calm periods to match average exposure. Without leverage it becomes "de-risk when volatility spikes". That cuts left-tail exposure but also cuts exposure to the high-return rebound days that cluster in high-volatility regimes (Section 3).
- Robust use: cap exposure using a volatility target to control drawdowns. Do not expect Sharpe improvement net of costs and taxes on a single index.
- Volatility management and trend filters are highly overlapping signals in crises, since both de-risk after vol spikes and price falls. Stacking them double-counts.

### Gaps
- No direct read of Barroso & Detzel ("Do limits to arbitrage explain the benefits of volatility-managed portfolios?", JFE 2021). Its numbers are second-hand.
- No source quantified volatility management specifically on NDX/QQQ.

## 5. Post-crash return predictability: buying after big drawdowns or extreme fear; momentum crashes

### Takeaway
Average forward 1-5 year returns after deep drawdowns or VIX spikes above 40 are well above unconditional averages. However, the results come from about 9 independent VIX>40 episodes and overlapping observations. One-year win rates after a 20% drawdown are only about 55% in long samples, with an average loss of about -21% when wrong. So buying the dip is a positive-expectancy tilt with large variance, not a reliable signal. Long-short momentum crashes during rebounds out of panic states. For long-only investors this means that after a crash, "past winners" lag beaten-down high-beta stocks.

### Cited Findings
- VIX ≥ 40 since 1990: 208 trading days, but only 9 independent episodes. The S&P was positive 12 months later about 96% of the time, but positive 3 months later only about 67% of the time, *below* the calm-market base rate — [ChartingLens](https://chartinglens.com/blog/vix-levels-stock-market-returns) (blog; computed Nov 2026)
- Wells Fargo (Jan 1990 to Apr 2025): after VIX spikes above 40, the S&P was up about 30% a year later on average — [NBC/CNBC citing Wells Fargo](https://www.nbcnewyork.com/news/business/money-report/this-is-what-typically-happens-to-stocks-after-periods-of-high-volatility/6243253/)
- Bilello: after VIX closes above 50, the S&P averaged +35% over one year. After VIX fell from 50 to 30, it typically gained about 18% over a year — [Benzinga](https://www.benzinga.com/markets/25/04/44878050/s-p-500-typically-gains-18-in-a-year-after-vix-drops-from-50-to-30-level-heres-what-analysts-say)
- Drawdown-entry averages (Ritholtz, month-end data since 1950). Buying after a 20% decline: +17% / +45% / +74% at 1/3/5 years. After a 30% decline: +21% / +48% / +88%. These use overlapping observations, and win rates are not reported — [A Wealth of Common Sense](https://awealthofcommonsense.com/2026/03/how-the-stock-market-performs-after-a-correction/) (via search snippet)
- Counterpoint (Fidelity's Timmer, data back to 1906): the S&P was positive in the year after a 20% drawdown only 55% of the time, with an average loss of -21% when negative. A daily-data analysis for 1929-2019 found further 1-year declines after a 20% drawdown were nearly twice as likely as otherwise. The baseline 1-year positive rate since 1985 is about 79% — [Yahoo Finance / Beaumont](https://finance.yahoo.com/news/probability-another-20-drawdown-higher-204027742.html); [IBKR Campus](https://www.interactivebrokers.com/campus/?p=158020)
- Daniel & Moskowitz, "Momentum Crashes" (JFE 2016; NBER w20439): momentum crashes happen in "panic states", after market declines and when volatility is high, at the same time as market rebounds. Past losers behave like call options, so shorting them is like shorting calls in a rising market. A dynamic momentum strategy, scaled by forecast mean and variance, about doubles the static strategy's Sharpe ratio. The result holds across 8 markets and asset classes — [NBER w20439](https://www.nber.org/papers/w20439); [Chicago Booth Review](https://www.chicagobooth.edu/review/understanding-momentum-crashes); [JFE record](https://econpapers.repec.org/RePEc:eee:jfinec:v:122:y:2016:i:2:p:221-247)

### Inferences
- The two bodies of evidence conflict, and the conflict is informative. Buying at the *first* 20% drawdown has close to coin-flip one-year odds, because some drawdowns turn into 1929/1973/2000/2008-style bears. Buying at *extreme* fear (VIX>40, drawdown above 30%) has high 12-month hit rates, but rests on only about 9 episodes, and the 3-month path is often worse.
- A robust long-only implementation is to stage entries (e.g. deploy reserve cash in tranches at -20%, -30%, -40%) rather than to time a single entry. Also accept that the 3-month path is often negative.
- Momentum-crash implication for a long-only tech/momentum tilt: in the rebound after a panic, rotating into "what held up best" underperforms. The panic state (market down, volatility high) is exactly when to *reduce* momentum-tilt weight, not raise it.
- Selection bias: all modern US samples are survivor samples. Japan after 1989 is the obvious counterexample for "always recovers".

### Gaps
- No primary data was retrieved on AAII bull-bear spread extremes or put/call ratio extremes and forward returns. These are often cited, with mixed and weak results in the literature, but are unverified here.
- No formal statistical test (with CIs) of post-VIX>40 returns versus the unconditional mean was found. With n≈9, any such test would have low power.

## 6. Cash drag, dividends, and rebalancing into drawdowns

### Takeaway
Only partial evidence was retrieved. Dividends materially speed up recovery after bears: in 2000-02 they nearly doubled the recovery gain. Timing studies show that even great versus terrible switching within an 80/20 portfolio is worth only about ±1.6-1.8pp/yr. Small, systematic rebalancing differences are therefore second-order next to staying invested.

### Cited Findings
- 2000 bear recovery: dividends nearly doubled the recovery gain. The 1973 nominal recovery of +267% was only +20% in real terms — [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2025/10/06/bear-market-recoveries-q3-2025)
- 80/20 stock/T-bill switching: no timing 8.7%, terrible timing 6.9%, great timing 10.6% (1997-2024). The 1970-1996 figures were 11.9% / 10.3% / 13.5% — [AQR](https://www.aqr.com/insights/perspectives/so-what-if-you-miss-the-markets-n-best-days)
- From 1997 to 2024 the S&P returned 9.3%/yr versus 2.0% for T-bills. The equity premium over cash is the cost of being out of the market — [AQR](https://www.aqr.com/insights/perspectives/so-what-if-you-miss-the-markets-n-best-days)

### Inferences
- Cash drag from a trend or volatility filter equals (equity minus T-bill return) times the fraction of time out of the market. With a premium of about 7pp/yr and a filter out about 20-30% of the time, the gross drag before crash avoidance is about 1.5-2pp/yr. The filter has to avoid roughly that much in crash losses to break even. This is consistent with post-1990 200-day results being about flat to slightly negative.
- Rebalancing into drawdowns, meaning buying equities as they fall to restore target weights, is a mild contrarian bet. It pays off after V-shaped recoveries (2009, 2020) and hurts in long bears (1929-32, Japan).

### Gaps
- No primary study of rebalancing bonuses or threshold-versus-calendar rebalancing returns through crashes was retrieved (e.g. Vanguard rebalancing research).
- No sourced figure for the current T-bill yield or quantified cash drag in 2026 was retrieved.
