# Short interest dataset: how it was built and what to watch

Built 2026-11-23 by `short_interest_data.py`. Output: `lab/short_interest.csv`.

## The short version

- 103,694 rows: 503 of 503 companies in `lab/universe.csv`, 213 reporting dates from 2017-12-29 to 2026-10-30. That is 24 dates a year (one in 2017, 20 so far in 2026).
- Every number comes from FINRA's free Query API. No key was needed, and FINRA refused nothing.
- The API has **no publication-date field**. The `published` column comes from FINRA's own published schedule pages, read for every year back to 2017. All 213 dates were found there, so the "settlement + 9 business days" stand-in was never used. Every row is marked `published_source = schedule`. No row is marked `finra`, because no FINRA data source states the date itself.
- Publication always fell **7 trading days after the settlement date**: 9 to 12 calendar days, typically 11.
- Spot checks: 9 of 10 independent public figures match exactly or to the stated rounding. The tenth is a 2019 press figure that is 6% lower.

## Source and the exact request

```
POST https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest
Accept: application/json
{"limit": 5000,
 "domainFilters":  [{"fieldName": "symbolCode", "values": ["AAPL", "MSFT", ...all 503...]}],
 "compareFilters": [{"compareType": "equal", "fieldName": "settlementDate", "fieldValue": "2026-10-30"}]}
```

- This returns one reporting date for the whole list in a single call (about 1 second).
- The list of dates comes from the same endpoint, filtered to AAPL, MSFT and SPY. The daily job adds a `"compareType": "greater"` filter on `settlementDate`.
- Single tickers work too, for example `{"compareFilters":[{"compareType":"equal","fieldName":"symbolCode","fieldValue":"MSFT"}]}`. For MSFT that returns 213 rows from 2017-12-29.
- Sorting is refused (HTTP 400) unless `settlementDate` is fixed with an `equal` filter, so the script does not sort on the server.
- Asking for `text/plain` returns CSV.
- The same data is also in bi-monthly files at `https://cdn.finra.org/equity/otcmarket/biweekly/shrtYYYYMMDD.csv`. Those exist from `shrt20171229.csv` onward; earlier dates return 403.
- Requests use a generic browser User-Agent, run at most about 2.5 per second, and retry with backoff.

**History before 2017-12:** none was found in FINRA's free sources. Both the API and the CDN files start at 2017-12-29. FINRA's own pages say that, historically, short interest for exchange-listed stocks was passed to the listing exchanges (NYSE, Nasdaq), which published it. Older history would have to come from those exchanges' own (generally paid) files. Nothing unofficial was added.

## Publication date: exactly what was done

1. **The data has no such date.** The dataset's metadata (`GET https://api.finra.org/metadata/group/otcMarket/name/consolidatedShortInterest`) lists the fields:
   - `settlementDate` and `accountingYearMonthNumber`
   - share quantities, `averageDailyVolumeQuantity`, `daysToCoverQuantity`
   - `revisionFlag`, `stockSplitFlag`

   None of them is a publication or dissemination date.
2. **FINRA's schedule pages.** The "Short Interest Reporting Dates" tables list, for each period, the settlement date, the due date and a third date:
   - 2017-2020 tables call it "Exchange Receipt Date";
   - 2021 onward call it "Publication Date".

   `www.finra.org` answers scripts with HTTP 403 (Cloudflare), so the script reads FINRA's page through the Internet Archive (`https://web.archive.org/web/<date>id_/<finra url>`). It reads 31 captures, 2017-03 to 2026-07, across the three addresses the page has had:
   - `/industry/short-interest/short-interest-reporting-due-dates`
   - `/filing-reporting/short-interest`
   - `/filing-reporting/regulatory-filing-systems/short-interest`

   These are copies of FINRA's own page, not a third-party schedule. The script parses each year's table. Where captures disagree, the latest capture wins. That happened once: for 2021-12-15, the 2020 capture said 2021-12-24 and all later captures said 2021-12-27 (Dec 24 became a holiday). 875 table rows were parsed, covering 240 settlement dates from 2017-01-13 to 2026-12-31. Raw pages are cached in `data/short_interest/schedule/`, and every parsed row is in `parsed_all.csv` there.
3. **Fallback.** For any date missing from the tables, use settlement + 9 business days (US federal holiday calendar). It was not needed here. In all 213 periods the fallback would have been on or after the real date, so it is conservative.
4. **Check that the date is real.** On 2026-11-23, the API had no rows for the 2026-11-13 settlement, whose scheduled publication date is 2026-11-24. The API does not show data before its schedule date.

**Lag:**

| What | Result |
|---|---|
| Settlement to publication | 7 trading days in every one of the 213 periods |
| In calendar days | 9 to 12, median 11 |
| Counted with federal holidays | 7 business days in 197 periods. The 6s fall on Columbus Day and Veterans Day (markets open); the 8s around Good Friday (markets closed). |
| Firms' filing deadline | 2 business days after settlement, 6 p.m. ET |

The schedule gives a date, not a time of day. Treat the figure as known after the close on `published`, and trade on it from the next session.

**Weaknesses:**
- The archive's latest capture of the live schedule page is from 2019. Today's page (2026-11 and all of 2027, checked by hand) is not in the archive yet. The 2026-07 capture covers dates through 2026-12-31. For 2027 periods, the daily job will use the +9 business-day stand-in unless the archive captures the page again. The stand-in is still marked "schedule", as the brief asked; to tell the two apart, compare against `parsed_all.csv`.
- FINRA has proposed weekly reporting with faster publication (SR-FINRA-2026-012). If approved, the stand-in would be too late and the period list would double. The code takes its periods from the API, so it will still pick them up.

## Columns

| Column | Meaning |
|---|---|
| `ticker` | as written in `lab/universe.csv` (BRK.B, BF.B) |
| `settlement_date` | the day the short positions are counted |
| `published` | the day FINRA's schedule says the figure became public |
| `short_interest` | shares sold short |
| `avg_daily_volume` | FINRA's average daily volume for the cycle |
| `days_to_cover` | FINRA's figure. FINRA sets it to **1.00 whenever short interest is below one day's volume** (2,036 rows). It would be blank wherever volume is 0; no row has zero volume. |
| `published_source` | `schedule` for all rows |
| `finra_symbol` | the symbol FINRA used on that date. This is an addition to the brief; see ticker changes below. |

## Spot checks against independent public figures

| Company | Settlement | This file | Independent figure | Source | Result |
|---|---|---|---|---|---|
| TSLA | 2026-06-30 | 79,109,257 (published 2026-07-10) | 79,109,257, listed with date 07/10/2026 | Benzinga quote page (search excerpt) | exact, date too |
| TSLA | 2026-07-15 | 70,646,375 | 70.6M | Curved Trading | match |
| TSLA | 2019-06-14 | 41,459,902 | 41.5M ("latest official data") | Seeking Alpha | match |
| TSLA | 2019-10-15 | 37,186,793 | almost 37.2M | Fortune, quoting Interactive Brokers | match |
| TSLA | 2020-01-15 | 24,954,265 | 24.9M | S&P Global / IHS Markit | match |
| TSLA | 2019-11-15 | 30,614,501 | 28.8M | Securities Finance Times | **6% off**; not explained, possibly a different cut of the data or an error in the article |
| AAPL | 2026-04-15 | 134,422,787, days to cover 3.39 | 134.4M, 3.39 | OptionsAnalysisSuite | match |
| AAPL | 2026-04-30 | 134,675,274, days to cover 2.93 | 134.7M, 2.93 | Equibles | match |
| AAPL | 2026-07-15 | 146,547,784, days to cover 3.06 | 146.5M, 3.06 | Curved Trading | match |
| CVNA (heavily shorted member) | 2026-05-29 | 72,224,125, volume 11,091,307, days to cover 6.51, published 2026-06-09 | the same four numbers, listed with date 06/09/2026 | Benzinga | exact |

The TSLA 2019 figures are counted before Tesla's 2020 and 2022 splits. That confirms the share counts are **not split-adjusted**.

The third-party numbers were read from search-result excerpts of those pages. They are secondary copies of the same FINRA/exchange data, not separate measurements.

## Gaps and ticker changes

**Missing companies:** none. All 503 have data.

**Missing periods:**
- None in the middle of any company's history.
- Rows per date range from 463 to 503 (median 490).
- 40 companies start after 2017-12-29 because they listed or were spun off later. The latest starters are EVRG, KDP, VRT, LIN, MRNA, DELL, FOX/FOXA, DOW, UBER, DD, OTIS, CARR, PLTR, ABNB, COIN, CEG, GEHC, GEV, SNDK, Q, FDXF, HONA and VYLR (first date 2026-10-15).
- Each starts at its first FINRA date.
- No new listing is carried back through a merger or spin-off: DD from DowDuPont, LIN from Praxair, VTRS from Mylan and KDP from Dr Pepper Snapple all start fresh.

**Ticker changes are handled automatically.** When a company changes symbol, FINRA's first row under the new symbol reports a "previous short position", which is the last figure under the old symbol. The script asks the API for the one row on the prior date with exactly that share count, which names the old symbol, then pulls the old symbol's earlier history. 3,049 rows (2.9%) came from another symbol; `finra_symbol` shows which. Examples:
- FB to META
- SQ to XYZ
- ANTM to ELV
- MMC to MRSH
- FLT to CPAY
- PKI to RVTY
- UTX to RTX
- IR to TT
- SYMC to NLOK to GEN
- AAXN to AXON
- IIVI to COHR
- PSTG to P
- ABC to COR
- SATS to ECHO
- BK to BNY
- EQR to VMRK
- PSKY to SKYD

There are 33 renames in all, plus 10 gaps filled the same way. For example, Fiserv traded as FI from 2023-06 to 2025-10, between two spells as FISV.

**Reused symbols are cut.** Where a ticker earlier belonged to a different issuer, the earlier rows are dropped. The rule: the issuer name, the symbol or the continuity changes, and FINRA's previous-position figure does not link up. There were 12 such tickers, for example:
- META was a Roundhill ETF until 2022-01;
- P was Pandora;
- MRNA was Marina Biotech;
- WTW was Weight Watchers;
- GEN was Genesis Healthcare;
- FOX/FOXA were the old Twenty-First Century Fox;
- COHR was the old Coherent before II-VI took the name;
- Chesapeake (EXE) shares before the 2020-21 bankruptcy were cancelled, so EXE starts at 2021-02-12.

Every decision is listed in `data/short_interest/last_run.json`.

**Splices to check by hand:**
- VRT carries its SPAC history (GSAH, 2018-08 to 2020-01).
- CEG has one when-issued row (CEGVV, 2022-01-31).

Both are the same shares before the event, but some users may want them removed.

**Revisions:**
- In 2,518 cases (2.5% of rows), FINRA flagged that the prior period's figure was revised.
- The median revision is 0.02%.
- The API keeps the **originally published** figure for the earlier date: the revised figure only appears as "previous" on the next row. So the file is point-in-time with respect to revisions too.

## Short interest as days of average volume, latest date (2026-10-30, 503 companies)

| | Short interest ÷ avg daily volume | FINRA days to cover |
|---|---|---|
| 10th percentile | 1.91 | 1.91 |
| 25th percentile | 2.48 | 2.48 |
| median | 3.32 | 3.32 |
| 75th percentile | 4.65 | 4.65 |
| 90th percentile | 6.04 | 6.03 |
| max | 14.97 (LYV) | 14.97 |
| min | 0.56 (SNDK) | 1.00 (floor) |

The highest after LYV:
- TPL 14.0
- BF.B 13.0
- TROW 12.6
- FOX 11.7
- ERIE 11.6
- KMB 11.6
- UNP 11.5

The two columns agree except at the low end, where FINRA floors days to cover at 1.

## Run times (this machine, from scratch)

| Run | Time | What it does |
|---|---|---|
| Full rebuild, no cache | 334 s | 213 period requests, about 40 archive pages, about 60 rename lookups |
| Full rebuild from cache | 21 s | |
| Daily update with one new period, no cache (as in a GitHub job) | 6 s | |
| Daily update with nothing new | 1 s | |
| Daily update where the stock list gained a member | about 60 s | fetches that ticker's whole history and the full schedule |

An update that dropped the last two dates and added them back produced a byte-identical file to the full rebuild. The cache in `data/short_interest/` (51 MB) is git-ignored.

## Traps

1. **Publication lag.** Join on `published`, not `settlement_date`. A signal dated by settlement date sees the number 9 to 12 calendar days early. Treat it as known after the close on `published`.
2. **No percent of float.** Shares outstanding and float are not in this file. "Short interest as a percent of float" needs a separate, point-in-time share count, for example from SEC filings.
3. **Today's members only.** The list is the current S&P 500. Companies that left the index (acquired, bankrupt, demoted) are absent. Back-tests on this file have survivorship bias.
4. **No split adjustment.** Share counts are as reported (TSLA before 2020 is in pre-split shares). Compare a company's short interest over time as a ratio to volume or to shares outstanding from the same date, not as raw counts across a split.
5. **Days-to-cover floor.** FINRA's `days_to_cover` is never below 1.00.
6. **Spliced histories.** Renamed companies carry their old symbol's rows; check `finra_symbol` if that matters.
