# quant-trading

Research-driven quant model for TSLA, SPCX (SpaceX, Nasdaq since 2026-06-12) mega-cap tech (AAPL, MSFT, NVDA, GOOGL, AMZN, META), the AI compute chain (AVGO, TSM, AMD, ORCL). (Anthropic/ANT was considered and removed before listing; MATH.md change log.)
It runs in the cloud on GitHub Actions, sends alerts to Discord and paper-trades on Alpaca.

**Start here:** [MATH.md](MATH.md) explains what was proven and what failed.

**Status:** the model is frozen as of 2026-11-19 and paper-traded for 12 months (MATH.md §Change control). No proven edge over equal-weighting the same stocks at the same volatility; the honest forward expectation is the end-2014 tech-list result, ~15% CAGR at Sharpe ~1.0, not the 23% in-sample backtest.

| Path | What |
|---|---|
| `reports/Quant trading for Tesla and big tech.md` | Synthesis of 13 parallel research agents |
| `research_notes/` | Raw notes from each research agent |
| `model.py` | Inverse-vol basket + 20% vol target + QQQ 200d regime overlay |
| `correlations.py` → `reports/correlations_results.md` | Residual, overnight/intraday, tail-dependence and lead-lag correlation study |
| `macro.py`, `events_study.py`, `pm_study.py`, `trump_study.py`, `altdata_study.py` | Predictor studies (macro, earnings/calendar, prediction markets, Trump posts, insider/short interest/TSMC). All null; see MATH.md table |
| `universe_study.py` → `reports/universe_results.md` | Other stocks, bonds, gold, trend ETFs, T-bill cash |
| `reports/Replicated predictors for tech stocks.md`, `Top traders methods and math.md`, `Trading psychology and behavior.md` | Literature research syntheses |
| `test_monitor.py` | Rebalance order logic + drawdown alerts against a fake Alpaca |
| `backtest.py` → `reports/backtest_results.md` | Backtest plus proof battery: bootstrap, HAC alpha, deflated Sharpe, PBO, IC |
| `candles.py` → `reports/candles_results.md` | 13 candlestick patterns × 3 horizons, Holm-corrected |
| `monitor.py` + `.github/workflows/monitor.yml` | Runs every 5 min in market hours: Discord alerts and daily paper rebalance |
| `test_model.py` | No-lookahead, weight-limit and stats self-checks |

## Setup (one time)

1. **Discord:** Server Settings → Integrations → Webhooks → New Webhook → Copy URL.
2. **Alpaca paper:** sign up at alpaca.markets → Paper Trading → API Keys → Generate.
3. Add the secrets. You can paste each value when prompted:
   ```
   gh secret set DISCORD_WEBHOOK_URL -R drposhbug/quant-trading
   gh secret set ALPACA_API_KEY -R drposhbug/quant-trading
   gh secret set ALPACA_SECRET_KEY -R drposhbug/quant-trading
   ```
4. Test it: GitHub → Actions → monitor → Run workflow → tick "force".

## Local

```
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python test_model.py
.venv/Scripts/python backtest.py
.venv/Scripts/python candles.py
```

Not financial advice. The paper URL is hard-coded in monitor.py; going live should be a deliberate code change.
