"""One monitoring pass. GitHub Actions runs this every 5 min in market hours (.github/workflows/monitor.yml).

- Alerts to Discord: unusual moves (|z| > 2.5 vs 60d vol), regime flips (QQQ vs 200d MA), and a daily summary with target weights.
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


def market_clock(now):
    """(is_open, minutes to today's close). Alpaca's clock handles holidays and 13:00 half days."""
    if AK:
        c = alpaca("GET", "/clock")
        return c["is_open"], (dt.datetime.fromisoformat(c["next_close"]) - now).total_seconds() / 60
    close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return now.weekday() < 5 and dt.time(9, 30) <= now.time() <= dt.time(16, 0), (close - now).total_seconds() / 60


def earnings_soon(sym, today):
    try:
        dates = yf.Ticker(sym).calendar.get("Earnings Date", [])
        return any(0 <= (d - today).days <= 3 for d in dates)
    except Exception:
        return False  # calendar is flaky; a missing haircut is not worth crashing the run


CASH_ETF = "SGOV"  # 0-3 month T-bills: idle cash earns ~the T-bill rate instead of 0


def rebalance(w, nodata):
    alpaca("DELETE", "/orders")  # cancel unfilled orders first, so positions are the whole truth and nothing doubles up
    equity = float(alpaca("GET", "/account")["equity"])
    held = {p["symbol"]: float(p["market_value"]) for p in alpaca("GET", "/positions")}
    if stale := sorted(nodata & set(held)):  # a failed download would read as weight 0 -> full sell of a real holding
        return equity, [f"SKIPPED rebalance: no price data for held {', '.join(stale)}"]
    w = {**w, CASH_ETF: max(0.0, 1 - sum(w.values()))}  # whatever the model leaves in cash goes to T-bills
    diffs = {s: w.get(s, 0) * equity * 0.98 - held.get(s, 0) for s in set(UNIVERSE) | set(held) | {CASH_ETF}}  # 2% cash buffer; held names outside the universe get sold
    lines = []
    for s, d in sorted(diffs.items(), key=lambda kv: kv[1]):  # sells first to free cash
        exit_all = s in held and w.get(s, 0) == 0
        if abs(d) < max(50, 0.01 * equity) and not exit_all:
            continue
        try:
            if exit_all:  # close by position, not notional: a notional sell of the snapshot value can exceed shares held or leave dust
                alpaca("DELETE", f"/positions/{s}")
            else:
                alpaca("POST", "/orders", json={"symbol": s, "notional": round(abs(d), 2), "side": "buy" if d > 0 else "sell",
                                                "type": "market", "time_in_force": "day"})
            lines.append(f"{'BUY ' if d > 0 else 'SELL'} {s} ${abs(d):,.0f}{' (close)' if exit_all else ''}")
        except requests.HTTPError as e:
            lines.append(f"FAILED {s}: {e.response.text[:120]}")
        except requests.RequestException as e:  # timeout etc.: report and keep going with the other names
            lines.append(f"FAILED {s}: {type(e).__name__}")
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
            try:  # one failed post must not leave the earlier ones unmarked (they'd be re-sent next run)
                discord(f"🇺🇸 **Trump post** — {', '.join(topics)} → `{' '.join(tickers)}`\n> {text[:300]}\n{link}\n"
                        f"{TRUMP_NOTE}")
            except requests.RequestException as e:
                print("discord failed:", type(e).__name__)
        state["seen_posts"] = (list(seen) + [p[3] for p in posts])[-500:]
    except Exception as e:
        print("trump feed failed:", e)


TRUMP_NOTE = "_Context only: 0 of 295 tests found these posts predict daily returns (reports/trump_results.md)._"

# Pre-committed drawdown tiers (reports/Trading psychology and behavior.md): decided now, not mid-drawdown.
# Alerts only. Cutting risk automatically would be an untested model change; any change goes through backtest.py.
DD_TIERS = [(-0.10, "review: inside the backtest's normal range (max drawdown -27%). Rule: no action."),
            (-0.20, "deep: in the worst tail of backtest drawdowns. Rule: decide on lowering vol_target at the next "
                    "scheduled review, after re-running backtest.py — never same-day.")]


EQUITY_LOG = "signals/equity_log.csv"


def log_equity(day, equity, gross, regime):
    """Append (date, equity, target gross, regime) once per day; the workflow commits signals/."""
    rows = pd.read_csv(EQUITY_LOG) if os.path.exists(EQUITY_LOG) else pd.DataFrame(columns=["date", "equity", "gross", "regime"])
    rows = rows[rows.date != day]  # a retry later the same day replaces the row
    rows.loc[len(rows)] = [day, round(equity, 2), round(float(gross), 4), regime]
    os.makedirs("signals", exist_ok=True)
    rows.to_csv(EQUITY_LOG, index=False)


def drawdown_alert(state, equity):
    """Track peak equity; return a message the first time each tier is crossed. Re-arms after recovering to -5%."""
    peak = max(state.get("peak_equity", equity), equity)
    state["peak_equity"] = peak
    dd = round(equity / peak - 1, 6)  # 90k/100k-1 is -0.0999...: round so exact tier hits count
    if dd > -0.05:
        state["dd_tier"] = 0
    tier = sum(dd <= t for t, _ in DD_TIERS)
    if tier > state.get("dd_tier", 0):
        state["dd_tier"] = tier
        return f"📉 **Drawdown {dd:.1%}** from peak ${peak:,.0f} — {DD_TIERS[tier - 1][1]}"
    return None


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    try:
        run(state)
    finally:  # always save, or a later crash re-sends already-sent alerts / repeats the rebalance next run
        json.dump(state, open(STATE, "w"), indent=1)


def run(state):
    now = dt.datetime.now(NY)
    today = now.date().isoformat()
    alt_data(state)
    is_open, to_close = market_clock(now)
    closing = to_close <= 30  # last 30 min of the session, 15:30 normally, 12:30 on half days
    if not FORCE and not is_open:
        print("market closed")
        return

    state.setdefault("alerted", {})
    alerted = state["alerted"].setdefault(today, [])
    state["alerted"] = {today: alerted}  # keep only today's dedupe keys

    px = yf.download(UNIVERSE + [BENCH], start=(now - dt.timedelta(days=800)).date().isoformat(),
                     auto_adjust=True, progress=False, threads=False)
    C = px["Close"].reindex(columns=UNIVERSE + [BENCH]).dropna(how="all").ffill()  # a gap in today's partial row would blank that name's vol -> weight 0 -> full sell
    r = C / C.shift(1) - 1
    vol = r.iloc[:-1].tail(P["vol_win"]).std()
    msgs = []

    for s in UNIVERSE:
        z = r[s].iloc[-1] / vol[s] if vol[s] > 0 else np.nan
        if abs(z) > 2.5 and f"move:{s}" not in alerted:
            msgs.append(f"⚡ **{s}** {r[s].iloc[-1]:+.2%} today ({z:+.1f}σ vs 60d vol)")
            alerted.append(f"move:{s}")

    q = C[BENCH]
    regime = "risk-on" if q.iloc[-1] >= q.rolling(P["regime_ma"]).mean().iloc[-1] else "risk-off"
    if state.get("regime") and state["regime"] != regime:
        msgs.append(f"🚦 Regime flip: **{regime}** (QQQ vs 200-day MA). Exposure {'restored' if regime == 'risk-on' else 'halved'} at the close rebalance if it holds.")
    state["regime"] = regime

    if (closing or FORCE) and state.get("rebalanced") != today:
        w = target_weights(C).iloc[-1]
        for s in UNIVERSE:
            if w[s] > 0 and earnings_soon(s, now.date()):
                w[s] /= 2  # earnings gap risk: report §risk, size down into the event
        table = "\n".join(f"`{s:5}` {w[s]:6.1%}" for s in UNIVERSE if w[s] > 0)
        summary = f"📊 **Daily target** ({today}, {regime}) — gross {w.sum():.0%}, cash {1 - w.sum():.0%}\n{table}"
        if AK:
            equity, orders = rebalance(w.to_dict(), {s for s in UNIVERSE if C[s].isna().all()})
            summary += f"\n🧾 Paper account ${equity:,.0f}\n" + ("\n".join(orders) or "no trades needed")
            if dd_msg := drawdown_alert(state, equity):
                msgs.append(dd_msg)
            if closing:  # one row per day at the close rebalance; track.py compares it with the backtest
                log_equity(today, equity, w.sum(), regime)
        msgs.append(summary)
        # failed/skipped orders retry next run (diffs come from live positions, so fills aren't repeated);
        # a forced midday run must not block the real closing rebalance
        if closing and not (AK and any(o.startswith(("FAILED", "SKIPPED")) for o in orders)):
            state["rebalanced"] = today

    for m in msgs:
        try:
            discord(m)
        except requests.RequestException as e:  # one failed post must not drop the rest
            print("discord failed:", type(e).__name__, getattr(e.response, "status_code", ""))  # str(e) can contain the webhook URL (public logs)


if __name__ == "__main__":
    main()
