"""Live paper account vs what the backtest says the model should have done over the same days.
Run: python track.py   (reads signals/equity_log.csv written by monitor.py)

Timing: the logged equity is the account equity snapshotted at the daily rebalance (~15:30 ET, 12:30 on half days),
BEFORE that day's orders are sent (monitor.rebalance reads /account first). So each live daily return runs
15:30 -> 15:30 and includes the trades made the previous afternoon, while the model's is close -> close. Expect a small
extra tracking error from that half-hour offset even when everything is correct; it should average out, not drift.

Large gaps mean the live system is not the strategy we tested (fills, costs, bugs) — find out why before trusting either.
"""
import math

import pandas as pd

from model import BENCH, load_prices, target_weights, backtest_returns

log = pd.read_csv("signals/equity_log.csv", parse_dates=["date"]).set_index("date").sort_index()
if len(log) < 2:
    raise SystemExit(f"Only {len(log)} day(s) logged; come back after a few rebalances.")

px = load_prices(start=(log.index[0] - pd.Timedelta(days=500)).date().isoformat())
model = backtest_returns(px, target_weights(px)).reindex(log.index).iloc[1:]  # model's close-to-close return per logged day
live = log.equity.pct_change().iloc[1:]
qqq = px[BENCH].pct_change().reindex(log.index).iloc[1:]

cum = lambda r: (1 + r.fillna(0)).prod() - 1
diff = (live - model).dropna()
print(f"{len(live)} trading days, {log.index[0].date()} to {log.index[-1].date()}")
print(f"Live account   {cum(live):+.2%}")
print(f"Backtest model {cum(model):+.2%}")
print(f"QQQ            {cum(qqq):+.2%}")
print(f"Daily tracking error vs model: {diff.std() * math.sqrt(252):.2%} annualised; "
      f"worst day gap {diff.abs().max():.2%} on {diff.abs().idxmax().date() if len(diff) else '-'}")
print("Rule of thumb: after ~60 days, tracking error above ~3%/yr or a persistent drift means fills or code differ from the backtest.")
