"""Self-check for event_odds_study.py (no network). Run: python test_event_odds_study.py"""
import numpy as np
import pandas as pd

import event_odds_study as E

T = pd.Timestamp("2025-06-18 14:00", tz=E.NY)


def legs(xs, ys, p, typ="FOMC", src="kalshi"):
    return pd.DataFrame(dict(src=src, type=typ, event="e", T=T, tk="", x=xs, y=ys, p_1d=p, p_1h=p, p_5m=p, id=list(map(str, xs))))


def main():
    assert [E.fed_bp(t) for t in ("X-H0", "X-H25", "X-C25", "X-C26", "X-H>25", "X-T0.3")][:5] == [0, 25, -25, -50, 50]
    assert np.isnan(E.fed_bp("X-T0.3")) and E.strike("KXCPI-26SEP-T0.4") == 0.4

    # FOMC: 80% hold, 20% cut 25 -> E = -5bp; outcome cut -> surprise -20bp. Probabilities are renormalised.
    r = E.summarize(legs([-25, 0, 25], [1, 0, 0], [0.2, 0.8, 0.0]))
    assert abs(r["E_5m"] + 5) < 1e-9 and abs(r["S"] + 20) < 1e-9
    r = E.summarize(legs([-25, 0, 25], [1, 0, 0], [0.1, 0.4, 0.0]))  # sums to 0.5 -> same after renormalising
    assert abs(r["E_5m"] + 5) < 1e-9

    # CPI ladder 'above k': printed 0.3 -> T0.1, T0.2 yes, T0.3 no. Market P(above)=[.9,.5,.1] -> S = .1*(.1+.5-.1)=.05
    r = E.summarize(legs([0.1, 0.2, 0.3], [1, 1, 0], [0.9, 0.5, 0.1], typ="CPI"))
    assert abs(r["S"] - 0.05) < 1e-9 and abs(r["X"] - 0.3) < 1e-9

    # rule: odds turned dovish (E fell) but SPY drifted down -> long; same direction -> no trade; tiny drift -> no trade
    d = pd.DataFrame(dict(E_1d=[0, 0, 0], E_5m=[-5, -5, -0.1], drift=[-0.01, 0.01, -0.01], hold=[0.002, 0.002, 0.002]))
    rr = E.rule_returns(d, "FOMC", "hold", "drift")
    assert abs(rr[0] - (0.002 - 4e-4)) < 1e-12 and np.isnan(rr[1]) and np.isnan(rr[2])

    # px_at never uses the bar that starts at t (it closes after t)
    b = pd.DataFrame(dict(ts=pd.date_range("2025-06-18 13:58", periods=3, freq="1min", tz=E.NY), open=[1., 2, 3], close=[1., 2, 3]))
    assert E.px_at(b, T) == 2.0

    x = np.arange(20.)
    b1, t, p, n = E.ols(2 * x + np.sin(x), x)
    assert abs(b1 - 2) < 0.1 and p < 1e-6 and n == 20
    m, t, p, n = E.mean_t([1, 2, 3, np.nan])
    assert m == 2 and n == 3
    print("selfcheck ok")


if __name__ == "__main__":
    main()
