# Kalshi combos: is buying NO (being the house) profitable?
Generated 2026-11-20 by `combo_study.py`. Pre-registered rule and sampling: see the script docstring.

## Inventory

1281 windows of 30s (3/day, 2025-09-15..2026-11-15); 113,841 combos created in them, 9,450 sampled settled combos with a fill (8 sampled were unsettled/never filled, dropped). Historical cutoff (GET /historical/cutoff): markets settled and trades before 2026-09-19 live under /historical/*; /historical/markets has no time filter, so pre-cutoff combos are found through /historical/trades windows.

| month | est. combos created / day | sampled | mean legs | median fill (contracts) | median fill $ (YES side) | median fill $ (NO side) | est. opening-fill NO-side $ / day | YES payout rate | NO ROI, maker fee | NO ROI, taker fee |
|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10 | 3,499 | 99 | 5.6 | 140 | 9.07 | 123 | 1.1M | 0.071 | +5.5% | +3.9% |
| 2025-11 | 11,712 | 231 | 5.4 | 112 | 9.27 | 98 | 4.0M | 0.087 | +4.2% | +2.6% |
| 2025-12 | 19,665 | 398 | 6.2 | 103 | 7.46 | 93 | 12.6M | 0.095 | +3.5% | +1.9% |
| 2026-01 | 40,258 | 596 | 7.2 | 104 | 5.79 | 95 | 22.6M | 0.092 | +3.0% | +1.5% |
| 2026-02 | 45,086 | 621 | 7.2 | 97 | 7.48 | 83 | 16.4M | 0.126 | +2.6% | +0.9% |
| 2026-03 | 63,825 | 790 | 6.9 | 103 | 9.00 | 87 | 26.5M | 0.150 | -0.4% | -2.0% |
| 2026-04 | 87,872 | 832 | 6.9 | 131 | 9.09 | 114 | 45.4M | 0.103 | +5.0% | +3.2% |
| 2026-05 | 117,120 | 916 | 6.9 | 162 | 8.85 | 145 | 75.2M | 0.100 | +1.4% | -0.1% |
| 2026-06 | 178,016 | 890 | 7.3 | 180 | 7.73 | 164 | 132.8M | 0.078 | +2.3% | +0.8% |
| 2026-07 | 204,387 | 928 | 7.8 | 212 | 6.21 | 188 | 148.0M | 0.069 | +3.3% | +1.8% |
| 2026-08 | 241,363 | 918 | 8.9 | 216 | 7.20 | 203 | 222.5M | 0.088 | +0.9% | -0.4% |
| 2026-09 | 739,680 | 888 | 9.8 | 195 | 6.36 | 170 | 730.2M | 0.096 | +1.2% | +0.0% |
| 2026-10 | 1,045,099 | 929 | 10.3 | 224 | 8.37 | 203 | 1,270.5M | 0.105 | -0.6% | -1.7% |
| 2026-11 | 1,580,992 | 414 | 10.4 | 169 | 9.06 | 148 | 2,452.4M | 0.153 | -5.7% | -6.7% |

Series: KXMVESPORTSMULTIGAMEEXTENDED 4685, KXMVECROSSCATEGORY 4190, KXMVENFLSINGLEGAME 248, KXMVENFLMULTIGAMEEXTENDED 127, KXMVENBASINGLEGAME 98, KXMVECROSSCATEGORY0 95, KXMVECBCHAMPIONSHIP 7

Category (all legs same category, else mixed): mixed 2461, NBA 1780, MLB 1649, NFL 1188, soccer 886, tennis 421, NCAAB 308, other 207, NCAAF 156, crypto 15m 127, NHL 94, MMA/boxing 71, WNBA 57, golf 33, crypto/fx other 12

Same-event legs (same game / same 15-min slot): 50%. Legs: median 6, max 129. First fill seconds after creation: median 21. Hours from fill to close: median 6.4. First fill taker side: YES 100%. Settlement values strictly between 0 and 1 (voided/fair-value legs): 32 of 9450.

## Calibration of the first-fill YES price

By price bucket:

| pb | n | days | mean YES price | mean YES payout | payout / price | mean NO return (no fee) |
|---|---|---|---|---|---|---|
| 0.00–0.01 | 1907 | 351 | 0.0043 | 0.0025 | 0.57 | +0.18% |
| 0.01–0.02 | 924 | 325 | 0.0140 | 0.0065 | 0.47 | +0.76% |
| 0.02–0.05 | 1677 | 374 | 0.0331 | 0.0270 | 0.81 | +0.63% |
| 0.05–0.10 | 1544 | 373 | 0.0726 | 0.0618 | 0.85 | +1.17% |
| 0.10–0.20 | 1487 | 369 | 0.1429 | 0.1251 | 0.88 | +2.11% |
| 0.20–0.35 | 1094 | 352 | 0.2627 | 0.2301 | 0.88 | +4.77% |
| 0.35–0.50 | 535 | 277 | 0.4144 | 0.3790 | 0.91 | +6.25% |
| 0.50–1.00 | 282 | 191 | 0.6071 | 0.5754 | 0.95 | +2.95% |

By number of legs:

| lb | n | days | mean YES price | mean YES payout | payout / price | mean NO return (no fee) |
|---|---|---|---|---|---|---|
| 2 | 647 | 298 | 0.2843 | 0.2556 | 0.90 | +4.91% |
| 3 | 1196 | 355 | 0.2063 | 0.1937 | 0.94 | +1.15% |
| 4–5 | 2347 | 383 | 0.1430 | 0.1287 | 0.90 | +2.16% |
| 6–8 | 2254 | 376 | 0.0879 | 0.0722 | 0.82 | +1.77% |
| 9–14 | 2007 | 364 | 0.0462 | 0.0372 | 0.80 | +1.12% |
| 15–+ | 996 | 300 | 0.0246 | 0.0178 | 0.72 | +0.62% |
| 1 | 3 | 3 | 0.0042 | 0.0000 | 0.00 | +0.42% |

By category:

| cat | n | days | mean YES price | mean YES payout | payout / price | mean NO return (no fee) |
|---|---|---|---|---|---|---|
| NFL | 1188 | 185 | 0.1000 | 0.0808 | 0.81 | +2.84% |
| NBA | 1780 | 226 | 0.1463 | 0.1288 | 0.88 | +2.61% |
| mixed | 2461 | 321 | 0.1053 | 0.0847 | 0.80 | +2.65% |
| NHL | 94 | 65 | 0.1341 | 0.1809 | 1.35 | -7.65% |
| NCAAB | 308 | 65 | 0.1638 | 0.1396 | 0.85 | +2.70% |
| MMA/boxing | 71 | 42 | 0.0632 | 0.0423 | 0.67 | +2.69% |
| soccer | 886 | 191 | 0.0618 | 0.0704 | 1.14 | -1.38% |
| tennis | 421 | 162 | 0.1245 | 0.1410 | 1.13 | -2.99% |
| other | 207 | 79 | 0.1138 | 0.0966 | 0.85 | +2.67% |
| MLB | 1649 | 195 | 0.1067 | 0.0879 | 0.82 | +2.52% |
| golf | 33 | 25 | 0.0711 | 0.0606 | 0.85 | +0.01% |
| crypto 15m | 127 | 67 | 0.2268 | 0.2362 | 1.04 | -5.99% |
| WNBA | 57 | 37 | 0.1334 | 0.1172 | 0.88 | +2.32% |
| crypto/fx other | 12 | 12 | 0.4223 | 0.2500 | 0.59 | +47.95% |
| NCAAF | 156 | 50 | 0.1625 | 0.1858 | 1.14 | -3.58% |

Same-event legs vs independent:

| same | n | days | mean YES price | mean YES payout | payout / price | mean NO return (no fee) |
|---|---|---|---|---|---|---|
| False | 4703 | 372 | 0.1124 | 0.1016 | 0.90 | +1.39% |
| True | 4747 | 392 | 0.1165 | 0.1004 | 0.86 | +2.09% |

## Parlay premium = first-fill YES price − product of leg mids at the same minute

Legs priced for 2,497 of 2,660 attempted combos (≤10 legs: every one created after 2026-09-19 plus a random 1500 earlier; a leg needs a two-sided 1-min quote within 60 min before the fill).

| slice | n | mean price | mean fair (product) | mean premium | median premium | premium / fair | mean payout | share premium ≥ 5pp |
|---|---|---|---|---|---|---|---|---|
| all | 2497 | 0.1355 | 0.1167 | +1.88pp | +0.57pp | +16.1% | 0.1289 | 10.5% |
| legs 2 | 233 | 0.2807 | 0.2625 | +1.82pp | +0.72pp | +6.9% | 0.2489 | 13.7% |
| legs 3 | 398 | 0.2139 | 0.1920 | +2.19pp | +0.80pp | +11.4% | 0.2194 | 15.1% |
| legs 4–5 | 740 | 0.1437 | 0.1235 | +2.02pp | +0.66pp | +16.3% | 0.1462 | 10.0% |
| legs 6–8 | 778 | 0.0828 | 0.0648 | +1.80pp | +0.50pp | +27.8% | 0.0723 | 9.8% |
| legs 9–14 | 348 | 0.0488 | 0.0343 | +1.45pp | +0.35pp | +42.3% | 0.0345 | 5.7% |
| same-event=False | 1343 | 0.1336 | 0.1238 | +0.97pp | +0.32pp | +7.9% | 0.1216 | 4.2% |
| same-event=True | 1154 | 0.1377 | 0.1083 | +2.94pp | +1.32pp | +27.1% | 0.1373 | 17.8% |
| MLB | 362 | 0.1213 | 0.1090 | +1.23pp | +0.34pp | +11.3% | 0.1050 | 6.4% |
| NBA | 328 | 0.1690 | 0.1331 | +3.59pp | +1.45pp | +27.0% | 0.1715 | 21.3% |
| NCAAB | 66 | 0.1536 | 0.1399 | +1.37pp | +0.73pp | +9.8% | 0.1818 | 6.1% |
| NCAAF | 89 | 0.2014 | 0.1848 | +1.66pp | +0.46pp | +9.0% | 0.2135 | 13.5% |
| NFL | 409 | 0.1097 | 0.0944 | +1.53pp | +0.74pp | +16.2% | 0.0856 | 9.0% |
| NHL | 34 | 0.1228 | 0.1099 | +1.29pp | +0.83pp | +11.7% | 0.1765 | 5.9% |
| crypto 15m | 70 | 0.2187 | 0.1506 | +6.80pp | +1.77pp | +45.1% | 0.2429 | 42.9% |
| mixed | 646 | 0.1421 | 0.1263 | +1.59pp | +0.46pp | +12.6% | 0.1204 | 8.5% |
| other | 90 | 0.1483 | 0.1289 | +1.95pp | +0.43pp | +15.1% | 0.1556 | 11.1% |
| soccer | 238 | 0.0792 | 0.0681 | +1.11pp | +0.36pp | +16.3% | 0.0983 | 3.4% |
| tennis | 116 | 0.1517 | 0.1433 | +0.84pp | +0.52pp | +5.9% | 0.1840 | 4.3% |

Does the product of legs forecast better than the combo price? (Brier, same combos)

combo price 0.0880, leg product 0.0898, YES payout rate 0.1289.

## Results

### Baseline: buy NO on every sampled combo at the first fill (= the RFQ maker's position)

| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |
|---|---|---|---|---|---|
| taker, fee ceil per contract (primary) | 9450 | 400 | +0.19% | [-0.70%, +1.00%] | 0.102 |
| taker, fee ceil per order | 9450 | 400 | +0.89% | [+0.00%, +1.71%] | 0.102 |
| maker (RFQ quoter) fee | 9450 | 400 | +1.64% | [+0.74%, +2.45%] | 0.102 |
| no fee | 9450 | 400 | +1.74% | [+0.84%, +2.56%] | 0.102 |
| maker fee, $-weighted by the fill's NO-side cost | 9450 | 400 | +0.76% | [+0.12%, +1.37%] | 0.102 |

### Pre-registered rule: premium ≥ 5pp → buy NO (n = 262)

| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |
|---|---|---|---|---|---|
| all | 262 | 155 | -6.06% | [-14.66%, +2.20%] | 0.321 |
| discovery first half | 91 | 62 | -10.66% | [-21.74%, +1.10%] | 0.286 |
| discovery second half | 92 | 58 | -1.75% | [-16.93%, +14.71%] | 0.315 |
| HOLDOUT last 30% (2026-10-07..) | 79 | 36 | -5.78% | [-25.84%, +11.91%] | 0.367 |

Same rule, other fee assumptions:

### rule, all

| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |
|---|---|---|---|---|---|
| taker, fee ceil per contract (primary) | 262 | 155 | -6.06% | [-14.66%, +2.20%] | 0.321 |
| taker, fee ceil per order | 262 | 155 | -5.92% | [-14.79%, +2.44%] | 0.321 |
| maker (RFQ quoter) fee | 262 | 155 | -4.11% | [-12.95%, +4.41%] | 0.321 |
| no fee | 262 | 155 | -3.53% | [-12.49%, +5.11%] | 0.321 |
| maker fee, $-weighted by the fill's NO-side cost | 262 | 155 | +11.60% | [-5.72%, +25.31%] | 0.321 |

### rule, holdout

| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |
|---|---|---|---|---|---|
| taker, fee ceil per contract (primary) | 79 | 36 | -5.78% | [-25.84%, +11.91%] | 0.367 |
| taker, fee ceil per order | 79 | 36 | -5.88% | [-26.02%, +11.54%] | 0.367 |
| maker (RFQ quoter) fee | 79 | 36 | -4.06% | [-24.54%, +14.02%] | 0.367 |
| no fee | 79 | 36 | -2.89% | [-23.69%, +15.51%] | 0.367 |
| maker fee, $-weighted by the fill's NO-side cost | 79 | 36 | +19.26% | [-13.72%, +46.73%] | 0.367 |

By legs / category / same-event (rule trades, primary fee):

| slice | n | days | mean ROI per $ | 95% CI (day-clustered) | YES hit rate |
|---|---|---|---|---|---|
| legs 2 | 32 | 28 | -10.66% | [-40.07%, +21.55%] | 0.469 |
| legs 3 | 60 | 55 | -14.48% | [-33.43%, +4.23%] | 0.400 |
| legs 4–5 | 74 | 63 | -8.96% | [-24.01%, +6.55%] | 0.351 |
| legs 6–8 | 76 | 64 | +0.40% | [-14.37%, +14.34%] | 0.211 |
| legs 9–14 | 20 | 18 | +12.75% | [-12.03%, +35.77%] | 0.150 |
| MLB | 23 | 18 | -9.35% | [-36.62%, +24.61%] | 0.348 |
| MMA/boxing | 1 | – | – | – | – |
| NBA | 70 | 50 | -17.76% | [-32.95%, -2.57%] | 0.357 |
| NCAAB | 4 | – | – | – | – |
| NCAAF | 12 | 9 | -10.69% | [-37.58%, +26.48%] | 0.333 |
| NFL | 37 | 30 | -8.75% | [-30.64%, +13.78%] | 0.270 |
| NHL | 2 | – | – | – | – |
| WNBA | 2 | – | – | – | – |
| crypto 15m | 30 | 25 | -12.88% | [-37.92%, +12.73%] | 0.400 |
| crypto/fx other | 3 | – | – | – | – |
| mixed | 55 | 48 | +16.64% | [-2.78%, +36.52%] | 0.236 |
| other | 10 | 10 | +29.21% | [-18.17%, +69.81%] | 0.200 |
| soccer | 8 | 7 | -17.43% | [-57.33%, +30.38%] | 0.375 |
| tennis | 5 | 5 | -43.81% | [-100.00%, +15.10%] | 0.600 |
| same-event=False | 57 | 50 | +3.65% | [-19.64%, +27.30%] | 0.351 |
| same-event=True | 205 | 133 | -8.76% | [-18.14%, +1.20%] | 0.312 |

**Pre-registered verdict: FAIL** (holdout CI > 0 and both discovery halves > 0).

## Tail risk (flat $1 stakes, chronological)

| book | n | total P&L $ | max drawdown $ | longest run of YES hits (NO losses) | worst day $ | largest single loss $ |
|---|---|---|---|---|---|---|
| all combos, primary fee | 9450 | +17.8 | -58.5 | 4 | -8.7 | -1.0 |
| rule, primary fee | 262 | -15.9 | -21.9 | 6 | -3.6 | -1.0 |
| rule, maker fee | 262 | -10.8 | -17.5 | 6 | -3.5 | -1.0 |

A NO stake at 0.99 makes +1% when the combo misses and −100% when it hits: about 1 hit per 100 such stakes erases the edge, so results hinge on a few hits.

## Capacity

First fill size: median 154 contracts, p90 1557; NO-side $ (size × (1−p)): median $136, p90 $1,529, total in sample $7,103,694. Rule trades: median NO $ 29.
Secondary trading after the opening fill: 17% of combos have any; secondary volume = 27% of opening-fill volume; share of secondary contracts where the taker bought YES (i.e. a resting NO-side order was hit): 77%. Secondary contracts traded ≥5h before close (a proxy for 'before the first leg starts'): 12.1% of opening volume.
Combo books show no standing quotes (yes bid 0 / ask 1) between trades: the only way to buy NO at the opening price is to be the RFQ quoter (maker, HVM 3 s confirm / 1 s execution timers, competing with ~5 combo makers answering in <300 ms).

