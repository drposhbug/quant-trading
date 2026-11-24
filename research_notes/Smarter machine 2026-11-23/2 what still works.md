# 2. What still works (Empiricist view)

Started 2026-11-23. Question: which cross-sectional predictors of relative returns still work in US large caps (S&P 500) after ~2015, how big, at which horizon, with which data.

Method: web search and page fetches only; papers, abstracts and replication data (Ken French library) preferred over blogs. Numbers marked [KF calc] are my own arithmetic on Ken French's public portfolio files (no repository code was run). Everything else carries its source link.

## A. The replication literature: the base rates

| Source | Finding relevant to large caps |
|---|---|
| McLean and Pontiff (2016, JF) | Anomaly returns are ~26% lower out of sample and ~58% lower after publication (the oft-quoted "about half"). Chen and Zimmermann replicate the ~50% post-publication drop. [Fed FEDS 2018-033](https://www.federalreserve.gov/econres/feds/files/2018033pap.pdf) |
| Hou, Xue and Zhang (2020, RFS) | With NYSE breakpoints and value weights (i.e. microcaps tamed), 65% of 452 anomalies fail t>1.96; 82% fail t>2.78. 96% of the "trading frictions" category fails. Replicated effects are much smaller than originally reported. [IDEAS](https://ideas.repec.org/a/oup/rfinst/v33y2020i5p2019-2133..html), [NBER w23394](https://nber.org/papers/w23394) |
| Jensen, Kelly and Pedersen (2023, JF) | Most of 153 factors replicate (Bayesian, alphas, capped value weights); the gap to HXZ's 35% is mostly construction choices (capped VW alone +8.5pp). They test alphas, not raw returns, and their mega-cap subsample is weaker than the all-stock one. [NBER w28432](https://nber.org/system/files/working_papers/w28432/w28432.pdf), data: jkpfactors.com |
| Chen and Zimmermann, Open Source Asset Pricing | Reproduces ~200 predictors; post-sample decay ~50%; Chen, Lopez-Lira and Zimmermann (2022+) find decay of ~50% post-sample and that risk-based theory does not prevent decay; returns fall most in first 5 years out-of-sample. [Fed page](https://www.federalreserve.gov/econres/feds/open-source-cross-sectional-asset-pricing.htm), [arXiv 2212.10317](https://arxiv.org/html/2212.10317v6) |
| Chen and Velikov (2023, JFQA) | 204 anomalies: after costs, post-publication decay and data-mining adjustment, the average anomaly nets about 4 bps/month (8 bps in the 2020 WP); the best net 10-20 bps; top-quartile post-2005 net ~21 bps/month (WP). [Fed FEDS 2020-039](https://www.federalreserve.gov/econres/feds/files/2020039pap.pdf), [JFQA](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/zeroing-in-on-the-expected-returns-of-anomalies/945133D5A3ECEEAF466AEE91551FD225) |
| Novy-Marx and Velikov (2016, RFS) | Anomalies with one-sided monthly turnover below ~50% mostly keep significant net spreads when built to limit costs (buy/hold spreads are the best simple fix); few higher-turnover anomalies survive. Size, value, momentum survive costs; reversal-type signals do not. [NBER w20721](https://www.nber.org/papers/w20721) |

Base rate for this project: take any published in-sample long-short number, halve it for publication, halve again for large caps / value weighting, then subtract costs. Most land at 0 to 20 bps/month.

## B. How much predictability exists at all (Q3)

- Gu, Kelly and Xiu (2020, RFS), test period 1987-2016, ~30,000 stocks, 94 characteristics. Monthly stock-level out-of-sample R2 (vs zero forecast), Table 1:
  - All stocks: OLS-3 0.16%, ENet 0.11%, RF 0.33%, GBRT 0.34%, NN3 0.40%.
  - Top 1000 by market cap: OLS-3 0.31%, RF 0.63%, GBRT 0.52%, NN3 0.70%.
  - Bottom 1000: NN3 0.45%.
  - Annual-horizon R2 is "nearly an order of magnitude larger". NN3 long-short decile Sharpe 1.35 value-weighted, 2.45 equal-weighted. Dominant features: price trends (mom1m short-term reversal, mom12m, chmom, indmom), then liquidity, then volatility. Footnote: R2 vs historical mean is ~3 points inflated, so always benchmark to zero. [NBER w25398](https://www.nber.org/papers/w25398.pdf)
  - Read: monthly R2 of 0.5-0.7% in big stocks corresponds to a monthly cross-sectional IC of roughly 0.05-0.08 at best, in-sample period ending 2016, before costs; much of the large-cap value came from short-term reversal (mom1m), which is expensive to trade.
- Avramov, Cheng and Metzker (2023, Management Science): deep-learning signal profits come mainly from hard-to-arbitrage stocks and high limits-to-arbitrage states; payoff falls ~62% excluding microcaps, ~68% excluding non-rated firms, ~80% excluding distressed firms around downgrades (figures as reported by CUHK summary; I did not see the table); costs reduce it further because of high turnover. [SSRN 3450322](https://papers.ssrn.com/abstract=3450322), [CUHK summary](https://cbk.bschool.cuhk.edu.hk/the-limitations-of-using-ai-to-pick-stocks/)
- These two papers disagree on emphasis: GKX say large-cap R2 is higher than small-cap; ACM say the dollar profits sit in small/distressed names. Both can be true: R2 per stock vs extreme-decile payoff.
- No ML paper I found shows S&P 500-only daily-horizon out-of-sample results after 2016 that would beat the GKX monthly numbers. Thin.

## C. Momentum, measured directly on post-2015 data (Q4) [KF calc]

Source data: Ken French, 6 portfolios formed on size and prior (t-12 to t-2) return, value-weighted, CRSP through 2026-09. "Big" = above NYSE median, so this is close to large-cap momentum. WML = Big HiPRIOR minus Big LoPRIOR (30/70 NYSE breakpoints). Files: [monthly](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_ME_Prior_12_2_CSV.zip), [daily](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_ME_Prior_12_2_Daily_CSV.zip).

Monthly-rebalanced big-cap WML (monthly file):

| Period | mean %/mo | sd | ann. Sharpe | t | % months >0 | skew | median |
|---|---|---|---|---|---|---|---|
| 1927-2015 | 0.57 | 5.21 | 0.38 | 3.6 | 60% | -2.48 | 0.75 |
| 1990-2015 | 0.44 | 5.25 | 0.29 | 1.5 | 59% | -0.97 | 0.64 |
| 2000-2015 | 0.24 | 5.81 | 0.14 | 0.6 | 59% | -1.11 | 0.46 |
| 2016-2026/09 | -0.13 | 5.11 | -0.09 | -0.3 | 51% | -0.33 | 0.15 |
| 2019-2026/09 | -0.10 | 5.60 | -0.06 | -0.2 | 53% | -0.36 | 0.41 |
| Small caps 2016-2026/09 (contrast) | 0.37 | 3.66 | 0.35 | 1.2 | 57% | -0.87 | 0.64 |

Daily big-cap WML (daily file, portfolios re-formed daily on t-250..t-21 return):

| Period | mean %/day | % days >0 | skew |
|---|---|---|---|
| 1990-2015 | 0.021 | 54.1% | -0.98 |
| 2016-2026/09 | -0.002 | 51.8% | -0.89 |
| 2019-2026/09 | 0.001 | 51.9% | -0.89 |

This is the project's own finding, reproduced on independent data: in big caps since 2016 momentum is right a bit more often than not (52-53% of days), median positive, mean about zero, negative skew. It is the known shape of momentum, and the post-2015 big-cap mean is not distinguishable from zero.

Fixes, tested on the same data (monthly returns from compounding the daily WML; no costs):

| Period | raw Sharpe | vol-scaled Sharpe (Barroso-Santa-Clara, 126-day realized vol, 12% target) | DM bear months (24-mo market return <0): raw mean in bear / non-bear |
|---|---|---|---|
| 1927-2015 | 0.39 | 0.65 (skew -0.17 -> +0.10) | -0.47 / +0.76 %/mo (183 bear months) |
| 1990-2015 | 0.30 | 0.57 | -0.65 / +0.69 (54) |
| 2016-2026/09 | -0.06 | 0.12 (skew -0.03 -> +0.50) | -3.95 / +0.16 (8 bear months: 2020-04, 2023-01, 2023-05..12) |
| 2019-2026/09 | -0.02 | 0.16 | -3.95 / +0.34 (same 8) |

Read: both fixes still point the right way after 2015 (vol scaling roughly halves volatility and turns skew positive; the bear filter would have dodged the April 2020 and January 2023 rebounds, -11% and -16% months), but the improvement is from ~0 to ~0.1-0.3 Sharpe over 10.75 years, t well below 1. Bear state was on only 8 of 129 months, so the DM evidence post-2015 rests on 2 events. Barroso and Detzel (2021, JFE) find that after costs, volatility management of non-market factors generally yields zero abnormal return [IDEAS](https://ideas.repec.org/a/eee/jfinec/v140y2021i3p744-767.html); DeMiguel et al. (2024, JF) argue a conditional multifactor version survives costs [LBS](https://lbsresearch.london.edu/id/eprint/3716).

Published claims: Daniel and Moskowitz (2016, JFE): momentum crashes happen in "panic states" after market declines, when volatility is high and the market rebounds; losers behave like short calls on the market; a dynamic strategy based on forecast mean and variance roughly doubles the static Sharpe. [NBER w20439](https://www.nber.org/papers/w20439). Barroso and Santa-Clara (2015, JFE): momentum risk is predictable from its own 6-month realized variance; scaling to constant vol raises Sharpe from ~0.53 to ~0.97 (1927-2011) and nearly removes crashes.

Note on my vol-scaled test: built on Ken French's daily file, whose portfolios are re-formed every day, so it is a daily-rebalanced WML compounded to months, not the exact monthly-formed WML of Barroso and Santa-Clara. The 0.53 -> 0.97 Sharpe figures for BSC are from my memory of the paper; the abstract only says scaling "virtually eliminates crashes and nearly doubles the Sharpe ratio" [econpapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:116:y:2015:i:1:p:111-120).

## D. Other price-based signals, post-2015, big caps

### Short-term (1-month) reversal [KF calc]
Ken French 6 portfolios on size and prior (t-1) return, value-weighted, Big LoPRIOR minus Big HiPRIOR ([file](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/6_Portfolios_ME_Prior_1_0_CSV.zip)):

| Period | Big mean %/mo | t | Small mean %/mo |
|---|---|---|---|
| 1927-2015 | +0.31 | 2.5 | +1.13 |
| 1990-2015 | +0.14 | 0.6 | +0.26 |
| 2016-2026/09 | -0.13 | -0.35 | +0.04 |
| 2019-2026/09 | -0.37 | -0.75 | -0.03 |

Raw 1-month reversal is dead in big caps, before costs. What the literature says survives:
- Medhat and Schmeling (2022, RFS), 1963-2018: split last month's return by share turnover: low-turnover stocks reverse, high-turnover stocks continue ("short-term momentum"), and short-term momentum is "strongest among the largest, most liquid, and most extensively covered stocks" and survives costs. [IDEAS](https://ideas.repec.org/p/cpr/ceprdp/15857.html). Data: OHLCV only. Sample ends 2018; no post-2018 check found.
- Residual / industry-relative reversal (Blitz, Huij, Lansdorp, Verbeek 2013 JFM; de Groot, Huij, Zhou 2012): reversal on factor-residual or within-industry returns stays profitable net of costs in large caps, ~30-50 bps/week net in the 2012 paper (old samples). Dai, Medhat, Novy-Marx and Rizova (2023): standard reversal = news-related effects + announcement-adjusted industry-relative reversal; the latter is the cleaner piece. [Alpha Architect summary](https://alphaarchitect.com/alpha-from-short-term-signals/), [Novy-Marx](https://mysimon.rochester.edu/novy-marx/research/RRLP.pdf). Data: OHLCV + industry codes + earnings dates. Post-2015 large-cap evidence: thin (Blitz et al. 2022 MSCI World large caps to 2021 reports significant reversal alphas, figures not verified).
- Overnight vs intraday (Lou, Polk, Skouras 2019 JFE): momentum profits are earned entirely overnight, reversal entirely intraday; continuation within each component and cross-period reversal persist for years. Costs make exploitation much less attractive. [LSE](https://researchonline.lse.ac.uk/id/eprint/87481). Data: open and close (already held). The project already includes overnight/intraday splits among its 345 patterns, and they did not stand out.

### Momentum variants
- Residual momentum (Blitz, Huij, Martens 2011): ~2x the risk-adjusted return of total-return momentum, 1926-2009; residual momentum improves Sharpe but does not remove crash risk. No clean post-2015 large-cap test found. Thin.
- 52-week high (George and Hwang 2004): nearness to the 52-week high subsumes much of momentum and does not reverse; later work calls it robust to size; no post-2015 US large-cap test found. Thin.
- Industry momentum: Ali and Hirshleifer (2020) show industry, customer/supplier, geographic and technology momentum are all insignificant once shared-analyst-coverage (CS) momentum is controlled (CS alpha 1.68%/mo, t = 9.67, all stocks, sample ends ~2016). [IDEAS](https://ideas.repec.org/a/eee/jfinec/v136y2020i3p649-675.html). Large-cap-only and post-2016 numbers not verified. Needs I/B/E/S coverage data (paid).
- The project's beta-adjusted momentum is already close to residual momentum, and it showed the same weak pattern.

## E. Fundamental and event signals

### Value, profitability, investment, low beta in big caps [KF calc]
Ken French 2x3 sorts, Big half only, value-weighted, monthly; low beta is big-size quintile, beta quintile 1 minus 5, raw (not beta-neutral).

| Spread | 1964-2015 | 1990-2015 | 2016-2026/09 | 2019-2026/09 |
|---|---|---|---|---|
| Value HiBM-LoBM | +0.23 (t 1.8) | +0.03 | 0.00 | +0.10 |
| Profitability HiOP-LoOP | +0.20 (t 2.0) | +0.32 (t 2.0) | +0.28 (t 1.0) | +0.23 (t 0.7) |
| Investment Lo-Hi | +0.20 (t 1.9) | +0.08 | -0.06 | -0.05 |
| Low beta - High beta (raw) | +0.10 | -0.26 | -1.67 (t -2.1) | -2.15 (t -2.0) |

Read: profitability is the only one of these with a positive (not significant) post-2015 big-cap spread. Value and investment are zero. Raw low-beta has been a large loser in large caps (high-beta megacaps led); the beta-neutral BAB form is different but the project ranks raw relative returns, so this is the relevant sign. These are slow signals (annual accounting updates), horizon 21 days and beyond; a daily 1-5 day ranker gains almost nothing from them except as a tilt. Data: free SEC XBRL financial statements.

### Post-earnings-announcement drift (PEAD) and the earnings-announcement premium
- Martineau (2022, Critical Finance Review): in large stocks PEAD "has been non-existent since 2006"; it disappeared later in microcaps; prices now fully absorb the surprise on the announcement day. [IDEAS](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html)
- Contested: Dickerson, Julliard and Mueller ("co-pricing factor zoo", JFE forthcoming) find earnings drift remains a major factor; Subrahmanyam (2025) reruns 2001-2024 and the drift survives mostly with microcaps in. [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again). For S&P 500 the weight of evidence says dead or near zero.
- Earnings-announcement premium (stocks earn more in announcement windows; Savor-Wilson 2016 ~9.9% annualized abnormal): concentrated in small stocks historically; a paper argues it has moved from announcement periods to 8-K filing periods ("The Disappearing Earnings Announcement Premium"). [IIMB](https://www.iimb.ac.in/ARC2020/Papers/The_Disappearing_Earnings_Announcement_Premium.pdf). Large-cap post-2015 size: thin, probably a few bps per announcement window. Data: earnings calendar (cheap).

### Analyst revisions and recommendation changes
Classic results (Chan, Jegadeesh, Lakonishok 1996 revisions; Womack 1996 recommendation changes) are among the more robust in the replication sets, but I found no study isolating post-2015 S&P 500 performance. Fed-staff evidence: predicted forecast errors explain ~8% of 3-month return variation out of sample from 1994. [Fed FEDS 2024-049](https://federalreserve.gov/econres/feds/files/2024049pap.pdf). 2025 LLM work finds analyst report text predicts 12-month returns beyond revisions. [arXiv 2502.20489](https://arxiv.org/html/2502.20489v1). Evidence for post-2015 large caps: mixed/thin. Data: I/B/E/S or similar (paid; free substitutes are poor).

### Short interest and daily short-sale volume
Shorting flows predicted negative returns in 2010-2015 when FINRA daily short volume was public, linked to short sellers trading known anomalies [Lehigh WP](https://www.lehigh.edu/~xuy219/research/Short_Final_Version.pdf). FINRA warns the daily file omits offsetting buys and is dominated by market-maker short sales [FINRA](https://www.finra.org/finra-data/browse-catalog/reg-sho-daily). Short-interest predictability historically sits in hard-to-borrow, small stocks; S&P 500 names are almost all general-collateral. Already tested on 12 megacaps (nothing). Evidence for large caps post-2015: weak.

### Options-implied measures
Muravyev, Pearson and Pollet (2025, JFE): options-based predictors (IV spread, skew, option/stock volume) predict returns because implied volatilities embed stock borrow fees; predictability from IV spread and skew falls by at least two-thirds when high-fee stocks are excluded. [IDEAS](https://ideas.repec.org/a/eee/jfinec/v172y2025ics0304405x25001618.html), [replication data](https://data.mendeley.com/datasets/n73cyx89gs). S&P 500 stocks are rarely high-fee, so the residual large-cap effect is small. Data: OptionMetrics-type IV surfaces (expensive). Evidence: weak for large caps.

### Insider trading
Cohen, Malloy and Pomorski (2012, JF): opportunistic insider trades earn ~82 bps/month value-weighted abnormal (sample to ~2007); routine trades carry nothing. [NBER digest](https://www.nber.org/digest/apr11/decoding-inside-information). Large-cap, post-2015: not found; opportunistic purchases in S&P 500 firms are rare, so breadth is tiny. Data: SEC Form 4 (free). Already tested on 12 megacaps (nothing). Weak for this setting.

### News sentiment
Ke, Kelly and Xiu (SESTM; Dow Jones Newswires, out-of-sample Feb 2004 - Apr 2020; text from the SSRN 3389884 version): daily long-short on news sentiment, open-to-open: equal-weighted Sharpe 4.21 (32 bps/day), value-weighted Sharpe 1.24 (9 bps/day, turnover ~91%/day). Large stocks: price response 11 bps on day 1 and complete after one day; small stocks 46 bps over three days. With 10 bps (large) / 20 bps (small) costs and a slow-turnover scheme, best net Sharpe ~1.05 (equal-weighted; driven by small stocks). [NSF PAR copy](https://par.nsf.gov/servlets/purl/10289824), [NBER w26186](https://www.nber.org/papers/w26186)
Lopez-Lira and Tang (LLM headline scoring, latest version Oct 2025): drift prediction is "especially for small stocks and negative news", and "strategy returns decline as LLM adoption rises". [arXiv 2304.07619](https://arxiv.org/abs/2304.07619)
Read: in large caps, news is absorbed in about a day; a close-to-close ranker that learns of news after the close can only catch the overnight/next-day part. Gross value-weighted edge ~9 bps/day at ~90% daily turnover is roughly break-even after realistic costs. Evidence: strong that it existed, mixed that a retail-cost large-cap version survives now. Data: timestamped news feed (paid) or headlines plus an LLM.

### Shared-analyst-coverage and supply-chain lead-lag
Ali and Hirshleifer (2020): CS momentum subsumes customer/supplier (Cohen-Frazzini 2008), industry and technology spillovers. Monthly horizon. Post-2016 large-cap: not verified. The project's own lead-lag tests on 12 megacaps found nothing. Mixed.

### ETF and index flows
Ben-David, Franzoni and Moussawi (2018, JF): higher ETF ownership raises daily volatility (+16% per s.d.); prices revert after large ETF flows within days; high-ETF-ownership stocks earn up to 56 bps/month premium. [NBER w20071](https://www.nber.org/papers/w20071). This is a noise/reversal effect lasting days; usable signal for S&P 500 ranking not established. Weak.

## F. Ranked table (large caps, post-2015)

Conversions are rough: for S&P 500 names a monthly top-minus-bottom-tercile spread of s %/month corresponds to a monthly rank IC of about s/15 (cross-sectional s.d. ~7%/month); treat ICs below as order-of-magnitude.

| Rank | Predictor | Horizon | Expected size in large caps after 2015 (gross unless noted) | Evidence | Data needed | Source |
|---|---|---|---|---|---|---|
| 1 | Profitability / quality (gross or operating profitability) | 21d+ (monthly-annual) | +0.2 to +0.3 %/mo big-cap spread, t~1 (IC ~0.01-0.02); turnover low so costs small | mixed (strong long-run, insignificant post-2015) | SEC XBRL fundamentals (free) | KF calc; [Novy-Marx & Velikov](https://www.nber.org/papers/w20721) |
| 2 | Momentum with crash control (vol-scaled 12-1, bear-state off) | 21d | raw ~0 (-0.1 %/mo); vol-scaled Sharpe ~0.1-0.3, t<1 (IC ~0.00-0.01) | mixed (strong pre-2015, near zero after in big caps) | OHLCV (held) + market index | KF calc; [Daniel-Moskowitz](https://www.nber.org/papers/w20439); [Barroso-Detzel](https://ideas.repec.org/a/eee/jfinec/v140y2021i3p744-767.html) |
| 3 | Turnover-conditioned 1-month return (short-term momentum in high-turnover, reversal in low-turnover); industry-relative, announcement-adjusted reversal | 5-21d | unknown post-2018; pre-2018 comparable to momentum; raw reversal is -0.1 to -0.4 %/mo post-2016 | mixed (published 2022-23, no post-sample check) | OHLCV (held) + industry + earnings dates | [Medhat-Schmeling](https://ideas.repec.org/p/cpr/ceprdp/15857.html); [Dai et al.](https://mysimon.rochester.edu/novy-marx/research/RRLP.pdf); KF calc |
| 4 | News / LLM sentiment of overnight news | 1d | VW ~9 bps/day gross 2004-2020, large stocks absorb in 1 day; ~0 after costs at 90% turnover; declining with LLM adoption | mixed | timestamped news + LLM scoring (paid feed) | [Ke-Kelly-Xiu](https://par.nsf.gov/servlets/purl/10289824); [Lopez-Lira-Tang](https://arxiv.org/abs/2304.07619) |
| 5 | Analyst revisions / recommendation changes; shared-analyst-coverage momentum | 5-63d | not established post-2015 for large caps; CS momentum 1.68%/mo all-stock alpha pre-2016 | mixed / thin | I/B/E/S (paid) | [Ali-Hirshleifer](https://ideas.repec.org/a/eee/jfinec/v136y2020i3p649-675.html) |
| 6 | Earnings-announcement premium (scheduled announcers) | 1-5d around date | small, a few bps per window; drifting to 8-K dates | weak | earnings calendar (cheap) | [IIMB WP](https://www.iimb.ac.in/ARC2020/Papers/The_Disappearing_Earnings_Announcement_Premium.pdf) |
| 7 | Residual momentum, 52-week high | 21d | no post-2015 big-cap test found; likely similar to plain momentum | weak (thin) | OHLCV (held) | [George-Hwang](https://www.bauer.uh.edu/tgeorge/papers/gh5-paper.pdf) |
| 8 | PEAD (SUE drift) | 21-63d | ~0 in large caps since ~2006 | dead (contested) | earnings + estimates | [Martineau](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html) |
| 9 | Options IV spread / skew / O/S volume / put-call | 1-21d | at least two-thirds of effect is borrow fees; large caps rarely high-fee | weak | option IV surfaces (expensive) | [Muravyev-Pearson-Pollet](https://ideas.repec.org/a/eee/jfinec/v172y2025ics0304405x25001618.html) |
| 10 | Short interest / daily short volume | 5-21d | small in large caps; daily FINRA file is market-maker noise | weak | FINRA files (free), borrow data (paid) | [FINRA](https://www.finra.org/finra-data/browse-catalog/reg-sho-daily) |
| 11 | Insider (opportunistic) trades | 21d+ | 82 bps/mo pre-2008 all-stock; breadth tiny in S&P 500 | weak | SEC Form 4 (free) | [CMP](https://www.nber.org/digest/apr11/decoding-inside-information) |
| 12 | ETF/index flow pressure | 1-5d | short-lived reversal, size unestablished | weak | ETF flows/holdings (paid) | [BFM](https://www.nber.org/papers/w20071) |
| 13 | Raw 1-month reversal | 21d | -0.13 %/mo 2016-26 big caps | dead | OHLCV | KF calc |
| 14 | Value (B/M), investment, raw low beta | 21d+ | 0.0, -0.06, -1.7 %/mo | dead (in this window) | fundamentals | KF calc |

## G. Answers

Q3 (how much predictability exists). GKX monthly R2 is 0.4% all stocks, 0.5-0.7% in the top 1000, in a test period ending 2016, before costs, with short-term reversal and momentum the main inputs, and both of those have since gone to about zero in big caps (sections C and D). Avramov et al. show most ML portfolio profit comes from microcaps/distressed/non-rated stocks. Chen-Velikov put the average anomaly at ~4 bps/month net. JKP find replication rates in mega and large stocks of 77% and 82% (EB, alphas, to 2019) and an in-sample to out-of-sample alpha decline of about one third (0.45 -> 0.31 %/mo average), with an out-of-sample/in-sample slope of 0.25-0.43. Realistic monthly IC for any single signal in S&P 500 after 2015: 0.00-0.03. I found no credible published daily-horizon, large-cap-only, post-2016 out-of-sample R2. Thin.

Q4 (many small wins, few large losses). Yes, this is the documented shape of momentum: Daniel and Moskowitz find negatively skewed returns with crashes in rebounds after bear markets ("panic states"), when losers behave like short calls on the market. Barroso and Santa-Clara find momentum's risk is predictable from its own recent volatility; scaling nearly doubles Sharpe and nearly removes crashes. On Ken French big-cap data, 2016-2026/09, momentum is positive on 52% of days with a median above zero, mean about zero and daily skew -0.9; the bear filter would have stepped aside for April 2020 (-11%) and January 2023 (-16%), and vol scaling lifts Sharpe from -0.06 to +0.12 and turns skew positive. Both fixes still point the right way, but the post-2015 gain is small and not significant (2 crash episodes; t < 1), and Barroso-Detzel find vol-managed non-market factors earn no alpha after costs.
