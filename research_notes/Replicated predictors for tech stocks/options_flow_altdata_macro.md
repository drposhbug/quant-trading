# Options-market, order-flow, alternative-data and cross-asset/macro predictors of US mega-cap tech returns (daily to monthly)

Scope note: research done 2026-11-18 with ~15 web queries. Most primary papers are paywalled; many figures come from abstracts, NBER digests, or summaries (CXO Advisory, Pulse.bot) and are flagged as such. Items in "Inferences" that draw on background knowledge rather than a source fetched this session are marked **[unverified background]**.

## Cross-cutting: how much do published anomalies survive (decay, costs)?

### Takeaway
Assume any published cross-sectional predictor has lost half or more of its edge since publication. After realistic trading costs, the average anomaly earns close to zero. Mega-caps have the lowest costs but also the least mispricing, so the bar for a new signal is high.

### Cited Findings
- Chen & Zimmermann's open-source dataset reproduces nearly 100% of the literature's predictability results and is updated annually. This is the free starting point for any cross-sectional signal (it includes many options signals). — [Chen & Zimmermann, Open Source Cross-Sectional Asset Pricing](https://cfr.ivo-welch.info/published/papers/chen2021open.pdf); [arXiv 2105.01380](https://arxiv.org/pdf/2105.01380)
- Returns after publication are about 50% smaller (McLean-Pontiff, replicated). Restricting to data after 2005 raises the decay to about 72% (Chen-Velikov). Another study of 191 predictors finds 65% post-publication decay. — [Fed FEDS 2021-037](https://www.federalreserve.gov/econres/feds/files/2021-037pap.pdf); [AEA 2018 paper](https://aeaweb.org/conference/2018/preliminary/paper/ZKzBYziN)
- Chen & Velikov (JFQA 2023) study 204 anomalies, accounting for effective spreads, post-publication decay and post-2005 trading technology. Investors should expect about 4 bps/month. The strongest anomalies net about 10 bps at best after a data-mining adjustment, and combinations net about 20 bps. These figures exclude price impact and short-sale fees. The 2020 working paper put the average at 8 bps/month and found 7 anomalies earning more than 60 bps/month net in post-publication, post-2005 data. — [Cambridge JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225); [Fed WP 2020-039](https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf)

### Inferences
- For a universe of about 10–30 mega-cap tech names, a cross-sectional long-short ranking is statistically weak: the breadth is too small. Time-series use is more realistic: tilting exposure to a stock or to the basket (e.g. QQQ/SMH) as the signal changes, using t-stats computed with Newey-West or block bootstrap.
- Costs for mega-caps are about 1–3 bps one way for stock, so daily-turnover signals are feasible. Option-based *trading* (as opposed to using options as a signal) costs far more. **[unverified background]**

### Gaps
- No source found that re-estimates options anomalies on a mega-cap-only subsample after 2015.

## 1. Options-market predictors

### Takeaway
Options signals (skew, IV spread, signed option volume) were real in the 1996–2010 cross-section. They are strongest where stock liquidity is low and information asymmetry is high, which is the opposite of mega-caps, and documented predictability has declined over time. Market-level option measures (VRP, implied correlation) have the best out-of-sample record, at roughly quarterly horizons. GEX is mainly a volatility-regime indicator, not a reliable directional forecast.

### Cited Findings
**Implied-volatility skew (Xing, Zhang & Zhao, JFQA 2010)**
- The smirk is OTM-put IV minus ATM-call IV. Steep-smirk stocks underperform, and the predictive power persists for at least six months. — [XZZ paper copy](https://www.iex.nl/Forum/Upload/2014/7383995.pdf); [Scribd copy](https://www.scribd.com/doc/119242338/Option-Skew-FINAL)
- Model-free option-implied *skewness* (as opposed to the smirk) reportedly does not predict returns. This comes from a secondary citation. — [Tsinghua PBCSF paper](https://www.pbcsf.tsinghua.edu.cn/__local/A/24/EA/815CC33800CAA0F7D894E9292A1_6CC8B38B_27B25.pdf?e=.pdf)

**IV spread / put-call parity deviations (Cremers & Weinbaum, JFQA 2010)**
- Stocks with relatively expensive calls outperform those with relatively expensive puts by about 50 bps per week. — [Cambridge JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/deviations-from-putcall-parity-and-stock-return-predictability/D9BA8F97580328AAFD7988B092FE5D50)
- The authors themselves report that predictability declines over the sample. It is larger when option liquidity is high and stock liquidity is low, and deviations are more likely when the stock faces more information risk. — [Cambridge JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/deviations-from-putcall-parity-and-stock-return-predictability/D9BA8F97580328AAFD7988B092FE5D50); [CXO summary](https://www.cxoadvisory.com/?p=1665)
- A later JFQA paper argues the spread partly proxies for aggregate volatility risk. It finds the strongest predictability in 2000–2003 and 2008–2012, so the decline is not monotonic. — [The Only Constant Is Change (JFQA)](https://core-prod.cambridgecore.org/core/services/aop-cambridge-core/content/view/9FA5F5022A15B608233F958C167DE162/S0022109023000182a.pdf/the-only-constant-is-change-nonconstant-volatility-and-implied-volatility-spreads.pdf)

**Option volume / put-call ratio (Pan & Poteshman, RFS 2006)**
- Uses *open-buy* put-call ratios from proprietary CBOE data, 1990–2001. Low-PCR stocks beat high-PCR stocks by more than 40 bps the next day and more than 1% over the next week. The predictability fades over several weeks. — [NBER w10925](https://www.nber.org/papers/w10925); [RFS record](https://econpapers.repec.org/RePEc:oup:rfinst:v:19:y:2006:i:3:p:871-908)
- *Publicly observable* volume signals predict returns for only one or two trading days. The source is nonpublic information, not inefficiency. — [NBER WP PDF](https://nber.org/system/files/working_papers/w10925/w10925.pdf)

**Variance risk premium (Bollerslev, Tauchen & Zhou, RFS 2009)**
- VRP (implied minus realized variance) predicts aggregate returns. It is strongest at a quarterly horizon, where it dominates other predictors. — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/08/rp08_48.pdf)
- Bollerslev, Marrone, Xu & Zhou (JFQA 2014) find finite-sample bias does not explain the result. The pattern holds in France, Germany, Japan, Switzerland, the UK and the US, and a global VRP predicts even better. — [Cambridge JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/stock-return-predictability-and-variance-risk-premia-statistical-inference-and-international-evidence/0BE5DE1D942A0342DDBA24D7BFBEA5C8)
- Pyun (2016 working paper) finds the out-of-sample performance of the BTZ-style VRP "comparably weak". An alternative construction gives an 8% monthly OOS R². — [AEA 2017](https://topcat.aeaweb.org/conference/2017/preliminary/paper/GDde2yiy)

**Implied correlation / dispersion**
- Driessen, Maenhout & Vilkov (JF 2009): correlation risk is priced, but the correlation risk premium cannot be exploited given realistic trading frictions. — [IDEAS](https://ideas.repec.org/a/bla/jfinan/v64y2009i3p1377-1406.html)
- Implied correlation together with the index VRP explains market excess returns with R² of about 12–15%. The result survives fundamental controls. This figure is from a working paper. — [Netspar WP](https://www.netspar.nl/wp-content/uploads/061_Driessen.pdf)
- Buss, Schönleber & Vilkov: implied correlation predicts market excess returns up to one year ahead, both in- and out-of-sample, while VRP works only about one quarter ahead. Their proposed mechanism is market-exposure concentration (beta dispersion), not diversification. — [AEA 2018](https://aeaweb.org/conference/2018/preliminary/paper/Rt6FbZde); [CEPR DP12760](https://repec.cepr.org/repec/cpr/ceprdp/DP12760.pdf)

**Dealer gamma exposure (GEX)**
- OptionMetrics (Maurer, 2026) finds GEX's power to forecast realized volatility is concentrated in *low-volatility* regimes, the inverse of the practitioner narrative. — [OptionMetrics research](https://optionmetrics.com/research/dealer-gamma-exposure-and-overnight-gap-risk-incremental-information-in-low-volatility-regimes/)
- An OptionMetrics SPY study finds "gamma exposure alone does not adequately explain realized volatility and return". Decomposing positions by dealer long/short call/put contradicts the standard GEX reading. — [OptionMetrics](https://optionmetrics.com/?p=3289)
- Jonsson & Nyberg (2025) reportedly find GEX changes predict next-day S&P 500 returns before and after 2020, weaker in the later period. This is a secondary summary only; not verified. — [Pulse.bot summary](https://www.pulse.bot/options-derivatives/news/gamma-exposure-and-sp500-return-predictability-921c3495-0d15-4d97-9643-e2b539de977e/)
- SpotGamma, a vendor, states that GEX does not predict direction. — [SpotGamma](https://spotgamma.com/gamma-exposure-explained/)
- GEX depends on assumptions about who holds the positions, because public open interest does not identify the holder. Values therefore differ across vendors. — same OptionMetrics and SpotGamma sources

**VIX term structure**
- Johnson (JFQA 2017): the VIX term-structure slope predicts next-day returns of *variance assets* (variance swaps, VIX futures, straddles), with quintile spreads of 0.29–1.81%/day gross. It does not predict the index. — [EconPapers](https://econpapers.repec.org/RePEc:cup:jfinqa:v:52:y:2017:i:06:p:2461-2490_00); [CXO](https://www.cxoadvisory.com/volatility-effects/vix-term-structure-slope-and-variance-asset-future-returns/)
- Fassas (2012) finds a weak, in-sample negative relation between changes in the VIX futures curve and S&P returns. — [CXO](https://cxoadvisory.com/volatility-effects/change-in-vix-futures-term-structure-as-stock-market-return-predictor)
- Quantpedia's VIX-futures term-structure strategy shows slightly negative out-of-sample performance, with alpha deteriorating. — [Quantpedia](https://quantpedia.com/strategies/exploiting-term-structure-of-vix-futures)

### Inferences
- **Mega-cap applicability:** Cremers-Weinbaum's finding that predictability is largest when stock liquidity is low implies AAPL, MSFT and NVDA should show the weakest effects. Treat skew, IV spread and PCR as unlikely to clear costs in mega-caps unless a subsample test shows otherwise.
- The publicly observable PCR (total volume from yfinance or Cboe) differs from Pan-Poteshman's proprietary open-buy volume. Their own result says public signals last only one or two days. Expect a weak free-data replication.
- The 0DTE boom since 2022 likely changed both GEX and PCR dynamics. Pre-2022 estimates may not transfer. **[unverified background]**
- The most promising options use for this project is *risk/regime*: VRP, implied correlation, and GEX sign as vol-target or exposure scalers for a mega-cap tech basket. Mega-cap tech dominates index weight, which links directly to the Buss et al. "concentration" mechanism.

### Data availability (2026)
- **Free:**
  - yfinance current option chains (no history; snapshots must be archived daily yourself).
  - Cboe VIX, VIX9D, VIX3M, VVIX, SKEW, and the implied-correlation indices (COR1M/COR3M) as index histories.
  - Cboe daily market-wide put-call ratio archives.
  - FRED VIXCLS.
  - **[unverified background]** Exact Cboe file availability and history length should be checked.
- **Paid:**
  - OptionMetrics IvyDB (WRDS, academic): historical IV surface for skew, IV spread and VRP per stock.
  - Cboe DataShop / Open-Close volume (open-buy volume as in Pan-Poteshman).
  - ORATS, SpotGamma, SqueezeMetrics (GEX/DIX; SqueezeMetrics historically offered a free DIX/GEX CSV, **[unverified background]**).

### Test design
1. Universe: about 15 mega-cap tech names plus QQQ, 2012–2026, daily.
2. Signals:
   - (a) XZZ smirk: 30-day 25-delta put IV minus ATM call IV.
   - (b) CW IV spread: call minus put IV at matched strikes, open-interest weighted.
   - (c) 5-day put-call volume ratio z-score.
   - (d) Market VRP: VIX² minus 22-day realized variance.
   - (e) COR3M level.
   - (f) VIX/VIX3M ratio.
3. Single-stock signals: run a pooled panel regression of next-1/5/21-day *excess-over-QQQ* returns on z-scored signals, with stock and date fixed effects and Driscoll-Kraay standard errors.
4. Market signals (d–f): predict QQQ/basket 21- and 63-day returns. Report Campbell-Thompson OOS R² with expanding-window estimation starting 2016, and a Clark-West test.
5. Cost layer: 2 bps one way plus a turnover penalty.
6. Placebo: shuffle signal dates.
7. Pass criterion: OOS R² > 0, and net Sharpe improvement over buy-and-hold of at least 0.2 in 2020–2026.

### Gaps
- No post-2015 replication of XZZ, CW, or Pan-Poteshman restricted to large caps was found.
- No peer-reviewed 2020s OOS test of VRP was found.
- The Jonsson-Nyberg GEX paper could not be verified at the primary source.
- Exact Cboe free-history coverage for COR1M/COR3M was not confirmed.

## 2. Flow predictors (short interest, ETF flows, 13F crowding, insiders, retail)

### Takeaway
Aggregate short interest is the strongest-documented flow predictor of the *market* (OOS R² about 13% annual, 1990–2012), but its performance is uneven over time. Retail order imbalance predicts the cross-section for a few weeks. Insider-purchase and crowding signals are concentrated in smaller, less-covered firms and are weak for mega-caps.

### Cited Findings
**Aggregate short interest**
- Rapach, Ringgenberg & Zhou (JFE 2016) build the Short Interest Index: the equal-weighted average of SI/shares outstanding, linearly detrended and standardized. In-sample annual R² is 12.89% and OOS R² is 13.24%. It beats 14 other predictors at 3-, 6- and 12-month horizons over 1990–2012, with utility gains of more than 300 bps/yr. The channel is cash flows. — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:121:y:2016:i:1:p:46-65); [WashU](https://source.washu.edu/?p=71258)
- Performance is uneven: it does not outperform in 1990–95, underperforms in 2000–07, and its value is concentrated in the late 1990s and 2008–09. A later combined-predictor study reports an OOS R² of −0.776% for SII. — [CXO Advisory](https://cxoadvisory.com/short-selling/aggregate-short-interest-and-future-stock-market-returns)

**Short-sale data**
- FINRA daily short-sale volume files are free and posted by 6 pm ET. Consolidated NMS files start 1 Aug 2018. The interactive grid covers 365 days, with older data via monthly files and the Query API. — [FINRA Daily Short Sale Volume](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files)
- FINRA states that short-sale volume is not equivalent to short interest, and the two series "are not necessarily correlated". Its 2019 notice says listed-stock short interest is published by the listing exchange. — [FINRA Info Notice 5/10/19](https://www.finra.org/rules-guidance/notices/information-notice-051019)
- A third-party scraper claims api.finra.org covers listed-stock short interest. This conflicts with the 2019 notice and is unverified. — [Apify actor](https://apify.com/scrapemint/short-selling-data-tracker)

**Retail flow**
- Boehmer, Jones, Zhang & Zhang (JF 2021) identify retail trades as TRF prints (exchange code "D") with sub-penny price improvement. The marketable retail order imbalance predicts the cross-section of returns for several weeks. About half the effect comes from persistence and liquidity provision, half from information. — [ABFER slides](https://www.abfer.org/media/abfer-events-2017/annual-conference/investment-finance/22-3-a-xiaoyan-zhang.pdf); [notes](https://zizouhe.github.io/reading-notes/notes/retail.html)
- Retail flow does not forecast aggregate market returns. — [AEA 2018](https://aeaweb.org/conference/2018/preliminary/paper/DG524NYr)
- Barardehi, Bernhardt, Da & Warachka argue the predictability comes from unwinding institutional price pressure, not informed retail traders. — [AEA 2025 slides](https://topcat.aeaweb.org/conference/2025/program/powerpoint/KNfZeaRs)

**Insider purchases (Form 4)**
- Cohen, Malloy & Pomorski (JF 2012): opportunistic, non-routine insider trades earn about 82 bps/month value-weighted abnormal return, while routine trades earn about zero. The most informed insiders are local, non-executive, and at poorly governed, geographically concentrated firms. — [NBER Digest](https://www.nber.org/digest/apr11/decoding-inside-information); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:67:y:2012:i:3:p:1009-1043)
- Lakonishok & Lee: the insider buy-sell spread is most pronounced in small stocks and much weaker for large companies. This is a secondary summary. — [IBKR Campus](https://www.interactivebrokers.com/campus/?p=256270)

**13F crowding**
- Brown, Howard & Lundblad ("Crowded Trades and Tail Risk"): cap-weighted most-owned stocks returned about 3 pp/yr more than least-owned stocks on average. Crowded stocks had significantly negative cumulative abnormal returns in 2008. — [FA-Mag summary](https://fa-mag.com/news/scientists-prove-crowded-hedge-fund-stocks-are-real-and-risky-43499.html); [AEA 2022](https://aeaweb.org/conference/2022/preliminary/paper/bFN7k78F)
- Barroso, Edelen & Karehnke: 13F crowding predicts lower momentum returns, but there is little evidence it predicts momentum tail risk. — [AMF paper](https://www.amf-france.org/fr/sites/institutionnel/files/private/2022-04/1_paul_karehnke_article.pdf)
- Chincarini, Lazo-Paz & Moneta (2023 WP) find a significant crowding-return relation in anomaly stocks. — [Carlo Alberto PDF](https://www.carloalberto.org/wp-content/uploads/2023/06/18_Chincarini_Lazo-Paz_Moneta_Crowding_Anomalies_03_14_23.pdf)

### Inferences
- **Mega-caps:**
  - Insider *selling* in mega-cap tech is almost all routine (10b5-1 plans), so it carries no signal. Open-market *purchases* are rare, so the sample is tiny.
  - Short interest in mega-caps is about 0.5–1.5% of float, so days-to-cover carries little information. Aggregate SII (market timing) is the more useful form. **[unverified background]**
- 13F data is 45 days stale and quarterly, so crowding is useful only as a slow risk/tail flag, not for daily-to-monthly alpha.
- The BJZZ retail-flow signal requires TAQ-level trade data. The sub-penny rule was degraded by SEC tick/rebate changes and the 2024 Reg NMS amendments; check before replicating. **[unverified background]**
- ETF creation/redemption flows: no rigorous predictive evidence was found this session. Treat as a gap. A common practitioner view is that flows chase returns and predict short-term reversal. **[unverified background]**

### Data availability (2026)
- **Free:**
  - SEC EDGAR Form 4 (XML) and 13F-HR (quarterly XML).
  - FINRA daily short-sale volume.
  - Exchange or FINRA bi-monthly short interest (source is ambiguous, see above).
  - ETF shares outstanding (from issuer sites, or yfinance sharesOutstanding snapshots).
- **Paid:**
  - TAQ (WRDS) for BJZZ retail flow.
  - S3 Partners / Ortex / IHS Markit for daily SI and borrow fees.
  - Bloomberg / ETF.com flow history.
  - WhaleWisdom (cheap) for parsed 13F.

### Test design
1. **SII replication:** pull bi-monthly SI for S&P 500 constituents, equal-weight, detrend in an expanding window (no look-ahead), and predict QQQ 1/3/6-month returns. Report OOS R² from 2010 onward against the historical mean.
2. **Insider:** parse EDGAR Form 4 transaction code "P" (open-market purchase) for the mega-cap tech names plus semis, 2005–2026. Exclude routine traders as defined by CMP: insiders who traded in the same month in each of the prior 3 years. Run an event study of 1/5/21-day CAR against QQQ. Expect fewer than 50 events, so report confidence intervals.
3. **Daily short-volume ratio** (FINRA ShortVolume/TotalVolume): 5-day z-score, predicting 1–5-day excess returns, as a panel. Because of the FINRA caveat (this is mostly market-maker hedging), the null is expected.

### Gaps
- No rigorous study of ETF creation/redemption flows predicting constituent returns was found.
- No mega-cap-specific evidence on days-to-cover was found.
- The current FINRA coverage of listed-stock short interest needs confirmation directly from the FINRA API docs.

## 3. Alternative data (credit card, app downloads, web traffic, satellite, job postings, supply chain incl. TSMC monthly revenue)

### Takeaway
Peer-reviewed evidence (satellite parking-lot counts) shows alt data front-runs earnings surprises, but the edge is concentrated around announcements, sits in retailers, and requires paid data. For mega-cap tech, the only free, high-frequency fundamental lead is TSMC's monthly revenue release (around the 10th of each month). No rigorous study of it was found, so it is a hypothesis to test, not an established predictor.

### Cited Findings
- Katona et al. (JFQA 2024/25, "On the Capital Market Consequences of Big Data: Evidence from Outer Space") use satellite car counts at retailers. Traders can anticipate earnings news, the strategy generates abnormal returns around quarterly announcements, and long- and short-side returns are asymmetric. — [Cambridge PDF](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/2F5F99D68D1F8940F61578F198D6C005/S0022109023001448a.pdf/on-the-capital-market-consequences-of-big-data-evidence-from-outer-space.pdf); [Berkeley Haas](https://newsroom.haas.berkeley.edu/magazine/summer-2019/stock-trading-from-space/)
- Berkeley Haas research suggests alt data may shift information advantages to sophisticated investors (a "dark side"). — [Berkeley Haas](https://newsroom.haas.berkeley.edu/?p=10688)
- Purchased credit-card data covers an unknown fraction of total sales, and accuracy depends on panel size and consistency. — [Earnest Analytics](https://www.earnestanalytics.com/insights/alternative-data-what-is-it-how-can-it-help-consumer-brands-and-investors)
- **TSMC monthly revenue:**
  - Media widely treat it as the closest near-real-time read on AI hardware demand.
  - Reported figures: July 2026 about +45% YoY, August about +53% YoY, October 2026 +14.7% MoM and +59.7% YoY.
  - The claim that a 2% miss versus consensus moves the stock more than 3% intraday has no supporting study.
  - Commentators note the series is noisy and seasonal, and that it validates demand, not valuation.
  - Sources: [TIKR](https://www.tikr.com/blog/tsmcs-sales-jumped-15-in-october-nvidias-supplier-isnt-seeing-the-ai-slowdown-yet); [FourWeekMBA (Aug)](https://fourweekmba.com/ai-tsmc-august-revenue-record-ai-demand-signal/); [FourWeekMBA (Jul)](https://fourweekmba.com/ai-tsmc-july-revenue-ai-demand-valuation/); [Nemo](https://explore.nemo.money/insights/tsmc-july-2026-revenue-ai-demand-semiconductor-supply-chain). All are commentary, some promotional.
- A widely circulated "12% annual alpha, 3-week lead" alt-data claim has no verifiable source. Disregard it. — [case-study page](https://offline-pixel.github.io/case-studies/discovering-alpha-with-alternative-data)

### Inferences
- Mega-cap tech revenue is global and diversified, and coverage is heavy (40–60 analysts). Consumer-panel data (cards, apps, web traffic) will move consensus for AAPL/AMZN segments, but any edge is likely priced in by institutions buying the same panels.
- The TSMC lead is mechanically plausible for NVDA, AMD, AVGO and SMH. TSMC reports before US chip designers report their quarters, so YoY-growth *surprises* (actual versus trailing trend) could lead 1–21-day returns. The test must use the release date, not the month-end date, to avoid look-ahead.
- Taiwan's broader monthly revenue releases and Korea's 10-/20-day export data (semis) are similar free, released-early supply-chain signals. **[unverified background]**
- Job postings (LinkUp, Revelio) and app data (Sensor Tower) are paid. Academic evidence for mega-caps specifically was not found.

### Data availability (2026)
- **Free:**
  - TSMC monthly revenue (investor.tsmc.com, plus TWSE MOPS for all Taiwan-listed suppliers).
  - Korea customs export data.
  - Google Trends.
  - Wikipedia pageviews API.
  - SEC 10-Q segment data.
  - **[unverified background]** These URLs and coverage are not checked this session.
- **Paid:**
  - Credit-card panels: Earnest, Facteus, Consumer Edge, Bloomberg Second Measure.
  - Apps: Sensor Tower, data.ai.
  - Web: Similarweb.
  - Satellite: Orbital Insight, RS Metrics.
  - Jobs: LinkUp, Revelio, Thinknum.
  - Supply chain: Bloomberg SPLC, FactSet Revere.

### Test design
1. Scrape TSMC monthly revenue history (2010–2026) with exact release timestamps.
2. Build the surprise signal: YoY growth minus its trailing 12-month mean, and the 3-month-average acceleration.
3. Event study on release day *t*. Measure returns from the close of *t* to *t*+1, *t*+5 and *t*+21 for NVDA, AMD, AVGO, MU, SMH and QQQ, in excess of SPY.
4. Regress each return on the surprise. Expect about 190 events, so use HAC errors.
5. Placebo: random dates in the same months.
6. Watch for overnight timing: TSMC releases during Asia hours, before the US open. Use the US close on *t*−1 to the open on *t* as the "immediate" window, so the tradable window starts at the US open.
7. Pass criterion: |t| > 2.5, given multiple-testing across 6 tickers × 3 horizons.

### Gaps
- No peer-reviewed or quant-research study of TSMC monthly revenue as a return predictor was found.
- No academic studies of credit-card, app, web or job-posting data specifically for mega-cap tech were found.
- 2026 vendor pricing was not researched.

## 4. Cross-asset / macro predictors (VIX term structure, credit spreads, yields, dollar, oil, bitcoin, semi cycle) and the Welch-Goyal critique

### Takeaway
The Goyal-Welch-Zafirov 2024 update (RFS) covers 46 variables through 2021. More than a third of the post-2008 predictors lose even in-sample significance, half of the remaining ones fail out-of-sample, and only a few survive. Market-level option measures (VRP, implied correlation) and short interest are among the better-documented survivors. VIX term structure predicts volatility assets, not equity index returns.

### Cited Findings
- Goyal, Welch & Zafirov (RFS 37(11), 2024) re-examine 29 variables from 26 post-2008 papers plus the 17 original variables, through end-2021. More than one-third no longer have even in-sample significance, half of the rest perform poorly out-of-sample, and "a small number" still perform reasonably both in- and out-of-sample. The specific survivors were not named in the abstract; full text at DOI 10.1093/rfs/hhae044. — [SFI abstract](https://www.sfi.ch/en/publications/a-comprehensive-2022-look-at-the-empirical-performance-of-equity-premium-prediction); [EconPapers](https://econpapers.repec.org/RePEc:oup:rfinst:v:37:y:2024:i:11:p:3490-3557.)
- Welch & Goyal (2008, original): no single predictor would have helped a real-time investor beat the historical-mean equity premium. — [NBER w10483 summary](https://causalclaims.trfetzer.com/paper/w10483.html)
- Xu & Liu (Quant Finance 2024): competing forecasting models, including ML, generally fail to beat the historical average. Hollstein et al. (IJF 2024): OLS OOS forecasts mostly underperform the historical mean internationally. — [IDEAS QF 2024](https://ideas.repec.org/a/taf/quantf/v24y2024i10p1445-1461.html); [Saarland PDF](https://publikationen.sulb.uni-saarland.de/bitstream/20.500.11880/39549/1/1-s2.0-S0169207024000414-main.pdf)
- The VIX term-structure findings (Johnson 2017; Quantpedia OOS) are in Section 1. They predict variance assets, not the index, and are weak or negative OOS for index timing.
- The short interest index and VRP/implied correlation are listed in Sections 1–2 as among the better OOS market predictors.

### Inferences
- **Responses to Welch-Goyal [unverified background]:** Campbell & Thompson (2008) sign/truncation restrictions, Rapach-Strauss-Zhou (2010) forecast combination, and Ferreira & Santa-Clara (2011) sum-of-parts each deliver small positive OOS R² (about 0.5–1.5% monthly). Monthly OOS R² of 0.5% is economically meaningful for a mean-variance investor. The realistic goal is therefore a small, stable tilt, not a large forecast.
- Credit spreads (BAA–AAA, HY OAS), term spread, T-bill rate, dollar index, oil, and bitcoin: no robust OOS equity-premium evidence was found this session. Default spread and term spread were among the original 2008 variables that failed OOS **[unverified background, check GWZ table]**.
- Bitcoin's lead on high-beta tech is a post-2020 co-movement story with very short history. Treat it as a risk-on/off regime correlate, not a validated predictor.
- **Semiconductor cycle:**
  - Candidates: SIA/WSTS monthly billings, Philly Fed / ISM new orders, Korea chip exports, TSMC revenue.
  - These are economically plausible leads for SOX and NVDA, but no OOS study was found.
  - The same test framework as Section 3 applies.
- The Welch-Goyal lesson for this project: always benchmark against the expanding historical mean (or buy-and-hold with vol targeting), report Campbell-Thompson OOS R² and Clark-West p-values, and pre-register the variable list to limit data mining.

### Data availability (2026)
- **Free:**
  - FRED: VIXCLS, BAMLH0A0HYM2 (HY OAS), BAA10Y, DGS10, DGS2, T10Y2Y, DTWEXBGS (dollar), DCOILWTICO.
  - Cboe VIX/VIX3M/VVIX/COR3M.
  - yfinance for BTC-USD, ^SOX, DX-Y.NYB, CL=F.
  - Amit Goyal's website hosts the updated Welch-Goyal predictor dataset, also free. **[unverified background, check current URL]**
  - SIA monthly billings press releases (free, lagged about 5 weeks).
- **Paid:**
  - WSTS detailed data.
  - Bloomberg indices.
  - ICE BofA index history beyond FRED's truncated window. **[unverified background]**: FRED ICE series were shortened to a rolling ~3 years in 2023; verify.

### Test design
1. **Target:** monthly and 21-day-ahead log excess return of the mega-cap tech basket (or QQQ), 2000–2026, with SOX as the target for semi-cycle variables.
2. **Predictors (pre-registered):**
   - VRP (VIX² minus RV)
   - COR3M
   - VIX/VIX3M
   - HY OAS level and 1-month change
   - 10y–2y spread
   - 1-month dollar change
   - 1-month oil change
   - 1-month BTC return (2015+ only)
   - Short Interest Index
   - TSMC YoY surprise
3. **Forecasts:**
   - Univariate expanding-window OLS from 2010, using only data available at the time (apply release lags: FRED series are daily, SIA has a 5-week lag, SI has a 2-week lag).
   - Campbell-Thompson restrictions: zero out a negative forecast and impose correct slope sign.
   - Equal-weight combination forecast (Rapach-Strauss-Zhou style).
4. **Metrics:**
   - OOS R² versus the expanding mean, with a Clark-West test.
   - Certainty-equivalent gain for a mean-variance investor with γ=3, weights capped at 0–1.5×.
   - Results reported separately for 2010–19 and 2020–26 to show decay.
   - Cost: 2 bps per unit of turnover.
5. **Decision rule:** keep a predictor only if OOS R² > 0 in *both* subperiods and the combination improves CER. Otherwise use it only as a vol/regime scaler.

### Gaps
- The names of the "small number" of survivors in GWZ 2024 were not obtained (paywalled). Read Table 1/2 of hhae044, or use Goyal's public data page.
- No source-backed OOS evidence was found for credit spreads, the dollar, oil, bitcoin, or semi-cycle indicators predicting tech or semi returns at daily-monthly horizons.
- No 2025–2026 papers were found that update the Welch-Goyal evaluation beyond 2021 data.
