# Grok: are we looking through the wrong lens? (2026-11-23)

The owner asked whether the project was simply not looking through the right lens for correlation. The question put to Grok is the first part of this file; its answer follows, unedited.

---

# Are we looking through the wrong lens?

You are an independent reviewer. A research project on about 500 US large-cap stocks (S&P 500 members by date, dead companies included; adjusted daily open, high, low, close, volume since 2016; free data only; a retail-sized account that trades once a day) has tested many ideas and found almost nothing. Its owner asks: "Is it possible you are just not looking through the right lens for correlation?" Answer him seriously.

## The lens used so far

Nearly every test asked one question: does some number known today line up, across stocks, with which stocks do better than the others over the next 1, 5 or 21 sessions? Measured by rank correlation across the stocks each day, or by the top third minus the bottom third, or by an event basket against the average stock.

## What that lens found

- 332 price-and-volume patterns (trends, ranges, volume, skew, correlations with 15 outside series, lead and lag): only 12-month momentum stood out, and its whole edge sits between the close and the next open (+2.8 bp a night, t 2.5; -2.2 bp in the daytime). It wins small on 55% of days and loses it back on a few news days.
- From a tradeable price (the next open), nothing stands out at any horizon. Momentum only on calm days is the nearest miss: right 18 of 30 times over 21 sessions, t 1.7.
- Events: after a stock's own shock, after a market shock, in a shocked stock's sector peers, after opening 10% down, and after big moves with or without an SEC 8-K filing behind them: no direction. One reading: stocks that open more than 10% up then lag (t -3.3, fading in recent years).
- Non-price: gross profitability, short interest (days to cover, from publication dates), last month's return split by trading activity: nothing. Earnings surprises are still to be tested.
- What IS strongly predictable: the size of moves. After a stock's shock its moves run 1.9 times normal the next day and 1.25 times for a month; after a market shock the market moves twice its normal size for a month; which stocks react most repeats (rank correlation 0.40).
- Taking out market and sector moves raised the cross-section's effective size from about 28 independent stocks to about 74.

## The question

1. Name the other lenses: different ways two things can be related that this lens cannot see. For each, say in one or two plain sentences what it is and what it could find here that the rank-correlation lens misses. Think widely: what is being predicted (not only direction), over what unit (stock, pair, sector, the whole market), under what condition (state of the market, time of day, time of year), in what shape (thresholds, tails, U-shapes), and through what link (who is forced to trade).
2. Rank the five lenses most likely to show something REAL and USABLE by this account with this data. For each give: the exact test in two or three sentences, what result would count, your probability that it shows something real, and how it would be used (to pick stocks, to size positions, to time the market, or to avoid losses).
3. Which lenses are popular but would only produce false discoveries here?
4. If the honest answer is that the owner is partly right, say where. If it is that there is nothing more in this data, say that and say what the data is still good for.

Answer in Markdown, at most 600 words. Write your complete answer as your reply.


---

# Grok

Almost every test asked whether a number known today ranks stocks by relative return over the next 1, 5, or 21 sessions. Other relations can be large and still score zero on that test.

### Other lenses

- **Shared drift.** A gain common to every stock, including the overnight market, produces no cross-sectional ranking.
- **Time of day.** Close-to-open and open-to-close are different targets. Your momentum edge sits in the night.
- **Magnitude.** How big the next move is. After shocks, ranges stay wide from a day to a month.
- **Dependence.** Which names amplify a selloff. Who reacts most already repeats (rank correlation 0.40).
- **Shape.** Tails and U-shapes, where both extremes agree and a straight rank cancels.
- **State.** A link only in calm markets, or only among quiet stocks, which the average day washes out.
- **Unit.** A pair, a sector basket, or the index as one series.
- **Forced trading.** Index adds and deletes, month-end rebalancing, December tax-loss sales: a few dated orders a year.
- **The jump.** An earnings surprise, or a change in short interest.

### Five tests, by chance of a real usable result

Prewrite each rule. Require both halves of the sample to agree after 1–2 bp each way.

1. **Volatility scaling. Probability ~0.80. Sizes positions.** Forecast the next 1-day and 21-day absolute move from trailing range plus a shock flag, and divide size by that forecast. It counts if later years beat a constant-vol book and the worst drawdown drops sharply. After a market shock, stay smaller for a month.

2. **Earnings calendar. Probability ~0.70 for range, ~0.25 for direction. Avoids losses; picks stocks only if direction lasts.** Compare the five days before a report, and the day after, with other days. Long published beats and short misses from the next open, sector-neutral, for 21 sessions. Cut size when both halves show wider ranges. Count direction only if post-2021 pays; the announcement night is already past.

3. **Downside beta. Probability ~0.65. Avoids losses.** On days the market falls more than 1%, record each stock’s sensitivity and forecast the next such day. It counts if later rank correlation stays above about 0.3. When forecast volatility is high, cut the names that magnify selloffs.

4. **Overnight drift of the basket. Probability ~0.55. Times the market.** Mean close-to-open versus open-to-close, equal-weight and cap-weight, split around 2021. It counts if the night stays positive in both halves after 2 bp. Buy the close, sell the open.

5. **Index adds and deletes. Probability ~0.35. Picks stocks.** From the first open after the announcement through the effective date, versus sector peers. It counts if adds lead and deletes lag in both halves, net of cost. A few names a year. An index fund is the forced trader.

### Lenses that manufacture false edges

Refitting the 332 scores, including with machine learning, redoes a finished search. A best t of 2.5 is what that width produces when nothing is real. Night versus day on momentum is a second look at the same winner; require unused years. The same bin holds calendar scans, new gap cutoffs, calm-day filters (t 1.7), per-stock seasons (~10 observations), every pair among 500 names, and macro timing from 15 series.

### Verdict

You are partly right. Shared night drift, move size, crash sensitivity, U-shapes, and forced index trades sit outside a cross-sectional rank. What is usable is risk: scale to forecast volatility, and hold less of the names that magnify selloffs.

Daily stock-picking in this file is finished. Large caps since 2016, bought at the next open, have been a dead heat. Give earnings surprises and index changes one prewritten test each. If the later half fails, no directional signal remains. The file is still the right tool for sizing, for night versus day, and for retiring ideas.
