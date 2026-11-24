# Point-in-time profitability from SEC filings: what was built and how good it is

Built 2026-11-23. Module: `fundamentals_data.py`. Data: `lab/fundamentals.csv`. Raw cache: `data/fundamentals/` (git-ignored, about 126 MB of gzipped JSON).

## What it is

For each company in `lab/universe.csv` and each 10-Q and 10-K it filed since January 2015, one row says what its profitability looked like **on the day the report was filed**. Only numbers public by that day are used, and for each period the value is the **first** one the company reported. Later restatements never replace it.

Columns: `ticker, cik, filed, period_end, form, revenue_ttm, gross_profit_ttm, op_income_ttm, net_income_ttm, assets, equity, gp_assets, op_assets`. Money is in US dollars. `gp_assets` is trailing gross profit over total assets (Novy-Marx gross profitability). `op_assets` is trailing operating income over total assets.

- Source: the SEC "company facts" API, `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`. Each request sends the User-Agent "Mozilla/5.0 (research script)". The script waits at least 0.25 s between requests (at most 4 a second) and retries with exponential backoff. If it gets HTTP 403 twice it stops with an error instead of retrying. The SEC served every request; none were refused.
- `fundamentals_data.update()` refreshes every company and rewrites the CSV. A company's JSON is fetched again only if its cache file is more than a day old. `fundamentals_data.load()` returns the CSV with `filed` and `period_end` parsed as dates. The module needs only `requests` (and pandas for `load()`). It uses no API key.
- Size: **22,622 rows, all 503 tickers** (500 distinct CIKs, because GOOG/GOOGL, FOX/FOXA and NWS/NWSA share one each). By form: 16,976 10-Q, 5,642 10-K and 4 10-KT. Amendments (10-K/A, 10-Q/A) are not rows. They are later filings, so they could only add restated values.
- Run time:
  - Full run with an empty cache: **6 min 45 s** (503 downloads of about 0.3 to 4 MB each).
  - Rebuild from a fresh cache: **about 35 s**.
  - A GitHub Actions job starts with no `data/` folder, because it is git-ignored. Each daily run there is therefore a full download of about 7 minutes, unless the job caches `data/fundamentals/` between runs.

## Ticker to CIK

The CIKs come from the CIK column of the constituents table in the saved Wikipedia page `data/universe/wiki_current.html`. It was parsed with regular expressions; lxml and bs4 are installed, but they are not used, so the CI job does not need them. **All 503 tickers matched; none are unmatched.** Ticker dots and dashes are normalised (BRK.B, BF.B). The CI runner will not have the Wikipedia file, so `update()` also reads the ticker-to-CIK pairs already in `lab/fundamentals.csv`. A ticker added to the universe later gets no CIK until the Wikipedia cache is refreshed; `update()` reports it in `missing_cik`.

Two companies moved their filings to a new CIK. The predecessor's facts are merged into the new CIK's so their history continues; this is the `PREDECESSORS` table in the module:

- **XOM**: the Wikipedia CIK (2115436) is the new ExxonMobil Holdings Corp. It has filed only since mid-2026. Exxon Mobil Corp (34088) is merged in. Without it XOM had 2 rows and no trailing figures.
- **GOOG/GOOGL**: Alphabet (1652044) is merged with Google Inc. (1288776), the filer before October 2015.

Other companies whose history starts late are genuine new listings or spin-offs (for example KHC, HPE, DOW, OTIS, CARR, GEHC, GEV, SOLV, VLTO, HONA). Some may be a reorganisation like XOM's that I did not detect, because the SEC's www pages, which link a company to its predecessors, refuse this User-Agent. **The CIK column holds the ticker's current CIK on every row**, including rows that came from a predecessor.

## How the trailing twelve months are built

For each filing, the inputs are the facts filed on or before its `filed` date, with each (start, end) period taking its earliest-filed value.

1. **10-K:** the fiscal-year figure that ends on the period end (340 to 380 days long, so 52/53-week years count).
2. **10-Q:** year-to-date + the last fiscal year − the same year-to-date period a year earlier. Every 10-Q carries the year-to-date figure and its prior-year comparative. A 3-, 6- and 9-month value is told apart by its `start` and `end`.
3. **Fallback:** the sum of four single quarters. Each quarter is a direct 3-month figure, the difference of two year-to-date figures, or, for a fourth quarter, the year minus the first nine months.

Tag choice:

- The alternatives are tried in the order you gave. Names that this filing itself uses for its own period come first.
- For revenue and cost, the **largest** of the names the filing uses is taken first. This was needed: ADM, for example, tags total revenue as `Revenues` and only a component as `RevenueFromContractWithCustomerExcludingAssessedTax`. It also changed what the second name covers between 2024 and 2025. Taking the first name in the list gave a trailing revenue of −$7 billion.
- I added three fallback tags:
  - `RevenuesNetOfInterestExpense`, for banks' total revenue;
  - `CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization`, which excludes depreciation as Compustat's cost of goods sold does (used by KR, LIN, CTSH and others);
  - `NetIncomeLossAvailableToCommonStockholdersBasic` and then `ProfitLoss`, for net income.
- Equity falls back to the version that includes non-controlling interests when the parent-only tag is missing.
- If a company changed tags between years (common in 2018), the names are pooled as a last resort.

Gross profit is `GrossProfit` when tagged, otherwise revenue minus cost, with two exceptions where it is left empty:

- **Insurers, including managed care.** If they report material claims costs, their cost tag is only the cost of products sold. This applies to UNH, CVS, CI, ELV, CNC, L and AJG. UNH's "gross profitability" was 1.27 before this rule.
- **Mismatched tags.** If revenue minus cost comes out below operating income by more than 5% of revenue, the two tags do not cover the same business. Only 3 rows are affected (GD and SLB).

Banks have no cost of revenue, so their gross profitability is empty, as asked; nothing is invented.

## Coverage by year end

The table counts companies whose latest filing by that date covers a period that ended within the previous 200 days.

| as of | companies with a recent filing | revenue | net income | gp_assets | op_assets | both |
|---|---|---|---|---|---|---|
| 2015-12-31 | 441 | 369 | 437 | 248 | 334 | 217 |
| 2016-12-31 | 446 | 367 | 442 | 252 | 341 | 222 |
| 2017-12-31 | 454 | 370 | 443 | 258 | 343 | 229 |
| 2018-12-31 | 457 | 384 | 452 | 246 | 350 | 217 |
| 2019-12-31 | 472 | 458 | 467 | 278 | 359 | 240 |
| 2020-12-31 | 476 | 461 | 473 | 296 | 363 | 253 |
| 2021-12-31 | 484 | 467 | 477 | 299 | 366 | 252 |
| 2022-12-31 | 486 | 473 | 484 | 301 | 373 | 258 |
| 2023-12-31 | 489 | 475 | 486 | 300 | 374 | 258 |
| 2024-12-31 | 495 | 482 | 490 | 305 | 372 | 261 |
| 2025-12-31 | 500 | 487 | 496 | 313 | 380 | 270 |
| 2026-11-23 | 483 | 471 | 480 | 308 | 365 | 266 |

In plain terms:

- **Gross profitability exists for about 250 to 310 of roughly 490 companies.** **Operating profitability exists for about 335 to 380.**
- The gaps are mostly structural, not bugs:
  - 144 companies never have `gp_assets`. They are banks, insurers, asset managers, exchanges, utilities, REITs, railroads, airlines, hotels and casinos, media and cable (CMCSA, CHTR, DIS), and payment networks (V, MA). Their income statements have no cost-of-revenue line, only "costs and expenses".
  - 92 companies never have `op_assets`. They never tag `OperatingIncomeLoss`, because they show no operating-income subtotal. Examples: LLY, MRK, PFE, BMY, JNJ (in most years), IBM, CVX, XOM, COP, NKE, EMR, GE, plus the financials.
- Revenue is thin before 2019 (about 370 companies) for two reasons. Some companies used tags outside the list then (for example `SalesRevenueGoodsNet`; ROL, TSCO, AOS, SYY, WDC). Some banks tagged no total revenue (RF, BNY, MTB, FITB).
- The drop at 2026-11-23 is a source problem, covered under the traps below.

## Spot check against the 10-Ks

The reference figures are the totals on the face of each company's 10-K income statement and balance sheet. Ours are the rows written for those 10-Ks, using first-reported values on the filing date. All figures are $ millions.

| company, fiscal year | item | 10-K | ours | diff |
|---|---|---|---|---|
| AAPL FY2023 (Sep) | revenue / gross profit / operating income / net income | 383,285 / 169,148 / 114,301 / 96,995 | same | 0 |
| | assets / equity | 352,583 / 62,146 | same | 0 |
| MSFT FY2023 (Jun) | revenue / gross profit / operating income / net income | 211,915 / 146,052 / 88,523 / 72,361 | same | 0 |
| | assets / equity | 411,976 / 206,223 | same | 0 |
| WMT FY2024 (Jan) | total revenues / revenue − cost of sales / operating income / net income | 648,125 / 157,983 / 27,012 / 15,511 | same | 0 |
| | assets / equity | 252,399 / 83,861 | same | 0 |
| XOM 2023 | revenue | 334,697 (sales and other operating revenue) | 344,582 | +3.0% (explained below) |
| | net income / assets / equity | 36,010 / 376,317 / 204,802 | same | 0 |
| JPM 2023 | total net revenue / net income | 158,104 / 49,552 | same | 0 |
| | assets / equity | 3,875,393 / 327,878 | same | 0 |
| UNH 2023 | revenue / operating income / net income / assets | 371,622 / 32,358 / 22,381 / 273,720 | same | 0 |
| | equity | 88,756 (UnitedHealth shareholders) | 94,421 | +6.4% (explained below) |

What the two differences are:

- **XOM:** the `Revenues` tag is "total revenues and other income", which includes equity-affiliate income and other income. It is correct as tagged, but broader than sales.
- **UNH:** UNH does not tag parent-only `StockholdersEquity`, so the fallback, equity including non-controlling interests, was used.

What the empty cells are:

- XOM and JPM have no gross profit or operating income; UNH has no gross profit. All three are left empty by design.
- The WMT figure first came out at 642,637, which is net sales only. After the "largest revenue name the filing uses" rule it matches total revenues.

Internal check of the 10-Q method: for 14,703 10-Q rows, the year-to-date result was compared with the sum of four single quarters built from the same first-reported facts. **97.2% agree within 0.5%.** The disagreements are companies that recast past quarters for a spin-off or a sale: HWM in 2020, AIG (Corebridge), BAX, GE, DHR, DVN. In those cases the first-reported pieces come from before and after the recast, so the trailing sum mixes two scopes. This is an unavoidable cost of insisting on first-reported values. It affects about 3% of 10-Q rows.

## Size of the hindsight problem

Over all periods reported more than once (187,523 fact-periods since mid-2014), I compared the first-reported value with the latest reported value of the same item for the same period:

| item | annual: differs by > 2% | interim: differs by > 2% |
|---|---|---|
| revenue | 6.7% | 4.8% |
| cost of revenue | 7.4% | 4.8% |
| gross profit | 7.6% | 5.5% |
| operating income | **10.6%** | 6.6% |
| net income | 4.2% | 2.8% |
| total assets (instant) | 1.6% | |
| equity (instant) | 2.0% | |

- **Overall, 4.3% of reported values were later changed by more than 2%, and 10.4% changed at all.** Such changes appear at 376 of the 500 companies.
- On the 10-K rows themselves, the latest-reported annual figure differs from the one in the dataset by more than 2% for:
  - 9.6% of operating-income rows, and 4.8% by more than 10%;
  - 6.8% of gross-profit rows;
  - 5.1% of net-income rows;
  - 1.4% of asset rows.
- Most of these changes are recasts for discontinued operations and segment changes, rather than error corrections. A backtest that used the SEC `frames` endpoint, or any "latest value" database, would therefore know about one in ten operating-income figures differently from how the market saw them.

## Filing lag

- **10-Q:** median 32 days from period end to `filed` (10th to 90th percentile: 24 to 39 days).
- **10-K:** median 51 days (38 to 59), easing slowly from 54 days in 2015 to 49 in 2026.
- The fastest filers report in 8 to 10 days (DAL).
- Late filers take far longer, after accounting problems or restatements: SMCI filed a 10-K 686 days after the period end, and TRMB and DLR also filed very late. A signal should use the `filed` date, never `period_end` plus an assumed lag.

## Where the trailing construction failed, and why

Rows that lack a value the same company reports in other rows:

- **Revenue: 1,445 rows, 141 companies, about 270 a year in 2015–2018 and about 35 a year after.** 1,148 of these have no revenue under any listed tag for that period: older tags outside the list, and banks. 295 fall in a company's first year of history (an IPO or spin-off has no prior fiscal year, so no trailing year can be built).
- **Operating income: 1,246 rows, 96 companies.** The company tags it in some years and not others (JNJ, KLAC, ROK, TRV, GPC, ETN, JCI, ROST, HON, IP). 204 rows are first-year cases.
- **Net income: 156 rows, 62 companies.** Almost all are first-year cases after an IPO or spin-off (VST, EXE, CARR, CEG, ABNB and others).
- **Assets: 18 rows (REG, KKR, LEN, WY). Equity: 60 rows (BX, KKR, WEC, REG, ARES).** No value is tagged at the period end.
- **Gross profitability: 2,667 rows, 147 companies.** The company has it in some years but not others, usually because the cost tag changed to one outside the list (XEL, T, FDX, DUK, AEP, LEN, ORCL, CPAY, DVN). 62 rows are insurer withholds.

Suspect values left in the data, rather than guessing a fix:

- CHRW's derived gross profit is too large: its cost tag covers only purchased transportation. Its `gp_assets` exceeds 1.5 in 14 rows.
- Biotechs (INCY, REGN, VRTX) and a few REITs and energy companies show derived gross margins above 90%, because their cost tag covers only part of their costs.
- Some rows show negative gross profit. Most are real: BA, cruise lines in 2020–21, MU, FCX. CPT's is a tag mismatch.

The full list of failures, with reasons, is returned in `update()["failures"]`.

## Traps to respect when using it

1. **`filed` is a date, not a time.** Many 10-Qs and 10-Ks are filed after the 4 pm close, often together with the earnings release. A row can only be acted on from the **next session's open** after `filed`. Using the close of `filed` itself is look-ahead.
2. **The earnings number is usually public before `filed`.** The press release (an 8-K) often comes days or weeks before the 10-Q or 10-K. This dataset is therefore conservative, not early: it shows when the full XBRL filing became public.
3. **Fiscal years that do not end in December.** 125 companies use another year end (January for retailers, June for MSFT, September for AAPL, and so on). `period_end` and `filed` are both correct, but "as of December 31" means a different fiscal quarter for different companies. For cross-sections, pick each company's latest row by `filed` date, not by fiscal year label.
4. **Companies missing because of the CIK table.** All 503 current tickers matched this time. A new index member gets a CIK only when the Wikipedia cache is refreshed, and a company that moved to a new CIK loses its history unless added to `PREDECESSORS`, as XOM and GOOG were.
5. **Survivorship: no dead companies are covered.** Only today's S&P 500 members are included. Companies that were acquired, went bankrupt or left the index are absent, so any backtest on this file alone is biased toward survivors.
6. **The SEC API is not complete or instant.** `companyfacts` is missing the latest filings of some co-registrant filers.
   - For 19 companies the CSV's latest row is the 2026-03-31 quarter. Most are utilities (NEE, SO, DUK, AEP, D, DTE, EXC, SRE, ETR, FE, CNP, LNT, EVRG, PPL); the rest are REITs (PLD, DLR, MAA, FRT, REG).
   - For C, the latest row is the 2025 10-K.
   - For NEE and C I checked the SEC submissions index. Their Q2 and Q3 10-Qs were filed with XBRL, but they are absent from `companyfacts`.

   This causes the dip in the last coverage row. Expect a lag of days to months for these companies.
7. **Tag meaning drifts.** The same XBRL name can cover the total in one year and a component in the next (ADM). The largest-name rule handles revenue and cost, but trailing sums built across a recast still mix scopes (about 3% of 10-Q rows).
8. **Share classes duplicate companies.** GOOG/GOOGL, FOX/FOXA and NWS/NWSA appear twice with identical numbers. De-duplicate by `cik` before ranking.
