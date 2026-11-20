# Is Polymarket any good at predictions? Calibration on resolved markets
Generated 2026-11-20 by `pm_calibration.py`. Pool: 40,140 resolved binary Polymarket markets (endDate 2023-01..2026-11, volume ≥ $500, pseudo-random 300/week). Stratified sample: 5,250 markets (≤250 per category × volume tercile). Price = last hourly CLOB point ≤ T−h, T = min(endDate, closedTime).

Pool category mix (before stratification): sports 40%, crypto 27%, other (weather etc.) 13%, politics 11%, tech/companies 3%, culture 3%, econ/fed 3%

## Horizon 1 day before resolution (n = 4,103)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 1907 | 0.020 | 0.014 | [0.010, 0.021] |
| 0.1–0.2 | 319 | 0.146 | 0.147 | [0.113, 0.190] |
| 0.2–0.3 | 309 | 0.247 | 0.201 | [0.160, 0.249] |
| 0.3–0.4 | 254 | 0.348 | 0.303 | [0.250, 0.362] |
| 0.4–0.5 | 311 | 0.454 | 0.392 | [0.340, 0.448] |
| 0.5–0.6 | 374 | 0.520 | 0.463 | [0.413, 0.513] |
| 0.6–0.7 | 141 | 0.646 | 0.681 | [0.600, 0.752] |
| 0.7–0.8 | 125 | 0.749 | 0.712 | [0.627, 0.784] |
| 0.8–0.9 | 100 | 0.848 | 0.840 | [0.756, 0.899] |
| 0.9–1.0 | 263 | 0.967 | 0.981 | [0.956, 0.992] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all (base = pooled YES rate) | 4103 | 2990 | 0.25 | 0.1014 | 0.2500 | 0.1886 | +0.46 | 0.310 | 0.565 | 0.022 | 0.86 |
| all (base = category YES rate) | 4103 | 2990 | 0.25 | 0.1014 | 0.2500 | 0.1843 | +0.45 | 0.310 | 0.553 | 0.022 | 0.86 |
| crypto | 297 | 291 | 0.36 | 0.1697 | 0.2500 | 0.2314 | +0.27 | 0.483 | 0.655 | 0.035 | 0.86 |
| culture | 619 | 345 | 0.24 | 0.0616 | 0.2500 | 0.1844 | +0.67 | 0.200 | 0.556 | 0.029 | 0.91 |
| econ/fed | 638 | 341 | 0.27 | 0.1173 | 0.2500 | 0.1955 | +0.40 | 0.354 | 0.580 | 0.053 | 0.85 |
| other (weather etc.) | 685 | 610 | 0.17 | 0.0753 | 0.2500 | 0.1407 | +0.46 | 0.241 | 0.455 | 0.028 | 0.89 |
| politics | 587 | 457 | 0.26 | 0.0873 | 0.2500 | 0.1935 | +0.55 | 0.276 | 0.576 | 0.045 | 0.87 |
| sports | 571 | 558 | 0.36 | 0.1782 | 0.2500 | 0.2296 | +0.22 | 0.519 | 0.652 | 0.043 | 0.73 |
| tech/companies | 706 | 416 | 0.19 | 0.0683 | 0.2500 | 0.1520 | +0.55 | 0.219 | 0.482 | 0.028 | 0.91 |
| volume tercile 1 (within category) | 1197 | 989 | 0.22 | 0.1006 | 0.2500 | 0.1700 | +0.41 | 0.313 | 0.523 | 0.063 | 0.88 |
| volume tercile 2 (within category) | 1368 | 1095 | 0.26 | 0.1048 | 0.2500 | 0.1939 | +0.46 | 0.320 | 0.576 | 0.023 | 0.86 |
| volume tercile 3 (within category) | 1538 | 1152 | 0.27 | 0.0991 | 0.2500 | 0.1970 | +0.50 | 0.299 | 0.583 | 0.030 | 0.85 |

Share of prices already ≤3¢ or ≥97¢ at this horizon: 39%

Favourite–longshot (both sides folded: cheap side of every market)

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 1137 | 0.007 | 0.001 | [0.000, 0.005] | 0.13 |
| 0.02–0.05 | 419 | 0.032 | 0.026 | [0.015, 0.046] | 0.82 |
| 0.05–0.10 | 346 | 0.072 | 0.058 | [0.038, 0.088] | 0.80 |
| 0.10–0.20 | 419 | 0.147 | 0.150 | [0.119, 0.188] | 1.02 |
| 0.20–0.35 | 619 | 0.271 | 0.242 | [0.210, 0.278] | 0.90 |
| 0.35–0.50 | 895 | 0.446 | 0.419 | [0.387, 0.452] | 0.94 |

## Horizon 7 days before resolution (n = 1,753)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 902 | 0.023 | 0.012 | [0.007, 0.022] |
| 0.1–0.2 | 155 | 0.145 | 0.174 | [0.123, 0.242] |
| 0.2–0.3 | 136 | 0.248 | 0.176 | [0.122, 0.249] |
| 0.3–0.4 | 98 | 0.346 | 0.337 | [0.251, 0.435] |
| 0.4–0.5 | 121 | 0.457 | 0.322 | [0.246, 0.410] |
| 0.5–0.6 | 105 | 0.524 | 0.429 | [0.338, 0.524] |
| 0.6–0.7 | 46 | 0.642 | 0.500 | [0.361, 0.639] |
| 0.7–0.8 | 43 | 0.744 | 0.721 | [0.573, 0.833] |
| 0.8–0.9 | 45 | 0.841 | 0.800 | [0.662, 0.891] |
| 0.9–1.0 | 102 | 0.961 | 0.980 | [0.931, 0.995] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all (base = pooled YES rate) | 1753 | 1281 | 0.21 | 0.0923 | 0.2500 | 0.1662 | +0.44 | 0.287 | 0.515 | 0.036 | 0.87 |
| all (base = category YES rate) | 1753 | 1281 | 0.21 | 0.0923 | 0.2500 | 0.1646 | +0.44 | 0.287 | 0.509 | 0.036 | 0.87 |
| crypto | 42 | 41 | 0.05 | 0.0391 | 0.2500 | 0.0454 | +0.14 | 0.147 | 0.191 | 0.071 | 0.97 |
| culture | 306 | 166 | 0.23 | 0.0882 | 0.2500 | 0.1746 | +0.49 | 0.280 | 0.534 | 0.036 | 0.88 |
| econ/fed | 369 | 193 | 0.21 | 0.0912 | 0.2500 | 0.1683 | +0.46 | 0.279 | 0.519 | 0.042 | 0.87 |
| other (weather etc.) | 257 | 224 | 0.18 | 0.0771 | 0.2500 | 0.1444 | +0.47 | 0.246 | 0.464 | 0.047 | 0.88 |
| politics | 326 | 265 | 0.20 | 0.0785 | 0.2500 | 0.1615 | +0.51 | 0.251 | 0.504 | 0.042 | 0.91 |
| sports | 228 | 222 | 0.28 | 0.1737 | 0.2500 | 0.2019 | +0.14 | 0.500 | 0.594 | 0.101 | 0.73 |
| tech/companies | 225 | 180 | 0.20 | 0.0641 | 0.2500 | 0.1573 | +0.59 | 0.219 | 0.494 | 0.034 | 0.92 |
| volume tercile 1 (within category) | 382 | 333 | 0.20 | 0.1052 | 0.2500 | 0.1594 | +0.34 | 0.325 | 0.499 | 0.087 | 0.87 |
| volume tercile 2 (within category) | 530 | 427 | 0.19 | 0.0823 | 0.2500 | 0.1531 | +0.46 | 0.264 | 0.484 | 0.049 | 0.89 |
| volume tercile 3 (within category) | 841 | 618 | 0.23 | 0.0926 | 0.2500 | 0.1768 | +0.48 | 0.284 | 0.539 | 0.025 | 0.87 |

Share of prices already ≤3¢ or ≥97¢ at this horizon: 40%

Favourite–longshot (both sides folded: cheap side of every market)

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 509 | 0.008 | 0.002 | [0.000, 0.011] | 0.24 |
| 0.02–0.05 | 271 | 0.032 | 0.015 | [0.006, 0.037] | 0.46 |
| 0.05–0.10 | 161 | 0.071 | 0.050 | [0.025, 0.095] | 0.70 |
| 0.10–0.20 | 200 | 0.148 | 0.180 | [0.133, 0.239] | 1.22 |
| 0.20–0.35 | 249 | 0.271 | 0.253 | [0.203, 0.310] | 0.93 |
| 0.35–0.50 | 300 | 0.443 | 0.397 | [0.343, 0.453] | 0.89 |

## Horizon 30 days before resolution (n = 752)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 423 | 0.029 | 0.007 | [0.002, 0.021] |
| 0.1–0.2 | 83 | 0.141 | 0.120 | [0.067, 0.208] |
| 0.2–0.3 | 40 | 0.243 | 0.275 | [0.161, 0.428] |
| 0.3–0.4 | 34 | 0.351 | 0.265 | [0.146, 0.431] |
| 0.4–0.5 | 40 | 0.456 | 0.250 | [0.142, 0.402] |
| 0.5–0.6 | 26 | 0.521 | 0.500 | [0.321, 0.679] |
| 0.6–0.7 | 27 | 0.642 | 0.556 | [0.373, 0.724] |
| 0.7–0.8 | 15 | 0.753 | 0.600 | [0.357, 0.802] |
| 0.8–0.9 | 25 | 0.848 | 0.960 | [0.805, 0.993] |
| 0.9–1.0 | 39 | 0.953 | 0.949 | [0.831, 0.986] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all (base = pooled YES rate) | 752 | 528 | 0.19 | 0.0757 | 0.2500 | 0.1523 | +0.50 | 0.243 | 0.483 | 0.042 | 0.90 |
| all (base = category YES rate) | 752 | 528 | 0.19 | 0.0757 | 0.2500 | 0.1496 | +0.49 | 0.243 | 0.471 | 0.042 | 0.90 |
| culture | 141 | 68 | 0.19 | 0.0701 | 0.2500 | 0.1548 | +0.55 | 0.230 | 0.488 | 0.086 | 0.94 |
| econ/fed | 166 | 91 | 0.26 | 0.0790 | 0.2500 | 0.1919 | +0.59 | 0.259 | 0.572 | 0.067 | 0.90 |
| other (weather etc.) | 129 | 110 | 0.16 | 0.0958 | 0.2500 | 0.1363 | +0.30 | 0.291 | 0.444 | 0.068 | 0.84 |
| politics | 164 | 129 | 0.16 | 0.0694 | 0.2500 | 0.1375 | +0.50 | 0.222 | 0.447 | 0.052 | 0.90 |
| sports | 39 | 35 | 0.26 | 0.1049 | 0.2500 | 0.1907 | +0.45 | 0.307 | 0.569 | 0.110 | 0.86 |
| tech/companies | 94 | 79 | 0.14 | 0.0551 | 0.2500 | 0.1192 | +0.54 | 0.193 | 0.402 | 0.067 | 0.95 |
| volume tercile 1 (within category) | 113 | 98 | 0.12 | 0.0733 | 0.2500 | 0.1085 | +0.32 | 0.236 | 0.375 | 0.075 | 0.94 |
| volume tercile 2 (within category) | 188 | 154 | 0.19 | 0.0819 | 0.2500 | 0.1515 | +0.46 | 0.264 | 0.481 | 0.068 | 0.90 |
| volume tercile 3 (within category) | 451 | 317 | 0.20 | 0.0737 | 0.2500 | 0.1624 | +0.55 | 0.236 | 0.506 | 0.027 | 0.90 |

Share of prices already ≤3¢ or ≥97¢ at this horizon: 36%

Favourite–longshot (both sides folded: cheap side of every market)

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 201 | 0.008 | 0.000 | [0.000, 0.019] | 0.00 |
| 0.02–0.05 | 128 | 0.032 | 0.008 | [0.001, 0.043] | 0.24 |
| 0.05–0.10 | 117 | 0.070 | 0.034 | [0.013, 0.085] | 0.49 |
| 0.10–0.20 | 108 | 0.144 | 0.102 | [0.058, 0.173] | 0.71 |
| 0.20–0.35 | 82 | 0.271 | 0.305 | [0.216, 0.411] | 1.12 |
| 0.35–0.50 | 100 | 0.435 | 0.320 | [0.237, 0.417] | 0.74 |

## Is there a tradable edge? (hold to resolution, returns per $ staked)

Rule: whenever the cheap side is priced 0.5–10¢ at the horizon, buy the favourite (= sell the longshot), or the reverse. Cost = half-spread + taker fee per share. t clusters by event (correlated legs of one event count once).

| horizon | rule | cost | trades | events | mean return | t (event-clustered) | worst trade |
|---|---|---|---|---|---|---|---|
| 1d | sell longshot (buy fav) | 0.0¢ | 1402 | 1139 | +0.96% | +1.58 | -100% |
| 1d | buy longshot | 0.0¢ | 1402 | 1139 | -51.43% | -4.00 | -100% |
| 1d | sell longshot (buy fav) | 0.5¢ | 1402 | 1139 | +0.44% | +0.49 | -100% |
| 1d | buy longshot | 0.5¢ | 1402 | 1139 | -57.07% | -5.37 | -100% |
| 1d | sell longshot (buy fav) | 1.0¢ | 1402 | 1139 | -0.07% | -0.61 | -100% |
| 1d | buy longshot | 1.0¢ | 1402 | 1139 | -61.36% | -6.68 | -100% |
| 1d | sell longshot (buy fav) | 2.0¢ | 1402 | 1139 | -1.08% | -2.80 | -100% |
| 1d | buy longshot | 2.0¢ | 1402 | 1139 | -67.57% | -9.22 | -100% |
| 7d | sell longshot (buy fav) | 0.0¢ | 769 | 613 | +1.48% | +3.56 | -100% |
| 7d | buy longshot | 0.0¢ | 769 | 613 | -54.43% | -2.55 | -100% |
| 7d | sell longshot (buy fav) | 0.5¢ | 769 | 613 | +0.96% | +2.48 | -100% |
| 7d | buy longshot | 0.5¢ | 769 | 613 | -62.66% | -4.18 | -100% |
| 7d | sell longshot (buy fav) | 1.0¢ | 769 | 613 | +0.44% | +1.39 | -100% |
| 7d | buy longshot | 1.0¢ | 769 | 613 | -67.69% | -5.66 | -100% |
| 7d | sell longshot (buy fav) | 2.0¢ | 769 | 613 | -0.57% | -0.78 | -100% |
| 7d | buy longshot | 2.0¢ | 769 | 613 | -73.96% | -8.42 | -100% |
| 30d | sell longshot (buy fav) | 0.0¢ | 369 | 293 | +2.47% | +4.18 | -100% |
| 30d | buy longshot | 0.0¢ | 369 | 293 | -79.86% | -9.81 | -100% |
| 30d | sell longshot (buy fav) | 0.5¢ | 369 | 293 | +1.94% | +3.40 | -100% |
| 30d | buy longshot | 0.5¢ | 369 | 293 | -81.45% | -10.77 | -100% |
| 30d | sell longshot (buy fav) | 1.0¢ | 369 | 293 | +1.42% | +2.62 | -100% |
| 30d | buy longshot | 1.0¢ | 369 | 293 | -82.78% | -11.69 | -100% |
| 30d | sell longshot (buy fav) | 2.0¢ | 369 | 293 | +0.39% | +1.07 | -100% |
| 30d | buy longshot | 2.0¢ | 369 | 293 | -84.89% | -13.49 | -100% |

## Kalshi macro markets (Fed, CPI, GDP, payrolls, unemployment)

2,988 settled strike markets, 313 events; series: KXCPIYOY 671, KXU3 613, KXCPI 534, KXFED 424, KXPAYROLLS 409, KXGDP 192, KXFEDDECISION 145

### Kalshi 1d (n = 2,320)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 762 | 0.028 | 0.012 | [0.006, 0.022] |
| 0.1–0.2 | 146 | 0.144 | 0.171 | [0.119, 0.241] |
| 0.2–0.3 | 96 | 0.249 | 0.229 | [0.156, 0.323] |
| 0.3–0.4 | 84 | 0.351 | 0.333 | [0.242, 0.439] |
| 0.4–0.5 | 80 | 0.448 | 0.438 | [0.334, 0.547] |
| 0.5–0.6 | 94 | 0.536 | 0.500 | [0.401, 0.599] |
| 0.6–0.7 | 104 | 0.649 | 0.635 | [0.539, 0.721] |
| 0.7–0.8 | 99 | 0.748 | 0.646 | [0.548, 0.734] |
| 0.8–0.9 | 145 | 0.853 | 0.855 | [0.789, 0.903] |
| 0.9–1.0 | 710 | 0.970 | 0.975 | [0.960, 0.984] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all Kalshi macro | 2320 | 311 | 0.48 | 0.0819 | 0.2500 | 0.2496 | +0.67 | 0.261 | 0.692 | 0.017 | 0.89 |
| KXCPI | 448 | 65 | 0.48 | 0.0750 | 0.2500 | 0.2495 | +0.70 | 0.246 | 0.692 | 0.027 | 0.89 |
| KXCPIYOY | 471 | 47 | 0.47 | 0.0605 | 0.2500 | 0.2489 | +0.76 | 0.210 | 0.691 | 0.030 | 0.93 |
| KXFED | 250 | 40 | 0.56 | 0.0018 | 0.2500 | 0.2469 | +0.99 | 0.020 | 0.687 | 0.019 | 1.00 |
| KXFEDDECISION | 122 | 29 | 0.24 | 0.0050 | 0.2500 | 0.1812 | +0.97 | 0.033 | 0.548 | 0.029 | 1.00 |
| KXGDP | 162 | 22 | 0.53 | 0.1121 | 0.2500 | 0.2490 | +0.55 | 0.356 | 0.691 | 0.081 | 0.85 |
| KXPAYROLLS | 394 | 44 | 0.59 | 0.1701 | 0.2500 | 0.2426 | +0.30 | 0.503 | 0.678 | 0.073 | 0.75 |
| KXU3 | 473 | 64 | 0.41 | 0.0881 | 0.2500 | 0.2415 | +0.64 | 0.276 | 0.676 | 0.048 | 0.88 |

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 695 | 0.011 | 0.001 | [0.000, 0.008] | 0.14 |
| 0.02–0.05 | 479 | 0.030 | 0.019 | [0.010, 0.035] | 0.63 |
| 0.05–0.10 | 296 | 0.069 | 0.057 | [0.036, 0.090] | 0.83 |
| 0.10–0.20 | 293 | 0.145 | 0.157 | [0.120, 0.203] | 1.08 |
| 0.20–0.35 | 280 | 0.273 | 0.314 | [0.263, 0.371] | 1.15 |
| 0.35–0.50 | 277 | 0.426 | 0.394 | [0.338, 0.452] | 0.92 |

### Kalshi 7d (n = 2,192)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 682 | 0.031 | 0.015 | [0.008, 0.027] |
| 0.1–0.2 | 146 | 0.142 | 0.164 | [0.113, 0.233] |
| 0.2–0.3 | 104 | 0.246 | 0.192 | [0.128, 0.278] |
| 0.3–0.4 | 92 | 0.347 | 0.348 | [0.258, 0.449] |
| 0.4–0.5 | 83 | 0.448 | 0.518 | [0.412, 0.622] |
| 0.5–0.6 | 100 | 0.544 | 0.550 | [0.452, 0.644] |
| 0.6–0.7 | 109 | 0.649 | 0.587 | [0.493, 0.675] |
| 0.7–0.8 | 100 | 0.752 | 0.690 | [0.594, 0.772] |
| 0.8–0.9 | 153 | 0.854 | 0.824 | [0.755, 0.876] |
| 0.9–1.0 | 623 | 0.967 | 0.973 | [0.957, 0.983] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all Kalshi macro | 2192 | 311 | 0.48 | 0.0908 | 0.2500 | 0.2495 | +0.64 | 0.287 | 0.692 | 0.022 | 0.87 |
| KXCPI | 427 | 65 | 0.48 | 0.0861 | 0.2500 | 0.2498 | +0.66 | 0.276 | 0.693 | 0.037 | 0.88 |
| KXCPIYOY | 454 | 45 | 0.44 | 0.0598 | 0.2500 | 0.2470 | +0.76 | 0.206 | 0.687 | 0.034 | 0.92 |
| KXFED | 236 | 42 | 0.55 | 0.0117 | 0.2500 | 0.2474 | +0.95 | 0.054 | 0.688 | 0.019 | 0.99 |
| KXFEDDECISION | 120 | 29 | 0.24 | 0.0214 | 0.2500 | 0.1833 | +0.88 | 0.092 | 0.553 | 0.031 | 0.98 |
| KXGDP | 166 | 22 | 0.54 | 0.1050 | 0.2500 | 0.2487 | +0.58 | 0.330 | 0.691 | 0.085 | 0.84 |
| KXPAYROLLS | 365 | 44 | 0.60 | 0.1873 | 0.2500 | 0.2405 | +0.22 | 0.549 | 0.674 | 0.097 | 0.72 |
| KXU3 | 424 | 64 | 0.41 | 0.1036 | 0.2500 | 0.2420 | +0.57 | 0.328 | 0.677 | 0.063 | 0.84 |

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 522 | 0.011 | 0.002 | [0.000, 0.011] | 0.18 |
| 0.02–0.05 | 470 | 0.030 | 0.013 | [0.006, 0.028] | 0.42 |
| 0.05–0.10 | 312 | 0.071 | 0.064 | [0.042, 0.097] | 0.91 |
| 0.10–0.20 | 300 | 0.144 | 0.170 | [0.132, 0.217] | 1.18 |
| 0.20–0.35 | 297 | 0.271 | 0.276 | [0.228, 0.330] | 1.02 |
| 0.35–0.50 | 291 | 0.422 | 0.467 | [0.411, 0.525] | 1.11 |

### Kalshi 30d (n = 1,787)

| bin | n | mean price | YES freq | 95% CI |
|---|---|---|---|---|
| 0.0–0.1 | 413 | 0.037 | 0.024 | [0.013, 0.044] |
| 0.1–0.2 | 168 | 0.144 | 0.101 | [0.064, 0.156] |
| 0.2–0.3 | 107 | 0.246 | 0.234 | [0.164, 0.322] |
| 0.3–0.4 | 81 | 0.344 | 0.346 | [0.251, 0.454] |
| 0.4–0.5 | 111 | 0.450 | 0.387 | [0.302, 0.480] |
| 0.5–0.6 | 121 | 0.532 | 0.537 | [0.449, 0.624] |
| 0.6–0.7 | 95 | 0.650 | 0.632 | [0.531, 0.722] |
| 0.7–0.8 | 104 | 0.748 | 0.788 | [0.700, 0.856] |
| 0.8–0.9 | 132 | 0.852 | 0.841 | [0.769, 0.894] |
| 0.9–1.0 | 455 | 0.961 | 0.969 | [0.949, 0.982] |

| slice | n | events | YES rate | Brier | Brier 50% | Brier base-rate | skill vs base | log loss | log loss base | ECE | hit rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all Kalshi macro | 1787 | 263 | 0.49 | 0.1068 | 0.2500 | 0.2500 | +0.57 | 0.338 | 0.693 | 0.018 | 0.85 |
| KXCPI | 368 | 55 | 0.49 | 0.1359 | 0.2500 | 0.2500 | +0.46 | 0.425 | 0.693 | 0.030 | 0.80 |
| KXCPIYOY | 407 | 42 | 0.46 | 0.1100 | 0.2500 | 0.2487 | +0.56 | 0.357 | 0.691 | 0.056 | 0.87 |
| KXFED | 253 | 40 | 0.58 | 0.0201 | 0.2500 | 0.2428 | +0.92 | 0.081 | 0.679 | 0.032 | 0.98 |
| KXFEDDECISION | 109 | 28 | 0.25 | 0.0464 | 0.2500 | 0.1863 | +0.75 | 0.164 | 0.560 | 0.045 | 0.94 |
| KXGDP | 145 | 21 | 0.59 | 0.1280 | 0.2500 | 0.2413 | +0.47 | 0.405 | 0.676 | 0.058 | 0.82 |
| KXPAYROLLS | 247 | 33 | 0.58 | 0.1632 | 0.2500 | 0.2438 | +0.33 | 0.489 | 0.681 | 0.067 | 0.76 |
| KXU3 | 258 | 44 | 0.41 | 0.1047 | 0.2500 | 0.2427 | +0.57 | 0.327 | 0.679 | 0.093 | 0.85 |

| cheap-side price | n | mean price | won | 95% CI | won / priced |
|---|---|---|---|---|---|
| 0.00–0.02 | 256 | 0.011 | 0.008 | [0.002, 0.028] | 0.72 |
| 0.02–0.05 | 315 | 0.030 | 0.019 | [0.009, 0.041] | 0.63 |
| 0.05–0.10 | 296 | 0.069 | 0.054 | [0.034, 0.086] | 0.78 |
| 0.10–0.20 | 301 | 0.146 | 0.126 | [0.093, 0.169] | 0.87 |
| 0.20–0.35 | 295 | 0.269 | 0.264 | [0.217, 0.318] | 0.98 |
| 0.35–0.50 | 324 | 0.435 | 0.429 | [0.376, 0.483] | 0.99 |

Kalshi edge test (fee ≈ 0.07·p·(1−p) per contract ≈ 0.35–0.65¢ at 5–10¢, plus half-spread):

| horizon | rule | cost | trades | events | mean return | t (event-clustered) | worst trade |
|---|---|---|---|---|---|---|---|
| 1d | sell longshot (buy fav) | 0.0¢ | 1470 | 294 | +1.05% | +0.77 | -100% |
| 1d | buy longshot | 0.0¢ | 1470 | 294 | -59.94% | -2.60 | -100% |
| 1d | sell longshot (buy fav) | 1.0¢ | 1470 | 294 | +0.02% | -0.74 | -100% |
| 1d | buy longshot | 1.0¢ | 1470 | 294 | -69.49% | -4.39 | -100% |
| 1d | sell longshot (buy fav) | 2.0¢ | 1470 | 294 | -0.99% | -2.25 | -100% |
| 1d | buy longshot | 2.0¢ | 1470 | 294 | -74.63% | -6.04 | -100% |
| 7d | sell longshot (buy fav) | 0.0¢ | 1304 | 285 | +1.18% | +0.00 | -100% |
| 7d | buy longshot | 0.0¢ | 1304 | 285 | -55.24% | -0.36 | -100% |
| 7d | sell longshot (buy fav) | 1.0¢ | 1304 | 285 | +0.15% | -1.05 | -100% |
| 7d | buy longshot | 1.0¢ | 1304 | 285 | -66.05% | -1.87 | -100% |
| 7d | sell longshot (buy fav) | 2.0¢ | 1304 | 285 | -0.87% | -2.10 | -100% |
| 7d | buy longshot | 2.0¢ | 1304 | 285 | -71.79% | -3.29 | -100% |
| 30d | sell longshot (buy fav) | 0.0¢ | 867 | 212 | +1.07% | +0.81 | -100% |
| 30d | buy longshot | 0.0¢ | 867 | 212 | -31.15% | -0.93 | -100% |
| 30d | sell longshot (buy fav) | 1.0¢ | 867 | 212 | +0.03% | -0.20 | -100% |
| 30d | buy longshot | 1.0¢ | 867 | 212 | -50.84% | -2.57 | -100% |
| 30d | sell longshot (buy fav) | 2.0¢ | 867 | 212 | -0.99% | -1.21 | -100% |
| 30d | buy longshot | 2.0¢ | 867 | 212 | -60.08% | -3.91 | -100% |

## Worked example: Anthropic IPO day, 2026-11-19

Prices: day before at 16:00 NY (2026-11-18 21:00 UTC) and pre-open 09:00 NY (14:00 UTC). Outcome = how the market resolved that evening.

| event | bucket / question | vol $ | p (eve) | p (pre-open) | outcome |
|---|---|---|---|---|---|
| anthropic-closing-share-price-on-ipo-day | $100 to $110 | 29,266 | 0.265 | 0.385 | no |
| anthropic-closing-share-price-on-ipo-day | $110 to $120 | 13,258 | 0.160 | 0.210 | no |
| anthropic-closing-share-price-on-ipo-day | $120+ | 15,918 | 0.085 | 0.120 | no |
| anthropic-closing-share-price-on-ipo-day | $70 to $80 | 11,787 | 0.038 | 0.012 | no |
| anthropic-closing-share-price-on-ipo-day | $80 to $90 | 15,476 | 0.065 | 0.034 | no |
| anthropic-closing-share-price-on-ipo-day | $90 to $100 | 28,832 | 0.315 | 0.230 | YES |
| anthropic-closing-share-price-on-ipo-day | <$70 | 4,797 | 0.015 | 0.007 | no |
| anthropic-ipo-closing-market-cap-119 | 100–200B | 93,827 | 0.001 | 0.001 | no |
| anthropic-ipo-closing-market-cap-119 | 200–300B | 36,127 | 0.002 | 0.001 | no |
| anthropic-ipo-closing-market-cap-119 | 300–400B | 87,700 | 0.002 | 0.001 | no |
| anthropic-ipo-closing-market-cap-119 | 400–600B | 56,622 | 0.002 | 0.002 | no |
| anthropic-ipo-closing-market-cap-119 | 600B+ | 105,465 | 0.996 | 0.997 | YES |
| anthropic-ipo-closing-market-cap-119 | <100B | 181,274 | 0.001 | 0.001 | no |
| anthropic-ipo-closing-market-cap-979 | 0.6–0.9T | 148,120 | 0.007 | 0.007 | no |
| anthropic-ipo-closing-market-cap-979 | 0.9–1.2T | 364,013 | 0.204 | 0.102 | no |
| anthropic-ipo-closing-market-cap-979 | 1.2–1.5T | 302,084 | 0.601 | 0.586 | YES |
| anthropic-ipo-closing-market-cap-979 | 1.5–1.8T | 216,568 | 0.160 | 0.289 | no |
| anthropic-ipo-closing-market-cap-979 | 1.8T+ | 624,216 | 0.032 | 0.041 | no |
| anthropic-ipo-closing-market-cap-979 | <0.6T | 68,325 | 0.001 | 0.001 | no |
| anthropic-ipo-closing-market-cap-above | $1.0T | 212,591 | 0.961 | 0.992 | YES |
| anthropic-ipo-closing-market-cap-above | $1.1T | 2,974,300 | nan | 0.958 | YES |
| anthropic-ipo-closing-market-cap-above | $1.25T | 435,103 | 0.645 | 0.785 | YES |
| anthropic-ipo-closing-market-cap-above | $1.2T | 367,014 | nan | 0.895 | YES |
| anthropic-ipo-closing-market-cap-above | $1.35T | 76,894 | nan | 0.575 | no |
| anthropic-ipo-closing-market-cap-above | $1.3T | 123,369 | nan | 0.720 | no |
| anthropic-ipo-closing-market-cap-above | $1.45T | 62,739 | nan | 0.375 | no |
| anthropic-ipo-closing-market-cap-above | $1.4T | 86,803 | nan | 0.535 | no |
| anthropic-ipo-closing-market-cap-above | $1.5T | 419,608 | 0.199 | 0.340 | no |
| anthropic-ipo-closing-market-cap-above | $1.6T | 78,962 | nan | 0.235 | no |
| anthropic-ipo-closing-market-cap-above | $1.75T | 287,925 | 0.060 | 0.102 | no |
| anthropic-ipo-closing-market-cap-above | $2.25T | 38,186 | 0.017 | 0.017 | no |
| anthropic-ipo-closing-market-cap-above | $2.5T | 27,431 | 0.012 | 0.011 | no |
| anthropic-ipo-closing-market-cap-above | $2.75T | 5,258 | 0.004 | 0.007 | no |
| anthropic-ipo-closing-market-cap-above | $2T | 182,573 | 0.036 | 0.042 | no |
| anthropic-ipo-closing-market-cap-above | $3T | 7,733 | 0.003 | 0.004 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $1.25–$1.5T | 2,091,667 | 0.421 | 0.477 | YES |
| anthropic-ipo-closing-market-cap-higher-strikes | $1.5–$1.75T | 2,393,975 | 0.113 | 0.228 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $1.75–$2.0T | 2,386,664 | 0.028 | 0.051 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $2.0–$2.25T | 2,073,274 | 0.021 | 0.021 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $2.25–$2.5T | 1,297,778 | 0.007 | 0.006 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $2.5–$2.75T | 833,783 | 0.004 | 0.004 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $2.75–$3.0T | 764,964 | 0.002 | 0.003 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | $3.0T+ | 920,839 | 0.002 | 0.003 | no |
| anthropic-ipo-closing-market-cap-higher-strikes | <$1.25T | 6,447,057 | 0.409 | 0.203 | no |
| anthropic-ipo-closing-price-above-ipo-price-on-first-day | Anthropic IPO: Closing Price above IPO Price on First Day? | 368,899 | 0.957 | 0.983 | YES |
| anthropic-ipo-first-day-pop-above | 0% | 1,180 | 0.980 | 0.975 | YES |
| anthropic-ipo-first-day-pop-above | 10% | 3,908 | 0.785 | 0.880 | YES |
| anthropic-ipo-first-day-pop-above | 100% | 2,333 | 0.015 | 0.021 | no |
| anthropic-ipo-first-day-pop-above | 20% | 2,273 | 0.515 | 0.675 | no |
| anthropic-ipo-first-day-pop-above | 30% | 851 | 0.480 | 0.425 | no |
| anthropic-ipo-first-day-pop-above | 50% | 2,073 | 0.170 | 0.110 | no |
| anthropic-ipo-first-day-pop-above | 75% | 1,493 | 0.070 | 0.035 | no |
| anthropic-ipo-open-price-above-ipo-price | Anthropic IPO: Open Price above IPO Price? | 20,946 | 0.970 | 0.984 | YES |
| anthropic-opening-share-price-on-ipo-day | $100 to $110 | 62,905 | 0.195 | 0.365 | no |
| anthropic-opening-share-price-on-ipo-day | $110 to $120 | 153,488 | 0.050 | 0.142 | YES |
| anthropic-opening-share-price-on-ipo-day | $120+ | 38,055 | 0.110 | 0.021 | no |
| anthropic-opening-share-price-on-ipo-day | $70 to $80 | 20,848 | 0.012 | 0.010 | no |
| anthropic-opening-share-price-on-ipo-day | $80 to $90 | 44,711 | 0.245 | 0.090 | no |
| anthropic-opening-share-price-on-ipo-day | $90 to $100 | 34,363 | 0.420 | 0.380 | no |
| anthropic-opening-share-price-on-ipo-day | <$70 | 10,276 | 0.009 | 0.009 | no |
| anthropic-opening-share-price-on-ipo-day | No IPO by December 31, 2027 | 2,733 | 0.015 | 0.001 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Down 10% to 0% | 6,790 | 0.029 | 0.041 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Down more than 10% | 3,218 | 0.011 | 0.009 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Up 0% to 10% | 4,501 | 0.160 | 0.070 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Up 10% to 20% | 3,885 | 0.275 | 0.190 | YES |
| how-much-will-anthropics-stock-move-on-ipo-day | Up 20% to 30% | 2,361 | 0.195 | 0.355 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Up 30% to 50% | 5,199 | 0.183 | 0.256 | no |
| how-much-will-anthropics-stock-move-on-ipo-day | Up 50%+ | 5,826 | 0.165 | 0.080 | no |

Pre-open Brier over 68 contracts: 0.081 (50%: 0.250). Mean pre-open price of the 14 buckets that won: 0.72.

## Literature (brief)
- Wolfers & Zitzewitz (2004), "Prediction Markets", *J. Econ. Perspectives* 18(2): prices are good aggregate forecasts,
  usually at least as good as polls/experts; flags thin markets, longshot bias and manipulation attempts as limits.
- Berg, Nelson & Rietz (2008), "Prediction market accuracy in the long run", *Int. J. Forecasting* 24: Iowa Electronic
  Markets beat 964 polls 74% of the time across 1988–2004 US elections, more so far from election day.
- Snowberg & Wolfers (2010), *J. Political Economy* 118(4): the favourite–longshot bias in racetrack betting is driven by
  probability misperception (longshots overbet). Page & Clemen (2013), *Economic Journal* 123: Intrade-era prediction
  markets well calibrated near expiry, but a longshot bias appears for events far in the future (cost of locked capital).
- Rothschild & Sethi (2016), *J. Prediction Markets*: one Intrade trader spent ~$4M propping Romney in 2012; prices moved
  but reverted — manipulation is possible short-term and costly. Failures: markets favoured Remain (Brexit) and Clinton
  in 2016, roughly like polls.
- 2024 US election: Polymarket had Trump ~60%+ for weeks while poll averages were ~50/50; the outcome favoured the market,
  but a few whales (one ~$30M+ French trader) moved the headline price, so one election is weak evidence either way.
- Diercks, Katz & Wright (2026), "Kalshi and the Rise of Macro Markets", FEDS 2026-010 (Federal Reserve Board): Kalshi
  FOMC-decision markets had a perfect record the day before meetings and matched/beat fed funds futures on rate paths;
  CPI markets compared well with consensus surveys. (Our Kalshi KXFED/KXFEDDECISION skill of 0.95–0.99 at 1–7d agrees.)
- Resolution/integrity: Polymarket's March 2025 Ukraine minerals-deal market resolved YES via a UMA vote despite no
  signed deal (large UMA holder suspected); a Columbia SSRN paper (Nov 2025, "Network-Based Detection of Wash Trading")
  estimates ~25% of 2022–25 Polymarket volume was likely wash trading (~45% in sports at peaks) — volume ≠ liquidity.
- Recent Polymarket calibration replications (theses/preprints/GitHub, not peer reviewed) mostly find good calibration
  with a mild longshot overpricing that grows with horizon — consistent with the tables above.

## Caveats
- T = min(endDate, closedTime). Markets that resolve early ("by date X" that happen, awards announced) are timed from the resolution stamp, which lags the news by hours to days (UMA liveness) — so the 1-day horizon partly scores prices set after the outcome was public. The 'share already ≤3¢/≥97¢' line shows how much.
- Only markets still listed by gamma with a 1/0 settlement; voided/50-50 and disputed-then-reversed markets are excluded, and delisted markets are invisible (survivorship).
- CLOB history price is the hourly point Polymarket serves (mid/last), not an executable quote; thin markets can show stale or one-sided prices. Spreads on 1–5¢ longshots are often ≥1¢, i.e. 20–100% of the price.
- Stratified sample: pooled numbers overweight small categories relative to Polymarket's actual mix (which is dominated by crypto up/down and sports). Category regexes are approximate.
- Many markets in one event are mechanically correlated (e.g. 20 'Will X win the Open?' legs); t-stats cluster by event but CIs in calibration tables do not.
