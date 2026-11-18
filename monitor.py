"""One monitoring pass. GitHub Actions runs this every 15 min on weekdays (.github/workflows/monitor.yml).

- Alerts to Discord: unusual moves (|z| > 2.5 vs 60d vol), bear-marubozu candles (the one pattern that passed
  candles.py), regime flips (QQQ vs 200d MA), and a daily summary with target weights.
- Paper trading: once a day in the last 30 min of the session, rebalances an Alpaca PAPER account to the model weights.
State (what was already alerted / rebalanced) lives in state.json, committed back by the workflow.
"""
import datetime as dt
import json
import os
import zoneinfo

import numpy as np
import pandas as pd
import requests
import yfinance as yf

import signals
from model import BENCH, P, UNIVERSE, target_weights

NY = zoneinfo.ZoneInfo("America/New_York")
STATE = "state.json"
HOOK = os.environ.get("DISCORD_WEBHOOK_URL")
AK, AS = os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET_KEY")
ALPACA = "https://paper-api.alpaca.markets/v2"  # paper only, on purpose: the model has not earned real money yet
FORCE = os.environ.get("FORCE") == "1"  # manual run: ignore market-hours gate


def discord(msg):
    if not HOOK:
        print(msg)
        return
    requests.post(HOOK, json={"content": msg[:1990]}, timeout=10).raise_for_status()


def alpaca(method, path, **kw):
    r = requests.request(method, ALPACA + path, timeout=15, **kw,
                         headers={"APCA-API-KEY-ID": AK, "APCA-API-SECRET-KEY": AS})
    r.raise_for_status()
    return r.json() if r.text else None


def market_open(now):
    if AK:
        return alpaca("GET", "/clock")["is_open"]  # handles holidays and half days
    return now.weekday() < 5 and dt.time(9, 30) <= now.time() <= dt.time(16, 0)


def earnings_soon(sym, today):
    try:
        dates = yf.Ticker(sym).calendar.get("Earnings Date", [])
        return any(0 <= (d - today).days <= 3 for d in dates)
    except Exception:
        return False  # calendar is flaky; a missing haircut is not worth crashing the run


def rebalance(w):
    equity = float(alpaca("GET", "/account")["equity"])
    held = {p["symbol"]: float(p["market_value"]) for p in alpaca("GET", "/positions")}
    diffs = {s: w.get(s, 0) * equity * 0.98 - held.get(s, 0) for s in UNIVERSE}  # 2% cash buffer
    lines = []
    for s, d in sorted(diffs.items(), key=lambda kv: kv[1]):  # sells first to free cash
        if abs(d) < max(50, 0.01 * equity):
            continue
        try:
            alpaca("POST", "/orders", json={"symbol": s, "notional": round(abs(d), 2), "side": "buy" if d > 0 else "sell",
                                            "type": "market", "time_in_force": "day"})
            lines.append(f"{'BUY ' if d > 0 else 'SELL'} {s} ${abs(d):,.0f}")
        except requests.HTTPError as e:
            lines.append(f"FAILED {s}: {e.response.text[:120]}")
    return equity, lines


def alt_data(state):
    """Snapshot prediction markets; alert on new market-relevant Trump posts. Never raises."""
    try:
        n, errs = signals.snapshot_prediction_markets()
        print(f"prediction markets: {n} rows", *errs)
    except Exception as e:
        print("prediction markets failed:", e)
    try:
        first_run = "seen_posts" not in state
        seen = set(state.get("seen_posts", []))
        posts = signals.new_trump_posts(seen)
        for topics, tickers, text, link in ([] if first_run else posts):  # first run: just mark the backlog as seen
            discord(f"🇺🇸 **Trump post** — {', '.join(topics)} → `{' '.join(tickers)}`\n> {text[:300]}\n{link}\n"
                    f"{TRUMP_NOTE}")
        state["seen_posts"] = (list(seen) + [p[3] for p in posts])[-500:]
    except Exception as e:
        print("trump feed failed:", e)


TRUMP_NOTE = "_Backtest: see reports/trump_results.md._"


def main():
    now = dt.datetime.now(NY)
    today = now.date().isoformat()
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    alt_data(state)
    if not FORCE and not market_open(now):
        print("market closed")
        json.dump(state, open(STATE, "w"), indent=1)
        return

    state.setdefault("alerted", {})
    alerted = state["alerted"].setdefault(today, [])
    state["alerted"] = {today: alerted}  # keep only today's dedupe keys

    px = yf.download(UNIVERSE + [BENCH], start=(now - dt.timedelta(days=800)).date().isoformat(),
                     auto_adjust=True, progress=False, threads=False)
    C = px["Close"][UNIVERSE + [BENCH]].dropna(how="all")
    O, Hh, L = (px[k][UNIVERSE].iloc[-1] for k in ("Open", "High", "Low"))
    r = C / C.shift(1) - 1
    vol = r.iloc[:-1].tail(P["vol_win"]).std()
    msgs = []

    for s in UNIVERSE:
        z = r[s].iloc[-1] / vol[s] if vol[s] > 0 else np.nan
        if abs(z) > 2.5 and f"move:{s}" not in alerted:
            msgs.append(f"⚡ **{s}** {r[s].iloc[-1]:+.2%} today ({z:+.1f}σ vs 60d vol)")
            alerted.append(f"move:{s}")
        rng, body = Hh[s] - L[s], C[s].iloc[-1] - O[s]
        if rng > 0 and body < 0 and -body >= 0.9 * rng and f"marubozu:{s}" not in alerted and now.time() >= dt.time(15, 30):
            msgs.append(f"🕯️ **{s}** forming a bear marubozu. Backtest: next day +0.50% avg vs normal, 57% hit "
                        f"(only pattern of 13 that survived testing — reports/candles_results.md)")
            alerted.append(f"marubozu:{s}")

    q = C[BENCH]
    regime = "risk-on" if q.iloc[-1] >= q.rolling(P["regime_ma"]).mean().iloc[-1] else "risk-off"
    if state.get("regime") and state["regime"] != regime:
        msgs.append(f"🚦 Regime flip: **{regime}** (QQQ vs 200-day MA). Exposure {'restored' if regime == 'risk-on' else 'halved'}.")
    state["regime"] = regime

    if (now.time() >= dt.time(15, 30) or FORCE) and state.get("rebalanced") != today:
        w = target_weights(C).iloc[-1]
        for s in UNIVERSE:
            if w[s] > 0 and earnings_soon(s, now.date()):
                w[s] /= 2  # earnings gap risk: report §risk, size down into the event
        table = "\n".join(f"`{s:5}` {w[s]:6.1%}" for s in UNIVERSE if w[s] > 0)
        summary = f"📊 **Daily target** ({today}, {regime}) — gross {w.sum():.0%}, cash {1 - w.sum():.0%}\n{table}"
        if AK:
            equity, orders = rebalance(w.to_dict())
            summary += f"\n🧾 Paper account ${equity:,.0f}\n" + ("\n".join(orders) or "no trades needed")
        msgs.append(summary)
        state["rebalanced"] = today

    for m in msgs:
        discord(m)
    json.dump(state, open(STATE, "w"), indent=1)


if __name__ == "__main__":
    main()
