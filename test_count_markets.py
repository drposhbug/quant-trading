"""Self-check for count_markets.py (no network). Run: python test_count_markets.py"""
import numpy as np
import pandas as pd

import count_markets as C


def main():
    # description window: ET noon -> 17:00 UTC (EST), year wrap handled
    d = ("posts on Truth Social between November 10, 12:00 PM ET and November 17, 2026, 12:00 PM ET. For the purposes")
    a, b = C.window(d, pd.Timestamp("2026-11-17", tz="UTC"))
    assert a == pd.Timestamp("2026-11-10 17:00", tz="UTC") and b == pd.Timestamp("2026-11-17 17:00", tz="UTC")
    a, b = C.window("from December 26 12:00 PM ET to January 2, 2026 12:00 PM ET", pd.Timestamp("2026-01-02", tz="UTC"))
    assert a == pd.Timestamp("2025-12-26 17:00", tz="UTC") and b.year == 2026
    a, b = C.window("from July 3 12:00 PM ET to July 10, 2026 12:00 PM ET", pd.Timestamp("2026-07-10", tz="UTC"))
    assert a.hour == 16  # EDT
    assert C.window("asdas", pd.Timestamp("2026-01-01", tz="UTC")) is None

    # bracket titles
    assert C.bounds("<20") == (0, 19) and C.bounds("200+") == (200, np.inf) and C.bounds("20–39") == (20, 39)
    assert C.bounds(" 40-59 ") == (40, 59) and C.bounds(">579") == (580, np.inf) and C.bounds("") is None
    br = [dict(lo=0, hi=19, y=0), dict(lo=20, hi=39, y=1), dict(lo=40, hi=np.inf, y=0)]
    assert C.partition(br) and not C.partition(br[:2]) and not C.partition([dict(br[0], y=1)] + br[1:])

    # rate profile: constant 2/hour -> mu = 2 * L for any L (whole weeks and partial)
    H = np.full(5000, 2)
    assert C.mu_at(H, 1000, 168) == 336 and C.mu_at(H, 1000, 100) == 200
    # profile is hour-of-week: posts only at one hour-of-week position -> counted once per remaining week
    H = np.zeros(5000, int)
    H[np.arange(5, 5000, 168)] = 7
    i = 5 + 168 * 10  # hour i is the busy hour-of-week
    assert C.mu_at(H, i, 1) == 7 and C.mu_at(H, i + 1, 167) == 0 and C.mu_at(H, i, 336) == 14
    # only past data: changing the future cannot change mu or r
    H = np.random.default_rng(0).poisson(3, 6000)
    m0, r0 = C.mu_at(H, 4000, 168), C.size_at(H, 4000, 168)
    H2 = H.copy()
    H2[4000:] = 50
    assert C.mu_at(H2, 4000, 168) == m0 and C.size_at(H2, 4000, 168) == r0
    assert r0 > 50  # Poisson data -> little overdispersion (large size)
    Hb = np.repeat(np.random.default_rng(1).choice([0, 10], 300), 24)  # bursty days -> strong overdispersion
    assert C.size_at(Hb, 5000, 168) < 20
    assert C.size_at(H, 700, 168) is None  # too little history

    # bracket probabilities: partition sums to 1; brackets already passed get 0
    lo, hi = [0, 20, 40, 60], [19, 39, 59, np.inf]
    p = C.bracket_probs(25, 15.0, 5.0, lo, hi)
    assert abs(p.sum() - 1) < 1e-9 and p[0] == 0
    assert np.allclose(C.bracket_probs(25, 0.0, 5.0, lo, hi), [0, 1, 0, 0])

    # betting: fee and P&L per share, first trigger only, ROI
    t = pd.Timestamp("2026-01-01", tz="UTC")
    df = pd.DataFrame(dict(id=["e", "e", "e"], lo=[0, 0, 20], t=[t, t + pd.Timedelta(hours=1), t], p=[.5, .6, .3],
                           ask=[.30, .31, .25], y=[1, 1, 0], venue="polymarket", week="w", b=t))
    bt = C.bets(df)
    assert len(bt) == 1 and bt.ask.iloc[0] == .30  # 2nd row same bracket later; 3rd edge 0.05 < 0.08
    assert abs(bt.cost.iloc[0] - (.30 + .05 * .3 * .7)) < 1e-12 and abs(bt.pnl.iloc[0] - (1 - bt.cost.iloc[0])) < 1e-12
    assert abs(C.fee(.5, "kalshi") - .0175) < 1e-12
    r = C.roi(bt.assign(week=["w1"]))
    assert abs(r[0] - bt.pnl.sum() / bt.cost.sum()) < 1e-12

    # chronological split keeps whole events together
    s = pd.DataFrame(dict(id=list("aabbccddeeffgghhiijj"), b=np.repeat(pd.date_range("2026-01-01", periods=10, tz="UTC"), 2)))
    dev, ho = C.split(s)
    assert set(ho.id) == {"h", "i", "j"} and not set(dev.id) & set(ho.id)
    print("ok")


if __name__ == "__main__":
    main()
