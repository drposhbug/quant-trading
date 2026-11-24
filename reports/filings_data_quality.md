# SEC 8-K filings dataset: data quality (built 2026-11-23)

Script: `filings_data.py` (`update()`, `load()`). Output: `lab/filings_8k.csv`.
Source: `https://data.sec.gov/submissions/CIK##########.json` plus its older pages.
No API key. User-Agent "Mozilla/5.0 (research script)". The SEC answered every request; nothing was refused.

## What is in the file

- **73,410 filings** (8-K and 8-K/A, filed 2016-01-01 to 2026-11-23) for **all 503 companies** in the stock list.
- Columns: `ticker, cik, accession, form, accepted_ny, filed, after_close, items`.
  `cik` is the CIK that actually filed (see predecessors below), so one ticker can have two CIKs.
- No duplicate (ticker, accession) pairs. 1,458 accessions appear under two tickers, and that is expected:
  share classes of one company (NWS/NWSA 1,258, GOOG/GOOGL 114, FOX/FOXA 82) and 4 joint CEG/EXC filings.
  **Count events per company, not per ticker**, or you double-count these.

### 8-Ks per year

| year | filings | companies with a filing | per company | 8-K/A |
|---|---|---|---|---|
| 2016 | 6,782 | 458 | 14.8 | 121 |
| 2017 | 6,649 | 467 | 14.2 | 179 |
| 2018 | 6,624 | 470 | 14.1 | 155 |
| 2019 | 6,705 | 478 | 14.0 | 117 |
| 2020 | 7,280 | 483 | 15.1 | 139 |
| 2021 | 6,805 | 487 | 14.0 | 124 |
| 2022 | 6,493 | 489 | 13.3 | 143 |
| 2023 | 6,514 | 491 | 13.3 | 164 |
| 2024 | 6,575 | 497 | 13.2 | 134 |
| 2025 | 6,721 | 500 | 13.4 | 109 |
| 2026 (to 23 Nov) | 6,262 | 503 | 12.5 | 94 |

About 13 to 15 per company per year, very stable. 2020 is the high (COVID updates and new debt deals).

### Item codes

Filings carrying each code (one filing can carry several):

| item | meaning | filings | share |
|---|---|---|---|
| 9.01 | financial statements and exhibits | 57,651 | 78.5% |
| 2.02 | results of operations | 22,452 | 30.6% |
| 8.01 | other events | 18,857 | 25.7% |
| 7.01 | Regulation FD disclosure | 16,300 | 22.2% |
| 5.02 | departure/appointment of officers or directors | 13,723 | 18.7% |
| 1.01 | material agreement | 7,380 | 10.1% |
| 5.07 | shareholder vote results | 5,573 | |
| 2.03 | new direct financial obligation (debt) | 4,619 | |
| 5.03 | charter or bylaw amendments | 2,487 | |
| 1.02 | termination of a material agreement | 864 | |
| 2.01 | completed acquisition or disposal | 682 | |
| 3.02 | unregistered equity sales | 537 | |
| 3.03 | changes to holders' rights | 504 | |
| 2.05 | exit or restructuring costs | 332 | 0.45% |
| 2.06 | material impairments | 142 | 0.19% |
| 3.01 | delisting or listing-rule notice | 105 | 0.14% |
| 5.04, 4.01, 5.05, 5.01, 2.04, 1.04, 5.08, 1.05 | | 97, 67, 61, 54, 52, 42, 24, 21 | |
| 4.02 | non-reliance on earlier financial statements | 18 | 0.02% |
| 1.03 | bankruptcy | 9 | 0.01% |
| 5.06 | change in shell company status | 1 | |

No filing has an empty `items` value (all 73,410 have codes, 2016 included).
1,161 filings carry **only 9.01**: these are almost all 8-K/As that add exhibits to an earlier filing (often the financial statements of an acquired business), so they hold no new event.
The rare, sharp events are rare here because these are large, surviving companies: only 9 bankruptcy items and 18 restatements (4.02) in ten years. Many 3.01 filings are routine (transfers between exchanges), not delisting threats.

## When filings arrive

Times are New York local. Trading days come from NYSE holiday rules in the script (including Juneteenth from 2022 and the closures of 5 Dec 2018 and 9 Jan 2025).

| | all 8-Ks | 8-Ks with 2.02 (results) |
|---|---|---|
| after the close (at/after 16:00, or weekend/holiday) | 58.4% | 44.1% |
| before the open (before 9:30 on a trading day) | 32.0% | 51.7% |
| during trading hours | 9.6% | 4.2% |

Only 0.14% fall on a weekend or holiday. 7.1% are accepted after 17:30, and for those (6.8% of all) the SEC's `filed` date is the **next** business day. `filed` is therefore not the day the news came out. Use `accepted_ny`.

## Acceptance time check: is `acceptanceDateTime` really UTC?

Yes. The raw value ends in `Z` (e.g. `2026-11-02T21:30:23.000Z`). Apple publishes its results at 4:30 pm New York time. Its 2.02 filings read **20:30Z in summer and 21:30Z in winter**. After converting to New York, 44 of Apple's 45 results filings land at 16:30 to 16:35 in both seasons: 11 in winter (UTC-5) and 25 in summer (UTC-4) at exactly 16:30, most of the rest a minute or two later. The one exception was accepted at 18:55. If the stamp were New York time mislabelled as `Z`, the clock reading would stay the same all year and the converted times would jump by an hour at each clock change. They don't, so the conversion is right.

### 2.02 filings in 2019 against an independent calendar

Compared with the Nasdaq earnings calendar already cached in `data/earnings/` (read only):

| ticker | Nasdaq calendar dates | 8-K 2.02 accepted (New York) | match |
|---|---|---|---|
| AAPL | 29 Jan, 30 Apr, 30 Jul, 30 Oct | 29 Jan 16:30, 30 Apr 16:30, 30 Jul 16:30, 30 Oct 16:30 | all 4 |
| MSFT | 30 Jan, 24 Apr, 18 Jul, 23 Oct | 30 Jan 16:03, 24 Apr 16:04, 18 Jul 16:03, 23 Oct 16:06 | all 4 |
| JPM | 15 Jan, 12 Apr, 16 Jul, 15 Oct | 15 Jan 06:46, 12 Apr 06:46, 16 Jul 06:45, 15 Oct 06:44 | all 4 |
| BA | 30 Jan, 24 Apr, 24 Jul, 23 Oct | 30 Jan 07:53, 24 Apr 07:56, 24 Jul 07:39, 23 Oct 07:35 | all 4 |
| WMT | 19 Feb, 16 May, 15 Aug, 14 Nov | 19 Feb 07:00, 16 May 07:00, 15 Aug 06:59, 14 Nov 07:00 | all 4 |

All 20 quarterly results dates match, and the times fit each company's habit: Apple and Microsoft after the close, JPM, Boeing and Walmart before the open.
There are two extra 2.02 filings, and both are real news: **AAPL 2 Jan 2019 16:30** (the letter cutting its revenue forecast) and **BA 18 Jul 2019 16:40** (the 737 MAX charge announced ahead of results).
So 2.02 does not always mean scheduled earnings. It also catches warnings and preliminary results, which may be the more valuable events.

## Gaps and coverage

- **Predecessor CIKs.** As `fundamentals_data.py` does for XOM and GOOG/GOOGL, the script merges an older CIK's filings into the ticker. The first build showed 11 more companies whose history began late because they moved to a new holding company or redomiciled. Each old CIK was checked against the SEC (its name, and 8-Ks ending as the successor's begin) and added: DIS (TWDC Enterprises 18, to Mar 2019), BLK (BlackRock Finance, to Oct 2024), CI (Cigna Holding, to Sep 2018), AVGO (Broadcom Pte and Avago, to Mar 2018), APA (Apache, to Mar 2021), MRVL (Marvell Technology Group, to Apr 2021), BG (Bunge Ltd, to Nov 2023), TPL (Texas Pacific Land Trust, to Dec 2020), APO (Apollo Asset Management, to Jan 2022), STE (STERIS Ltd, to Mar 2019), LIN (Praxair, to Oct 2018).
  A predecessor's filings are kept only **before the successor's first 8-K**. After that the old CIK is a subsidiary, often filing its own debt news. This added 838 filings. Google Inc. (1288776) has no 8-Ks since 2016, so GOOG/GOOGL begin with Alphabet, which is correct.
- **46 companies still have no 8-K before July 2016.** None of these is a CIK split we could merge. They are:
  - Listings or spin-offs after 2016: TWLO, INVH, CVNA, VST, OKTA, VICI, EVRG, VRT, BE, MRNA, DOW, FOX/FOXA, UBER, AMCR, CRWD, DDOG, CARR, OTIS, VTRS, PLTR, ABNB, DASH, COIN, APP, HOOD, CEG, GEHC, TKO, VLTO, GEV, SOLV, RDDT, SW, SNDK, SKYD, Q, FDXF, HONA, VYLR.
  - Mergers that created a new filer from two old ones: DD (DowDuPont, 2017), BKR (Baker Hughes plus GE Oil & Gas, 2017), IR (Gardner Denver, listed 2017). These were left alone because neither parent is "the" predecessor.
  - Former foreign filers that sent 6-K reports, not 8-Ks: NXPI (8-Ks from Aug 2019), CRH (2024), FERG (2024).
- **Missing `items`:** none.
- **Amendments (8-K/A):** 1,479 (2.0%). See the trap below.

## Run times (this machine, about 3.7 requests a second)

- **Full rebuild** (no CSV): 1,051 requests (503 main files, predecessor files, and every older page that reaches 2016; pages ending before 2016 are skipped), **400 seconds (about 7 minutes)**.
- **Daily update** (CSV present): **503 requests, one per company, 171 seconds (about 3 minutes)**. The cache under `data/filings/` is not needed, so a GitHub job without the cache works. Re-running it on the same day added 0 rows and left the file unchanged, so the merge is stable.
  The daily path does not fetch predecessor CIKs; they no longer file for the parent.
  A ticker new to the list, or a ticker whose CIK in `lab/fundamentals.csv` changed, gets a full fetch automatically.
  The main file holds about the last 1,000 filings of each kind, so a missed daily run only loses data if a company files more than that in the gap.

## Traps a user must respect

1. **After-close filings are for the next session.** `after_close = 1` (58% of all 8-Ks, 44% of results) means the news arrived at or after 16:00, or on a weekend or holiday. The first price that can react is the **next session's open**, not that day's close. Filings before 9:30 (32%) can be traded at that day's open. The 9.6% during hours hit prices mid-session, so a close-to-close test cannot tell whether you acted before or after the move.
   Half-day sessions (closing at 13:00 on the day after Thanksgiving, some Christmas Eves and some 3 Julys) are **not** marked: a filing at 14:00 on those days is really after the close.
2. **Use `accepted_ny`, not `filed`.** For filings accepted after 17:30 (7%), `filed` is the next business day, one day after the news.
3. **8-K/A amendments repeat earlier news.** They correct or add exhibits to an earlier 8-K, often weeks later. Treat them as new events and you will see stale news as fresh. For event studies, drop `form == "8-K/A"` or keep it only for codes like 5.02 where the amendment can add facts.
4. **Item 9.01 is only exhibits.** It sits on 78% of filings and says nothing by itself. Filings whose only item is 9.01 (1,161) are not events.
5. **2.02 is not only scheduled earnings.** It includes warnings and preliminary results, like AAPL on 2 Jan 2019. Separate them, for example by distance from the usual quarterly date.
6. **Share classes and joint filers** (NWS/NWSA, GOOG/GOOGL, FOX/FOXA, CEG/EXC) carry the same accession under two tickers. Count events once per company.
7. **Survivorship.** The list is **today's** 503 members. Companies that went bankrupt, were taken over, or dropped out since 2016 are absent, together with their 8-Ks (and most real 1.03 bankruptcy and 3.01 delisting events with them). Any test on this file only covers survivors and companies added later. It shows nothing about what happened to companies that died.
8. **Late starters.** 46 tickers enter after mid-2016. A per-company base rate over all years is biased unless you count only the years each company was filing.
