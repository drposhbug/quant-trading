# Versions

How this project changes, what version is running, and how to ask for a change. The full record with every test
is the change log in [MATH.md](MATH.md); this page is the short form.

## How a change is made here (and how Tesla does it)

Tesla numbers every release of its driving software (12.3.6 means generation 12, third model update, sixth fix).
A new version is trained on data from the cars, checked in simulation, and then run in **shadow mode**: it rides
along making its own decisions without controlling anything, and its decisions are compared with what actually
happened. Only then is it released, to a few drivers first and then to everyone, with release notes, and it is
pulled back if it misbehaves.

This project uses the same four stages, and a version cannot skip one:

| Stage | Tesla | Here |
|---|---|---|
| 1. Write it down | the change and what it is meant to fix | the rule and the bar it must clear, committed to the repository before any result exists |
| 2. Test on recorded data | simulation and replayed drives | the past test: each past day's decision rebuilt using only what was known that day |
| 3. Shadow | runs in cars without controlling them | makes its calls every day after the close; they are scored when they come due; nothing trades |
| 4. Release | staged rollout, with rollback | switched on in the bot only after passing the bar three monthly reviews running, or by the owner's choice for a risk setting; the old version stays one switch away |

## How to ask for a change

Say it in a sentence, for example "hold less after bad news" or "use earnings". Then:

1. It gets the next version number and its rule is written and committed first.
2. It is tested on the past the same day and the result is reported, pass or fail.
3. Pass or fail, it runs in shadow so new days can confirm or contradict the past.
4. Nothing reaches the bot without stage 4.

Three things that are never done, because they are how a model fools its owner: changing a rule after seeing its
result and keeping the old score; testing many variations and reporting the best; switching something on in the
middle of a loss to make the loss stop.

## The bot (what trades the paper account)

| Version | Date | What changed | Status |
|---|---|---|---|
| B1.0 | 2026-11-19 | Frozen model: inverse-volatility weights, 20% volatility target, cuts exposure when the market trend turns down | retired 2026-11-21; kept as the comparison |
| B2.0 | 2026-11-21 | Fully invested, no volatility target (owner's decision, by growth odds) | superseded |
| **B2.1** | 2026-11-23 | Trend tilt: twice the weight in the third of names with the strongest 12-month trend, half in the weakest third. No orders while the market is closed | **live** |
| B2.2 | 2026-11-23 | Half of every position for 21 sessions after a market shock. On the past: worst fall 25% against 36% (31% against 41% on the current names), worst day halved, 0.8% a year less growth | shadow; the owner's choice |
| B2.3 | 2026-11-23 | Half weight after a shock only in the names that fall hardest. On the past: worst fall about 4 points smaller, growth 0.0% to 1.8% a year lower | shadow |

Rejected on the past and not kept: five selling rules, closing out completely after a shock, selling a stock after
its own shock, dropping the tilt after a shock or when wild, trimming the hardest-falling names all the time.
The bot re-tests its own settings each month (learn.py) and the daily shadow is in
[reports/shadow_versions.md](reports/shadow_versions.md).

## The machine (the research model; it never trades)

| Version | Date | What changed | Result on the past | Status |
|---|---|---|---|---|
| M1 | 2026-11-23 | Small neural network on 14 textbook inputs, retrained monthly | failed (grows faster than the live book in 7% of simulated histories) | shadow; four experiments queued for the Saturday routine |
| M2 | 2026-11-23 | Pattern-finder: picks its own 10 of 945 patterns, ten stocks | failed (33%); its finds could not be told from luck | shadow |
| M3 (calls v2) | 2026-11-23 | About 500 stocks, a luck bar, three horizons, a probability on every call | nothing passed | replaced |
| M3.1 (calls v3) | 2026-11-23 | Every result measured from the next open, the first price anyone can trade at | nothing stands out at any horizon | replaced |
| **M4 (calls v4)** | 2026-11-23 | Every company that was in the index on the day, dead ones included; market and sector moves taken out; one learner that speaks only when the whole crowd of patterns beats luck; trend on calm days; separate entries for profitability and busy/quiet months | nothing passes; nearest is the trend on calm days (right 18 of 30 times over 21 sessions) | **running in shadow**: [reports/daily_calls.md](reports/daily_calls.md) |
| M4.1 | 2026-11-23 | Earnings surprise and about-to-report entries added to M4 | nothing passes (surprise right 36 of 73; about to report 192 of 353, a coin gets 158 to 195) | in shadow from the next daily run |

Tested once as stand-alone ideas, all with no pattern: direction after a stock's shock, after a market shock, in a
shocked stock's sector peers, after opening 10% down, with or without a company announcement behind the move;
short interest; profitability; busy/quiet month (the wrong way round); holding less of the names that fall hardest
(weaker than halving everything).

## What keeps it learning

- **Every weekday after the close** (GitHub job `mlp-log`): the machine re-reads every pattern's record with the new
  day in it, makes its calls, scores the calls that have come due, and updates the probabilities. The candidates
  of the bot are tracked in shadow.
- **Every Friday**: profitability figures are refreshed from new SEC filings.
- **Every Saturday** (Claude routine): the queued experiments on the network, then a check that the daily logs
  are complete.
- **Early each month** (learn.py): the bot re-tests its own settings and every challenger against bars fixed in
  advance; a setting changes only after three reviews in a row agree.
