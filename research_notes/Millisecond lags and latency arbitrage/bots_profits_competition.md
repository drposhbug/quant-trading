# Latency-arbitrage bots and lead-lag trading on prediction markets: profits and competition (2024 to Nov 2026)

Source-quality legend: **[ACAD]** academic preprint with stated methodology; **[RESEARCH]** industry research with stated methodology; **[MEDIA]** journalism; **[SELF]** self-reported, vendor, or analyst-on-X claims that are not independently verified. **Survivorship warning:** almost every wallet-profit figure below comes from a winner who was publicised by an X analyst, a bot vendor, or a media outlet repeating them. Nobody publishes the losing bot wallets, so these figures cannot be used to estimate a typical entrant's return.

## Q1. What do on-chain analyses show about top bot wallets on short-dated crypto Up/Down markets (profits, trade counts, win rates)?

### Takeaway
One wallet, 0x8dxd, is well documented as a profitable bot on 15-minute BTC/ETH/SOL Up/Down markets. Its widely quoted record ("$313 to ~$414K–$438K in one month, 98% win rate") comes from an X analyst and was never independently audited. A later tracker snapshot shows about $2.4M realized PnL on about $201M of volume, which is roughly 1.2% of volume. That is a thin margin per dollar traded, not "free money". The rigorous academic work is mostly null or negative for an outside lag trader.

### Cited Findings
- **0x8dxd (CoinDesk, Jan 2026) [MEDIA, relaying on-chain profile]:** the wallet "appears to be using a trading bot to predict crypto prices in 15-minute increments, up over $233K in the past week and $658K overall" — [CoinDesk on X](https://x.com/CoinDesk/status/2010830430207939065); [Phemex recap](https://phemex.com/news/article/polymarket-trader-0x8dxd-gains-658k-using-trading-bot-53003)
- **"$313 to $414K in one month, 98% win rate" [SELF]:** the claim comes from X account Dexter's Lab (Jan 5, 2026), covering BTC/ETH/SOL 15-minute Up/Down markets at $4,000–5,000 per bet. BeInCrypto/Yahoo reported it with no on-chain verification or methodology — [Yahoo/BeInCrypto, Jan 6 2026](https://finance.yahoo.com/news/arbitrage-bots-dominate-polymarket-millions-100000888.html). Finance Magnates embedded the same post and said it had not verified the figure — [Finance Magnates, Jan 7 2026](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/)
- **Variant figures for the same wallet [SELF]:** a Medium post gives $313 (Dec 2025) to about $438,000 by Jan 6, 2026, with a 98% win rate over 6,615 predictions — [Medium](https://medium.com/@weare1010/claude-ai-trading-bots-are-making-hundreds-of-thousands-on-polymarket-2840efb9f2cd). The figures conflict slightly with the $414K and $658K numbers above.
- **Later tracker snapshot [third-party analytics, derived from on-chain data, not re-verified]:** predicts.guru lists 0x8dxd at about +$2.37M realized PnL, about $201M total volume, and 34,810 markets traded, with the latest trade around Aug 24, 2026 (snapshot Nov 2026). The page returned HTTP 429 when fetched directly; these figures come from a search snippet — [predicts.guru](https://www.predicts.guru/checker/0x63ce342161250d705dc0b16df89036c8e5f9ba9a)
- **Other named bots [SELF / promotional tracker]:** Polybot Arena lists "distinct-baguette" (15-minute markets, "buys dips, sells peaks", 142-second median hold), "abrak25" (5-minute high frequency, "$13K+ daily P&L" since Feb 2026), "vidarx" (4,562 predictions, active since Nov 2025), "vague-sourdough", and "BoneReader". Most have no win rate or trade count, and the site gives no ranking or verification methodology. A bot called "Qualitative" reportedly lost about $5K in 18 hours after publishing its strategy and being targeted — [Polybot Arena](https://polybot-arena.com/blog/how-polymarket-bots-trade/)
- **Other bot claims [SELF]:** an "Igor Mikerin" bot is said to have made $2.2M in two months from ensemble news and social models, which is not latency arbitrage. Unnamed bots reportedly made about $206K at over 85% win rates, against about $100K for humans running similar strategies. No source is given for the comparison. The article also says "dozens of bots" farm 15-minute BTC markets, with "many earning tens of thousands per month" — [Yahoo/BeInCrypto](https://finance.yahoo.com/news/arbitrage-bots-dominate-polymarket-millions-100000888.html)
- **Leaderboard bot share [SELF]:** one analysis claims 14 of the 20 most profitable wallets on Polymarket's public leaderboard are bots. This comes from a search snippet, and the methodology is unknown — [Medium](https://medium.com/@weare1010/claude-ai-trading-bots-are-making-hundreds-of-thousands-on-polymarket-2840efb9f2cd)
- **Broader academic baseline [ACAD]:** Saguillo, Ghafouri, Kiffer and Suarez-Tangil ("Unravelling the Probabilistic Forest", AFT 2025) estimate about $40M of realized arbitrage profit on Polymarket from Apr 2024 to Apr 2025. This is within-market rebalancing (YES+NO≠1) and combinatorial arbitrage, not CEX-lag arbitrage — [arXiv 2508.03474](https://arxiv.org/abs/2508.03474); [Decrypt](https://decrypt.co/339958/40-million-free-money-glitch-crypto-prediction-markets)
- **OpenMarket dataset paper [ACAD] (Gregory Young, arXiv Jul 2026):**
  - Data: millisecond-synchronized Polymarket BTC markets and Binance BTC-USDT, 12 Feb–15 May 2026, 727M rows, 2.9M lead-lag pairs.
  - Lag: apparent median lag of 16 ms between venue clocks, with a ±99 ms offset ambiguity. On the collector clock, Polymarket quotes respond to large Binance moves after a **median 347 ms**. Top-of-book spreads are one tick.
  - Profitability: a 43-feature walk-forward model did **not** beat the order-book-implied probability. Simulated trading **lost** about −0.116 normalized payoff units per attempted trade after fees and slippage.
  - Source: [arXiv 2607.26245](https://arxiv.org/abs/2607.26245)
- **Portnaya [ACAD]** (Kyiv School of Economics, arXiv Jun 2026), "Do Prediction Markets Match Option Prices?":
  - Compares Polymarket BTC threshold contracts with Binance-option-implied prices.
  - Finds a mean gap of 6.3pp over 287 observations.
  - A delta-hedged arbitrage proxy stays profitable after conservative costs, but with marginal statistical precision. Per the Spanish-language coverage below, Polymarket tended to overprice the BTC bets.
  - This is a slower, daily or threshold mispricing, not a millisecond lag.
  - Sources: [arXiv 2606.19517](https://arxiv.org/html/2606.19517v1); [DiarioBitcoin](https://www.diariobitcoin.com/trading/estudio-detecta-que-polymarket-sobrevaloro-apuestas-sobre-bitcoin-frente-a-opciones-de-binance/)
- **PolySwarm [ACAD, system design]:** proposes a latency-arbitrage module that derives CEX-implied probabilities from a log-normal model. No backtested profitability was found in the summary — [arXiv 2604.03888](https://arxiv.org/pdf/2604.03888)
- **Practitioner live results [SELF, but negative, so not survivorship-biased]:**
  - After 176 resolved trades, a developer found directional 15-minute crypto trading a losing game. Only buying both sides for under $1 was profitable — [DEV](https://dev.to/manja316/176-trades-on-polymarket-what-my-bot-actually-made-its-not-what-you-think-3iib)
  - Another team's directional 15-minute strategy ran at −37.81% and was disabled — [LayerX](https://layerx.xyz/blog/polymarketbots)
  - A live 5-minute BTC study saw 2–4¢ slippage per token. Combined asks were at or above $1.00 after the 2% taker fee — [Medium](https://medium.com/@gwrx2005/ai-augmented-arbitrage-in-short-duration-prediction-markets-live-trading-analysis-of-polymarkets-8ce1b8c5f362)
  - An LLM-agent paper reports live win rates of 25–27% against a ~53% breakeven. The source is a search snippet — [search summary; see Medium/benjamincup](https://benjamincup.substack.com/p/the-ultimate-guide-to-building-a)

### Inferences
- The "98% win rate" figure is misleading as an edge measure. Buying a side after spot has already moved gives high hit rates at high entry prices. The ~1.2% realized PnL/volume ratio implied by the predicts.guru snapshot is the more informative number, if that figure is accurate.
- The best measured reaction time for Polymarket quotes to Binance moves is a median of about 0.35 s (OpenMarket). Practitioner claims of "30–90 second lags" on 5-minute markets conflict with this and should be treated as unverified or stale.

### Gaps
- I found no Dune dashboard or independent on-chain audit giving 0x8dxd's trade count, win rate, or monthly PnL trajectory. The predicts.guru page was rate-limited.
- I found no systematic census of all bot wallets on Up/Down markets, including the losers. Without one, the cross-section of returns is unknowable from public sources.
- The Portnaya and PolySwarm full texts were not read; their figures come from abstracts and snippets.

## Q2. Cross-venue arbitrage (Polymarket vs Kalshi) and the sports lead-lag

### Takeaway
The Pantera finding is real. Kalshi leads about 80% of large NFL in-game moves by a median of about 7 s. Executable Polymarket↔Kalshi arbitrage, however, is small, rare and short-lived: gaps of about 1–3¢, against a fee break-even of about 3¢ near 50¢ prices. Large headline gaps are mostly stale quotes, and live gaps close in seconds.

### Cited Findings
- **Pantera Research Lab [RESEARCH]** (Ally Zach and Danning Sui, Feb 5, 2026):
  - Sample: all 282 games of the 2025 NFL season through Jan 18, 2026, on each platform; about $359M notional on Polymarket and $1.3B on Kalshi.
  - Kalshi leads the initial repricing in **about 80% of large moves, with a median lead of about 7 s**: 78.6% of 5–10pp moves (n=1,236), 86.7% of 10–20pp moves (n=459), 85.7% of 20pp+ moves (n=126).
  - Polymarket's Kyle-style depth is about 3–4× higher.
  - The authors hypothesise that Polymarket's ~3-second sports order delay contributes to the lag.
  - Caveats: one sport, executed trades only, and no trader IDs on Kalshi.
  - Source: [Pantera Research Lab](https://panteraresearchlab.xyz/research/the-super-bowl-of-prediction-markets-kalshi-and-polymarkets-battle-for-price-vs-liquidity/)
- **Cross-venue census [RESEARCH/blog]** (Mar–Aug 2026; elections, World Cup winner and similar markets):
  - 385 sustained gaps of at least 2¢. Median peak 2.9¢, 90th percentile 5.7¢. Median duration 4.5 h on long-dated markets.
  - **None of the 12 largest raw gaps survived a freshness check** (stale quotes, up to 124 days old).
  - The break-even gap after both venues' taker fees is about 3¢ at mid prices and about 1¢ near the extremes. 54% of episodes peaked below 3¢. Fresh pairs had a median paper profit of about 1¢ before slippage.
  - Source: [PredictMarketCap](https://predictmarketcap.com/analysis/prediction-market-arbitrage-study)
- **Live sports gaps [SELF, developer]:** across a matcher covering about 98% of sports and esports markets, 870 gaps were logged in 24 h. Gaps had a **median life of about 9 s, and 96% closed within 30 s**. Net arbitrage on one major match (Argentina v Egypt, $20.8M of Polymarket volume) was only **$439** — [DEV](https://dev.to/michaelmustopo/built-a-prediction-market-arbitrage-no-sizable-arbitrage-found-36cf)
- **Esports, 30 days [SELF]:** Polymarket–Kalshi arbitrages were 4,435 in a month, **0.09% of all arbitrages**. Mispricings were mostly against sportsbooks, not between the two prediction venues — [DEV](https://dev.to/dozor/polymarket-kalshi-arbitrage-vs-sportsbooks-30-days-of-esports-data-1dc2)
- **A 2¢ gap that lost money [SELF]:** after real fees, a detected 2¢ gap netted −1.4¢ — [DEV](https://dev.to/botcookery/our-polymarket-kalshi-arbitrage-monitor-found-one-2c-gap-after-real-fees-it-lost-14c-41b7)
- **Window compression [SELF, unsourced]:** cross-platform arbitrage windows reportedly fell from an average of 12.3 s (2024) to 2.7 s (Q1 2026). The figure comes from a vendor blog with no methodology — [TurbineFi](https://www.turbinefi.com/blog/prediction-market-arbitrage-latency-speed-2026)
- **Settlement-rule risk:** the two venues settle differently, for example on postponed games, so a "hedged" pair is not risk-free — [Totalis](https://www.totalis.trade/blogs/prediction-markets/prediction-market-arbitrage)

### Inferences
- The ~7 s Kalshi lead is a signal for trading Polymarket against Kalshi, but it is not free money:
  - it applies to the initial repricing of large moves;
  - Polymarket's sports order delay works against the follower;
  - market makers on Polymarket are likely already reading Kalshi.
- The leading venue is where information arrives first, so on Kalshi the edge belongs to whoever has the fastest game feed, not to the cross-venue trader.

### Gaps
- No independent replication of the Pantera lead-lag for NBA or other sports, or for the 2026 NFL season.
- No public PnL for any identified cross-venue arbitrage operator.
- No verified source for the 12.3 s → 2.7 s compression figure.

## Q3. Is there evidence of stock/index Up/Down market mispricing vs the live stock?

### Takeaway
I found no rigorous evidence, either for or against.

### Cited Findings
- Polymarket and Benzinga run S&P 500 "open up or down" style contracts. Benzinga's coverage reports only the prices, for example 73% for a higher open, with no lag analysis — [Benzinga, Nov 2026](https://benzinga.com/markets/prediction-markets/26/11/63418031/stock-market-will-sp-500-open-up-or-down-today-81)
- General calibration work finds major Polymarket markets fairly efficient, with residual mispricing mainly in the tails (a longshot bias) — [Koroleva Lab](https://blog.korolevalab.com/blog/2026/polymarket-accuracy/)

### Inferences
- Equity Up/Down markets can only lag during the hours when the underlying is trading or futures are live. Equity data is also less free and fast to get than Binance websockets, so the competitor set is probably smaller. This is speculation with no data behind it.

### Gaps
- No study, dashboard or wallet analysis of Polymarket or Kalshi stock/index Up/Down markets versus live equity or futures prices was found. This is an open gap; an in-house measurement would be original.

## Q4. How did competition evolve, how did Polymarket respond, and what does a new entrant face?

### Takeaway
The clean taker-latency edge on 15-minute crypto markets peaked in late 2025 and early 2026, when fees were zero and a 500 ms taker delay applied. Polymarket then made a series of changes during 2026 (listed below) that moved value to makers and to the fastest colocated operators. A new entrant now faces three obstacles:
- fees near 50¢ prices that roughly equal the typical lag edge;
- sub-second incumbents, since quotes react in about 0.35 s;
- settlement on Chainlink rather than Binance, which creates basis risk.

### Polymarket's 2026 changes
- **Jan 2026:** dynamic taker fees on 15-minute crypto markets.
- **Feb 2026:** removed the 500 ms taker delay.
- **Mid-2026:** moved settlement from a single-price snapshot to a TWAP after a manipulation study.

### Cited Findings
- **Dynamic taker fees (Jan 2026) [MEDIA]:** Polymarket introduced dynamic taker fees on 15-minute crypto markets, peaking near 50% odds at about **3.15% on a 50¢ contract**. The stated purpose was "to redirect value from latency arbitrage toward genuine liquidity provision" and to fund daily maker rebates. Makers are not charged — [Finance Magnates, Jan 7 2026](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/); [Cointelegraph](https://cointelegraph.com/news/polymarket-quietly-adds-taker-fees-15-minute-crypto-markets). A KuCoin guide gives a lower maximum of 1.80%, which conflicts with this — [KuCoin](https://www.kucoin.com/blog/polymarket-fees-trading-guide-2026). A practitioner later cites a **2% taker fee** on 5-minute markets — [Medium](https://medium.com/@gwrx2005/ai-augmented-arbitrage-in-short-duration-prediction-markets-live-trading-analysis-of-polymarkets-8ce1b8c5f362)
- **500 ms taker delay removed (~Feb 18–20, 2026) [MEDIA, unannounced]:**
  - Polymarket quietly removed the delay on short-term BTC markets.
  - The delay had protected market makers from being picked off. The quoted reaction was "latency is now the only moat", which favours colocated operators.
  - Makers still receive rebates.
  - Source: [Protos](https://protos.com/polymarket-ends-trading-loophole-for-bitcoin-quants/)
  - A DEV guide claims the delay later went to 250 ms and then 50 ms (Aug 17, 2026). This is unverified and inconsistent with the Protos account — [DEV](https://dev.to/soulcrancerdev/how-to-build-a-polymarket-trading-bot-50ms-delay-edition-20o4)
- **CLOB location [SELF]:** the order book is reportedly hosted in London (AWS eu-west-2), which matters for colocation — search summary of [benjamincup Substack](https://benjamincup.substack.com/p/the-ultimate-guide-to-building-a)
- **Settlement manipulation and the move to TWAP [ACAD + MEDIA]:**
  - Paper: Dai, Jia and Yu (arXiv Jun 2026; Stanford/SMU per CoinDesk) find spot order-flow spikes and large reversals around 5-minute BTC settlement. Manipulators profit mostly at retail's expense, and the effect is "largely absent" in 15-minute contracts — [arXiv 2606.31675](https://arxiv.org/abs/2606.31675)
  - Scale: CoinDesk reports **821 accounts made $8.2M** in likely manipulated windows, with 93% of non-market-maker losses falling on retail — [CoinDesk, Aug 7 2026](https://www.coindesk.com/business/2026/08/07/how-a-five-second-trick-let-traders-drain-millions-from-polymarket)
  - Response: Polymarket switched to TWAP settlement via Chainlink Data Streams (30 s for 5-minute markets, 60 s for 15-minute and 4-hour markets) and added $1M in liquidity rewards — same CoinDesk article.
  - Kalshi already settles on a CF Benchmarks 60-second average — same CoinDesk article.
- **Settlement benchmark mismatch:** the 5m/15m/4h Up/Down contracts resolve on a Chainlink price, not Binance, so a Binance-lag strategy carries basis risk — [arXiv 2606.31675 (search summary)](https://arxiv.org/pdf/2606.31675)
- **Crowding and strategy decay [SELF]:**
  - A bot that published its strategy was reportedly targeted and lost about $5K in 18 hours — [Polybot Arena](https://polybot-arena.com/blog/how-polymarket-bots-trade/)
  - One commentary (via search snippet) says two of three famous bots stopped after the rule changes. The bots are not named and the claim is unverified.
  - A tracker snapshot puts 0x8dxd's last trade around Aug 2026 — [predicts.guru](https://www.predicts.guru/checker/0x63ce342161250d705dc0b16df89036c8e5f9ba9a)
- **Ecosystem saturation:** curated lists catalogue 100–150+ Polymarket bots, many of them commercial 5-, 15- and 60-minute crypto bots — [polbots.com](https://polbots.com/); [GitHub list](https://github.com/sssobolevski/polymarket-bots)

### Inferences
- **Edge timeline:** the latency edge was most lucrative from roughly Nov 2025 to Jan 2026. In that window fees were zero, the 500 ms delay protected anyone who rested orders, and a handful of bots took large sums.
- **After the changes:**
  - The ~3% peak fee at 50¢ roughly equals the price move that a sub-second Binance lead typically provides.
  - Pure taker-side latency arbitrage near even odds was therefore largely priced out.
  - What remained was the large-move tail, plus maker or market-making strategies that collect rebates.
- **What this means for a home-network entrant** (likely 50–200 ms from London, settling on Chainlink rather than Binance):
  - They would be competing against operators whose quotes already react in about 350 ms.
  - The academic and practitioner evidence that does not suffer from survivorship (OpenMarket, the negative dev logs) points to negative expectancy for taker lag strategies.
- **Shift of value:** profit moved from "fast taker" to "fast maker" and, on 5-minute markets until the TWAP fix, to settlement manipulators.

### Gaps
- No primary Polymarket document with the exact fee formula or current taker delay was retrieved.
- No time series of median reprice latency or of top-bot PnL, from before to after the fee change, was found. That would be the direct measure of whether bots compressed the edge.
- No data on Kalshi's own 15-minute crypto markets' lag versus spot, or on bot activity there.
