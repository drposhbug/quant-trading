# Prediction Market Latency Architecture (Polymarket, Kalshi) — as of Nov 2026

## Q1. Polymarket CLOB design, server location, rate limits, websockets, measured latencies

### Takeaway
Polymarket (international) is a hybrid CLOB: EIP-712-signed orders are matched off-chain by a centralized operator and settled atomically on Polygon. Origin servers are in AWS eu-west-2 (London) behind Cloudflare, and KYC'd traders can co-locate there. IP rate limits are generous: 5,000 POST /order per 10s burst. The binding limit is the per-signer token bucket (40–600 orders/s by volume tier). Network RTT from a nearby EU host is about 1–6 ms, but practitioners report end-to-end signal-to-order times of hundreds of ms, mostly due to client code.

### Cited Findings
**Architecture**
- Orders are EIP-712-signed messages. The signature authorizes the settlement contract to trade without custody. Fields include token ID, side, price, size, expiration, and a millisecond timestamp. The CLOB operator validates signature, balance, allowance, and tick size, then matches. — [Polymarket docs: Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)
- The operator submits matched trades on-chain. Settlement is atomic (transfer, split, or merge of complete sets in pUSD), and finality comes on Polygon. Trade statuses run MATCHED → MINED → CONFIRMED, with RETRYING and FAILED as other states. — [Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)
- Order types are GTC, GTD, FOK, and FAK. FAK was added May 28 2025 and Post-Only on Jan 6 2026. Batch orders went from 5 to 15 per request (Aug 21 2025). — [Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle); [Changelog](https://docs.polymarket.com/changelog.md)
- **CLOB V2** went live Apr 28 2026, with new Exchange contracts, pUSD collateral, fees set at match time, and V1 orders wiped. The Python `py-clob-client` is deprecated in favour of `py-clob-client-v2` (1.2.2, Nov 12 2026) and the Rust `polymarket_client_sdk_v2`. — [Changelog](https://docs.polymarket.com/changelog.md)
- **Async commit pipeline** (rollout Jul 24 2026) "cuts matching latency." POST /order now returns `tradeIDs` instead of `transactionHashes` on FAK/FOK matches, so the API response is decoupled from chain submission. — [Changelog](https://docs.polymarket.com/changelog.md)

**Server location and co-location**
- Docs say: "Primary Servers: eu-west-2. Closest Non-Georestricted Region: eu-west-1." Users who complete a KYC/KYB form can co-locate directly in eu-west-2. This is open to market makers and self-trading individuals only, not to Builder or third-party apps. — [Polymarket docs: Geoblock](https://docs.polymarket.com/api-reference/geoblock.md)
- The UK, US, Germany, France, and others are close-only on both frontend and API. Ireland, Netherlands, Japan, and South Korea are restricted on the frontend only, and the **API is not restricted** there. — [Geoblock](https://docs.polymarket.com/api-reference/geoblock.md)
- The API sits behind the Cloudflare CDN, with origin on AWS eu-west-2. — [Glassnode latency monitor (via search snippet; page unreachable at fetch time)](https://hyperlatency.glassnode.com/prediction-markets/about)
- A practitioner reports p50 latencies to clob.polymarket.com:443 (2026). Amsterdam: ~1.2 ms ping, 1.4 ms TCP, ~6 ms TTFB. Frankfurt: ~16 ms TTFB. London: ~19 ms TTFB. US-East: ~110 ms TTFB. Singapore: ~195 ms TTFB. The author infers an Amsterdam point of presence, which is likely the Cloudflare edge, not the origin. — [dev.to bluewhale-quant-lab](https://dev.to/bluewhale-quant-lab/i-measured-polymarkets-api-latency-from-5-regions-heres-the-script-and-the-results-3mjm); this conflicts with the eu-west-2 origin in [Geoblock docs](https://docs.polymarket.com/api-reference/geoblock.md)
- A VPS vendor (marketing) claims 0.83 ms from Dublin to clob.polymarket.com. — [QuantVPS](https://www.quantvps.com/blog/polymarket-servers-location)
- One bot author measured ~340 ms average from signal to order placement in TypeScript. — [dev.to search snippet](https://dev.to/casatrick/my-polymarket-trading-bot-in-rust-after-typescript-kept-missing-fills-4ena)
- The polyfill-rs benchmark shows market fetch at 321.6 ± 92.9 ms (Rust) versus 1.366 s (official Python client), end-to-end. — [polyfill-rs](https://docs.rs/crate/polyfill-rs/0.2.2)

**Rate limits (IP-based, Cloudflare, sliding windows; requests are throttled/queued rather than rejected)** — [Rate limits](https://docs.polymarket.com/quickstart/introduction/rate-limits)
- CLOB general: 9,000/10s. Market data: /book, /price, and /midpoint 1,500/10s each. Batch /books 500/10s.
- POST /order: 5,000/10s burst, 120,000/10min sustained. DELETE /order is the same.
- POST /orders: 2,000/10s burst, 21,000/10min sustained. DELETE /cancel-all: 250/10s burst.
- History: POST /order was 500/10s burst in May 2025, raised to 5,000/10s in Apr 2026, and the sustained limit rose to 120k/10min on Jun 1 2026. — [Changelog](https://docs.polymarket.com/changelog.md)

**Per-signer token buckets (the real limit)** — [Trading rate limits](https://docs.polymarket.com/api-reference/trading-rate-limits)

| Tier | 30-day volume | Order tokens/s (burst) | Cancel tokens/s (burst) |
|---|---|---|---|
| Standard | — | 40 (60) | 80 (120) |
| Copper | $30k+ | 60 (90) | 120 (180) |
| Bronze | $50k+ | 80 (120) | 160 (240) |
| Silver | $100k+ | 200 (300) | 400 (600) |
| Gold | $500k+ | 400 (600) | 800 (1,200) |
| Platinum | $2.5M+ | 450 (675) | 900 (1,350) |
| Diamond | $5M+ | 525 (787) | 1,050 (1,575) |
| Elite | $10M+ | 600 (900) | 1,200 (1,800) |

- Volume is measured on the maker wallet, and tiers refresh every 3 hours. Response headers are `Poly-RateLimit-Remaining`, `-Reset`, and `-Tier`, plus `Retry-After` on 429. Cancel-all costs 1 + N tokens, and lower tiers can go negative. Warning-mode enforcement started Jul 24 2026.

**Websockets** — [WebSocket overview](https://docs.polymarket.com/market-data/websocket/overview)
- Market channel: `wss://ws-subscriptions-clob.polymarket.com/ws/market`. Messages are `book`, `price_change`, `last_trade_price`, and `tick_size_change`. With `custom_feature_enabled` you also get `best_bid_ask`, `new_market`, and `market_resolved`. The client must send `PING` every 10 s.
- Sports channel: `wss://sports-api.polymarket.com/ws`. The server streams all games and pings every 5 s, and the client must answer `pong` within 10 s. Docs caution that "sports data may be delayed, may contain errors, or may omit recent events."
- PolyBolt reference prices: `wss://ws-live-v2.polymarket.com/ws`, authenticated, launched Sep 15 2026 and replacing legacy RTDS. It carries `price.crypto` (Chainlink default) and `price.equity`, with updates "up to five times per second." — [WS overview](https://docs.polymarket.com/market-data/websocket/overview); [Changelog](https://docs.polymarket.com/changelog.md)
- The 100-token subscription cap on the market channel was removed May 28 2025. — [Changelog](https://docs.polymarket.com/changelog.md)
- The user/order channel is documented on a separate "Real-Time Order Updates" page, which was not retrieved.

### Inferences
- For a lead-lag strategy, a host in AWS eu-west-2 (co-location form) or eu-west-1/Amsterdam gives single-digit-ms network RTT. A US host adds about 90–110 ms. Client stack choice (Python versus Rust) and the venue's own taker delays (Q2) dominate beyond that.
- The Amsterdam ~1 ms figure is most likely the Cloudflare edge. True RTT to the origin matching engine is probably edge-to-London plus processing. *Inferred.*
- At the Standard tier (40 orders/s), any multi-market quoting strategy will hit the per-signer bucket long before the IP limits.

### Gaps
- No official matching-engine latency, p99 order acknowledgement time, or websocket publish latency is published. The Glassnode monitor page was unreachable (DNS failure) during research.
- The user channel spec, connection and subscription caps per websocket, and an official cancel-on-disconnect/heartbeat spec were not found. Only the third-party Rust SDK README mentions heartbeats that cancel all orders on disconnect ([polymarket-client-sdk](https://docs.rs/crate/polymarket-client-sdk/0.4.3/source/README.md)).

## Q2. Taker delays / speed bumps (sports and crypto)

### Takeaway
Yes, Polymarket deliberately delays marketable (taker) orders. Crypto and finance up/down markets get a short delay, which is 150 ms since Sep 4 2026 (previously 250 → 50 → 150 ms). Configured live sports markets get a seconds-scale delay: historically 3 s, now 1 s on some leagues and varying by market. Delayed orders are uncancellable and are re-validated at expiry. These are explicit anti-latency-arbitrage measures.

### Cited Findings
- Crypto and finance up/down markets: the order is held, re-validated, then matched or rested. The API blocks until the final result. The docs page states 250 ms, and whether a market has the delay is flagged on `GET /clob-markets/{condition_id}`. — [Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)
- The changelog records the crypto taker delay cut from 250 ms to 50 ms on Aug 17 2026, then raised to 150 ms on Sep 4 2026. **The current value is therefore 150 ms**, and the order-lifecycle page's 250 ms looks stale. — [Changelog](https://docs.polymarket.com/changelog.md)
- Sports: "Applies to configured sports markets around live game conditions." The order waits for the market's configured delay window and has status `delayed`. It **cannot be cancelled** during the window and is rejected if market, balance, allowance, or risk checks fail at expiry. — [Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)
- The help centre (dated Apr 20 2026) says: "sports markets include a 3-second delay on the placement of marketable orders" and "A 1-second taker delay is currently being tested on NBA and MLB markets." — [Polymarket Help: Limit orders](https://intercom.help/polymarket/en/articles/13364444-limit-orders)
- A third-party check on Oct 27 2026 found Premier League markets at 1 s and NBA markets at no delay. Per-market configuration changes. — [startpolymarket in-play guide (search snippet)](https://startpolymarket.com/strategies/in-play-trading/)
- Makers (resting, post-only) are not delayed. Only marketable orders are. — [Order lifecycle](https://docs.polymarket.com/concepts/order-lifecycle)

### Inferences
- Asymmetric speed bump: resting makers can still cancel instantly while takers wait 150 ms (crypto) or about 1–3 s (sports). Stale-quote sniping by takers is therefore heavily penalised. A lead-lag edge on Polymarket has to come from fast *cancel/requote* as a maker, not from taking. *Inferred.*
- Combined with crypto taker fees (Q4), this probably explains why the classic Binance→Polymarket 15-min "latency arb" became much harder after Jan 2026. *Inferred.*

### Gaps
- No minimum-resting-time rule for makers was found. There is no authoritative list of which sports markets carry delays or their current lengths. Query the market endpoint per market.

## Q3. Kalshi: API tiers, FIX, co-location-like options, rate limits

### Takeaway
Kalshi is a fully centralized CFTC DCM. It offers REST, WebSocket, and FIX 5.0SP2 (TLS) on a shared token-bucket budget, with seven tiers by trailing 30-day volume share (Basic 100 write-tokens/s up to Prestige 9,600). AWS PrivateLink (Premier+) and VPC peering (Prime+) are the closest thing to co-location. The origin is reportedly AWS us-east-2 (Ohio), via third party.

### Cited Findings
- Tiers are Basic, Advanced, Expert, Premier, Paragon, Prime, and Prestige. Expert and above are earned on 30-day volume share (Earn/Keep): Expert 0.075%/0.05%, Premier 0.125%/0.10%, Paragon 0.25%/0.20%, Prime 0.50%/0.40%, Prestige 1.00%/0.80%. Advanced is self-upgraded via API after placing an API order. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits)
- Predictions budgets in tokens/s (Read/Write): Basic 200/100, Advanced 300/300, Expert 600/600, Premier 1,200/1,200, Paragon 2,400/2,400, Prime 4,800/4,800, Prestige 12,000/9,600. A default request costs 10 tokens, so Basic is about 10 order writes/s. Batch create costs 10 per order and batch cancel 2 per order. FIX Order Cancel costs 1 token. Write buckets above Basic hold 3 s of budget. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits)
- Concurrent websocket connections: 200 (Basic–Expert), 500 Premier, 750 Paragon, 1,000 Prime and Prestige. — [Kalshi rate limits](https://docs.kalshi.com/getting_started/rate_limits)
- FIX (FIXT.1.1/FIX50SP2, TLS 1.2+, one connection per API key) production hosts are `mm.fix.elections.kalshi.com` (order entry) and `marketdata.fix.elections.kalshi.com`. Sessions are NR order entry (8228), RT with retransmission (8230), Drop Copy (8229), Post Trade (8231), RFQ (8232), and Market Data (8233). RT, DC, and PT require contacting institutional@kalshi.com. Mass cancel is limited to 1/s. — [Kalshi FIX connectivity](https://docs.kalshi.com/fix/connectivity)
- **AWS PrivateLink requires Premier tier or above, and VPC peering requires Prime or above.** — [Kalshi FIX connectivity](https://docs.kalshi.com/fix/connectivity)
- Origin is reported as AWS us-east-2 (Ohio) behind CloudFront. — [Glassnode (search snippet)](https://hyperlatency.glassnode.com/prediction-markets/about). A VPS vendor claims 1.14 ms RTT from Chicago (Feb 2026) and infers Chicago hosting. — [QuantVPS](https://www.quantvps.com/blog/kalshi-servers-location). These conflict. Ohio fits sub-few-ms Chicago RTT, but 1.14 ms is tight for Chicago–Ohio (~400 km). It could be the CloudFront edge.
- The legacy tier system (Advanced 30 TPS write, Premier 100 TPS write) is superseded. — [old readme.io](https://trading-api.readme.io/reference/tiers-and-rate-limits)

### Inferences
- PrivateLink or VPC peering into Kalshi's AWS VPC implies Kalshi runs in AWS, with us-east-2 most likely. A trader in the same region via PrivateLink would bypass CloudFront. *Inferred.*
- No taker speed bump on Kalshi was found, in contrast to Polymarket.

### Gaps
- No official Kalshi region disclosure, matching-engine latency, or websocket publish latency was found. Whether Kalshi has any sports-market order delay was not established.

## Q4. Fees (Polymarket, Kalshi)

### Takeaway
Both use a p(1−p) parabolic taker fee. Polymarket charges `fee = C × rate × p × (1−p)`, with the rate by category (crypto 0.07, sports 0.05, politics/finance 0.04, geopolitics 0). Makers pay nothing and receive 15–25% rebates. Kalshi's standard taker fee is `ceil(0.07 × C × p × (1−p))`, and a maker fee of 0.0175 applies on designated series. A new Polymarket fee and rebate schedule takes effect Nov 20 2026 23:59 UTC, which is today.

### Cited Findings
- Polymarket rates by category (taker / maker rebate): Crypto 0.07/20%, Sports 0.05/15%, Finance 0.04/25%, Politics 0.04/25%, Economics, Culture, Weather, and Other 0.05/25%, Mentions and Tech 0.04/25%, Geopolitics 0, Combos 0.05/0%. "Makers are never charged fees." Fees are set at match time. — [Polymarket fees](https://docs.polymarket.com/trading/fees)
- At p = 0.5, the peak crypto taker fee is $0.0175 per share (0.07 × 0.25). That is $1.75 per 100 shares, or 3.5% of the $0.50 premium per side. — [Polymarket fees](https://docs.polymarket.com/trading/fees)
- Timeline: 15-min crypto taker fees from Jan 5 2026 (peak 1.56%), 5-min crypto markets from Feb 12 2026, all crypto markets from Mar 6 2026, Fee Structure V2 by category on Mar 30 2026, and the sports coefficient raised from 0.03 to 0.05 (rebate from 25% to 15%) on Jul 10 2026. On Nov 20 2026 23:59 UTC, maker rebates move to volume tiers of 3/7/10/15%, and taker rebate tiers change (Obsidian 50%, new Onyx 60%). — [Changelog](https://docs.polymarket.com/changelog.md)
- Kalshi taker fee is round-up(0.07 × contracts × P × (1−P)). Maker fee is 0.0175 multiplier only on series listed with maker fees. Sources conflict on the effective date (Feb 5 2026 vs Jul 7 2026). — [Kalshi fee schedule PDF](https://kalshi.com/docs/kalshi-fee-schedule.pdf); [secondary summaries](https://www.predictionhunt.com/blog/kalshi-fees-complete-guide-2026)

### Inferences
- At p = 0.5, a taker round trip costs about 3.5¢ per $1 contract on both Polymarket crypto (0.07) and Kalshi standard (0.07, rounded up). That is about 7% of the premium, before spread. Polymarket sports (0.05) costs about 2.5¢. Lead-lag taker signals must move price by several cents to clear costs. Maker-side strategies are structurally favoured on both venues. *Inferred from formulas.*

### Gaps
- Exact post-Nov-20-2026 Polymarket rebate tier thresholds were not retrieved. The official Kalshi fee PDF was not fetched directly, so its current version is unverified.

## Q5. Settlement/resolution timing and Polymarket US vs international

### Takeaway
Polymarket international resolves via the UMA Optimistic Oracle, with a ~2 h liveness window if undisputed, and about 2–4 extra days if disputed and sent to the DVM vote. Kalshi settles centrally. Polymarket US (operated via QCEX, the CFTC-designated venue) is a separate, conventionally centralized exchange. It has its own REST/FIX API (apidocs.polymarketexchange.com), Ed25519 keys, and price-time priority CLOB, and its keys do not work on the international CLOB.

### Cited Findings
- UMA liveness is ~2 h on Polymarket. Most markets resolve undisputed at liveness expiry, and disputes take 48–96 h. — [startpolymarket: how markets resolve](https://startpolymarket.com/learn/how-markets-resolve/); [UMA FAQ: DVM resolves in 2–4 days, liveness configurable 2 h–2 days](https://docs.uma.xyz/faqs). One guide says 24–48 h ([pm.wiki](https://pm.wiki/uk/learn/how-prediction-markets-resolve)), an outlier.
- Intra-trade settlement: off-chain match then Polygon settlement. The Jul 2026 async commit means fills are acknowledged before the chain transaction. — [Changelog](https://docs.polymarket.com/changelog.md)
- Polymarket US docs at apidocs.polymarketexchange.com describe a continuous CLOB with price-time priority, FIX NewOrderSingle order entry, separate order-management and market-data FIX gateways, and static IP allowlisting via fix@qcex.com. — [Polymarket US FIX order entry (search snippet)](https://apidocs.polymarketexchange.com/api-reference/fix-api/fix-order-entry-and-matching). The FIX overview page is behind a partner access code. — [FIX overview](https://apidocs.polymarketexchange.com/api-reference/fix-api/fix-overview)
- US keys come from polymarket.us/developer after KYC, are Ed25519-signed, and are separate from the polymarket.com CLOB. A secondary source puts the US Retail API at 23 REST and 2 WS endpoints. — [Dwellir guide](https://www.dwellir.com/guides/polymarket-api-guide)
- The US exchange opened nationwide to iOS users in May 2026. — [SBC Americas](https://sbcamericas.com/2026/05/13/polymarket-us-exchange-nationwide-reach/)

### Inferences
- For capital turnover, Polymarket international locks capital for at least ~2 h after event end, plus days on dispute. Positions can be exited earlier by selling on the book. *Inferred.*
- Polymarket US is likely hosted in a US region, not eu-west-2, so it is a separate latency venue from the international book. *Unverified inference.* The US and international books are not shared liquidity.

### Gaps
- Polymarket US server region, rate limits, fees, and any taker delays were not found (partner docs gated). Kalshi settlement timing after outcome determination was not documented in the sources reviewed.
