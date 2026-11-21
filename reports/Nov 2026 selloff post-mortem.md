# Nov 2026 selloff post-mortem: the model did its job, the plumbing did not, and nothing predicted it

Written 2026-11-21. Sources: `reports/selloff_postmortem_results.md` (numbers, from `selloff_postmortem.py`), four
research notes in `research_notes/Nov 2026 selloff post-mortem/` (historian, predictability, return-seeker, sceptic),
and independent reviews by Astra 6.2 and Grok (`grok_astra_reviews.md` in the same folder; neither had web access).

## Summary

- QQQ fell 19.9% from its 6 October peak to 20 November, 5.7% of it on the last day. The frozen model's own backtest
  lost 15.9% over the same stretch; the 12 names held equally and fully invested lost 21.8%.
- Nobody predicted it with a rule that works in general, including us. The model does not forecast. It cut exposure
  from 94% to 40% on 5 November when QQQ fell through its 200-day average (with one whipsaw back up on 11–12
  November), which is why the last two sessions cost 3.4% (model) instead of 10.5% (the basket).
- The paper account lost 5.0%, not 3.4%. The 1.6-point gap is execution: the first orders were queued while the
  volatility target was still 25%, and Thursday's rebalance never ran. Both were fixed before this report. Two more
  plumbing faults were found and are fixed locally, not yet pushed.
- History says a recovery is the likely outcome and a long bear is the tail: after the eight comparable Nasdaq-100
  drops since 1985 the index was higher a year later six times. This model will recover more slowly than the index
  if the rebound is sharp. That is the price of the protection it gave on Friday.
- "Bigger gains" has no free version. Every lever that raises expected return in this research raises drawdown at
  least as much, except the three that are not trading: account type, savings, and not interfering.
- Recommendation: change nothing in the model, push the plumbing fixes, and take two candidate ideas to the scheduled
  review. All five independent reviewers reached the same first conclusion.

## What happened

The S&P 500 peaked on 6 October and fell for six weeks: −4.4% on 5 November, a one-week bounce, then seven straight
losses ending with −3.7% on 20 November (−11.6% from the peak). The damage was concentrated in AI and semiconductors:
Nvidia −14%, AMD −13%, Broadcom −12% on the last day, after a Reuters report that SEC staff are examining Nvidia's
accounting, the CEO's resignation on 12 November, a weak Anthropic listing, and Fed officials talking about rate
hikes. The VIX closed near 36. This model's universe is twelve names from exactly that part of the market.

## How the model behaved

| | 6 Oct – 20 Nov | 19–20 Nov (account live) |
|---|---|---|
| Equal-weight basket, fully invested | −21.8% | −10.5% |
| QQQ | −19.9% | −7.7% |
| Frozen model, backtest | −15.9% | −3.4% |
| Paper account | (not live) | −5.0% |

The model was 91–100% invested through October, because the trend was up and volatility was moderate. It took most of
the first leg down, including the 5 November fall at 94% invested. That day QQQ closed below its 200-day average and
the model cut to 40%. QQQ closed back above the average on 11 and 12 November, so the model went back up to 78%, and
was cut again to 39% on 13 November: one whipsaw, which is the known cost of this rule. Exposure was 34% by
20 November as volatility rose. A −15.9% drawdown is inside the backtest's range (worst: −22.5%).

The account's extra 1.6 points have two causes, both traced in the order history:

1. **Entry at the old volatility target.** The first orders were queued at 17:17 ET on 18 November, when the code
   still said 25%. The freeze at 20% was committed at 19:30. The account bought 46% instead of 38%.
2. **Thursday's rebalance never ran.** GitHub's scheduler fired no run during market hours on 19 November, so the 46%
   was carried into Friday. On Friday's moves that alone cost about 0.6% of equity. The monitor was rebuilt that
   night as one long-running job and ran on time on Friday.

## Could it have been predicted?

No, on the evidence. Each signal that looked meaningful afterwards fails on its record:

| Signal before the drop | Record |
|---|---|
| Fund-manager cash at 3.6% (BofA "sell signal") | Also fired in Dec 2024, Jul, Nov and Dec 2025, May and Jul 2026, before the October record high. Only evidence is BofA's own backtest. |
| AI-bubble warnings | Continuous all year. Research on price run-ups finds the peak comes on average about six months after a bubble is identifiable. |
| Bearish retail surveys (AAII bears above 50%) | Normally read as a buy signal. It failed here, as it did early in 1974, 2002, 2008 and 2022. |
| Low implied correlation ("no contagion priced") | The academic sign agrees with a warning, but at a horizon of quarters and with no tested trading rule. |
| Valuation and concentration | Explain about 4% of one-year returns. Useful over a decade, not a month. |
| Crash models, VIX term structure, credit spreads | No credible false-alarm rates; VIX and credit already failed 0 of 44 in this repo. |
| Break of the 200-day average | The one signal with a long record. The model already uses it, as risk control rather than forecast. |

Astra's point is the cleanest statement of the limit: the false-alarm rate of these warnings is unknown, because
nobody counts the alarms that were followed by rallies. The repo's own record (about 700 tests, 0 of 8 the day before
the drop) says the same.

## What would have done better, and what it costs

Hindsight on one episode. The right-hand columns are the whole backtest (2015–2026), which is what each choice costs
or earns in ordinary times.

| Variant | 6 Oct – 20 Nov | Full-sample CAGR | Full-sample worst drawdown |
|---|---|---|---|
| Frozen model | −15.9% | +22.9% | −22.5% |
| Volatility target 15% | −12.3% | +18.8% | −19.9% |
| Sell everything below the 200-day | −14.4% | +20.6% | −25.7% |
| No 200-day rule | −17.5% | +25.0% | −29.7% |
| Volatility target 25% | −17.3% | +25.7% | −26.7% |

Every variant that lost less in this episode earns less over the full sample, and the reverse. The Sharpe ratios are
all between 1.17 and 1.26. There is no setting that was simply better; there is a dial between return and drawdown,
and it was set at 20% three days ago. Changing it now, after a loss, is the mistake the change-control rules exist to
prevent.

What genuinely would have helped was not in the model: sizing the first orders at the frozen target and not missing
Thursday. That is worth 1.6 points and is already fixed.

## How the account recovers

- The account needs +5.3% to get back to $100,000. At 34% invested, that takes a basket gain of about 16%.
- Base rate (historian note): the Nasdaq-100 has closed about 20% below its high eight times since 1985. Twelve months
  later it was higher in six (median of all eight about +42%) and lower in two: 2000 (−53%, 15.6 years to a new high)
  and 2022 (−10%, 2.1 years). In four of the six recoveries the index first fell another 3 to 13 points.
- The model recovers more slowly than the index in a sharp rebound. Run on the index, the same engine made 33% against
  78% in the year after the 2020 trigger and 19% against 43% after 2025. After April 2000 it lost 15% against 53%.
- On the shipped names, the model was 31–39% invested at each of QQQ's five earlier 15% drops since 2015. Over the
  next three months it made about +6% in three of the four recoveries (+11% in 2025) while the fully invested basket
  made +15% to +38%; after the 2022 hit it lost 8% over the year against 17% for the basket. Even if markets calm at
  once, the volatility scale stays low until late February 2027, when 20 November leaves the 60-day window
  (`research_notes/Crash playbook and system ideas/reentry_design.md`).
- Nothing observable now separates the two families reliably. The best of a weak set is the central bank: all three
  long bears (2000, 2022, Japan 1990) had tightening after the first leg, and a December hike is about 91% priced.
  That is three cases and a classification made by hand, so it is a reason for humility, not a signal.
- The model re-risks by rule: full weight returns when QQQ closes back above its 200-day average (about 12% above
  Friday's close), and the volatility scale rises as the 60-day window calms.

The realistic path is therefore slow: months, not weeks, and a real chance of further loss first. The main risk to
the account is whipsaw (a sharp rally the model mostly misses, then another break).

## Fixes

| Fault | Effect | Status |
|---|---|---|
| First orders sized at 25% volatility target | 46% invested instead of 38% | One-off; cannot recur |
| GitHub scheduler missed 19 Nov | 46% carried into Friday, about −0.6% | Fixed 19 Nov (long-running job) |
| T-bill buy ignores skipped stock trims (`monitor.py` rebalance) | Stocks 39% vs 34% target, cash −$3.6k | **Fixed locally with a regression test; not pushed** |
| Drawdown alert anchored at $95,083, not $100,000 (`state.json`) | The −10% alert would fire at −14.4% | **Corrected locally; not pushed** |
| Trades under 1% of equity per name are skipped | Up to ~12 points of exposure error in the worst case | Open: shrinking the band moves live toward the backtest, but it is rebalance logic under change control. For the scheduled review. |
| `equity_log.csv` has one row | `track.py` cannot run until Monday; the first two sessions are not in the record | Self-heals; no action |
| Forced runs can trade with the market closed; no backup trigger late in the session; no stale-price or fill check | How the first orders came to fill at the open | Open, low urgency |

## Bigger gains

Honest forward expectation for this model is about 15% a year at a Sharpe ratio of 1.0 at best (the 23% backtest
includes names picked with hindsight; the same engine on the end-2014 list earned 15.3%, less than QQQ's 17.6%).
The menu, from the return-seeker note:

| Lever | Extra return | Extra risk | Chance it passes one pre-registered test |
|---|---|---|---|
| Hold it in a tax-advantaged account | +2 to +7 points after tax | None | Not a test; do it before real money |
| Save $500 a month | Equal to +6 points on $100k | None | Not a test |
| Do not interfere | +1 to +2 points kept | None | Not a test |
| Gold or Treasury sleeve, re-levered to the same risk | +1 to +2 points | Slightly lower drawdown | 20% |
| Lean tax-loss harvesting | +0.5 to +0.8 points after tax | None | 10% |
| Faster re-entry after VIX ≥ 40 | +0.3 points | Up to 3 points | 10% (failed on 20 Nov) |
| Remove the 200-day rule | +1 to +2 points | Drawdown roughly doubles | 3% |
| Leverage 1.5x | +3.3 points if Sharpe is 0.7; +0.5 if 0.35 | Drawdown −34% to −50% | 1% |
| Leverage 2x or leveraged ETFs | +5.9 points; +0.3 if Sharpe is 0.35 | −62% (QLD's worst: −83%) | 1% |
| Earnings, overnight, option selling | Zero or less after costs | Fatter left tail | 1–3% |

Leverage is the only lever that moves the headline number, and it is a purchase of risk, not an improvement: the
repo's own six-market study found no leverage level that reliably beat holding once financing was charged. The
frozen model is already about quarter-Kelly on its point estimate. Asking for more return two sessions into a 5%
loss is the pattern the retail-loss studies describe (the break-even effect), which the sceptic note flags as a
larger risk than anything in the model.

## For the scheduled review (2027-11-19), not before

1. **Tightening-regime gate.** When QQQ is below its 200-day average and the 2-year yield is above its level 126
   sessions earlier, hold 25% of target instead of 50%. The only idea from this episode with a published mechanism
   (the Fed's asymmetric response to equity falls, absent when hikes are priced). November 2026 must be excluded from
   the judged window. Estimated chance of passing: 5–8%.
2. **Diversifying sleeve** (gold or intermediate Treasuries at the same total risk). Estimated chance: 20%.
3. **The no-trade band** in the rebalance code (plumbing that changes exposure).

Running none of these is defensible. Each one counts as a new trial.

## Where the reviewers disagree with us

- **Astra:** the weakest decision was moving the volatility target 15% → 25% → 20% after looking at results, right
  before freezing it. The freeze stops further tuning; it does not validate the choice. Set the risk budget from the
  dollar loss the owner can sit through.
- **Sceptic:** process risk is larger than model risk. The universe, the target, the freeze and the first orders all
  happened within about three hours, and eight challengers were run on the day of the drop. A one-theme basket also
  cannot answer the real-money question, which is this versus a plain index fund. Judge the paper year against QQQ.
- **Grok:** the same criticism, sharper: the one-test, never-in-a-drawdown rule was applied to eight ideas on the day
  of the drop and shipped nothing, but it was not applied to the risk budget, the only setting that decides how much
  the account can lose. Its advice is to leave 20% alone until a pre-registered test says otherwise: "Monday is for
  the missed rebalance and the cash-floor bug, not for getting the money back."

None of them argues for changing the model now. Both external reviews are in `grok_astra_reviews.md`.
