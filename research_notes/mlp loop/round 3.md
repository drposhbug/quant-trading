# Round 3: why the pattern-finder failed and how to fix it (2026-11-23)

Asked of Grok after the pattern-finder (discover_odds.py) failed its one test, and after the owner asked for a
machine that makes calls every day so that it can be seen what comes true. Grok got the machine's rules, its
results and a draft plan. Opinions, not evidence. Its answer is below, unedited.

## Checks run the same day on the failed run (development years, ten names)

- The ten patterns it trusted at each refit had an average rank IC of +0.108 in their own past and +0.003 in the
  21 sessions that followed (720 pattern-months).
- Shuffled outcomes (every stock given another stock's future, 20 shuffles): the best ten candidates scored 0.214
  on average (0.163 to 0.266) against 0.228 for the real outcomes. 30% of shuffles looked at least as good.
- 464 of 945 candidates pointed the same way in both halves on real outcomes, 487 on shuffled ones.
- Multiplied pairs were 73% of its picks and 63% of the candidates.
These confirm Grok's causes 2 and 3: the selector crowned luck, and the pairs made the contest easier to win.

## What was built from it (daily_calls.py, rules "v2 2026-11-23")

Taken from Grok: no multiplied pairs; "shrink, don't crown" with a noise bar; no vote if the latest 252 sessions
disagree; NO VIEW when nothing clears the bar; favoured and avoided thirds, scored as favoured minus avoided and
rank IC; the trend ranking on every board; non-overlapping calls in the tally; 21 sessions as the one official
board; no verdict before a count fixed on day one; a rules name on every row, a new name starting a new tally.

Where it departs from Grok, and why:
- About 500 names, not 100. Grok's own table says 500 names reach a meaningful count in about a fifth of the time
  (1.5 years against 8 at 21 sessions). A clean, dated list of S&P 500 members already existed in the project.
- History from 2016, not 2007: that is where the price source starts.
- The noise bar re-signs blocks of each pattern's own daily rank ICs instead of shuffling names within a day.
  Shuffling names would make every day independent and every stock alike, and on 500 stocks that sets the bar far
  too low: real rankings swing together with the market and for weeks at a time. Re-signing blocks keeps both.
- A next-session side board is kept, against Grok's advice, because the owner asked to watch calls come true day
  by day. It is labelled as a side board and can never become the official one.

---

# Grok

## Why it failed

The walk-forward was honest. It failed because that search had almost nothing it could hear, then crowned noise anyway.

**1. The sample could not confirm a real effect (main cause).** Ten highly correlated megacaps, a 21-day residual, about 72 independent dates. One rank IC has noise near 0.3, so the mean is known only to about ±0.04. The trend score itself printed +0.006. A true IC of 0.03 would often fail this exact test. The book gap (27.4% vs 28.5%, ahead in 33% of bootstraps) is a fully invested bull market plus a coin-flip tilt. *Check:* average pairwise correlation of the ten, and the scale of the 21-day residual. Correlation above ~0.7 and a thin residual means the target is shared noise.

**2. The selector crowned noise, and the crown stuck.** Same sign in two halves lets roughly half of 945 candidates through. The top 10 by the worse half's t-stat is a max-of-hundreds contest. Windows of 250+ days that move only 21 days barely change the ranking, which is the 75% retention. Stability here is a sticky in-sample score, not a law. Forward skill was the tell: disagreements with the trend score were right 49% of 1,427 pairs, and the part of the forecast the trend score does not explain had IC −0.028. *Check:* at each refit, plot the selection score against IC over the *next* 21 sessions only. A high in-sample score and a forward IC on zero confirms the curse. Also compare retention 252 days apart; if that falls toward the base rate while 21-day retention stays ~75%, the stability was overlap.

**3. Products were built to win that contest.** They are 600 of 945 names, less correlated with each other, so the 0.7 filter fills the list with them. A product is a few joint outliers, enough to keep one sign in both halves. The champions (distance from the 252-day average × chip correlation, and cousins) are what that filter keeps. *Check:* product share among the chosen 10 versus 63%. Well above that, the filter preferred products. If a champion's score collapses after the ten biggest target days are dropped, outliers were the pattern.

**4. The self-check was easier than the job.** Two loud patterns among 40, and a white-noise rejection, do not show it can find an IC of 0.02 among 945 on ten names. Opinion, ~70%: with 945 candidates, N=10, and a planted IC of 0.02, this selector misses it or returns products.

The network's +0.014 and 22% failed the same bar. This window did not hold a second signal of the size that hurdle demands. Do not "fix" 2016–2021. It is spent.

## The fix

The forward-only board is the right response. The redesign is only partly right.

**Drop:** the 600 products; t > 2.5 as a believe/silence switch; a 1-day model as a result; any pass/fail reread of 2016–2021; the range "100 to 500."

**1. Shrink, don't crown.** Keep the 345 raw patterns. Each refit, permute names within each day's target, 100 times, and take the 95th percentile of the *best* |mean IC| in each shuffle. Weight is sign(train IC) × max(|train IC| − that bar, 0), and zero if the most recent 252 known sessions disagree in sign. If all weights are zero, log NO VIEW and leave the trend book unchanged.

**2. One hundred names, from 2007.** On day one, freeze the 100 US common stocks with the highest 60-day dollar volume. If one later disappears, drop it from that day and do not replace it. Learn from 2007-01-01 after 252 sessions of warmup. Publish z-scores for all 100 and, from those same scores, for the 12. Survivorship biases what is learned. It does not bias a tally of days that have not happened, if the list is not rewritten and old results are not a gate. Opinion, ~85%.

**3. Two horizons, one official.** Official: next 21 sessions. Side board, labeled as such: next 5, selected only on 5-day outcomes. Log every close if you want. Do not add a 1-session claim.

**4. The board below, trend score on every row, code hash on every forecast.** A new hash starts a new board at zero. The old one keeps running.

## Selection rule

Choose-on-two, confirm-on-a-third is the right shape and the wrong threshold. On 100 names one IC has noise near 0.10, and a year of 21-day returns is about 12 independent bets, so the mean is known to about ±0.03. A true IC of 0.03 often prints t ≈ 1 on the confirm year. t > 2.5 means "show an IC near 0.07," which liquid US names almost never do. Opinion, ~75%: the machine would stay silent, and the silence would get tweaked. That tweak is another test.

The shuffle bar already prices the winner's curse, because the hurdle is the best of 345 under a shuffled target. The latest 252 sessions are only a sign check.

## Scoreboard

Each close, for each name and live horizon, log the forecast, the bucket (top third favoured, bottom third avoided, else middle), the trend score's bucket, and the code hash.

When the horizon comes due: mean return of favoured minus mean return of avoided. A win is a positive spread. Store rank IC too. Do not score whether favoured names rose.

Show the overlapping win count, labeled overlapping. The official fraction is non-overlapping cohorts only (every 21 sessions, or every 5). Never add horizons into one tally.

Bets needed before a ~55% hit rate, or an IC near 0.02, is even suggestive:

| Universe | Independent bets | 5-day time | 21-day time |
|---|---|---|---|
| 12 | a few hundred | several years | a decade or more |
| 100 | ~100 | ~2 years | ~8 years |
| 500 | ~20 | ~4 months | ~1.5 years |

Until then, print: too early; independent bets so far are K; the benchmark is a coin; here is the trend score on those same bets. No green light before the count fixed on day one.

## How this fools us

**1. Several boards.** Two horizons, two universes, and the trend comparison are more than one chance. *Rule:* one official number, frozen now — 21-day favoured-minus-avoided on the 100, with the 12 beside it. Side boards cannot be promoted after they are seen.

**2. Overlapping streaks.** Daily 21-day scores move together. *Rule:* official tally is non-overlapping; stop-time is 100 independent dates on the 100; no result announcement before that.

**3. A bull market, or a quiet rewrite.** "Favoured stocks rose" is true in any rally. Editing the list or the code because the board looks bad is a new experiment with the old score. *Rule:* spreads and rank ICs only; frozen list; frozen hash; new hash, new board.

## Prior

Opinion. "Real skill" means a positive true forward rank IC whose favoured-minus-avoided spread clears a half-spread cost. This is not the chance the board looks good.

| Horizon | Where | Before costs | After costs |
|---|---|---|---|
| 21 sessions | 100 names | 20% | 15% |
| 21 sessions | the 12 | 12% | 10% |
| 5 sessions | 100 names | 12% | 5% |
| 5 sessions | the 12 | 8% | 4% |

A forced 1-session test: under 10% before costs and under 5% after, on either set. The useful result of the next year is a logged, unedited null.
