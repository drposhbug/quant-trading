# pm_models: sports prediction models and LLM/news components

Audit note, 2026-11-21. Everything here is paper or research code. Numbers marked "re-run" were reproduced offline and read-only from `betting/sports_data.sqlite3`.

## Purpose

This unit holds the statistical sports models (soccer, NBA, tennis, World Cup), the studies that compared them with bookmaker prices, an LLM research agent (Grok plus Gemini) and two free ESPN collectors (injuries, news). METHODS.md's core finding (models lose to the market in three sports) and its one "validated" result (EPL +6% at best price) both come from here.

## Data flow

- **Ingest.** Results and odds go into SQLite: EPL from football-data.co.uk (`ingest_premier_league.py`), NBA from nba_api (`ingest_nba.py`), tennis from a GitHub mirror of tennis-data.co.uk covering 2021 to early 2024 (`ingest_tennis.py:49-51`). Features (Elo, form, head-to-head, rest, shots, xG) are built by walking matches in date order and updating ratings only after a match's features are read.
- **Studies.** Three scripts refit a model on earlier seasons and score the next season against the market: `nba_diagnose.py:105-125` (13 seasons, 15,226 games), `tennis_diagnose.py:104-133` (3 years, 10,987 matches), `train_market_model.py:180-218` (XGBoost, 19 EPL seasons).
- **Saved weights.** Trainers store coefficients plus end-of-history ratings (`nba_model_weights.json`, `club_model_weights_*.json`). `analyze_prices.py:169-187` loads them to print a `model_prob` beside each sharp-line signal.
- **LLM agent.** `external_factors_agent.py` sends team names, a date and a context string to xAI Grok with web and X search (`:149-160`), pastes Grok's text into a Google Gemini prompt (`:211-240`) and saves a JSON report with a win-probability adjustment. About two paid calls per fixture. No account data or repo content is sent.
- **Collectors.** `nba_injuries.py --snapshot` and `news_watch.py` store ESPN injury reports and headlines. No code reads these tables back for a decision.

## Decision rules and parameters

- NBA Elo: K 20, home edge 100, 25% season regression, 10-game form (`nba_features.py:40-53`). Tennis Elo: K 32, 20-match form (`tennis_features.py:34-38`). Soccer Elo: K 20, home edge 65, promoted clubs start at 1430 (`club_features.py:33-46`).
- Market benchmark. NBA: closing moneyline from a public archive, power de-vig (`nba_odds.py:27-28`, `:55-81`). Tennis: Pinnacle, power de-vig (`tennis_diagnose.py:63`). EPL: pre-closing market-average odds, proportional de-vig (`ingest_premier_league.py:122-124`, `train_xgboost_model.py:55-58`).
- EPL bet rule: bet an outcome when model minus market exceeds a threshold chosen on the previous season from 2/3/4/5/8 points; skip the whole season if no threshold had positive ROI on at least 15 bets (`train_market_model.py:65-66`, `:135-149`). Interval reported at 90% (`:68`).
- Model stakes: blocked for NBA and tennis, allowed for `premier_league` (`bet_sizer.py:74-94`); 5% cap, quarter Kelly (`:61-62`).
- LLM adjustment: capped at 15 points when parsed (`external_factors_agent.py:47`, `:253-254`). Research runs only with `--research` and a 5-point model/market gap (`analyze_prices.py:221`, `:253-255`).
- Root `sports.py` has its own, separate Elo (K 20, home edge 48 NFL / 100 NBA, one-third regression, `sports.py:41-42`). It logs a 1-unit paper bet when Elo and the Polymarket mid differ by more than 5 points (`:43`, `:230-237`).

## What happens on a given day

- Cloud, every 3 hours: `sports.run_daily()` prices NFL/NBA games with the `sports.py` Elo and logs paper bets. This is the only model output that reaches a paper bet.
- Local scheduler (`run_daily.bat`, judged from the database copy of 20 November): injuries about twice a day, news about every 20 minutes, then `analyze_prices.py --alert --paper-log`. The betting/ models add a context column only; stakes use the sharp-line gap (`analyze_prices.py:268`).
- The LLM agent is not called by any scheduled job. Injury and news data influence nothing.

## Assumptions the code makes

- Stored dates are true match dates. For tennis 36% have day and month swapped (`ingest_tennis.py:89-90`).
- The power de-vig suits every two-outcome market. On NBA closing lines it is the worst of three methods.
- Saved ratings are current. They stop in May/June 2026 and the season lists are hard-coded to end at 2025-26.
- Team names match across sources. "Los Angeles Clippers" resolves to a dead pre-2015 rating.
- A prompt instruction plus a keyword filter stops Grok seeing results of matches already played.
- The best price across dozens of bookmakers can actually be had.

## Tests

`betting/test_pipeline.py` checks de-vig arithmetic, that flipping the last result leaves that row's tennis and NBA features unchanged, the staking gate, and a few data sanity checks. The 46 checks relevant here pass (run read-only today). `test_sports.py` covers the `sports.py` Elo arithmetic, no-lookahead and ledger handling.

Not tested: date order, de-vig calibration against results (the test asserts only the direction), soccer features, the walk-forward splits, threshold selection, the bootstrap, stale weights, name mapping, fees in `sports.py`, and every part of the LLM agent and the ESPN parsers. CI runs none of these tests, and its requirements lack scikit-learn and xgboost, so the betting models cannot run in the cloud.

## What the re-runs showed

- **NBA.** Reproduced exactly: the model loses in 13 of 13 seasons, gap +0.020 (95% interval +0.017 to +0.024). Sound.
- **Tennis.** Reproduced (+0.0553). With dates repaired the gap is +0.042. Still a loss in 3 of 3 years, shrinking each year as ratings warm up from a cold start.
- **EPL.** Reproduced (log loss 0.977 vs 0.959; 2,165 bets; +6.0% at best price, +0.9% at average odds). About 86% of the log-loss gap is XGBoost noise: an XGBoost given only market prices loses by 0.015. A low-variance logistic model with the same stats is still worse than the market, so "no information in these features" holds. The +6% does not hold up: its 95% interval includes zero, and without the previous-season gate the same model earns +2% to +4% at best price and -1% to -3% at average odds.

## Current state

- NBA weights: 23,074 games to 2026-06-13. EPL weights: 12,614 matches to 2026-05-24 (90 matches from 2003-05 silently missing). Tennis: 15,933 matches.
- LLM: 45 reports, all generated 2026-07-07, none since. Median adjustment 6.5 points.
- Collectors: 11,745 injury rows (134 polls) and 36,963 news rows (5,020 polls), 2026-09-09 to 2026-11-20.
- `paper_trades`: 604 rows, 48 with a model probability (context only).
- Elo paper ledger (`signals/sports_ledger.csv`): 30 rows, 12 open bets (11 on the home team), none settled.
