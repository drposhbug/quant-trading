"""Self-check for maker_sim.py (no network). Run: python test_maker_sim.py"""
import numpy as np

import maker_sim as M


def main():
    # book: forward-filled 1-min candles, only candles closed at or before t; wide spread -> last trade
    c = np.array([[60, .40, .42, .41, 1], [120, np.nan, np.nan, .45, 1], [180, .30, .50, .44, 1]])
    b, a, m = M.book(c, [59, 60, 130, 200])
    assert np.isnan(m[0]) and abs(m[1] - .41) < 1e-9 and abs(m[2] - .41) < 1e-9 and abs(m[3] - .44) < 1e-9

    # quotes: mid 0.505, h=2c -> bid floor(0.485)=0.48, ask ceil(0.525)=0.53
    cand = np.array([[0, .50, .51, .50, 1]])
    T0, T1 = 100.0, 100.0 + M.STEP  # one quote interval
    # trade AT the bid (not through), trade at quote time, then trade-through of 30 -> fill 10 (queue 0.5 x 30 = 15, cap 10)
    tr = np.array([[100.0, .40, 100], [150, .48, 100], [160, .47, 30], [170, .46, 30]])
    f, posted = M.simulate(tr, cand, [0.505], T0, T1)
    assert posted == 20 and len(f) == 1 and f[0, 1] == 1 and f[0, 2] == 10 and f[0, 3] == .48 and f[0, 0] == 160
    # partial fills accumulate in time order; ask side symmetric
    tr = np.array([[150, .54, 4], [160, .55, 8]])
    f, _ = M.simulate(tr, cand, [0.505], T0, T1)
    assert list(f[:, 2]) == [2, 4] and (f[:, 1] == -1).all() and (f[:, 3] == .53).all()
    # post-only: a bid that would cross the best ask is not posted
    f, posted = M.simulate(np.empty((0, 3)), cand, [0.60], T0, T1)
    assert posted == 10  # ask only
    # maker fee per order, ceil to the cent: 10 @ 0.48 x 0.0175 = 0.04368 -> 0.05
    tr = np.array([[160, .47, 30]])
    f, _ = M.simulate(tr, cand, [0.505], T0, T1, fee_mult=1.0)
    assert abs(f[:, 4].sum() - 0.05) < 1e-12

    # inventory cap and skew: keep buying -> never above 50; skew lowers quotes
    cand2 = np.array([[0, .30, .70, .50, 1]])
    grid_n = 8
    tr = np.array([[100 + k * M.STEP + 1, .01, 1000] for k in range(grid_n)])
    f, _ = M.simulate(tr, cand2, [0.5] * grid_n, 100, 100 + grid_n * M.STEP)
    inv = np.cumsum(f[:, 1] * f[:, 2])
    assert inv.max() == 50 and list(f[:, 3][:4]) == [.48, .47, .47, .46]  # 0.5c/10 contracts skew, floored to the tick

    # capital: buy 10 @ .40 (cap 4.0), sell 20 @ .60 -> short 10, cap max(4, 10 x 0.4) = 4; then sell 10 more @ .70 -> 20 short avg .65
    f = np.array([[1, 1, 10, .40, 0], [2, -1, 20, .60, 0], [3, -1, 10, .70, 0]])
    assert abs(M.capital(f) - 20 * (1 - .65)) < 1e-9

    # score: decomposition adds up (spread + AS settlement - fee = P&L)
    f = np.array([[100, 1, 10, .48, .05], [200, -1, 5, .53, 0]])
    s = M.score(f, cand, 1, 1.0)
    assert abs(s["spread"] + s["asS"] - s["fees"] - s["pnl"]) < 1e-9 and abs(s["pnl"] - (10 * .52 - 5 * .47 - .05)) < 1e-9

    # team matching for the Pinnacle join
    assert M.team_match("Los Angeles R", "Los Angeles Rams") and not M.team_match("Los Angeles R", "Los Angeles Chargers")
    assert M.team_match("Chicago WS", "Chicago White Sox") and not M.team_match("Chicago C", "Chicago White Sox")
    assert M.team_match("A's", "Athletics")
    print("ok")


if __name__ == "__main__":
    main()
