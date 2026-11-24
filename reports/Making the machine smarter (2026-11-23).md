# Making the machine smarter: what is happening, and what to build

2026-11-23. Five Opus researchers (data, evidence, mathematics, market mechanics, news), a first-principles review by
Astra 6.2, and our own numbers on about 500 stocks since 2016. Their notes are in
`research_notes/Smarter machine 2026-11-23/`. This page is the decision. Grok's attack on it is summarised at the end.

## The decision

The machine does not need more patterns. It has one real finding, it has been measuring it at a price nobody can
trade, and it hears the market through so much shared noise that it could not see a real edge of normal size even if
one were there. So the order is: make the measurement true, make the instrument sharper, and only then feed it new
information, one pre-registered test at a time. News is used for how big a move will be, not which way.

## What is actually happening

1. **There is one real thing: the 12-month trend, and it is an overnight effect.** Favouring the top third of 500
   stocks by 12-month trend was right on 55.2% of 2,338 days. Split the next session in two: from the close to the
   next open it earned +2.8 hundredths of a percent a night (t 2.5); from the open to the close it lost 2.2.
2. **It wins small and loses big.** The worst 5% of days lost 310%; the other 95% made 323%. The worst days are
   news days: the session after 2020-11-06 (the Pfizer vaccine) cost 13.3%, the CPI surprise of November 2022 5.5%.
3. **Measured from a price you can trade, the machine has nothing.** Its calls are made after the close. Scored
   from the next morning's open (rules v3, fixed tonight before any call was scored), no pattern stands out at any
   horizon and the trend ranking is right 48% of the time for the next session. The edge sat in the overnight step
   the machine was missing. The trading bot acts at 15:30, before the close, which is why it can earn the trend.
4. **332 patterns are about 9 ideas.** Most are near-copies. That is why "luck" could produce anything from 8 to
   60 standouts at once.
5. **500 stocks behave like about 28.** If stocks moved independently, one day's ranking score would wobble by
   0.045. It wobbles by 0.19, because every ranking rides the market, sectors and styles. Power goes with the
   square, so 500 names give the information of about 28.
6. **So real edges are below what it can see.** For the next 21 sessions the smallest edge it could detect is a
   ranking score (rank IC) of 0.025 for one idea chosen in advance and 0.043 for the best of the lot. Published
   edges in large companies are 0.01 to 0.02.
7. **The edge does not build with time.** Against the next 1, 5 and 21 sessions the trend scored 0.0175, 0.0147
   and 0.0062. A lasting drift would have grown to about 0.04 and 0.08. The big-loss days eat it.

## News and Trump: what is a pattern and what is not

| Belief | What the numbers say |
|---|---|
| News makes stocks move more, for a while | **Real and strong.** After a stock's own shock day (11,041 cases) its moves are 1.9 times normal the next session, 1.5 times for the week, 1.25 times for the month. After a market-wide shock (83 since 2017) the market moves about twice its normal for a month. |
| Some stocks are more news-sensitive | **Real, and stable.** Which stocks react most on market shock days repeats (rank correlation 0.40 with their previous ten shocks). |
| Tesla is special | **No.** Tesla is always volatile (55% a year against 25% for the typical stock), but it has shock days about as often as others once that is allowed for, and a study of 3,158 Musk tweets found no effect on its price. |
| After the shock, the direction is predictable | **No.** Next session after a stock's up-shock: +0.07% (t 0.8); after a down-shock: -0.01%. The hardest-hit stocks did not bounce or keep falling reliably. |
| Trump moves the whole market | **He raises volatility: yes.** April 2025's tariff days are among the largest shocks in the data. **Predictable direction: no.** Our earlier test of 13,731 posts found nothing, and the research found no study that does. "Sell-off, then he backs down" rests on fewer than ten episodes, all decided by one man; in 2018-2019 the market fell 11.5% over 11 trade-war days and did not rebound the next week. |

Use: a shock tells the machine to trust itself less and hold less, because the next moves will be larger. It does not
tell it which way.

## What to build, in order

Done tonight: outcomes measured from the next open; a running evidence score for new days that can be read daily.

1. **A true stock list.** Add the companies that died or were dropped since 2016 (the dated list exists locally).
   Today's list flatters every test.
2. **Strip out the shared moves.** Remove market, sector and style from both the patterns and the outcomes, so the
   machine ranks what is particular to each stock. That turns "about 28 stocks" back toward several hundred and
   brings 21-session edges of normal size into view. No new data. The largest gain available.
3. **Nine families, shrunk, not 332 votes.** Combine the patterns as a few independent ideas, each weighted by how
   far the whole crowd's record exceeds luck (formula below). A horizon with nothing switches itself off.
4. **Crash control.** Hold less of the trend when the trend bet itself has been wild: its t went from 0.25 to 0.96
   and its lopsidedness halved on our data; published big-company results agree in direction and are also weak.
5. **New information, one test at a time, each with rules written first.** In this order:
   earnings dates and surprises (free: SEC filing times and Nasdaq's calendar, both checked by live calls);
   profitability from SEC filings (slow and cheap to trade; +0.28% a month in big companies since 2016, not yet
   significant); last month's return split by how heavily the stock traded (prices and volume only); headlines
   from the Alpaca news feed, to tell a move with news from a move without.
6. **A shock state** from prices and the free policy-uncertainty indices: widens the probabilities and cuts size.

## What to stop

More price patterns, multiplied pairs, picking the top few. Next-session calls as a trading idea: at this edge the
turnover costs 7 to 9 hundredths of a percent a day, more than the edge. Predicting direction from posts. Options
signals, short-sale volume, insider trades, fund flows, lead-lag between stocks: the evidence for large companies is
gone or was never there.

## The mathematics, in plain words

- **How many ideas?** K = (sum of λ)² / (sum of λ²), over the eigenvalues λ of how the patterns' scores move together. Here 9.
- **How many stocks, really?** N × (0.045 / 0.19)², the square of ideal wobble over seen wobble. Here 28.
- **Smallest edge it can see:** c × (wobble of one block) / √(number of blocks), with c = 2 for one idea chosen in advance and 3.5 for the best of many.
- **How much of a pattern's record to believe:** its strength times max(0, 1 - luck's spread / the crowd's spread). When the crowd looks like luck, this is zero.
- **Evidence on new days:** E = 2^(n+1) · B(k+1, n-k+1) · I½(n-k+1, k+1) for k right out of n. Starts at 1; 20 confirms; luck gets there at most 1 time in 20 however often one looks. 76 right of 124 gives 5.3.
- **From a ranking score to a probability:** ρ = 2 sin(π·IC/6); chance a stock at z beats the typical one = Φ(ρz / √(1-ρ²)). A real IC of 0.02 gives the best tenth of stocks 51.5%.

## What to expect

A monthly ranking with a real score of 0.02 is worth about 1 to 1.5% a year over the market, and proving it would
take decades. Astra puts 20% on any frozen learner beating a crash-controlled trend. The realistic prize is a trend
that crashes less and a machine that says "no view" when that is the truth.

## Where the reviewers disagreed

- Earnings drift: the evidence review says it has been gone in large companies since about 2006; Astra gives an
  earnings-surprise test 60%. It goes first because it is cheap to settle.
- Stage B on new days needs about 160 calls to confirm a true 60% hit rate and 800 for 55%: nobody found a faster
  honest route.

## Grok's attack on this decision (added the same night)

Grok was given the findings and the plan and asked what is wrong with them (notes file 7). What it changed:

- **Strip out market and sector moves, keep style.** Removing style as well would delete the trend itself. Grok
  expects 500 stocks to become worth about 100 this way, not several hundred (its odds of several hundred: 20%).
- **The overnight edge is probably not tradeable.** It needs four auction fills a night and breaks even at 0.028%
  all-in; a one-day lag in the ranking loses another 10 to 20%. Grok's odds that it pays after costs: 20%.
- **The trend's 55% hit rate is one bet repeated**, not 2,338 separate ones. Its mean is the honest number: t 0.25.
- **An untested news idea:** after a stock's shock, do the stocks of the same sector that did not jump drift over
  the next 1 to 5 sessions? Its odds that this confirms: 10%.
- **Against weighting patterns by their own record** (step 3): it hands the job back to the best of the search.
  Kept, but gated: the learner speaks only when the whole crowd of patterns beats luck, and each new piece of
  information is judged on its own, not through the learner.
- Grok's odds that the finished plan beats a volatility-scaled trend after costs: 12%. Astra's: 20%.
