# 5. News shocks and Trump: what is a pattern (event analyst)

Date: 2026-11-23. Researcher 5 of 5 (STORM). Scope: news and volatility, news and direction,
Trump and the whole market, free daily shock data, what a once-a-day trader can do.

Marking: [checked] = read in the source this session; [abstract] = from the abstract or an
official summary; [memory] = well-known published number that I did not re-open this session,
so check it before relying on it.

## Short answer

The owner's belief splits cleanly in two.

- **Size of moves (volatility) after news: real, strong, and forecastable.** But almost all of it
  is already in the stock's own recent volatility. Knowing that news arrived adds a little,
  mostly on high-volatility days. Tesla is not a special case: it is a high-volatility,
  high-attention stock, and a volatility model that knows that already "knows" Tesla reacts violently.
- **Direction after news: weak for large caps after 2010, and fragile after costs.** The classic
  pattern (moves with real news drift, moves without news reverse) is real in the papers, but it
  is concentrated in small, illiquid stocks and in old samples, and it is measured in basis points per day.
- **Trump and the market: three claims, three verdicts.** (1) His trade statements raise
  volatility: yes, well documented. (2) They move the market in a predictable direction: only
  after the fact. Escalations go down and retreats go up, but you cannot know in advance which kind
  of post comes next, and the in-house test of 13,731 posts found nothing tradable. (3) "Overreact
  then reverse" (TACO): true in 2025-2026 escalations that were later walked back (April 2025,
  May 2025, January 2026), false for the 2018-2019 trade war (11 announcement days, no bounce
  the following week). The sample is fewer than ten episodes and depends on his choices. It is
  a story, not a pattern you can test.

## 1. News and volatility

### Volatility clustering and the leverage effect (real, strongest pattern in finance)
- Volatility is persistent: today's realized variance forecasts tomorrow's, next week's and next
  month's. The HAR model (Corsi 2009, J. Financial Econometrics), which uses only daily, weekly and
  monthly realized variance, is the standard benchmark and hard to beat out of sample. [memory]
- Leverage or asymmetry: a fall raises future volatility more than a rise of the same size (Black
  1976; Engle and Ng 1993 "news impact curve"; Patton and Sheppard 2015, REStat, "Good
  volatility, bad volatility": negative semivariance predicts future volatility much better than
  positive semivariance). [memory]
- With daily data only (no intraday), use squared or absolute daily returns, or the high-low range
  (Parkinson or Garman-Klass) as a realized-variance proxy. Range estimators are about 5 times as
  efficient as squared close-to-close returns. [memory]

### Scheduled news (real and stable at the stock level)
- **Earnings days**: the size of a stock's earnings-day move is persistent from quarter to quarter
  and is priced in options as a separate jump (Dubinsky, Johannes, Kaeck and Seeger 2019 RFS,
  "Option pricing of earnings announcement risks"). [memory] This is the best-supported form of
  "some stocks react more violently to news": it is stock-specific, it repeats, and the dates are
  known in advance.
- **Macro announcement days** (FOMC, CPI, jobs): higher volatility and historically higher average
  returns (Savor and Wilson 2013 JFQA: about 11 bp a day on announcement days against about 1 bp on
  other days, 1958-2009). [memory] The pre-FOMC drift (Lucca and Moench 2015 JF: about 49 bp in
  the 24 hours before FOMC, 1994-2011 [memory]) **largely disappeared after 2015** (Kurov,
  Wolfe and Gilbert 2021, Finance Research Letters; sample to 2019). [abstract]

### Does "news arrived" add anything beyond the move itself?
- Boudoukh, Feldman, Kogan and Richardson (NBER w18725 2013; RFS 2019), S&P 500, 2000-2009,
  1.9 million Dow Jones stories: volatility on **identified** news days is more than twice that
  on other days. Days with no news and days with unidentified news look the same. The
  market-model R-squared falls from about 30-33% on no-news days to 15.9% on identified-news days.
  [checked] So news days are days when stock-specific variance dominates. That is a statement
  about the day of the news, which you only know once the day has happened.
- For **forecasting** volatility, adding news is a small gain: the stock's own move already holds
  most of the information. Rahimikia and Poon (arXiv 2108.00480; 23 NASDAQ stocks 2007-2022):
  headline-based models beat HAR mainly on high-volatility days. Earlier sentiment-word additions
  improved forecasts "only marginally". [abstract] Halouskova and Lyocsa: attention and sentiment
  measures improve forecasts for almost all of 404 US stocks, but by small amounts. [abstract]
- Verdict: news counts add little to a HAR or GARCH forecast that already has the return. The
  exceptions are **scheduled** events (earnings, FOMC), where you know about the shock **before**
  it happens. That is the useful asymmetry for a once-a-day trader.

### Are some stocks persistently more news-sensitive (Tesla)?
- Barber and Odean 2008 RFS "All that glitters": individual investors are net buyers of
  attention-grabbing stocks (in the news, abnormal volume, extreme one-day returns). [memory]
- Barber, Huang, Odean and Schwarz 2022 JF (Robinhood, 2018-2020): the stocks Robinhood users buy
  most each day earn about **-4.7% average abnormal return over the next 20 days**. Extreme herding
  episodes reverse more (about 9% according to a UC Davis summary; check this in the paper).
  [abstract] This is the most relevant direction result for attention stocks: attention-driven
  surges tend to reverse. The size is large, but it is concentrated in herding events, which are
  rare in the top 500.
- Musk tweets and TSLA: the evidence is mixed and mostly from theses. The most careful study I
  found (Corvinus J. of Social Science & Policy; 3,158 tweets, 2,420 trading days) finds no
  significant effect on Tesla's price. A Louvain thesis finds only 2 of 14 major Musk events
  significant. [abstract] The one famous event ("funding secured", 2018-08-07) is a single episode.
- Verdict: TSLA's "news sensitivity" is high total volatility (implied volatility usually 2 to 3
  times the S&P 500's) plus retail attention. The useful test is whether a stock's move on news
  days, scaled by its own pre-event volatility, ranks stocks the same way year after year. If the
  scaled ranking is not stable, "news-sensitive" means only "volatile", and the project's
  volatility estimate already covers it.

## 2. News and direction

| Study | Sample | Finding | Size |
|---|---|---|---|
| Chan 2003 JFE | US stocks 1980-2000, monthly | Drift after bad news, reversal after extreme moves with no news | "mainly seen in smaller, more illiquid stocks" [abstract] |
| Tetlock 2007 JF | WSJ column, Dow, 1984-1999 | 1 s.d. of media pessimism, next day Dow -8.1 bp (t=3.94), 6.8 bp reversed over days 2-5 | Market level, fully reverses [checked] |
| Tetlock 2010 RFS, 2011 RFS | Dow Jones news | Public news reduces short-term reversal. Stale news brings overreaction and later reversal | [memory] |
| Savor 2012 JFE | 1995-2009, stocks with analyst coverage | Moves backed by an analyst report drift; moves without one reverse. Combined strategy 35% a year abnormal return (gross) | Drift only when the move and the recommendation change agree in sign [abstract] |
| Boudoukh et al. 2013/2019 | S&P 500 2000-2009 | Next-day autocorrelation -3.7% on no-news days, -2.9% on unidentified-news days, +0.7% on identified-news days. Sentiment adds ~5.6 bp. Long-short strategies: continuation 19.6 bp/day (Sharpe 1.7), reversal 15.6 bp/day (Sharpe 1.8), **gross**, daily turnover | Authors note daily trading costs would be large [checked] |
| Jiang, Li and Wang 2021 JFE | High-frequency data, news vs non-news returns | Underreaction to firm news is pervasive; strategy "remains profitable after transaction costs"; stronger when investors are distracted | [abstract] |
| Martineau 2022 CFR | PEAD | Post-earnings drift **non-existent in large caps since about 2006**. Disputed by two 2025 papers (e.g. Dickerson, Julliard and Mueller) | [abstract] |
| Barber et al. 2022 JF | Robinhood 2018-2020 | Attention-driven buying reverses: -4.7% over 20 days | [abstract] |

Reading for 1, 5 and 21 sessions in large caps after 2015:
- **1 session**: the no-news reversal is a few percent of the day's move (autocorrelation about
  -0.03), so a 5% no-news move predicts about 15-20 bp back. That is the same order as the cost of
  a round trip in one stock for a retail trader at the close, before any spread widening on volatile days.
- **5 sessions**: Tetlock-type sentiment effects fully reverse within a week at the market level.
  Stock-level drift after real news is a few tenths of a percent at most in S&P 500 names.
- **21 sessions**: the large-cap drift literature (PEAD, news momentum) mostly shows decay after
  the mid-2000s. Jiang, Li and Wang is the strongest recent counterexample but needs intraday data
  to separate news-driven from non-news returns.
- **Costs**: all the daily-rebalanced versions turn over close to 100% a day. At 5-10 bp a side
  for a retail account at the close, the 15-20 bp a day gross edges from 2000-2009 shrink to near
  zero. Weekly versions are cheaper but weaker.
- **Practical gap**: the project has no news flags yet. Without an article count per ticker per day
  it cannot split news days from no-news days. Alpaca/Benzinga can provide that (see section 4).

## 3. Trump and the whole market

### 2017-2020 (Twitter)
- **Trade-war announcement days** (Amiti, Kong, Gomez and Weinstein; NY Fed Liberty Street,
  December 2024): 11 announcement days, January 2018 to August 2019. Value-weighted US market down
  about **11.5% in total** (about $4.1 trillion). Largest days: 2018-03-22 -2.4%, 2018-03-23 -1.9%,
  2019-05-13 -2.5%, 2019-08-23 -2.5%. Two of the 11 days were positive. The effect "entirely
  occurs on the trading days corresponding to the announcements" and **did not bounce back the
  following week**. The authors read this as evidence against overreaction. [checked]
- **Fed-criticism tweets** (Bianchi, Gomez-Cram, Kind and Kung 2023, JME): tweets attacking the
  Fed lowered fed-funds futures, with a larger effect at longer horizons; a VAR links them to
  stocks and bond premia. [abstract] The move is in rates expectations, not a stock-direction rule.
- **JPMorgan "Volfefe" (September 2019)**: the share of tweets followed within 5 minutes by a
  significant move in Treasury yields; it explained a "measurable fraction" of 2- and 5-year
  implied rate volatility; trigger words "China", "billion", "products". [abstract, press] Intraday
  and about rates, not stocks.
- **Company-specific tweets** (Ge, Kurov and Wolfe 2019, J. Financial Research; November 2016 to
  2017): they move the named stock and raise volume and volatility, more before the inauguration,
  with "some evidence" of reversal in the next few days. [abstract] The sample is a few dozen
  tweets, and the effect is intraday.

### 2025-2026 (Truth Social)
- **2025-04-02 "Liberation Day"**: S&P 500 -11% over 2025-04-03 and 2025-04-04 (FRBSF Economic
  Letter 2025-23). [checked] 2025-04-09 pause: S&P 500 about +9.5%, its best day since 2008.
  VIX close about 52 on 2025-04-08. [memory] This is the one clear "overreact then reverse" case,
  and the reversal came from a policy change, not from market dynamics.
- **May 2025**: S&P +2.1% after the 50% EU tariff threat was withdrawn. The FT columnist Robert
  Armstrong named the pattern "TACO". [press]
- **2025-10-10**: 100% China tariff threat, S&P -2.71%, Nasdaq -3.56%, 83% of S&P members down;
  futures +1.5% the next session after softer comments; full recovery "within a month or so". [press]
- **2026-01-20 Greenland tariff threat on European allies**: S&P -2.1%, then +1.16% the next day
  after a "framework" was reported. [press]
- **2026-02-20 Supreme Court rules IEEPA does not authorize tariffs (6-3)**: S&P +0.7%. A muted
  reaction, because the ruling was expected. [press]
- An unattributed backtest quoted in the press ("short S&P futures on escalation, buy back 5 days
  later": +12% since February 2025) is one regime and one decision-maker, with no named source. Do not use it.
- **No peer-reviewed study of Truth Social posts and stock returns was found.** A JPMorgan count
  (Fortune, May 2025) says about 10% of 2025 posts moved markets, fewer than in the first term. [press]
- The in-house test (13,731 posts, 12 megacaps plus QQQ, nothing survives correction; tariff posts
  on a quarter of sessions) is consistent with the literature: the market reacts to **policy
  actions and surprises**, not to the count of posts.

### Three claims separated

| Claim | Evidence | Sample | Verdict |
|---|---|---|---|
| His statements raise volatility | Volfefe (rates); Ge-Kurov-Wolfe (single stocks); VIX 2025-04; EPU and TPU spikes | Hundreds of tweets intraday; a handful of daily episodes | **Real**, but intraday and mostly visible in EPU, TPU and VIX the same day |
| They move the market in a predictable direction | Escalation down, retreat up, after the fact. You cannot know in advance which post is coming. In-house test null | 11 days (2018-19), about 5-8 episodes (2025-26) | **Not supported** as a forecast |
| Overreaction then reversal | 2018-19: no reversal. 2025-26: reversals when he backed down | Fewer than 10 episodes, one decision-maker | **Weak / not testable**: it depends on his future choices and probably wears off once the market expects it |

### Which stocks are exposed, and is it stable enough to rank?
- **April 2025 was mostly a macro and risk shock, not a trade-exposure shock.** FRBSF: energy (-17%
  in two days), financials, industrials and materials had the most negative CAPM-abnormal returns.
  Information technology, consumer discretionary and telecom were *positive* relative to their
  betas. Within the "Magnificent 7" the abnormal returns ranged from significantly positive to
  significantly negative. [checked]
- At the firm level, 10-K text measures of tariff exposure (Han et al. 2026 Economics Letters),
  import and supplier exposure (Boston Fed WP 26-15) and trade exposure plus uncertainty
  sensitivity (IMF WP 2026/070) predict lower abnormal returns around 2025-04-02. [abstract] The
  2018 trade war gave similar results for China-exposed firms (Huang, Lin, Liu and Tang). [memory]
- **Stability**: a Bloomberg piece claims rankings of tariff "winners" and "losers" built on April 2
  carried into later tariff news (not readable here: 403). Evidence that the exposure ranking
  holds across episodes is thin. The only usable form is a rolling **beta to a daily trade-policy
  uncertainty series** (TPU or EPU), which can be estimated and checked out of sample.

## 4. Free daily shock series

| Series | Where | History | Publication delay | Point-in-time? |
|---|---|---|---|---|
| Baker-Bloom-Davis daily US EPU | FRED `USEPUINDXD`; policyuncertainty.com | 1985 [memory] | Daily; FRED updated 2026-11-23 for data to 2026-11-22, i.e. about 1 day | Newspaper counts are rescaled, so check ALFRED vintages before trusting history. Assume possible revisions and use t-1 |
| Caldara-Iacoviello TPU (daily) | matteoiacoviello.com/tpu.htm (also Minneapolis Fed page) | Daily since the 1980s [memory]; firm-level TPU from earnings calls | Daily file updated 2026-11-09 per the site, i.e. irregular, days to weeks | No vintages; treat as revised |
| Caldara-Iacoviello GPR (daily) | matteoiacoviello.com/gpr.htm | Daily from 1985 [memory] | Roughly weekly | Not vintaged |
| VIX, VIX9D, VIX3M, VVIX | Cboe historical CSVs; FRED `VIXCLS` | VIX 1990; VIX3M 2007 | Same day | Yes (market prices) |
| VIX futures settlements (term structure) | Cboe CFE historical data | 2004 | Same day | Yes |
| Alpaca news (Benzinga) | `/v1beta1/news`, filter by symbol and dates | 2015 onward [abstract]; about 600-900 headlines a day | Real time | Timestamped at publication, so close to point-in-time. Coverage is Benzinga's choice and grew over time. 200 calls/min on the free plan. Paper-account key needed. Terms: for your own use, no redistribution |
| GDELT 2.0 | gdeltproject.org, BigQuery | February 2015 onward (events back to 1979) [memory] | 15 minutes | Yes, but noisy and dominated by geopolitics |
| Wikipedia pageviews | Wikimedia REST API | July 2015 [memory] | Next day | Yes (counts are final); an attention proxy à la Barber-Odean |
| Truth Social posts | CNN-maintained JSON archive; trumpstruth.org; the project's own 13,731-post set | 2022 onward | Minutes | Yes if you keep your own timestamps. Edits and deletions are a risk |
| Trump tweets 2009-2021 | thetrumparchive.com | 2009-2021 | Closed | Yes |
| Single-stock implied volatility | No good free history. Option chains (snapshot only) can be saved daily from now on | Starts the day you start collecting | Same day | Only if you collect it yourself |
| Earnings dates | SEC EDGAR 8-K item 2.02 filing timestamps | 2001 onward | Minutes | Yes, the best free point-in-time earnings calendar |

## 5. What a slow trader can do with shocks

| Idea | Evidence | Realistic after 2015 | Main way it fails |
|---|---|---|---|
| Volatility-managed market exposure (Moreira and Muir 2017 JF) | Spanning-regression alphas positive and still positive in later data [memory/abstract] | Cederburg, O'Doherty, Wang and Yan 2020 JFE: across 103 strategies, real-time versions **do not systematically beat** unmanaged ones (unstable weights). For the market itself, the gain is a modest Sharpe improvement at best [abstract] | Cuts exposure after the crash and misses the V-shaped rebound (April 2025, March 2020). Leverage needed in calm periods |
| Scale momentum by its own volatility (Barroso and Santa-Clara 2015; Daniel and Moskowitz 2016) | Momentum Sharpe roughly 0.5 to 0.9-1.0 in the long US sample [memory]. Volatility scaling helps momentum more than other factors (Bianchi et al. 2022 "Taming momentum crashes") [abstract] | **The best-supported idea for this project.** It does not dodge a one-day shock (2020-11-09), but it lowers exposure when momentum's own volatility is already high, as it was in late 2020 and late 2022 | Scheduled shocks (CPI, vaccine results) hit in a single day. Add an "event-day" exposure cut for known dates (CPI, FOMC, jobs) as a separate test |
| Short-term reversal conditional on VIX or no-news (Nagel 2012 RFS) | Reversal returns are forecast by VIX: about 9 bp higher a week per VIX point in large stocks (replication cited by Drechsler et al.) [abstract] | Large-cap unconditional reversal is weak after costs. Conditional on high VIX and no news, it is plausible at 5 sessions | Reversal is liquidity provision: it loses in the first days of a crash, and the cost of trading rises exactly when it pays |
| Buy the market after policy-driven selloffs | 2025-04, 2025-10, 2026-01 rebounded. 2018-19 announcement days did not | Fewer than 10 episodes, one president | One decision-maker, so the pattern can end at any time. Survivorship: we remember the reversals |
| Avoid momentum before known macro dates | Momentum's worst days here are CPI and vaccine days | Unknown, a project-specific test | Most of the big losses are unscheduled |

## Suggested tests on about 500 stocks with free data

1. **Shock-conditioned reversal, split by news**: for |close-to-close return| above 3 sigma (own
   60-day volatility), compare next 1/5/21-session excess returns when Alpaca/Benzinga shows 0
   headlines against 1 or more, 2016 onward. Report after 10 bp round-trip cost. This directly
   tests Chan/Savor/Boudoukh in the project's universe.
2. **Momentum volatility scaling plus event-day cuts**: scale the momentum spread by inverse
   126-day realized volatility of the spread (Barroso and Santa-Clara), and separately halve
   exposure on the day before CPI and FOMC. Judge by drawdown on the known bad days (2020-11-09,
   2022-11-10) **and** by the full-period Sharpe ratio, so the test does not just fit those two days.
3. **Is news sensitivity a stable stock trait?** Per stock and year: mean |earnings-day
   return| / pre-event sigma (EDGAR 8-K dates), and beta of returns to daily changes in TPU/EPU.
   Check the rank correlation from year to year. If it is low, drop the idea. If it is high, use it
   as a risk input (position size), not as an alpha.

## Claim table

| Claim | Verdict | Size | Sample | Usable by a once-a-day trader | Free data | Source |
|---|---|---|---|---|---|---|
| Volatility clusters and rises more after falls | Real pattern | Dominant source of forecastable variance | Decades, all markets | Yes (sizing, risk) | Daily OHLC | Corsi 2009; Patton-Sheppard 2015 |
| News days have about twice the stock-specific variance | Real pattern | Variance more than 2x; R² 33% falls to 16% | S&P 500 2000-09 | Marginal (known only after the event, except scheduled news) | Alpaca news count | Boudoukh et al. 2019 |
| News counts improve volatility forecasts beyond returns | Weak | Small, mostly on high-volatility days | 23-404 stocks | Marginal | Alpaca, GDELT | Rahimikia-Poon; Halouskova-Lyocsa |
| Earnings-day move size is a persistent stock trait | Real pattern | Priced separately in options | Many years, broad | Yes (sizing ahead of known dates) | EDGAR 8-K dates | Dubinsky et al. 2019 |
| TSLA-type stocks are uniquely news-sensitive | Not supported beyond high volatility and attention | Musk-tweet effects null in the best study | 3,158 tweets | No as alpha; yes via volatility | Price data | Corvinus study; theses |
| Attention surges reverse | Real pattern (retail herding) | -4.7% over 20 days for top Robinhood buys | 2018-2020 | Marginal (no Robinhood data now; Wikipedia views as proxy) | Wikipedia pageviews | Barber et al. 2022 |
| No-news big moves reverse; news moves drift | Real but small in large caps | Autocorrelation -3.7% vs +0.7%; about 15-20 bp/day gross | S&P 500 2000-09; Chan's effect mainly small caps | Marginal (costs) | Alpaca news | Chan 2003; Savor 2012; Boudoukh et al. |
| Pervasive underreaction to firm news | Real (needs intraday data to measure) | Profitable after costs per authors | US stocks, high-frequency | Marginal | Not free (intraday) | Jiang-Li-Wang 2021 |
| PEAD in large caps | Not supported after 2006 (disputed) | About 0 | Large caps | No | EDGAR | Martineau 2022 |
| Pre-FOMC drift | Not supported after 2015 | About 0 | 2016-2019 | No | Fed calendar | Kurov-Wolfe-Gilbert 2021 |
| Media pessimism moves the market then reverses | Real (old) | -8.1 bp, 6.8 bp reversed within a week | 1984-1999 | No (too small) | GDELT tone | Tetlock 2007 |
| Trump trade statements raise volatility | Real pattern | Large, but intraday | Hundreds of tweets; 2025 episodes | Marginal (visible in EPU, TPU, VIX at the close) | EPU, TPU, VIX | Volfefe; Ge-Kurov-Wolfe |
| Trump posts predict market direction | Not supported | In-house null on 13,731 posts | 2025-2026 | No | Truth Social archive | In-house; no peer-reviewed study found |
| Trade-war announcement days fall and stay down | Real (11 days) | -11.5% total, no rebound in a week | 2018-2019 | No (unpredictable timing) | — | Amiti, Kong, Gomez, Weinstein |
| "TACO": tariff selloffs reverse | Weak / episodic | -10% then +9.5% (April 2025); -2.1% then +1.2% (January 2026) | Fewer than 10 episodes | No (one decision-maker; may end) | VIX, TPU | Press; FRBSF 2025-23 |
| Tariff exposure ranks stocks stably | Weak | Exposure predicts April 2025 abnormal returns, but sectors behaved as macro beta | 1-2 episodes | Marginal (as a risk factor) | TPU beta, 10-K text | Han et al. 2026; FRBSF; Boston Fed WP 26-15 |
| Volatility-managed market exposure | Weak after costs and out of sample | Small Sharpe gain at best | 103 strategies | Marginal | Prices | Moreira-Muir 2017; Cederburg et al. 2020 |
| Volatility-scaled momentum | Real pattern | Sharpe roughly doubles in the long sample; less recently | US 1927 onward | Yes | Prices | Barroso-Santa-Clara 2015; Daniel-Moskowitz 2016 |
| Reversal profits rise with VIX | Real pattern | About 9 bp/week per VIX point (large stocks) | 1998-2010 and replications | Marginal | VIX | Nagel 2012 |

## Sources
- NY Fed Liberty Street, "Using stock returns to assess the aggregate effect of the U.S.-China trade war" (2024-12): https://libertystreeteconomics.newyorkfed.org/2024/12/using-stock-returns-to-assess-the-aggregate-effect-of-the-u-s-china-trade-war/
- FRBSF Economic Letter 2025-23, "Market Reactions to Tariff Announcements": https://www.frbsf.org/wp-content/uploads/el2025-23_5cfd27.pdf
- Boudoukh, Feldman, Kogan, Richardson, NBER w18725: https://www.nber.org/papers/w18725.pdf ; RFS 2019: https://ideas.repec.org/a/oup/rfinst/v32y2019i3p992-1033..html
- Tetlock 2007 JF: https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf
- Savor 2012 JFE: https://ideas.repec.org/a/eee/jfinec/v106y2012i3p635-659.html ; CFA digest: https://rpc.cfainstitute.org/research/cfa-digest/2013/02/stock-returns-after-major-price-shocks-the-impact-of-information-digest-summary
- Chan 2003 JFE: https://econpapers.repec.org/RePEc:eee:jfinec:v:70:y:2003:i:2:p:223-260
- Jiang, Li, Wang 2021 JFE: https://papers.ssrn.com/abstract=2679614
- Martineau 2022 CFR: https://cfr.ivo-welch.info/published/papers/martineau2021rest.pdf ; UCLA brief: https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again
- Barber, Huang, Odean, Schwarz 2022 JF: https://profiles.wustl.edu/en/publications/attention-induced-trading-and-returns-evidence-from-robinhood-use/ ; https://gsm.ucdavis.edu/news/what-effect-brokerage-robinhood-having-stock-market
- Musk tweets (Corvinus): https://cjssp.uni-corvinus.hu/index.php/cjssp/article/view/977
- Rahimikia and Poon: https://arxiv.org/html/2108.00480v6
- Bianchi, Gomez-Cram, Kind, Kung: https://econ.jhu.edu/research-highlights/threats-to-central-bank-independence-high-frequency-identification-with-twitter/
- Volfefe: https://en.wikipedia.org/wiki/Volfefe_index ; https://www.cnbc.com/2019/09/08/donald-trump-is-tweeting-more-and-its-impacting-the-bond-market.html
- Ge, Kurov, Wolfe 2019: https://ideas.repec.org/a/bla/jfnres/v42y2019i2p213-242.html
- Kurov, Wolfe, Gilbert 2021: https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf
- Cederburg et al. 2020: https://www.lehigh.edu/~xuy219/research/COWY.pdf
- Nagel 2012: https://www.nber.org/papers/w17653 ; Drechsler et al.: https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2020/12/18-20.Drechsler2.pdf
- Bianchi et al. "Taming momentum crashes": https://strathprints.strath.ac.uk/90217/1/Bianchi-etal-SSRN-2022-Taming-momentum-crashes.pdf
- 2025 tariff firm-level studies: Han et al. 2026 https://scholarlyworks.adelphi.edu/esploro/outputs/journalArticle/Tariff-exposure-and-liberation-day-reactions/991004547559806266 ; Boston Fed WP 26-15 https://www.bostonfed.org/-/media/Documents/Workingpapers/PDF/2026/WP2615.pdf ; IMF WP 2026/070 https://www.imf.org/-/media/files/publications/wp/2026/english/wpiea2026070-source-pdf.pdf
- Episodes: Fortune 2025-10-10 https://fortune.com/2025/10/10/trump-2-percent-sp-500-china-tariffs-rare-earths-metals/ ; Fortune 2026-01-20 https://fortune.com/2026/01/20/wall-street-banking-taco-trade-greenland-tariffs/ ; Fortune 2026-02-20 https://fortune.com/2026/02/20/wall-street-calm-reaction-scotus-tariff-ruling-markets/ ; Fortune 2025-05-02 (JPMorgan post count) https://fortune.com/2025/05/02/markets-swings-truth-social-posts-jpmorgan-potfolio-manager/
- Data: FRED USEPUINDXD https://fred.stlouisfed.org/series/USEPUINDXD ; TPU https://www.matteoiacoviello.com/tpu.htm ; GPR https://www.matteoiacoviello.com/gpr.htm ; Alpaca news https://docs.alpaca.markets/docs/historical-news-data ; Alpaca forum on 2015-2016 coverage https://forum.alpaca.markets/t/historical-news-data-missing-for-2016/13576
