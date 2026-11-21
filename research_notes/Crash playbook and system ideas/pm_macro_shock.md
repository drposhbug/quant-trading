# Prediction markets around a macro shock (pm_macro_shock)

Written 2026-11-21. Snapshot: Kalshi and Polymarket public APIs at about 01:00 ET on Saturday; SPX option last trades from Friday 15:00–16:15 ET (Yahoo). Prices are bid/ask in cents. [calc] is my own calculation from those feeds.

## Findings

1. **The whole episode is listed, and a US retail account can trade it on Kalshi.** The 9 December Fed decision (4.2M contracts open on "hold"; 57,000 bid and 137,000 offered at 89/90¢ on "hike 25"), CPI, payroll and GDP ladders, year-end S&P and Nasdaq ranges, year-low and year-high "touch" contracts, a NYSE circuit-breaker contract, a 2027 recession and Nvidia's next CEO ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXFEDDECISION&status=open)). Kalshi is CFTC-supervised, serves US users and pays 3.50% a year on cash and positions ([help page](https://help.kalshi.com/en/articles/13823847-how-is-kalshi-regulated)). Takers pay 0.07·p·(1−p) a contract, 1.75¢ at 50¢; makers pay a quarter of that on the Fed, CPI and yearly index series ([fee types](https://docs.kalshi.com/api-reference/market/get-series); the coefficient is from a [secondary summary](https://www.oddsshopper.com/articles/prediction-markets/kalshi-fee-schedule-by-market) because the fee PDF returned HTTP 429). The $25,000 in the [index](https://assets.kalshi.com/contract_terms/INX.pdf) and [Fed](https://assets.kalshi.com/contract_terms/FEDDECISION.pdf) terms is a position accountability level, not a cap. Polymarket's main exchange is close-only for US persons ([geoblock](https://docs.polymarket.com/api-reference/geoblock.md)). Its [fee table](https://docs.polymarket.com/trading/fees) now charges 0.05·p·(1−p) on finance and tech and 0.01 on economics. `lag_results.md` assumed no fee; at 3¢ a side its rule earned nothing.

2. **Fed contracts agree with fed funds futures.** Expected move on 9 December: Kalshi 22.2 bp, December futures 22.5 bp at Friday's close (25.1 against 27.5 on Thursday) [calc: Kalshi hourly candles; Yahoo ZQX26 96.12, ZQZ26 95.96]. Polymarket quotes each leg within 1¢ of Kalshi. Published gaps have the same sign and size: prediction markets sat 2.4 to 5 bp below futures in summer 2026, "measured, not explained" ([Crypto Briefing](https://cryptobriefing.com/research-two-prices-fed/)). A 20¢ gap on a far-dated meeting was a difference in the question and closed to 1¢ by the eve of the decision ([Dune](https://dune.com/blog/pricing-the-fed-kalshi-polymarket-cme-fedwatch), via a search summary).

3. **The year-end S&P ladder matches SPX options to within a point.** I fitted one smile (SVI) to the last trades of 277 SPX options expiring 31 December (at-the-money volatility 28.2%). P(S&P above 6,845.5 on 31 December): options 64.6%, Kalshi 64/65¢. Across the ten 200-point buckets from 6,200 to 8,200 the mean gap is 0.9 points and the largest 2.1, against an error of 2–3 points in my fit. The best taker edge after the fee is 0.8¢ [calc]. Three informal projects agree. Over 25 days to 19 November, 17 of 486 naive signals survived spread, fee, uncertainty and size ([report](https://raw.githubusercontent.com/japark22/kalshi-mispricing-engine/main/results/REPORT.md)). Where the gap was 3¢ or more, Kalshi scored slightly better than the options (Brier 0.126 against 0.130); half the quoted size was gone after about 18 seconds; a cross-venue package paying $1 never cost under $1.045 ([README](https://github.com/tavelarocque/implied-odds-research)). The third reports "no evidence of an edge" ([README](https://github.com/arjun-chowdhry/kalshi-vs-options)).

4. **Crash odds are not over-priced. Far longshots are, and that is not an edge.** Kalshi prices the tail below 6,400 at 8/22¢ against 16.7% from options, and "touches 6,300 by year-end" at 24/26¢ against a bound of 14–28% from options and 19% in history. On 4 November Polymarket priced "S&P touches 7,000 by 31 December" at 28¢; it happened 16 days later. "Touches 8,200" is 2–3¢ on Kalshi and 4/6¢ on Polymarket against at most 1% from options; "touches 4,500" is 5.5/6.2¢ on Polymarket against at most 2.7%. But options are a poor anchor after a volatility spike. In the 26 episodes since 1990 in which the VIX first closed between 33 and 45, the S&P touched +15.8% within 28 sessions twice (8%), and it stood above the equivalent of 6,845.5 in 21 (81%, interval about 62–92%, against 65% priced) [calc: Yahoo ^GSPC and ^VIX]. That difference is the buy-the-fear premium this repo failed to confirm on 20 November (P = 0.054 to 0.159). Depth settles it: the real bids for "touches 8,200" on Kalshi total about 345 contracts at 2.0–2.2¢, $8 of premium.

5. **Quotes go stale after jumps, once for an hour, but the excess over cost is small.** On Friday the year-end contract traded 102,000 contracts at a median spread of 1¢. Between 10:00 and 11:00 ET the S&P fell 95 points and the quote stayed at 79/80¢; it then fell 8¢ in an hour on 54,000 contracts. Over the day, 63–75% of its response to the index arrived one 5- or 10-minute window late [calc: 1-minute Kalshi candles against Yahoo 1-minute SPX]. Against the option-implied value it was about 6¢ rich at 11:00 and 14:00 and within 3¢ at the other six hourly marks. I held the smile fixed at the close, which overstates those gaps because volatility was lower earlier. A round trip costs 3–4¢ (two fees of 1.2–1.6¢ and a 1¢ spread). That leaves two signals worth 1–3¢ a contract on a −3.7% day.

6. **There is no weekend index signal.** Kalshi trades through the weekend ([schedule](https://api.elections.kalshi.com/trade-api/v2/exchange/schedule)), but Monday's ladders, listed on Friday evening, had traded at most 2,134 contracts each by about 01:00 ET and were quoted 20–35¢ wide (S&P at or above 6,910: 42/70¢ against 54% from options). The lowest Nasdaq bucket, "25,100 or below", already contained Friday's close of 25,029.

7. **As a hedge they lose to holding less.** A year-end "below 6,400" payoff is worth 16.7¢ by options. Built from 13 Kalshi buckets with a 1¢ tick it costs 22¢ plus about 1.5¢ of fees, 41% more [calc]. The 6,300 touch is fairly priced but shows 7 contracts at the best ask and about 1,100 within 2¢. An S&P binary also leaves the basis between the index and twelve technology stocks. The model's cut to 34% invested is the hedge that costs no premium.

8. **As information they are worth reading, not trading.** Markets price about 90% for a December hike and about 50% for another in January; 64% that the S&P ends 2026 above its 2025 close; 23/32¢ that it is back above 7,400 and 5/12¢ above 7,800; 15/28¢ that the Nasdaq-100 is above 28,000, roughly its 200-day average, on 31 December; and 25/26¢ for a 2027 recession. On those odds the model is still at half weight at year-end about four times in five.

9. **Already ruled out in this repo.** Odds do not lead these stocks (0 of 113 robust, `pm_results.md`) and give no pre-announcement edge at FOMC, CPI or earnings (`event_odds_results.md`). Polymarket daily markets add nothing to the overnight gap (0 of 71, `pm_close_results.md`) and lag the stock without a tradable gap (`lag_results.md`). Selling longshots earns under 1.5% before a 2¢ cost (`pm_calibration.md`). Making markets loses to adverse selection (`maker_sim_results.md`).

## Evidence table

| Quantity, 20–21 November | Prediction market | Benchmark | Reading |
|---|---|---|---|
| Expected Fed move, 9 Dec | 22.2 bp | 22.5 bp, futures | same |
| S&P above 6,845.5 on 31 Dec | 64/65¢ | 64.6% options; 81% history (21 of 26) | same as options |
| Ten buckets, 6,200–8,200 | | mean gap 0.9 point, largest 2.1 | inside costs |
| S&P below 6,400 on 31 Dec | 8/22¢ | 16.7% options | 41% dearer to buy |
| Touches 6,300 by 31 Dec | 24/26¢ | 14–28% options; 19% history (5 of 26) | fair |
| Touches 8,200 by 31 Dec | Kalshi 2–3¢; Polymarket 4/6¢ | at most 1% options; 4% history (1 of 26) | rich, $8 deep |
| NYSE circuit breaker in 2026 | 5.1/5.8¢ | 8% history (2 of 26) | fair |
| Friday, year-end contract | unchanged through a 95-point fall | up to 6¢ off; 3–4¢ round trip | 1–3¢, twice |
| "SPY touches $700 in November", priced 4 Nov | 7¢ | resolved yes | a seller at 93¢ lost all of it |

All [calc] from the Kalshi API, Polymarket [gamma](https://gamma-api.polymarket.com/events/slug/spx-hit-dec-2026) and CLOB price history, and Yahoo. History rows use the 26 VIX episodes in finding 4.

## Ideas worth a pre-registered test (or why none)

None is worth a trial slot. Fees of 1–2¢ a side are as large as nearly every gap I measured, and the two visible biases are a few dollars to a few hundred dollars deep. The two least bad:

1. **Option-anchored longshot seller.** Contracts: Kalshi KXINXMAXY, KXINXMINY and the Nasdaq equivalents; Polymarket "hit" ladders on paper only. Let D be the option-implied probability of finishing beyond the barrier, so 2D bounds the touch. At 15:55 ET, if the YES bid is at least 6D and at least 2D + 2¢, buy NO for the displayed size and hold to settlement. Benchmark zero. Fee 0.07·p·(1−p) on Kalshi, 0.05 on Polymarket. Sample: 150 fills over at least 12 expiry months, bootstrap by month, both halves positive. Pass probability 3%. Finding 4 says the anchor is wrong on the upside, each month is one draw, and November shows the loss.
2. **Stale-quote taker on long-dated index contracts.** KXINXPOS and the KXINXY buckets; 1-minute Kalshi candles (bid and ask are observed) and SPY bars, 2025 to date, excluding 20 November 2026. Fair value is the mid 60 minutes earlier plus the contract's trailing five-day sensitivity times the index change. If the bid is 4¢ or more above fair, sell at it by buying NO (mirror image for the ask); exit when the quote is within 1¢ of fair, or at the close. Cost: the Kalshi fee both ways. Benchmark zero. Sample: 300 signals, bootstrap by day, both halves positive. Pass probability 5%. It is `lag_results.md` on another venue (+5.7% at 2¢, nothing at 3¢, decaying), it was found by looking at one day, and each price level holds about 1,000 contracts.

Two things cost nothing: refresh the Polymarket fee constants from the live table, and keep `any_favorites.py` excluding price markets.

## What I looked for and did not find

- A peer-reviewed comparison of index event contracts with options after fees. Only the three GitHub projects; a Stevens student project returned 404.
- Any study of prediction-market spreads, depth or calibration conditioned on high volatility.
- Historical option quotes. Finding 3 is one snapshot, not the selloff. Polymarket's price history for open markets returned the current price for past dates, so I used resolved contracts only.
- Kalshi's fee PDF (HTTP 429) and a readable copy of the Fed's revised Kalshi paper.
- Listings, fees and state limits at Polymarket US, Robinhood, Interactive Brokers' ForecastEx and CME. The shared web-search budget ran out before I could verify them.
- A documented weekend or overnight effect in index contracts beyond the election-night studies in `reports/Polymarket as a trading predictor.md`.
