"""Self-check for weather_study.py (no network). Run: python test_weather_study.py"""
import math

import numpy as np
import pandas as pd

import weather_study as W


def main():
    # Kalshi fee: ceil to the cent of 0.07*C*P*(1-P)
    assert W.fee(0.5, 100) == 1.75 and W.fee(0.5, 1) == 0.02 and W.fee(0.10, 100) == 0.63 and W.fee(0.01, 1) == 0.01

    # bracket bounds from strike types (integer highs): 'greater 81' -> >= 82, 'less 74' -> <= 73, 'between 78 79'
    m = dict(ticker="X-23JUN10-T81", event_ticker="HIGHNY-23JUN10", result="no", open_time="2023-06-09T14:00:00Z",
             close_time="2023-06-11T03:59:00Z")
    r = W.rec({**m, "strike_type": "greater", "floor_strike": 81}, "NY", True)
    assert r["lo"] == 82 and r["hi"] == np.inf and r["date"] == pd.Timestamp("2023-06-10")
    r = W.rec({**m, "strike_type": "less", "cap_strike": 74}, "NY", True)
    assert r["lo"] == -np.inf and r["hi"] == 73
    r = W.rec({**m, "strike_type": "between", "floor_strike": 78, "cap_strike": 79}, "NY", True)
    assert (r["lo"], r["hi"]) == (78, 79)

    # bracket probabilities: a full partition sums to 1; zero error + tiny kernel puts the mass on the forecast's bracket
    lo, hi = [-np.inf, 70, 72, 74], [69, 71, 73, np.inf]
    p = W.bracket_probs(72.5, np.random.default_rng(0).normal(0, 3, 400), lo, hi)
    assert abs(p.sum() - 1) < 1e-9 and p[1] < p[2]
    p = W.bracket_probs(70.0, np.zeros(100), lo, hi, h=0.1)
    assert p[1] > 0.999
    p = W.bracket_probs(70.0, np.full(100, 3.0), lo, hi, h=0.1)  # forecast runs 3F cold -> high 73
    assert p[2] > 0.999

    # state_at uses only candles closed at or before t; wide spread falls back to last trade; no ask -> nan
    c = np.array([[100, .40, .44, .42, 5], [200, .0, .90, .30, 1], [300, .50, .52, .51, 9]])
    mid, ask, last = W.state_at(c, 250)
    assert mid == .30 and ask == .90 and last == .30
    mid, ask, last = W.state_at(c, 300)
    assert abs(mid - .51) < 1e-12 and ask == .52
    assert all(math.isnan(x) for x in W.state_at(c, 50))
    assert math.isnan(W.state_at(np.array([[1, .99, 1.0, .99, 0]]), 5)[1])

    # implied mean: tails at one degree past the edge; renormalised
    assert abs(W.implied_mean(lo, hi, [0, .5, .5, 0]) - 71.5) < 1e-12
    assert abs(W.implied_mean(lo, hi, [.25, 0, 0, .25]) - 71.5) < 1e-12  # (68 + 75) / 2

    # slot times: 08:00 New York on a summer day = 12:00 UTC; 15:00 LA the day before in winter = 23:00 UTC
    assert W.slot_time(pd.Timestamp("2025-07-01"), "America/New_York", "T2 D 08:00") == pd.Timestamp("2025-07-01 12:00", tz="UTC")
    assert W.slot_time(pd.Timestamp("2025-01-10"), "America/Los_Angeles", "T1 D-1 15:00") == pd.Timestamp("2025-01-09 23:00", tz="UTC")

    # forecast_at: no lookahead (run not yet available), NBS preferred, 36h staleness cap
    t = pd.Timestamp("2025-07-01 12:00", tz="UTC")
    mos = pd.DataFrame(dict(model=["GFS", "NBS", "NBS"], date=pd.Timestamp("2025-07-01"),
                            avail=[t - pd.Timedelta(hours=1), t - pd.Timedelta(hours=3), t + pd.Timedelta(minutes=1)], f=[80., 82., 90.]))
    assert W.forecast_at(mos, pd.Timestamp("2025-07-01"), t) == (82.0, "NBS")
    assert W.forecast_at(mos.iloc[[0]], pd.Timestamp("2025-07-01"), t) == (80.0, "GFS")
    assert math.isnan(W.forecast_at(mos.iloc[[0]], pd.Timestamp("2025-07-01"), t + pd.Timedelta(hours=40))[0])

    # ROI bootstrap: all winners at 0.5 -> ROI ~ +100% minus fee; CI around it
    roi, lo_, hi_, p = W.roi_boot(np.array([48.25] * 30), np.array([51.75] * 30), np.arange(30))
    assert abs(roi - 48.25 / 51.75) < 1e-12 and lo_ <= roi <= hi_ and p < .01

    m_, t_, p_, n_ = W.cluster_t([1, 1, 2, 2, 3, 3], [1, 1, 2, 2, 3, 3])
    assert abs(m_ - 2) < 1e-12 and n_ == 3
    print("ok")


if __name__ == "__main__":
    main()
