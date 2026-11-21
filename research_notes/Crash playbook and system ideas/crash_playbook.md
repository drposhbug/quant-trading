# Crash playbook: what pays in a drawdown without a forecast

2026-11-21. STORM note. No repo code was run and nothing else was changed. **[calc]** = my arithmetic on Yahoo index closes (^GSPC from 1927, ^NDX from 1985, to 2026-11-20, price only), the Cboe VIX file and the repo's cached T-bill series; scripts are in `C:\Users\tyler\AppData\Local\Temp\claude\28f7d7c4cc43e090\18bb9d78-57a2-4803-a7fe-5a5825765403\scratchpad\storm\crash_playbook\`. These are base rates, not tests or trading rules. Dollar examples assume a single filer in the 22% bracket; the owner's real bracket and holdings are unknown. The shared web-search budget ran out before every source was checked.

## Findings

1. **After triggers like today's, a gain has been no more likely than on any other day.** Counting each episode once (Table A), the index was higher 12 months later 62–80% of the time, against 75–82% for any day. Means are higher after the Nasdaq and VIX triggers, but no cell reaches t = 2. Charts that count every high-VIX day show 93%; counting episodes removes about 70% of the excess (E1). In about half the episodes the index fell another 10% or more within the year (E2), and the strongest cell I found does not replicate (E3). The repo's 0 of 44 agrees.
2. **Selling was the expensive error; waiting to buy is a cheap one.** Sellers in 2008–09 and 2020 ended well behind holders, and almost a third of panic sellers never came back (E4–E6). A lump sum beat twelve monthly instalments two times in three, in a drawdown or not, by 2.5 points on average, with a worse bad tail (E7). Averaging in is right only when the alternative is not investing.
3. **Rebalancing into a fall is risk control with a premium near zero.** It deepened the trough by 0.5–5 points and was usually 0.3–3 points ahead once the index recovered; in the Nasdaq-100's 2000–02 fall it cost 16 points at the low (E8–E10). The frozen model does the opposite on purpose, so a buy-the-dip overlay would cancel it.
4. **Tax: one real move, one mostly folklore.** Loss harvesting needs no forecast but is small (E11, E12). On $100,000 put into a Nasdaq-100 fund at the October high, the $19,800 short-term loss is worth $660 on the 2026 return with no gains to offset, about $1,400 net over seven years once the lower basis is taxed at 15%, or $4,356 at once against short-term gains [calc]. "Convert to a Roth at a discount" is a bet on recovery that cannot be undone (E13). Neither applies to the paper account.
5. **Do not** add leverage after a loss, concentrate in the hardest-hit names, or act on a call of the bottom (E14–E16). Retail did the first two this month.
6. **Ranked playbook, no forecast needed.**
   1. *Both:* change nothing by hand. Paper: no override, added risk, new instruments or reset (a reset changes the record, not a position). Real: do not sell.
   2. *Real savings:* keep contributions on schedule; invest cash already meant for stocks.
   3. *Real savings:* harvest taxable losses by 31 December into a fund on a different index. The paper account pays no tax.
   4. *Real savings:* use IRA room, $7,500 each for 2026 and 2027.
   5. *Real savings, not the model:* rebalance to target once 5 points off, new money first.
   6. *Real savings:* Roth conversion only if tax rates already justified it.

## Evidence table

**Table A. Forward returns after the three triggers that fired by 2026-11-20** [calc]. Episode = first close through the trigger, re-armed by a new all-time high (VIX: 126 sessions below 35). Cells: median/share higher/worst (any-day share higher). 36m has one or two fewer episodes.

| Trigger | n | 1m | 3m | 6m | 12m | 36m |
|---|---|---|---|---|---|---|
| S&P 500 11.6% below high, 1950– | 21 | +1.6/62%/−14.7 (62%) | +0.4/57%/−10.9 (67%) | +5.3/62%/−11.3 (71%) | +15.9/62%/−39.0 (75%) | +30.5/80%/−27.9 (86%) |
| Nasdaq-100 19.8% below high, 1985– | 8 | +10.1/62%/−7.8 (63%) | +15.2/75%/−4.2 (70%) | +25.9/75%/−14.7 (74%) | +42.6/75%/−52.8 (82%) | +44.9/86%/−70.2 (88%) |
| VIX first close ≥ 35, S&P 500, 1990– | 15 | +2.9/67%/−18.2 (64%) | +8.1/73%/−21.0 (70%) | +12.7/87%/−32.2 (75%) | +20.6/80%/−15.9 (81%) | +34.6/100%/+5.2 (83%) |

| # | Evidence | Source |
|---|---|---|
| E1 | Every day with VIX ≥ 35 (354): 93% higher at 12 months, mean +28%. The 15 episodes: 80%, +15%. Any day: 81%, +10% | [calc] |
| E2 | Fell a further 10% or more within a year: 11 of 21 (S&P), 4 of 8 (Nasdaq), 7 of 15 (VIX) | [calc] |
| E3 | Best of 135 correlated cells: Nasdaq-100 six months after first closing 10% below a high, +19% against +10% on comparable days (t = 2.8, n = 33). S&P 500 since 1950: +6.2% against +4.6%. 32 of 35 episodes sit in 1985–99 or 2016–26 | [calc] |
| E4 | 401(k) savers who sold all stock in Oct 2008–Mar 2009 and stayed out: +2% by June 2011. Those who kept stock: +50% | [InvestmentNews on Fidelity, 2011](https://www.investmentnews.com/retirement-planning/401k-holders-who-bailed-on-stocks-in-2008-made-out-worse-fidelity/38251) |
| E5 | Under 0.5% of Vanguard self-directed investors went all-cash in Feb–May 2020; 56–58% of them were ahead at end-March, 14–16% by end-May | [FA Magazine on Vanguard, 2020](https://www.fa-mag.com/news/the-price-of-panic-58093.html) |
| E6 | Almost a third of panic sellers (653,455 accounts) never returned to risky assets | [MIT](https://dspace.mit.edu/handle/1721.1/141712); [Irish Times, 2021](https://www.irishtimes.com/business/personal-finance/stocktake-married-middle-aged-male-investors-more-likely-to-freak-out-1.4694880) |
| E7 | Lump sum against 12 monthly instalments: wins 63% of S&P 500 month-starts since 1934 (+2.5 points at 12 months), 62% of those 10% or more below the high; Nasdaq-100 73% and 69% (+6.8). Its worst 5% trail by 13–27 points. Vanguard: 68%; averaging beat cash 69% of the time | [calc]; [Vanguard, 2023](https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf) |
| E8 | 60/40, 1926–2009: 8.5% a year rebalanced monthly, 8.6% annually, 9.1% never (84% average equity) | [Vanguard, 2010](https://www.aaii.com/files/journal/pdf/best-practices-for-portfolio-rebalancing.pdf) |
| E9 | 60/40 index/T-bills from each pre-bear peak since 1956, rebalanced monthly minus untouched: −0.5 to −1.0 points at the trough in six fast falls, −2.4 to −4.8 in five longer ones, −15.6 for the Nasdaq-100 in 2002; +0.3 to +3.0 at recovery in 9 of 11. Man AHL: 5 points more drawdown in 2007–09 | [calc]; [Man AHL](https://www.man.com/maninstitute/strategic-rebalancing-summary) |
| E10 | Threshold against calendar rebalancing: 5–22 bp a year, from fewer trades | [Vanguard, 2024](https://corporate.vanguard.com/content/dam/corp/research/pdf/the_rebalancing_edge_optimizing_target_date_fund_rebalancing_through_threshold_based_strategies.pdf) |
| E11 | Harvesting: 0.82% a year with the wash-sale rule, 1926–2018 (2.13% in 1926–49, 0.51% in 1949–72), given gains to offset at 35%; about 3 points of spread across investors. Long-run value under 0.2–0.3% a year because the lower basis gives most back; in the 0% bracket harvest gains instead | [Chaudhuri et al., 2020](https://rpc.cfainstitute.org/en/research/financial-analysts-journal/2020/empirical-evaluation-tax-loss-harvesting-alpha); [Khang et al., 2021](https://rpc.cfainstitute.org/research/financial-analysts-journal/2021/tax-loss-harvesting); [Kitces, 2014](https://www.kitces.com/blog/evaluating-the-tax-deferral-and-tax-bracket-arbitrage-benefits-of-tax-loss-harvesting/) |
| E12 | $3,000 a year of net loss against other income. No substantially identical purchase 30 days either side, including in an IRA (where the loss is not added to basis); no IRS rule on ETF pairs. 2026, single: 22% from $50,400; 0% long-term gains to $49,450. IRA limit $7,500 for 2026 and 2027 | IRS: [Topic 409](https://www.irs.gov/taxtopics/tc409), [Pub. 550](https://www.irs.gov/publications/p550), [brackets](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill), [IRA 2026](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-ira-contribution-limits), [IRA 2027](https://www.irs.gov/node/167581); [gains thresholds](https://www.currentfederaltaxdevelopments.com/blog/2025/10/9/2026-inflation-adjustments-for-tax-professionals-revenue-procedure-2025-32-analysis) |
| E13 | A Roth conversion is taxed on the value converted and cannot be undone. The same shares: $4,400 of tax now against $5,500 in October | [ThinkAdvisor, updated 2026-10-20](https://www.thinkadvisor.com/tax-facts/2026/05/21/the-market-downturn-discount-for-roth-conversions/); [calc] |
| E14 | $9bn went into TQQQ in the first half of 2022 as it fell 71%; the average dollar lost 79%. On 2026-11-05 retail sold single stocks and kept buying TQQQ and SOXL | [FactSet, 2022](https://insight.factset.com/h1-2022-etf-flows-steadfast-brave...and-foolhardy); [IBTimes, 2026-11-06](https://www.ibtimes.com/retail-investors-stock-selling-dow-market-rout-3809508) |
| E15 | 40% of Russell 3000 stocks (57% in technology) fell 70% or more for good, 1980–2014; 58% of US stocks since 1926 did not beat T-bills. Retail bought $1.6bn of Nvidia and $401m of a 2x Nvidia fund in three sessions; it fell 14% on 20 November | [J.P. Morgan, 2014](https://www.chase.com/content/dam/privatebanking/en/mobile/documents/eotm/eotm_2014_09_02_agonyescstasy.pdf); [ASU on Bessembinder](https://news.wpcarey.asu.edu/20180917-do-stocks-outperform-treasury-bills); [Hedgeweek, 2026-11-17](https://hedgeweek.com/news/retail-investors-pour-1-6bn-into-nvidia-despite-ai-selloff); brief |
| E16 | Rallies of 10% or more inside bear markets: ten in the Nasdaq-100's −83% of 2000–02 (largest +53%), four in the S&P 500's −57% of 2007–09. "Sell at −20%, return at a new high" buys back 25% higher | [calc] |

## Ideas worth a pre-registered test (or why none)

- **No predictive test.** Table A is the whole case for buying the panic and it does not separate from an ordinary day. H5 (VIX ≥ 40 re-entry) failed at P = 0.054 / 0.083 / 0.159 and cannot be re-tuned; a VIX ≥ 35 or drawdown-depth version is that re-tune, and E3 is what a re-tune finds. Prior under 2%.
- **One structural candidate for the 2027-11-19 review, only if real money will sit in a taxable account: lot order alone.** H1 bundled four rules and lost 1.0–2.0 points a year before tax (`reports/retail_edge_results.md`). Its part (a) changes no trade: when the frozen rule sells, sell loss lots first instead of FIFO, so pre-tax tracking error is zero. Test with H1's ledger, metric and bootstrap on both universes. My estimate: +0.2 to +0.6 points a year after tax; 30% to pass. Moot in an IRA or if the broker cannot choose lots. It is a new trial.

## What I looked for and did not find

- What 2022 sellers earned afterwards.
- Vanguard's 2020 "cash panickers" note and 2022 "Rational rebalancing" paper (dead links; E5 is second-hand).
- The MIT paper's text ("30.9% never returned" is from press coverage).
- Alpaca's documented tax-lot method.
- Total-return data before 1988. With dividends (1988–2025) the lump sum wins 76%, so E7 understates it.
- A stock/bond version of E9 (mine uses T-bills).
- A checked source for expected returns rising with implied variance (Martin 2017 [memory]); if true it is pay for risk, not edge.
