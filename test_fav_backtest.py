"""Checks for fav_backtest.py. Run: python test_fav_backtest.py"""
import json

import numpy as np
import pandas as pd

import fav_backtest as F

T = pd.Timestamp


def mk(q="Nuggets vs. Pistons", outs=("Nuggets", "Pistons"), px=("1", "0"), gst="2025-03-01 00:00:00+00", smt="moneyline",
       opened="2025-02-23T05:00:00Z", closed="2025-03-01 04:44:43+00", end="2025-03-08T00:00:00Z", vol=5000):
    return dict(id="m1", question=q, groupItemTitle="", outcomes=json.dumps(list(outs)), outcomePrices=json.dumps(list(px)),
                clobTokenIds=json.dumps(["t0", "t1"]), gameStartTime=gst, sportsMarketType=smt, startDate=opened,
                createdAt=opened, endDate=end, closedTime=closed, volumeNum=vol)


def ev(markets, slug="nba-den-det-2025-02-28", start=None, tags=()):
    return dict(id="e1", slug=slug, title="", start=start, tags=set(tags), markets=markets)


# pnl: buy at 0.90 (+1c), sports 0.05 fee -> fee/share 0.0045
assert abs(F.pnl(0.90, 1, 0.05) - ((1 - 0.91) / 0.91 - 0.0045 / 0.91)) < 1e-12
assert abs(F.pnl(0.90, 0, 0.0) + 1) < 1e-12
assert F.fee_rate("NBA", True, T("2026-07-09", tz="UTC")) == 0.03 and F.fee_rate("NBA", True, T("2026-07-10", tz="UTC")) == 0.05
assert F.fee_rate("geopolitics", False, T("2025-01-01", tz="UTC")) == 0 and F.fee_rate("crypto", False, T("2025-01-01", tz="UTC")) == 0.07

# sports game: decision = start - 2h, team-named outcomes, token0 won
r = F.candidates(ev([mk()]), "NBA", True)
assert len(r) == 1 and r[0]["dec"] == T("2025-02-28 22:00", tz="UTC") and r[0]["y0"] == 1 and r[0]["timing"] == "start-2h"
assert F.candidates(ev([mk(q="Spread: Rams (-1.5)")]), "NFL", True) == []          # props / spreads excluded
assert F.candidates(ev([mk(smt="totals")]), "NFL", True) == []
assert F.candidates(ev([mk(px=("0.5", "0.5"))]), "NBA", True) == []                # 50-50 void excluded
assert F.candidates(ev([mk(vol=10)]), "NBA", True) == []                           # thin
assert F.candidates(ev([mk(gst="2025-02-23 04:00:00+00")]), "NBA", True) == []     # decision before market opened
# no start time: slug date fallback; golf: end - 3d
r = F.candidates(ev([mk(gst=None)]), "NBA", True)
assert r[0]["dec"] == T("2025-02-27 22:00", tz="UTC")
g = mk(q="Will X win the 2025 Open?", outs=("Yes", "No"), px=("0", "1"), gst=None, opened="2025-09-20T00:00:00Z",
       closed="2025-10-05 22:00:00+00", end="2025-10-05T00:00:00Z")
r = F.candidates(ev([g], slug="2025-open-winner"), "golf", True)
assert r[0]["dec"] == T("2025-10-02", tz="UTC") and r[0]["kind"] == "yes" and r[0]["y0"] == 0
# non-sports: scheduled end - 7d; must still be open then
n = mk(q="Will the Fed cut?", outs=("Yes", "No"), gst=None, smt=None, opened="2025-01-01T00:00:00Z",
       closed="2025-03-01 00:00:00+00", end="2025-03-01T00:00:00Z")
assert F.candidates(ev([n], slug="fed"), "economics/Fed", False)[0]["dec"] == T("2025-02-22", tz="UTC")
assert F.candidates(ev([{**n, "closedTime": "2025-02-10 00:00:00+00"}], slug="fed"), "economics/Fed", False) == []

# grouping
assert F.sport_group(dict(slug="epl-ars-che-2025-10-01", title=""), "soccer") == "EPL"
assert F.sport_group(dict(slug="tur-gal-fen-2025-10-01", title=""), "soccer") == "other soccer"
assert F.sport_group(dict(slug="atp-a-b-2025-10-01", title="ATP Challenger Lima: A vs B"), "tennis") == "other tennis"
assert F.sport_group(dict(slug="atp-a-b-2025-10-01", title="Shanghai: A vs B"), "tennis") == "ATP"
assert F.sport_group(dict(slug="next-knicks-coach", title=""), "nba") is None
assert F.nonsport_group(dict(tags={2, 21})) == "crypto" and F.nonsport_group(dict(tags={2, 1})) is None
assert F.nonsport_group(dict(tags={2, 100265})) == "geopolitics" and F.nonsport_group(dict(tags={144, 101206})) == "world elections"

# bets: favourite side folding, range filter
sm = pd.DataFrame(dict(mid=["a", "b", "c"], event=["e", "e", "f"], group="NBA", sports=True, y0=[1, 1, 0],
                       dec=pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"], utc=True), kind="named",
                       p0=[0.90, 0.08, 0.50]))
b = F.bets(sm)
assert list(b.mid) == ["a", "b"] and list(b.won) == [1, 0] and np.allclose(b.p, [0.90, 0.92])

# cluster stats: ROI is the bet-weighted mean; CI covers it; a sure-win sample has p ~ 0
cb = pd.DataFrame(dict(pnl=[0.1, 0.1, -1.0, 0.1] * 50, cluster=np.repeat(np.arange(100), 2)))
roi, lo, hi, p = F.cluster_stats(cb)
assert abs(roi - cb.pnl.mean()) < 1e-12 and lo < roi < hi
assert F.cluster_stats(pd.DataFrame(dict(pnl=np.r_[[0.1] * 99, 0.09], cluster=range(100))))[3] < 1e-6
print("ok")
