# Practitioner View: What Actually Lets Small Investors Beat a Rules-Based Long-Only Tech Portfolio

Format: simulated expert interview. Each thread is a Q, then a sourced answer, then a sharper follow-up. Tags: **[EVIDENCE]** = peer-reviewed or large-sample data; **[ANECDOTE]** = practitioner claim or self-reported record; **[SURVIVORSHIP]** = selection-bias warning. Research date 2026-11-20. 16 tool calls; several primary PDFs (SPIVA 2025, the AQR tail-risk paper, McConnell 2015 spinoffs) could not be fetched, so some figures come from secondary summaries and are flagged as such.

## Thread 1: What edges do small accounts have that funds don't?

### Takeaway
Practitioners agree that the main structural edge is **small size**. It lets you trade names and events that funds can't (micro-caps, spinoffs, index deletions, merger spreads) and frees you from benchmark-hugging. The documented premiums are real but have **shrunk since publication** (the index effect has nearly gone; spinoff returns depend on the holding period and on outliers), and some carry hidden crash risk (merger arb behaves like a short put). None of these edges is "tech beta", so they diversify a long-only tech book rather than improve it.

### Cited Findings
**Q1: Is the "small money" advantage real, or just a story?**
- **[ANECDOTE]** Buffett, BusinessWeek, June 25 1999: "It's a huge structural advantage not to have a lot of money. I think I could make you 50% a year on $1 million. No, I know I could. I guarantee that." At the 1999 Berkshire meeting he said he "may have been very slightly misquoted, but I certainly said something to that effect." The method was to "know everything about everything small" (deep-value micro-caps, Korean stocks, special situations) — [Yahoo/Benzinga summary](https://sg.news.yahoo.com/ideas-behind-buffett-1999-50-020022676.html); [GuruFocus](https://www.gurufocus.com/news/384700/the-oracle-shared-insights-on-making-50-a-year-managing-small-sums)
- **[ANECDOTE / SURVIVORSHIP]** His real small-capital record (the partnership years) was about 30% a year, not 50% — [Base Hit Investing](https://basehitinvesting.substack.com/p/how-buffett-made-50-per-year). One survivor of thousands of small-cap value investors. Not evidence that a typical small account can do this.

**Follow-up Q2: Which specific small-account niches have data behind them? Start with spinoffs.**
- **[EVIDENCE]** Cusatis, Miles & Woolridge (1993) studied spinoffs from 1965 to 1988 and found significantly positive abnormal returns for spinoffs, parents and the combined pairs over up to 36 months — [McConnell et al., J. Business 2001](https://business.purdue.edu/faculty/mcconnell/publications/spinoffs-ex-ante-2001-vol74.pdf); [IDEAS](https://ideas.repec.org/a/ucp/jnlbus/v74y2001i2p245-80.html)
- **[ANECDOTE]** Greenblatt's *You Can Be a Stock Market Genius* (1997) popularised the result and cites roughly 10% a year of outperformance for spinoffs and 6% for parents — [GuruFocus](https://www.gurufocus.com/news/262404/nasd)
- **[EVIDENCE: replication weakens it]** McConnell, Ozbilgin & Wahal (2001) tested whether an investor could earn the excess returns *after* publication. The results "depended heavily on the holding period". A later Purdue study (146 spinoffs, 2001–2012, 36-month window) and a 2004 update reported >20% three-year outperformance versus industry, but **one large outlier drove much of the average** — [Purdue JPM 2015](https://business.purdue.edu/faculty/mcconnell/publications/The%20Stock%20Price...2013%20jpm.2015.42.1.143.pdf) (PDF not parsed; figures from search summary, so verify)

**Follow-up Q3: Index deletions, a forced-selling niche funds can't exploit?**
- **[EVIDENCE: edge decayed]** Greenwood & Sammon, "The Disappearing Index Effect" (J. Finance 2025): the S&P 500 inclusion/deletion abnormal returns that were large in the 1990s averaged only about 0.1% in 2010–2020 — [NBER w30748](https://www.nber.org/system/files/working_papers/w30748/w30748.pdf); [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/jofi.13410)
- **[EVIDENCE, practitioner-produced]** Research Affiliates ("Nixed: The Upside of Getting Dumped"): deleted stocks outperformed by >5% a year over the next five years, but the deletion strategy *lagged* the S&P 500 and Russell 1000 as of year-end 2023 — [Research Affiliates](https://www.researchaffiliates.com/publications/press-exclusive/1043-nixed-the-upside-of-getting-dumped); see also [Arnott & Wu, CFA brief](https://rpc.cfainstitute.org/sites/default/files/docs/research-reports/rf_arnott-wu_active-indexing_online.pdf). The announcement-window effect has gone; a slow multi-year rebound in deletions may survive, but it is a value tilt with long dry spells.

**Follow-up Q4: Merger arbitrage, which needs no prediction skill?**
- **[EVIDENCE]** Mitchell & Pulvino (J. Finance 2001), 4,750 mergers 1963–1998: returns are uncorrelated with the market in flat or rising markets but **positively correlated in severe declines**, so the payoff resembles **selling index puts** — [Mitchell & Pulvino](https://tevgeniou.github.io/EquityRiskFactors/bibliography/RiskArbitrage.pdf); crash/speed-of-capital dynamics in [Mitchell-Pulvino NBER 2010](https://conference.nber.org/confer/2010/Risks10/Mitchell_Pulvino.pdf)
- Implication: merger arb doesn't hedge a tech portfolio's bear market; it fails at the same time.

**Follow-up Q5: Closed-end fund discounts?**
- I found no return study of a retail CEF-discount strategy in this pass. Mitchell/Pulvino/Pedersen discuss CEF arbitrage and chart median equity-CEF discounts for 2002–2010 but report no strategy returns — [HBS "Limited Arbitrage"](https://www.hbs.edu/ris/Publication%20Files/Limited%20Arbitrage%20in%20Equity%20Markets_b0527518-7bfb-435b-a926-7a6d235693db.pdf)

### Inferences
- The small-account edges with the most evidence (spinoffs, deletions, merger arb, micro-caps) are **event- or illiquidity-driven, not tech-specific**. They would sit beside the tech portfolio, not improve it.
- Every published niche shows **post-publication decay** (index effect about 0; spinoffs sensitive to holding period and outliers). Haircut any backtest by 50% or more.
- Merger arb's short-put profile is the opposite of what a long-tech book needs in a crash.
- The two cheapest edges, **no benchmark** (you can hold cash or trend-exit) and **patience** (long holding periods), need no special data. They come up again in Threads 2 and 3.

### Gaps
- No primary figures for spinoff returns after 2012, and the 2015 Purdue PDF could not be parsed.
- No CEF discount strategy return study was found.
- Tax-lot harvesting value (practitioner claims of about 1%+ a year of tax alpha) was not researched in this pass. Needs Parametric/AQR direct-indexing studies.
- No net-of-cost micro-cap capacity study was found that quantifies the size at which the edge disappears.

## Thread 2: How do pros manage drawdowns and position sizing in bear markets?

### Takeaway
Top macro practitioners (Tudor Jones, Druckenmiller) combine **trend-based exits** with **asymmetric sizing** (big when right, fast cuts when wrong). The best-documented, cheapest version for a small investor is a **moving-average trend filter**. It cuts drawdowns sharply at a cost of whipsaw and some lagging in bull markets. Tail hedging with puts (Spitznagel/Universa) works brilliantly in crashes, but AQR finds a robustly **negative long-run return** for long puts, and CalPERS dropped its program over cost.

### Cited Findings
**Q1: What do the legends actually do in bear markets?**
- **[ANECDOTE]** Paul Tudor Jones, interviewed by Tony Robbins (*Money: Master the Game*): "My metric for everything I look at is the 200-day moving average of closing prices… if you use the 200-day moving average rule, then you get out." He says he was flat at the top of the 1987 crash because price had gone under the 200-day. "The most important rule is to play great defense, not great offense." — [Meb Faber blog](https://mebfaber.com/2014/11/06/paul-tudor-jones-on-the-200-day-moving-average/)
- **[ANECDOTE]** Druckenmiller, in Schwager's *The New Market Wizards*, on what Soros taught him: "it's not whether you're right or wrong that's important, but how much money you make when you're right and how much you lose when you're wrong." In the 1992 sterling trade Soros pushed a planned $1.5B position to about $10B because the downside was bounded — [Acquirer's Multiple](https://acquirersmultiple.com/2017/11/stanley-druckenmiller-the-greatest-lesson-i-ever-learned-from-george-soros/); [MoneyWeek](https://moneyweek.com/investments/investment-strategy/605020/stan-druckenmiller-position-size-really-matters)
- **[SURVIVORSHIP]** The "30 years, no down year" claims about Druckenmiller appear only in secondary blogs (e.g. [GHG Substack](https://ghginvest.substack.com/p/7-timeless-investing-lessons-of-stanley)). I could not verify them against primary audited data. Tudor's "19.5% a year, 25 years, no losing year" is likewise a blog claim. These are survivors drawn from a large population of macro traders who blew up.

**Follow-up Q2: Is the 200-day rule supported beyond Tudor's anecdote?**
- **[EVIDENCE, in-sample caveat]** Faber, "A Quantitative Approach to Tactical Asset Allocation" (2007; JPM update 2018): sell to cash when monthly price is below its 10-month SMA. The five-asset portfolio over 1973–2011 had a max drawdown of −9.56% vs −46.0% for buy-and-hold, with volatility of 7.0% vs 10.1% (secondary table). Faber admits the 10-month window was chosen with knowledge of Siegel's prior results, so it is **in-sample**. Out-of-sample checks were done on other markets — [SSRN 962461 via Scribd](https://www.scribd.com/doc/116881446/SSRN-id962461); [Juniata write-up](https://admissions.juniata.edu/offices/juniata-voices/media/andrew-and-castro.pdf)
- **[EVIDENCE]** The rule whipsaws often. ±5% bands cut whipsaw and turnover — [Systematic Investor](https://systematicinvestor.github.io/Moving-Average); robustness of simple systems in [Alpha Architect](https://alphaarchitect.com/are-uber-simple-asset-allocation-systems-robust/)

**Follow-up Q3: Trend filter vs Spitznagel-style puts. Which hedge is cheaper?**
- **[EVIDENCE]** AQR, "Tail Risk Hedging: Contrasting Put and Trend Strategies" (2020): negative long-run returns to long-put strategies are "likely a robust" result, and AQR **prefers trend over puts** after practical considerations — [AQR](https://www.aqr.com/insights/research/white-papers/tail-risk-hedging-contrasting-put-and-trend-strategies); [AQR JSI PDF](https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/Journal-of-Systematic-Investing-Vol-1-Issue-1--Tail-Risk-Hedging-AQR.pdf)
- **[ANECDOTE, self-reported]** Universa reported a 3,612% return in Q1 2020. It measures itself by the effect on the *total portfolio's* CAGR, not by standalone return. Aaron Brown (Bloomberg) called the numbers "legit but with an asterisk", and rivals dispute the method. I found no independent audit of Universa's long-run returns — [Advisor Perspectives](https://www.advisorperspectives.com/articles/2020/05/06/an-aqr-warning-and-a-3-612-return-fire-up-the-black-swan-debate); [Bloomberg/Brown](https://www.bloomberg.com/opinion/articles/2023-04-06/universa-s-3-126-black-swan-return-is-legit-but-with-an-asterisk)
- **[EVIDENCE: institutional outcome]** CalPERS ended its tail-hedge program, citing high cost, lack of scalability and better alternatives. (It then missed the March 2020 payoff.) — [Institutional Investor](https://www.institutionalinvestor.com/article/2bswz8monky7s5k5w79j4/portfolio/if-you-used-this-hedging-strategy-youd-be-sleeping-at-night-right-now)

### Inferences
- For a long-only tech book, a **200-day/10-month trend exit plus volatility targeting** is the practitioner-endorsed and evidence-backed default. It is cheap, simple and scalable. Puts need precise sizing and the discipline to keep paying for them; most institutions don't have it.
- Trend filters protect best against **slow** bears (2000–02, 2008, 2022). They help little against **fast** crashes (Oct 1987 is a lucky exception; March 2020 gaps hit before the signal). Puts cover the gap risk that trend misses, so a small put sleeve plus trend is the theoretical "barbell".
- Druckenmiller's lesson for sizing is asymmetry: the losing side needs pre-defined cuts, and the winning side can be pressed. Vol targeting is the mechanical version of this.

### Gaps
- Dalio (risk parity / All Weather) and the Taleb barbell (90% safe / 10% convex) were **not researched in this pass**. No sourced figures.
- No quantified annual bleed for Universa-style hedging (practitioners often cite low single-digit % a year for a 3% put sleeve). The AQR PDF was not fetched for exact numbers.
- No S&P-500-only or Nasdaq-100-only 200-day results were sourced. Tech-specific trend-filter evidence is still needed.
- No primary audited Druckenmiller or Tudor Jones annual return series.

## Thread 3: What do real individual-investor track records show about who outperforms and why?

### Takeaway
The evidence is lopsided. Most active funds and most individuals lose to the index, mainly through **trading costs and bad timing, not stock selection**. A small, identifiable top cohort does persist: the top decile at roughly +6% a year risk-adjusted (Coval et al.), and fewer than 1% of Taiwanese day traders. The investors who win in aggregate are the ones who **trade least**.

### Cited Findings
**Q1: Baseline. How do professionals do against the index?**
- **[EVIDENCE]** SPIVA US Year-End 2025: 79% of active large-cap funds underperformed the S&P 500 in 2025 (65% in 2024). Over 15 years, **no category** had a majority of active managers beat its benchmark. Secondary coverage cites about 90% of large-cap funds lagging over 15 years (not confirmed in the primary document, which returned 403) — [SPIVA](https://www.spglobal.com/spdji/en/spiva/article/spiva-us-year-end-2025/); [InvestmentNews](https://investmentnews.com/equities/active-managers-stumble-again-in-2025-as-large-caps-dominate/265541)
- **[EVIDENCE, counterpoint]** An IAA Active Managers Council-backed study argues SPIVA overstates underperformance by counting funds rather than assets: 55% of active US equity funds underperformed passive vehicles over 20 years by its method, vs 92% under SPIVA — [Yahoo Finance](https://finance.yahoo.com/markets/stocks/articles/investment-scorecard-systematically-understates-active-194406600.html). Note that the sponsor has a conflict of interest.

**Follow-up Q2: Individuals then. Where exactly do they lose?**
- **[EVIDENCE]** Barber & Odean, "Trading Is Hazardous to Your Wealth" (J. Finance 2000), 66,465 discount-broker households, 1991–1996: the most active traders earned **11.4%** a year vs **17.9%** for the market. Infrequent traders earned 18.5%. Average household gross return was 17.7% but net was 15.3% (an abstract version says 16.4%). The cause is **trading costs and frequency, not stock picking** — [Barber & Odean PDF](https://faculty.haas.berkeley.edu/odean/Papers%20current%20versions/Individual_Investor_Performance_Final.pdf); [EconPapers](https://econpapers.repec.org/RePEc:bla:jfinan:v:55:y:2000:i:2:p:773-806)
- **[EVIDENCE, critique]** Bonaparte & Cooper (NBER w16022) attribute part of the gap to household selection: "while trading is costly, how hazardous it actually is remains an open issue" — [NBER](https://www.nber.org/papers/w16022.pdf)
- **[EVIDENCE]** Morningstar *Mind the Gap 2026* (10 years to Dec 31 2025): the average dollar in US funds and ETFs earned **8.7%** a year vs **9.9%** fund total return, a 1.2-point **timing gap** (about 12% of return). The gap was −0.4% for the least-volatile funds and −2.1% for the most volatile, and wider for ETFs than for mutual funds — [Morningstar](https://www.morningstar.com/business/insights/research/mind-the-gap-2025); [Advisor Perspectives](https://www.advisorperspectives.com/commentaries/2026/08/21/what-advisors-can-learn-from-the-investor-return-gap?firm=vettafi)

**Follow-up Q3: Is there a cohort that persistently wins? Can it be identified ex ante?**
- **[EVIDENCE]** Coval, Hirshleifer & Shumway, "Can Individual Investors Beat the Market?" (RAPS 2021): investors in the top decile in the first half of the sample beat the bottom decile by about 8% a year in the second half. The published version puts the top decile at about **6% a year risk-adjusted**. Top-decile trades earned 15 bp a day in the following week, fading after a month. The cross-period performance correlation is only about **10%**. Most other investors did not beat the market after costs — [CHS PDF](https://sites.uci.edu/dhirshle/files/2019/06/Can-individual-investor-beat-the-market_0718_CHS.pdf); [OSU release](https://news.osu.edu/some-investors-really-can-beat-the-market-study-suggests/). (The press-release "38% above market" figure is not in the paper; ignore it.)
- **[EVIDENCE]** Barber, Lee, Liu & Odean, Taiwan day traders 1992–2006 (J. Fin. Markets 2014): only the prior year's top **4,000 traders (<1% of day traders)** went on to earn reliably positive abnormal returns net of costs. The likely mechanism is liquidity provision in a pure limit-order market. Aggregate day-trader performance net of fees was **negative in all 15 years**, and losers kept trading at nearly the same rate as winners — [Day Trading Skill PDF](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf); [IDEAS](https://ideas.repec.org/a/eee/finmar/v18y2014icp1-24.html)

**Follow-up Q4: So what separates winners from losers?**
- Across these studies the consistent separators are: **low turnover** (Barber-Odean infrequent traders beat the market), **avoiding timing mistakes in volatile products** (Morningstar gap −2.1% in volatile funds), and for the rare skilled cohort, **short-horizon information or liquidity provision** that decays within weeks (CHS; BLLO). Sources as above.

### Inferences
- **[SURVIVORSHIP]** Famous individual winners (Buffett's partnership, Market Wizards) are drawn from the right tail of a population where more than 90% lose to the index. Schwager interviewed survivors, so his books document what winners say, not what makes winners.
- The base rates are about 1–10% persistent winners, a 10% persistence correlation and short-lived edges. Discretionary overrides of a rules-based portfolio should be expected to **subtract** value unless they are themselves systematic and pre-registered.
- The most robust "outperformance" lever for a small investor is not alpha. It is **avoiding the behaviour gap** (about 1.2–2.1 points a year), which a frozen, rules-based model already captures. The next levers are a cheap trend/vol-target overlay for drawdowns (Thread 2) and uncorrelated event-driven niches (Thread 1), with heavy post-publication haircuts.

### Gaps
- No IRS or tax-return study of individual investor returns was found in this pass.
- No 2020s retail-cohort study (Robinhood era, e.g. Welch 2022 or Barber et al. 2022 on Robinhood herding) was researched. Worth a follow-up.
- No primary SPIVA 2025 15-year category percentages (PDF blocked). Survivorship rates for funds are also unconfirmed.
- Whether Coval et al.'s top-decile edge survives modern zero-commission or PFOF execution is unknown.
