# Engineering & Legal Constraints for a Retail Low-Latency Lead-Lag System (US person, Nov 2026)

Note on sources: many latency figures come from VPS vendors (QuantVPS, tradingvps.io, NYC Servers) with a commercial interest. Those are labelled "vendor claim". Anything not sourced is in Inferences or Gaps and labelled as an estimate.

## Q1. Where are the servers, and what end-to-end latency can a retail system realistically achieve (home PC vs $5–50/mo VPS vs bare metal near NJ)?

### Takeaway
The venues are spread across continents: Polymarket international is in London (AWS eu-west-2), Kalshi reportedly in AWS us-east-2 (Ohio), Coinbase in AWS us-east-1 (N. Virginia), Binance probably in AWS Tokyo, and Alpaca's market data in NY with order servers in GCP us-east4 (Virginia). So no single box is close to everything. A same-region cloud VM gets roughly 1–15 ms to a given venue. Home broadband adds tens of ms plus jitter. Venue-side delays (Polymarket taker delays, Alpaca's ~10–20 ms internal data latency) are often larger than the network gap a retail trader can close.

### Cited Findings
**Venue locations**
- Polymarket (international CLOB): "Primary Servers: eu-west-2" (AWS London). "Closest Non-Georestricted Region: eu-west-1" (Dublin). Polymarket says KYC/KYB'd users can request co-location access in eu-west-2. — [Polymarket docs: geoblock](https://docs.polymarket.com/developers/CLOB/geoblock); [search summary of same page](https://docs.polymarket.com/api-reference/geoblock.md)
- Vendor claim: QuantVPS Dublin reaches clob.polymarket.com in 0.83 ms, and AWS eu-west-1 is under 2 ms from London. — [QuantVPS](https://www.quantvps.com/blog/polymarket-servers-location)
- Kalshi: a third-party latency monitor (Glassnode) places Kalshi's order book behind AWS CloudFront with origin in AWS us-east-2 (Ohio). Kalshi does not publish its region. A VPS vendor instead guesses "Chicago metro" from latency tests. — [Glassnode latency monitor about page (search snippet; page fetch failed)](https://hyperlatency.glassnode.com/prediction-markets/about); contradicted/unclear: [QuantVPS Kalshi servers](https://www.quantvps.com/blog/kalshi-servers-location)
- Kalshi FIX hosts: order entry `mm.fix.elections.kalshi.com`, market data `marketdata.fix.elections.kalshi.com`. AWS PrivateLink is available at Premier tier and above, VPC peering at Prime and above, both via institutional@kalshi.com. No region is named. — [Kalshi FIX connectivity](https://docs.kalshi.com/fix/connectivity)
- Coinbase: US Spot Exchange infrastructure is hosted in AWS US-EAST-1 across multiple AZs. — [Coinbase systems & operations docs](https://docs.cdp.coinbase.com/exchange/introduction/systems-operations.md)
- Binance: widely reported as AWS Tokyo (ap-northeast-1), but this is not officially confirmed. Binance.com returns HTTP 451 to US IPs. — [CCXT latency blog](https://docs.ccxt.com/blog/how-far-is-your-exchange)
- Alpaca: a 2021 staff post says the data servers are "in New York", colocated with the SIP, with typically under 20 ms latency, and the account/trading servers are at "Google ... us-east4 data center North Virginia". This is 2021 info and may be stale. — [Alpaca forum: data center locations](https://forum.alpaca.markets/t/alpaca-data-center-locations/5640)
- Alpaca forum staff reply: REST and WebSocket data arrive with "approx. 10–20ms" latency. One user measured 600 ms–1 s end to end, which depends heavily on the network. — [Alpaca forum: latency on real-time API](https://forum.alpaca.markets/t/latency-on-real-time-alpaca-api/19092); [What are your response times?](https://forum.alpaca.markets/t/what-are-your-response-times/5550)

**Measured latencies from datacenters (median TTFB on the order-book endpoint, includes server processing; Globalping probes)**
- Coinbase: 10 ms from New York, 10 ms from London, 44 ms from Tokyo. Binance: blocked from NY, 229 ms from London, 8 ms from Tokyo. Kraken: 92 ms from NY, 16 ms from London, 249 ms from Tokyo. — [CCXT "How far is your exchange?"](https://docs.ccxt.com/blog/how-far-is-your-exchange)
- Independent benchmark from a US-East server: Coinbase p50 of 13.6 ms. — [FillBench on DEV](https://dev.to/fillbench/i-benchmarked-9-crypto-exchange-apis-from-a-us-datacenter-p50p95p99-45dm)
- Vendor/review-site claim: Vultr New Jersey reaches NY4 (Secaucus) in about 0.9 ms over 3 hops. Vultr starts at $5/mo (regular) and $6/mo (high-frequency). — [bestusavps review](https://bestusavps.pages.dev/reviews/vultr); [bestusavps east coast](https://bestusavps.pages.dev/best-for/us-east-coast)
- Home broadband: FCC Measuring Broadband America reported all terrestrial providers below 60 ms latency to its test servers, and satellite above 600 ms (2015 report, via news summary). Fiber outperforms cable. — [advanced-television summary of FCC](https://www.advanced-television.com/2016/12/02/fcc-average-us-broadband-speed-rising-rapidly/); [FCC 2023 MBA report PDF](https://data.fcc.gov/download/measuring-broadband-america/2023/2023-Fixed-Measuring-Broadband-America-Report.pdf)
- The CCXT author warns that a laptop's ping is not a production ping and recommends measuring from the deployment region. Some venues (for example Bybit) return 403 to datacenter IP ranges. — [CCXT blog](https://docs.ccxt.com/blog/how-far-is-your-exchange)

**Venue-imposed delays (these set a floor no matter how fast you are)**
- Polymarket: "selected crypto and finance up/down markets" use a 250 ms taker delay, then re-validate. You can detect it with `GET https://clob.polymarket.com/clob-markets/{condition_id}` → `itode: true`. Sports markets have a configured delay "around live game conditions". During either delay the order "is pending and cannot be canceled". — [Polymarket order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)
- Sources disagree on the sports delay. Docs say a 1 s matching delay. An older help article says 3 s, with 1 s being tested on NBA/MLB. A third party saw 1 s on EPL and none on NBA as of 27 Oct 2026. — [Polymarket order lifecycle (md)](https://docs.polymarket.com/concepts/order-lifecycle.md); [Polymarket help: limit orders](https://intercom.help/polymarket/en/articles/13364444-limit-orders); [startpolymarket in-play](https://startpolymarket.com/strategies/in-play-trading/)

### Inferences
- Estimated tiers (my estimates from the figures above plus fibre physics of about 1 ms RTT per 100 km; not measured by me):
  - **Home PC, US East, fibre/cable**: about 10–40 ms RTT to NJ/VA cloud venues (Coinbase, Alpaca), about 25–50 ms to Ohio (Kalshi), about 75–110 ms to London (Polymarket int'l), about 150–200 ms to Tokyo (Binance). Add Wi-Fi/bufferbloat jitter of 5–100+ ms under load, plus Python processing. Realistic end-to-end signal→order-ack is about 50–300 ms.
  - **$5–50/mo VPS in the right region** (AWS/GCP same region, or Vultr/DO NJ): about 1–15 ms network RTT per venue. Realistic end-to-end in Python asyncio is about 5–30 ms per leg. Cross-venue legs still pay inter-region RTT: NJ↔London about 70–80 ms, NJ↔Ohio about 10–15 ms.
  - **Bare metal in NJ (e.g., near NY4/Carteret), about $100–300+/mo**: sub-ms to NJ equity datacenters. This only helps if you have direct exchange or SIP feeds. Alpaca's own path (NY data plus a VA order gateway, about 10–20 ms internal) caps the gain for an Alpaca user.
- For a cross-venue lead-lag (e.g., US equities/crypto leading Polymarket), the irreducible cost is the inter-region hop (NJ/VA→London about 35–40 ms one way). Two boxes are the natural design: a signal box near the leader, and an execution box in eu-west-1 for Polymarket or us-east-2 for Kalshi, linked by a persistent TCP/websocket.
- The Polymarket 250 ms and 1–3 s delays mean lags shorter than the delay cannot be captured on delayed markets as a taker. Being 5 ms vs 50 ms away barely matters there. They also expose takers to adverse selection, because makers can cancel during your pending window.

### Gaps
- No official Kalshi hosting region. The us-east-2 claim comes from one third-party monitor whose page I could not fetch (DNS failure), and it conflicts with a vendor's "Chicago" guess. Measure it yourself (e.g., traceroute or TCP connect time from us-east-1/us-east-2/us-east-4).
- No official Binance or current Alpaca location disclosure. Alpaca's info is from 2021.
- No authoritative 2023+ FCC median idle latency for fibre vs cable was extracted (only the 2015 summary). Polymarket US (DCM) hosting location was not found.
- No independent measurement of Polymarket eu-west-1↔eu-west-2 RTT. Only vendor claims.

## Q2. What latency is needed to compete for lags that close in 1 s, 10 s, 60 s?

### Takeaway
No source publishes a retail-competitiveness table, so this section is almost entirely inference. Lags closing within about 1 s are contested by co-located or same-region bots and are partly neutralised by Polymarket's taker delays. 10 s lags are reachable from a same-region VPS. 60 s lags are reachable even from home if the signal itself is fast.

### Cited Findings
- Polymarket's 250 ms taker delay on selected crypto/finance up/down markets and its 1–3 s sports delays were introduced to curb automated latency gaming (reported as "Polymarket Locks Taker Orders to Curb Automated Gaming"). — [Polymarket order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle); [news headline (secondary)](https://san-1510.aid.brainsum.com/news/top-news/polymarket-locks-taker-orders-curb-automated-gaming)
- Polymarket offers co-location in eu-west-2 to KYC/KYB'd users, so the fastest competitors are sub-ms from the matching engine. — [Polymarket geoblock docs](https://docs.polymarket.com/developers/CLOB/geoblock)
- Vendors report traders moving to Tokyo for Hyperliquid, claiming a "200ms edge over global rivals" (vendor/news claim). — [cryptorank](https://cryptorank.io/news/feed/36445-hyperliquid-traders-in-tokyo-gain-200ms-edge-over-global-rivals)
- Kalshi rate-limit tiers (tokens/s at 10 tokens per request; read/write): Basic 200/100 (≈20 reads and 10 writes per second), Advanced 300/300, Expert 600/600, Premier 1,200, Paragon 2,400, Prime 4,800, Prestige 12,000/9,600. Higher tiers require 0.075–1.0% of trailing 30-day volume. WebSocket connection limit is 200 for Basic through Expert. A 429 carries no Retry-After header. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits)
- Polymarket US REST: 20 requests/s per IP (search snippet of official docs, which are access-gated). — [Polymarket US API docs (gated)](https://apidocs.polymarketexchange.com/getting-started/rate-limits)

### Inferences (all estimates)
- Rule of thumb: you need total reaction time (detect + decide + order RTT + venue delay) well under the half-life of the lag, and you need to be faster than the marginal competitor, not just faster than the lag.
  - **≤1 s lags**: on undelayed books you compete with eu-west-2 co-located or same-region bots that react in about 1–20 ms. A home PC (100–300 ms end-to-end to London) arrives late, after the quote has already moved. A Dublin VPS (about 5–20 ms) is borderline. On delayed markets (250 ms / 1 s) the lag may close before your taker fill and you cannot cancel, so expect strong adverse selection. Treat this as not realistically harvestable for retail.
  - **~10 s lags**: a same-region VPS (5–30 ms) is ample. Home is often OK too, but jitter, reconnects and Python GC pauses matter more than mean latency. The edge comes from signal quality and fill probability, not ms.
  - **~60 s lags**: latency is irrelevant at the network level. Home PC is fine. Limits are data quality (SIP vs IEX), fees and spread, and rate limits (Kalshi Basic allows about 10 writes/s).
- If a lag persists for 10–60 s on a liquid market, it is more likely an illiquidity or fee wall than free money. This matches the repo's earlier finding (commit f3e2662) that Polymarket/Kalshi are well calibrated with no edge after about 1 c costs.

### Gaps
- No public empirical study found of how fast Polymarket/Kalshi prices converge to external signals (e.g., BTC spot → 15-min up/down markets). That would need the user's own logged data.

## Q3. Engineering: websocket client design, clock sync, one-way vs RTT measurement, logging

### Takeaway
Use a single asyncio process per venue with application-level heartbeats, exponential-backoff reconnects with snapshot resync, and two timestamps per message (venue exchange time plus local receipt time). On AWS, sync clocks with chrony against Amazon Time Sync. Its PTP hardware clock gives microsecond-level accuracy, which makes one-way latency estimates meaningful. At home, NTP gives only ms-level accuracy, so measure RTT and treat one-way as RTT/2 with caveats.

### Cited Findings
- Amazon Time Sync Service provides microsecond-level accuracy on supported EC2 instances via NTP or a PTP Hardware Clock (PHC). Direct PTP is Linux only. The PHC does not pass an error bound to chrony, so AWS exposes `phc_error_bound` via ENA sysfs to add. NTP smears leap seconds and the PHC does not. — [AWS blog: microsecond-accurate clocks on EC2](https://aws.amazon.com/blogs/compute/its-about-time-microsecond-accurate-clocks-on-amazon-ec2-instances); [EC2 NTP config](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/configure-ec2-ntp.html)
- AWS added nanosecond hardware packet timestamps (latest ENA driver) in June 2025. ClockBound gives timestamps with error bounds for comparing events across instances. — [AWS what's new](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-time-sync-nanosecond-hardware-packet-timestamps); [ClockBound docs](https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/compare-timestamps-with-clockbound.html)
- Third-party claim: Kalshi websockets disconnect silently after about 60 s without client activity, so send pings (not confirmed in official docs). — [pm.wiki Kalshi API recipes](https://pm.wiki/de/learn/kalshi-api-python-recipes)
- Alpaca users report selective websocket feed failures at market open on the paid plan. — [Alpaca forum](https://forum.alpaca.markets/t/selective-websocket-feed-failures-during-market-open-need-feedback/17587)
- Coinbase had an outage when an AWS us-east-1 cooling failure exposed trading-system coupling, so single-region dependency is a real failure mode. — [lavx news on Coinbase postmortem](https://news.lavx.hu/article/coinbase-postmortem-shows-aws-cooling-failure-exposed-trading-system-coupling)
- During a Polymarket delay the order cannot be cancelled, so log the order state transitions (pending→matched/placed). — [Polymarket order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)

### Inferences (design recommendations; practitioner consensus, not individually sourced)
- **Client**: Python `asyncio` with the `websockets` or `aiohttp` library is fine at 10–60 s horizons. Use `uvloop` on Linux and `orjson` for parsing. Run one task per connection, push into an `asyncio.Queue`, and keep a single strategy consumer. Never do blocking I/O in the receive loop. Write logs from a separate thread or process.
- **Heartbeats**: send protocol ping every 10–20 s (under Kalshi's ~60 s idle cutoff), and also run a staleness watchdog: if no message on an active market for N seconds, force a reconnect.
- **Reconnects**: exponential backoff with jitter (0.5 s → 30 s cap). After reconnect, re-subscribe, fetch a REST snapshot, and reconcile sequence numbers. Mark the book "dirty" and do not trade until resynced. Log every gap.
- **Timestamps per message**: `t_exch` (venue's own timestamp, if provided), `t_recv_wall` (`time.time_ns()` on receipt, before parsing), and `t_recv_mono` (`time.monotonic_ns()`, for intervals). For orders, log `t_send`, `t_ack`, `t_fill`, and the venue's order timestamps.
- **One-way vs RTT**: RTT = `t_ack − t_send` on the monotonic clock, which needs no clock sync. One-way feed latency = `t_recv_wall − t_exch`. This is only meaningful if your clock error (chrony `tracking` offset, or ClockBound bound) is much smaller than the latency. On AWS PHC that is µs, so fine. At home over internet NTP, expect ms-level error (estimate 1–10 ms; I found no source quantifying it), so one-way numbers below about 20 ms are noise. Also, venue timestamps can be taken at gateway or engine and have unknown own-clock error.
- **Lead-lag measurement**: compute lags across venues using `t_exch` from each venue, not local receipt times. Separately report "observable lag" from local receipt times, since that is what you can trade.
- **Logging**: append-only newline-delimited JSON or Parquet per venue per day, raw messages plus the local timestamps. Rotate daily and compress, then replay later through the same strategy code for a backtest of fills and latencies.
- **Windows home PC caveat**: Windows timer/clock resolution and the W32Time service are much worse than chrony on Linux. Run the system on a Linux VPS, or at least WSL2 with chrony (estimate).

### Gaps
- No primary source for typical internet-NTP accuracy for home users, or for Python asyncio per-message overhead. Both are estimates.

## Q4. Costs: VPS, data feeds (Alpaca SIP, Massive/Polygon, Databento)

### Takeaway
A workable retail stack costs roughly $5–50/mo per VPS region plus $99–$199/mo for real-time US equity data. Prediction-market feeds are free with an account.

### Cited Findings
- Alpaca Algo Trader Plus: $99/month. Full real-time SIP for all US exchanges, real-time OPRA options, unlimited WebSocket symbols, up to 10,000 API requests/min. The free plan is IEX-only. — [Alpaca market data docs](https://docs.alpaca.markets/docs/market-data); [alpaca.markets/data](https://alpaca.markets/data)
- Massive (formerly Polygon) Stocks Advanced: $199/month, individual use only, "real-time stock data, 20+ years of history, websockets". 20% off annual. Business pricing is separate. — [Massive pricing](https://massive.com/pricing)
- Databento: live US equities requires a Standard/Plus/Unlimited subscription. Standard was $199/month as of the Jan 2025 announcement. Subscription prices were updated on 22 Jun 2026 due to higher exchange license fees (new figures not retrieved). Historical data is $/GB. New users get $125 in free credits. — [Databento pricing change Jan 2025](https://databento.com/blog/upcoming-changes-to-pricing-plans-in-january-2025); [Databento subscription update](https://databento.com/blog/updates-to-subscription-pricing); [Databento live data docs](https://databento.com/docs/portal/live-data)
- Vultr: from $5/mo regular, $6/mo high-frequency (review site). — [bestusavps Vultr](https://bestusavps.pages.dev/reviews/vultr)
- Kalshi API, websocket and FIX market data have no listed data fee. Access tiers are volume-based. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits)

### Inferences
- Minimal stack estimate: one VPS in us-east-1 (Coinbase plus Alpaca-adjacent) and one in eu-west-1 (Polymarket int'l, if legally usable) or us-east-2 (Kalshi), at about $10–40/mo for small instances. Add Alpaca SIP at $99, for a total of about $110–180/mo. Adding Databento or Massive brings it to about $300–400/mo. Cloud egress is negligible for websocket clients.
- Bare metal near NJ adds about $100–300+/mo (estimate, no source retrieved) and only helps with direct feeds.

### Gaps
- Current (post-June-2026) Databento prices and AWS/GCP instance prices were not retrieved. Bare-metal NJ pricing is not sourced.

## Q5. Legal/ToS: Polymarket international vs Polymarket US, Kalshi eligibility, state restrictions, automated trading, and the risk of using a VPN

### Takeaway
For a US person, Polymarket international is close-only. Opening positions via VPN breaches its terms and can lead to account freezes or refused withdrawals, with no US regulator to appeal to. It is not clearly a crime for the individual, but it is not a viable basis for a system. The compliant routes are Polymarket US (CFTC DCM, KYC, API with Ed25519 keys) and Kalshi (DCM, API/FIX officially supported). Both are subject to unsettled state-by-state sports-contract litigation. Automated trading is explicitly supported on both regulated venues, within rate limits.

### Cited Findings
- Polymarket's geoblock lists the US under "Regulatory-Restricted Jurisdictions (Close-Only on Frontend and API)": US users can close but not open positions. The page says nothing about VPNs. — [Polymarket geoblock docs](https://docs.polymarket.com/developers/CLOB/geoblock)
- Background: under a January 2022 CFTC settlement, Polymarket paid a penalty and agreed to block US persons. — [allium.so](https://allium.so/blog/is-polymarket-legal-in-the-us-the-state-of-play/) (secondary)
- Secondary sources say Polymarket's terms prohibit VPNs or proxies (one cites §2.1.4, which I could not verify against the primary ToS). They say accounts can be frozen, positions voided and withdrawals refused. From May 2026 Polymarket reportedly blocks known VPN ranges and suspends suspicious accounts. There are no known prosecutions of US individuals for VPN access, and there is "no regulatory body to appeal to" in a dispute. — [CardPlayer: Polymarket cracks down on VPNs](https://www.cardplayer.com/poker-news/1664455-like-post-black-friday-online-poker-sites-polymarket-cracks-down-on-vpns); [KuCoin news: Polymarket tightens KYC and blocks VPN](https://www.kucoin.com/news/flash/polymarket-tightens-kyc-and-blocks-vpn-access-amid-regulatory-pressure); [thesharptake](https://thesharptake.pages.dev/articles/is-polymarket-legal-in-the-us/)
- Polymarket US: QCX LLC (dba Polymarket US) is a CFTC DCM. A November 2025 amended order allows an intermediated model through FCMs. US access began December 2025 via waitlist, and the iOS waitlist was removed in May 2026. — [pm.wiki Polymarket US](https://pm.wiki/uk/projects/polymarket-us); [Cointelegraph](https://regional-front.cointelegraph.com/news/polymarket-cftc-approval-main-platform-us-report); [SBC Americas](https://sbcamericas.com/2026/05/13/polymarket-us-exchange-nationwide-reach/)
- Polymarket US public API (February 2026): REST with 20+ endpoints, streaming feeds, Python/TS SDKs, Ed25519 keypair auth tied to KYC. Official docs (gated) reportedly limit REST to 20 req/s per IP. Docs conflict on WebSocket vs gRPC/Connect streaming. — [DeFi Rate](https://defirate.com/news/polymarket-launches-public-api-unlocks-permissionless-liquidity/); [Polymarket US API docs (gated)](https://apidocs.polymarketexchange.com/api-reference)
- In April 2026 Polymarket asked the CFTC to let US users onto its main international exchange. A CFTC probe was reported in June 2026. There is no approval as of the sources found. — [Bloomberg Law](https://news.bloomberglaw.com/bloomberg-government-news/polymarket-seeks-cftc-blessing-to-bring-main-exchange-back-to-us); [KuCoin/CryptoBriefing](https://www.kucoin.com/news/flash/polymarket-seeks-cftc-approval-to-reopen-to-us-traders)
- Polymarket US state availability (third-party, provisional): "40+ states". Reported unavailable as of mid-2026: AZ, IL, MA, MD, MI, MT, NJ, NV, OH. SSN is required for API users. — [pm.wiki how to use Polymarket in US](https://pm.wiki/hi/learn/how-to-use-polymarket-in-the-us)
- Kalshi state litigation: the 3rd Circuit (April 2026, 2-1) held New Jersey cannot block Kalshi's sports contracts (CEA preemption). The 9th Circuit (Nevada) held unanimously that sports contracts are not swaps and states may enforce gambling law. The 6th Circuit (Ohio/Tennessee, 25 Sep 2026) also sided with the states. That is a circuit split with 20+ suits pending and a possible Supreme Court path. — [The Block](https://www.theblock.co/post/396437/kalshi-wins-appeal-new-jersey-sports-event-contracts); [Courthouse News](https://courthousenews.com/third-circuit-blocks-states-from-regulating-kalshi-prediction-market/); [PYMNTS](https://pymnts.com/legal/2026/a-second-federal-appeals-court-rules-sports-event-contracts-are-not-swaps); [ARY News](https://arynews.tv/us-appeals-court-rules-against-kalshi-says-states-can-regulate-prediction-markets)
- Kalshi API/FIX are first-class products. Tiers are auto-earned (Advanced requires one API order and an upgrade call). FIX retransmission, drop-copy and post-trade ports are gated via institutional@kalshi.com. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits); [Kalshi FIX connectivity](https://docs.kalshi.com/fix/connectivity)
- Alpaca: FINRA approved amendments to Rule 4210 replacing the PDT provisions with an intraday margin framework. Alpaca has removed the PDT rule and the $25k minimum for Trading API users. Alpaca is an API-first broker, so automated trading is its core use case. — [Alpaca blog: FINRA retires PDT rule](https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/)

### Inferences
- A VPN on Polymarket international creates several risks. It breaches ToS (contract risk: frozen funds, voided positions). Polymarket is actively detecting VPNs. Any profits sit on an offshore venue with no US recourse. It also undermines the 1256/capital-loss tax arguments and could look like deliberate evasion of the 2022 CFTC order's geofence. Criminal exposure for the individual appears low (no known cases), but this is not legal advice. Recommendation: do not build a strategy on it. Use Polymarket US or Kalshi. Note that Polymarket US and international have separate order books, so int'l prices can serve only as a read-only signal. Reading public data is not trading, though ToS on scraping should be checked.
- The user's state of residence matters for sports contracts on both Kalshi and Polymarket US, and can change mid-strategy with court rulings.

### Gaps
- I could not retrieve the primary Polymarket international Terms of Use text (VPN clause, freeze clause), the Polymarket US ToS on automated trading, Kalshi's member agreement text on bots, or Alpaca's Customer Agreement clauses on algorithmic trading. All are from secondary sources or inferred.
- The exact effective date of the FINRA PDT replacement, and whether Alpaca paper accounts follow it, are unverified.

## Q6. Market-abuse rules (wash trading, spoofing) and tax treatment of event-contract gains

### Takeaway
On CFTC DCMs (Kalshi, Polymarket US), spoofing, wash trades and pre-arranged trades are illegal under the CEA, and the CFTC named them 2026 enforcement priorities for prediction markets, with possible criminal referrals. A bot that self-crosses or cancels quotes aggressively must be designed to avoid it. Tax treatment is unsettled: there is no IRS guidance. Conservative treatment is ordinary or other income or short-term capital gain. Section 1256 60/40 for Kalshi is an aggressive position, and it is essentially unavailable for Polymarket international.

### Cited Findings
- On 25 Feb 2026 the CFTC Division of Enforcement issued a Prediction Markets Advisory. It covers disruptive trading and spoofing under CEA §4c(a)(5), and wash or pre-arranged noncompetitive trades under §4c(a)(1)/(2)(A) and Reg 1.38(a). DCMs must surveil and prevent these. — [Mondo Visione: CFTC prediction markets advisory](https://mondovisione.com/media-and-resources/news/cftc-enforcement-division-issues-prediction-markets-advisory-2026225); [GT Law](https://www.gtlaw.com/en/insights/2026/4/prediction-markets-a-cftc-enforcement-update)
- 31 Mar 2026: Enforcement Director David Miller listed "spoofing, disruptive trading during a closing period, and wash trading" as priorities and said the CFTC would make criminal referrals where appropriate. — [Akin Gump](https://www.akingump.com/en/insights/alerts/the-cftc-is-watching-enforcement-director-outlines-new-priorities); [Clifford Chance PDF](https://www.cliffordchance.com/content/dam/cliffordchance/briefings/2026/04/CFTC%20Enforcement%20Director%20David%20Miller%20Remarks.pdf)
- An August 2026 CFTC letter warned that prediction-market volume-reward programs could incentivize wash trading. — [GT Law / search summary](https://www.gtlaw.com/en/insights/2026/4/prediction-markets-a-cftc-enforcement-update)
- Tax: no IRS guidance specific to prediction-market contracts as of 2026. Options in use include Schedule 1 "Other Income" (ordinary), Form 8949/Schedule D (mostly short-term), and §1256 60/40 for Kalshi, which is contested and which many practitioners reject. §1256 is "very hard to argue" for Polymarket. Gambling treatment is also debated. Kalshi's 1099s reportedly do not report event-contract trading profits, though one source claims a 1099-MISC over $600. Taxable at settlement, not at withdrawal. — [CoinLedger](https://coinledger.io/blog/prediction-markets-tax); [Awaken Tax: Kalshi](https://awaken.tax/media/article/kalshi-taxes); [Awaken Tax: prediction market taxes](https://awaken.tax/media/article/prediction-market-taxes); [Keeper Tax](https://www.keepertax.com/posts/how-to-file-taxes-on-kalshi-and-polymarket)

### Inferences
- Bot design implications: add a self-trade prevention check (never let your own bid and ask cross), avoid placing orders you intend to cancel before execution to move price (spoofing intent), log cancel reasons, keep order-to-trade ratios sane, and avoid churning for volume rewards or tier upgrades. Kalshi tiers above Advanced are earned on volume share, which creates a wash-trade temptation the CFTC has specifically flagged.
- Tax: keep full per-trade logs (the logging design in Q3 doubles as the tax ledger) because 1099 coverage is incomplete. Budget for ordinary-income rates on net gains unless a CPA signs off on §1256.

### Gaps
- I did not retrieve the primary text of the CFTC advisory or the statute. I found no 2026 enforcement case against a retail prediction-market bot. No IRS notice or ruling exists; a gap in the law, not just in this research.
