# Machine Learning for Predicting Returns of Individual Large-Cap Stocks (TSLA, mega-cap tech)

Scope note: 16 tool calls. Several primary PDFs (GKX NBER/AQR versions, an Erasmus replication thesis) came back as binary and could not be read, so some exact table figures are secondary-sourced and flagged as such.

## 1. Gu, Kelly & Xiu "Empirical Asset Pricing via ML": findings; are the gains concentrated in small caps?

### Takeaway
GKX (RFS 2020) found that nonlinear models (trees, neural nets) roughly double the predictive R² of linear models, but the absolute numbers are tiny: about 0.3-0.4% monthly out-of-sample R² at the stock level. The headline Sharpe of 2.45 is equal-weighted (small-cap tilted), while value-weighted it is 1.35. GKX themselves say large, liquid stocks are predicted *better* in R² terms. But follow-up work (Avramov, Cheng & Metzker 2023) shows that most of the *tradable profit* from ML signals disappears once you exclude microcaps and distressed stocks and add trading costs. So it's "both": large caps are statistically more predictable per GKX, but the money is mostly in small, illiquid names.

### Cited Findings
- ML "offers an improved description of expected return behavior relative to traditional forecasting methods." Gains to investors are large, "in some cases doubling the performance of leading benchmarks." All methods agree that the dominant predictors are variations on momentum, liquidity and volatility. — [SSRN abstract](https://papers.ssrn.com/abstract=3306110); [NBER w25398](https://www.nber.org/papers/w25398.pdf)
- Monthly out-of-sample R², per a secondary summary: a linear model with 900+ predictors overfits (R² < 0). Penalized or dimension-reduced linear models reach about 0.26%. Nonlinear models reach about 0.33-0.40%. Neural nets reach about 0.5-0.7% monthly even for large caps. — [Mirova Research Center summary](https://www.research-center.mirova.com/en/research-library/Empirical-Asset-Pricing-via-Machine-Learning) (secondary; I could not verify against GKX Table 1 because the PDF would not parse)
- Long-short decile portfolio Sharpe ratios: neural net 1.35 value-weighted and 2.45 equal-weighted, versus linear 0.61 and 0.83. Market timing on the S&P 500: Sharpe 0.77 versus 0.51 for buy-and-hold. — [Mirova summary](https://www.research-center.mirova.com/en/research-library/Empirical-Asset-Pricing-via-Machine-Learning)
- Authors (via Chicago Booth Review): machines are better at forecasting the risk premium of a large, liquid stock than of a small, less liquid one. They also caution that the findings "do not tell us about economic mechanisms or equilibria." — [Chicago Booth Review](https://review.chicagobooth.edu/finance/2018/article/machine-learning-can-help-money-managers-time-markets-build-portfolios-and)
- Avramov, Cheng & Metzker (Management Science 2023): ML signals identify mispriced stocks, but excluding microcaps, distressed stocks or high-volatility periods sharply reduces profits. Profits fall further with reasonable trading costs, because of high turnover and extreme positions. Out-of-sample period is 1987-2017. — [SSRN 3450322](https://papers.ssrn.com/abstract=3450322); [EconPapers](https://econpapers.repec.org/RePEc:inm:ormnsc:v:69:y:2023:i:5:p:2587-2619)
- Counterpoint: cost-aware ML strategies can survive. An LSTM-based strategy reports a net six-factor alpha of 1.20%/yr (t = 3.46), per a summary of Azevedo, Hoegner & Velikov. — [Quantpedia summary](https://quantpedia.com/the-expected-returns-of-machine-learning-strategies/) (secondary)
- An Erasmus master's thesis that used a subset of the data reportedly could not replicate the original performance. — [EUR thesis](https://thesis.eur.nl/pub/59944/513098rh-thesis.pdf) (I could not read the full text; snippet only)

### Inferences
- GKX is a **monthly, cross-sectional** result over thousands of stocks. It does not show that you can predict *TSLA's* next-day return. Cross-sectional ranking R² does not carry over to single-name time-series timing.
- Large caps having higher R² but lower long-short profits fits a simple picture: large caps have small, steady predictable components (mostly risk premia), while the large mispricings are in illiquid names that cost a lot to trade.
- A monthly R² of 0.5% implies a correlation between forecast and return of about 0.07 at best. That is a weak signal that only pays off when diversified across many names.

### Gaps
- Exact GKX Table 1 R² numbers for the top-1,000 and bottom-1,000 subsamples could not be read from the primary PDF. From the author's prior knowledge (unverified this session), NN3 is about 0.40% overall, with the top-1,000 higher than the bottom-1,000. Verify against the RFS paper before quoting.
- No independent replication with full text was found.

## 2. Feature engineering that matters; label design (triple-barrier, meta-labeling)

### Takeaway
Across studies the features that consistently carry signal are price-based: momentum and short-term reversal, volatility, and liquidity/volume. Options-implied features also have good evidence at weekly horizons: implied-volatility skew and the call-put IV spread. Intraday, order-flow and order-book features dominate. Lopez de Prado's triple-barrier labels and meta-labeling are widely recommended, but their out-of-sample evidence is thin and mostly from vendors or blogs.

### Cited Findings
- GKX: the dominant predictors across all model classes are momentum, liquidity and volatility variants. — [SSRN](https://papers.ssrn.com/abstract=3306110); [Mirova](https://www.research-center.mirova.com/en/research-library/Empirical-Asset-Pricing-via-Machine-Learning)
- Xing, Zhang & Zhao (2010): firm-level IV skew (OTM put IV minus ATM call IV) predicts cross-sectional equity returns. — [Lancaster eprint (Fu et al.)](https://eprints.lancs.ac.uk/id/eprint/80351); [Netspar/Driessen](https://www.netspar.nl/wp-content/uploads/079_Driessen.pdf)
- Cremers & Weinbaum (2010): the call-put IV spread predicts weekly returns, more strongly for firms with asymmetric information. — [Netspar/Driessen WP](https://www.netspar.nl/wp-content/uploads/079_Driessen.pdf)
- Lin, Lu & Driessen: low IV spread or high IV skew predicts lower returns the following week. Much of the effect is linked to analyst and earnings news. — [Netspar WP](https://www.netspar.nl/wp-content/uploads/079_Driessen.pdf)
- Fu, Arisoy, Shackleton & Umutlu (2016): IV skew has the most significant predictive power across horizons, before and after 2008. — [Lancaster eprint](https://eprints.lancs.ac.uk/id/eprint/80351)
- Caveat: option-implied predictability may partly reflect stock borrow fees, which themselves predict returns (an AEA 2023 paper). This matters little for mega-caps, which are cheap to borrow. — [AEA 2023](https://www.aeaweb.org/conference/2023/program/paper/RsBt64RZ)
- Sirignano & Cont (Quant Finance 2019) trained a deep net on billions of US equity quotes and trades to predict the direction of the next mid-price move. A "universal" model pooled across stocks beat stock-specific linear and nonlinear models out of sample, stayed stable across stocks and periods, and worked on stocks not in training. Longer order-flow history helped; normalizations and sector splits did not. — [arXiv 1803.06917](https://arxiv.org/abs/1803.06917v1)
- Triple-barrier and meta-labeling evidence:
  - Hudson & Thames (vendor) say event sampling plus triple-barrier plus meta-labeling improves strategies. — [Hudson & Thames 2019](https://hudsonthames.org/?p=3448)
  - Warsaw working papers use triple-barrier labels with supervised-autoencoder MLPs on the S&P 500, EUR/USD and BTC (out-of-sample to 2022) and find gains only under specific noise and bottleneck tuning. — [arXiv 2404.01866](https://arxiv.org/html/2404.01866v2); [WNE WP](https://www.wne.uw.edu.pl/application/files/3517/0809/6919/WNE_WP439.pdf)
  - A purged-CV blog experiment on EURUSD ticks found out-of-sample AUC between 0.42 and 0.55, i.e. near chance. — [MQL5 article](https://www.mql5.com/en/articles/23310) (low-quality source)
- Kaggle: the 2021 Jane Street Market Prediction winner blended XGBoost with a supervised-autoencoder MLP. — [BulletTech write-up](https://bullettech.github.io/BulletTech/Main_Course/Machine_Learning/2022-01-30-Kaggle-exp-s2)
- Kaggle: in the 2024-25 Jane Street Real-Time competition (anonymized features, sample-weighted zero-mean R² on responder_6), competitive public-leaderboard scores were about 0.009-0.013. Strong approaches used GRU encoder-decoders, online-updated CatBoost and rolling-statistic features. — [competitor notes (Chinese)](https://2kkkkk.github.io/OneNotes/Kaggle/Jane%20street/总结.htm); [HKUST course page](https://aifin-hkust.github.io/project3/project3.JS_forecast.pdf)

### Inferences
- For a mega-cap single name, the most credible inputs are:
  - short-horizon reversal and momentum
  - realized volatility and volume shocks
  - options-implied features (skew, IV spread, IV term structure), useful around earnings
  - intraday order-flow imbalance
  - news and earnings events
- Triple-barrier labels are sensible because they match a trade with a stop-loss and take-profit. Meta-labeling, a second model that sizes or filters a primary signal, is mainly a way to manage risk, not a source of edge. Neither is proven to create alpha on its own.
- Best practices from *Advances in Financial ML* (book content, not re-fetched this session): purged and embargoed k-fold CV, combinatorial purged CV, the deflated Sharpe ratio to correct for multiple testing, and fractional differentiation. Their main value is preventing self-deception in backtests.
- Pooling across many stocks, as Sirignano & Cont did, beats training a per-ticker model. For TSLA, train on a universe and apply the model to TSLA.

### Gaps
- No peer-reviewed independent out-of-sample test of meta-labeling alone was found.
- The winning solutions and final private-leaderboard scores for Jane Street 2024-25 and Optiver Trading at the Close (2023) were not found. Check the Kaggle discussion tabs.
- I did not get Sirignano & Cont's exact accuracy numbers.

## 3. Deep learning / LLMs / foundation models for single-stock prediction (2023-2026); replication failures

### Takeaway
LLM news-sentiment signals are the strongest recent result: Lopez-Lira & Tang tested GPT-4 after its training cutoff. But the effect is concentrated in small stocks and negative news, it decays quickly (Sharpe 6.5 → 1.2 by 2024), and it is unprofitable at 20 bps per trade. LLM "agent" trading papers collapse under longer, broader backtests. Time-series foundation models (Chronos, TimesFM) have negative out-of-sample R² on daily returns. Look-ahead bias from LLM memorization is a major and well-documented source of inflated results.

### Cited Findings
- Lopez-Lira & Tang (arXiv 2304.07619, v6 Oct 2025):
  - Setup: gpt-4-0314 (training cutoff Sept 2021) labels news headlines; sample is Oct 2021-May 2024, 4,123 US stocks, 159,137 firm-headline-days.
  - Overnight-news next-day drift: 0.34%/day, 58% hit rate, Sharpe 2.97. Intraday-news drift: 0.50%/day, Sharpe 2.63. About 700% cumulative before costs.
  - The "93.3% hit rate" is for the *initial reaction*, which only traders with early news access could capture. It is not a tradable forecast.
  - Small-firm interaction coefficient is 0.404 versus a base of 0.087 (about 4-5x stronger in small caps).
  - Short leg: 26 bps/day, Sharpe 2.01. Long leg: 8 bps/day, Sharpe 0.78.
  - Sharpe by period: 6.54 (2021Q4), 3.68 (2022), 2.33 (2023), 1.22 (Jan-May 2024).
  - Costs: still above 300% cumulative at 5 bps, above 100% at 10 bps, unprofitable at 20 bps.
  - GPT-1, GPT-2 and BERT do not predict.
  - — [arXiv 2304.07619v6](https://arxiv.org/html/2304.07619v6)
- Li, Kim, Cucuringu & Ma (FINSABER, arXiv 2505.07078): over two decades and 100+ symbols, previously reported LLM-strategy advantages "deteriorate significantly." LLM strategies are too conservative in bull markets, underperforming passive benchmarks, and too aggressive in bear markets, taking heavy losses. Prior studies often tested less than one year on fewer than ten stocks against buy-and-hold only. — [arXiv 2505.07078](https://arxiv.org/abs/2505.07078v2)
- Gao, Jiang & Yan, "A Test of Lookahead Bias in LLM Forecasts": memorization substantially amplifies the apparent predictive power of LLM forecasts. — [arXiv 2512.23847](https://arxiv.org/pdf/2512.23847v1)
- Look-Ahead-Bench (Benhenda, arXiv 2601.13770) uses an agentic setup on five large-cap stocks. Standard LLMs show severe alpha decay out of sample, while point-in-time models are stable. — [arXiv 2601.13770](https://arxiv.org/pdf/2601.13770); [GitHub](https://github.com/benstaf/lookaheadbench)
- DatedGPT (NeurIPS 2026) uses time-aware pretraining. Look-ahead-biased models add about 26.4 bps per s.d. "lookahead premium." The bias-free headline model reports Sharpe 3.20 (unreplicated, before costs). — [NeurIPS listing](https://neurips.cc/virtual/2026/178292)
- "Re(Visiting) Time Series Foundation Models in Finance" (arXiv 2511.18578) covers daily excess returns in 94 countries over 34 years:
  - zero-shot Chronos-large: out-of-sample R² about -1.37%, direction accuracy just above 51%
  - TimesFM-500M: R² about -2.80%
  - pretraining on financial data improves Chronos-small to about -0.59% (still negative)
  - — [arXiv 2511.18578](https://arxiv.org/html/2511.18578v1)
- Off-the-shelf foundation models on hourly US equity returns give nearly flat forecasts that correlate poorly with realized rankings ("forecast collapse"). — [alphaXiv 2608.14106](https://www.alphaxiv.org/abs/2608.14106.md) (preprint)
- Index-level exception: zero-shot Chronos matched the best traditional models on Nasdaq-100 and S&P 500 data, and fine-tuning hurt. — [ISD 2025 paper](https://isd2025.fon.bg.ac.rs/wp-content/uploads/ISD_2025_camera_ready_265.pdf)

### Inferences
- **Hype flags:**
  - LLM trading-agent papers built on a few tickers over a short window.
  - Any LLM backtest whose test period falls before the model's training cutoff.
  - "90%+ accuracy" claims, which usually measure contemporaneous reaction, not prediction.
  - Foundation-model papers that report MSE on prices rather than returns.
- For TSLA and mega-caps specifically, the LLM news effect is weakest exactly where you want to use it: large caps are heavily covered, so news is priced within minutes. The remaining edge is likely in speed of reaction and in negative news.
- Deep sequence models (LSTM, GRU, transformers) win mainly on large, pooled, high-frequency datasets (Sirignano & Cont, Kaggle Jane Street). They don't win on single-ticker daily series, where there are too few independent samples.
- Reinforcement learning: I found no credible out-of-sample evidence in this session. Treat RL trading claims with strong skepticism.

### Gaps
- There is no rigorous published study of ML specifically on TSLA or the Magnificent 7 at daily or intraday horizons with realistic costs.
- I found no RL studies with rigorous out-of-sample evaluation.
- No independent replication of Lopez-Lira & Tang was found.

## 4. Realistic out-of-sample accuracy / IC numbers

### Takeaway
Honest benchmarks:
- Monthly stock-level R² of about 0.3-0.7% (GKX).
- Daily foundation-model R² below zero.
- Directional accuracy of 51-58% for credible daily signals.
- Kaggle top intraday R² of about 0.01.

Any single-stock daily direction accuracy far above 55-60%, or Sharpe above 3 net of costs, should be presumed to be leakage or overfitting.

### Cited Findings
- GKX: monthly stock-level out-of-sample R² of about 0.33-0.40% for nonlinear models and about 0.5-0.7% for large caps with neural nets. — [Mirova summary](https://www.research-center.mirova.com/en/research-library/Empirical-Asset-Pricing-via-Machine-Learning)
- Zero-shot foundation models on daily returns: R² of -1.37% to -2.80%, with about 51% direction accuracy. — [arXiv 2511.18578](https://arxiv.org/html/2511.18578v1)
- LLM news drift: 55-58% hit rate and Sharpe 2.6-3.0 gross, decaying to 1.2 by 2024 and dying at 20 bps cost. — [arXiv 2304.07619v6](https://arxiv.org/html/2304.07619v6)
- Jane Street 2024-25: competitive weighted R² of about 0.009-0.013 on the public leaderboard. — [competitor notes](https://2kkkkk.github.io/OneNotes/Kaggle/Jane%20street/总结.htm)
- Out-of-sample AUC for a triple-barrier pipeline on FX ticks: 0.42-0.55. — [MQL5](https://www.mql5.com/en/articles/23310) (low quality)
- ML signal net alpha after costs: about 1.2%/yr for the best LSTM strategy (summary of Azevedo, Hoegner & Velikov). — [Quantpedia](https://quantpedia.com/the-expected-returns-of-machine-learning-strategies/)

### Inferences
- An information coefficient (IC) of 0.02-0.05 per stock per period is a good, realistic daily cross-sectional signal. This is a practitioner rule of thumb, consistent with the R² of about 0.5% (implied correlation of about 0.07) above, but not directly sourced here.
- By the "fundamental law," a single stock like TSLA has breadth of 1 per period. Even a real IC of 0.03 gives a poor single-name information ratio unless you trade many times or across many names. Trading one mega-cap with ML is structurally disadvantaged versus a cross-sectional book.
- TSLA's high volatility (often 50-60% annualized) amplifies noise. The same R² translates into larger drawdowns and makes edges harder to tell apart statistically.

### Gaps
- I found no published IC numbers specific to mega-cap tech names.
- Optiver Trading at the Close final scores were not retrieved.
- Practitioner IC rules of thumb are not sourced in this session.
