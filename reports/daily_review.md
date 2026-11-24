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

## 2026-11-24

- Equity $96,045 at 15:30, down 1.9% on the day ($97,939 on 11-23); about 98% in stocks; regime risk-off; 4.0% below the $100,000 peak.
- Today's session is logged and rebalanced; the missed list did not grow (still only 2026-11-19).
- No code change to the order or logging path since the last review; the owner's commits were research studies, the network lab and workflow additions, not repairs.
- test_monitor.py passes. test_model.py and track.py could not get prices: this sandbox is refused by Yahoo Finance (403), so the model side of track.py reads 0% (live +1.01% over 2 days). Not a defect.
- Nothing to fix.
