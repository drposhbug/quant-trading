"""Checks for tsm_premium_study.py: premium formula, Taiwan-holiday handling, FX timing, z has no look-ahead, FWL."""
import numpy as np
import pandas as pd

import tsm_premium_study as t


def frame(n=80):
    idx = pd.bdate_range("2024-01-01", periods=n)
    rng = np.random.default_rng(0)
    tw_px = 1000 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    tw = pd.DataFrame({"Close": tw_px, "Adj Close": tw_px, "Volume": 1.0}, index=idx)
    tw.loc[idx[10], "Volume"] = 0                           # Taiwan holiday (Yahoo zero-volume row)
    fx = pd.DataFrame({"Open": 32.0, "Close": 99.0}, index=idx)  # Close must never be used on day D
    us_px = 5 * tw_px / 32.0 * 1.2                           # flat 20% premium
    us = pd.DataFrame({"Open": us_px, "Close": us_px, "Adj Close": us_px}, index=idx)
    return {"2330.TW": tw, "TWD=X": fx, "TSM": us}, idx


def test_premium_and_timing():
    d, idx = frame()
    f = t.premium_frame(d)
    assert np.allclose(f["prem"].dropna(), 0.2)              # uses FX Open (32), not the same-day Close (99)
    assert np.isnan(f.loc[idx[10], "prem"]) and np.isnan(f.loc[idx[10], "tw_ret"])  # holiday dropped


def test_z_no_lookahead():
    s = pd.Series(np.random.default_rng(1).normal(size=200))
    z1 = t.zscore(s)
    s2 = s.copy()
    s2.iloc[150:] += 10
    z2 = t.zscore(s2)
    assert np.allclose(z1.iloc[:150].dropna(), z2.iloc[:150].dropna())
    assert z1.iloc[:60].isna().all() and z1.iloc[60:].notna().all()
    assert np.isclose(z1.iloc[60], (s.iloc[60] - s.iloc[:60].mean()) / s.iloc[:60].std())


def test_fwl_equals_multivariate():
    rng = np.random.default_rng(2)
    x, c = rng.normal(size=500), rng.normal(size=500)
    y = 0.3 * x - 0.7 * c + rng.normal(size=500)
    yr, xr = t.fwl(y, x, c)
    b_fwl = (xr @ yr) / (xr @ xr)
    b_ols = np.linalg.lstsq(np.column_stack([np.ones(500), x, c]), y, rcond=None)[0][1]
    assert np.isclose(b_fwl, b_ols)


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
    print("ok")
