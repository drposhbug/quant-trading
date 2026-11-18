"""Rebalance order logic against a fake Alpaca. No network. Run: python test_monitor.py"""
import monitor

calls = []


def fake(method, path, **kw):
    calls.append((method, path, kw.get("json")))
    if path == "/account":
        return {"equity": "100000"}
    if path == "/positions":
        return [{"symbol": "NVDA", "market_value": "10000"}, {"symbol": "OLDX", "market_value": "5000"},
                {"symbol": "AAPL", "market_value": "9900"}]
    return {}


monitor.alpaca = fake

# Normal day: NVDA dropped to 0 -> close position; OLDX outside universe -> close; AAPL within 1% band -> no order; MSFT buy.
_, lines = monitor.rebalance({"AAPL": 0.10, "MSFT": 0.05}, nodata={"ANT"})
orders = [c for c in calls if c[0] in ("POST", "DELETE")]
assert ("DELETE", "/positions/NVDA", None) in orders and ("DELETE", "/positions/OLDX", None) in orders, orders
assert not any(c[0] == "POST" and c[2]["symbol"] in ("AAPL", "ANT") for c in orders), orders
buy = [c[2] for c in orders if c[0] == "POST"]
assert ("DELETE", "/orders", None) == calls[0]  # stale open orders cancelled before anything else
assert {"symbol": "MSFT", "notional": 4900.0, "side": "buy", "type": "market", "time_in_force": "day"} in buy, buy
sgov = [b for b in buy if b["symbol"] == "SGOV"]  # idle 85% -> T-bills: 0.85 * 100k * 0.98
assert len(sgov) == 1 and abs(sgov[0]["notional"] - 83300.0) < 0.01, buy
assert len(buy) == 2, buy
assert orders.index(("DELETE", "/positions/NVDA", None)) < len(orders) - 1  # sells before the buy

# Download failure on a held name: skip the whole rebalance, never sell it.
calls.clear()
_, lines = monitor.rebalance({"AAPL": 0.10}, nodata={"ANT", "NVDA"})
assert not [c for c in calls if c[0] == "POST" or c[1].startswith("/positions/")] and "SKIPPED" in lines[0], lines

print("all checks passed")

# Drawdown tiers: alert once per tier, re-arm after recovery.
st = {}
assert monitor.drawdown_alert(st, 100_000) is None
assert monitor.drawdown_alert(st, 95_000) is None
assert "-10.0%" in monitor.drawdown_alert(st, 90_000)
assert monitor.drawdown_alert(st, 89_000) is None  # same tier: no repeat
assert "deep" in monitor.drawdown_alert(st, 80_000)
assert monitor.drawdown_alert(st, 97_000) is None and st["dd_tier"] == 0  # recovered past -5%: re-armed
assert "review" in monitor.drawdown_alert(st, 89_000)
print("drawdown checks passed")

# Equity log: one row per day, retries replace.
import os, tempfile
monitor.EQUITY_LOG = os.path.join(tempfile.mkdtemp(), "eq.csv")
monitor.log_equity("2026-11-19", 100000, 0.47, "risk-off")
monitor.log_equity("2026-11-19", 100100, 0.47, "risk-off")
monitor.log_equity("2026-11-20", 100500, 0.5, "risk-off")
import pandas as pd
lg = pd.read_csv(monitor.EQUITY_LOG)
assert list(lg.date) == ["2026-11-19", "2026-11-20"] and lg.equity.iloc[0] == 100100, lg
print("equity log checks passed")
