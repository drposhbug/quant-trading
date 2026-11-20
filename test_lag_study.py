"""lag_study.py pure pieces (fair value, runs, paper rule, cluster bootstrap). No network. Run: python test_lag_study.py"""
import numpy as np

from lag_study import cluster_boot, fair, runs, simulate


def test_fair():
    assert abs(fair(np.array([100.0]), 100.0, 0.02, np.array([195]))[0] - 0.5) < 1e-12
    hi, lo = fair(np.array([101.0, 101.0]), 100.0, 0.02, np.array([390, 30]))
    assert 0.5 < hi < lo < 1  # same lead, less time left -> more certain
    assert np.isnan(fair(np.array([101.0]), 100.0, 0.02, np.array([0]))[0])


def test_runs():
    assert list(runs(np.array([1, 1, 0, 1, 0, 0, 1, 1, 1], bool))) == [2, 1, 3]
    assert len(runs(np.zeros(5, bool))) == 0


def test_simulate_hold_to_resolution():
    p, f = np.full(389, 0.50), np.full(389, 0.60)  # fair 10pp above PM all day
    t = simulate(p, f, y=1.0, c=0.02)
    assert t["side"] == 1 and t["m"] == 2 and abs(t["price"] - 0.52) < 1e-12  # next-minute fill at ask
    assert not t["exited"] and abs(t["pnl"] - (1 / 0.52 - 1)) < 1e-12
    assert simulate(p, f, y=0.0, c=0.02)["pnl"] == -1.0


def test_simulate_down_side_and_exit():
    p, f = np.full(389, 0.60), np.full(389, 0.50)
    f[100:] = 0.605  # gap closes at minute 101 (index 100) -> sell at next minute's bid
    t = simulate(p, f, y=1.0, c=0.01)
    assert t["side"] == -1 and abs(t["price"] - 0.41) < 1e-12  # buy Down at 1 - bid = 1 - 0.59
    assert t["exited"] and abs(t["pnl"] - ((1 - 0.61) / 0.41 - 1)) < 1e-12


def test_simulate_no_trade_late_or_small():
    p, f = np.full(389, 0.50), np.full(389, 0.54)  # 4pp minus 2c cost: no trade
    assert simulate(p, f, 1.0, 0.02) is None
    f = np.full(389, 0.50)
    f[365:] = 0.9  # big gap but T < 30
    assert simulate(p, f, 1.0, 0.02) is None


def test_cluster_boot():
    x = np.r_[np.full(50, 0.1), np.full(50, 0.12)]
    m, lo, hi, p = cluster_boot(x, np.repeat(np.arange(10), 10), B=500)
    assert lo <= m <= hi and p < 0.01


if __name__ == "__main__":  # python test_lag_study.py (no pytest in the venv)
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all tests ok")
