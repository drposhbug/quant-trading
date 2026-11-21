# Astra 6.2 verification of the code-audit findings (2026-11-21)

Astra was given a secrets-free copy of the repo and 19 defects reported by the audit readers, plus three extra questions (X1: the local T-bill sizing fix; X2: half-day handling; X3: the tracking-error clock offset). It was asked to refute each. The X1 gap it found (an infeasible T-bill sale) was patched afterwards, with a test.

| ID | Verdict | Severity | One-sentence reason | Smallest fix |
|---|---|---|---|---|
| stock_model-1 | confirmed | medium | `monitor.py:204` fills QQQ before the freshness check at 216, so an old close can determine today’s regime at 221 and `model.py:118–120`. | Validate the raw QQQ value and session date before filling. |
| stock_model-2 | confirmed | high | At `model.py:90–109`, a stale eligible stock can reach zero volatility, making its inverse weight infinite and every normalized weight zero at 112. | Reject stale inputs before trading and mask zero or negligible volatility before division. |
| pm_trader-1 | confirmed | high | `odds_compare.py:135–153` prefers a matching start but accepts an unmatched fallback, which `trader.py:196–236,331–340` caches and trades against the fixture clock. | Require both team identities and a compatible token start, including on cache hits. |
| pm_trader-3 | confirmed | high | `trader.py:273–293` retries errors, absent bids and zero fills indefinitely, with no resolution path to realize the payout or release exposure. | Settle remaining shares from an authoritative final payout. |
| pm_trader-4 | confirmed | high | `polymarket_exec.py:203–215` can fill only the best-bid size, yet `trader.py:294–299` books that quantity’s P&L and `db.py:664` closes the position. | Record the fill and decrement remaining shares atomically. |
| pm_trader-5 | confirmed | medium | `trader.py:126,157–161,488–489` permits the quoted spread, compares the next midpoint to the entry ask, then makes the sold token immediately eligible again. | Compare midpoint to entry midpoint and block re-entry on the same signal. |
| pm_trader-6 | confirmed | medium | `polymarket_exec.py:83–94,110–112` ignores a `base_fee` response and charges a percentage of notional, whereas even `METHODS.md:55` specifies a price-dependent per-share fee. | Use the market’s fee schedule for each fill and retain the actual entry fee. |
| pm_models-1 | confirmed | medium | `bet_sizer.py:81–93` enables EPL model stakes without enforcing best-price execution, although the reported positive interval requires it and the model fails its log-loss gate. | Require verified executable best odds or close the gate. |
| pm_models-2 | refuted | none | The daily workflow does log the losing Elo rule, but `reports/sports_results.md:46–58` explicitly retains this paper ledger for forward calibration. | None for logging; identify its calibration purpose on the scorecard. |
| pm_models-4 | confirmed | medium | With pandas 3.0.1, the exact parser at `ingest_tennis.py:89–90` turned `2024-02-12` into December 2, which `to_rows` persists at 122. | Parse ISO and day-first inputs explicitly, then rebuild dated features. |
| stock_proof-1 | confirmed | high | `monitor.py:62,235–236` logs intraday equity while `track.py:23–31` scores it against close-to-close returns, permitting a false failure. | Score session-close equity. |
| stock_proof-2 | confirmed | medium | `track.py:27` counts cash flows as returns, and `scorecard.py:138–144` carries them into cumulative return and drawdown. | Adjust for external flows and start a new measurement period on reset. |
| stock_proof-3 | confirmed | medium | `MATH.md:74` requires drift assessment, but `scorecard.py:150–155` omits it and `model.py:124–136` omits the execution buffer and band. | Specify a drift tolerance against a benchmark incorporating documented execution and dividend treatment. |
| options_sleeve-1 | confirmed | high | Beyond the calendar horizon, `options_earnings.py:106–112` takes `min()` of an empty sequence at 107, outside the per-symbol handler at 321–325. | Return “no covered reaction session” and continue scanning. |
| options_sleeve-2 | confirmed | low | `options_earnings.py:116–122,307–312` allows a pre-09:45 close and forces natural pricing on expiry, but lines 15–19 explicitly document expiry precedence. | Clarify the exception in the experiment’s exit-window description. |
| pm_paper_sleeves-1 | confirmed | medium | Tennis scores a final 0.5 as a loss plus fees at `tennis_favorites.py:206–213`, while `sport_favorites.py:233–238` and `any_favorites.py:244–248` discard its economic loss. | Book `(final_payout − ask − fee)/ask` and include split resolutions. |
| pm_paper_sleeves-3 | confirmed | medium | `any_favorites.py:194–213,271` admits related tokens and passes individual returns to the independent-row bootstrap at `sport_favorites.py:254`. | Resample by underlying event or shared outcome. |
| pm_paper_sleeves-4 | confirmed | medium | `sports.py:240–244,279–286,382–393` uses fee-free payout arithmetic in both callers, including when the forward entry used a real ask. | Capture the market-specific entry fee and deduct it once. |
| pm_paper_sleeves-5 | confirmed | medium | `sports.py:114–115,178–183` requires the ET date to equal the slug date, excluding the November 19 evening game whose slug says November 20. [Market record](https://polymarket.com/sports/nfl/nfl-ind-hou-2026-11-20) | Match teams and kickoff timestamp. |
| X1 | confirmed | medium | `monitor.py:68–90` correctly nets skipped trades but can request an infeasible SGOV sale or an unfunded buy. | Bound SGOV by holdings and fund buys from refreshed cash after sells fill. |
| X2 | refuted | none | The scheduled authenticated loop uses Alpaca’s actual close at `loop_monitor.py:43–55` and `monitor.py:47–51,187–189`. | None for half-days. |
| X3 | confirmed | high | The timing offset can independently exceed 3% annualized; the one-row equity log cannot establish an observed breach. | Retrieve the broker’s regular-session closing equity by date. |

### X1–X3

**X1.** The regression covers six skipped $900 trims. Full stock exits are correctly excluded from `skip`, and line 75 rechecks SGOV’s **adjusted** difference, so it can cross the band in either direction. A remaining in-band SGOV difference leaves a cash-buffer discrepancy smaller than the band. The substantive counterexample is skipped trims exceeding the entire SGOV target: line 71 then implies negative SGOV holdings. Conversely, skipped stock buys can increase the SGOV buy before submitted sells fill. Failed or rounded-down stock sales also leave expected proceeds unavailable. If SGOV’s original weight is zero, line 78 liquidates an existing position regardless of its adjusted target.

**X2.** On November 27, the `:17` hourly starts span 07:17–15:17 ET. Even the earliest loop’s 5h40 budget reaches 12:57. From 12:15 it sleeps two minutes between passes. The first eligible open pass from 12:30 to 13:00 rebalances, and successful completion suppresses repeats. After close, the bookkeeping pass returns without trading. Delivery delays can still miss the window.

**X3.** For independent closing-interval returns with daily standard deviation \(s\), yesterday’s interval enters the gap positively and today’s negatively, giving annualized error \(s\sqrt{504}\). Just **13.4 basis points** clears 3%. If the interval carries 3% of daily portfolio variance, 20% annual portfolio volatility gives **4.9%** timing error; 10% gives **2.45%**. The variance share is an assumption. Retries can also replace the snapshot later in the window.

Historical ledger counts and replay percentages were not independently reproduced. EPL season skipping uses prior-season validation, so it does not establish look-ahead bias.

### Fix first

1. **pm_trader-1** — Verify the contract before pricing or buying it.
2. **pm_trader-4** — Preserve unsold shares so exposure and realized P&L reconcile.
3. **stock_model-2** — Prevent one stale quote from liquidating the stock sleeve.