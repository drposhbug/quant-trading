# Daily review

One entry per trading day: what happened, why, and what was changed. Written by the daily review routine
(first entry by hand, 2026-11-23). The routine may repair plumbing; it never changes the trading rules.

## 2026-11-23

- Equity $97,628 at the close ($97,939 logged at 15:30), up 2.8% on the day. The bot ended the day about 96% in stocks.
- What went wrong: the buy orders queued on Saturday filled at Monday's open, after the gap, about 8% above Friday's
  closes. Cause: a forced run sent market orders while the market was shut. Fixed: a forced run no longer trades when
  the market is closed.
- Also repaired: track.py compared the account with the retired cut-loss model. It now compares with the book the bot
  actually holds.
- Changed by decision, not as a repair: trend tilt on; monthly self-review added; neural network added as a
  challenger (it failed its test and is not live).
- test_monitor.py and test_model.py pass. One session is on the missed list (2026-11-19).
