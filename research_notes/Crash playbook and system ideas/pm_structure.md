# Structural edges on Polymarket and Kalshi (key: pm_structure)

Written 2026-11-21. Every number carries a source link or is marked [calc]: my own calculation today from public, unauthenticated exchange endpoints. These are single snapshots, not backtests. The web-search quota ran out before a few checks (last section).

## Findings

**1. Kalshi now pays for resting quotes, and the repo has never counted that money.**
Its Liquidity Incentive Program lists 8,658 active programmes worth $725k for their current periods (most last a week), about $110–190k a day [calc from `api.elections.kalshi.com/trade-api/v2/incentive_programs`]. The filed terms: one book snapshot a second; each side needs 1,000 contracts resting; an order at the side's reference price scores in full and half as much per tick behind it; the pool is split pro rata; under $1 per programme is not paid; it expires by 1 January 2027 unless re-filed ([CFTC filing](https://www.cftc.gov/filings/orgrules/rules10142633813.pdf), [help page](https://help.kalshi.com/en/articles/13823851-liquidity-incentive-program)). It needs a direct Kalshi account; customers of brokers are excluded. `maker_sim.py` scored fills only and found −12.6%.

I sampled 600 of these markets at 00:59 ET today [calc]:

- 89% met the two-sided test, and 245 had not traded in seven days.
- Joining both reference prices with 100 contracts (about $98 of collateral) would hold a median 1.9% of the pool. That is $0.31 a day, or 0.33% a day on collateral (quartiles 0.08% and 0.99%), if the book stayed as it was.
- Over the previous seven days makers in these markets earned +0.74¢ a contract marked to the mid (bootstrap interval −1.83 to +2.71; −1.84¢ without the ten busiest markets). That is about zero, like the repo's −1¢. Incentives on the same markets were $63.8k for the week.

What could erase it:

- It is one quiet-hour snapshot, and the share assumes nobody reacts.
- The yield looks best where other makers have just fled, so ranking by yield selects the toxic markets.
- The worst sampled market cost its makers $2.3k in the week.
- Quotes must be ones you accept being filled on; the filing cites Kalshi's spoofing rule.

**2. The favourites sleeves are scored on a book the owner cannot trade, and the fee tier decides the sign.**
Polymarket's documentation lists the United States as close-only on site and API ([geoblock page](https://docs.polymarket.com/api-reference/geoblock)). The US exchange is a separate book with its own schedule ([fees](https://docs.polymarket.us/fees)):

- taker coefficient 0.095 below $10k of 30-day volume, falling to 0.0695 at $250k;
- API takers pay 0.0695 with a 70% rebate from 21 November to 31 December 2026 (net 0.021);
- makers pay nothing.

On 140 games listed on both books today, the US spread was 0.5¢ against 1.0¢ and the mids matched. Buying the favourite cost 0.84¢ less through the US API than on the international book, and 0.37¢ more at the US entry tier [calc]. The measured favourite edge is +0.8% a bet (`reports/fav_backtest_results.md`).

**3. Rebates are gone for small accounts.**
Since 20 November 23:59 UTC Polymarket pays maker and taker rebates only above $200k of 30-day weighted volume ([maker rebates](https://docs.polymarket.com/programs/maker-rebates), [changelog](https://docs.polymarket.com/changelog)). The US exchange starts maker rebates at $10M of 30-day volume. Kalshi's taker rebate needs 2,000,000 of monthly "effective volume" ([filing](https://www.cftc.gov/filings/orgrules/rules10142633445.pdf)). Polymarket taker coefficients are now 0.05 or 0.01 by category and 0 for geopolitics ([fees](https://docs.polymarket.com/trading/fees)). `betting/METHODS.md` still says 0.03, and the 0.04 fallback in `any_favorites.py` is no longer on the schedule.

**4. "Bonds" are the favourite-longshot bias at its thinnest, not carry.**
A 97¢ Kalshi contract costs 97.2¢ with the taker fee, so it must win 97.2% of the time, and one loss cancels about 35 wins [calc]. The financing is roughly neutral on Kalshi and a cost on Polymarket:

- Kalshi pays 3.50% on cash and positions ([APY page](https://help.kalshi.com/en/articles/13823847-apy-on-kalshi)).
- Four-week bills pay 4.11% ([Treasury](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_bill_rates&field_tdr_date_value_month=202611)).
- Polymarket pays nothing on idle collateral and 3.25% on a short list of long-dated markets ([holding rewards](https://help.polymarket.com/en/articles/13364459-holding-rewards)).

The repo's own bins put contracts priced 0.90–1.00 at +0.5 to +0.8 points on Kalshi macro markets and +1.9 on Polymarket (n = 102). Neither is distinguishable from zero (`reports/pm_calibration.md`). The tail is real: more than 1,150 Polymarket markets went to arbitration in 2026 by mid-May, more than in all of 2025, and ten wallets hold over half the votes in most disputes ([Finance Magnates](https://financemagnates.com/fintech/polymarkets-arbitration-model-faces-conflict-of-interest-questions)). `any_favorites.py` already tests this, and a second test is not justified.

**5. Who earns it.**
The average Kalshi maker does: +1.91¢ a contract in single-name markets and +0.82¢ in broad ones before fees, steady through early 2026, from selling YES to optimistic takers and holding to settlement ([Bartlett and O'Hara](https://conference.nber.org/conf_papers/f243677.pdf), 41.6M trades). The repo's simulation fills only when the price trades through, so it is the pessimistic bound; a slow small maker sits between the two.

Of $39.6M of arbitrage taken on Polymarket in the year to April 2025, cross-market logic earned about $95k; the rest was within one market, a speed contest ([Saguillo et al.](https://arxiv.org/abs/2508.03474)). 69% of 2.9M human-paced Polymarket accounts lost money ([Galaxy via Crypto Briefing](https://cryptobriefing.com/galaxy-research-polymarket-retail-losses/)).

**6. What small size buys, and what this does for the selloff.**
Kalshi pools of $40–180 a period per market are too small for a firm and carry no per-account cap [calc]. Polymarket US is the opposite: at least $22.1M of pools for games from 21 November to 4 December, 99% of it for in-game quoting, with a median target of 3,400 contracts a side [calc from `gateway.polymarket.us/v1/incentives`]. That is the latency contest the repo already rejected.

Nothing here profits from the selloff itself. Incentive income and 3.5% interest are small and unrelated to equity beta.

## Evidence table

| Item | Figure | Source |
|---|---|---|
| Kalshi fees | taker 0.07·p(1−p), 1.75¢ at 50¢; maker 0.0175·p(1−p) on listed series | [filing](https://www.cftc.gov/filings/orgrules/rules10142633445.pdf); [paper, note 16](https://conference.nber.org/conf_papers/f243677.pdf) |
| Kalshi incentive programmes | median $75 a period ($14 a day); target 1,000 and discount 0.5 on all 8,658 | [calc] |
| Polymarket liquidity rewards (not open to US accounts) | 8,379 markets, $74k a day, median $3; minimum payout $1 | [calc]; [docs](https://docs.polymarket.com/programs/liquidity-rewards) |
| Taker fee per contract on heavy favourites (0.80–0.97, 48 games, medians) | US entry tier 1.07¢; international 0.57¢; US API net 0.24¢ | [calc] |
| Kalshi takers and makers, equal-weighted | takers −31%, makers −10%; makers buying above 50¢ +2.6% | [Bürgi, Deng and Whelan](https://www2.gwu.edu/~forcpgm/2026-001.pdf) |
| Selling YES only, as a maker | twice the profit, three times the dispersion; worst deciles all settled YES | [Bartlett and O'Hara](https://conference.nber.org/conf_papers/f243677.pdf) |

## Ideas worth a pre-registered test

**1. Kalshi incentive maker, paper sleeve. Pass probability 0.30.**

- Universe: active `liquidity` programmes from the public list; non-sports, non-crypto series; at least three days of programme left; market closes more than 48 hours ahead; both sides meet the target.
- Selection: each day at 12:00 ET, 40 markets drawn by sha1(ticker + date). Never ranked by yield.
- Quotes: 100 contracts a side at each side's reference price, re-checked every 15 minutes; inventory capped at 300 a market.
- Fills: a paper bid fills in full the first time any public trade prints at or through its price. Maker fee by series. Hold to settlement.
- Reward: the filed formula on one-minute book snapshots with our size included, then halved; zero if under $1 for the programme.
- Unit: one market-period; stake is peak collateral; minimum n is 300.
- Pass: total P&L over total stake above zero, event-clustered bootstrap 95% interval above zero, positive in both chronological halves.
- Stop: −10% of mean deployed collateral after 100 market-periods. If the programme ends before n reaches 300, the sleeve closes unscored.

A pass recommends one thing: a live check with at most $200 that Kalshi's actual credits match the estimate. The owner decides.

**2. Venue shadow log. Not a test; 0.8 that it leaves the owner better off.**
At each entry the favourites and sports scripts already log, also store the Polymarket US best bid, ask and size for the same game (`gateway.polymarket.us/v1/markets/{slug}/book`, public). No frozen rule changes and no n restarts. Read-out at 200 paired entries: mean all-in cost difference at coefficients 0.095, 0.0695 and 0.021 with a paired bootstrap interval, and each sleeve's ROI re-priced on the US book. Any promotion recommendation quotes the US-priced figure.

**3. Kalshi resting-bid favourites. Pass probability 0.08; I would not spend a trial on it.**
Non-sports markets with an objective source, 7–30 days to close, side priced 0.90–0.97, spread at most 2¢. Rest a bid one tick above the best bid for 24 hours under the same fill rule, hold to settlement, flat $100. n = 200 settled, same pass bar. The repo's Kalshi bins are inside noise, and resting bids fill most when the favourite is weakening.

Not worth a trial: buying 97–99¢ contracts as a taker; Polymarket–Kalshi pair trades (`reports/Millisecond lags and latency arbitrage.md`); in-game incentive quoting; splitting orders to use cent rounding on Polymarket US.

## What I looked for and did not find

- An independent audit of what incentive farmers net after fills, on either venue. My figures are one snapshot and one week.
- Kalshi's fee PDF (HTTP 429 twice). The formula comes from Kalshi's own filing and the public series endpoint.
- Whether Polymarket US pays interest, what deposits and withdrawals cost, and which states it excludes today.
- Dispute or reversal rates for contracts priced above 95¢; I found counts of disputes only.
- Whether Polymarket has replaced UMA; its holding-rewards page says a new resolution system is "anticipated".
- Kalshi position limits (they vary by contract and do not bind at this size), Becker's original paper, and anything on Robinhood or ForecastEx.
