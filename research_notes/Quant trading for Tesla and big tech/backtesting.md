# Python Backtesting Frameworks and Backtest-Overfitting Methodology

Research date: 2026-11-18. I pulled the GitHub stats live from the GitHub REST API (`/repos/{r}`, `/releases/latest`, `/commits?per_page=1`) on that date.

## 1. Framework comparison: maintenance status in 2026, speed, live-trading support

### Takeaway
In Nov 2026 the actively maintained options are vectorbt (OSS) and vectorbt PRO, NautilusTrader, LEAN, zipline-reloaded and bt. backtesting.py gets slow, occasional releases. backtrader is effectively abandoned: its last commit was in April 2023. To share one codebase between backtest and live trading, the real choices are LEAN and NautilusTrader (both have Interactive Brokers). For fast research over many parameter sets, use vectorbt or vectorbt PRO.

### Cited Findings
GitHub snapshot (stars / last commit / latest GitHub release / license / open issues), taken 2026-11-18:

| Repo | Stars | Last commit | Latest release | License | Open issues |
|---|---|---|---|---|---|
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | 9,886 | 2026-11-11 | v1.2.1 (2026-11-11) | non-standard (GitHub "NOASSERTION"; Apache-2.0 + Commons Clause, from prior knowledge) | 129 |
| [mementum/backtrader](https://github.com/mementum/backtrader) | 23,760 | 2023-04-19 (last push 2024-08-19) | no GitHub releases | GPL-3.0 | 64 |
| [stefan-jansen/zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded) | 2,021 | 2026-11-02 | 3.2.1 (2026-10-25) | Apache-2.0 | 4 |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | 22,596 | 2026-11-18 | GitHub Releases not used (the last one is from 2017) | Apache-2.0 | 326 |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | 31,665 | 2026-11-18 | v1.231.0 (2026-08-02); v2.0.0rcN pre-releases | LGPL-3.0 | 119 |
| [pmorissette/bt](https://github.com/pmorissette/bt) | 3,040 | 2026-11-16 | v1.4.1 (2026-10-10) | MIT | 13 |
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 9,259 | 2026-08-05 | no GitHub releases; PyPI 0.6.6 (2026-07-22) | AGPL-3.0 | 110 |

- backtesting.py on PyPI: 0.6.6 came out 2026-07-22, a year after 0.6.5 (2025-07-30). Before that, 0.6.2 to 0.6.4 shipped in Feb–Mar 2025. — [PyPI backtesting JSON](https://pypi.org/pypi/backtesting/json)
- vectorbt PRO: the official site lists v2026.10.5 as current, with "agent skills and concept-boosted knowledge search" and a matching Rust build. The previous release, v2026.9.5, added "native Rust simulators, streaming indicators, and portfolio continuation". Full changelogs are for subscribers only. — [vectorbt.pro](https://vectorbt.pro/)
- NautilusTrader architecture: a Rust-native, deterministic, event-driven engine. Python is the control plane, through PyO3 bindings, and strategies can also be written in pure Rust. The same strategy and execution-algorithm code can run in backtest and live. The project warns that live trading adds venue, transport, timing, persistence and reconciliation behaviour that simulation may not reproduce. Backtests run at nanosecond resolution. — [NautilusTrader GitHub README](https://github.com/nautechsystems/nautilus_trader)
- NautilusTrader integrations: Interactive Brokers is listed as "stable". Alpaca does **not** appear in the integrations table. The other integrations are mostly crypto and betting venues (Binance, Bybit, Coinbase, OKX, Kraken, Hyperliquid, dYdX, Deribit, Betfair, Polymarket, Kalshi). The project targets bi-weekly releases and warns that breaking changes can happen. Its docs cover the v2 line (`2.0.0rcN`, installed with `pip install -U nautilus_trader --pre`). Plain `pip install` still gives the stable v1 line, which has a different API, and the project advises against running release candidates in production. Python 3.13–3.15. — [NautilusTrader GitHub README](https://github.com/nautechsystems/nautilus_trader)
- The README gives no quantitative speed benchmarks. It mentions only a Rust core, the mimalloc allocator, tokio async networking and CodSpeed benchmarking. — [NautilusTrader GitHub README](https://github.com/nautechsystems/nautilus_trader)
- LEAN reality modelling: by default `DefaultBrokerageModel` uses `NullSlippageModel`, which means **zero slippage**. Built-in alternatives are `ConstantSlippageModel`, `VolumeShareSlippageModel` (volume_limit 0.025, price_impact 0.1) and `MarketImpactSlippageModel`, which has permanent and temporary impact terms (alpha 0.891, beta 0.600, gamma 0.314, eta 0.142, latency 0.075 s). — [LEAN slippage key concepts](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/slippage/key-concepts); [LEAN supported slippage models](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/slippage/supported-models)

### Inferences
- From prior knowledge, not re-verified this session:
  - vectorbt has no broker live-trading layer. Its speed comes from vectorized NumPy/Numba, which suits sweeping thousands of parameter combinations, but event-level order realism is limited.
  - backtrader has live adapters for IB and Oanda, but they are unmaintained and depend on old library versions.
  - zipline-reloaded, bt and backtesting.py are backtest-only with no live broker integration.
  - LEAN (C# engine, Python API) runs live through QuantConnect cloud or the LEAN CLI, with brokers including IB, Alpaca and Tradier.
- LEAN's MarketImpactSlippageModel defaults look like the Almgren–Thum–Hauptmann–Li (2005) impact-model estimates. This is my inference and the docs do not say so.
- LEAN's default is zero slippage, so a LEAN backtest that does not set a slippage model will overstate returns.
- Rough speed ranking (inference, no benchmark found): vectorbt PRO (Numba + Rust) ≈ vectorbt > NautilusTrader (Rust event engine) > LEAN (C#) > zipline-reloaded > bt ≈ backtesting.py > backtrader (pure-Python event loop).
- For a TSLA/big-tech equity project, a practical stack is: vectorbt for research and parameter sweeps, then LEAN or NautilusTrader with IB for event-driven validation and live trading.

### Gaps
- I found no independent, reproducible 2026 speed benchmark comparing these frameworks. The vectorbt.pro/features/performance page exists but I did not fetch it, and the features/overview page returned 404.
- vectorbt PRO pricing and licence terms, and whether it supports live or paper trading, were not confirmed.
- I did not confirm LEAN's current list of brokers or its release versioning. It ships through Docker images and the LEAN CLI, not GitHub releases.
- I did not verify live-trading support for zipline-reloaded, bt, backtesting.py or backtrader from primary docs this session.

## 2. Biases (lookahead, survivorship, data snooping) and validation (walk-forward, purged/embargoed k-fold, CPCV)

### Takeaway
Purged k-fold drops training samples whose labels overlap the test period. An embargo also drops a buffer of samples right after the test set. CPCV builds many train/test paths from the same data, so you get a distribution of out-of-sample results instead of the single path walk-forward gives. A 2024 study found that CPCV had lower PBO and a higher DSR than walk-forward, k-fold or purged k-fold.

### Cited Findings
- Purged CV removes overlapping observations and can add a temporal embargo buffer around the test set to reduce leakage further. — [Wikipedia: Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation)
- Walk-forward gives exactly one OOS performance path, so the variance that comes from the choice of split is never measured. CPCV gives many more test paths, which makes statistical tests for overfitting possible. — [tradingstrategy.ai backtesting methodology](https://tradingstrategy.ai/docs/learn/backtesting.html); [Wikipedia: Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation)
- Arian, Norouzi Mobarekeh and Seco (2024), *Knowledge-Based Systems*, DOI 10.1016/j.knosys.2024.112477: in a synthetic controlled environment calibrated to S&P 500 data, CPCV had lower PBO and a higher DSR statistic than walk-forward, k-fold and purged k-fold. Walk-forward "exhibits notable shortcomings in false discovery prevention" (higher temporal variability, weaker stationarity). — via search summary; preprint [Scribd SSRN-id4778909](https://www.scribd.com/document/725401650/SSRN-id4778909)
- skfolio ships a CPCV implementation, and a 2024 asset-allocation paper used it with purging and embargoing to remove leakage and serial correlation. — [arXiv 2407.17645](https://arxiv.org/pdf/2407.17645)
- CPCV implementations also exist in fynance. — [fynance docs](https://fynance.readthedocs.io/en/latest/generated/fynance.data.combinatorial_purged_cv.html)
- Harvey, Liu and Zhu argue that most claimed findings in financial economics are likely false because of data mining (see section 3). — [NBER w20592](https://www.nber.org/papers/w20592)

### Inferences
- These are standard definitions, but I did not find a primary source for them this session:
  - **Lookahead bias**: the strategy uses information it would not have had at decision time. Examples: trading on the same bar's close that generated the signal, unlagged fundamentals or restated data, or using the adjusted-price split factor before the split date.
  - **Survivorship bias**: testing only on today's index members. A "big tech" universe picked in 2026 is survivorship-biased by construction. TSLA and NVDA are in it because they won. Use point-in-time index membership, or state that the analysis is conditional on hindsight selection.
  - **Data snooping**: trying many variants and reporting the best. The fix is to record every trial and then apply DSR, PBO or a haircut (section 3).
- Practical rule for daily mega-cap strategies:
  - Shift signals by one bar, fill at the next open or close, and use the next-open price with a spread cost.
  - Purge any sample whose label horizon (e.g. 5-day forward return) overlaps the test fold.
  - Set the embargo to at least the label horizon.

### Gaps
- I did not read the primary text of López de Prado, *Advances in Financial Machine Learning* (2018, ch. 7 and 12). The purging, embargo and CPCV definitions above come from secondary sources.
- The Arian et al. figures come from a search summary and a preprint, not the published article.

## 3. Deflated Sharpe ratio, PBO, multiple-testing haircuts

### Takeaway
Report the number of trials N. Deflate the best Sharpe ratio for N, skew and kurtosis (DSR). Estimate PBO with CSCV. Expect a backtest Sharpe ratio to be haircut, heavily when it is marginal: Harvey and Liu find the haircut is above 50% when the annualized Sharpe is below 0.4, and at most 25% when it is above 1.0. A new factor should clear t > 3.0, not 2.0.

### Cited Findings
- Bailey and López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", *Journal of Portfolio Management* 40(5):94–107, 2014, DOI 10.3905/jpm.2014.40.5.094. The DSR corrects for selection bias under multiple testing and for non-normal returns, adjusting for skewness and kurtosis. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- The DSR is "a PSR where the rejection threshold is adjusted to reflect the multiplicity of trials". PSR is the Probabilistic Sharpe Ratio (Bailey and López de Prado 2012). With a single trial, DSR = PSR. — [CAIA](https://caia.org/node/5735); [MetricGate](https://metricgate.com/docs/deflated-johnson-sharpe-ratio/)
- N is rarely known exactly, so the trial count is a judgment call. — [MetricGate](https://metricgate.com/docs/deflated-johnson-sharpe-ratio/)
- Bailey, Borwein, López de Prado and Zhu, "The Probability of Backtest Overfitting", *Journal of Computational Finance* 20(4), 2017, DOI 10.21314/JCF.2016.322. The paper proposes estimating PBO with combinatorially symmetric cross-validation (CSCV), which gives reasonable estimates with relatively small errors. — [Risk.net](https://www.risk.net/journal-of-computational-finance/2471206/the-probability-of-backtest-overfitting); [eScholarship PDF](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf); [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- Harvey, Liu and Zhu, "…and the Cross-Section of Expected Returns", *Review of Financial Studies* 29(1):5–68, 2016:
  - They survey 316 factors from 313 published papers and 63 working papers.
  - A new factor needs t > 3.0, roughly p < 0.0027.
  - Most claimed findings are likely false.
  - One secondary source notes that 3.0 may itself be too low, because unpublished tests are undercounted.
  - — [EconPapers RFS](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.); [NBER w20592](https://www.nber.org/papers/w20592)
- Harvey and Liu, "Backtesting", *Journal of Portfolio Management*, Fall 2015:
  - The paper gives a method for setting the haircut on a reported Sharpe ratio and a profit hurdle, using Bonferroni, Holm and BHY adjustments for the number of tests.
  - The haircut is **nonlinear**, not the rule-of-thumb 50%. Below an annualized Sharpe of 0.4 the haircut is almost always above 50%. Above 1.0 it is at most 25%.
  - It assumes normal returns.
  - — [Duke PDF P120](https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF); [Man Group summary](https://www.man.com/insights/backtesting); [Advisor Perspectives](https://www.advisorperspectives.com/articles/2016/04/28/special-edition-can-you-trust-investment-research)
- quantstrat (R) implements a `SharpeRatio.haircut` function. — [rdrr.io](https://rdrr.io/github/marsanul/quantstrat/man/SharpeRatio.haircut.html)

### Inferences
- These formulas are from prior knowledge, not checked against the PDF this session:
  - PSR(SR*) = Φ[(SR̂ − SR*)·√(T−1) / √(1 − γ₃·SR̂ + (γ₄−1)/4·SR̂²)].
  - DSR sets SR* to the expected maximum Sharpe of N independent trials: SR* ≈ √V[SR]·((1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(N·e))), where γ ≈ 0.5772 is the Euler–Mascheroni constant.
  - A common acceptance threshold is DSR > 0.95.
- From prior knowledge: CSCV splits the matrix of trial returns into S even blocks (e.g. S = 16) and forms every combination of S/2 in-sample blocks against the complementary out-of-sample blocks. PBO is the share of combinations in which the best in-sample config ranks below the OOS median (logit λ ≤ 0).
- Workflow recommendation:
  - Log every config tried (N).
  - Validate with CPCV or walk-forward.
  - Report DSR and PBO.
  - Require t > 3 for the headline strategy.
  - Treat any Sharpe ratio below about 1 on a single stock such as TSLA as likely noise once haircut.

### Gaps
- I could not extract text from the Bailey PDFs (no PDF renderer, and SSRN returned 403). The exact formulas and the S/threshold recommendations need checking against [davidhbailey.com/dhbpapers/deflated-sharpe.pdf](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf) and [backtest-prob.pdf](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf).
- I did not confirm Python implementations of DSR and PBO, such as mlfinlab (now commercial) or the `pypbo` packages, or their maintenance status.

## 4. Modeling transaction costs, slippage and spreads for liquid mega caps

### Takeaway
Quoted spreads on AAPL and MSFT during regular hours are around 1 bp. Commissions at retail brokers are often zero. For small retail size, the cost that matters is the half-spread plus slippage on signal-to-fill delay. A conservative default is 2–5 bp per side for TSLA and other mega caps. Do not leave framework defaults alone: LEAN's default slippage is zero. Market impact only matters at institutional size.

### Cited Findings
- Illustrative spreads from explainers (example quotes, not measured data):
  - Mega caps such as AAPL and MSFT during regular hours run about 0.5–1 bp.
  - AAPL $213.45/$213.47 ≈ 0.9 bp.
  - MSFT $441.80/$441.85 ≈ 1.1 bp.
  - Liquid large caps often have spreads of $0.01 or less in normal hours.
  - — [ryanoconnellfinance.com](https://ryanoconnellfinance.com/trading-execution/); [tapeboard](https://tapeboard.com/blog/what-is-the-bid-ask-spread); [Bankrate](https://www.bankrate.com/investing/what-is-bid-ask-spread/)
- A Nasdaq article on the new round-lot rules reports that, for stocks over $250 that got a 40-share round lot, average spreads compressed 34%, from "42bps to 25bps" per the search snippet. TSLA was among the names affected. I did not verify this because the article fetch timed out, and the units look suspiciously large for mega caps. They may be in different units or refer to a broader group. — [Nasdaq: new round lots helped decrease spreads](https://www.nasdaq.com/articles/new-round-lots-helped-decrease-spreads)
- LEAN's volume-share slippage caps fills at 2.5% of bar volume by default and scales impact with the square of the order's volume share. Its market-impact model separates permanent and temporary impact. — [LEAN supported slippage models](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/slippage/supported-models)
- Crypto and tokenized TSLA perp spreads (e.g. 0.28 bp on Binance/OKX vs 1.4 bp on Bitget) are **not** comparable to US-listed equities. — [DeFiLlama](https://defillama.com/research/spotlight/tokenized-stocks-volume-liquidity)

### Inferences
- Suggested cost model for daily or intraday mega-cap backtests:
  - Commission: your broker's actual schedule. IB Pro tiered is roughly $0.0035/share (from prior knowledge, not verified).
  - Half-spread: about 0.5–1 bp for AAPL, MSFT, NVDA, GOOGL, AMZN and META, and about 1–2 bp for TSLA.
  - Slippage or adverse selection: 1–3 bp for market-on-open/close or market orders. More around the open, near earnings and in fast markets.
  - Stress test: double the costs and confirm the edge survives.
- For high-turnover strategies the break-even cost per trade is the useful number. Report it: annual gross alpha ÷ (2 × annual turnover).
- Impact matters only at size. A square-root model, impact ≈ σ_daily·√(Q/ADV), means retail sizes in names with more than $10B of daily turnover have negligible impact.
- Use the framework parameters: `fees` / `slippage` in vectorbt `Portfolio.from_signals`, `commission` / `spread` in backtesting.py, and the slippage and fee models in LEAN and NautilusTrader. I did not verify these parameter names this session.

### Gaps
- I found no primary 2025–2026 TAQ or exchange measurement of quoted or effective spreads in bp for TSLA, AAPL, MSFT or NVDA. Better sources would be SEC Rule 605/606 execution-quality reports, Nasdaq or NYSE market-quality stats, or academic TAQ studies.
- I did not verify the effect of the late-2025 SEC tick-size and round-lot changes (Reg NMS amendments) on mega-cap spreads.
- I did not survey the default cost settings in vectorbt, backtesting.py, NautilusTrader or zipline-reloaded.
