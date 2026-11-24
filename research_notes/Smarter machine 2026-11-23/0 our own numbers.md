# Our own numbers (2026-11-23)

Computed by Claude on the daily-calls data: about 500 S&P 500 members (the list of 2026-11-18, survivors only), Alpaca
adjusted daily bars 2016-01-04 to 2026-11-23, 332 patterns. Exploration, not tests: nothing here was pre-registered
except where stated, and anything adopted from it is judged on new days.

## 1. How many independent things are there?

| Horizon | Independent ideas among the 332 | Largest idea's share | One day's rank IC wobbles by | Smallest mean IC visible: one idea chosen in advance / best of the lot |
|---|---|---|---|---|
| 21 sessions | 8.3 | 28% | 0.174 | 0.0248 / 0.0430 |
| 5 sessions | 9.0 | 27% | 0.190 | 0.0138 / 0.0243 |
| 1 session | 9.1 | 26% | 0.198 | 0.0082 / 0.0145 |

Independent ideas: (sum of eigenvalues)² / (sum of squared eigenvalues) of the patterns' block-IC correlation. If the
500 stocks moved independently the daily wobble would be 1/sqrt(499) = 0.045. Seen: about 0.19, so the 500 names
carry the information of about 500 x (0.045/0.19)² = 28.

Patterns beyond |t| (close-to-close outcomes, as in rules v2), with luck's average count in brackets:

| Horizon | above 2 | above 2.5 | above 3 | above 3.5 | Share that looks like pure noise | Chance a pattern at 3 is luck |
|---|---|---|---|---|---|---|
| 21 sessions | 10 (14.9) | 2 (3.9) | 0 (0.7) | 0 (0.1) | 83% | 99% |
| 5 sessions | 24 (15.0) | 2 (4.1) | 0 (0.9) | 0 (0.1) | 71% | 61% |
| 1 session | 75 (14.9) | 50 (4.1) | 24 (0.9) | 13 (0.1) | 74% | 6% |

The 12-month trend (return over 252 sessions leaving out the latest 21): t +0.42 at 21 sessions (mean IC +0.0063),
+1.80 at 5 (+0.0147), +3.51 at 1 (+0.0175). If the 1-session edge simply lasted, 5 sessions would show about +0.039
and 21 about +0.080.

Under rules v3 (outcomes from the next open) the 1-session standouts fall to 9, about what luck gives.

## 2. Anatomy of the trend's next-session bet (favoured third minus avoided third)

| Part of the next session | Right | Mean | Median | Lopsidedness (skew) | t |
|---|---|---|---|---|---|
| Whole (close to close) | 55.2% of 2,338 days | +0.56 bp | +8.67 bp | -1.43 | +0.26 |
| Overnight (close to next open) | 55.7% | +2.80 bp | +4.10 bp | -1.71 | +2.54 |
| Daytime (next open to close) | 52.3% | -2.20 bp | +4.03 bp | -0.64 | -1.30 |

- The worst 5% of days sum to -309.7%; all other days sum to +322.7%; total +13.0%.
- Worst days (bet placed at that close, lost the next session): 2020-11-06 -13.3%, 2020-05-15 -6.0%, 2022-11-09
  -5.5%, 2020-05-22 -5.3%, 2020-03-18 -4.2%, 2020-06-05 -4.1%.
- Mean bp a day and share of days right, by year: 2017 -2.0/52%, 2018 +2.4/59%, 2019 -1.3/52%, 2020 -1.1/57%,
  2021 -5.4/51%, 2022 +4.7/56%, 2023 -4.5/50%, 2024 +7.8/57%, 2025 +2.4/59%, 2026 +1.2/57%.
- Market up over the last 21 sessions: -2.13 bp (skew -1.92). Market down over the last 21: +6.44 bp (skew -0.33).
  Market more than 10% below its one-year high: -8.51 bp.
- By how wild the bet itself was over the previous 126 sessions: calm third +3.97 bp, middle +3.14 bp, wild third
  -5.40 bp. Scaling the bet down when it has been wild: t +0.96 and skew -0.58, against +0.25 and -1.40 unscaled.

## 3. Shocks in prices

Definitions fixed before looking. Stock shock: the stock's move against the average stock is more than 3 of its own
normal daily moves on more than twice its normal volume. Market shock: SPY moves more than 2.5 of its normal daily
moves. Normal = the 60 sessions before.

- Relative volatility a year: typical stock 25%; TSLA 55% (rank 17), NVDA 43% (49), AAPL 23% (359), MSFT 22% (381).
- Shock days a year: typical stock 2.3; TSLA 3.1 (rank 86). Most: FSLR 4.8, IBM 4.6, BA 4.3.
- Share of a stock's variance from its wildest 5% of days: typical 52%; TSLA 46% (rank 393).
- Stable trait across stocks, first half against second half: shock frequency +0.44, volatility +0.68, shock
  frequency beyond what volatility explains +0.37.
- After a stock's own shock (11,041 cases on 2,071 dates): its moves are 1.92 times normal the next session, 1.46
  times in sessions 2 to 5, 1.25 times in sessions 6 to 21.
- Direction after an up shock: +7 bp against the average stock next session (t +0.8), +11 bp over 5 (t +0.4), 0 over
  21. After a down shock: -1 bp, -9 bp, -10 bp, all t below 0.5 in size.
- Market shocks: 83 since 2017 (54 down, 29 up); 20 in 2020, 6 in 2025, 11 in 2026. The market's moves stay about
  twice normal for the following 21 sessions (2.07, 2.23, 1.98 times).
- The market after a down shock: +0.26% next session (t +0.9), +1.02% over 21 sessions (ordinary days: +1.25%).
  After an up shock (29 cases): -0.83% next session (t -1.6), -1.63% over 5 (t -1.7). A hint, not evidence.
- Which stocks move most on market shock days repeats: rank correlation +0.40 between a stock's reaction on its
  previous 10 shocks and the next one (73 shock days).
- After a shock, the stocks that moved most with it against those that moved least: -0.18% next session (t -0.9),
  -0.36% over 5 (t -0.7), -0.23% over 21 (t -0.4). Nothing reliable.
- Shock days in 2025 and 2026: 2025-03-10, 04-03 (-4.9%), 04-04 (-5.9%), 04-09 (+10.5%), 08-22, 10-10; 2026-01-20,
  02-06, 03-31, 04-08, 06-05, 10-30, 11-04, 11-05 (-4.4%), 11-09, 11-20 (-3.6%), 11-23 (+4.7%).
