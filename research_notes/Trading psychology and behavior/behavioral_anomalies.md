# Behavioral-finance anomalies for a daily-rebalanced, long-only, 12-name US mega-cap tech portfolio (skeptic / replication view, as of Nov 2026)

Universe: TSLA, AAPL, MSFT, NVDA, GOOGL, AMZN, META, AVGO, TSM, AMD, ORCL, SPCX. Long-only means any anomaly whose return sits in the short leg (most of the behavioral ones) can only be used as "underweight / exclude", never "short".

## Which anomalies survive in mega-caps after 2010 and after costs? Which have been arbitraged?

### Takeaway
The general literature says most published anomalies are concentrated in micro/small caps and decay roughly 50-70% after publication. Among the behavioral candidates, the ones with the best documented evidence *in large/liquid stocks* are (a) residual / industry-adjusted short-term reversal (weekly to monthly), (b) the overnight-vs-intraday return split, including attention-driven buying at the open that reverses during the day, and (c) momentum variants (52-week-high, frog-in-the-pan). Each of these is still weak or unproven *after 2010, net of costs, inside a 12-stock universe*. PEAD in large caps has been essentially gone since about 2006, and that decay is now disputed. The MAX/lottery, IVOL, Google-search attention and sentiment effects are mostly small-cap or short-leg effects, and a long-only mega-cap book cannot harvest them.

### Cited Findings

**Overall replication and decay (base rates)**
- McLean & Pontiff (JF 2016), 97 predictors: returns are 26% lower out-of-sample and 58% lower post-publication. About 32 points of the decline is attributed to publication-informed trading. The decline is larger for predictors with higher in-sample returns, and returns are higher in high-idiosyncratic-risk, low-liquidity stocks. — [Gwern copy of paper](https://Www.Gwern.net/doc/economics/2016-mclean.pdf); [fa-mag summary](https://fa-mag.com/news/markets-don-t-work-as-well-as-we-thought-25092.html?section=68)
- Jacobs and coauthors (international) find the US is the only country with a reliable post-publication decline in long/short returns. — [HU Berlin paper](https://www.wiwi.hu-berlin.de/en/Professorships/bwl/finance/seminars/papers-fin-acc-res-seminars/17s/jacobs.pdf)
- Hou, Xue & Zhang, "Replicating Anomalies" (RFS 2020), 447 anomalies. With NYSE breakpoints and value weights, 286 (64%) are insignificant at 5%, including 95 of 102 liquidity variables. At t > 3, 380 (85%) fail. They blame microcaps, which are about 3% of market cap but about 60% of names. — [NBER w23394](https://www.nber.org/papers/w23394.pdf); [Alpha Architect](https://alphaarchitect.com/replicating-anomalies/)
- Chen & Zimmermann's open-source data reproduces nearly 100% of the literature's in-sample predictability. Post-publication returns are about 50% smaller, which replicates McLean-Pontiff. Restricting post-publication data to post-2005 raises the decay to about 72% (Chen & Velikov). — [Chen-Zimmermann CFR](https://cfr.ivo-welch.info/published/papers/chen2021open.pdf); [Fed FEDS 2021-037](https://www.federalreserve.gov/econres/feds/files/2021-037pap.pdf)
- Jensen, Kelly & Pedersen (JF 2023) find 84.9% of 153 factors "replicate" across 93 countries. But they use capped value weights (winsorized at the NYSE 80th percentile) so that no mega-stock dominates, and their returns are gross, not net. Their optimism therefore does not carry over to a mega-cap-only book. — [Alpha Architect](https://alphaarchitect.com/is-there-a-replication-crisis-in-finance/); [CBS](https://research.cbs.dk/en/publications/is-there-a-replication-crisis-in-finance/)

**Short-term reversal, industry-adjusted and residual reversal**
- Conventional short-term reversal profits largely disappear after trading costs in several studies. De Groot, Huij & Zhou (2011) show the cost drag comes mainly from small caps, and that net reversal profits are large and positive among large caps over the last decade of their sample. — [EFMA 2011 paper](https://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2011-Braga/papers/0259_update.pdf)
- Blitz et al. (2012): residual (factor-adjusted) reversal earns more than 8% per year net of costs and is robust over time and across stocks. — [Robeco](https://www.robeco.com/en-uk/insights/2011/11/short-term-residual-reversal); [EFMA 2012](https://www.efmaefm.org/0EFMSYMPOSIUM/2012/papers/017_update.pdf)
- Robeco (2023) asks whether short-term reversal has "truly vanished". Its answer is that enhanced versions, which combine reversal with short-term industry and factor momentum, double the risk-adjusted return. The framing implies the plain version has weakened. — [Robeco 2023](https://www.robeco.com/en-us/insights/2023/10/reversing-the-trend-of-short-term-reversal)
- Reversal is stronger within industries than across them (Da & Schaumburg; Rosenberg-Reid-Lanstein). Da, Liu & Schaumburg (Mgmt Sci 2014): the return component not explained by cash-flow news is what reverses. — [NY Fed SR 513](https://www.newyorkfed.org/research/staff_reports/sr513.html); [RePEc](https://econpapers.repec.org/RePEc:inm:ormnsc:v:60:y:2014:i:3:p:658-674)
- In S&P 500 stocks, short-run reversal is of a magnitude "not easily explained by... direct transaction costs alone." — [Kellogg](https://www.kellogg.northwestern.edu/academics-research/research/detail/2008/short-run-reversal-in-the-market-for-large-stocks)
- Reversal returns jump in the weeks after large market declines. The strategy behaves like a short-volatility / liquidity-provision bet. Frazzini-Israel-Moskowitz live-trading costs are under a tenth of earlier academic estimates. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- Intra-industry reversals show up in all sub-periods, including recent decades after tick-size reductions. — [NUS paper](https://web2-bschool.nus.edu.sg/wp-content/uploads/media_rp/publications/BwXb81392625636.pdf)

**Earnings-day overreaction / PEAD**
- Martineau (CFR 2022), "Rest in Peace PEAD": for large stocks PEAD has been non-existent since 2006, and prices fully reflect surprises on the announcement date. — [CFR](https://nowpublishers.com/article/Details/CFR-0122)
- Two 2025 accepted papers dispute this and say PEAD is alive. Subrahmanyam argues the disagreement comes from research-design choices. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again)
- Hou-Xue-Zhang list abnormal earnings-announcement returns among the anomalies that do replicate. — [Alpha Architect](https://alphaarchitect.com/replicating-anomalies/)
- The MAX effect is absent when the max-return day is driven by an earnings announcement (Nguyen & Truong 2017). — [EFMA 2017](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2017-Athens/papers/EFMA2017_0220_fullpaper.pdf)

**Momentum and its behavioral variants**
- George & Hwang (JF 2004): nearness to the 52-week high explains a large share of momentum profits. Sample is all CRSP stocks, 1963-2001. International tests are mixed (significant in 10 of 16 markets), and the strategy turns negative in pessimistic-sentiment states. — [paper](https://typeset.io/pdf/the-52-week-high-and-momentum-investing-4u9j16d52p.pdf); [Quantpedia](https://quantpedia.com/Screener/Details/88); [Massey](https://mro.massey.ac.nz/bitstreams/99e67c25-4ed2-4314-bd0b-062930e5742b/download)
- Da, Gurun & Warachka (RFS 2014), frog-in-the-pan: 6-month momentum falls monotonically from 5.94% (continuous information) to -2.07% (discrete information), 1927-2007. Continuous-information momentum stays significant for about 8 months, discrete for about 2. More media coverage goes with discrete information. — [paper](https://www3.nd.edu/%7Ezda/Frog.pdf); [Alpha Architect](https://alphaarchitect.com/frog-in-the-pan-identifying-the-highest-quality-momentum-stocks/)
- Grinblatt & Han: the capital-gains overhang created by the disposition effect is the key driver of momentum. With CGO in the regression, momentum disappears. — [NBER w8734](https://nber.org/papers/w8734). No direct US out-of-sample replication of the "CGO subsumes momentum" result turned up. A 2025 China study using CGO diverges from the US results. — [arXiv 2505.20608](https://export.arxiv.org/pdf/2505.20608)

**Overnight vs intraday split**
- Lou, Polk & Skouras (JFE 2019): momentum profits accrue overnight, while value and size accrue intraday. Each component shows same-period continuation and cross-period reversal lasting years ("tug of war" between clienteles). — [LSE PDF](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf); [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/)
- Kelly & Clark (J. Asset Mgmt 2011): the market earns its return overnight, and characteristic-sorted portfolios often show day and night returns of opposite sign. — [Lafayette](https://dspace.lafayette.edu/handle/10385/1012); [Jones-Pyun-Wang](https://sjpyun.github.io/daynight.pdf)
- Berkman, Koch, Tuttle & Zhang (JFQA 2012), 3,000 largest US stocks, 1996-2008: attention events lead to retail buying concentrated at the next open. High-attention, low-institutional-ownership stocks earn +0.2 to 0.3% overnight and reverse -0.2 to -0.4% intraday. The effect is stronger in hard-to-value stocks. — [Cambridge/JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/paying-attention-overnight-returns-and-the-hidden-cost-of-buying-at-the-open/F9AAD159B512C651F09D5D52011D88E0); [KU PDF](https://kuscholarworks.ku.edu/bitstream/1808/10965/1/Koch_Paying%20Attention.pdf)
- Aboody et al. (JFQA 2018) treat overnight returns as a firm-level sentiment measure. — [PDF](https://anderson-review.ucla.edu/wp-content/uploads/2021/03/Aboody-et-al_overnight_returns_and_firmspecific_investor_sentiment_JFQA2018.pdf)
- Harvesting the overnight effect by buying at the close and selling at the open is "prohibitively expensive" in single stocks, which is why the NightShares ETFs used futures. — [WealthManagement](https://www.wealthmanagement.com/etfs/new-etfs-aim-to-capture-those-overnight-returns-in-stock-market)

**Attention (volume, news, Google search)**
- Da, Engelberg & Gao (JF 2011), Russell 3000, 2004-2008: rising ticker-search volume (SVI) predicts higher prices over the next 2 weeks and a reversal within the year. The price pressure is mostly in smaller stocks, and a later paper finds it significant only among smaller stocks. — [paper](https://rady.ucsd.edu/faculty/directory/engelberg/pub/portfolios/GOOGLE.pdf); [CXO](https://www.cxoadvisory.com/sentiment-indicators/google-search-data-as-a-measure-of-investor-attention/)

**Lottery / MAX and the IVOL puzzle**
- Bali, Cakici & Whitelaw (JFE 2011): stocks with high MAX underperform. Caliskan (2020), using the same data, finds the effect is concentrated before the 1990s, is largely a proxy for IVOL, and is unstable over time. It vanishes after bear markets, and it is strongest in stocks with low institutional ownership. — [NYU WP](https://archive.nyu.edu/jspui/bitstream/2451/27871/2/wpa08025.pdf); [IDEAS Caliskan](https://ideas.repec.org/a/spr/manrev/v70y2020i4d10.1007_s11301-019-00176-3.html); [EFMA 2017](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2017-Athens/papers/EFMA2017_0220_fullpaper.pdf)
- IVOL puzzle (Ang-Hodrick-Xing-Zhang 2006): Detzel et al. replicate it as significant even in the largest size quintile. But the 1963-2000 AHXZ sample shows an unusually strong effect relative to pre-1963 and post-2000. The effect is fragile to the estimation window and to MAX controls, and it is partly explained by reversal in small high-IVOL stocks. — [Detzel CFR](https://cfr.ivo-welch.info/published/papers/detzel2019cross.pdf); [Kowalke replication](https://jums.ub.uni-muenchen.de/JMS/article/download/5167/3450)

**Sentiment (Baker-Wurgler)**
- Stambaugh, Yu & Yuan (JFE 2012): 11 anomalies are stronger after high Baker-Wurgler sentiment, and the effect is concentrated in the short leg. Sentiment shows no relation to long-leg returns. — [NBER w16898](https://www.nber.org/papers/w16898.pdf); [AQR](https://www.aqr.com/Our-Firm/AQR-Insight-Award/2012/Honorable-Mention-2)

**Analyst extrapolation / glamour**
- Bordalo, Gennaioli, La Porta & Shleifer (JF 2019): 20 more years of data confirm La Porta (1996). Stocks with low long-term-growth forecasts (LLTG) outperform stocks with high forecasts (HLTG), whose forecasts are too optimistic and later revised down. HLTG stocks have higher beta and do worse in downturns. — [NBER w23863](https://www.nber.org/papers/w23863.pdf); [Harvard](https://shleifer.scholars.harvard.edu/publications/diagnostic-expectations-and-stock-returns-0)

### Inferences
- **Arbitraged or dead for this use case:** PEAD in large caps (gone since about 2006 per Martineau; contested). MAX/lottery (pre-1990s, low-institutional-ownership, short leg). Google SVI price pressure (small caps, 2004-08 sample). Baker-Wurgler sentiment, used directly (short leg of small, speculative stocks; long legs unaffected). Every mega-cap here is heavily held by institutions and covered by dozens of analysts, which is the opposite of the conditions where these effects live.
- **Plausibly alive in large caps, at least gross:** residual or industry-adjusted 1-week to 1-month reversal, and the overnight/intraday clientele split. Both are tied to liquidity provision against retail and attention flows, which are high in TSLA, NVDA, AMD and SPCX. Their economic return is partly compensation for liquidity risk (short-vol-like), not a free lunch.
- **Momentum variants:** 52-week-high and FIP are cross-sectional *ranking refinements* of momentum. With 12 names they can at most tilt weights. The evidence is from broad CRSP samples. I found no source specific to mega-caps after 2010.
- **Glamour / LTG:** nearly the whole universe would count as "high LTG" relative to the market. Within 12 names the LTG spread is narrow, and no within-mega-cap evidence was found. The useful lesson is risk management: HLTG stocks do much worse in downturns.
- **"Industry-adjusted" is ill-defined here.** All 12 names are effectively one industry (tech/semis plus TSLA and SPCX). Residual reversal should instead use returns net of market, a semis/tech factor (e.g., SOXX/XLK) and each name's beta.

### Gaps
- No source found testing short-term reversal, 52-week-high, FIP or CGO *specifically within the top ~50 US stocks after 2010, net of costs*. All large-cap evidence above is "largest quintile / S&P 500 / top 3,000" and mostly predates 2012.
- Momentum crash risk (e.g., Daniel-Moskowitz) and post-2009 large-cap momentum performance were not verified in this session.
- No full-text verification of the 2025 pro-PEAD papers. Kelly & Clark is cited via secondary summaries only.
- SPCX: could not verify what this ticker is or how much history it has. If it is a recent listing, it has too little history for most lookback signals (52-week high needs 252 days; IVOL/MAX need about 1 month).

## Expected effect sizes for a 12-name universe (the power problem) and concrete test designs

### Takeaway
Published effect sizes come from decile spreads over 1,000+ stocks and do not transfer to 12 highly correlated names. Realistic within-universe signal ICs are probably 0.01-0.03. Detecting a few basis points per day of spread with t > 2 takes many years of daily data, so most tests here will be underpowered. Pre-register a short list of signals, use free data, and judge each signal against an equal-weight benchmark net of costs, with a fixed 2010-2020 / 2021-2026 split.

### Cited Findings
- Effect sizes in the source papers are for broad cross-sections. Berkman et al.: overnight +0.2-0.3% and intraday -0.2-0.4% in high-attention, low-institutional-ownership stocks. — [JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/paying-attention-overnight-returns-and-the-hidden-cost-of-buying-at-the-open/F9AAD159B512C651F09D5D52011D88E0)
- FIP: 5.94% vs -2.07% over 6 months, across all stocks. — [Frog.pdf](https://www3.nd.edu/%7Ezda/Frog.pdf)
- Residual reversal: more than 8% per year net, broad universe. — [Robeco](https://www.robeco.com/en-uk/insights/2011/11/short-term-residual-reversal)
- Decay haircuts to apply: about 58% post-publication on average, about 72% using post-2005 data. — [McLean-Pontiff](https://Www.Gwern.net/doc/economics/2016-mclean.pdf); [FEDS 2021-037](https://www.federalreserve.gov/econres/feds/files/2021-037pap.pdf)
- Free predictor data with monthly portfolio returns for hundreds of signals: Open Source Asset Pricing (Chen-Zimmermann), updated annually. — [Chen-Zimmermann](https://cfr.ivo-welch.info/published/papers/chen2021open.pdf)

### Inferences
**Power arithmetic (my calculation, not sourced).** Assume a daily top-half minus bottom-half spread among 12 correlated mega-caps has a daily standard deviation of about 1.0-1.5%. The t-stat is (mean / sd) x sqrt(N days).
- At a true mean of 5 bp/day (about 12%/yr) and sd 1.5%: t = 2 needs N = (2 x 1.5/0.05)^2 = 3,600 days, about 14 years.
- At 2 bp/day: about 22,500 days, about 90 years.

After the 50-70% decay haircut, a large-cap residual-reversal effect is plausibly in the 1-4 bp/day range. A 2010-2026 backtest (about 4,000 days) can therefore only confirm effects of roughly 5 bp/day or more. Anything smaller is indistinguishable from noise, so a positive backtest is weak evidence and a null result is uninformative.

**Breadth.** The fundamental law gives IR roughly equal to IC x sqrt(breadth). With 12 names, the 12 x 252 daily "bets" are heavily autocorrelated (lookbacks overlap) and correlated across names (one factor, tech beta, dominates). Effective breadth is far below 3,000 per year, perhaps a few hundred.

**Costs.** Mega-cap half-spreads are about 1 bp, but daily rebalancing of a reversal tilt can mean 20-50% turnover per day. At 2-5 bp round-trip all-in (spread plus slippage), that costs about 0.5-2.5 bp/day, which is the same order as the expected edge.

**Concrete test designs** (all from free data: yfinance or Stooq daily OHLCV including opens; Google Trends; Open Source Asset Pricing; FRED; Baker-Wurgler index from Wurgler's NYU page):
1. **Residual reversal (highest prior).** Signal = minus the cumulative 5-day (and 21-day) residual return from a rolling 60-day regression on SPY and SOXX. Long-only implementation: tilt weights around equal-weight, w_i proportional to 1/12 x (1 + k x z_i), clipped at 0, with k chosen ex ante. Test the IC (Spearman rank) of the signal against next-day and next-5-day returns. Report net of 3 bp/side, with turnover. Condition on VIX regime, since the effect is short-vol-like.
2. **Overnight/intraday decomposition.** Split returns into close-to-open (CO) and open-to-close (OC). Test (a) whether trailing 1-12-month CO-return momentum predicts next-month CO and OC returns per Lou-Polk-Skouras, and (b) the Berkman attention effect: after an abs(return) above 2 sd or a volume spike above 2x the 20-day average, does the next day's OC return reverse? Long-only use = timing: delay buys until after the open or lean against opening gaps. Note that rebalancing at the open versus the close changes the result.
3. **52-week-high / FIP as momentum filters.** Rank by price/52-week-high and by FIP-adjusted 12-1 momentum, monthly. Report rank IC versus next-month returns. Expect it to be underpowered, so treat it as a tiebreaker, not a driver.
4. **Earnings-day overreaction.** Event study over about 60 quarters x 12 names, about 700 events. Does the day-0/day-1 abnormal return reverse over days 2-10? Small N, so report a bootstrap CI.
5. **Negative screens (kill rules, not alpha).** MAX (top-5-day average daily return over the past month) and IVOL as underweight signals. Expect nulls in mega-caps. Run them only to confirm the null, and drop them if the CI includes 0.
6. **Multiple-testing hygiene.** Pre-register the signals and parameter grid. Require t > 3 (HXZ/Harvey standard) or deflate the Sharpe ratio for the number of variants tried. Hold out 2023-2026 untouched until the final run.

### Gaps
- No published study gives within-top-12 mega-cap ICs for any of these signals, so the 1-4 bp/day prior is my extrapolation, not a sourced number.
- Daily standard deviation of the 12-name spread and realistic turnover should be measured from the repo's own data rather than assumed.
