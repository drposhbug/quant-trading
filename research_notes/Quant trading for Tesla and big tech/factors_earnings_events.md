# Factor Models and Earnings/Event-Driven Strategies for TSLA and Mega-Cap Tech (AAPL, MSFT, NVDA, GOOGL, AMZN, META)

Research date: 2026-11-18. About 16 tool calls. Two primary pages (Martineau CFR, IIMB "Disappearing EAP") returned HTTP 403, so some claims rest on search abstracts or snippets. These are flagged.

## Q1. Factor models (FF5, q-factor, AQR): computing single-stock exposures, free factor data, and which factors matter for these names

### Takeaway
Free daily factor returns are easy to get: Ken French (FF3/FF5/Mom/reversal, daily), AQR (QMJ, BAB, HML Devil, daily), and global-q.org (q4/q5). Single-stock exposures come from a rolling time-series regression of excess returns on those factors. For the Mag-7, the published exposures are consistent: high market beta (TSLA and NVDA the highest), large size (negative SMB), negative value, positive quality/profitability, and frequently strong momentum. Most of their outperformance, though, has been residual (stock-specific) return, not factor return. Factors explain how these stocks are exposed. They are weak tools for timing them.

### Cited Findings
- The Ken French Data Library offers Fama/French 3 factors (monthly, weekly, daily), Fama/French 5 factors 2x3 (adds RMW and CMA; monthly and daily), Momentum, Short-Term Reversal and Long-Term Reversal (monthly and daily), plus Developed/regional sets. Data on the page ran through Sept 2026. US research returns switched to the CRSP CIZ (Flat File 2.0) format from the Jan 2025 release — [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
- AQR publishes daily Quality Minus Junk factors (Asness, Frazzini, Pedersen 2014), daily Betting-Against-Beta factors for the US and 23 international markets, and daily HML Devil, all as Excel workbooks. The listing pages show conflicting "last updated" dates (Jul 31 vs Aug 31, 2026) — [AQR Datasets](https://www.aqr.com/Insights/Datasets); [AQR QMJ Daily](https://www.aqr.com/Insights/Datasets/Quality-Minus-Junk-Factors-Daily); download URLs are hard-coded in the R package aqqr — [aqqr source](https://rdrr.io/github/Reckziegel/aqqr/src/R/factors_daily.R)
- Frazzini's NYU data library moved to AQR in Nov 2014. Use AQR's own page — [Frazzini Data Library](https://pages.stern.nyu.edu/~afrazzin/data_library.htm)
- The Hou-Xue-Zhang q-factor (q4) and Hou-Mo-Xue-Zhang (2020) q5 data (adds an expected-growth factor) are sourced from global-q.org. The authors provide daily, weekly and other frequencies. One R mirror's copy covers 1967-01 to 2019-12, so pull directly from global-q.org for current data — [ExpectedReturns Q5 docs](https://rdrr.io/github/JustinMShea/ExpectedReturns/man/Q5.monthly.html); [Which-factors vignette](https://rdrr.io/github/JustinMShea/ExpectedReturns/f/vignettes/Which-factors.Rmd); [q5 NBER w24709](https://www.nber.org/papers/w24709.pdf)
- The Python package `getfactormodels` wraps FF, q-factor and other libraries in one downloader — [getfactormodels GitHub](https://github.com/x512/getfactormodels)
- Two Sigma's Venn analysis (2015-2025): the Mag-7 had beta above 1 to the equity factor over the past decade. Tesla's beta was 1.95 and Nvidia's 1.84 (the highest). Much of the outperformance came from residual returns, "the hardest component to predict or replicate systematically" — [Two Sigma Venn](https://www.venn.twosigma.com/insights/quantifying-the-magnificence-of-the-magnificent-7)
- BlackRock (exposures as of 6/30/2023): the Mag-7 is the largest weight in the quality factor. Quality (profitability) was the only factor to beat the market in 2023. The group has high exposure to large size and negative exposure to value, strong momentum (especially NVDA and META), and negligible weight in min-vol, value and small size — [BlackRock: Factors & the Magnificent Seven](https://blackrock.com/us/individual/investment-ideas/what-is-factor-investing/factor-commentary/andrews-angle/factors-and-magnificent-seven); [Advisor Perspectives repost](https://www.advisorperspectives.com/commentaries/2023/09/07/factors-magnificent-seven-blackrock)
- Firstlinks describes the group as rich in size, quality, momentum and growth factors. ETF Action (2026) argues the Mag-7 is "not one factor", with very different returns across the seven — [Firstlinks](https://www.firstlinks.com.au/article/challenges-for-the-magnificent-seven-stocks); [ETF Action](https://www.etfaction.com/mag-7-unbundled-dispersion-valuation-and-equal-weights-turn/)

### Inferences
- How to compute exposures: regress daily (or weekly) excess returns `r_i - RF` on `[Mkt-RF, SMB, HML, RMW, CMA, Mom]` (French), optionally adding QMJ/BAB (AQR) or swapping in q5 (ME, IA, ROE, EG). Use rolling 252-day (daily) or 36-60-month (monthly) OLS windows. Expect TSLA's loadings to be unstable and to carry a low R^2, because idiosyncratic variance dominates.
- Because these are 6-7 stocks all in the "big" size bucket, cross-sectional factor sorts within the group are statistically meaningless. Factors are better used for (a) risk decomposition and hedging (strip out market beta and momentum), (b) building residual-return signals, and (c) inverse-vol or beta-neutral weighting. Low-vol/BAB logic argues for underweighting TSLA and NVDA relative to MSFT and AAPL on a risk basis.
- The value and investment (CMA) factors load negatively on almost all of these names. A value tilt within the group means "less NVDA/TSLA", not a clean alpha signal.

### Gaps
- I found no peer-reviewed study of factor timing within the Mag-7 specifically.
- I did not fetch the French variable-definitions page. Standard RMW (operating profitability) and CMA (asset growth) definitions come from FF (2015), not from a source checked here.
- The current global-q.org file list and update date were not verified (the site itself did not appear in search results).

## Q2. Earnings announcement effects: pre-earnings drift, PEAD on mega caps, surprise/revision signals, implied vs realized move

### Takeaway
PEAD is essentially dead for large caps: Martineau (CFR 2022) reports no drift in large stocks since about 2006, because prices absorb the surprise on the announcement day. The earnings announcement premium (Savor-Wilson, about 9.9% annualized abnormal return for firms scheduled to announce) is the better-documented pre-event effect, but later work says it is fading or shifting. Analyst-revision momentum has support in academic work, but evidence that it survives in large caps is thin. Options-implied earnings moves are, on average, larger than realized moves (vendor studies only), but the edge is name-specific. NVDA's implied move overstated the realized move in 14 of 20 quarters, while META's realized move exceeded implied in 6 of 12.

### Cited Findings
- Martineau, "Rest in Peace Post-Earnings Announcement Drift" (Critical Finance Review 2022): for large stocks PEAD has been non-existent since 2006. It disappeared more recently for microcaps. Prices now incorporate the surprise on the announcement date (abstract only; full text returned 403) — [CFR listing](https://nowpublishers.com/article/Details/CFR-0122); [IDEAS](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html)
- A Columbia CEASA paper (Zhao 2022) finds PEAD declined significantly. Beyond the standard "more arbitrage capital" explanation, it offers declining earnings persistence as an alternative — [PEAD Declined over time (Columbia)](https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf)
- Dissent: a 2026 Penman and Zhu paper revisits PEAD/accruals and reaches conclusions different from prior work (seen only as a search snippet; not verified) — [search context: Alpha Architect accounting anomalies](https://alphaarchitect.com/accounting-anomalies/)
- Savor and Wilson (2016, JF): firms scheduled to announce earn an annualized abnormal return of about 9.9%, interpreted as compensation for systematic risk in announcement news — [Savor-Wilson draft (Wharton)](https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Draft20111215p_edited.pdf); [Quantpedia: Earnings Announcement Premium](https://quantpedia.com/strategies/earnings-announcement-premium)
- Quantpedia says the premium is not confined to a 3-day window but extends across the announcement month, and has appeared consistently since 1927 — [Quantpedia](https://quantpedia.com/strategies/earnings-announcement-premium)
- "The Disappearing Earnings Announcement Premium" (IIMB ARC 2020) argues the premium has weakened. Other work finds it shifted from earnings dates toward 8-K filing periods (titles and snippets only; the PDF returned 403) — [IIMB paper](https://www.iimb.ac.in/ARC2020/Papers/The_Disappearing_Earnings_Announcement_Premium.pdf)
- A separate paper attributes large pre-announcement returns over a 10-day window to the resolution of uncertainty risk before the announcement — [Tsinghua PBCSF working paper](https://eng.pbcsf.tsinghua.edu.cn/dfiles/yifabiao1.pdf)
- Analyst revisions: large price moves confirmed by same-direction analyst revisions continue, while unconfirmed moves reverse (Govindaraj, Livnat, Savor, Zhao). The authors caution that results may be driven by smaller stocks — [Alpha Architect summary](https://alphaarchitect.com/follow-the-trend-and-the-sell-side/)
- Low and Tan (2016, IRFA): the size of analyst revisions predicts returns beyond price momentum, with upgrades more informative than downgrades — [core.ac.uk](https://core.ac.uk/download/83969469.pdf); [HKU paper](https://hub.hku.hk/bitstream/10722/182132/1/Content.pdf)
- An earlier study (Ayers, Li, Yeung 2011) notes analyst-based drift has also declined (search snippet) — [ScienceGate](https://www.sciencegate.app/document/10.2308/accr.00000027)
- Implied vs realized (vendor studies, not peer-reviewed): 28,898 US reports from 2023-2026 show an average implied move of ±9.18% against an average realized ±6.32%. Only 25.2% closed beyond the implied move, and the gap widens for larger implied moves — [EarningsWatcher](https://earnings-watcher.com/wiki/options-implied-move-vs-actual-earnings-study-2026). Of 9,651 S&P 500 straddles, 59.5% were overpriced, with a median edge of +0.84pp, concentrated in a few names — [iVolatility](https://www.ivolatility.com/news/3147). FlashAlpha: the largest implied moves were overpriced 93% of the time, but small implied moves on megacaps were "breached repeatedly" — [FlashAlpha](https://flashalpha.com/articles?tag=ExpectedMove)
- NVDA: the options-implied post-earnings move exceeded the actual move in 14 of the last 20 quarters (Cboe LiveVol data via a syndicated article; lower-reliability host) — [syndicated report](https://1strespondernews.com/first-dry/Nvidia-PostEarnings-Volatility-Options-Pricing-Overestimated-Swings-in-14-of-Last-20-Quarters-19-1570); see also [ORATS: is NVDA earnings vol underpriced](https://orats.com/blog/is-nvda-earnings-volatility-underpriced)
- META: across 12 reports, the average absolute move was about 7.9% against an average implied move of 7.2%. Realized exceeded implied in 6 of 12 quarters — [ORATS META](https://orats.com/blog/meta-earnings-expected-move)

### Inferences
- For these 7 names, do not build a PEAD strategy on SUE drift. Any signal is in the announcement-day gap itself.
- The surviving earnings-related edges are (a) volatility selling (short straddle/strangle or iron condor into earnings), sized per name using each name's own implied/realized history, since META is a counterexample, and (b) holding or overweighting into the announcement window (the EAP), which is weak and possibly decaying.
- Revision signals (consensus EPS changes over 1-3 months) are cheaper to test as a weighting tilt among the 7 than as a timing signal. Expect small effects in mega caps, which have heavy analyst coverage.

### Gaps
- I found no study of PEAD or EAP restricted to the Mag-7 or the top-10 by market cap. The Martineau "large stocks" bucket is the best proxy.
- I did not get the exact EAP decay magnitudes (the IIMB paper was blocked).
- I found no peer-reviewed implied-vs-realized earnings-move study for 2010-2026. Academic analogs (e.g., earnings IV crush literature) were not searched.

## Q3. Other events: index rebalancing, Tesla deliveries, NVDA/AAPL product events, FOMC, CPI, options expiry

### Takeaway
Most classic event anomalies have decayed since 2010-2015. The S&P inclusion effect is largely gone, and deletions went from -12.4% (2000s) to -0.6% (2010-2020). The pre-FOMC drift weakened or vanished after 2015, though this is disputed. Tesla delivery reports show a repeated "sell the news on a beat" pattern in 2023-2026 headlines, but there is no systematic study. Apple product events show a weak, inconsistent "sell the news" narrative from journalism, not rigorous CARs. CPI days were extremely volatile in 2022 and calmer after 2023. These are volatility events, not directional ones.

### Cited Findings
- Greenwood and Sammon, "The Disappearing Index Effect" (JF 2025; 1980-2020): the S&P 500 addition abnormal return has shrunk substantially. Migrations from MidCap grew from about 50% to over 70% of additions, offsetting forced buying. Deletion effects ran -4.6% (1980s), -16.1% (1990s), -12.4% (2000-09) and -0.6% (2010-20) — [Alpha Architect summary](https://alphaarchitect.com/disappearing-index-effect/); [Ivey PDF](https://test2.ivey.uwo.ca/media/m2kh5j5y/the-disappearing-index-effect.pdf)
- Bennett, Stulz and Wang (1997-2017 data): the positive announcement effect of inclusion has disappeared, and the long-run impact became negative — [SSRN 3656628](https://papers.ssrn.com/abstract=3656628); [ECGI PDF](https://ecgi.global/sites/default/files/working_papers/documents/bennettstulzwangfinal.pdf)
- Lucca and Moench (2015) found a large pre-FOMC equity excess return for 1994-2011. Kurov, Wolfe and Gilbert extended the sample to Dec 2019 and found the drift "essentially disappeared after 2015" (Finance Research Letters 2020). Ben Dor and Rosa (2019) reportedly find no post-2015 change, so the evidence conflicts — [Kurov-Wolfe-Gilbert PDF](https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf); [NY Fed SR 512](https://econpapers.repec.org/RePEc:fip:fednsr:512)
- Tesla deliveries (secondary news, not a study):
  - Q3 2025: about 497,100 delivered against 447,600 expected, yet the stock dipped — [finanzen.net](https://finanzen.net/nachricht/aktien/tesla-q3-deliveries-smash-estimates-but-wall-street-wasn-t-impressed-what-gives-14980566)
  - Q2 2025: shares had fallen on each of the prior three delivery reports, described as "sell-the-news" — [americancompanies.com](https://americancompanies.com/news/tesla-tsla-deliveries-rise-25-stock-falls/)
  - Q4 2025: a miss, but the stock rose slightly as investors focused on AI/robotics — [Briefing.com](https://briefing.com/story-stocks/archive/2026/1/2/tesla-shrugs-off-q4-delivery-miss-as-investors-pivot-to-ai-and-robotics-future-(tsla))
  - Q1 2026: 358,023 delivered, a wide miss, and the stock fell about 3% — [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/tesla-misses-q1-2026-delivery-151513261.html)
  - Q3 2023: the stock fell as much as 3.7% on a record delivery count — [NBC DFW](https://www.nbcdfw.com/news/business/money-report/tesla-stock-slips-after-it-reports-462890-total-deliveries-during-the-third-quarter/3660551/)
- Apple events: Bespoke says shares tend to fall or struggle for a few days after product presentations ("buy the rumor, sell the news"), but not always. The stock rose about 8% on the 2007 iPhone debut day, and gained an average 5.2% in the month before iPhone announcements — [Benzinga/Bespoke](https://feeds2.benzinga.com/trading-ideas/long-ideas/15/09/5826044/apple-stock-falls-after-event-heres-how-the-stock-acts-histor). The stock dropped about 2% after the Vision Pro reveal (2023) — [Benzinga](https://www.benzinga.com/news/large-cap/23/06/32746359/d-j-vu-moment-alert-vision-pro-launch-triggers-concerns-over-apple-stock-dip-similar-to-original-i). NerdWallet reports an average +1.93% one-week return after the last 7 events (2-year window) — [NerdWallet newsletter](https://nerdyinvestor-nerdwallet.beehiiv.com/p/do-product-launches-move-tech-stocks)
- CPI: in 2022 the S&P 500 closed lower after 7 of 12 CPI releases. Since 2023 it closed higher after 12 of 18 — [E*TRADE](https://us.etrade.com/knowledge/library/perspectives/daily-insights/cpi-and-spx). One 2022 blog cites average CPI-day moves of about 5% over 4 months (secondary, treat cautiously) — [MacroVisor](https://macrovisor.beehiiv.com/p/january-cpi-data). Pre-CPI put demand rose while the Fed was hawkish (Feb 2023) — [Fortune](https://fortune.com/2023/02/12/stock-market-selloff-likely-if-upcoming-inflation-reading-disappoints-fed-strategists-warn/)

### Inferences
- For TSLA, which entered the S&P in Dec 2020, and the mega caps that are already in every index, index-inclusion trades are irrelevant. What matters is quarterly rebalance and Nasdaq-100 special-rebalance flows, which were not researched here.
- Treat TSLA deliveries, CPI and FOMC as known volatility dates. Use them as features (event-day dummies for vol forecasting, position-size cuts) rather than as directional signals. The "sell the news" pattern after delivery beats is anecdotal and conditional on the pre-report run-up.
- Product events (WWDC, the September iPhone event, NVDA GTC) need your own event study (market-model CAR, [-5,+5]) on 2010-2026 data. The existing evidence is journalism.

### Gaps
- Options expiry (monthly OPEX, quad witching, 0DTE) effects on these stocks: not researched in this pass. Stock pinning near strikes (Ni, Pearson and Poteshman 2005) is known from background knowledge only and was not verified here.
- I found no systematic event study of Tesla delivery reports or NVDA GTC/product events.
- I found no formal academic estimate of a CPI-day equity announcement premium after 2010. The macro-announcement premium literature (e.g., Savor-Wilson 2013) was not fetched.
- The Nasdaq-100 2023 special rebalance (which cut Mag-7 weights) was not researched.

## Q4. Free and cheap fundamentals and estimates data (SEC XBRL, FMP, Finnhub, Zacks)

### Takeaway
SEC EDGAR XBRL (companyfacts and frames APIs, plus bulk companyfacts.zip) is free and keyless, with a 10 requests/second fair-access limit and a required User-Agent. It is the best source for point-in-time-ish fundamentals (use filing dates). Finnhub's free tier gives 60 calls/minute for non-commercial use, but whether consensus estimates are included free is unclear. FMP and Zacks were not verified in this pass.

### Cited Findings
- SEC EDGAR APIs: no key needed. The fair-access limit is 10 requests/second per IP, and a declared User-Agent with contact info is required — [Arkolith guide](https://arkolith.com/blog/sec-edgar-api-guide); [tldrfiling rate limits](https://tldrfiling.pages.dev/blog/sec-edgar-api-rate-limits-best-practices)
- Bulk downloads at sec.gov/files/ include company_tickers.json, companyfacts.zip and submissions.zip. There are no daily caps; target about 8 requests/second — [tldrfiling](https://tldrfiling.pages.dev/blog/sec-edgar-api-rate-limits-best-practices); [dev.to overview](https://dev.to/pickuma/sec-edgar-for-developers-the-free-fundamentals-api-hiding-in-plain-sight-1cbi)
- Finnhub's free tier offers 60 API calls/minute. The pricing table lists EPS/Revenue/EBITDA/EBIT estimates, but it could not be confirmed whether they are free — [Finnhub pricing](https://finnhub.io/pricing). The free key is non-commercial — [ClaudeCodeHQ comparison](https://www.claudecodehq.com/blog/best-financial-data-apis-ai-workflows)

### Inferences
- For 7 stocks, the minimal stack is: EDGAR companyfacts for fundamentals (profitability, asset growth, book value, matching the RMW/CMA/HML definitions), French/AQR/global-q for factor returns, and a free source for earnings dates and consensus (Finnhub or FMP), cross-checked by hand. Historical point-in-time consensus estimates (needed for honest revision backtests) are the hardest piece to get for free.
- Survivorship and look-ahead risk: XBRL companyfacts includes restated values. Filter by `filed` date and `form` to approximate point-in-time data.

### Gaps
- FMP free-tier limits and estimates coverage: not verified.
- Zacks (paid ESP / Earnings Surprise data, Nasdaq Data Link): not verified.
- Whether any free source provides point-in-time historical consensus EPS (I/B/E/S-like) for 2010-2026: not found. This is likely the binding constraint for revision-signal backtests.
