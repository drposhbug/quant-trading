# How Top Systematic/Quant Firms Make Money (RenTec, Two Sigma, D.E. Shaw, Citadel/Citadel Securities, Jane Street, HRT/Virtu, AQR, Man AHL, Bridgewater) — and What Transfers to a Retail Daily Long-Only Mega-Cap Tech System

Research date: 2026-11-18. Budget-limited pass (~20 tool calls). Many figures come from press reports citing unnamed people; these are flagged. **Survivorship bias warning for all sections:** every firm here was chosen because it survived and became famous. Failed quant shops (e.g., LTCM, and the many smaller stat-arb funds that closed after the 2007 "quant quake") are absent from this sample. Lessons drawn from it overstate how often these edges work.

## Q1: What does public evidence say about each firm's methods and edge sources?

### Takeaway
The best-documented edges fall into four groups: (1) **very short-horizon statistical arbitrage at massive trade counts plus leverage**, at RenTec Medallion (documented by a Senate report: >100,000 trades/day, ~20:1 leverage via basket options); (2) **market making / liquidity provision at scale with speed**, at Citadel Securities, Jane Street, HRT and Virtu (documented by Virtu's 10-K and academic HFT papers showing profits concentrated in the fastest firms); (3) **diversified slow factor and trend premia**, at AQR and Man AHL (documented in their own published research); and (4) **discretionary-systematic global macro**, at Bridgewater. Multi-strategy firms (Citadel Wellington, D.E. Shaw) mix these with pod-level risk controls. Recent filings and enforcement cases (Two Sigma at the SEC in 2025, Jane Street at SEBI in 2025) give rare views inside.

### Cited Findings

**Renaissance Technologies (Medallion)**
- In the July 2014 Senate PSI hearing, Sen. Levin said basket options let RenTec reach leverage "as high as 20:1", against the 2:1 limit under ordinary broker margin rules. The bank put up about 90% of the capital and the fund about 10%. — [Senate Hearing 113-422, govinfo](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm)
- RenTec's basket trading averaged "more than 100,000 trades each day, or about 30 million trades a year". Turnover was about 87% within 3 months, and orders went directly to exchanges with execution in milliseconds. — [Senate Hearing 113-422](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm)
- Witness Steve Rosenthal (Urban-Brookings) described the strategy as statistical arbitrage, using a model first built in the 1990s and continually refined. He said the adviser had about 200–250 staff, about 90 of them math/science PhDs. — [Senate Hearing 113-422](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm)
- Basket options produced about $34B in pre-tax profits for RenTec (2000–2014). The subcommittee estimated more than $6B in avoided taxes, because short-term gains were converted to long-term rates. — [Accounting Today](https://www.accountingtoday.com/news/renaissance-avoided-more-than-6-billion-tax-senators-say); [Senate hearing](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm)
- Renaissance's position (its own statement): the options were driven by business needs, not taxes. It said the average holding period of the Deutsche Bank options was 455 days. Note that this is the holding period of the *option wrapper*, not of the underlying trades. — [RenTec statement, Senate HSGAC](https://www.hsgac.senate.gov/wp-content/uploads/imo/media/doc/STMT%20-%20Renaissance%20(July%2022%202014).pdf)
- Bradford Cornell (UCLA, 2019 SSRN) reports Medallion's average annual return over 1988–2018 as 66.1% gross and 39.2% net, with standard deviation 31.7% gross and 20.3% net. — [Cornell via CXO Advisory / Institutional Investor](https://www.institutionalinvestor.com/article/b1k2fymby99nj0/Famed-Medallion-Fund-Stretches-Explanation-to-the-Limit-Professor-Claims); [SSRN copy](https://www.scribd.com/document/470291821/SSRN-id3504766-pdf). **Conflict:** an arXiv paper argues that averaging annual returns overstates the compounded rate, and puts the compounded gross figure much lower (31.8%), against Cornell's 63.3% — [arXiv 2405.10917](https://arxiv.org/pdf/2405.10917v2). The figures come from investor data cited by Zuckerman; they are not audited public filings.
- Fees of 5% management and 44% performance are widely reported but appear in secondary sources, not in Cornell's paper — [CXO Advisory](https://www.cxoadvisory.com/investing-expertise/proof-of-superior-investment-expertise/).
- **Myth-adjacent:** the claim that "Medallion is right 50.75% of the time" traces to a secondhand anecdote about Robert Mercer, not to any disclosure — [luxalgo summary](https://luxalgo.com/blog/simons-strategies-renaissance-trading-unpacked). The "2-day average holding period" claim is a single blog source. Zuckerman's account describes holdings of about a day or two up to a week or two — [Goodreads notes from Zuckerman](https://www.goodreads.com/notes/46025922-the-man-who-solved-the-market/13424516-zubair-habib/ac09e147-2acb-477a-8b37-c6dc212f714b); [quantvps](https://www.quantvps.com/blog/jim-simons-trading-strategy).

**Jane Street**
- 2025 trading revenue was a record $39.6B. This figure **includes gains on long-term investments**, notably early stakes in Anthropic and CoreWeave, so it is not pure market-making spread capture. — [Bloomberg via Fortune, Aug 15 2026](https://www.fortune.com/2026/08/15/jane-street-loss-15-billion-situational-awareness-stake-ai-bets/)
- About $15B loss in July 2026, the first monthly slump in about a decade. It was sourced to an unnamed person, with the FT reporting first. Causes cited were Jane Street's stake in the AI-focused hedge fund Situational Awareness (hit with margin calls after AI stocks reversed), "wrong-way bets" in Asian equities, and volatility. Net trading revenue YTD 2026 was still above $40B. Jane Street says it "closed a significant portion of its risk" in the areas that lost money and became "more selective about risk". — [Fortune/Bloomberg](https://www.fortune.com/2026/08/15/jane-street-loss-15-billion-situational-awareness-stake-ai-bets/). **Contested:** one outlet argues the loss figure is hard to square with a Fitch upgrade to BBB- — [CryptoBriefing](https://cryptobriefing.com/jane-street-15b-loss-claim-debunked/) (low-quality source).
- Financing: a $14.6B fixed-rate bond deal led by JPMorgan (investors included PIMCO, Capital Group and Fidelity) to refinance floating-rate loans and revamp an $11B capital stack — [Fortune/Bloomberg](https://www.fortune.com/2026/08/15/jane-street-loss-15-billion-situational-awareness-stake-ai-bets/). Reports also say part of the debt is moving to private lenders, which would narrow disclosure — [Traders Union](https://tradersunion.com/news/stocks/show/3001768-jane-street-15bn-loss-debt-shift/).
- SEBI interim order (3 July 2025): SEBI alleged that on index-options expiry days, Jane Street bought Bank Nifty constituents and futures to move the index while holding larger opposite options positions. It ordered ₹4,843.57 crore (about $570M) impounded, which Jane Street deposited on 14 July 2025. Jane Street calls the activity "index arbitrage" and disputes the order. It is interim, not a final ruling. — [Business Standard](https://www.business-standard.com/amp/markets/news/sebi-bars-jane-street-orders-rs-4844-cr-disgorgement-market-manipulation-125070400081_1.html); [Legal500](https://www.legal500.com/developments/thought-leadership/sebi-update-interim-order-against-jane-street-group-for-alleged-index-manipulation/)

**Citadel Securities / HRT / Virtu (market makers)**
- Citadel Securities' 2025 trading revenue was about $12.2B (+25% y/y), and HRT's about $12.3B. Both come from Reuters citing unnamed sources — [Reuters syndication (WDEZ)](https://wdez.com/?p=938851). **Conflict:** Hedgeweek/Bloomberg reported a Q2 2025 "record $7.3bn" for Citadel Securities, while IFR put Q2 at $2.4B — [Hedgeweek](https://www.hedgeweek.com/news/citadel-securities-posts-record-7-3bn-trading-revenue); [IFR](https://www.ifre.com/opinion/2308284/trading-titans-diverge-as-jane-streets-prop-push-pays-off). Treat the quarterly figures as unreliable.
- Virtu (public, audited 10-K): 2025 Adjusted Net Trading Income was $2,145.3M (+34.3%), of which Market Making was $1,666.3M (78%) and Execution Services $479.0M (22%). Average daily ANTI was $8.6M, up from $6.4M. Net income was $912.3M. — [Virtu FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000009/virt-20251231.htm); [Q4'25 8-K](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000003/exhibit991q425.htm). Virtu is the only firm in this group with audited public P&L. Its daily ANTI figure illustrates the business model: many small, consistent daily gains from spread capture on huge volume.
- Academic evidence (Baron, Brogaard, Hagströmer, Kirilenko): HFT revenues are highly concentrated and the concentration is not declining. Small latency differences are associated with large revenue differences, and aggressive (liquidity-taking) HFTs earned far more than passive ones. One early draft reports 122% vs 26% annualized, as reported in a secondary summary. — [CFTC working paper](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf); [Imperial repository](https://spiral.imperial.ac.uk/entities/publication/314ff61c-b583-44e9-b508-01aac9fa0e43)

**Two Sigma**
- In January 2025 the SEC settled with Two Sigma for a $90M civil penalty, after Two Sigma had voluntarily repaid $165M to funds and accounts. Model vulnerabilities were identified by March 2019 but not fixed until August 2023, which let a researcher (Jian Wu) alter model parameters. Wu was later indicted (U.S. v. Wu, 25-cr-413 SDNY) and is reportedly a fugitive. — [GlobalTrading](https://www.globaltrading.net/?p=37298); [ThinkAdvisor](https://www.thinkadvisor.com/amp/2025/09/12/ex-two-sigma-quant-charged-with-fraud-by-federal-prosecutors/). This is a rare documented look at model-governance risk inside a large quant firm.

**Citadel (Wellington) and D.E. Shaw**
- 2025 returns: Citadel Wellington +10.2% (person familiar), D.E. Shaw Oculus +28.2%, D.E. Shaw Composite +18.5% (one table labels this an estimate). The S&P 500 returned about 16.4%. — [Yahoo Finance/Business Insider](https://finance.yahoo.com/news/2025-returns-hedge-funds-rolling-234728986.html); [SentiSense](https://sentisense.ai/blog/best-performing-hedge-funds-2026/)

**AQR, Man AHL (trend/factor)**
- AQR's "A Century of Evidence on Trend-Following" (Hurst, Ooi, Pedersen; JPM 2017) finds positive trend returns across 67 markets back to 1880, with low correlation to traditional assets. Trend returns plotted against stocks form a "smile" (strong in extreme up and down equity years), with drawdowns of up to about 25%. Results stay positive after "2-and-20" fees. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing?aqrPDF=1); [PDF mirror](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)
- 2025: AQR Apex (multi-strategy) +19.6%, AQR Helix (alternative trend) +18.6% — [itiger/Bloomberg syndication](https://www.itiger.com/news/2600609750). Man AHL Diversified lost 7.8% in nine April days and was -15.15% YTD at that point. Man's own research put rolling 12-month trend returns at -18.6% to 30 Apr 2025. — [Hedgeweek](https://hedgeweek.com/news/man-groups-quant-hedge-funds-slide-as-market-volatility-roils-trend-strategies); [Man Institute "Is this time different?"](https://www.man.com/insights/is-this-time-different)

**Bridgewater**
- Pure Alpha gained about 33–34% in 2025, its best year in roughly 50 years. Reuters/press report that it followed a 2012–2024 stretch in which annual returns rarely exceeded about 3% (the low-return-decade claim comes from a Substack summarizing press). — [Hedgeweek](https://www.hedgeweek.com/bridgewaters-pure-alpha-outpaces-peers-with-33-2025-gain/); [Finimize](https://finimize.com/content/bridgewater-just-logged-its-best-year-in-50-years)

**Industry context**
- 2025 was hedge funds' best year since 2009, with gains driven heavily by equities long/short and macro (AI, tariffs, crypto themes) — [CNBC Jan 13 2026](https://www.cnbc.com/2026/01/13/hedge-funds-financial-crisis-short-citadel-bridgewater-ai-crypto-tariffs-pharma.html)

### Inferences
- **Edge taxonomy by firm (documented vs inferred):** RenTec Medallion = short-horizon stat arb + leverage + financing engineering (documented by the Senate report). Market makers = spread capture + latency + inventory internalization of retail order flow (documented for Virtu; inferred for the private firms). Jane Street's 2025–26 numbers show a growing **principal/venture** component (Anthropic, CoreWeave, Situational Awareness), not just market making. AQR/AHL = diversified trend and factor premia across many asset classes with volatility targeting (documented in their research). Bridgewater = macro with systematic risk parity / "all-weather" construction. Bridgewater's method was not researched in depth here.
- Leverage is a core multiplier at the top firms. Medallion's ~20:1 via basket options is the clearest documented case. A raw signal that earns a few basis points per trade becomes a 40–60%/year business only with high turnover plus leverage plus cheap financing.

### Gaps
- No primary source reviewed for D.E. Shaw's or Two Sigma's strategy mix (both are described in press as multi-strategy with large systematic equity books; not verified here). No Two Sigma 2025 return found.
- Citadel Securities' bond offering documents and Jane Street's offering memoranda were not obtained. Figures rely on Bloomberg/Reuters citing unnamed sources.
- No full-year 2025 or 2026 YTD Man AHL figure found.
- Bridgewater Daily Observations excerpts and Two Sigma Street View were not reviewed (budget).

## Q2: Why do Medallion's returns not transfer to RIEF/RIDA?

### Takeaway
Medallion runs high-turnover, short-holding-period strategies whose capacity is small (reportedly capped around $10B, employee-only), plus high leverage. RIEF and RIDA are built for institutional capacity (tens of billions), with longer holding periods, lower turnover and long-biased or factor-tilted equity exposure. That puts them in the crowded factor/momentum space, where returns are ordinary and drawdowns are correlated with other quants.

### Cited Findings
- Medallion strategies run at higher turnover and shorter holding periods than RIEF, and those strategies have lower capacity — [Wikipedia: Renaissance Technologies](https://en.wikipedia.org/wiki/Renaissance_Technologies) (secondary); [Chris Leithner](https://www.chrisleithner.com/how-warren-buffett-has-trounced-the-worlds-greatest-hedge-fund-manager/)
- Medallion's size is reported as capped at about $10B, around 2010 — [arXiv 2405.10917](https://arxiv.org/pdf/2405.10917v2) (secondary claim)
- Institutional Investor reports a long-run divergence: "The Famed Medallion Fund Is Crushing It. Other RenTech Funds, Not So Much" — [Institutional Investor](https://www.institutionalinvestor.com/article/b1l98yt4p0bvr4/The-Famed-Medallion-Fund-Is-Crushing-It-Other-RenTech-Funds-Not-So-Much)
- RIEF: +22.7% in 2024 (best since 2011), then **-14.39% in October 2025** (-7.5% YTD), then +12.65% in November 2025 (+2.34% YTD). The October loss came alongside a broad quant/momentum unwind; Goldman's prime brokerage saw quant long/short funds fall 1.7% that month. — [Institutional Investor Oct 2025](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october); [II Nov comeback](https://www.institutionalinvestor.com/article/premium/renaissances-public-funds-stage-double-digit-comeback-november); [iTiger "October chill"](https://www.itiger.com/news/1113033661)
- A blog table lists RIDA at about -10.3% YTD by early November 2025 and Medallion at an *estimated* +20% for 2025. These are unverified. — [funanc1al blog](https://funanc1al.com/blogs/follow-the-pundits/renaissance-technologies-in-2025-quant-quake-post-simons-growing-pains-amp-the-limits-of-the-machine)
- Medallion 2024 return of about +30% is unverified (profile site) — [freenance.io](https://freenance.io/funds/renaissance-technologies/)

### Inferences
- Capacity math: a signal with a 1–2 day half-life must be traded quickly. Market impact grows with position size (roughly with the square root of participation rate, per standard impact models). The profit per dollar therefore collapses as AUM scales. The same signal set cannot be sold at $50B+ to outside investors, so outside funds must use slower signals with lower Sharpe ratios.
- RIEF's 2025 drawdown pattern (a sharp month-long loss followed by a sharp rebound) is consistent with crowded factor exposure (momentum and AI winners), not idiosyncratic short-term alpha. This matters for a retail mega-cap tech momentum system, which owns the same crowded trade.

### Gaps
- RenTec does not publish returns. All Medallion figures after 2018 are unverified.
- RIEF/RIDA full-year 2025 and 2026 YTD numbers were not found.

## Q3: How do these firms manage risk?

### Takeaway
Documented practices are tight drawdown-triggered capital cuts at pod shops (often a 5% drawdown is the first trigger, though exact rules vary and are mostly anecdotal), central risk books that hedge factor crowding, volatility targeting at trend and factor managers, and fast risk reduction after losses (Jane Street after July 2026). The documented failures were model governance (Two Sigma), leverage plus concentration in a crowded theme (Jane Street's AI stake, July 2026), and crowded factor exposure (RIEF, October 2025).

### Cited Findings
- Pod stop-outs: an informal but widely repeated version is that a PM's capital is halved at a 5% drawdown and the pod is shut at 7.5%. Other accounts say 5%/10%, and capital is sometimes pulled at 2.5–3%. There is no universal threshold. Millennium is described as quicker to close pods than Citadel, which weighs long-run pod track records. All of this comes from commentary and forums, not filings. — [Resonanz Capital](https://resonanzcapital.com/insights/when-risk-controls-make-diversification-conditional); [WSO forum](https://www.wallstreetoasis.com/forum/hedge-fund/multi-manager-risk-limits)
- BlueCrest and Millennium closed pods quickly after the August 2024 turmoil — [BNN Bloomberg](https://www.bnnbloomberg.ca/investing/2024/08/30/bluecrest-millennium-pods-faced-quick-closure-after-turmoil/)
- Central risk books at multi-managers may hedge firm-wide concentration in names and factors without telling the pods — [Resonanz Capital](https://resonanzcapital.com/insights/when-risk-controls-make-diversification-conditional) (commentary)
- March 2026 volatility exposed weaknesses in the multi-strategy model (a "performance reset") — [HedgeCo](https://www.hedgeco.net/news/03/2026/the-multistrategy-performance-reset.html)
- Jane Street post-loss: closed a significant portion of risk in the losing areas and reduced risk in other strategies — [Fortune/Bloomberg](https://www.fortune.com/2026/08/15/jane-street-loss-15-billion-situational-awareness-stake-ai-bets/). After the loss, the Fed and Bank of England reportedly stepped up scrutiny of ties between banks and trading firms — [CryptoBriefing](https://cryptobriefing.com/fed-boe-review-bank-risks-jane-street-loss/) (low-quality source).
- Trend followers size positions by volatility. AQR's century study notes drawdowns of up to about 25% even so. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing?aqrPDF=1)
- Model governance failure: Two Sigma left known model vulnerabilities unfixed for more than 4 years ($165M of client harm repaid, $90M penalty) — [GlobalTrading](https://www.globaltrading.net/?p=37298)

### Inferences
- The common pattern is many small, independent bets, each with a hard loss limit, and capital re-allocated mechanically on drawdown. For a single long-only retail book on correlated mega-cap tech, the closest analogues are portfolio-level volatility targeting and a drawdown-based exposure cut. Diversification across uncorrelated pods is not available.

### Gaps
- No primary documentation of Citadel's or Millennium's actual risk limits. Bridgewater's risk-parity mechanics were not verified in this pass.

## Q4: Performance 2022–2026, especially AI / mega-cap tech

### Takeaway
2025 was a strong year for macro (Bridgewater +33–34%), multi-strategy (D.E. Shaw Oculus +28%), trend at AQR (+18.6%) and market makers (record revenues). Man AHL trend struggled in H1 2025. The AI / mega-cap tech trade caused the sharpest documented quant pain: RIEF's October 2025 momentum unwind and Jane Street's July 2026 loss tied to an AI fund. Evidence for 2022–2024 was not collected in this pass beyond RIEF 2024 (+22.7%).

### Cited Findings
- RIEF -14.39% in October 2025, in a momentum/quant unwind — [Institutional Investor](https://www.institutionalinvestor.com/article/renaissance-suffers-huge-losses-october); [iTiger](https://www.itiger.com/news/1113033661)
- Jane Street's July 2026 loss of about $15B followed a sharp reversal in US AI stocks after a strong early-2026 rally. Situational Awareness faced margin calls and offloaded a large part of its equity book to Citadel. — [Fortune/Bloomberg](https://www.fortune.com/2026/08/15/jane-street-loss-15-billion-situational-awareness-stake-ai-bets/)
- Citadel Wellington was reportedly up 5.7% in H1 2026 (date ambiguous in source) — [SentiSense](https://sentisense.ai/blog/best-performing-hedge-funds-2026/)
- Other 2025 figures are in the Q1 cited findings (Wellington +10.2%, Oculus +28.2%, Pure Alpha +33–34%, AQR Helix +18.6%, Virtu ANTI +34%).

### Inferences
- The crowded AI and mega-cap tech momentum trade has twice (October 2025 and July 2026) produced sharp, correlated losses even at the most sophisticated firms. A retail long-only system concentrated in that trade owns this crash risk directly, with no hedge.

### Gaps
- 2022 (the trend-following boom year, equity bear market) and 2023–2024 returns for most firms were not collected in this pass.
- No firm-level attribution of returns specifically to mega-cap tech names was found. 13F holdings would be needed.

## Q5: Which edge sources are available to a retail daily-rebalancing long-only US mega-cap tech system with free data?

### Takeaway
Mostly **not available**: speed and latency (the market-making and HFT edge), order-flow internalization, Medallion-style high-turnover stat arb (needs leverage, cheap financing, tick data and low costs), basket-option financing, alternative data, and short-side and cross-asset diversification. **Partially available**: slow factor premia (time-series and cross-sectional momentum, low-vol / quality tilts) and the volatility-targeting and drawdown-control risk methods used by AQR/AHL and the pod shops. The retail advantage is small size: no capacity constraint and no forced deleveraging by investors. That only helps for slow, cheap-to-trade signals.

### Cited Findings
- Speed concentrates HFT profits in the fastest firms, and concentration is not declining — [Baron et al., CFTC WP](https://www.cftc.gov/idc/groups/public/@economicanalysis/documents/file/oce_riskandreturn0414.pdf)
- Market-making P&L is a spread-capture business at scale ($8.6M per day average for Virtu) — [Virtu 10-K](https://www.sec.gov/Archives/edgar/data/1592386/000159238626000009/virt-20251231.htm)
- Medallion relied on ~20:1 leverage and >100k trades/day — [Senate Hearing](https://www.govinfo.gov/content/pkg/CHRG-113shrg89882/html/CHRG-113shrg89882.htm)
- Trend premia are documented over 100+ years, but they rely on **diversification across 67 markets and long/short positioning**. Single-asset-class long-only trend is a much weaker version. — [AQR Century](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing?aqrPDF=1)

### Inferences
| Edge source | Who uses it | Retail daily long-only mega-cap tech? |
|---|---|---|
| Latency, co-location, spread capture | Citadel Sec, Jane Street, HRT, Virtu | No. Needs exchange infrastructure and capital |
| Retail order-flow internalization | Citadel Sec, Virtu | No |
| Intraday/multi-day stat arb at huge trade counts | Medallion | No. Costs, data, leverage and shorting are all missing |
| Leverage and financing engineering (basket options, repo) | Medallion, pod shops, Jane Street | No (Reg T 2:1 at most; costly) |
| Alternative data (satellite, card spend, etc.) | Two Sigma, D.E. Shaw, pods | Largely no (paid). Free proxies only |
| Cross-asset trend and carry | AQR, Man AHL, Bridgewater | Weak version only (long-only, single sector) |
| Equity factor premia (momentum, quality, low-vol) | AQR, RIEF | Yes, partially. Mega-cap tech momentum is the crowded trade that crashed in October 2025 |
| Volatility targeting and drawdown-based exposure cuts | AHL, AQR, pod shops | Yes. Fully replicable with free daily data |
| Small size / no capacity limit | n/a (an institutional handicap) | Yes. The real retail edge, but only for slow signals |
| Cash/T-bill yield on idle capital | All (financing income) | Yes (e.g., SGOV) |

- Realistic expectations: survivorship-biased famous records (Medallion 39% net) are not a benchmark. AQR/AHL-style diversified trend has had multi-year flat periods and drawdowns of about 25%. A concentrated long-only tech system should expect beta-dominated returns and the crowding crashes seen in October 2025 and July 2026.

### Gaps
- No direct evidence found on what slow factor signals still earn net of costs within a 10–20 stock mega-cap universe. Note that the project's own studies (`reports/`) are the relevant test bed.
