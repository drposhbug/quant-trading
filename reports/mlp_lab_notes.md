# Network lab notes

One entry per run of the scheduled network lab task (newest last). The rules are in mlp_odds.py's docstring, the
experiments in lab/queue.md, every score in reports/mlp_lab_log.csv. Plain words; numbers come from the files.

## 2026-11-23 (by hand, before the first scheduled run)

- Session 1 ended with three experiments, all reverted, and the starting network failing its one test on the
  years from 2022 on (growth odds 0.07 against the live book).
- Astra 6.2 and Grok reviewed the plan for a scheduled task (research_notes/mlp loop/round 2.md). Both said a
  loop that keeps testing on the same six years would mostly find noise, and that the old keep test was too weak.
  The test was replaced the same day, before any further experiment: a change must now beat the live book on the
  development years by the same bar it will face later, and rank the stocks better than the trend score does.
- The starting network under the new test: growth odds 0.22 against the live book (needs 0.90), rank IC +0.014
  against the trend score's +0.006 over 71 months. It is the reference, not an experiment.
- Four experiments are written in lab/queue.md. The code refuses a fifth. After them the lab is closed to
  history.
- A forward record started: after each close the network's forecast for every stock is logged, and scored 21
  sessions later (signals/mlp_forecasts.csv, signals/mlp_forward.csv). That is where new evidence will come from.
  Both reviewers put the honest wait at years.

## 2026-11-23, later (by hand): the pattern-finder

- The owner asked for a model that finds its own trends and correlations instead of the textbook ones. Built as
  discover_odds.py: it makes 945 candidate patterns out of each stock's open, high, low, close and volume and 15
  outside series (bonds, gold, oil, the dollar, sectors, the VIX), and every month keeps the 10 that held up in
  both halves of everything it had seen so far. Its rules were written and committed before it was scored.
- Result on the development years, one run: it did not pass. Its book grew faster than the live book in 33% of
  simulated histories (it needs 90%), 27.4% a year against 28.5%. Its ranking of the stocks was no better than a
  coin: rank IC -0.011 against the trend score's +0.006, and what it added to the trend score was below zero
  (partial rank IC -0.028). When it disagreed with the trend score about two stocks it was right 49% of the time.
- What it found looked convincing from the inside. It kept three quarters of its patterns from month to month,
  and each had worked in both halves of its own past. Its favourite, used in 55 of 73 months: distance from the
  one-year average combined with how closely the stock moves with chip stocks. None of it carried to months the
  machine had not seen. That is what a search over many patterns on ten stocks looks like: the finds are real in
  the past and absent in the future.
- It is not in the live book. It now logs its forecast and the ten patterns behind it after every close
  (signals/discover_forecasts.csv, signals/discover_found.csv), scored 21 sessions later
  (signals/discover_forward.csv). That record is the only place it can still earn anything.
- The lab's budget went from 4 to 5 for this run. The four experiments in lab/queue.md are untouched and still
  wait for the scheduled task.
