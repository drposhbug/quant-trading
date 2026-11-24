# Attack this decision

You are an independent reviewer. A research project (paper money) ranks about 500 US large-cap stocks after each close for the next 1, 5 and 21 sessions, from 332 price-and-volume patterns on daily data since 2016. Tonight it took its own results apart and decided what to build next. Find what is wrong with the findings and the plan. Mark opinions and give probabilities.

## Findings

1. The only pattern that ever stood out from luck was 12-month momentum, and only for the next session. Favouring the top third by it was right on 55.2% of 2,338 days with a median of +8.7 bp, a mean of +0.6 bp and a skew of -1.4: the worst 5% of days lose 310% and the other 95% make 323%. The worst days are news days (the session after the Pfizer vaccine news of 2020-11-09 cost 13.3%).
2. Split by time of day, the edge is all overnight: close to next open +2.8 bp a night (t 2.5); next open to close -2.2 bp (t -1.3).
3. The machine makes its calls after the close but scored them from that close. Re-scored from the next open, nothing stands out at any horizon, and the momentum ranking is right 48% of days.
4. The 332 patterns are about 9 independent ideas (participation ratio of the eigenvalues of their block-IC correlation). One day's rank IC has a standard deviation of 0.19, against 0.045 if the 500 stocks were independent, so the cross-section carries the information of about 28 independent stocks. The smallest mean IC detectable at 21 sessions is 0.025 for one hypothesis chosen in advance and 0.043 for the best of 332.
5. Shocks (a stock moving more than 3 of its normal daily moves on double volume: 11,041 cases; the market moving more than 2.5: 83 days) predict the SIZE of later moves (stock: 1.9 times normal next session, 1.25 times over the month; market: twice normal for a month) and which stocks react most (rank correlation 0.40 with their previous ten shocks). They do not predict direction: every t is below 1 in size, except the market after an up-shock, -0.83% next session, t -1.6, 29 cases. A test of 13,731 presidential posts against megacap stocks found nothing.
6. Scaling the momentum bet down when its own 126-session volatility is high lifts its t from 0.25 to 0.96 and its skew from -1.4 to -0.6.

## The plan, in order

(a) Score everything from the next open (done). (b) Add the dead companies to the stock list. (c) Remove market, sector and style from patterns and outcomes, to turn 28 effective stocks back toward several hundred. (d) Combine patterns as about 9 families with empirical-Bayes shrinkage, weight = t x max(0, 1 - null variance / observed variance), instead of thresholded votes. (e) Volatility-scale momentum. (f) Add new information one pre-registered test at a time: earnings dates and surprises (SEC 8-K timestamps, Nasdaq calendar), profitability from SEC XBRL, last month's return split by turnover, headline counts from a news feed. (g) Use shocks to widen probabilities and cut size, never for direction. New days are judged by an anytime-valid evidence score that confirms at 20.

## Questions

1. Which finding is most likely an artefact, and what check would expose it?
2. Is step (c) right? What exactly should be removed, and what does over-neutralising destroy?
3. The overnight result: is it tradeable by an account that can send market-on-close and market-on-open orders, after realistic costs for large caps? Give your arithmetic.
4. The owner believes news reactions (Tesla is his example) and presidential statements "must be a statistical pattern". What is the strongest version of his idea that we have NOT yet tested, with free daily data?
5. What is the one thing missing from the plan, and what would you delete from it?
6. Your probability that the finished plan produces anything that beats volatility-scaled momentum after costs.

Answer in Markdown, at most 600 words. Write your complete answer as your reply.
