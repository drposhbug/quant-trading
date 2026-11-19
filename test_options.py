"""options_earnings.py against a fake Alpaca. No network. Run: python test_options.py"""
import datetime as dt
import math
import os
import tempfile

import options_earnings as oe

NY = oe.NY
D = dt.date
oe.HOOK = None
oe.AK, oe.AS = "opt-key", "opt-secret"
oe.SK = None
TMP = tempfile.mkdtemp()
oe.TRADES, oe.STATE = os.path.join(TMP, "trades.csv"), os.path.join(TMP, "state.json")
SESS = [D(2026, 11, d) for d in (16, 17, 18, 19, 20, 23, 24, 25, 27, 30)] + [D(2026, 12, d) for d in (1, 2, 3, 4)]


def tv(k):
    return 3 * 0.8 ** abs(k - 100)


def q(m, spread=0.10):
    return {"bp": round(m * (1 - spread / 2), 4), "ap": round(m * (1 + spread / 2), 4)}


EXP = "2026-11-20"
CONTRACTS = [{"symbol": f"NVDA261120{t}{k * 1000:08d}", "type": "call" if t == "C" else "put", "strike_price": str(k),
              "expiration_date": EXP, "open_interest": "500"} for k in range(90, 111) for t in "CP"]
SNAPS = {c["symbol"]: {"latestQuote": q(max(100 - c_k, 0) + tv(c_k) if c["type"] == "call" else max(c_k - 100, 0) + tv(c_k))}
         for c in CONTRACTS for c_k in [int(c["strike_price"])]}

calls, W = [], {}


def reset(**kw):
    calls.clear()
    W.clear()
    W.update(equity="100000", next_close="2026-11-19T16:00:00-05:00", order={"status": "new"}, contracts=CONTRACTS,
             snaps=SNAPS, acct="PA1", stock_acct="PA2", positions=[])
    W.update(kw)


def fake(method, url, key, secret, **kw):
    calls.append((method, url, kw.get("json")))
    p = url.split(".markets", 1)[1]
    if p.endswith("/account"):
        return {"equity": W["equity"], "account_number": W["acct"] if key == "opt-key" else W["stock_acct"]}
    if p.endswith("/clock"):
        return {"is_open": True, "next_close": W["next_close"]}
    if p.endswith("/calendar"):
        return [{"date": d.isoformat()} for d in SESS]
    if p.endswith("/positions"):
        return W["positions"]
    if p.endswith("/options/contracts"):
        return {"option_contracts": W["contracts"]}
    if "/trades/latest" in p:
        return {"trade": {"p": 100.4}}
    if p.startswith("/v1beta1/options/snapshots/"):
        return {"snapshots": W["snaps"]}
    if p.startswith("/v1beta1/options/snapshots"):
        return {"snapshots": {s: W["snaps"][s] for s in kw["params"]["symbols"].split(",")}}
    if method == "POST":
        return {"id": "o1"}
    if method == "GET" and "/orders/" in p:
        return W["order"]
    return None


oe._http = fake
oe.earnings = lambda sym, today: (D(2026, 11, 19), "amc") if sym == "NVDA" else None


def chain():
    return {("C" if c["type"] == "call" else "P", float(c["strike_price"])):
            {"symbol": c["symbol"], "bid": SNAPS[c["symbol"]]["latestQuote"]["bp"],
             "ask": SNAPS[c["symbol"]]["latestQuote"]["ap"], "oi": 500} for c in CONTRACTS}


def posts():
    return [c for c in calls if c[0] in ("POST", "DELETE")]


def at(h, m, day=19):
    return dt.datetime(2026, 11, day, h, m, tzinfo=NY)


# --- strike / wing selection + sizing (0.5% rule)
sp, why = oe.build(chain(), 100.4, 100_000)
assert why is None and sp["strikes"] == [94.0, 100.0, 106.0], (sp, why)  # ATM 100, implied move = 6.0 straddle mid
assert abs(sp["implied_move"] - 6 / 100.4) < 1e-3
c_mid = 6 - 2 * tv(106)
c_nat = 2 * 3 * 0.95 - 2 * tv(106) * 1.05
assert abs(sp["limit_credit"] - (c_mid - 0.1 * (c_mid - c_nat))) < 0.006 and sp["limit_credit"] == 4.39, sp
assert sp["qty"] == math.floor(500 / ((6 - 4.39) * 100)) == 3, sp
assert [l["side"] for l in sp["legs"]] == ["sell", "sell", "buy", "buy"]
assert oe.build(chain(), 100.4, 30_000)[1].startswith("qty < 1")

# --- liquidity skips
ch = chain()
ch[("C", 106.0)] = {**ch[("C", 106.0)], "bid": 0.5, "ask": 1.1}
assert "bid-ask" in oe.build(ch, 100.4, 100_000)[1]
ch = chain()
ch[("P", 100.0)] = {**ch[("P", 100.0)], "oi": 99}
assert "open interest" in oe.build(ch, 100.4, 100_000)[1]

# --- event days: after close -> enter report day; before open -> enter prior session; holiday skipped
assert oe.event_days(D(2026, 11, 19), "amc", SESS) == (D(2026, 11, 19), D(2026, 11, 20))
assert oe.event_days(D(2026, 11, 23), "bmo", SESS) == (D(2026, 11, 20), D(2026, 11, 23))
assert oe.event_days(D(2026, 11, 25), "amc", SESS) == (D(2026, 11, 25), D(2026, 11, 27))  # Thanksgiving

# --- entry time gating: last 30 min only; half day uses the 13:00 close
for now, close, want in [(at(15, 35), "2026-11-19T16:00:00-05:00", 1), (at(15, 25), "2026-11-19T16:00:00-05:00", 0),
                         (at(12, 35), "2026-11-19T13:00:00-05:00", 1), (at(12, 25), "2026-11-19T13:00:00-05:00", 0)]:
    reset(next_close=close)
    st = {}
    oe.run(st, now)
    assert len(posts()) == want, (now, close, posts())
reset()
st = {}
oe.run(st, at(15, 35))
o = posts()[0][2]
assert o["order_class"] == "mleg" and o["limit_price"] == "-4.39" and o["qty"] == "3", o
assert [l["position_intent"] for l in o["legs"]] == ["sell_to_open", "sell_to_open", "buy_to_open", "buy_to_open"]
assert st["spreads"]["NVDA"]["status"] == "entering" and st["spreads"]["NVDA"]["expiry"] == EXP
oe.run(st, at(15, 40))  # same event: decided once, never a second order
assert len(posts()) == 1, posts()

# --- no entry when drawdown > 10%
reset(equity="89000")
st = {"peak_equity": 100_000}
oe.run(st, at(15, 35))
assert not posts() and "NVDA:2026-11-19" in st["done"], posts()
reset(equity="91000")
st = {"peak_equity": 100_000}
oe.run(st, at(15, 35))
assert len(posts()) == 1

# --- one per underlying (state or live option position) and max 4 open
reset(positions=[{"symbol": "NVDA261127C00100000", "asset_class": "us_option"}])
oe.run({}, at(15, 35))
assert not posts()
reset()
oe.run({"spreads": {s: {"status": "entering", "order_id": "x"} for s in "ABCD"}}, at(15, 35))
assert not posts()

# --- fill -> open; exit gating on the reaction day 09:45-10:30
OPEN = {"status": "open", "legs": sp["legs"], "qty": 3, "strikes": sp["strikes"], "expiry": "2026-11-27",
        "entry_day": "2026-11-19", "reaction_day": "2026-11-20", "credit": 4.39, "implied_move": 0.06, "spot": 100.4,
        "max_loss": 161}
reset(order={"status": "filled", "legs": [{"side": "sell", "filled_avg_price": "3"}, {"side": "sell", "filled_avg_price": "3"},
                                           {"side": "buy", "filled_avg_price": "0.8"}, {"side": "buy", "filled_avg_price": "0.8"}]})
st = {"spreads": {"NVDA": {**OPEN, "status": "entering", "order_id": "o1"}}, "done": ["NVDA:2026-11-19"]}
oe.run(st, at(15, 40))
assert st["spreads"]["NVDA"]["status"] == "open" and st["spreads"]["NVDA"]["credit"] == 4.4
for now, want in [(at(9, 40, 20), 0), (at(9, 50, 20), 1), (at(10, 45, 20), 0), (at(9, 50, 19), 0)]:
    reset()
    st = {"spreads": {"NVDA": dict(OPEN)}}
    oe.run(st, now)
    assert len(posts()) == want, (now, posts())
reset()
st = {"spreads": {"NVDA": dict(OPEN)}}
oe.run(st, at(9, 50, 20))
o = posts()[0][2]
assert [l["position_intent"] for l in o["legs"]] == ["buy_to_close"] * 2 + ["sell_to_close"] * 2
assert o["limit_price"] == f"{6 - 2 * tv(106):.2f}", o  # first try: at mid

# --- close before expiry regardless of time (session before 11-27 is 11-25)
reset()
oe.run({"spreads": {"NVDA": dict(OPEN)}}, at(14, 0, 25))
assert len(posts()) == 1
reset()
oe.run({"spreads": {"NVDA": dict(OPEN)}}, at(14, 0, 24))
assert not posts()

# --- unfilled close: cancel, then after 2 tries a marketable limit
reset(order={"status": "new"})
st = {"spreads": {"NVDA": {**OPEN, "status": "closing", "close_order_id": "c1", "close_attempts": 2}}}
oe.run(st, at(10, 0, 20))
assert posts() == [("DELETE", oe.TRADE + "/orders/c1", None)], posts()
reset(order={"status": "canceled"})
oe.run(st, at(10, 5, 20))
assert posts()[0][2]["limit_price"] == f"{2 * 3 * 1.05 - 2 * tv(106) * 0.95:.2f}", posts()  # pay the ask, sell the bid

# --- filled close -> trade logged, spread removed
reset(order={"status": "filled", "legs": [{"side": "buy", "filled_avg_price": "1.5"}, {"side": "buy", "filled_avg_price": "1.0"},
                                           {"side": "sell", "filled_avg_price": "0.2"}, {"side": "sell", "filled_avg_price": "0.3"}]})
st = {"spreads": {"NVDA": {**OPEN, "status": "closing", "close_order_id": "c1"}}}
oe.run(st, at(10, 0, 20))
assert st["spreads"] == {}
row = open(oe.TRADES).read().splitlines()[-1].split(",")
assert row[1] == "NVDA" and float(row[5]) == 2.0 and float(row[6]) == round((4.39 - 2.0) * 300, 2), row

# --- DRY_RUN: nothing sent to the trading API
oe.DRY = True
reset()
oe.run({}, at(15, 35))
reset()
oe.run({"spreads": {"NVDA": dict(OPEN)}}, at(9, 50, 20))
assert not posts(), posts()
oe.DRY = False

# --- same-account refusal
oe.SK, oe.SS = "stock-key", "stock-secret"
reset(acct="PA1", stock_acct="PA1")
assert oe.same_account()
oe.main()
assert not posts() and not [c for c in calls if c[1].endswith("/clock")], calls
reset()
assert not oe.same_account()
oe.SK = "opt-key"
assert oe.same_account()
oe.SK = None
print("all options checks passed")
