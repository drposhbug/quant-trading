# Case study: the 2026-11-23 rebound (Huang reinstated at Nvidia)

## What happened

| When (ET) | Event | Source |
|---|---|---|
| Fri 11-20 close | Selloff day: NVDA −14.0%, AMD −13.3%, AVGO −12.2%, QQQ −5.7%. Bot (frozen rules: vol target + risk-off halving) rebalanced to **34% invested**. Equity $95,084. | signals/equity_log.csv |
| Sat 11-21 | Owner switches the live book to fully invested (MATH.md change log, `LIVE`). Orders queued for Monday's open. | monitor.py |
| Sat 11-21 19:34 | Last bot pass of the weekend. Polymarket: "Jensen Huang rejoins NVIDIA by Dec 31" = **6.7%**; "by Nov 30" = **1.9%**. | signals/prediction_markets.csv |
| Sun 11-22 17:20 | Trump: market down $6T since the midterms, NASDAQ −20%. | trumpstruth.org |
| **Sun 11-22 21:54** | **Trump: "I hope the Board of Nvidia rehires Jensen Huang."** No bot pass was scheduled, so no alert and no odds snapshot. | trumpstruth.org |
| Mon 11-23 pre-market | Nvidia board reinstates Huang. Nasdaq-100 futures +7%, hit the limit and halted. Trump (09:07): "correct and proper decision." | Reuters, WSJ, Bloomberg headlines |
| Mon 11-23 09:30 | Open: NVDA **+33.1%** gap, TSM +21%, ORCL +15%, QQQ +7.8%. Queued dip buys fill **after** the gap. | yfinance |
| Mon 11-23 midday | Most names below their open: TSM −4.5%, AMD −3.6%, NVDA −1.5%, QQQ −0.6%. The new money is flat to slightly down. | yfinance |

## The money

| Book at Friday's close | Invested | Monday P&L (close-to-close, est.) |
|---|---|---|
| What ran (frozen rules) | 34% | **+2.8% ≈ +$2,640** |
| New all-in rules, had they run Friday | 99% | **+8.2% ≈ +$7,750** |

Roughly $5,100 of the rebound was missed. That is not because the dip wasn't bought. The buy decision came after the last
pre-rebound price (Friday's close), and the whole rebound happened while US stocks were shut.

## What we learn, and what we deliberately don't

**Don't learn:** "after a crash, buy." One rebound is one data point. The selloff post-mortem
(`selloff_postmortem.py`) tested every predictor we have across past selloffs and none of them separated rebounds from
deeper falls. The prediction market gave this outcome 6.7%. It was a genuine surprise. Writing a rule from it would be
fitting to noise.

**Do learn (process, not prediction):**

1. **Being out of the market during a selloff risks missing gap rebounds.** This is well documented: the best days
   cluster next to the worst days. It is the trade-off the owner accepted on 11-21 by going all-in. Under the new rules
   the money is already invested before any rebound. The cost is riding the full fall if there is no rebound.
2. **Weekend blind spot. Fixed 2026-11-23.** The decisive signals (Trump's Sunday-night post, and any Polymarket move
   after it) arrived while no run was scheduled. monitor.yml now also runs hourly on weekends and weekday nights. Those
   off-hours passes only snapshot odds and send alerts; they never trade.
3. **Weekend decisions fill late.** A discretionary change made Saturday can't trade until Monday 09:30 unless orders
   use Alpaca's overnight session (Sun 20:00 – Mon 04:00 ET, limit orders only). Not built yet; owner's call.

## Pre-registered test (from today, before seeing any more data)

**H1:** When a stock-specific Polymarket/Kalshi market moves ≥ 15 points while US stocks are closed, the stock's next
open gaps in the direction implied by the move.

- **Data:** the off-hours snapshots that now accumulate in `signals/prediction_markets.csv`.
- **Test:** sign test plus mean gap vs the stock's normal open-gap size, once there are ≥ 20 events. Holm-correct if other
  thresholds are tried.
- **Pass:** p < 0.05, the same sign in both halves of the events, and a mean gap larger than the round-trip cost of
  trading in the overnight session.
- **Until it passes:** alerts only, no trading.
