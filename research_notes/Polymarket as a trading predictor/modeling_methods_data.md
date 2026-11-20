# Modeling Methods and Data Engineering for Prediction-Market-Driven Trading (as of Nov 2026)

Scope: practitioner and data-engineer methods for turning Polymarket and Kalshi prices into trading inputs. This covers bracket-to-distribution conversion, entry rules and fill probability, cross-asset designs, sizing, data plumbing, sample size, and forward testing.

Research budget note: about 15 searches and fetches. I could not extract the full text of the Fed paper PDF because no PDF tool was available locally. Where I give formulas without a fetched source, they are standard derivations and are listed under Inferences, not Cited Findings.

---

## Q1. Which public write-ups and open-source projects use prediction-market odds as trading inputs, and what do they report?

### Takeaway
Rigorous public evidence is thin. Academic work shows that Kalshi distributions are well-behaved and useful as *expectations measures*: a Fed paper finds Kalshi FOMC forecasts about as accurate as the primary-dealer survey. Published "odds → asset return" trading results are small-sample, single-event, or unconditionally weak. Even a careful student project found the unconditional signal significant only for oil.

### Cited Findings
- FEDS 2026-010, "Kalshi and the Rise of Macro Markets" (Diercks, Katz, Wright; Feb 12, 2026, later revised). It calls Kalshi "a high-frequency, continuously updated, distributionally rich benchmark" for macro expectations — [Fed abstract page](https://federalreserve.gov/econres/feds/kalshi-and-the-rise-of-macro-markets.htm); [PDF](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf)
- Secondary summaries of that paper make three further claims. (1) Implied distributions are "well-behaved and broadly consistent" with established instruments. (2) Fed-funds forecasts are on par with the primary dealer survey about three meetings ahead. (3) No traded options give the fed funds distribution after a specific FOMC meeting, and Kalshi fills that gap. Several summary sites (for example, libertify) look AI-generated, so verify numbers against the PDF — [search summary of Fed/NatLawReview/Katten coverage](https://natlawreview.com/article/federal-reserve-researchers-find-prediction-markets-deliver-forecasting-value); [ECB conference version, Wright](https://www.ecb.europa.eu/press/conferences/shared/pdf/20261005_monpolconf/Wright_paper.pdf)
- flyingduck0 "ML Seminar Project" (GitHub Pages dashboard):
  - Signals: Polymarket hourly signals pm_delta, pm_z, pm_vol and a missingness flag, z-scored against a rolling 20-hour window. A shock is |ΔPM_t| > μ_t + 2σ_t.
  - Assets: SPY, QQQ, oil, BTC, gold, and ES.
  - Tests: Jordà local-projection IRFs at h=1–6 on shock hours with HC3 errors, and LightGBM with 5-fold expanding walk-forward.
  - Costs: 1–2 bps round trip.
  - Events: 9–13 per macro-release type over a 13-month window. The authors call the results "directional rather than definitive."
  - Results: The incremental-R² joint F-test (PM signals added to a VIX/DXY/rates baseline, 9,673 hours) is significant only for oil (p<0.05). They highlight INF→Oil at p<0.001 in the pre-event activity test.
  - [flyingduck0 ML Seminar Project](https://flyingduck0.github.io/ML_Seminar_Project/)
- Quiver Quantitative / Barchart DJT study:
  - Granger tests suggested DJT lagged Polymarket Trump-win odds.
  - A next-day strategy was positive on 51 of 92 days.
  - Barchart reported +10% since Jul 1, 2024, against a loss for buy-and-hold.
  - Caveat: this is a single stock and a single election, and it has no out-of-sample test.
  - [Quiver](https://www.quiverquant.com/news/Trump+Media+Stock+%28DJT%29+Linked+to+Election+Odds%3F+Our+Investigation+); [Barchart](https://www.barchart.com/story/news/29231845/trump-media-stock-djt-linked-to-election-odds-our-investigation)
- arXiv 2603.03152 looks at Polymarket after three 2024 election shocks. The debate-induced jump largely reversed, while the assassination-attempt repricing persisted. So odds shocks are not uniformly "information" — [papers.mewayz summary of arXiv 2603.03152](https://papers.mewayz.com/paper/arxiv_2603.03152)
- Boğaziçi/SSRN paper: 5-minute Polymarket probabilities combined with stock prices in an event study around July 2024. Its focus is partisan firm exposure, not a trading rule — [PDF](https://web.bogazici.edu.tr/torul/polcap.pdf)
- evan-kolberg/prediction-market-backtesting is a NautilusTrader-based framework for backtesting prediction-market contracts themselves, not cross-asset trades. It is still in active development — [GitHub](https://github.com/evan-kolberg/prediction-market-backtesting)
- The Orrery signal backtests use only markets that are currently live, which is an explicit survivorship issue — [Orrery](https://www.orrery.me/backtest)
- Practitioner Substack and blog content on PM "alpha" is common, but it is mostly unverified marketing. Examples are the navnoorbawa Substack and the "84% of Polymarket traders lose money" dev.to post — [Substack](https://navnoorbawa.substack.com/p/the-mathematical-execution-behind); [dev.to](https://dev.to/manja316/84-of-polymarket-traders-lose-money-i-backtested-6225-trades-to-find-what-actually-works-3n32)

### Inferences
- The defensible use is as an *expectations/regime measure*: implied mean, dispersion, and event probability as features. It is weaker as a standalone directional alpha signal. Positive public trading results are single-event anecdotes.
- The publication filter is heavy. Projects that found nothing rarely publish, and vendors publish what sells.

### Gaps
- I found no peer-reviewed, out-of-sample study showing that PM-odds-based equity or ETF trading rules beat costs across many events.
- I did not get full-text methodology from FEDS 2026-010 (PDF text extraction failed). That paper is the best primary source for distribution construction and should be read directly.

---

## Q2. (a) Turning bracket markets into a distribution, EV and quantiles; handling vig and missing tails

### Takeaway
Treat each bracket's YES price (preferably mid, or better a bid/ask range) as an unnormalized probability mass. Normalize to remove overround, choose a tail model for open-ended brackets, and compute the mean, CDF and quantiles from the resulting piecewise distribution. This is the discrete analogue of Breeden-Litzenberger: digital option price = discounted P(S>K). The mean is the most fragile output because it depends on the tail assumption. The median and interquartile range are robust.

### Cited Findings
- Kalshi range and ladder markets split an outcome into mutually exclusive bands, each a separate yes/no contract. Differencing across strikes gives the implied distribution — [Kalshi: how to read probabilities](https://news.kalshi.com/p/how-to-read-probabilities); [Kalkine BTC year-end ranges](https://www.kalkine.com/news/general-news/bitcoin-price-prediction-2026-kalshi-markets-give-even-odds-across-a-60000-to-70000-year-end-range)
- A Glasgow paper recovers the market-implied interquartile range from Kalshi's contract ladder, using dispersion rather than the mean as the robust statistic — [eprints.gla.ac.uk 390184](https://eprints.gla.ac.uk/390184/1/390184.pdf)
- Polymarket "IPO closing market cap" markets work as follows:
  - Resolution: first-day closing market cap = shares outstanding × first-day closing price.
  - Ties: a value exactly on a boundary goes to the higher bracket.
  - Source: the primary exchange's official listing.
  - OpenAI variant: resolves "no IPO" if nothing lists by Dec 31, 2026.
  - [frenzycap: Anthropic IPO closing market cap](https://www.frenzycap.com/predictions/event/polymarket/anthropic-ipo-closing-market-cap); [OpenAI](https://www.frenzycap.com/predictions/event/polymarket/openai-ipo-closing-market-cap)
- Anthropic snapshot (Nov 15, 2026), illustrating that bracket sums need checking:
  - $1.25–1.5T at 42.1%
  - $1.5–1.75T at 20.8%
  - $1.75–2.0T at 9.2%
  - ≥$1.5T at about 34.1%, per FourWeekMBA's sum
  - [CryptoSlate](https://cryptoslate.com/?p=583589); [FourWeekMBA](https://fourweekmba.com/ai-anthropic-ipo-polymarket-odds-of-a-1-5t-debut-fall-to-34/)

### Inferences (standard derivations, not sourced)
**Inputs.** Brackets i=1..n with edges [L_i, U_i). Brackets 1 and n may be open (L_1=−∞ or U_n=+∞). Use mid m_i = (bid_i+ask_i)/2, falling back to last trade only if the spread is tight.
- Overround: O = Σ m_i. On Polymarket, Σ asks > 1 > Σ bids is typical, and the gap is spread, not a bookmaker margin. Normalize p_i = m_i / O. Alternatives:
  - Proportional normalization (above). This is simple and is the default.
  - Power or Shin-style normalization, which takes more out of longshots. Use it if you believe favorite-longshot bias (Q4) inflates the cheap tail brackets: p_i ∝ m_i^k, solving for k so that Σ p_i = 1.
  - Report the result as a band: compute the distribution once from bids and once from asks, each normalized, to get a cheap "bid-ask envelope" on the mean and quantiles.
- Polymarket "negRisk" multi-outcome events are mutually exclusive by construction. Kalshi "above K" ladders are cumulative, not brackets: P(X≥K_j) must be non-increasing in K. Enforce monotonicity (isotonic regression) before differencing: p_j = P(≥K_j) − P(≥K_{j+1}). That differencing is the Breeden-Litzenberger analogue.

**Within-bracket shape.** Uniform within each bracket gives a piecewise-linear CDF:
- F(x) = Σ_{j<i} p_j + p_i·(x−L_i)/(U_i−L_i) for x in bracket i.
- Quantile q: find i where the cumulative crosses q, then x_q = L_i + (q − F(L_i))/p_i · (U_i − L_i).
- Mean: E[X] = Σ p_i·(L_i+U_i)/2 for closed brackets, plus the tail terms.
- A smoother option is a monotone cubic (PCHIP) fit of the CDF through the bracket edges, or a lognormal or skew-normal fit to the bracket masses by least squares/KL. Use the fitted parametric distribution only for the tails.

**Missing tails.** The open-ended "≥U" or "<L" bracket has unknown conditional mean.
- (i) Use the parametric (lognormal) fit to compute E[X | X ≥ U].
- (ii) Use an exponential/Pareto tail calibrated so the density is continuous at U.
- (iii) Report the mean under several assumptions. Prefer the median and quantiles (insensitive to the tail) for rules.
- Unit conversion: IPO brackets are on *market cap*. Convert to price with price = cap / shares_outstanding, using the exact share count the resolution rules use (often basic shares outstanding, not fully diluted). A wrong share count shifts every quantile.

**Fine-ness limit.** With 5–8 brackets, quantiles inside a wide bracket are interpolation artefacts. State the bracket width as the precision of any "implied median".

### Gaps
- I found no published practitioner standard for de-vigging Polymarket bracket sets (proportional vs power/Shin). The choice is a judgment call, so test sensitivity.
- I could not confirm the Fed paper's exact construction (interpolation and tail treatment) without the PDF text.

---

## Q3. (b) Event-driven entry rules using the distribution, and the fill-probability problem

### Takeaway
Rules like "buy the IPO only if the open is below the implied median" or "rest a limit at the implied 25th percentile" are easy to state. But the market-implied distribution is for the *close*, not the intraday low, and limits placed in the left tail mostly don't fill. The fills you do get are adverse-selected: you are filled exactly when the stock is weak. The fill rate and conditional return must be modeled together.

### Cited Findings
- Resolution is on the first-day *close* market cap, so the PM distribution says nothing directly about the intraday path or low — [frenzycap Anthropic rules](https://www.frenzycap.com/predictions/event/polymarket/anthropic-ipo-closing-market-cap)
- Data from the user's own record (not independently verified): Anthropic IPO priced at $83 with an intraday low of $92.72, so a $70 limit would never have filled.
- Bürgi/Deng/Whelan find that makers earn better returns than takers on Kalshi (takers about −32%, makers about −10% on average). For anyone trading the *contracts*, resting orders get adverse selection, but crossing the spread costs much more — [CEPR VoxEU](https://cepr.org/index%2Ephp/voxeu/columns/economics-kalshi-prediction-market)

### Inferences
- **Signal definitions (pre-registered):** Let F be the implied distribution of first-day close price, frozen at a fixed timestamp T0 (for example, at pricing or 5 minutes before the open), never later.
  - Rule A (value): buy at the open if Open < Median(F), or Open < E[F] − k·IQR.
  - Rule B (limit ladder): place limits at Q_{0.25}(F) and Q_{0.10}(F) for the session and cancel at the close.
  - Exit: at the close (matches the resolution horizon), or at day N.
- **Fill model:** P(fill at limit ℓ) = P(intraday low ≤ ℓ). Estimate it with a model of low-vs-close:
  - For a Brownian path with daily vol σ_d, P(min over the day ≤ ℓ) ≈ 2·Φ(ln(ℓ/O)/σ_d) for ℓ<O (reflection principle, zero drift).
  - IPO day-one vol is extreme and skewed, so calibrate σ_d empirically from past IPO first days (open-to-low ratios), not from a formula.
  - With an implied close distribution centered well above the IPO price, low-quantile limits have near-zero fill probability. The Anthropic example fits this: low $92.72 against an implied distribution far above it.
- **Expected value of a limit rule** = P(fill) × E[return | fill]. Backtests that ignore unfilled orders, or that assume fills when the low only touches the limit, overstate both. Require a trade-through (low < ℓ − tick) and assume queue position at the back.
- **Practical alternative to deep limits:** limits at intermediate quantiles relative to the *open*, like Open × (1 − x%). Or a conditional rule: "if price trades below Q_{0.25}(F) after 30 minutes, buy." This keeps fill rates meaningful.
- **Stale distribution risk:** IPO bracket markets keep trading during the session, so the live distribution moves toward the realized price. Using an intraday-updated F to evaluate an entry that uses intraday prices is look-ahead/circular. Freeze F.

### Gaps
- I found no public dataset or study of IPO first-day open/low/close relative to Polymarket implied distributions. This would have to be built from your own snapshots (the repo already snapshots Anthropic, OpenAI, and IPO markets per commit 1b4d08d).

---

## Q4. (c) Combining odds changes with asset prices; (d) Kelly sizing with calibration error

### Takeaway
Standard cross-asset designs are: event studies around odds jumps (local projections with HC3 or Newey-West errors), odds levels as regime or conditioning features, and hedging binary event risk with contracts. For sizing, Kelly with a PM-derived p must be shrunk. PM probabilities have a documented favorite-longshot bias, and your own edge estimate is noisy. Practitioners use 1/4 to 1/2 Kelly, and there is no rigorous formula for the exact fraction.

### Cited Findings
- **Event-study template:** r(t+h) = α + β·ΔPM(t) + ε on shock hours, h=1..6, HC3 errors (Jordà local projections). Add a distributed-lag model with Newey-West (5 lags) and walk-forward ML — [flyingduck0](https://flyingduck0.github.io/ML_Seminar_Project/)
- **Not every odds jump is persistent:** the debate jump reversed, while the assassination-attempt repricing persisted — [arXiv 2603.03152 summary](https://papers.mewayz.com/paper/arxiv_2603.03152)
- **Calibration evidence:**
  - Favorite-longshot bias on Kalshi: cheap contracts win less often than priced, and expensive ones slightly more. Prices become more accurate near close. Uses over 300k contracts — [Bürgi, Deng, Whelan (GWU WP 2026-001)](https://www2.gwu.edu/~forcpgm/2026-001.pdf); [CESifo WP 12122](https://www.ifo.de/DocDL/cesifo1_wp12122.pdf)
  - The average after-fee return figures differ by version: about −22% (UCD July 2025) against about −20% pre-fee (secondary summary) — [UCD WP2025_19](https://www.ucd.ie/economics/t4media/WP2025_19.pdf)
  - arXiv 2602.19520 covers 292M trades across 327k binary contracts on two exchanges. It decomposes calibration into components and finds a Kalshi political-market effect that does not replicate on Polymarket — [arXiv 2602.19520](https://arxiv.org/html/2602.19520v1)
  - One secondary summary says Fed and rate markets show no detectable longshot bias in a 2,668-contract macro study. It is unverified — [pm.wiki calibration](https://pm.wiki/es/data/glossary/calibration)
- **Kelly theory:** Beygelzimer, Langford, and Pennock give a confidence-based justification for fractional Kelly in prediction markets — [arXiv 1201.6655](https://pdf.arxiv.org/pdf/1201.6655)
- **Practitioner rules for Kelly:**
  - Use 1/4–1/2 Kelly. Go above half Kelly only after 50+ resolved trades with verified calibration.
  - The "half Kelly keeps about 75% of growth" claim comes from a single simulation.
  - Kelly assumes independent bets, but PM events are often correlated.
  - [NexusFi](https://nexusfi.com/a/prediction-markets/position-sizing-binary-markets); [LessWrong: never go full Kelly](https://www.lesswrong.com/posts/TNWnK9g2EeRnQA8Dg/never-go-full-kelly)

### Inferences
- **Kelly for a binary contract** bought at price c (paying 1) with your probability p: f* = (p − c)/(1 − c). For selling (buying NO): f* = (c − p)/c. Subtract fees from the edge first.
- **Kelly for an equity trade sized from an implied distribution:** f* ≈ μ/σ² (continuous approximation). Here μ = E_F[ln(X/entry)] and σ² = Var_F[ln X] from the implied distribution. The risk-neutral vs physical gap is unknown, so shrink.
- **Calibration error:**
  - Replace p with a calibrated p̃ = g(p), where g comes from a reliability curve (isotonic or Platt) fit on resolved markets of the same category. Then shrink toward the market price: p_used = c + λ(p̃ − c), with λ in [0,1].
  - If edge uncertainty has standard deviation s_e around an estimated edge e, the growth-optimal fraction scales roughly by e²/(e² + s_e²). This is a Bayesian shrinkage heuristic.
  - With a handful of events, s_e ≥ e, which implies ≤ 1/2 Kelly and often much less.
- **Hedging event risk:**
  - Hedge ratio h = ΔV_asset(event) / ΔV_contract = (V_yes − V_no) / 1 per contract.
  - Here V_yes and V_no are the scenario values of the equity position, estimated from past analogous events.
  - Basis risk is large: resolution wording differs from the economic event, and liquidity is shallow.

### Gaps
- I found no peer-reviewed formula that maps measured PM calibration error to an optimal Kelly fraction.
- I found no category-specific calibration curve for IPO bracket markets. They are too new and too few.

---

## Q5. (e) Data availability and engineering

### Takeaway
Polymarket price history is a resampled price series with undocumented window caps (about 15 days per startTs/endTs request reported, and `interval=max` returns empty on some resolved markets). Trades are capped at an offset of 10k. The only complete record is on-chain fills. Kalshi has a cleaner split into live and historical endpoints, separated by moving cutoffs (trades cutoff about 2026-09-03 as of Nov 2). Both venues need explicit handling of closed/archived markets to avoid survivorship bias. **The cheapest reliable dataset for a new strategy is your own forward snapshot of order books.**

### Cited Findings
- **Polymarket CLOB `GET /prices-history`** — [official timeseries doc](https://docs.polymarket.com/developers/CLOB/timeseries.md); [API reference](https://docs.polymarket.com/api-reference/pricing/get-price-history-for-a-traded-token)
  - `market` is the token (asset) id. `startTs` and `endTs` are optional.
  - `interval` enum: max, all, 1m, 1w, 1d, 6h, 1h.
  - `fidelity`: "Accuracy of the data expressed in minutes. Default is 1 minute."
  - Response: `history: [{t, p}]`, so price only, with no size.
  - The doc does **not** state the maximum window or the fidelity bounds.
- Dwellir's write-up adds four practical limits — [Dwellir](https://www.dwellir.com/blog/polymarket-historical-data):
  - startTs/endTs windows are "15 days or less."
  - On a resolved market, `interval=max` returned nothing at fidelity=60, and fidelity=720 gave 12-hour points.
  - The series is not a trade record: 1-minute closes differed from the on-chain tape by a median of $0.055 in a fast BTC market.
  - Data API `/trades` errors past offset 10,000 and lists each trade per side, which double-counts volume.
- A GitHub issue reports that `interval=max` returns an empty history — [py-clob-client #216](https://github.com/Polymarket/py-clob-client/issues/216)
- **Community docs conflict on fidelity limits:** a CLI guide says the cap is 5000 points, and an MCP wrapper says 1–500. Neither is official — [Mintlify CLI](https://www.mintlify.com/stat-guy/polymarket/commands/clob); [Glama MCP](https://glama.ai/mcp/servers/PaulieB14/graph-polymarket-mcp/tools/get_price_history)
- **On the user's "14-day window" figure:** I found no official source. Dwellir says ≤15 days, and the official doc is silent. Chunking requests at ≤14 days is a safe choice.
- **Gamma `/markets`:** closed markets appear only with `closed=true` — [Dwellir](https://www.dwellir.com/blog/polymarket-historical-data)
- **On-chain fills (the complete record)** — [Dwellir](https://www.dwellir.com/blog/polymarket-historical-data)
  - Exchange versions: V1 fills run to block 86,126,998 (2026-04-28 11:00 UTC) and V2 starts at block 86,100,351 (2026-04-27 20:12 UTC). They overlap by about 15 hours, so query both.
  - Each trade emits two OrderFilled events; count maker legs. The token id is not indexed, so filter client-side.
  - Volume is about 2.9M fills per day. AMM-era markets are not covered.
  - Alternatives: the subgraph, Dune decoded tables, and scrapers.
- **Kalshi historical split** — [Kalshi docs](https://docs.kalshi.com/getting_started/historical_data); [cutoff endpoint](https://docs.kalshi.com/api-reference/historical/get-historical-cutoff-timestamps)
  - `GET /historical/cutoff` returns four cutoffs: `market_settled_ts`, `trades_created_ts`, `orders_updated_ts`, and `market_positions_last_updated_ts`. They advance over time.
  - Historical endpoints: `/historical/markets`, `/historical/markets/{ticker}`, `/historical/markets/{ticker}/candlesticks`, `/historical/trades`, `/historical/fills`, `/historical/orders`, and `/historical/positions`.
  - Events and series stay on their original endpoints. Resting orders and unsettled positions stay live.
  - There is no historical endpoint with settlement-record fields.
- On Nov 2, 2026, `/historical/cutoff` returned `trades_created_ts: 2026-09-03`. Kalshi candlesticks come at 1-minute, 1-hour, and 1-day periods, and public market data needs no key — [Dwellir](https://www.dwellir.com/blog/polymarket-historical-data)
- **Survivorship:** the Orrery backtests use only currently live markets — [Orrery](https://www.orrery.me/backtest)

### Inferences
- **Timestamp alignment:** PM data is 24/7 UTC epoch seconds, while equities trade 09:30–16:00 America/New_York with DST. Use the following procedure:
  - Convert everything to UTC, then map each PM observation to an exchange session with a calendar library (e.g. `pandas_market_calendars`/`exchange_calendars`).
  - Define features "as of" a strict cutoff: the last PM price at or before T0, with `merge_asof(direction="backward")`.
  - The prices-history `p` is a sampled/last price, so it can be stale in illiquid markets. Store the time since the last trade and the bid/ask, and filter out stale points.
- **Point-in-time snapshots:** Polymarket price history has no book depth, and bracket markets get added mid-life as new brackets are listed. A historical reconstruction can sum to well under or over 1 if you miss brackets added later. Snapshot all brackets of an event, together with bid/ask/size, on a schedule. The repo's monitor and snapshot jobs are the right asset, and the GitHub cron reliability issue noted in commit fc74a90 matters here.
- **Resolution rules to store with each event:** metric (close cap vs open), share-count source, tie-to-higher-bracket rule, deadline and "no IPO" branch, and resolution source. Store them as text at snapshot time, because rules can be clarified later.
- **Survivorship:** enumerate events with `closed=true` (Gamma) and the Kalshi historical markets endpoint, not just live listings. Include markets that resolved "no IPO" or were cancelled.

### Gaps
- Official Polymarket max-window and fidelity bounds are undocumented. Verify empirically and log the API's behavior.
- I found no stated Kalshi API rate limits on the historical-data page.

---

## Q6. How many comparable events exist, and is there enough statistical power? Best practice for a forward (paper) test

### Takeaway
The sample is too small for an IPO-specific backtest:
- Polymarket "IPO closing market cap" bracket markets exist for perhaps a few dozen 2026 listings (Kraken, Oura, ITG, Lime, Bending Spoons, Deep Fission, Anthropic, SpaceX/OpenAI conditional, ...), many with thin books.
- Fed meetings give 8 per year.
- Macro releases give about 12 per type per year.

Detecting a realistic first-day edge at conventional power needs hundreds of events. Treat any IPO rule as a pre-registered forward test with a small, fixed risk budget and Bayesian updating, not as a backtested strategy.

### Cited Findings
- Polymarket IPO closing-market-cap markets seen in search include ITG, Lime, Bending Spoons (pages say resolved Jul 1, 2026, unverified), Deep Fission, Kraken (above-$26B variant), Oura, Anthropic, OpenAI, and SpaceX (conditional on an IPO before 2028) — [lines.com ITG](https://www.lines.com/prediction-markets/business/itg-ipo-closing-market-cap-20260625034819511); [lines.com Lime](https://www.lines.com/prediction-markets/business/lime-ipo-closing-market-cap-20260625030421630); [lines.com Bending Spoons](https://www.lines.com/prediction-markets/business/bending-spoons-ipo-closing-market-cap-20260625032229784); [Deep Fission](https://www.lines.com/prediction-markets/finance/deep-fission-ipo-closing-market-cap); [Orrery Kraken](https://orrery.me/markets/kraken-ipo-closing-market-cap-above-26b); [struct Oura](https://explorer.struct.to/events/oura-ipo-closing-market-cap); [SpaceX](https://www.lines.com/prediction-markets/finance/spacex-ipo-closing-market-cap)
- The careful macro event study had only 9–13 events per type over 13 months and called its results directional — [flyingduck0](https://flyingduck0.github.io/ML_Seminar_Project/)
- Practitioner advice: verify calibration over 50+ resolved trades before going above half Kelly — [NexusFi](https://nexusfi.com/a/prediction-markets/position-sizing-binary-markets)

### Inferences
- **Power arithmetic:** IPO first-day returns have a cross-sectional standard deviation of tens of percent. Take σ ≈ 30% as a rough assumption (not sourced here). To detect a 5% mean edge at α=0.05 with 80% power, n ≈ (2.8·σ/δ)² ≈ (2.8·6)² ≈ 280 events. Even a 10% edge needs about 70. A few dozen IPO bracket markets, a fraction of them liquid, is underpowered by roughly 5–10×.
- **Where n is larger:**
  - Kalshi/Polymarket FOMC markets: 8 per year, but history exists since about 2021–22, so roughly 30–40 meetings.
  - CPI and NFP markets: about 12 per year each.
  - Pooling across event types with a common rule ("trade when price is below the implied median") raises n, but it assumes homogeneity.
  - None of these alone reaches about 280.
- **Forward test protocol** (consistent with the repo's frozen-model and change-control practice):
  1. Pre-register the rule, the distribution-construction recipe (normalization, tail model, freeze time T0), entry and exit, and fill assumptions in a dated, committed file before each event.
  2. For each event, log the frozen implied distribution, the realized open, low, high and close, would-be fills, and the PnL net of costs.
  3. Score the forecast itself with proper scoring rules:
     - log score or CRPS of the realized close against the implied distribution;
     - PIT histogram of the realized-close quantile within F, which should be uniform if calibrated.
     These accumulate evidence faster than PnL.
  4. Use sequential or Bayesian evaluation: a posterior on mean edge with a skeptical prior centered at 0, or a sequential probability ratio test. Avoid repeated naive t-tests.
  5. Keep the size small and fixed (for example, ≤1/4 Kelly against a shrunk edge) until the PIT/CRPS evidence and n≥30–50 justify more.
  6. Keep a log of rule changes. Any change resets the evaluation sample.
- **Costs to include:**
  - Equity side: IPO-day spreads and slippage, which are wide in the first minutes.
  - PM side, if hedging or trading the contracts: taker fees and spread. Takers lose much more than makers on Kalshi.
  - Opportunity cost of capital reserved for unfilled limits.

### Gaps
- I found no authoritative count of resolved Polymarket and Kalshi IPO bracket markets with liquidity statistics. This should be enumerated via Gamma `closed=true` with a search on "IPO", which I did not do here.
- I found no sourced cross-sectional standard deviation of 2026 IPO first-day returns. The 30% figure above is an assumption to replace with real data.
