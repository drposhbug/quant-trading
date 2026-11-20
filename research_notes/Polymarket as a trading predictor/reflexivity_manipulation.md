# Prediction Markets: Reflexivity, Manipulation, Insider Trading and Reliability (skeptic/regulator view, as of 2026-11-19)

Status labels used below: **PROVEN** = conviction, settlement or regulator finding; **CHARGED** = indictment/complaint, allegations only; **ALLEGED** = media/academic flags, no legal finding; **STUDY** = academic estimate.

## Q1. Is there academic evidence that prediction-market prices are hard to manipulate for long, vs recent evidence of successful manipulation in thin markets?

### Takeaway
The classic literature (Rhode-Strumpf field study, Hanson-Oprea-Porter lab, Hanson-Oprea theory) says manipulation attempts produce measurable but short-lived price moves that get arbitraged away, and can even improve accuracy by adding liquidity. That result assumes deep, arbitraged markets with outcomes the manipulator cannot affect. The 2024-2026 record shows the main failure modes are elsewhere: wash trading inflating volume, insiders trading on outcomes they know in advance, people trading on outcomes they control (Santos), and manipulation of the resolution step (UMA votes). None of these is the "push the price and hope" attack the classic papers test.

### Cited Findings
- Rhode and Strumpf (NBER, 2006) study historical and modern speculative attacks on political stock markets, including one on the Iowa Electronic Market in 2000. Every attack produced measurable initial price changes, and prices in almost every case moved back, so attacks generally failed — [NBER PDF](https://conference.nber.org/confer/2006/daes06/rhode.pdf)
- Hanson, Oprea and Porter ran the first lab study of price manipulation in asset markets. The literature treats it, with Rhode-Strumpf and Camerer's experiments, as evidence that manipulation attempts tend to fail. They note that identifying manipulation in the field is "difficult" and that field evidence is "scarce and tenuous" — [CERGE-EI PDF](https://www.cerge-ei.cz/pdf/events/papers/120206_t.pdf)
- Hanson and Oprea (2009, *Economica*) add a manipulator with a price target to a Kyle model. Manipulators add liquidity that informed traders exploit, so average accuracy can *rise* — [summary](https://stafforini.com/works/hanson-2009-manipulator-can-aid/) (I read a secondary summary, not the full text)
- Choo, Kaplan and Zultan (2021 experiment): *suspecting* manipulation lowers trust in a market even when no manipulation happens. This is cited in the later manipulation literature — [arXiv 2503.03312](https://arxiv.org/html/2503.03312v1) (secondary citation)
- A 2026 arXiv agent-based model of prediction-market manipulation warns that the media and the public often read prices as a binary "who is the likely winner" call. A manipulator then needs to move the headline, not hold the price, which makes short-lived distortions consequential — [arXiv 2601.20452](https://arxiv.org/html/2601.20452v1)
- An outcome-control case, **PROVEN by settlement**. In July 2026 the CFTC settled with former Rep. George Santos over Kalshi contracts on whether he would attend the 2026 State of the Union. He built a "No" position after saying publicly he would attend, posted about what he would wear, the "Yes" price rose within hours, and he exited at a profit. Terms: about $17,570 disgorgement, a $17,500 penalty, cease-and-desist and a 3-year trading ban; he neither admitted nor denied. Kalshi detected the trades, froze the account and referred him to the CFTC and DOJ. His counsel denies any intent to manipulate — [The Block](https://www.theblock.co/news/regulation/2026-07-31-george-santos-to-pay-35000-cftc-settlement-kalshi-sotu-bet-410338); [NOTUS](https://notus.org/us-news/george-santos-settles-kalshi-insider-trading-case-with-the-cftc)
- Resolution-layer manipulation is covered under Q4 (UMA). In the March 2025 Ukraine minerals-deal market (about $7M), critics alleged a whale used UMA voting power to force the resolution, and Polymarket refused refunds — [web3isgoinggreat](https://web3isgoinggreat.com/single/polymarket-governance-attack); [CoinDesk](https://dev.coindesk.com/markets/2025/03/27/polymarket-uma-communities-lock-horns-after-usd7m-ukraine-bet-resolves)

### Inferences
- The "hard to manipulate" result covers price manipulation in liquid markets whose outcome is exogenous. It does not cover (i) markets where a trader controls the outcome (Santos, "will X say Y" markets), (ii) markets where the resolver can be captured (UMA), or (iii) thin long-tail markets where one wallet is most of the book.
- For trading signals: a sharp move in a thin market that is not confirmed by other venues should be expected to mean-revert (Rhode-Strumpf), *unless* it is informed flow (see Q3). The two look similar at first.

### Gaps
- I did not read the Hanson-Oprea or Rhode-Strumpf full texts; the effect sizes above come from abstracts and citing papers.
- I found no rigorous 2024-2026 academic study measuring how long manipulative price pushes persist on Polymarket or Kalshi.

## Q2. What share of Polymarket volume is wash trading, per published studies?

### Takeaway
About 25% of Polymarket's all-time volume (about $4.5B) is classified as likely wash trading in the only major study: Sirolly, Ma, Kanoria and Sethi of Columbia/Barnard, an SSRN preprint from November 2025 that has not been peer reviewed. The share swings a lot by period (about 60% of weekly volume in December 2024, under 5% in May 2025, about 20% in October 2025) and by category (sports 45%, elections 17%, politics 12%). Treat reported volume as an inflated liquidity measure, especially in sports.

### Cited Findings
- Authors: Allen Sirolly, Hongyao Ma and Yash Kanoria (Columbia Business School) and Rajiv Sethi (Barnard). Method: an algorithm on public Polygon on-chain data that flags clusters of wallets trading mostly with each other. It flagged 14% of 1.26M wallets — [Fortune](https://fortune.com/2025/11/07/polymarket-wash-trading-inflated-prediction-markets-columbia-research/); [study PDF copy](https://gamblingharm.org/wp-content/uploads/2025/11/Polymarket-Wash-Trading-Study.pdf)
- About 25% of all-time volume; peak about 60% of weekly volume in December 2024; under 5% in May 2025; about 20% in October 2025. By category: sports 45%, elections 17%, politics 12%. About $4.5B of trades flagged — [Decrypt](https://decrypt.co/347842/columbia-study-25-polymarket-volume-wash-trading); [Fortune](https://fortune.com/2025/11/07/polymarket-wash-trading-inflated-prediction-markets-columbia-research/)
- Suggested causes: no KYC, no fees, and possible farming for an expected token airdrop (the authors' hypothesis). They do not accuse Polymarket of doing it. Polymarket said it was reviewing the study. The authors say the classification is not definitive — [Fortune](https://fortune.com/2025/11/07/polymarket-wash-trading-inflated-prediction-markets-columbia-research/)
- Kalshi is off-chain, so no comparable public analysis is possible — [Fortune](https://fortune.com/2025/11/07/polymarket-wash-trading-inflated-prediction-markets-columbia-research/)
- The CFTC's June 25, 2026 proposal would require exchanges to collect traders' employer and occupation data, which it says is "necessary to detect insider trading and prevent wash trading" — [DeFi Rate](https://defirate.com/news/cftc-proposes-employer-occupation-reporting-for-prediction-market-traders/)
- Some headlines report "up to 60%". That is the December 2024 peak, not the overall share — [Cointelegraph](https://cointelegraph.com/news/columbia-study-polymarket-wash-trading-research)

### Inferences
- Wash trades are self-crossed, so they mostly inflate *volume* and leave *price* largely unaffected. A volume-weighted or volume-filtered signal (e.g. "only trust markets above $X volume") is directly corrupted by them.
- Wash activity tracks incentives such as airdrop expectations, so the share can rise again around token or points events.

### Gaps
- I found no published update of the Columbia estimate covering 2026, and no wash-trading estimate for Polymarket US (the CFTC-regulated venue) as opposed to the offshore venue.

## Q3. Documented insider cases, their price signatures, whether insider flow could be a predictive signal, and the legal/ethical issues

### Takeaway
Since April 2026, the DOJ and CFTC have brought parallel criminal and civil insider-trading cases over prediction-market trades. Their theory is that event contracts are swaps covered by CEA §6(c)(1) and Rule 180.1 (misappropriation). The shared price signature: a new wallet places concentrated, low-probability bets in the hours to days before an announcement. Academic screens find such flow wins about 70% of the time, so it is predictive. However, trading on it knowingly or through a tip chain carries legal risk, and the signal arrives only shortly before the public news.

### Cited Findings
**Proven or charged cases**
- **CHARGED, April 2026, Maduro raid.** Active-duty US Army soldier Gannon Ken Van Dyke allegedly used classified information on the operation to capture Maduro. He opened a Polymarket account around December 26, 2025, used a VPN, and placed 13 bets from December 27 to January 2 (for example $96 on US forces in Venezuela, about $1,323 on Maduro out by end of January, and $6,100 on January 1), one of them hours before the January 3 operation. Reported winnings exceed $400K. He tried to delete his account on January 6 and moved proceeds to a foreign crypto vault. Charges: 3 CEA counts, wire fraud, and an unlawful monetary transaction. Polymarket says it referred the trades to the DOJ — [Al Jazeera](https://www.aljazeera.com/news/2026/4/23/us-soldier-charged-with-using-polymarket-to-bet-on-nicolas-maduro-abduction); [Fox](https://www.fox5ny.com/news/us-soldier-charged-betting-maduro-mission-polymarket); [A&O Shearman](https://www.lit-wc.aoshearman.com/doj-and-cftc-charge-us-soldier-for-insider-trading-in-prediction-markets)
- **CHARGED, May 27, 2026, Google "Year in Search".** Google engineer Michele Spagnuolo (account "AlphaRaccoon") is charged in SDNY with commodities fraud, wire fraud and money laundering, with a parallel CFTC civil complaint (CEA §6(c)(1), Reg. 180.1). He allegedly made about $1.2M on 20+ Polymarket contracts from October to December 2025 using internal, confidential Year-in-Search ranking data, with "near-perfect accuracy". It is the first such case against a public-company employee and shows the theory reaches corporate information, not just government secrets — [Davis Wright Tremaine](https://www.dwt.com/blogs/financial-services-law-advisor/2026/05/doj-cftc-case-employee-prediction-market-trading); [Debevoise](https://www.debevoise.com/insights/publications/2026/06/doj-and-cftc-bring-first-ever-prediction-markets); [MoFo](https://www.mofo.com/resources/insights/260601-doj-and-cftc-bring-parallel-insider-trading-actions)
- **PROVEN by settlement, July 2026.** Santos/Kalshi (see Q1). This is outcome control or self-dealing rather than classic insider trading.
- The CFTC enforcement director has called the idea that insider-trading rules don't apply to prediction markets a "myth" — [Blank Rome](https://www.blankrome.com/news-and-events/insider-trading-meets-prediction-markets-federal-enforcers-put-the-industry-on-notice/); [NYU Compliance & Enforcement](https://wp.nyu.edu/compliance_enforcement/2026/05/14/polymarket-insider-trading-charges-illustrate-doj-and-cftc-prediction-markets-enforcement-strategy/)
- Israeli authorities indicted a civilian and an IDF reservist over prediction-market bets. I have only this secondary mention and no details — [Harvard Law corpgov (Mitts and Ofir)](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/)

**Alleged, not charged (as far as I found)**
- **Nobel Peace Prize, October 2025.** Machado's odds jumped from about 3.6% to over 70% just before the announcement. Three accounts, including the new account "dirtycup", made about $90K together. The Nobel Institute said "we're looking into it". I found no reported outcome — [The Block](https://www.theblock.co/news/web3/2025-10-10-officials-probe-polymarket-over-suspicious-trades-predicting-nobel-peace-prize-winner-reports-374199); [Decrypt](https://decrypt.co/343840/nobel-peace-prize-organizers-intestigating-polymarket-insider-trades)
- **Iran strike, February 28, 2026.** Six new wallets made about $1.2M buying "Yes" as low as $0.10. Account "Magamyman" first traded 71 minutes before the news, at about 17% implied odds, and made about $553K — [Harvard Law corpgov](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/); [Bloomberg graphic](https://www.bloomberg.com/graphics/2026-polymarket-bets-iran-war-insider-trading/) (Bloomberg says it is impossible to determine definitively that the trades used nonpublic information)
- Also flagged: the "Burdensome-Mix" account made about $485K from $38.5K on the Maduro capture (it is not clear whether this is the charged soldier). Other flags: the Taylor Swift engagement ("romanticpaul") and the OpenAI browser launch — [Harvard Law corpgov](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/)
- **2024 "Théo" French whale.** Not an insider case, but the template for "whale moves odds". He staked $30M+ on Trump across 4 (later 8) accounts. He told the WSJ he had commissioned private "neighbor polls"; the WSJ could not verify this or rule out political ties. Chainalysis estimates about $78.7M net profit. France's ANJ opened an investigation and Polymarket geoblocked French users. No wrongdoing has been established — [Quartz](https://qz.com/donald-trump-election-betting-polymarket-whale-trader-1851691650); [The Block](https://www.theblock.co/post/324996/french-polymarket-whale-us-election-profit-france-ban); [casino.org](https://www.casino.org/news/polymarket-whale-funded-neighbor-surveys-to-win-85m-on-trump/)

**Systematic evidence**
- Mitts (Columbia) and Ofir (Haifa), "From Iran to Taylor Swift" (SSRN, 2026). They screened 93K+ Polymarket markets and about 50K wallets from February 2024 to February 2026 using five signals: bet size versus the cross-section, bet size versus the trader's own history, profitability, pre-event timing, and directional concentration. Flagged wallet-market pairs: 210,718, with a **69.9% win rate** (more than 60 standard deviations above chance) and about **$143M** of anomalous profit, which they call a lower bound. Limits: buy-side only, positions of $500+ only, and they cannot rule out coincidence or hedging. A Rutgers statistician questioned the method — [Harvard Law corpgov](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/); [AOL/coverage](https://www.aol.com/articles/informed-traders-polymarket-netted-143-082601427.html)
- Mitts and Ofir argue Kalshi (a DCM with surveillance) carries heavier obligations than offshore Polymarket, which pushes insiders offshore. They judge H.R. 7004 (barring officials from trading on MNPI) unlikely to cover most of the documented cases — [Harvard Law corpgov](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/)
- An AFA paper on "public learning from decentralized prediction markets" finds informed traders split activity across wallets and over time to hide it before announcements — [AFA](https://afajof.org/management/viewp.php?n=267904) (abstract only)
- Polymarket's terms of service (as of October 2025) did not appear to bar trading on insider information — [Decrypt](https://decrypt.co/343840/nobel-peace-prize-organizers-intestigating-polymarket-insider-trades)

### Inferences
- **Price signature to screen for:** a fresh or newly funded wallet, a first-ever trade, large size relative to market depth, buying a <20% outcome, a cluster of similar wallets, and timing from minutes to about 7 days before a scheduled or unscheduled announcement.
- **As a signal:** it is real (a 70% hit rate on low-probability buys), but (i) it fires late, often 1 hour to a few days before the news; (ii) by the time the move is visible the price has jumped (Machado went from 3.6% to 70%), so most of the edge is gone; (iii) false positives include whales with real research (Théo) and wash or airdrop flow. Its best use is as a confirmation or flag, not as standalone alpha.
- **Legal and ethical issues:** Following public on-chain flow is not itself insider trading, because the data is public. Liability arises if you know or should know the flow comes from misappropriated MNPI and you act as a tippee, or if you trade a related security or derivative on information obtained in breach of duty. If the event touches a listed company, SEC overlap is possible. Ethically, profiting alongside leaks of classified military operations is a reputational risk. This is my reading of the law-firm commentary above, not legal advice.

### Gaps
- I found no published accuracy or false-positive analysis of a real-time "insider wallet" detector used as a forward trading signal; the Mitts-Ofir results are ex post.
- I found no outcome of the Nobel probe and no US charges tied to the Iran-strike wallets.
- I could not confirm whether "Burdensome-Mix" is Van Dyke's account; the profit figures differ ($400K+ versus $485K).

## Q4. Resolution disputes and oracle (UMA) controversies

### Takeaway
Polymarket resolves markets through UMA's optimistic oracle. A proposed outcome can be disputed, and after escalation UMA token holders vote. The vote is weighted by stake, so large UMA holders who may also hold positions decide contested outcomes. There have been repeated high-dollar disputes from 2024 to 2026, at least one alleged governance attack, and a case where Polymarket publicly disagreed with UMA.

### Cited Findings
- **2024, Barron Trump/DJT market.** Polymarket publicly said "We firmly believe that UMA got this resolution wrong" — [The Block](https://www.theblock.co/post/302171/polymarket-contradicts-umas-resolution-on-barron-trumps-involvement-with-djt-token)
- **March 2025, Ukraine minerals deal (about $7M).** A whale allegedly used concentrated UMA voting to resolve "Yes" before any deal was signed, and Polymarket declined refunds. **ALLEGED** (no legal finding) — [CoinDesk](https://dev.coindesk.com/markets/2025/03/27/polymarket-uma-communities-lock-horns-after-usd7m-ukraine-bet-resolves); [web3isgoinggreat](https://web3isgoinggreat.com/single/polymarket-governance-attack)
- **2025, "Zelenskyy wears a suit" market (about $237M).** It resolved "No" despite photos traders argued showed a suit. Critics said "This isn't decentralized" and pointed to large-holder influence — [Decrypt](https://decrypt.co/329210/polymarket-rules-no-237m-controversial-bet-over-zelenskyys-suit?amp=1); [The Defiant](https://thedefiant.io/news/nfts-and-web3/polymarket-controversy-heats-up-after-the-zelenskyy-suit-market-resolves)
- **June 2026, Strategy (MicroStrategy) May bitcoin sale (about $85M).** It went to a UMA vote after a second resolution cycle and resolved "No" following a late rules clarification. One trader reportedly lost about $500K. The largest voters reportedly netted over $299K and over $370K from dispute voting — [The Defiant](https://thedefiant.io/news/markets/usd85m-polymarket-dispute-over-strategy-s-may-bitcoin-sale-puts-uma-s-token-voting-oracle-on); [Cointelegraph](https://cointelegraph.com/news/polymarket-dispute-strategys-bitcoin-sale-resolves-no); [DeFi Rate](https://defirate.com/?p=12726)
- How the process works: a proposal can be disputed twice before escalating to a token-holder vote — [ariverwhale substack](https://ariverwhale.substack.com/p/understanding-uma-and-dispute-resolution) (secondary)

### Inferences
- Resolution risk is a fat tail separate from forecast accuracy. Markets with ambiguous wording ("suit", "agreement", "sale") can settle against the real-world outcome. A price near 95% can mean "event happened, but the resolution is uncertain", not "95% likely".
- For the trading use case, prefer markets with objective, data-feed resolution (exchange prints, official tallies) and down-weight subjective-wording markets. Kalshi and Polymarket US (DCMs) resolve centrally under CFTC rules, which removes token-vote risk but adds exchange discretion.

### Gaps
- I verified the dollar figures only through crypto trade press; amounts vary between outlets.
- I found no academic quantification of how often UMA resolutions are disputed or overturned.

## Q5. Reflexivity: do odds influence outcomes or asset prices, and what does that mean for odds as trading signals?

### Takeaway
There is new experimental evidence (Brennan Center, September 2026) that showing voters market odds shifts who they think will win. Whether this changes votes is unproven, and older bandwagon evidence is mixed and small. On asset prices, Polymarket election odds Granger-led DJT stock in 2024 (a Quiver Quant media analysis) and moved long-end Treasuries by about 2bp per 10pp change in Trump's odds (an Aktuğ-Torul working paper). Odds function as a tradable macro factor, not only a forecast.

### Cited Findings
- **Brennan Center survey experiment** (1,994 registered voters, September 21, 2026). It randomized poll and Kalshi-odds displays. Higher displayed market odds made respondents more likely to name that candidate as the likely winner. Warnings about market caveats did not reduce reliance on the odds. Respondents also favored regulation. Note this is a single, advocacy-linked study — [Brennan Center](https://www.brennancenter.org/our-work/analysis-opinion/new-study-finds-prediction-markets-are-influencing-voters-and-voters-want); [casino.org](https://www.casino.org/news/prediction-markets-sway-voters-according-to-brennan-center-study/)
- The existence of bandwagon effects "remains a matter of dispute", with some evidence that perceived momentum raises support — [Journal of Prediction Markets 2016 WP](https://researchdmr.com/files/JournalofPredictionMarkets2016WP.pdf)
- Andy Hall on media amplification ("When Predictions Become News"): odds are increasingly reported as news — [Free Systems substack](https://freesystems.substack.com/p/when-predictions-become-news)
- Polymarket 2024 election odds Granger-caused DJT stock moves but not the reverse, and a simple backtest showed excess returns. The authors warn the relationship may not persist. This is media analysis, not peer reviewed — [Quiver Quant via Barchart](https://www.barchart.com/story/news/29231845/trump-media-stock-djt-linked-to-election-odds-our-investigation)
- Aktuğ and Torul (May 2026 working paper): daily rises in Polymarket's Trump-win probability map to long-end Treasury steepening and term-premium repricing, about 2bp per +10pp, with a coherent cross-asset "Trump trade" signature — [Boğaziçi PDF](https://web.bogazici.edu.tr/torul/yield.pdf)
- An arXiv 2026 microstructure study of the 2024 Polymarket presidential market (debate, assassination attempt, Biden dropout) found that the dropout drew heavy two-sided trading but little net repricing, i.e. disagreement rather than information — [arXiv 2603.03152](https://arxiv.org/abs/2603.03152v2)
- The CFTC's June 10, 2026 proposed rule would allow sports contracts while narrowing contracts on terrorism, assassination and war, explicitly citing insider-trading concerns. It had a 45-day comment period, and I found no final rule — [The Block](https://www.theblock.co/news/regulation/2026-06-10-cftc-unveils-sweeping-rule-proposal-fast-growing-prediction-markets-404258)

### Regulatory status (November 2026)
- **CFTC (Chair Michael Selig):** asserts exclusive federal jurisdiction. It withdrew the 2024 proposal to ban political and sports contracts, issued an ANPRM in March 2026, the June 10 listing-standards proposal, and the June 25 employer/occupation reporting proposal. No final rules found — [The Block](https://www.theblock.co/news/regulation/2026-06-10-cftc-unveils-sweeping-rule-proposal-fast-growing-prediction-markets-404258); [DeFi Rate](https://defirate.com/news/cftc-proposes-employer-occupation-reporting-for-prediction-market-traders/); [Corporate Compliance Insights](https://www.corporatecomplianceinsights.com/cftc-withdraws-proposed-rule-prediction-markets/)
- **States vs Kalshi (sports contracts):**
  - Third Circuit (April 2026): for Kalshi; its contracts are swaps on a DCM.
  - Ninth Circuit (August 28, 2026, Nevada): against Kalshi.
  - Sixth Circuit (September 25, 2026, Ohio/Tennessee): against Kalshi; it was not shown the contracts are swaps, and the CEA would not preempt state law anyway.
  - Fourth Circuit (Maryland): against Kalshi.
  - Connecticut: preliminary injunction denied on August 10; the Second Circuit denied an injunction pending appeal on November 3.
  - There is a circuit split, and a cert petition is pending at the Supreme Court. More than a dozen states have acted. These are mostly preliminary-injunction rulings.
  - Sources: [CNBC](https://www.cnbc.com/2026/09/25/appeals-court-rules-states-can-regulate-sports-prediction-markets.html); [The Block](https://www.theblock.co/news/regulation/2026-09-26-kalshi-loses-appeal-over-ohio-and-tennessee-sports-betting-laws-widening-circuit-split-416937); [Sportico](https://www.sportico.com/law/analysis/2026/kalshi-maryland-4th-circuit-ruling-decision-1234958963/)
- **Polymarket US:** bought the CFTC-licensed exchange and clearinghouse QCEX for $112M (July 2025). It received an amended DCM designation in November 2025 and began opening its US app to waitlisted users. On April 28, 2026 it reportedly filed for permission for US users to trade the main offshore book (outcome unconfirmed). A June 2026 CFTC probe was reported by a single source (unconfirmed) — [Decrypt](https://decrypt.co/350003/polymarket-set-us-return-following-approval-cftc); [The Block](https://www.theblock.co/amp/post/381253/polymarket-begins-opening-us-app-to-users-on-waitlist); [KuCoin news](https://www.kucoin.com/news/flash/polymarket-seeks-cftc-approval-to-reopen-to-us-traders)
- **Congress:** bipartisan bills to bar trading on MNPI by officials (for example H.R. 7004) have been introduced but not passed — [The Block](https://www.theblock.co/news/regulation/2026-06-10-cftc-unveils-sweeping-rule-proposal-fast-growing-prediction-markets-404258); [Harvard Law corpgov](https://corpgov.law.harvard.edu/2026/03/25/from-iran-to-taylor-swift-informed-trading-in-prediction-markets/)

### Inferences (for odds as trading signals)
- Odds feed back into asset prices (the Trump trade in Treasuries and DJT). Reflexivity therefore runs mainly *odds → prices*. A manipulated or wash-inflated move can briefly move linked assets, which argues for (a) requiring cross-venue confirmation (Polymarket and Kalshi), (b) filtering out markets dominated by a few wallets, and (c) fading isolated spikes in thin markets.
- An odds → outcome effect is plausible for perceptions (Brennan) but not shown for vote shares. It is a secondary concern for equity or macro signals.
- Signal-hygiene checklist from this research:
  1. Discount volume by up to about 25-45%, more in sports.
  2. Flag new-wallet, concentrated, low-probability buys as possible informed flow.
  3. Haircut subjective-resolution markets for UMA risk.
  4. Avoid markets a single actor can control, e.g. "will X attend or say Y".
  5. Expect regulatory shocks (state actions, CFTC listing rules) to change which markets exist and how liquid they are.

### Gaps
- The Brennan study's full methodology and its effect on vote intention (as opposed to win expectations) were not reviewed in full.
- I found no peer-reviewed causal study showing that prediction-market odds changed an election or corporate outcome.
- The DJT lead-lag result is from 2024 media analysis; I found no 2026 replication.
