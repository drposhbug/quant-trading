# Option Pricing Math, Volatility, VRP and Earnings for US Mega-Cap Tech Options

Scope: TSLA, NVDA, AAPL, MSFT, GOOGL, AMZN, META, AVGO, TSM, AMD, ORCL. Researched 2026-11-18.
Notation: S = spot, K = strike, T = years to expiry, r = continuously compounded risk-free rate, q = continuous dividend yield, sigma = volatility, N() = standard normal CDF, n() = standard normal PDF, n(x) = exp(-x^2/2)/sqrt(2*pi).

Note on sources: the formulas in Q1 are standard textbook results (Hull, *Options, Futures and Other Derivatives*, chs. on BSM and Greeks; Natenberg, *Option Volatility and Pricing*). I did not fetch the textbooks. Every number in the worked example was computed in this session with a short script, and put-call parity checked out to 1e-6. Online references for the formulas are linked where available.

---

## Q1. Exact formulas (BSM, American adjustments, parity, Greeks) and a worked 30-day ATM NVDA example

### Takeaway
Use BSM with a continuous dividend yield (Merton 1973) as the quoting and Greeks engine. For these names it is nearly exact for calls, because dividends are tiny or zero (TSLA, AMD and AMZN pay none; NVDA's yield is about 0.02%). Listed single-stock options are American, so early exercise matters mainly for deep-ITM puts, and for calls only just before an ex-dividend date. For a 30-day ATM option, price ≈ 0.4·S·σ·√T, and the straddle ≈ 0.8·S·σ·√T, which is the market's "expected move".

### Cited Findings

**Black-Scholes-Merton with continuous dividend yield q** — [Wikipedia: Black–Scholes model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model); Hull (textbook)
- d1 = [ln(S/K) + (r − q + σ²/2)·T] / (σ√T),  d2 = d1 − σ√T
- Call C = S·e^(−qT)·N(d1) − K·e^(−rT)·N(d2)
- Put  P = K·e^(−rT)·N(−d2) − S·e^(−qT)·N(−d1)
- The PDE every European claim V satisfies: ∂V/∂t + ½σ²S²·∂²V/∂S² + (r − q)·S·∂V/∂S − rV = 0. In Greek form: Θ + ½σ²S²Γ + (r − q)SΔ − rV = 0.
- With discrete dividends, the escrowed-dividend approach is common: replace S by S − PV(dividends before expiry).

**Put-call parity** — [Wikipedia: Put–call parity](https://en.wikipedia.org/wiki/Put%E2%80%93call_parity); Hull
- European: C − P = S·e^(−qT) − K·e^(−rT). With discrete dividends: C − P = S − PV(D) − K·e^(−rT).
- American options give only bounds. With no dividends: S − K ≤ C − P ≤ S − K·e^(−rT). With dividends: S − PV(D) − K ≤ C − P ≤ S − K·e^(−rT) (Hull).
- Practical use: back out the implied forward and the implied borrow from call and put mids. Parity violations in hard-to-borrow names are a borrow-fee signal, not free money. TSLA has historically been the most relevant name here.

**Why American equity options differ** — Hull; [Wikipedia: Black–Scholes model, American options](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model)
- Calls on a non-dividend stock: early exercise is never optimal, so American value = European value. This applies to TSLA, AMD and AMZN, which pay no dividend.
- Calls on dividend payers: early exercise can be optimal only just before an ex-date, and only if the dividend D > K·(1 − e^(−r·τ)), where τ is the time from the ex-date to expiry. Equivalently, exercise when the extrinsic value of the call is less than the dividend. For AAPL, MSFT, AVGO, ORCL, META, GOOGL and TSM, quarterly dividends are small relative to price. The early-exercise premium therefore matters only for deep-ITM calls into ex-dates, which is the "dividend play" pin risk for short calls.
- Puts: early exercise can be optimal whenever the put is deep enough ITM that the interest earned on K exceeds the remaining time value. So American puts are worth more than European puts, and the gap grows with r. With r ≈ 4% in 2024–26, this premium is non-trivial for deep-ITM puts.
- Pricing: use binomial or trinomial trees (CRR), finite differences, or the Barone-Adesi–Whaley / Bjerksund–Stensland approximations. OptionMetrics IvyDB computes American IVs with a binomial tree, so academic IV numbers are already early-exercise adjusted.

**The Greeks (European BSM, with yield q)** — [Wikipedia: Greeks (finance)](https://en.wikipedia.org/wiki/Greeks_(finance)); Hull; Natenberg

| Greek | Call | Put | Practical reading |
|---|---|---|---|
| Delta Δ | e^(−qT)·N(d1) | e^(−qT)·(N(d1) − 1) | Hedge ratio in shares. Rough proxy for the probability of finishing ITM (N(d2) is the risk-neutral one). |
| Gamma Γ | e^(−qT)·n(d1) / (S·σ·√T) | same | Change in delta per $1 move. Peaks ATM and explodes as T → 0. |
| Vega ν | S·e^(−qT)·n(d1)·√T | same | $ per 1.00 of vol (divide by 100 for per vol point). Largest ATM and long-dated. |
| Theta Θ (per year) | −S·e^(−qT)·n(d1)·σ/(2√T) − r·K·e^(−rT)·N(d2) + q·S·e^(−qT)·N(d1) | −S·e^(−qT)·n(d1)·σ/(2√T) + r·K·e^(−rT)·N(−d2) − q·S·e^(−qT)·N(−d1) | Divide by 365 (calendar) or 252 (trading) for per-day theta. Note the convention you use. |
| Rho ρ | K·T·e^(−rT)·N(d2) | −K·T·e^(−rT)·N(−d2) | $ per 1.00 change in r. Small for short-dated options. |

Second-order Greeks that matter for skew trading:
- Vanna = ∂Δ/∂σ = −e^(−qT)·n(d1)·d2/σ
- Volga (vomma) = ν·d1·d2/σ

**Gamma-theta identity and the P&L of a delta-hedged option** — follows from the BSM PDE (Hull; Sinclair, *Volatility Trading*)
- With r = q = 0: Θ = −½·Γ·S²·σ_imp². Theta is the rent paid for gamma.
- Discrete delta-hedged P&L of a long option over dt ≈ ½·Γ·S²·[(ΔS/S)² − σ_imp²·dt]. Integrated over the life: P&L = ½ ∫ Γ_t·S_t²·(σ_realized,t² − σ_imp²) dt. The P&L is path dependent because it is weighted by dollar gamma, so where the stock realizes its volatility matters, not just how much.
- Daily breakeven move for a delta-hedged option ≈ σ_imp/√365 per calendar day (σ_imp/√252 per trading day).

**Worked example: 30-day ATM NVDA (computed in this session)**
- Inputs (illustrative, not live quotes): S = K = $180, σ = 45%, r = 4.0%, q = 0 (NVDA's ~0.02% yield is negligible), T = 30/365 = 0.08219.
- d1 = 0.08999, d2 = −0.03902.
- Call = $9.541, Put = $8.950, Straddle = $18.49 (10.27% of spot). Parity residual = 0.000000.
- Rule-of-thumb check: 0.4·S·σ·√T = $9.29 per leg, and 0.8·σ·√T = 10.32% for the straddle.
- Δ_call = 0.536, Δ_put = −0.464.
- Γ = 0.01711 per $1.
- Vega = $0.205 per vol point per share ($20.50 per contract).
- Θ_call = −$0.163 per calendar day, Θ_put = −$0.144 per day.
- ρ_call = +$0.071, ρ_put = −$0.076 per 1% change in rates.
- Gamma-theta check: ½·Γ·S²·σ²/365 = $0.154 per day. This equals the volatility part of the theta; the rest (≈ $0.01) is the carry term.
- Breakeven daily move: S·σ/√365 = $4.24, or 2.36%. The hedged call makes money on days NVDA moves by more than about ±2.4%.
- Short-dated scaling (same S and σ, ATM): Γ = 0.0356 with Θ = −$0.32/day at 7 DTE; Γ = 0.094 with Θ = −$0.85/day at 1 DTE. Gamma and theta both scale as 1/√T, so the gamma-theta tradeoff stays fixed per unit of σ², but dollar swings per day grow fast. This is why 0–7 DTE options turn small differences between realized and implied volatility into large P&L variance.

**The straddle as the implied move**
- If the move X ~ N(0, s²), then E|X| = s·√(2/π) ≈ 0.798·s. An ATM straddle ≈ 0.8·σ·√T·S is therefore the market's expected absolute move, not its standard deviation (which is about 1.25× the straddle). (Standard result; follows from the formulas above.)

### Inferences
- For these names, the BSM-with-q engine plus a tree for deep-ITM puts and ex-dividend calls is sufficient. The model is not where the errors come from; the vol input (skew, term structure, earnings jump) is.
- Theta is quoted inconsistently (365 vs 252 days, and brokers vary). Any backtest that compares theta collected to realized moves must use one day-count convention throughout.

### Gaps
- I did not fetch Hull or Natenberg directly. The formulas are standard and were numerically verified (parity holds exactly, and the gamma-theta identity reconciles), but page citations are not given.

---

## Q2. Implied vs realized vol, skew/smile, term structure, and the variance risk premium (single-stock vs index; does it survive costs?)

### Takeaway
The variance risk premium (VRP: implied variance above subsequently realized variance) is large and highly significant for indexes. For individual stocks, including mega-cap tech, it is much smaller and often statistically insignificant. Much of the index premium is a price of correlation risk, not of single-stock variance risk. Single-stock VRP strategies look profitable before costs but are largely eroded by option bid-ask spreads, unless execution is patient or timed.

### Cited Findings

**Carr & Wu, "Variance Risk Premiums"** — RFS 2009; numbers below are from the 2004 working-paper version ([NYU PDF](https://engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf); [RePEc listing, RFS 22(3):1311–1341](https://econpapers.repec.org/RePEc:oup:rfinst:v:22:y:2009:i:3:p:1311-1341)). OLDER FINDING, sample Jan 1996–Feb 2003.
- Method: the variance swap rate (the risk-neutral expected variance) is replicated by a strip of OTM options. Model-free form: SW ≈ (2/T)·Σ (ΔK_i/K_i²)·e^(rT)·O(K_i), where O(K_i) is the OTM option price at strike K_i. The VRP is RV − SW, and the log VRP is ln(RV/SW), which is the excess return on a long variance swap.
- Sample: 5 indexes and 35 of the most actively traded stocks.
- Mean log VRP and t-statistics (Table 5):

| Underlying | Mean log VRP | t-stat |
|---|---|---|
| SPX | −0.594 | −9.5 |
| NDX | −0.207 | −4.4 |
| MSFT | −0.277 | −5.9 |
| AMZN | −0.151 | −2.0 |
| ORCL | −0.081 | −1.7 |
| INTC | −0.024 | −0.5 |

- Index premium: excess return on long variance swaps is over −50% per month for the S&P 500 and the Dow.
- Single stocks: the mean log VRP is significantly negative for 21 of the 35 stocks. The mean VRP in variance units is insignificant for all but 3 of the 35.
- Interpretation: the authors conjecture the market prices mainly the market (systematic) component of variance risk, not each stock's own variance. However, the CAPM "variance beta" leaves large negative intercepts, so other factors are needed.
- Average levels (Table 4, in vol units): MSFT realized 38.3% vs swap 42.7%; AMZN realized 62.1% vs swap 65.6%; SPX realized 18.8% vs swap 24.4%.

**Driessen, Maenhout & Vilkov, "The Price of Correlation Risk"** — JF 2009, 64(3):1377–1406 ([RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:64:y:2009:i:3:p:1377-1406); [Tilburg repository](https://repository.tilburguniversity.edu/items/3f5ec1dc-a815-49fd-8575-e951fa6ed057); [Netspar WP](https://www.netspar.nl/wp-content/uploads/061_Driessen.pdf)). OLDER FINDING.
- Uses S&P 100 index options and options on its components. Correlation risk is priced, and correlation exposure explains the cross-section of index vs individual option returns.
- Index options are expensive because they hedge correlation spikes. Individual variance risk is not priced on average, so the index VRP is mostly a correlation risk premium.
- A strategy that sells index variance and buys component variance (a dispersion trade) has a high alpha for a frictionless CRRA investor. Realistic frictions, especially individual-option bid-ask spreads, largely eliminate it.

**Bakshi & Kapadia (2003)** — "Delta-Hedged Gains and the Negative Market Volatility Risk Premium", RFS 16(2):527–566 ([IDEAS](https://ideas.repec.org/a/oup/rfinst/v16y2003i2p527-566.html)). OLDER FINDING.
- Delta-hedged S&P 500 options lose money on average, which is evidence of a negative market volatility risk premium. Losses are larger when volatility is higher and smaller away from the money.
- Their companion paper on individual equity options ("Volatility Risk Premiums Embedded in Individual Equity Options", J. Derivatives 2003) reports smaller delta-hedged losses for individual stocks than for the index. I could not retrieve its abstract or numbers here; treat this as an unverified summary (see Gaps).

**Goyal & Saretto (2009)** — "Cross-Section of Option Returns and Volatility", JFE 94(2):310–326 ([RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:94:y:2009:i:2:p:310-326); [working paper PDF](https://www.cis.upenn.edu/~mkearns/finread/CrossOptions.pdf)). OLDER FINDING.
- Sorts stocks on (historical realized vol − ATM implied vol). Long straddles or delta-hedged options where HV ≫ IV, short where IV ≫ HV, earn large returns.
- Transaction costs reduce profitability. Delta-hedged versions are less hurt. I did not obtain the net-of-cost figures.

**Cao & Han (2013)** — "Cross Section of Option Returns and Idiosyncratic Stock Volatility", JFE 108(1):231–249 ([RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:108:y:2013:i:1:p:231-249); [OptionMetrics summary](https://optionmetrics.com/research/j-cao-and-b-han-cross-section-of-option-returns-and-idiosyncratic-stock-volatility/)).
- Delta-hedged equity option returns are negative on average and decrease with idiosyncratic volatility. They interpret this as dealers charging more on high-IVOL names because of arbitrage costs.
- Limits-to-arbitrage controls cut the relation by about 40%.

**Bollerslev, Tauchen & Zhou (2009)** — RFS 22(11):4463–4492 ([RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:22:y:2009:i:11:p:4463-4492)).
- The index VRP (model-free implied variance minus realized variance) predicts aggregate market returns. This is an index-level result only.

**Trading costs**
- Muravyev & Pearson, "Options Trading Costs Are Lower than You Think", RFS 2020, 33(11):4973–5014 ([IDEAS](https://ideas.repec.org/a/oup/rfinst/v33y2020i11p4973-5014..html); [CXO summary](https://www.cxoadvisory.com/equity-options/timing-option-trades-to-suppress-trading-frictions/)).
  - Effective spreads for traders who time executions are less than 40% of conventional measures. The average effective spread is about 1/4 smaller than conventional estimates.
  - The average quoted spread on S&P 500 stock options is cited as up to 17.2% (relative to option price).
  - Non-timing traders still pay roughly the full conventional half-spread.

**Skew, smile and term structure**
- Equity skew means OTM put IV > ATM IV > OTM call IV, reflecting the negative spot-vol correlation and crash or jump risk. (Standard; see the Carr & Wu discussion of the leverage effect in the [NYU PDF](https://engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf).)
- Term structure: normally upward sloping in calm regimes and inverted in stress. Single-stock term structure is dominated by scheduled earnings, which add a variance "lump" to every expiry that spans the event (see Q3). DJKS note that this makes single-stock term structures negatively sloped into an event ([DJKS NYU 2017 slides](https://www.stern.nyu.edu/sites/default/files/assets/documents/NYU%20conference%20Johannes%20final.pdf)).

### Inferences
- For mega-cap tech, expect a single-stock VRP that is positive (implied > realized) but much thinner than the index VRP. In Carr-Wu, MSFT's log VRP was about half of SPX's and AMZN's about a quarter, with low statistical power. A plain "sell single-stock vol" book mostly harvests the systematic part of the premium, with worse liquidity than SPX.
- The DMV result implies that if the goal is harvesting VRP, selling index variance (SPX, or NDX/QQQ for a tech tilt) captures more premium per unit of cost. Selling single-name variance is closer to zero-premium, with jump risk added.
- Costs decide the outcome. With quoted spreads of 5–17% of option value on single names, a 30-day straddle that is 10% of spot can lose most of a 1–3 vol-point edge to the spread unless orders are worked near mid. Muravyev-Pearson suggests patient execution recovers much of this.
- Evidence vintage: almost all core VRP evidence uses data from 1996 to the mid-2010s. Post-2020 regimes (retail call buying, 0DTE growth, the AI-driven vol in NVDA, AMD and AVGO) are not covered by the peer-reviewed work found.

### Gaps
- No peer-reviewed 2023–2026 estimate of single-stock VRP specifically for the 11 mega-caps was found. Re-estimate from OptionMetrics or ORATS data (IV30 vs subsequent RV30, excluding and including earnings windows) before relying on a number.
- Bakshi-Kapadia individual-equity paper: magnitudes not retrieved.
- Goyal-Saretto net-of-cost returns: not retrieved.

---

## Q3. Earnings: pricing in the term structure, implied move extraction, IV crush, and is the earnings straddle overpriced for mega-caps?

### Takeaway
The earnings jump can be backed out of the IV term structure with a simple variance-additivity formula (Dubinsky-Johannes-Kaeck-Seeger). For the 50 most option-active firms, a mega-cap-heavy sample, implied earnings vol consistently exceeds realized, and straddles held over announcements lose about 8% per event. Gao-Xing-Zhang find the opposite (pre-announcement straddles earn +3.34%), but the effect is concentrated in small, illiquid, high-kurtosis firms. Retail demand bids up announcement options (de Silva-Smith-So). Recent vendor data shows the premium is regime dependent: early-2026 earnings seasons saw realized moves exceed implied.

### Cited Findings

**Model and extraction formulas (DJKS)**
- Sources: Dubinsky, Johannes, Kaeck & Seeger, "Option Pricing of Earnings Announcement Risks", RFS 2019, 32(2):646–687 ([IDEAS](https://ideas.repec.org/a/oup/rfinst/v32y2019i2p646-687..html)); [NYU Stern 2017 conference slides](https://www.stern.nyu.edu/sites/default/files/assets/documents/NYU%20conference%20Johannes%20final.pdf).
- Model: log-price follows diffusion plus deterministic-date jumps. At each earnings date, return jump J ~ N(μ, σ_Q²). Arrival times are known.
- Annualized IV for an expiry T (in years) spanning one event: σ_T²·T = σ_d²·T + σ_Q². So σ_T² = σ_d² + σ_Q²/T, where σ_d is the diffusive (ex-event) vol.
- Term-structure estimator, using two expiries T1 < T2 that both include the event: σ_Q² = (σ_1² − σ_2²) / (1/T1 − 1/T2).
  - Check from the slides: GBP/USD 1-month IV 28.21%, 2-month IV 21.51% → σ_Q = 7.5%. I recomputed this in this session as 7.45%. Spot fell 10% the next day.
- Implied diffusive vol: σ_d² = σ_1² − σ_Q²/T1.
- Time-series estimator: compare IV just before vs just after the announcement, σ_Q² = (σ_pre² − σ_post²)·T. The paper argues the term-structure estimator is more robust and less noisy; the two correlate at 93% across firms.
- Implications:
  - IV rises into the event (σ_Q²/T grows as T shrinks).
  - IV drops discontinuously afterwards. This is IV crush: the σ_Q²/T term vanishes.
  - Term structure slopes down across expiries that include the event.
- Worked example (computed here, illustrative): 7-day IV 90%, 35-day IV 55%, both spanning the earnings date → σ_Q = 11.0% one-day move standard deviation, expected absolute move ≈ 0.798 × 11.0% = 8.8%, implied diffusive vol ≈ 41.9%. After the event, front IV would fall from 90% toward about 42%. That fall is the crush.
- Straddle-implied move (practitioner version): implied move ≈ front-expiry ATM straddle / S, which is E|move| over the whole expiry, including non-event days. A cleaner version is σ_Q·√(2/π) from the term-structure estimator.

**DJKS empirical results** — [NYU slides](https://www.stern.nyu.edu/sites/default/files/assets/documents/NYU%20conference%20Johannes%20final.pdf); [IDEAS abstract](https://ideas.repec.org/a/oup/rfinst/v32y2019i2p646-687..html). OLDER FINDING, data roughly 2000–2015.
- Sample: OptionMetrics data from 2000 onward, the 50 most option-active firms each year. This includes the large-cap tech names (Apple, Google, Intel, Netflix are mentioned).
- About 20% of Google's total volatility occurs in the 4 days after earnings.
- Apple's earnings-jump vol has a time-series standard deviation of about 3%.
- Option-implied earnings vol is highly informative: 85% cross-sectional correlation with future realized earnings-day volatility.
- There is uniform evidence that implied earnings jump vol exceeds subsequent realized vol (Q-vol > P-vol). Standardized returns average less than 1.
- Announcement straddle returns are about −8% per earnings announcement and highly significant.
- Adding earnings jumps to SV models cuts pricing errors by 15–20% overall, which matters more than random jumps.

**Gao, Xing & Zhang, "Anticipating Uncertainty: Straddles around Earnings Announcements"** — JFQA 2018, 53(6):2587–2617 ([RePEc](https://econpapers.repec.org/RePEc:cup:jfinqa:v:53:y:2018:i:06:p:2587-2617_00); [Cambridge](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/anticipating-uncertainty-straddles-around-earnings-announcements/7B34877AD5E06304BA3C55FBA3219FDD)). OLDER FINDING.
- ATM straddles bought 3 days before and held to the announcement earn a highly significant +3.34%, whereas straddles normally lose.
- The effect is stronger in smaller firms and firms with higher volatility, higher kurtosis, more volatile past earnings surprises, and lower volume or higher transaction costs.
- Practitioner summaries note that bid-ask spreads widen around announcements and returns fall after costs ([BSIC](https://bsic.it/straddling-outside-and-into-earnings/); [Alpha Architect](https://alphaarchitect.com/2013/02/straddle-earnings-announcements-and-win/)).
- This contradicts DJKS's −8% per announcement. Different universes (all optionable firms vs the top-50 most active) and different holding windows likely explain the gap.

**de Silva, Smith & So, "Losing is Optional: Retail Option Trading and Expected Announcement Volatility"** — Review of Finance 2025 ([Stanford GSB](https://www.gsb.stanford.edu/faculty-research/publications/losing-optional-retail-option-trading-expected-announcement); [MIT Sloan summary](https://mitsloan.mit.edu/ideas-made-to-matter/retail-investors-lose-big-options-markets-research-shows)).
- Retail investors buy options ahead of high expected-announcement-volatility events, bid up prices, pay wide spreads, and are slow to exit after the event.
- Retail losses average 5–9% around announcements, and 10–14% for high-EAV announcements. Market makers take the other side.

**Recent and practitioner evidence (lower quality, flagged)**
- ORATS (vendor blog, 2026-02-12): straddles on reporting U.S. companies returned about +45% on average over the four weeks to 2026-02-11, vs a trailing 12-quarter average of about −2%. Actual moves "consistently exceeded" implied in that season, while implied moves had overstated realized moves in prior years. No mega-cap breakdown or sample size was given ([ORATS](https://orats.com/blog/earnings-straddles-strong-season-2026)).
- A widely mirrored 2026 article claims NVDA's implied move exceeded its actual move in 14 of the last 20 quarters (attributed to Cboe LiveVol). It appeared only on spam or mirror domains with no methodology. UNVERIFIED; do not rely on it.

### Inferences
- For mega-caps, the more relevant evidence (DJKS top-50 universe; the de Silva-Smith-So retail-demand channel, which is strongest in high-attention names like NVDA and TSLA) points to a positive earnings variance premium on average. The GXZ positive straddle returns concentrate in small, illiquid names that are not this universe.
- The premium is regime dependent and fat-tailed. A trailing-12-quarter straddle return of about −2% (ORATS), compared with DJKS's −8%, suggests the edge has compressed since the 2000–2015 sample. Single seasons can swing to +45% for long straddles, so short-earnings-vol strategies need tail controls: defined risk (iron flies or condors) or small sizing.
- Use the term-structure estimator, not the raw front straddle, to measure the priced earnings move. Compare σ_Q·√(2/π) against the historical distribution of |earnings-day returns| for that ticker (e.g., trailing 12–20 quarters). This is the comparison the user's `earnings_premium_study.py` should be making.
- IV crush is mechanical, not alpha. Shorting front-month IV into earnings profits only if the realized jump is less than σ_Q. The crush itself is already priced, because the diffusive vol σ_d after the event is roughly forecastable from the back months.

### Gaps
- No peer-reviewed, post-2020 study reporting implied vs realized earnings moves specifically for the 11 mega-caps was found. This must be measured directly.
- The DJKS firm-level table (per-ticker σ_Q and premium) was not accessible. The RFS full text is paywalled.
- The DJKS straddle return definition (exact entry and exit timing, costs) could not be confirmed from the slides.

---

## Q4. Skew: what it implies and does it predict returns (Xing-Zhang-Zhao) in large caps?

### Takeaway
A steep put skew signals informed demand for downside protection. Stocks with the steepest smirks have underperformed those with the flattest by about 10.9% per year in 1996–2005 (Xing-Zhang-Zhao). The effect is pre-cost and older. A January 2026 Illinois study argues that stock borrowing fees explain away option-based return predictors, and its large-cap applicability is untested here.

### Cited Findings
- Xing, Zhang & Zhao, "What Does the Individual Option Volatility Smirk Tell Us About Future Equity Returns?", JFQA 2010, 45(3):641–662 ([Cambridge](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/what-does-the-individual-option-volatility-smirk-tell-us-about-future-equity-returns/ECFD16BA9ACBDC8D577D1BD866FBEA72); [RePEc](https://econpapers.repec.org/RePEc:cup:jfinqa:v:45:y:2010:i:03:p:641-662_00); [CXO summary](https://www.cxoadvisory.com/volatility-effects/smirking-because-they-know-something/)). OLDER FINDING, data 1996–2005.
  - SKEW = IV(OTM put, K/S ≈ 0.80–0.95) − IV(ATM call, K/S ≈ 0.95–1.05). This is the standard XZZ definition; the exact moneyness band was not re-verified from the full text.
  - The steepest-smirk quintile underperforms the flattest by 10.9% per year (working paper). CXO reports about 15% per year risk-adjusted for a weekly-rebalanced long-short, before costs. The figures differ across versions.
  - Predictability persists for at least 6 months and is robust to size, book-to-market, idiosyncratic vol and momentum.
  - The steepest-smirk firms have the worst earnings surprises the next quarter. This is consistent with informed traders using OTM puts and slow stock-market incorporation of the information.
- Counter-evidence (headline only, not read in full): University of Illinois Gies news, Jan 2026, "Study: borrowing fee is the variable that debunks theory that options predict future stock returns" ([Gies](https://giesbusiness.illinois.edu/news/2026/01/07/study--borrowing-fee-is-the-variable-that-debunks-theory-that-options-predict-future-stock-returns)). This suggests option-implied predictors, possibly including skew and parity deviations, proxy for short-sale costs. UNVERIFIED detail.

### Inferences
- In mega-caps, borrow is cheap and informed-trader concentration in the options market is diluted by huge liquidity. Skew predictability is therefore likely weaker than the cross-sectional average. The XZZ long-short spread comes from the whole optionable universe, not large caps.
- For trading, skew is better used as a pricing input than a directional signal. Steep put skew makes put spreads and risk reversals relatively expensive or cheap, and it rises into earnings for some names.
- Mega-cap tech has, at times, shown flat or call-skewed surfaces during momentum or retail call-buying regimes (e.g. TSLA, NVDA). This is not sourced here and is flagged as an observation to verify from data.

### Gaps
- No study was found testing XZZ predictability restricted to mega-caps or post-2010 data. The Illinois 2026 study's authors, venue and numbers were not retrieved.
- The exact XZZ moneyness filters and maturity window were not re-verified from the published text.
