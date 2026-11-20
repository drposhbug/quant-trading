# Prediction-market odds around scheduled announcements (FOMC, CPI, earnings, IPOs)

Study only: model.py stays frozen. Code: `event_odds_study.py` (self-check: `test_event_odds_study.py`).

## 0. Pre-registration (written 2026-11-20 before any odds-at-horizon, outcome or return was computed)

Only market inventories (which events/markets exist, close times) were looked at before writing this.

**Question.** Around scheduled announcements, do Kalshi/Polymarket odds (a) predict the announcement before it happens,
and (b) carry tradable information about the stock/index move?

**Events and odds sources (2023-01 .. 2026-11, resolved only).**
- FOMC: Kalshi FEDDECISION/KXFEDDECISION (legs = rate change in bp; primary). Polymarket fed-decision / fed-interest-rates
  events: accuracy only (secondary). T = 14:00 ET on the scheduled statement day (events_study.FOMC).
- CPI: Kalshi CPI/KXCPI headline MoM ladder ("above k%"; primary). Kalshi CPIYOY and Polymarket "<month>-inflation-us-monthly":
  accuracy only (secondary). T = 08:30 ET on the release day (date of the Kalshi market close).
- Earnings (TSLA NVDA AAPL MSFT GOOGL AMZN META AVGO TSM AMD ORCL, + SPCX): Polymarket "Will X beat quarterly earnings?"
  (EPS > consensus at creation). Kalshi has only earnings-call *mention* markets, not beat markets -> none used.
  T = SEC 8-K Item 2.02 acceptance time (events_study cache) for the matching report; TSM (6-K filer) = 00:30 ET on the
  slug date (TSMC releases ~01:00-02:00 ET).
- IPOs (ANT 2026-11-19, SPCX): Polymarket IPO-day price/market-cap/pop buckets. n = 2 issues -> descriptive only, no test.

**Odds at horizon h** = last observation stamped at or before T - h (h = 1 day, 1 hour, 5 minutes), minute fidelity
(Kalshi: mid of yes bid/ask from 1-min candlesticks, last price if no two-sided quote; Polymarket: CLOB prices-history
fidelity=1), no older than 2 days. Multi-leg events are summarised by the market-implied expectation E_h:
- FOMC: E = sum_k dbp_k p_k with legs' p normalised to sum to 1; actual = dbp of the leg that resolved YES.
- CPI ladder: E-differences and surprise use sum_i w_i (.) over strikes, w_i = gap to the next strike (0.1 for the last).
- Earnings: E = p(beat).
- **Surprise** S = actual - E_5min (FOMC: bp; CPI: pp of MoM CPI; earnings: y - p).

**Assets.** FOMC: SPY (primary), QQQ, SHY (2y-yield proxy). CPI: SPY (primary), QQQ. Earnings: the stock minus QQQ
(same window). Alpaca SIP 1-min bars (FOMC/CPI), daily bars (earnings). Price at time t = close of the last 1-min bar
starting before t (no look-ahead).

**Primary post-announcement return** (one per type): FOMC SPY 14:00 -> 14:30. CPI SPY 08:30 (pre-market) -> 10:00.
Earnings: last close before T -> close of the first session after T (stock minus QQQ).
Secondary (reported, not in Holm): FOMC 5/60 min, QQQ, SHY; CPI 08:30->08:35, 09:30->09:35/10:00/10:30, QQQ;
earnings next open -> close.

**Primary tests (Holm across all 15; pass = Holm p < 0.05 AND same sign in both chronological halves).**
For each type in {FOMC, CPI, Earnings}:
1. Accuracy at T-5min: per-event mean leg Brier of the market vs a naive forecast, paired t over events (df = n-1).
   Naive: FOMC = persistence (previous meeting's decision gets probability 1); CPI = persistence (previous month's print);
   earnings = leave-one-out pooled beat rate. T-1d, T-1h, log loss, 50% baseline and calibration: secondary.
2a. Late information ("leak"): OLS, one row per event, of S_1h = actual - E_1h on dE_late = E_5min - E_1h (HC1 SE, t on n-2 df).
2b. Same dE_late -> primary post-announcement return.
3. Surprise -> reaction: primary return on S (expected sign: FOMC/CPI negative, earnings positive).
4. Tradable rule (fixed, one per type, 2 bp per side = 4 bp round trip):
   s = sign of the odds drift E_5min - E_1d, oriented so "good for stocks" is +1 (FOMC/CPI: s = -sign(dE), earnings:
   s = +sign(dp)); no trade if |dE| is below 0.5 bp (FOMC), 0.005 pp (CPI), 0.005 (earnings).
   Trade only when the asset's own pre-announcement drift (previous close -> T-5min; earnings: previous session's
   close-to-close excess return) has the opposite sign to s ("the stock has not followed the odds").
   Position s in the primary asset from T-5min to the end of the primary window. Test: mean net return > 0, t over trades.

**Power.** n is fixed by history: ~29 Kalshi FOMC meetings, ~46 CPI releases, ~45 earnings markets (2025-10 onward).
A 30-event regression detects only |corr| >~ 0.5 at 80% power; most of these tests are underpowered and a fail is
"no evidence", not "no effect".

<!-- RESULTS BELOW ARE WRITTEN BY event_odds_study.py on 2026-11-20 -->

## 1. Inventory (events x markets found, resolved, 2023-01 .. 2026-11)

| type     | src        |   events |   legs | first      | last       |   events with odds at T-1d/1h/5m |
|:---------|:-----------|---------:|-------:|:-----------|:-----------|---------------------------------:|
| CPI      | kalshi     |       45 |    401 | 2023-01-12 | 2026-11-10 |                               45 |
| CPI      | polymarket |        9 |     74 | 2025-12-18 | 2026-11-10 |                                9 |
| CPI YoY  | kalshi     |       44 |    642 | 2023-01-12 | 2026-10-14 |                               44 |
| Earnings | polymarket |       46 |     46 | 2025-10-29 | 2026-11-17 |                               46 |
| FOMC     | kalshi     |       27 |    135 | 2023-05-03 | 2026-10-28 |                               27 |
| FOMC     | polymarket |       32 |    130 | 2023-02-01 | 2026-10-28 |                               31 |

Earnings events with odds at all three horizons, by ticker: AAPL 3, AMD 5, AMZN 5, AVGO 4, GOOGL 5, META 5, MSFT 3, NVDA 4, ORCL 4, SPCX 1, TSLA 4, TSM 3. Kalshi lists no beat/EPS markets for these names (only earnings-call *mention* markets).
Excluded: Kalshi CPI -25SEP, -25OCT (2025 shutdown: Sept CPI released 2025-10-24 after trading closed 10-15; October CPI never published).

## 2. Results: pre-registered primary tests (Holm across all 15)

| type     | test                                          |   n |   effect | unit      |        t |        p |   holm_p |       h1 |       h2 | pass   |
|:---------|:----------------------------------------------|----:|---------:|:----------|---------:|---------:|---------:|---------:|---------:|:-------|
| FOMC     | 1 accuracy: naive Brier - market Brier (T-5m) |  25 |   0.1466 | Brier pts |   3.5905 |   0.0015 |   0.0191 |   0.1408 |   0.1519 | True   |
| FOMC     | 2a leak: (actual - E_1h) on (E_5m - E_1h)     |  26 |   4.7845 | slope     |   2.2926 |   0.0309 |   0.3093 |  11.1899 |   2.6335 | False  |
| FOMC     | 2b late odds move -> SPY_30m                  |  26 |  -0.0012 | slope     |  -1.2565 |   0.2210 |   1.0000 |  -0.0024 |  -0.0009 | False  |
| FOMC     | 3 surprise -> SPY_30m                         |  26 |  -0.0003 | slope     |  -3.9730 |   0.0006 |   0.0079 |  -0.0003 |  -0.0003 | True   |
| FOMC     | 4 rule: net return, SPY_hold (trades only)    |   0 | nan      | mean      | nan      | nan      |   1.0000 | nan      | nan      | False  |
| CPI      | 1 accuracy: naive Brier - market Brier (T-5m) |  43 |   0.1746 | Brier pts |   6.1454 |   0.0000 |   0.0000 |   0.1298 |   0.2174 | True   |
| CPI      | 2a leak: (actual - E_1h) on (E_5m - E_1h)     |  44 |  -1.0500 | slope     |  -1.2487 |   0.2187 |   1.0000 |   0.2305 |  -4.4657 | False  |
| CPI      | 2b late odds move -> SPY_to1000               |  44 |  -0.0735 | slope     |  -2.6253 |   0.0120 |   0.1323 |  -0.0883 |  -0.0424 | False  |
| CPI      | 3 surprise -> SPY_to1000                      |  44 |  -0.0236 | slope     |  -2.2008 |   0.0333 |   0.3093 |  -0.0475 |  -0.0027 | False  |
| CPI      | 4 rule: net return, SPY_hold (trades only)    |  11 |  -0.0042 | mean      |  -1.6667 |   0.1265 |   0.7593 |  -0.0053 |  -0.0033 | False  |
| Earnings | 1 accuracy: naive Brier - market Brier (T-5m) |  46 |   0.0194 | Brier pts |   0.6591 |   0.5132 |   1.0000 |  -0.0338 |   0.0726 | False  |
| Earnings | 2a leak: (actual - E_1h) on (E_5m - E_1h)     |  46 |   1.7975 | slope     |   3.1763 |   0.0027 |   0.0327 |   2.7952 |   1.7166 | True   |
| Earnings | 2b late odds move -> c2c                      |  46 |  -0.1023 | slope     |  -1.2991 |   0.2007 |   1.0000 |   0.0868 |  -0.1145 | False  |
| Earnings | 3 surprise -> c2c                             |  46 |   0.0510 | slope     |   2.0303 |   0.0484 |   0.3872 |   0.0572 |   0.0407 | False  |
| Earnings | 4 rule: net return, hold (trades only)        |  16 |  -0.0312 | mean      |  -2.0084 |   0.0630 |   0.4407 |  -0.0397 |  -0.0227 | False  |

**4 of 15 pass.** Units: FOMC E/S in bp, CPI in pp of MoM CPI, earnings in probability; returns are fractions (0.001 = 10 bp). h1/h2 = same statistic in the earlier/later half of events.

## 3. Accuracy (all sources and horizons; secondary except the Kalshi FOMC/CPI and Polymarket earnings T-5m rows tested above)

Brier = mean over legs per event, then over events. naive = persistence (Kalshi FOMC/CPI) or leave-one-out beat rate (earnings). uniform = 1/K for exclusive buckets, 0.5 for ladders/binaries.

| type     | src        | horizon   |   events |   brier |    naive |   uniform |   logloss |   leg_hit |
|:---------|:-----------|:----------|---------:|--------:|---------:|----------:|----------:|----------:|
| CPI      | kalshi     | T-1d      |       45 |  0.0613 |   0.2397 |    0.2500 |    0.2057 |    0.9243 |
| CPI      | kalshi     | T-1h      |       45 |  0.0596 |   0.2397 |    0.2500 |    0.2032 |    0.9265 |
| CPI      | kalshi     | T-5m      |       45 |  0.0633 |   0.2397 |    0.2500 |    0.2108 |    0.9141 |
| CPI      | polymarket | T-1d      |        9 |  0.0478 | nan      |    0.1100 |    0.1582 |    0.9407 |
| CPI      | polymarket | T-1h      |        9 |  0.0424 | nan      |    0.1100 |    0.1506 |    0.9753 |
| CPI      | polymarket | T-5m      |        9 |  0.0424 | nan      |    0.1100 |    0.1468 |    0.9630 |
| CPI YoY  | kalshi     | T-1d      |       44 |  0.0523 | nan      |    0.2500 |    0.1848 |    0.9384 |
| CPI YoY  | kalshi     | T-1h      |       44 |  0.0597 | nan      |    0.2500 |    0.2002 |    0.9273 |
| CPI YoY  | kalshi     | T-5m      |       44 |  0.0594 | nan      |    0.2500 |    0.2002 |    0.9194 |
| Earnings | polymarket | T-1d      |       46 |  0.1249 |   0.1348 |    0.2500 |    0.3892 |    0.8261 |
| Earnings | polymarket | T-1h      |       46 |  0.1396 |   0.1348 |    0.2500 |    0.4384 |    0.8043 |
| Earnings | polymarket | T-5m      |       46 |  0.1154 |   0.1348 |    0.2500 |    0.3828 |    0.8478 |
| FOMC     | kalshi     | T-1d      |       27 |  0.0042 |   0.1520 |    0.1602 |    0.0251 |    1.0000 |
| FOMC     | kalshi     | T-1h      |       27 |  0.0064 |   0.1520 |    0.1602 |    0.0286 |    0.9852 |
| FOMC     | kalshi     | T-5m      |       27 |  0.0051 |   0.1520 |    0.1602 |    0.0251 |    0.9852 |
| FOMC     | polymarket | T-1d      |       31 |  0.0052 | nan      |    0.1882 |    0.0322 |    1.0000 |
| FOMC     | polymarket | T-1h      |       31 |  0.0084 | nan      |    0.1882 |    0.0389 |    0.9839 |
| FOMC     | polymarket | T-5m      |       31 |  0.0092 | nan      |    0.1882 |    0.0409 |    0.9758 |

### Calibration, all legs pooled

T-1d:

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 608 | 0.017 | 0.007 | [0.003, 0.017] |
| 0.1–0.2 | 57 | 0.143 | 0.088 | [0.038, 0.189] |
| 0.2–0.3 | 28 | 0.249 | 0.107 | [0.037, 0.272] |
| 0.3–0.4 | 30 | 0.355 | 0.200 | [0.095, 0.373] |
| 0.4–0.5 | 29 | 0.450 | 0.276 | [0.147, 0.457] |
| 0.5–0.6 | 30 | 0.537 | 0.667 | [0.488, 0.808] |
| 0.6–0.7 | 30 | 0.644 | 0.767 | [0.591, 0.882] |
| 0.7–0.8 | 28 | 0.751 | 0.750 | [0.566, 0.873] |
| 0.8–0.9 | 50 | 0.856 | 0.900 | [0.786, 0.957] |
| 0.9–1.0 | 402 | 0.974 | 0.980 | [0.961, 0.990] |

T-5min:

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 594 | 0.018 | 0.005 | [0.002, 0.015] |
| 0.1–0.2 | 56 | 0.144 | 0.071 | [0.028, 0.170] |
| 0.2–0.3 | 35 | 0.252 | 0.086 | [0.030, 0.224] |
| 0.3–0.4 | 20 | 0.347 | 0.350 | [0.181, 0.567] |
| 0.4–0.5 | 37 | 0.457 | 0.324 | [0.196, 0.485] |
| 0.5–0.6 | 40 | 0.526 | 0.500 | [0.352, 0.648] |
| 0.6–0.7 | 30 | 0.642 | 0.767 | [0.591, 0.882] |
| 0.7–0.8 | 30 | 0.751 | 0.667 | [0.488, 0.808] |
| 0.8–0.9 | 48 | 0.848 | 0.896 | [0.778, 0.955] |
| 0.9–1.0 | 402 | 0.975 | 0.980 | [0.961, 0.990] |

## 4. Secondary reaction regressions (not Holm-corrected; exploratory)

| type     | test                                                |   n |   effect |       t |      p |
|:---------|:----------------------------------------------------|----:|---------:|--------:|-------:|
| FOMC     | SPY_5m on S                                         |  26 |  -0.0003 | -5.4052 | 0.0000 |
| FOMC     | SPY_5m on dE_late                                   |  26 |  -0.0018 | -2.4315 | 0.0229 |
| FOMC     | SPY_60m on S                                        |  26 |  -0.0003 | -0.9302 | 0.3615 |
| FOMC     | SPY_60m on dE_late                                  |  26 |  -0.0005 | -0.2291 | 0.8207 |
| FOMC     | QQQ_5m on S                                         |  26 |  -0.0004 | -3.9452 | 0.0006 |
| FOMC     | QQQ_5m on dE_late                                   |  26 |  -0.0023 | -2.7083 | 0.0123 |
| FOMC     | QQQ_30m on S                                        |  26 |  -0.0004 | -4.4955 | 0.0001 |
| FOMC     | QQQ_30m on dE_late                                  |  26 |  -0.0017 | -1.5153 | 0.1428 |
| FOMC     | QQQ_60m on S                                        |  26 |  -0.0003 | -0.9121 | 0.3708 |
| FOMC     | QQQ_60m on dE_late                                  |  26 |  -0.0016 | -0.5504 | 0.5871 |
| FOMC     | SHY_5m on S                                         |  26 |  -0.0001 | -3.0636 | 0.0053 |
| FOMC     | SHY_5m on dE_late                                   |  26 |  -0.0001 | -0.2198 | 0.8279 |
| FOMC     | SHY_30m on S                                        |  26 |  -0.0001 | -3.9237 | 0.0006 |
| FOMC     | SHY_30m on dE_late                                  |  26 |  -0.0001 | -0.3663 | 0.7174 |
| FOMC     | SHY_60m on S                                        |  26 |  -0.0001 | -2.4028 | 0.0244 |
| FOMC     | SHY_60m on dE_late                                  |  26 |  -0.0001 | -0.1914 | 0.8499 |
| CPI      | SPY_5m on S                                         |  44 |  -0.0362 | -6.4827 | 0.0000 |
| CPI      | SPY_5m on dE_late                                   |  44 |   0.0468 |  1.7886 | 0.0809 |
| CPI      | SPY_open5m on S                                     |  44 |   0.0005 |  0.2789 | 0.7817 |
| CPI      | SPY_open5m on dE_late                               |  44 |  -0.0019 | -0.1610 | 0.8729 |
| CPI      | SPY_open30m on S                                    |  44 |   0.0066 |  1.4163 | 0.1641 |
| CPI      | SPY_open30m on dE_late                              |  44 |  -0.0474 | -2.1521 | 0.0372 |
| CPI      | SPY_open60m on S                                    |  44 |   0.0065 |  1.0955 | 0.2795 |
| CPI      | SPY_open60m on dE_late                              |  44 |  -0.0547 | -2.6426 | 0.0115 |
| CPI      | QQQ_5m on S                                         |  44 |  -0.0470 | -6.4015 | 0.0000 |
| CPI      | QQQ_5m on dE_late                                   |  44 |   0.0643 |  1.9752 | 0.0548 |
| CPI      | QQQ_to1000 on S                                     |  44 |  -0.0181 | -1.4968 | 0.1419 |
| CPI      | QQQ_to1000 on dE_late                               |  44 |  -0.0679 | -2.0698 | 0.0447 |
| CPI      | QQQ_open5m on S                                     |  44 |   0.0015 |  0.5124 | 0.6110 |
| CPI      | QQQ_open5m on dE_late                               |  44 |  -0.0176 | -1.6496 | 0.1065 |
| CPI      | QQQ_open30m on S                                    |  44 |   0.0181 |  3.1883 | 0.0027 |
| CPI      | QQQ_open30m on dE_late                              |  44 |  -0.0633 | -2.9905 | 0.0046 |
| CPI      | QQQ_open60m on S                                    |  44 |   0.0196 |  2.7186 | 0.0095 |
| CPI      | QQQ_open60m on dE_late                              |  44 |  -0.0805 | -2.6450 | 0.0114 |
| Earnings | o2c on S                                            |  46 |  -0.0109 | -0.9913 | 0.3269 |
| Earnings | o2c on dE_late                                      |  46 |  -0.0220 | -0.4525 | 0.6532 |
| FOMC     | robustness: test 3 without largest |S| (2024-09-18) |  25 |   0.0000 |  0.0533 | 0.9579 |
| CPI      | robustness: test 3 without largest |S| (2025-02-12) |  43 |  -0.0221 | -1.7979 | 0.0796 |
| Earnings | robustness: test 3 without largest |S| (2026-02-05) |  45 |   0.0490 |  1.5946 | 0.1181 |

## 5. IPOs (descriptive, n = 2 issues)

| issuer   | snapshot      |   legs |   brier |   brier50 |   mean_p_winners |   mean_p_losers |
|:---------|:--------------|-------:|--------:|----------:|-----------------:|----------------:|
| ANT      | T-1d 16:00    |     68 |  0.0642 |    0.2500 |           0.6629 |          0.1011 |
| ANT      | IPO day 09:00 |     68 |  0.0810 |    0.2500 |           0.7195 |          0.1416 |
| SPCX     | T-1d 16:00    |     23 |  0.0382 |    0.2500 |           0.8389 |          0.1147 |
| SPCX     | IPO day 09:00 |     23 |  0.0461 |    0.2500 |           0.8819 |          0.1425 |

<details><summary>FOMC event list (26)</summary>

| T                |     E_1d |     E_1h |     E_5m |   actual |        S |   SPY_drift |   SPY_30m |   SHY_30m |
|:-----------------|---------:|---------:|---------:|---------:|---------:|------------:|----------:|----------:|
| 2023-06-14 14:00 |   0.9852 |   0.7389 |   0.7389 |   0.0000 |  -0.7389 |      0.0017 |   -0.0064 |   -0.0021 |
| 2023-07-26 14:00 |  24.7525 |  24.7500 |  24.7500 |  25.0000 |   0.2500 |     -0.0024 |    0.0002 |   -0.0003 |
| 2023-09-20 14:00 |   0.2463 |   0.2463 |   0.1238 |   0.0000 |  -0.1238 |      0.0020 |   -0.0022 |   -0.0008 |
| 2023-11-01 14:00 |   0.2463 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |      0.0043 |    0.0006 |    0.0003 |
| 2023-12-13 14:00 |   0.2488 |   0.2475 |   0.1281 |   0.0000 |  -0.1281 |      0.0008 |    0.0065 |    0.0029 |
| 2024-01-31 14:00 |  -0.2475 |  -0.4950 |  -0.2475 |   0.0000 |   0.2475 |     -0.0072 |   -0.0026 |   -0.0004 |
| 2024-03-20 14:00 |  -0.2475 |  -0.2475 |  -0.2488 |   0.0000 |   0.2488 |     -0.0002 |    0.0042 |    0.0005 |
| 2024-05-01 14:00 |  -0.0000 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |     -0.0020 |    0.0041 |    0.0003 |
| 2024-06-12 14:00 |  -0.3731 |  -0.3731 |  -0.3731 |   0.0000 |   0.3731 |      0.0106 |    0.0002 |   -0.0004 |
| 2024-07-31 14:00 |  -0.4975 |  -0.4975 |  -0.4950 |   0.0000 |   0.4950 |      0.0162 |    0.0012 |   -0.0004 |
| 2024-09-18 14:00 | -37.5616 | -34.8522 | -36.0714 | -50.0000 | -13.9286 |     -0.0001 |    0.0049 |    0.0017 |
| 2024-11-07 14:00 | -24.2537 | -24.5050 | -24.7500 | -25.0000 |  -0.2500 |      0.0068 |   -0.0001 |   -0.0003 |
| 2024-12-18 14:00 | -23.6453 | -23.6453 | -24.0148 | -25.0000 |  -0.9852 |      0.0022 |   -0.0089 |   -0.0014 |
| 2025-01-29 14:00 |  -0.0000 |  -0.1238 |  -0.1225 |   0.0000 |   0.1225 |     -0.0043 |   -0.0035 |   -0.0005 |
| 2025-03-19 14:00 |  -0.2475 |  -0.2475 |  -0.2475 |   0.0000 |   0.2475 |      0.0041 |    0.0026 |    0.0014 |
| 2025-05-07 14:00 |  -0.6188 |  -0.6188 |  -0.6127 |   0.0000 |   0.6127 |      0.0011 |   -0.0023 |    0.0004 |
| 2025-06-18 14:00 |  -0.3713 |  -0.3695 |  -0.2463 |   0.0000 |   0.2463 |      0.0038 |   -0.0003 |    0.0004 |
| 2025-07-30 14:00 |  -0.4926 |  -0.4926 |  -0.4926 |   0.0000 |   0.4926 |      0.0022 |    0.0002 |    0.0003 |
| 2025-12-10 14:00 | -23.6453 | -23.8916 | -23.6585 | -25.0000 |  -1.3415 |     -0.0004 |    0.0020 |    0.0002 |
| 2026-01-28 14:00 |  -0.0000 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |     -0.0008 |   -0.0013 |   -0.0001 |
| 2026-03-18 14:00 |  -0.0000 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |     -0.0063 |   -0.0009 |    0.0002 |
| 2026-04-29 14:00 |  -0.0000 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |     -0.0019 |   -0.0020 |   -0.0004 |
| 2026-06-17 14:00 |  -0.0000 |  -0.0000 |  -0.0000 |   0.0000 |   0.0000 |      0.0000 |   -0.0062 |   -0.0014 |
| 2026-07-29 14:00 |   4.9751 |   6.7164 |   4.6798 |   0.0000 |  -4.6798 |     -0.0062 |    0.0012 |   -0.0002 |
| 2026-09-16 14:00 |  21.1823 |  21.5347 |  20.9360 |  25.0000 |   4.0640 |      0.0032 |   -0.0008 |   -0.0010 |
| 2026-10-28 14:00 |   1.4778 |   0.9852 |   0.4975 |   0.0000 |  -0.4975 |      0.0023 |   -0.0005 |   -0.0001 |

</details>

<details><summary>CPI event list (44)</summary>

| T                |       X |   E_1d |   E_1h |   E_5m |       S |   SPY_drift |   SPY_5m |   SPY_to1000 |
|:-----------------|--------:|-------:|-------:|-------:|--------:|------------:|---------:|-------------:|
| 2023-02-14 08:30 |  0.5000 | 0.4630 | 0.4625 | 0.4630 |  0.0370 |      0.0032 |   0.0015 |      -0.0023 |
| 2023-03-14 08:30 |  0.4000 | 0.4085 | 0.4055 | 0.3215 |  0.0785 |      0.0091 |  -0.0018 |       0.0065 |
| 2023-04-12 08:30 |  0.1000 | 0.2375 | 0.2250 | 0.2110 | -0.1110 |      0.0011 |   0.0086 |       0.0023 |
| 2023-05-10 08:30 |  0.4000 | 0.3975 | 0.4100 | 0.4130 | -0.0130 |     -0.0009 |   0.0042 |       0.0046 |
| 2023-06-13 08:30 |  0.1000 | 0.3365 | 0.3265 | 0.3280 | -0.0280 |      0.0007 |   0.0003 |       0.0028 |
| 2023-07-12 08:30 |  0.2000 | 0.2010 | 0.1960 | 0.1785 |  0.0215 |      0.0023 |   0.0044 |       0.0074 |
| 2023-08-10 08:30 |  0.2000 | 0.3980 | 0.4050 | 0.4040 | -0.0040 |      0.0059 |  -0.0003 |       0.0067 |
| 2023-09-13 08:30 |  0.6000 | 0.6415 | 0.6395 | 0.6370 | -0.0370 |     -0.0001 |  -0.0016 |       0.0020 |
| 2023-10-12 08:30 |  0.4000 | 0.6320 | 0.6300 | 0.6330 |  0.0670 |      0.0044 |  -0.0026 |      -0.0068 |
| 2023-11-14 08:30 |  0.0000 | 0.3715 | 0.3850 | 0.3885 | -0.0885 |      0.0014 |   0.0102 |       0.0165 |
| 2023-12-12 08:30 |  0.1000 | 0.2585 | 0.2555 | 0.2550 |  0.0450 |      0.0022 |  -0.0016 |      -0.0038 |
| 2024-01-11 08:30 |  0.3000 | 0.4445 | 0.4435 | 0.4395 |  0.0605 |      0.0025 |  -0.0026 |      -0.0031 |
| 2024-02-13 08:30 |  0.3000 | 0.3455 | 0.3630 | 0.3695 |  0.1305 |     -0.0029 |  -0.0068 |      -0.0109 |
| 2024-03-12 08:30 |  0.4000 | 0.5690 | 0.5535 | 0.5570 | -0.0570 |      0.0028 |   0.0011 |       0.0014 |
| 2024-04-10 08:30 |  0.4000 | 0.1810 | 0.1945 | 0.1930 |  0.1070 |      0.0017 |  -0.0129 |      -0.0133 |
| 2024-05-15 08:30 |  0.3000 | 0.2730 | 0.2775 | 0.2800 | -0.0800 |      0.0003 |   0.0044 |       0.0038 |
| 2024-06-12 08:30 |  0.0000 | 0.2080 | 0.2160 | 0.2145 | -0.1145 |      0.0012 |   0.0057 |       0.0087 |
| 2024-07-11 08:30 | -0.1000 | 0.1460 | 0.1455 | 0.1465 | -0.1465 |     -0.0012 |   0.0038 |       0.0017 |
| 2024-08-14 08:30 |  0.2000 | 0.2805 | 0.2760 | 0.2670 |  0.0330 |      0.0004 |  -0.0018 |      -0.0020 |
| 2024-09-11 08:30 |  0.2000 | 0.2610 | 0.2670 | 0.2705 |  0.0295 |     -0.0012 |  -0.0035 |      -0.0070 |
| 2024-10-10 08:30 |  0.2000 | 0.1905 | 0.1965 | 0.1965 |  0.1035 |     -0.0005 |  -0.0010 |      -0.0020 |
| 2024-11-13 08:30 |  0.2000 | 0.4525 | 0.4745 | 0.4700 | -0.1700 |     -0.0015 |   0.0030 |       0.0017 |
| 2024-12-11 08:30 |  0.3000 | 0.3765 | 0.3915 | 0.3945 |  0.0055 |      0.0014 |   0.0018 |       0.0048 |
| 2025-01-15 08:30 |  0.4000 | 0.4220 | 0.4745 | 0.4675 |  0.0325 |      0.0040 |   0.0109 |       0.0132 |
| 2025-02-12 08:30 |  0.5000 | 0.4260 | 0.4170 | 0.3965 |  0.2035 |      0.0001 |  -0.0088 |      -0.0064 |
| 2025-03-12 08:30 |  0.2000 | 0.4090 | 0.4055 | 0.4080 | -0.1080 |      0.0087 |   0.0029 |      -0.0027 |
| 2025-04-10 08:30 | -0.1000 | 0.2130 | 0.1715 | 0.1880 | -0.1880 |     -0.0197 |   0.0043 |      -0.0075 |
| 2025-05-13 08:30 |  0.2000 | 0.3655 | 0.3680 | 0.3710 | -0.0710 |     -0.0005 |   0.0013 |       0.0040 |
| 2025-06-11 08:30 |  0.1000 | 0.2515 | 0.2760 | 0.2805 | -0.0805 |     -0.0014 |   0.0040 |       0.0015 |
| 2025-07-15 08:30 |  0.3000 | 0.3450 | 0.3440 | 0.3430 |  0.0570 |      0.0026 |   0.0017 |      -0.0013 |
| 2025-08-12 08:30 |  0.2000 | 0.3430 | 0.3565 | 0.3570 | -0.0570 |      0.0006 |   0.0032 |       0.0014 |
| 2025-09-11 08:30 |  0.4000 | 0.4270 | 0.4230 | 0.4195 |  0.0805 |      0.0023 |  -0.0020 |       0.0027 |
| 2025-12-18 08:30 |  0.2000 | 0.3460 | 0.3335 | 0.3410 | -0.0410 |      0.0048 |   0.0017 |       0.0052 |
| 2026-01-13 08:30 |  0.3000 | 0.4060 | 0.4215 | 0.4215 | -0.0215 |     -0.0012 |   0.0033 |      -0.0003 |
| 2026-02-13 08:30 |  0.2000 | 0.3350 | 0.3435 | 0.3730 | -0.0730 |     -0.0017 |   0.0022 |      -0.0010 |
| 2026-03-11 08:30 |  0.3000 | 0.3455 | 0.3660 | 0.3505 |  0.0495 |     -0.0007 |  -0.0023 |       0.0008 |
| 2026-04-10 08:30 |  0.9000 | 1.0015 | 0.9995 | 1.0000 |  0.0000 |      0.0009 |  -0.0003 |      -0.0008 |
| 2026-05-12 08:30 |  0.6000 | 0.6845 | 0.6945 | 0.7065 | -0.0065 |     -0.0045 |   0.0002 |      -0.0014 |
| 2026-06-10 08:30 |  0.5000 | 0.8010 | 0.8015 | 0.7975 |  0.0025 |     -0.0086 |   0.0024 |       0.0057 |
| 2026-07-14 08:30 | -0.3000 | 0.1515 | 0.1620 | 0.1770 | -0.1770 |     -0.0005 |   0.0046 |       0.0029 |
| 2026-08-12 08:30 |  0.1000 | 0.4695 | 0.4870 | 0.4870 |  0.0130 |      0.0030 |  -0.0001 |      -0.0012 |
| 2026-09-11 08:30 |  0.4000 | 0.7610 | 0.7645 | 0.7410 |  0.0590 |      0.0063 |  -0.0012 |       0.0037 |
| 2026-10-14 08:30 |  0.6000 | 0.9610 | 0.9780 | 0.9735 |  0.0265 |      0.0025 |  -0.0055 |      -0.0089 |
| 2026-11-10 08:30 |  0.4000 | 0.3750 | 0.3635 | 0.3645 |  0.1355 |      0.0007 |  -0.0044 |      -0.0033 |

</details>

<details><summary>Earnings event list (46)</summary>

| T                | tk    |   E_1d |   E_1h |   E_5m |   actual |   drift |     c2c |
|:-----------------|:------|-------:|-------:|-------:|---------:|--------:|--------:|
| 2025-10-29 16:00 | GOOGL | 0.8100 | 0.7950 | 0.7850 |   1.0000 |  0.0220 |  0.0405 |
| 2025-10-29 16:00 | META  | 0.9050 | 0.9000 | 0.9050 |   0.0000 | -0.0042 | -0.0980 |
| 2025-10-30 16:00 | AMZN  | 0.8950 | 0.8700 | 0.8900 |   1.0000 | -0.0170 |  0.0910 |
| 2025-11-04 16:00 | AMD   | 0.9030 | 0.9040 | 0.8990 |   1.0000 | -0.0167 |  0.0186 |
| 2025-12-10 16:00 | ORCL  | 0.8300 | 0.8300 | 0.9100 |   1.0000 |  0.0026 | -0.1051 |
| 2025-12-11 16:00 | AVGO  | 0.9415 | 0.9645 | 0.9425 |   1.0000 | -0.0127 | -0.0952 |
| 2026-01-15 00:30 | TSM   | 0.9355 | 0.8820 | 0.9380 |   1.0000 | -0.0017 |  0.0408 |
| 2026-01-28 16:00 | META  | 0.8900 | 0.7850 | 0.8200 |   1.0000 | -0.0096 |  0.1100 |
| 2026-01-28 16:00 | TSLA  | 0.2450 | 0.4050 | 0.3700 |   1.0000 | -0.0020 | -0.0285 |
| 2026-02-03 16:00 | AMD   | 0.8800 | 0.9050 | 0.9000 |   1.0000 | -0.0015 | -0.1557 |
| 2026-02-04 16:00 | GOOGL | 0.9625 | 0.9500 | 0.9400 |   1.0000 | -0.0022 |  0.0090 |
| 2026-02-05 16:00 | AMZN  | 0.9105 | 0.9595 | 0.9585 |   0.0000 | -0.0298 | -0.0767 |
| 2026-02-25 16:00 | NVDA  | 0.9190 | 0.9320 | 0.9155 |   1.0000 | -0.0005 | -0.0425 |
| 2026-03-04 16:00 | AVGO  | 0.9350 | 0.9560 | 0.9545 |   1.0000 | -0.0035 |  0.0510 |
| 2026-03-10 16:00 | ORCL  | 0.7850 | 0.7550 | 0.7500 |   1.0000 | -0.0142 |  0.0919 |
| 2026-04-16 00:30 | TSM   | 0.9600 | 0.9845 | 0.9755 |   1.0000 | -0.0266 | -0.0362 |
| 2026-04-22 16:00 | TSLA  | 0.1850 | 0.2200 | 0.3550 |   1.0000 | -0.0139 | -0.0300 |
| 2026-04-29 16:00 | AMZN  | 0.9355 | 0.9420 | 0.9050 |   1.0000 |  0.0067 | -0.0016 |
| 2026-04-29 16:00 | MSFT  | 0.9235 | 0.8910 | 0.9015 |   1.0000 | -0.0173 | -0.0486 |
| 2026-04-29 16:00 | META  | 0.9040 | 0.9100 | 0.8870 |   1.0000 | -0.0094 | -0.0948 |
| 2026-04-29 16:00 | GOOGL | 0.9465 | 0.9690 | 0.9805 |   1.0000 | -0.0057 |  0.0903 |
| 2026-04-30 16:00 | AAPL  | 0.9350 | 0.9420 | 0.9610 |   1.0000 | -0.0049 |  0.0228 |
| 2026-05-05 16:00 | AMD   | 0.9665 | 0.9635 | 0.9640 |   1.0000 |  0.0272 |  0.1654 |
| 2026-05-20 16:00 | NVDA  | 0.9735 | 0.9730 | 0.9575 |   1.0000 | -0.0036 | -0.0196 |
| 2026-06-03 16:00 | AVGO  | 0.9570 | 0.9605 | 0.9615 |   1.0000 | -0.0023 | -0.1210 |
| 2026-06-10 16:00 | ORCL  | 0.9150 | 0.2300 | 0.5350 |   1.0000 | -0.0021 | -0.1190 |
| 2026-07-16 00:30 | TSM   | 0.8700 | 0.9300 | 0.9300 |   1.0000 |  0.0005 | -0.0068 |
| 2026-07-22 16:00 | TSLA  | 0.7400 | 0.7750 | 0.6300 |   0.0000 | -0.0079 | -0.1262 |
| 2026-07-22 16:00 | GOOGL | 0.9605 | 0.9760 | 0.9725 |   1.0000 | -0.0095 | -0.0523 |
| 2026-07-29 16:00 | MSFT  | 0.9150 | 0.9300 | 0.9300 |   1.0000 |  0.0132 |  0.1221 |
| 2026-07-29 16:00 | META  | 0.8460 | 0.8785 | 0.8780 |   0.0000 |  0.0072 | -0.1125 |
| 2026-07-30 16:00 | AMZN  | 0.9485 | 0.9155 | 0.9365 |   1.0000 |  0.0061 |  0.1467 |
| 2026-07-30 16:00 | AAPL  | 0.8750 | 0.8050 | 0.8050 |   1.0000 | -0.0470 | -0.0800 |
| 2026-08-04 16:00 | AMD   | 0.9450 | 0.9675 | 0.9775 |   1.0000 |  0.0361 | -0.0614 |
| 2026-08-04 16:00 | SPCX  | 0.3700 | 0.3450 | 0.4500 |   1.0000 |  0.0603 | -0.1271 |
| 2026-08-26 16:00 | NVDA  | 0.9620 | 0.9605 | 0.9635 |   1.0000 | -0.0168 |  0.0737 |
| 2026-09-02 16:00 | AVGO  | 0.9615 | 0.9775 | 0.9045 |   1.0000 | -0.0089 | -0.0393 |
| 2026-09-10 16:00 | ORCL  | 0.7600 | 0.8000 | 0.8000 |   1.0000 | -0.0431 | -0.0261 |
| 2026-10-21 16:00 | TSLA  | 0.5250 | 0.6150 | 0.6200 |   1.0000 |  0.0236 | -0.0022 |
| 2026-10-21 16:00 | META  | 0.1820 | 0.1360 | 0.4210 |   0.0000 | -0.0058 | -0.0412 |
| 2026-10-28 16:00 | MSFT  | 0.8100 | 0.7550 | 0.7550 |   1.0000 | -0.0066 |  0.0125 |
| 2026-10-28 16:00 | GOOGL | 0.2350 | 0.2950 | 0.3250 |   0.0000 |  0.0074 | -0.1123 |
| 2026-10-29 16:00 | AMZN  | 0.6650 | 0.6700 | 0.2800 |   0.0000 | -0.0283 |  0.0206 |
| 2026-11-02 16:00 | AAPL  | 0.8750 | 0.8200 | 0.9450 |   1.0000 | -0.0047 | -0.0251 |
| 2026-11-03 16:00 | AMD   | 0.7600 | 0.6150 | 0.6150 |   1.0000 |  0.0304 |  0.0004 |
| 2026-11-17 16:00 | NVDA  | 0.8835 | 0.8460 | 0.8900 |   1.0000 |  0.0029 | -0.0328 |

</details>

## 6. Deviations from the pre-registration (found while checking data, before reading any test result)

- Earnings timing: the first run timed T at the 8-K acceptance. Minute odds showed the beat markets jumping to 0/1
  between 16:00 and the 8-K (press release goes out first; TSLA's 8-K lags by up to 40 min), so T-5min was partly
  post-release. After-close filings are now timed at 16:00 ET (T-5min = 15:55). This lowers measured accuracy.
- Kalshi 1-min candles only exist when a quote changes, so a 26h window missed standing quotes on quiet legs.
  Hourly points over T-10d were added and the staleness limit raised to 10 days; in exclusive buckets (FOMC) a leg with
  no quote at all in 10 days is set to 0 before renormalising.
- Polymarket legs now require `closed` (a 99.5c unresolved December-2026 Fed leg had slipped in).

## 7. Verdict (written after the final run, 2026-11-20)

**(a) Do the odds predict the announcement before it happens? Yes for FOMC and CPI; barely for earnings.**
- FOMC: Kalshi Brier 0.004-0.006 at T-1d/1h/5m vs 0.15 for "same as last meeting" (passes, Holm p = 0.02). Every
  meeting's favourite at T-1d was the actual decision (leg hit rate 100%); Polymarket is the same. The decision is
  known a day ahead, so there is nothing left for the announcement to reveal about the *decision* (statement, dots and
  press conference are not priced by these markets).
- CPI (headline MoM ladder): Brier 0.06 vs 0.24 persistence (passes, Holm p < 0.001), but the odds barely improve
  from T-1d to T-5min (0.061 -> 0.063): no late information arrives in the last day.
- Earnings beat (Polymarket, 46 reports 2025-10..2026-11): Brier 0.115 at T-5min vs 0.135 for the pooled beat rate;
  not significant (p = 0.51), first half worse than the naive rate. These markets are mostly a beat-rate prior.

**Late-move "leak" tests.** FOMC and CPI: no (Holm p 0.31 / 1.0). Earnings: formally passes (slope 1.8, Holm p =
0.03), but it is two events: AMZN 2026-10-29 (p fell 0.67 -> 0.28 between 15:00 and 15:55 ET, then missed) and
ORCL 2026-06-10 (0.23 -> 0.54, beat). Dropping those two: slope 1.46, p = 0.26. Treat it as two anecdotes worth
watching, not a signal.

**(b) Tradable information about the move? No.**
- Surprise -> reaction is there and has the expected sign (markets use the odds as the expectation): FOMC SPY
  -3 bp per bp of hawkish surprise over 30 min (passes, Holm p = 0.008), SHY and QQQ agree (secondary); CPI SPY
  -2.4% per pp of MoM surprise to 10:00 (p = 0.03, Holm 0.31), -3.6%/pp in the first 5 pre-market minutes
  (secondary, t = -6.5); earnings +5% excess per unit of beat surprise (p = 0.048, Holm 0.39). But the FOMC result is
  one meeting: without 2024-09-18 (the 50 bp cut, surprise -13 bp) the slope is 0.0 (p = 0.96). With odds at
  99% the day before, FOMC surprises are almost always ~0.
- None of this is tradable, because the surprise is only known after T. The pre-registered pre-announcement rules:
  FOMC 0 trades (odds never drifted >= 0.5 bp against SPY's own drift); CPI 11 trades, -42 bp mean net (t = -1.7);
  earnings 16 trades, -3.1% mean net excess (t = -2.0). All fail; signs are negative.
- Late odds moves -> returns (2b): none pass. The CPI secondary row (late E move vs open-anchored 09:30->10:00 SPY,
  t = -2.2) are exploratory among ~36 secondary regressions and would not survive correction.
- IPOs (n = 2, descriptive): ANT and SPCX buckets were informative (Brier 0.06-0.08 / 0.04-0.05 vs 0.25), winners
  priced 0.66-0.88 on average; nothing testable.

**Per type.** FOMC: accurate, untradable (no uncertainty left by T-1d). CPI: accurate vs naive, reaction follows the
surprise, no pre-release edge. Earnings: weak forecaster, reaction follows the surprise, rule loses. IPOs: too few.

**Power.** n = 26 FOMC / 44 CPI / 46 earnings / 2 IPOs. Fails are "no evidence", not proof of no effect; the FOMC pass
in test 3 and the earnings leak pass each hinge on one or two events.

## 8. What to log going forward (forward, out-of-sample)

- Every Polymarket earnings-beat market for the 12 names: p at T-1d, 15:00, 15:30, 15:55 and the press-release
  timestamp (wire time, not 8-K) -> re-run the leak test once n >= 100; flag any >= 20-point move in the final hour
  before the release (the AMZN 2026-10-29 pattern).
- Kalshi KXCPI / KXCPIYOY / core CPI ladders at 08:00, 08:25, plus SPY 08:30->08:35 and 09:30->10:00 -> track the
  CPI 2b exploratory row (late E move -> open-anchored return) as a fresh pre-registered test after 24 new releases.
- Kalshi KXFEDDECISION + Polymarket at T-1d/T-5min and SPY/SHY 14:00->14:30: only meetings with a live (5-95%)
  leg at T-1d carry information; expect few.
- New IPO-day markets (open/close/market-cap buckets) at T-1d 16:00 and 09:00 with first-trade time and price.
