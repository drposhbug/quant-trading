# Network lab: the experiments

Written 2026-11-23, before any of them ran. This list is the whole budget under rule 2 (mlp_odds.py docstring):
four for the scheduled task and a fifth the owner added the same day (at the end). `python mlp_odds.py --dev`
counts the runs and refuses one more. Run them in this order. Do not add, swap, split or
re-run one, and do not design a change from a verdict or from the worst-month lines: both reviewers named that as
the way a loop fits anecdotes. Sources: `research_notes/mlp loop/round 2.md`.

Every experiment is ONE change from the starting network ("v1 baseline", the file as committed with this list),
not from an earlier experiment. It gets a new `VARIANT["name"]` (the heading below) and `VARIANT["judged_from"]`
set to the day it is run. The code decides: on `VERDICT: revert`, restore mlp_odds.py and commit only the log row.

## 1. `v3 ridge on the four slow inputs`  (Grok's first choice, its prior 0.11)

Replace the network with a ridge regression on four inputs only: `r126`, `r252`, `ma200`, `high`.
At each refit, on the same training rows the code passes to `fit` today (`tr` in `walk_forward`):
standardise each input column with that training set's mean and standard deviation, centre the target on its
training mean (the target stays divided by its training standard deviation as now), and solve
`b = inv(X.T @ X / n + 0.1 * I) @ (X.T @ y / n)`. Forecast = the test rows, standardised with the training mean
and standard deviation, times `b`. No seeds, no early stopping, no validation split. Same refit schedule, same
target, same tilt. Why: with four slow, collinear views of one price path, heavy shrinkage is the model; and it
answers whether these prices hold anything the trend score does not (read its partial rank IC).

## 2. `v3 ridge on all 14 inputs`  (Astra's linear yardstick, its prior 0.12)

Replace `fit`/`predict` with a ridge regression on the 14 inputs the network uses, fitted on exactly the rows the
network takes gradient steps on (inside `fit`: the rows with `day <= cut - FWD`; the validation rows are not
used). Centre X and y on those rows, solve `b = inv(Xc.T @ Xc / n + 0.001 * I) @ (Xc.T @ yc / n)`, restore the
intercept. No seeds. Why: it shows whether the hidden layer earns its 257 weights.

## 3. `v3 two hidden units`  (Grok, its prior 0.08)

`VARIANT["hidden"] = 2`. Nothing else changes. Why: 257 weights on about 71 independent months is far too many;
this is the same network with 33.

## 4. `v3 blend 80% trend rank, 20% network rank`  (Astra's first choice, its prior 0.25; Grok expects it to lose)

Run this one only if the reference row's `partial_ic` in reports/mlp_lab_log.csv is above 0 (the starting network
adds something to the trend score). If it is 0 or below, do not run it: write that in the notes and the lab closes
with three experiments.
The network is unchanged. Only the score handed on changes: at the end of `walk_forward`, replace the forecast
frame `F` with `0.8 * T.rank(axis=1, pct=True) + 0.2 * F.rank(axis=1, pct=True)`, where
`T = scores(px, {**P, "w_trend": 1.0})` on the same dates and names, both ranked across the names that have a
forecast that day (mask `T` where `F` is missing). Days with no forecast stay empty. Why: adding the trend score
as an input let the network ignore it (session 1); a fixed blend lets the network move only the marginal holdings.

## Parked: these need data the lab does not have

They are not experiments for this list. A person decides whether to fetch the data and open a new, separately
budgeted round.
- Training on a wider universe (both reviewers' strongest idea): needs dated index membership, prices of the
  firms that left, and delisting returns. Names that trade today would add hindsight.
- Overnight residual momentum: needs opening prices, split-consistent.
- Earnings-shock input: needs announcement dates. Grok: 0.75 that it repeats the null already logged.
- Dollar volume: needs volume.

## 5. `v4 the machine picks its own patterns`  (added by the owner, 2026-11-23; run by hand, not by the scheduled task)

The owner asked for a model that "looks for unique trends and makes its own correlations" instead of using the
textbook inputs. It is a separate file, discover_odds.py, whose docstring is the full definition, fixed before it
was scored: 945 candidate patterns built from each stock's open, high, low, close and volume and 15 outside
series; every 21 sessions it keeps the 10 that held up in both halves of what it has seen; one equal vote each.
Run once with `python discover_odds.py --dev`, same bar as the four above. The budget went from 4 to 5 for it.
Whatever its verdict, it has a forward record of its own (signals/discover_*.csv).

## After the five

The lab is closed to history. New evidence comes only from the forward record (signals/mlp_forecasts.csv and
signals/mlp_forward.csv), which grows by one day at a time.
