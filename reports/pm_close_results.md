# Polymarket as a same-day CLOSE predictor (pre-open / intraday)

## 0. Pre-registration (written 2026-11-20, before any outcome, return or Polymarket price was loaded)

This is a STUDY. It does not touch the frozen model (model.py, universe, monitor; MATH.md "Change control").
Known before writing this (from resolution text only, no prices): Polymarket daily "<TICKER> Up or Down on <date>"
markets exist for TSLA, NVDA, AAPL, MSFT, GOOGL, AMZN, META, SPCX and the indices SPX, NDX (also QQQ); none for AVGO,
TSM, AMD, ORCL. They resolve **Up if the official close on the date is above the official close of the previous trading
day** (not vs the day's open; ties 50-50). Monthly ladders "Will <TICKER> close above $K end of <month>?" resolve on the
last trading day's official close.

**Data.** Polymarket CLOB prices-history at 1-minute fidelity (YES = "Up" token). Snapshot p(T) = last point stamped at
or before T (never after), no older than 60 min, else missing. T = 09:25, 10:00, 15:00 ET. NYSE half days dropped.
Stocks: Alpaca SIP, adjustment=all, 1-minute bars incl. extended hours + daily bars. SPX -> SPY, NDX -> QQQ (QQQ market
-> QQQ). Bars are stamped at their start, so "price at T" = close of the last bar starting before T.

**Baseline (information a trader has at T, no fitted parameters).** Zero-drift random walk from the current price:
p_base(T) = Phi( ln(S_T / C_prev) / (sigma_oc * sqrt(f_T)) ), sigma_oc = std of ln(close/open) over the prior 60
sessions (shifted, no lookahead), f_T = fraction of the 390-minute session still to come (1, 360/390, 60/390).
S_0925 = last pre-market trade before 09:25; if no pre-market trade, p_base = 0.5.

**Tests** (each per instrument and pooled; pooled SE = Driscoll-Kraay, i.e. Newey-West with 5 lags on per-date sums;
per instrument this is plain Newey-West, 5 lags):
- **A. Information beyond the baseline** (T = 09:25, 10:00, 15:00): d = (p_base - y)^2 - (p_PM - y)^2 (Brier
  improvement; y = 1 if resolved Up). Test mean(d) != 0. Calibration tables and Brier/log-loss reported descriptively.
- **B. Tradable part** (T = 09:25, 10:00, 15:00): regress r(T -> close) on x = p_PM - p_base, where r(09:25 -> close)
  = open -> close (the first price you can trade at 09:30), r(10:00 -> close), r(15:00 -> close). Effect = bp per +10pp
  of x. Rank IC reported (not part of the pass rule). Net-of-cost reported in C.
- **C. Paper rule** (fixed): at the open, long the instrument open -> close iff p_PM(09:25) > 0.60, else flat (no
  shorts). 2 bp per side. Daily book = average over all instruments with a market that day (signal off -> 0).
  Compared with always-long-at-open (same cost) and flat. Stationary bootstrap (L = 5, B = 2000) of the daily series:
  C1 = P(Sharpe_rule <= 0); C2 = P(Sharpe_rule <= Sharpe_always_long) (paired). Two-sided p = 2 min(P, 1 - P).
- **D. Monthly ladders** (h = 1, 5, 10 trading days before the last trading day of the month, read at 16:00 ET, <= 2
  days stale): survival S(K) = P(close > K) from each strike's YES price, made non-increasing in K (running min from
  the lowest strike) and clipped to [0, 1]. Baseline: lognormal, zero drift, sigma = 60-day realised daily vol * sqrt(h
  trading days), from the stock close on the snapshot day. Score: mean Brier over the listed strikes (a discrete CRPS
  on the strike grid). Test mean(Brier_base - Brier_PM) != 0, one obs per ticker-month, Driscoll-Kraay by month (lags 1).
  PIT of the realised close (linear interpolation of 1 - S between strikes; tails clamped) reported as a decile
  histogram with a chi-square uniformity test (descriptive).

**Pass rule** (as in MATH.md): Holm across ALL tests A + B + C + D run, Holm p < 0.05, AND the effect has the same sign
in both chronological halves of that test's sample. Tests with n < 30 (D: < 10 months) are not run and listed.
**Primary sample:** all resolved markets. **Sensitivity (not in the pass rule):** only markets with lifetime volume >=
$5,000 (lifetime volume includes post-snapshot trading; it is a liquidity filter, not a signal).
Nothing is tuned; thresholds above are fixed.

**Expectation written now:** Up/Down resolves vs the PREVIOUS close, so most of p_0925 should be the overnight gap.
The question that matters is whether p_PM - p_base predicts the part still tradable (B, C). A null is the prior.

<!-- RESULTS BELOW ARE WRITTEN BY pm_close_study.py on 2026-11-20 -->

## 1. Inventory

Daily Up/Down markets found by enumerating every trading day 2025-06-01..2026-11-19 x prefix (gamma /events/slug). `rule` = what the resolution text compares against (parsed from the description). `panel` = resolved Up/Down rows with stock data on a full session; `with_p0925` = a CLOB point within 60 min before 09:25 ET.

| inst   |   markets | first      | last       |   resolved_up_down |   median_vol |   vol_ge_5k | rule                    | source              |   panel |   with_p0925 |   up_rate |
|:-------|----------:|:-----------|:-----------|-------------------:|-------------:|------------:|:------------------------|:--------------------|--------:|-------------:|----------:|
| aapl   |       276 | 2025-10-15 | 2026-11-19 |                275 |    4123.5485 |         116 | prev close 275, open 1  | Pyth                |     272 |          271 |    0.5221 |
| amzn   |       276 | 2025-10-15 | 2026-11-19 |                275 |    3556.7164 |         116 | prev close 275, other 1 | Pyth                |     272 |          271 |    0.5037 |
| googl  |       276 | 2025-10-15 | 2026-11-19 |                275 |    3768.1746 |         120 | prev close 275, other 1 | Pyth                |     272 |          271 |    0.5037 |
| meta   |       276 | 2025-10-15 | 2026-11-19 |                275 |    4027.0150 |         123 | prev close 275, other 1 | Pyth                |     272 |          272 |    0.4890 |
| msft   |       276 | 2025-10-15 | 2026-11-19 |                275 |    3531.6494 |         110 | prev close 275, open 1  | Pyth                |     272 |          272 |    0.4963 |
| ndx    |       135 | 2025-10-15 | 2026-08-04 |                133 |    6013.4998 |          75 | prev close 134, open 1  | Wall Street Journal |     130 |          129 |    0.5385 |
| nvda   |       275 | 2025-10-15 | 2026-11-19 |                274 |    5323.4252 |         142 | prev close 274, open 1  | Pyth                |     271 |          271 |    0.4908 |
| qqq    |        23 | 2026-03-25 | 2026-04-27 |                 23 |    7455.4864 |          13 | prev close 23           | Pyth                |      23 |           23 |    0.7391 |
| spcx   |       101 | 2026-06-29 | 2026-11-19 |                101 |     463.9029 |           2 | prev close 101          | Pyth                |     101 |          100 |    0.4653 |
| spx    |       275 | 2025-10-15 | 2026-11-19 |                274 |   91838.5930 |         249 | prev close 274, open 1  | Wall Street Journal |     271 |          270 |    0.5166 |
| tsla   |       276 | 2025-10-15 | 2026-11-19 |                275 |    4639.2711 |         132 | prev close 275, other 1 | Pyth                |     272 |          271 |    0.5000 |


Monthly ladders ("close above $K end of <month>", resolve on the official close of the last trading day of the month; source Yahoo Finance "Close").

| inst   |   months | first   | last    |   strikes |   median_vol |   last_day_rule |
|:-------|---------:|:--------|:--------|----------:|-------------:|----------------:|
| aapl   |       11 | 2025-11 | 2026-10 |       143 |    2374.0892 |          1.0000 |
| amzn   |       11 | 2025-11 | 2026-10 |       143 |    1309.8425 |          1.0000 |
| googl  |       11 | 2025-11 | 2026-10 |       143 |    4043.0740 |          1.0000 |
| meta   |       11 | 2025-11 | 2026-10 |       143 |    1427.5075 |          1.0000 |
| msft   |       11 | 2025-11 | 2026-10 |       143 |    1825.9926 |          1.0000 |
| nvda   |       11 | 2025-11 | 2026-10 |       143 |    2853.4794 |          1.0000 |
| spcx   |        4 | 2026-07 | 2026-10 |        52 |     126.1160 |          1.0000 |
| tsla   |       11 | 2025-11 | 2026-10 |       143 |    2524.9589 |          1.0000 |


## 2. Results (Holm over all tests run)

**0 of 71 tests pass** (Holm p < 0.05 and same sign in both chronological halves).

| Test                                                  | Inst   |    n | start      | end        |   effect |        t |      p |   Holm p |      h1 |      h2 | same sign halves   | Pass   |
|:------------------------------------------------------|:-------|-----:|:-----------|:-----------|---------:|---------:|-------:|---------:|--------:|--------:|:-------------------|:-------|
| B (p_PM-p_base) -> r(15:00->close)                    | meta   |  272 | 2025-10-16 | 2026-11-19 |   0.0113 |   3.2963 | 0.0010 |   0.0695 |  0.0093 |  0.0133 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |  -0.0100 |  -2.3109 | 0.0208 |   1.0000 | -0.0124 | -0.0076 | True               | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | POOLED | 2417 | 2025-10-16 | 2026-11-19 |   0.0032 |   2.3002 | 0.0214 |   1.0000 |  0.0023 |  0.0043 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | POOLED | 2417 | 2025-10-16 | 2026-11-19 |   0.0099 |   2.2582 | 0.0239 |   1.0000 |  0.0086 |  0.0109 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | googl  |  271 | 2025-10-16 | 2026-11-19 |   0.0242 |   2.2550 | 0.0241 |   1.0000 |  0.0166 |  0.0404 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | spcx   |   91 | 2026-07-14 | 2026-11-19 |   0.0205 |   2.2371 | 0.0253 |   1.0000 |  0.0245 |  0.0165 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | googl  |  272 | 2025-10-16 | 2026-11-19 |   0.0129 |   2.1432 | 0.0321 |   1.0000 |  0.0151 | -0.0005 | False              | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | meta   |  272 | 2025-10-16 | 2026-11-19 |   0.0213 |   2.0849 | 0.0371 |   1.0000 |  0.0193 |  0.0239 | True               | False  |
| A Brier gain PM vs baseline @15:00                    | spx    |  271 | 2025-10-16 | 2026-11-19 |   0.0051 |   1.8437 | 0.0652 |   1.0000 |  0.0038 |  0.0063 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | meta   |  272 | 2025-10-16 | 2026-11-19 |   0.0081 |   1.8427 | 0.0654 |   1.0000 |  0.0058 |  0.0103 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | tsla   |  271 | 2025-10-16 | 2026-11-19 |  -0.0070 |  -1.8346 | 0.0666 |   1.0000 | -0.0093 | -0.0047 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | ndx    |  129 | 2025-10-16 | 2026-08-04 |  -0.0182 |  -1.7869 | 0.0740 |   1.0000 | -0.0220 | -0.0145 | True               | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | googl  |  272 | 2025-10-16 | 2026-11-19 |   0.0048 |   1.6994 | 0.0892 |   1.0000 |  0.0053 |  0.0036 | True               | False  |
| A Brier gain PM vs baseline @15:00                    | meta   |  272 | 2025-10-16 | 2026-11-19 |   0.0070 |   1.6917 | 0.0907 |   1.0000 |  0.0055 |  0.0084 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | POOLED | 2421 | 2025-10-16 | 2026-11-19 |  -0.0035 |  -1.6734 | 0.0942 |   1.0000 | -0.0066 | -0.0005 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |   0.0167 |   1.5646 | 0.1177 |   1.0000 |  0.0038 |  0.0306 | True               | False  |
| A Brier gain PM vs baseline @15:00                    | tsla   |  272 | 2025-10-16 | 2026-11-19 |   0.0047 |   1.5557 | 0.1198 |   1.0000 |  0.0010 |  0.0085 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | amzn   |  272 | 2025-10-16 | 2026-11-19 |   0.0041 |   1.5533 | 0.1204 |   1.0000 |  0.0041 |  0.0041 | True               | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | msft   |  272 | 2025-10-16 | 2026-11-19 |   0.0025 |   1.4965 | 0.1345 |   1.0000 |  0.0007 |  0.0085 | True               | False  |
| D ladder Brier gain PM vs lognormal, h=5d             | POOLED |   81 | 2025-11    | 2026-10    |   0.0039 |   1.3758 | 0.1689 |   1.0000 |  0.0030 |  0.0046 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |  -0.0262 |  -1.3657 | 0.1720 |   1.0000 | -0.0459 | -0.0109 | True               | False  |
| A Brier gain PM vs baseline @15:00                    | msft   |  272 | 2025-10-16 | 2026-11-19 |  -0.0061 |  -1.3526 | 0.1762 |   1.0000 | -0.0150 |  0.0029 | False              | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | spx    |  271 | 2025-10-16 | 2026-11-19 |   0.0063 |   1.2767 | 0.2017 |   1.0000 |  0.0014 |  0.0095 | True               | False  |
| D ladder Brier gain PM vs lognormal, h=10d            | POOLED |   81 | 2025-11    | 2026-10    |  -0.0058 |  -1.2532 | 0.2101 |   1.0000 | -0.0081 | -0.0040 | True               | False  |
| A Brier gain PM vs baseline @15:00                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |  -0.0039 |  -1.2168 | 0.2237 |   1.0000 | -0.0078 |  0.0000 | False              | False  |
| D ladder Brier gain PM vs lognormal, h=1d             | POOLED |   81 | 2025-11    | 2026-10    |  -0.0170 |  -1.2101 | 0.2262 |   1.0000 |  0.0032 | -0.0324 | False              | False  |
| A Brier gain PM vs baseline @10:00                    | POOLED | 2417 | 2025-10-16 | 2026-11-19 |   0.0021 |   1.1889 | 0.2345 |   1.0000 | -0.0033 |  0.0074 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | ndx    |  130 | 2025-10-16 | 2026-08-04 |  -0.0053 |  -1.1397 | 0.2544 |   1.0000 | -0.0146 |  0.0041 | False              | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | msft   |  272 | 2025-10-16 | 2026-11-19 |   0.0139 |   1.0931 | 0.2743 |   1.0000 |  0.0231 |  0.0038 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | tsla   |  272 | 2025-10-16 | 2026-11-19 |   0.0194 |   1.0853 | 0.2778 |   1.0000 |  0.0501 | -0.0053 | False              | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |   0.0089 |   1.0541 | 0.2918 |   1.0000 |  0.0020 |  0.0193 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | amzn   |  272 | 2025-10-16 | 2026-11-19 |   0.0110 |   1.0398 | 0.2984 |   1.0000 |  0.0114 |  0.0087 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | spcx   |  100 | 2026-06-29 | 2026-11-19 |   0.0302 |   0.9908 | 0.3218 |   1.0000 |  0.0284 |  0.0296 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | ndx    |  129 | 2025-10-16 | 2026-08-04 |  -0.0119 |  -0.9357 | 0.3494 |   1.0000 | -0.0118 | -0.0153 | True               | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | ndx    |  130 | 2025-10-16 | 2026-08-04 |   0.0083 |   0.8999 | 0.3682 |   1.0000 |  0.0053 |  0.0192 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | msft   |  272 | 2025-10-16 | 2026-11-19 |   0.0039 |   0.8958 | 0.3704 |   1.0000 |  0.0049 |  0.0029 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | googl  |  272 | 2025-10-16 | 2026-11-19 |  -0.0042 |  -0.8802 | 0.3787 |   1.0000 | -0.0128 |  0.0045 | False              | False  |
| A Brier gain PM vs baseline @10:00                    | tsla   |  272 | 2025-10-16 | 2026-11-19 |   0.0027 |   0.8357 | 0.4033 |   1.0000 |  0.0020 |  0.0035 | True               | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | tsla   |  272 | 2025-10-16 | 2026-11-19 |   0.0034 |   0.7500 | 0.4532 |   1.0000 |  0.0081 |  0.0013 | True               | False  |
| A Brier gain PM vs baseline @09:25                    | amzn   |  271 | 2025-10-16 | 2026-11-19 |  -0.0028 |  -0.7434 | 0.4572 |   1.0000 | -0.0095 |  0.0038 | False              | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | spx    |  270 | 2025-10-16 | 2026-11-19 |  -0.0055 |  -0.7255 | 0.4682 |   1.0000 | -0.0094 | -0.0034 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | ndx    |  130 | 2025-10-16 | 2026-08-04 |  -0.0029 |  -0.7206 | 0.4712 |   1.0000 | -0.0049 | -0.0010 | True               | False  |
| C rule Sharpe > 0 (bootstrap)                         | BOOK   |  272 | 2025-10-16 | 2026-11-19 |  -0.5733 | nan      | 0.5170 |   1.0000 | -0.7428 | -0.3983 | True               | False  |
| C rule Sharpe - always-long Sharpe (paired bootstrap) | BOOK   |  272 | 2025-10-16 | 2026-11-19 |   0.3645 | nan      | 0.5890 |   1.0000 | -0.2437 |  0.9325 | False              | False  |
| A Brier gain PM vs baseline @10:00                    | msft   |  272 | 2025-10-16 | 2026-11-19 |   0.0017 |   0.5074 | 0.6119 |   1.0000 | -0.0084 |  0.0117 | False              | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | amzn   |  272 | 2025-10-16 | 2026-11-19 |   0.0019 |   0.4883 | 0.6253 |   1.0000 | -0.0031 |  0.0049 | False              | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | spcx   |   91 | 2026-07-14 | 2026-11-19 |   0.0043 |   0.4865 | 0.6266 |   1.0000 | -0.0013 |  0.0141 | False              | False  |
| A Brier gain PM vs baseline @10:00                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |  -0.0018 |  -0.4797 | 0.6314 |   1.0000 | -0.0082 |  0.0046 | False              | False  |
| A Brier gain PM vs baseline @10:00                    | spx    |  271 | 2025-10-16 | 2026-11-19 |   0.0015 |   0.4648 | 0.6420 |   1.0000 | -0.0049 |  0.0079 | False              | False  |
| A Brier gain PM vs baseline @09:25                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |  -0.0019 |  -0.4612 | 0.6447 |   1.0000 | -0.0025 | -0.0013 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | tsla   |  271 | 2025-10-16 | 2026-11-19 |  -0.0087 |  -0.4504 | 0.6524 |   1.0000 | -0.0127 | -0.0024 | True               | False  |
| A Brier gain PM vs baseline @10:00                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |   0.0015 |   0.3738 | 0.7085 |   1.0000 | -0.0035 |  0.0064 | False              | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | nvda   |  271 | 2025-10-16 | 2026-11-19 |   0.0015 |   0.3191 | 0.7496 |   1.0000 | -0.0068 |  0.0088 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | POOLED | 2417 | 2025-10-16 | 2026-11-19 |   0.0005 |   0.3153 | 0.7525 |   1.0000 | -0.0021 |  0.0032 | False              | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |  -0.0010 |  -0.2978 | 0.7659 |   1.0000 |  0.0036 | -0.0051 | False              | False  |
| A Brier gain PM vs baseline @09:25                    | meta   |  272 | 2025-10-16 | 2026-11-19 |  -0.0013 |  -0.2884 | 0.7730 |   1.0000 |  0.0003 | -0.0028 | False              | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | meta   |  272 | 2025-10-16 | 2026-11-19 |  -0.0035 |  -0.2380 | 0.8119 |   1.0000 | -0.0072 |  0.0008 | False              | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | msft   |  272 | 2025-10-16 | 2026-11-19 |   0.0019 |   0.2371 | 0.8126 |   1.0000 | -0.0124 |  0.0214 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | spcx   |   91 | 2026-07-14 | 2026-11-19 |   0.0014 |   0.2009 | 0.8407 |   1.0000 |  0.0063 | -0.0034 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | amzn   |  272 | 2025-10-16 | 2026-11-19 |   0.0005 |   0.1936 | 0.8465 |   1.0000 |  0.0001 |  0.0009 | True               | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |   0.0021 |   0.1847 | 0.8534 |   1.0000 | -0.0009 |  0.0073 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | aapl   |  271 | 2025-10-16 | 2026-11-19 |  -0.0005 |  -0.1504 | 0.8805 |   1.0000 |  0.0013 | -0.0023 | False              | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | POOLED | 2421 | 2025-10-16 | 2026-11-19 |   0.0009 |   0.1390 | 0.8894 |   1.0000 | -0.0042 |  0.0093 | False              | False  |
| A Brier gain PM vs baseline @09:25                    | spcx   |  100 | 2026-06-29 | 2026-11-19 |  -0.0010 |  -0.1382 | 0.8901 |   1.0000 | -0.0025 |  0.0005 | False              | False  |
| A Brier gain PM vs baseline @09:25                    | googl  |  271 | 2025-10-16 | 2026-11-19 |  -0.0005 |  -0.1157 | 0.9079 |   1.0000 | -0.0028 |  0.0018 | False              | False  |
| A Brier gain PM vs baseline @09:25                    | spx    |  270 | 2025-10-16 | 2026-11-19 |  -0.0004 |  -0.0918 | 0.9268 |   1.0000 | -0.0049 |  0.0042 | False              | False  |
| B (p_PM-p_base) -> r(09:25->close)                    | amzn   |  271 | 2025-10-16 | 2026-11-19 |   0.0009 |   0.0765 | 0.9390 |   1.0000 | -0.0056 |  0.0119 | False              | False  |
| A Brier gain PM vs baseline @15:00                    | googl  |  272 | 2025-10-16 | 2026-11-19 |  -0.0002 |  -0.0516 | 0.9589 |   1.0000 | -0.0035 |  0.0032 | False              | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | ndx    |  130 | 2025-10-16 | 2026-08-04 |   0.0001 |   0.0425 | 0.9661 |   1.0000 |  0.0004 |  0.0008 | True               | False  |
| B (p_PM-p_base) -> r(15:00->close)                    | spx    |  271 | 2025-10-16 | 2026-11-19 |  -0.0000 |  -0.0160 | 0.9872 |   1.0000 | -0.0015 |  0.0008 | False              | False  |
| B (p_PM-p_base) -> r(10:00->close)                    | spcx   |   91 | 2026-07-14 | 2026-11-19 |   0.0004 |   0.0098 | 0.9922 |   1.0000 | -0.0050 |  0.0094 | False              | False  |


B `effect` = slope of the return on (p_PM − p_base) (return per 1.0 of probability; ×1e3 = bp per +10pp). A `effect` = mean Brier improvement of PM over the baseline (positive = PM better). D `effect` = mean Brier improvement of the ladder over the lognormal (positive = ladder better).

Rank IC for B tests (descriptive):

| Test                               | Inst   |    n |   rank_ic |
|:-----------------------------------|:-------|-----:|----------:|
| B (p_PM-p_base) -> r(09:25->close) | POOLED | 2421 |    0.0010 |
| B (p_PM-p_base) -> r(09:25->close) | aapl   |  271 |   -0.0000 |
| B (p_PM-p_base) -> r(09:25->close) | amzn   |  271 |   -0.0049 |
| B (p_PM-p_base) -> r(09:25->close) | googl  |  271 |    0.1574 |
| B (p_PM-p_base) -> r(09:25->close) | meta   |  272 |    0.0013 |
| B (p_PM-p_base) -> r(09:25->close) | msft   |  272 |    0.0921 |
| B (p_PM-p_base) -> r(09:25->close) | ndx    |  129 |   -0.1344 |
| B (p_PM-p_base) -> r(09:25->close) | nvda   |  271 |   -0.1253 |
| B (p_PM-p_base) -> r(09:25->close) | spcx   |  100 |   -0.0145 |
| B (p_PM-p_base) -> r(09:25->close) | spx    |  270 |   -0.0569 |
| B (p_PM-p_base) -> r(09:25->close) | tsla   |  271 |    0.0003 |
| B (p_PM-p_base) -> r(10:00->close) | POOLED | 2417 |    0.0528 |
| B (p_PM-p_base) -> r(10:00->close) | aapl   |  271 |    0.0564 |
| B (p_PM-p_base) -> r(10:00->close) | amzn   |  272 |    0.0608 |
| B (p_PM-p_base) -> r(10:00->close) | googl  |  272 |    0.0950 |
| B (p_PM-p_base) -> r(10:00->close) | meta   |  272 |    0.1086 |
| B (p_PM-p_base) -> r(10:00->close) | msft   |  272 |    0.0134 |
| B (p_PM-p_base) -> r(10:00->close) | ndx    |  130 |    0.0383 |
| B (p_PM-p_base) -> r(10:00->close) | nvda   |  271 |    0.0645 |
| B (p_PM-p_base) -> r(10:00->close) | spcx   |   91 |   -0.0770 |
| B (p_PM-p_base) -> r(10:00->close) | spx    |  271 |    0.0447 |
| B (p_PM-p_base) -> r(10:00->close) | tsla   |  272 |    0.0582 |
| B (p_PM-p_base) -> r(15:00->close) | POOLED | 2417 |    0.0395 |
| B (p_PM-p_base) -> r(15:00->close) | aapl   |  271 |   -0.0435 |
| B (p_PM-p_base) -> r(15:00->close) | amzn   |  272 |    0.0435 |
| B (p_PM-p_base) -> r(15:00->close) | googl  |  272 |    0.0259 |
| B (p_PM-p_base) -> r(15:00->close) | meta   |  272 |    0.0911 |
| B (p_PM-p_base) -> r(15:00->close) | msft   |  272 |    0.0990 |
| B (p_PM-p_base) -> r(15:00->close) | ndx    |  130 |    0.0409 |
| B (p_PM-p_base) -> r(15:00->close) | nvda   |  271 |    0.0055 |
| B (p_PM-p_base) -> r(15:00->close) | spcx   |   91 |    0.1759 |
| B (p_PM-p_base) -> r(15:00->close) | spx    |  271 |   -0.0090 |
| B (p_PM-p_base) -> r(15:00->close) | tsla   |  272 |    0.0319 |


Tests not run (too few observations): A Brier gain PM vs baseline @09:25/qqq (n=23), B (p_PM-p_base) -> r(09:25->close)/qqq (n=23), A Brier gain PM vs baseline @10:00/qqq (n=23), B (p_PM-p_base) -> r(10:00->close)/qqq (n=23), A Brier gain PM vs baseline @15:00/qqq (n=23), B (p_PM-p_base) -> r(15:00->close)/qqq (n=23)

## 3. How much does Polymarket know beyond the price at the snapshot? (descriptive)

| snapshot   |    n |   brier_PM |   brier_base |   brier_50 |   corr_PM_base |   sd_resid_pp |
|:-----------|-----:|-----------:|-------------:|-----------:|---------------:|--------------:|
| 09:25      | 2421 |     0.2163 |       0.2128 |     0.2500 |         0.9393 |        7.6986 |
| 10:00      | 2417 |     0.1574 |       0.1595 |     0.2500 |         0.9633 |        7.8384 |
| 15:00      | 2417 |     0.0624 |       0.0629 |     0.2500 |         0.9793 |        8.5568 |


Calibration of p_PM at 09:25 (pooled):

| p_09:25       |   n |   mean_p |   freq_up |
|:--------------|----:|---------:|----------:|
| (-0.001, 0.1] |  62 |    0.068 |     0.097 |
| (0.1, 0.2]    | 150 |    0.157 |     0.233 |
| (0.2, 0.3]    | 209 |    0.256 |     0.287 |
| (0.3, 0.4]    | 340 |    0.354 |     0.359 |
| (0.4, 0.5]    | 360 |    0.457 |     0.456 |
| (0.5, 0.6]    | 387 |    0.554 |     0.501 |
| (0.6, 0.7]    | 356 |    0.652 |     0.598 |
| (0.7, 0.8]    | 266 |    0.749 |     0.729 |
| (0.8, 0.9]    | 206 |    0.847 |     0.782 |
| (0.9, 1.0]    |  85 |    0.943 |     0.906 |


Calibration of the gap-only baseline at 09:25 (pooled):

| b_09:25       |   n |   mean_p |   freq_up |
|:--------------|----:|---------:|----------:|
| (-0.001, 0.1] | 103 |    0.040 |     0.175 |
| (0.1, 0.2]    | 123 |    0.156 |     0.163 |
| (0.2, 0.3]    | 184 |    0.254 |     0.261 |
| (0.3, 0.4]    | 344 |    0.354 |     0.358 |
| (0.4, 0.5]    | 411 |    0.449 |     0.467 |
| (0.5, 0.6]    | 432 |    0.553 |     0.491 |
| (0.6, 0.7]    | 341 |    0.646 |     0.666 |
| (0.7, 0.8]    | 238 |    0.746 |     0.748 |
| (0.8, 0.9]    | 150 |    0.845 |     0.807 |
| (0.9, 1.0]    | 102 |    0.962 |     0.863 |


## 4. Paper rule (fixed): long at the open iff p_PM(09:25) > 0.60, else flat; 2 bp per side

|   days |   trades |   obs |    hit |   sharpe_rule |   sharpe_always |   sharpe_flat |   mean_rule_bp |   mean_always_bp |   cum_rule |   cum_always | h1            | h2            |     P1 |     P2 |
|-------:|---------:|------:|-------:|--------------:|----------------:|--------------:|---------------:|-----------------:|-----------:|-------------:|:--------------|:--------------|-------:|-------:|
|    272 |      913 |  2421 | 0.4951 |       -0.5733 |         -0.9378 |        0.0000 |        -2.2783 |          -6.5344 |    -0.0652 |      -0.1767 | -0.74 / -0.50 | -0.40 / -1.33 | 0.7415 | 0.2945 |

`h1`/`h2` = (rule Sharpe / always-long Sharpe) in each half. P1 = bootstrap P(Sharpe_rule ≤ 0); P2 = P(Sharpe_rule ≤ Sharpe_always). Flat = 0 return, Sharpe 0.

## 5. Monthly ladders

|       h |       n |   months |   brier_pm |   brier_base |    gain |
|--------:|--------:|---------:|-----------:|-------------:|--------:|
|  1.0000 | 81.0000 |  11.0000 |     0.0545 |       0.0374 | -0.0170 |
|  5.0000 | 81.0000 |  11.0000 |     0.0583 |       0.0622 |  0.0039 |
| 10.0000 | 81.0000 |  11.0000 |     0.0854 |       0.0797 | -0.0058 |


PIT deciles (counts in 0-10%, ..., 90-100%; uniform if calibrated; chi-square, 9 df):

|   h | forecast   |   n | deciles                 |   chi2_p |
|----:|:-----------|----:|:------------------------|---------:|
|   1 | pm         |  81 | 4 7 7 6 11 12 11 11 5 7 |   0.4148 |
|   1 | base       |  81 | 9 5 10 11 3 5 11 6 9 12 |   0.2948 |
|   5 | pm         |  81 | 2 5 11 10 16 9 10 5 6 7 |   0.0429 |
|   5 | base       |  81 | 4 4 6 12 17 8 10 4 4 12 |   0.0066 |
|  10 | pm         |  81 | 2 12 8 7 16 14 7 5 8 2  |   0.0035 |
|  10 | base       |  81 | 7 5 10 9 11 13 7 8 5 6  |   0.5579 |


## 6. Sensitivity: only markets with lifetime volume >= $5,000 (not in the pass rule)

| Test                                                  | Inst   |    n | start      | end        |   effect |        t |      p |
|:------------------------------------------------------|:-------|-----:|:-----------|:-----------|---------:|---------:|-------:|
| A Brier gain PM vs baseline @09:25                    | POOLED | 1177 | 2025-10-16 | 2026-11-19 |  -0.0013 |  -0.5545 | 0.5793 |
| B (p_PM-p_base) -> r(09:25->close)                    | POOLED | 1177 | 2025-10-16 | 2026-11-19 |   0.0036 |   0.4751 | 0.6347 |
| A Brier gain PM vs baseline @10:00                    | POOLED | 1178 | 2025-10-16 | 2026-11-19 |  -0.0002 |  -0.0807 | 0.9357 |
| B (p_PM-p_base) -> r(10:00->close)                    | POOLED | 1178 | 2025-10-16 | 2026-11-19 |   0.0110 |   1.9342 | 0.0531 |
| A Brier gain PM vs baseline @15:00                    | POOLED | 1178 | 2025-10-16 | 2026-11-19 |   0.0005 |   0.2524 | 0.8007 |
| B (p_PM-p_base) -> r(15:00->close)                    | POOLED | 1178 | 2025-10-16 | 2026-11-19 |   0.0016 |   0.7818 | 0.4343 |
| D ladder Brier gain PM vs lognormal, h=1d             | POOLED |   68 | 2025-11    | 2026-10    |  -0.0117 |  -1.1856 | 0.2358 |
| D ladder Brier gain PM vs lognormal, h=5d             | POOLED |   68 | 2025-11    | 2026-10    |   0.0048 |   1.4519 | 0.1465 |
| D ladder Brier gain PM vs lognormal, h=10d            | POOLED |   68 | 2025-11    | 2026-10    |  -0.0084 |  -2.1075 | 0.0351 |
| C rule Sharpe > 0 (bootstrap)                         | BOOK   |  258 | 2025-10-16 | 2026-11-19 |  -2.0584 | nan      | 0.0200 |
| C rule Sharpe - always-long Sharpe (paired bootstrap) | BOOK   |  258 | 2025-10-16 | 2026-11-19 |  -0.6407 | nan      | 0.3480 |


## 7. Verdict and caveats (written after the first run, 2026-11-20; numbers refer to the tables above)

**Polymarket is not a usable pre-open or intraday close predictor for these names. 0 of 71 tests pass.**

- **What the markets price.** Since 2025-10-16 every daily market resolves on close vs the PREVIOUS close. So the
  09:25 price is mostly the overnight gap: its correlation with the gap-only random-walk baseline is 0.94 at 09:25
  and 0.98 at 15:00. At 09:25 Polymarket is slightly WORSE than the baseline (pooled Brier 0.216 vs 0.213, gain t = −1.67).
  It is a little overconfident on "Up": the 0.5-0.6 bin resolves Up 50% of the time, and the 0.8-0.9 bin 78%.
  At 10:00 and 15:00 it ties the baseline (gain t = 1.19 and 0.32).
- **Tradable part.** (p_PM − p_base) at 09:25 does not predict open→close: pooled slope ≈ 0.1 bp per +10 pp
  (t = 0.14), rank IC 0.001. The 10:00 and 15:00 pooled slopes are small and positive (≈ 1 bp and 0.3 bp per
  +10 pp to the close, t ≈ 2.3 unadjusted, Holm 1.0), much less than a 4 bp round trip. Treat it as a weak
  hypothesis to watch, not a signal.
  The best single row (META 15:00, t = 3.3, Holm 0.07) is one of 71 tests.
- **Paper rule (long at the open iff p_0925 > 0.60).** Net Sharpe −0.57 vs −0.94 for always-long-at-open, over 272
  days. It loses less only because it is in the market less: open→close was a losing hold in this period
  (−6.5 bp/day after costs; the stocks' gains came overnight). Bootstrap P(rule ≤ always) = 0.29, and its edge flips
  sign between the halves. On markets with ≥ $5k volume the rule's Sharpe is −2.1.
- **Monthly ladders.** No better than a lognormal with trailing 60-day vol (Brier gain −0.017 / +0.004 / −0.006 at
  1 / 5 / 10 days, n = 81 ticker-months over 11 months, all p > 0.17). The h = 1 loss is concentrated in months
  whose last day follows an earnings release (Oct/Apr: AMZN, MSFT, GOOGL), where the ladder correctly widens but
  the realised close landed in the middle. PIT at 10 days is hump-shaped (chi-square p = 0.004): the ladders are too
  wide, i.e. underconfident, not sharp.
- **Caveats.** About 13 months, 2,421 market-days, roughly 270 per name. The MDE at the Holm level is |corr| ≈ 0.08
  pooled and ≈ 0.25 per name, so the test rules out large effects only. The volumes are tiny: median lifetime volume
  is $3.5-6k per single-stock market (SPX median $92k) and SPCX's is $464, so a few hundred dollars can move a
  price. Prices are the CLOB's sampled price (no bid/ask). The source moved from NASDAQ/WSJ to Pyth 1-minute
  candles on 2026-03-25. The 2025-10-15 batch (close vs the same day's OPEN) is excluded. There are no daily markets
  for AVGO, TSM, AMD or ORCL, and QQQ has only 23 days (not run). The baseline is deliberately simple. A fitted
  one would make Polymarket look worse, not better.

**What to log going forward (cheap, forward-only, no model change).** Every trading day, snapshot each daily
Up/Down market's best bid/ask/size and last price at 09:25, 10:00 and 15:00 ET, plus the stock's last pre-market or
intraday trade at the same second. Snapshot the monthly ladders once a day at 16:00 with bid/ask. Re-run this
script unchanged at 12 months of logs. Only the 10:00/15:00 pooled B tests are worth re-testing, and they should
be pre-registered then as the only two tests.

