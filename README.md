# quant-trading

Research-driven quant model for TSLA, SPCX (SpaceX, Nasdaq since 2026-06-12) and mega-cap tech (AAPL, MSFT, NVDA, GOOGL, AMZN, META).
It runs in the cloud on GitHub Actions, sends alerts to Discord and paper-trades on Alpaca.

**Start here:** [MATH.md](MATH.md) explains what was proven and what failed.

| Path | What |
|---|---|
| `reports/Quant trading for Tesla and big tech.md` | Synthesis of 13 parallel research agents |
| `research_notes/` | Raw notes from each research agent |
| `model.py` | Inverse-vol basket + 15% vol target + QQQ 200d regime overlay |
| `backtest.py` → `reports/backtest_results.md` | Backtest plus proof battery: bootstrap, HAC alpha, deflated Sharpe, PBO, IC |
| `candles.py` → `reports/candles_results.md` | 13 candlestick patterns × 3 horizons, Holm-corrected |
| `monitor.py` + `.github/workflows/monitor.yml` | Runs every 15 min in market hours: Discord alerts and daily paper rebalance |
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
