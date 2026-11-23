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