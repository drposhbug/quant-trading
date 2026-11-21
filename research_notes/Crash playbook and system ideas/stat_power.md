# Statistics and power of the whole programme (stat_power)

Written 2026-11-21. Numbers marked [calc] are my own, from the data named beside them.

## Findings

1. **No paper sleeve can return a true PASS.** At each sleeve's minimum n, the edge needed for an 80% chance of passing is four to seven times the repo's pooled retrospective estimate (+0.8%) for the favourites sleeves, and above the repo's own best case for options and Elo (table). The experiments are less informative than the prior: a 300-bet tennis test has a standard error of 1.6%, and the uncertainty it is meant to resolve is 0.9% [calc].
2. **The family will probably produce a false PASS anyway.** With zero edge everywhere, the chance that at least one of the seven ROI sleeves shows PASS is 28% if each is judged once at its minimum n and 56% if `scorecard.py` keeps re-judging the growing sample daily up to twice that n [calc: 20,000 simulated ledgers per sleeve, `fav_stats` rule]. The 95% interval is too narrow for a win-small, lose-big payoff (false-pass rate 4–5%, not 2.5%), the verdict is never frozen ([repeated looks inflate error](https://link.springer.com/doi/10.1186/1471-2288-3-15)), and the any-category bootstrap treats correlated legs as independent.
3. **The stock sleeve's yardstick measures the clock, not execution.** `track.py` compares a 15:30-to-15:30 live return with a close-to-close model return. With the frozen model's own weights that offset alone gives 5.3% a year of daily tracking error (4.3–6.5% across every 250-session window; none at or under the 3% bar) [calc: yfinance 60-minute bars, 729 sessions to 2026-11-20]. It falls to 2.3% on 5-day sums and 1.3% on 21-day sums, as timing noise does, and it scales with exposure (6.9% per unit of gross), so it will look fine at 34% invested and fail after re-risking. Friday showed it: $95,083.54 at 15:30, $94,975 at the close.
4. **Twelve months cannot measure skill against any benchmark.** The standard error of a one-year Sharpe ratio is 1.0–1.2 ([Lo 2002](https://econpapers.repec.org/RePEc:taf:ufajxx:v:58:y:2002:i:4:p:36-52), formula [memory]). In its own hindsight backtest the model trailed QQQ in 34% of rolling 12-month windows [calc].
5. **The count is about 1,150 tests, not 700, in three days.** My tally from `reports/` is 1,153 tests in 24 studies; the first commit is 2026-11-18. The best of 1,153 independent null tests is expected to reach z = 3.3 [calc, [expected-maximum formula](https://papers.ssrn.com/abstract=2460551)]; Benjamini-Hochberg at 20% would need P ≤ 0.00017 for a first rejection ([method](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)).
6. **Prior and false-discovery rate.** Zero tradable edges in 24 studies gives a posterior mean of 2.0% for the next predictive idea (95% upper bound 7.6%, Jeffreys) [calc]. At 2%, one P < 0.05 pass is false 75% of the time at 80% power and 83% at 50%. Requiring both universes helps less than it seems: their z-scores correlate about 0.7 in the 20 November slate, so the joint false-pass rate is 0.02 and the false-discovery rate 62% [calc]. Under 20% needs P ≤ 0.004, close to the t > 3.0 hurdle of [Harvey, Liu and Zhu](https://www.nber.org/papers/w20592), or two passes on independent data (16%).
7. **"Pre-registered" does not help when the idea came from the same data.** The gold sleeve already shows P = 0.024 on the shipped universe (`universe_results.md`). Re-tested on that window plus the paper year, it passes there again with 82% probability even if gold adds nothing from here [calc].
8. **Selection shrinkage is close to total.** The Wimbledon retro (+11%, 37 of 38) has P = 0.040 before correcting for the choice of band. The forward ledger has since settled 278 bets on that rule at +0.48% (standard error 2.3%), 4.6 standard errors below +11% [calc: `paper_favorites.sqlite3`]. Across the 34 groups in `fav_backtest_results.md`, pooled ROI is −0.38% (standard error 0.31) with no significant heterogeneity (Q = 41.8 on 33 df, P = 0.14; between-group spread 0.93% a bet). Empirical-Bayes weights of 0.05–0.47 move the existing set from +0.8% to −0.15% and tennis from +1.3% to 0.0% [calc]. The 0.90–0.97 band rests on sportsbook data; on Polymarket prices it shows −0.9% (n = 216) in the backtest and +0.5% (n = 89) forward. Even published anomalies lose [12% to publication bias](https://www.federalreserve.gov/econres/feds/publication-bias-and-the-cross-section-of-stock-returns.htm) and [58% after publication](https://rpc.cfainstitute.org/research/cfa-digest/2016/06/does-academic-research-destroy-stock-return-predictability-digest-summary).
9. **The treadmill costs more than it can return.** If the +0.8% were real, $100 stakes on 2,240 bets a year earn $1,792; at the shrunk estimate they lose $336 [calc]. Twelve predictive ideas a year under the current rule give 0.24 expected false promotions against 0.14 true ones [calc]. The post-mortem's non-test levers are worth thousands a year with no trial.

## Evidence table

All [calc] unless a file is named. "Re-judged" means daily looks up to twice the minimum n.

| Sleeve (minimum n) | Edge needed for 80% power | Repo's own estimate | False PASS at zero edge (once / re-judged) | Time to n |
|---|---|---|---|---|
| Stock model (250 sessions) | tracking error ≤ 3% | clock offset alone: 5.3% | not applicable: fails by construction | 251 sessions exist to 2027-11-19: one more miss allowed, the rule says five |
| Options iron fly (120 trades) | +0.14 to +0.15 of max loss per trade | −0.16 to −0.01 (`Options math and strategy.md`) | 2.3% | 5 of 12 names too large for one contract at $500 risk (my proxy): at most 28 trades a year, 4.3 years or more |
| Sports Elo (200 bets) | +26% to +29% ROI | −6.5% [−12.0, −1.1] on 2,203 bets (`sports_results.md`) | 1%; the STOP rule fires 41% of the time | about 33 days |
| IPO brackets (30 events) | wins 72% of events | none; no scorer exists | 4.9% | 0 events in the feed; years |
| Tennis heavy favourites (300) | +3.6% a bet | +0.8% or less | 4.7% / 11.8% | Jul–Sep 2027 (1.3 a day in season, none until January) |
| Soccer favourites (300) | +5.4% | +0.8% pooled | 3.6% / 10.3% | 1 to 7 years |
| NBA favourites (300) | +4.8% | +2.2% [−2.2, +6.1] | 4.0% / 10.5% | 1 to 2 seasons |
| NFL/NHL/MLB favourites (300) | +3.7% | none | 4.6% / 11.7% | about 30 bets a year: 10 years |
| Any-category favourites (200) | +3.5% | −2.7% to +1.5% by category | 11–16% / 25–32% (69 entries are 30 outcomes) | about January 2027 |

What the stock paper year can distinguish:

| Comparison | Noise over 12 months | Verdict |
|---|---|---|
| Live against model on end-of-day equity | expected tracking error 0.8–1.6% | Informative within about 60 sessions |
| Fill shortfall against the close | standard error about 4 bp (assumes 50 trade-days) | Informative |
| Sharpe against QQQ | standard error 0.58; needs a gap of 1.43 | Backtest gap 0.41: 12 years. Hindsight-free gap 0.16: 80 years |
| Sharpe against QQQ at the model's own daily exposure | 0.34 | Best return benchmark; still 27 years for 0.16 |
| Sharpe against equal-weight at matched volatility | 0.47 | 53 years for 0.16 |
| Return against QQQ | 10.5–12.2 points | Context only |

## Ideas worth a pre-registered test (or why none)

No predictive idea. At a 2% prior and with tests this weak, another one adds a trial and no information. Four process changes for the scheduled review:

1. **Fix the yardstick.** Take live returns from Alpaca's daily portfolio history ([equity "as of the end of each time window", available since account creation](https://docs.alpaca.markets/us/v1.1/reference/getaccountportfoliohistory-1.md)); keep the 3% bar. This also recovers 19 and 20 November; check the daily mark against 20 November first. No tracking error has been scored yet (one row in `equity_log.csv`), as with the fill rule clarified on 20 November. Set the minimum n to 245 so five permitted misses cannot leave the sleeve unjudged.
2. **One favourites hypothesis, judged once.** Pool tennis, soccer, NBA and any-category; cluster by event or game day (`fav_backtest.cluster_stats` already does it; `any_fav_trades` needs an event column); freeze the verdict at n = 2,000 or 2027-11-19. PASS needs P ≤ 0.005 or a second cohort. Close the family if the upper 95% bound is under +2%.
3. **Promotion bar and budget.** Predictive ideas: at most four a year, each admitted only if the detectable edge is within twice the plausible one, and promoted at P ≤ 0.005 or on two independent samples, with a stated minimum effect size. Structural ideas (costs, taxes, execution) stay at P < 0.05. No challenger runs within five sessions of a 3% daily loss or inside a drawdown tier. Zero promotions after twelve months ends predictive research.
4. **Holdout clause.** The judged window must exclude the data that suggested the idea. For gold that means 2004–2015 on the ^NDX engine, written down first and deliberately not run here.

**Stop now, because they cannot reach an answer:** the Sports Elo pass/fail (its own backtest already rejected it), IPO brackets, and NFL/NHL/MLB favourites. Relabel options as data collection with no PASS verdict. Suspend the any-category verdict until its interval is clustered.

**Reset:** keep the account. Two sessions carry no information about skill and a reset changes no future return. It would restart the record after a bad start, which is selective reporting, and move the −10% review tier from 5 points away to 10. A fresh $100,000 account still has a 20–31% chance of being down after a year [calc: 15% or 9% return, 18% volatility].

## What I looked for and did not find

- Any power calculation in `MATH.md` or `scorecard.py`. Only the options report and `pm_results.md` have one.
- A rule that freezes a verdict, or any allowance for eight sleeves being judged at once.
- IPO day-one bracket markets in `signals/prediction_markets.csv`: none.
- Settled bets outside tennis: Elo 0, sport favourites 1, any-category 0.
- How many bands the Wimbledon retro tried, so its exact selection penalty is unknown.
- A venue: the favourites sleeves read the international Polymarket book, which the repo's notes call close-only for US persons.
- Benjamin et al. (P < 0.005) and Hou-Xue-Zhang: the shared search budget ran out, so neither is cited.
