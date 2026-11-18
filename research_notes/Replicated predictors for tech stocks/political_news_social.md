# Political, News, Social-Media and Prediction-Market Signals as Predictors of US Mega-Cap Tech Returns

Scope note: about 20 search/fetch calls. Two primary PDFs (FEDS 2026-010 and NBER w26308) would not parse with the fetch tool, so findings from them come from abstracts or search snippets and are marked as such. Overall conclusion for a daily-rebalancing retail system with minutes of data lag: **almost every documented effect here is minutes-scale and is priced before a daily-close system can act. The only slower-moving pieces are (a) LLM/news-sentiment drift, concentrated in small caps and shrinking, and (b) attention measures (Google SVI) on 1-2 week horizons, with reversal afterward. For mega-cap tech, treat these signals as regime/volatility conditioners, not as return alphas.**

## Trump posts (Twitter 2018-2021, Truth Social 2022-2026) and tariff/trade announcements: measured impact and pricing speed

### Takeaway
Trade-war and tariff posts have a measurable, statistically significant **minute-scale** effect on US indices and volatility. Pricing happens within minutes, and in 2026 some of it happens *before* the post (possible leakage). The evidence for a stock-index effect from tariff tweets is itself contested (Bianchi-Kind-Kung find it negligible), and large announcements like Liberation Day were priced as macro shocks within the session, then reversed by policy U-turns. No source shows next-day drift that a daily-close system could capture.

### Cited Findings
- *Decision Support Systems* (2021), "Do President Trump's tweets affect financial markets?" uses exact tweet timestamps with high-frequency data. Tweets are followed by higher uncertainty, more trading and a decline in the US stock market. Topic modeling shows **most topics have no effect**, and the US market responds only to "trade war" tweets. The authors report positive abnormal returns from an automated trading system, which by construction trades intraday. — [datalearner summary of DSS paper](https://datalearner.com/academic/journal-papers/0167-9236/volumes-and-issues/309/paper-detail/4951)
- Another study of more than 3,200 tweets finds US-China trade-war tweets negatively predict S&P 500 returns and positively predict VIX, with Granger causality running from tweets to returns. — [search summary; Applied Economics Letters via RePEc](https://econpapers.repec.org/RePEc:taf:apeclt:v:27:y:2020:i:18:p:1485-1488)
- **Contradicting evidence:** NBER w26308 (Bianchi, Kind and Kung) reports that presidential tweets on trade and tariff policy have, on average, a *negligible* effect on the stock market. This comes from the search snippet because the PDF could not be parsed. — [NBER w26308](https://www.nber.org/system/files/working_papers/w26308/revisions/w26308.rev2.pdf)
- An event study of Trump tweets uses a **30-minute event window** with intraday index data, which is the standard design and shows the horizon researchers consider relevant. — [ResearchGate, "Presidential Attack Risk"](https://www.researchgate.net/publication/372293654_Presidential_Attack_Risk_The_Impact_of_Trump's_Tweets_on_Financial_Markets)
- Tweets flagged by Twitter as false or misleading are associated with significant abnormal returns, higher intraday volatility and volume surges in S&P 500 firms, with stronger effects in policy-sensitive industries. — [Journal of Media Economics 2026](https://www.tandfonline.com/doi/full/10.1080/08997764.2026.2617248)
- **Truth Social 2026, minute-level study (pre-print, not peer-reviewed):** It covers 1,341 posts from Jan 25 to Apr 8, 2026, matched to minute-level US equity ETF and oil data, with matched controls and a 24h-shift falsification test. It finds 15 events with unusual trading, and **only oil-related posts** produced abnormal activity. In several events prices moved sharply **in the minutes before** the post, for example a sell-off about 20 minutes before an Iran post. The odds of these patterns by chance are reported as about one in a billion. The CFTC is reportedly investigating. Code and data are on GitHub. — [The Conversation](https://stories.theconversation.com/the-market-moves-before-trump-posts/)
- An Axios review of 269 Iran-related posts found **average 5-minute futures moves of 0.73%** after posts, against a 0.2% average 5-minute move overall. The secondary source also says reactions are becoming "less durable." — [CoinEdition citing Axios](https://coinedition.com/how-trumps-truth-social-posts-moved-bitcoin-stocks-and-oil-in-2025-and-2026/)
- **Liberation Day (Apr 2, 2025):** Ivo Welch finds many of the most tariff-exposed assets did not fall while many of the least exposed did. Losses were too large to be explained by tariffs alone, so markets priced a macro shock. — [SSRN, Welch](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6855298)
- Firms with higher tariff exposure (from corporate filings) had significantly lower short-term abnormal returns around Apr 2, 2025. — [Economics Letters / ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S016517652500624X)
- The Nasdaq-100 fell as much as 4.91% intraday during the Liberation Day sell-off. A 90-day pause announcement later sparked a same-day relief rally. — [Betashares timeline](https://www.betashares.com.au/insights/liberation-day-upended-markets/); index closes from secondary sources (S&P -4.8%, Nasdaq Comp. about -6% on Apr 3) — [Wikipedia](https://en.wikipedia.org/wiki/Liberation_Day_tariffs)
- Commercial real-time tools exist, such as the TipRanks Trump dashboard and Trump Post Alert, which sells AI alerts. They are products, not evidence. — [TipRanks](https://www.tipranks.com/trump-dashboard), [Trump Post Alert](https://trumppostalert.com/)

### Inferences
- **Decay speed is minutes.** Every rigorous design uses windows of 5 to 30 minutes. A retail system with minutes of lag is competing with HFT and possibly informed pre-post traders, so the post-release edge is near zero.
- The pre-post moves in 2026 mean the post timestamp is *not* the information-arrival time. Any backtest keyed on post time will overstate post-release predictability.
- For mega-cap tech, the tradable use is **risk management**: a count of tariff or trade-war posts, or a keyword-scored daily aggregate, as an input to a volatility-target or exposure scaler. This fits the repo's existing 25% vol-target design. It is not an expected-return signal.
- The large tariff shocks (Liberation Day, then the pause) show sign reversals within days, so a daily "fade or follow" rule would face regime-dependent signs.

### Gaps
- I found no peer-reviewed study of Truth Social posts against **individual mega-cap tech stocks** (AAPL, NVDA and others) with next-day horizons.
- I could not parse the exact effect sizes in NBER w26308. My recollection is that its main contribution concerns Trump tweets about the Fed moving fed funds futures, but that is unverified here.
- I found no study measuring how the decay speed of the post effect changed from 2018 to 2026.

## Elon Musk posts, TSLA and SpaceX (SPCX)

### Takeaway
The evidence is mixed and mostly comes from student theses. Some find a statistically significant same-day effect on TSLA. Others, including the most careful design found, find no effect once confounding news is controlled. No reliable evidence shows multi-day predictability. SPCX began trading on Jun 12, 2026, and there is no study yet.

### Cited Findings
- Princeton thesis: Musk tweets have a statistically significant effect on Tesla and EV rivals, with "limited to no evidence" that returns on surrounding days are affected. — [Princeton DataSpace](https://dataspace.princeton.edu/handle/88435/dsp01r781wk23g)
- Corvinus study of 3,158 tweets and 2,420 trading days (33 events): **no significant impact** on TSLA, consistent with informational efficiency. It excludes pre-event days contaminated by fundamental news. — [Corvinus Journal](https://cjssp.uni-corvinus.hu/index.php/cjssp/article/download/977/pdf_1)
- Portuguese master's thesis: could not reject a zero effect of Musk tweets on TSLA returns. — [IPP repository](https://recipp.ipp.pt/bitstreams/7abfce04-d799-4bee-8ad8-0e401f7f8d88/download)
- Georgia Southern thesis: Tesla-related tweets increase abnormal returns, but more tweets per day reduce the absolute effect. — [Georgia Southern](https://digitalcommons.georgiasouthern.edu/honors-theses/850/)
- **SpaceX IPO:** It listed on Nasdaq as **SPCX** on Jun 12, 2026, at a $135 fixed offer price, raising about $75B on roughly 555M shares, the largest IPO ever. It opened at $150 and traded as high as $168.75 on the first day. — [Built In](https://builtin.com/articles/spacex-ipo-valuation-20260612), [Michigan Public/NPR](https://www.michiganpublic.org/2026-06-12/spacex-stock-lifts-off-rising-above-its-ipo-price), [Stocktwits](https://stocktwits.com/news-articles/markets/equity/spacex-ipo-pricing-135-per-share-will-value-the-rocket-maker-at-1.77-trillion/cZ0jlpNReUn)
- Before the IPO, Musk answered a report of a lowered valuation target with a one-word "false" on X, an example of the CEO post as a price-relevant denial. — [Basenor](https://basenor.com/blogs/news/musk-denies-spacex-lowered-its-ipo-target-price)

### Inferences
- Treat Musk posts as **noise for a daily system**. Any effect is same-day, concentrated in the minutes after posting, and not robust across studies.
- SPCX has under 6 months of history, too short for any event study. Its index inclusion and lock-up expiries are likely to dominate flows more than posts do.

### Gaps
- I found no peer-reviewed, intraday, post-2022 study of Musk's X posts against TSLA, and none for SPCX.
- I found no study of whether Musk posts help predict TSLA volatility, which would be the more plausible use.

## Polymarket / Kalshi odds (Fed, recession, tariffs, elections): do they lead equities?

### Takeaway
Fed research shows Kalshi is an **accurate, real-time macro-expectations gauge**: perfect FOMC-eve record, smaller CPI errors than the Bloomberg consensus, and the only market-based source for GDP, payrolls and unemployment expectations. I found **no study showing prediction-market odds changes lead equity returns**. The documented lead-lag runs *between* prediction venues (Polymarket leads Kalshi in politics). Usable as features, unproven as alpha.

### Cited Findings
- Diercks, Katz and Wright, "Kalshi and the Rise of Macro Markets" (FEDS 2026-010, Feb 2026; a later version dated Sep 20, 2026 appears at the ECB conference). The **Kalshi median and mode had a perfect record the day before FOMC meetings**, a statistically significant improvement over fed funds futures. Kalshi also has significantly smaller headline CPI forecast errors than the Bloomberg consensus and is the only market-based forecast source for GDP, core inflation, unemployment and NFP. The authors recommend using it for risk-neutral PDFs of FOMC decisions. — [Fed FEDS page](https://federalreserve.gov/econres/feds/kalshi-and-the-rise-of-macro-markets.htm); [National Law Review summary](https://natlawreview.com/article/federal-reserve-researchers-find-prediction-markets-deliver-forecasting-value); [ECB copy](https://www.ecb.europa.eu/press/conferences/shared/pdf/20261005_monpolconf/Wright_paper.pdf)
- The FEDS abstract page does **not** discuss equities or whether Kalshi reacts faster than futures. — [Fed FEDS page](https://federalreserve.gov/econres/feds/kalshi-and-the-rise-of-macro-markets.htm)
- Ng, Peng, Tao and Zhou (SSRN 5331995) find Polymarket outperforms polls and leads Kalshi in price discovery for politics, while Kalshi leads in sports. Over 2023-2026 price discovery is bidirectional, and large cross-venue discrepancies persist. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995)
- Accuracy varies by venue. One study reports Polymarket correct on 67% of markets, Kalshi 78% and PredictIt 93%. — [DL News](https://www.dlnews.com/articles/markets/polymarket-kalshi-prediction-markets-not-so-reliable-says-study/)
- Bürgi, Deng and Whelan find an average pre-fee contract return of **-20%** on Kalshi, consistent with longshot bias and noisy prices at extremes. — [UCD WP2025_19](https://www.ucd.ie/economics/t4media/WP2025_19.pdf); [VoxEU](https://cepr.org/voxeu/columns/economics-kalshi-prediction-market)
- The 2026 Truth Social study notes about $7B bet across exchanges and instruments around posts, with possible informed trading before posts, so prediction and futures markets can contain leaked information. — [The Conversation](https://stories.theconversation.com/the-market-moves-before-trump-posts/)

### Inferences
- For Fed outcomes, Kalshi carries roughly the same information as fed funds futures, which equities already price continuously. An odds change is therefore more likely *contemporaneous* with equity moves than leading.
- Plausible niche uses are recession, tariff and shutdown contracts, where no futures market exists. A daily change in recession or tariff odds could be tested as a regime or vol feature. This must be validated in-house because no published equity-return evidence exists.
- Longshot bias means raw probabilities near 0 or 1 are miscalibrated. Use changes or mid-range contracts.

### Gaps
- I found no academic or practitioner study (2024-2026) testing whether Polymarket or Kalshi odds Granger-cause S&P/Nasdaq or mega-cap returns at any horizon.
- I could not read the FEDS 2026-010 section on news responses because the PDF would not parse.

## News sentiment (RavenPack, LLM-scored headlines, GDELT), Reddit/WSB, Google Trends: which survive out-of-sample in large caps?

### Takeaway
LLM-scored headlines (Lopez-Lira and Tang) predict returns out-of-sample, but the tradable part is the post-reaction **drift, concentrated in small stocks and negative news, and shrinking as LLM adoption rises**. RavenPack-era evidence agrees that news predictability is short-horizon and lives in weak-information stocks, so mega-cap tech is the worst case. WSB sentiment shows weak correlation outside meme stocks. Google SVI predicts 1-2 week returns and then reverses, mainly through small-cap retail attention. None has strong out-of-sample evidence for mega-cap tech at a daily horizon.

### Cited Findings
- **Lopez-Lira and Tang (arXiv 2304.07619 v6):** Using post-cutoff headlines, GPT-4 achieves about a **90% portfolio-day hit rate on the "non-tradable initial reaction."** GPT-4 scores also predict subsequent drift, **"especially for small stocks and negative news."** Abstract: **"Strategy returns decline as LLM adoption rises, consistent with improved price efficiency."** — [arXiv v6 abstract](https://arxiv.org/abs/2304.07619v6)
- Earlier version: Oct 2021 to May 2024, 4,123 US stocks, long-short on overnight news earns **about 34 bps/day before costs**. Effects are stronger in smaller stocks. — [search summary of arXiv v5/v6](https://arxiv.org/pdf/2304.07619v5.pdf). An AI-aggregator claim that Sharpe fell from 3.8 to 1.22 by early 2024 is **unverified**. — [pulse.bot (low reliability)](https://www.pulse.bot/ai/blogs/can-chatgpt-forecast-stock-price-movements-680b3dee-231f-4644-b717-0fb80e1ea03a/)
- Chen, Tang, Zhou and Zhu (2025): ChatGPT scoring of WSJ headlines (1996-2022) has aggregate market-level predictive power, while a simple negative-news ratio does not. — [arXiv 2502.10008](https://pdf.arxiv.org/pdf/2502.10008)
- RavenPack (2000-2014): news-driven predictability is significant only at **short horizons** and in stocks with poor information environments (small, low analyst coverage, low institutional ownership). — [AEA 2017 paper](https://aeaweb.org/conference/2017/preliminary/paper/G46EGhsb)
- Ke, Kelly and Xiu (text-based sentiment versus RavenPack-style scores): news about small and volatile stocks takes roughly **twice as long** to be fully priced, and price responses are about 4x larger for below-median-size stocks. — [Nottingham seminar version](https://www.nottingham.ac.uk/economics/documents/seminar-papers/senior/2020/xiu-18-11-20.pdf)
- Sentiment factors built over longer horizons are more persistent and may be useful for long-term management. — [EFMA 2020](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2020-Dublin/papers/EFMA%202020_stage-1301_question-Full%20Paper_id-515.pdf)
- **Reddit/WSB:** a 2025 arXiv study of GME and AMC finds sentiment only weakly correlated with prices, while comment volume and Google search trends are stronger signals. — [arXiv 2507.22922](https://arxiv.org/abs/2507.22922v1). Other work finds no alpha from simply following the subreddit's picks. — [Alpha Architect / Swedroe](https://alphaarchitect.com/retail-investors/). WSB is predictive for GME with out-of-sample checks, but only for a meme stock. — [Springer](https://link.springer.com/content/pdf/10.1007/s42521-023-00084-y.pdf)
- **Google Trends:** Da, Engelberg and Gao (JF 2011) find that a rise in SVI for Russell 3000 stocks (2004-2008) predicts higher prices over the **next two weeks**, with subsequent reversal. The reversal detail comes from a summary and replications rather than the paper text I read. — [working paper PDF](https://rady.ucsd.edu/faculty/directory/engelberg/pub/portfolios/GOOGLE.pdf); [EUR thesis summary](https://thesis.eur.nl/pub/73285/Thesis-Berend-van-Hessen-Final-.pdf). Search-based FEARS sentiment predicts market-level reversal over the next few days. — [Da, Engelberg, Gao RFS 2015](https://www3.nd.edu/%7Epgao/papers/Rev.%20Financ.%20Stud.-2015-Da-1-32.pdf)

### Inferences
- **Mega-cap tech is the hardest place for news signals.** It has the most coverage, the fastest pricing and the most LLM-equipped competitors. The papers' own decomposition shows the "initial reaction" (minutes to same session) is the bulk of the effect and is non-tradable.
- The most defensible daily use is to score **overnight** headlines (published after the close) before the next open or close. That is the Lopez-Lira design. Expect only a few bps per day at best in large caps, before costs, and a decaying edge.
- GDELT and Reddit are free inputs for attention or volume features. Sentiment polarity adds little, while volume or attention adds more and mostly in small or meme names.
- Google SVI on mega-caps is saturated: the names are always searched, so abnormal-SVI shocks are rare and mostly coincide with earnings or news already priced.

### Gaps
- I found no paper isolating LLM-headline predictability within the top-50 market-cap stocks after 2024.
- I could not verify GDELT's 2026 status, update cadence or any large-cap OOS study using GDELT tone.
- I found no published large-cap OOS test of WSB or Google Trends since 2023.

## Free/legal historical data sources and API costs (as of 2026)

### Takeaway
Prediction-market data is the cheapest and cleanest source, with free public read APIs. X is now pay-per-use at about $0.005 per post read with monthly caps, so modest monitoring of a few accounts is cheap but full-archive backfills are not. Truth Social has no official API. Options are paid scrapers (gray area under the ToS) or academic datasets.

### Cited Findings
- **X API:** pay-per-use with no subscription or minimum. The free tier closed to new signups on Feb 6, 2026 according to one source. Reads cost about **$0.005 per post**, with a monthly read cap of 2M or 3M according to conflicting third-party sources. Above the cap, Enterprise pricing is unpublished. Posting costs about $0.01-0.015, or $0.20 with a URL. X says the Developer Console shows the authoritative rates. — [Postproxy](https://www.postproxy.dev/blog/x-api-pricing-2026/), [OpenTweet](https://opentweet.io/x-api-pricing), [bundle.social](https://bundle.social/blog/x-api-pricing-2026-costs-limits), [apiserpent](https://apiserpent.com/blog/free-twitter-x-api) (all third-party; cap figures conflict)
- **Truth Social:** no official API. Paid Apify scrapers export JSON. One charges about **$2 per 1,000 posts** and its sample output includes `realDonaldTrump`. — [Apify](https://apify.com/scrapevanta/truth-social-post-extractor). A free Zenodo Truth Social dataset (2023, about 165 MB) exists. — [Zenodo 7531625](https://zenodo.org/records/7531625). An academic 2024-election dataset holds 1.5M posts from Feb to Oct 2024. — [ISI/USC](https://www.isi.edu/results/publications/15607/unfiltered-conversations-a-dataset-of-2024-us-presidential-election-discourse-on-truth-social/)
- **Polymarket:** free read APIs with no authentication. CLOB `/prices-history` returns per-market price series, the Data API `/trades` returns trade history (10,000 rows per query), and Gamma API keeps closed markets queryable. **Kalshi:** public candlesticks, trades and historical-archive endpoints are free, with a live/historical cutoff. Dune has free Polymarket tables (including hourly prices) and Kalshi aggregates. — [PredictionHunt](https://www.predictionhunt.com/blog/polymarket-kalshi-historical-data), [Dune](https://dune.com/data/prediction-markets), [Oddpool Kalshi docs](https://docs.oddpool.com/kalshi/overview.md)
- The Trump 2026 minute-level study published its code and data on GitHub, which gives a ready-made timestamped post set for Jan-Apr 2026. — [The Conversation](https://stories.theconversation.com/the-market-moves-before-trump-posts/)

### Inferences
- **Cheapest viable stack for this repo:**
  - Kalshi and Polymarket official APIs, free, for daily snapshots of Fed, recession and tariff odds.
  - An X pay-per-use account for a handful of accounts (Trump cross-posts, Musk, company handles). A few thousand reads a month cost tens of dollars.
  - GDELT, free, for news-volume and tone features.
  - Google Trends through unofficial libraries. These are rate-limited and the data is sampled and renormalized per query.
- **Legality:** official APIs are clean. Scraping Truth Social or X violates their ToS, which is a contract issue rather than clearly illegal for public data in the US. It is still a dependency risk because scrapers break.
- **Point-in-time hygiene:** store your own snapshots with retrieval timestamps. Vendor and API histories may be revised or backfilled, and the 2026 pre-post moves show the publication timestamp is not the information time.

### Gaps
- The official X pricing page (docs.x.com) was not fetched. Read caps conflict across third-party sources (2M versus 3M).
- I did not verify GDELT 2026 availability or cost, which has historically been free via BigQuery and raw files.
- I found no confirmed source for full-history Trump Truth Social posts (2022-2026) as a free official download.
- I did not research the cost of RavenPack or other commercial news-sentiment feeds. They are institutionally priced and not published.
