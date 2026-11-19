"""Self-checks: no lookahead, weight limits, stats math. Run: python test_model.py"""
import numpy as np
import pandas as pd

from backtest import deflated_sharpe, pbo_cscv, prices
from model import BENCH, EVENT_CAPS, P, backtest_returns, target_weights

px = prices()

# 1. No lookahead: weights at date d must not change when data after d is removed.
for d in px.index[[-400, -150, -20]]:
    full = target_weights(px).loc[d]
    cut = target_weights(px.loc[:d]).loc[d]
    assert np.allclose(full.values, cut.values, atol=1e-12), f"lookahead at {d}"

# 2. Limits: long-only, no leverage, caps respected.
w = target_weights(px)
assert (w >= 0).all().all() and (w.sum(axis=1) <= 1 + 1e-9).all()
for c in w:
    assert (w[c] <= EVENT_CAPS.get(c, P["cap"]) + 1e-12).all(), c
assert px["ANT"].notna().any() or (w["ANT"] == 0).all()  # unlisted name (no prices) never trades
for sz in ("invvol", "hrp"):  # 4. HRP path: same limits, no lookahead
    d = px.index[-150]
    hw = target_weights(px.loc[:d], {**P, "sizing": sz}).loc[d]
    assert np.allclose(target_weights(px, {**P, "sizing": sz}).loc[d], hw, atol=1e-12) and hw.sum() <= 1 + 1e-9

# 3. Stats sanity: pure-noise strategies should look overfit, a real edge should not.
rng = np.random.default_rng(0)
noise = rng.normal(0, 0.01, (2000, 40))
assert pbo_cscv(noise) > 0.3, "PBO should flag noise"
edge = noise + np.linspace(0, 0.002, 40)  # trial j has a real, monotonic edge
assert pbo_cscv(edge) < 0.1, "PBO should pass a real edge"
dsr, _ = deflated_sharpe(pd.Series(noise[:, 0]), noise.mean(0) / noise.std(0))
assert dsr < 0.95, "DSR should reject noise"

# 4. One missing close must not zero a name for 60 days.
holed = px.copy()
holed.loc[holed.index[-30], "AAPL"] = np.nan
assert target_weights(holed)["AAPL"].iloc[-29:].gt(0).all(), "missing close zeroed AAPL"

# 5. Costs: charged on the trade from DRIFTED weights to target, including the first entry from cash.
idx = pd.bdate_range("2020-01-01", periods=50)
flat = pd.DataFrame({"A": 100.0, "B": 50.0, BENCH: 1.0}, index=idx)
w_const = pd.DataFrame({"A": 0.5, "B": 0.5}, index=idx)
cost = -backtest_returns(flat, w_const)  # zero drift: only the entry trade (turnover 1.0 at 5bp) costs anything
assert np.isclose(cost.iloc[0], 5e-4) and np.allclose(cost.iloc[1:], 0), "zero-drift constant weights: entry cost only"
moving = flat.assign(A=100 * 1.01 ** np.arange(50))  # A drifts up 1%/day: holding 50/50 needs a daily rebalance
net = backtest_returns(moving, w_const)
gross = 0.5 * moving["A"].pct_change().fillna(0)
assert ((gross - net).iloc[1:] > 1e-7).all(), "drifting prices must cost something to rebalance"

print("all checks passed")
