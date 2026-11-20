# Kalshi maker simulation: resting quotes around a fair value

Generated 2026-11-20 02:59 by [maker_sim.py](../maker_sim.py). Paper study only: no orders, no accounts.

## Pre-registration (written 2026-11-20 before any simulation result; one parameter set, not changed after)

Question: can a retail trader profit as a **maker** on Kalshi (resting quotes around a fair value), and does a
fair-value edge help?

- **Sample** (deterministic: within each stratum, markets ordered by sha1(ticker); resolved yes/no; total volume ≥ 1,000
  contracts; resolution 2024-01-01 → 2026-11-19):
  sports game winners KXNFLGAME/KXNBAGAME/KXMLBGAME/KXNHLGAME, one market per game (lowest hash), 100 games per league;
  daily high temperature KXHIGH{NY,CHI,MIA,AUS,LAX,DEN,PHIL} (market list from weather_study's cache), 100 brackets per city;
  economics KXCPI/KXFED/KXPAYROLLS (incl. legacy CPI-/FED- tickers listed under them), 150 markets per series.
  Extra Pinnacle sample: NFL/MLB games resolving 2026-09-10 → 2026-11-19 that match a Pinnacle game in the snapshot DB,
  60 per league (union with the main sample; reported only as a paired baseline-vs-Pinnacle comparison).
- **Resolution time T**: sports = scheduled start = expected_expiration_time − 3h; weather and econ = close_time
  (econ markets close ~5 min before the 8:30 ET release / 2:00 pm ET Fed decision).
- **Quoting window**: [max(open, T − 48h), min(T − 15 min, close)]. Quotes refreshed every 5 minutes on a fixed grid.
- **Fair value** at refresh time t (data strictly at or before t):
  (1) baseline: the market's own mid, from the last 1-minute candle closed at or before t
      ((yes_bid + yes_ask)/2 when both sides exist and spread ≤ 10¢, else last trade);
  (2a) weather informed: weather_study's model, P(bracket) with high = latest NBM-text (else GFS MOS) forecast available
      at t (run + 2h / + 4h) + error drawn from that city's errors on D−365…D−2 (D−1 15:00 errors before the event day,
      D 08:00 errors on it), Gaussian kernel h = 1°F, ≥ 60 errors;
  (2b) sports informed: Pinnacle moneyline, multiplicative de-vig, latest snapshot at or before t, no older than 12 h
      (else no quote). Other informed sources: none available with timestamped history → skipped.
- **Quotes**: bid = fair − h − skew, ask = fair + h − skew, rounded away from fair to the 1¢ tick; h = 2¢ (primary),
  1¢ and 3¢ (sensitivity); skew = 0.5¢ per 10 contracts of YES inventory; 10 contracts per side; inventory capped at
  ±50 (side size shrinks so the cap cannot be breached); post-only (a side that would cross the last candle's
  opposite best quote is not posted); no quote below 1¢ or above 99¢.
- **Fill model** (conservative): a resting bid fills only on a later public trade printed STRICTLY below the bid
  (strictly above for an ask), at most 0.5 × the printed size, until the order's 10 contracts are used up; trades at the
  quote's own timestamp never fill it. Fill price = our quote.
- **Fees**: series with Kalshi fee_type `quadratic_with_maker_fees` pay a maker fee ceil(0.0175 × multiplier × C × P(1−P))
  per order (one order = one side of one 5-min quote); other series pay no maker fee. Current fee type applied to all
  history. Taker fee 0.07 × multiplier × P(1−P) shown for comparison.
- **Score**: hold to settlement. P&L per market ($) and ROI = Σ P&L / Σ capital, capital per market = the largest
  collateral the inventory ever needed (long: contracts × average YES cost; short: contracts × (1 − average sale price)).
  Decomposition per fill: spread earned = side × (mid at fill − price); adverse selection = side × (mid at +5 min / +60 min /
  settlement − mid at fill). Fill rate = filled / posted contracts.
- **Statistics**: 95% CI by resampling resolution days (B = 2000). Chronological halves; holdout = last 30% of each
  category's markets by T. **Pass** (per category and fair value, h = 2¢ only): ROI > 0 with CI lower bound > 0, ROI > 0
  in both halves and in the holdout. h = 1¢/3¢ never decide a pass.

## Data coverage

| category | sub | markets sampled | with data | first T | last T | trades fetched | page cap hit | maker-fee series |
|---|---|---|---|---|---|---|---|---|
| econ | CPI | 150 | 150 | 2024-02-13 | 2026-11-10 | 16,020 | 0 | yes (×1) |
| econ | FED | 150 | 150 | 2024-01-31 | 2026-10-28 | 4,900 | 0 | yes (×1) |
| econ | JOBS | 150 | 150 | 2024-01-05 | 2026-11-06 | 18,534 | 0 | yes (×1) |
| sports | MLB | 155 | 155 | 2025-04-24 | 2026-10-29 | 281,879 | 0 | yes (×0.5) |
| sports | NBA | 100 | 100 | 2025-04-18 | 2026-11-17 | 291,511 | 0 | yes (×1) |
| sports | NFL | 131 | 131 | 2025-08-08 | 2026-11-17 | 1,557,297 | 1 | yes (×1) |
| sports | NHL | 100 | 100 | 2025-04-23 | 2026-11-15 | 57,323 | 0 | yes (×1) |
| weather | AUS | 100 | 100 | 2024-01-04 | 2026-11-09 | 43,786 | 0 | no (×0) |
| weather | CHI | 100 | 100 | 2024-02-03 | 2026-11-19 | 55,319 | 0 | no (×0) |
| weather | DEN | 100 | 100 | 2024-11-24 | 2026-11-19 | 48,200 | 0 | no (×0) |
| weather | LAX | 100 | 100 | 2025-01-13 | 2026-10-29 | 115,632 | 0 | no (×0) |
| weather | MIA | 100 | 100 | 2024-01-15 | 2026-11-12 | 61,308 | 0 | no (×0) |
| weather | NY | 100 | 100 | 2024-01-20 | 2026-11-18 | 79,756 | 0 | no (×0) |
| weather | PHIL | 100 | 100 | 2024-11-21 | 2026-11-12 | 32,804 | 0 | no (×0) |

Pinnacle-matched games (extra sample, NFL/MLB 2026-09-10 → 11-19): 120. Kalshi trade prints are taker executions (price, size, time); there is no historical order book, so queue position and hidden size are unknown — the 0.5 queue share and the strict trade-through rule stand in for them.

## Results, h = 2¢ (primary), main sample

### Baseline fair value = the market's own mid (no edge)

| category | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 1550 | 989 | 1.6% | 195,566 | -1,968 | -1.27 | 15,668 | -12.6% | [-16.1%, -9.0%] | -15.9% | -8.8% | -11.0% | fail |
| econ | 450 | 173 | 0.5% | 14,707 | +169 | +0.38 | 1,580 | +10.7% | [-4.0%, +26.6%] | +8.6% | +12.5% | +15.1% | fail |
| sports | 400 | 160 | 0.2% | 8,201 | -140 | -0.35 | 1,340 | -10.4% | [-20.7%, -0.1%] | -7.5% | -13.7% | -12.4% | fail |
| weather | 700 | 656 | 3.3% | 172,657 | -1,997 | -2.85 | 12,749 | -15.7% | [-19.4%, -12.0%] | -19.4% | -11.6% | -14.9% | fail |

| category / sub | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| econ / CPI | 150 | 65 | 0.5% | 5,585 | -14 | -0.09 | 694 | -2.0% | [-16.0%, +12.3%] | +0.2% | -4.5% | -12.5% | fail |
| econ / FED | 150 | 5 | 0.0% | 52 | +2 | +0.01 | 37 | +5.3% | [—, —] | +4.6% | +5.9% | -119.7% | fail |
| econ / JOBS | 150 | 103 | 0.6% | 9,071 | +181 | +1.21 | 849 | +21.3% | [-2.0%, +46.7%] | +17.9% | +24.2% | +33.0% | fail |
| sports / MLB | 100 | 22 | 0.1% | 371 | -29 | -0.29 | 129 | -22.4% | [-59.4%, +27.0%] | -80.5% | -1.2% | +36.9% | fail |
| sports / NBA | 100 | 74 | 0.4% | 3,899 | -86 | -0.86 | 733 | -11.7% | [-25.6%, +1.5%] | -5.3% | -22.0% | -25.7% | fail |
| sports / NFL | 100 | 15 | 0.3% | 3,096 | -28 | -0.28 | 187 | -15.2% | [-31.5%, -0.3%] | -31.6% | -11.9% | -10.8% | fail |
| sports / NHL | 100 | 49 | 0.1% | 836 | +4 | +0.04 | 290 | +1.3% | [-25.3%, +30.8%] | +2.9% | -3.6% | -6.0% | fail |
| weather / AUS | 100 | 99 | 3.1% | 23,870 | -265 | -2.65 | 1,914 | -13.8% | [-23.9%, -3.1%] | -20.0% | -8.7% | -8.9% | fail |
| weather / CHI | 100 | 95 | 3.2% | 23,889 | -187 | -1.87 | 1,924 | -9.7% | [-17.9%, -0.9%] | -3.7% | -16.3% | -27.2% | fail |
| weather / DEN | 100 | 96 | 2.9% | 22,532 | -387 | -3.87 | 1,755 | -22.1% | [-31.9%, -12.9%] | -20.0% | -24.4% | -31.6% | fail |
| weather / LAX | 100 | 92 | 3.8% | 27,921 | -244 | -2.44 | 1,868 | -13.1% | [-22.7%, -3.8%] | -13.9% | -12.2% | -12.4% | fail |
| weather / MIA | 100 | 91 | 3.3% | 22,766 | -186 | -1.86 | 1,768 | -10.5% | [-20.5%, -1.4%] | -17.6% | -2.4% | -7.5% | fail |
| weather / NY | 100 | 85 | 4.4% | 31,306 | -333 | -3.33 | 1,699 | -19.6% | [-30.4%, -9.0%] | -30.4% | -9.9% | -14.7% | fail |
| weather / PHIL | 100 | 98 | 2.7% | 20,374 | -395 | -3.95 | 1,820 | -21.7% | [-31.3%, -11.9%] | -29.2% | -13.7% | -15.2% | fail |

### Informed fair value (weather: NWS forecast model)

| category | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sports | 34 | 1 | 0.0% | 10 | -3 | -0.10 | 3 | -101.2% | [—, —] | — | -101.2% | -101.2% | fail |
| weather | 700 | 622 | 1.2% | 46,706 | -668 | -0.95 | 10,683 | -6.3% | [-11.6%, -1.1%] | -12.4% | +0.5% | -3.8% | fail |

| category / sub | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sports / MLB | 5 | 0 | 0.0% | 0 | +0 | +0.00 | 0 | — | [—, —] | — | — | — | fail |
| sports / NFL | 29 | 1 | 0.0% | 10 | -3 | -0.12 | 3 | -101.2% | [—, —] | — | -101.2% | -101.2% | fail |
| weather / AUS | 100 | 93 | 1.3% | 7,553 | +24 | +0.24 | 1,687 | +1.4% | [-11.0%, +13.6%] | +1.8% | +1.1% | +14.5% | fail |
| weather / CHI | 100 | 92 | 1.2% | 6,752 | +29 | +0.29 | 1,618 | +1.8% | [-8.2%, +11.4%] | +0.7% | +3.0% | -10.0% | fail |
| weather / DEN | 100 | 90 | 1.1% | 6,374 | -77 | -0.77 | 1,618 | -4.8% | [-16.1%, +5.8%] | -8.8% | -1.3% | -7.1% | fail |
| weather / LAX | 100 | 84 | 1.2% | 6,423 | -116 | -1.16 | 1,352 | -8.6% | [-24.8%, +7.2%] | -8.9% | -8.2% | -27.7% | fail |
| weather / MIA | 100 | 85 | 1.3% | 7,091 | +13 | +0.13 | 1,559 | +0.8% | [-9.9%, +11.3%] | +0.8% | +0.8% | +7.0% | fail |
| weather / NY | 100 | 83 | 1.3% | 7,060 | -399 | -3.99 | 1,411 | -28.3% | [-46.3%, -9.8%] | -52.5% | -4.4% | -19.6% | fail |
| weather / PHIL | 100 | 95 | 1.0% | 5,453 | -141 | -1.41 | 1,437 | -9.8% | [-22.2%, +1.4%] | -17.5% | -0.6% | +8.7% | fail |

### Sports: baseline vs Pinnacle on the same games (Pinnacle-matched sample, 2026-09-10 → 11-19)

| league / fair | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLB / baseline | 60 | 15 | 0.0% | 258 | +33 | +0.56 | 72 | +46.0% | [-6.7%, +94.9%] | +14.7% | +62.9% | +32.2% | fail |
| MLB / informed | 60 | 2 | 0.0% | 20 | -7 | -0.12 | 7 | -100.7% | [—, —] | -100.7% | — | — | fail |
| NFL / baseline | 60 | 0 | 0.0% | 0 | +0 | +0.00 | 0 | — | [—, —] | — | — | — | fail |
| NFL / informed | 60 | 2 | 0.0% | 20 | -7 | -0.12 | 7 | -101.3% | [—, —] | — | -101.3% | -101.3% | fail |

## Adverse-selection decomposition (h = 2¢; ¢ per filled contract)

Spread earned = distance of the fill from the mid at fill time; AS = how far the mid then moves against the fill (negative = adverse). Net = spread + AS settlement − fee.

| category / fair | contracts | spread earned ¢/ct | AS +5 min ¢/ct | AS +60 min ¢/ct | AS settlement ¢/ct | maker fee ¢/ct | net ¢/ct | taker fee would be ¢/ct |
|---|---|---|---|---|---|---|---|---|
| all / baseline | 195,814 | +1.77 | -3.12 | -2.73 | -2.71 | -0.05 | -0.99 | 1.23 |
| all / informed | 46,746 | +1.36 | -4.00 | -3.06 | -2.82 | -0.00 | -1.46 | 1.11 |
| econ / baseline | 14,707 | +1.87 | -2.14 | -1.81 | -0.30 | -0.42 | +1.15 | 1.40 |
| sports / baseline | 8,450 | +1.85 | -1.99 | -1.96 | -2.72 | -0.44 | -1.30 | 1.44 |
| sports / informed | 40 | +0.25 | -1.00 | -7.00 | -35.75 | -0.35 | -35.85 | 1.20 |
| weather / baseline | 172,657 | +1.76 | -3.26 | -2.84 | -2.92 | -0.00 | -1.16 | 1.20 |
| weather / informed | 46,706 | +1.36 | -4.00 | -3.05 | -2.79 | -0.00 | -1.43 | 1.11 |

| category / sub / fair | contracts | spread earned ¢/ct | AS +5 min ¢/ct | AS +60 min ¢/ct | AS settlement ¢/ct | maker fee ¢/ct | net ¢/ct | taker fee would be ¢/ct |
|---|---|---|---|---|---|---|---|---|
| econ / CPI / baseline | 5,585 | +1.86 | -2.00 | -1.51 | -1.72 | -0.39 | -0.25 | 1.28 |
| econ / FED / baseline | 52 | +2.02 | -1.81 | -1.23 | +1.95 | -0.17 | +3.79 | 0.46 |
| econ / JOBS / baseline | 9,071 | +1.88 | -2.23 | -2.00 | +0.56 | -0.44 | +2.00 | 1.48 |
| sports / MLB / baseline | 619 | +1.79 | -1.32 | -1.54 | -1.39 | -0.30 | +0.10 | 0.85 |
| sports / MLB / informed | 20 | +0.50 | -1.00 | -1.00 | -36.50 | -0.25 | -36.25 | 0.81 |
| sports / NBA / baseline | 3,899 | +1.68 | -1.85 | -1.72 | -3.42 | -0.47 | -2.20 | 1.53 |
| sports / NFL / baseline | 3,096 | +2.09 | -2.53 | -2.51 | -2.61 | -0.40 | -0.92 | 1.38 |
| sports / NFL / informed | 20 | +0.00 | -1.00 | -13.00 | -35.00 | -0.45 | -35.45 | 1.59 |
| sports / NHL / baseline | 836 | +1.85 | -1.18 | -1.33 | -0.89 | -0.52 | +0.44 | 1.68 |
| weather / AUS / baseline | 23,870 | +1.92 | -3.50 | -2.97 | -3.03 | -0.00 | -1.11 | 1.17 |
| weather / AUS / informed | 7,553 | +1.62 | -4.09 | -2.76 | -1.30 | -0.00 | +0.32 | 1.15 |
| weather / CHI / baseline | 23,889 | +1.62 | -3.07 | -2.78 | -2.41 | -0.00 | -0.78 | 1.20 |
| weather / CHI / informed | 6,752 | +0.53 | -4.12 | -2.89 | -0.10 | -0.00 | +0.43 | 1.12 |
| weather / DEN / baseline | 22,532 | +1.78 | -3.36 | -3.29 | -3.50 | -0.00 | -1.72 | 1.18 |
| weather / DEN / informed | 6,374 | +1.68 | -4.18 | -3.86 | -2.89 | -0.00 | -1.21 | 1.05 |
| weather / LAX / baseline | 27,921 | +1.76 | -3.05 | -2.67 | -2.63 | -0.00 | -0.87 | 1.19 |
| weather / LAX / informed | 6,423 | +1.59 | -3.48 | -2.62 | -3.40 | -0.00 | -1.81 | 1.04 |
| weather / MIA / baseline | 22,766 | +1.71 | -3.21 | -2.52 | -2.52 | -0.00 | -0.82 | 1.25 |
| weather / MIA / informed | 7,090 | +1.43 | -3.86 | -2.23 | -1.25 | -0.00 | +0.18 | 1.26 |
| weather / NY / baseline | 31,306 | +1.79 | -2.88 | -2.46 | -2.85 | -0.00 | -1.06 | 1.21 |
| weather / NY / informed | 7,060 | +1.71 | -3.74 | -3.15 | -7.36 | -0.00 | -5.66 | 1.13 |
| weather / PHIL / baseline | 20,374 | +1.76 | -4.04 | -3.44 | -3.69 | -0.00 | -1.94 | 1.19 |
| weather / PHIL / informed | 5,453 | +0.86 | -4.65 | -4.16 | -3.44 | -0.00 | -2.58 | 1.01 |

## Sensitivity: half-spread h (labelled sensitivity only, never decides a pass)

| category / fair / h | markets | with fills | fill rate | contracts filled | P&L $ | $/market | capital $ | ROI | 95% CI | half 1 | half 2 | holdout | pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all / baseline / 0.01 | 1550 | 1146 | 2.2% | 270,704 | -3,208 | -2.07 | 19,850 | -16.2% | [-19.5%, -12.6%] | -17.6% | -14.5% | -16.8% | fail |
| all / baseline / 0.02 | 1550 | 989 | 1.6% | 195,566 | -1,968 | -1.27 | 15,668 | -12.6% | [-16.1%, -9.0%] | -15.9% | -8.8% | -11.0% | fail |
| all / baseline / 0.03 | 1550 | 886 | 1.1% | 137,821 | -1,455 | -0.94 | 13,026 | -11.2% | [-14.9%, -7.5%] | -17.7% | -3.9% | -7.3% | fail |
| all / informed / 0.01 | 734 | 643 | 1.2% | 48,928 | -728 | -0.99 | 10,558 | -6.9% | [-11.6%, -2.1%] | -11.4% | -1.4% | -2.7% | fail |
| all / informed / 0.02 | 734 | 623 | 1.2% | 46,716 | -671 | -0.91 | 10,686 | -6.3% | [-11.3%, -1.1%] | -11.5% | -0.2% | -1.3% | fail |
| all / informed / 0.03 | 734 | 624 | 1.1% | 43,892 | -615 | -0.84 | 10,817 | -5.7% | [-10.6%, -0.3%] | -10.7% | +0.5% | +1.1% | fail |
| econ / baseline / 0.01 | 450 | 218 | 0.9% | 28,405 | +109 | +0.24 | 2,387 | +4.5% | [-9.4%, +19.0%] | +5.9% | +3.2% | +2.7% | fail |
| econ / baseline / 0.02 | 450 | 173 | 0.5% | 14,707 | +169 | +0.38 | 1,580 | +10.7% | [-4.0%, +26.6%] | +8.6% | +12.5% | +15.1% | fail |
| econ / baseline / 0.03 | 450 | 134 | 0.3% | 7,949 | +135 | +0.30 | 1,087 | +12.4% | [-2.0%, +28.8%] | -3.3% | +24.3% | +33.9% | fail |
| sports / baseline / 0.01 | 400 | 252 | 0.4% | 15,439 | -145 | -0.36 | 2,262 | -6.4% | [-15.2%, +1.7%] | -2.4% | -10.6% | -12.9% | fail |
| sports / baseline / 0.02 | 400 | 160 | 0.2% | 8,201 | -140 | -0.35 | 1,340 | -10.4% | [-20.7%, -0.1%] | -7.5% | -13.7% | -12.4% | fail |
| sports / baseline / 0.03 | 400 | 121 | 0.1% | 5,241 | -66 | -0.16 | 878 | -7.5% | [-20.7%, +5.7%] | -7.6% | -7.4% | -9.9% | fail |
| sports / informed / 0.01 | 34 | 6 | 0.0% | 57 | -14 | -0.40 | 23 | -58.3% | [—, —] | +46.2% | -101.0% | -101.0% | fail |
| sports / informed / 0.02 | 34 | 1 | 0.0% | 10 | -3 | -0.10 | 3 | -101.2% | [—, —] | — | -101.2% | -101.2% | fail |
| sports / informed / 0.03 | 34 | 0 | 0.0% | 0 | +0 | +0.00 | 0 | — | [—, —] | — | — | — | fail |
| weather / baseline / 0.01 | 700 | 676 | 4.5% | 226,860 | -3,171 | -4.53 | 15,200 | -20.9% | [-24.5%, -17.4%] | -22.8% | -18.8% | -21.8% | fail |
| weather / baseline / 0.02 | 700 | 656 | 3.3% | 172,657 | -1,997 | -2.85 | 12,749 | -15.7% | [-19.4%, -12.0%] | -19.4% | -11.6% | -14.9% | fail |
| weather / baseline / 0.03 | 700 | 631 | 2.4% | 124,631 | -1,524 | -2.18 | 11,060 | -13.8% | [-17.6%, -9.9%] | -20.5% | -6.8% | -10.6% | fail |
| weather / informed / 0.01 | 700 | 637 | 1.3% | 48,871 | -714 | -1.02 | 10,534 | -6.8% | [-12.1%, -2.2%] | -12.2% | -0.5% | -4.1% | fail |
| weather / informed / 0.02 | 700 | 622 | 1.2% | 46,706 | -668 | -0.95 | 10,683 | -6.3% | [-11.6%, -1.1%] | -12.4% | +0.5% | -3.8% | fail |
| weather / informed / 0.03 | 700 | 624 | 1.1% | 43,892 | -615 | -0.88 | 10,817 | -5.7% | [-10.9%, -0.4%] | -11.7% | +1.2% | -3.8% | fail |

| category / fair / h | contracts | spread earned ¢/ct | AS +5 min ¢/ct | AS +60 min ¢/ct | AS settlement ¢/ct | maker fee ¢/ct | net ¢/ct | taker fee would be ¢/ct |
|---|---|---|---|---|---|---|---|---|
| all / baseline / 0.01 | 270,704 | +0.97 | -2.23 | -2.05 | -2.09 | -0.07 | -1.18 | 1.18 |
| all / baseline / 0.02 | 195,566 | +1.78 | -3.13 | -2.73 | -2.73 | -0.05 | -1.01 | 1.23 |
| all / baseline / 0.03 | 137,821 | +2.53 | -4.14 | -3.51 | -3.54 | -0.04 | -1.06 | 1.25 |
| all / informed / 0.01 | 48,928 | +1.23 | -3.89 | -2.95 | -2.72 | -0.00 | -1.49 | 1.09 |
| all / informed / 0.02 | 46,716 | +1.36 | -4.00 | -3.05 | -2.80 | -0.00 | -1.44 | 1.11 |
| all / informed / 0.03 | 43,892 | +1.48 | -4.14 | -3.37 | -2.88 | -0.00 | -1.40 | 1.13 |
| econ / baseline / 0.01 | 28,405 | +1.08 | -1.29 | -1.22 | -0.29 | -0.41 | +0.38 | 1.34 |
| econ / baseline / 0.02 | 14,707 | +1.87 | -2.14 | -1.81 | -0.30 | -0.42 | +1.15 | 1.40 |
| econ / baseline / 0.03 | 7,949 | +2.62 | -3.34 | -2.51 | -0.50 | -0.43 | +1.70 | 1.43 |
| sports / baseline / 0.01 | 15,439 | +1.02 | -1.14 | -1.22 | -1.52 | -0.44 | -0.94 | 1.44 |
| sports / baseline / 0.02 | 8,201 | +1.87 | -2.01 | -1.98 | -3.13 | -0.44 | -1.70 | 1.46 |
| sports / baseline / 0.03 | 5,241 | +2.57 | -2.95 | -2.57 | -3.38 | -0.44 | -1.25 | 1.47 |
| sports / informed / 0.01 | 57 | +0.46 | -0.87 | -1.13 | -23.93 | -0.40 | -23.88 | 1.38 |
| sports / informed / 0.02 | 10 | +0.50 | -1.00 | -13.00 | -34.50 | -0.40 | -34.40 | 1.57 |
| weather / baseline / 0.01 | 226,860 | +0.96 | -2.43 | -2.21 | -2.36 | -0.00 | -1.40 | 1.15 |
| weather / baseline / 0.02 | 172,657 | +1.76 | -3.26 | -2.84 | -2.92 | -0.00 | -1.16 | 1.20 |
| weather / baseline / 0.03 | 124,631 | +2.52 | -4.24 | -3.61 | -3.74 | -0.00 | -1.22 | 1.23 |
| weather / informed / 0.01 | 48,871 | +1.23 | -3.90 | -2.95 | -2.69 | -0.00 | -1.46 | 1.09 |
| weather / informed / 0.02 | 46,706 | +1.36 | -4.00 | -3.05 | -2.79 | -0.00 | -1.43 | 1.11 |
| weather / informed / 0.03 | 43,892 | +1.48 | -4.14 | -3.37 | -2.88 | -0.00 | -1.40 | 1.13 |
## Verdict (written after the results above; not part of the generated tables)

- **No category passes** the pre-registered bar at h = 2¢, with either fair value.
- **Adverse selection eats the spread everywhere.** Under the trade-through fill rule a fill earns about +1.8¢ against the
  mid, then the mid moves about 2–3¢ against it within 5 minutes and stays there through settlement. Quoting wider does
  not help: at 1¢, 2¢ and 3¢ the spread earned grows, but the adverse move grows just as much, and net stays at about
  −1¢ per contract overall. These are mostly toxic fills: the print only goes through your quote once the market has
  already repriced.
- **Weather (no maker fee)** loses about 16% on capital with the market's mid as fair value, worst in every city.
  Quoting around the NWS-forecast model loses less (−6.3%, CI [−11.6%, −1.1%]) and is about flat in AUS, CHI and MIA.
  But it is still negative overall and loses badly in NY. The forecast model does not know the observed temperature on
  the event day, and the market does.
- **Economics** is the only positive cell: +10.7%, CI [−4%, +27%], positive in both halves and the holdout, driven by
  payrolls (+21%). It fails the CI bar, on only ~$1.6k of capital and 0.5% fill rate. Treat it as a hypothesis for
  forward paper testing, not a result.
- **Sports** (maker fee 0.0175, MLB ×0.5) loses about 10%. Quoting around a Pinnacle line up to 12 h old barely fills:
  post-only blocks the side that would cross, and the side that does fill is the stale one, at about −35¢ per contract.
  Snapshots roughly twice a day are not a usable fair value for a maker.
- Caveats: sports history exists only from 2025. Today's maker-fee designation is applied to all history. There is no
  order-book history, so queue position is modelled, not observed. The fill rule is conservative on how often you fill
  but realistic about which fills you get.
