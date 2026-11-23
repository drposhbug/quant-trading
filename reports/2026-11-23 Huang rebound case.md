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

## End-of-day update (broker records and closing prices, 2026-11-23 after the close)

These replace the midday estimates above.

| Book held at Friday's close | Monday, close to close |
|---|---|
| Frozen rules (33.7% invested) | +2.55% |
| The account (39% held, then bought to 96% at the open) | **+2.79%, +$2,653, to $97,628** |
| Fully invested at Friday's close (99%) | +7.49%, about +$7,110 |
| Equal-weight basket / QQQ | +8.62% / +7.00% |

- QQQ opened +7.81% and closed +7.00%: the whole gain was the opening gap. NVDA opened +33.1% and closed +31.5%.
- Friday's holdings made +$2,994. The $55,040 of stock bought at 09:31–09:38 was down $445 by the close.
- Against being fully invested at Friday's close, about $4,460 was missed.

| | 19–23 Nov (the account's three sessions) | Since the 6 Oct peak |
|---|---|---|
| QQQ | −1.29% | −14.30% |
| Frozen rules (backtest) | −0.96% | −13.79% |
| Fully invested basket (backtest) | −2.14% | −13.75% |
| The account | −2.37% | not live |

Over the round trip the frozen rules are ahead of the fully invested basket: they saved more on 19–20 November than
they gave up on the 23rd. The account trails both because of the two set-up errors (1.6 points) and the purchases at
the open.

After the 49 Nasdaq-100 days of +6% or more since 1985 (84% of them below the 200-day average, 28 in 2000–02), the
index was higher 21 sessions later 49% of the time (median −0.3%), 63 sessions later 57% (median +2.7%, worst −46%)
and 252 sessions later 51% (median +7.8%, worst −59%, best +115%). The eight since 2009 were all followed by gains.

At the close the account is 96% in stocks; the frozen rules would hold 31%. QQQ is 4.6% below its 200-day average.
Independent reviews by Astra 6.2 and Grok: `research_notes/2026-11-23 rebound/astra_grok_verdicts.md`.

Timing, from Grok's sourced timeline (`research_notes/2026-11-23 rebound/grok_news_timeline.md`): Nvidia's release
came at 08:55 ET on Monday; the board had voted on Sunday. From 04:00 to about 08:50 ET Nvidia traded only 7–9% above
Friday's close and Nasdaq-100 futures about +3.5%; after 08:55 the futures hit their 7% limit and were halted until the
bell. The queued orders were regular-session market orders, so they waited for 09:30 and paid on average 8.1% above
Friday's closes on the $55,040 (about $4,450, nearly the whole shortfall). Pre-market limit orders were the only way to
have caught part of it after Friday's close.
