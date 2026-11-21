# Historian view: what past episodes say about the Nov 2026 selloff

Written 2026-11-21. Builds on `research_notes/Market theories retail edge/historian_view.md` and `bad_times.md`; nothing there is repeated.

**Provenance.** "[calc]" = my own calculation from the repo's cached Yahoo prices (`data/leverage_px.pkl`, `^NDX` from 1985, `^N225` from 1965; price only, no dividends, costs or cash interest). Scripts: `C:\Users\tyler\AppData\Local\Temp\claude\28f7d7c4cc43e090\18bb9d78-57a2-4803-a7fe-5a5825765403\scratchpad\hist\ep.py` and `ep2.py` in the same folder. Depths and recovery dates for 2000, 2018, 2020, 2022 and 2025 agree with [chartrow's QQQ table](https://chartrow.com/nasdaq-100/drawdown) to within a point. "[memory]" = unverified.

## 1. The analogs

Trigger: first close at least 19.9% below the all-time high (the QQQ reading on 2026-11-20). The Nasdaq-100 has done this eight times since 1985 [calc].

| Peak | Sessions to -20% | Run-up, prior 12m / 24m | +1m | +3m | +6m | +12m | Final trough | Years, peak to new high |
|---|---|---|---|---|---|---|---|---|
| 1987-10-05 | 10 | +54% / +98% | -7.8 | +1.5 | +12.0 | +12.9 | -39.9% | 1.6 |
| 1990-07-16 | 24 | +15% / +30% | -3.8 | -3.7 | +26.2 | +42.0 | -32.9% | 0.6 |
| 1998-07-20 | 30 | +37% / +132% | +18.0 | +36.6 | +66.6 | +110.2 | -23.0% | 0.3 |
| **2000-03-27** | 12 | +119% / +288% | -6.3 | +8.9 | -14.7 | **-52.8** | **-82.9%** | **15.6** |
| 2018-08-29 | 79 | +31% / +60% | +10.8 | +21.6 | +25.6 | +43.8 | -23.0% | 0.6 |
| 2020-02-19 | 16 | +38% / +43% | +14.7 | +32.0 | +53.6 | +78.1 | -28.0% | 0.3 |
| **2021-11-19** | 73 | +38% / +100% | +9.3 | -4.2 | -7.6 | **-9.6** | **-35.6%** | **2.1** |
| 2025-02-19 | 32 | +24% / +76% | +13.8 | +30.5 | +43.6 | +43.1 | -22.9% | 0.3 |
| 2026-10-06 | ~32 | +26% / +58% | ? | ? | ? | ? | ? | ? |

- Twelve months after the trigger the index was higher in 6 of 8 cases and lower in 2 (median of all eight about +42%). The six-and-two split is the base rate; n = 8.
- Among the six *fast* drops (32 sessions or fewer), 5 recovered within 1.6 years. The sixth was April 2000.
- In 4 of the 6 "recovered" cases the trigger was not the low: the index fell a further 3 to 13 points, measured from the peak (1987, 1990, 2018, 2020).
- 2011 and 2015-16 never reached -19.9% on the Nasdaq-100 [calc], so they are milder than today, not analogs.
- **Japan.** Nikkei peak 1989-12-29, -20% after 52 sessions (1990-03-20). Then -2.8% / +4.2% / -22.5% / -14.7% at 1/3/6/12 months, final trough -81.9%, 34 years to a new high [calc]. Peak level 38,915 and the fall to 20,221 by October 1990 are confirmed by [convextrade](https://convextrade.com/history/1990-japan-bubble-burst).
- **March-April 2000.** The Composite closed at 3,321 on 2000-04-14, 34% below its 5,048.62 record ([Star-Bulletin, 2000](https://archives.starbulletin.com/2000/04/14/business/market.html)), and ended the year at 2,470.52, down 39.3% ([EBSCO](https://www.ebsco.com/research-starters/economics/nasdaq-dive-prompts-dot-com-crash)). The summer 2000 rebound above 4,000 is confirmed only as "last close above 4,000 was 2000-09-07" ([Wikipedia](https://www.wikipedia.com/wiki/Closing_milestones_of_the_Nasdaq_Composite)).
- **The accounting phase of 2000-02 came after the first leg, not with it.** Lucent cut reported revenue in November-December 2000 and the SEC inquiry followed; the SEC later alleged about $1.15bn of improperly recognised revenue ([SEC, 2004](https://www.sec.gov/news/press/2004-67.htm)). Cisco wrote off $2.25bn of inventory in 2001 and its stock went from $82 to $13.63 in thirteen months ([CIO](https://www.cio.com/article/266552/it-organization-what-went-wrong-at-cisco-in-2001.html)). No past episode in the table had a probe at the sector leader *inside* the first six weeks. That part of November 2026 has no clean precedent.

## 2. What separated the two families at the comparable point

Honest answer: nothing I can find did so reliably. Tested against the table:

| Candidate signal | Verdict |
|---|---|
| Speed of the drop | No. The worst case (2000) was the second fastest, at 12 sessions. |
| A bounce afterwards | No. The Nasdaq-100 was +8.9% three months after the April 2000 trigger and the Nikkei +4.2% after March 1990; both then fell about 80%. |
| Below the 200-day average | No. True in 7 of 8; the one exception was 2000, when the index was still above it. |
| Prior run-up | Partly. 2000 is alone at +119% / +288%, consistent with Greenwood-Shleifer-You (already in the repo). But 2022 (+38% / +100%) and Japan 1989 (+31% / +70%) became long bears from ordinary run-ups, and 1998 (+132% over 24 months) recovered in four months. 2026 sits at +26% / +58%, which looks like the "recovered" group and proves little. |
| Central bank direction | The best of a weak set. The Fed raised 50bp to 6.5% on 2000-05-16, a month after the first leg ([Federal Reserve](https://www.federalreserve.gov/boarddocs/press/General/2000/20000516/default.htm)). The Bank of Japan raised its discount rate on 1990-03-20 and again on 1990-08-30, to 6% ([BoJ](https://www.boj.or.jp/en/statistics/boj/other/discount/discount.htm)). The Fed was also hiking through 2022 ([Bankrate](https://www.bankrate.com/banking/federal-reserve/history-of-federal-funds-rate/)). So 3 of 3 long bears had tightening after the first leg. The fast recoveries had easing or a pivot within about three months (1987, 1998, 2019, 2020, 2025) [memory, not verified this pass]. |

Caveats on the last row: n = 8, the classification is mine, and the pivot is known only afterwards (the Fed hiked at the December 2018 low and reversed weeks later [memory]). Today a December hike is about 91% priced (brief), which matches the bad family *as things stand*.

## 3. Trend rule and volatility targeting in each family

Published evidence:
- Faber's 10-month rule on the S&P 500, 1901-2012: 10.2% a year versus 9.3%, volatility 12.0% versus 17.9%, worst drawdown -50.3% versus -83.5%, gross of costs. It did not widen its lead over 1940-2000, and the 10-month choice may be data-snooped ([CXO Advisory summary of Faber 2013](https://www.cxoadvisory.com/technical-trading/long-term-outperformance-from-trends-defined-by-moving-averages)).
- Harvey et al.: volatility scaling lifts the US equity Sharpe ratio from 0.40 to 0.48-0.51 and cuts volatility-of-volatility from 4.6% to 1.8% ([Alpha Architect summary](https://alphaarchitect.com/volatility-targeting-improves-risk-adjusted-returns/)). The gain is thinner left tails, and scaling works like a short-term trend overlay ([Man Group](https://www.man.com/insights/the-impact-of-volatility-targeting)).
- V-shaped cost: risk-parity managers de-levered in March 2020 and "totally missed the rebound in Q2 and Q3" ([Institutional Investor](https://www.institutionalinvestor.com/article/2bswpyzz05fjtwnke2qdc/portfolio/not-all-risk-parity-strategies-sucked-last-year)). MSCI calls it a "sour spot" of de-risking at the bottom ([MSCI](https://www.msci.com/research-and-insights/blog-post/the-risk-of-risk-limits)).

My own replay on the Nasdaq-100 [calc]. "Half" = 50% exposure below the 200-day average. "Engine-like" = that plus a 20% volatility target (60-day, capped at 100%). Figures are return from the peak to the day the index regained it (buy-and-hold is about 0% by construction), then worst drawdown.

| Episode | Half rule | Engine-like | Drawdown: hold / half / engine |
|---|---|---|---|
| 1987 | -2.0% | -5.0% | -39.9 / -27.7 / -24.0 |
| 1998 | -5.4% | -9.1% | -23.0 / -22.8 / -17.3 |
| 2018 | -5.8% | -6.9% | -23.0 / -19.9 / -17.7 |
| 2020 | -2.1% | -12.2% | -28.0 / -24.5 / -19.9 |
| 2025 | -1.5% | -6.8% | -22.9 / -16.4 / -15.4 |
| 2000-16 | +21.7% | +120.1% | -82.9 / -68.9 / -38.6 |
| 2021-23 | +6.0% | +9.4% | -35.6 / -27.0 / -22.4 |

- **V-shaped family:** the rules cost 2 to 12 points and shaved 5 to 16 points off the drawdown. The cost is the slow re-entry: in the 12 months after the trigger the engine-like rule made 43% versus 110% (1998), 33% versus 78% (2020) and 19% versus 43% (2025).
- **Long family:** it lost 15% versus 53% in the 12 months after April 2000.
- This is an insurance profile. It also answers "how does the account recover": if this is a V, at well under half the index's pace.

## 4. The stock at the centre of an accounting probe

- Formal SEC investigations are common and mostly end quietly. Of 12,861 closed in 2000-2017, about 10% of listed firms were under one in an average year, while enforcement actions touch under 1% of firm-years. The largest size decile draws 20% of investigations. The average one lasts three years; only 19% are disclosed at the outset ([Blackburne et al., Wharton](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2020/02/2019.12-Undisclosed-SEC-Investigations.pdf)).
- Staff "examining" may be the earlier inquiry stage; the SEC closed roughly 45% of those in 1992-2010 without opening a formal investigation (same paper).
- Being investigated is still bad news on average: median market-adjusted return -5.7% one year and -9.4% two years after opening (same paper).
- On disclosure, three-day returns average about -4.1%, and about -2.9% even for firms never sanctioned (Solomon and Soltes, [Berkeley copy](https://lawcat.berkeley.edu/record/1129102/files/fulltext.pdf); from a search snippet, the fetch returned 403). Another study finds a mean of -6.2% and a median near -3% ([McDowell 2005](https://archive.nyu.edu/bitstream/2451/25947/2/McDowell_2005.pdf)). Nvidia's -14% day is two to three times the typical reaction, on a day the Nasdaq fell 5.3%.
- Two cases. Lucent: a real revenue problem, a $25m penalty and no further restatement required ([SEC](https://www.sec.gov/news/press/2004-67.htm)); the stock was destroyed by the business, not the fine [memory]. Super Micro: auditor resigned 2024-10-24, a special committee found no misconduct on 2024-12-02 and the stock rose almost 20% that day ([Nasdaq.com](https://www.nasdaq.com/articles/supermicro-rises-special-committee-finds-no-misconduct)).

## Looked for and not found

- The share of SEC investigations that end in a restatement or sanction. The SEC withheld outcomes from the Wharton data; "mostly nothing" is my inference from 10% versus under 1%.
- A base rate for "probe plus CEO departure" at a megacap.
- Faber's original paper and AQR numbers on whipsaw cost in V-shaped years; I have a secondary summary and my own replay only.
- A rigorous study of volatility-targeting re-entry lag after March 2020 (press and a simulation only).
- Sourced daily levels for the summer 2000 rebound, the 1987 and 1998 Nasdaq legs, and the Fed's 1998, 2019 and 2020 moves.
- GAO's per-company restatement price drop.
- FRED downloads timed out, so the index tables rest on the repo's Yahoo cache alone.
