# Stock <-> Polymarket daily Up/Down: is there an exploitable minute-level lag?

## 0. Pre-registration (written 2026-11-20 before any lag statistic, gap or P&L was computed)

STUDY only; the stock model stays frozen (MATH.md "Change control"). Code: `lag_study.py` (`--selfcheck`, tests in
`test_lag_study.py`). Market list and 08:00-15:01 ET 1-minute CLOB histories are reused from `pm_close_study.py`'s
caches (`data/pm_close_daily_inv.pkl`, `data/pm_close_daily_hist.pkl`); this study only adds the 14:55-16:00 ET tail
(`data/lag_pm_tail.pkl`), Alpaca SIP 1-minute and daily bars (`data/lag_stocks.pkl`) and a trades sample
(`data/lag_trades.pkl`). Known beforehand from the resolution text: markets resolve **Up if the official close on
the date is above the official close of the previous trading day** (2456 of 2465 parse as "prev close"; the rest are
dropped). Instruments: TSLA NVDA AAPL MSFT GOOGL AMZN META SPCX (stock itself), SPX -> SPY, NDX and QQQ -> QQQ
(ETF proxies; adjustment=all so the prior close is dividend-adjusted like an index). NYSE half days dropped.

**Minute grid.** m = 1..390, t_m = 09:30 + m minutes ET. S_t = close of the last regular-hours bar that ENDS at or before
t (bars are stamped at their start). p_t = last CLOB prices-history point stamped at or before t, at most 5 minutes old,
else missing. PM prices are used only for m <= 389 (15:59); the stock at m = 390 is the 16:00 close of the bars.

**Fair value** (no fitted parameter): f_t = Phi( ln(S_t / R) / (sigma * sqrt(T/390)) ), R = previous regular close
(Alpaca daily bar), T = 390 - m minutes to close, sigma = std of the last 20 daily close-to-close log returns ending the
previous day (known before the open). gap_t = f_t - p_t.

**Calibration** (descriptive): at 10:00, 11:00, ..., 15:00, 15:30: decile table of f vs outcome, Brier of f vs Brier of
p, and the logistic calibration slope of y on logit(f) (1 = calibrated, > 1 = f too timid).

**Lag tests** (pooled and per instrument; Driscoll-Kraay SE by date, 5 lags; k = 1, 5, 15 minutes):
- a(k) PM lags stock: p_{t+k} - p_t on gap_t. Slope = share of the gap closed in k minutes.
- a'(k) bounce-robust version: p_{t+k} - p_t on f_t - p_{t-1} (an i.i.d. quote/print error in p_t is not on both sides).
- b1(k) PM leads stock: 1e4 * ln(S_{t+k}/S_t) on (p_t - p_{t-1}) - (f_t - f_{t-1}) in units of 10pp (PM moving away
  from fair in the last minute). Effect = bp per 10pp.
- b2(k): same target on p_t - f_t (10pp units) — PM sitting above fair predicts the stock up.
- c1: p_t - p_{t-1} on sum_{L=1..5}(f_{t-L} - f_{t-L-1}) (PM catches up to past fair moves).
- c2: 1e4 * ln(S_{t+1}/S_t) on p_t - p_{t-5} (10pp units) (stock catches up to past PM moves).
- Cross-correlation of 1-minute changes (Delta p vs Delta f and vs the stock 1-min return) at lags -15..+15:
  descriptive.
Rows require all inputs present; t + k <= 15:59 for PM targets and <= 16:00 for stock targets.

**Gaps** (descriptive): share of market-minutes with |gap| > 5pp / 10pp (all minutes and T >= 30); episode length
(consecutive minutes above threshold) mean / median / p90; AR(1) half-life of gap_t per minute = ln(0.5)/ln(phi).

**Paper rule (fixed).** Per market, at most ONE trade: the first minute t with T >= 30 and either
f_t - ask_t > 5pp (buy Up at the ask) or bid_t - f_t > 5pp (buy Down at 1 - bid_t), where ask/bid = p_t +/- c
(clipped to [0.01, 0.99]), c = 2c primary (1c and 3c sensitivity; c is the cost per side relative to the history
price, i.e. a full spread of 2c, conservative for a mid). **Execution at the next minute's price** (t+1, plus c); a
same-minute fill is reported as sensitivity only. Exit: the first later minute with |f - p| < 1pp, sold at the next
minute's bid (Up) / 1 - ask (Down); otherwise held to resolution (pays 1 or 0). P&L per $ = proceeds / entry price - 1.
No fees assumed (fee schedule for these markets unverified; noted). Inference: mean P&L per $ over trades, bootstrap
CI resampling DATES (all markets on a date share the same stock move), B = 2000; two-sided p = 2 min(P(<=0), P(>=0)).
Capacity: from the public trades endpoint (data-api v2) for a random sample of up to 200 traded markets: $ notional
traded within +/-5 min of entry and from entry to 16:00, and the share of minutes with any trade.

**Pass rule** (MATH.md): Holm across ALL tests above (a, a', b1, b2, c1, c2 pooled and per instrument, plus the paper
rule at 2c), Holm p < 0.05 AND same sign in both chronological halves (split by date). For "exploitable" the paper rule
must also pass. Nothing is tuned; thresholds fixed here.

**Priors written now.** a(k) will look strongly positive partly mechanically (noise in p_t shows up as
apparent gap-closing) — a' is the cleaner check, and only the paper rule after costs
answers "exploitable". The fair model ignores the intraday U-shaped vol and that sigma includes the overnight move,
so it is expected to be too timid early in the day; gaps from that are model error, not lag.

<!-- RESULTS BELOW ARE WRITTEN BY lag_study.py on 2026-11-20 -->

## 1. Coverage

2416 resolved markets with a full session, sigma and >= 30 CLOB points; 938,693 market-minutes with both a PM price and a stock price (of 939,824). `pm_moves_per_day` = median count of minutes in which the history price changed.

| inst   |   markets | first      | last       |   median_vol |   market_minutes |   pm_moves_per_day |
|:-------|----------:|:-----------|:-----------|-------------:|-----------------:|-------------------:|
| aapl   |       271 | 2025-10-16 | 2026-11-19 |       4099.5 |           105299 |              233.0 |
| amzn   |       272 | 2025-10-16 | 2026-11-19 |       3556.7 |           105690 |              211.5 |
| googl  |       272 | 2025-10-16 | 2026-11-19 |       3696.3 |           105689 |              211.5 |
| meta   |       272 | 2025-10-16 | 2026-11-19 |       4027.0 |           105689 |              209.5 |
| msft   |       272 | 2025-10-16 | 2026-11-19 |       3471.5 |           105689 |              210.0 |
| ndx    |       130 | 2025-10-16 | 2026-08-04 |       6404.7 |            50490 |              171.0 |
| nvda   |       271 | 2025-10-16 | 2026-11-19 |       5323.4 |           105300 |              217.0 |
| qqq    |        23 | 2026-03-25 | 2026-04-27 |       7455.5 |             8867 |              116.0 |
| spcx   |        90 | 2026-07-15 | 2026-11-19 |        540.5 |            34991 |              227.5 |
| spx    |       271 | 2025-10-16 | 2026-11-19 |      94541.3 |           105300 |              246.0 |
| tsla   |       272 | 2025-10-16 | 2026-11-19 |       4601.8 |           105689 |              209.0 |


## 2. Fair-value calibration

| time   |    n |   brier_fair |   brier_PM |   logit_slope_fair |   logit_slope_PM |   mean_abs_gap_pp |
|:-------|-----:|-------------:|-----------:|-------------------:|-----------------:|------------------:|
| 10:00  | 2416 |       0.1625 |     0.1573 |             1.3899 |           1.0802 |            7.2870 |
| 11:00  | 2416 |       0.1334 |     0.1238 |             1.6263 |           1.1292 |            8.0475 |
| 12:00  | 2406 |       0.1144 |     0.1060 |             1.8562 |           1.1546 |            8.4306 |
| 13:00  | 2416 |       0.0984 |     0.0889 |             1.9089 |           1.1783 |            8.2496 |
| 14:00  | 2416 |       0.0826 |     0.0754 |             1.8503 |           1.1692 |            7.7618 |
| 15:00  | 2416 |       0.0656 |     0.0624 |             1.5565 |           1.1392 |            6.4729 |
| 15:30  | 2416 |       0.0519 |     0.0544 |             1.4038 |           1.1006 |            5.5099 |


Pooled over the snapshots, by fair-value decile:

| f             |    n |   mean_fair |   mean_PM |   freq_up |
|:--------------|-----:|------------:|----------:|----------:|
| (-0.001, 0.1] | 3017 |       0.026 |     0.040 |     0.015 |
| (0.1, 0.2]    | 1247 |       0.149 |     0.090 |     0.067 |
| (0.2, 0.3]    | 1281 |       0.250 |     0.148 |     0.112 |
| (0.3, 0.4]    | 1301 |       0.352 |     0.254 |     0.207 |
| (0.4, 0.5]    | 1426 |       0.450 |     0.417 |     0.365 |
| (0.5, 0.6]    | 1453 |       0.550 |     0.606 |     0.594 |
| (0.6, 0.7]    | 1275 |       0.649 |     0.766 |     0.770 |
| (0.7, 0.8]    | 1255 |       0.750 |     0.861 |     0.876 |
| (0.8, 0.9]    | 1351 |       0.851 |     0.926 |     0.950 |
| (0.9, 1.0]    | 3296 |       0.973 |     0.968 |     0.992 |


## 3. Lag tests (Holm over all tests incl. per instrument and the paper rule)

**75 of 169 tests pass.** Pooled:

| Test                                                   | Inst   |      n |   effect |        t |      p |   Holm p |      h1 |      h2 | same sign halves   | Pass   |
|:-------------------------------------------------------|:-------|-------:|---------:|---------:|-------:|---------:|--------:|--------:|:-------------------|:-------|
| a PM lags: dp(t->t+1) on gap                           | POOLED | 936248 |   0.0521 |  12.7554 | 0.0000 |   0.0000 |  0.0583 |  0.0471 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | POOLED | 933803 |   0.0325 |  11.6052 | 0.0000 |   0.0000 |  0.0371 |  0.0286 | True               | True   |
| b1 PM leads: r(t->t+1) bp on (dp-df) per 10pp          | POOLED | 936248 |   0.0263 |   0.4251 | 0.6708 |   1.0000 |  0.1753 | -0.1312 | False              | False  |
| b2 PM leads: r(t->t+1) bp on (p-f) per 10pp            | POOLED | 938693 |   0.0139 |   1.5118 | 0.1306 |   1.0000 |  0.0309 | -0.0015 | False              | False  |
| a PM lags: dp(t->t+5) on gap                           | POOLED | 926508 |   0.0802 |  10.0014 | 0.0000 |   0.0000 |  0.1028 |  0.0613 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | POOLED | 924063 |   0.0565 |   9.1353 | 0.0000 |   0.0000 |  0.0774 |  0.0389 | True               | True   |
| b1 PM leads: r(t->t+5) bp on (dp-df) per 10pp          | POOLED | 926616 |   0.0004 |   0.0059 | 0.9953 |   1.0000 |  0.0776 | -0.0812 | False              | False  |
| b2 PM leads: r(t->t+5) bp on (p-f) per 10pp            | POOLED | 929061 |   0.0619 |   1.6056 | 0.1084 |   1.0000 |  0.0819 |  0.0412 | True               | False  |
| a PM lags: dp(t->t+15) on gap                          | POOLED | 902158 |   0.1063 |   7.6184 | 0.0000 |   0.0000 |  0.1512 |  0.0694 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | POOLED | 899713 |   0.0821 |   6.8798 | 0.0000 |   0.0000 |  0.1235 |  0.0476 | True               | True   |
| b1 PM leads: r(t->t+15) bp on (dp-df) per 10pp         | POOLED | 902536 |   0.0656 |   0.7764 | 0.4375 |   1.0000 |  0.0316 |  0.1021 | True               | False  |
| b2 PM leads: r(t->t+15) bp on (p-f) per 10pp           | POOLED | 904981 |   0.1711 |   1.6966 | 0.0898 |   1.0000 |  0.2548 |  0.0862 | True               | False  |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | POOLED | 924168 |   0.1973 |  44.0225 | 0.0000 |   0.0000 |  0.1839 |  0.2134 | True               | True   |
| c2 PM leads: r(t->t+1) bp on (p_t-p_(t-5)) per 10pp    | POOLED | 926508 |  -0.0129 |  -0.4283 | 0.6684 |   1.0000 | -0.0372 |  0.0116 | False              | False  |
| paper rule 2c next-minute: mean P&L per $              | POOLED |   2354 |   0.0570 | nan      | 0.0060 |   0.5460 |  0.1063 |  0.0050 | True               | False  |


a/a' effect = share of the gap closed over k minutes; b/c effect = stock bp per 10pp; c1 = slope of dp on summed past df.

Per instrument (only passing rows shown; full count above):

| Test                                                   | Inst   |      n |   effect |       t |      p |   Holm p |     h1 |     h2 | same sign halves   | Pass   |
|:-------------------------------------------------------|:-------|-------:|---------:|--------:|-------:|---------:|-------:|-------:|:-------------------|:-------|
| a PM lags: dp(t->t+1) on gap                           | aapl   | 105024 |   0.0782 |  7.7396 | 0.0000 |   0.0000 | 0.0965 | 0.0633 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | amzn   | 105415 |   0.0512 |  6.0921 | 0.0000 |   0.0000 | 0.0639 | 0.0427 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | googl  | 105414 |   0.0490 |  8.0026 | 0.0000 |   0.0000 | 0.0593 | 0.0399 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | meta   | 105414 |   0.0416 |  9.8193 | 0.0000 |   0.0000 | 0.0401 | 0.0435 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | msft   | 105414 |   0.0405 |  6.6612 | 0.0000 |   0.0000 | 0.0428 | 0.0384 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | ndx    |  50359 |   0.0738 |  6.2699 | 0.0000 |   0.0000 | 0.0772 | 0.0681 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | nvda   | 105026 |   0.0561 |  7.8269 | 0.0000 |   0.0000 | 0.0712 | 0.0463 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | spcx   |  34899 |   0.0797 |  6.5193 | 0.0000 |   0.0000 | 0.0668 | 0.1051 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | spx    | 105026 |   0.0437 |  5.9875 | 0.0000 |   0.0000 | 0.0728 | 0.0254 | True               | True   |
| a PM lags: dp(t->t+1) on gap                           | tsla   | 105414 |   0.0584 | 10.1771 | 0.0000 |   0.0000 | 0.0755 | 0.0487 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | aapl   | 104749 |   0.0506 |  7.8968 | 0.0000 |   0.0000 | 0.0611 | 0.0419 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | amzn   | 105140 |   0.0321 |  5.5980 | 0.0000 |   0.0000 | 0.0415 | 0.0257 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | googl  | 105139 |   0.0313 |  7.9246 | 0.0000 |   0.0000 | 0.0366 | 0.0268 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | meta   | 105139 |   0.0275 |  9.8093 | 0.0000 |   0.0000 | 0.0238 | 0.0319 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | msft   | 105139 |   0.0240 |  6.6093 | 0.0000 |   0.0000 | 0.0263 | 0.0216 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | ndx    |  50228 |   0.0420 |  6.9152 | 0.0000 |   0.0000 | 0.0350 | 0.0551 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | nvda   | 104752 |   0.0356 |  8.5624 | 0.0000 |   0.0000 | 0.0461 | 0.0287 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | spcx   |  34807 |   0.0284 |  5.7591 | 0.0000 |   0.0000 | 0.0232 | 0.0386 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | spx    | 104752 |   0.0367 |  6.3795 | 0.0000 |   0.0000 | 0.0544 | 0.0255 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+1) on f_t-p_(t-1)  | tsla   | 105139 |   0.0378 |  9.2643 | 0.0000 |   0.0000 | 0.0518 | 0.0296 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | aapl   | 103932 |   0.1136 |  7.0100 | 0.0000 |   0.0000 | 0.1595 | 0.0768 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | amzn   | 104319 |   0.0738 |  5.2549 | 0.0000 |   0.0000 | 0.1081 | 0.0507 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | googl  | 104318 |   0.0811 |  7.4265 | 0.0000 |   0.0000 | 0.1164 | 0.0489 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | meta   | 104318 |   0.0672 |  8.9192 | 0.0000 |   0.0000 | 0.0703 | 0.0638 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | msft   | 104318 |   0.0606 |  6.1074 | 0.0000 |   0.0000 | 0.0793 | 0.0408 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | ndx    |  49835 |   0.1354 |  7.3892 | 0.0000 |   0.0000 | 0.1500 | 0.1097 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | nvda   | 103934 |   0.0862 |  7.0405 | 0.0000 |   0.0000 | 0.1197 | 0.0644 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | spcx   |  34535 |   0.1192 |  6.6715 | 0.0000 |   0.0000 | 0.1017 | 0.1542 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | spx    | 103934 |   0.0585 |  4.8677 | 0.0000 |   0.0001 | 0.1109 | 0.0255 | True               | True   |
| a PM lags: dp(t->t+5) on gap                           | tsla   | 104318 |   0.0885 |  7.6567 | 0.0000 |   0.0000 | 0.1279 | 0.0662 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | aapl   | 103657 |   0.0805 |  6.8514 | 0.0000 |   0.0000 | 0.1160 | 0.0515 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | amzn   | 104044 |   0.0501 |  4.7291 | 0.0000 |   0.0002 | 0.0784 | 0.0308 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | googl  | 104043 |   0.0586 |  7.1227 | 0.0000 |   0.0000 | 0.0888 | 0.0306 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | meta   | 104043 |   0.0504 |  8.7794 | 0.0000 |   0.0000 | 0.0527 | 0.0479 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | msft   | 104043 |   0.0424 |  5.6366 | 0.0000 |   0.0000 | 0.0612 | 0.0223 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | ndx    |  49704 |   0.0951 |  7.2366 | 0.0000 |   0.0000 | 0.0980 | 0.0905 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | nvda   | 103660 |   0.0623 |  7.1224 | 0.0000 |   0.0000 | 0.0902 | 0.0438 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | spcx   |  34443 |   0.0589 |  5.5900 | 0.0000 |   0.0000 | 0.0523 | 0.0721 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | spx    | 103660 |   0.0500 |  4.8836 | 0.0000 |   0.0001 | 0.0901 | 0.0244 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+5) on f_t-p_(t-1)  | tsla   | 104043 |   0.0633 |  6.7496 | 0.0000 |   0.0000 | 0.1011 | 0.0413 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | aapl   | 101202 |   0.1531 |  6.0726 | 0.0000 |   0.0000 | 0.2238 | 0.0975 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | amzn   | 101579 |   0.0934 |  4.1557 | 0.0000 |   0.0031 | 0.1569 | 0.0519 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | googl  | 101578 |   0.1149 |  5.9808 | 0.0000 |   0.0000 | 0.1918 | 0.0443 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | meta   | 101578 |   0.0905 |  7.0957 | 0.0000 |   0.0000 | 0.1049 | 0.0739 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | msft   | 101578 |   0.0837 |  4.7204 | 0.0000 |   0.0002 | 0.1278 | 0.0379 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | ndx    |  48525 |   0.2008 |  6.0859 | 0.0000 |   0.0000 | 0.2430 | 0.1285 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | nvda   | 101204 |   0.1058 |  5.8238 | 0.0000 |   0.0000 | 0.1580 | 0.0724 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | spcx   |  33625 |   0.1696 |  6.4760 | 0.0000 |   0.0000 | 0.1547 | 0.2013 | True               | True   |
| a PM lags: dp(t->t+15) on gap                          | tsla   | 101578 |   0.1063 |  5.7031 | 0.0000 |   0.0000 | 0.1817 | 0.0638 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | aapl   | 100927 |   0.1190 |  5.7631 | 0.0000 |   0.0000 | 0.1750 | 0.0742 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | amzn   | 101304 |   0.0697 |  3.6872 | 0.0002 |   0.0215 | 0.1246 | 0.0335 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | googl  | 101303 |   0.0916 |  5.4897 | 0.0000 |   0.0000 | 0.1612 | 0.0270 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | meta   | 101303 |   0.0721 |  6.6290 | 0.0000 |   0.0000 | 0.0856 | 0.0567 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | msft   | 101303 |   0.0658 |  4.2180 | 0.0000 |   0.0024 | 0.1075 | 0.0220 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | ndx    |  48394 |   0.1565 |  5.4233 | 0.0000 |   0.0000 | 0.1863 | 0.1065 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | nvda   | 100930 |   0.0816 |  5.4262 | 0.0000 |   0.0000 | 0.1262 | 0.0527 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | spcx   |  33533 |   0.1074 |  5.2258 | 0.0000 |   0.0000 | 0.1014 | 0.1206 | True               | True   |
| a' PM lags (bounce-robust): dp(t->t+15) on f_t-p_(t-1) | tsla   | 101303 |   0.0806 |  4.7059 | 0.0000 |   0.0002 | 0.1550 | 0.0377 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | aapl   | 103669 |   0.1877 | 28.0762 | 0.0000 |   0.0000 | 0.1759 | 0.2043 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | amzn   | 104055 |   0.1926 | 32.4662 | 0.0000 |   0.0000 | 0.1818 | 0.2048 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | googl  | 104054 |   0.1842 | 20.2827 | 0.0000 |   0.0000 | 0.1584 | 0.2211 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | meta   | 104054 |   0.2130 | 19.9302 | 0.0000 |   0.0000 | 0.1904 | 0.2348 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | msft   | 104054 |   0.1898 | 20.6033 | 0.0000 |   0.0000 | 0.1770 | 0.2051 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | ndx    |  49709 |   0.1846 | 16.1881 | 0.0000 |   0.0000 | 0.1597 | 0.2078 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | nvda   | 103671 |   0.2058 | 37.5834 | 0.0000 |   0.0000 | 0.1996 | 0.2128 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | spcx   |  34449 |   0.1974 |  9.0366 | 0.0000 |   0.0000 | 0.1759 | 0.2201 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | spx    | 103671 |   0.2061 | 34.8969 | 0.0000 |   0.0000 | 0.2035 | 0.2095 | True               | True   |
| c1 PM lags: dp_t on sum df_(t-1..t-5)                  | tsla   | 104054 |   0.2157 | 42.8850 | 0.0000 |   0.0000 | 0.2114 | 0.2208 | True               | True   |


Per-instrument a'(5) slopes (descriptive):

| Inst   |      n |   effect |      t |   Holm p | Pass   |
|:-------|-------:|---------:|-------:|---------:|:-------|
| aapl   | 103657 |   0.0805 | 6.8514 |   0.0000 | True   |
| amzn   | 104044 |   0.0501 | 4.7291 |   0.0002 | True   |
| googl  | 104043 |   0.0586 | 7.1227 |   0.0000 | True   |
| meta   | 104043 |   0.0504 | 8.7794 |   0.0000 | True   |
| msft   | 104043 |   0.0424 | 5.6366 |   0.0000 | True   |
| ndx    |  49704 |   0.0951 | 7.2366 |   0.0000 | True   |
| nvda   | 103660 |   0.0623 | 7.1224 |   0.0000 | True   |
| qqq    |   8723 |   0.0211 | 2.2511 |   1.0000 | False  |
| spcx   |  34443 |   0.0589 | 5.5900 |   0.0000 | True   |
| spx    | 103660 |   0.0500 | 4.8836 |   0.0001 | True   |
| tsla   | 104043 |   0.0633 | 6.7496 |   0.0000 | True   |


Not run (n < 30): none

Cross-correlation of 1-minute changes (positive lag L: the stock/fair move happened L minutes BEFORE the PM move):

|      lag |   corr(dp_t, df_(t-L)) |           n |   corr(dp_t, r_(t-L)) |
|---------:|-----------------------:|------------:|----------------------:|
| -15.0000 |                 0.0027 | 902536.0000 |                0.0007 |
| -14.0000 |                -0.0008 | 904944.0000 |               -0.0005 |
| -13.0000 |                 0.0019 | 907352.0000 |                0.0006 |
| -12.0000 |                 0.0016 | 909760.0000 |                0.0011 |
| -11.0000 |                -0.0027 | 912168.0000 |                0.0001 |
| -10.0000 |                 0.0028 | 914576.0000 |                0.0001 |
|  -9.0000 |                 0.0011 | 916984.0000 |                0.0017 |
|  -8.0000 |                 0.0031 | 919392.0000 |                0.0009 |
|  -7.0000 |                 0.0005 | 921800.0000 |               -0.0011 |
|  -6.0000 |                 0.0033 | 924208.0000 |                0.0037 |
|  -5.0000 |                -0.0015 | 926616.0000 |               -0.0003 |
|  -4.0000 |                 0.0035 | 929024.0000 |               -0.0003 |
|  -3.0000 |                 0.0073 | 931432.0000 |                0.0013 |
|  -2.0000 |                 0.0004 | 933840.0000 |               -0.0010 |
|  -1.0000 |                -0.0011 | 936248.0000 |               -0.0018 |
|   0.0000 |                 0.0104 | 936248.0000 |                0.0079 |
|   1.0000 |                 0.4405 | 933832.0000 |                0.3237 |
|   2.0000 |                 0.0722 | 931416.0000 |                0.0504 |
|   3.0000 |                 0.0150 | 929000.0000 |                0.0116 |
|   4.0000 |                 0.0022 | 926584.0000 |                0.0039 |
|   5.0000 |                 0.0075 | 924168.0000 |                0.0065 |
|   6.0000 |                 0.0079 | 921752.0000 |                0.0037 |
|   7.0000 |                -0.0000 | 919336.0000 |                0.0042 |
|   8.0000 |                 0.0008 | 916920.0000 |                0.0012 |
|   9.0000 |                 0.0005 | 914504.0000 |                0.0020 |
|  10.0000 |                 0.0034 | 912088.0000 |                0.0019 |
|  11.0000 |                 0.0054 | 909672.0000 |                0.0032 |
|  12.0000 |                 0.0010 | 907256.0000 |                0.0023 |
|  13.0000 |                 0.0008 | 904840.0000 |                0.0021 |
|  14.0000 |                -0.0014 | 902424.0000 |               -0.0017 |
|  15.0000 |                 0.0029 | 900008.0000 |                0.0018 |


## 4. Gaps |fair - PM|

| sample      |   threshold_pp |   share_of_minutes |   markets_with_episode |   episodes |   mean_len |   median_len |   p90_len |
|:------------|---------------:|-------------------:|-----------------------:|-----------:|-----------:|-------------:|----------:|
| all minutes |         5.0000 |             0.5326 |                 0.9859 |      46020 |    10.8636 |       2.0000 |   16.0000 |
| all minutes |        10.0000 |             0.3060 |                 0.9483 |      36640 |     7.8404 |       2.0000 |   12.0000 |
| T >= 30     |         5.0000 |             0.5543 |                 0.9859 |      43607 |    11.0426 |       2.0000 |   17.0000 |
| T >= 30     |        10.0000 |             0.3183 |                 0.9474 |      34623 |     7.9869 |       2.0000 |   12.0000 |


AR(1) per minute:

| sample      |      n |    phi |   half_life_min |
|:------------|-------:|-------:|----------------:|
| all minutes | 936248 | 0.9449 |         12.2190 |
| T >= 30     | 868760 | 0.9504 |         13.6282 |


## 5. Paper rule (one trade per market; |fair - ask/bid| > 5pp, T >= 30; exit at |gap| < 1pp or resolution)

|   cost_c | fill                     |    n |   dates |   up_side |    hit |   mean_pnl_per_usd |   ci_lo |   ci_hi |      p |     h1 |      h2 |   exited_early |   median_entry |   median_hold_min |
|---------:|:-------------------------|-----:|--------:|----------:|-------:|-------------------:|--------:|--------:|-------:|-------:|--------:|---------------:|---------------:|------------------:|
|   1.0000 | next minute              | 2368 |     272 |    0.4383 | 0.5312 |             0.1179 |  0.0728 |  0.1639 | 0.0000 | 0.1706 |  0.0624 |         0.9882 |         0.4250 |           12.0000 |
|   1.0000 | same minute (optimistic) | 2368 |     272 |    0.4383 | 0.7230 |             0.3044 |  0.2566 |  0.3530 | 0.0000 | 0.3251 |  0.2825 |         0.9899 |         0.3650 |           11.0000 |
|   2.0000 | next minute              | 2354 |     272 |    0.4397 | 0.4868 |             0.0570 |  0.0152 |  0.0999 | 0.0060 | 0.1063 |  0.0050 |         0.9881 |         0.4250 |           13.0000 |
|   2.0000 | same minute (optimistic) | 2354 |     272 |    0.4397 | 0.6899 |             0.2368 |  0.1915 |  0.2844 | 0.0000 | 0.2554 |  0.2173 |         0.9898 |         0.3600 |           12.0000 |
|   3.0000 | next minute              | 2336 |     272 |    0.4354 | 0.4418 |             0.0031 | -0.0388 |  0.0471 | 0.9010 | 0.0568 | -0.0535 |         0.9884 |         0.4300 |           14.0000 |
|   3.0000 | same minute (optimistic) | 2336 |     272 |    0.4354 | 0.6605 |             0.1838 |  0.1400 |  0.2300 | 0.0000 | 0.2046 |  0.1618 |         0.9902 |         0.3650 |           13.0000 |


By instrument (2c, next-minute fill):

| inst   |   n |    hit |   mean_pnl |   median_vol |
|:-------|----:|-------:|-----------:|-------------:|
| aapl   | 267 | 0.5393 |     0.1299 |    4099.5234 |
| amzn   | 263 | 0.4639 |    -0.0033 |    3559.3225 |
| googl  | 267 | 0.4944 |     0.0592 |    3649.1341 |
| meta   | 262 | 0.5229 |     0.0828 |    4113.1715 |
| msft   | 269 | 0.4461 |    -0.0306 |    3415.0777 |
| ndx    | 125 | 0.4880 |     0.1993 |    6378.8402 |
| nvda   | 266 | 0.4398 |     0.0187 |    5205.5883 |
| qqq    |  22 | 0.5455 |     0.2084 |    6709.8116 |
| spcx   |  90 | 0.6556 |     0.2330 |     540.4701 |
| spx    | 257 | 0.4475 |    -0.0394 |   90806.3001 |
| tsla   | 266 | 0.4774 |     0.0965 |    4601.8500 |


Capacity, trades sample (public trades endpoint, USD notional = size x price, both outcomes):

| index              |   count |    25% |     50% |     75% |    mean |
|:-------------------|--------:|-------:|--------:|--------:|--------:|
| usd_pm5min         |  200.00 |   4.44 |   44.16 |  165.01 |  217.98 |
| usd_entry_to_close |  200.00 | 837.43 | 2104.11 | 6622.47 | 8547.01 |
| usd_session        |  200.00 | 865.21 | 2151.31 | 6643.95 | 8769.25 |
| median_trade_usd   |  199.00 |   4.80 |    7.13 |   10.00 |    8.52 |
| minutes_with_trade |  200.00 |   0.06 |    0.10 |    0.16 |    0.15 |


## 6. Interpretation and verdict (hand-written after the 2026-11-20 run; a rerun of lag_study.py drops this section)

- **Direction.** Polymarket follows the stock; the stock does not follow Polymarket. Every "PM leads" test (b1, b2,
  c2) is null pooled and per instrument; the cross-correlation is ~0 at all negative lags. "PM lags" tests (a, a', c1)
  pass everywhere (Holm), but the economic size is small: a' closes ~3% / 6% / 8% of the gap in 1 / 5 / 15 minutes.
- **The 1-minute lag is mostly a timestamp artifact.** CLOB prices-history points are stamped at second 0-20 of the
  minute (median second 11), so the point used at t is ~50 s older than the stock price at t. The cross-correlation
  peak at L = +1 (0.44) with a small tail at L = 2 (0.07) and L = 3 (0.015) means PM reprices within ~1-2 minutes;
  only the L >= 2 part is a real (small) lag.
- **Gaps are mostly fair-model error, not lag.** The fair value is too timid (logit slope 1.4-1.9; sigma is
  close-to-close and includes the overnight move, intraday vol is U-shaped) and PM has the lower Brier at every
  snapshot except 15:30. So |gap| > 5pp on ~53% of minutes and the 12-14 minute AR(1) half-life measure disagreement
  with a crude model, not a stale market. PM is the better-calibrated forecaster here.
- **Paper rule fails the pre-registered bar.** 2c next-minute: +5.7% per $ (CI 1.5%-10%), raw p = 0.006, Holm p =
  0.55; halves +10.6% then +0.5% (decaying). 3c: +0.3% (CI -3.9%..+4.7%). The same-minute fills (+18-30%) are the
  timestamp artifact above and are not achievable. 99% of trades exit on the 1pp rule after ~13 minutes, so the P&L
  depends entirely on the assumed bid/ask, which we do not observe.
- **Capacity is negligible.** Trades sample (200 traded markets): median $44 traded within +/-5 min of entry, median
  trade $7, median session notional $2.1k, a trade in only ~10% of minutes. SPX is the only liquid series (median
  lifetime volume ~$95k) and it has a negative rule P&L (-3.9%).
- **Verdict: no exploitable lag in either direction** on this data. Not tradable at size; the only positive cell
  rests on an unobserved spread and fails Holm.

**Data limits.** prices-history is a book-derived displayed price (it moves in ~210 minutes/day while trades occur in
~40), not an executable quote and not last trade; true spreads are unknown. Thin books are easy to push
(manipulation / one-off quotes). SPX/NDX use SPY/QQQ as proxies. No fees assumed (schedule for these markets
unverified). US access: international Polymarket restricts US persons; whether these markets list on the CFTC-
regulated Polymarket US exchange was not checked.

**To confirm live:** order-book snapshots (best bid/ask + depth to $500) for every open Up/Down market every 5-10
seconds, with exchange timestamps, alongside SIP quotes (not 1-minute bars) for the underlying; then rerun section 5
with real touch prices and fill only what the book shows. A rule that does not survive real asks over ~3 months
(> 2,000 signals) should be dropped.
