# 1. Data sources (data-engineer view) — 2026-11-23

Goal: free or under-$50/month data, point-in-time, 2016/2018+, S&P 500 coverage, daily refresh, scriptable, that adds information beyond daily OHLCV.

Legend: **VERIFIED** = I called the endpoint today (2026-11-23) and saw the response. **DOC** = read in documentation or known from prior knowledge, not called. All SEC calls used User-Agent "Mozilla/5.0 (research script)".

---

## 1. SEC EDGAR submissions API (filing timestamps: 8-K item 2.02, 10-Q, 10-K, Form 4 …)

- Endpoint: `https://data.sec.gov/submissions/CIK##########.json` (10-digit zero-padded CIK). Older pages: `CIK##########-submissions-001.json`.
- VERIFIED (AAPL, CIK 320193): HTTP 200, 164 KB. Fields: accessionNumber, filingDate, reportDate, **acceptanceDateTime** (to the second, UTC "Z"), form, **items** (e.g. "2.02,9.01"), primaryDocument, isXBRL. The "recent" block holds 1,005 filings back to 2015-10-07; the overflow file covers 1994-2015. 46 AAPL 8-Ks with item 2.02 found, e.g. 2016-01-26T21:31:06Z, 2026-11-02T21:30:23Z.
- Point-in-time: YES, and the best one available. acceptanceDateTime is the moment EDGAR accepted the filing. Note it is UTC: 21:30Z = 16:30 ET in winter (after the close) — convert with tz, and an 8-K accepted after 16:00 ET belongs to the NEXT session's tradable information.
- Caveat: the 8-K 2.02 is usually filed minutes after the press release (wire). Timing is good to "same evening", not to the second of the news.
- Coverage: every SEC registrant, so all S&P 500. Ticker→CIK map is needed (see trap below).
- Rate limit / terms: SEC fair-access policy, max 10 requests/second, declared User-Agent required. Free, public domain.
- IMPORTANT VERIFIED QUIRK: `https://www.sec.gov/files/company_tickers.json` and `https://www.sec.gov/Archives/...` returned **403** with the generic UA; `data.sec.gov` returned 200. SEC's policy asks for a UA that contains a contact (company + email). The daily job will need a real contact UA for www.sec.gov paths (that's the user's call; I did not add any).
- Effort: 3-4 h. 500 calls/day at 5/s = under 2 min. Use it to build (a) an exact earnings-date calendar since 2016 (8-K 2.02 accept times), (b) days-since/until-earnings features, (c) filing-event flags (8-K items 1.01, 2.05, 5.02 CEO change, etc.).

## 2. SEC XBRL companyfacts / frames (fundamentals with filed dates)

- Endpoints: `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`; `https://data.sec.gov/api/xbrl/companyconcept/CIK…/us-gaap/{Tag}.json`; `https://data.sec.gov/api/xbrl/frames/us-gaap/{Tag}/USD/CY2019Q1.json`.
- VERIFIED: AAPL companyfacts 200, 3.9 MB, 512 us-gaap concepts. Each fact has start, end, val, accn, fy, fp, form, **filed**, frame. EPS diluted and NetIncomeLoss go back to fiscal 2007 (filed 2009). Frames call 200, 2,715 companies for Revenues CY2019Q1.
- Point-in-time: YES in companyfacts (each value appears once per filing that reported it, with its own `filed` date, so the first-reported and later restated numbers are both present — take the earliest `filed` per (concept, period) for an as-first-reported series). **Frames are NOT point-in-time**: they keep one value per company per period, the latest filed — restated. Do not backtest on frames.
- Traps seen: tag changes (AAPL "Revenues" only 11 rows, then RevenueFromContractWithCustomerExcludingAssessedTax from 2018 on, after ASC 606) — need a concept fallback list per field. Q4 is not reported as a quarter (derive FY minus 9M). `filed` is a date, not a time: join on the 10-Q/10-K acceptanceDateTime from the submissions API to get the time.
- Coverage: all filers since ~2009 XBRL. Bulk: `https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip` (DOC; ~1 GB+, www path → needs contact UA).
- Rate limit / cost: as above, free.
- Effort: 6-10 h (concept mapping, Q4 derivation, first-reported logic). Gives standardized unexpected earnings (SUE from seasonal random walk), accruals, asset growth, gross profitability, share issuance — the classic anomaly inputs, all point-in-time.

## 3. SEC Form 4 insider trades, 13F, fails-to-deliver, full-text search

- Form 4 filings appear in the submissions API (VERIFIED: 598 Form 4 rows for AAPL in the "recent" block, each with acceptanceDateTime). Trade details (role, shares, price, code P/S/A/M) are in the XML under `https://www.sec.gov/Archives/edgar/data/{cik}/{accn}/` or the quarterly "Insider Transactions Data Sets" (DOC, 2003+).
- Fails-to-deliver: `https://www.sec.gov/files/data/fails-deliver-data/cnsfailsYYYYMMa.zip` returned **403 with the generic UA (not verified)**. DOC: twice-monthly, ~2-week lag, by CUSIP + ticker. Fails are tiny for large caps; low priority.
- 13F: quarterly, 45-day lag, by CUSIP. Low priority for 1-21 day horizons.
- Full-text search `https://efts.sec.gov/LATEST/search-index?...` VERIFIED 200 (2001+ per docs). Keyword events; not needed first.
- Point-in-time: YES (acceptance times). Free. Blocker: every www.sec.gov path needs a contact-bearing UA (verified 403 without one).
- Effort: Form 4 open-market purchases (code P) by officers/directors: 6-8 h (XML parsing, amendments; 10b5-1 flag exists only from 2023). Insider purchases predict, sales mostly don't; in large caps purchases are rare, so the signal is sparse.

## 4. FINRA Reg SHO daily short-sale volume

- Endpoint: `https://cdn.finra.org/equity/regsho/daily/CNMSshvolYYYYMMDD.txt` (consolidated, all FINRA TRFs + ORF).
- VERIFIED: 2026-11-20 file 200; AAPL ShortVolume 10,861,139, ShortExempt 35,576, TotalVolume 21,590,114, Market "B,Q,N". CNMS files exist from 2018-08-01 (200); the 2016-01-04 CNMS file is 403 (does not exist).
- Pre-Aug-2018: per-facility files. VERIFIED 200 for `FNSQshvol20160104.txt` (Nasdaq TRF; AAPL 7,836,303 short of 18,109,841) and `FNYXshvol20160104.txt` (NYSE TRF); `FNQCshvol`/`FNRAshvol` for that date 403. For 2016-2018 sum the per-facility files; the facility set changes over time, so expect a level break in Aug 2018. Use per-stock z-scores vs the stock's own 60-day history.
- Only off-exchange (TRF/ORF) volume, about 40-50% of total; "short" includes market-maker hedging, so ratios sit near 40-55% for everyone. The signal is the abnormal change, not the level.
- Point-in-time: YES; published same evening (DOC, ~18:00 ET). Coverage: all NMS stocks. No key, no stated rate limit; one ~1-2 MB file a day. Free.
- Effort: 2-3 h (+1 h for the pre-2018 stitch).

## 5. FINRA equity short interest (twice monthly)

- Endpoint: `POST https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest`, JSON body `{"limit":5000,"compareFilters":[{"compareType":"equal","fieldName":"symbolCode","fieldValue":"MSFT"}]}`. Works **without a key** (VERIFIED).
- VERIFIED fields: settlementDate, currentShortPositionQuantity, previousShortPositionQuantity, averageDailyVolumeQuantity, daysToCoverQuantity, changePercent, revisionFlag, stockSplitFlag. MSFT: 213 rows, earliest settlement **2017-12-29**, latest 2026-10-30 (the 2026-11-14 settlement is not yet out, i.e. ~7 business-day lag). Sorting server-side returns 400 unless partition keys are given — filter by symbol or by settlementDate (all symbols) and sort locally.
- Point-in-time: PARTLY. Records carry the settlement date, NOT the publication date. Publication is ~7-8 business days later (FINRA calendar). Lag each record to its dissemination date (conservatively settlement + 10 business days). revisionFlag marks corrections; keep first-seen values going forward.
- Coverage: exchange-listed + OTC. 2016-2017 not in this API (before FINRA took this over, exchanges published it). From 2018 meets the bar.
- Rate limit: not stated for unauthenticated public datasets; 5,000 rows per synchronous request (DOC). Free.
- Effort: 3 h. Features: SI / shares outstanding (dei:EntityCommonStockSharesOutstanding from XBRL), days to cover, change. Documented modest negative predictor at monthly horizons.

## 6. Nasdaq earnings calendar (unofficial JSON endpoint)

- Endpoint: `https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD` (browser-like UA + `Accept: application/json`).
- VERIFIED: past dates return symbol, name, time ("time-pre-market" / "time-after-hours" / "time-not-supplied"), **eps (actual), epsForecast (consensus), surprise %, noOfEsts**, fiscalQuarterEnding, marketCap. 2016-04-26 works: 149 rows, AAPL eps $1.90 vs consensus $1.97, surprise -3.55%, 15 estimates; 2026-10-29 AMZN $1.89 vs $2.01. Future dates (2026-11-25) return consensus, # estimates, last year's EPS and report date, and time of day. `api/analyst/AAPL/earnings-surprise` returned 404.
- Point-in-time: MIXED. Announcement date: yes. Consensus/actual: plausibly as of the announcement (the 2016 AAPL $1.97 is close to the consensus of the time as I recall it) but undocumented (Zacks-sourced; could be revised). **marketCap is today's** (AAPL shows $4.98 T on the 2016 page) — never use it. "time" is mostly "not supplied" for old dates — take timing from the SEC 8-K 2.02 acceptance time.
- Coverage: all US listings with estimates; S&P 500 essentially complete.
- Terms: undocumented endpoint behind nasdaq.com; site terms restrict automated use and redistribution. One request a day for personal research is low-risk but not clearly permitted; it can break or be blocked without notice. Free.
- Effort: 3 h for a 2016-2026 backfill (~2,700 daily calls at 1/s) + 1 h daily job. Gives analyst-consensus surprise for post-earnings drift (PEAD), the strongest earnings anomaly available for free; also "earnings within N days" flags.

## 7. Alpaca news, corporate actions, options (account already exists)

- News: `GET https://data.alpaca.markets/v1beta1/news?symbols=AAPL&start=...` (DOC). Benzinga-sourced, **history back to 2015** (Alpaca docs: "historical news data dating back to 2015"). Fields id, headline, summary, author, created_at, updated_at, symbols, source. NOT VERIFIED live (needs the project key; instructed not to use keys). created_at is the publish time, so point-in-time yes (use created_at, never updated_at). Rate limit 200 req/min on the free plan (DOC); 50 articles per page. Benzinga headlines include analyst upgrades/downgrades/price-target changes, so headline tagging gives a free **analyst-revision proxy**. Effort 6-10 h (paginated backfill of a few hundred thousand articles, dedupe, keyword/sentiment tags). Terms: included with Alpaca data for account holders.
- Corporate actions: `GET https://data.alpaca.markets/v1/corporate-actions` (DOC): splits, dividends, mergers, symbol changes with dates — mainly the **ticker-change map**. 2 h.
- Options: historical option data only **since February 2024** (DOC, Alpaca "Historical Option Data" page). Too short for a 2016+ backtest; could start archiving per-stock put/call volume or IV forward now for a later test.

## 8. Wikipedia pageviews API

- Endpoint: `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Apple_Inc./daily/20150701/20151231`.
- VERIFIED: 200; Apple_Inc. 2015-07-01 = 11,551 views. Data starts **2015-07-01** (API floor).
- Point-in-time: YES (daily counts final; available next morning UTC). Days are UTC, so day t's count is known before day t+1's open but not at day t's close: lag one day.
- Coverage: needs a hand-built ticker-to-article map (~500 titles); renames (Facebook -> Meta Platforms) break series because the API counts the exact title, not redirects. Rate limit generous with a descriptive UA (DOC ~100 req/s); free, CC0.
- Effort: 4 h (mostly the title map). Attention signal; published evidence is modest (abnormal attention -> short-term reversal / higher volatility).

## 9. Free tiers of commercial APIs (DOC only — all need a key, none called)

- Finnhub free: 60 calls/min (several sources); free earnings-surprise endpoint returns only the last few quarters; estimates/revisions are premium. Not enough history.
- Financial Modeling Prep free: ~250 calls/day, limited history and symbol set; historical earnings surprises/estimates in paid tiers (~$19-29/mo). Cheapest paid path to earnings-estimate history; consensus is a current snapshot, not a revision history.
- Alpha Vantage free: 25 calls/day; EARNINGS endpoint gives reportedDate, reportedEPS, estimatedEPS, surprise per quarter for many years. 500 symbols = 20 days of free calls to backfill, or ~$50/mo tier. Same "estimate as of when?" caveat.
- Tiingo free: ~1,000 req/day, 500 unique symbols/month; news and full fundamentals are add-ons.
- Polygon (Massive) free: 5 calls/min, ~2 years of history. Too short.
- EODHD free: 20 calls/day; fundamentals/estimates in paid tiers ($20+/mo).
- Verdict: nothing free beats Nasdaq + SEC for earnings; Alpha Vantage or FMP are fallbacks if the Nasdaq endpoint dies. None gives a point-in-time history of estimate revisions (that is I/B/E/S, institutional pricing). These free-tier numbers are from memory and third-party pages, not checked today.

## 10. Other candidates checked

- **FRED** (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=...`, no key): VERIFIED 200. Market-wide only. Trap seen: BAMLH0A0HYM2 (HY spread) now returns data only from 2023-11-24 (ICE licensing cut the history). For point-in-time macro use ALFRED vintages (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=2020-01-10` VERIFIED 200). Regime conditioning only.
- **Ken French data library**: VERIFIED 200 (5-factor daily zip, 150 KB). Monthly updates with a lag; for evaluation/risk-adjustment, not a stock feature.
- **Open Source Asset Pricing (Chen-Zimmermann)**: page VERIFIED 200; DOC: release 2026.10, 212 predictors, parquet on Hugging Face, no account needed, most data end **Dec 2025**, option-based ones end 2022, keyed by CRSP permno (ticker map needs CRSP). Annual refresh, so not a daily feed. Use as a **prior** for which signals to rebuild from SEC data, and to validate our versions.
- **CBOE**: VIX history VERIFIED (1990-01-02 to 2026-11-20). Total put/call CSV VERIFIED but the archive **ends 2019-10-04**, market-level only. No free per-stock option-volume history from CBOE/OCC (OCC only has an interactive query tool, DOC). Skip.
- **GDELT DOC API**: VERIFIED (timelinevol for "Microsoft", 15-minute resolution) but hit **429, 1 request per 5 s**; DOC window ~2017+. Company-name queries are noisy (Apple, Amazon). Low value per hour.
- **Google Trends**: no official API; pytrends scraper, heavy rate limiting, values re-scaled and re-sampled per request (not reproducible), daily only for windows under ~9 months. Fails point-in-time. Skip. (Not called.)
- **ETF holdings/flows**: issuer files show only today's holdings, no history; flows need shares-outstanding history (paid). Skip; could archive forward.
- **S&P 500 membership history** (needed for survivorship, not a signal): Wikipedia "List of S&P 500 companies" change table or the public GitHub dataset fja05680/sp500 (DOC, not called).

---

## Ranked top five for this project

1. **SEC EDGAR submissions API** — exact acceptance timestamps (to the second) for every 8-K 2.02 earnings release, 10-Q/10-K, 8-K event item and Form 4 since 1994; official, free, point-in-time by construction. Backbone for event features and for timing every other source. (3-4 h)
2. **Nasdaq earnings calendar endpoint** — free consensus EPS, actual EPS, surprise %, # estimates back to 2016, plus forward dates; enables analyst-surprise drift and pre-earnings flags. Risks: unofficial/terms; estimate vintage undocumented. Cross-check dates against #1. (4 h)
3. **SEC XBRL companyfacts (first-reported values)** — point-in-time fundamentals (seasonal-random-walk SUE, accruals, asset growth, profitability, net issuance) with filed dates; also shares outstanding for short-interest ratios. (6-10 h)
4. **FINRA short interest + daily short-sale volume** — short positioning; free, no key; SI from 2017-12, daily short volume from 2016 (stitched pre-Aug-2018). SI must be lagged to its publication date. (5-6 h together)
5. **Alpaca news (Benzinga, 2015+)** — already covered by the existing account; timestamped headlines give news-volume/attention and analyst up/downgrade events. Not verified live (key needed). Runner-up: Wikipedia pageviews (verified, 2015-07+, free) as the attention proxy.

## Traps

**Restated data**: XBRL frames and most fundamentals APIs return the latest restated value — always take the earliest `filed` per period from companyfacts; consensus numbers from Nasdaq/Alpha Vantage/FMP may have been revised and nobody documents the vintage; Nasdaq's historical marketCap is today's. **Timestamps after the close**: SEC acceptanceDateTime is UTC (21:30Z = 16:30 ET in winter, 20:30Z = 16:30 ET in summer); most earnings 8-Ks land after 16:00 ET, so that information belongs to the next session — a feature for day t may only use records accepted before 16:00 ET on t. Short interest is dated by settlement but published ~7-8 business days later; Wikipedia days are UTC. **Survivorship**: the universe must be the S&P 500 as it was on each date, and delisted names' filings and short data must be kept — fetching only today's 500 CIKs silently drops the losers. **Ticker changes**: key everything on SEC CIK, not ticker (FB->META; GOOG/GOOGL two tickers one CIK; BRK.B vs BRK-B vs BRK/B formats differ across FINRA, Nasdaq, Alpaca). FINRA and Nasdaq use the ticker of the day, so a dated ticker-to-CIK map (Alpaca corporate actions + SEC) is required. **Access**: every www.sec.gov path (ticker map, Archives, FTD, bulk zips) returned 403 to the anonymous UA; data.sec.gov did not. A daily job touching www.sec.gov needs a UA with a real contact address, which is the owner's decision.

