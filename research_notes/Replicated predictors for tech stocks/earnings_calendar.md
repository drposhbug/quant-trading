# Earnings/Event and Calendar-Effect Predictors for US Mega-Cap Tech (daily to monthly)

Scope note: research conducted 2026-11-18 using about 15 search/fetch calls. Several findings come from secondary summaries (Alpha Architect, Quantpedia, CXO, Substack posts, UCLA Anderson Review) rather than full paper text. These are flagged. Items marked "[unsourced]" are the researcher's own domain knowledge or methodology. They are kept out of Cited Findings on purpose and should be verified before they go in a report.

## Q1. Do PEAD, the earnings announcement premium, the pre-earnings run-up and peer/supply-chain earnings spillovers still exist in mega-caps?

### Takeaway
Classic accounting-surprise PEAD is essentially dead in large caps. The best evidence (Martineau 2022; Subrahmanyam 2025 replication) puts it near zero for non-microcaps since about 2001–2006. Defenders of PEAD rely on samples that include microcaps or on return-based or text-based surprise measures. The earnings announcement premium (EAP) was documented in-sample (Savor-Wilson ~9.9%/yr). The evidence on size points both ways, and there are signs the premium is fading. Peer and supply-chain spillovers (Cohen-Frazzini customer momentum, 1.55%/mo in-sample) are real in the older literature. I found no post-2010 mega-cap-specific test, and the effect is most plausibly weakest in heavily covered, commonly owned names like NVDA/AVGO/AMD/TSM.

### Cited Findings
**PEAD**
- Martineau (2022, "Rest in Peace Post-Earnings Announcement Drift"): PEAD began disappearing from non-microcap stocks in 2001 and had "completely disappeared" by 2006. Prices of most stocks now adjust fully on announcement day. He attributes this to decimalization (2001) and to Reg NMS (2005), which accelerated HFT. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/)
- Subrahmanyam (2025 working paper) replicates the earnings-drift factor on US data from Feb 2001 to Dec 2024. All stocks: t = 2.18. Excluding microcaps (bottom 20th NYSE percentile, ~3% of market cap): t = 1.43, not significant. He concludes microcaps drive the apparent drift. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/)
- Counter-evidence: Dickerson, Julliard & Mueller (JFE 2025, "co-pricing factor zoo") find an earnings-drift factor remains important. Their factor is built from announcement abnormal returns, not accounting SUE. Hirshleifer, Peng & Wang (RFS 2025) find drift with t ≈ 14 but do not filter out microcaps. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/)
- Text-based surprise (PEAD.txt, JFQA): drift from text-based earnings-call surprise is "considerable even in recent years when the classic PEAD is close to 0." — [PEAD.txt, Cambridge/JFQA](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/5EB217BB68B5FB054FE38541BAAC4679/S0022109022001181a.pdf/peadtxt-post-earnings-announcement-drift-using-text.pdf)
- Small recent large-cap test (SSRN, Luthra, 2025–2026): 40 earnings events at 10 large US companies. Mean 20-day drift +0.67% (SD 6.29%, t = 0.67), not significant. Very small sample. — [SSRN 7137218](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7137218)
- Non-peer-reviewed blog: 43,111 US announcements, 2023–2026. Reports a drift spread in every size group, including large caps (~2.0 points), and says the spread compressed sharply in 2025–26. Methodology unverified. — [guptagaurav.info](https://guptagaurav.info/articles/earnings-drift)

**Earnings announcement premium (EAP)**
- Savor & Wilson (JF 2016): firms scheduled to report earn an annualized abnormal return of ~9.9%, interpreted as compensation for systematic risk. Early announcers earn more than late ones. — [econbiz record](https://www.econbiz.de/Record/earnings-announcements-and-systematic-risk-wilson-mungo/10011426694); [Wharton draft](https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Draft20111215p_edited.pdf)
- Size dependence is contested. Barber et al. (global EAP) find the premium is larger for the smallest stocks than the largest, by roughly 6%/yr. Earlier work by Lamont found the largest premium among the biggest US firms. — [Barber et al. (TAU seminar PDF)](https://en-coller.tau.ac.il/sites/nihul_en.tau.ac.il/files/media_server/Recanati/management/seminars/account/barber.pdf); [Alpha Architect summary](https://alphaarchitect.com/2016/09/28/introducing-the-global-earnings-announcement-premium/)
- A UChicago dissertation finds the market-level effect is largest for "bellwether" (large, market-correlated) firms, while the firm-level premium is concentrated in small stocks. — [Lombardi thesis](https://knowledge.uchicago.edu/record/163/files/Lombardi_uchicago_0330D_14112.pdf)
- "The Disappearing Earnings Announcement Premium" (IIMB ARC 2020) argues the premium has shifted from earnings-announcement windows to pre-announcement 8-K filing periods. Full text returned 403, so magnitudes could not be checked. — [IIMB PDF](https://www.iimb.ac.in/ARC2020/Papers/The_Disappearing_Earnings_Announcement_Premium.pdf)

**Peer / supply-chain spillovers**
- Cohen & Frazzini (JF 2008, "Economic Links and Predictable Returns"): customer-momentum long-short portfolio earns 1.55%/month (~18.6%/yr) abnormal return. Links come from SFAS 131 major-customer disclosures. The mechanism is limited attention. Common mutual-fund ownership of the customer and supplier weakens the predictability. — [typeset PDF](https://typeset.io/pdf/economic-links-and-predictable-returns-1acnxz4kzc.pdf); [SUFE summary](https://academicnewsletter.sufe.edu.cn/info/360813)
- An NBER working paper finds that industry, customer, customer/supplier-industry and technology momentum alphas become insignificant or negative after controlling for its "CS momentum" factor. These spillovers may be one common phenomenon, not separate signals. — [NBER w25201](https://www.nber.org/system/files/working_papers/w25201/revisions/w25201.rev0.pdf)
- Intra-industry information transfer literature (Foster 1981 onward): Hann, Kim & Zheng (RAST 2019) show the first announcer's implied-volatility change is positively associated with peers' IV changes, more strongly when the announcer is a bellwether. Brushko & Ferris find that processing of the first industry announcement is delayed. One 1996–2015 study links peer announcements to analyst-forecast-based drift. — [RePEc RAST 2019](https://ideas.repec.org/a/spr/reaccs/v24y2019i3d10.1007_s11142-019-9487-1.html); [CERGE-EI WP663](https://www.cerge-ei.cz/pdf/wp/Wp663.pdf); [core.ac.uk](https://core.ac.uk/download/286029861.pdf)

### Inferences
- For AAPL/MSFT/NVDA/GOOGL/AMZN/META/AVGO/TSM, assume SUE-based PEAD ≈ 0 after costs. Any residual drift is concentrated in days 0–2, where execution matters most.
- The NVDA → AVGO/AMD/TSM spillover is the kind of link Cohen-Frazzini predicts. Those names are among the most commonly held and most heavily covered stocks, and common ownership is exactly the condition under which the original paper finds the effect weakens. Expect the same-day reaction (co-movement on NVDA's announcement day, after hours) to capture almost all of it. A next-day or multi-day drift is unlikely to be tradable.
- The EAP is the most plausible survivor, because it is framed as a risk premium rather than mispricing. For mega-caps, though, it is an expected return of roughly tens of bps per event, and announcement-week volatility is very high.
- [unsourced] Proposed test design, for all of these: build an event panel of mega-cap earnings dates (2010–2026), using the announcement timestamp and before-open/after-close (BMO/AMC) flag to set day 0 correctly. Measure the CAR of the market-adjusted (or SMH/QQQ-beta-adjusted) return over windows [−5,−1] (run-up / EAP), [0,1] (reaction) and [2,20], [2,60] (PEAD). Sort by surprise using (a) EPS vs consensus, (b) the day-0/1 abnormal return (return-based SUE, which is what the DJM factor uses), and (c) guidance change. For spillovers: when NVDA reports AMC, regress AVGO/AMD/TSM/MU/SMCI next-open-to-close and days [2,5] returns on NVDA's day-1 abnormal return. Use block bootstrap over events. Report results split pre- and post-2016. With ~8 names × 4 quarters × 16 yrs ≈ 500 events, power is low, so pre-register the windows.
- [unsourced] Data: earnings dates and EPS surprises are available roughly free via yfinance / Nasdaq / Zacks calendars, but history is patchy and BMO/AMC timing is unreliable. Clean consensus and timestamps require I/B/E/S (WRDS, paid) or a paid vendor (Estimize, FactSet, Refinitiv). SFAS 131 customer links are in Compustat Segments (paid). Free alternative: hand-code links from 10-K "major customer" disclosures on EDGAR.

### Gaps
- No source found for the pre-earnings run-up (e.g., Barber et al. / Aboody et al. style pre-announcement drift) specifically in post-2010 large caps.
- No post-2010 replication of Cohen-Frazzini restricted to mega-caps or to the AI/semiconductor supply chain. The NVDA→AVGO/AMD/TSM spillover is untested in the sources found.
- I could not get magnitudes from the "Disappearing EAP" paper (403).
- Cost-sensitivity numbers specific to PEAD in large caps were not found. Martineau's result makes the question moot for classic SUE.

## Q2. Pre-FOMC drift, turn-of-month, pre-holiday, options-expiration week, index rebalance: status post-2015?

### Takeaway
Peer-reviewed post-2015 evidence is negative or weak for most of these. The pre-FOMC drift faded sharply after ~2015 (Kurov et al.), though practitioner backtests through 2024 claim it is still alive in high-VIX regimes. The S&P 500 inclusion effect has largely disappeared (Greenwood-Sammon, JF 2025). The pre-holiday effect is now a small-cap phenomenon. Turn-of-month is the most persistent index-level calendar effect, but the post-2008 support is practitioner-only. Options-expiration week (Stivers-Sun) was specifically a large, heavily optioned stock effect, with an in-sample period ending in 2008 and no out-of-sample update found.

### Cited Findings
**Pre-FOMC drift**
- Lucca & Moench (JF 2015) sample: 1994–2011. Later studies find the effect much weaker afterward. — [ResearchGate, Disappearing Pre-FOMC Drift](https://www.researchgate.net/publication/345940053_The_Disappearing_Pre-FOMC_Announcement_Drift)
- Kurov, Halova Wolfe & Gilbert (2021, "The Disappearing Pre-FOMC Announcement Drift"): the drift essentially disappeared after 2015, for meetings both with and without press conferences. A secondary summary cites the mean falling from ~0.49% to ~0.05% per meeting; that number has not been checked against the paper. They attribute the drift to resolution of uncertainty, measured by VIX. — [ResearchGate](https://www.researchgate.net/publication/345940053_The_Disappearing_Pre-FOMC_Announcement_Drift); [Applied Economics 2024 follow-up](https://www.tandfonline.com/doi/full/10.1080/00036846.2024.2322573)
- Practitioner backtest (Quantseeker, 1993–2024, SPY/QQQ on EODHD data): full-sample CAGR ~4% and Sharpe 0.5–0.6. The strategy was "flat between 2016 and 2019 before gaining momentum again". It reports no t-stats or subperiod figures and says the effect is stronger when VIX is high. — [Quantseeker](https://www.quantseeker.com/p/trading-the-fed-the-pre-fomc-drift)
- A related paper documents an "FOMC announcement reversal". — [ResearchGate](https://www.researchgate.net/publication/362775066_The_FOMC_Announcement_Reversal)

**Turn-of-month (TOM)**
- Maberly & Waggoner (Atlanta Fed WP 2000-11): TOM effects in S&P 500 futures disappear after 1990, and the result carries over to spot. They warn about out-of-sample inference from in-sample regularities. — [Atlanta Fed](https://www.atlantafed.org/research/publications/wp/2000/11.aspx)
- Xu & McConnell (2006): TOM persists over 1987–2005 and is not confined to small stocks or the US. — [CXO / Quantpedia summary](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)
- Carchano & Pardo (2011): only 3 of 188 calendar anomalies are significant in both half-samples, and the S&P 500 TOM is one of them. They caution about data snooping. — [CXO Advisory](https://cxoadvisory.com/calendar-effects/stock-index-futures-calendar-effects)
- Practitioner (Potomac/Norgate, S&P 500 1980–Q3 2024): holding only 4 TOM days per month earned an annual return just 0.89% lower than being invested on all other days. This is a hypothetical backtest. — [ETF Trends](https://www.etftrends.com/etf-strategist-channel/turn-month-effect/)

**Pre-holiday**
- Ko & Yang (Critical Finance Review 2024), extending Ariel (1990) through 1983–2019: the pre-holiday effect now exists only among small firms. For large firms the difference is insignificant, especially after 1990. — [CFR PDF](https://cfr.ivo-welch.info/published/papers/ko2021pre.pdf); [nowpublishers](https://nowpublishers.com/article/Details/CFR-0111)
- An S&P 500 1930–1999 study finds the effect "greatly diminished after 1987". — [core.ac.uk](https://core.ac.uk/works/2843318)
- Robins & Smith (2019, 1926–2016): the effect remains significant in the CRSP VW portfolio and low-size portfolios in each subperiod, with a slight decline over time. — [ASU W.P. Carey](https://knowledge.wpcarey.asu.edu/20190311-dont-bet-holiday-effect-boost-market-returns)

**Options-expiration week**
- Stivers & Sun (JBF 2013, S&P 100 stocks): weekly returns in expiration weeks (the week containing the third Friday) are high, and the following week modestly underperforms. The 2010 WP used 28 large caps, 1996–2008: 0.45% in expiration weeks vs 0.12% in other weeks, larger when option/stock volume is high. In the pre-listed-options era (1948–1972) the expiration-week return was not unusual. The proposed mechanism is market-maker hedge rebalancing. — [RePEc JBF 2013](https://ideas.repec.org/a/eee/jbfina/v37y2013i11p4226-4240.html); [Quantpedia](https://quantpedia.com/strategies/option-expiration-week-effect); [CXO](https://cxoadvisory.com/calendar-effects/option-expiration-week-stock-return-drill-down)
- Garcia-Ares & Muravyev (2025, per a Substack summary): more than half of monthly anomaly returns occur in a two-day option-expiration window. This is secondary and unverified. — [Harbourfront Quant](https://harbourfrontquant.substack.com/p/expiration-effects-and-return-anomalies)

**Index rebalance**
- Greenwood & Sammon (JF 2025, 80(2):657–698, "The Disappearing Index Effect"): S&P 500 addition abnormal returns fell from ~7.4% in the 1990s to under 1% recently. Deletion effects fell from −16.6% (1990s) to −0.6% (2010–2020). Drivers: more additions are migrations from the MidCap 400 (offsetting flows) and greater liquidity provision. Growth of index AUM did not raise the effect. — [Harvard DASH](https://dash.harvard.edu/server/api/core/bitstreams/a6521969-9113-4987-a523-c66fa908d420/content); [NBER w30748](https://www.nber.org/system/files/working_papers/w30748/w30748.pdf); [Alpha Architect](https://alphaarchitect.com/disappearing-index-effect/)

### Inferences
- For a mega-cap tech book these are timing overlays on beta, not alpha sources. Pre-FOMC and TOM operate at index level. A mega-cap tech basket (QQQ-like) is high-beta to SPX, so it should inherit any index effect scaled by beta.
- The index-inclusion effect is irrelevant for existing mega-caps, which are already members. Remaining rebalance flows are Nasdaq-100 annual/special rebalances (e.g., the 2023 special rebalance) and S&P quarterly share/float changes. These are anticipated and liquidity-provided in the most liquid names.
- Options-expiration week is the one calendar effect whose mechanism specifically targets heavily optioned large caps. That fits AAPL/NVDA/TSLA/MSFT. But the weekly/0DTE options boom since ~2022 has spread gamma across every day, which plausibly dilutes a monthly-OpEx-specific effect [unsourced speculation].
- [unsourced] Test design. Daily returns of each mega-cap and an equal-weight basket, 2000–2026, split pre-2015 / 2015–2026. Regress on dummies:
  - pre-FOMC: day before the 2pm announcement (dates from federalreserve.gov)
  - TOM: last trading day plus first 3 of the month
  - pre-holiday: day before NYSE holidays
  - OpEx week: week containing the 3rd Friday
  - post-OpEx week
  
  Use HAC SEs and report bps/day and the hit rate. Compare to buy-and-hold, and charge 1–2 bps round-trip per switch on QQQ. Shuffle-date placebo tests guard against snooping.
- [unsourced] Data: all free. Use daily OHLC (yfinance/Stooq), the FOMC calendar (Fed website) and NYSE holiday calendars. Intraday 2pm timing (pre-FOMC is properly measured 2pm(t−1) → 2pm(t)) needs minute data, which is paid or limited free (Polygon/Alpaca free tiers).
- Cost sensitivity: these trade at most ~8–40 times a year on an ETF with roughly a 1 bp spread. Costs are small relative to a claimed ~49 bp pre-FOMC move but comparable to a ~5 bp post-2015 move.

### Gaps
- No peer-reviewed post-2015 TOM study for US large caps was found. Persistence evidence after 2008 is practitioner backtests.
- No out-of-sample (post-2008) replication of Stivers-Sun was found.
- The exact Kurov et al. per-meeting numbers come from a secondary summary.
- No evidence was found on Nasdaq-100 rebalance effects specifically.

## Q3. Analyst revisions and guidance changes: effect size in mega-caps

### Takeaway
I found no source quantifying analyst-revision or guidance-change drift for mega-caps specifically. The academic anomaly (post-forecast-revision drift) is documented on broad US samples. Generic anomaly-decay evidence (McLean-Pontiff; Chen-Velikov) implies little net alpha remains in liquid names.

### Cited Findings
- Post-forecast-revision drift exists on broad US samples and is attributed largely to analysts underreacting in their own revisions (positive serial correlation in individual analysts' revisions). — [JBFA 2020, RePEc](https://ideas.repec.org/a/bla/jbfnac/v47y2020i9-10p1151-1181.html)
- Upward revisions are found to be more informative than downward ones (asymmetry). — [search summary of core.ac.uk / HKU papers](https://hub.hku.hk/bitstream/10722/182132/1/Content.pdf)
- Hong, Lim & Stein (JF 2000): momentum profits decline with size and analyst coverage. This is a bibliographic reference only; I did not read its findings directly. — [core.ac.uk](https://core.ac.uk/download/83969469.pdf)
- Market-condition context (not a predictive test): the Citi US Earnings Revision Index fell for 14 straight weeks into March 2025. — [SentimenTrader](https://sentimentrader.com/blog/a-persistent-decline-in-us-earnings-revisions)

### Inferences
- Mega-caps have 40–70 covering analysts, which per Hong-Lim-Stein-style logic is the setting with the least underreaction. Expect revision drift to be small and mostly absorbed within a day or two.
- Guidance changes for mega-caps are usually released with earnings, so they collapse into the earnings-event test in Q1. Measure the guidance surprise (new guide midpoint vs prior consensus) and test [2,20]-day drift.
- [unsourced] Data: consensus revision histories need I/B/E/S detail files or FactSet/Refinitiv (paid). Free proxies (yfinance `eps_trend` / `eps_revisions`) give only current snapshots, not point-in-time history, so you must archive them going forward. That rules out a historical backtest without paid data.

### Gaps
- No mega-cap-specific estimate of revision drift or guidance drift was found, and nothing post-2010 or post-publication specifically for revisions.

## Q4. Which effects are already arbitraged away in the largest, most liquid names?

### Takeaway
The cross-anomaly literature says decay is worst exactly where arbitrage is cheapest. Post-publication returns fall ~58% on average (McLean-Pontiff), more for liquid, low-idiosyncratic-risk portfolios. After costs, decay and the post-2000s trading era, the average anomaly's expected return is ~4 bps/month (Chen-Velikov). Classic PEAD, the index-inclusion effect and the large-cap pre-holiday effect are effectively gone. Pre-FOMC drift is much weaker and regime-dependent. TOM, EAP and OpEx-week are unresolved candidates worth an out-of-sample test.

### Cited Findings
- McLean & Pontiff (JF 2016, 97 predictors): returns are 26% lower out-of-sample and 58% lower post-publication. The implied publication effect is ~32%. Decay is larger for predictors with higher in-sample returns and for those cheaper to arbitrage (liquid stocks, low idiosyncratic risk). — [gwern PDF](https://Www.Gwern.net/doc/economics/2016-mclean.pdf); [CXO](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation)
- Chen & Zimmermann (RAPS 2020, 156 predictors): publication-bias-adjusted returns are only ~12% below in-sample. Bias is too small to explain post-publication decay (p = .0001), which points to mispricing that gets arbitraged. A replication finds post-publication returns ~50% smaller. — [Fed FEDS 2018-033](https://www.federalreserve.gov/econres/feds/files/2018033pap.pdf); [Fed page](https://www.federalreserve.gov/econres/feds/publication-bias-and-the-cross-section-of-stock-returns.htm)
- A study using the Chen-Zimmermann data finds long-short returns decay ~65% post-publication, and ~35% lower going forward when peer review labels the predictor as risk. — [AFA/afajof](https://afajof.org/management/viewp.php?n=8400)
- Chen & Velikov (JFQA 2023, 204 anomalies): after effective spreads, post-publication decay and the modern trading era (early 2000s on), the average anomaly's expected return is ~4 bps/month. The best are ~10 bps after controlling for data mining, and combinations reach ~20 bps net. — [Cambridge/JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225)
- PEAD gone in non-microcaps since ~2006; decimalization/HFT are the cited mechanism. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/)
- S&P 500 inclusion effect fell from ~7.4% to under 1%. — [Harvard DASH](https://dash.harvard.edu/server/api/core/bitstreams/a6521969-9113-4987-a523-c66fa908d420/content)
- Pre-holiday effect is insignificant for large firms. — [Ko & Yang, CFR](https://cfr.ivo-welch.info/published/papers/ko2021pre.pdf)
- Pre-FOMC drift faded after 2015. — [Kurov et al., ResearchGate](https://www.researchgate.net/publication/345940053_The_Disappearing_Pre-FOMC_Announcement_Drift)

### Inferences
Status scorecard for mega-cap tech, as of 2026. Judgment calls are based on the citations above.

| Effect | Status | Basis |
|---|---|---|
| SUE-PEAD | Dead | Martineau; Subrahmanyam |
| Index inclusion | Dead for incumbents | Greenwood-Sammon |
| Pre-holiday | Dead for large caps | Ko-Yang |
| Pre-FOMC | Mostly faded, regime-dependent | Kurov et al. vs Quantseeker |
| TOM | Possibly alive at index level | Practitioner evidence only |
| EAP | Possibly alive as a risk premium | Contested on size |
| OpEx-week | Untested out of sample | In-sample ends 2008 |
| Revision / guidance drift | Unknown, likely small | No mega-cap evidence found |
| Peer / supply-chain spillover | Likely same-day only | No mega-cap test found |

- Any surviving edge in mega-caps should be expected in single-digit to low-double-digit bps per event. Budget for that, and treat t > 3 on post-2015 data as the bar, per Harvey-Liu-Zhu style multiple-testing logic [unsourced reference].
- Text-based or return-based surprise measures (PEAD.txt; the DJM factor) are the variants that still show drift. They are the only earnings-drift designs worth testing on mega-caps.

### Gaps
- Neither McLean-Pontiff nor Chen-Velikov breaks out decay for the top-50 or mega-cap bucket specifically. The "worse in large caps" claim is an inference from their liquidity/idiosyncratic-risk splits.
- No 2025–2026 peer-reviewed evidence specific to mega-cap tech was found for any of these effects.
