# Prediction markets (Polymarket, Kalshi) as signals for US equities: TSLA, SPCX, mega-cap tech (as of 2026-11-18)

> Method note: I could NOT call the Polymarket or Kalshi APIs live. From this machine, gamma-api.polymarket.com, clob.polymarket.com, docs.polymarket.com and api.elections.kalshi.com all failed with TLS "connection reset" (curl and WebFetch), while example.com worked. That looks like a network or ISP block, not an API fault. A sandbox bypass was denied. So every endpoint detail below comes from the docs and from third-party developer write-ups found by search. Test each URL yourself before you build on it. Odds snapshots come from news and aggregator pages, and the date is given where one was known.

## 1. Evidence (2020-2026) that prediction-market prices lead stock and index returns

### Takeaway
The best evidence for a lead is from the 2024 election. A 1pp rise in Polymarket's Trump-win probability went with about 13bp of NEXT-DAY return on a 34-asset "Trump trade" basket (Goldstein, Li and Wang, as summarized by a blog). On index-level questions such as "S&P closes above X", prediction markets mostly track same-day options and add little. The edge is in questions options cannot price: Fed and CPI distributions, earnings beats, and discrete corporate events. I found no rigorous study of TSLA, SPCX or a single mega-cap stock.

### Cited Findings
- **Election lead-lag (the strongest equity result):** Goldstein, Li and Wang regress next-day returns of a 34-asset Trump-trade basket on daily changes in Polymarket's Trump-YES probability, over roughly Jan-Nov 2024. The basket covers equity ETFs, bond ETFs, 6 bank stocks, FX, commodities and 3 "Connected" names such as DJT. Results: about **13bp next-day return per +1pp** of probability, and a simple long-short strategy with a **Sharpe of about 2**. To handle reverse causality, they show that price impact from uninformed Polymarket trades also spreads to traditional markets "before partially reversing". Caveats: the basket was picked from media narratives, the Connected leg is driven by DJT, and the source I read is a blog summary dated 2026-08-14, not the paper. I could not get the paper's title or venue. — [Alpha in Academia, "The Odds Lead the Tape"](https://www.alphainacademia.com/p/the-odds-lead-the-tape)
- **Cross-platform price discovery:** Ng, Peng, Tao and Zhou (SSRN, first posted Jul 2025, revised Apr 2026) study Polymarket, Kalshi, PredictIt and Robinhood around the 2024 election. Polymarket **leads Kalshi** in price discovery, most of all when liquidity is high. Liquid markets beat polls. **Net order imbalance from large trades strongly predicts subsequent (contract) returns.** — [SSRN 5331995](https://papers.ssrn.com/abstract=5331995)
- **Global equity reactions to 2024 election probabilities:** an event study and panel regressions across 40+ stock indexes, using high-frequency prediction-market data. Developed APAC and European markets react moderately, and emerging markets such as Mexico react strongly. — [SSRN 5238389](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5238389); [MDPI JRFM version](https://www.mdpi.com/1911-8074/19/3/191)
- **Options tracked the election odds as well:** option-implied measures, including DJT's stock price, tracked Trump's odds in 2024. Unlike 2016, there was no post-result reversal of the "Trump trade". — [UCSD forecasting paper](https://pages.ucsd.edu/~ssaiegh/forecast_2024.pdf)
- **Macro, Fed and CPI (Kalshi):** Diercks (Fed Board), Katz and Wright, "Kalshi and the Rise of Macro Markets", FEDS WP 2026-010 / NBER w34702. It uses data from 2022 onward and compares Kalshi with Fed funds futures, Bloomberg surveys and Blue Chip forecasts. Kalshi gives the full distribution of the post-FOMC rate directly, while futures need adjusting. Its fed-funds error at 150 days ahead is "very close" to that of futures. A secondary summary claims "statistically significant improvements" for fed funds and CPI, but the paper's own wording is more cautious. This is a forecast-accuracy paper, not a stock lead-lag paper. — [FEDS PDF](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf); [NBER w34702](https://www.nber.org/papers/w34702); stronger claim in [DeFi Rate](https://defirate.com/news/federal-reserve-study-finds-kalshi-markets-rival-traditional-economic-forecast-tools/)
- **Earnings-beat markets (single stocks):** Gómez-Cram, Guo, Kung (LBS) and Jensen (Yale), "Financial Prediction Markets: A New Measure of Earnings Expectations". Polymarket "beat EPS" contracts were about **68% accurate one week before** earnings and **77% the day before**, against about **62% for analysts**. Sample window: 15 Sep to 15 Nov 2025. I could not verify their stock-reaction results. — [InGame summary](https://www.ingame.com/kalshi-polymarket-prediction-studies/); Brier score of 0.152 cited in [Zhang, "What Do Earnings Prediction Markets Know?"](https://afajof.org/management/viewp.php?n=271488)
- **Only a small informed minority sets prices:** the same group finds that about 3% of traders drive Polymarket's accuracy. — [SSRN 6617059](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6617059); [CoinDesk, 2026-04-26](https://www.coindesk.com/markets/2026/04/26/only-3-of-traders-drive-prediction-markets-accuracy-not-the-crowd-study-finds)
- **Index-level markets add no edge over options (vendor analysis, not peer-reviewed):** Tradytics reviewed an archive of 5.95M Kalshi and Polymarket markets. Odds on S&P and Nasdaq closes match same-day options: strikes differ by 4-6 points on average, and the implied close range is 1.01-1.03x the options range. Daily "S&P up or down" markets picked the right side **56%** of the time, which is about the base rate of up days. Stocks rose after 54.6% of earnings beats and 36.5% of misses. Problems: no sample period, no significance tests, a commercial conflict of interest, and an internal contradiction about the 56%. Updated 2026-11-05. — [Tradytics](https://tradytics.com/learn/does-polymarket-predict-the-stock-market)

### Inferences
- The lead most likely shows up where the contract prices a **discrete binary event that no listed derivative prices directly**: elections, a merger announcement, an earnings beat, a tariff deal. Where options or futures exist (index levels, the Fed path), arbitrage ties the prediction market to them and any lead is small.
- The Goldstein et al. effect partly reverses. That suggests part of the "signal" is price-pressure contagion, not information, so a strategy should expect some giveback.
- For TSLA and SPCX, the best candidate signal is a Musk-event market such as the Tesla-SpaceX merger market. Its price moves before the news reaches the equity tape on weekends and after hours. This is untested.

### Gaps
- I found no peer-reviewed lead-lag study on TSLA, SPCX, NVDA or any single mega-cap, and none on tariff or recession markets versus equities.
- I could not read the Goldstein, Li and Wang paper itself. The magnitudes come from a blog summary.
- I could not verify the Gómez-Cram et al. results on post-earnings stock reactions.

## 2. Which Polymarket and Kalshi markets matter for these tickers

### Takeaway
Relevant markets fall into four groups: (a) Musk and Tesla/SpaceX corporate events, chiefly the **Tesla-SpaceX merger announcement** market; (b) the **"Largest company end of <month> 2026"** market-cap race for NVDA, AAPL, MSFT and GOOGL; (c) macro markets: FOMC decision and "how many cuts in 2026", plus S&P daily up/down and level markets; (d) per-company **earnings-beat** markets. All odds below are dated snapshots, and several conflict.

### Cited Findings
- **Tesla-SpaceX merger:** Polymarket has markets for an official announcement "by Dec 31, 2026" and "by Dec 31, 2027". Snapshot of Nov 16, 2026: about 27.5% for 2026 and about 88% for 2027. Musk said on Oct 20, 2026 that both companies had formed special committees. Earlier readings: Benzinga (Oct 2026) had 15% for Dec 2026 and 63% for end-2027 on about $1.56M volume. 24/7 Wall St (Oct 5, 2026) had 62.5% for 2027, and in early Sep 2026 it reported the market near 50%. Across articles, the 2026-deadline odds have ranged from about 15% to 38%. — [Benzinga (SPCX tag)](https://www.benzinga.com/markets/prediction-markets/26/10/62605726/tesla-spacex-merger); [24/7 Wall St Oct](https://247wallst.com/investing/2026/10/05/tesla-is-down-16-this-year-and-bettors-now-favor-a-musk-merger-with-spacex/); [24/7 Wall St Sep](https://247wallst.com/investing/2026/09/04/tesla-just-put-driverless-cybercabs-on-austin-streets-but-bettors-are-pricing-a-spacex-merger-at-nearly-50/); [Market Periodical, Oct 21](https://themarketperiodical.com/2026/10/21/spacex-stock-on-edge/); [Yahoo, 18% odds](https://finance.yahoo.com/markets/stocks/articles/polymarket-gives-18-odds-tesla-225026188.html); [Forbes, May 27, 2026](https://www.forbes.com/sites/tylerroush/2026/05/27/could-musk-merge-spacex-and-tesla-heres-what-analysts-and-betting-markets-say/)
- The context articles also mention a Polymarket market on "Tesla releases Optimus by Dec 31, 2026" (about 3.6%). Forbes reports that SpaceX acquired xAI in Feb 2026, so SpaceX-xAI merger markets are stale. — same sources as above
- **Market-cap race:** "Largest Company end of November 2026" and "end of December 2026" (outcomes include NVIDIA, Apple, Microsoft, Alphabet and Saudi Aramco). The readings conflict: one Polymarket page (about Nov 13) shows **Apple 89%, NVIDIA 10%**; an aggregator on Nov 5 shows Apple 60%, NVIDIA 38%, MSFT 2%; earlier snapshots show NVIDIA 54-73%; Lines.com (undated) shows NVIDIA 82%. Apple reportedly overtook NVIDIA around July 2026, and the lead has changed hands more than once. — [Polymarket Dec-2026 event](https://polymarket.com/event/largest-company-end-of-december-2026); [Polymarket Nov-2026 event](https://polymarket.com/event/largest-company-end-of-november-2026); [predictmarketcap](https://predictmarketcap.com/events/largest-company-end-of-december-2026); [Lines.com](https://www.lines.com/prediction-markets/economy/largest-company-end-of-october-2026); [CryptoBriefing](https://cryptobriefing.com/nvidia-polymarket-apple-market-cap-race/)
- **Fed:** Polymarket's "How many Fed rate cuts in 2026?" showed zero cuts at about 97-99% in recent snapshots. It was 43% in April (Forbes, Apr 13, 2026) and about 88.8% in August. An aggregator reports that Kalshi priced the Dec 8-9, 2026 FOMC at **hike 95% / hold 6% / cut 1%** (Nov 17). That reading is unusual and comes from a third party; check it on Kalshi (series KXFED / KXFEDDECISION). — [Polymarket event](https://polymarket.com/event/how-many-fed-rate-cuts-in-2026); [Forbes](https://www.forbes.com/sites/digital-assets/2026/04/13/no-cuts-polymarket-bettors-dump-fed-rate-cut-hopes/); [Blockchain.News](https://blockchain.news/news/polymarket-sees-84-odds-of-zero-fed-cuts-in-2026-after-risk-off-swing-0hnn97216oc00); [CNBC prediction markets hub](https://www.cnbc.com/markets/prediction-markets/)
- **Equity index markets:** Polymarket runs a daily "S&P 500 Up or Down" (open) contract, which Benzinga writes up every day. Volumes can be small, for example $9,246 in one session. Kalshi has "How high will the S&P get this year" (KXINXMAXY) and daily SPY close-above ladders. — [Benzinga example](https://www.benzinga.com/markets/prediction-markets/26/11/63330216/stock-market-will-sp-500-open-up-or-down-today-79); [Kalshi KXINXMAXY](https://kalshi.com/markets/kxinxmaxy/sp-500-max-yearly/kxinxmaxy-01jan2027)
- **Category pages** for finding markets: Polymarket [Fed](https://polymarket.com/predictions/fed) and [Economic Policy](https://polymarket.com/predictions/economic-policy). Shutdown, tariff and recession markets also exist as categories, but I found no figures I could cite. — [coinstats aggregator](https://coinstats.app/prediction-markets/odds/)

### Inferences
- **TSLA and SPCX:** the merger market is the single most relevant contract. A jump in it should move SPCX and TSLA in opposite or same directions depending on the implied exchange ratio. That relationship is untested; build the pair from the price history and look for lead-lag on weekend and after-hours jumps.
- **Mega-caps:** the "largest company" market is mostly a derivative of the stock prices themselves, because it resolves on market cap. Expect it to LAG or move with the stocks, not lead them. Earnings-beat markets for NVDA, AAPL, MSFT, GOOGL, AMZN and META are better candidates for information.
- **Macro:** Fed and CPI markets help as a clean, directly read distribution to use as a regime feature. They are unlikely to lead Fed funds futures by much.

### Gaps
- I have no verified live list of current tariff, China, recession, shutdown, robotaxi, Starship or AI-race markets with their slugs and volumes. That needs a live Gamma `public-search` call.
- I found no dedicated Polymarket market on SPCX price levels or index inclusion.

## 3. How to pull historical and live data for free

### Takeaway
All read access is free and needs **no API key**. Polymarket: use Gamma (`gamma-api.polymarket.com`) to find markets and their `clobTokenIds`, then call CLOB `GET /prices-history?market=<token_id>` for the time series. Kalshi: use REST v2 (`api.elections.kalshi.com/trade-api/v2` or `external-api.kalshi.com/trade-api/v2`) for markets and candlesticks, which need no auth. Its WebSocket needs a key. The biggest gotcha is history depth: Polymarket's fine-grained history goes back only about 30 days, and explicit windows are capped at 15 days.

### Cited Findings
**Polymarket: endpoints and parameters**
- Gamma base URL: `https://gamma-api.polymarket.com`. It has events and markets list endpoints, `/events/slug/{slug}` and `/markets/slug/{slug}`, a `tag_id` filter, and keyset pagination (`after_cursor`; `offset` is rejected on the keyset variant). On market objects, `clobTokenIds` is a **JSON-encoded string** of token IDs, so parse it twice. — [List events docs](https://docs.polymarket.com/api-reference/events/list-events); [Get event by slug](https://docs.polymarket.com/cn/api-reference/endpoints/gamma/get-events-slug-slug); [keyset markets](https://docs.polymarket.com/api-reference/markets/list-markets-keyset-pagination)
- CLOB price history: `GET https://clob.polymarket.com/prices-history`. Parameters: `market` (a CLOB **token ID**, not the market ID), and either `interval` (`1h`, `6h`, `1d`, `1w`, `1m`, `max`, where `1m` = one month) or `startTs`/`endTs` (Unix seconds), plus `fidelity` (bucket size in minutes, default 1). Response: `{"history":[{"t":<unix>,"p":<price>}, ...]}`. — [Polymarket docs: Get prices history](https://docs.polymarket.com/api-reference/markets/get-prices-history); [Orderbook guide](https://docs.polymarket.com/trading/orderbook)
- **History depth (tested by one developer on 2026-10-24):** with `interval=max`, fidelity 1-719 returns only **about 30 days**; fidelity **720 or 1440 returns the full history** (462 days back to the market's start). Explicit `startTs/endTs` windows longer than **15 days** fail with `{"error":"invalid filters: 'startTs' and 'endTs' interval is too long"}`. Long windows at fine granularity therefore have to be stitched from 15-day chunks, and that may still be limited by retention. Reported pitfalls: `interval=max` at fine fidelity can come back as an **empty array without an error**; `1w` needs fidelity of 5 or more and `1m` needs 10 or more. — [dev.to (2026-10-24)](https://dev.to/matveyg/i-asked-polymarket-for-90-days-of-prices-and-got-30-coarser-points-got-me-462-577k); [Predictefy tutorial](https://blog.predictefy.com/polymarket-api-python); [AlphaScope guide](https://www.alphascope.app/blog/polymarket-historical-data)
- A separate Data API route, `data-api.polymarket.com/v2/prices-history`, uses different parameter names (`token_id`, `interval` or `start`/`end`). Do not mix the two routes. — [Polymarket docs (via search summary)](https://docs.polymarket.com/api-reference/markets/get-prices-history)
- **Rate limits (official):** Gamma allows 4,000 requests per 10s in general and **350 per 10s on `/public-search`**. CLOB allows 9,000 per 10s in general. Cloudflare enforces limits **per IP** and **throttles (queues) instead of rejecting**. Reads need no key. — [Polymarket Rate Limits](https://docs.polymarket.com/api-reference/rate-limits)
- Paid tick and order-book history (250ms books) exists if you need more than ~30 days at fine granularity. — [polyorderbooks](https://polyorderbooks.com/polymarket-historical-data); [launchpoly free sources](https://launchpoly.com/blog/kalshi-polymarket-historical-data)

**Example URLs for Polymarket (built from the docs; NOT live-tested here, see the method note):**
```
# 1. Find markets by keyword
https://gamma-api.polymarket.com/public-search?q=tesla%20spacex%20merger
# 2. Get an event and its markets (slug taken from the polymarket.com/event/<slug> URL)
https://gamma-api.polymarket.com/events/slug/largest-company-end-of-december-2026
https://gamma-api.polymarket.com/events/slug/how-many-fed-rate-cuts-in-2026
# 3. Active markets ranked by volume
https://gamma-api.polymarket.com/markets?active=true&closed=false&order=volume24hr&ascending=false&limit=50
# 4. Full-history daily series for one outcome token (take the YES id from clobTokenIds[0])
https://clob.polymarket.com/prices-history?market=<YES_TOKEN_ID>&interval=max&fidelity=1440
# 5. Last ~30 days at 1-minute resolution (or use startTs/endTs chunks of 15 days or less)
https://clob.polymarket.com/prices-history?market=<YES_TOKEN_ID>&interval=max&fidelity=1
https://clob.polymarket.com/prices-history?market=<YES_TOKEN_ID>&startTs=1761955200&endTs=1763164800&fidelity=60
# Live top of book / midpoint
https://clob.polymarket.com/midpoint?token_id=<YES_TOKEN_ID>
https://clob.polymarket.com/book?token_id=<YES_TOKEN_ID>
```
(`midpoint` and `book` are standard CLOB read endpoints that I know from the docs. I could not re-verify them this session.)

**Kalshi**
- Public REST endpoints need **no account or key**: series, events, markets, public trades and candlesticks. **The WebSocket needs API-key auth even for public channels.** — [Predictefy Kalshi guide](https://blog.predictefy.com/kalshi-api-guide); [Kalshi docs: Get Market Candlesticks](https://docs.kalshi.com/api-reference/market/get-market-candlesticks)
- Candlestick routes: `GET /series/{series_ticker}/markets/{ticker}/candlesticks`, the event-level `GET /series/{series_ticker}/events/{ticker}/candlesticks`, and the batch `GET /markets/candlesticks` (up to 100 tickers and 10,000 candles per call). Periods are 1 (min), 60 (hour) and 1440 (day). Markets that settled **before the historical cutoff** must be read from `GET /historical/markets/{ticker}/candlesticks`. Call `GET /historical/cutoff` on every run instead of hardcoding the cutoff. — [Kalshi historical candlesticks](https://docs.kalshi.com/api-reference/historical/get-historical-market-candlesticks); [Get Historical Cutoff](https://docs.kalshi.com/api-reference/historical/get-historical-cutoff-timestamps); [Kalshi changelog](https://docs.kalshi.com/changelog)
- Base URLs: the docs' samples use `https://external-api.kalshi.com/trade-api/v2`, and `https://api.elections.kalshi.com/trade-api/v2` is listed as also supported and serves all markets, not only elections. — [Get Historical Cutoff](https://docs.kalshi.com/api-reference/historical/get-historical-cutoff-timestamps); [Kalshi historical API spec mirror](https://apis.io/apis/kalshi/kalshi-historical-api/)
- Rate limits: a third-party source gives the Basic tier as 200 read and 100 write tokens per second, with most calls costing 10. No separate unauthenticated limit is published. — [Predictefy](https://blog.predictefy.com/kalshi-api-guide); [predictionhero](https://predictionhero.com/insights/kalshi-api-guide)

**Example URLs for Kalshi (NOT live-tested here):**
```
https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXFED&status=open&limit=100
https://api.elections.kalshi.com/trade-api/v2/events?series_ticker=KXINXMAXY
https://api.elections.kalshi.com/trade-api/v2/series/KXFED/markets/<MARKET_TICKER>/candlesticks?start_ts=<unix>&end_ts=<unix>&period_interval=60
https://api.elections.kalshi.com/trade-api/v2/historical/cutoff
https://api.elections.kalshi.com/trade-api/v2/markets/trades?ticker=<MARKET_TICKER>&limit=1000
```
(The candlestick parameter names `start_ts`, `end_ts` and `period_interval` are from my knowledge of the docs, not from a page I fetched this session.)

### Inferences
- Pipeline: (1) pick the markets once with Gamma `public-search`; (2) every day, pull `fidelity=1440, interval=max` for the full daily history; (3) archive `fidelity=1` every day going forward, because minute data older than about 30 days is lost; (4) align the series to NYSE closes, and take Friday-close to Monday-open separately.
- Use the YES token's price as the probability. Check that the YES and NO prices sum to about 1, and filter out bars with no trades. Thin markets print stale prices.

### Gaps
- I could not run any live test, because outbound connections to Polymarket and Kalshi domains were reset on this machine. All URLs need a smoke test from a network that can reach them.
- I could not confirm `closed=true` filtering on Gamma `/markets` from the docs. It is widely used in examples.

## 4. Practical pitfalls: liquidity, manipulation, resolution, and 24/7 trading against market hours

### Takeaway
Treat prediction-market prices as noisy, sometimes manipulated, and liquidity-dependent. Weight by volume and depth, prefer large-trade order flow, and expect partial reversals. The 24/7 trading gives a real weekend and after-hours information window, but I found no study that validates it as a Monday-open signal.

### Cited Findings
- **Thin liquidity and whales:** in Polymarket's 2024 election markets, early thin depth meant high price impact, wide arbitrage gaps, and room for whales to distort prices. Efficiency improved as participation broadened. After the Sep 10 debate, odds moved from 53-46 to about 50-50 within hours. — [arXiv 2603.03136](https://arxiv.org/html/2603.03136v2)
- **Wash trading:** a Columbia study ("Network-Based Detection of Wash Trading") estimates that about **25% of Polymarket's historical volume is artificial**. It peaked at about 60% in Dec 2024, fell below 5% in May 2025, and was back near 20% when reported (late 2025). 14% of 1.26M wallets were flagged, and sports markets were hit hardest at 45%. The likely motive is airdrop farming. Reported in press coverage; I did not read the paper. — [Gizmodo](https://gizmodo.com/study-finds-around-a-quarter-of-polymarket-trades-are-fake-2000683231); [Yahoo Finance](https://finance.yahoo.com/news/25-polymarket-trading-volume-may-203104855.html)
- **Who sets prices:** about 3% of traders drive accuracy, and most others lose money. Large-trade imbalance predicts returns. — [CoinDesk](https://www.coindesk.com/markets/2026/04/26/only-3-of-traders-drive-prediction-markets-accuracy-not-the-crowd-study-finds); [SSRN 5331995](https://papers.ssrn.com/abstract=5331995)
- **Cross-venue gaps:** prices differ a lot between Polymarket and Kalshi on the same event. Polymarket tends to lead. — [SSRN 5331995](https://papers.ssrn.com/abstract=5331995)
- **Partial reversal:** price impact from uninformed trades reaches traditional assets, then partially reverses. — [Alpha in Academia](https://www.alphainacademia.com/p/the-odds-lead-the-tape)
- **Weekend / Monday signal:** Benzinga and Yahoo publish Polymarket's daily "S&P 500 open up or down" odds next to futures. One example: Nov 16, 2026, 38% chance of a higher open, which resolved "Down". These are descriptive, often low-volume (about $9k), and nobody has tested them as a forecast. Tradytics finds that daily up/down calls are right 56% of the time, roughly the base rate. — [Benzinga](https://www.benzinga.com/markets/prediction-markets/26/11/63330216/stock-market-will-sp-500-open-up-or-down-today-79); [Tradytics](https://tradytics.com/learn/does-polymarket-predict-the-stock-market) **(anecdotal or vendor evidence)**
- **Correlation vs causation:** on risk-off days, Fed "zero cuts" odds and stock selloffs move together. That shows both reacting to the same news, not a lead. — [Blockchain.News](https://blockchain.news/news/polymarket-sees-84-odds-of-zero-fed-cuts-in-2026-after-risk-off-swing-0hnn97216oc00) **(anecdotal)**

### Inferences
- **Resolution mechanics:** prices converge to 0 or 1 near expiry, and time decay dominates for deadline markets ("by Dec 31"). Use the change in the logit, or adjust for the time left. Do not use the raw price level. Watch out for rolling deadlines (2026 vs 2027 merger markets) and resolution disputes.
- **Market hours:** prediction markets trade 24/7 and US equities do not. The cleanest tests are (a) the Friday 4pm ET to Monday 9:30 ET change in odds against the Monday open-to-close or close-to-open return, and (b) moves after hours on event nights. Pre-market and overnight equity venues now absorb part of this, so the edge may be small.
- Filter by minimum 24h volume and depth, and drop markets where one wallet dominates the flow (Polymarket is on-chain, so this can be checked).

### Gaps
- I found no study of weekend prediction-market moves as Monday equity signals for any ticker.
- I found nothing systematic on whether Kalshi's CFTC regulation lowers manipulation compared with Polymarket. Polymarket's US-regulated venue ("Polymarket US") is a separate API and was not researched.
