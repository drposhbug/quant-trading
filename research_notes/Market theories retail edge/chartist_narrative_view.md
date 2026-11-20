# Chartists and Narratives: the Believers' Case and the Strongest Rebuttals

Scope: the case for technical analysis (TA), Dow theory, Elliott wave, Wyckoff, Shiller's narrative economics and Keynes' beauty contest, tested against the evidence. Written as a simulated expert interview: a question, a sourced answer, then a sharper follow-up, with at least 3 rounds per thread. EVIDENCE = a published, quantified result. BELIEF = practitioner or theoretical claim with no quantified out-of-sample support.

Research date 2026-11-20. Coverage and limits: abstracts and secondary summaries for most papers. Full-text figures come from Sullivan-Timmermann-White (1999) and the Bybee-Kelly-Manela-Xiu NBER working paper (2021), both extracted from the PDFs.

---

## Q1. What is the best academic evidence for technical analysis, and how has it held up out of sample since the 1990s?

### Takeaway
The believers' best evidence is real but dated. Simple moving-average and breakout rules on the DJIA beat cash from 1897 to 1986, even after a data-snooping correction over 7,846 rules. Over 1987-1996, though, the same rules showed "scant evidence" of value, and S&P 500 futures from 1984 to 1996 showed none. Surveys count more positive studies than negative ones, but say profits mostly ran "until the early 1990s." Newer support comes in two forms: cross-sectional (moving-average timing on high-volatility portfolios) and forecast-combination (technical indicators predicting the equity premium about as well as macro variables). Both are weaker claims than "chart patterns make money after costs today."

### Cited Findings

**Round 1: "What is the single strongest piece of evidence for TA?"**
- Brock, Lakonishok and LeBaron (1992, BLL) tested 26 rules (moving averages and trading-range breaks) on 90 years of the DJIA. The rules "significantly outperform a benchmark of holding cash," and "every one of the trading rules they consider is capable of beating the benchmark." — [Sullivan, Timmermann & White 1999, J. Finance, describing BLL](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- BLL themselves acknowledged the risk: "numerous moving average rules can be designed, and some, without a doubt, will work. However, the dangers of data snooping are immense." — [STW 1999 quoting BLL p.1736](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)

**Round 2: "Is that result just data snooping?"**
- Sullivan, Timmermann and White (STW) built a universe of 7,846 rule parameterizations (filters, moving averages, support/resistance, channel breakouts, on-balance volume). They applied White's Reality Check bootstrap to the DJIA for 1897-1996. Over BLL's own sample (1897-1986), "certain trading rules did indeed outperform the benchmark, even after adjustment is made for data-snooping." Snooping-adjusted p-values were below 0.002 in all four subperiods. — [STW 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- The best rule over 100 years in the full universe was a 5-day simple moving average. The best rule in the BLL universe was a 50-day variable moving average with a 1% band, at 9.4% a year. An investor following the ex-ante best rule (recursive cumulative-wealth selection) would have earned 14.9% a year, more than 2 points below the ex-post best rule. That gap shows hindsight selection cost about 2 points a year even inside the "good" era. — [STW 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)

**Round 3: "So did it survive after publication?"**
- No. Over 1987-1996, "the probability that the best-performing trading rule did not outperform the benchmark during this period is nearly 12 percent." STW concluded there was "scant evidence that technical trading rules were of any economic value." On S&P 500 futures, where costs and shorting are easy to model, they found "no evidence that the trading rules outperform the benchmark" over 1984-1996. — [STW 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)
- A later out-of-sample test of the same well-known rules on 1987-2011 data found no evidence that they predict stock markets. — [summary of "Predictability of the simple technical trading rules: an out-of-sample test" (vLex)](https://law-journals-books.vlex.com/vid/predictability-simple-technical-trading-rules-855670296). I saw only the secondary summary, not the paper's numbers.

**Round 4: "What does the whole literature say?"**
- Park and Irwin (2007, J. Economic Surveys) reviewed 95 "modern" studies: 56 positive, 20 negative, 19 mixed. Early studies found profits in FX and futures but not in stocks. Modern studies found profits "at least until the early 1990s." The authors flag data snooping, ex-post selection of rules, and the difficulty of estimating risk and transaction costs. — [Park & Irwin via RePEc](https://econpapers.repec.org/RePEc:bla:jecsur:v:21:y:2007:i:4:p:786-826); [AgMAS 2004 working version](https://ageconsearch.umn.edu/record/37487/files/AgMAS04_04.pdf)
- The 2004 working version counted 92 studies (58 positive, 24 negative, 10 mixed). It also cites surveys showing about 30-40% of practitioners believe TA is an important driver of prices at short horizons. — [Park & Irwin 2004](https://ageconsearch.umn.edu/record/37487/files/AgMAS04_04.pdf)
- Belief versus use: in Taylor's (1992) survey of London FX chief dealers, more than 90% placed some weight on TA. — [STW 1999 citing Taylor](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf) Widespread use does not show that TA is profitable.

**Round 5: "What about chart patterns themselves (head-and-shoulders and the like)?"**
- Lo, Mamaysky and Wang (2000, J. Finance) detected 10 classic patterns (5 pairs, such as head-and-shoulders and double tops/bottoms) using nonparametric kernel regression on US stocks, 1962-1996. They found that "several technical indicators do provide incremental information and may have some practical value." — [MIT abstract](https://web.mit.edu/Alo/www/Papers/techanal.html); [NBER w7613](https://www.nber.org/papers/w7613)
- The CFA Institute digest adds two caveats. Traditional patterns "may not be optimal for detecting statistical anomalies," and patterns that detect anomalies "need not be optimal for indicating trading profits." The paper tests whether the distribution of returns shifts after a pattern; it does not test whether a strategy makes money. — [CFA Digest 2001](https://rpc.cfainstitute.org/-/media/documents/article/cfa-digest/2001/dig-v31-n1-811-pdf.pdf)

**Round 6: "Is there any post-2000 evidence believers can lean on?"**
- Han, Yang and Zhou (2013, JFQA) applied a 10-day moving-average timing rule to volatility-decile portfolios. For high-volatility portfolios, CAPM and Fama-French 3-factor abnormal returns were "of great economic significance," larger than momentum. These returns were not explained by market timing, sentiment, default risk or liquidity risk. The effect gets stronger as information uncertainty rises. — [IDEAS/RePEc](https://ideas.repec.org/a/cup/jfinqa/v48y2013i05p1433-1461_00.html); [CFA digest](https://rpc.cfainstitute.org/research/cfa-digest/2014/08/a-new-anomaly-the-cross-sectional-profitability-of-technical-analysis-digest-summary)
- Neely, Rapach, Tu and Zhou (2014, Management Science) forecast the monthly US equity premium out of sample over 1960-2008, using the Campbell-Thompson out-of-sample R-squared. Technical indicators matched or beat macro variables. They are better at catching the fall in the premium near business-cycle peaks, while macro variables catch the rise near troughs. Combining the two "substantially" improves the gains. — [St. Louis Fed WP 2010-008](https://files.stlouisfed.org/files/htdocs/wp/2010/2010-008.pdf); [RePEc](https://econpapers.repec.org/RePEc:inm:ormnsc:v:60:y:2014:i:7:p:1772-1791)

### Inferences
- EVIDENCE (strong, dated): trend rules on the DJIA beat cash from 1897 to 1986 even after snooping correction. EVIDENCE (strong, negative): the same edge disappeared after about 1987 on the index and never showed up in futures, where costs are realistic. The likely explanations are publication decay and arbitrage, plus the fact that a 5-day moving average on a non-tradable index ignores costs and stale-price effects.
- The surviving pro-TA results (Han-Yang-Zhou, Neely et al.) are about moving averages as a trend or volatility filter, mostly in small, illiquid, high-volatility stocks or as an equity-premium forecaster. None of them supports discretionary pattern reading.
- The 56/20/19 "majority positive" count is weak evidence in itself: it is a vote count of studies that are subject to publication bias and the same snooping problems. A retail trader should start from zero edge for any published single-instrument TA rule after costs.
- Out-of-sample R-squared figures for the equity premium are typically around 1% a month (my recollection, not verified here). Even if real, that is a tilt in risk premium, not a high-Sharpe strategy.

### Gaps
- I could not extract BLL's own headline buy-minus-sell return spread, or Lo-Mamaysky-Wang's per-pattern statistics (for example, Kolmogorov-Smirnov results by pattern). Full text not accessed.
- I did not get Neely et al.'s exact out-of-sample R-squared values, or Han-Yang-Zhou's alpha in % per year and their transaction-cost-adjusted figures.
- I did not verify any post-2013 replications of Han-Yang-Zhou. Whether the high-volatility moving-average anomaly survives realistic costs in small caps is unknown.
- I found no rigorous academic test of Dow theory (a classic one by Brown, Goetzmann and Kumar, 1998, exists, but I did not retrieve it), and none of Wyckoff accumulation and distribution schematics.

---

## Q2. Can narratives be measured with news and text, and does narrative intensity predict returns or crashes?

### Takeaway
Narratives can now be measured. A topic model of WSJ articles explains about 25% of monthly stock-market variation in-sample, and about 18% out-of-sample. That figure is for the same month, not the next one, so it explains returns rather than predicting them. Text does help forecast macro variables (output and employment), and survey "crash beliefs" are measurable and strongly biased. Evidence that narrative intensity predicts future aggregate returns or crashes in a tradable way is thin. Google-search attention predicts short-lived price pressure that reverses, but the famous "Google debt" strategy has a hindsight-selection problem.

### Cited Findings

**Round 1: "Shiller says stories drive markets. Can anyone measure that?"**
- Bybee, Kelly, Manela and Xiu ("Business News and Business Cycles," NBER w29344, 2021; J. Finance 79(5), 2024) fit a topic model to WSJ text for 1984-2017. The abstract says "800,000" articles; the final dataset is 763,887 articles with an 18,432-term vocabulary. The model is optimal at 180 topics. They find "news attention closely tracks a wide range of economic activities and explains 25% of aggregate stock market returns." — [NBER w29344 PDF](https://www.nber.org/system/files/working_papers/w29344/w29344.pdf); [NBER page](https://www.nber.org/papers/w29344)

**Round 2: "Explains, or predicts? Can I trade it?"**
- It is contemporaneous. Footnote 3: "Our analysis focuses on explaining contemporaneous aggregate stock market fluctuations." The authors also say "such contemporaneous correlations have little to say about whether news text contains distinct or incremental information." With an expanding-window out-of-sample regression, the fit falls to 17.8% for market returns and 43.6% for market volatility, still for the same month. — [NBER w29344 PDF](https://www.nber.org/system/files/working_papers/w29344/w29344.pdf)
- Popular coverage overstated this. Nieman Lab reported that news coverage "predicts 25%" of stock-market fluctuations, but the paper's claim is explanation in the same month. — [Nieman Lab](https://niemanlab.org/?p=198140) vs [paper](https://www.nber.org/system/files/working_papers/w29344/w29344.pdf)
- Where text does predict: in a macro VAR, attention to the "recession" topic has "economically large and highly significant predictive power for future output and employment." A shock lowers output by up to 1.99% (1.25% when the topic is ordered last in the VAR) and employment by 0.92% (0.51%). In penalized forecasting models it beats economic policy uncertainty (EPU), the VIX and consumer sentiment. "Recession" and "problems" attention also drive market volatility. — [NBER w29344 PDF](https://www.nber.org/system/files/working_papers/w29344/w29344.pdf)
- The paper cites García (2013) for the finding that news sentiment forecasts stock returns, "especially during recessions." — [NBER w29344 PDF, fn. 3](https://www.nber.org/system/files/working_papers/w29344/w29344.pdf)

**Round 3: "What about crashes? Do crash narratives predict crashes?"**
- Goetzmann, Kim and Shiller (NBER w22143) used investor surveys from 1989 to 2015. The median investor put the chance of a 1929- or 1987-style crash in the next 6 months at about 10%. Historical data (1929-1988) suggest about 1.7%. They attribute the gap to availability bias, with the financial press shaping crash beliefs asymmetrically. — [NBER digest](https://www.nber.org/digest/jul16/w22143.html); [NBER w22143](https://www.nber.org/papers/w22143)
- On this evidence, crash narratives measurably distort beliefs, and the distortion runs toward overestimating crashes. That is evidence of mispriced fear, not of crash prediction.

**Round 4: "Is narrative economics itself testable?"**
- Portes (IMF F&D review) finds Shiller's narratives hard to turn into testable hypotheses, with "remarkably little reference to empirical evidence," and calls some of the causal claims a stretch. — [IMF F&D March 2020](https://www.imf.org/en/Publications/fandd/issues/2020/03/book-review-narrative-economics-portes)
- DeLong: "I could invent 1000 narrative 'theories' to fit any set of time series data." — [Econlib post](https://www.econlib.org/archives/2017/04/heterodoxy_at_t.html)
- Shiller himself says narrative-based forecasts can become narratives in turn, and the process "has a random component." — [NPR 2019](https://www.npr.org/2019/10/16/770686962/how-stories-shape-the-economy)

**Round 5: "Attention data, such as Google Trends: is that a usable crowd-story signal?"**
- Da, Engelberg and Gao ("In Search of Attention," J. Finance 2011) introduced Google's Search Volume Index (SVI) as a direct measure of retail attention. A rise in SVI predicts higher prices over the next couple of weeks, followed by a reversal. — [working paper](https://rady.ucsd.edu/faculty/directory/engelberg/pub/portfolios/GOOGLE.pdf). A later paper reports that the price pressure and reversal are significant only among smaller stocks. — [WHU paper](https://opus4.kobv.de/opus4-whu/files/697/Can_retail_investor_attention_enhance_market_efficiency_2015.pdf). This is a secondary description; I did not verify the effect sizes.
- Preis, Moat and Stanley (Sci. Reports 2013) tested 98 search terms over 2004-2011. The best, "debt," produced a 326% gain. Sornette's objection: how would anyone have known in advance to pick "debt"? That makes it the best of 98 tries, with no snooping correction. — [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3635219); [Nature news](https://www.nature.com/news/counting-google-searches-predicts-market-movements-1.12879)

### Inferences
- EVIDENCE: narratives measured from text track the economy and explain a large share of same-month returns, about 18% out of sample. That is a breakthrough in explanation (the Roll 1988 puzzle), not a trading signal.
- EVIDENCE (weak or mixed): text and attention predict macro variables, volatility, and short-horizon retail price pressure in small stocks, which then reverses. The reversal itself is the tradable part, and it favours fading the attention spike, not riding it.
- BELIEF: that measured narrative intensity gives tradable early warnings of crashes. I found no out-of-sample evidence. The one quantified crash-narrative result (Goetzmann-Kim-Shiller) shows the crowd overestimates crash odds about 6-fold (10% vs 1.7%), which suggests selling crash fear, not buying it.
- Keynes' beauty contest (prices reflect what people expect others to expect) is consistent with attention-driven price pressure. In the evidence above, though, it shows up as temporary pressure that reverses, not as persistent trends a chartist can ride.

### Gaps
- I did not retrieve Manela and Moreira's "News Implied Volatility" (NVIX; J. Financial Economics 2017), which reportedly finds that text-based uncertainty predicts returns, especially at war and disaster times. Unverified here.
- I found no formal Challet-style replication of Preis et al. in this session. Search did not surface it.
- García (2013) effect sizes, and the post-publication performance of SVI strategies, are not quantified here.
- I found no study testing whether Shiller-style "viral" narrative counts (for example, Google Ngram bubble words) predict index drawdowns out of sample.

---

## Q3. Why do Elliott wave and Fibonacci lack evidence, and are any self-fulfilling price-level effects (round numbers, 52-week highs, support/resistance) measurable?

### Takeaway
Elliott wave and Fibonacci ratios have essentially no rigorous peer-reviewed support. Wave counts are subjective and flexible enough to fit any path after the fact. Price-level effects with plausible mechanisms are well documented. In FX, stop-loss and take-profit orders cluster at round numbers (Osler, NY Fed), which makes trends reverse at published support/resistance and accelerate after a break. In stocks, retail order flow is lopsided around whole-dollar prices (100M+ trades), and the 52-week high acts as an anchor that predicts returns better than standard momentum. The first group is a belief system; the second is measurable order-flow microstructure.

### Cited Findings

**Round 1: "Make the case for Elliott wave and Fibonacci."**
- Peer-reviewed tests of Elliott wave counts are very rare. One evidence review cites Batchelor and Ramyar (2006), "Magic Numbers in the Dow," as the most rigorous test of Fibonacci ratios. It argues that searching thousands of wave and ratio combinations will produce apparent predictive power in hindsight by chance alone. — [evidencefinance review (unrefereed)](https://evidencefinance.neocities.org/elliotwave). I did not verify Batchelor-Ramyar's numbers directly; my recollection is that they found no excess Fibonacci-ratio frequency in Dow swings, but that is unconfirmed here.
- Critics describe Elliott wave as pareidolia, meaning seeing patterns in noise. — [Wikipedia: Elliott wave principle](https://www.wikipedia.org/wiki/Elliot_wave)
- The Fibonacci retracement evidence comes from small, low-quality studies with mixed results. A Pakistan cement-sector study finds reversals follow the ratios "to some extent." [IDEAS](https://ideas.repec.org/a/arp/ijefrr/2018p159-164.html) A HKUST student project on Vanguard ETFs finds Fibonacci trading "significantly underperforming" buy-and-hold. [HKUST](https://cse.hkust.edu.hk/~rossiter/independent_studies_projects/fibonacci_trading/fibonacci_trading.pdf) An energy and crypto study reports gains over buy-and-hold with no snooping control. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8752186)

**Round 2: "Fine, but traders do watch levels. Is there a measurable self-fulfilling level effect?"**
- Osler (NY Fed Staff Report 125; J. Finance 2003) studied about 9,700 stop-loss and take-profit orders at a large dealing bank (September 1999 to April 2000). Take-profit orders cluster strongly at round numbers, which explains why trends reverse at support and resistance. Stop-loss orders cluster just beyond round numbers, which explains why trends accelerate once a level breaks. — [NY Fed SR125](https://www.newyorkfed.org/research/staff_reports/sr125); [J. Finance 2003 (IDEAS)](https://ideas.repec.org/a/bla/jfinan/v58y2003i5p1791-1819.html)
- Osler (Economic Policy Review, 2000) tested support and resistance levels that six FX firms published to clients and concluded they "are effective" at predicting where intraday trends stop. — [NY Fed EPR 2000](https://resources.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.pdf); [NY Fed press note](https://www.newyorkfed.org/newsevents/news/research/2000/rp000622a)
- Osler, SR150 ("Stop-loss orders and price cascades"): executed stop-loss sells cluster just below round numbers and stop-loss buys just above. Using high-frequency DEM, JPY and GBP quotes from 1996 to 1998, trend-acceleration effects after round-number crossings are consistent with stop cascades. Osler cautions that the statistics cannot prove causation. — [NY Fed SR150](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.html)

**Round 3: "Does this replicate in equities, with more data?"**
- Bhattacharya, Holden and Jacobsen (2012, Management Science) studied more than 100 million US stock trades. Liquidity demanders buy too much one cent below round numbers and sell too much one cent above them. The imbalance scales with how round the number is: largest at whole dollars, then half dollars, and so on. The authors call this a "threshold trigger effect" when a price crosses a round number, and estimate liquidity demanders lose close to $1B a year. — [SSRN](https://papers.ssrn.com/ab_id=1569922); [Holden PDF](https://host.kelley.iu.edu/cholden/Bhattacharya%20Holden%20and%20Jacobsen%20(2012).pdf); [EconPapers](https://econpapers.repec.org/RePEc:inm:ormnsc:v:58:y:2012:i:2:p:413-431); [HKUST summary](https://bm.hkust.edu.hk/bizinsight/2017/03/penny-wise-dollar-foolish)
- George and Hwang (2004, J. Finance): ranking stocks by nearness to their 52-week high (long near-high, short far-from-high) "explains a large portion of the profits from momentum investing" and beats conventional momentum. They attribute it to anchoring and underreaction; follow-up work finds standard risk factors do not explain it. — [typeset.io copy](https://typeset.io/pdf/the-52-week-high-and-momentum-investing-4u9j16d52p.pdf); [Alpha Architect summary](https://alphaarchitect.com/2014/11/the-secret-to-momentum-is-the-52-week-high)

**Round 4: "So which chartist levels have real support?"**
- Round numbers and where orders cluster around them: supported in FX (Osler) and stocks (BHJ). Anchors like the 52-week high: supported (George-Hwang). Support/resistance from traders' own lines: Osler's 2000 test of published FX levels is positive, but intraday and over a 1990s sample. Fibonacci and Elliott ratios: not supported. STW's 7,846-rule universe included support/resistance and channel-breakout (Dow-theory "line") rules, which shared the general post-1986 failure on the DJIA. — [STW 1999](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf)

### Inferences
- The believers win on mechanism, not mysticism. Levels matter where many people put resting orders: round numbers, obvious highs and lows, published levels. Those effects are microstructure (stop cascades, take-profit walls) and are measured in cents and pips at intraday horizons. That is the domain of market makers with order-book data, not retail swing traders.
- The BHJ result cuts against retail traders. Liquidity takers who react to round-number thresholds are the side that loses about $1B a year, so the retail crowd that believes in levels pays for the effect rather than capturing it.
- 52-week-high anchoring is a monthly-horizon, cross-sectional factor (a relative of momentum), not a single-chart signal. It has been widely known since 2004, so expect decay similar to other published anomalies.
- Elliott wave and Fibonacci stay BELIEF. Their flexibility (wave counts can be re-labelled after the fact) makes them close to unfalsifiable, which is itself the main rebuttal.

### Gaps
- I did not obtain Osler's quantitative hit rates (for example, the share of times published levels stopped trends versus artificial random levels) or the size of post-break moves.
- I did not retrieve Batchelor-Ramyar (2006) directly, nor any study of Wyckoff schematics.
- I did not examine whether the 52-week-high effect survives after 2004. Some later literature (for example, on short-term reversals and the 52-week-high ratio, [J. Empirical Finance 2024](https://ideas.repec.org/a/eee/empfin/v79y2024ics0927539824000902.html)) exists but was not reviewed.
- I found no source on index-level round-number "resistance" (for example, Dow 10,000 or S&P round thousands). The Donaldson-Kim search returned nothing.
