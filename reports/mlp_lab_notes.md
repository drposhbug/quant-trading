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
