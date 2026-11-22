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
sgov = [b for b in buy if b["symbol"] == "SGOV"]  # idle 85% -> T-bills: 0.85 * 100k * 0.98, less AAPL's skipped $100 trim
assert len(sgov) == 1 and abs(sgov[0]["notional"] - 83200.0) < 0.01, buy
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
assert "down 10%" in monitor.drawdown_alert(st, 90_000)
assert monitor.drawdown_alert(st, 89_000) is None  # same tier: no repeat
assert "deep loss" in monitor.drawdown_alert(st, 80_000)
assert monitor.drawdown_alert(st, 97_000) is None and st["dd_tier"] == 0  # recovered past -5%: re-armed
assert "let it ride" in monitor.drawdown_alert(st, 89_000)
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

# Non-fractionable asset (fresh IPO): whole-share qty; under one share -> INFO, not FAILED.
calls.clear()
def fake_nf(method, path, **kw):
    calls.append((method, path, kw.get("json")))
    if path == "/account": return {"equity": "100000"}
    if path == "/positions": return []
    if path.startswith("/assets/"): return {"fractionable": path != "/assets/SPCX"}
    return {}
monitor.alpaca = fake_nf
_, lines = monitor.rebalance({"SPCX": 0.03}, nodata=set(), last={"SPCX": 120.0})
o = [c[2] for c in calls if c[0] == "POST" and c[2]["symbol"] == "SPCX"]
assert o and o[0]["qty"] == str(int(0.03 * 100000 * 0.98 / 120)) and "notional" not in o[0], o
calls.clear()
_, lines = monitor.rebalance({"SPCX": 0.03}, nodata=set(), last={"SPCX": 5000.0})
assert not [c for c in calls if c[0] == "POST" and c[2]["symbol"] == "SPCX"] and any(l.startswith("INFO SPCX") for l in lines), lines
assert not any(l.startswith("FAILED") for l in lines), lines

# Missed rebalance: previous sessions after the last completed rebalance are reported once and accumulate.
monitor.alpaca = lambda m, p, **k: [{"date": "2026-11-19"}, {"date": "2026-11-20"}, {"date": "2026-11-23"}]
st = {"rebalanced": "2026-11-19"}
import datetime as _dt
msg = monitor.missed_rebalance(st, _dt.date(2026, 11, 23))
assert "2026-11-20" in msg and st["missed"] == ["2026-11-20"], (msg, st)
assert monitor.missed_rebalance({"rebalanced": "2026-11-20"}, _dt.date(2026, 11, 23)) is None
print("fractionable + missed-rebalance checks passed")

# 2026-11-20 case: many small stock overweights, each under the 1% band. T-bills must not be bought with money that is
# still in stocks: orders placed + positions kept must not exceed equity (no margin).
names = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META"]
def fake2(method, path, **kw):
    calls.append((method, path, kw.get("json")))
    return {"equity": "100000"} if path == "/account" else [{"symbol": s, "market_value": "5800"} for s in names] if path == "/positions" else {}
monitor.alpaca = fake2
calls.clear()
monitor.rebalance({s: 0.05 for s in names}, nodata=set())  # targets 4900 each, held 5800: every trim is $900 < $1000 band
posts = [c[2] for c in calls if c[0] == "POST"]
assert [p["symbol"] for p in posts] == ["SGOV"], posts
assert posts[0]["notional"] + 6 * 5800 <= 100000 * 0.98 + 0.01, posts  # was 68600 + 34800 = 103.4% of equity
print("skipped-trim cash check passed")

# Netting can ask to sell more T-bills than are held (stocks over target, little SGOV): close SGOV, never oversell it.
def fake3(method, path, **kw):
    calls.append((method, path, kw.get("json")))
    return {"equity": "100000"} if path == "/account" else (
        [{"symbol": s, "market_value": "17000"} for s in names] + [{"symbol": "SGOV", "market_value": "2000"}]) if path == "/positions" else {}
monitor.alpaca = fake3
calls.clear()
monitor.rebalance({s: 0.165 for s in names}, nodata=set())  # stock targets 16170, held 17000: six skipped $830 trims; SGOV target 980
assert ("DELETE", "/positions/SGOV", None) in calls, calls
assert not [c for c in calls if c[0] == "POST"], calls  # no notional SGOV sale larger than the holding, no stock orders
print("T-bill oversell check passed")
