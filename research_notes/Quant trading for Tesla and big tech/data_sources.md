# Market Data Sources for a Retail Python Quant (TSLA / mega-cap tech), as of Nov 2026

Research date: 2026-11-18. Every price is marked with the date of its source. The unlabeled "official" figures come from vendor pages fetched on 2026-11-18. Many pricing figures come from third-party or competitor comparison pages, and those are flagged.

## 1. Provider-by-provider status, limits and prices (daily, intraday, tick, fundamentals, options)

### Takeaway
At the cheap end of the 2026 market there are four main options. Alpaca is free (IEX feed) or $99/mo for full SIP plus OPRA. Massive (the renamed Polygon.io) runs $0 to $199/mo per asset class. Tiingo's paid plan is about $30/mo. Alpha Vantage is $49.99/mo and up. yfinance is still free but unofficial and rate-limited. Databento is the tick/L2/L3 specialist. Its new subscription prices, effective June 2026, are mostly out of hobbyist range, but pay-as-you-go historical data with $125 in free credit keeps it usable for one-off tick pulls. IEX Cloud no longer exists in its original form.

### Cited Findings

**yfinance (Yahoo, unofficial scraper)**
- Yahoo's rate limit is not formally documented. — [Slingacademy guide](https://www.slingacademy.com/article/rate-limiting-and-api-best-practices-for-yfinance/)
- Users reported "Too Many Requests. Rate limited" errors on versions 0.2.57 to 0.2.59. Some said the block lasted more than 24 hours. — [yfinance GitHub issue #2422](https://github.com/ranaroussi/yfinance/issues/2422); [Discussion #2431](https://github.com/ranaroussi/yfinance/discussions/2431)
- The block appears to be per IP. Users hitting it from shared hosts concluded it is Yahoo-imposed (anecdotal). — [PythonAnywhere forum](https://www.pythonanywhere.com/forums/topic/35819/)
- One r/algotrading user says a yfinance script "suddenly and (to me, inexplicably) broken at least twice" (ANECDOTAL). — [r/algotrading via mirror](https://reddit.birdcat.cafe/r/algotrading/comments/1kthgcr/comparing_affordable_intraday_data_sources)
- Comparison articles describe it as lacking the reliability needed for serious trading. — [edgeful blog, 2026](https://edgeful.com/blog/posts/yahoo-finance-api-alternatives)

**Alpaca Market Data (official docs, fetched 2026-11-18)**
- Basic plan: free. Real-time equities from IEX only. History since 2016, but the most recent 15 minutes of SIP data are blocked. 30 WebSocket symbols. Options come from an "indicative" feed with 200 WebSocket quotes. 200 historical calls/min. — [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api)
- Algo Trader Plus: $99/month. Real-time data from all US exchanges (SIP). History since 2016 with no restriction. Unlimited equity WebSocket symbols. OPRA options feed with 1,000 WebSocket quotes. 10,000 historical calls/min. — [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api)
- Free users can request `feed='delayed_sip'` to get full-market SIP data delayed 15 minutes. — [Alpaca forum](https://forum.alpaca.markets/t/does-the-realtime-api-endpoint-behave-differently-with-a-paid-subscription/17925)
- A comparison page checked 2026-11-02 ranks Alpaca Algo Trader Plus ($99) as the cheapest plan meeting "500 symbols, real-time 1-minute bars". — [aifinhub comparison, revised 2026-11-14](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- One r/algotrading commenter calls Alpaca "good for beginners, 99$/mo for unlimited traffic, generous rate limits" (ANECDOTAL). — [r/algotrading thread via mirror](https://axebps-redlib.hf.space/r/algotrading/comments/1h4tte0/algotraders_what_is_your_goto_api_for_realtime)

**Massive (formerly Polygon.io)**
- Polygon.io rebranded to Massive.com. Existing keys and integrations keep working, and api.polygon.io still serves requests. — [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html)
- The rebrand date is reported as 2025-10-30. — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/). Another page says "early 2026". — [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html). The two sources conflict.
- Stocks plans, checked 2026-11-02:

  | Plan | Price | Data timing | History | Limits |
  |---|---|---|---|---|
  | Basic | $0 | end-of-day | 2 years | 5 calls/min |
  | Starter | $29/mo | 15-min delay | 5 years | |
  | Developer | $79/mo | 15-min delay | 10 years | |
  | Advanced | $199/mo | real-time | 20+ years | |

  — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- Some pages list Developer at $99/mo and call that the pre-rebrand price, so the $79 vs $99 discrepancy is unresolved. — [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html)
- From the official page, fetched 2026-11-18:
  - Stocks Advanced costs $199/mo, or $159/mo billed annually. It includes real-time data, WebSockets, "20+ years of history" and Financials & Ratios, for individual use only.
  - A standalone Financials & Ratios add-on costs $29/mo.
  - The other tiers did not render in the fetch. — [massive.com/pricing](https://massive.com/pricing)
- Pricing is per asset class: stocks, options and forex/crypto are separate subscriptions. — [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html)
- r/algotrading users and comparison articles describe it as a solid US-equities choice that "can become expensive" (ANECDOTAL/aggregator). — [gummysearch Reddit aggregate](https://gummysearch.com/tools/best-products/data-provider/); [r/algotrading Tiingo vs Polygon thread](https://redlib.hbubli.cc/r/algotrading/comments/1ka6yv8/tiingo_vs_polygon_as_data_source/mpkqo5z)

**Tiingo**
- Fundamentals plans:
  - Free: $0
  - Power: $30/mo, with 10,000 requests/hour and 100,000/day
  - Commercial: $50/mo
  - Plans cover 80+ fundamental indicators, updated 12 to 24 hours after filings. — [Tiingo fundamentals page](https://api.tiingo.com/products/fundamental-data-api)
- Older or other sources quote $10/mo, or about $36/mo for "Pro". This looks stale. — [daytradereview](https://daytradereview.com/tiingo-review); [MarketParquet](https://marketparquet.com/vs/tiingo)
- The intraday/real-time feed is IEX only: REST for historical intraday, WebSocket for trades and top of book. The license is internal use only. — [Tiingo IEX API](https://api.tiingo.com/products/iex-api)
- IEX carries about 2 to 5% of consolidated volume, so IEX-only intraday bars are partial. — [aifinhub Q2 2026 benchmark](https://aifinhub.pages.dev/benchmarks/state-of-ai-market-data-2026/). The source is competitor-adjacent.

**Alpha Vantage**
- The free key allows 25 requests/day. — [alphavantage.co/premium](https://alphavantage.co/premium)
- The free limit has shrunk over time: 500/day, then 100/day, now 25/day. — [macroption](https://wws.macroption.com/alpha-vantage-api-limits/)
- Premium tiers are priced by requests per minute, with no daily cap:

  | Price | Requests/min |
  |---|---|
  | $49.99/mo | 75 |
  | $99.99/mo | 150 |
  | $149.99/mo | 300 |
  | $199.99/mo | 600 |
  | $249.99/mo | 1,200 |

  — [apicostcalc](https://apicostcalc.com/alpha-vantage.html); [multiples.vc 2026](https://multiples.vc/compare/alpha-vantage-api-alternatives). Third-party figures; not confirmed on the official page in this session.

**Databento**
- New subscription prices took effect 2026-06-22, citing higher exchange license fees. The blog lists "Databento US Equities: $4,000" per month. — [Databento blog, 2026-05-29](https://databento.com/blog/updates-to-subscription-pricing)
- A third-party page checked 2026-11-02 lists these US Equities plans:

  | Plan | Price | Includes |
  |---|---|---|
  | Standard | $199/mo | real-time, limited feeds |
  | Plus | $1,500/mo, annual contract | L2/L3 |
  | Unlimited | $4,000/mo, annual contract | L2/L3, entire history since May 2018 |

  Order-book history is 1 month on Standard and Plus. Historical data is metered per GB, with $125 of free credits that expire after 6 months. — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- The Standard plan was introduced in January 2025 at $199/mo. — [Databento blog, Jan 2025](https://databento.com/blog/upcoming-changes-to-pricing-plans-in-january-2025)
- "US Equities Mini" is pay as you go for historical data, "lowest cost to get started". — [Databento US equities catalog](https://databento.com/catalog/us-equities)
- Comparisons say it "excels in low-latency and high-fidelity data" at a premium price. — [dev.to 2025 comparison](https://dev.to/simplycode/2025-best-data-api-for-system-traders-4ik0)

**IEX Cloud status**
- IEX notified clients on 2024-05-31 and retired all IEX Cloud products on 2024-08-31. The business was under 2% of IEX Group revenue and loss-making. — [WatersTechnology](https://waterstechnology.com/data-management/7951882/iex-cloud-closure-forces-fintech-clients-to-seek-data-alternatives)
- A former IEX Cloud head bought the assets days before the deadline, aiming to replicate the service, starting from "zero revenue and a blank subscriber list". — [WatersTechnology](https://waterstechnology.com/trading-tech/7951983/facing-platform-shutdown-former-iex-cloud-head-buys-its-assets-in-11th-hour-bid)
- The IEX exchange feed itself lives on as the free real-time source for Alpaca Basic and Tiingo. — [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api); [Tiingo IEX](https://api.tiingo.com/products/iex-api)

**EODHD**
- Delisted symbols can be listed with a delisted flag, and then the EOD, Fundamentals, Dividends and Splits endpoints work for them as for active tickers. — [EODHD docs post](https://eodhd.com/financial-apis/wp-json/wp/v2/posts/8038)
- A paid plan is quoted at $19.99/mo. This is a third-party figure, and the tier is unclear. — [findmymoat](https://www.findmymoat.com/vs/eodhd-vs-tikr)
- EODHD covers delisted tickers, ticker changes and options, which FMP is said to lack. — [findmymoat EODHD vs FMP](https://www.findmymoat.com/vs/eodhd-eod-historical-data-vs-financial-modeling-prep-fmp). This conflicts with the next item.

**Financial Modeling Prep (FMP)**
- FMP's bulk EOD data reportedly covers delisted companies such as Twitter and Credit Suisse. — [businessquant](https://businessquant.com/resources/eod-stock-data-apis)
- Plans are reported as $0 to $99/mo, with entry tiers limited to US markets. — [lambdafin 2026](https://www.lambdafin.com/articles/financial-data-api-2026)
- Another source quotes $22/mo starter with 250 calls/day EOD. — [multiples.vc](https://multiples.vc/compare/fmp-api-alternatives)
- The entry tier reportedly forbids redistribution or display. — [multiples.vc](https://multiples.vc/compare/fmp-api-alternatives)
- The official pricing page returned HTTP 403 to the fetcher, so none of these figures are verified.
- FMP markets itself as an IEX Cloud replacement with "30+ years of historical prices and fundamentals" (vendor claim). — [FMP blog](https://site.financialmodelingprep.com/de/developer/docs/blog/Best-Alternative-for-IEX-Cloud-Market-Data-API-Financial-Modeling-Prep-FMP)

**SEC EDGAR (free, official fundamentals)**
- The maximum request rate is 10 requests/second. A User-Agent header with a company/name and contact email is required. — [SEC Accessing EDGAR Data](https://www.sec.gov/os/accessing-edgar-data)
- Requests without a User-Agent get HTTP 403 and risk an IP block. — [arkolith guide](https://arkolith.com/blog/sec-edgar-api-guide)
- The XBRL company-facts endpoint is `https://data.sec.gov/api/xbrl/companyfacts/CIK{10-digit-CIK}.json`. — [arkolith guide](https://arkolith.com/blog/sec-edgar-api-guide)

**Options: ORATS and Cboe DataShop**
- ORATS 2-minute snapshot history (2015 to present) costs $2,000 one-time, or $199/month as a subscription. The same page lists $599 for an older or other dataset; it may be EOD from 2007, but the fetch summary is ambiguous. — [ORATS two-minute data](https://orats.com/two-minute-data)
- ORATS 1-minute intraday history (Aug 2020 onward) costs $1,500 one-time, about 28 TB delivered via S3. — [ORATS one-minute data](https://orats.com/one-minute-data)
- ORATS near-EOD data covers 2007 onward and 5,000+ symbols. Snapshots are taken 14 minutes before the close. — [ORATS near-EOD](https://orats.com/near-eod-data)
- Cboe DataShop has no public price: it is custom quote or institutional. Interval data covers 2012 onward. — [Cboe historical data](https://www.cboe.com/solutions/options-analytics/historical-data); [DataShop options intervals](https://datashop.cboe.com/options-intervals); [FlashAlpha comparison](https://flashalpha.com/articles/institutional-options-data-providers-compared-2026). FlashAlpha is a competitor.
- Cheap real-time options quotes are available through Alpaca Algo Trader Plus (OPRA, $99/mo). Massive sells options as a separate asset-class subscription. — [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api); [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html)

### Inferences
- For a TSLA/mega-cap universe of fewer than 20 tickers, rate limits matter less than feed quality. IEX-only intraday data (Alpaca Basic, Tiingo) is fine for prototyping, but it understates volume and can misprint highs and lows relative to the consolidated tape.
- Daily bars for mega-caps are close to a commodity, so free sources are adequate. The differentiators are tick/quote data and options history, and that is where costs jump: Massive Advanced at $199/mo, ORATS, Databento.
- Databento's pay-as-you-go credits ($125) are likely enough for a one-off TSLA trades/quotes sample, which avoids the subscription entirely.

### Gaps
- Massive Starter and Developer tiers and the options plan prices could not be confirmed from massive.com directly, because the page rendered only partially. The Developer price is $79 or $99.
- FMP and EODHD official 2026 price tables were not retrieved: FMP returned 403, and EODHD was not fetched.
- FRED API rate limits were not found in this session. FRED is free with an API key, but the exact limit is unverified.
- No independent measurements of yfinance's 2026 rate-limit thresholds were found. The current state of the yfinance library (version, fixes) was not checked.
- The current status of the revived IEX Cloud successor is unknown.

## 2. Historical depth, adjusted vs unadjusted data, and survivorship bias

### Takeaway
Cheap APIs give 2 to 20+ years of depth: Alpaca from 2016, Massive Basic 2 years up to Advanced 20+, Databento equities from May 2018, ORATS options from 2007. For a TSLA/mega-cap strategy, survivorship bias barely matters for the target tickers. It does matter if the universe is selected by screens such as "current Nasdaq-100". Survivorship-bias-free data needs Norgate, Sharadar or EODHD's delisted endpoints, plus point-in-time index membership.

### Cited Findings
- Historical depth by vendor:

  | Vendor / plan | Depth |
  |---|---|
  | Alpaca (both plans) | since 2016 |
  | Massive Basic | 2 years |
  | Massive Starter | 5 years |
  | Massive Developer | 10 years |
  | Massive Advanced | 20+ years |
  | Databento US Equities | since May 2018 (Unlimited plan) |

  — [Alpaca docs](https://docs.alpaca.markets/docs/about-market-data-api); [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- The comparison page does not mention survivorship bias or delisted coverage for Alpaca, Databento or Massive. — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- Norgate specializes in survivorship-bias-free US, Australian and Canadian data, including delisted stocks and historical index membership. — [Norgate](https://norgatedata.com/); [enlightenedstocktrading review](https://enlightenedstocktrading.com/norgate-data)
- Norgate price estimates are about $270 to $790/year. — [MarketParquet](https://marketparquet.com/vs/norgate). A forum says the cheapest survivorship-free tier is $630/year. — [QuantConnect forum](https://www.quantconnect.com/forum/discussion/21226/would-you-pay-for-cheap-point-in-time-s-amp-p-500-data-survivorship-bias-free/). The figures conflict.
- Sharadar covers 20,000+ US companies, active and delisted. Professionals must buy through Nasdaq Data Link. — [QuantRocket Sharadar](https://quantrocket.com/pricing/data/sharadar)
- EODHD exposes delisted tickers through a delisted flag. — [EODHD](https://eodhd.com/financial-apis/wp-json/wp/v2/posts/8038)
- Even with survivorship-free prices, index membership bias remains unless you use point-in-time constituents. — [Concretum Group](https://concretumgroup.com/how-to-construct-a-survivorship-bias-free-database-in-norgate-using-python/)
- Traders specifically seek unadjusted plus survivorship-free EOD data, and few cheap vendors offer both (forum, ANECDOTAL). — [EliteTrader thread](https://www.elitetrader.com/et/threads/looking-for-unadjusted-survivorship-bias-free-eod-data.382018)

### Inferences
- TSLA had a 5:1 split in 2020 and a 3:1 split in 2022, so mixing adjusted and unadjusted series will silently break backtests and option-strike alignment. Store raw bars plus a corporate-actions table, and adjust locally. (Split facts come from general knowledge and were not sourced in this session.)
- Selecting "big tech" by today's market cap is a look-ahead/survivorship bias in itself. Use point-in-time membership if the universe rotates.

### Gaps
- The default adjustment behavior of each API was not verified in this session: yfinance `auto_adjust`, Alpaca's `adjustment` parameter, and Massive's `adjusted=true` default.
- Whether Massive includes delisted tickers on cheap tiers was not confirmed.

## 3. Recommended stack: beginner vs serious hobbyist

### Takeaway
A beginner can spend $0 with yfinance or Alpaca Basic for bars, SEC EDGAR for fundamentals and FRED for macro, and should cache everything locally. A serious hobbyist would spend about $100 to $300/mo: Alpaca Algo Trader Plus ($99, SIP + OPRA) or Massive Stocks Advanced ($199), optionally ORATS ($199/mo) for options history, Norgate or Sharadar for survivorship-free research, and Databento pay-as-you-go for occasional tick pulls.

### Cited Findings
- Alpaca is commonly recommended for beginners and cheap real-time data (ANECDOTAL, r/algotrading). — [r/algotrading via mirror](https://axebps-redlib.hf.space/r/algotrading/comments/1h4tte0/algotraders_what_is_your_goto_api_for_realtime)
- yfinance is fine for hobby backtests. Polygon/Massive or Alpaca are the common picks for serious US equities work, and Databento for tick-level data (aggregated Reddit/blog opinion, ANECDOTAL). — [gummysearch Reddit aggregate](https://gummysearch.com/tools/best-products/data-provider/); [dev.to comparison](https://dev.to/simplycode/2025-best-data-api-for-system-traders-4ik0)
- Alpaca Algo Trader Plus at $99/mo ranks first on cost for real-time 1-minute bars across 500 symbols (comparison checked 2026-11-02). — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)
- SEC EDGAR is free at up to 10 requests/second. — [SEC](https://www.sec.gov/os/accessing-edgar-data)
- ORATS is $199/mo, or $2,000 one-time for 2-minute options history from 2015. — [ORATS](https://orats.com/two-minute-data)
- Databento offers $125 in free historical credits. — [aifinhub](https://aifinhub-monorepo.pages.dev/articles/market-data-apis-compared-2026/)

### Inferences
- **Beginner ($0):**
  - Prices: yfinance for daily bars, with local caching (parquet) and backoff. Alpaca Basic for intraday and paper trading, using IEX real-time and `delayed_sip` for history.
  - Fundamentals: SEC EDGAR companyfacts.
  - Macro: FRED.
  - Alpha Vantage's free tier (25/day) is too small to be the main source.
- **Serious hobbyist (about $100 to $400/mo):**
  - Bars and options quotes: Alpaca Algo Trader Plus at $99, which covers SIP bars and real-time OPRA options. Massive Stocks Advanced at $199 is the alternative if you want 20+ years and the bundled financials.
  - Options history: ORATS, or Massive options.
  - Survivorship-free research: Norgate, about $270 to $790/yr.
  - Tick/L2 data: occasional Databento pay-as-you-go pulls.
  - Fundamentals: Tiingo Power ($30) or FMP as a cleaner normalized layer over EDGAR.
- Using the broker's own feed (Alpaca) for both backtest and live trading reduces bar-mismatch problems between research and execution.

### Gaps
- No 2026 r/algotrading threads were retrieved directly. The Reddit evidence is 2024–2025 and comes through mirrors.
- No head-to-head data-quality audit was found: for example, comparing bad-tick rates or split-adjustment errors on TSLA across vendors.
