# Wide universe from Alpaca alone: data quality

`wide_universe.py` rebuilds the survivorship-free S&P 500 panel each day using Alpaca and two small committed
files, with no access to the local `data/universe/` caches. The figures below come from a run on 2026-11-23,
checked against the local build (`universe_data.py`, caches dated 2026-11-18).

```python
from wide_universe import load, missing
panel, member = load()   # panel["o"|"h"|"l"|"c"|"v"]: DataFrame[day x id]; member: bool DataFrame[day x id]
missing()                # ids with no bars at all
```

## What is in it

| | |
|---|---|
| ids | **729**: every company that was an S&P 500 member at any time from 2016-01-04 to 2026-11-18 |
| ids with bars | 725. The other 4 (`CCE`, `SNDK@2016`, `STI`, `TE`) are all-empty columns, listed by `missing()` |
| members today | 503 (open spells, which stay members after the file's last date) |
| companies that left the index | **226**. Of these, 97 stopped trading at or just before their exit ("dead": acquired, merged, failed), 4 of them with no bars at all. The other 129 were dropped and kept trading |
| days | 2016-01-04 .. today (2,739 sessions on 2026-11-23) |
| member-days with a price | 99.2% (2016) up to 99.8-100% (2017 on). 2,720 of 1,379,922 member-days are empty, listed below |
| load time | **~93 s** for a full load: ~92 s for the single `daily_calls.bars()` call (742 symbols, 8 chunks of 100, ~200 paged requests) and ~2 s to assemble |

### The two files

* `lab/universe_members.csv` (`id, member_from, member_to, open`): 729 spells, one per id, cut to start no earlier
  than 2016-01-04. Dates are the first and last trading day in the index. `open=1` (503 rows) means still a
  member on 2026-11-18. For those, `member_to` is that date and the loader keeps them true after it.
* `lab/universe_symbols.csv` (`id, symbol, use_from, use_to`): 752 rows, 742 Alpaca symbols. 708 ids use one row.
  21 ids are stitched from 2 or 3 symbols, and 10 more use a single symbol that differs from the id. Rows are
  calendar-inclusive. An empty `use_to` means the row is still running. The first row starts about 400 days
  before the first membership, so lookbacks exist when a company enters. A closed id ends 10 days after its exit,
  as in the local build.

### How ids were stitched (reproduced from `universe_data.build()`)

Each id is a chain of membership spells (`chains.pkl`). For each piece of a chain, the build picked one Alpaca
symbol (`build_log.json` → `pieces`). That could be the ticker of the time, a later name, or the id's own ticker,
because Alpaca usually files a renamed company's history under its newest symbol. `OVERRIDES` then replaced part
of a piece with another symbol. I re-ran the build's window and stitching logic on its own cached bars, tagged
every bar with its source symbol, and turned the runs of each symbol into rows. On the cached bars this
reproduces `prices.pkl` exactly, apart from cells that came from yfinance (see the check below). In practice:

* **Renames where Alpaca keeps the old bars under the old symbol** become 2-3 rows: FB→META, HCP→PEAK→DOC,
  ABC→COR, ANTM→ELV, UTX→RTX, CTL→LUMN, MYL→VTRS, LB→BBWI, COG→CTRA, CDAY→DAY, FLT→CPAY, RE→EG, WRK→SW, EQR→VMRK,
  CBS→VIAC→…→SKYD.
* **Renames where Alpaca already files the history under the new symbol** become one row with the new symbol:
  TT (IR), BKR after 2017-07, TFC (BBT), J (JEC), GEN (NLOK), FISV (FI), MRSH (MMC), BNY (BK), ECHO (SATS), FBHS
  (bars under FBIN), WYND (bars under TNL).
* **OVERRIDES** become extra rows: YHOO→AABA, TSO→ANDV, DLPH→APTV, BHI→BKR, UA→UAA (class split), and
  ARNC→HWM 2020-04-01..15 (Arconic Inc. traded as HWM after the ARNC symbol passed to the spun-off Arconic Corp).
* **`@` ids** are earlier, different companies that used the same ticker, for example `ILMN@2024` (Illumina
  until 2024-06) versus `ILMN` (re-added 2026-09). Their rows are cut to their own window, so a ticker's later
  issuer never leaks in.
* **Moved since the build.** Between 2026-11-18 and 2026-11-23, Alpaca moved the history of BLL, PKI, WLTW and
  PSKY to BALL, RVTY, WTW and SKYD. The old symbols now return nothing, so the file uses the new symbols. The
  loader also guards against this in general: if a row's symbol has no bars in its range, the id's later
  symbols fill it, and `fallbacks()` lists those rows. None were needed on 2026-11-23.

Loader rules carried over from the build:

* Bars with volume 0 are dropped. Alpaca keeps printing the last price after a delisting (MON, and DOW
  2017-09..2019-03).
* When an id changes symbol, the earlier bars are rescaled so the levels join. The join is exact when the old
  symbol has a bar on the new symbol's first day. Otherwise the join day's return is taken as 0%, as in
  `_stitch`.
* Rows may overlap. A later row takes over from its first bar, and the earlier row's extra bars are used only
  for the join.
* o/h/l/c are multiplied by the join factor and volume is divided by it.

## Check against the local dataset

These are the cells where `source.pkl` says the close came from Alpaca: 1,424,955 cells over 2016-01-04 ..
2026-11-18. The loader has a close in every one of them.

| test | result |
|---|---|
| close within 0.5% of `prices.pkl` | **96.41%** (1,373,777 cells) |
| same, leaving out the 13 spin-patched ids and SKYD | 97.69% |
| after one constant factor per id (level shifts from re-adjustment) | 99.18%; 99.91% leaving out spin-patched ids and SKYD |
| daily log returns within 0.1% | **99.996%** of 1,424,228 |
| membership mask vs `membership.pkl` (2016-01-04 .. 2026-11-18) | identical |
| o/h/l/c consistency (low ≤ open, close ≤ high) | no violations |

On the build's own cached bars, before Alpaca's changes since 2026-11-18, agreement was 98.66%. Every
disagreement there came from the spin patches and SKYD.

Ids that disagree, and why:

1. **Spin-off patches (13 ids: FTV, IBM, IP, J, JCI, MMM, MRK, PFE, PNR, RTX, TDG, TT, YUM).** The local build
   replaced one day's return with yfinance's to remove a fake spin-off drop. That rescales every earlier price.
   The loader uses Alpaca only, so it keeps the fake drop, and all cells before the patch day differ by that
   day's factor (4-12%, and up to 3.4x for RTX on 2020-04-03). From the patch day on, 100% agree. **These fake
   drops are back in the panel**: RTX 2020-04-03 (log -1.24), PNR 2018-05-01 (-0.41), YUM 2016-11-01 (-0.35),
   TT 2020-03-02 (-0.12), JCI 2016-10-31, FTV 2025-06-30, TDG 2025-09-02 and the rest. Winsorize or drop those
   days.
2. **Re-adjustment since 2026-11-18 (AMGN, ATO, BBWI, CCEP, CMI, CNP, EVRG, FBHS, LKQ, MCHP, SNA, TSCO, VTRS,
   SNDK).** With `adjustment=all`, Alpaca back-adjusts the whole history for each new dividend or split, so
   every earlier level shifts by a constant: 0.5-1.6% for dividends, and 1/8 for SNDK's split after 2026-11-18.
   Returns are unchanged. This is expected and will keep happening, so compare returns, not levels.
3. **SKYD (Paramount).** Paramount's 2022-02-17 .. 2025-08-06 bars are in no Alpaca symbol. Alpaca's `PARA` is
   a different company, and the local build filled that stretch from yfinance. The panel has a hole there, and
   the CBS/VIAC levels before it are left as Alpaca has them, so they are 46% above the local build. No return
   across the hole can be computed.
4. **WTW.** WLTW now returns nothing, and Alpaca's WTW series has a fake +3.7% day on 2021-12-30, where the old
   WLTW bars joined. Earlier cells are 4.2% below the local build.

Cells the loader has but the local build had from yfinance or not at all:

* DOW: 1,920 cells. Alpaca now has Dow Inc. bars from 2019-04-02, which the build filled from yfinance.
* DOW@2017: 420 cells. Alpaca now returns Dow Chemical bars from 2016-01-04 to 2017-08-31 under `DOW`, where the
  build found none. The level and drift look like Dow Chemical, but this has not been verified against a second
  vendor.
* SKYD: 3 cells.

## Companies that left the index: last bar and the last 21 sessions

Of 226 ids that left, 97 stopped trading at or before their exit:

* 62 have their last bar on the exit day.
* 30 stopped 1-5 sessions before the exit. These are mostly acquisitions closing a few days before S&P removes
  the name; holding the deal price to the exit is right.
* 1 (TMK) traded one day past its exit. That is the unlinked rename to GL, described below.
* 4 have no bars at all.

The 129 dropped names keep trading, and their series run to 10 days after the exit.

The last 21-session return before the final bar shows whether a dead company ends at a real final price. For
the dead group the median is +1.1%; 5% of them are below -17.8% and the worst is -75%. Mergers end near the deal
price. The tail is:

| id | exit | last bar | 21-session return | what happened |
|---|---|---|---|---|
| FRC | 2023-05-03 | 2023-04-28 | -75% | seized 2023-05-01; the final ~-100% is **missing** |
| SIVB | 2023-03-14 | 2023-03-09 | -67% | seized 2023-03-10; the final ~-100% (the day it was halted) is **missing** |
| SBNY | 2023-03-14 | 2023-03-10 | -48% | seized 2023-03-12; final loss **missing** |
| RTN | 2020-04-03 | 2020-04-02 | -42% | merged into UTX/RTX in the COVID crash; real |
| DWDP / DRE / POM / NBL | | | -14% to -18% | stock-for-stock deals in falling markets; real |

So the worst outcomes are a hole, not a price. The three 2023 bank failures stop at their last trade, 48-75%
down over a month, and the -100% that followed never appears. No other company that stopped trading inside the index
fell more than 42% in its last month. Distressed names such as FTR, ENDP, CHK and PCG were dropped while still
trading, and their series run to 10 days after the exit. For a strategy that can hold a name into its exit, add an explicit delisting return (about -100% for FRC,
SIVB and SBNY).

Four companies that left have **no exit price at all**:

* STI: SunTrust, merged into Truist 2019-12. The symbol was reused later.
* TE: TECO Energy, acquired 2016-07.
* CCE: Coca-Cola Enterprises, became CCEP 2016-05.
* SNDK@2016: SanDisk, acquired by WDC 2016-05.

All four were cash or stock acquisitions, not failures, so the hole costs coverage rather than the worst
returns.

The dead count is also slightly inflated by three renames that the local build did not link, so one company
shows as an exit followed by a new entry the next day. The two series have correlation 1.0 across the overlap:

* DWDP→DD (2019-06)
* SYMC→GEN (Symantec→NortonLifeLock, 2019-11)
* TMK→GL (Torchmark→Globe Life, 2019-08)

They are kept as in the local build (separate ids). A study of exits should treat them as continuing.

## Member-days without a price (2016-01-04 .. 2026-11-18)

| id | empty member-days | why (carried over from `MISSING_WHY`, updated) |
|---|---|---|
| STI | 990 | SunTrust: no Alpaca bars under STI |
| SKYD | 869 | Paramount 2022-02-17 .. 2025-08-06: not in Alpaca (the local build used yfinance) |
| FTI | 261 | FMC Technologies before the 2017-01-17 Technip merger; Alpaca FTI starts with TechnipFMC |
| ARNC | 210 | Alcoa Inc. before its 2016-11-01 split; Alpaca ARNC starts 2016-11-01 |
| TE | 125 | TECO Energy; Alpaca TE bars belong to a later issuer (outside the window) |
| CCE | 102 | Coca-Cola Enterprises; the symbol returns nothing |
| SNDK@2016 | 90 | SanDisk; SNDK was reused in 2025 by the new SanDisk |
| ~30 others | 1-5 each | acquisitions: last trade a few days before the index exit (NBL 5, JNPR 4, RHT 4, FRC 3, SIVB 3, ...) |
| AMCR | 2 | added 2019-06-07, first NYSE trade 2019-06-11 |

`MISSING_WHY` listed `DOW@2017` as having no bars; on 2026-11-23 Alpaca has them (see above).

## Known artefacts in member daily returns (|log r| > 0.4)

There are 46 such days. Most are real: the 2023 bank failures, the 2020-03-09 oil crash, earnings gaps. The
known artefacts are:

* From `SUSPECT`: SW 2016-05-16 (WestRock bars at a wrong level), TGNA 2017-06-01 (Cars.com spin-off unadjusted),
  EVHC 2016-12-02 (merger symbol switch, also +1.13 that day), UA 2016-04-08 (class-C first day).
* Spin-off days no longer patched: RTX 2020-04-03 and PNR 2018-05-01 (YUM, TT, JCI and others are smaller than
  0.4 but still fake).
* New: WTW 2021-12-30 (+3.7%, small but fake).

Other spin-offs of companies that have left the index were never patched, for example WYND 2018-06 and EQT@2018
2018-11; their last 21-session returns of -56% and -66% come from that. Winsorize daily returns, for example at
±40%.

## Limits

1. Alpaca only, so nothing before 2016-01-04. Use 2017-01 as the start for 12-month lookbacks.
2. Levels move whenever Alpaca re-adjusts. Compute returns inside the panel and never compare stored levels
   across days.
3. Alpaca can move a renamed company's history to its new symbol at any time, as it did with four symbols in the
   five days before this check. `fallbacks()` covers the case where the old symbol goes empty. Check
   `missing()` and `fallbacks()` after each run, and update `lab/universe_symbols.csv` when a fallback appears.
4. The members file ends 2026-11-18. Later index changes are not in it: open spells just stay true. Extend the
   file (and `universe_data.TAIL`) when S&P changes the index.
5. Membership timing, selection bias into the index and the provenance limits are as in
   `reports/universe_data_quality.md`.
