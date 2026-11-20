"""Checks for sharp_snapshot_study.py: de-vig, fee/P&L, first-edge selection, Gamma parsing, day bootstrap."""
import numpy as np
import pandas as pd

import sharp_snapshot_study as s


def _rows(league, prices, t="2026-10-01T00:00:00Z"):
    return pd.DataFrame({"snapshot_time": t, "league": league, "home_team": "A", "away_team": "B",
                         "commence_time": "2026-10-02T00:00:00Z", "outcome": list("HDA"[:len(prices)] if len(prices) == 3 else "HA"),
                         "price": prices})


def test_devig_two_and_three_way():
    two = s.devig(_rows("americanfootball_nfl", [0.55, 0.50]))
    assert np.isclose(two.fair.sum(), 1) and np.isclose(two.fair.iloc[0], 0.55 / 1.05)
    three = s.devig(_rows("soccer_epl", [0.5, 0.3, 0.25]))
    assert np.isclose(three.fair.sum(), 1)
    # incomplete soccer set (2 of 3 outcomes) is dropped
    assert s.devig(_rows("soccer_epl", [0.5, 0.3]).assign(outcome=["H", "D"])).empty


def test_pnl_and_fee():
    # win at 0.5 with 5% fee: cost per share 0.5 + 0.05*0.25 = 0.5125
    assert np.isclose(s.pm_pnl(0.5, 1, 0, 0.05), 1 / 0.5125 - 1)
    assert np.isclose(s.pm_pnl(0.5, 0, 0, 0.05), -1)
    assert np.isclose(s.pm_pnl(0.5, 1, 0.01, 0.0), 1 / 0.51 - 1)
    assert list(s.fee_rate(["2026-07-09T10:00:00Z", "2026-07-10T00:00:00Z"])) == [0.03, 0.05]


def test_first_edge_takes_earliest_qualifying_row():
    df = pd.DataFrame({"pm_token_id": ["x", "x", "x", "y"],
                       "snapshot_time": ["t3", "t1", "t2", "t1"], "edge": [0.10, 0.01, 0.04, 0.02]})
    b = s.first_edge(df, 0.03)
    assert list(b.pm_token_id) == ["x"] and b.snapshot_time.iloc[0] == "t2"


def test_parse_gamma_list_dict_and_voids():
    m = {"closed": True, "clobTokenIds": '["a", "b"]', "outcomePrices": '["1", "0"]', "gameStartTime": "g"}
    assert s.parse_gamma([m])["a"]["settle"] == 1.0 and s.parse_gamma([m])["b"]["settle"] == 0.0
    assert s.parse_gamma({"data": [m]})["a"]["settle"] == 1.0
    assert s.parse_gamma({"error": "x"}) == {}
    void = dict(m, outcomePrices='["0.5", "0.5"]')
    assert s.parse_gamma([void])["a"]["settle"] is None
    still_open = dict(m, closed=False)
    assert s.parse_gamma([still_open])["a"]["settle"] is None


def test_boot_ci_covers_mean_and_is_day_clustered():
    pnl = np.r_[np.ones(50), -np.ones(50)]
    m, lo, hi = s.boot_ci(pnl, np.repeat(["d1", "d2"], 50))
    assert m == 0 and lo == -1 and hi == 1     # only two days -> CI spans both extremes
    m, lo, hi = s.boot_ci(np.full(30, 0.2), np.arange(30))
    assert np.isclose(lo, 0.2) and np.isclose(hi, 0.2)


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
    print("ok")
