"""scorecard.py against fake Alpaca accounts and temp CSVs. No network. Run: python test_scorecard.py"""
import json
import os
import tempfile

import numpy as np
import pandas as pd

import scorecard as sc

T = tempfile.mkdtemp()
P = lambda f: os.path.join(T, f)
sc.EQUITY_LOG, sc.STOCK_STATE, sc.OPT_TRADES, sc.OPT_STATE = P("eq.csv"), P("st.json"), P("opt.csv"), P("ost.json")
sc.SPORTS, sc.PM, sc.STATE = P("sports.csv"), P("pm.csv"), P("sc_state.json")

# ---- metrics math
assert abs(sc.max_drawdown([100, 120, 90, 130]) - (90 / 120 - 1)) < 1e-12
assert sc.roi([10, -5], [100, 100]) == 0.025 and sc.roi([1], [0]) is None
assert abs(sc.tstat([1, 2, 3]) - 2 / (1 / np.sqrt(3))) < 1e-12 and sc.tstat([5, 5]) is None
lo, hi = sc.bootstrap_roi([1.0] * 50 + [-1.0] * 50, [1.0] * 100)
assert lo < 0 < hi, (lo, hi)
lo, hi = sc.bootstrap_roi([0.9] * 80 + [-1.0] * 20, [1.0] * 100)
assert lo > 0, lo
print("metrics checks passed")

# ---- rule evaluation
assert sc.verdict(10, 120, True) == "INSUFFICIENT_N"
assert sc.verdict(120, 120, True) == "PASS" and sc.verdict(500, 120, False) == "FAIL"
assert sc.verdict(5, 120, True, stop=True) == "STOP" and sc.verdict(40, 30, None) == "NOT_SCORED"

# options: 130 trades, mean > 0 with t > 2 -> PASS; account -12% from peak -> STOP
sc.oe.AK = "fake"
sc.oe.alpaca = lambda m, p, **k: {"equity": "95000"}
json.dump({"peak_equity": 100000, "spreads": {}}, open(sc.OPT_STATE, "w"))
rng = np.random.default_rng(1)
pd.DataFrame({"pnl": rng.normal(30, 50, 130)}).to_csv(sc.OPT_TRADES, index=False)
o = sc.options()
assert o["n"] == 130 and o["t"] > 2 and o["verdict"] == "PASS", o
pd.DataFrame({"pnl": rng.normal(-1, 50, 130)}).to_csv(sc.OPT_TRADES, index=False)
assert sc.options()["verdict"] == "FAIL"
sc.oe.alpaca = lambda m, p, **k: {"equity": "88000"}
assert sc.options()["verdict"] == "STOP"
os.remove(sc.OPT_TRADES)
sc.oe.alpaca = lambda m, p, **k: {"equity": "100000"}
assert sc.options()["verdict"] == "INSUFFICIENT_N"

# sports: no ledger -> insufficient; winning ledger -> PASS; losing after 100 bets -> STOP
assert sc.sports()["verdict"] == "INSUFFICIENT_N"
n = 220
won = np.tile([1, 1, 0], n)[:n]
led = pd.DataFrame({"model_prob": 0.7, "market_price": 2.0, "stake": 10.0, "outcome": won,
                    "pnl": np.where(won == 1, 10.0, -10.0)})
led.loc[n] = [0.6, 0.5, 0.0, 1, np.nan]  # logged candidate, not bet: counts for Brier, not ROI
led.to_csv(sc.SPORTS, index=False)
s = sc.sports()
assert s["n"] == n and s["verdict"] == "PASS" and s["ci"][0] > 0 and s["n_brier"] == n + 1, s
assert abs(s["brier_market"] - ((0.5 - pd.Series(list(won) + [1])) ** 2).mean()) < 1e-12  # decimal odds 2.0 -> 0.5
led = led.iloc[:120].assign(pnl=lambda d: np.where(d.outcome == 1, 1.0, -10.0))
led.to_csv(sc.SPORTS, index=False)
assert sc.sports()["verdict"] == "STOP"

# ipo: resolved = bracket markets that dropped out of the latest snapshot; brackets of one IPO = one event
rows = [("t1", "polymarket", f"acme-{b}", f"Acme IPO closing market cap between ${b}B and ${b + 5}B?") for b in (10, 15)]
rows += [("t1", "polymarket", "acme-hi", "Acme IPO closing market cap above $20B?"),
         ("t1", "polymarket", "spacex-high", "Will SpaceX have the highest IPO Market Cap 2026?"),  # not a close bracket
         ("t2", "polymarket", "beta-1", "Beta IPO closing market cap above $5B?"),  # still open
         ("t2", "polymarket", "fed", "Fed cut?")]
pd.DataFrame(rows, columns=["ts_utc", "source", "market_id", "question"]).assign(yes_price=0.5, volume_24h=1).to_csv(sc.PM, index=False)
i = sc.ipo()
assert i["markets"] == 3 and i["n"] == 1 and i["verdict"] == "INSUFFICIENT_N", i
print("rule checks passed")

# ---- stocks with a fake Alpaca + fake track.compare (no prices download)
pd.DataFrame({"date": ["2026-11-19", "2026-11-20", "2026-11-23"], "equity": [100000, 98000, 99000],
              "gross": 0.5, "regime": "risk-off"}).to_csv(sc.EQUITY_LOG, index=False)
json.dump({"missed": ["2026-11-19"]}, open(sc.STOCK_STATE, "w"))
sc.track.compare = lambda log: dict(qqq=0.01, model=-0.008, te=0.02, live=0, days=2, worst=0, worst_day="-")
sc.fill_shortfall = lambda start: (3.0, 40)
sc.monitor.AK = "fake"
sc.monitor.alpaca = lambda m, p, **k: {"equity": "101000"} if p == "/account" else [{"symbol": "NVDA"}, {"symbol": "SGOV"}]
s = sc.stocks()
assert abs(s["ret"] - 0.01) < 1e-12 and abs(s["maxdd"] + 0.02) < 1e-12 and s["n"] == 3, s
assert all(s["checks"].values()) and s["verdict"] == "INSUFFICIENT_N", s
sc.monitor.alpaca = lambda m, p, **k: {"equity": "101000"} if p == "/account" else [{"symbol": "OLDX"}]
assert sc.stocks()["checks"]["positions"] is False
print("stocks checks passed")

# ---- report length + dedupe
card = sc.build()
assert card["stocks"]["verdict"] != "ERROR" and card["sports"]["verdict"] == "STOP", card
big = {**card, "sports": {**card["sports"], "error": "x" * 5000, "verdict": "ERROR"}}
assert len(sc.report(big)) <= 1900 and len(sc.report(card)) <= 1900
assert "Scorecard" in sc.markdown(card)
sent = []
sc.monitor.discord = lambda msg: sent.append(msg) or True
sc.main()
sc.main()
assert len(sent) == 1 and json.load(open(sc.STATE))["last_report"] == card["date"], sent
sc.monitor.discord = lambda msg: False  # failed post: not marked, retried next run
os.remove(sc.STATE)
sc.main()
assert not os.path.exists(sc.STATE)
print("report checks passed")
print("all checks passed")
