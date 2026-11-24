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

## 2026-11-23, evening (by hand): why the pattern-finder failed, and the daily calls

- Why it failed, checked on its own run. The ten patterns it trusted each month had worked in their own past
  (rank IC +0.108) and did nothing in the month that followed (+0.003). When every stock was handed another
  stock's future, it "found" patterns that looked just as good (30% of those shuffles looked better than the real
  thing). With ten stocks, luck's best ten out of 945 tries always look convincing. Grok's review agrees and adds
  that the multiplied pairs made the contest easier to win (research_notes/mlp loop/round 3.md).
- The fix is not another test on old years; those are used up. It is a rebuilt machine that is judged only on
  days that have not happened: daily_calls.py. About 500 stocks instead of ten, no multiplied pairs, and a noise
  bar: a pattern gets a vote only by how far its record beats what the best of 345 patterns reaches by luck.
- Every day after the close it ranks the stocks for the next 21 sessions (the official board), the next 5 and
  the next 1, and logs which third it favours and which it avoids, for the market and for the bot's own names.
  When a call comes due it is marked right or wrong. A plain 12-month trend ranking is scored beside it.
  The page to read is reports/daily_calls.md.
- First dry run, before any real call: at 21 and 5 sessions the strict entry had no view, because nothing stood
  out from luck. At 1 session it trusted 13 patterns, and all 13 are versions of the 12-month trend the bot
  already uses. A second entry, "best guess", was added so there is a call to watch every day; it uses patterns
  that stand out one at a time (7 at 21 sessions, about what luck alone gives; 24 at 5; 75 at 1).
- No verdict before 20 non-overlapping official calls, about 20 months. Until then the page says "too early".

## 2026-11-23, night (by hand): the past test, probabilities, and counting the crowd

- The owner asked why wait 20 months when all of the past is there. Fair: the machine's record on the past is now
  the first verdict. Every fifth session since 2019 each call was rebuilt with only what was known that day and
  checked against what followed. New days now only confirm or contradict it.
- Result: no entry passes. For the next 21 sessions the best guess was right 31 times in 73 (a coin gets 28 to
  45). For the next 5 it was right 180 times in 366. The nearest miss is the strict entry's next-session calls:
  right 76 times in 124 (61%, more than a coin's 51 to 73), but its wins were small and its losses large enough
  that the average gain is not clearly above zero. It is marked "fails", with that reason.
- Every call now carries a probability, and each of the bot's stocks a chance of beating the typical stock.
  They come from that same past record, pulled toward 50%, and every real result from now on moves them. They
  are all near 50% (47% to 53% for the stocks), because that is what the record supports. The probabilities are
  checked as well: when it says 53%, did it happen about 53% of the time?
- The owner's point that many lucky-looking things at once may be one real thing nobody proved is now counted
  every day. On 2026-11-23, for the next session, 75 patterns stood out one at a time where luck rarely gives more
  than 43: something real is there, and it is mostly the 12-month trend seen through many windows. For the next
  5 and 21 sessions the counts (24 and 10) are inside what luck gives.

## 2026-11-23, late (by hand): the research round, and the clock

- The owner asked for research on how to make the machine smarter: five Opus researchers, Astra and Grok, and our
  own numbers. The decision is in reports/Making the machine smarter (2026-11-23).md.
- The most important finding is about the clock. The machine makes its calls after the close but was scoring
  them from that close, a price nobody can trade at once it is known. The trend's whole next-session edge sat in
  the step from the close to the next open. Measured from the next open (rules v3), nothing stands out at any
  horizon. The trading bot acts at 15:30, before the close, so this does not take away the bot's trend.
- Why the machine was nearly blind: its 332 patterns are about 9 ideas, and 500 stocks behave like about 28,
  because every ranking rides the market and the sectors. Real edges in large companies are smaller than the
  smallest it could see. Stripping out the shared moves is the largest gain available and needs no new data.
- News and Trump: shocks reliably predict how large the next moves will be, for weeks, and which stocks react
  most. They do not predict direction, in our data or in the published studies.
- New days are now judged by a running evidence score that can be read every day (1 is nothing, 20 confirms).

## 2026-11-23, last entry of the day (by hand): closing out on news, and the machine rebuilt (v4)

- "See the news and close out." Tested on the bot's own book with six rules written first
  (reports/news_stop_odds.md). Closing out completely after a shock barely helps: on the market's 37 worst
  shock days half of the fall had already happened by the open, and over the next 5 sessions the market was up
  67% of the time. What does lose less is holding half the book for a month after any market shock: the worst
  fall was 25% instead of 36% (and 31% instead of 41% on the bot's current names), the worst single day was
  halved, and it cost 0.8% a year of growth. That is the owner's choice; it is not wired into the bot.
- News direction is now closed on daily data. A stock's own shock, a market shock, and (Grok's idea) the
  shocked stock's sector peers: none predicts direction. The size of later moves is strongly predictable.
- The machine was rebuilt as version 4: every company that was in the index on the day, including the dead
  ones; market and sector moves removed; one learner that only speaks when the whole crowd of patterns beats
  luck; the trend standing aside when it has been wild; and separate entries for new information.
- Its record on the past: nothing passes. The nearest is the trend on calm days (right 18 of 30 times over 21
  sessions, with milder worst cases). "Busy month keeps going" went the wrong way. Profitability showed
  nothing. The learner had no view at 21 or 5 sessions on any old day.
- Removing the shared moves made the instrument sharper, though less than hoped: the list is now worth about 74
  independent stocks, up from about 28.
- Still to come: the two earnings entries, when the earnings file has finished downloading.
