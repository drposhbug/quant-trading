# Ideas for the network lab (2026-11-23)

Asked of Astra 6.2 and Grok: what should the network learn from, how should it be trained, what should it check after each mistake, and how could the loop fool itself. Opinions, not evidence. The lab's rules are in mlp_odds.py.

Constraint the loop adds: a change must run on GitHub from prices Yahoo serves, so Astra's first idea (train on point-in-time S&P 500 peers) needs that membership data committed first and is parked.

---

# Astra 6.2

## 1. Inputs, target and training data

These are subjective probabilities that each change, tried alone, improves the current network’s expected out-of-sample rank IC on the end-2014 list. A higher IC can still produce a worse tilt.

| Rank | Change | Probability | Definition and rationale |
|---|---|---:|---|
| 1 | Train on comparable stocks | 45% | Each date, select the 30 point-in-time S&P 500 members with the highest trailing 252-session correlation to QQQ. Compute features and relative-return labels within that group. At inference, rank within the actual book. This supplies more examples of leadership changing hands without selecting today’s winners. |
| 2 | Learn return ranks | 40% | Replace each daily target with `(midrank − 1)/(N − 1) − 0.5`, ranking forward returns ascending. Keep squared loss. One stock doubling then counts as one first-place finish, which matches the decision more closely. |
| 3 | Add the live score | 35% | Feed the network the daily cross-sectional z-score of the exact composite used by the live tilt, before bucketing. The network currently has to reconstruct the skipped-month trend from separately standardized inputs. Skipping the latest month also has an established empirical precedent. [Kenneth French’s momentum definition](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library/det_mom_factor.html) |
| 4 | Add QQQ-adjusted intermediate momentum | 25% | For each session compute stock log return minus QQQ log return times the stock’s preceding 60-session beta. Sum over sessions \(t-125\) through \(t-21\), divide by their residual standard deviation, then z-score across names. This can distinguish persistent stock leadership from a high-beta rally. |

I’d skip additional VIX and rate transforms, candlesticks, presidential-post sentiment, prediction odds and deeper networks. The project’s prior tests give little reason to spend another pass on them.

## 2. Training design

**Try the broader training universe first.** Six development years contain roughly 72 nonoverlapping monthly outcomes. Additional peers provide more within-month comparisons, though they add no independent market regimes. Keep the evaluation book fixed and retain exits in training labels. For every pass, split early stopping on whole dates and purge training labels that reach validation. At 15:30 ET, yesterday’s close is the latest completed daily bar available for features and matured labels.

## 3. Learning from mistakes

- **Disagreements with trend.** On pairs the models order differently, measure how often the network picks the winner. Persistent losses favor shrinking its score toward trend.
- **Portfolio attribution.** Sum each name’s daily weight difference versus live times its subsequent return. Separate promotions, demotions and turnover costs. If rank gains disappear at bucket boundaries, test a buffer there.
- **Beta exposure.** In the worst months, split active return into lagged-beta exposure times QQQ return and the residual. Repeated beta-driven misses motivate the QQQ-adjusted feature.
- **Dependence on names and dates.** Recompute the IC gain leaving out each stock and each development year. If one omission erases it, discard the change.

## 4. Guardrails

Monthly verdicts can turn the lockbox into another development set, even through pass/fail feedback. **Allow one historical lockbox verdict for one frozen finalist.** Subsequent challengers earn evidence on newly arriving paper trades. The existing full-window report already gives partial information about 2022 onward.

## 5. Honest prior

**25%** that the development-selected finalist achieves higher lockbox CAGR than live on the end-2014 list. That judgment uses your reported results. The negative IC on the deciding list weighs more heavily than the favorable hindsight basket. I’d keep the live tilt and log the challenger’s timestamped disagreements until prospective returns justify switching.
---

# Grok

## 1. Inputs, target and training data

P(real month-ahead rank value) on 10–12 megacap tech names. ~1,150 tests left only slow trend. Mean rank-IC SE for 2016–2021 is ~0.04.

1. **0.18 — PIT universe.** Every point-in-time S&P 500 name that day with ≥252 sessions. Target: next-21-session return minus that day’s equal-weight mean. Same feature formulas. Score on the book. Reason: ~250 weights need more than twelve names.

2. **0.14 — Overnight residual momentum.** Sum of log(open / prior close) over t−126…t−21 and t−63…t−21, minus β̂ times the same QQQ sum, divided by 60-session vol, z-scored in the book. β̂ is the slope of 60 daily close-to-close returns on QQQ. Reason: the drift that survived is overnight.

3. **0.12 — Skip-month residual momentum.** (Return from t−252 to t−21) minus β̂ times QQQ over that window, divided by the std of residuals from that 60-day fit, z-scored. Replaces raw 126- and 252-session returns. Reason: the live signal with the market leg removed. Similar betas cap the gain.

4. **0.11 — Rank target.** Percentile of next-21 relative return inside the training universe that day; squared error on the percentile. Reason: the tilt only uses thirds, and dollar errors are single-name spikes.

5. **0.08 — Orthogonal target.** Next-21 relative return minus a past-only, same-day cross-sectional fit on the live trend score. Keep only if residual rank IC > 0. Reason: the rest mostly reprints the tilt.

6. **0.07 — Earnings residual.** If an earnings date is in the last 63 sessions: (close two sessions after / close the session before − 1) / 60-day vol × exp(−days/63); else 0. Reason: one dated shock on a one-month clock.

7. **0.05 — Dollar volume.** log(21-day mean of close×volume) − log(252-day mean), z-scored. Reason: participation beside price.

8. **0.05 — Idio vol.** Std of residuals from the 60-day QQQ regression, z-scored, low scored high. Reason: the vol input you have still contains QQQ.

**Skip:** macro, ^IRX, VIX level, prediction-market odds, presidential posts, candlesticks, RSI, 1–5 session reversal, extra layers, LSTMs. Shared factors and already-null families. Twelve names, one beta.

## 2. Training design

Do item 1 first. Keep 16 tanh units, the 21-session refit, and 3 seeds. The hidden layer is variance; the rows are the fix. Fit a linear item-3 score on the same PIT rows. If its 2016–2021 rank IC on the book matches the net, ship the linear score.

## 3. Learning from mistakes

Development years only:

1. **Halves and names.** Rank IC in 2016–2018, in 2019–2021, and after dropping each name. A miss on a half or a name → revert.
2. **Trend clone.** Corr(forecast, live score), and rank IC after a same-day regression on that score. Corr > ~0.7 and residual IC ≤ 0 → drop raw 63/126/252 returns.
3. **Disagreement.** Rank IC in months the forecast’s thirds differ from the trend’s. ≤ 0 → revert.
4. **Sides and turnover.** Hit rate of each predicted third, and membership turnover. A weak side → move that multiplier toward 1×. Turnover up with flat IC → more L2, or 8 units.
5. **Permute the six worst months.** IC loss from the 5-session return or QQQ’s 21-session return → drop that input. Loss spread across inputs → revert.

## 4. Guardrails

The biggest leak is selecting every pass on the same 2016–2021 path, then handing the lockbox one survivor. +0.01 is ~0.3 SE. Overlapping 21-session labels make a daily bootstrap look tighter than ~72 months.

**Rule to add:** five passes, budget fixed now. A keep also needs rank IC up by ≥0.05 in 2016–2018 and by ≥0.05 in 2019–2021, on the end-2014 top 10, with residual-to-trend IC ≥ 0 in both halves. Keeps, stops, and the mistakes note use data through 2021 only.

## 5. Honest prior

**0.12.** On the end-2014 list, rank IC is −0.02 and the net leads in 7% of bootstraps. The 94% case is the hindsight twelve. The lockbox is one leadership path.

Keep the trend tilt. Use PIT membership, a no-trade band on the monthly score, and shrink the tilt toward inverse-vol when trend-score dispersion is small. One linear residual-momentum score, pre-registered, reported once, then frozen.
