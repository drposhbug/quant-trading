"""Live paper account vs what the backtest says the model should have done over the same days.
Run: python track.py   (reads signals/equity_log.csv written by monitor.py)

Timing: the logged equity is the account equity snapshotted at the daily rebalance (~15:30 ET, 12:30 on half days),
BEFORE that day's orders are sent (monitor.rebalance reads /account first). So each live daily return runs
15:30 -> 15:30 and includes the trades made the previous afternoon, while the model's is close -> close. Expect a small
extra tracking error from that half-hour offset even when everything is correct; it should average out, not drift.

Cash: the backtest earns 0 on cash; live idle cash sits in SGOV, and Alpaca paper credits no dividends, so SGOV's
price-only return is ~0 too — comparable as is. Real money would add ~T-bill yield x cash share on top.

Large gaps mean the live system is not the strategy we tested (fills, costs, bugs) — find out why before trusting either.
"""
import math

import pandas as pd

from model import BENCH, load_prices, target_weights, backtest_returns


def compare(log):
    """log: equity_log rows indexed by date (>= 2 rows). Live vs backtest model vs QQQ over the logged days."""
    px = load_prices(start=(log.index[0] - pd.Timedelta(days=500)).date().isoformat())
    m = backtest_returns(px, target_weights(px))
    idx = log.index  # compound the model across sessions between logged dates (a missed day spans two sessions live)
    model = pd.Series([(1 + m[(m.index > a) & (m.index <= b)]).prod() - 1 for a, b in zip(idx[:-1], idx[1:])], index=idx[1:])
    live = log.equity.pct_change().iloc[1:]
    qqq = px[BENCH].reindex(log.index).pct_change().iloc[1:]
    cum = lambda r: (1 + r.fillna(0)).prod() - 1
    diff = (live - model).dropna()
    return dict(days=len(live), live=cum(live), model=cum(model), qqq=cum(qqq), te=diff.std() * math.sqrt(252),
                worst=diff.abs().max(), worst_day=diff.abs().idxmax().date() if len(diff) else "-")


if __name__ == "__main__":
    log = pd.read_csv("signals/equity_log.csv", parse_dates=["date"]).set_index("date").sort_index()
    if len(log) < 2:
        raise SystemExit(f"Only {len(log)} day(s) logged; come back after a few rebalances.")
    c = compare(log)
    print(f"{c['days']} trading days, {log.index[0].date()} to {log.index[-1].date()}")
    print(f"Live account   {c['live']:+.2%}")
    print(f"Backtest model {c['model']:+.2%}")
    print(f"QQQ            {c['qqq']:+.2%}")
    print(f"Daily tracking error vs model: {c['te']:.2%} annualised; worst day gap {c['worst']:.2%} on {c['worst_day']}")
    print("Rule of thumb: after ~60 days, tracking error above ~3%/yr or a persistent drift means fills or code differ from the backtest.")
