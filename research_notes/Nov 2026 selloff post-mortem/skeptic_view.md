# Skeptic / risk-manager view: Nov 2026 selloff post-mortem

Written 2026-11-21. Read-only review: no code was run and no file edited. Code claims carry file:line. Items I could not check are marked **[unverified]**.

## Bottom line

Two sessions say nothing about the model and a lot about the plumbing. The model did what it was built to do (-3.4% vs QQQ -7.7%, `reports/selloff_postmortem_results.md:12`); the account lost 1.6 points more for mechanical reasons. The bigger danger now is the owner: "how do we recover" and "how do we get bigger gains" after a 5% loss are the questions the loss-chasing literature predicts.

## 1. Model risk over the next 12 months, ranked

1. **The return expectation is mostly name selection.** The shipped list earns 23.2% CAGR; the same engine on the end-2014 list earns 15.3%, below QQQ's 17.6% (`reports/backtest_results.md:9,19,20`). Before the four AI-chain names were added the 8-name model showed 18.0% (`:14`). About a third of the headline is hindsight, and the engine adds nothing over the same names at the same volatility (p = 0.62, `MATH.md:16`).
2. **It will lag any fast rebound, by design.** Gross is 34% and QQQ is 10.8% below its 200-day average. The 60-day vol window (`model.py:22,94`) keeps November's moves in the estimate until about mid-February. Recovering 5% at one-third exposure needs roughly a 15% basket rally first. The repo's own table: after similar drops the engine made +43% against +110% for holding in 1998, and a median +13.7% against +17.6% over 126 days (`selloff_postmortem_results.md:51,61`). Out of sample, volatility-managed portfolios do not systematically beat unmanaged ones ([Cederburg et al., JFE 2020](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117)). The 200-day rule's post-2009 whipsaw record is from secondary sources only ([CFA Institute blog](https://rpc.cfainstitute.org/blogs/enterprising-investor/2022/technical-analysis-revisited-moving-averages-above-average-returns)) **[primary study not fetched]**.
3. **Gap risk in risk-on.** At the October peak gross was 91-100% with 31% in four semis (`selloff_postmortem_results.md:25-28`). A repeat of Friday's semis move from there costs about 3.7% of equity in a day, and a daily-close rule cannot act on it. A single name at the 25% cap (`model.py:24`) gapping 30% costs 7.5%. Whether any name actually reaches the cap is **[unverified]**.
4. **One factor, not twelve stocks.** All twelve sell into the same AI capex (`model.py:9-11`). The 60-day covariance (`model.py:97,115`) lags a correlation spike, and correlation-aware sizing was tested and rejected (`MATH.md:22`).
5. **Data.** Backtest and live weights both come from yfinance (`model.py:39`, `monitor.py:198`), with no cross-check against Alpaca's prices.
6. **SPCX.** Low: the 5% cap is about 1.7% of equity now. Lockup expires 2026-12-08 (`MATH.md:124`).

## 2. Process risk

- **Timeline from git.** First commit, universe 8 to 12 names, vol target 15 to 25 to 20%, freeze and first orders all happened within about three hours on one evening (commits `3637743`, `3457a03`, `a348b61`). The freeze protects a configuration that was itself chosen quickly after looking at results.
- **The account ran the abandoned 25% target for its first two days [inference].** Model gross at the 11-18 close was 38% at a 20% target; 38% x 25/20 x the 0.98 buffer = 46.6%, which matches the ~46% bought. The cut to 20% reached the account only on Friday afternoon.
- **What the evidence says.** After losses, bets that offer a chance to break even become unusually attractive ([Thaler and Johnson 1990](https://ideas.repec.org/a/inm/ormnsc/v36y1990i6p643-660.html)). People take more risk after a paper loss and less after a realized one ([Imas, AER 2016](https://econpapers.repec.org/RePEc:aea:aecrev:v:106:y:2016:i:8:p:2086-2109)); this account holds a paper loss in a paper account. The most active households lagged the market by several points a year ([Barber and Odean 2000](https://faculty.haas.berkeley.edu/odean/papers/returns/Returns.html)). The timing gap for fund investors is about 1.1 points a year ([Morningstar Mind the Gap 2024](https://marketing.morningstar.com/content/cs-assets/v3/assets/blt9415ea4cc4157833/blt5d1d34a59bd78a2c/680a4bd8c4d2e877fdb4b354/Mind_the_Gap_2024.pdf)). Dalbar's much larger figures are disputed on method and should not be quoted ([Kitces guest post](https://www.kitces.com/blog/does-the-dalbar-study-grossly-overstate-the-behavior-gap-guest-post/), [Advisor Perspectives](https://www.advisorperspectives.com/articles/2017/05/08/testing-dalbar-s-claims-about-mutual-fund-investors)).
- **Where change control is weakest.**
  1. It is self-enforced: the same person writes the rule, the test and the log.
  2. There is no limit on challengers. Eight were run on the day of the drop, plus a leverage study. All failed and the rule held, but H5 at P = 0.054 (`reports/retail_edge_results.md:47`) is the kind of near-miss that gets re-specified. Every re-run is a new trial.
  3. "Plumbing" is exempt (`MATH.md:80`), yet the rebalance logic is listed as frozen (`MATH.md:53`) and has a live-only band and buffer that change exposure. The exemption needs a definition: a fix is plumbing only if it moves live trading closer to `model.backtest_returns`.
  4. The universe changed after the freeze (ANT removed, `MATH.md:103`). Defensible, but it is a precedent.

## 3. Execution findings

**(a) Confirmed.** `monitor.py:66` sets SGOV to 1 minus the model's stock weight. `:67` sizes every line at 98% of equity. `:71` skips any trade under max($50, 1% of equity). Skipped stock trims are never subtracted from the SGOV buy. On 11-20: stocks stayed at 39% against a 33.3% target (5.7 points of skipped trims), SGOV went to 64.7%, total 103.7%, so cash was about -3.7% of equity, which is the -$3.6k observed.

- Worst case: twelve names each just under 1% over target gives 12 points of excess stock and cash of -10% of equity. At a 34% target that is 45% in stocks, 36% more risk than the model.
- The band is 1% of equity against positions averaging 2.8%, so it is a ~35% relative band. The backtest has no band (`model.py:124-136`), so this is untested live-only behaviour.
- Smallest fix for the margin, before the loop at `:69` **[not run]**: collect the stock names the band will skip and do `diffs[CASH_ETF] += sum(diffs[s] for s in skipped)`.
- That does not fix the exposure error. Fixing that means shrinking the band (commissions are zero and orders are fractional, so it buys little). It moves live toward the backtest, but it is a decision for the lead.

**(b) Other failure modes**

| # | Finding | Where | Severity |
|---|---|---|---|
| 1 | Drawdown tiers are anchored at $95,083.54, not $100,000. The -10% alert fires at $85.6k, which is -14.4% from the start. Cause **[unverified]**. | `state.json:27`, `monitor.py:157` | High |
| 2 | `equity_log.csv` has one row (11-20, $95,083.54). `track.py` cannot run, and the first two sessions will never be in the tracking record. | `track.py:37` | High |
| 3 | A forced run with the market closed still sends orders; they queue and fill at the next open at stale sizes. This is how the first buys happened. | `monitor.py:185,222` | High |
| 4 | Thursday's miss: GitHub cron fired no run in market hours (cause known and patched). Remaining gap: the last trigger is 20:17 UTC, which is 15:17 ET in winter. If the loop dies after that there is no restart before the close. An uncaught `/clock` error kills the loop. | `monitor.yml:7`, `loop_monitor.py:43` | Medium |
| 5 | No check that the last price row is today's. If Yahoo returns data only to yesterday, weights and regime are a day stale and the day is marked done. A gap in one name is forward-filled silently. | `monitor.py:198-200,227` | Medium |
| 6 | A `monitor.py` crash (Yahoo rate limit, empty frame) is swallowed: the return code is ignored and no Discord alert is sent until the next day's missed-rebalance check. | `loop_monitor.py:19,32` | Medium |
| 7 | An accepted order is treated as filled. The day is marked done with no fill check, so a halted name can sit unfilled. | `monitor.py:86-88,236` | Medium |
| 8 | Sells are sent first but not awaited, so buys rely on margin buying power. A cash account would reject them. | `monitor.py:69,86` | Medium (real money), low (paper) |
| 9 | Positions are read right after cancel-all; whether cancels are complete on return is **[unverified]** ([docs](https://docs.alpaca.markets/reference/deleteallorders)). | `monitor.py:61-63` | Low |
| 10 | Half days use Alpaca's clock (12:30 on 11-27). Looks right, never exercised live. | `monitor.py:51,184` | Low |
| 11 | Alert text says max drawdown -27%; backtest says -22.5%. | `monitor.py:123` | Low |

## 4. What a two-day sample can and cannot say

- **Skill: nothing.** Backtest volatility of 17.9% is about 1.1% a day and 1.6% over two days. The model's -3.4% is about two unconditional standard deviations, and unremarkable with VIX at 36. Even a full year cannot tell a Sharpe of 1.0 from 0: the standard error of a one-year Sharpe is about 1.
- **Execution: a lot.** Live -5.0% against model -3.4%. Friday's excess exposure explains 0.57 points (`selloff_postmortem_results.md:38-39`); the rest is Thursday's larger position and the open-versus-close entry **[inference]**.
- **Normal range.** With an honest 15% return and 18% volatility, a year at -15% is a 1-in-20 outcome. The strategy's drawdown from its October peak is already -15.9% against a backtest maximum of -22.5%, and the same engine on the Nasdaq-100 reached -34% to -39% (`reports/leverage_results.md:64`, `MATH.md:15`).
- **When to worry.** Tracking error above 3% a year after 60 sessions or a one-sided drift; a one-day gap over about 0.5% with no known cause; more than 5 missed sessions (already 1); equity below about $77,500, which is past anything in the backtest. P&L inside those limits is not information.

## 5. The honest null, and the case against it

**Change nothing in the model.** No tested change beats it: 0 of 8 on 11-20 and about 700 before. The loss is inside the normal range. Any change now is conditioned on two days and made in the state Thaler-Johnson and Imas describe. Lower exposure after a drop is the designed cost of the drawdown control, not a fault. Fix the plumbing in section 3, reset the drawdown anchor to $100,000, and wait.

**Against.** The paper year tests execution only (`MATH.md:73`), which any basket could test. On hindsight-free names the engine returns less than QQQ, with no edge over holding the same names at lower exposure. Twelve months of a one-theme basket, during an accounting probe of its largest company, will not inform the real choice between this and a broad index fund. Freezing a three-hour-old configuration is anchoring as much as discipline.

**My read.** The second argument is right about real money and wrong about the paper model. It is a reason never to size real money on 23%, and to judge the year against QQQ and a plain index fund. It is not a reason to edit the model during a drawdown.
