"""Checks for combo_study.py. Run: python test_combo_study.py"""
import numpy as np
import pandas as pd

import combo_study as C

# fees: 0.07*.5*.5 = 1.75c -> 2c per contract; tiny tails still cost a full cent per contract
assert C.taker_fee_contract(0.5) == 0.02 and C.taker_fee_contract(0.999) == 0.01 and C.taker_fee_contract(1.0) == 0
assert abs(C.taker_fee_order(0.99, 1000) - 0.70 / 1000) < 1e-12          # 0.07*1000*.99*.01 = 0.693 -> 70c
assert C.maker_fee(0.9, pd.Timestamp("2026-08-01", tz="UTC")) == 0
assert abs(C.maker_fee(0.9, pd.Timestamp("2026-09-01", tz="UTC")) - 0.035 * 0.09) < 1e-12
# roi: NO at 0.99 + 1c fee; combo misses (NO pays 1) -> 0; hits -> -1
assert abs(C.roi(0.99, 1, 0.01)) < 1e-12 and abs(C.roi(0.99, 0, 0.01) + 1) < 1e-12 and abs(C.roi(0.8, 1, 0) - 0.25) < 1e-12
# candle mids: live *_dollars, historical plain, cents, one-sided
assert abs(C.mid({"yes_bid": {"close_dollars": "0.40"}, "yes_ask": {"close_dollars": "0.44"}}) - 0.42) < 1e-12
assert abs(C.mid({"yes_bid": {"close": "59"}, "yes_ask": {"close": "61"}}) - 0.60) < 1e-12
assert np.isnan(C.mid({"yes_bid": {"close": "0.5"}, "yes_ask": {"close": "0.5"}}))
cs = [{"end_period_ts": 100, "yes_bid": {"close": "0.2"}, "yes_ask": {"close": "0.3"}},
      {"end_period_ts": 200, "yes_bid": {"close": "0.6"}, "yes_ask": {"close": "0.7"}}]
assert abs(C.leg_price(cs, 150, "yes") - 0.25) < 1e-12 and abs(C.leg_price(cs, 250, "no") - 0.35) < 1e-12   # no look-ahead, NO side
assert np.isnan(C.leg_price(cs, 99, "yes")) and np.isnan(C.leg_price(cs, 200 + 3601, "yes"))     # none before / stale
# categories and same-event
L = lambda *e: [{"event_ticker": x} for x in e]
assert C.combo_cat(L("KXNFLGAME-26NOV19INDHOU", "KXNFLTD-26NOV19INDHOU")) == "NFL"
assert C.combo_cat(L("KXBTC15M-26NOV200145", "KXETH15M-26NOV200145")) == "crypto 15m"
assert C.combo_cat(L("KXNFLGAME-26NOV19INDHOU", "KXNBAGAME-26NOV19LALBOS")) == "mixed"
assert C.same_event(L("KXNFLGAME-26NOV19INDHOU", "KXNFLTEAMFIRSTTD-26NOV19INDHOU-HOU"))
assert C.same_event(L("KXBTC15M-26NOV200145", "KXETH15M-26NOV200145"))
assert not C.same_event(L("KXNFLGAME-26NOV19INDHOU", "KXNFLGAME-26NOV22MIABUF"))
# day-clustered bootstrap: CI covers the mean, wider when one day dominates
m, lo, hi = C.day_boot([1, 1, 0, 0], ["a", "a", "b", "b"])
assert m == 0.5 and lo == 0 and hi == 1
# drawdown and streaks
assert C.max_dd([0.01, 0.01, -1, 0.01]) == -1 and C.max_dd([-1, 0.5]) == -1
assert C.worst_streak([1, 1, 0, 1, 1, 1]) == 3
# windows are reproducible and inside each day
w = C.windows()
assert w == C.windows() and len(w) == C.PER_DAY * ((C.END - C.START).days + 1)
print("ok")
assert C.day_boot([1, 0], ["a", "b"], w=[3, 1])[0] == 0.75
print("ok weighted")
