"""sports.py self-checks, no network. Run: python test_sports.py"""
import math
import os
import tempfile

import numpy as np
import pandas as pd

import sports as s

# 1. Win-prob formula.
assert s.win_prob(0) == 0.5 and abs(s.win_prob(400) - 10 / 11) < 1e-12 and abs(s.win_prob(-100) + s.win_prob(100) - 1) < 1e-12

# 2. Elo update math (hand-computed). NBA: home 1500 vs away 1500, home wins by 10.
p = s.win_prob(100)
mult = 13 ** 0.8 / (7.5 + 0.006 * 100)
h, a = s.elo_update(1500, 1500, 110, 100, "nba")
assert abs(h - (1500 + 20 * mult * (1 - p))) < 1e-9 and abs(h + a - 3000) < 1e-9  # zero-sum
# NFL: neutral site, away wins by 7; winner's edge = +0 -> mult = ln(8)
h, a = s.elo_update(1500, 1500, 10, 17, "nfl", neutral=True)
assert abs(a - (1500 + 20 * math.log(8) * 0.5)) < 1e-9
# Upset moves more than an expected win of the same margin.
assert s.elo_update(1400, 1600, 20, 10, "nfl")[0] - 1400 > s.elo_update(1600, 1400, 20, 10, "nfl")[0] - 1600

# 3. No lookahead: changing results on/after date d must not change probabilities for games on dates <= d.
rng = np.random.default_rng(0)
teams = list("ABCDEF")
rows = []
for k, d in enumerate(pd.date_range("2020-01-01", periods=60)):
    for j in range(3):  # 3 games per day, incl. same-day games
        hm, aw = rng.choice(teams, 2, replace=False)
        rows.append(dict(date=d.strftime("%Y-%m-%d"), season=2020 + k // 30, home=hm, away=aw,
                         hs=float(rng.integers(80, 120)), as_=float(rng.integers(80, 120)), neutral=False))
g = pd.DataFrame(rows)
p_full, _ = s.walk_forward(g, "nba")
cut = "2020-02-10"
g2 = g.copy()
g2.loc[g2.date >= cut, ["hs", "as_"]] = [[200.0, 50.0]] * int((g2.date >= cut).sum())
p2, _ = s.walk_forward(g2, "nba")
assert np.allclose(p_full[g.date <= cut], p2[g.date <= cut]) and not np.allclose(p_full[g.date > cut], p2[g.date > cut])
# Unplayed games (no score) are priced but never update ratings.
g3 = g.copy()
g3.loc[g3.date >= cut, ["hs", "as_"]] = np.nan
p3, _ = s.walk_forward(g3, "nba")
assert p3.notna().all() and np.allclose(p3[g.date <= cut], p_full[g.date <= cut])
# Season regression: 1/3 toward the mean at the first game of a new season.
_, r_end = s.walk_forward(g[g.season == 2020], "nba")
first = g[g.season == 2021].iloc[0]
exp = s.win_prob((r_end[first.home] - r_end[first.away]) * (2 / 3) + 100)
assert abs(p_full[g[g.season == 2021].index[0]] - exp) < 1e-12

# 4. Price never taken at/after start; prefers start - 2h.
start = pd.Timestamp("2024-01-01 20:00", tz="UTC")
t0 = int(start.timestamp())
hist = [(t0 - 3 * 3600, 0.40), (t0 - 2 * 3600 + 2, 0.42), (t0 - 3600, 0.45), (t0, 0.90), (t0 + 3600, 1.0)]
assert s.price_before(hist, start) == (0.42, t0 - 2 * 3600 + 2)
assert s.price_before(hist[2:], start) == (0.45, t0 - 3600)  # fallback: last point before start
assert np.isnan(s.price_before(hist[3:], start)[0])

# 5. Betting rule, P&L, ledger idempotence and settlement.
assert s.decide(0.60, 0.50, 0.51, 0.51) == ("home", 0.51) and s.decide(0.40, 0.50, 0.51, 0.52) == ("away", 0.52)
assert s.decide(0.54, 0.50, 0.51, 0.51)[0] == ""
assert abs(s.bet_pnl("home", 0.5, 1.0) - 1.0) < 1e-12 and s.bet_pnl("away", 0.4, 1.0) == -1.0
assert abs(s.bet_pnl("away", 0.5, 0.5) - 0.0) < 1e-12  # push / 50-50 resolution returns the stake

now = pd.Timestamp("2026-11-20 12:00", tz="UTC")
cands = [dict(league="nba", slug="nba-bos-nyk-2026-11-20", game_start_utc="2026-11-21T00:30:00+00:00", home="Knicks",
              away="Celtics", p_elo_home=0.62, p_mkt_home=0.50, ask_home=0.51, ask_away=0.51),
         dict(league="nfl", slug="nfl-kc-buf-2026-11-22", game_start_utc="2026-11-22T18:00:00+00:00", home="Bills",
              away="Chiefs", p_elo_home=0.48, p_mkt_home=0.50, ask_home=0.51, ask_away=0.51)]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "ledger.csv")
    s.open_candidates = lambda now: cands
    s.home_payouts = lambda led, now: {}
    s.run_daily(path, now)
    s.run_daily(path, now + pd.Timedelta(hours=3))  # same day again: nothing new
    led = s.read_ledger(path)
    assert len(led) == 2 and led.stake.tolist() == [1.0, 0.0] and led.bet_team.fillna("").tolist() == ["Knicks", ""]
    s.home_payouts = lambda led, now: {"nba-bos-nyk-2026-11-20": 0.0, "nfl-kc-buf-2026-11-22": 1.0}
    later = now + pd.Timedelta(days=3)
    s.run_daily(path, later)
    led = s.read_ledger(path)
    assert abs(led.pnl[0] - (-1.0)) < 1e-12 and led.pnl[1] == 0.0 and led.home_payout.tolist() == [0.0, 1.0]
    s.home_payouts = lambda led, now: {"nba-bos-nyk-2026-11-20": 1.0}  # a later, different answer must not overwrite
    s.run_daily(path, later + pd.Timedelta(days=1))
    led2 = s.read_ledger(path)
    assert led2.pnl.tolist() == led.pnl.tolist() and len(led2) == 2
# Winning away bet at 0.40 pays 1.5 units.
L = s.log_candidates(s.read_ledger("nonexistent.csv"), [dict(cands[1], p_elo_home=0.30, ask_away=0.40)], now)
assert abs(s.settle(L, {"nfl-kc-buf-2026-11-22": 0.0}, now).pnl[0] - 1.5) < 1e-12

# 6. Day-block bootstrap CI brackets the mean.
lo, hi = s.boot_roi(np.r_[np.ones(50), -np.ones(50)] * 0.9, np.repeat(np.arange(25), 4))
assert lo < 0 < hi
print("test_sports: all passed")
