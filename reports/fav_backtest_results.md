# Favourite backtest across Polymarket groups (which groups to add to the forward paper tests)
Generated 2026-11-20 by `fav_backtest.py`. Window 2024-01-01 → 2026-11-20 (decision time).

**Rule (fixed before looking, identical for all groups):** favourite side of each resolved binary market, price at the decision time (sports games: last hourly CLOB point ≥ 2h before start; sports without a start time — golf/F1/boxing/UFC cards — scheduled end − 3 days; non-sports: scheduled end − 7 days), buy if 0.85–0.97, hold to resolution. Entry = price + 1¢; fee = rate·p(1−p) per share (sports 0.03 → 0.05 from 2026-07-10, geopolitics 0, crypto 0.07, other non-sports 0.04). Clean 1/0 settlements only; volume ≥ $1,000.

Candidates: 175,680 markets; priced sample ≤ 2000 per group (61,220 with a usable price); bets (price in range): 9,418. CI = bootstrap over clusters (sports: game day; non-sports: event). p = one-sided cluster-robust test of ROI > 0; Holm across all groups below. Bets/yr = in-range rate in the priced sample × candidates in the last 12 months.

## Sports groups

| group | bets | clusters | bets/yr | win rate | avg price | ROI/$ | 95% CI (cluster boot) | p (ROI≤0) | Holm p | 0.85–0.90 | 0.90–0.95 | 0.95–0.97 | halves | discovery 70% | holdout 30% (n) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ATP | 151 | 97 | 803 | 0.921 | 0.907 | +0.0% | [-4.5%, +4.3%] | 0.492 | 1.000 | +5.4% (64) | -5.3% (72) | +3.3% (15) | +1.6% / -1.4% | +0.8% | -1.8% (45) |
| Bundesliga | 111 | 56 | 84 | 0.874 | 0.895 | -3.9% | [-11.8%, +3.8%] | 0.832 | 1.000 | -7.7% (65) | +4.1% (37) | -8.6% (9) | -2.4% / -5.3% | -2.6% | -6.7% (33) |
| CS2 | 142 | 106 | 630 | 0.887 | 0.894 | -2.3% | [-8.3%, +3.1%] | 0.789 | 1.000 | -3.2% (85) | -1.7% (49) | +3.2% (8) | -0.3% / -4.3% | -3.2% | -0.2% (42) |
| Dota | 193 | 120 | 251 | 0.902 | 0.892 | -0.5% | [-5.4%, +4.3%] | 0.577 | 1.000 | -1.6% (116) | +0.9% (67) | +2.8% (10) | -1.0% / +0.1% | +0.5% | -2.7% (57) |
| EPL | 127 | 73 | 83 | 0.906 | 0.889 | +0.4% | [-5.1%, +5.6%] | 0.449 | 1.000 | +0.0% (87) | +0.8% (35) | +2.9% (5) | +3.9% / -3.1% | -0.2% | +1.7% (38) |
| F1 | 452 | 75 | 258 | 0.909 | 0.926 | -3.1% | [-6.4%, -0.2%] | 0.978 | 1.000 | -6.6% (112) | -1.7% (186) | -2.4% (154) | +0.2% / -6.4% | -1.4% | -7.2% (135) |
| La Liga | 144 | 80 | 102 | 0.931 | 0.897 | +2.2% | [-2.9%, +6.3%] | 0.181 | 1.000 | +1.7% (82) | +2.9% (54) | +2.8% (8) | +4.1% / +0.2% | +2.5% | +1.4% (43) |
| Ligue 1 | 103 | 64 | 71 | 0.922 | 0.890 | +2.1% | [-5.1%, +8.4%] | 0.279 | 1.000 | +1.3% (68) | +3.8% (31) | +3.2% (4) | +1.8% / +2.5% | +1.5% | +3.7% (30) |
| LoL | 344 | 182 | 535 | 0.913 | 0.898 | +0.0% | [-3.5%, +3.3%] | 0.489 | 1.000 | -2.2% (191) | +2.8% (133) | +3.1% (20) | -1.3% / +1.4% | +0.0% | +0.1% (103) |
| MLB | 3 | 3 | 0 | 1.000 | 0.936 | +5.6% | [+2.1%, +10.8%] | 0.017 | nan | +10.8% (1) | — (0) | +3.0% (2) | +10.8% / +3.0% | +5.6% | — (0) |
| MLS | 79 | 54 | 56 | 0.899 | 0.875 | +1.1% | [-6.3%, +8.0%] | 0.378 | 1.000 | +1.9% (70) | -5.4% (8) | +3.5% (1) | +3.8% / -1.4% | +2.5% | -2.2% (23) |
| MMA/UFC | 108 | 61 | 60 | 0.917 | 0.899 | +0.8% | [-6.2%, +7.0%] | 0.403 | 1.000 | +7.6% (61) | -7.6% (29) | -8.6% (18) | +0.7% / +1.0% | +3.7% | -6.0% (32) |
| NBA | 237 | 163 | 154 | 0.920 | 0.887 | +2.2% | [-2.2%, +6.1%] | 0.153 | 1.000 | +0.8% (169) | +5.7% (66) | +2.6% (2) | +1.8% / +2.6% | +1.4% | +4.1% (71) |
| NCAAB | 438 | 131 | 1016 | 0.916 | 0.914 | -1.3% | [-4.7%, +1.7%] | 0.789 | 1.000 | -5.5% (162) | +2.0% (177) | -0.2% (99) | +4.2% / -6.8% | +0.6% | -5.7% (131) |
| NCAAF | 386 | 81 | 267 | 0.922 | 0.910 | -0.1% | [-3.0%, +2.8%] | 0.527 | 1.000 | +1.2% (157) | -1.8% (166) | +1.3% (63) | +1.7% / -1.9% | +1.2% | -3.1% (115) |
| NFL | 39 | 29 | 19 | 0.949 | 0.888 | +5.3% | [-3.4%, +11.4%] | 0.096 | 1.000 | +4.5% (29) | +8.1% (9) | +3.5% (1) | +3.9% / +6.6% | +6.8% | +1.4% (11) |
| Serie A | 142 | 90 | 109 | 0.887 | 0.889 | -1.8% | [-7.1%, +3.8%] | 0.732 | 1.000 | -2.1% (91) | -1.4% (48) | +3.5% (3) | +1.4% / -4.9% | -0.4% | -5.1% (42) |
| UCL | 256 | 56 | 135 | 0.918 | 0.900 | +0.6% | [-3.7%, +4.1%] | 0.385 | 1.000 | +2.9% (136) | -3.6% (90) | +3.0% (30) | +1.9% / -0.7% | -0.1% | +2.2% (76) |
| Valorant | 133 | 86 | 143 | 0.932 | 0.886 | +3.8% | [-1.3%, +8.2%] | 0.053 | 1.000 | +5.0% (100) | +0.1% (30) | +3.2% (3) | +6.4% / +1.4% | +4.4% | +2.6% (39) |
| WNBA | 93 | 82 | 45 | 0.849 | 0.892 | -6.3% | [-14.4%, +1.3%] | 0.937 | 1.000 | -8.8% (58) | -2.2% (34) | +3.5% (1) | -4.4% / -8.1% | -8.0% | -2.1% (27) |
| WTA | 236 | 139 | 643 | 0.936 | 0.904 | +2.1% | [-1.7%, +5.5%] | 0.128 | 1.000 | +3.4% (107) | +2.5% (104) | -5.2% (25) | -0.0% / +4.2% | +1.3% | +4.1% (70) |
| boxing | 53 | 29 | 36 | 0.962 | 0.912 | +4.1% | [-1.9%, +8.5%] | 0.064 | 1.000 | +2.9% (23) | +6.0% (19) | +3.0% (11) | +3.5% / +4.7% | +3.1% | +6.5% (15) |
| cricket | 241 | 136 | 233 | 0.946 | 0.910 | +2.5% | [-1.3%, +5.7%] | 0.081 | 1.000 | +2.5% (100) | +3.4% (86) | +1.1% (55) | +4.5% / +0.5% | +3.8% | -0.4% (72) |
| esports other | 232 | 152 | 207 | 0.858 | 0.897 | -5.9% | [-11.5%, -1.1%] | 0.989 | 1.000 | -7.3% (135) | -6.4% (72) | +3.0% (25) | -4.4% / -7.4% | -3.8% | -11.0% (69) |
| golf | 572 | 77 | 696 | 0.935 | 0.931 | -0.7% | [-3.1%, +1.6%] | 0.725 | 1.000 | +5.1% (133) | -3.5% (185) | -1.8% (254) | +0.7% / -2.2% | +0.7% | -4.0% (171) |
| other soccer | 196 | 148 | 2876 | 0.913 | 0.901 | -0.2% | [-4.9%, +3.9%] | 0.528 | 1.000 | +0.1% (98) | -1.2% (79) | +3.0% (19) | +0.3% / -0.6% | -0.2% | -0.1% (58) |
| other tennis | 391 | 137 | 2711 | 0.880 | 0.904 | -4.3% | [-7.7%, -0.9%] | 0.993 | 1.000 | -7.9% (176) | -2.5% (171) | +3.2% (44) | -4.8% / -3.8% | -6.5% | +1.0% (117) |
| (top-7 soccer, team-win YES only) | 63 | 51 | 42 | 0.937 | 0.888 | +4.0% | [-3.1%, +9.9%] | 0.130 | nan | +2.7% (44) | +7.4% (17) | +2.7% (2) | -0.0% / +7.9% | +3.9% | +4.3% (18) |

Groups with no favourite priced 0.85–0.97 at the decision time in the priced sample: NHL (1998 priced) — favourites in these sports are rarely that heavy before the game.

## Non-sports groups

| group | bets | clusters | bets/yr | win rate | avg price | ROI/$ | 95% CI (cluster boot) | p (ROI≤0) | Holm p | 0.85–0.90 | 0.90–0.95 | 0.95–0.97 | halves | discovery 70% | holdout 30% (n) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US politics | 571 | 469 | 2559 | 0.949 | 0.923 | +1.5% | [-0.4%, +3.5%] | 0.070 | 1.000 | +5.0% (162) | -0.3% (217) | +0.7% (192) | -0.0% / +3.1% | +1.1% | +2.6% (171) |
| crypto | 379 | 253 | 370 | 0.934 | 0.923 | -0.3% | [-3.1%, +2.3%] | 0.584 | 1.000 | +4.6% (103) | -3.3% (156) | -0.7% (120) | +2.0% / -2.6% | +0.6% | -2.3% (113) |
| culture/awards | 616 | 394 | 2474 | 0.920 | 0.925 | -1.8% | [-4.0%, +0.4%] | 0.947 | 1.000 | -2.0% (155) | -2.2% (275) | -1.0% (186) | +0.1% / -3.7% | -0.3% | -5.5% (184) |
| economics/Fed | 532 | 466 | 2496 | 0.930 | 0.923 | -0.6% | [-3.1%, +1.7%] | 0.697 | 1.000 | -0.6% (147) | -1.9% (215) | +1.0% (170) | -0.5% / -0.7% | -1.9% | +2.3% (159) |
| geopolitics | 525 | 376 | 950 | 0.907 | 0.921 | -2.7% | [-5.5%, +0.0%] | 0.972 | 1.000 | -9.6% (154) | +1.4% (219) | -1.8% (152) | -2.0% / -3.4% | -1.5% | -5.6% (157) |
| tech/companies | 380 | 263 | 537 | 0.945 | 0.928 | +0.5% | [-2.4%, +3.0%] | 0.368 | 1.000 | +0.6% (85) | +1.5% (146) | -0.6% (149) | +0.2% / +0.8% | +0.4% | +0.6% (114) |
| weather | 360 | 172 | 324 | 0.922 | 0.920 | -1.2% | [-4.3%, +1.7%] | 0.775 | 1.000 | -1.4% (115) | +0.5% (138) | -3.0% (107) | -1.6% / -0.7% | -1.1% | -1.2% (108) |
| world elections | 453 | 318 | 625 | 0.927 | 0.924 | -1.1% | [-4.0%, +1.5%] | 0.783 | 1.000 | -4.9% (123) | +0.5% (178) | +0.2% (152) | -0.8% / -1.3% | -1.0% | -1.2% (135) |

## Decision

ADD = not already forward-tested, ROI > 0 in discovery (first 70%) AND holdout (last 30%), cluster-CI lower bound > −1%, ≥ 30 bets.

- **Add:** US politics
- **Exclude:** CS2, Dota, F1, LoL, MLB, MMA/UFC, NCAAB, NCAAF, NFL, Valorant, WNBA, boxing, cricket, crypto, culture/awards, economics/Fed, esports other, geopolitics, golf, other soccer, other tennis, tech/companies, weather, world elections
- Existing forward groups present here: ATP, Bundesliga, EPL, La Liga, Ligue 1, MLS, NBA, Serie A, UCL, WTA

| set | bets/yr | expected ROI per bet (bets/yr-weighted) | pooled 95% CI |
|---|---|---|---|
| existing (tennis ATP/WTA, top-7 soccer, NBA) | 2240 | +0.8% | [-1.0%, +2.2%] |
| recommended additions | 2559 | +1.5% | [-0.4%, +3.5%] |
| existing + additions | 4798 | +1.2% | [-0.4%, +2.1%] |

## Coverage (candidate markets by decision year)

| group           |   2024 |   2025 |   2026 |
|:----------------|-------:|-------:|-------:|
| ATP             |      6 |    703 |  10515 |
| Bundesliga      |      0 |    404 |    680 |
| CS2             |      0 |    817 |   8303 |
| Dota            |      0 |    463 |   2286 |
| EPL             |    139 |    558 |    811 |
| F1              |     80 |   1293 |    647 |
| La Liga         |      0 |    518 |    892 |
| Ligue 1         |      0 |    431 |    688 |
| LoL             |      0 |    280 |   2974 |
| MLB             |      1 |   2493 |   2502 |
| MLS             |      0 |    584 |   1412 |
| MMA/UFC         |     56 |    534 |    600 |
| NBA             |    489 |   1453 |    954 |
| NCAAB           |      0 |   3110 |   3760 |
| NCAAF           |    263 |    818 |   1198 |
| NFL             |    304 |    334 |    225 |
| NHL             |    190 |   1457 |   1026 |
| Serie A         |      0 |    494 |    887 |
| UCL             |    279 |    432 |    680 |
| US politics     |   1234 |   1339 |   8495 |
| Valorant        |      0 |     95 |   2032 |
| WNBA            |      0 |    311 |    361 |
| WTA             |      0 |    435 |   5121 |
| boxing          |     31 |     69 |     84 |
| cricket         |      0 |    203 |   1753 |
| crypto          |    372 |   2343 |   1567 |
| culture/awards  |    318 |   2763 |   6906 |
| economics/Fed   |    175 |   2566 |   8273 |
| esports other   |     37 |    790 |   1884 |
| geopolitics     |    164 |   2069 |   2970 |
| golf            |     53 |    870 |   2376 |
| other soccer    |    424 |   7045 |  27936 |
| other tennis    |     17 |    470 |  13679 |
| tech/companies  |    123 |    654 |   2740 |
| weather         |     42 |    183 |    953 |
| world elections |    241 |    326 |   2765 |

## Caveats

- **Selection bias.** Groups are chosen *after* seeing these results (~30 groups). Even with Holm, the chosen set's backtest ROI is biased upward; the forward paper test is the verdict, not this table.
- CLOB history price is an hourly mid/last, not an executable ask. The +1¢ spread is a flat assumption; thin markets (esports, small soccer leagues, challengers) often have wider books, which the forward rule's spread ≤ 0.05 / ask-within-0.05 filter will partly reject.
- The fee schedule is applied retroactively (most of 2024–25 had no taker fees) so the ROI is what the rule would earn under today's fees.
- Only markets Gamma still lists with a 1/0 settlement are seen (survivorship); voids are excluded rather than counted as 0 return. Tag coverage of 2024 is thin (Polymarket added per-game markets and sport tags mostly in 2025), so most of the evidence is 2025–26.
- Multi-leg events (golf/F1 winners, elections, awards) mean many correlated bets per event; clustering by event handles that in the CI, but the number of independent outcomes is the cluster count, not the bet count.
- Non-sports decision uses the endDate Gamma shows now; markets whose end date was extended or edited after creation are timed from the final date (a mild lookahead the forward test does not have).
- Bets/yr for multi-leg groups (US politics, elections, culture, golf, F1) counts every leg; the number of independent outcomes per year is closer to the cluster share of that figure.
- Bets/yr counts every in-range favourite at one decision time; the forward scripts poll repeatedly and enter at the first in-range observation, so live entry counts and prices will differ.
