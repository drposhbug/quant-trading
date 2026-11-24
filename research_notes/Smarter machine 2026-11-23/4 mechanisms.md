# 4 Mechanisms: market-structure skeptic notes (2026-11-23)

Perspective: a pattern is worth learning only if (a) someone is forced or paid to create it and (b) there is a reason it has not been traded away (capacity limits, risk, an effect too small or too slow for the people who could trade it). Behavioural patterns are allowed, but only with a named reason they have not been arbitraged.

Confidence tags: [V] = checked against an abstract or summary in this session; [M] = from memory of the paper, should be checked before anyone relies on the exact number; [pre-2015] = evidence documented only before 2015.

---

## Q1. Why momentum wins small and often, then loses big

### Mechanism
1. **Option-like payoff after market declines (time-varying beta).** After a bear market the loser leg is full of high-beta, beaten-down stocks (often distressed, levered). The long-short book is therefore *short market beta* exactly when the market is most likely to rebound sharply. In a rebound the losers rally hardest: the strategy behaves like a short call on the market. Daniel and Moskowitz (2016, JFE 122(2), "Momentum Crashes") [V for the doubling claim, M for the crash sizes]: the winner-minus-loser (WML) portfolio lost about 91% in July-August 1932 and about 73% in March-May 2009, both in the rebound after a crash. Their dynamic strategy, scaled by forecast mean and variance, roughly doubles the static strategy's Sharpe ratio. Grundy and Martin (2001) first documented the beta flip.
2. **Volatility clustering in momentum itself.** Barroso and Santa-Clara (2015, JFE 116(1), "Momentum Has Its Moments") [M]: scale WML to a constant volatility target using its own realized volatility over the last six months (126 days). Over 1927-2011, Sharpe rose from about 0.53 to about 0.97 and excess kurtosis fell from about 18 to about 2.7. Momentum risk is predictable; market risk does not explain it.
3. **Crowding.** Lou and Polk ("Comomentum", RFS 2022) [M]: when momentum stocks co-move unusually strongly (abnormal residual correlation among winners and among losers), arbitrage capital is crowded, and subsequent momentum returns are low or negative, with reversal. Crowded exits produce the sharp days, for example 9 Nov 2020 (vaccine news: value up, momentum down), one of the worst momentum days on record, and the Jan 2021 meme-stock short squeeze.
4. **Turning points.** Goulding, Harvey and Mazzoleni (JFE 149(3), 2023, "Momentum Turning Points") [V]: when slow (12-month) and fast (1-2-month) trend signals disagree (states they call Correction and Rebound), the market is more likely at a turning point. Those states have lower average returns and higher volatility, and they are where slow momentum is caught wrong-footed. Blending slow and fast speeds adds alpha. Companion paper: "Breaking Bad Trends" (FAJ 2023).
5. **Newer.** Bianchi et al. ("Taming momentum crashes", SSRN 2022) [V]: modelling time-varying *skewness* reduces downside exposure beyond volatility scaling. Byun and Jeon (FAJ 2023) [V, secondary]: crashes are concentrated in names far from their 52-week highs. Dierkes and Krupski's crash indicator (1928-May 2020) [V, secondary]: Sharpe 1.12 vs 0.94 for constant-volatility scaling.

### Why it is not traded away
Momentum is a crowded, capacity-limited premium. The crash risk *is* the reason the premium exists: it is a short-option payoff, and few want to sell that option at the bottom of a bear market. Volatility scaling is well known but costs return in calm trends and requires de-risking at precisely the moment it feels wrong.

### Observable warning states (in order of practicality with daily prices)
- **(a) Realized volatility of the momentum long-short itself**, trailing 3-6 months. The best single state variable: it is cheap, it is computable from the project's data, and it carries most of the gain (Barroso and Santa-Clara).
- **(b) Bear-market flag**: market return over the past 24 months is negative (Daniel and Moskowitz). Combined with high market volatility, this marks the rebound-crash state.
- **(c) Beta of the momentum book to the market**: a strongly negative beta means the book is short the rebound.
- **(d) Slow/fast trend disagreement** (Goulding, Harvey and Mazzoleni).
- **(e) Comomentum** (crowding): needs residual correlations, which can be computed from daily returns.

For a long-only top-N momentum book (the project's case), the crash shows up as the winners (defensive or the prior leaders) lagging a junk rally. The same states apply. The long-only loss is smaller, but it is a large *relative* loss against the market.

---

## Q2. Mechanical effects in large caps

The main table is below; notes on each row follow it.

| Mechanism | Who is forced | Timing | Recent size in large caps | Slow retail capturable? | Free data | Source |
|---|---|---|---|---|---|---|
| S&P 500 additions | Index funds must buy by effective date | Announce (about 5 days before effective) to the effective-date close | Abnormal return fell from about 7.4% (1990s) to <1% (2010-2020); deletions -16% (1990s) to -0.6% (2010s) | No (front-run by pros; pre-announcement drift; migrations from MidCap net out demand) | S&P press releases; Wikipedia change log | Greenwood and Sammon, JF 80(2) 2025 [V] |
| Quarterly S&P rebalance / float and share changes | Index funds | 3rd Friday of Mar/Jun/Sep/Dec close | Small, intraday and closing auction; mostly reverses within days | No | Exchange closing-auction data (not free) | Practitioner; no clean recent study found |
| Month-end / quarter-end pension and balanced-fund rebalancing | Pensions, target-date and balanced funds with fixed weights | Last days of the month/quarter; also threshold rebalances mid-month | When equities are overweight after a stock-beats-bond month, next-day equity return about -17 bp; about $16bn/yr cost | **Marginal-yes** (market-level timing; a slow trader can act at month end) | Month-to-date stock vs bond returns (SPY, AGG/TLT) | Harvey, Mazzoleni and Melone, NBER w33554 (2025) [V] |
| Payment-cycle "dash for cash" (turn of month) | Institutions raising cash for month-end payments (pensions, payroll, settlements) | Selling about T-8 to T-4 before month end; high returns the following ~7 days | Turn-of-month market premium documented globally; magnitude not verified this session | **Marginal-yes** (market-level, calendar-only) | Index prices only | Etula, Rinne, Suominen and Vaittinen, RFS 33(1) 2020 [V] |
| ETF creation/redemption flows | Authorized participants arbitrage ETF mispricing into the underlying | Days to weeks | Short high-flow / long low-flow ETFs: +1.1-2.0%/month (all US equity ETFs; large liquid sector ETFs likely smaller) | **Marginal** (weekly horizon fits; check it survives in SPDR sector ETFs after 2018) | ETF shares outstanding (issuer sites, daily) | Brown, Davies and Ringgenberg, RoF 25(4) 2021 [V] |
| Option-dealer gamma hedging | Market makers delta-hedging | Intraday, last 30 minutes; reverts over the next days | Negative dealer gamma: market intraday momentum; positive gamma: damping/reversion | No (intraday; dealer positioning data is paid) | SqueezeMetrics-style GEX (paid); OCC open interest (partial) | Baltussen, Da, Lammers and Martens, JFE 142(1) 2021 [V] |
| Option-expiry pinning | Delta-hedgers of large open interest | Monthly expiry Friday (and now daily 0DTE on the index) | Pinning toward strikes on expiry day documented for optionable stocks | No (sub-1-day, cents) [pre-2015] | Open interest by strike (CBOE, partly free) | Ni, Pearson and Poteshman, JFE 2005 [M, pre-2015] |
| Leveraged and inverse ETF rebalancing | LETF sponsors must rebalance near the close in the direction of the day's move | Last ~30 minutes on large-move days | Gross effect real on |move| > 2% days, but small after flows; most of 2022-23 LETF decay is compounding, not rebalancing | No (intraday close) | LETF AUM and leverage (issuer) | Ivanov and Lenkey (2006-2014, small) [V]; Bianchi and Goldberg arXiv 2026 [V] |
| Buybacks and blackout windows | Firms legally constrained to stop buying from about quarter end to a few days after earnings | About 4-6 weeks per quarter | Practitioner test found no significant return difference for heavy repurchasers in or out of blackout | No (no detectable effect) | 10-Q repurchase tables; earnings calendar | Alpha Architect 2019 (blog, not peer-reviewed) [V]; ECGI repurchase-timing work [V] |
| Earnings-announcement premium | Not forced; risk and attention premium (volume and attention spike, risk concentrated in announcement) | Announcement week; run-up into the date | Options-implied ex-ante premium about 15 bp per announcement, S&P 500 firms 2010-2021; premium may have shifted toward 8-K dates after 2004 | **Yes-marginal** (hold into scheduled dates: 4 times a year x 15 bp, before costs) | Earnings calendar (Nasdaq/Yahoo, free); prices | AEA 2024 paper [V]; "Disappearing EAP" (IIMB 2020) [V]; Frazzini and Lamont 2007 [pre-2015] |
| Ex-dividend dates | Tax-driven dividend capture and avoidance | Ex-date | Price drop below the dividend historically; large caps today: a few bp, eaten by taxes and spread | No | Dividend calendar | Elton and Gruber 1970 onward [pre-2015, M] |
| Tax-loss selling / turn of the year | Taxable investors realising losses in December | Late Dec to early Jan | January effect concentrated in small caps; in large caps weak and inconsistent since 2000 | No | Prices | Literature consensus [M] |
| Passive inflows on pay dates (401k contributions) | Defined-contribution plans investing payroll contributions | 1st and 15th, turn of month | Folded into the turn-of-month effect; no separate clean large-cap estimate | Marginal (same trade as the turn of month) | Calendar | Etula et al. 2020 [V, as above] |
| Short squeeze / securities-lending constraints | Shorts forced to cover; borrow recalls | Event-driven | S&P 500 names are almost all general collateral (cheap borrow); squeezes rare (2021 memes were mostly non-S&P) | No | FINRA short interest (twice monthly); borrow fees (paid) | Project's own earlier short-interest test found nothing [project] |
| IPO lock-up expiries | Insiders become free to sell | 90-180 days after IPO | About -1 to -3% around expiry, mostly small, new firms; rarely S&P 500 members | No (outside universe) | IPO prospectuses | Field and Hanka JF 2001 [pre-2015, M] |

### Notes per mechanism
- **Index effect.** This is the textbook forced-trade effect, and it is now nearly gone in the S&P 500. Three reasons (Greenwood and Sammon): migrations from MidCap 400 to S&P 500 mean MidCap funds sell while S&P funds buy, so net demand is small; pre-announcement predictability lets pros position early; and liquidity provision has deepened. Lesson: even a forced trader's footprint is arbitraged once it is predictable and large.
- **Rebalancing flows.** This is the most promising mechanical effect for *this* setting. The forced trader is large (trillions in balanced, target-date and pension assets) and calendar-bound, and the direction is computable from public prices (equity vs bond return month to date). The signal is market-level, not cross-sectional, so it does not fit a 500-stock ranking. It would time the account's *net equity exposure* in the last days of the month. Effect size about 17 bp next day is near the threshold where costs (a few bp) leave something, but only a handful of trades a year carry it. Expect decay now that it is published (2025).
- **Turn of month.** This has the longest persistence of any calendar effect and has a forced-payment mechanism (Etula et al.). It is also market-level.
- **ETF flows.** These have a mechanism (authorized-participant arbitrage passes non-fundamental demand into the underlyings) and a weekly horizon. The reported 1.1-2.0%/month is across all ETFs. The test should use only liquid sector ETFs and their large-cap holdings and should check post-2018 data.
- **Gamma, pinning, LETF.** All are real but intraday. A slow trader cannot capture them. At most they explain noise in close-to-close returns (end-of-day momentum on negative-gamma days, reverting over the next days). One possible use: a negative-gamma state is a *volatility regime* flag, not a return signal.
- **Buyback blackouts.** The mechanism is plausible, but the effect is undetectable: buybacks are a small fraction of daily volume, and blackouts across firms are staggered.
- **Earnings-announcement premium.** This is not forced. It is a risk premium, and risk premia are what persist. It is stock-level and calendar-driven, so it fits a cross-sectional ranking as a *tilt*: prefer names with an announcement inside the holding window. It is cheap to test because the free earnings calendar is enough. Evidence after 2010 is thin and mixed, so it needs its own out-of-sample test.

---

## Q3. Where information is slow even in large caps

The general principle: information is slow when processing it is costly and the payoff to any one analyst is small. Examples are long text, cross-firm links nobody owns, and intangibles with no market price.

- **Lazy Prices** (Cohen, Malloy and Nguyen, JF 75(3) 2020; sample 1995-2014) [V]: firms that change the text of their 10-K or 10-Q underperform. There is no announcement reaction; returns accrue later through news and earnings. Evidence after 2015: I found only a student replication (weak) and an options-market follow-up showing that the volatility smirk rises after big changes, which means the options market is now pricing it. Treat as **documented mainly before 2015**. Data: free (EDGAR).
- **Customer-supplier links** (Cohen and Frazzini, JF 2008) [M, pre-2015]: returns of major customers predict supplier returns about a month ahead. Shared-analyst links (Ali and Hirshleifer, JFE 2020) [M]: connected-firm momentum strongest via shared analysts. Post-2015 evidence is thin. These link signals are widely harvested by quant funds. The project's own lead-lag scan on 12 megacaps found nothing, consistent with decay in the most-watched names.
- **Intangible-heavy firms / R&D** (Eberhart et al.; Lev and Srivastava "Explaining the Recent Failure of Value", 2019-2022) [M]: accounting book value misses intangibles, so pricing errors persist where earnings are depressed by expensed R&D. This is a slow, months-to-years effect. Its evidence is mainly through valuation factors, not a daily ranking.
- **Complexity** (Cohen and Lou, JFE 2012, conglomerates) [M, pre-2015]: multi-segment firms are priced late relative to pure plays. Large caps are often conglomerates, so this applies in principle, but post-2015 evidence was not found.
- **Decay benchmark.** McLean and Pontiff (JF 2016) [V]: anomaly returns are 26% lower out of sample and 58% lower after publication, and the decay is larger for anomalies with bigger in-sample returns. A 2025 study [V] finds the average post-publication anomaly alpha is close to zero when weights are estimated out of sample. Default prior for any published slow-information signal in S&P 500 names after 2015: assume at most half the published effect, possibly zero.

Bottom line: slow-information signals need text or filing data, horizons of weeks to months, and are documented mostly before 2015. They suit a slow trader *by horizon*, but the edge in large caps is likely small now.

---

## Q4. The ceiling, from the fundamental law

IR is about TC x IC x sqrt(BR), where TC is the transfer coefficient (how well constraints let the portfolio express the signal) and BR is the number of *independent* bets per year.

**Why nominal breadth is a lie.** A daily ranking of 500 names looks like 500 x 252 = 126,000 bets a year (sqrt about 355). That would give IC 0.01, IR 3.5, which no one gets from public price data in large caps. Two corrections:
- Stocks share factors (market, sector, size, style). Effective independent names are perhaps 50-100, not 500.
- At 5- and 21-day horizons, daily forecasts overlap. Independent periods are 252/h per year: about 50 for h=5 and 12 for h=21.

| Horizon | Effective BR/yr (approx.) | IR gross, IC=0.01 | IC=0.02 | IC=0.03 |
|---|---|---|---|---|
| 21 days | 75 names x 12 = 900 | 0.30 | 0.60 | 0.90 |
| 5 days | 75 x 50 = 3,750 | 0.61 | 1.22 | 1.84 |
| 1 day | 75 x 252 = 18,900 | 1.37 | 2.75 | 4.12 |

**Then costs and TC.**
- *Cost per unit of signal.* Quintile long-short spread per period is about IC x (cross-sectional sd of returns) x 2.8.
  - At 1 day, cross-sectional sd is about 1.7%. IC 0.01 gives about 4.8 bp/day gross, IC 0.02 about 9.5 bp, IC 0.03 about 14 bp. A daily-horizon signal turns over most of the book each day (about 70-90%), so round-trip cost at about 5 bp per side is about 7-9 bp/day. Net: **IC 0.01 negative, IC 0.02 about zero, IC 0.03 marginally positive**. Daily ICs of 0.03 from price/volume in large caps are what professional stat-arb competes for at much lower cost.
  - At 21 days, cross-sectional sd is about 8%. IC 0.02 gives about 45 bp per month gross. Turnover of 30-50% a month costs about 3-5 bp a month, so costs are negligible.
- *TC.* A long-only retail book holding 10-30 names has TC of perhaps 0.3-0.5. Multiply the gross IR by that.

**Realistic net ceiling.** A monthly-horizon ranking with IC 0.02 gives IR of about 0.6 x 0.4 to 0.5, i.e. **about 0.25-0.30**. At 4-5% tracking error, that is **about +1-1.5%/yr over the market**. IC 0.01 gives about 0.12-0.15, which is indistinguishable from zero over 10 years: the t-stat after 10 years is IR x sqrt(10), about 0.4-0.5. The market's own Sharpe is about 0.4-0.5 long run. Combining it with an independent active IR of 0.3 lifts the total Sharpe only to sqrt(0.45² + 0.3²), about 0.54.

**Detecting it.** Detecting an IR of 0.3 at 2 sigma takes (2/0.3)², about **44 years**. Even a real edge at this ceiling cannot be confirmed from 2016-2026 data alone. Any backtest showing IR above 1 at the monthly horizon from price data in large caps should be presumed to contain an error.

Note: the project's measured edge (momentum right on 53% of days, average about zero) implies a realized IC at or below about 0.01. That sits at the bottom row of this table.

---

## Q5. Three most likely self-deceptions from here

1. **Counting only the survivor tests (multiple testing / garden of forking paths).** The repo already holds 15+ studies (overnight, pairs, odd-lot, liquidation, lead-lag, PM drift, and others) plus 12-megacap tests of 8 data families. The next "pass" will be the best of about 30+ tries. Guard:
   - Keep a ledger of every variant tried.
   - Use a deflated Sharpe ratio or Bonferroni/Holm across the ledger.
   - Pre-register the test before looking.
   - Reserve a holdout the model never touches.
   - Overlapping 5- and 21-day returns inflate t-stats by about sqrt(h). Use Newey-West or non-overlapping samples.
2. **Universe and timing look-ahead.** Using *today's* S&P 500 list back to 2016 is survivorship bias. It flatters momentum and anything long, because the names that rose got added and the ones that fell got deleted. Also check:
   - Signals computed on the close and traded at the same close.
   - Adjusted prices that embed future splits and dividends incorrectly.
   - Earnings dates known only afterwards.

   Guard: point-in-time membership, and trade at the next open or the next close.
3. **Mistaking factor or regime exposure for skill.** 2016-2026 was dominated by megacap tech and growth. A ranking that is quietly long beta, long tech, or long low-volatility will "work" for reasons that can flip at a turning point, which is exactly the momentum-crash mechanism. Guard:
   - Report IC and returns after neutralising market beta, sector, and size.
   - Report by regime: bull, bear, rebound, and the 2022 drawdown.
   - Compare against the trivial baseline of buying SPY plus sector momentum.

   A close fourth: **cost optimism at short horizons**. A 1-day signal with IC below 0.02 cannot survive real spreads; see Q4.

---

## Sources (this session)
- Daniel and Moskowitz, Momentum Crashes, NBER w20439 / JFE 2016: https://www.nber.org/papers/w20439
- Bianchi et al., Taming momentum crashes (SSRN 2022): https://strathprints.strath.ac.uk/90217/1/Bianchi-etal-SSRN-2022-Taming-momentum-crashes.pdf
- Alpha Architect summaries: https://alphaarchitect.com/risk-of-momentum-crashes/ ; https://alphaarchitect.com/avoiding-momentum-crashes/
- Goulding, Harvey and Mazzoleni, Momentum Turning Points, JFE 2023: https://econpapers.repec.org/RePEc:eee:jfinec:v:149:y:2023:i:3:p:378-406
- Greenwood and Sammon, The Disappearing Index Effect: https://www.nber.org/system/files/working_papers/w30748/w30748.pdf ; https://ideas.repec.org/a/bla/jfinan/v80y2025i2p657-698.html
- Harvey, Mazzoleni and Melone, The Unintended Consequences of Rebalancing, NBER w33554: https://www.nber.org/papers/w33554
- Etula, Rinne, Suominen and Vaittinen, Dash for Cash, RFS 2020: https://academic.oup.com/rfs/article/33/1/75/5494694
- Brown, Davies and Ringgenberg, ETF Arbitrage, Non-Fundamental Demand, and Return Predictability, RoF 2021: https://ideas.repec.org/a/oup/revfin/v25y2021i4p937-972..html
- Baltussen, Da, Lammers and Martens, Hedging Demand and Market Intraday Momentum, JFE 2021: https://www3.nd.edu/~zda/intramom.pdf
- Leveraged ETF rebalancing: Fed FEDS 2013-48 https://www.federalreserve.gov/pubs/feds/2013/201348/ ; Ivanov and Lenkey https://pure.psu.edu/en/publications/do-leveraged-etfs-really-amplify-late-day-returns-and-volatility/ ; CXO summary https://www.cxoadvisory.com/volatility-effects/front-running-leveraged-etfs-at-the-end-of-the-day ; arXiv 2604.27287
- Buyback blackouts: https://alphaarchitect.com/buyback-blackout-periods-do-not-negatively-impact-market-performance/
- Earnings-announcement premium: https://www.iimb.ac.in/ARC2020/Papers/The_Disappearing_Earnings_Announcement_Premium.pdf ; https://aeaweb.org/conference/2024/program/paper/5GGEki7i ; Frazzini and Lamont https://www.nber.org/papers/w13090
- Lazy Prices: https://www.nber.org/papers/w25084
- McLean and Pontiff: https://Www.Gwern.net/doc/economics/2016-mclean.pdf ; post-publication alphas https://finance-conference.wpcarey.asu.edu/sites/default/files/2025-02/Out-of-Sample_Alphas_%282025-02-12%29_with_link.pdf
- From memory, to verify: Barroso and Santa-Clara (JFE 2015); Lou and Polk Comomentum (RFS 2022); Grundy and Martin (2001); Ni, Pearson and Poteshman (JFE 2005); Cohen and Frazzini (JF 2008); Cohen and Lou (JFE 2012); Field and Hanka (JF 2001); Ali and Hirshleifer (JFE 2020).
