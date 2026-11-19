# Practicalities of retail US equity options trading in 2026: execution, Alpaca, taxes, data

Scope: how mega-cap single-stock options (TSLA, NVDA, AAPL, MSFT, GOOGL, AMZN, META, AVGO, TSM, AMD, ORCL) actually trade at retail scale, how Alpaca handles options, the tax rules, and historical data for backtests. Research date: 2026-11-18. I ran about 16 searches and fetches. Anything marked UNVERIFIED or listed under Gaps has no primary source here.

## Q1: Spreads, liquidity and the round-trip cost of a 4-leg iron butterfly on NVDA/AAPL

### Takeaway
I found no primary source that gives spread as a % of mid, broken down by delta and expiry, for these specific tickers. The academic benchmark is Muravyev and Pearson (RFS 2020). The conventional quoted spread on S&P 500 stock options averages about 17% of the option price. Traders who time their executions pay effective spreads under 40% of the conventional measures. Use those numbers as the inputs to a cost model, and measure the actual NVDA/AAPL spreads yourself from a quote snapshot (OPRA feed) before trusting any assumption.

### Cited Findings
- Muravyev and Pearson, "Options Trading Costs Are Lower than You Think" (Review of Financial Studies 33(11), 2020). Traders who time their executions pay effective spreads under 40% of conventional measures. The overall average effective spread is about one-quarter smaller than conventional estimates — [RePEc](https://ideas.repec.org/a/oup/rfinst/v33y2020i11p4973-5014..html); [HHS summary](https://hhs.se/en/houseoffinance/outreach/news--press/news/2021/trading-costs-are-lower-than-previously-thought)
- A secondary summary says the adjusted effective spread is about two-thirds of the conventional effective spread and about half of the quoted spread. It also says traders who don't time their executions still pay the full conventional half-spread — [CXO Advisory](https://www.cxoadvisory.com/equity-options/timing-option-trades-to-suppress-trading-frictions/)
- Another paper quotes Muravyev-Pearson as finding an average quoted bid-ask spread of about 17.2% for S&P 500 stock options. This is relative to the option price, averaged across all strikes and expiries, so it is dominated by cheap OTM contracts. I took it from a search snippet and did not read the full PDF — [MQL5-hosted PDF of the paper](https://c.mql5.com/forextsd/forum/209/Option%20Trading%20Costs%20Are%20Lower%20than%20You%20Think.pdf)
- Tick sizes: Penny Program classes quote in $0.01 below $3.00 and $0.05 at $3.00 and above. Non-penny classes quote in $0.05 and $0.10. SPY, QQQ and IWM quote in pennies at every price. The optionsnest page in this list is secondary and unverified — [MarketData.app](https://www.marketdata.app/education/options/option-tick-sizes/); [Fidelity](https://www.fidelity.com/research/options/optionpplaunch.shtml); [optionsnest](https://optionsnest-com.pages.dev/handbook/penny-pilot/)
- AAPL is listed as penny-eligible — [MarketData.app](https://www.marketdata.app/education/options/option-tick-sizes/)
- On Alpaca, mleg orders fill all four legs together or not at all — [Alpaca support](https://alpaca.markets/support/why-are-multi-leg-orders-useful)

### Inferences
- **Iron butterfly round trip, worked from the tick rules above. These are not measured numbers.** A 30-DTE NVDA or AAPL iron fly has an ATM straddle priced above $3, so those two legs are in $0.05 ticks and in practice usually quote 1–3 ticks wide ($0.05–$0.15). The wings are cheaper (often under $3, penny ticks), and each is roughly $0.02–$0.10 wide. That puts the sum of the four leg spreads at about $0.15–$0.50. Crossing every spread on both entry and exit costs that full sum, which is 3–10% of a typical $5–8 credit. Filling at mid costs close to 0, and a realistic retail fill a little worse than mid costs about 1–4%. Weekly or earnings-week flies with a smaller credit can cost a larger share.
- The 17% average quoted spread is a cross-sectional average that the cheap far-OTM wings pull up, so it should not be applied to ATM legs. Model spread per leg as a function of option price and delta.
- In a backtest, charge at least half the summed quoted spread on each side (entry and exit), plus about $0.02–0.05 per contract in regulatory and clearing fees (UNVERIFIED for Alpaca's schedule). A strategy whose edge disappears when it pays the full spread is not robust.

### Gaps
- No primary source for per-ticker spread % by delta/expiry or for open interest on the 11 names. The best fix is to pull an OPRA snapshot (Alpaca Algo Trader Plus, ThetaData or Databento cbbo-1m) and compute the numbers directly.
- No public fill-rate statistics for mid-priced complex orders at retail brokers.
- PFOF: I did not find Alpaca's current options routing and payment-for-order-flow disclosure in this pass (it is published in SEC Rule 606 reports). Unverified.

## Q2: Alpaca options API and how the paper environment fills options orders

### Takeaway
Alpaca fills paper orders against real-time NBBO quotes when they become marketable. Buys fill at the ask and sells at the bid, so a limit at mid fills only once the market moves through it. Quote size is not checked, and there is no queue position, price improvement or slippage modeling. Alpaca does not document options-specific or mleg-specific paper fill rules. That makes paper less realistic than live in both directions: it is optimistic on size and pessimistic on price improvement. On the free plan, options quotes come from the indicative feed, which is derived from OPRA rather than the real quotes and is meant for testing.

### Cited Findings
**Order mechanics**
- Options order types are market, limit, stop and stop_limit. Stop and stop_limit are single-leg only. TIF must be day or gtc. qty must be a whole number, notional is not allowed, and extended_hours must be false — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)
- Multi-leg orders use `order_class: "mleg"` with a `legs` array of at most 4 legs. Each leg has symbol, ratio_qty, side and position_intent (buy_to_open, sell_to_close, etc.). mleg orders can be market or limit only. For mleg, `qty` is the number of strategy units — [Alpaca Create Order reference](https://docs.alpaca.markets/reference/postorder); [Options Level 3](https://docs.alpaca.markets/docs/options-level-3-trading)
- **Price sign convention:** "In case of mleg, the limit_price parameter is expressed with the following notation: A positive value indicates a debit... A negative value signifies a credit." So an iron fly sold for a credit of $5.00 is sent as `limit_price: -5.00` — [Alpaca Create Order reference](https://docs.alpaca.markets/reference/postorder)
  - Conflict: every example on the Level 3 docs page uses a positive limit_price, and that page never states the sign rule. Trust the API reference. Test with a tiny paper order to confirm — [Options Level 3](https://docs.alpaca.markets/docs/options-level-3-trading)
- The greatest common divisor of the leg ratios must be 1, so a 2:4 order is rejected and must be sent as 1:2. Equity legs are not supported in mleg. All legs must be covered within the same mleg order, so naked short legs are rejected in mleg (this affects rolls and calendars) — [Options Level 3](https://docs.alpaca.markets/docs/options-level-3-trading)
- Levels: 0 is disabled, 1 is covered calls and cash-secured puts, 2 adds buying calls and puts, 3 adds spreads. Options are enabled by default in paper. Multi-leg / Level 3 is available in paper and live — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading); [changelog](https://docs.alpaca.markets/changelog/multi-leg-level-3-options-trading-in-paper)
- Level 3 maintenance margin ignores premium and uses the theoretical maximum loss. Separate expirations are calculated separately — [Options Level 3](https://docs.alpaca.markets/docs/options-level-3-trading)

**Exercise and assignment**
- Exercise with `POST /v2/positions/{symbol}/exercise`. Requests sent between market close and midnight are rejected. A do-not-exercise instruction requires contacting support — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)
- With no instructions, contracts that are ITM by $0.01 or more are exercised automatically at expiry. If the account lacks buying power to exercise, Alpaca sells the position within the last hour before expiry — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)
- Assignments are not pushed over the websocket. You have to poll the REST account-activities endpoint for non-trade activities (NTAs). In paper, NTAs sync the next day — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)

**Paper fill simulation**
- "All orders submitted in paper trading will be matched against the best available current market price (NBBO)." Orders fill only once marketable. A buy limit fills when the ask reaches it, and a sell limit fills when the bid reaches it — [Alpaca Paper Trading](https://docs.alpaca.markets/us/docs/paper-trading)
- 10% of eligible orders get a random partial fill. Order quantity is not checked against NBBO size — [Alpaca Paper Trading](https://docs.alpaca.markets/us/docs/paper-trading)
- Not modeled in paper: market impact, information leakage, latency slippage, queue position, price improvement, regulatory fees, dividends — [Alpaca Paper Trading](https://docs.alpaca.markets/us/docs/paper-trading)
- Staff on the forum: paper buys fill at the ask and sells at the bid, using SIP NBBO. The market-data subscription does not change paper fills. The fill model looks only at quotes — [forum 14303](https://forum.alpaca.markets/t/does-a-paid-account-give-more-accurate-paper-market-fills/14303); [forum 18223](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223)
- Forum users report paper limit orders filling 50–260 seconds after the price crossed — [forum 18223](https://forum.alpaca.markets/t/paper-trading-fill-delays-of-50-260-seconds-limit-orders-filled-minutes-after-price-crossed/18223)
- Alpaca does not document how a paper mleg order is checked for marketability (net NBBO of the legs versus the net limit). I found no official source.

**Data feeds**
- The `indicative` feed is free. Its quotes are derived from OPRA rather than being the actual quotes, and its trades are delayed 15 minutes. The `opra` feed requires a subscription — [Alpaca historical option data](https://docs.alpaca.markets/docs/historical-option-data)
- OPRA access requires Algo Trader Plus (listed at $99/month) and a signed OPRA agreement. The websocket allows 1000 quote subscriptions on OPRA versus 200 on indicative — [Alpaca Market Data docs](https://docs.alpaca.markets/docs/about-market-data-api); [forum 18445](https://forum.alpaca.markets/t/error-opra-agreement-is-not-signed/18445)
- Alpaca staff, 2025-09-12 and 2026-02-01: indicative data "can vary from the actual opra data and is meant primarily for testing" and "should not be used for live trading." There is no separate paper data: what you get depends on the subscription, not the account type — [forum 17795](https://forum.alpaca.markets/t/paper-trading-options-pricing/17795)
- Alpaca's historical options data starts only in February 2024 — [Alpaca historical option data](https://docs.alpaca.markets/docs/historical-option-data)
- The contracts endpoint returns 100 results by default, and its default expiration_date_lte is the next weekend, so set both explicitly — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)

### Inferences
- A paper iron fly with a limit at mid will usually not fill until the quotes move through it. A live order can fill at mid or better because market makers improve price on complex orders. Expect paper fill rates to be lower and paper fill prices to be worse than live for patient mid-priced orders. Expect paper to be too optimistic for orders larger than the displayed size. Paper P&L is not a good proxy for live execution costs. Log the NBBO at submission and at fill for both, and compare.
- If the paper account runs on the free plan, the quotes driving the strategy are indicative, not real OPRA.
- Since assignments only show up by polling, an early-assignment check (poll activities each morning) is required for short-option strategies.

### Gaps
- No official statement on paper mleg fill logic, or on whether paper uses OPRA or indicative quotes for its fill decisions on options.
- Rate limits for the options REST API were not confirmed in this pass (the equities default is commonly cited as 200 req/min, UNVERIFIED for options).

## Q3: Assignment, early exercise and pin risk

### Takeaway
American-style single-stock options can be assigned at any time. The main early-assignment trigger for short calls is a dividend: if a deep ITM short call's extrinsic value (roughly the price of the same-strike put) is below the coming dividend, expect assignment the day before ex-dividend. At expiry, Alpaca exercises any contract ITM by $0.01 or more. A short strike that ends near the money therefore carries pin risk and can leave you with an unhedged stock position.

### Cited Findings
- A short call whose extrinsic value is less than the dividend is a candidate for early exercise. The risk is highest the day before the ex-date. The same-strike put price works as a proxy for the call's extrinsic value. Closing before the ex-date is the only way to remove the risk fully — [Schwab dividend risk](https://www.schwab.com/learn/story/ex-dividend-dates-understanding-dividend-risk); [Schwab assignment risks](https://www.schwab.com/learn/story/risks-options-assignment)
- Alpaca auto-exercises at $0.01 ITM and liquidates positions that lack buying power in the last hour before expiry — [Alpaca Options Trading](https://docs.alpaca.markets/docs/options-trading)

### Inferences
- Among these names, TSLA and AMD pay no dividend (UNVERIFIED for 2026), so the dividend risk applies to AAPL, MSFT, GOOGL, META, AVGO, TSM (ADR), ORCL and NVDA (whose dividend is tiny). Iron flies are mostly near ATM, so dividend early exercise only matters after a large move or close to the ex-date.
- Pin risk for a short iron fly: the body strike can finish exactly at the money, and after-hours moves can change the exercise decision for the long holder. A backtest should model a close on expiry day instead of assuming cash-like settlement at intrinsic value.

### Gaps
- I did not retrieve the primary OCC documents on exercise by exception and the 5:30pm ET submission cutoff.

## Q4: Taxes for equity options vs Section 1256 index options, wash sales, IRA restrictions

### Takeaway
Single-stock and ETF options (including SPY and QQQ) are taxed under ordinary capital-gains rules, and wash-sale rules apply to them. Broad-based index options (SPX, NDX, RUT) are Section 1256 nonequity options: they get 60% long-term / 40% short-term treatment, are marked to market at year end, are reported on Form 6781, and are exempt from wash-sale rules. For a short-dated strategy, 1256 treatment cuts the blended tax rate substantially.

### Cited Findings
- Section 1256 covers regulated futures, foreign currency contracts, nonequity options and dealer equity options. Nonequity options are options that are not on a single stock or a narrow-based index — [IRS Form 6781 (2023)](https://www.irs.gov/pub/irs-prior/f6781--2023.pdf); [TaxSlayer Pro](https://support.taxslayerpro.com/hc/en-us/articles/360040712794)
- Gains and losses are 60% long-term and 40% short-term regardless of holding period. Open positions are marked to market on the last business day of the tax year — [IRS Form 6781](https://www.irs.gov/pub/irs-prior/f6781--2023.pdf)
- Wash-sale rules do not apply to Section 1256 contracts. ETF options (SPY, QQQ, IWM) are equity options with full wash-sale exposure — [beancount guide (secondary)](https://beancount.io/blog/2026/05/14/section-1256-contracts-60-40-tax-treatment-futures-broad-based-index-options-regulated-forex-form-6781-mark-to-market-traders-guide); [terms.law (secondary)](https://terms.law/Trading-Legal/guides/section-1256-contracts.html)

### Inferences
- For a high-turnover iron fly strategy, an SPX/NDX version is taxed at a blended ~26.8% top federal rate (0.6×20% + 0.4×37%) versus 37% for NVDA/AAPL short-term gains. That is roughly a 10-point difference in after-tax return. SPX/NDX are also European-style and cash-settled, which removes early-assignment and pin-to-stock risk. As far as I found, Alpaca does not offer index options (UNVERIFIED).
- Wash-sale rules on equity options: repeatedly closing a losing iron fly and reopening a substantially identical one within 30 days can defer losses. Treat this as a bookkeeping risk.

### Gaps
- I did not retrieve the text of IRS Pub 550 on straddle rules (Section 1092), which can also defer losses on offsetting positions. Unverified.
- IRA restrictions: I found no source in this pass. The general industry practice is that IRAs allow covered calls, cash-secured puts, long options and defined-risk spreads (broker-dependent), and prohibit naked short calls and margin. Whether Alpaca offers options in IRAs is UNVERIFIED.

## Q5: Historical option-chain data with bid/ask for 2016–2026, and how to backtest honestly

### Takeaway
The cheapest reliable source of EOD chains with bid/ask covering 2016–2026 for these names appears to be a one-time ORATS near-EOD backfill ($599, from 2007, quotes taken around 14 minutes before the close) or a historicaloptiondata.com bundle (about $230–$865+). For intraday NBBO, Databento's OPRA cbbo-1m (history from 2013, about $2/GB pay-as-you-go) and ThetaData Standard/Pro ($80–$160/month, 8–12 years) are the value options. Alpaca's own history starts only in February 2024, which is not enough for a 2016–2026 test.

### Cited Findings
- **ORATS:** near-EOD data at $99/month recurring or a $599 one-time historical backfill from 2007 (about 500 GB). 1-minute intraday data is available from August 2020 — [ORATS near-EOD](https://orats.com/near-eod-data); [ORATS 1-minute](https://orats.com/one-minute-data)
- **historicaloptiondata.com:** the shop lists Level 1 from $230 (prices), Level 2 from $295 (adds Greeks and IV) and Level 3 from $865. The homepage table shows higher one-time prices for full history (e.g. Level 3 at $1,905 for 20+ years). The two pages conflict — [shop](https://historicaloptiondata.com/shop/); [home](https://historicaloptiondata.com/)
- **Cboe DataShop Option EOD Summary:** data from January 2012. A December 2024 schedule lists $35 per symbol per month or $420 per month for the full market. One-time full history is reported at about $8,500. Academic institutions get 50% off. DataShop has no fixed public price list — [DataShop](https://datashop.cboe.com/); [Option EOD Summary layout](https://datashop.cboe.com/documents/Option_EOD_Summary_Layout.pdf); [ORATS comparison (vendor-biased)](https://orats.com/compare/orats-vs-cboe-datashop); [academic discount](https://datashop.cboe.com/academic-discount)
- **ThetaData:** Value tier at $40/month (4 years, 1-minute), Standard at $80/month (tick quotes, 8 years), Pro at $160/month (12 years). The free tier offers EOD data only, at 20 requests/minute, and sources disagree on whether it covers 30 days or 1 year. Commercial use is $1,600/month — [ThetaData pricing](https://thetadata.net/pricing); [FlashAlpha comparison June 2026](https://flashalpha.com/articles/options-data-pricing-comparison-flashalpha-thetadata-polygon-spotgamma-squeezemetrics); [ThetaData commercial](https://thetadata.net/commercial-use)
- **Databento OPRA.PILLAR:** usage-based pricing per uncompressed GB. The example rates are about $2/GB for cbbo-1s and cbbo-1m, versus $210/GB for tcbbo and $280/GB for trades. cbbo-1m history starts 2013-04-01 and cbbo-1s starts 2023-03-28. A Standard OPRA subscription costs $199/month. Use `metadata.get_cost` to get a quote before downloading — [Databento pricing](https://databento.com/pricing); [unit prices docs](https://databento.com/docs/api-historical/metadata/metadata-list-unit-prices); [OPRA plans blog](https://databento.com/blog/introducing-new-opra-pricing-plans)
- **Massive (formerly Polygon.io, rebranded late 2025):** options are billed separately from stocks. The entry tier is delayed, and real-time options begin around the $199/month Advanced tier. Third-party price lists conflict; check massive.com/pricing — [apicostcalc](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html); [FlashAlpha](https://flashalpha.com/articles/options-data-pricing-comparison-flashalpha-thetadata-polygon-spotgamma-squeezemetrics)
- **OptionMetrics IvyDB:** the academic and institutional standard (via WRDS). I found no public 2026 price; it is generally sold under institutional licenses. Not verified.
- **Alpaca:** history from February 2024 only — [Alpaca docs](https://docs.alpaca.markets/docs/historical-option-data)

### Inferences: backtesting without fooling yourself
- **Fill at bid/ask, not mid.** Sell at the bid and buy at the ask, or at most use mid plus about 25–50% of the half-spread for patient limit orders. That range fits Muravyev-Pearson's finding that traders who time executions get roughly 40–67% of conventional costs.
- **EOD snapshot timing:** ORATS takes its near-EOD quotes about 14 minutes before the close. Pairing those quotes with the 4:00pm stock close mismatches the underlying price against the option prices. Use the underlying price stored in the same snapshot.
- **Contract survivorship:** build each day's chain from that day's snapshot, including contracts that have since expired or were adjusted after splits. Avoid reconstructing chains from a list of currently listed contracts. NVDA (10:1 in 2024), TSLA (5:1 2020, 3:1 2022), AMZN (20:1 2022), GOOGL (20:1 2022) and AVGO (10:1 2024) split during the window, so strikes must be split-adjusted consistently (UNVERIFIED split dates from memory).
- **Look-ahead in IV:** vendor IVs and Greeks are often computed using that day's close or a fitted surface that includes later data. Use only quantities observable at decision time, such as IV from your own calculation on quotes available then. Earnings dates must be the dates known as of each day.
- **Early exercise and dividends:** model assignment for American short calls when extrinsic value falls below the dividend, and for deep-ITM puts. At expiry, model a close-out cost instead of settlement at intrinsic value.
- **Liquidity filter:** require open interest and volume thresholds, and skip contracts quoted with a zero bid.

### Gaps
- OptionMetrics IvyDB pricing for 2026 was not found.
- Massive (Polygon) options history depth and official prices were not confirmed from the primary page.
- historicaloptiondata.com prices conflict between its own pages.
