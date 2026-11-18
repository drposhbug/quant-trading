# Brokers with APIs for Automated US Equity/Options Retail Trading (as of Nov 2026)

Scope: Alpaca, Interactive Brokers (TWS API / ib_async), Tradier, Schwab Trader API, Tastytrade, Webull / Robinhood API status, QuantConnect live. Research done 2026-11-18. About 14 searches and fetches; several numbers come from third-party or forum sources and are flagged as such.

## Commissions, PFOF, API quality, paper trading, options/shorting, fractional shares

### Takeaway
Most retail API brokers now charge $0 for stocks. They differ on options pricing and on PFOF. IBKR Pro is the main option that charges per share and does not take PFOF. Alpaca, Tradier and Schwab route to market makers and receive order-flow revenue. For options-heavy work, Tradier Pro ($10/mo, $0 equity options) and tastytrade ($1/contract to open, $0 to close) are the cost leaders. Alpaca is the easiest to set up for paper trading.

### Cited Findings
**Alpaca**
- Options trading through the API has zero commissions. — [Alpaca Trading API](https://alpaca.markets/trading-api)
- Margin: up to 4X intraday and 2X overnight buying power. — [Alpaca algotrading](https://alpaca.markets/algotrading)
- PFOF: Alpaca's 2026 Q1 606 filing says Alpaca Securities earns revenue from third-party liquidity providers based on the order flow executed at each destination. Quarterly 606 PDFs (2026Q1, 2026Q2) are published. — [Alpaca 606 2026Q1](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q1.pdf); [Alpaca 606 2026Q2](https://files.alpaca.markets/disclosures/library/SEC+606a1+-+2026Q2.pdf); [FINRA-hosted 606 2024Q3](https://cdn.finra.org/606/2024/288202_606_NMS_2024_Q3_V3.pdf)
- Fractional (notional) orders support only `day` TIF, with market, limit, stop and stop-limit types. Some sequences of fractional sells outside market hours are rejected because they would create a net short. — [Alpaca Orders docs](https://docs.alpaca.markets/docs/orders-at-alpaca)
- Short selling: the buying-power check for an opening short is the greater of the limit price or ask+3%, times quantity. Extended-hours shorts are treated the same as regular-hours shorts. — [Alpaca Orders docs](https://docs.alpaca.markets/docs/orders-at-alpaca)
- Options orders: market, limit, stop and stop-limit with `day`/`gtc` only. No IOC/FOK/OPG/CLS. — [Alpaca Orders docs](https://docs.alpaca.markets/docs/orders-at-alpaca)
- A developer review in 2026 called Alpaca a "commission-free automated trading" API for developers. — [DEV Community review](https://dev.to/pickuma/alpaca-api-review-commission-free-automated-trading-for-developers-in-2026-41m1)

**Interactive Brokers**
- IBKR Pro Tiered for US stocks: USD 0.0005–0.0035/share depending on monthly volume, per IBKR's EU-region page. The Canadian-site schedule starts at USD 0.0035 for ≤300k shares/month and falls to 0.0010 at 20M+. Tiered is capped at 0.5% of trade value. Fixed is USD 0.005/share. — [IBKR Commissions Stocks](https://investors.interactivebrokers.com/en/pricing/commissions-stocks.php); [IBKR (EU mirror)](https://gdcdyn.interactivebrokers.com/en/index.php?f=49637)
- Directed API orders cannot use Tiered. SmartRouted API orders can use Tiered or Fixed. — [IBKR Commissions Stocks](https://investors.interactivebrokers.com/en/pricing/commissions-stocks.php)
- Volume from open/close auctions, outside-RTH and sub-dollar orders above 10% of monthly US stock volume is charged at the lesser of USD 0.005/share or 1% of trade value. — [IBKR Commissions Stocks](https://investors.interactivebrokers.com/en/pricing/commissions-stocks.php)
- IBKR Lite accounts trading in the overnight session pay Fixed pricing, so overnight is not free on Lite. — [IBKR Commissions Stocks](https://investors.interactivebrokers.com/en/pricing/commissions-stocks.php)
- The FINRA TAF fee holiday runs Oct 1 – Dec 31, 2026. — [IBKR Commissions Stocks](https://investors.interactivebrokers.com/en/pricing/commissions-stocks.php)
- Options and futures tiered ranges ($0.15–$0.65 and $0.25–$0.85 per contract) come from a third-party review, not IBKR. — [daytradingz IBKR review](https://daytradingz.com/interactive-brokers-review/)

**Tradier**
- Pro ($10/mo): $0 stock, ETF and equity/ETF option commissions. Single-listed index options cost $0.35/contract. Pro Plus ($35/mo) charges $0.10/contract on index options. Lite (free) charges $0.35/contract on equity/ETF options and index options. ORF is $0.02/contract, and the options TAF is $0.00 for 10/1–12/31/2026. Pricing is stated as of March 2026. — [Tradier pricing](https://tradier.com/individuals/pricing); [BrokerChooser Tradier fees](https://brokerchooser.com/broker-reviews/tradier-review/tradier-fees)

**Tastytrade**
- Options cost $1/contract to open, capped at $10 per leg, and $0 to close. API access has no extra charge. — [CryptoSlate tastytrade review](https://cryptoslate.com/brokers/tastytrade-review/); [api-evangelist tastytrade](https://github.com/api-evangelist/tastytrade)
- Index options: one source says SPX adds $0.60/contract. Sources disagree on whether the cap applies. — [tradingbrokers Tradier vs Tastytrade](https://tradingbrokers.com/tradier-vs-tastytrade/)
- Official developer docs are at developer.tastytrade.com. — [tastytrade developer docs](https://developer.tastytrade.com/docs/)

**Webull**
- Webull's official OpenAPI lets developers place, modify, cancel and query US stock, ETF and options orders. Some regional pages exclude index options. — [Webull Trading API overview](https://developer.webull.com.sg/apis/docs/trade-api/overview); [About Webull OpenAPI](https://developer.webull.com.au/apis/docs/about-open-api)
- Requests are signed with HMAC-SHA256 using the App Key and App Secret. — [Zuplo Webull API guide](https://dev.to/zuplo/webull-api-guide-endpoints-authentication-python-sdks-3a82)

**Robinhood**
- Robinhood's documented developer API is the Crypto Trading API. Keys come from a desktop-only credentials portal. — [Robinhood Crypto API](https://robinhood.com/us/en/support/articles/crypto-api)
- On May 27, 2026, Robinhood launched "Agentic Trading" (beta). Third-party AI agents connect to dedicated accounts through Robinhood MCP servers. Robinhood says it supports equities "out of the gate", with options, crypto, futures and event contracts "coming soon". — [Robinhood newsroom](https://robinhood.com/us/en/newsroom/robinhood-is-now-open-to-agents/); [The Block](https://www.theblock.co/post/402729/robinhood-ai-powered-crypto-trading-launching-agentic-stock-trading-beta)
- Crypto was added to Agentic Trading around July 20, 2026. Some coverage says options are now included, but Robinhood's own page does not confirm it. — [Genfinity](https://genfinity.io/2026/07/21/robinhood-agentic-trading-crypto-ai-agents/); [Crypto Briefing](https://cryptobriefing.com/robinhood-agentic-trading-crypto-equities/)
- As of January 2026, Robinhood had no official, supported public REST API for stocks or options for retail. — [Bitget wiki](https://www.bitget.cloud/wiki/does-robinhood-have-an-api-for-stocks)

**QuantConnect**
- Live brokerages documented include Interactive Brokers, Tradier, tastytrade, TradeStation, Trading Technologies, crypto venues and QC Paper Trading. — [QC brokerages](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages.md); [QC tastytrade](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/tastytrade.md); [QC IB](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/interactive-brokers.md)
- Live-node quotas by tier: Free 0, Quant Researcher 2, Team 10, Trading Firm and Institution unlimited. Each algorithm needs its own node. — [QC deployment docs](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/deployment.md)
- Pricing is unverified. A third-party review lists Researcher at $60/mo with 1 live node and Team at $120/mo, which conflicts with the official 2-node quota. — [quantt.co.uk review](https://www.quantt.co.uk/resources/quantconnect-review)

### Inferences
- For mega-cap stock trading at small size, $0 PFOF brokers (Alpaca, Schwab, Tradier) cost about the same as IBKR Pro Tiered, which is about $0.35 per 100 shares plus fees. IBKR's advantage is routing control and no PFOF, not a lower headline commission.
- For an options-heavy strategy, Tradier Pro at $10/mo beats per-contract pricing above roughly 10–30 contracts a month.
- Robinhood is not a realistic programmatic venue for a Python quant. Its stock access is MCP and agent-oriented beta, not a documented REST trading API.

### Gaps
- Alpaca's actual 606 per-share PFOF numbers. The PDF could not be text-extracted.
- Schwab and Webull commission and PFOF details were not separately verified. Both are generally $0 stock commissions; Schwab options are commonly $0.65/contract. This is not verified in this session.
- IBKR's official options commission schedule was not fetched.
- Tastytrade's official fee page and current stock commission were not fetched.
- Webull OpenAPI US account eligibility and any minimums.

## Python libraries, reliability and rate limits

### Takeaway
IBKR has the most capable and most cumbersome stack: a TWS or Gateway process plus ib_async. Alpaca has the cleanest official SDK and a REST/WebSocket model. Schwab, tastytrade and Robinhood rely mainly on community wrappers. Published rate limits: Alpaca about 200 req/min per account; Schwab 120 req/min for non-order calls, with an order limit of 0–120/min set at app registration.

### Cited Findings
- **ib_async** is the maintained successor to ib_insync. The original author, Ewald de Wit, died in early 2024. It is now at github.com/ib-api-reloaded/ib_async, requires Python ≥3.10 and installs with `pip install ib_async`. — [PyPI ib_async](https://pypi.org/project/ib_async); [ecosyste.ms ib_async](https://awesome.ecosyste.ms/projects/github.com%2Fib-api-reloaded%2Fib_async)
- IBKR's own docs say ib_insync users should migrate to ib_async, but that IBKR "will always advise clients use our direct TWS API implementation whenever possible". — [IBKR TWS API docs: ib_insync and ib_async](https://www.interactivebrokers.com/docs/tws-api/doc/third-party-api-platforms/non-standard-tws-api-languages-and-packages/ib-insync-and-ib-async)
- Alpaca: 200 requests/min per account for the Trading API. Headers include X-Ratelimit-Limit and X-Ratelimit-Remaining. Paid data plans raise the Market Data API limit (1,000–10,000/min reported), not the trading limit. — [Alpaca support: usage limit](https://alpaca.markets/support/usage-limit-api-calls); [Alpaca forum: rate limit clarity](https://forum.alpaca.markets/t/rate-limit-clarity/7202); [Alpaca rate limits docs](https://docs.alpaca.markets/docs/rate-limits)
- Users report 429 errors on Alpaca when creating orders. — [Alpaca forum 429](https://forum.alpaca.markets/t/429-rate-limit-exceeded-when-creating-orders/14120)
- Schwab: non-order throttle is 120 req/min per application. Order throttle is 0–120/min, set at app registration per account. schwab-py recommends 120. Exceeding a limit returns HTTP 429. — [schwab-py getting started](https://schwab-py.readthedocs.io/en/latest/_sources/getting-started.rst.txt); [TD/Schwab API forum](https://apiforums.tdameritrade.com/node/116); [schwabdev](https://docsearch.algolia.com/mcp/docs/repo/tylerebowers/schwabdev)
- Tastytrade Python options are unofficial. The main one is `tastyware/tastytrade` (pip `tastytrade`); another is `tastytrade-sdk`. — [tastyware/tastytrade](https://github.com/tastyware/tastytrade); [PyPI tastytrade-sdk](https://pypi.org/project/tastytrade-sdk/)
- Webull has an official Python SDK, `webull-openapi-python-sdk`, for Python 3.8–3.13. It also has an official MCP server and CLI. — [Zuplo Webull guide](https://zuplo.com/learning-center/webull-api); [webull-openapi-mcp](https://github.com/webull-inc/webull-openapi-mcp)
- A 2026 developer review mentions Alpaca rate limits during volatile opens. — [DEV Community review](https://dev.to/pickuma/alpaca-api-review-commission-free-automated-trading-for-developers-in-2026-41m1)

### Inferences
- At 200 req/min (Alpaca) or 120 req/min (Schwab), market data should come from WebSocket streams, not polling. Order traffic for a few mega-cap tickers fits within these limits.
- IBKR needs an always-on TWS or IB Gateway process with daily restarts. That is the main reliability cost.

### Gaps
- Tradier rate limits. The docs page returned 404.
- Tastytrade API rate limits.
- Official Schwab rate-limit page; the 120/min figures come from community libraries.
- IBKR TWS API pacing limits (commonly cited as 50 msgs/sec) were not verified this session.

## Order types, execution quality for mega caps, overnight/24h trading

### Takeaway
Alpaca, IBKR and Schwab all offer 24/5 trading for many NMS stocks, including TSLA and big tech. Overnight sessions accept limit orders only (IBKR also allows Adaptive) and exclude options. Alpaca and IBKR expose overnight trading through the API. Schwab's overnight session is documented only for thinkorswim. Execution-quality data for mega caps (605/606 stats) was not obtained.

### Cited Findings
- Alpaca 24/5: Sunday 8pm to Friday 8pm ET, overnight session 8pm–4am ET, all NMS securities. Limit orders only, DAY/GTC, `extended_hours=true`. Per-asset eligibility is in the `overnight_tradable` field. OTC and options are excluded. Launched for Trading API users in early 2026. — [Alpaca 24/5 docs](https://docs.alpaca.markets/docs/245-trading); [Crowdfund Insider](https://www.crowdfundinsider.com/2026/02/259268-alpaca-introduces-24-5-trades-for-trading-api-providing-almost-round-the-clock-access/); [Alpaca forum: live 24/5](https://forum.alpaca.markets/t/live-24-5-trading/18393)
- Alpaca order types: market, limit, stop, stop-limit, MOO/LOO/MOC/LOC, bracket, OCO, OTO, trailing stop. TIF options: day, gtc (auto-canceled after 90 days), opg, cls, ioc, fok. — [Alpaca Orders docs](https://docs.alpaca.markets/docs/orders-at-alpaca)
- IBKR API overnight: set the contract exchange to `"OVERNIGHT"` with primaryExchange set to the listing exchange. Alternatively use SMART with `order.includeOvernight=True` for "OVERNIGHT+DAY". Only Limit and Adaptive orders are allowed. Client Portal API uses conidex such as `265598@OVERNIGHT`. — [IBKR TWS API: trading the overnight session](https://www.interactivebrokers.com/docs/tws-api/doc/orders/place-order/trading-the-overnight-session.md); [IBKR Campus API overnight](https://www.interactivebrokers.com/campus/ibkr-quant-news/api-overnight-trading/)
- Schwab 24/5: more than 1,100 securities (S&P 500, Nasdaq-100 and hundreds of ETFs) through EXTO orders. Each order is capped at $2M notional or 50,000 shares. The overnight session is "available exclusively on thinkorswim". — [Schwab 24/5](https://www.schwab.com/24-5-trading); [Schwab press release Jul 2025](https://pressroom.aboutschwab.com/press-releases/press-release/2025/Schwab-Makes-Expanded-24-Hour-Trading-Available-to-All-Clients/default.aspx)

### Inferences
- For TSLA and big tech overnight automation, Alpaca and IBKR are the confirmed API paths. Schwab Trader API overnight support is unverified and possibly absent.
- Overnight liquidity is thin, which is why every venue requires limit orders. Strategies should not expect regular-hours spreads overnight.

### Gaps
- Mega-cap execution-quality statistics (price improvement, effective/quoted spread) by broker. No Rule 605 data was retrieved.
- Whether Schwab Trader API accepts session=SEAMLESS/EXTO overnight orders.
- Tradier, tastytrade and Webull overnight availability.

## Account minimums and PDT constraints

### Takeaway
The SEC approved FINRA's removal of the Pattern Day Trader rule and its $25,000 minimum on April 14, 2026, effective June 4, 2026. It is replaced by intraday margin standards. Brokers may phase in changes through October 2027, so each broker's current rules need checking. The margin-account minimum is now the standard $2,000.

### Cited Findings
- The SEC granted accelerated approval to FINRA Rule 4210 amendments (SR-FINRA-2025-017, Release 34-105226) on April 14, 2026. The amendments remove the PDT designation, the $25k minimum and day-trading buying power provisions. — [Federal Register public inspection](https://public-inspection.federalregister.gov/2026-07485.pdf); [ThinkAdvisor](https://www.thinkadvisor.com/amp/2026/04/14/sec-approves-plan-removing-day-trading-limit-for-small-investors/)
- Effective June 4, 2026. Brokers may monitor intraday margin in real time or with an end-of-day calculation. Some firms have up to 18 months, until about Oct 20, 2027, to adopt. — [Firstrade guide](https://blog.firstrade.com/blog/2026/6/3/the-complete-guide-to-the-pdt-rule-elimination-everything-investors-need-to-know-on-day-one); [QuantInsti](https://www.quantinsti.com/articles/finra-pdt-rule-removal-2026/)
- E*TRADE's comparison table: the new minimum is $2,000, the same as any margin account. — [E*TRADE PDT change](https://us.etrade.com/knowledge/library/margin/pattern-day-trading-rule-change)
- Schwab covered the approval. — [Schwab: SEC approves scrapping $25,000 minimum](https://international.schwab.com/story/sec-approves-scrapping-25000-day-trader-minimum)

### Inferences
- PDT is largely no longer the binding constraint for small accounts. Intraday margin calls and each broker's own policies replace it. Cash accounts are still subject to settlement (T+1) and good-faith-violation rules.

### Gaps
- Which of the brokers in scope (Alpaca, IBKR, Tradier, Schwab, tastytrade, Webull) have finished switching from PDT to the new intraday margin regime.
- Broker-specific account minimums, such as IBKR's $0 cash minimum or tastytrade's options-level requirements, were not verified this session.
- The FINRA Regulatory Notice and SEC release were not fetched directly; the details come from secondary sources.
