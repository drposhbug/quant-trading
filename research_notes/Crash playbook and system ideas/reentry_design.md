# Trend and volatility-target design: is there a better-specified version?

Perspective: reentry_design. Written 2026-11-21.

`[calc]` means my own run on the repo's cached prices (to 2026-11-19) under the `retail_edge_tests.py` protocol:
next-close fills, 5 bp, 1-point band, T-bills on cash. Triples are shipped / end-2014 / ^NDX since 1990. The harness
reproduced the repo's benchmark rows (Sharpe 1.251 / 0.957 / 0.859) before any challenger ran, and each specification
was written before its run. Scripts and outputs:
`C:/Users/tyler/AppData/Local/Temp/claude/28f7d7c4cc43e090/18bb9d78-57a2-4803-a7fe-5a5825765403/scratchpad/storm/reentry_design/`.
I looked at 17 variants, so every P below is in-sample and unadjusted.

Labels: **E5** = average of five gates, 50 to 250 days. **C5** = the same, 100 to 300 days. **T5** = the 200-day gate
averaged over the last 5 sessions.

## Findings

**1. For the gate and the volatility input the answer is "leave it".** I ran four gate designs (E5, C5, T5 and a
21-session version) and two volatility inputs (exponentially weighted with the same average lag, and downside-only).
Sharpe moved by −0.011 to +0.023 against the frozen model, and the smallest P on any universe was 0.17 [calc]. I then
ran the five main designs unchanged on the leverage study's six indices. Pooled P was 0.28 to 0.67, and T5, the
best-looking design on the stock universes, had a lower Sharpe in five of the six markets [calc]. None can pass the
repo's test.

**2. Specification luck is real but small here, and the daily check already removes the worst kind.**
- Published: a monthly-checked 10-month rule returned 10.5% or 11.3% a year, with a 19% or 30% drawdown, depending on
  which of two adjacent days it traded. A dual-momentum rule returned 43% or 146% over a decade on a 9- or 10-month
  lookback. Staggering the trades removes this luck without changing the average (Newfound, table below).
- This model checks daily, so it has no rebalance-day luck. Checked monthly, its CAGR would range from 21.4% to 23.8%
  and its worst drawdown from −19.8% to −30.0% across the 21 possible days, at a lower Sharpe (1.16 against 1.25)
  [calc].
- Lookback luck, shipped universe: across six lookbacks (50 to 300 days) Sharpe ranges from 1.20 to 1.31, and the
  calendar-year gap between best and worst averages 5.8 points (16.3 in 2021). The 200-day ranks third of six, so it
  was not a lucky pick [calc].
- E5 is exactly the average of the single-lookback strategies (correlation 0.999). Ensembles cost 0.1 to 1.1 points of
  CAGR, because faster lookbacks sit in risk-off more often, and 0.6 to 1.7 points after tax [calc].

**3. The volatility estimator does not matter.** Harvey et al. find the equity Sharpe rises from 0.40 to 0.48–0.51
for any half-life from 10 to 90 days, "not very sensitive to the choice". Downside volatility wins 70 of 103 real-time
comparisons against 50 for total volatility (Wang and Yan), but in leveraged factor portfolios with double the
turnover. Here it adds 0.02 Sharpe at best (P ≥ 0.17) and deepens the ^NDX drawdown from −31.6% to −33.1% [calc].

**4. The sour spot is the volatility target, not the 200-day switch.** In nine Nasdaq-100 bear markets since 1987
the frozen engine, run on the index itself, held a median 22% at the low and needed a median 83 sessions to get back to 80%, by which time the index
was 34% off its low. With the switch alone it needed 37 sessions [calc]. From the peak to one year past the low, the
engine beat holding in 2000–02 (+61 points), 2007–09 (+17) and 2021–22 (+10), matched it in 1990, and trailed in 1998
(−47), 2020 (−26), 1987 (−11), 2025 (−11) and 2018 (−7). It took a median 66% of the fall and 36% of the next six
months' rebound [calc]. No design moved rebound capture by more than 2 points, so nothing tested keeps the insurance
for less. MSCI found the same in 2020: a 20% risk limit lost 17.7% against 30.5% at the low, trailed by 7.7 points by
August, and would have led by more than 10 in a slow, 2008-style recovery.

The switch itself is a small, steady premium. On ^NDX since 1990, 94 of 127 risk-off spells lost money and the median
spell lasted 3 sessions. The switch cost 1.4 points a year and cut the worst drawdown from −47% to −32% [calc].
Faster re-entry has a published out-of-sample record (Goulding, Harvey and Mazzoleni: slow after corrections, fast
after rebounds), but its gain over a fixed blend is Sharpe 0.52 against 0.51 over 50 years. The repo's VIX rule rests
on two episodes.

**5. Cadence: keep daily with the band, and fix one flaw.** Weekly rebalancing saves 12% of turnover and adds a
1.6-point CAGR range and a 4.7-point drawdown range by weekday. Removing the band multiplies orders by 16 for no gain
(P = 0.59 / 0.78). The flaw is that each name is banded separately, so a broad de-risking is skipped. Gross exposure
is off target by 1.7 points on average, 4.5 at the 95th percentile and 6.8 at worst, and sits 1.0 point too high on
average in risk-off [calc].

**For the owner now.** QQQ needs about +12% to regain its 200-day line (+8% for the 300-day, +17% for the 50-day, so
an ensemble would be no faster today). If the market turned as calm as last summer from Monday, the volatility scale
would still dip to about 0.60 in December and stay below 0.76 until 19 February 2027, when the 20 November session
leaves the 60-day window [calc]. That means roughly 30–38% invested while QQQ is below its 200-day. A slow recovery
is the design, not a fault. Resetting the paper account changes none of this: the model would buy back the same 34%.

## Evidence table

| Claim | Number | Source |
|---|---|---|
| Gate designs, Sharpe change | E5 +0.003 / −0.001 / +0.004; C5 −0.011 / 0.000 / +0.003; T5 +0.018 / +0.023 / +0.003 (P 0.27 / 0.21 / 0.42) | [calc] |
| Volatility inputs, Sharpe change | exponential +0.020 / +0.018 / +0.005; downside +0.018 / +0.012 / +0.002 | [calc] |
| Six-index check, pooled P | E5 0.57, C5 0.28, T5 0.62, exponential 0.37, downside 0.67 | [calc] |
| Gate price jittered by 0.30% (the 15:30-to-close move has sd 0.35%) | frozen CAGR sd 0.23 points; T5 cuts it 62%, C5 34% | [calc], repo 5-minute QQQ cache |
| Weekly / monthly range across offsets | CAGR 22.7–24.3% / 21.4–23.8%; drawdown −21.2 to −25.8% / −19.8 to −30.0% | [calc] |
| Band plus aggregate trigger | worst exposure error 6.8 → 1.0 points; tracking error 0.79% → 0.26% a year; orders 172 → 771 a year; turnover 3.7× → 4.7× | [calc] |
| Rebalance-day luck, 10-month rule | 11.33% vs 10.51% a year; drawdown 19.0% vs 30.2% | https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/ |
| Timing luck, stock/cash rule | 9.6% to 11.1% a year across 21 offsets | https://blog.thinknewfound.com/2018/01/quantifying-timing-luck/ |
| Tranching in small accounts | 348 bp CAGR spread; about 2 tranches pay at $25k | https://quantpedia.com/the-tranching-dilemma/ |
| Lookback fragility | 43.1% vs 146.1% total return | https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/ |
| No persistent best lookback | 1,023 trend rules; picking by past return adds little | https://blog.thinknewfound.com/2019/12/timing-trend-model-specification-with-momentum/ |
| Estimator insensitivity | Sharpe 0.40 → 0.48–0.51; turnover 5× vs under 1× a year | https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf |
| Downside volatility | 70 vs 50 of 103; monthly weight change 0.69 vs 0.36 | https://www.lehigh.edu/~xuy219/research/Downside.pdf |
| Implied volatility adds little (blog) | VIX coefficient 0.14 vs 0.71 for past volatility | https://qoppac.blogspot.com/2025/11/is-predicting-vol-better-worth-effort.html |
| Conventional targeting | better Sharpe in 8 of 10 markets, deeper drawdown in 4 | https://rpc.cfainstitute.org/research/financial-analysts-journal/2020/conditional-volatility-targeting |
| Speed asymmetry, 1969–2018 | Sharpe: slow 0.41, blend 0.51, fast 0.34, dynamic 0.52 | https://benny.aeaweb.org/conference/2021/preliminary/powerpoint/ihbRDkeH |
| Slow trend in recent drawdowns | 12-month signal lost in the three latest of eight | https://people.duke.edu/~charvey/Research/Published_Papers/P140_The_best_of.pdf |
| Sour spot, 2020 | −17.7% vs −30.5%, then 7.7 points behind | https://www.msci.com/research-and-insights/blog-post/the-risk-of-risk-limits |
| Frictions, November 2026 | SEC fee $20.60 per $1m sold; FINRA fee $0.000195 a share; $25,000 day-trading minimum gone since 4 June 2026 | https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2 ; https://www.finra.org/rules-guidance/rule-filings/sr-finra-2024-019/fee-adjustment-schedule ; https://www.finra.org/rules-guidance/notices/26-10 |

## Ideas worth a pre-registered test (or why none)

**1. Aggregate trigger on the no-trade band (plumbing).** Against the frozen `monitor.rebalance`: keep the
1%-of-equity band per name. After applying it, if the skipped stock trades sum to more than 1% of equity in either
direction, skip nothing that day. Test: paired stationary bootstrap (L = 20, B = 2,000) on tracking error against the
zero-band engine, P(challenger's tracking error ≥ frozen's) < 0.05 on both universes. Guards: Sharpe no more than 0.05
lower, turnover under 1.5 times the frozen model's. Baseline today: P = 0.000 on both, Sharpe −0.004 / +0.005 [calc].
Pass probability 85%. It earns nothing. It makes the account hold what the model says. Turnover rises 28%, so run the
tax ledger first if the real account will be taxable.

**2. Gate and volatility input: leave it.** Pass probability for each of the five designs is about 2%. Each needs
roughly +0.03 to +0.06 Sharpe on both universes. The best show +0.02 on the stock universes and nothing across six
indices. The repo's superiority test cannot approve a change
whose only claim is less luck, and the luck at stake (about 1.5% a year of tracking difference against the average
lookback) does not justify a new rule.

## What I looked for and did not find

- Any design that improves rebound capture without giving back protection.
- An out-of-sample record for breadth-thrust or volatility-normalisation re-entry rules. The shared search budget ran
  out before I could look.
- A published comparison of range-based or implied-volatility inputs inside a long-only, capped volatility target.
- Primary tables for Bongaerts et al. and Cederburg et al. (summaries only), Faber's results after 2016, and AQR's
  trend-speed numbers for 2020.
- A tax benefit from T5. Its after-tax gain (+0.50 / +0.35 points) is smaller than its pre-tax gain [calc].
