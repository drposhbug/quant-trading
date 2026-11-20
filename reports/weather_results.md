# Weather forecasts vs Kalshi daily-high markets

Generated 2026-11-20 06:25 by [weather_study.py](../weather_study.py). Paper study only: no orders, no accounts.

## Pre-registration (written before the first run; not changed after)

A development run on a partial cache (166 NY events, 2026) was used only to debug the code; no test, threshold,
time or model setting was changed after it (only report formatting, and a descriptive model-calibration table was added).

Question: do official NWS model forecasts (and their updates) predict Kalshi daily high-temperature outcomes better than the
market price, after Kalshi fees, so a US retail trader could bet them?

- **Sample**: KXHIGH{NY,CHI,MIA,AUS,LAX,DEN,PHIL} (+ legacy HIGH* tickers), event dates 2023-01-01 → 2026-11-19, every bracket.
  Chronological holdout = last 30% of event dates (from 2025-09-19).
- **Prices**: hourly Kalshi candles; state at time t = last candle that *closed* at or before t (quotes carried forward).
  Price = bid/ask mid when the spread ≤ 10¢, else last trade.
- **Times** (local to the city): T1 = 15:00 the day before (Kalshi opens these markets ~10:00 ET the day before, so 10:00
  local would precede the open for western cities), T2 = 08:00 on the day, T3 = 12:00 on the day.
- **Forecast**: latest NBM text (NBS) run available at t (run + 2h), else latest GFS MOS (run + 4h); daytime max row.
  Probability model: high = forecast + e, e drawn from that city's and slot's errors (CLI high − forecast) on days
  D−365…D−2 only (no lookahead), Gaussian-kernel smoothed (h = 1.0°F), ≥ 60 past errors required.
- **Tests** (13, Holm-corrected together; a PASS also needs the same sign and p < 0.05 on the holdout alone;
  standard errors clustered by event date):
  1. Calibration at T1/T2/T3: mean(outcome − price) for cheap brackets (price < 0.15) and rich ones (≥ 0.5) — 6 tests.
  2. Brier(model) − Brier(market) per bracket at T1/T2/T3, same brackets (events with every bracket priced) — 3 tests; pass needs < 0.
  3. Update lag: each new NBS/GFS-MOS run (available time A) that moves the forecast high for an open market by ≥ 2°F.
     Market-implied mean high E(t) from renormalised bracket prices. Move toward the new forecast sign(ΔF)·(E(A+h) − E(A)),
     h = 1, 2, 3 h — 3 tests; pass needs > 0. A−3h → A reported for context (has the market already moved?).
  4. Betting rule at T2 (08:00 local, event day): buy every bracket with model prob − ask ≥ 8pp, 100 contracts,
     pay the ask (no ask quote → last trade + 2¢) plus the Kalshi taker fee ceil(0.07·C·P·(1−P)) to the cent, hold to
     settlement. 1 test on per-bet ROI; table reports ROI = Σpnl/Σcost with a day-bootstrap 95% CI (B = 2000).

## Data coverage

| city | station | events | brackets | with candles | first | last | contracts traded |
|---|---|---|---|---|---|---|---|
| AUS | KAUS | 1284 | 7701 | 7701 | 2023-05-11 | 2026-11-18 | 80,970,042 |
| CHI | KMDW | 1417 | 8501 | 8501 | 2023-01-01 | 2026-11-18 | 110,962,265 |
| DEN | KDEN | 729 | 4374 | 4374 | 2024-11-20 | 2026-11-18 | 53,803,676 |
| LAX | KLAX | 683 | 4098 | 4098 | 2025-01-05 | 2026-11-18 | 188,900,809 |
| MIA | KMIA | 1287 | 7718 | 7718 | 2023-05-11 | 2026-11-18 | 107,984,407 |
| NY | KNYC | 1416 | 8493 | 8493 | 2023-01-01 | 2026-11-18 | 151,015,849 |
| PHIL | KPHL | 729 | 4374 | 4374 | 2024-11-20 | 2026-11-18 | 44,569,251 |

Contracts traded per year (all 7 cities): 2023: 5,631,708, 2024: 81,671,968, 2025: 212,955,356, 2026: 437,947,267.

Settlement check (IEM archive of the NWS CLI vs the bracket Kalshi settled YES). From late 2025/2026 Kalshi's rules name
The Weather Company (still the CLI station, e.g. CLINYC/CLIMDW) instead of the NWS report:

| city | settlement source | events | CLI high inside the YES bracket |
|---|---|---|---|
| AUS | NWS | 1187 | 100.0% |
| AUS | TWC | 97 | 100.0% |
| CHI | NWS | 1320 | 100.0% |
| CHI | TWC | 97 | 100.0% |
| DEN | NWS | 632 | 100.0% |
| DEN | TWC | 97 | 100.0% |
| LAX | NWS | 584 | 100.0% |
| LAX | TWC | 97 | 100.0% |
| MIA | NWS | 1182 | 99.9% |
| MIA | TWC | 97 | 99.0% |
| NY | NWS | 1318 | 100.0% |
| NY | TWC | 96 | 100.0% |
| PHIL | NWS | 632 | 100.0% |
| PHIL | TWC | 97 | 100.0% |

Forecast skill (all days 2022-03 → 2026-11, the error history the model draws on):

| slot | days | model used (NBS share) | mean error (obs − fcst) | MAE | SD |
|---|---|---|---|---|---|
| T1 D-1 15:00 | 12061 | 100% | +0.20 | 1.93 | 2.72 |
| T2 D 08:00 | 12061 | 100% | +0.15 | 1.78 | 2.54 |
| T3 D 12:00 | 12061 | 100% | +0.14 | 1.77 | 2.53 |

## Test 1: Kalshi calibration

**T1 D-1 15:00** (n = 42132 brackets, 7459 events; Brier 0.1172)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 17686 | 0.039 | 0.028 | [0.025, 0.030] |
| 0.1–0.2 | 7477 | 0.145 | 0.132 | [0.124, 0.140] |
| 0.2–0.3 | 6754 | 0.249 | 0.242 | [0.232, 0.252] |
| 0.3–0.4 | 5931 | 0.343 | 0.342 | [0.330, 0.354] |
| 0.4–0.5 | 2806 | 0.441 | 0.451 | [0.432, 0.469] |
| 0.5–0.6 | 1026 | 0.537 | 0.566 | [0.536, 0.596] |
| 0.6–0.7 | 301 | 0.640 | 0.621 | [0.565, 0.674] |
| 0.7–0.8 | 89 | 0.742 | 0.719 | [0.618, 0.802] |
| 0.8–0.9 | 42 | 0.841 | 0.762 | [0.615, 0.865] |
| 0.9–1.0 | 20 | 0.947 | 0.500 | [0.299, 0.701] |

**T2 D 08:00** (n = 43855 brackets, 7535 events; Brier 0.1026)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 21790 | 0.029 | 0.020 | [0.018, 0.022] |
| 0.1–0.2 | 5852 | 0.144 | 0.120 | [0.112, 0.129] |
| 0.2–0.3 | 4543 | 0.247 | 0.223 | [0.212, 0.236] |
| 0.3–0.4 | 4403 | 0.347 | 0.339 | [0.325, 0.353] |
| 0.4–0.5 | 3633 | 0.444 | 0.430 | [0.414, 0.446] |
| 0.5–0.6 | 2175 | 0.542 | 0.544 | [0.523, 0.565] |
| 0.6–0.7 | 832 | 0.638 | 0.649 | [0.616, 0.681] |
| 0.7–0.8 | 258 | 0.738 | 0.733 | [0.675, 0.783] |
| 0.8–0.9 | 133 | 0.844 | 0.865 | [0.796, 0.913] |
| 0.9–1.0 | 236 | 0.962 | 0.928 | [0.888, 0.955] |

**T3 D 12:00** (n = 44831 brackets, 7545 events; Brier 0.0881)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 26487 | 0.020 | 0.015 | [0.014, 0.017] |
| 0.1–0.2 | 4186 | 0.143 | 0.140 | [0.130, 0.151] |
| 0.2–0.3 | 3012 | 0.244 | 0.238 | [0.223, 0.254] |
| 0.3–0.4 | 2767 | 0.345 | 0.353 | [0.335, 0.371] |
| 0.4–0.5 | 2527 | 0.446 | 0.438 | [0.419, 0.458] |
| 0.5–0.6 | 2331 | 0.544 | 0.522 | [0.501, 0.542] |
| 0.6–0.7 | 1532 | 0.643 | 0.612 | [0.587, 0.636] |
| 0.7–0.8 | 826 | 0.739 | 0.676 | [0.643, 0.707] |
| 0.8–0.9 | 472 | 0.843 | 0.801 | [0.762, 0.834] |
| 0.9–1.0 | 691 | 0.966 | 0.906 | [0.882, 0.926] |

## Test 2: model vs market

| slot | city | brackets | events | Brier market | Brier model | log loss market (event) | log loss model (event) |
|---|---|---|---|---|---|---|---|
| T1 D-1 15:00 | all | 42132 | 7459 | 0.1172 | 0.1251 | 1.296 | 1.443 |
| T1 D-1 15:00 | AUS | 7035 | 1267 | 0.1214 | 0.1255 | 1.357 | 1.444 |
| T1 D-1 15:00 | CHI | 7769 | 1401 | 0.1219 | 0.1334 | 1.331 | 1.526 |
| T1 D-1 15:00 | DEN | 4307 | 727 | 0.1172 | 0.1228 | 1.384 | 1.518 |
| T1 D-1 15:00 | LAX | 4059 | 681 | 0.1064 | 0.1188 | 1.204 | 1.463 |
| T1 D-1 15:00 | MIA | 7112 | 1267 | 0.1066 | 0.1099 | 1.129 | 1.168 |
| T1 D-1 15:00 | NY | 7581 | 1392 | 0.1238 | 0.1339 | 1.312 | 1.490 |
| T1 D-1 15:00 | PHIL | 4269 | 724 | 0.1180 | 0.1269 | 1.386 | 1.575 |
| T2 D 08:00 | all | 43855 | 7535 | 0.1026 | 0.1198 | 1.128 | 1.402 |
| T2 D 08:00 | AUS | 7406 | 1283 | 0.1074 | 0.1221 | 1.191 | 1.420 |
| T2 D 08:00 | CHI | 8307 | 1417 | 0.0988 | 0.1234 | 1.090 | 1.456 |
| T2 D 08:00 | DEN | 4374 | 729 | 0.1012 | 0.1208 | 1.171 | 1.492 |
| T2 D 08:00 | LAX | 4096 | 683 | 0.0955 | 0.1175 | 1.066 | 1.433 |
| T2 D 08:00 | MIA | 7335 | 1283 | 0.1010 | 0.1048 | 1.072 | 1.130 |
| T2 D 08:00 | NY | 7995 | 1411 | 0.1073 | 0.1265 | 1.137 | 1.452 |
| T2 D 08:00 | PHIL | 4342 | 729 | 0.1037 | 0.1232 | 1.182 | 1.515 |
| T3 D 12:00 | all | 44831 | 7545 | 0.0881 | 0.1180 | 0.934 | 1.407 |
| T3 D 12:00 | AUS | 7551 | 1284 | 0.0997 | 0.1202 | 1.090 | 1.428 |
| T3 D 12:00 | CHI | 8437 | 1417 | 0.0871 | 0.1215 | 0.926 | 1.453 |
| T3 D 12:00 | DEN | 4374 | 729 | 0.0881 | 0.1208 | 0.970 | 1.492 |
| T3 D 12:00 | LAX | 4098 | 683 | 0.0632 | 0.1174 | 0.658 | 1.433 |
| T3 D 12:00 | MIA | 7634 | 1287 | 0.0883 | 0.1022 | 0.891 | 1.139 |
| T3 D 12:00 | NY | 8363 | 1416 | 0.0912 | 0.1232 | 0.946 | 1.471 |
| T3 D 12:00 | PHIL | 4374 | 729 | 0.0873 | 0.1223 | 0.948 | 1.513 |

Model's own calibration at T2 D 08:00 (all brackets with a model probability):

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 18217 | 0.042 | 0.036 | [0.034, 0.039] |
| 0.1–0.2 | 9370 | 0.147 | 0.115 | [0.109, 0.122] |
| 0.2–0.3 | 9704 | 0.253 | 0.269 | [0.260, 0.278] |
| 0.3–0.4 | 5684 | 0.324 | 0.345 | [0.333, 0.358] |
| 0.4–0.5 | 1626 | 0.439 | 0.492 | [0.468, 0.516] |
| 0.5–0.6 | 131 | 0.540 | 0.435 | [0.353, 0.521] |
| 0.6–0.7 | 158 | 0.642 | 0.576 | [0.498, 0.650] |
| 0.7–0.8 | 83 | 0.757 | 0.663 | [0.556, 0.755] |
| 0.8–0.9 | 48 | 0.848 | 0.458 | [0.326, 0.597] |
| 0.9–1.0 | 238 | 0.991 | 0.878 | [0.830, 0.914] |

## Test 3: does the market lag model updates?

4503 qualifying updates (|ΔF| ≥ 2°F; mean |ΔF| = 2.39°F).

| window | updates | mean move toward new forecast (°F) | t | share of |ΔF| |
|---|---|---|---|---|
| A−3h → A (before availability) | 4503 | +0.048 | +5.38 | 2.0% |
| A → A+1h | 4503 | +0.022 | +3.85 | 0.9% |
| A → A+2h | 4503 | +0.041 | +5.83 | 1.7% |
| A → A+3h | 4503 | +0.080 | +8.20 | 3.3% |

## Test 4: fixed betting rule

| slice | bets | days | hit rate | mean price paid | ROI after fees [95% day-bootstrap CI] | median contracts traded ±2h |
|---|---|---|---|---|---|---|
| all | 6667 | 1268 | 8.4% | 0.092 | -13.2% [-21.1%, -5.7%] | 1,376 |
| first half | 1775 | 634 | 17.2% | 0.139 | +18.5% [+4.5%, +30.4%] | 318 |
| second half | 4892 | 634 | 5.2% | 0.075 | -34.2% [-41.8%, -26.0%] | 1,796 |
| development (first 70%) | 2870 | 842 | 13.0% | 0.119 | +4.2% [-6.8%, +14.7%] | 544 |
| holdout (last 30%) | 3797 | 426 | 5.0% | 0.072 | -34.7% [-43.8%, -25.8%] | 2,316 |
| priced at ask | 6525 | 1237 | 8.2% | 0.090 | -14.0% [-22.1%, -6.3%] | 1,441 |
| no ask: last + 2¢ | 142 | 123 | 20.4% | 0.185 | +4.7% [-28.7%, +41.5%] | 32 |
| city AUS | 1092 | 766 | 9.2% | 0.095 | -9.2% [-23.8%, +5.0%] | 1,050 |
| city CHI | 1517 | 970 | 7.5% | 0.090 | -20.6% [-33.1%, -9.2%] | 1,000 |
| city DEN | 845 | 539 | 7.3% | 0.077 | -10.4% [-28.8%, +9.5%] | 1,197 |
| city LAX | 835 | 522 | 7.3% | 0.084 | -17.5% [-33.8%, -0.4%] | 6,207 |
| city MIA | 532 | 458 | 17.5% | 0.162 | +2.4% [-14.3%, +19.1%] | 1,928 |
| city NY | 1077 | 714 | 5.9% | 0.083 | -32.0% [-45.6%, -17.5%] | 2,060 |
| city PHIL | 769 | 485 | 8.8% | 0.080 | +4.0% [-15.8%, +24.0%] | 826 |
| year 2023 | 578 | 290 | 10.4% | 0.117 | -15.5% [-36.5%, +5.9%] | 58 |
| year 2024 | 728 | 292 | 11.4% | 0.120 | -10.1% [-26.1%, +7.1%] | 410 |
| year 2025 | 2376 | 364 | 10.9% | 0.102 | +2.2% [-12.3%, +15.4%] | 1,216 |
| year 2026 | 2985 | 322 | 5.3% | 0.073 | -30.7% [-41.4%, -20.1%] | 2,503 |
| model prob − price ≥ 15pp | 2823 | 981 | 11.5% | 0.098 | +11.0% [-2.3%, +23.3%] | 1,736 |

## Exploratory (not pre-registered, not in the Holm family)

Sell the overpriced cheap brackets from test 1: at T2 D 08:00, every bracket with price < 0.15 and a YES bid > 0.5¢,
buy NO at 1 − YES bid (100 contracts, taker fee), hold to settlement.

| slice | bets | days | NO hit rate | mean NO price | ROI after fees [95% CI] | median contracts ±2h |
|---|---|---|---|---|---|---|
| all | 11557 | 1311 | 95.6% | 0.955 | -0.1% [-0.5%, +0.2%] | 1,332 |
| holdout (last 30%) | 6441 | 426 | 95.8% | 0.953 | +0.2% [-0.3%, +0.7%] | 2,266 |
| year 2026 | 4958 | 322 | 95.7% | 0.953 | +0.1% [-0.4%, +0.7%] | 2,556 |

## All tests

| # | test | mean | t | p | Holm p | n clusters (days) | holdout mean | holdout p | pass |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 calib T1 D-1 15:00 cheap p<0.15: mean(y − price) | -0.0125 | -7.61 | 0.0000 | 0.0000 | 1405 | -0.0122 | 0.0000 | **PASS** |
| 2 | 1 calib T1 D-1 15:00 rich p>=0.5: mean(y − price) | +0.0095 | +0.65 | 0.5134 | 0.8805 | 879 | +0.0649 | 0.0036 | fail |
| 3 | 1 calib T2 D 08:00 cheap p<0.15: mean(y − price) | -0.0123 | -9.98 | 0.0000 | 0.0000 | 1417 | -0.0090 | 0.0000 | **PASS** |
| 4 | 1 calib T2 D 08:00 rich p>=0.5: mean(y − price) | -0.0071 | -0.77 | 0.4403 | 0.8805 | 1286 | +0.0346 | 0.0074 | fail |
| 5 | 1 calib T3 D 12:00 cheap p<0.15: mean(y − price) | -0.0041 | -4.26 | 0.0000 | 0.0001 | 1417 | -0.0080 | 0.0000 | **PASS** |
| 6 | 1 calib T3 D 12:00 rich p>=0.5: mean(y − price) | -0.0436 | -6.25 | 0.0000 | 0.0000 | 1401 | +0.0029 | 0.7485 | fail |
| 7 | 2 Brier(model) − Brier(market) T1 D-1 15:00 | +0.0073 | +10.30 | 0.0000 | 0.0000 | 1409 | +0.0154 | 0.0000 | fail |
| 8 | 2 Brier(model) − Brier(market) T2 D 08:00 | +0.0157 | +19.24 | 0.0000 | 0.0000 | 1417 | +0.0281 | 0.0000 | fail |
| 9 | 2 Brier(model) − Brier(market) T3 D 12:00 | +0.0276 | +26.78 | 0.0000 | 0.0000 | 1417 | +0.0435 | 0.0000 | fail |
| 10 | 3 lag: market moves toward new run, A → A+1h | +0.0225 | +3.85 | 0.0001 | 0.0004 | 1102 | +0.0192 | 0.0092 | **PASS** |
| 11 | 3 lag: market moves toward new run, A → A+2h | +0.0410 | +5.83 | 0.0000 | 0.0000 | 1102 | +0.0535 | 0.0000 | **PASS** |
| 12 | 3 lag: market moves toward new run, A → A+3h | +0.0795 | +8.20 | 0.0000 | 0.0000 | 1102 | +0.0765 | 0.0000 | **PASS** |
| 13 | 4 bet rule ROI per bet (pnl/cost) | -0.3377 | -6.55 | 0.0000 | 0.0000 | 1268 | -0.5123 | 0.0000 | fail |

**6 of 13 tests pass.**

## Verdict

- **Calibration**: Kalshi temperature brackets are well calibrated. Cheap brackets (< 15¢) resolve YES about 1pp less
  often than priced (tests 1/3/5 pass), a mild longshot bias; selling them at the bid after fees earns ≈ 0 (exploratory table).
- **Forecast model vs market**: the market beats the NWS MOS/NBM-text model at every time and in every city (tests 7–9:
  model Brier worse, holdout too). The model is calibrated but less sharp; the market has hourly NBM/HRRR runs, observations
  and the morning's temperatures that the 4-cycle public archive does not.
- **Update lag**: after a ≥ 2°F change in a new run, the market's implied high drifts toward it by ~0.02–0.08°F over 1–3 h
  (statistically real, tests 10–12 pass), but that is only 1–3% of the forecast change, and it moved as much before the run
  was (conservatively) available. Too small to pay a 1–2¢ spread plus fees on a 2°F bracket.
- **Betting rule**: model − ask ≥ 8pp at 08:00 loses -13.2% after fees overall and -34.7% on the holdout; it was
  positive in the first half of bet days (thinner books) but sharply negative in the second half and in 2026, as volume grew.
- **Verdict: no tradable edge** for a retail trader from public NWS model guidance. Nothing to forward paper-log.
