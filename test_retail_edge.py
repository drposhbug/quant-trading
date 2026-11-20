"""Self-checks for retail_edge_tests.py: tax netting, wash sales, lot order, bands, gates. Run: python test_retail_edge.py"""
import numpy as np
import pandas as pd

from backtest import prices
from model import backtest_returns, target_weights
from retail_edge_tests import (RATES, ZERO, Ledger, gate_frozen, gate_hyst, lagged, sim, tax_due, vix_episodes,
                               weights)

R = RATES
# 1. tax netting by character, $3k limit, carryforward
assert np.isclose(tax_due(1000, 2000, 0, 0, 0, R)[0], 1000 * .408 + 2000 * .238)
assert np.isclose(tax_due(-500, 2000, 0, 0, 0, R)[0], 1500 * .238)          # ST loss offsets LT gain
t, cs, cl = tax_due(-10000, 1000, 0, 0, 0, R)                                 # net ST loss 9k: 3k deducted, 6k carried
assert np.isclose(t, -3000 * .37) and np.isclose(cs, 6000) and cl == 0
assert np.isclose(tax_due(0, 0, 100, 6000, 0, R)[0], 100 * .408 - 3000 * .37)  # carryforward used next year
assert tax_due(5, 5, 5, 0, 0, ZERO)[0] == 0

# 2. wash sale AFTER: loss sale then a buy within 30 days -> loss disallowed, basis + tacked holding period
L = Ledger(10000, R, cost=0)
L.px = {"A": 100.0}
L.buy("A", "A", 1000, 0)
L.px = {"A": 80.0}
L.sell([(L.lots["A"][0], 10)], 40)
assert np.isclose(L.real["st"], -200)
L.buy("A", "A", 800, 50)
assert np.isclose(L.real["st"], 0) and np.isclose(L.lots["A"][0][2], 100) and L.lots["A"][0][3] == 50 - 40

# 3. wash sale BEFORE (the model's own recent buy): only the replacement share count is disallowed
L = Ledger(10000, R, cost=0)
L.px = {"A": 100.0}
L.buy("A", "A", 1000, 0)
L.px = {"A": 80.0}
L.buy("A", "A", 400, 35)  # 5 shares
old = next(l for l in L.lots["A"] if l[4] == 0)
L.sell([(old, 10)], 40)
assert np.isclose(L.real["st"], -100)  # 5 of 10 shares' loss recognised
rep = L.lots["A"][0]
assert np.isclose(rep[1], 5) and np.isclose(rep[2], 100) and rep[3] == 35 - 40
# and no wash outside 30 days
L = Ledger(10000, R, cost=0)
L.px = {"A": 100.0}
L.buy("A", "A", 1000, 0)
L.px = {"A": 80.0}
L.sell([(L.lots["A"][0], 10)], 40)
L.buy("A", "A", 800, 71)
assert np.isclose(L.real["st"], -200)

# 4. challenger lot order: ST losses, LT losses, LT gains, ST gains; highest basis first
L = Ledger(0, R, cost=0)
L.px = {"A": 100.0}
L.lots["A"] = [["A", 1, 90, 900, 900, 0], ["A", 1, 120, 900, 900, 0], ["A", 1, 110, 0, 0, 0],
               ["A", 1, 80, 0, 0, 0], ["A", 1, 95, 0, 0, 0]]
assert [l[2] for l in L.order("A", "tax", 1000)] == [120, 110, 95, 80, 90]
assert [l[2] for l in L.order("A", "fifo", 1000)][:3] == [110, 80, 95]

# 5. band simulator: band=0 reproduces model.backtest_returns; a 1 pp band trades less
px = prices()
start = px.index[312]
W = lagged(target_weights(px), start)
r0, _ = sim(px, W, pd.Series(0.0, index=px.index), band=0.0)
assert np.allclose(r0.values, backtest_returns(px, W).values, atol=1e-12)
r1, _ = sim(px, W, pd.Series(0.0, index=px.index))
assert abs(r1.sum() - r0.sum()) < 0.5 and not np.allclose(r1, r0)

# 6. decomposed weights reproduce the frozen model; hysteresis gate switches no more often than the frozen gate
w, _ = weights(px)
assert np.allclose(w.mul(gate_frozen(px), axis=0).values, target_weights(px).values, atol=1e-12)
gh, gf = gate_hyst(px), gate_frozen(px)
assert (gh.diff().abs() > 0).sum() <= (gf.diff().abs() > 0).sum()
assert set(gh.unique()) <= {0.5, 1.0}

# 7. VIX episodes: one spike to 50, decay below 30 -> exactly one episode, none re-triggered within 126 sessions
v = pd.Series([20.0] * 10 + [50.0] + [45, 35, 29, 28, 41, 25] + [20.0] * 200, index=pd.bdate_range("2000-01-03", periods=217))
eps, _ = vix_episodes(v)
assert len(eps) == 1 and eps[0] == v.index[13]
print("test_retail_edge: all checks passed")
