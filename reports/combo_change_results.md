# Kalshi combos: why did 'be the house' flip in Oct–Nov 2026? And a leg-correlation model
Generated 2026-11-20 by `combo_change_study.py` from the `combo_study.py` sample (9,450 settled combos, first fill = RFQ fill). Method and pre-registration: script docstring.

## A1. Month-by-month decomposition of NO ROI (buy NO at first fill)

Stable model (fit on 6,301 combos before 2026-08-01): logit E[y] = -0.024 +1.015·logit p -0.060·same-event -0.109·ln legs. No-fee ROI = pricing (p − ŷ)/(1−p) + luck (ŷ − y)/(1−p); maker ROI = no-fee + fee. Premium vs legs = p − product of leg mids (priced subset only).

| month | n | mean p | ŷ (stable) | realised y | NO ROI maker | = pricing | + luck | + fee | luck p (y~Bern ŷ, indep.) | y vs p: p (indep.) | n priced | p − leg product (mean / median) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10 | 99 | 0.096 | 0.080 | 0.071 | +5.5% | +2.1% | +3.4% | +0.00% | 0.829 | 0.935 | 16 | +2.34 / +1.23pp |
| 2025-11 | 231 | 0.120 | 0.100 | 0.087 | +4.2% | +2.6% | +1.6% | +0.00% | 0.726 | 0.929 | 49 | +2.80 / +1.80pp |
| 2025-12 | 398 | 0.113 | 0.093 | 0.095 | +3.5% | +2.6% | +1.0% | +0.00% | 0.683 | 0.957 | 74 | +2.04 / +0.83pp |
| 2026-01 | 596 | 0.112 | 0.093 | 0.092 | +3.0% | +2.6% | +0.4% | +0.00% | 0.612 | 0.965 | 102 | +2.93 / +1.29pp |
| 2026-02 | 621 | 0.146 | 0.123 | 0.126 | +2.6% | +3.1% | -0.5% | +0.00% | 0.384 | 0.920 | 100 | +3.37 / +1.58pp |
| 2026-03 | 790 | 0.154 | 0.131 | 0.150 | -0.4% | +3.2% | -3.6% | +0.00% | 0.025 | 0.415 | 146 | +2.91 / +1.36pp |
| 2026-04 | 832 | 0.132 | 0.113 | 0.103 | +5.0% | +2.7% | +2.2% | +0.00% | 0.914 | 0.999 | 146 | +2.07 / +0.97pp |
| 2026-05 | 916 | 0.114 | 0.096 | 0.100 | +1.4% | +2.4% | -1.0% | +0.00% | 0.213 | 0.851 | 166 | +0.86 / +0.27pp |
| 2026-06 | 890 | 0.096 | 0.080 | 0.078 | +2.3% | +2.0% | +0.3% | +0.00% | 0.584 | 0.958 | 179 | +1.53 / +0.43pp |
| 2026-07 | 928 | 0.091 | 0.076 | 0.069 | +3.3% | +2.0% | +1.4% | +0.00% | 0.869 | 0.995 | 177 | +1.53 / +0.55pp |
| 2026-08 | 918 | 0.099 | 0.084 | 0.088 | +0.9% | +2.1% | -1.1% | -0.15% | 0.224 | 0.794 | 148 | +1.30 / +0.31pp |
| 2026-09 | 888 | 0.106 | 0.090 | 0.096 | +1.2% | +2.3% | -0.7% | -0.38% | 0.317 | 0.851 | 332 | +1.92 / +0.48pp |
| 2026-10 | 929 | 0.109 | 0.093 | 0.105 | -0.6% | +2.3% | -2.6% | -0.36% | 0.038 | 0.468 | 608 | +1.75 / +0.42pp |
| 2026-11 | 414 | 0.119 | 0.101 | 0.153 | -5.7% | +2.6% | -7.9% | -0.35% | 0.000 | 0.012 | 254 | +1.69 / +0.44pp |

'luck p' = one-sided probability of luck at least this bad if outcomes were independent Bernoulli(ŷ); 'y vs p' = same for no-fee ROI if outcomes were Bernoulli(price) (price fair, no house edge). Combos on the same day share games, so these independent-draw p-values are too small; the day-clustered tests below are the ones that count.

## A1(iii). Mix

Cells = category × legs bucket × same-event (114 cells). Early = 2025-10..2026-07 (n=6301), late = 2026-10..2026-11 (n=1343). Late cells absent early carry 10% of late combos.

| quantity (NO ROI, maker fee) | value |
|---|---|
| early actual | +2.63% |
| late actual | -2.17% |
| late within-cell ROI at EARLY mix (fixed weights) | -4.05% |
| early within-cell ROI at LATE mix | +2.23% |
| change explained by mix (late actual − late@early mix) | +1.88pp |
| change within cells (late@early mix − early actual) | -6.68pp |
| pricing component: early / late / late@early mix | +2.53% / +2.42% / +2.99% |
| luck component: early / late / late@early mix | +0.10% / -4.24% / -6.64% |

**Category** (share of sampled combos by month)

| month | NFL | NCAAF | NBA | MLB | NCAAB | soccer | tennis | crypto 15m | mixed | other |
|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10 | 100% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 2025-11 | 81% | 0% | 17% | 0% | 0% | 0% | 0% | 0% | 2% | 0% |
| 2025-12 | 68% | 0% | 27% | 0% | 0% | 0% | 0% | 0% | 5% | 0% |
| 2026-01 | 38% | 0% | 45% | 0% | 4% | 0% | 0% | 0% | 10% | 3% |
| 2026-02 | 5% | 0% | 39% | 0% | 24% | 7% | 2% | 0% | 20% | 3% |
| 2026-03 | 0% | 0% | 45% | 4% | 17% | 5% | 2% | 0% | 23% | 3% |
| 2026-04 | 0% | 0% | 34% | 27% | 0% | 4% | 3% | 0% | 28% | 4% |
| 2026-05 | 0% | 0% | 28% | 33% | 0% | 6% | 8% | 0% | 22% | 2% |
| 2026-06 | 0% | 0% | 11% | 30% | 0% | 27% | 5% | 0% | 25% | 2% |
| 2026-07 | 0% | 0% | 0% | 37% | 0% | 19% | 12% | 1% | 27% | 4% |
| 2026-08 | 0% | 0% | 0% | 31% | 0% | 7% | 6% | 2% | 39% | 14% |
| 2026-09 | 16% | 6% | 0% | 19% | 0% | 9% | 3% | 3% | 36% | 8% |
| 2026-10 | 17% | 8% | 7% | 3% | 0% | 11% | 5% | 5% | 37% | 8% |
| 2026-11 | 15% | 6% | 16% | 0% | 1% | 9% | 2% | 5% | 37% | 9% |

**Legs bucket** (share of sampled combos by month)

| month | 2 | 3 | 4–5 | 6–8 | 9–14 | 15–+ |
|---|---|---|---|---|---|---|
| 2025-10 | 9% | 18% | 31% | 26% | 12% | 3% |
| 2025-11 | 9% | 23% | 35% | 18% | 13% | 3% |
| 2025-12 | 8% | 13% | 33% | 26% | 19% | 2% |
| 2026-01 | 6% | 14% | 27% | 29% | 18% | 7% |
| 2026-02 | 9% | 15% | 25% | 25% | 17% | 9% |
| 2026-03 | 8% | 15% | 29% | 23% | 17% | 8% |
| 2026-04 | 9% | 15% | 29% | 21% | 19% | 8% |
| 2026-05 | 7% | 14% | 27% | 25% | 22% | 6% |
| 2026-06 | 6% | 13% | 26% | 25% | 22% | 8% |
| 2026-07 | 5% | 11% | 25% | 27% | 24% | 8% |
| 2026-08 | 6% | 9% | 21% | 22% | 27% | 15% |
| 2026-09 | 7% | 9% | 20% | 23% | 24% | 17% |
| 2026-10 | 7% | 11% | 19% | 22% | 22% | 19% |
| 2026-11 | 6% | 9% | 17% | 21% | 27% | 21% |

**First-fill YES price bucket** (share of sampled combos by month)

| month | 0.00–0.01 | 0.01–0.02 | 0.02–0.05 | 0.05–0.10 | 0.10–0.20 | 0.20–0.35 | 0.35–0.50 | 0.50–1.00 |
|---|---|---|---|---|---|---|---|---|
| 2025-10 | 12% | 11% | 28% | 17% | 17% | 9% | 3% | 2% |
| 2025-11 | 10% | 9% | 20% | 22% | 21% | 13% | 3% | 3% |
| 2025-12 | 12% | 11% | 19% | 20% | 17% | 14% | 4% | 2% |
| 2026-01 | 14% | 11% | 17% | 18% | 20% | 12% | 5% | 2% |
| 2026-02 | 11% | 6% | 16% | 14% | 22% | 20% | 8% | 2% |
| 2026-03 | 10% | 6% | 18% | 17% | 20% | 15% | 10% | 4% |
| 2026-04 | 14% | 9% | 18% | 16% | 19% | 13% | 7% | 3% |
| 2026-05 | 17% | 11% | 18% | 18% | 15% | 12% | 6% | 3% |
| 2026-06 | 22% | 10% | 20% | 18% | 14% | 9% | 4% | 2% |
| 2026-07 | 24% | 12% | 21% | 16% | 11% | 10% | 3% | 2% |
| 2026-08 | 29% | 11% | 16% | 14% | 13% | 9% | 5% | 3% |
| 2026-09 | 29% | 11% | 16% | 14% | 11% | 10% | 5% | 4% |
| 2026-10 | 29% | 9% | 16% | 14% | 14% | 9% | 6% | 3% |
| 2026-11 | 24% | 8% | 18% | 16% | 14% | 11% | 4% | 5% |

**Same-event** (share of sampled combos by month)

| month | independent | same-event |
|---|---|---|
| 2025-10 | 29% | 71% |
| 2025-11 | 31% | 69% |
| 2025-12 | 22% | 78% |
| 2026-01 | 23% | 77% |
| 2026-02 | 54% | 46% |
| 2026-03 | 53% | 47% |
| 2026-04 | 49% | 51% |
| 2026-05 | 48% | 52% |
| 2026-06 | 48% | 52% |
| 2026-07 | 51% | 49% |
| 2026-08 | 68% | 32% |
| 2026-09 | 62% | 38% |
| 2026-10 | 56% | 44% |
| 2026-11 | 48% | 52% |

**Series** (share of sampled combos by month)

| month | CROSSCATEGORY | NFL/NBA single | SPORTSMULTIGAMEEXT |
|---|---|---|---|
| 2025-10 | 0% | 100% | 0% |
| 2025-11 | 0% | 61% | 39% |
| 2025-12 | 0% | 25% | 75% |
| 2026-01 | 0% | 22% | 78% |
| 2026-02 | 2% | 0% | 98% |
| 2026-03 | 59% | 1% | 41% |
| 2026-04 | 43% | 0% | 57% |
| 2026-05 | 32% | 0% | 68% |
| 2026-06 | 19% | 0% | 81% |
| 2026-07 | 16% | 0% | 84% |
| 2026-08 | 67% | 0% | 33% |
| 2026-09 | 100% | 0% | 0% |
| 2026-10 | 100% | 0% | 0% |
| 2026-11 | 100% | 0% | 0% |

**Late (Oct–Nov) NO ROI (maker) by category vs early**

| category | early n | early ROI | late n | late ROI | late YES rate | late ŷ | late luck |
|---|---|---|---|---|---|---|---|
| NFL | 816 | +2.8% | 224 | +0.5% | 0.112 | 0.099 | -1.7% |
| NCAAF | 0 | +nan% | 95 | -2.5% | 0.158 | 0.129 | -4.8% |
| NBA | 1650 | +3.2% | 130 | -5.0% | 0.154 | 0.105 | -7.5% |
| MLB | 1168 | +2.5% | 26 | -1.1% | 0.077 | 0.078 | -2.9% |
| NCAAB | 303 | +3.7% | 5 | -57.8% | 0.600 | 0.278 | -64.4% |
| soccer | 601 | +0.6% | 141 | -7.1% | 0.121 | 0.060 | -8.6% |
| tennis | 280 | -2.5% | 54 | -5.9% | 0.154 | 0.114 | -8.0% |
| crypto 15m | 17 | +1.4% | 68 | -4.8% | 0.206 | 0.170 | -8.6% |
| mixed | 1294 | +4.0% | 493 | +0.2% | 0.089 | 0.080 | -1.5% |
| other | 172 | +1.2% | 107 | -2.8% | 0.121 | 0.100 | -4.7% |

Nov 2026 worst days (NO ROI, maker): 2026-11-03 n=31.0 hits 10 vs ŷ 3.7 ROI -27%; 2026-11-09 n=29.0 hits 7 vs ŷ 4.5 ROI -16%; 2026-11-02 n=30.0 hits 7 vs ŷ 2.8 ROI -16%; 2026-11-04 n=29.0 hits 6 vs ŷ 2.9 ROI -14%. Nov ex those 4 days: -0.45%.

## A2. Competition signals

| month | median s creation→fill | p90 s | median fill contracts | p90 contracts | share split fill (>1 trade in 2 s) | sd of p − leg product (pp) | IQR (pp) | median p / leg product |
|---|---|---|---|---|---|---|---|---|
| 2025-10 | 22 | 53 | 140 | 898 | 1.0% | 3.12 | 1.59 | 1.544 |
| 2025-11 | 24 | 57 | 112 | 898 | 0.9% | 3.40 | 3.27 | 1.291 |
| 2025-12 | 24 | 56 | 103 | 1297 | 2.8% | 3.89 | 2.13 | 1.288 |
| 2026-01 | 23 | 52 | 104 | 1150 | 10.6% | 6.13 | 3.96 | 1.317 |
| 2026-02 | 21 | 50 | 97 | 833 | 6.1% | 6.42 | 3.06 | 1.187 |
| 2026-03 | 21 | 52 | 103 | 978 | 1.9% | 5.28 | 2.43 | 1.210 |
| 2026-04 | 17 | 52 | 131 | 1331 | 1.3% | 4.54 | 2.67 | 1.141 |
| 2026-05 | 19 | 51 | 162 | 1376 | 3.1% | 2.17 | 0.91 | 1.101 |
| 2026-06 | 19 | 50 | 180 | 1672 | 0.8% | 4.02 | 1.42 | 1.162 |
| 2026-07 | 19 | 51 | 212 | 1744 | 0.4% | 4.20 | 1.39 | 1.180 |
| 2026-08 | 19 | 49 | 216 | 2273 | 0.3% | 3.98 | 1.14 | 1.093 |
| 2026-09 | 24 | 2603 | 195 | 2000 | 0.1% | 4.31 | 1.58 | 1.127 |
| 2026-10 | 31 | 25202 | 224 | 2605 | 0.6% | 4.94 | 1.47 | 1.079 |
| 2026-11 | 31 | 3191 | 169 | 2469 | 1.2% | 4.59 | 1.38 | 1.065 |

First fill > 120 s after creation (combo market reused / re-requested later), share and NO ROI maker fast vs slow: 2026-09 17% (+1.2% / +1.2%); 2026-10 27% (-0.4% / -1.3%); 2026-11 22% (-5.9% / -4.7%).

Public trade prints carry no account or quoter ids, so the number of distinct counterparties is not inferable from this data. 'creation→fill' includes the requester's own confirm time, so it bounds rather than measures quoter speed.

## A1/A2 tests (day-clustered bootstrap, two-sided, Holm over these 6)

| test | estimate [95% CI] | p | Holm p |
|---|---|---|---|
| 2026-10 luck ≠ 0 (y vs stable ŷ) | -2.61% [-5.40, +0.03] | 0.0535 | 0.1605 |
| 2026-11 luck ≠ 0 (y vs stable ŷ) | -7.89% [-13.19, -3.04] | 0.0003 | 0.0015 |
| late − early pricing component | -0.11% [-0.30, +0.08] | 0.2715 | 0.2715 |
| late − early premium p − leg product | -0.33pp [-0.75, +0.10] | 0.1240 | 0.2480 |
| late − early NO ROI maker | -4.80% [-7.53, -2.13] | 0.0003 | 0.0015 |
| late − early luck component | -4.33% [-7.13, -1.57] | 0.0020 | 0.0080 |

## B. Leg-correlation model (pre-registered; train < 2026-08-01, test 2026-08-01..11-15)

Training same-event leg pairs with both results known: 41,371 (deduplicated) across 708 type-pair keys; leg results fetched for 49,278 leg markets. Fitted k = 0.55 (train log-loss 0.2797 vs 0.2818 at k=0). Priced combos: train 1155, test 1342.

Most common pair keys (training): 

| pair (typeA, typeB, team relation) | n | P(A) | P(B) | P(A&B) | shrunk lift |
|---|---|---|---|---|---|
| KXNBAPTS:yes / KXNBAREB:yes / same | 2338.0 | 0.684 | 0.774 | 0.540 | 1.02 |
| KXNBAPTS:yes / KXNBAPTS:yes / opp | 2093.0 | 0.667 | 0.673 | 0.460 | 1.02 |
| KXNBAPTS:yes / KXNBAREB:yes / opp | 1767.0 | 0.692 | 0.784 | 0.550 | 1.01 |
| KXNBAPTS:yes / KXNBAPTS:yes / same | 1728.0 | 0.653 | 0.679 | 0.453 | 1.02 |
| KXNBAAST:yes / KXNBAPTS:yes / same | 1454.0 | 0.753 | 0.713 | 0.552 | 1.03 |
| KXNBA3PT:yes / KXNBAPTS:yes / same | 1448.0 | 0.701 | 0.691 | 0.523 | 1.08 |
| KXNBA3PT:yes / KXNBAPTS:yes / opp | 1053.0 | 0.718 | 0.692 | 0.495 | 1.00 |
| KXNBAAST:yes / KXNBAPTS:yes / opp | 1047.0 | 0.749 | 0.677 | 0.516 | 1.02 |
| KXNBAAST:yes / KXNBAREB:yes / same | 1020.0 | 0.762 | 0.803 | 0.626 | 1.03 |
| KXNBA3PT:yes / KXNBAREB:yes / same | 847.0 | 0.750 | 0.782 | 0.593 | 1.01 |
| KXNBAAST:yes / KXNBAREB:yes / opp | 734.0 | 0.759 | 0.817 | 0.617 | 1.00 |
| KXNBA3PT:yes / KXNBAREB:yes / opp | 668.0 | 0.765 | 0.832 | 0.636 | 1.00 |
| KXNBAREB:yes / KXNBAREB:yes / opp | 668.0 | 0.787 | 0.798 | 0.641 | 1.02 |
| KXNBA3PT:yes / KXNBAAST:yes / same | 630.0 | 0.737 | 0.748 | 0.571 | 1.04 |
| KXNBAGAME:yes / KXNBAPTS:yes / same | 593.0 | 0.642 | 0.698 | 0.489 | 1.09 |

**Test-period forecast scores** (lower is better; Δ vs combo price with day-clustered 95% CI)

| subset | n | Brier price | Brier leg product | Brier model | Δ Brier model − price | log-loss price | log-loss product | log-loss model | Δ log-loss model − price |
|---|---|---|---|---|---|---|---|---|---|
| all test | 1342 | 0.0943 | 0.0952 | 0.0969 | +0.0026 [-0.0005, +0.0058] | 0.3059 | 0.3088 | 0.3228 | +0.0170 [+0.0026, +0.0349] |
| same-event | 565 | 0.0996 | 0.1039 | 0.1078 | +0.0082 [+0.0015, +0.0151] | 0.3164 | 0.3276 | 0.3611 | +0.0447 [+0.0109, +0.0858] |
| independent | 777 | 0.0904 | 0.0889 | 0.0889 | -0.0014 [-0.0037, +0.0007] | 0.2982 | 0.2950 | 0.2950 | -0.0032 [-0.0086, +0.0020] |
| 2026-08 | 148 | 0.0876 | 0.0882 | 0.0876 | -0.0000 [-0.0041, +0.0058] | 0.2751 | 0.2739 | 0.2734 | -0.0017 [-0.0101, +0.0111] |
| 2026-09 | 332 | 0.0890 | 0.0900 | 0.0904 | +0.0014 [-0.0037, +0.0057] | 0.2974 | 0.2989 | 0.3015 | +0.0041 [-0.0084, +0.0151] |
| 2026-10 | 608 | 0.0852 | 0.0856 | 0.0898 | +0.0047 [-0.0010, +0.0104] | 0.2747 | 0.2770 | 0.3092 | +0.0345 [+0.0043, +0.0706] |
| 2026-11 | 254 | 0.1267 | 0.1292 | 0.1274 | +0.0007 [-0.0052, +0.0071] | 0.4094 | 0.4180 | 0.4121 | +0.0026 [-0.0133, +0.0193] |

**Rule: buy NO when p − model ≥ 4pp** (test period, maker fee)

| slice | n | days | mean ROI per $ [95% CI, day-clustered] | YES hit rate |
|---|---|---|---|---|
| TEST all (maker fee) | 111 | 58 | +2.38% [-13.50, +18.54] | 0.315 |
| TEST all (taker fee) | 111 | 58 | +0.49% [-15.04, +16.28] | 0.315 |
| TEST all (no fee) | 111 | 58 | +3.57% [-12.57, +20.05] | 0.315 |
| TEST 2026-08 | 10 | 7 | +10.27% [-38.96, +52.80] | 0.200 |
| TEST 2026-09 | 34 | 16 | +0.04% [-24.42, +29.53] | 0.353 |
| TEST 2026-10 | 45 | 23 | +6.14% [-18.92, +30.40] | 0.311 |
| TEST 2026-11 | 22 | 12 | -5.26% [-46.93, +29.16] | 0.318 |
| TEST MLB | 9 | 7 | -11.73% [-49.99, +25.26] | 0.333 |
| TEST NBA | 10 | 8 | -34.34% [-72.50, +14.05] | 0.500 |
| TEST NCAAB | 1 | – | – | – |
| TEST NCAAF | 13 | 10 | -5.82% [-32.20, +28.58] | 0.308 |
| TEST NFL | 8 | 8 | -3.25% [-44.23, +35.45] | 0.250 |
| TEST crypto 15m | 14 | 13 | -28.13% [-63.95, +6.95] | 0.500 |
| TEST mixed | 30 | 25 | +40.87% [+16.01, +67.19] | 0.133 |
| TEST other | 18 | 16 | +1.18% [-42.61, +45.44] | 0.389 |
| TEST soccer | 3 | – | – | – |
| TEST tennis | 5 | 5 | -17.22% [-74.43, +38.35] | 0.400 |
| TEST same-event=False | 39 | 31 | +23.51% [-4.67, +51.06] | 0.256 |
| TEST same-event=True | 72 | 47 | -9.06% [-26.43, +10.81] | 0.347 |
| train (in-sample context only) | 135 | 94 | +1.61% [-8.62, +12.66] | 0.237 |
| TEST benchmark: NO on every priced combo | 1342 | 106 | -0.96% [-3.60, +1.61] | 0.145 |

**Rule: buy YES when model − p ≥ 4pp** (test period; as RFQ requester you would be the taker, so the taker row is the realistic one)

| slice | n | days | mean ROI per $ [95% CI, day-clustered] | YES hit rate |
|---|---|---|---|---|
| TEST all (maker fee) | 60 | 37 | -19.55% [-68.01, +36.56] | 0.217 |
| TEST all (taker fee) | 60 | 37 | -23.01% [-69.39, +30.13] | 0.217 |
| TEST 2026-08 | 4 | – | – | – |
| TEST 2026-09 | 7 | 6 | -100.00% [-100.00, -100.00] | 0.000 |
| TEST 2026-10 | 35 | 18 | -21.53% [-74.35, +41.47] | 0.229 |
| TEST 2026-11 | 14 | 9 | +48.60% [-100.00, +212.07] | 0.357 |
| TEST MLB | 5 | 5 | -100.00% [-100.00, -100.00] | 0.000 |
| TEST NBA | 1 | – | – | – |
| TEST NCAAF | 1 | – | – | – |
| TEST NFL | 18 | 12 | +4.14% [-100.00, +108.70] | 0.278 |
| TEST crypto 15m | 27 | 20 | -23.76% [-81.81, +53.91] | 0.222 |
| TEST mixed | 4 | – | – | – |
| TEST other | 3 | – | – | – |
| TEST tennis | 1 | – | – | – |
| train (in-sample context only) | 38 | 33 | -37.69% [-77.93, +15.80] | 0.184 |

## Durable-segment screen (NO at first fill, maker fee, all sampled combos)

| segment | Oct25–Jul26 ROI [CI] | Aug–Sep26 ROI | Oct–Nov26 ROI [CI] | late n |
|---|---|---|---|---|
| NFL | +2.81% [+0.73, +4.80] | +5.45% | +0.54% [-6.85, +7.02] | 224 |
| NCAAF | +nan% [+nan, +nan] | -6.59% | -2.50% [-11.47, +7.87] | 95 |
| NBA | +3.17% [+0.91, +5.42] | +nan% | -4.95% [-13.98, +2.88] | 130 |
| MLB | +2.47% [-0.21, +4.94] | +2.58% | -1.12% [-14.79, +8.37] | 26 |
| soccer | +0.65% [-1.39, +2.50] | -4.56% | -7.14% [-13.95, -1.22] | 141 |
| tennis | -2.55% [-7.36, +2.35] | -2.95% | -5.88% [-18.03, +6.36] | 54 |
| mixed | +3.98% [+1.66, +6.36] | +1.40% | +0.23% [-3.59, +3.60] | 493 |
| other | +1.17% [-6.42, +9.80] | +3.80% | -2.80% [-12.22, +4.76] | 107 |
| same-event | +3.03% [+1.57, +4.46] | +1.82% | -3.52% [-7.15, -0.01] | 628 |
| independent | +2.14% [+0.45, +3.91] | +0.57% | -0.98% [-4.27, +1.92] | 715 |
| legs 2 | +6.21% [-0.42, +13.51] | +13.76% | -14.16% [-27.84, -0.20] | 90 |
| legs 3 | +3.61% [-0.08, +7.07] | -7.64% | -5.04% [-14.10, +3.23] | 140 |
| legs 4–5 | +2.20% [+0.15, +4.20] | +2.40% | +0.31% [-5.61, +6.09] | 243 |
| legs 6–8 | +2.57% [+0.83, +4.29] | +0.60% | -1.55% [-6.57, +2.95] | 288 |
| legs 9–14 | +1.75% [+0.54, +2.91] | +0.40% | -0.63% [-3.98, +2.63] | 315 |
| legs 15–+ | +1.44% [+0.21, +2.52] | +1.06% | -1.37% [-3.93, +0.80] | 265 |
| price 0.00–0.01 | +0.31% [+0.05, +0.49] | -0.19% | +0.34% [+0.32, +0.37] | 364 |
| price 0.01–0.02 | +0.91% [+0.29, +1.41] | +0.89% | -0.40% [-3.22, +1.40] | 114 |
| price 0.02–0.05 | +0.89% [-0.01, +1.73] | +1.27% | -1.72% [-4.69, +0.94] | 224 |
| price 0.05–0.10 | +1.88% [+0.32, +3.27] | -0.82% | -0.65% [-4.76, +3.17] | 198 |
| price 0.10–0.20 | +2.26% [-0.33, +4.63] | +2.33% | +0.10% [-5.42, +5.13] | 192 |
| price 0.20–0.35 | +5.91% [+1.86, +9.93] | +5.97% | -5.97% [-19.75, +7.21] | 126 |
| price 0.35–0.50 | +6.69% [-2.23, +15.71] | +7.33% | -0.47% [-20.73, +20.36] | 72 |
| price 0.50–1.00 | +17.97% [-2.36, +36.76] | -9.52% | -32.28% [-59.52, -3.83] | 53 |

## A2b. Kalshi product / fee changes Aug–Nov 2026 (docs.kalshi.com/changelog unless noted)

- 2026-08-20: combo maker fee starts (0.5× multiplier, i.e. 0.035·q(1−q)); all-independent-NFL-leg combos exempt (KXMVECROSSCATEGORY0-SHARD1).
- 2026-08-22: fee swap — a quoter executing against an order resting < 5 s pays maker fee, resting side pays taker; post-only kept, repeat crossers can be rate-limited.
- 2026-09-03: finer combo ticks ($0.0001 below 1c / above 99c, $0.001 between) — makes tighter quoting possible.
- 2026-09-10: `target_cost_excludes_fees` RFQ flag. 2026-09-17: new combos all on KXMVECROSSCATEGORY (football on …CROSSCATEGORY0); RFQ/quote actions count against shard-1 write budget (matches the series shift in A1(iii)).
- 2026-10-01: `obscure_creator_id` (requester identity can be hidden from quoters — harder to screen sharp requesters).
- 2026-10-19: cancelled crossing post-only quotes count toward quoting penalties. 2026-11-12: max 100 open RFQs per user.
- Volume: record days 2026-10-10/11 (~$3.9B notional, parlays ~70%; cryptobriefing). As of 2026-11-03 parlay takers had lost ~$1.0B since Sep 2025 and makers netted ~$520M after ~$89M maker fees (cdcgaming / SCCG) — i.e. the house side was still profitable in aggregate. No source found naming new quoters entering or makers losing in Oct–Nov.

