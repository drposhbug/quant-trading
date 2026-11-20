# Lead-lag and information efficiency: prediction markets vs financial asset prices (as of Nov 2026)

Status flags: **[PUB]** = peer-reviewed or journal; **[WP]** = unpublished working paper or preprint; **[INFORMAL]** = blog, industry report or student thesis. Almost all 2024–2026 evidence is [WP].

## Q1. Do prediction-market odds lead financial prices, or the reverse? At what horizon?

### Takeaway
For **political events** (elections), the evidence consistently shows prediction markets lead equities, Treasuries and single stocks. The lead is **minutes to hours intraday** (election night), plus a **next-day** spillover that partly reverses. Most of the lead comes from hours when financial cash markets are closed. For **macro and Fed events**, Kalshi is at least as accurate as fed funds futures and consensus forecasts. I found no study showing Kalshi *leads* rates futures intraday. Outside discrete political shocks, no study shows prediction-market odds predicting equity-index returns.

### Cited Findings
**Classic results**
- Snowberg, Wolfers & Zitzewitz, "Partisan Impacts on the Economy" (QJE 122(2), 2007) **[PUB]**. They use election-night Tradesports/IEM probabilities together with electronic index futures during the vote count. In 2004, markets priced the S&P 500 about **1.6% higher** under Bush and 10-yr yields about **11 bp higher**. For 2000 (no prediction market), futures alone imply at least **+1.3%**. Elections since 1880 suggest a Republican president raises equity valuations by **2–3%**. — [NBER Digest](https://www.nber.org/digest/oct06/electoral-outcomes-and-financial-markets); [NBER w12073](https://www.nber.org/system/files/working_papers/w12073/w12073.pdf); [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/working-papers/partisan-impacts-economy-evidence-prediction-markets-close-elections)
- Their design treats the prediction market as the probability measure and regresses asset moves on its changes. It is an identification tool, not a trading signal. The follow-up NBER w12751 applies the same method to control of Congress. — [NBER w12751](https://www.nber.org/system/files/working_papers/w12751/w12751.pdf)
- Wolfers & Zitzewitz, "Prediction Markets," JEP 18(2), 2004 **[PUB]**. Market forecasts are "typically fairly accurate" and beat most moderately sophisticated benchmarks. Election-day average absolute error was about **1.5 pp**. — [NBER w10504](https://www.nber.org/papers/w10504); [RePEc](https://econpapers.repec.org/RePEc:aea:jecper:v:18:y:2004:i:2:p:107-126)
- Berg, Nelson & Rietz, IJF 24(2), 2008 **[PUB]**. Across 964 poll comparisons in the 1988–2004 presidential elections, the IEM was closer to the final vote share **74% of the time**. It significantly beat polls in every election when forecasting **more than 100 days** ahead. — [IEM summary](https://iemweb.biz.uiowa.edu/about-iem/research/prediction-market-accuracy-in-the-long-run/); [RePEc](https://econpapers.repec.org/RePEc:eee:intfor:v:24:y:2008:i:2:p:285-300)

**2024 election: odds leading assets**
- Aktuğ & Torul, "Price Discovery Across Political Prediction Markets" (June 2026) **[WP]**. They use **5-minute** data. On election night the Polymarket probability and E-mini S&P futures had a level correlation of 0.89, but **Polymarket moved first at every stage**. Polymarket reached 25% of its overnight move **15 min** before the future, 50% **25 min** before, and 75–90% roughly **3 to 3.75 hours** before. The prediction-market consensus also led Trump Media (DJT) across the overnight gap and priced two weekend shocks while financial markets were closed. — [Aktuğ & Torul PDF](https://academics.bogazici.edu.tr/torul/pridis.pdf)
- Aktuğ & Torul, "Election Probabilities and the Treasury Yield Curve" (May 2026) **[WP]**.
  - A daily **+10 pp** Trump probability went with about **+2 bp** of 2s10s steepening. The short end did not move. About 95% of the 10-yr response was term premium.
  - **58%** of the average absolute daily probability move happened while cash Treasury markets were closed. The yield response loads entirely on that overnight component, which rules out same-day reverse causality.
  - On Nov 6, 2024, **12.5 of the 16 bp** rise in the 10-yr yield (78%) was already priced in CME ZN futures by 08:00 ET.
  - The ZN overnight gap is not significant on days other than Election Day (t = 0.1, N = 457).
  - Out-of-sample slope R² across six event dates was 0.34. A 2020 PredictIt replication has consistent signs.
  - [Aktuğ & Torul yield PDF](https://academics.bogazici.edu.tr/torul/yield.pdf)
- Goldstein, Li & Wang, "Learning from Prediction Markets: The Transmission of Information and Noise to Traditional Assets" (2026) **[WP]**, with a best-paper award at RAPS/RCFS Europe. Changes in Polymarket probabilities **predict next-day returns of "Trump trades" across asset classes, followed by partial reversals**. Using wallet-level on-chain data, they find uninformed (noise) flow drives the next-day predictability and then reverses. The price impact of informed flow persists. — [Chen Wang project page](https://chenwang.one/publication/predmkt/)
- Coin Metrics (industry): from May to Aug 2024, the correlation between Trump odds and BTC returns was moderate and peaked at **0.4**. This is a daily correlation, not a lead-lag test. — [Coin Metrics SOTN #283](https://coinmetrics.substack.com/p/state-of-the-network-issue-283)

**Crypto: Polymarket vs options**
- Portnaya, "Do Prediction Markets Match Option Prices? Bitcoin Threshold Evidence from Binance and Polymarket" (arXiv 2606.19517, June 2026) **[WP]**.
  - Polymarket BTC threshold contracts deviate from Binance option-implied probabilities by a mean of **5.6 pp** (214 hourly obs). The pooled gap is **6.3 pp**, and about **11 pp** against Deribit.
  - The gap mean-reverts with a half-life of about **4 hours**. It is largest at low probabilities and long maturities, which is consistent with longshot demand on Polymarket.
  - A delta-hedged arbitrage proxy stays profitable after conservative costs, but with **marginal statistical precision**. The abstract does not state which venue leads.
  - [arXiv 2606.19517](https://arxiv.org/abs/2606.19517)

**Fed and macro: Kalshi vs futures and surveys**
- Diercks, Katz & Wright, "Kalshi and the Rise of Macro Markets," FEDS 2026-010 (Feb 12, 2026) **[WP]**, Fed Board staff paper. Fortune called it an NBER working paper; the version I read is the FEDS release.
  - Since 2022 the Kalshi median and mode had a **perfect record on the day before FOMC meetings**. This is a statistically significant improvement over fed funds futures, which must be read as a two-outcome split.
  - At **150 days** (three meetings) ahead, Kalshi's MAE is very similar to the NY Fed Survey of Market Expectations.
  - On release day, headline CPI MAE is about **7 bp for Kalshi vs 8 bp for the Bloomberg consensus** (significant for median and mode). Core CPI and unemployment are statistically tied with consensus. Kalshi is never significantly worse.
  - Intraday, the probabilities respond sharply to news, for example a July 2025 cut probability rising to 25% after Waller and Bowman remarks. The authors say these dynamics are "missed with daily data."
  - [FEDS 2026-010](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf); [Fortune coverage](https://fortune.com/2026/01/28/kalshi-prediction-market-federal-reserve-betting-forecast-nber-working-paper/)

### Inferences
- The robust lead exists because prediction markets trade **24/7** while cash equities and Treasuries are closed (weekends, overnight, election night). Once futures are open, the lead shrinks to **minutes**. That timing is consistent with financial markets learning from the odds, not with a persistent inefficiency.
- The Goldstein-Li-Wang next-day effect is the only result close to a daily horizon. It is **event-specific** (2024 election "Trump trades") and **partly reverses**, so it is a fragile basis for a daily strategy.
- For Fed and CPI outcomes, Kalshi is a better *expectations measure*, mainly because it shows a full distribution. Nothing shows it front-runs SOFR or fed funds futures prices in a tradable way.

### Gaps
- No full-text coefficients from Goldstein-Li-Wang: the PDF was unreachable (404 on the guessed URL). I don't have the size of the next-day predictability, the reversal size, or the asset list.
- I found no study testing whether Polymarket or Kalshi probabilities predict **equity-index or cross-sectional stock returns** outside elections. One search summary said such a test appears not to exist.
- I found no intraday lead-lag study of Kalshi CPI/FOMC contracts vs SOFR or fed funds futures or Treasuries at the release minute.
- Ng, Peng, Tao & Zhou, "Price Discovery and Trading in Modern Prediction Markets" (SSRN 5331995) returned 403. The only numbers available come from the search summary in Q3.

## Q2. Calibration and accuracy: favorite-longshot bias (FLB), Brier scores, exploitability after fees

### Takeaway
Both Kalshi and Polymarket are well calibrated overall and get sharper near resolution, but both show a **clear favorite-longshot bias**. Cheap contracts lose roughly 20–60% after costs. Expensive contracts (≥70–90¢) earn **small** positive returns, around 1–3%. The only documented after-fee edge (buying favorites as a maker on Kalshi) is small and capital-intensive, and it says nothing about stock or crypto prices.

### Cited Findings
- Bürgi, Deng & Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market" (UCD WP25/19, July 2025; CESifo WP 12122; Jan 2026 revision) **[WP]**.
  - Sample: transaction data on more than 300k contracts.
  - The average return on Kalshi contracts is about **−20%**. Contracts at **≤10¢** lose **over 60%** after fees. Returns are small and positive above 50¢, with **statistically significant small positive post-fee returns above 70¢**.
  - Makers who buy contracts at ≥50¢ earn about **+2.6%**.
  - The taker fee during the sample was **$0.07·P·(1−P)** per contract, rounded up to the cent. Makers paid no fee.
  - The bias appears to be shrinking over time.
  - [Whelan PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf); [UCD WP](https://www.ucd.ie/economics/t4media/WP2025_19.pdf); [CESifo](https://www.ifo.de/en/cesifo/publications/2026/working-paper/makers-and-takers-economics-kalshi-prediction-market)
- The Feb 2026 GWU version contrasts these results with Berg & Rietz (2019), who found **no FLB on the IEM**. — [GWU WP 2026-001](https://www2.gwu.edu/~forcpgm/2026-001.pdf)
- Cardozo & Rivero-Wildemauwe, "The Favorite-Longshot Bias in Prediction Markets: Evidence from Polymarket" (arXiv 2609.12878, Sep 2026) **[WP]**.
  - Sample: 588M trades by 2.48M accounts.
  - Purchases **below 10¢ lose 19.3¢ per $**. Purchases **at or above 90¢ earn 0.83¢ per $**. These are gross figures; the abstract does not report net-of-fee or net-of-spread returns.
  - The result depends on weighting. Weighting contracts equally, longshots lose 6.3¢ per $. Grouping contracts by parent event, longshots **gain 4.1¢**.
  - The FLB is present in Crypto and Politics and **absent in Sports**.
  - [arXiv 2609.12878](https://arxiv.org/abs/2609.12878)
- Princeton senior thesis (Apr 2026) **[INFORMAL]**: 188,509 resolved Polymarket binaries (Nov 2022 to Dec 2025). The overall Brier Skill Score is **0.398**, ranging from **0.264 in sports** to **0.565 in politics**. — [Princeton thesis](https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c); domain dynamics in [arXiv 2602.19520](https://arxiv.org/html/2602.19520v2)
- Blog analysis of 7,661 Polymarket markets **[INFORMAL]**: Brier score about **0.025 at 24 hours** and **0.042 at 30 days**, with underpricing in the mid-range. It has selection bias toward high-volume markets. — [LessWrong](https://www.lesswrong.com/posts/Hruc6Gwo3vBZFGb6v/empirical-calibration-of-polymarket-analysis-of-7-661)
- A Polymarket whale-wallet audit **[INFORMAL]** found a +0.42 Spearman correlation between Brier score and realized profit. Because a higher Brier score means worse forecasts, more profitable wallets were *worse* forecasters. — [Convexly](https://hn.jakechampion.name/reader/https://www.convexly.app/blog/polymarket-whale-audit)

### Inferences
- The FLB means **raw prices overstate the probability of tail outcomes**, for example "S&P down 10%" or "BTC > X" longshots. Any signal built from low-probability contracts should be shrunk toward 0 before use. The Portnaya BTC result (gap largest at low probabilities) is consistent with this.
- The after-fee edge is economically small (+1–3% on favorites, makers only) and sits inside the prediction market itself. It is not an edge in financial assets.

### Gaps
- No paper reports Polymarket FLB returns **net of** current fees and spreads. Polymarket's 2025–26 fee schedule was not verified here.
- Brier comparisons across venues (Polymarket vs Kalshi) are only available from informal sources.

## Q3. Cross-venue lead-lag (Polymarket vs Kalshi vs Betfair vs PredictIt)

### Takeaway
Price discovery is **shared and depends on context**. Polymarket and Betfair dominated the 2024 election, with Kalshi gaining a large share within weeks. Polymarket tends to lead in politics; Kalshi tends to lead in sports and when its relative volume and block activity are high. Leads are **seconds to minutes**.

### Cited Findings
- Aktuğ & Torul (June 2026) **[WP]**, 5-minute data, nine venues, 2024 election. The order-book exchanges Polymarket and Betfair hold about **85%** of information shares, and no dealer sportsbook exceeds 11%.
  - In the Kalshi window (Oct 4 to Nov 5, 2024), **Polymarket 44% and Kalshi 41%**, with tight Hasbrouck bounds but very wide bootstrap CIs (Polymarket [1.3%, 64.8%]).
  - In the Biden-withdrawal window, Polymarket 37% and Betfair 41%.
  - Polymarket and Betfair account for 91% of the 761 detected jumps.
  - [PDF](https://academics.bogazici.edu.tr/torul/pridis.pdf)
- Ng, Peng, Tao & Zhou, SSRN 5331995 (rev. Apr 2026) **[WP]**. Around the 2024 election, Polymarket beat polls and **led Kalshi**. Over 2023–2026 discovery is **bidirectional**: Kalshi leads in sports and when its relative volume and large-trade activity are higher, while Polymarket leads in politics and entertainment. These details come from a search summary; the SSRN page returned 403. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5331995)
- Pantera Research Lab **[INFORMAL]**: in sports, **Kalshi leads the initial repricing in about 80% of large moves**, with a median lead of **about 7 seconds**. — [Pantera Research Lab](https://panteraresearchlab.xyz/research/the-super-bowl-of-prediction-markets-kalshi-and-polymarkets-battle-for-price-vs-liquidity/)
- Practitioner reports say simple cross-venue arbitrage is being competed away by prop firms running automated agents. — [CryptoSlate](https://cryptoslate.com/easy-money-on-polymarket-and-kalshi-is-disappearing-as-prop-firms-deploy-ai-agents/)

### Inferences
- Cross-venue leads of seconds to minutes are useless to a daily-rebalancing system. For a daily snapshot, taking the most liquid venue for the event type, or averaging Polymarket and Kalshi, is sufficient.

### Gaps
- No peer-reviewed cross-venue study yet. The information-share confidence intervals are very wide.

## Q4. Tradable edge in financial markets after costs; data frequency; implications for a daily-rebalancing retail system

### Takeaway
**I found no study showing a robust, after-cost edge in stocks, indices or rates from prediction-market signals.** The documented leads are intraday or overnight, cluster around a few huge political events, and are absorbed by the next open. The one daily-horizon effect (Goldstein-Li-Wang) is a single-election finding that partly reverses. Showing lead-lag at all requires **1–5-minute** data; daily data mostly shows contemporaneous co-movement.

### Cited Findings
- Lead-lag in the published work is measured at **5-minute** resolution (Aktuğ & Torul), **1-minute** CME Globex data, or **hourly** data (Portnaya BTC). Daily regressions identify direction only by splitting overnight from trading hours. — [pridis](https://academics.bogazici.edu.tr/torul/pridis.pdf); [yield](https://academics.bogazici.edu.tr/torul/yield.pdf); [arXiv 2606.19517](https://arxiv.org/abs/2606.19517)
- Away from Election Day, the overnight ZN futures gap explained by political odds is **statistically zero** (t = 0.1). Financial markets had already incorporated the odds by the next open. — [yield PDF](https://academics.bogazici.edu.tr/torul/yield.pdf)
- The Fed authors say Kalshi's informative intraday dynamics are "missed with daily data." — [FEDS 2026-010](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf)
- The only after-cost "profitable" claim tied to a financial asset is Portnaya's BTC delta-hedged arbitrage proxy. It is statistically marginal, it trades *inside* Polymarket against options, and it does not predict BTC direction. — [arXiv 2606.19517](https://arxiv.org/abs/2606.19517)
- Goldstein-Li-Wang: next-day predictability exists but is **noise-driven and partly reverses**. — [project page](https://chenwang.one/publication/predmkt/)

### Inferences
- For a **daily-rebalancing retail system**, prediction-market odds are best used as:
  - (a) an **event-risk and regime overlay**, for example the probability of a Fed cut or an election outcome, used to scale exposure;
  - (b) a weekend or overnight **gap estimator** for the Monday or next open, which is the one window where the lead clearly exists. A retail account usually cannot trade it before the open; extended hours or futures would be needed.
- A daily snapshot of odds is near-contemporaneous with the close for liquid markets, so expect little standalone alpha. Any test should record the timestamp of the odds snapshot relative to the 16:00 ET close. Otherwise look-ahead or co-movement will masquerade as prediction.
- Shrink low-probability (<10–15¢) contract prices toward zero because of the FLB.

### Gaps
- No out-of-sample, after-cost backtest anywhere of trading equities or ETFs on daily prediction-market changes.
- Most evidence comes from one event (the 2024 election). There is little evidence on generalization to recurring macro events beyond forecast accuracy.
