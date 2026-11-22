"""Earnings iron-butterfly SEPARATE EXPERIMENT in the SECOND Alpaca paper account (ALPACA_OPT_* keys).
Does not touch the frozen stock model (MATH.md change control) or its account. Run by monitor.yml after monitor.py.

Pre-registered (implemented exactly, nothing tuned):
  Events  yfinance Ticker.calendar "Earnings Date"; timing from get_earnings_dates (time < 09:30 ET -> before open,
          else / unknown / 00:00 -> after close). Entry session = last session before the reaction session.
  Entry   last 30 min of the entry session. Nearest expiry on/after the reaction day (<= 7 calendar days).
          Short ATM call + put (strike nearest spot), long wings at strikes nearest spot +/- implied move
          (implied move = ATM straddle mid). One mleg limit order at the NATURAL credit minus $0.05 (changed 2026-11-19, before any trade: Alpaca paper fills
          only marketable orders, so P&L is measured at worst-case fills).
Go-live rule (pre-committed): no real money until ~120 closed trades show a positive average P&L at these fills
(reports/Options math and strategy.md: expected result ~0 to slightly negative; ~120 trades to detect a 0.1 edge).
          qty = floor(0.5% equity / max loss), max loss = (wider wing - credit) x 100. Skip if qty < 1, any leg's
          bid-ask > 20% of its mid, or any leg's open interest < 100.
  Exit    reaction session 09:45-10:30 ET: mleg limit at mid (2 tries), then marketable limit. Also closed on the
          session before expiry (and on expiry day) regardless: never held through expiry.
  Limits  one spread per underlying, max 4 open, no new entries if account drawdown from peak > 10%.
Safety (2026-11-19, not part of the measured rule): partial entry fills keep the filled quantity; closes size to the
legs actually held in /positions; on/after expiry day any remaining spread is closed at once at a marketable limit
(Discord alert); every run alerts once on any option position not in state.
DRY_RUN=1: logs intended orders, sends nothing to the trading API, saves no state, prints instead of Discord.
"""
import csv
import datetime as dt
import json
import math
import os
import re
import zoneinfo

import requests
import yfinance as yf

from model import UNIVERSE

NY = zoneinfo.ZoneInfo("America/New_York")
STATE = "options_state.json"
TRADES = "signals/options_trades.csv"
HOOK = os.environ.get("DISCORD_WEBHOOK_URL")
AK, AS = os.environ.get("ALPACA_OPT_API_KEY"), os.environ.get("ALPACA_OPT_SECRET_KEY")
SK, SS = os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET_KEY")  # stock-model account: only to refuse if same
TRADE = "https://paper-api.alpaca.markets/v2"  # paper only, hard-coded on purpose
DATA = "https://data.alpaca.markets"
DRY = os.environ.get("DRY_RUN") == "1"
# RISK 0.005 -> 0.02 on 2026-11-21 (owner): at $500 one contract's max loss ($600-1,950) skipped most of the universe
RISK, MAX_OPEN, MAX_DD, MAX_SPREAD, MIN_OI, MAX_DAYS = 0.02, 4, 0.10, 0.20, 100, 7
EXIT_FROM, EXIT_TO = dt.time(9, 45), dt.time(10, 30)
DEAD = ("canceled", "expired", "rejected", "done_for_day")


def discord(msg):
    if DRY or not HOOK:
        print(msg)
        return
    try:
        requests.post(HOOK, json={"content": msg[:1990]}, timeout=10).raise_for_status()
    except requests.RequestException as e:  # str(e) can contain the webhook URL (public logs)
        print("discord failed:", type(e).__name__)


def _http(method, url, key, secret, **kw):
    r = requests.request(method, url, timeout=15, **kw, headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})
    r.raise_for_status()
    return r.json() if r.text else None


def alpaca(method, path, **kw):
    if DRY and method != "GET":
        print(f"DRY_RUN would {method} {path} {json.dumps(kw.get('json'))}")
        return None
    return _http(method, TRADE + path, AK, AS, **kw)


def data(path, **params):
    return _http("GET", DATA + path, AK, AS, params=params)


def same_account():
    """True if the options keys point at the stock model's account. Unknown stock account -> only key comparison."""
    if not SK:
        return False
    if SK == AK:
        return True
    return alpaca("GET", "/account")["account_number"] == _http("GET", TRADE + "/account", SK, SS)["account_number"]


# ---------------------------------------------------------------- calendar
def earnings(sym, today):
    """(report date, 'bmo'|'amc') of the next report on/after today, or None. Fails soft."""
    try:
        d = min(x for x in (yf.Ticker(sym).calendar or {}).get("Earnings Date") or [] if x >= today)
    except Exception:
        return None
    timing = "amc"  # unknown -> after close
    try:
        for ts in yf.Ticker(sym).get_earnings_dates(limit=8).index:
            ts = ts.tz_convert(NY)
            if ts.date() == d and dt.time(0, 0) < ts.time() < dt.time(9, 30):  # 00:00 = no time given
                timing = "bmo"
    except Exception:
        pass
    return d, timing


def event_days(report, timing, sess):
    """(entry session, reaction session) from the report date and timing; sess = sorted trading dates."""
    entry = max(s for s in sess if (s < report if timing == "bmo" else s <= report))
    return entry, min(s for s in sess if s > entry)


def sessions(today):
    cal = alpaca("GET", "/calendar", params={"start": (today - dt.timedelta(days=14)).isoformat(),
                                              "end": (today + dt.timedelta(days=30)).isoformat()})
    return sorted(dt.date.fromisoformat(c["date"]) for c in cal)


def close_due(sp, now, sess):
    d, exp = now.date(), dt.date.fromisoformat(sp["expiry"])
    if d <= dt.date.fromisoformat(sp["entry_day"]):
        return False
    if d >= max(s for s in sess if s < exp):  # session before expiry, or expiry day itself
        return True
    return d >= dt.date.fromisoformat(sp["reaction_day"]) and EXIT_FROM <= now.time() <= EXIT_TO


# ---------------------------------------------------------------- spread construction
def mid(q):
    return (q["bid"] + q["ask"]) / 2


def build(chain, spot, equity):
    """chain: {(type 'C'|'P', strike): {symbol, bid, ask, oi}}. Returns (spread dict, None) or (None, skip reason)."""
    both = sorted({k for t, k in chain if t == "C"} & {k for t, k in chain if t == "P"})
    if not both:
        return None, "no chain"
    atm = min(both, key=lambda k: abs(k - spot))
    sc, sp_ = chain[("C", atm)], chain[("P", atm)]
    im = mid(sc) + mid(sp_)
    calls = [k for t, k in chain if t == "C" and k > atm]
    puts = [k for t, k in chain if t == "P" and k < atm]
    if not calls or not puts:
        return None, "no wing strikes"
    kc, kp = min(calls, key=lambda k: abs(k - (spot + im))), min(puts, key=lambda k: abs(k - (spot - im)))
    lc, lp = chain[("C", kc)], chain[("P", kp)]
    legs = [(sc, "sell"), (sp_, "sell"), (lc, "buy"), (lp, "buy")]
    for q, _ in legs:
        if q["oi"] < MIN_OI:
            return None, f"{q['symbol']} open interest {q['oi']} < {MIN_OI}"
        if mid(q) <= 0 or q["ask"] - q["bid"] > MAX_SPREAD * mid(q):
            return None, f"{q['symbol']} bid-ask {q['bid']}/{q['ask']} > 20% of mid"
    c_mid = sum(mid(q) * (1 if s == "sell" else -1) for q, s in legs)
    c_nat = sc["bid"] + sp_["bid"] - lc["ask"] - lp["ask"]
    # Entry at the natural price minus $0.05: Alpaca paper fills only marketable orders (at NBBO), and the free
    # 'indicative' quotes may lag, so a mid-ish limit would rarely fill. Changed 2026-11-19 before any trade;
    # P&L is therefore measured at worst-case fills (conservative).
    credit = round(c_nat - 0.05, 2)
    max_loss = (max(kc - atm, atm - kp) - credit) * 100
    if credit <= 0 or max_loss <= 0:
        return None, f"bad credit {credit}"
    qty = math.floor(RISK * equity / max_loss)
    if qty < 1:
        return None, f"qty < 1 (max loss ${max_loss:,.0f}/contract)"
    return dict(legs=[{"symbol": q["symbol"], "side": s} for q, s in legs], strikes=[kp, atm, kc], qty=qty,
                limit_credit=credit, mid_credit=round(c_mid, 4), implied_move=round(im / spot, 4), spot=spot,
                max_loss=round(max_loss, 2)), None


def spot_price(sym):
    return float(data(f"/v2/stocks/{sym}/trades/latest", feed="iex")["trade"]["p"])  # free plan: no recent SIP


def quotes(symbols):
    snaps = data("/v1beta1/options/snapshots", symbols=",".join(symbols), feed="indicative")["snapshots"]
    return {s: {"bid": float(snaps[s]["latestQuote"]["bp"]), "ask": float(snaps[s]["latestQuote"]["ap"])} for s in symbols}


def get_chain(sym, reaction):
    """Nearest expiry on/after the reaction day within 7 calendar days -> (expiry, chain) or (None, {})."""
    cs = alpaca("GET", "/options/contracts", params={
        "underlying_symbols": sym, "expiration_date_gte": reaction.isoformat(), "status": "active",
        "expiration_date_lte": (reaction + dt.timedelta(days=MAX_DAYS)).isoformat(), "limit": 10000})["option_contracts"]
    if not cs:
        return None, {}
    exp = min(c["expiration_date"] for c in cs)
    cs = {c["symbol"]: c for c in cs if c["expiration_date"] == exp and c.get("tradable", True)}
    snaps, token = {}, None
    while True:
        p = {"feed": "indicative", "expiration_date": exp, "limit": 1000, **({"page_token": token} if token else {})}
        r = data(f"/v1beta1/options/snapshots/{sym}", **p)
        snaps.update(r.get("snapshots") or {})
        if not (token := r.get("next_page_token")):
            break
    chain = {}
    for s, c in cs.items():
        q = (snaps.get(s) or {}).get("latestQuote")
        if q:
            chain[(c["type"][0].upper(), float(c["strike_price"]))] = {
                "symbol": s, "bid": float(q["bp"]), "ask": float(q["ap"]), "oi": int(float(c.get("open_interest") or 0))}
    return exp, chain


def plan(sym, reaction, equity):
    exp, chain = get_chain(sym, reaction)
    if not chain:
        return None, f"no listed expiry within {MAX_DAYS} days of {reaction}"
    sp, why = build(chain, spot_price(sym), equity)
    if sp:
        sp["expiry"] = exp
    return sp, why


# ---------------------------------------------------------------- orders
def mleg(legs, qty, price, opening):
    """price > 0 debit, < 0 credit (Alpaca mleg convention)."""
    intent = {("sell", True): "sell_to_open", ("buy", True): "buy_to_open", ("sell", False): "sell_to_close",
              ("buy", False): "buy_to_close"}
    return alpaca("POST", "/orders", json={
        "order_class": "mleg", "qty": str(qty), "type": "limit", "limit_price": f"{price:.2f}", "time_in_force": "day",
        "legs": [{"symbol": l["symbol"], "ratio_qty": "1", "side": l["side"], "position_intent": intent[(l["side"], opening)]}
                 for l in legs]})


def net_fill(o, sell_positive):
    """Net per-spread price from leg fills (credit if sell_positive), falling back to |filled_avg_price|."""
    try:
        return round(sum(float(l["filled_avg_price"]) * (1 if (l["side"] == "sell") == sell_positive else -1)
                         for l in o["legs"]), 4)
    except (KeyError, TypeError, ValueError):
        return abs(float(o["filled_avg_price"]))


def held_qty():
    """{option symbol: absolute contracts held} from live /positions."""
    return {p["symbol"]: abs(int(float(p["qty"]))) for p in alpaca("GET", "/positions") or []
            if p.get("asset_class") == "us_option"}


def submit_close(sym, sp, state, force=False):
    held = held_qty()
    n = [held.get(l["symbol"], 0) for l in sp["legs"]]
    if not any(n):  # nothing left (closed by hand, expired, assigned): stop tracking it
        del state["spreads"][sym]
        discord(f"🦋 {sym} iron fly: no legs held any more, dropped from state (check fills/assignment by hand)")
        return
    if len(set(n)) > 1:
        discord(f"⚠️ {sym} iron fly legs held unevenly {n}: closing {min(n) or max(n)} as a spread, CHECK BY HAND")
    sp["qty"] = min(n) or max(n)  # ponytail: uneven legs closed as one mleg; fix leftovers by hand (alerted above)
    q = quotes([l["symbol"] for l in sp["legs"]])
    short = {l["symbol"]: l["side"] == "sell" for l in sp["legs"]}
    marketable = force or sp.get("close_attempts", 0) >= 2
    debit = sum((q[s]["ask"] if marketable else mid(q[s])) if sh else -(q[s]["bid"] if marketable else mid(q[s]))
                for s, sh in short.items())
    legs = [{"symbol": l["symbol"], "side": "buy" if l["side"] == "sell" else "sell"} for l in sp["legs"]]
    o = mleg(legs, sp["qty"], round(debit, 2), opening=False)
    sp["close_attempts"] = sp.get("close_attempts", 0) + 1
    sp["status"], sp["close_order_id"] = "closing", (o or {}).get("id")


def log_trade(sym, sp, debit, exit_spot, qty):
    pnl = round((sp["credit"] - debit) * 100 * qty, 2)
    new = not os.path.exists(TRADES)
    os.makedirs(os.path.dirname(TRADES), exist_ok=True)
    with open(TRADES, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "symbol", "expiry", "qty", "credit", "debit", "pnl", "implied_move", "realized_move"])
        w.writerow([dt.datetime.now(NY).date().isoformat(), sym, sp["expiry"], qty, sp["credit"], debit, pnl,
                    sp["implied_move"], round(abs(exit_spot / sp["spot"] - 1), 4)])
    return pnl


def filled(o):
    return int(float(o.get("filled_qty") or 0))


def manage(state, sym, sp, now, sess):
    if sp["status"] == "entering":
        o = alpaca("GET", f"/orders/{sp['order_id']}")
        if o["status"] == "filled" or (o["status"] in DEAD and filled(o) > 0):  # partial fill: keep what filled
            sp["qty"] = filled(o) or sp["qty"]
            sp["credit"], sp["status"] = net_fill(o, True), "open"
            discord(f"🦋 **{sym} iron fly opened** {sp['qty']}x {'/'.join(f'{k:g}' for k in sp['strikes'])} "
                    f"exp {sp['expiry']} credit ${sp['credit']:.2f} (implied move {sp['implied_move']:.1%}, "
                    f"max loss ${sp['max_loss'] * sp['qty']:,.0f})")
        elif o["status"] in DEAD:
            del state["spreads"][sym]
            discord(f"🦋 {sym} iron fly entry not filled ({o['status']})")
        return
    expiring = now.date() >= dt.date.fromisoformat(sp["expiry"])
    if sp["status"] == "closing":
        get = lambda: alpaca("GET", f"/orders/{sp['close_order_id']}") if sp.get("close_order_id") else {"status": "canceled"}
        o = get()
        if o["status"] not in ("filled", *DEAD):  # still working: cancel, and resubmit only once the cancel is final
            alpaca("DELETE", f"/orders/{sp['close_order_id']}")
            if (o := get() or {"status": "?"})["status"] not in DEAD:
                return  # no double close; next run retries
        n = filled(o) or (sp["qty"] if o["status"] == "filled" else 0)
        if n:  # (partial) close fill: book it; partial fills from earlier close orders are averaged in
            sp["closed"] = sp.get("closed", []) + [[n, net_fill(o, False)]]
        if o["status"] == "filled":
            qty = sum(c[0] for c in sp["closed"])
            debit = round(sum(c[0] * c[1] for c in sp["closed"]) / qty, 4)
            pnl = log_trade(sym, sp, debit, spot_price(sym), qty)
            del state["spreads"][sym]
            discord(f"🦋 **{sym} iron fly closed** {qty}x debit ${debit:.2f} vs credit ${sp['credit']:.2f} → P&L ${pnl:+,.0f}")
            return
        sp["status"] = "open"
    if sp["status"] == "open" and expiring:  # backstop: never carry a leg past expiry, whatever the time window
        discord(f"🚨 {sym} iron fly still held on/after expiry {sp['expiry']}: closing NOW at a marketable limit")
        submit_close(sym, sp, state, force=True)
    elif close_due(sp, now, sess):
        submit_close(sym, sp, state)


def entries(state, now, equity, sess):
    today = now.date()
    held = {re.match(r"[A-Z]+", p["symbol"]).group() for p in alpaca("GET", "/positions") if p.get("asset_class") == "us_option"}
    dd = equity / state["peak_equity"] - 1
    for sym in UNIVERSE:
        if not (ev := earnings(sym, today)) or ev[0] >= sess[-1]:  # report past the 30-day calendar: min() of nothing
            continue                                                   # would kill the scan for every later name
        entry, reaction = event_days(*ev, sess)
        key = f"{sym}:{ev[0]}"
        if entry != today or key in state["done"]:
            continue
        try:
            why = ("already holding" if sym in state["spreads"] or sym in held else
                   f"max {MAX_OPEN} open" if len(state["spreads"]) >= MAX_OPEN else
                   f"drawdown {dd:.1%} > {MAX_DD:.0%}" if dd < -MAX_DD else None)
            sp = None if why else (r := plan(sym, reaction, equity))[0]
            why = why or r[1]
            if sp:
                o = mleg(sp["legs"], sp["qty"], -sp["limit_credit"], opening=True)
                print(f"{sym} entry: {sp}")
                if o:
                    state["spreads"][sym] = {**sp, "status": "entering", "order_id": o["id"], "entry_day": today.isoformat(),
                                             "reaction_day": reaction.isoformat()}
            else:
                discord(f"🦋 {sym} earnings {ev[0]} ({ev[1]}): skipped, {why}")
            state["done"] = (state["done"] + [key])[-200:]
        except requests.HTTPError as e:
            discord(f"🦋 {sym} entry FAILED: {e.response.status_code} {e.response.text[:200]}")
        except Exception as e:
            discord(f"🦋 {sym} entry FAILED: {type(e).__name__} {str(e)[:200]}")


def reconcile(state):
    """Alert (once per symbol) on any live option position that no tracked spread owns."""
    mine = {l["symbol"] for sp in state["spreads"].values() for l in sp.get("legs", [])}
    orphans = sorted(set(held_qty()) - mine)
    new = [s for s in orphans if s not in state.get("orphans", [])]
    if new:
        discord(f"⚠️ options account holds positions the bot does not track: {', '.join(new)} — CHECK BY HAND")
    state["orphans"] = orphans


def run(state, now):
    state.setdefault("spreads", {})
    state.setdefault("done", [])
    c = alpaca("GET", "/clock")
    if not c["is_open"]:
        print("market closed")
        return
    to_close = (dt.datetime.fromisoformat(c["next_close"]) - now).total_seconds() / 60  # half days: 13:00 close
    equity = float(alpaca("GET", "/account")["equity"])
    state["peak_equity"] = max(state.get("peak_equity", equity), equity)
    sess = sessions(now.date())
    reconcile(state)
    for sym, sp in list(state["spreads"].items()):
        try:
            manage(state, sym, sp, now, sess)
        except Exception as e:  # one bad spread must not block the others
            discord(f"🦋 {sym} manage FAILED: {type(e).__name__} {str(e)[:200]}")
    if to_close <= 30:
        entries(state, now, equity, sess)


def preview(now):
    """DRY_RUN only: upcoming events and the spread the bot would build for the nearest one."""
    today, sess = now.date(), sessions(now.date())
    evs = sorted((e[0], s, e[1]) for s in UNIVERSE if (e := earnings(s, today)))
    print("upcoming earnings:", *[f"{d} {s} ({t})" for d, s, t in evs[:5]], sep="\n  ")
    for d, s, t in evs:
        if d > sess[-1]:
            break
        entry, reaction = event_days(d, t, sess)
        sp, why = plan(s, reaction, float(alpaca("GET", "/account")["equity"]))
        print(f"{s}: entry {entry}, reaction {reaction} ->", json.dumps(sp, indent=1) if sp else why)
        return


def main():
    if not AK:
        print("no ALPACA_OPT_API_KEY: options bot off")
        return
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = dt.datetime.now(NY)
    try:
        if same_account():
            discord("🛑 options bot REFUSED: options keys point at the stock-model account")
            return
        if DRY:
            preview(now)
        run(state, now)
    except Exception as e:  # never fail the workflow
        discord(f"🦋 options bot FAILED: {type(e).__name__} {str(e)[:200]}")
    finally:
        if not DRY:
            json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
