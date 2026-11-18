# Regime Detection and Strategy Ensembling for a TSLA / Mega-Cap Tech Quant System

Scope: regime signals (HMM, VIX term structure, trend filters, macro/credit), signal combination, alpha-decay monitoring, and live monitoring architecture. Evidence mostly 2010-2026; some foundational older work is noted where later papers build on it. Most sources test on **indices or broad factor portfolios, not single stocks**. Applying them to TSLA (very volatile, idiosyncratic) is an extrapolation and is flagged as such.

## Q1. Regime signals (HMM, VIX/term structure, trend filters, macro/credit): out-of-sample evidence

### Takeaway
Regime filters reliably **cut drawdowns** out of sample (often by half on equity indices). They raise Sharpe modestly at best, and returns rarely improve. Simple, persistent filters (jump models, long moving averages, credit stress) are more robust than raw HMMs, which trade too much. VIX term-structure signals carry information mainly in rare backwardation episodes. Single-stock evidence is weak.

### Cited Findings
**HMM vs. statistical jump models (strongest OOS test found)**
- Shu, Yu & Mulvey (arXiv 2402.05272) ran a 0/1 index-vs-T-bill strategy on the S&P 500, DAX and Nikkei. Test period 1990-2023, rolling 3,000-day refits, 10 bp one-way costs, 1-day execution delay. S&P 500 results: buy-and-hold Sharpe 0.48 / max drawdown -55.2%; HMM 0.54 / -28.9% with 141% turnover; jump model 0.68 / -26.6% with 44% turnover. — [arXiv 2402.05272](https://arxiv.org/html/2402.05272v2)
- In that study the HMM *lowered* S&P return (8.5% vs 10.2% buy-and-hold), and its Sharpe fell below buy-and-hold at a 5-day delay for the DAX and Nikkei. The jump model (a penalty that enforces regime persistence) held up: S&P Sharpe was 0.68 / 0.71 / 0.70 at 1, 5 and 10-day delays. — [arXiv 2402.05272](https://arxiv.org/html/2402.05272v2)
- The same paper notes that regime signals lag turning points by about 2 weeks, can miss rebounds, and may struggle in long choppy markets. It argues HMMs are sensitive to mis-estimation and mis-specification. — [arXiv 2402.05272](https://arxiv.org/html/2402.05272v2)
- Earlier work (Bulla et al.) found that Markov-switching allocation, which cuts exposure in high-vol states, was profitable after costs out of sample on US, Japanese and German indices. — [MPRA 21154](https://mpra.ub.uni-muenchen.de/21154/1/MPRA_paper_21154.pdf)
- A 2026 paper used a 3-state Gaussian HMM chosen by BIC, ETF data 2004-2025, a 1-day lag and RL on top. Its 2022-2025 OOS Sharpe was 0.83 vs 0.82 for a 60/40 rotation benchmark, i.e. essentially no Sharpe gain, though drawdown was shallower. — [arXiv 2605.27848](https://arxiv.org/pdf/2605.27848)

**Trend filters (200-day MA / 10-month rule)**
- Faber's 10-month MA timing rule was re-tested with 1972-2005 as in-sample and the following ~11 years as out-of-sample, across stocks, bonds, REITs and commodities. The result is reported as favorable. (Secondary summary.) — [etf.com / Swedroe](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist)
- Counter-evidence: a StockCharts test of the S&P 500 200-day MA over 25 years found many whipsaws and a lower CAGR, plus a *higher* drawdown than buy-and-hold, though it avoided the 2000-02 and 2008-09 bears. — [StockCharts](https://articles.stockcharts.com/article/articles-arthurhill-2018-04-systemtrader---putting-the-200-day-moving-average-through-the-wringer/)
- Philosophical Economics found MA rules performed poorly on **individual securities**, which is directly relevant to TSLA. — [Philosophical Economics](https://www.philosophicaleconomics.com/?p=7296)
- CXO Advisory warns of data-snooping bias when many MA rules are compared on the same sample, and notes that results depend on the bull/bear mix of the sample. — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/taking-the-noise-out-of-technical-trading/)
- Hurst, Ooi & Pedersen (AQR, JPM 2017) tested time-series trend across 67 markets since 1880. It did well in 8 of the 10 largest 60/40 drawdowns and was strongest in extreme equity years, including 2008. Note: AQR sells trend products, and the headline results assume 2/20 fees. — [Alpha Architect summary](https://alphaarchitect.com/?p=34042); [paper PDF](https://www.TrendFollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf)

**VIX level and term structure**
- Johnson (2011 working paper): the VIX term structure predicts next-quarter S&P 500 returns with an adjusted R² of about 5.2%, while spot VIX alone has little predictive power. — [Johnson WP](https://www.bauer.uh.edu/departments/finance/documents/seminars/Johnson_020712.pdf)
- Macrosynergy: a normal (contango) VIX curve showed no significant predictive power. Inversion (backwardation) works as a *contrarian* timing signal, so it points to higher subsequent returns, not lower. — [Macrosynergy](https://macrosynergy.com/?p=41000)
- A low slope (backwardation) is followed by higher returns on variance and VIX products. These are gross results, and frictions may erode them. — [CXO Advisory](https://www.cxoadvisory.com/volatility-effects/vix-term-structure-slope-and-variance-asset-future-returns/)
- Other papers find the implied-vol term structure predicts S&P excess returns, mostly at short horizons. — [EFMA 2016](https://efmaefm.org/0efmameetings/efma%20annual%20meetings/2016-Switzerland/Papers/EFMA2016_0213_fullpaper.pdf); [JRFM 2019](https://mdpi.com/1911-8074/12/3/113)

**Volatility scaling as a regime response**
- Moreira-Muir volatility-managed portfolios show positive in-sample spanning alphas. Cederburg, O'Doherty, Wang & Yan (JFE 2020) tested 103 equity strategies. Real-time implementable versions generally had *lower* Sharpe and certainty-equivalent returns than the unmanaged portfolios, which they attribute to structural instability. — [Cederburg et al. WP](https://www.lehigh.edu/~xuy219/research/COWY.pdf); [Alpha Architect](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/)
- DeMiguel, Martín-Utrera & Uppal (JF 2024): a *conditional multifactor* volatility-managed portfolio does beat the unconditional one out of sample and net of costs. — [LBS PDF](https://lbsresearch.london.edu/id/eprint/3716/1/The%20Journal%20of%20Finance%20-%202024%20-%20DeMIGUEL%20-%20A%20Multifactor%20Perspective%20on%20Volatility%E2%80%90Managed%20Portfolios.pdf)

**Macro / credit**
- Gilchrist & Zakrajšek (AER 2012) split corporate credit spreads into expected default and an "excess bond premium" (EBP). EBP shocks lead to significant declines in activity *and equity prices*, and the EBP accounts for essentially all of credit spreads' forecasting power. — [NBER w17021](https://www.nber.org/papers/w17021); [NBER Reporter 2018](https://www.nber.org/reporter/2018number4/role-financial-factors-economic-fluctuations)
- The Fed publishes EBP-based recession probabilities, which give a free, maintained regime input. — [FEDS Notes 2016](https://www.federalreserve.gov/econres/notes/feds-notes/updating-the-recession-risk-and-the-excess-bond-premium-20161006.html)
- Man Group (Mulliner, Harvey et al., 2025) scored "similarity to past periods" on 7 annual-change z-scored variables: S&P 500, yield-curve slope, oil, copper, T-bill yield, equity vol and stock-bond correlation. Positioning on the most-similar historical dates performed best, and the least-similar did worst. Alpha was reported at >3 standard errors. Sources disagree on the publication date (March vs June 2025). — [Man Group](https://www.man.com/insights/regimes-systematic-models-power-of-prediction); [Fi-desk](https://www.fi-desk.com/insights-analysis-man-group-quants-qualify-todays-economic-regime/)

### Inferences
- For TSLA and mega-caps, regime filters should mostly **scale exposure or gross leverage** (risk-on/off), not flip direction. The robust benefit is drawdown reduction, not extra return.
- Regime persistence matters more than the model class. A jump-penalized or heavily smoothed signal beats a raw HMM once turnover and delay are counted. Practically: require N days of confirmation, or use hysteresis bands.
- Index-level regime signals (SPX/NDX trend, VIX curve, EBP / HY OAS) are likely more reliable for a TSLA book than regime models fit on TSLA's own price. Single-stock MA filters have poor evidence.
- VIX backwardation is better treated as a "stress now / possible capitulation" flag than as a sell signal, since the evidence says forward returns after inversion are *higher*.

### Gaps
- No OOS study found that applies HMM or jump models specifically to TSLA or a mega-cap tech basket.
- I did not verify Faber's OOS numbers from the primary paper; the summary is secondary.
- No net-of-cost evidence found for VIX term-structure timing of equities.
- I did not check the full Man Group paper's sample period or costs.

## Q2. Signal combination: equal-weight vs IC-weighted vs ML stacking; why momentum + mean reversion + carry improves Sharpe

### Takeaway
With few, noisy signals, **equal weighting (of volatility-normalized signals) is hard to beat**. This is the "forecast combination puzzle": estimation error in the weights eats the theoretical gain. IC-weighting helps only with long, stable IC histories and shrinkage. ML ensembles win mainly in large cross-sections (thousands of stocks), not in a single-name or small-basket book. Combining helps because low or negative correlation between signals raises breadth (IR ≈ IC × √breadth).

### Cited Findings
- **Forecast combination puzzle:** optimized combination weights generally fail to beat a simple average, because estimating the weights adds variance. Equal weights have lower variance than estimated "optimal" weights. — [Frazier et al., arXiv 2308.05263](https://arxiv.org/pdf/2308.05263)
- Recent work (Lee & Lee 2025/2026) keeps the simple average as the baseline and adds only selected individual signals, with modest gains in macro forecasting. — [UCR WP 202514](https://ideas.repec.org/p/ucr/wpaper/202514.html); [UCR WP 202603](https://economics.ucr.edu/repec/ucr/wpaper/202603.pdf)
- **Fundamental law:** IR ≈ TC × IC × √BR. Breadth for correlated signals comes from the inverse correlation matrix, so correlated signals add little breadth. A generalized version weights factors by the inverse of the *IC covariance* matrix, using mean IC / IC volatility, which penalizes unstable or correlated signals. — [CFA technical appendix](https://www.cfainstitute.org/-/media/documents/support/programs/cfa/technical-append-to-analysis-of-active-portfolio-mgmt.pdf); [Generalized fundamental law](https://alphafocusir.com/research/)
- Grinold's rule for converting a z-score signal into an expected return: alpha = volatility × IC × score. — [CFA technical appendix](https://www.cfainstitute.org/-/media/documents/support/programs/cfa/technical-append-to-analysis-of-active-portfolio-mgmt.pdf)
- Caveat: the Grinold formula's assumptions break down for IC > 0.10 and assume equal skill across assets. — [New Frontier estimation-error note](https://newfrontieradvisors.com/media/oixdgglx/estimation-error-technical-companion.pdf); [Menchero, JOIM](https://joim.com/wp-content/uploads/emember/downloads/p0543.pdf)
- **Diversifying style combos:** Asness, Moskowitz & Pedersen (JF 2013) find value and momentum negatively correlated within and across 8 asset classes (average within-class correlation about -0.49). The 50/50 combination beat either factor alone in every market studied. — [Chicago Booth Review](https://www.chicagobooth.edu/review/better-bet); [etf.com / Swedroe](https://www.etf.com/sections/index-investor-corner/swedroe-close-look-value-momentum); [paper](https://pages.stern.nyu.edu/~lpederse/papers/ValMomEverywhere.pdf)
- **ML stacking:** Gu, Kelly & Xiu (RFS 2020), ~30,000 US stocks over 60 years. Timing the S&P 500 with neural-net forecasts gave an OOS Sharpe of 0.77 vs 0.51 for buy-and-hold. A value-weighted NN long-short decile spread gave a Sharpe of 1.35, more than double the leading linear benchmark. The highest Sharpe figures (~2.45, equal-weighted) lean heavily on micro-caps. Trees, NNs and their ensembles beat linear models mainly by capturing interactions. — [NBER w25398](https://www.nber.org/papers/w25398.pdf); [SSRN](https://papers.ssrn.com/abstract=3306110)

### Inferences
- Recommended default for a TSLA / mega-cap system: z-score each signal (trend/momentum, short-term mean reversion, carry-like signals such as implied-vol vs realized, earnings drift, etc.). Volatility-normalize each signal, average them equal-weight, then cap the result. Move to IC-weighting only with **shrinkage toward equal weight** (e.g. 50/50 blend) and IC estimated over years, not months.
- Momentum and mean reversion work at different horizons (trend over months, reversal over days) and tend to be negatively correlated. Combining them raises effective breadth, which is the mechanism behind the Sharpe gain, not either signal getting stronger. The quantitative proof here is value + momentum (AMP 2013); the momentum + mean-reversion + carry Sharpe gain for single stocks was **not** directly sourced.
- ML stacking needs breadth. With ~10 mega-caps, the cross-section is too small for GKX-style results to transfer. Overfitting risk dominates, which points to the deflated-Sharpe checks in Q3.

### Gaps
- No primary source found quantifying the Sharpe gain from momentum + mean reversion + carry specifically in single stocks or tech. "Carry" for equities (dividend yield, borrow fee, implied-vol carry) is poorly defined for TSLA, which pays no dividend.
- No head-to-head OOS study found of equal-weight vs IC-weight vs stacking on a small single-stock universe.
- Bayesian IC-shrinkage literature was not located.

## Q3. Alpha decay monitoring and live strategy health checks

### Takeaway
Published anomalies lose roughly a third to over half of their return after publication, so decay should be the default expectation. Live health checks should compare realized performance against a *deflated* backtest expectation, not the raw backtest Sharpe. Use rolling Sharpe/IC, drawdown versus expected, and change-point tests (CUSUM). Bake in kill rules ahead of time.

### Cited Findings
- McLean & Pontiff (JF 2016), 82 published anomalies (72 replicable): the average post-publication return falls about 35%. Related estimates put the in-sample to post-publication decline near 58%, with decay peaking 3-4 years after publication. Anomalies that are costlier to arbitrage decay less. — [CXO Advisory](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation); [Advisor Perspectives](https://api.advisorperspectives.com/articles/2014/05/06/can-investors-profit-using-academic-research)
- Jacobs & Müller (2017) find a reliable post-publication decline only in the US, partly explained by a general time trend. — [Jacobs & Müller WP](https://www.wiwi.hu-berlin.de/en/Professorships/bwl/finance/seminars/papers-fin-acc-res-seminars/17s/jacobs.pdf)
- Cross-sectional stock momentum's efficacy has faded over the last decade (per a Cambridge Associates summary). — [Cambridge Associates 1Q18](https://publishedresearch.cambridgeassociates.com/wp-content/uploads/2018/02/Investment-Publications-Highlights-1Q18.pdf)
- **Deflated Sharpe Ratio** (Bailey & López de Prado, JPM 2014) corrects for selection bias from multiple trials and for non-normal returns (skew, kurtosis). The companion Probabilistic Sharpe Ratio and Minimum Backtest Length guard against picking strategies that are high Sharpe in-sample but zero or negative out of sample. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- Bailey, Borwein, López de Prado, Salehipour & Zhu: in their setup, more than ~45 variations make a Sharpe ≥ 1.0 achievable by chance. In one demo, in-sample Sharpe was 1.59 and out-of-sample -0.18. — [Backtest overfitting PDF](https://ioandc.com/wp-content/uploads/2021/08/backtestfail.pdf); [CXO summary](https://www.cxoadvisory.com/big-ideas/backtest-overfitting-the-movies/)
- Practitioner tooling for decay detection includes CUSUM with calibrated thresholds and rolling alpha regression. Rolling regression is claimed to flag decay earlier than raw P&L, but I found no independent validation. — [Video summary](https://videohighlight.com/v/CWOhChDdnn4)
- A typical dashboard metric is a rolling 63-day Sharpe by strategy. — [qgtm docs](https://qgtm-docs.pages.dev/tutorial/09-running-the-platform)

### Inferences
- Record the number of backtest trials per strategy and compute DSR/PSR at go-live. Set the "expected live Sharpe" to the deflated value, haircut a further ~35-50% for decay per McLean-Pontiff.
- A 63-day rolling Sharpe is very noisy: its standard error is about √(252/63) ≈ 2 Sharpe units annualized. Use it as a display metric, not a kill trigger. Better triggers: (a) a CUSUM on daily excess returns versus expected mean; (b) drawdown beyond roughly 1.5-2× the backtest max drawdown; (c) rolling 6-12 month IC of each signal below zero with statistical significance; (d) feature-distribution drift (e.g. a PSI/KS test on signal inputs) to catch data or regime breaks.
- Monitor each sub-signal separately, not just the ensemble. A dead signal hides inside a healthy blend.

### Gaps
- No peer-reviewed source found specifying optimal CUSUM or rolling-Sharpe thresholds for retiring a strategy.
- No study found measuring alpha decay specifically in TSLA or mega-cap tech signals.

## Q4. Practical live signal-monitoring architecture for retail quants

### Takeaway
Retail practice centres on a scheduled pipeline: data refresh, then signal compute, then risk checks, then orders/alerts. Add an **independent** kill switch with persisted state, heartbeat/dead-man alerts, and push notifications (Slack/Telegram/email). Sources here are practitioner blogs and open-source docs, not authoritative references.

### Cited Findings
- Kill switches should be tiered: multiple triggers (daily loss, max drawdown, margin spikes, order-rate anomalies, execution errors), multiple actions and fallbacks, and independence from strategy logic. — [Stratzy](https://stratzy.in/blog/algo-kill-switch-engineering-how-smart-traders-protect-capital-in-volatile-markets); [NexusFi](https://nexusfi.com/a/automation/automated-risk-controls)
- When several controls fire, the most severe state wins, and severity never auto-downgrades. — [NexusFi](https://nexusfi.com/a/automation/automated-risk-controls)
- Persist the kill-switch trip to a file and check it at startup, so an auto-restart cannot silently re-enable trading. — [QuantInsti](https://www.quantinsti.com/articles/monitor-trading-bot-real-time/)
- Monitoring metrics: per-strategy drawdown, rolling Sharpe, exposure, open positions, plus portfolio-level aggregate drawdown and correlation. — [ClawHub risk service](https://clawhub.ai/greenhelix-trading-bot-risk-service); [qgtm docs](https://qgtm-docs.pages.dev/tutorial/09-running-the-platform)
- Heartbeat and dead-man switch patterns: one config uses a 48-hour dead-man timer, another escalates if the operator is unreachable for 30 minutes. Critical alerts go out on kill-switch trips and max-drawdown breaches via logs plus Slack. Prometheus metrics feed Grafana/Datadog/CloudWatch. — [Alpha Oracle docs](https://ben-ripley.github.io/alpha-oracle/user-guide/operations/monitoring-alerts.html); [qgtm docs](https://qgtm-docs.pages.dev/tutorial/09-running-the-platform)

### Inferences
Minimal retail architecture consistent with the above (an inference, not sourced as a standard):
1. **Scheduler**: cron or Windows Task Scheduler, or APScheduler. Run an EOD job about 30-60 minutes after the close for daily signals, plus a pre-open sanity job. Intraday only if signals need it.
2. **Data refresh**: pull prices and VIX/VIX3M (or the VIX futures curve). Pull credit spreads (e.g. FRED HY OAS) and the Fed EBP for regime. Validate each pull: staleness, missing bars, split/adjustment jumps. On failure, **fail closed** (no new trades) and alert.
3. **Regime layer**: compute a few robust flags (index trend vs 200-day or 10-month MA, VIX curve inversion, credit-stress z-score, optional jump-model state). Combine them into a gross-exposure multiplier with hysteresis.
4. **Signal layer**: equal-weight z-scored signals, times the regime multiplier, then volatility target and position caps.
5. **Health checks**: log every signal value and position to a DB (SQLite/Parquet). A daily job computes per-signal rolling IC, a strategy CUSUM versus deflated expectation, and drawdown versus backtest. Run drift tests on inputs.
6. **Alerting**: Telegram/Slack/email for failures, kill trips and drift. Send a daily "I'm alive" heartbeat, and treat its absence as an alert.
7. **Kill switch**: a separate process or check with persisted state that requires a manual reset.

### Gaps
- No authoritative or academic reference architecture for retail monitoring was found. Sources are vendor docs and blogs of unverified quality.
- No data found on how often retail systems fail from data or infrastructure issues versus alpha decay.
