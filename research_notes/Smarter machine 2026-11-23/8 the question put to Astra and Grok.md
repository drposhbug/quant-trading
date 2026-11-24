# First principles: what is happening in this data, and what is the right way to build a learner on it?

You are an independent reviewer and a mathematician. Reason from first principles, derive rather than assert, and disagree with the set-up wherever it is wrong. Mark opinions as opinions and give probabilities.

## The system

A research project (paper money only) ranks about 500 US large-cap stocks (the S&P 500 members of a fixed date, so survivors only) after every close, for three horizons: the next 1, 5 and 21 sessions. Data: Alpaca adjusted daily open, high, low, close, volume, 2016-01 to 2026-11, about 2,740 sessions.

It builds 345 patterns per stock per day, each a z-score across the names: returns over 5 to 252 sessions with or without the latest 5 or 21, split into overnight and daytime parts; daily range, volume against its 60-day normal, close location in the range (levels and short-against-long); skew, largest one-day gain and loss, share of up days, downside against upside variance, one-day autocorrelation; distance from rolling highs, lows and averages; return-volume correlation; for each of 15 outside series (SPY, IWM, EEM, TLT, IEF, HYG, GLD, USO, UUP, XLK, XLF, XLE, SMH, VIXY, QQQ): rolling correlation over 63/126/252, its change, beta, beta-adjusted residual return over several windows, beta times the series' recent move; correlation with the other names and one-day lead and lag.

For each pattern and horizon: a daily rank IC across the names against the forward return. ICs are averaged in blocks (21 sessions, or 5 for the two short horizons) and summarised as t = sum of block means / sqrt(sum of squared block means). Luck is measured by re-signing the blocks at random 500 times, the same signs for all patterns (so correlation between patterns is kept). The bar is the 95th percentile of the largest |t| across the 345 under re-signing; it comes out near 3.5 at every horizon.

Three entries make a call each day (top third of the ranking is favoured, bottom third avoided; a call is right when favoured beats avoided over the horizon):
- "sure": a pattern votes with weight max(|t| - bar, 0), signed, and not at all if its latest 252 sessions disagree in sign. No voter means no view.
- "best guess": the same with the bar set to 2.
- "trend": the single pattern "return over 252 sessions leaving out the latest 21", divided by 60-day volatility.

## Results

Count of patterns with |t| above 2, with luck's typical count and its 95th percentile under re-signing:
- 1 session: 75 (luck 8, rarely above 43)
- 5 sessions: 24 (luck 8, rarely above 60)
- 21 sessions: 10 (luck 9, rarely above 46)

What "sure" trusts today: nothing at 21 or 5 sessions. At 1 session, 13 patterns with t from 3.5 to 4.2, all of them the 12-month return leaving out the latest month, raw or with one outside series' beta removed (strongest: residual against small caps, t 4.2).

The record on the past: every 5th session from mid-2019, each call rebuilt using only what was known that day. Non-overlapping calls on the 500 names (mean spread is favoured minus avoided, before costs):

| Horizon | Entry | Calls | Right | Mean spread | t of mean |
|---|---|---|---|---|---|
| 21 | sure | 4 | 2 | -1.12% | -0.7 |
| 21 | best guess | 73 | 31 (42%) | -0.44% | -1.0 |
| 21 | trend | 73 | 39 (53%) | -0.23% | -0.5 |
| 5 | sure | 26 | 8 (31%) | -0.45% | -1.5 |
| 5 | best guess | 366 | 180 (49%) | -0.06% | -0.8 |
| 5 | trend | 366 | 192 (52%) | -0.02% | -0.1 |
| 1 | sure | 124 | 76 (61%) | +0.14% | +1.5 |
| 1 | best guess | 367 | 197 (54%) | +0.04% | +0.8 |
| 1 | trend | 367 | 194 (53%) | -0.02% | -0.3 |

On the bot's own 12 megacap tech names, same calls: trend at 21 sessions right 44 of 73 (60%), mean +0.70%, t 0.8; sure at 1 session right 68 of 124, mean +0.40%, t 1.7.

Per-stock probabilities of beating the median stock, calibrated by tenth of the ranking on the same rebuilt past: every one lies between 47% and 53%.

An earlier version on only 10 names, choosing the top 10 of 945 candidates (the 345 plus 600 random products) by "same sign in two halves", failed: the chosen patterns had rank IC +0.108 in their own past and +0.003 in the following month, and shuffled outcomes produced equally convincing picks.

About 1,150 earlier tests on 12 megacap tech names (macro, earnings, insider trades, short interest, news, prediction markets, lead-lag, candles) found nothing beyond the slow trend.

## Constraints

Free data only. numpy, pandas, scipy. A GitHub Actions job of a few minutes after each close. The 2019 to 2026 record has been read once for these three entries. A clean point-in-time S&P 500 membership list with dead companies (closes and volume from 2016) exists locally. The owner is not a statistician; he wants the machine "smarter and more efficient" and asked for first-principles thinking and new mathematics where it is warranted.

## Questions

1. **Decipher.** From first principles, what do these numbers say is going on? Explain, with a mechanism and a check on existing data for each: (a) a ranking right on 61% of days whose mean is not reliably positive; (b) 12-month patterns clearing a luck bar at the 1-session horizon but not at 5 or 21; (c) the best guess landing below 50% at 21 sessions; (d) luck ranges as wide as "typically 8, sometimes 60"; (e) the trend doing better on 12 megacaps than on 500 names.
2. **The limit, derived.** For N names, daily rank-IC noise sigma, horizon h, T days and K candidates with effective number K_eff, derive the smallest true mean IC that can be told from luck. Evaluate it for N of about 500 and T of about 2,300 at h = 1, 5, 21, stating your assumed sigma. What does it imply about which horizons and which kinds of information can ever show up here? What N or T would be needed to see an IC of 0.01, 0.02, 0.03?
3. **The right estimator, derived.** Replace weight = max(|t| - bar, 0). Derive the weights that minimise forecast error given 345 correlated t-values, most of them noise: two-groups or empirical Bayes, Tweedie's formula, and the role of the correlation between patterns (the block matrix B of shape 345 x blocks is stored, and so are the re-signing draws). Give formulas that can be coded directly in numpy. Would it have changed the results above, and how would we know without re-reading the same past as a second test?
4. **New mathematics, if warranted.** (i) A better yardstick than hit rate and t-of-mean for a negatively skewed bet. (ii) A test for the new-days stage that permits looking every day without inflating luck: the exact process, boundary and expected sample size for true hit rates of 53%, 55% and 60%. (iii) The exact map from a rank IC to a per-stock probability of beating the median. (iv) Anything else you would derive.
5. **Information.** Rank the five kinds of free, point-in-time data most likely to add real information independent of price for about 500 US large caps at 1 to 21 sessions. For each: the exact free source, your probability that it shows a real effect here, and the rank IC you would expect.
6. **Efficiency.** What should be deleted? Which parts waste compute, and which waste statistical power?
7. **Your prior** that anything built here ever beats the plain trend after costs, and what you would do with the same effort instead.

Answer in Markdown, about 1,200 words, formulas in plain text or LaTeX. Write your complete answer as your reply.
