# Millisecond lead-lag and latency arbitrage in US equities and futures: what retail can and cannot exploit (as of Nov 2026)

Note on dating: most hard numbers come from academic papers (data from 2005 to 2015) and vendor and exchange disclosures (2013 to 2024). I found no 2025 or 2026 primary source that updates the Chicago to NJ route records or the ES-SPY race statistics. Treat all figures as "latest published", not "current".

## Q1. Measured lead-lag: how far do ES/NQ futures lead SPY/QQQ and stocks?

### Takeaway
Futures (ES) are the price-discovery center for the S&P 500. ES moves start about 91% of ES-SPY arbitrage opportunities. The lag is set by the Chicago to NJ speed-of-light floor (about 4 ms one-way). The ES-SPY correlation is near zero at 1 ms, about 0.46 at 100 ms, about 0.69 at 1 s and about 0.91 at 10 s (2011 data). The median ES-SPY arbitrage window shrank from 97 ms (2005) to 7 ms (2011). Races in the London stock market (2015) last only 5 to 10 microseconds (modal).

### Cited Findings
- Hasbrouck (2003, JF 58(6), 2375–2400): "most of the price discovery occurs in the E-mini market" for the S&P 500 and Nasdaq-100. E-mini price changes generally lead the regular futures and the ETFs. ETFs play a smaller informational role. For the S&P 400 MidCap the ETF dominates. Estimated at resolutions down to 1 second. — [RePEc/JF](https://econpapers.repec.org/RePEc:bla:jfinan:v:58:y:2003:i:6:p:2375-2400); [NYU working paper](https://archive.nyu.edu/handle/2451/27374)
- A separate later study estimates the E-mini is about 6.26 times more important than SPY in price formation. This is not Hasbrouck's number. — [arXiv 1408.3650](https://arxiv.org/pdf/1408.3650)
- Budish, Cramton and Shim (QJE 2015), ES vs SPY median midpoint-return correlation, all 2011 trading days. These are "Mid" location (no light-speed offset), simple returns: — [BCS NBER version](https://conference.nber.org/conf_papers/f69665.pdf)
  - 1 ms: 0.0073
  - 10 ms: 0.0923
  - 100 ms: 0.4622
  - 1 s: 0.6879
  - 10 s: 0.9057
  - Averaged returns at 1 min: about 0.99+
- BCS correlogram (2011): the correlation-maximizing offset treats Chicago events as happening about 8 to 9 ms before New York events. At that offset the correlation is 0.0374 at 1 ms, 0.1976 at 10 ms and 0.4884 at 100 ms. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- BCS: 91% of ES-SPY arbitrage opportunities start with a price change in ES and 9% with SPY. This is consistent with ES being the center of price discovery. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- BCS: the median duration of ES-SPY arbitrage opportunities fell from 97 ms in 2005 to 7 ms in 2011. Profit per opportunity stayed flat at about 0.08 index points per unit. — [Richmond Fed summary](https://www.richmondfed.org/publications/research/econ_focus/2015/q3/research_spotlight); [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- BCS: highly correlated single-stock pairs (HD/LOW, GS/MS, XOM/CVX) have "essentially zero correlation at high frequency" (1 ms, 100 ms) but meaningful correlation at 1 minute. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- BCS: TAQ (consolidated, regulatory-feed) timestamps are "on the order of tens to hundreds of milliseconds delayed relative to the direct-feed data" (practitioner estimate, data from 2005 to 2011). — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- Aquilina, Budish and O'Neill (QJE 2022; LSE message data, 2015): — [NBER w29011](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf); [FCA OP50](https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-50-quantifying-high-frequency-trading-arms-race-new-methodology)
  - Races happen about once per minute per FTSE 100 symbol.
  - The modal race lasts 5 to 10 microseconds.
  - Races are about 20% of trading volume.

### Inferences
- Even in 2011 the ES-SPY lead-lag was set by the roughly 4 ms light-travel floor plus a few ms of processing. Arbitrage windows (median 7 ms) were close to that floor. By the 2015 UK data, races were decided within microseconds. A lag measured in milliseconds is fully contested by professional firms.
- At human-usable horizons (1 s or more) ES and SPY are already about 0.69 correlated, and at 10 s or more about 0.91 (2011 numbers). The market has only become faster since 2011. Any residual "lead" a retail system observes at second scale is mostly microstructure noise: tick-size rounding (ES tick 0.25 points vs SPY 0.01 dollars, about 0.10 index points) and bid-ask bounce. It is not an exploitable lag.

### Gaps
- I found no published ES-SPY or NQ-QQQ lead-lag estimate on post-2020 data. 2011 is the latest year with BCS-style numbers.
- I could not verify Hasbrouck's exact information-share percentages because the full text was not retrieved.
- I found no published number for the futures to single-stock lag. Single stocks react to index futures moves through ETF and basket arbitrage. By analogy the lag should be at the same ms or microsecond scale, but this is unsourced.

## Q2. Economics of latency arbitrage: size of the prize, costs, concentration

### Takeaway
ES-SPY alone was worth about $75M/yr (2005 to 2011). Latency arbitrage overall is about a 0.5 bp tax on trading and about $5bn/yr across global equities. Over 80% of race wins and losses go to 6 firms. Each race is worth only about half a tick, so it pays only at enormous volume with microsecond infrastructure.

### Cited Findings
- BCS: about 1,000 ES-SPY arbitrage opportunities per day. Profits per opportunity:
  - Median: 13 ES lots, 0.09 index points, $91.68.
  - 99th percentile: 135 lots, $885.46.
  - Daily profit in the NYSE-only data: $82k on average. Scaled to all venues: about $312k/day, or about $75M/yr.
  — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- Aquilina, Budish and O'Neill: — [NBER w29011](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf); [FCA OP50](https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-50-quantifying-high-frequency-trading-arms-race-new-methodology)
  - Each race is worth about half a tick.
  - The top 6 firms take over 80% of race wins and losses.
  - Latency arbitrage works like a roughly 0.5 bp tax on trading volume.
  - Removing it would cut the cost of liquidity by 17%.
  - About $5bn/yr is at stake in global equities.
- Infrastructure cost and speed: Spread Networks' straight Chicago-NJ fiber, built for an estimated $300M, cut round-trip time from about 16 ms to 13 ms (2010). Microwave links made it obsolete within a few years. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- CME Aurora colocation cost: $15,000 to $19,000 per month per 52U rack plus a $10,000 deposit. These are unofficial launch-era estimates. CME charges a one-time $500 for the Aurora cross-connect. A 10 Gb link tied to Equinix Secaucus is $12,000/month plus $2,000 to install. — [A-Team](https://a-teaminsight.com/cmes-aurora-co-lo-quick-facts/); [CME connectivity options](https://www.cmegroup.com/globex/connectivity-options.html); [Databento](https://databento.com/blog/cme-colocation)

### Inferences
- Half a tick per race spread over 6 dominant firms means the expected value of entering as a small player is negative. The fixed costs alone exceed any plausible retail capital base. Colocation (about $200k/yr per rack, estimate), microwave bandwidth (not publicly priced) and direct feeds all add up before one race is won.

### Gaps
- I found no current (2025–26) official CME Aurora or NYSE Mahwah / Nasdaq Carteret colocation price list. Microwave bandwidth pricing (McKay, NLN, etc.) is not public.
- I found no post-2015 US-specific race-share estimate. The 20% figure is from LSE data.

## Q3. Chicago–New Jersey links: microwave vs fibre latency

### Takeaway
The fastest microwave route from CME Aurora to Equinix NY4 was about 3.962 ms one-way (2020). The theoretical speed-of-light geodesic minimum is 3.955 ms. The best fibre is about 6.55 to 6.65 ms one-way (about 13.1 to 13.3 ms round trip). The race is now in single microseconds.

### Cited Findings
- FCC-license reconstruction (Bhattacherjee et al., IMC 2020): — [IMC 2020 paper](https://bdebopam.github.io/papers/imc2020-hft.pdf)
  - 9 connected networks ran CME to NY4 as of 1 Apr 2020.
  - Fastest: New Line Networks at 3.96171 ms one-way. Pierce Broadband was second, 0.4 µs slower.
  - On CME-NYSE and CME-Nasdaq, NLN was ahead by 8.1 µs and 0.8 µs.
  - Best CME-NY4 latency fell from 4.00 ms (2013) to 3.962 ms (2020), against a c-speed minimum of 3.955 ms.
- Nasdaq listed the fastest fibre Carteret to Aurora at 6.65 ms one-way, and its microwave product at 4.09 ms one-way. — [Nasdaq microwave doc](https://www.nasdaqtrader.com/content/Productsservices/trading/CoLo/microwave.pdf) (via search summary; older document)
- McKay Brothers Aurora to Carteret, round trip: 8.181 ms, then 8.147 ms (Nov 2013), 8.12 ms (Mar 2014), 7.98 ms (2014, the first under 8.0 ms). Quincy (McKay data) Aurora to Carteret one-way: 4.11 ms, then 3.982 ms (2016). — [McKay 2014 roadmap](https://mckay-brothers.com/mckay-brothers-releases-2014-us-microwave-roadmap); [McKay status update](https://mckay-brothers.com/mckay-brothers-delivers-status-update-2014-us-microwave-roadmap); [Quincy](https://quincy-data.com/quincy-data-lowers-latency-mckay-brothers-upgrades)
- Within NJ, ICE's wireless Mahwah to Secaucus (NY4/NY5) is about 116.7 to 117.8 µs one-way. Nasdaq's NJ metro to NY4 is 89 to 186 µs depending on product. — [ICE NJ metro](https://www.theice.com/market-data/connectivity-and-feeds/wireless/new-jersey-metro); [Nasdaq metro](https://m.nasdaqtrader.com/content/Productsservices/trading/CoLo/MetroFS.pdf)
- Within Chicago, McKay's Aurora to 350 E. Cermak is 370 µs round trip. — [McKay](https://mckay-brothers.com/mckay-brothers-opens-another-route-with-best-known-latency-aurora-cermak-service-clocks-in-at-370-microseconds)

### Inferences
- Microwave beats fibre by about 2.6 ms one-way (about 40%). Among microwave networks the gap is under 10 µs. Anyone without microwave is about 2.6 ms or more behind on every Chicago-to-NJ signal, and those signals are decided well within that 2.6 ms.

### Gaps
- I found no published 2021–2026 route records, including millimeter-wave, laser or shortwave hybrids. The task brief's "~4 ms vs ~6.5 ms" figure matches the one-way numbers above.

## Q4. SIP vs direct feeds; IEX speed bump; staleness of retail data (Alpaca IEX vs SIP)

### Takeaway
The SIP's own processing is now only about 13 to 15 µs. The real gap between SIP and direct feeds comes from geography and aggregation: hundreds of µs to ms, and historically tens to hundreds of ms for TAQ-style regulatory timestamps. Alpaca's free real-time feed is IEX only. IEX is a single venue, so its quotes can differ substantially from the NBBO. Free users can get SIP only if it is at least 15 minutes old. The IEX speed bump is 350 µs one-way.

### Cited Findings
- UTP SIP (Tape C) latency, measured from SIP receipt to SIP dissemination: — [UTP Q2-2024 stats](https://utpplan.com/DOC/UTP_Website_Statistics_Q2-2024-June.pdf); [UTP latency definitions](https://utpplan.com/PageParts/LatencyCharts.html)
  - Quotes, 2Q24: average 14.6 µs, median 12.8 µs, 10th percentile 11.9 µs, 90th 14.6 µs, 99th 18.0 µs.
  - Trades, 2Q24: average 15.2 µs, median 14.2 µs, 99th 24.5 µs.
  - In 1Q18 the quote median was 16.5 µs.
  - UTP also publishes "realized latency" from the matching-engine event to SIP dissemination, at the 10th/50th/99.9th percentiles.
- TAQ timestamps were tens to hundreds of ms behind direct feeds (2005 to 2011 era). — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- IEX: a 38-mile (61 km) fibre coil adds a 350 µs delay, about 700 µs round trip at the POP. Toronto's TSX speed bump is 1 to 3 ms. — [Wikipedia: IEX](https://en.wikipedia.org/wiki/IEX); [arXiv 1903.12458](https://arxiv.org/pdf/1903.12458)
- Alpaca market data: — [Alpaca forum](https://forum.alpaca.markets/t/unclear-subscription-type-and-limitations/10233); [Alpaca learn](https://alpaca.markets/learn/understanding-stock-market-data); [Massive vs Alpaca](https://massive.com/compare/massive-vs-alpaca)
  - The free plan streams real-time data from IEX only. Its quotes "will not be full market NBBO and can vary substantially."
  - Free-plan historical SIP queries must end at least 15 minutes before now.
  - The paid SIP tier ("Algo Trader Plus") has been cited at $99/month. Third-party sources conflict ($9 vs $99), so check Alpaca's pricing page.
- An Alpaca forum user measured 200 to 350 ms for REST API price and account calls. The same user reports account servers in Google us-east4 (N. Virginia) and data servers in New York. — [Alpaca forum](https://forum.alpaca.markets/t/what-are-your-response-times/5550)

### Inferences
- A retail stream (Alpaca websocket, IEX or SIP, delivered over the public internet from NY to the user's server) is probably 5 to 50+ ms behind exchange direct feeds in normal conditions. This is an estimate stacked from: the SIP aggregation hop, Alpaca's relay processing, internet transit and JSON parsing. With the IEX feed the problem is coverage, not only speed: IEX carries only a small share of volume, so its top of book often lags or differs from the NBBO.
- Alpaca's free SIP data, delayed 15 minutes, is useless for any intraday lag signal.

### Gaps
- I found no published end-to-end latency measurement of Alpaca's websocket feed versus exchange timestamps. IEX's market share was not retrieved; it is commonly cited at about 2 to 3%, but that is unverified here.
- I did not find the CTA (Tapes A and B) SIP latency figures.

## Q5. Retail order path: routing, PFOF, order-to-fill latency (Alpaca, cloud)

### Takeaway
Alpaca's internal OMS adds under 1.5 ms (85% of orders) to under 5 ms (95%). Client-to-Alpaca API round trips are 20 ms to a few hundred ms. Alpaca routes non-directed orders to wholesalers or market makers that pay for order flow. Cloud us-east-1 is about 3.5 ms from the NJ exchanges, versus about 0.1 ms on dedicated NJ metro wireless and microseconds in colocation.

### Cited Findings
- Alpaca OMS v2 (blog, 22 Nov 2021): 85% of orders are processed in under 1.5 ms and 95% in under 5 ms. The old v1 averaged about 150 ms, up to 500 ms under load. This is internal processing only, not end-to-end. — [Alpaca blog](https://alpaca.markets/blog/alpaca-launches-next-gen-order-management-system/)
- A forum repost attributed to Alpaca support gives about 20 ms one-way request time and about 9 ms median order execution (undated). Users report much larger paper-trading latency than live. — [Alpaca forum: execution speed](https://forum.alpaca.markets/t/measured-execution-speed/10732); [Alpaca forum: paper vs live](https://forum.alpaca.markets/t/massive-paper-trading-latency-vs-live-trading/9053)
- Alpaca receives payment from third-party liquidity providers (e.g. GTS Securities) based on order flow, per its 606 reports up to 2026Q2. An older (2021) page named Virtu, Citadel Execution Services and Jane Street. In March 2025 FINRA found Alpaca failed to disclose PFOF arrangement details in its 606 reports. — [Alpaca 606 2025Q4](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2025Q4.pdf); [Alpaca 606 2026Q2](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q2.pdf); [Alpaca PFOF explainer](https://alpaca.markets/learn/love-it-or-hate-it-inside-payment-for-order-flow-and-commission-free-trading-apps/); [FINRA 2025](https://finra.org/sites/default/files/2025-03/SD-2436-Alpaca-03-06-2025.pdf)
- Virtu's 606 text: a wholesaler can use its anticipated profit to give price improvement, to pay for order flow, or keep it. Citadel Securities had about 41% of PFOF (CRS). — [CRS IF12332](https://www.everycrsreport.com/reports/IF12332.html)
- A trading firm (Proof Trading) running US equities in AWS us-east-1 reports about 3.5 ms network latency to the NJ trading centers. This is a self-reported figure; the article returned 403 and was seen only via a search snippet. — [Proof Trading, Medium](https://medium.com/prooftrading/trading-in-the-cloud-market-microstructure-considerations-e601619f2c80)
- Databento cites about 1.05 ms from DC3 to CH1 and about 1.2 ms from DC3 to AWS Chicago (Local Zone). Note: us-east-2 is Ohio, not Chicago. — [Databento docs](https://databento.com/docs/architecture/performance-optimization.md)

### Inferences
- A typical retail order loop on Alpaca, over the public internet, runs signal → API → OMS → wholesaler → fill → ack in about 30 to 300+ ms (estimate). That is 3 to 5 orders of magnitude slower than a race (5 to 10 µs) and about 1 to 2 orders slower than even the 2011 ES-SPY windows (7 ms).
- Under PFOF, a marketable retail order is filled internally by a wholesaler at or inside the NBBO. The wholesaler sees the same futures move faster. Any "stale" price the retail trader thinks it is hitting is already repriced, or the wholesaler chooses the fill.

### Gaps
- There are no official Alpaca end-to-end order-to-fill latency stats. Wholesaler internal fill times are not public.

## Q6. Conclusion: at what timescale could any lag remain for a retail system?

### Takeaway
At ms and sub-second scales: no. Professionals own those horizons outright (microsecond races; about 3.96 ms vs 3.955 ms physical floor). At seconds: no reliable edge. ES and SPY were already 0.69 correlated at 1 s and 0.91 at 10 s in 2011, and the market is faster now. What is left is noise plus spread and fees. Retail can only compete at minutes and longer, where the "edge" is no longer latency but information processing or risk premia.

### Cited Findings
- ES-SPY correlation is about 0.69 at 1 s and about 0.91 at 10 s (2011). Arbitrage windows had a median of 7 ms. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)
- Races last 5 to 10 µs (modal) and are 80%+ concentrated among 6 firms. — [NBER w29011](https://www.nber.org/system/files/working_papers/w29011/w29011.pdf)
- A retail data and order loop is roughly 20 to 350 ms (Alpaca API measurements) plus about 3.5 ms of cloud-to-NJ network latency. — [Alpaca forum](https://forum.alpaca.markets/t/what-are-your-response-times/5550); [Proof Trading](https://medium.com/prooftrading/trading-in-the-cloud-market-microstructure-considerations-e601619f2c80)
- The ES tick (0.25 points) is coarser than SPY's (about 0.10 index points). Rounding keeps high-frequency correlations below 1 even without any true lag. — [BCS](https://conference.nber.org/conf_papers/f69665.pdf)

### Inferences
- The retail loop (about 50 to 300 ms) is slower than the whole lifetime of a cross-market arbitrage, so retail is always the stale quote being picked off, never the sniper. Any apparent "futures lead SPY by X seconds" pattern in retail bar data (1 s or 1 min) is most likely an artifact. Possible causes:
  - Timestamp misalignment between a CME data vendor and an IEX/SIP feed.
  - IEX-only quotes lagging the NBBO.
  - Bar-close sampling.
  - Bid-ask bounce.
  
  Any such pattern should be tested with trading costs: a SPY spread of about 1 cent (about 0.15 bp) plus slippage, against a moved quote.
- A plausible exception is not latency arbitrage. Slower information diffusion (minutes to days) in less-followed names, or event processing (earnings, macro releases parsed faster than humans), can still exist at horizons a cloud server can act on. Even there, machine-readable macro releases are raced at the ms level by HFTs (see the UNSW "Low Latency Trading on Macroeconomic Announcements" work found in search; not fetched).

### Gaps
- I found no peer-reviewed study that tests a retail-latency (100 ms to 1 s) ES→SPY strategy net of costs on recent data. That is the key empirical gap, and the user could test it directly with CME and SIP tick data (e.g. Databento) if desired.
