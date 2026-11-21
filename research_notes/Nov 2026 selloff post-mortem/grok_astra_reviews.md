# Independent reviews by Astra 6.2 and Grok (2026-11-21)

Both models were given the same facts brief and the same seven questions, with no web access and no view of the repo. Their answers are opinions and hypotheses, not evidence: figures they recall from memory are unverified, and the probabilities are subjective. The brief and prompt are reproduced at the end.

---

# Astra 6.2 (codex exec -m gpt-6.2-astra, read-only)

## 1. Diagnosis

This was a broad equity correction with much larger losses in semiconductors and AI stocks. On November 20 the Dow fell 1.9%, the S&P 500 fell 3.7%, and the semiconductor index fell 10.7%. The reported catalysts fit that pattern, but the brief cannot establish how much selling each caused.

The model entered at 46% gross after its trend filter had already triggered. It lost 5.0% against QQQ’s 7.7% over two sessions. That is consistent with partial protection. Inverse-volatility sizing still left all 12 stocks exposed to the same selloff. A 20% annualized volatility target sets neither a daily loss limit nor a drawdown floor. The missed rebalance, 39% actual versus 34% target stock exposure, and negative cash are separate execution issues. Their contribution to the loss requires an order-by-order replay.

## 2. Was it predictable?

**Elevated risk was observable. The timing and size of Friday’s fall were not reliably forecastable from these facts.** The November 5 decline and November 13 QQQ trend break documented deterioration. The latter had already cut the model’s exposure before its first purchase. Nvidia’s leadership change and higher-rate expectations identified specific risks. Low implied correlation indicated that options priced relatively little joint movement, without telling investors when stocks would fall together.

Low fund cash suggested vulnerability, while managers had already cut tech exposure and retail investors were selling. Persistent bearish sentiment and repeated bubble warnings supplied no clear entry or exit date. Earlier scares followed by new highs illustrate the cost of acting early. Treating the seven-loss streak, Friday’s VIX close, or post-drop fear readings as advance warnings for Friday uses hindsight.

**The false-alarm rate is unknown.** Estimating it requires all prior signals under a fixed definition, including alarms followed by rallies, and a specified loss threshold and horizon. Neither the 700 research tests nor the eight failed variants count those episodes. A 5% significance threshold is not a forecast’s false-alarm rate.

## 3. What a rules-based system could have done better

| Change | Normal-time cost |
|---|---|
| **Execution:** Record each scheduled run, alert on missed completion, and reconcile fills before retrying within a fixed execution window. Diagnose Thursday from logs. | Monitoring and reconciliation work. |
| **Execution:** Size SGOV from available cash after confirmed stock fills, allowing for outstanding orders and fees. Apply a portfolio-level tolerance to accumulated skipped trims. | Small cash drag and more trades when small deviations add up. |
| **Model:** A standing semiconductor exposure cap could reduce losses from a sector shock. The tested cap failed its admission test. | Less participation in semiconductor rallies. |

At 15:30, the official close is still unknown. Audit whether live trading and the backtest use the same available signal. Using the previous close consistently costs up to one session of responsiveness. The live loss had not reached the −10% review tier.

## 4. Recovery

From $94,975, breakeven requires **5.29%**. The S&P needs **13.1%** from 11.6% down, and QQQ needs **24.8%** from 19.9% down. These are recovery hurdles, not expected returns.

Historical recollection, **unverified**: broad-index corrections have recovered in months, while deeper bear markets have taken years. The brief supplies no comparable-event forward returns or median recovery times for either index or engine. CAGR and maximum drawdown cannot supply them. At 34% stock exposure, a sudden 10% basket rebound earns roughly 3.4% before carry, costs, and rebalancing. A sustained advance permits re-entry. A sharp rebound followed by another break can leave the engine buying back higher and cutting again lower. That whipsaw is the main recovery risk.

## 5. Bigger gains

Ranked by my subjective probability of a **positive net log-return improvement significant at one-sided P < 0.05 on both universes** in one pre-registered paired comparison. These are judgment calls, not measured frequencies.

| Rank / lever | Expected effect and added risk | Probability |
|---|---|---:|
| 1. Moderate leverage | Raises gains if returns exceed financing and volatility drag. Magnifies losses. Prior financing-aware evidence was weak. | 20% |
| 2. Added premia | A genuinely diversifying return source could improve compound growth. Adds implementation costs and another strategy that can lose. | 15% |
| 3. Broader universe | Reduces dependence on AI. Could lower returns during tech leadership. | 12% |
| 4. More concentration | Increases upside if the chosen names win. Adds single-name risk without a validated selection signal. | 8% |
| 5. Faster re-entry | Captures more of a V-shaped recovery. Adds false starts. The closest prior result depended heavily on two episodes. | 6% |
| 6. Options overlay | Calls add convex upside at a premium. Repeated premium losses can reduce compound growth. | 4% |

## 6. Up to four pre-registered tests

**One prospective test.** Hypothesis: 1.25× frozen stock exposure improves net compound growth. On each US trading session from November 23, 2026 through November 19, 2027, multiply frozen stock weights by 1.25 and allocate the residual to SGOV. Charge negative residuals the daily SGOV total return plus 2%/252 per session. Use frozen execution assumptions and deduct one additional basis point per dollar of incremental stock turnover. Start both portfolios at identical equity and cash.

For each required universe, measure mean daily paired net log-return difference. Draw 100,000 stationary-bootstrap samples of the mean-centered differences, expected block length 20 sessions, circular wrapping, seed 20261121. Pass only if each observed mean is positive and fewer than 5% of its null replicates equal or exceed it. One forward year gives limited power.

## 7. Where I disagree with the model’s owners

The weakest decision was moving the volatility target **15% → 25% → 20% after inspecting results**, immediately before freezing it. That choice governs every position and the losses the owner must tolerate. Freezing it prevents further tuning but cannot validate the original selection. Set the risk budget from the dollar loss the owner can carry through a drawdown, and treat the selected target’s historical performance as in-sample.
---

# Grok (grok CLI, headless, tools and web search disabled)

The live book did what a half-invested AI basket does in a correlation spike. From the Thursday open to Friday’s close it fell 5.0% ($100k → $94,975) while QQQ fell 7.7%. That gap is the regime rule. Alpha versus the equal-weight basket was already dead (t = 0.70).

## 1. Diagnosis

A sector drawdown with a macro assist, short of a broad bear. S&P −11.6% from the 6 Oct high is a correction. Nasdaq about −18% and QQQ −19.9% sit at the edge of a bear market. Friday was one trade: NVDA −14%, AMD −13%, AVGO −12%, SOX −10.7%, QQQ −5.7%, VIX from the mid-20s to ~36–37. Gold and bitcoin fell too, which fits deleveraging. The reported catalysts are a cluster, not a single cause.

The engine is twelve AI/megacap names, inverse-vol weights, a 20% vol target, a 100% gross cap, and a halving when QQQ is below its 200-day. That halving was already on (QQQ first closed under the average on 13 Nov). The account was bought at ~46% gross; Friday’s target was 34%. Average name loss since entry was about 12%, so ~39% gross produces a ~5% account loss. Full gross on that basket would have been a low-teens day.

Two misses sat on a working rule. Thursday’s 15:30 rebalance never ran, so that day’s target never hit the market. Friday’s skip of trades under ~1% of equity left stocks near 39% versus 34%, and cash at −$3.6k.

Backtest CAGR 23.2% (Sharpe 1.25, max drawdown −22.5%) is the winner’s list. The same engine on the end-2014 top-10 tech names did 15.3% and 0.97. Defend ~15% CAGR and a Sharpe near 1.

## 2. Was it predictable?

No fact in the brief was a usable ex-ante sell for this week.

- AAII bears at 48–51%, and four weeks of retail selling, are contrary readings. In memory they lean toward later gains (unverified). As crash timers they false-alarm on most firings, because those readings are common and 10% breaks are not.
- BofA cash at 3.6% is a real published complacency flag, and the tech-overweight cut shows managers were already leaving. It is slow. Bubble warnings all year, each scare followed by highs, plus MS/RBC/JPM calling the correction nearly over on 9 Nov, are the base rate. A threshold that stays “on” for long stretches precedes some selloffs and a larger number of quiet periods. False alarms dominate. No verified hit-rate table is available here, and none is invented.
- VIX ~25 with implied correlation ~22% on 9 Nov described shape: contagion was cheap. It is also the ordinary state of that market (unverified: implied correlation sits in the teens and twenties far more often than at crisis levels). As a timer, “correlation is normal” almost always false-alarms. The content showed up as Friday’s index move once correlation repriced.
- The 13 Nov 200-day break had information, and the model had already halved. Nvidia headlines were idiosyncratic. About 700 pre-registered tests in this program found no edge after multiple-testing correction. The eight ideas run on 20 Nov went 0 for 8.

Hindsight, specifically: counting this year’s bubble essays as the ones that mattered; reading high AAII bears as a warning; any threshold chosen because it would have cut gross before Friday.

## 3. What a rules-based system could have done better

**Execution.** Make the 15:30 job fire. Normal-times return cost is about zero. The missed Thursday run is the one defect that may have left stale, higher gross through Thursday and Friday morning. Thursday’s unfilled target is not in the brief, so the dollars are unknown.

Drop the per-name skip when cash would go negative or gross would sit more than 2 percentage points above target. Cost is a few extra megacap trades, well under 10 bp/year at a 1–2 bp spread unless it binds constantly.

Fill on the backtest’s clock (15:30), including the first day. Cost is one afternoon of cash at inception.

**Model.** Nothing already tested would have been flat into Friday. The halving is the crash rule, and it was on. MA bands and VIX re-entry failed; VIX ≥ 40 came closest (P = 0.054 / 0.083 / 0.159), with gains concentrated in 2008–11 and Apr 2025. The account is at −5%. The pre-committed −10% tier is “review, no action.” A model edit this weekend fits the week the freeze exists to ignore.

## 4. Recovery

The account needs about +5.3% to be flat. At ~35–39% gross, a bounce of roughly 14% in the basket does that, before T-bill carry. Bill yield is not in the brief (the 10-year is ~4.9%). QQQ is 10.8% under its 200-day, so a reclaim needs a rally on the order of 12% against a frozen average, less as the average falls. Until that cross, the rules keep roughly half exposure. A V-shaped bounce heals the account more slowly than QQQ. A grind lower is what the halving is for.

Unverified, approximate index history: non-recession S&P drawdowns of 10–15% have often retraced within a quarter or two; 2018’s decline near 20% took about four months to reclaim the high; 2020’s crash about five months; 2022’s bear about two years for the S&P and longer for the Nasdaq. A vol-targeted, trend-filtered book usually takes less of the V — it is light at the low, and vol scaling buys back after vol falls — and less of the long bear. Backtest max drawdown −22.5% versus QQQ −35% and the basket −44% is that tradeoff. There is no version that is fully invested at the bottom and also keeps the drawdown cut.

The realistic path is partial participation until a 200-day reclaim, then a full re-risk, with a multi-month wait if this rhymes with 2022. The main risk is another leg in the same twelve names. Friday was a portfolio day. A second one at ~39% gross costs another ~4–5% and puts the −10% tier in view. The SEC exam, the CEO vacancy, hike pricing, and CTA flow under the 200-day are still open. An oversold put/call ratio does not close them.

## 5. Bigger gains

Bigger gains here are bigger risk. Seven hundred empty tests and an 0-for-8 slate are the base rate for free alpha. Each probability is the chance the lever beats the frozen model at P < 0.05 on a paired bootstrap of **mean daily return, on both universes, in one pre-registered try**. A Sharpe gate, the honest one for a risk-control engine, pulls every risk-scaling idea toward ~0.05. Their own leverage study already failed once financing was real.

1. **Leverage ~1.5×, financed.** Largest CAGR lift if excess returns stay positive: several points, not a doubling. Vol and drawdown scale; −22% becomes a mid-30s drawdown or worse. P(return) = 0.20. P(Sharpe) ≈ 0.06.
2. **Vol target 20% → 25%.** The same dial, milder when the gross cap binds. Already walked 15 → 25 → 20 on 18–19 Nov after looking at results. P(return) = 0.18. P(Sharpe) ≈ 0.05.
3. **Drop the 200-day halving.** This is the equal-weight basket’s 36% CAGR and −44% drawdown. The rule is off most days in a bull sample, so the added CAGR is smaller than that gap. You give back the product. P = 0.12.
4. **More concentration.** Heavier NVDA/AMD/AVGO is the loss just taken (AMD −21% since entry) and likely fails the 2014 list. P = 0.10.
5. **Faster re-entry after VIX ≥ 40.** Best-of-eight selection already spent the luck. Several VIX spikes are not the low. P = 0.08.
6. **Broader universe.** Lower CAGR, more honest book. P(beat this list on return) = 0.08.
7. **Added premia.** Expected effect ~0 after costs. P = 0.05.
8. **Options.** Puts are priced for the move after VIX has already jumped. A standing put program costs on the order of 1–3 pp/year in calm markets (unverified; single-name puts cost more). Collars sell the rebound. P(return) = 0.05.

## 6. Up to four pre-registered tests

Decide only at the next scheduled review. Shared setup: daily returns 2015-03-02 through 2026-11-19, shipped list and end-2014 top-10, stationary bootstrap, mean block 21 days, 10,000 resamples, seed 20261121, 1 bp per side, paired against the frozen engine. Both universes must clear.

1. **Gross compliance.** Constraint “cash ≥ 0 and |gross − target| ≤ 2 pp,” even when a name’s trade is under 1% of NAV, cuts mean absolute gross error versus the skip. Pass: one-sided P < 0.05 on that error, both lists, and CAGR drag under 15 bp/year on both (point estimate).
2. **Leverage.** 1.25× the engine, borrow at 3-month T-bill + 50 bp (FRED DTB3), halving applied after the scale, gross cap 125%. Pass: one-sided P < 0.05 on **Sharpe**, both lists. A return-only win is recorded and is not a pass.
3. **Name cap.** A 10% cap (SPCX stays 5%) has higher Sharpe than 25%. Pass: one-sided P < 0.05 on Sharpe, both lists.
4. **Five-day re-risk ramp.** After QQQ crosses from below to above its 200-day, step gross from the risk-off weight to the risk-on weight in five equal 15:30 slices. Pass: one-sided P < 0.05 on Sharpe, both lists, and CAGR no more than 50 bp/year lower on either list (point estimate).

## 7. Where you disagree with the model's owners

The vol target moved 15% → 25% → 20% on 18–19 Nov after looking at results, inside a selloff that had already started, and the freeze locked the peeked number. The research rule — one pre-registered test, both universes, never during a drawdown — was applied to eight ideas on the crash day and shipped nothing. It was not applied to the risk budget. A freeze that ratifies a parameter chosen by eye fails at the only knob that sets how much this account can lose. Leave 20% alone until a section-6 test says otherwise. Monday is for the missed rebalance and the cash-floor bug, not for getting the money back.

---

# Prompt and brief sent to both

You are an independent reviewer of a small rules-based equity model after a sharp selloff. Everything you know about the episode is in the brief below; you have no web access, so label anything from memory as unverified and do not invent data for 2026.

Answer in Markdown, under 1,200 words, with these sections:
1. **Diagnosis** — what kind of event this was and how the model behaved relative to its design.
2. **Was it predictable?** — which of the listed pre-drop facts, if any, had real ex-ante information, and what the base rate of false alarms for that kind of signal is. Be specific about what is hindsight.
3. **What a rules-based system could have done better** — only changes that do not need hindsight. Separate execution fixes from model changes. Name the cost of each change in normal times.
4. **Recovery** — what history says about returns and time-to-recover after comparable drawdowns for an index and for a vol-targeted, trend-filtered engine (which de-risks at the bottom). What is the realistic path and the main risk?
5. **Bigger gains** — rank the levers honestly (leverage, concentration, universe, added premia, options overlays, faster re-entry, anything else). For each: expected effect, the risk it adds, and your probability (a number) that it would beat the frozen model in one pre-registered paired-bootstrap test at P < 0.05.
6. **Up to four pre-registered tests** — hypothesis, metric, data window, pass bar. Written so they could be run without further choices.
7. **Where you disagree with the model's owners** — the single strongest criticism of the frozen model or its change-control process.

Do not flatter. If the honest answer is "nothing would have helped" or "bigger gains only come with bigger risk", say so with numbers.

---
# Facts brief (as of Saturday 2026-11-21). Treat as given; anything you add from memory is unverified.

## The market episode
- Peak: 2026-10-06 (S&P 500 record close 7,818.93). 2026-11-05: S&P -4.4%, Nasdaq -5.5% ("worst day since April 2025").
  Week ending 11-13 was a brief up week. Then seven straight S&P losses (longest since Feb 2020).
- Friday 2026-11-20: S&P 500 -3.7% (6,910; -8.6% on the week; -11.6% from peak), Nasdaq Comp -5.3% (-10% week, ~-18% from peak),
  QQQ -5.67% (-19.9% from peak, 10.8% below its 200-day average; first close below the 200d on 2026-11-13), Dow -1.9%, SOX -10.7%.
  VIX closed ~36-37 (intraday ~40), up from ~25 on 11-09 and ~23 on 11-16. 10y yield ~4.9% (5.1% on 11-12). Gold -4.6%, bitcoin ~$59k then $56k Saturday.
- Day moves 11-20: NVDA -14.0%, AMD -13.3%, AVGO -12.2%, TSM -9.5%, ORCL -8.5%, SPCX (SpaceX, IPO'd 2026-06) -7.7%, TSLA -7.6%, META -5.9%, AMZN -4.1%, MSFT -2.8%, GOOGL -2.7%, AAPL -1.9%.
- Reported triggers: Reuters report that SEC staff are examining Nvidia's accounting; Nvidia CEO Jensen Huang resigned ~11-12; Anthropic IPO fell ~9% on day two;
  Fed officials floating hikes (Dec hike ~91% priced); post-midterm data-centre regulation risk; oil ~$84-93; break of the 200-day triggering systematic (CTA) selling.
- Pre-drop sentiment (published before 11-20): AAII bears 48-51% for weeks; retail net sellers four straight weeks; BofA fund-manager survey 11-17: cash 3.6%
  (BofA "sell signal" level), tech overweight cut from 37% to 12%, only 3% expect recession; Cboe 11-09: VIX ~25 but S&P implied correlation only 22% ("no contagion priced");
  AI-bubble warnings had been continuous all year (Dalio Jan and Oct, Gartner, BofA), each earlier scare followed by new highs. On 11-09 Morgan Stanley, RBC and JPMorgan strategists said the correction was nearly over.
- Post-drop: CNN Fear & Greed 10-14 (extreme fear), equity put/call 1.02 (highest since Apr 2025), strategists split (Siegel/Kass buy or hold; BTIG, BofA see more downside).

## The model ("frozen model", paper-traded on Alpaca since 2026-11-19, $100k)
- Long-only basket of 12 megacap tech/AI names: TSLA, SPCX, AAPL, MSFT, NVDA, GOOGL, AMZN, META, AVGO, TSM, AMD, ORCL. No stock-picking signal (trend+reversal signal was tested and rejected).
- Sizing: inverse-volatility weights (60-day), 25% per-name cap (SPCX 5%), scaled to a 20% annualised portfolio vol target, never above 100% gross.
- Regime rule: gross exposure halved when QQQ closes below its 200-day average. Idle cash in T-bills (SGOV). Rebalanced daily near the close (15:30 ET).
- Backtest 2015-03 to 2026-11-19: CAGR 23.2%, vol 17.9%, Sharpe 1.25, max drawdown -22.5% (QQQ: 17.6%, 22.1%, 0.84, -35.1%; equal-weight basket: 36.1% CAGR, -44% drawdown).
  Same engine on the end-2014 top-10 tech list (no hindsight in the name list): CAGR 15.3%, Sharpe 0.97. Honest forward expectation ~15% CAGR, Sharpe ~1.0 at best.
  Alpha vs equal-weight basket is not significant (t = 0.70): the engine is risk control, not return.
- Prior research in this repo: ~700 pre-registered tests (macro, events, alt-data, candlesticks, Trump posts, prediction markets, calendar, lead-lag) found no predictive edge after
  multiple-testing correction. A slate of 8 "retail edge" ideas run 2026-11-20 (tax-aware execution, muni cash, month-end timing, MA band, faster re-entry after VIX>=40, semis cap, 52-week high, net liquidity): 0 of 8 pass.
  VIX>=40 re-entry came closest (P = 0.054 / 0.083 / 0.159; gain concentrated in 2008-11 and 2025-04).
  Leverage study (engine x 1.25/1.5/2.0 on 6 indices since 1950-1988): leverage did not reliably beat buy-and-hold once financing costs were real.
- Change control: model frozen to 2027-11-19. A change ships only if it beats the frozen model in ONE pre-registered paired stationary-bootstrap test (P < 0.05) on both
  the shipped universe and the end-2014 list, decided at a scheduled review, never during a drawdown. Vol target was changed 15% -> 25% -> 20% on 11-18/19 after looking at results (acknowledged overfitting risk).
- Pre-committed drawdown tiers: -10% "review, no action"; -20% "decide on lowering vol target at the next scheduled review, never same day".

## What the live account did
- First buys filled at the open on Thursday 2026-11-19 at ~46% gross (model already in risk-off). The 15:30 rebalance on 11-19 was missed (cause not yet known).
- Friday 15:30 rebalance: target gross 34%; trimmed AAPL, MSFT, AMZN, put the rest in SGOV. Trims under ~1% of equity per name are skipped, so stocks ended ~39% and cash -$3.6k (small unintended margin).
- Equity $94,975 at Friday's close: -5.0% in two sessions versus QQQ -7.7%. Per-name loss since entry: AMD -21%, NVDA -19%, AVGO -16%, ORCL -14%, TSM -13%, SPCX -12%, TSLA -12%, META -10%, GOOGL -10%, AMZN -9%, MSFT -7%, AAPL -3%.
- The owner is a retail investor who wants to know: could this have been predicted, what could have been done better, how the account recovers, and how to get bigger gains.
