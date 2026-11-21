# Behaviour, the reset question and real-money gates

Written 2026-11-21. "[calc]" is my own calculation from the repo's cached prices with `model.py` imported unchanged (scripts `calc1.py` to `calc3.py` in `C:\Users\tyler\AppData\Local\Temp\claude\28f7d7c4cc43e090\18bb9d78-57a2-4803-a7fe-5a5825765403\scratchpad\storm\behavior_reset\`). None is a trial of a rule.

## Findings

**Recommendation: keep the account. Do not reset it, and do not sell to cash.**

1. **A reset improves no statistic.** The paper year's pass tests are percentages or counts that start at the first logged rebalance, 2026-11-20. Return is equity over the first logged row, $95,083.54 (`scorecard.py:141`); tracking error uses day-to-day percent changes (`track.py:27`); set-up fills are already excluded (`MATH.md:76-78`). So the legitimate restart was made on 20 November, and the scorecard already shows the clean baseline. A reset changes the dashboard dollar figure and the alert anchor, which no test reads. Carried into the same log, the jump to $100,000 is a one-day 5.3% gap, which alone puts tracking error at 5.3% a year against a 3% limit [calc].
2. **It repeats the original mistake.** Alpaca no longer resets paper accounts; it creates and deletes them, each with new API keys, so the scorecard could no longer read the old fills. The 1.6-point error began with that kind of manual restart: commit `8c28d20` (18 November) cleared the rebalance flag "to start paper trading with new keys", and orders were queued after hours at the 25% target.
3. **It over-corrects and selects on outcome.** Errors cost 1.6 points; the model lost the other 3.4 as designed (model-only equity $96,600). Extra exposure pays on an up day, so beforehand the error was a coin flip, and resetting only after tails is selection. As a standing option, restarting whenever the account is 5% under its start adds 2.8 to 3.0 points to the reported first-year return and cuts losing first years from 21% to 13% for the engine on the Nasdaq-100 since 1986 [calc]. That is close to fund-incubation bias and nearly twice the model's unproven alpha (1.6% a year, t = 0.67, `MATH.md:19`).
4. **Minus 5% is this model's ordinary condition.** It sits at least 5% below a prior high on 42% of days (shipped names) and 56% (Nasdaq-100 engine). Of all start dates, 40 to 46% are 5% under water at some point in year one. From a risk-off start needing +5.3%, the median wait is 62 to 75 sessions, and 14 to 34% of starts are still below after 250 [calc]. Expect a red number for months.
5. **The scarce output of the paper year is the operator.** A one-year Sharpe ratio has a standard error near 1 (sceptic note), and tracking error can be measured in any market. Whether the owner leaves a losing account alone can only be observed in a drawdown, and this is the first. The laboratory evidence gives direction, not size. A reset lifts motivation in weak performers, but a frozen system gives motivation nowhere to go except tinkering. Real money has no reset.
6. **Selling to cash fails on its own evidence.** The rule has already cut stocks to about a third. Stop-losses add value only when returns trend, and the engine's monthly returns do not (lag-1 autocorrelation +0.01 to +0.02, standard error 0.05 to 0.08) [calc]. After the Nasdaq-100 engine's own drawdown first reached 15% (13 cases since 1987), the next 252 sessions returned a median +21%, rose in 10 and at worst lost 15% [calc].

**For a reset.** (a) It costs nothing real, and the dashboard would match the tracked percentage, removing a daily prompt to get even. (b) Resets raise persistence after a poor start, and abandoning the project would cost more than a cosmetic restart.

**Against.** (a) It conditions the record on outcome and erases 3.4 points of designed loss. (b) It is a discretionary act on session two, against the spirit of "never during a drawdown", and it breaks log, keys and order history to change a number no test reads.

**Real-money gates, all required.** 250 logged sessions inside the four execution thresholds. Zero unlogged interventions, with any −10% alert answered "review, no action". A written dollar loss limit, with the allocation at most that limit ÷ 0.40 (the engine's worst on the Nasdaq-100 is −39%, `MATH.md:15`). The choice justified against QQQ and a plain index fund. A tax-advantaged account and code that works without margin (sceptic finding 8). A live pilot first. For a prediction-market sleeve, a pass repeated on a second sample: 300 bets at 0.93 need a measured edge above 3.1% and have 9% power against a true 1% [calc].

**Pre-commitment text.**

> The paper account is never reset, re-funded, flattened or paused because of its profit or loss. A reset is allowed only if all four hold: (1) a verified fault leaves the account holding something the frozen model would never hold, and the next scheduled rebalance cannot repair it; (2) I would do the same had the fault made money; (3) cause, date and equity before and after are written in the MATH.md change log first; (4) returns are chain-linked across the reset, and the missed-session count, drawdown peak and n carry over. Never within 48 hours of a loss, never to drop a bad start, at most once in the 12 months. Anything else waits for the scheduled review. A breach is logged as an intervention and counts against the real-money gate.

## Evidence table

| Claim | Evidence | Failure case or caveat |
|---|---|---|
| After a loss | Break-even bets attract ([Thaler & Johnson 1990](https://ideas.repec.org/a/inm/ormnsc/v36y1990i6p643-660.html)). CBOT traders with morning losses were 16% more likely to take above-average afternoon risk ([Coval & Shumway 2005](https://ideas.repec.org/a/bla/jfinan/v60y2005i1p1-34.html)). Paper losses raise risk-taking; realised ones lower it ([Imas 2016](https://ideas.repec.org/a/aea/aecrev/v106y2016i8p2086-2109.html)). Reference points adapt less to losses than gains ([Arkes et al. 2008](https://ideas.repec.org/a/eee/jobhdp/v105y2008i1p67-81.html)). Decisions are judged by outcome ([Baron & Hershey 1988](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/baron-hershey-jpsp1988.pdf)) | Abstracts only. A 2020 replication of Imas found the fall, not the rise ([Experimental Economics](https://link.springer.com/article/10.1007/s10683-020-09663-x)) |
| Resets change effort | Weak performers given a reset kept playing 41% of the time against 26%; strong performers did worse ([Dai 2018](https://www.anderson-review.ucla.edu/reset/)). Landmarks prompt goal starts ([Dai, Milkman & Riis 2014](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2014.1901)) | Effort, not investing results |
| Restartable records are inflated | Incubated funds beat others by 3.5% a year, risk-adjusted, until launch ([Evans 2010](https://ideas.repec.org/a/bla/jfinan/v65y2010i4p1581-1611.html)). Topstep: 16.8% of attempts pass, 51.8% of people eventually do ([Fortunly 2026](https://fortunly.com/statistics/prop-firm-challenge-pass-rate-statistics/)) | Vendor-reported |
| Paper transfers poorly | Risk aversion rises when real stakes are scaled up, not hypothetical ones ([Holt & Laury 2002](https://www.aeaweb.org/articles?id=10.1257/000282802762024700)). Heavy simulator users trade more with real money and underperform ([Anginer et al. 2024](https://ideas.repec.org/a/taf/hbhfxx/v25y2024i4p436-448.html)) | Scale effect disputed ([2005 reply](https://econweb.ucsd.edu/~jandreon/Econ264/papers/Holt%20Laury%20AER%202005.pdf)) |
| Going to cash in a crash | Vanguard 2020: under 0.5% went all-cash; the share better off fell from 58% at end-March to 14% at end-May ([FA Magazine](https://www.fa-mag.com/news/the-price-of-panic-58093.html)). Fidelity, 2008 to mid-2011: balances +2% for those who stayed out, +50% for holders ([InvestmentNews](https://www.investmentnews.com/retirement-planning/401k-holders-who-bailed-on-stocks-in-2008-made-out-worse-fidelity/38251)). 31% of panic sellers never returned ([Elkind et al. 2022](https://dspace.mit.edu/handle/1721.1/141712)) | Balances include contributions |
| Size of the behaviour gap | 1.2 points a year; 2.1 for the most volatile funds ([Morningstar 2026](https://www.morningstar.com/business/insights/research/mind-the-gap)) | About 0.10 after removing a hindsight effect ([Fulkerson et al. 2026](https://walton.uark.edu/insights/posts/do_investors_really_lose_fund_returns_to_bad_timing.php)) |
| Institutions | Managers fired by 3,400 plan sponsors then did no worse than their replacements ([Goyal & Wahal 2008](https://ideas.repec.org/a/bla/jfinan/v63y2008i4p1805-1847.html)). Norway's fund bought 40% of its equity holdings during 2008, by rule ([Norges Bank 2009](https://www.norges-bank.no/en/news-events/news-publications/Speeches/2009/The-global-economic-crisis-and-its-impact-on-Sovereign-Wealth-Funds-The-example-of-Norway)) | One fund |
| Stop-losses | Lower expected return unless returns trend ([Kaminski & Lo 2014](https://dspace.mit.edu/handle/1721.1/114876)); tight stops lose after costs ([Lo & Remorov 2017](https://econbiz.de/Record/stop-loss-strategies-with-serial-correlation-regime-switching-and-transactions-costs-andrew/10013011284)); no change in losses versus holding ([Lei & Li 2009](https://openjournals.libs.uga.edu/fsr/article/view/4933)) | Monthly index stops added 50 to 100 bp a month while stopped out (its working paper) |
| Pre-commitment; looking less | Automatic sell orders cut the disposition effect; reminders did not ([Fischbacher et al. 2017](https://ideas.repec.org/a/oup/rfinst/v30y2017i6p2110-2129..html)). Traders shown prices less often took 33% more risk and earned 53% more ([Larson, List & Metcalfe 2016](https://www.nber.org/papers/w22605)) | No effect with real funds over a year ([Beshears et al. 2017](https://www.nber.org/papers/w16868)) |
| Reset mechanics | "create and delete paper accounts, rather than resetting them" ([Alpaca docs](https://docs.alpaca.markets/docs/paper-trading)). IRAs for API users ([Alpaca, May 2026](https://alpaca.markets/blog/alpaca-introduces-individual-retirement-accounts-for-trading-api-users/)) | Undated |

## Ideas worth a pre-registered test (or why none)

No predictive idea comes from this angle. An account-level stop-loss is not worth a trial: the 200-day rule already is one, the engine's returns show no trend to harvest, and the nearest tested variant, full exit, lost (`reports/selloff_postmortem_results.md`). Chance of passing: about 2%.

Four process actions, none a model change:

1. Adopt the reset rule and annotate 19 and 20 November in the change log: set-up cost 1.6 points, tracked window starts 2026-11-20, the missed session still counts.
2. Keep an intervention ledger as the paper year's fifth statistic: every manual order, forced run, state edit, parameter change or pause, dated, with a reason.
3. Show less money: gap to the model in basis points daily, dollars weekly. Evidence mixed.
4. Write the dollar loss limit now.

## What I looked for and did not find

- A study of paper-account resets and later real-money results.
- Direct evidence that a written policy statement reduces panic selling; commentary and simulations only.
- Thaler and Johnson's tables, Vanguard's original "cash panickers" note (404), and full texts of Imas, Holt and Laury, and Lei and Li.
- Any measure of whether paper-drawdown tolerance predicts real-money tolerance.
- Whether Alpaca's API IRAs are cash or margin accounts, and whether a deleted paper account's orders stay retrievable.
- The owner's dollar loss tolerance, tax bracket and account type.
- Whether a paper account existed before the 18 November "new keys" restart.
