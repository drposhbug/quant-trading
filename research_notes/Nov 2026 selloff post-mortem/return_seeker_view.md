# Return-seeker view: how do we get bigger gains?

2026-11-21. STORM perspective note; nothing here was re-run. Repo numbers are cited from `reports/`. "P(pass)" is my subjective probability that the lever beats the frozen model in ONE pre-registered paired-bootstrap test (P < 0.05, shipped universe AND end-2014 list, MATH.md change control). Items marked **[unverified]** are from memory or a secondary source I could not confirm this session.

## Bottom line

Nothing on the menu raises return per unit of risk by an amount this project can prove. The levers that reliably add return either add risk in proportion (leverage, less de-risking) or are not trading levers at all (account type, savings). At $100k, a tax-advantaged account and $500/month of new savings are worth more than every tested signal combined.

Working assumptions for the arithmetic: forward excess Sharpe 0.7 (the end-2014 list shows 0.84 ex T-bill in `backtest_results.md`, haircut for hindsight), vol 16%, T-bill 4.2% ([FRED DGS3MO, 2026-11-02](https://fred.stlouisfed.org/series/dgs3mo)), borrowing at T-bill + 1.5% (about 5.7%; matches IBKR Pro's benchmark + 1.5% tier under $100k, [page undated](https://www.interactivebrokers.com/en/index.php?f=55459)). Growth = r + L·μ − (L−1)·spread − ½L²σ².

## 1. More risk at the same Sharpe

| Leverage L | CAGR if Sharpe 0.7 | CAGR if Sharpe 0.35 | Vol drag | MaxDD, repo ^NDX engine since 1986 |
|---|---|---|---|---|
| 1.0 | 14.1% | 8.5% | 1.3% | −34% |
| 1.5 | 17.4% (+3.3 pp) | 9.0% (+0.5 pp) | 2.9% | −50% |
| 2.0 | 20.0% (+5.9 pp) | 8.8% (+0.3 pp) | 5.1% | −62% |

- The gain exists only if the Sharpe estimate is right. At half the assumed Sharpe, leverage adds nothing and still doubles the drawdown.
- Repo (`leverage_results.md`): no L passes. L = 1.5 added +0.5 to +3.8 pp CAGR across six indices, but the Nikkei drawdown went from −42% to −70% and under T-bill + 3% financing it won in only 3 of 6 markets. On the shipped names, P(Sharpe L=1.5 ≤ L=1.0) = 1.000: leverage rescales the bet, it does not improve it.
- Raising the vol target alone does little because the 100% gross cap binds; real extra risk needs borrowing.
- Vehicles: margin costs the spread above. LETFs: the repo found QLD tracks synthetic 2x within −0.5%/yr and fell −83%. Futures finance closer to T-bill; deep ITM calls add option spreads on single names **[both unverified]**.
- Published: vol targeting improves Sharpe mainly for equities (0.40 to ~0.5, [Harvey et al. 2018](https://people.duke.edu/~charvey/Research/Published_Papers/P135_The_impact_of.pdf)), but out of sample the gain is not systematic ([Cederburg et al., JFE 2020](https://www.lehigh.edu/~xuy219/research/COWY.pdf)).
- P(pass) on the repo's Sharpe metric: ~1%. A CAGR-metric test would pass more often, but it only tests whether tech stocks went up.

## 2. Kelly, honestly applied

Full Kelly leverage = Sharpe / vol = 0.7 / 0.16 = 4.4x. That number is useless: the standard error of a Sharpe ratio over 11.6 years is about 0.34, so a true Sharpe of 0.35 (Kelly 2.2x) is well within the data. Half-Kelly on the point estimate (2.2x) is full Kelly on the plausible low case, and betting 2x Kelly has zero expected growth. Estimation error always argues for shrinking ([MacLean, Thorp, Ziemba 2010](https://escholarship.org/content/qt5mr5k8qj/qt5mr5k8qj.pdf)). The frozen model at L = 1 is about quarter-Kelly on the point estimate and half-Kelly on the low case: already where a careful sizer would sit. Extra CAGR: none defensible. P(pass): ~1%.

## 3. Less de-risking

- Dropping the risk engine entirely: 32.6% CAGR vs 23.2%, MaxDD −41.7% vs −22.5%, Sharpe 1.23 vs 1.25 (`backtest_results.md`, hindsight names). That is +9 pp for nearly double the drawdown: again leverage, not edge.
- Long run, the engine at L = 1 earned less than buy-and-hold in 5 of 6 markets (^NDX 13.2% vs 14.9%) while cutting MaxDD from −82% to −34%. The 200-day rule costs roughly 1 to 2 pp/yr and buys drawdown control. Independent out-of-sample work agrees that moving-average timing does not beat holding on return ([Zakamulin 2014](https://link.springer.com/article/10.1057/jam.2014.25)).
- ±2% band (H4): fails. VIX ≥ 40 faster re-entry (H5): +0.3 pp CAGR, P = 0.054 / 0.083 / 0.159, gain concentrated in 2008-11 and 2025-04; it failed its gate and by the repo's own rule cannot be re-tuned.
- P(pass): removing/softening the halving ~3%; a newly registered re-entry rule ~10%, and only if this selloff supplies a fresh episode.

## 4. Different universe, uncorrelated streams

- Gold sleeve: Sharpe 1.35 vs 1.26 (P = 0.024); IEF + GLD: 1.42 (P = 0.029) but CAGR drops 23% to 18% (`universe_results.md`). Neither clears Bonferroni (0.0042) and neither was run on the end-2014 list. Levering the diversified book back to equal vol would add about +1 to +2 pp after financing, if the Sharpe gain is real. Gold fell 4.6% on 11-20, so the hedge is unreliable on the days that matter.
- Managed futures: +0.13 Sharpe on a 5-year window in the repo. The SG Trend Index lost about 18.7% in the 12 months to April 2025, its worst stretch in 25 years ([AlphaSimplex via AdvisorAnalyst](https://advisoranalyst.com/?p=167192)).
- Value, quality, small, international: published factor returns are 26% lower out of sample and 58% lower post-publication ([McLean and Pontiff, JF 2016](https://econpapers.repec.org/RePEc:bla:jfinan:v:71:y:2016:i:1:p:5-32)). Broadening lowers single-sector ruin risk; it is not a return lever. Equal-weight challenger: closed, fails (0.895 vs 0.975 on the honest list).
- P(pass): gold/IEF sleeve ~20% (higher Sharpe, lower CAGR); trend sleeve ~8%; factor tilts ~3%.

## 5. Harvestable premia

- Earnings-announcement premium: repo FAIL, −8.3%/yr vs equal-weight, t = −1.43; adding a 20% sleeve cut Sharpe 1.32 to 1.15.
- Post-earnings drift: gone from non-microcaps by 2006 ([Martineau 2022](https://nowpublishers.com/article/Details/CFR-0122)); two 2025 papers dispute this ([UCLA Anderson brief](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again)). Unsettled, so not bankable.
- Overnight vs intraday: disappears after costs ([Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/)); the NightShares ETFs liquidated in August 2023 ([Elm Wealth](https://elmwealth.com/night-shift/)).
- Put-writing / covered calls: S&P 500 beat BXM and PUT in 2023, 2024 and 2025 (2025: 17.9% vs 8.9% / 9.2%); PUT Sharpe 0.51 vs 0.61 since 2007 ([Dividend.com](https://www.dividend.com/options-and-income-channel/is-options-upside-becoming-capped/), **[unverified against Cboe data]**). I found no direct academic measurement of post-2020 variance-premium decay **[unverified]**. On this basket, calls cap the right tail that produced the return. Retail pays an average 12.6% bid-ask spread on its preferred weekly options and loses on average ([Bryzgalova, Pavlova, Sikorskaya, JF 2023](https://lbsresearch.london.edu/id/eprint/2827)).
- P(pass): 1 to 3% each.

## 6. Non-trading levers

- Account type: the repo's own tax ledger (H1, top bracket, taxable) shows after-tax CAGR of 16.2% vs 23.4% pre-tax (shipped) and 10.6% vs 15.5% (end-2014). Daily rebalancing in a taxable account costs about 5 to 7 pp/yr. Running the same model in an IRA/Roth recovers most of that with no added risk; less at lower brackets.
- Loss harvesting: 0.82%/yr with the wash-sale rule, 1926-2018 ([Chaudhuri, Burnham, Lo, FAJ 2020](https://rpc.cfainstitute.org/research/financial-analysts-journal/2020/empirical-evaluation-tax-loss-harvesting-alpha)). The repo's rule set gave +0.6 to +0.8 pp after tax but lost 1 to 2 pp pre-tax; fail (P = 0.13 / 0.22).
- Savings: 15% on $100k is $15k/yr. $500/month is $6k/yr, the same dollars as +6 pp CAGR, with certainty.
- Cash yield: +0.5%/yr (C1), already done. Fees: near zero.
- Behaviour gap: investors earned 1.2 pp/yr less than their funds over the 10 years to 2025, 2.1 pp in the most volatile funds, about 14 pp in spot bitcoin ETFs ([Morningstar Mind the Gap 2026](https://www.morningstar.com/business/insights/research/mind-the-gap)). More vol makes this worse.

## 7. Reaching for return after a loss

- Most active US households earned 11.4% vs the market's 17.9%, 1991-96 (Barber and Odean 2000, **[unverified this session]**).
- Fewer than 1% of Taiwanese day traders were reliably profitable ([Barber, Lee, Liu, Odean 2014](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24)); 97% of Brazilians who day traded for 300+ days lost money ([Chague, De-Losso, Giovannetti](https://econpapers.repec.org/RePEc:fgv:eesptd:525)).
- 93% of Indian individual F&O traders lost money FY22-24, and over 75% of losers kept trading ([SEBI 2024](https://www.sebi.gov.in/media-and-notifications/press-releases/sep-2024/updated-sebi-study-reveals-93-of-individual-traders-incurred-losses-in-equity-fando-between-fy22-and-fy24-aggregate-losses-exceed-1-8-lakh-crores-over-three-years_86906.html)).
- Retail lost $358k per day on S&P 0DTE options after May 2022 ([Bloomberg on Beckmeyer et al.](https://www.bloomberg.com/news/articles/2023-04-21/day-traders-lose-358-000-per-day-gambling-on-zero-day-options)).
- A US cap on retail FX leverage cut high-leverage traders' losses by 40% ([Heimer and Simsek, NBER w24176](https://nber.org/papers/w24176)).

The account is two sessions old, down 5.0%, and the vol target was already moved 15% to 25% to 20% on 11-18/19. Asking for more return now is the pattern these studies describe. The change-control rule ("never during a drawdown") exists for exactly this.

## Ranked table

| # | Lever | Expected extra CAGR | Extra drawdown | P(pass) | Verdict |
|---|---|---|---|---|---|
| 1 | Tax-advantaged account | +2 to +7 pp after tax (bracket-dependent) | none | n/a (arithmetic) | Do first |
| 2 | Save $500/month | = +6 pp at $100k, in dollars | none | n/a | Do |
| 3 | Do not interfere (behaviour gap) | +1 to +2 pp kept | none | n/a | Do |
| 4 | Gold / IEF sleeve | −0.3 to −5 pp unlevered; +1 to +2 pp if re-levered | slightly lower | 20% | Best testable candidate; register for 2027 |
| 5 | Lean tax-loss harvesting (taxable only) | +0.5 to +0.8 pp after tax | none | 10% | New hypothesis, 2027 |
| 6 | Faster re-entry after panic | +0.3 pp | ≤ 3 pp | 10% | Failed gate; needs new episodes |
| 7 | Managed-futures sleeve | 0 to +1 pp | lower | 8% | Too little data |
| 8 | Leverage 1.5x (margin/futures) | +3.3 pp if Sharpe 0.7; +0.5 pp if 0.35 | −22% to −32% (sample); −34% to −50% (long run) | 1% | Risk purchase, not edge |
| 9 | Leverage 2x / LETFs | +5.9 pp to +0.3 pp | −62% long run; QLD −83% | 1% | No |
| 10 | Remove 200-day halving | +1 to +2 pp | roughly doubles | 3% | Risk purchase |
| 11 | Half-Kelly on point estimate (2.2x) | unknowable | ruin-adjacent | 1% | No |
| 12 | Factor tilts / equal weight | ~0 | mixed | 3% | No (EW already closed) |
| 13 | Earnings, PEAD, overnight, option selling | ≤ 0 after costs | fatter left tail | 1 to 3% | No |

Bigger gains here mean bigger risk (rows 8 to 11) or more savings and less tax (rows 1 to 3). Rows 4 to 7 are the only research worth registering for the 2027-11-19 review.
