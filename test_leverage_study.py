"""Self-checks for leverage_study.py: financing/dividend math, drawdown duration, rolling 10y, recovery, no lookahead.
Run: python test_leverage_study.py"""
import numpy as np
import pandas as pd

from leverage_study import ENG, boot_paths, const_w, engine_w, frame, recovery, roll10, run, underwater_years

idx = pd.bdate_range("2000-01-03", periods=600)
flat = pd.Series(100.0, index=idx)
px = frame(flat)
rf = pd.Series(0.04 / 252, index=idx)

# 1. Flat price: 2x pays (rf + spread) on 1 unit borrowed, 0.5x earns rf on half, 1x earns only the dividend.
r2 = run(px, const_w(px, 2.0, idx[0]), rf, 0.015, 0.0)
assert np.allclose(r2.iloc[1:], -(0.04 + 0.015) / 252)
r05 = run(px, const_w(px, 0.5, idx[0]), rf, 0.015, 0.0)
assert np.allclose(r05.iloc[1:], 0.5 * 0.04 / 252)
r1 = run(px, const_w(px, 1.0, idx[0]), rf, 0.015, 0.0, dy=0.03)
assert np.allclose(r1.iloc[1:], 0.03 / 252)
# entry cost on day 0, nothing earned before the first close
assert np.isclose(run(px, const_w(px, 2.0, idx[0]), rf, 0.0, 10.0).iloc[0], -2 * 10 / 1e4 + 0.04 / 252)  # still in cash

# 2. Underwater: -10% then back after exactly 100 business days -> duration in years.
r = pd.Series(0.0, index=idx)
r.iloc[10] = -0.1
r.iloc[110] = 1 / 0.9 - 1
assert np.isclose(underwater_years(r), (idx[109] - idx[9]).days / 365.25)  # peak to last day under
rec, depth = recovery(r, "2000-01-03", "2000-01-14")
assert np.isclose(rec, (idx[110] - idx[9]).days / 365.25) and np.isclose(depth, -0.1)

# 3. Rolling 10y CAGR of a constant 5%/yr compounding series is 5%.
d = pd.bdate_range("1990-01-01", "2012-12-31")
c = pd.Series(1.05 ** (1 / 261), index=d) - 1
assert np.allclose(roll10(c), 0.05, atol=0.002)

# 4. Engine weights: no lookahead, gross <= L, zero before start.
rng = np.random.default_rng(1)
s = pd.Series(100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, 900))), index=pd.bdate_range("2001-01-01", periods=900))
p = frame(s)
w = engine_w(p, 1.5, p.index[252])
cut = engine_w(p.iloc[:700], 1.5, p.index[252])
assert np.allclose(w.iloc[:700].values, cut.values)
assert (w.sum(axis=1) <= 1.5 + 1e-9).all() and (w.iloc[:252] == 0).all().all() and w.iloc[300:].sum(axis=1).gt(0).all()
assert ENG["vol_target"] == 0.20 and ENG["regime_ma"] == 200  # frozen params

# 5. Bootstrap paths: shape and range.
bp = boot_paths(50, 30, 10, 5, rng)
assert bp.shape == (10, 30) and bp.min() >= 0 and bp.max() < 50
print("ok")
