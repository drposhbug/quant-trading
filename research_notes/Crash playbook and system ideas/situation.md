# Current-situation desk: fact sheet for the crash playbook

As of Saturday 2026-11-21, about 01:15 ET. Prices are Friday's close; crypto and prediction markets were read at 05:51–05:56 UTC. Futures reopen Sunday 18:00 ET. "[calc]" is my calculation from the tagged data (scripts in `C:\Users\tyler\AppData\Local\Temp\claude\28f7d7c4cc43e090\18bb9d78-57a2-4803-a7fe-5a5825765403\scratchpad\storm\situation\`). The shared web-search budget ran out part-way; gaps are listed at the end.

**Sources.**
[TS] [TheStreet close wrap](https://pro.thestreet.com/market-commentary/the-sp-500s-worst-week-since-april-2025-ends-in-a-correction) ·
[ST] [Stocktwits wrap](https://finance.yahoo.com/markets/stocks/articles/nasdaq-100-ends-worst-week-013025833.html) ·
[RT] [Reuters on the SEC](https://live.euronext.com/en/financial-news/nvidias-accounting-focus-us-sec-investigation-sources-say) ·
[CN] [CNBC](https://cnbc.com/2026/11/20/nvidias-7-week-losing-streak-is-longest-since-2008-financial-crisis.html) ·
[IN] [InvestmentNews](https://www.investmentnews.com/equities/embattled-nvidia-faces-sec-probe-as-california-attorney-general-mulls-action/269054) ·
[LB] [10-Q delay](https://longbridge.com/news/305948432) ·
[DC] [Reuters on data centres](https://investing.com/news/world-news/trump-says-us-to-penalize-firms-building-data-centers-abroad-5042390) ·
[FS] [FactSet Earnings Insight, 20 Nov](https://advantage.factset.com/hubfs/Website/Resources%20Section/Research%20Desk/Earnings%20Insight/EarningsInsight_112026.pdf) ·
[TK] [TradingKey](https://www.tradingkey.com/analysis/stocks/us-stocks/262300737-nvidia-stock-nvda-forward-pe-drops-11-7x-hitting-15-year-low-tradingkey) ·
[SIB] [Siblis](https://siblisresearch.com/data/nasdaq-100-pe-ratio/) ·
[Y] [Yahoo Finance quotes and option chains](https://finance.yahoo.com/quote/QQQ/) ·
[F] [FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2) (also BAMLC0A0CM, BAMLH0A3HYC, DGS2, CPIAUCSL, UNRATE, A191RL1Q225SBEA, VIXCLS) ·
[PM] [Polymarket public API](https://gamma-api.polymarket.com/public-search?q=fed%20decision%20december) ·
[KX] [Kalshi public API](https://api.elections.kalshi.com/trade-api/v2/events?series_ticker=KXFEDDECISION&status=open&with_nested_markets=true) ·
[CB] [Coinbase spot](https://api.coinbase.com/v2/prices/BTC-USD/spot) ·
[FINRA] [margin statistics](https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics) ·
[AAII] [survey](https://www.aaii.com/sentimentsurvey) ·
[FOMC] [Fed calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) ·
[BLS] [jobs](https://www.bls.gov/schedule/news_release/empsit.htm), [CPI](https://www.bls.gov/schedule/news_release/cpi.htm) ·
[NYSE] [hours](https://www.nyse.com/trade/hours-calendars) ·
[AVGO] [Broadcom IR](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026) ·
[OPB] [midterms](https://www.opb.org/article/2026/11/04/2026-midterms-democrats-win-the-senate/)

## Findings

1. **Nothing has been resolved since the close.** Reuters says SEC enforcement staff are examining Nvidia's accounting; it could not establish the issues, and neither side commented [RT]. Nvidia has not filed its 10-Q, which it normally files with earnings; the 40-day deadline is about 4 December [LB, calc]. Treasury wants answers from the board within 10 days of about 17 November [IN]. Trump said on Friday he will tax US firms that build data centres abroad [DC]. Bitcoin is $55.8k, down 9.7% in 24 hours [CB].

2. **The economy is not the problem; the Fed is.** Q3 GDP grew 3.4% and unemployment is 4.1%. CPI is 4.1% year on year and 5.7% annualised over three months [F, calc]. A 25bp hike on 9 December is 92% priced on CME [TS] and 91% on Polymarket and Kalshi [PM, KX]. Hike pricing eased with the selloff (61bp through November 2027, from 86bp a week earlier) and bonds rallied on Friday [TS]. That is a brake on the Fed, not a pivot.

3. **Stocks are cheap only if forecasts hold.** The S&P 500 forward P/E was 17.1 at Thursday's close and is about 16.5 after Friday [FS, calc], against 19.8 (5-year) and 19.1 (10-year) [FS]. Nvidia is near 8 times forward earnings [CN]; a week earlier, 11.7 was already its lowest since 2011 [TK]. But consensus forward EPS is 2.1 to 3.8 times trailing EPS at Nvidia, Broadcom, Micron and AMD [Y, calc], and analysts already see S&P earnings growth falling from 33.7% in 2026 to 3.6% in Q2 2027 [FS]. Low multiples on peak forecasts are how cyclical tops look.

4. **Fear is extreme at the index, not across the market.** VIX is 35.9 with an inverted curve [Y] and the equity put/call ratio is 1.02 [TS]. Yet 49% of S&P members are above their 200-day average (technology 31%, health care 80%) [calc]. AAII bears fell to 42% on 18 November [AAII]. High-yield spreads are 352bp against 461bp at the April 2025 peak [F], and margin debt was 3.6% below its record at end-October [FINRA]. This is a sector crash with calm credit; a broad washout has not happened.

5. **Prediction markets agree with futures and options.** Fed odds match across three venues within two points. Kalshi's year-end S&P and Nasdaq-100 prices sit within about 4 points of probabilities I backed out of SPY and QQQ options, inside my estimation error [KX, Y, calc]. The one apparent gap is Polymarket's "AI bubble burst by 31 December" at 64%, against an option-implied 79–86% chance that Nvidia closes 50% below its record; an ambiguous rule on a third condition explains it [PM, calc]. Only the Fed markets are deep ($48m traded) [PM]. I found nothing to trade.

6. **The model's clock is slow by construction.** QQQ needs +12.3% to regain its 200-day average of 683.06 [Y, calc]. Options put QQQ above that level at 15% on 31 December, 30% on 19 March and 38% on 30 June. Another 10% fall is 18%, 23% and 27% (risk-neutral, at expiry) [calc]. The 5 and 20 November returns stay in the 60-session volatility window until 2 and 18 February 2027 [calc]. About two-thirds of the account earns the 4.1% bill rate [Y]. QQQ closed below its 200-day on 5–10 November, above on 11–12 and below since 13 [calc]; the brief dates the first break to 13 November.

7. **Three scenarios, no forecast.**
   - *Sharp recovery.* After the 17 earlier first closes of VIX at 35 or more since 1990, the S&P was higher a year later 14 times (median +21.6%), and the low came within five sessions in 9 [calc]. Earnings grew 32.9% [FS] and credit is calm. This overlaps the repo's failed VIX re-entry test: a base rate, not a rule.
   - *Range-bound grind.* The modal option outcome: QQQ between −10% and its 200-day level in March is about 47% [calc]. Kalshi gives 52% for a permanent Nvidia CEO before 1 March [KX].
   - *First leg of a bear.* The Fed is tightening after the first leg, the historian note's 3-of-3 marker. Five of the 17 VIX episodes fell at least 10% further (1990, 2002, 2008, 2020, 2022) [calc]. Nvidia has $118bn of data-centre guarantees [LB], CCC spreads are 1,361bp [F], and Kalshi prices a 2027 recession at 25% [KX].

## Evidence table

| Item | Value | Source |
|---|---|---|
| S&P 500 / Nasdaq-100 / QQQ | 6,910.39 (−11.6% from peak) / 25,028.98 (−19.8%) / 608.45 (10.9% below 200-day) | [Y] |
| VIX 9-day / 30-day / 3-month / 1-year | 40.7 / 35.9 / 30.9 / 27.6 | [Y] |
| 2-year / 10-year yield | 4.65% / 4.95%. The 2-year was 4.13% 126 sessions ago, so the review's tightening gate is on | [TS], [F] calc |
| High-yield / investment-grade / CCC spread, 19 Nov | 352 / 94 / 1,361bp (high yield 303bp on 6 Oct) | [F] |
| Week: HYG / IEF / TLT / gold / Brent | −0.8% / +1.8% / +2.6% / −9.5% / $92.57. Treasuries hedged; gold did not | [Y] |
| Breadth, week | 32 S&P members up, 470 down; median member 16% below its high | [calc], [TS] |
| Forward P/E (next fiscal year) | NVDA 7.6, ORCL 9.2, TSM 13.6, AVGO 15.7, META 15.7, GOOGL 17.3, MSFT 20.0, AMZN 22.6, AMD 24.1, AAPL 32.4, TSLA 160 | [Y] |
| Trailing P/E percentile, own 10 years | NVDA 0, GOOGL 0, AMZN 0, ORCL 1, META 19, MSFT 27, TSM 43, AMD 64, AVGO 80, AAPL 94 (the haven) | [calc] |
| Nasdaq-100 forward P/E | 21.24 on 31 Oct; about 18.7 now | [SIB], [calc] |
| Margin debt | $1,448bn in October; record $1,502bn in June | [FINRA] |
| Fed, 9 Dec | CME 92% hike. Polymarket: hold 0.082/0.084, +25bp 0.89/0.90. Kalshi: hold 0.08/0.09 | [TS], [PM], [KX] |
| Fed, 27 Jan; two hikes by March | Polymarket hike 0.49/0.50; Kalshi 0.78/0.79 | [PM], [KX] |
| Recession | 2026: Polymarket 0.039/0.040, Kalshi 0.01/0.02. 2027: Kalshi 0.25/0.26 | [PM], [KX] |
| S&P up on the year (close ≥ 6,845.5) | Kalshi 0.64/0.65; options 66% | [KX], [calc] |
| S&P touches 6,200 by year end | Kalshi 0.171/0.174; Polymarket 0.20/0.217; options 23–38% | [KX], [PM], [calc] |
| Anthropic closes below its $83 IPO price by 31 Dec | 0.79/0.81 (closed $88.91) | [PM], [ST] |
| Calendar, next week | 23 Nov Williams, $69bn 2-year. 24 Nov $70bn 5-year, Dell. 25 Nov PCE, GDP, Beige Book, $44bn 7-year. 26 Nov closed. 27 Nov 13:00 close. 28 Nov Fed blackout | [TS], [NYSE] |
| Calendar, after | 4 Dec jobs. 9 Dec Fed 14:00 with projections; Broadcom after the close. 10 Dec CPI. 18 Dec S&P rebalance. 24 Dec 13:00 close. 3 Jan Democratic Congress. 26–27 Jan Fed | [BLS], [FOMC], [AVGO], [PM], [OPB] |

## Ideas worth a pre-registered test (or why none)

No new predictive idea comes out of this desk, and I would not spend a trial here. Every gauge above is a level the repo has already tested as a signal (VIX, credit, valuation, prediction-market odds), and the cross-venue check found no gap wider than the spread. Four non-test actions follow:

1. **Keep the account and add a second baseline** ($94,975 and QQQ 608.45 on 20 November) rather than reset. A reset changes no future return and erases the execution record the paper year exists to collect. On Alpaca it also means a new paper account and new API keys [memory], so new secrets and new set-up orders in a holiday week with VIX at 36.
2. **Pin the calendar to the change-control rule:** no model decision between 4 and 10 December (jobs, the 10-Q deadline, the Fed and Broadcom on one day, then CPI).
3. **Check the half-day path.** 27 November is the first live 13:00 close, so the rebalance window becomes 12:30–13:00 ET. `monitor.py` reads Alpaca's clock for this and no test covers it.
4. **Write the tightening-gate rule into MATH.md now.** Its condition is true today, so data from here on is out-of-sample only if the rule is fixed before the outcome. Its chance of passing stays 5–8%.

## What I looked for and did not find

- Sunday futures (not yet open), and any Nvidia, SEC or Fed statement after Friday's close.
- Forward P/E history per stock. I used trailing P/E percentiles from Yahoo's reported EPS as a proxy. The Nasdaq-100 10-year median (22.9) appears only in a search snippet.
- Current CTA, volatility-control and buyback-blackout figures; Nasdaq-100 reconstitution dates; confirmed Oracle and Micron dates; the 20 November Fear & Greed reading; Kalshi's fee schedule; Cboe option chains (blocked, so I used Yahoo's closing quotes).
- Friday's high-yield spread (FRED stops at 19 November) and November margin debt (due mid-December).
- Any prediction-market price far enough from futures or options to cover fees.
