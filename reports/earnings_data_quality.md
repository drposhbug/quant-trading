# Earnings data: what `lab/earnings.csv` holds and how far to trust it

Built 2026-11-23 by `earnings_data.py` from Nasdaq's public earnings calendar
(`https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD`, no key, one page per date). Raw pages are cached in
`data/earnings/` (git-ignored, 2,864 files, 43 MB). Each run fetches only the missing pages, plus the last 10 days and
the next 30 days, because those pages change.

## What the file contains

One row per quarterly earnings announcement, 2016-01-07 to 2026-12-18 (the last 47 rows, from 2026-11-23 on, are
upcoming announcements). The file has **20,993 rows covering 505 tickers**: the 503 names in `lab/universe.csv`
plus SPCX and TSM from `model.UNIVERSE`. Every ticker on the list has at least one row.

| column | meaning |
|---|---|
| date | the calendar date Nasdaq lists the announcement on |
| ticker | the project's dotted form (Nasdaq's `BRK/B` becomes `BRK.B`) |
| when | `before` (pre-market), `after` (after hours) or `unknown`. **Almost always `unknown` for past dates; see below** |
| eps | reported EPS, as Nasdaq lists it. **Not split-adjusted** (AAPL 2020-01-28 shows 4.99, 2022 shows 2.10) |
| eps_forecast | the consensus forecast Nasdaq shows for that quarter |
| surprise_pct | Nasdaq's surprise, (eps - forecast) / abs(forecast) x 100 |
| n_est | number of estimates behind the consensus |
| fiscal_quarter | the month the fiscal quarter ended, `YYYY-MM` |

Use `earnings_data.load()` to read it with dates and numbers parsed. To keep every symbol on the calendar, use
`earnings_data.build(tickers="all", out=...)`. Pass a longer list to `build(tickers=[...])` or `update(tickers=[...])`.

## Coverage by year (past announcements only)

| year | rows | tickers | tickers with 3 or more | with 4 or more | forecast | surprise | n_est | when known |
|---|---|---|---|---|---|---|---|---|
| 2016 | 1,795 | 455 | 452 | 429 | 98.9% | 90.1% | 98.9% | 0% |
| 2017 | 1,828 | 460 | 457 | 447 | 99.3% | 90.4% | 99.3% | 0% |
| 2018 | 1,836 | 461 | 457 | 455 | 99.2% | 92.6% | 99.2% | 0% |
| 2019 | 1,868 | 474 | 468 | 456 | 98.9% | 92.0% | 98.9% | 0% |
| 2020 | 1,900 | 478 | 476 | 469 | 98.8% | 94.9% | 98.8% | 0% |
| 2021 | 1,933 | 485 | 483 | 479 | 99.3% | 95.9% | 99.3% | 0% |
| 2022 | 1,936 | 486 | 485 | 480 | 99.3% | 94.3% | 99.3% | 0% |
| 2023 | 1,951 | 490 | 487 | 487 | 99.3% | 94.6% | 99.3% | 0% |
| 2024 | 1,972 | 496 | 494 | 487 | 99.2% | 94.5% | 99.2% | 0% |
| 2025 | 1,988 | 498 | 497 | 496 | 99.4% | 95.2% | 99.4% | 0% |
| 2026 to Nov 20 | 1,939 | 504 | 498 | 435 | 99.5% | 92.2% | 99.5% | 3.7% |

Reported EPS is present on every past row except 63 rows in February 2026 (see the holes below). The surprise
is missing more often than the forecast mainly because Nasdaq leaves it blank when the forecast is 0 or very
small. The ticker count grows over time because companies that listed after 2016 (for example CEG,
GEHC and SOLV) have no earlier rows. In 2026 the share with four reports is lower only because Q4 2026 is not
reported yet.

## Holes in the source

- **2016-06-06 to 2016-07-08 is empty.** Nasdaq answers "No record found" for all 22 weekdays. Announcements in
  that window are simply absent: ORCL, FDX, NKE, ACN, ADBE, MU, GIS, CCL, DRI and others are missing their
  May-quarter results. This accounts for most of the 2016 gaps of more than 120 days between a ticker's reports.
- **2026-02-19 returns an HTML web page instead of JSON** on every attempt (19 tries over about two hours).
  That day's announcements are missing; WMT's Q4 report, for example, appears in the SEC record but not here. The
  module stores an empty placeholder for this date, tries it once on each run, and fills it in if Nasdaq fixes the
  page.
- **February 2026 has 63 rows with a forecast but no EPS.** These are leftover schedule entries that were never
  filled in, and they are the only past rows that carry before/after timing. Treat them as "announcement happened
  around this date, result unknown".
- Apart from those holes, about 1 to 2% of company-quarters a year are missing: 147 gaps of more than 120 days
  across the whole file. Most fall around January (a few companies' Q4 reports never appear) or come from mergers.
- Weekdays with no rows at all are, apart from the June 2016 block and 2026-02-19, market holidays or quiet days
  (for example Christmas, July 4 and the first business days of January).

## Duplicates and how they were resolved

The raw pages give 21,026 rows for the list. There is 1 exact repeat of the same date and ticker. Thirty-three rows
were removed as duplicates. A duplicate means the same ticker again within 5 days, or the same fiscal quarter
again within 45 days.

- **ECHO, 24 rows.** EchoStar's history has two rows for every quarter from 2016 to 2021, about two weeks apart,
  because Nasdaq merged two companies' histories under today's symbol (old EchoStar and DISH). The later row
  was kept. **Which company each kept ECHO row belongs to before 2022 is not certain.**
- **February 2026, 8 rows** (FIS, DTE, GDDY, GPN, PANW, PPL, WAT, CEG). An early schedule entry with no EPS was
  followed a few days later by the actual result. The row with the result was kept.
- **SMCI, 1 row.** A delayed filing (2025-02-25) repeated a quarter already listed. The row with the forecast was kept.

The rule: keep the row with a reported EPS, then one with a forecast, then one with known timing, then the later
date. Two junk rows were also dropped: on 2019-01-01, a holiday, Nasdaq lists PANW and WDAY results for fiscal
April 2012. Any row whose fiscal quarter ended more than 200 days before its date is removed.

**Lost minus signs.** In a few rows a minus sign is missing from the EPS or the forecast. For example, TSLA on
2017-08-02 shows EPS -2.04 against a forecast of "$2" with a surprise of -2%. Nasdaq's own surprise figure is
consistent with the true signs, so the module flips a sign only when doing so reproduces the stated surprise.
That fixed 6 rows. In 99.65% of rows, recomputing the surprise from EPS and forecast matches Nasdaq's figure
within 0.1 point. The remaining few mismatches (for example SBAC 2018-07-30, IRM and SPG 2018-10-25) are left
as Nasdaq gives them; for these, trust EPS and forecast over `surprise_pct`.

## Check against the SEC record (ten companies)

For AAPL, MSFT, JPM, WMT, XOM, TSLA, NVDA, BA, KO and UNH, every past Nasdaq row was compared with the 8-K
filings listing item 2.02 (results of operations) in `data.sec.gov/submissions`, using the acceptance time
converted to New York time. The SEC's `acceptanceDateTime` really is UTC: JPM's 06:45 ET releases show as
10:45Z.

- **Date match: 437 of 439 Nasdaq announcements (99.5%) fall on exactly the 8-K date.** None were off by one day.
  None were off by 2 to 7 days. The 2 unmatched rows are XOM's July and October 2026 reports. The SEC record for
  CIK 34088 (Exxon Mobil) now carries no ticker and no 2026 earnings 8-Ks, so Exxon apparently files under a
  new entity. That is an SEC-side change, not a Nasdaq error.
- **The SEC has 60 item-2.02 8-Ks with no Nasdaq row.** 47 are Tesla's quarterly delivery reports, and 13 are
  other non-calendar releases: NVDA's revenue warnings (2019-01-28, 2022-08-08), BA charge pre-announcements,
  AAPL's 2019-01-02 guidance cut, XOM's February reserve/10-K filings, and WMT 2026-02-19 (the broken page).
  **Pre-announcements and profit warnings are not in this file.**
- **Timing.** By acceptance time, AAPL, MSFT, NVDA and TSLA always announce after 16:00, and BA, JPM, KO, UNH, WMT
  and XOM always before 09:30. Nothing was filed during market hours. Nasdaq states the timing for only 2 of these
  439 rows (KO and XOM in February 2026, both "before"), and both agree with the SEC. The other 437 say "unknown".

## How far "when" can be trusted

Nasdaq shows pre-market or after-hours **only while a date is still upcoming**. Once the date passes, the page
switches to "time-not-supplied" (checked across all 159,000 calendar rows for every symbol: no stated time on any past date except
a handful in Jan–Feb 2026). For the next month, 85% of upcoming rows have a time. On the two past rows where it
could be checked, it was right.

From now on, the daily job keeps the timing it saw before each date passed: a cached time is carried into the
re-fetched page and marked `_time_from_cache`. So `when` will build up going forward. **The history 2016–2025
has no timing at all.** For backtests, get it elsewhere: from the SEC 8-K acceptance time as above (it agreed
perfectly in this sample), or assume a company keeps its habit, since all ten checked companies did every quarter.

## Were historical forecasts revised after the fact?

This cannot be settled from one download. Nasdaq keeps no earlier copies, and a page fetched today is all there is.
What can be said:

- **For revision:** the pages are clearly rebuilt from a current database, not frozen. A 2016 page shows today's
  market cap, today's company name, and today's symbol: META for Facebook in 2016, P for "Everpure", ECHO
  for EchoStar. Companies that no longer exist (TWX, MON, CELG, YHOO, LNKD, ATVI and others) are missing from old
  pages entirely. Rebuilt data can also have been revised.
- **Against revision:** EPS and forecasts are on the basis of their time, not split-adjusted (AAPL, NVDA, AMZN
  and GOOGL show pre-split values before their splits). The number of estimates looks like that of its era
  (TSLA had 1 to 2 estimates in 2016–2018 and 10 or more by 2025). The share of beats sits at 77–86% every year,
  which is the usual 2016–2025 pattern rather than a suspiciously perfect one.
- Verdict: probably the consensus as it stood shortly before each report, but **not proven point-in-time**. Do not
  build a strategy whose edge depends on small surprises; a forecast revised by a cent would erase it.

## Traps for anyone using this file

1. **An "after" announcement can only be traded at the next session's open.** Without known timing, which is the
   case for all history, assume the result is usable no earlier than the open of the trading day after `date`.
   That is safe for both before and after reporters, though it gives away the first-day reaction of pre-market
   reporters.
2. **No point-in-time guarantee on the consensus** (above). Treat `surprise_pct` as approximate.
3. **Survivorship.** Old pages contain only companies that still exist under today's identity. Combined with a
   universe of today's S&P 500, any backtest is a survivors' backtest.
4. **Today's tickers are applied to the past.** That suits this project's list, but a historical ticker list
   (FB, TWTR) will not match. Some histories mix companies (ECHO before 2022).
5. **EPS is not split-adjusted.** Compare EPS only with the forecast of the same row, or work with
   `surprise_pct`. Never compare EPS levels across a split.
6. **Holes:** 2016-06-06 to 07-08, 2026-02-19, and the 63 February 2026 rows without results. Pre-announcements and
   profit warnings are not included.
7. **Upcoming dates move.** Rows dated in the future are schedules. They are re-fetched daily and may shift or
   disappear. Only use a date once it is in the past.
8. `date` is the date of the release. For an after-hours release this matches the SEC acceptance date. An EDGAR
   *filing* date can be the next day for late filings; none of the 437 matched cases had this.

## Running it

- Full rebuild from an empty cache: about 2,860 pages. Nasdaq answers in about 2 seconds a page even at the
  allowed 3 requests a second, so it took **about 100 minutes**.
- Daily update: about 30 pages (last 10 days, next 30 days, and one try at the broken date), **80 seconds to
  3 minutes**. Exit code 1 only if a page inside the refresh window fails. A past page that keeps failing becomes
  a placeholder and does not fail the job.
- Politeness: at most about 3 requests a second, exponential backoff with jitter on errors, Retry-After honoured
  on HTTP 429, and the run stops after 8 failures in a row.
