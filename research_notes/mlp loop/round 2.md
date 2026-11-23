# Round 2: how to make the network smarter and more efficient (2026-11-23)

Asked of Astra 6.2 and Grok after lab session 1 (three experiments, all reverted) and before a scheduled Claude
task was created. Each got the network's source, the results so far and seven questions: which changes are most
likely real, how to get more out of so little data, how to save compute, how a scheduled loop should run, how to
score forecasts on new days, what "actively learning" can honestly mean, and their prior. Opinions, not evidence.

## Where they agree

- A weekly agent that keeps testing changes on the same 2016 to 2021 months is a search that finds noise. Grok:
  60% that it keeps a false winner under the old +0.01 rule. Both: a short list written in advance (Astra two more
  experiments, Grok four), then no more testing on history.
- The old keep rule was too weak (+0.01 rank IC is a third of a standard error). Astra also found two flaws in the
  scoring: the leave-one-out test compared a reduced sample with a full one, and a December 2021 forecast was
  scored with January 2022 prices.
- The monthly refit on new outcomes already is the honest learning. Daily updates would chase the last shock.
- New evidence can only come from a dated forecast log scored on days that had not happened. The wait is years:
  a true rank IC of 0.05 needs about six years to show at this noise level.
- Their priors that this ever beats the live trend tilt on new days: Astra about 10%, Grok about 5%.

## Where they differ

- Astra's first choice is a fixed blend (80% trend rank, 20% network rank), prior 25%. Grok expects a blend to
  lose (80%) unless the network first shows it adds something to the trend score.
- Grok would start with a heavily shrunk ridge on four slow inputs; Astra with a ridge on all 14 as a yardstick.

## What was done with it (the same day, before any further experiment)

- Rule 2 in mlp_odds.py: the yardstick is the live book, the bar is the official one (growth odds 0.90, both
  halves, any one year left out) plus a better ranking than the trend score that survives leaving out any stock or
  year. Prices frozen in lab/dev_prices.csv and cut at 2021-12-31.
- Budget: four experiments, written in lab/queue.md (Grok's ridge, Astra's ridge, two hidden units, Astra's
  blend). The code refuses a fifth.
- Forward record: mlp_odds.py --log, run after each close by .github/workflows/mlp_log.yml.
- A kept variant needs 252 sessions after its own date before it can pass the official bar.
- Not done: Astra's 99% bootstrap bound and its single decision at 84 months; Grok's reviews at months 36 and 60.
  The official bar stays as it was, with the 252-session floor added. Parked for lack of data: a wider training
  universe with dated membership, opening prices, earnings dates.

---

# Astra 6.2

**I’d freeze the live trend tilt as champion, fix the evaluator, and give the lab two more historical experiments.** The rank-target result is the most interesting finding from session 1. Its reported rejection doesn’t establish that one year explains the gain. The spent lockbox, however, gives me little reason to trust the standalone network.

### 1. Fix the comparison first

- `dev()` caps forecast dates, but `target()` reads the full price history. A December 2021 IC observation can use January 2022 returns. Slice prices at `DEV_END` **before** constructing targets. Pin the same forecast dates and eligible names for both variants.
- The deletion test compares the challenger **after deletion** with the incumbent’s **full-sample** IC. Recompute both on each identical deletion and compare their difference. The incumbent’s IC without the rank target’s best year is the missing number. Rescore the archived experiments once under the corrected evaluator and preserve both verdicts.
- `fit()` chooses its validation split from surviving rows. Require a complete 21-session outcome and verify that the last training outcome precedes the first validation forecast. Audit the imported execution code too. A score using the final close needs an executable price after that close.

### 2. Experiments, in order of expected forward growth

Both candidates need only adjusted daily closes for the fixed names and QQQ. My probabilities are subjective chances of **positive expected net log-growth versus live**. Sampling luck can produce a winning record more often.

| Rank | Single change from the original MLP | Prior | Drop condition |
|---|---|---:|---|
| 1 | Change only the score passed to `tilt`. On each day’s common eligible names use `0.8 × percentile_rank(live trend) + 0.2 × percentile_rank(MLP)`, ascending with average ties. Use live’s tie-breaker. | 25% | Drop if it never changes holdings or fails the growth screen below. |
| 2 | Replace `fit/predict` with ridge on the identical gradient-training rows and scaled target. Center X and y on those rows, solve `(Xc.T @ Xc / n + 0.001 I) b = Xc.T @ yc / n`, restore the intercept. Freeze the penalty. | 12% | Drop as a trading candidate if it fails the screen. Retain its forecast as the linear yardstick. |

I’d implement ridge first because it cheaply answers whether nonlinear fitting earns its complexity. The blend ranks first because the MLP only has to improve a few marginal holdings. Adding trend as an input gave the network discretion to ignore it. Blending fixes its influence explicitly.

The model already pools stocks and dates. Overlapping labels and common shocks limit the independent information in those rows. Ridge shrinks redundant coefficients. The three QQQ inputs are common within a date, so their additive ridge contribution cancels in ranking. I’d defer feature selection and loss tuning. Wider training is the one proposal that adds observations, primarily across firms. Selecting today’s Yahoo tickers imports survival and membership hindsight. A credible expansion needs dated constituent lists, departed firms’ price histories and delisting outcomes.

### 3. Compute and search budget

Cache immutable price snapshots, features, targets, row masks, live returns and archived baseline forecasts. The blend needs no refit. Parallelize independent seeds where cores permit and verify forecast and holdings parity. Warm starts, fewer seeds, fewer refits, shorter training and replacing Adam with ridge all change the estimator. Count each proposed change as an experiment.

Run **one final development session** with both candidates preregistered against the original baseline, bringing the total to five including session 1. Then disable historical search. For admission to forward tracking, require positive mean daily net log-growth **over live**, with a positive one-sided lower bound from a paired circular block bootstrap (63-session blocks, 20,000 common draws, 99% bound per candidate for five trials). Require positive growth differences under every single-year deletion. Use identical predeclared costs. Report paired IC differences as diagnostics. This conservative screen still cannot undo earlier adaptive research. [White, *A Reality Check for Data Snooping*](https://onlinelibrary.wiley.com/doi/10.1111/1468-0262.00152)

### 4. Forward evidence and active learning

Freeze the qualifying rule with highest development net growth, including its monthly refit recipe. Queue other candidates. Each version owns its timestamped record. A refit continues that record. A design change starts another and cannot inherit earlier returns.

After each close and before execution, append a timestamped immutable record of data vintage, eligible names, model/code hashes, training-label cutoff, seeds, scores, ranks and intended weights for both books. Append execution timestamps, prices, costs, turnover and daily paired log returns as realized. After 21 sessions append outcomes and rank IC on a fixed nonoverlapping grid. Log missed runs. Never reconstruct a missed forecast for official credit.

At the supplied noise level, IC standard error after \(M\) months is roughly \(0.04\sqrt{72/M}\). A true IC of 0.05 takes about **76 months for 80% power** at a one-sided 10% threshold under stable variance and independent months. An IC of 0.02 takes about **470 months**. Growth needs its own power calculation from paired return variability. I’d schedule one decision at 84 months using the specified 0.90 growth bar, disjoint half-window checks and shipped-list check. Monthly reports can show cumulative growth difference, uncertainty, turnover, matured IC count and forecast coverage without issuing verdicts.

Monthly refitting already learns from new outcomes. I’d schedule forecast capture daily and refits every 21 sessions. The agent should never tune from forward disappointments, reopen the lockbox, erase failures, repeatedly test for promotion, or modify the bot. **My prior is about 10%** that this bounded loop admits a genuinely superior variant that also clears the forward bar at its scheduled review. I’d spend the remaining effort on point-in-time universe coverage and execution-quality measurement.

---

# Grok

The live trend tilt stays the book. Opinion: about **5%** that a disciplined version of this lab ever produces a variant which beats that tilt on days after the variant was frozen, and about **2%** that a weekly five-experiment agent is how it happens. About **60%** that the weekly agent, under the +0.01 rule, keeps a false winner. The lockbox already answered for this network: rank IC **−0.047**, growth odds **0.07**.

The fit has **257** weights (14×16 + 16 + 16 + 1). The deciding sample is about **10** names and **72** non-overlapping months, so a rank-IC standard error near **0.04**. A keep of +0.01 is under half a standard error. Experiment 2 (IC +0.053, then +0.011 with its best year removed) is the shape of the next “win” on this window. The leakage gap, the shared bootstrap seed, and a lockbox you can spend once are sound. The open search on that same window is the part that fails.

## 1. Changes, least unlikely first

Probabilities are my opinion of a **real** gain versus the live tilt after the freeze date. Read the baseline line you already print — how often the network is right when it disagrees with the trend — before spending a slot. If that rate is about **50%** or below, the ensemble weight on the network is zero and rows 3–6 are moot.

| # | One pre-registered experiment | P(real gain) | Drop when | Data |
|---|-------------------------------|-------------:|-----------|------|
| 1 | Ridge on `r126`, `r252`, `ma200`, `high` only. Global mean/variance on the training rows. Penalty `λ = 0.1 × n_rows`. Same walk-forward, same 21-day relative target, same tilt. | 0.11 | Dev growth odds < 0.40, or partial rank IC ≤ 0 | Closes + QQQ |
| 2 | Same ridge, trained on a frozen end-2014 list of ~40 names, applied only to the 10 | 0.08 | Skip unless membership and delistings are real | PIT index membership and delisting returns. A Yahoo list of names that still trade is a different, biased experiment |
| 3 | `hidden = 2`, same 14 inputs, same net | 0.08 | Dev rank IC below +0.016, or the year-deletion IC below the baseline | Closes + QQQ |
| 4 | Add one column to the row-1 ridge: 252-session sum of log(open / prior close), drop the latest 21 sessions, subtract β× the same sum for QQQ, scale by overnight vol | 0.08 | IC below baseline, or the gain sits in one year | Yahoo Open and Close, split-consistent |
| 5 | Residual target: each training day, subtract that day’s cross-sectional projection of the relative 21-day return onto the trend score. Judge IC against the raw relative return | 0.07 | Partial IC of the forecast versus the raw forward return ≤ 0 | Closes + QQQ |
| 6 | One added input: 60-day residual volatility versus QQQ | 0.05 | It fails the year-deletion rule. The book is already inverse-vol weighted | Closes + QQQ |

Partial rank IC: each rebalance date, regress the forecast cross-sectionally on the trend score; Spearman of the residual against the forward relative return; average over development dates.

Leave session 1’s three ideas alone, including any pairwise rank loss (that is the rank target again). Dollar volume and an earnings shock sit below this list. Earnings need announcement dates and a point-in-time surprise. Opinion, about **0.75**: another earnings feature repeats the null you already logged.

## 2. What actually adds information

Run row 1 and report the partial IC. That number is the only justification for a second score.

Stock-days are already pooled in the fit. Overlapping days stay out of the standard error. The useful prior is on the coefficients: mean zero, except a positive loading on a single 12-month, skip-month feature. With four slow, collinear transforms of one price path, heavy shrinkage **is** the model.

Early stopping inside `fit` minimises squared error while the keep rule watches Spearman IC. Those can crown different fits. Opinion, about **0.80**: swapping the loss moves monthly IC by less than 0.01.

Extra Yahoo names that exist today add survivorship, and the shipped 12-name growth odds of **0.61** are a property of a list chosen later. On the published development gap (26.2% versus 28.5%), a fixed blend with the network is a diluted live book. Opinion, about **0.80**: a 50/50 blend loses to the live tilt on the next sample. Blend only after the partial IC is positive and survives year deletion.

## 3. Compute

Cache the feature matrix and targets, keyed by a hash of the prices. Re-runs then skip the rebuild and leave the forecast unchanged.

These are different estimators and count as experiments: warm-starting Adam from the previous refit, refitting every 63 sessions, dropping seeds, changing patience. The closed form in row 1 is the real speed-up, and it is a model change.

Opinion, about **0.90**: four minutes is cheap beside one false keep.

## 4. The loop

The development window is spent. Three adaptive looks, plus a printout of the worst months and the names the net favoured, are enough for an agent to fit anecdotes.

- Remaining budget: **four** experiments, written down before any run. The agent executes that list. It does not invent the next change from `VERDICT` or from the worst-month lines.
- Retire “+0.01 rank IC.” Keep a shadow candidate only when partial rank IC stays positive after deleting any one year and any one name. That candidate does not become the book.
- The timer runs a **logger**, monthly. It runs a search **zero** times.
- Historical testing ends when those four are done, and sooner if row 1’s partial IC is ≤ 0.
- One frozen champion: the live trend tilt. Challengers log beside it. A keep must not move `judged_from` and throw away the champion’s clock. A stack of development keeps dated from the last edit is one search with a short memory.

## 5. Forward log

Append-only, written at the close, never refreshed when Yahoo revises history or the code changes:

`date, git_sha, variant, name, nn_score, nn_rank, nn_weight, trend_score, trend_weight`

Fill `ret_21d` and that date’s Spearman IC once the 21 sessions exist.

Monthly IC noise is about **0.34**. The standard error of the mean is about **0.06** after 36 months and about **0.04** after 60. A true IC of 0.03 is still unresolved at five years. Two looks, both pre-registered:

- **Month 36:** drop the shadow if mean rank IC is negative and growth odds versus live are below 0.25.
- **Month 60:** promote only if mean IC is positive, the lower 90% interval on the CAGR gap is above zero, and both halves are ahead.

Until month 36 the report is the wealth ratio, the running IC with its standard error, and “no decision.” The current 0.90 bar, with both halves above 0.50, is a sound shield for the live book. A small true edge will sit behind that bar for years. A miss is a reason to wait, and the model stays frozen while you wait.

## 6. “Actively learning”

The refit every 21 sessions, on outcomes known by that close, already puts the latest errors into the next fit. That is the whole of honest adaptation.

Another Adam step each day, starting from yesterday’s weights, re-fits the last shock. With ten names that shock is one idiosyncratic move. The skip-month in the live score exists because the last month is a bad teacher. Opinion, about **0.85**: online updates lose to the walk-forward refit you have.

The agent never: changes live weights or gets imported by the trading job; looks at 2022-onward while choosing a variant; adds a feature aimed at a named month or a named stock; lowers the bar, adds seeds until the t-stat moves, or widens the net after a loss; cites the hindsight 12-name result; merges its own keep onto the champion.

## 7. Prior, and the same effort

| Event | P (opinion) |
|---|---:|
| A variant from a capped, pre-registered list beats the live tilt after its freeze date, at a five-year bar | **0.05** |
| A weekly autonomous five-experiment loop does so | **0.02** |
| That weekly loop keeps a false development winner if +0.01 remains the rule | **0.60** |
| This network, already at 0.07 since 2022, later clears the same rule | **0.03** |

Run row 1 once. If the partial IC is ≤ 0, record that these prices have nothing further to add, and point the schedule at the live book plus one shadow whose code is never edited. The 1,150 pre-registered tests are the finding. A 257-weight net on ten stocks, retrained by a cloud agent, adds a commit history and more variance.
