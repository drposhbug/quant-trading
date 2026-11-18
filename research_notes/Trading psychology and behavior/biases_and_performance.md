# Behavioral-Finance Biases and Individual Traders' Results (behavioral-economist view)

Scope note: research done 2026-11-18 using about 18 tool calls. Most numbers come from abstracts, author pages, or reputable summaries (NBER, RePEc, SSRN, MIT Sloan, Bloomberg). I could not machine-read the full PDFs (no PDF text tools in this environment), so table-level figures are marked where they rest on secondary summaries. Items I know from background reading but could NOT verify this session are in **Gaps**, not in Cited Findings.

## 1. What do the canonical studies (Barber-Odean, Odean, Kahneman-Tversky, Shefrin-Statman, later work) find, with numbers?

### Takeaway
The core retail biases are well documented with large samples: overconfidence leads to excess trading (net returns fall from about 15% to 10% a year for the most active quintile), the disposition effect makes investors about 1.5x more likely to realize gains than losses, attention drives retail buying into stocks that then underperform, and lottery preference costs 2-3 pp a year. Loss aversion holds up in meta-analysis (lambda about 1.96, slightly below K-T's 2.25), but the *explanation* for the disposition effect (prospect theory versus beliefs) is contested.

### Cited Findings
**Overconfidence / excess trading**
- Barber & Odean (2000, JF), "Trading Is Hazardous to Your Wealth": 60,000+ households at a large US discount broker, Feb 1991 to Dec 1996. The average household earned 17.7% gross and 15.3% net annualized (geometric), against 17.1% for the value-weighted market, and turned over about 80% of its portfolio a year. The most active 20% (at least 9.6% monthly turnover) earned **10.0% net**, roughly 7 pp a year below the market. — [Odean, Berkeley page](https://faculty.haas.berkeley.edu/odean/papers/returns/Returns.html)
- Barber & Odean (2001, QJE), "Boys Will Be Boys": the authors tie excess trading to overconfidence. Men trade more than women and lose **0.94 pp more per year** to trading. Popular summaries give the gap as about 1 pp for men and about 1.4 pp for single men. — [BoysWillBeBoys.pdf](https://faculty.haas.berkeley.edu/odean/papers/gender/BoysWillBeBoys.pdf); [Turtletrader summary of Barber-Odean article](https://www.turtletrader.com/overconfident/)
- Counterpoint: Bonaparte & Cooper (NBER w16022) argue that rational agents facing adjustment costs can reproduce the trading-returns pattern, and say how "hazardous" trading is "remains an open issue". — [NBER w16022](https://www.nber.org/system/files/working_papers/w16022/revisions/w16022.rev0.pdf)

**Disposition effect**
- Odean (1998, JF): 10,000 accounts at a discount broker, 1987-1993. The proportion of gains realized (PGR) was **0.148** and the proportion of losses realized (PLR) was **0.098**, a ratio of about 1.5. — [NUS RMI WP 2019-12 citing Odean Table I](https://rmi.nus.edu.sg/wp-content/uploads/2021/04/RMI-WPS-2019-12.pdf)
- Ben-David & Hirshleifer (2012, RFS): the probability of selling has a **V-shape** in gains and losses, steeper on the gain side. The disposition effect "is not driven by a simple direct preference for selling a stock by virtue of having a gain versus a loss", which points to belief-based or speculative motives rather than pure realization utility. — [IDEAS RFS 25(8)](https://ideas.repec.org/a/oup/rfinst/v25y2012i8p2485-2532.html); [Ben-David & Hirshleifer WP](https://en-coller.tau.ac.il/sites/nihul_en.tau.ac.il/files/media_server/Recanati/management/seminars/account/Ben-David_Hirshleifer_2011_12_13_v1.pdf)

**Loss aversion / prospect theory**
- Brown, Imai, Vieider & Camerer (2024, JEL 62(2):485-516) meta-analysed 607 estimates from 150 articles (1992-2017). The mean loss-aversion coefficient is **1.955** (95% interval 1.820-2.102), somewhat below Tversky-Kahneman's (1992) **2.25**. Few study characteristics moderate it. — [AEA JEL](https://www.aeaweb.org/doi/10.1257/jel.20221698); [RePEc](https://econpapers.repec.org/RePEc:aea:jeclit:v:62:y:2024:i:2:p:485-516); [Healthcare Economist summary](https://healthcare-economist.com/2024/06/26/empirical-estimates-of-loss-aversion)

**Limited attention**
- Barber & Odean (2008, RFS), "All That Glitters": individuals are net buyers of attention-grabbing stocks (news, abnormal volume, extreme one-day returns). The reason is a search-cost asymmetry: buyers choose from thousands of stocks, sellers only from what they own. Stocks individuals buy on high-attention days later underperform the stocks they sell. Institutions, and professionals' buying in particular, are the least affected. — [RFS 2008 PDF](https://www.smallake.kr/wp-content/uploads/2020/12/allthatglitters_rfs_2008.pdf); [RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:21:y:2008:i:2:p:785-818)

**Lottery preference**
- Kumar (2009, JF 64(4)), "Who Gambles in the Stock Market?": about 70,000 investors. Lottery-type stocks are defined as priced under $5 with high volatility and extreme positive returns (high idiosyncratic skewness). Investors who hold them underperform by about **2-3 pp a year**, and the underperformance is larger for low-income investors who overweight them. Demand rises in downturns, and the clientele resembles state-lottery players. — [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:64:y:2009:i:4:p:1889-1933); [UT Austin news](https://news.utexas.edu/2009/02/26/investors-who-gamble-in-the-stock-market-have-same-characteristics-as-lottery-players-study-shows)

### Inferences
- Ranked by measured annual cost to the typical retail investor: excess trading/overconfidence (up to about 7 pp for heavy traders) > lottery preference (2-3 pp) > gender-linked overconfidence (about 1 pp). The disposition effect's cost is usually expressed as tax drag and momentum forgone, and I did not verify a clean annual number for it (see Gaps).
- The attention asymmetry (it hits buying, not selling) shows up again in the Robinhood evidence and, in mirror image, among professionals (Section 3).

### Gaps
- Shefrin & Statman (1985, JF) named the "disposition effect". I did not retrieve its text, and it is mainly conceptual and tax-based rather than an effect-size paper.
- Odean's (1998) estimate of the cost of the disposition effect: from memory, winners sold outperform losers held by about 3.4 pp over the next year. **Not verified this session.**
- Barber-Odean (2000) gross returns for the top quintile and the exact market-adjusted gap, plus the "men trade 45% more" figure: **not verified** (search did not surface them).
- Herding, FOMO, anchoring (e.g. 52-week-high anchoring, George & Hwang 2004) and recency/extrapolation (e.g. Greenwood & Shleifer 2014 survey expectations): no searches run within budget, so no sourced numbers. FOMO has no clean academic effect-size literature that I know of. It is usually proxied by attention/herding (see Robinhood below).
- Replication of prospect theory: Ruggeri et al. (2020, Nature Human Behaviour; 19 countries) is believed to largely replicate K-T's 1979 items. **Not verified this session.** Critiques of loss aversion's generality (Gal & Rucker 2018) are also not verified.

## 2. Day-trader and modern retail outcomes: Taiwan, Brazil, Robinhood, 0DTE and retail options

### Takeaway
Across countries and decades, persistent day traders almost all lose money: about 97% lose in both Taiwan and Brazil, and fewer than 1% are reliably profitable. Robinhood-era herding predicts negative short-run returns (-3% to -6% over 5 days for the most-bought stocks), though the aggregate Robinhood portfolio was *not* a disaster (Welch). Retail options trading is the clearest 2020s case of bias-driven losses: about $358k a day in 0DTE SPX options after May 2022, and 5-14% losses on pre-earnings option buys.

### Cited Findings
**Taiwan (full market, 1992-2006)**
- Barber, Lee, Liu & Odean (2014, J. Financial Markets), "The Cross-Section of Speculator Skill": **less than 1%** of day traders predictably and reliably earn positive abnormal returns net of fees. The top 500 ranked traders keep earning positive net returns the following year, while bottom-ranked traders lose. — [RePEc finmar v18](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)
- Barber, Lee, Liu, Odean & Zhang (2020, RAPS), "Learning, Fast or Slow": **97%** of day traders are likely to lose money in future day trading, and **74%** of day-trading volume comes from traders with a history of losses. Unprofitable traders are more likely to quit, but too slowly. The results fit overconfidence and biased learning better than rational learning. — [RePEc RAPS 10(1):61-93](https://econpapers.repec.org/RePEc:oup:rasset:v:10:y:2020:i:1:p:61-93.); [WP PDF](https://www.econ.puc-rio.br/uploads/adm/seminarios/Learning_fast_or_slow_180606.pdf)

**Brazil (equity mini-index futures, entrants 2013-2015)**
- Chague, De-Losso & Giovannetti, "Day Trading for a Living?" (SSRN 3423101, 2019-2020): among individuals who day-traded for **more than 300 days**, **about 97% lost money**. Only **1.1%** earned more than the Brazilian minimum wage, and only 0.5% (0.4% in a later version) earned more than a bank teller's starting salary. There was no evidence of learning. Caveat: the 97% applies to persistent traders, not everyone who tried. Blog figures of "94% / 19,646 traders" conflict with the paper and should not be used. — [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); [IDEAS](https://ideas.repec.org/p/spa/wpaper/2019wpecon47.html); [Quantpedia summary](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/)

**US Robinhood era**
- Barber, Huang, Odean & Schwarz (2022, JF), "Attention-Induced Trading and Returns: Evidence from Robinhood Users": intense Robinhood buying predicts negative returns. The top stocks bought each day show average **5-day abnormal returns of -3%**, and **-6%** for the most extreme herding events. Herding is tied to the app's simplified display (e.g. "Top Movers"). During Robinhood outages, retail trading in high-attention stocks falls more. Caveats from summaries: returns are gross, and the negative returns are concentrated in stocks under $1B market cap. — [SSRN 3715077 PDF](https://www.smallake.kr/wp-content/uploads/2020/12/SSRN-id3715077.pdf); [UC Davis](https://gsm.ucdavis.edu/news/what-effect-brokerage-robinhood-having-stock-market); [Evidence Investor / Swedroe](https://www.evidenceinvestor.com/post/why-most-robinhood-traders-earn-lousy-returns)
- Counter-evidence, Welch (2022, JF 77(3):1489-1527), "The Wisdom of the Robinhood Crowd": using Robintrack data from mid-2018 to mid-2020, the aggregate crowd portfolio showed good market timing and positive alpha. Robinhood users *bought* during the March 2020 crash (no panic selling), and holdings tilted toward large, high-volume stocks. Caveat: few individual users actually hold this aggregate portfolio. — [NBER w27866](https://www.nber.org/papers/w27866); [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:77:y:2022:i:3:p:1489-1527)

**0DTE and retail options (2021-2025)**
- Beckmeyer, Branger & Gayda, "Retail Traders Love 0DTE Options... But Should They?" (working paper, 2023; CBOE data from about Jan 2021 to Feb 2023): about 75% of retail S&P 500 option trades are 0DTE. Average retail losses were **$184k a day** over the full sample and **$358k a day** after daily expirations began (16 May 2022). About **60%** of losses come from transaction costs and spreads. The authors read the motive as gambling and entertainment. — [Bloomberg](https://www.bloomberg.com/news/articles/2023-04-21/day-traders-lose-358-000-per-day-gambling-on-zero-day-options); [WealthManagement](https://www.wealthmanagement.com/equities/retail-investors-are-in-love-with-same-day-options); [CXO summary](https://www.cxoadvisory.com/individual-investing/retail-0dte-option-trader-performance)
- Later versions: a CFR Cologne working paper (cfr-25-09, 2025) and a 2026 AEA session paper appear to extend the analysis and report similar retail losses. **I could not read the PDF text, so I can't confirm the updated numbers.** — [CFR WP 25-09](https://www.cfr-cologne.de/download/workingpaper/cfr-25-09.pdf); [AEA 2026](https://www.aeaweb.org/conference/2026/program/paper/StD8aadb)
- Dim, Eraker & Vilkov (2024), "0DTEs: Trading, Gamma Risk and Volatility Propagation" (SSRN 4692190): this is about market impact, not retail P&L. Aggregate 0DTE gamma is *inversely* related to intraday volatility, so it stabilizes rather than destabilizes. Retail-profit claims attributed to this line of work could not be verified. — [Harbourfront summary](https://harbourfrontquant.substack.com/p/the-rise-of-0dte-options-cause-for-concern-or-business-as-usual)
- de Silva, Smith & So, "Losing is Optional: Retail Option Trading and Earnings Announcement Volatility" (Review of Finance, 2025): retail investors concentrate option *purchases* before earnings, especially high expected-volatility announcements. They lose **5-9% on average** and **10-14%** on high expected-volatility events, roughly **$3B over 10 years**. The main channels are overpaying (wide spreads, inflated IV) and failing to close positions after the announcement, which looks like a disposition effect in options. — [MIT Sloan](https://mitsloan.mit.edu/ideas-made-to-matter/retail-investors-lose-big-options-markets-research-shows); [Quantpedia](https://quantpedia.com/how-retail-losses-money-in-option-trading/); [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/working-papers/losing-optional-retail-option-trading-expected-announcement)

### Inferences
- The two independent "97%" figures (Taiwan, Brazil) come from different markets, instruments (stocks versus futures), and eras, which makes the result robust. Persistence despite losses is the behavioral signature: overconfidence plus biased self-attribution, or gambling utility.
- In 2020s options, most of the measured loss is *frictions paid to market makers* (about 60% for 0DTE; spreads for earnings options). That is consistent with lottery preference (paying for skewness) combined with attention-driven timing.
- The Welch versus Barber et al. conflict is mostly about the unit of analysis. The aggregate, buy-and-hold-weighted crowd did fine in a strong bull market, while attention-driven *marginal trades* in small caps lost money.

### Gaps
- SEC/FINRA investor studies (e.g. the SEC DERA paper on retail "hope" trading, sec.gov dera-hope-reasonable-prc-2503) appeared in search results but were not read.
- Exact sample size (number of traders) for Chague et al. is not confirmed (about 19,646 is a blog figure, unverified). Barber et al. Taiwan sample counts were not retrieved.
- No verified 2024-2026 retail *equity* day-trading outcome study for the US was found within budget.

## 3. Do professionals show the same biases?

### Takeaway
Yes, but selectively. Institutional managers show real skill in *buying* and poor, heuristic-driven *selling*: their sells underperform random selling. That matches the retail attention asymmetry in reverse. Professionals are less susceptible to attention-driven buying (Barber-Odean 2008).

### Cited Findings
- Akepanidtaworn, Di Mascio, Imas & Schmidt (2023, JF 78(6):3055-3098), "Selling Fast and Buying Slow: Heuristics and Trading Performance of Institutional Investors" (NBER w29076, 2021): the average portfolio is about $573M. Buys show skill, while sells underperform **even random-selling strategies**. The authors attribute this to uneven attention, with a systematic, costly heuristic used in selling but not in buying. Selling performance improves on earnings-announcement days, when information is salient, which shows the skill exists but is deployed selectively. — [NBER w29076](https://nber.org/papers/w29076); [Institutional Investor](https://www.institutionalinvestor.com/article/2bswcawc1qi0khnmhq0w0/portfolio/portfolio-managers-are-good-at-buying-but-stink-at-selling)
- In Barber-Odean (2008), professional (institutional) buying is the least influenced by attention-grabbing events. — [RFS 2008 PDF](https://www.smallake.kr/wp-content/uploads/2020/12/allthatglitters_rfs_2008.pdf)

### Inferences
- The professional bias looks like **limited attention plus a "sell extreme past returners" heuristic** rather than overconfidence-driven turnover. Debiasing implication: apply the same research discipline to exits as to entries, for example a systematic sell rule.

### Gaps
- Exact basis-point figures (buy alpha, cost of sells versus random, sample period, number of managers) could not be extracted because the PDF was not machine-readable here. From memory, the sample is 783 portfolios, about $1T, 2000-2016, with sells costing about 70-80 bp a year versus random. **Unverified; check the paper.**
- Disposition effect in mutual funds (e.g. Frazzini 2006) and hedge funds: not searched.

## 4. Measured cost of biases and persistence in 2020-2026 data

### Takeaway
The biases look structurally persistent. The same patterns found in 1987-2006 data (excess trading, attention herding, lottery demand, failure to learn) recur in Robinhood (2018-2021), 0DTE (2021-2023+) and earnings-option (2010s-2020s) data. The main 2020s change is that losses have migrated to options, where spreads and lottery-like payoffs magnify them.

### Cited Findings
- Robinhood herding (2018-2020): -3% to -6% 5-day abnormal returns after herding events. — [SSRN 3715077](https://www.smallake.kr/wp-content/uploads/2020/12/SSRN-id3715077.pdf)
- 0DTE retail (2021-2023): about $358k a day in losses after May 2022, about 60% of it frictions. — [Bloomberg](https://www.bloomberg.com/news/articles/2023-04-21/day-traders-lose-358-000-per-day-gambling-on-zero-day-options)
- Retail earnings options: 5-14% losses, about $3B over 10 years (published 2025). — [MIT Sloan](https://mitsloan.mit.edu/ideas-made-to-matter/retail-investors-lose-big-options-markets-research-shows)
- Loss aversion remains stable at about 2 across 25 years of studies, with few moderators. — [AEA JEL 2024](https://www.aeaweb.org/doi/10.1257/jel.20221698)
- Mitigating evidence: Robinhood users did not panic-sell in March 2020, and the aggregate portfolio had positive alpha in 2018-2020. — [NBER w27866](https://www.nber.org/papers/w27866)

### Inferences
- For a systematic/quant trader, the practical lessons are: (1) turnover and spreads are the dominant measurable cost of overconfidence; (2) exits deserve rules as rigorous as entries (Akepanidtaworn et al.); (3) avoid paying for skewness (lottery stocks, short-dated options) unless there is a quantified edge; (4) retail attention spikes are, if anything, a weak contrarian signal in small caps, but only *gross* of costs.
- Replication status in brief: the disposition effect *pattern* replicates widely, but its prospect-theory *explanation* is contested (Ben-David & Hirshleifer). The "trading is hazardous" interpretation is challenged by rational adjustment-cost models (Bonaparte & Cooper). Loss aversion's magnitude is somewhat smaller than K-T's 2.25 (about 1.96). Robinhood "dumb money" is nuanced by Welch. I found no outright failed replications of the Taiwan or Brazil day-trading loss results.

### Gaps
- No verified post-2023 (2024-2026) peer-reviewed estimate of total US retail trading losses was found. Bias-specific cost estimates on 2024-2026 data (e.g. meme-stock or crypto-adjacent equities, prediction markets) were not located within budget.
- Anchoring and recency/extrapolation costs in recent data: not searched.
