# What rebounds, and does the frozen model hold it

Written 2026-11-21.

**Provenance.** [calc] = my own calculation from the repo's caches (`data/prices.csv`, `data/retail_edge.pkl`, `data/universe/`; closes to 2026-11-19 plus Friday's moves from the brief) or from the [Ken French data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) (to 2026-09). Scripts and output: `C:\Users\tyler\AppData\Local\Temp\claude\28f7d7c4cc43e090\18bb9d78-57a2-4803-a7fe-5a5825765403\scratchpad\storm\rebound_cross_section\`. Calculations are descriptive, not registered tests. "Summary" marks a figure taken from a search summary, not the source page (the shared web-search budget ran out).

## Findings

1. **Exposure, not stock selection, sets the account's rebound.** The model is 33.9% invested [calc]. If every name returned to its 6 October price, the twelve names held equally would gain 30.8%, the model's inverse-volatility mix 25.0%, and the account about 8.5% at today's exposure. Nine-tenths of the gap is exposure. The weighting costs 2.0 points of equity in that rebound and saves 1.3 if the fall repeats [calc]. A reset changes none of this: percentage capture is the same from $94,975 or $100,000.
2. **The riskiest names lead off a true low.** In the 12 months after US bear-market lows, high-beta big caps beat low-beta by a median 42 points and prior losers beat winners by 30 [calc].
3. **From a date knowable in advance, the same tilt averages zero.** After the first month-end 10% below the high, high-beta big caps beat low-beta in 6 of 15 cases (median −4 points) [calc]. A failed rally has the same cross-section as a bottom, and there were 26 of them in 16 bear markets [calc].
4. **This is not yet the momentum-crash state.** Fourteen of the 15 worst momentum months followed a negative two-year market return ([Daniel and Moskowitz](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf)); SPY's is about +20% [calc]. Three of the four biggest losers (NVDA, TSM, AMD) were among the four strongest 12-month performers [calc], so "buy the losers" and "buy the winners" name the same stocks.
5. **Megacap reversal after extreme moves is gone.** One-month reversal in the biggest size quintile earned −0.20% a month in 2010–2026 before costs, and megacaps that fell 8% or more in a day did not bounce over the next 21 sessions [calc].
6. **A probe plus a CEO exit has a poor record; a probe alone does not.** Of seven hand-picked large companies with both, six lagged SPY over the next 12 months (median −37 points) [calc]. Neither "sell it" nor "buy it" has a tested record at this size. NVDA is 2.5% of equity, so a further 50% fall costs 1.2 points [calc].
7. **Old leaders are a coin flip from the low and a poor bet before it.** Technology led into seven comparable dates. It lagged for three years after four of them and led after the last three [calc]. The basket assumes the fourth repeat follows the last three.

## Evidence table

| Question | Evidence | Source |
|---|---|---|
| Model's share of its basket's rebound | 35–59% of the basket's 126-session gain after QQQ first closed 15% below its high (2016, 2018, 2020, 2025); 72% of the further loss in 2022. End-2014 list | [calc] |
| Inverse-volatility vs equal weight, weighting only | Captures 97% of equal weight's up months and 92% of its down months (end-2014 list); 92% and 93% (shipped). Sleeve weights now: AMD 4.1%, ORCL 5.6%, AVGO 6.4%, NVDA 7.3%, TSM 7.4%, against 8.6% each; semiconductors 25% against 34.5% | [calc]; equal-weight challenger closed in MATH.md |
| Low-volatility indices in rebounds | S&P 500 Low Volatility took 67.9% of the upside and 55.7% of the downside over 15 live years. A much stronger tilt than this model's | [S&P DJI](https://www.spglobal.com/spdji/en/documents/education/education-sp-500-low-volatility-index-15-years-of-live-performance.pdf), summary |
| Leaders off true lows, big caps | 12 months after ten month-end bear lows since 1926: market median +35%; high beta minus low +42 points (6 of 7 since 1963); high variance minus low +25 (7 of 7); losers minus winners +30 (8 of 10) | [calc] |
| The 2009 and 1932 cases | Losers +163%, winners +8%, March–May 2009; +232% and +32%, July–August 1932. The reversals ran for months | [NBER w20439](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf) |
| Megacaps, last four episodes | 50 largest S&P 500 names by dollar volume: the ten biggest losers beat the ten best holders by 13–71 points over 63 sessions after SPY's −15% date; by −4 and −8 over 126 sessions in 2020 and 2022 | [calc] |
| From a knowable date | First month-end 10% or more below the high, 19 cases: 7 fell a further 10% or more. High beta minus low over 12 months: mean +4, median −4, range −29 to +81 (n = 15). Losers minus winners: median −9 (7 of 19 positive) | [calc] |
| Same, hindsight-free names | End-2014 list, five QQQ −15% dates: three biggest losers minus three best holders −0.1, +0.9 and −1.1 points at 21, 63 and 126 sessions | [calc] |
| Failed rallies | 26 rallies of 10% or more later undercut: seven in 1929–32, five in 2000–02, four in 2007–09, two in 2022. Mean +18% over a median 36 sessions. Losers beat winners by 10.8 points in them (81% of cases), against +7.0 in the first 21 sessions off real lows, then lost 11.5 on the way to the lower low. Goldman's count: 19 global rallies since the 1980s, averaging 44 days | [calc]; [Bloomberg](https://www.bloomberg.com/news/articles/2025-05-06/goldman-says-bear-market-rallies-are-norm-as-pain-trade-thriving), summary |
| Megacap one-month reversal | Biggest quintile, last month's losers minus winners: +0.41% a month 1926–89 (t = 2.2); +0.21% 1990–2009 (t = 0.6); −0.20% 2010–2026 (t = −0.5), gross | [calc] |
| Megacap one-day shocks | Same 50-name set, 316 falls of 8% or more against SPY since 2017: next 21 sessions mean 0.0%, median −1.2%, 44% positive. Falls of 12% or more: −2.1% over 5 sessions. Exception: on days SPY lost 2% or more, +4.4% over 5 sessions (n = 23, one of four subsets examined) | [calc] |
| Published, short horizon | Heavily traded large stocks continue for a month (16% a year in the top turnover decile). Price shocks with news drift. Single short-term signals in large caps earn 6–8% gross and below −2% net at 25 bp | [Medhat and Schmeling](https://repec.cepr.org/repec/cpr/ceprdp/DP15857.pdf), summary; [Savor](https://econpapers.repec.org/RePEc:eee:jfinec:v:106:y:2012:i:3:p:635-659), summary; [Robeco](https://www.robeco.com/en-uk/insights/2022/05/beyond-fama-french-alpha-from-short-term-signals) |
| Probe and CEO exit, large companies | Both within six months (Freddie Mac 2003, Fannie Mae 2004, AIG 2005, UnitedHealth 2006, Valeant 2016, GE 2018, Kraft Heinz 2019): 12-month return against SPY median −37 points, one of seven positive. Probe only (Microsoft 1999, Bristol-Myers 2002, Apple 2006, IBM 2013, Alibaba 2016): median +19. Exit only, 11 cases: median −17 | [calc]; dates from memory, failed companies (Enron, WorldCom, Lucent) absent |
| Large samples | Firms sanctioned for misreporting lost 41% of value. After fraud accusations, long-run performance matched peers | [University of Washington](https://www.washington.edu/news/2006/11/13/a-companys-reputation-is-what-gets-fried-when-its-books-get-cooked/), summary; [Marciukaityte et al.](https://econpapers.repec.org/RePEc:taf:ufajxx:v:62:y:2006:i:3:p:32-41), summary |
| Nvidia as reported | Civil probe of disclosures, unconfirmed; the CFO is interim chief; no permanent successor | [InvestmentNews, 2026-11-17](https://www.investmentnews.com/equities/embattled-nvidia-faces-sec-probe-as-california-attorney-general-mulls-action/269054) |
| Industry leadership | Rank correlation of relative return, 36 months before the peak against 36 after the low: 0.00 (49 industries, ten bears). From the first −20% month-end, the old bull's top three of 12 industries beat the market over five years in one of nine cases. Technology as a top-two leader into seven −10% dates: −11 to −28 points over three years (1929, 1969, 1978, 2000); +14 to +76 (2018, 2020, 2022) | [calc]; see also [SentimenTrader, 2020](https://www.sentimentrader.com/blog/the-right-sectors-arent-leading-us-out-of-the-bottom) |
| Rebalancing band | A 1-point no-trade band changes Sharpe by under 0.01 and rebound-window returns by 0.1–0.2 points | [calc] |

## Ideas worth a pre-registered test

None. Three were considered; a fourth is not a test.

1. **Equal base weights while QQQ is below its 200-day average** (`sizing = "ew"` on those days only; one paired stationary bootstrap, L = 20, B = 2,000, Sharpe, both universes, window ending 2026-10-05). Inside the engine the swap moved the 126-session return after the five trigger dates by −0.4 to +2.3 points (end-2014 list) [calc], because the volatility target scales the riskier mix down. Chance of passing: 2%. The unconditional version is already closed.
2. **A megacap shock rule, in either direction** (halve or raise a name for 21 sessions after a one-day fall of 8% or more against QQQ). The 316-event record shows neither drift nor reversal. Chance: 2%. The repo's post-earnings-dip and trend-plus-reversal tests already failed.
3. **An event cap, as policy for the scheduled review.** Add a name to `EVENT_CAPS` at 5% of the sleeve once it has both a reported regulator accounting or disclosure inquiry and an unplanned CEO exit. Lift it after the first audited annual report under a permanent chief. Neither universe contains a qualifying event, so no bootstrap is possible; the evidence is seven hand-picked companies. Effect today: NVDA from 2.5% to 1.7% of equity [calc]. It is a risk-policy choice like the SPCX cap, small either way, and not one to make during a drawdown.
4. **Write down the expected lag now** (documentation, no model change). On the end-2014 list the model made 30–70% of QQQ's gain in the 126 sessions after the trigger dates of the four recoveries [calc]. Recording that range shows in advance that lagging a sharp rally is the design.

Why none: every cross-sectional effect here is large only from the true low, which cannot be dated in advance. The exposure question was already tested (faster re-entry, P = 0.054 / 0.083 / 0.159) and may not be re-tuned.

## What I looked for and did not find

- Published capture ratios for inverse-volatility weighting of megacaps (only the low-volatility index).
- Momentum-crash results for megacaps alone (biggest size quintile used instead).
- Any study of a regulator probe combined with a CEO exit at very large companies, or of forced founder-CEO exits (only sudden deaths: −3.25% over three days, [working paper](https://www.ecgi.global/sites/default/files/2026-09/fin-935-2023_heterogeneous_ceo_death_effects_1_0.pdf), summary).
- An after-cost study of megacap reversal on post-2010 data (mine is gross).
- Solomon and Soltes's one-year return table, the S&P DJI page and the forced-turnover study (blocked or paywalled).
- Nvidia news after 17 November beyond the brief; the search budget was spent.
- Current fees or access rules: nothing here needs a new instrument, so not checked.
