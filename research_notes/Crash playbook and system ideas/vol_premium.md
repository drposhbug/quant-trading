# Volatility premium after a spike

STORM perspective `vol_premium`, 2026-11-21. **[calc]** = my own calculation from public data: Cboe index histories
(`cdn.cboe.com/api/global/us_indices/daily_prices/<INDEX>_History.csv`), Cboe VIX-futures settlement files
([daily](https://www.cboe.com/us/futures/market_statistics/settlement/),
[per contract](https://www.cboe.com/us/futures/market_statistics/historical_data/)), Yahoo closes and Friday's option
chains. Nothing in the repo was run. "(summary)" = search summary only.

## Findings

**No volatility trade here has positive expected value after costs for a small account. After past spikes the
best-paid risk was plain equity, which the model already holds by rule. The useful actions are to buy no protection
now and to sell no volatility into the spike.**

Friday's close [calc]: VIX 35.89 (9-day 40.72, 3-month 30.94), December VIX future 28.46, Nasdaq-100 VXN 45.25.
It is the 18th time since 1990 that the VIX first closed at or above 35 after 63
quieter sessions. (The brief's "25 on 11-09" is the 6 November close. The repo's VIX ≥ 40 re-entry rule has not
armed: 40.03 was intraday.)

1. **Selling at the spike earns no more per unit of risk.** VIX minus the next 21 sessions' realised volatility
   averaged 4.4 points when VIX was at or above 30, against 2.9 to 6.2 in calmer buckets, but with a standard deviation
   of 13.6 points against 3.7 to 7.4 (non-overlapping blocks, 1990–2026) [calc]. After the 17 earlier first closes at
   or above 35, a seller of 30-day variance won 13 times and still lost on average: September 2008 and February 2020
   each cost four to five times the premium [calc].
2. **Investable versions lagged plain stock.** After the 11 episodes since 2007, the Cboe PutWrite index (PUT) returned
   14.3% over the next year against 21.6% for the S&P 500, beat it twice, and lost 12.7% and 15.9% in the first month
   in 2008 and 2020. Defined-risk versions did worse: iron condor (CNDR) +4.0%, iron butterfly (BFLY) +1.7% [calc].
3. **The futures curve already prices the fall.** Shorting the first monthly VIX future at those 11 closes and holding
   to settlement won 8 times and lost 7.1 points in total (−43.5 in 2020, −36.4 in 2008) [calc]. On 2 March 2020 the
   VIX was 33 and the 18 March future 26; the VIX ended near 70
   ([Cheng, Tuck](https://tuck.dartmouth.edu/news/articles/the-market-underappreciated-the-risk-of-a-pandemic)). With
   VIX/VIX3M above 1.10 (now 1.16) the long-VIX-futures fund VIXY averaged +11.2% over the next 21 sessions (median
   −9.9%) [calc]. In this episode the inverse fund SVIX had taken $72 million of inflows by 9 November
   ([Benzinga](https://www.webull.com/news/15895511758586880)) and has fallen 33% since [calc].
4. **The index premium has had no alpha since the benchmarks went live.** CAPM alpha of six Cboe option-selling indices
   was +1.6% to +5.1% a year in 1990–2006 (back-filled history). For all seven it was −0.1% to −4.5% in 2007–2019 and
   −1.1% to −3.1% in 2020–2026, none significant [calc]. VIX minus realised is still 3 to 4 points (4.7 before 2007)
   [calc]; the tradable strategies do not capture it.
5. **Earnings sleeve.** No closed trades yet. Megacap earnings-day moves do not scale with the VIX: the mean absolute
   move was 6.0–6.3% in every VIX bucket (517 reports, 2014–2026), though 22% exceeded twice the stock's own average
   at VIX ≥ 30 against 13–15% otherwise [calc]. The straddle does scale, because it prices non-event volatility (NVDA
   80%, AMD 96%, AVGO 82% implied; 21-day realised 77%, 129%, 82% [calc]). In a stylised simulation, doubling
   non-event volatility cuts the part of the straddle that vanishes after the report from 44% to 26% and the gross
   edge per unit of maximum loss from 0.11 to 0.05 (jump 20% overpriced), while costs stay near 0.2 [calc]. Crossing four legs at Friday's
   closing quotes cost up to 20% of the mid credit [calc]. NVDA on 17 November: implied about 8%
   ([Cboe](https://www.cboe.com/insights/posts/week-of-11-16-2026-retail-turns-bearish-on-nvda-ahead-of-earnings/)),
   −2.9% the next day, −14% two sessions later [calc]. Next: AVGO 9 December
   ([Broadcom](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026)),
   ORCL about 14 December (Yahoo, unconfirmed). The repo's verdict (about zero; a plumbing test) stands.
6. **Protection now.** A 28-day put 5% out of the money cost 1.71% of spot on SPY and 2.60% on QQQ; a zero-cost QQQ
   collar with that put caps the month at +4.4% [calc]. Insuring the model's stock sleeve this way costs about 0.9% of
   account equity a month. The put-protected index (PPUT) lagged the S&P 500 by 1.10% per 21 sessions when bought at
   VIX ≥ 30, against 0.06–0.24% below 25, and by 6.5 points over the year after the 17 spikes (ahead in 3) [calc].
   Holding less matches it: 70% S&P 500 plus T-bills had PPUT's worst drawdown (−41.4% vs −42.0%) and 1.2 points a year
   more return, 1990–2026 [calc]. The model's 34% exposure is the cheap hedge.
7. **Permanent long volatility.** The tail fund TAIL lost 6.5% a year since 2017; 90% SPY plus 10% TAIL (11.9% a year,
   −28.7% drawdown) was no better than 80% SPY plus T-bills (11.6%, −27.7%). The put-spread-collar fund JHEQX (7.3% a
   year) matched a 50–55% SPY mix (7.6–8.1%). Trend funds paid in 2022 (DBMF +31.5%) and not in this drop (−4.8%)
   [calc].

Access has changed since the repo's options report: Alpaca has listed index options (SPX, XSP, VIX; no NDX) since
2 September 2026
([blog](https://alpaca.markets/blog/alpaca-launches-index-options-via-trading-api),
[docs](https://docs.alpaca.markets/us/docs/index-options)), and the $25,000 day-trading minimum ended on 4 June 2026
([FINRA](https://www.finra.org/rules-guidance/notices/26-10)).

## Evidence table

Tail outcomes over each S&P 500 peak-to-trough window [calc]:

| Window | S&P 500 | PUT | CNDR | BFLY | SVXY (short VIX; −0.5x since 2018) | TAIL |
|---|---|---|---|---|---|---|
| Aug–Dec 1987 | −33.5% | n/a | −11.6% | −14.0% | n/a | n/a |
| Aug 2008–Mar 2009 | −47.3% | −34.8% | −5.0% | −8.5% | n/a | n/a |
| Jan–Feb 2018 | −8.8% | −6.2% | −4.0% | −3.7% | −91.6% | +4.7% |
| Feb–Mar 2020 | −33.9% | −28.9% | −9.2% | −3.2% | −55.3% | +28.4% |
| Jul–Aug 2024 | −8.5% | −4.4% | −0.5% | +2.4% | −37.7% | +11.9% |
| Feb–Apr 2025 | −18.9% | −15.0% | −10.2% | −7.0% | −34.7% | +27.1% |
| 6 Oct–20 Nov 2026 | −11.6% | −6.8% | −3.3% | −2.7% | −26.6% | +12.5% |

A capped loss per trade does not cap the drawdown: BFLY lost 2.3% a year from mid-2007 with a −54.9% drawdown, and
CNDR made 0.8% a year [calc].

| Published source | Finding |
|---|---|
| [Cheng, RFS 2019](https://ideas.repec.org/a/oup/rfinst/v32y2019i1p180-227..html) | The VIX premium falls or stays flat when risk rises; cutting short exposure when it turns negative beat staying short |
| [Simon and Campasano](https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2013-Reading/papers/EFMA2013_0164_fullpaper.pdf) (summary) | The basis predicts VIX-futures returns: short in contango, long in backwardation (2006–2011) |
| [Dew-Becker and Giglio, Chicago Fed 2025](https://www.chicagofed.org/publications/working-papers/2025/2025-17) | "Over the past 15 years, option alphas have become indistinguishable from zero" |
| [Israelov and Nielsen, AQR 2015](https://www.aqr.com/Insights/Research/Journal-Article/Still-Not-Cheap-Portfolio-Protection-in-Calm-Markets) (summary) | Premium 3.4 points on average 1990–2014, more variable when implied volatility is high |

## Ideas worth a pre-registered test (or why none)

None on the options account. A rule that trades only after spikes gets about one episode every two years, against 120
trades needed, and the evidence points the wrong way for selling now. For the record:

- **Fade, not spike (put-write timing).** Hold the Cboe PutWrite index (PUT; Russell 2000: PUTR)
  only while the 63-session VIX maximum is at least 30 and the VIX has closed at or below 80% of it; T-bills otherwise.
  Benchmark: a constant index and T-bill mix of equal beta. Pass: paired stationary bootstrap P < 0.05 on both
  underlyings, then a 20% sleeve against the frozen model on both universes. My exploratory look, which spends the
  in-sample: alpha in that state +2.0% a year for PUT (t = 0.7), +4.4% for PUTR (t = 1.0), −6.2% for the Nasdaq-100
  BuyWrite (t = −1.6); in the spike state itself −12% (t = −1.2) [calc]. Probability of passing: 2%. Not worth a trial.
- **Prediction-market tails against listed options.** A Polymarket "close above $K" contract is a digital call, and
  the listed chain gives a ceiling for its fair price. One snapshot on 21 November: NVDA November YES bids of 15.2¢,
  6¢ and 5¢ at $150, $160 and $170 against option-implied 8.3%, 2.7% and 0.9%; depth 40–150 shares; taker fee
  0.05·p(1−p) ([Polymarket](https://docs.polymarket.com/trading/fees)); other tickers' books average 58¢ wide [calc].
  Rule: daily at 16:00 ET, 2 to 10 sessions before month-end, buy NO on any strike above spot whose YES bid is at
  least 3¢ above the option-implied probability (adjacent call spread, interpolated to the resolution date); hold to
  resolution; flat stakes; dry-run. Pass: 200 settled entries, mean ROI > 0, bootstrap 95% interval above 0 clustered
  by ticker-month, positive in both halves. Probability: 8%. Capacity is tens of dollars a strike, and it is a short
  call on names the stock model owns.
- **Iron-fly sleeve.** Keep the rule. Log the jump-implied move from two expiries, the event share of the straddle and
  the NBBO at entry and exit, so the 120-trade verdict can be split by regime. Its chance of passing its own test: 3%.

## What I looked for and did not find

- Implied earnings moves by VIX regime. Free history starts in February 2024 and needs API keys, so finding 5 rests on
  mechanism, realised moves and one case.
- A published, cost-inclusive study of defined-risk index spreads entered after VIX spikes. Vendor material only.
- Loss figures for retail put sellers in October 1987, and a primary source for Allianz Structured Alpha's 2020 loss.
- Cboe's collateral treatment for BFLY; its alpha assumes T-bill collateral like CNDR.
- Polymarket index ladders (my query returned none) and Kalshi index-range pricing: the shared web-search budget ran
  out before I could check Kalshi.
