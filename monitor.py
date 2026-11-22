"""One monitoring pass. GitHub Actions runs this every 5 min in market hours (.github/workflows/monitor.yml).

- Alerts to Discord: unusual moves (|z| > 2.5 vs 60d vol), regime flips (QQQ vs 200d MA), and a daily summary with target weights.
- Paper trading: once a day in the last 30 min of the session, rebalances an Alpaca PAPER account to the model weights.
State (what was already alerted / rebalanced) lives in state.json, committed back by the workflow.
"""
import datetime as dt
import json
import os
import zoneinfo
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
import yfinance as yf

import signals
from model import BENCH, P, UNIVERSE, target_weights

# Owner override 2026-11-21: dip trade, fully invested. Same inverse-vol basket and caps, but no vol-target scaling
# and no risk-off halving. Ends the frozen-model paper test (MATH.md change log). Revert: LIVE = P.
LIVE = {**P, "vol_target": float("inf"), "regime_scale": 1.0}
NAMES = {"TSLA": "Tesla", "SPCX": "SpaceX", "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Google",
         "AMZN": "Amazon", "META": "Meta", "AVGO": "Broadcom", "TSM": "TSMC", "AMD": "AMD", "ORCL": "Oracle",
         "SGOV": "T-bills (cash)"}
START = 100_000


def plain(order):
    """'BUY  AAPL $9,767' -> 'buying $9,767 of Apple' for Discord; FAILED/SKIPPED/INFO lines pass through."""
    side, sym, *rest = order.split()
    if side not in ("BUY", "SELL"):
        return order
    return f"{'buying' if side == 'BUY' else 'selling'} {rest[0]} of {NAMES.get(sym, sym)}{' (all of it)' if '(close)' in rest else ''}"

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
    try:  # swallow here so no caller can print a traceback containing the webhook URL (public Actions logs)
        requests.post(HOOK, json={"content": msg[:1990]}, timeout=10).raise_for_status()
        return True
    except requests.RequestException as e:
        print("discord failed:", type(e).__name__, getattr(e.response, "status_code", ""))
        return False


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


CASH_ETF = "SGOV"  # 0-3 month T-bills: idle cash earns ~the T-bill rate instead of 0


def ask_link(now, equity, day, regime):
    """A claude.ai link with today's numbers pre-filled, so the owner can ask why from Discord (webhooks are one-way)."""
    acct = f"account ${equity:,.0f} ({equity / START - 1:+.1%} since the $100,000 start), " if equity else ""
    q = (f"My paper-trading bot holds big tech stocks, about 99% invested, rebalanced daily. As of {now:%b %d %Y}: {acct}"
         f"Nasdaq trend {'up' if regime == 'risk-on' else 'down'} vs its 200-day average. Last day's moves: "
         + ", ".join(f"{s} {x:+.1%}" for s, x in day.items())
         + ". Search today's news and explain in plain English, no jargon, why these stocks moved and what to watch next.")
    return f"❓ [**Ask Claude why**](https://claude.ai/new?q={quote(q)}) (opens a chat with today's numbers filled in)"


def rebalance(w, nodata, last=None):
    """last: {symbol: latest price}, needed for whole-share orders on non-fractionable assets (fresh IPOs like ANT)."""
    alpaca("DELETE", "/orders")  # cancel unfilled orders first, so positions are the whole truth and nothing doubles up
    equity = float(alpaca("GET", "/account")["equity"])
    held = {p["symbol"]: float(p["market_value"]) for p in alpaca("GET", "/positions")}
    if stale := sorted(nodata & set(held)):  # a failed download would read as weight 0 -> full sell of a real holding
        return equity, [f"SKIPPED rebalance: no price data for held {', '.join(stale)}"]
    w = {**w, CASH_ETF: max(0.0, 1 - sum(w.values()))}  # whatever the model leaves in cash goes to T-bills
    diffs = {s: w.get(s, 0) * equity * 0.98 - held.get(s, 0) for s in set(UNIVERSE) | set(held) | {CASH_ETF}}  # 2% cash buffer; held names outside the universe get sold
    skip = {s for s, d in diffs.items() if abs(d) < max(50, 0.01 * equity) and not (s in held and w.get(s, 0) == 0)}
    # Stock trims/adds too small to trade stay in the book, so T-bills get what is actually left over. Without this,
    # a dozen skipped trims left stocks 5.7 pts over target on 2026-11-20 and SGOV was still bought in full: cash -$3.6k.
    diffs[CASH_ETF] += sum(diffs[s] for s in skip - {CASH_ETF})
    lines, frac = [], {}
    for s, d in sorted(diffs.items(), key=lambda kv: kv[1]):  # sells first to free cash
        exit_all = s in held and (w.get(s, 0) == 0 or d <= -held[s])  # target 0, or told to sell the whole holding or more (T-bills after netting)
        if abs(d) < max(50, 0.01 * equity) and not exit_all:
            continue
        try:
            if exit_all:  # close by position, not notional: a notional sell of the snapshot value can exceed shares held or leave dust
                alpaca("DELETE", f"/positions/{s}")
            else:
                if s not in frac:
                    frac[s] = alpaca("GET", f"/assets/{s}").get("fractionable", True)
                size = {"notional": round(abs(d), 2)}
                if not frac[s]:  # fresh IPOs start non-fractionable: Alpaca rejects notional orders -> whole shares
                    qty = int(abs(d) / (last or {}).get(s, float("inf")))
                    if qty < 1:
                        lines.append(f"INFO {s}: not fractionable, ${abs(d):,.0f} is under one share; skipped")
                        continue
                    size = {"qty": str(qty)}
                alpaca("POST", "/orders", json={"symbol": s, **size, "side": "buy" if d > 0 else "sell",
                                                "type": "market", "time_in_force": "day"})
            lines.append(f"{'BUY ' if d > 0 else 'SELL'} {s} ${abs(d):,.0f}{' (close)' if exit_all else ''}")
        except requests.HTTPError as e:
            lines.append(f"FAILED {s}: {e.response.text[:120]}")
        except requests.RequestException as e:  # timeout etc.: report and keep going with the other names
            lines.append(f"FAILED {s}: {type(e).__name__}")
    return equity, lines


def alt_data(state):
    """Snapshot prediction markets; alert on Trump posts, Fed policy news and Reddit meme surges. Never raises."""
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
        prev = state.get("seen_posts", [])  # ordered list: [-500:] must drop the oldest, not arbitrary set members
        state["seen_posts"] = (prev + [p[3] for p in posts if p[3] not in seen])[-500:]
    except Exception as e:
        print("trump feed failed:", e)
    try:
        first_run = "seen_fed" not in state
        prev = state.get("seen_fed", [])
        items = signals.new_fed_items(set(prev))
        for kind, title, link in ([] if first_run else items):
            who, _, what = title.partition(", ") if kind == "speech" else ("", "", title)
            discord(f"🏦 **Fed {'speech by ' + who if kind == 'speech' else 'announcement'}:** {what or title}\n{link}\n"
                    "_Fed news can move interest rates and tech stocks. Info only, the bot doesn't trade on it._")
        state["seen_fed"] = (prev + [l for _, _, l in items])[-200:]
    except Exception as e:
        print("fed feed failed:", e)
    try:
        today = dt.datetime.now(NY).date().isoformat()
        done = [k for k in state.get("seen_memes", []) if k.startswith(today)]
        for tk, n, before, rank, st in signals.meme_surges():
            if f"{today}:{tk}" in done:
                continue
            discord(f"🔥 **Meme surge: {tk}** was mentioned {n} times on Reddit in the last day, up from {before} "
                    f"(#{rank} most talked-about){', and it is trending on StockTwits' if st else ''}.\n"
                    "_Hype spikes like this often fade within days. Info only, the bot doesn't trade these._")
            done.append(f"{today}:{tk}")
        state["seen_memes"] = done
    except Exception as e:
        print("meme radar failed:", e)


TRUMP_NOTE = "_Context only: 0 of 295 tests found these posts predict daily returns (reports/trump_results.md)._"

# Pre-committed drawdown tiers (reports/Trading psychology and behavior.md): decided now, not mid-drawdown.
# Alerts only. Cutting risk automatically would be an untested model change; any change goes through backtest.py.
DD_TIERS = [(-0.10, "Drops like this happened in testing and recovered. Recommended: do nothing, let it ride."),
            (-0.20, "This is a deep loss, as bad as the worst stretches in testing. Recommended: don't panic-sell; "
                    "talk it through before changing anything.")]


def missed_rebalance(state, today):
    """Alert once per day if the previous trading session never got a completed rebalance (cron dropped, or all
    attempts FAILED/SKIPPED). Missed dates accumulate in state['missed'] for the paper-year execution check."""
    last = state.get("rebalanced")
    if not last:
        return None
    cal = alpaca("GET", "/calendar", params={"start": (today - dt.timedelta(days=10)).isoformat(), "end": today.isoformat()})
    prev = [c["date"] for c in cal if c["date"] < today.isoformat()]
    missed = [d for d in prev if d > last]
    if not missed:
        return None
    state["missed"] = sorted(set(state.get("missed", [])) | set(missed))
    return f"⚠️ **The bot didn't trade on {', '.join(missed)}** (last trade day {last}), usually a GitHub hiccup. It catches up by itself. Days missed so far: {len(state['missed'])}."


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
        return f"📉 **The account is down {-dd:.0%} from its high** of ${peak:,.0f}. {DD_TIERS[tier - 1][1]}"
    return None


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    try:
        run(state)
    finally:  # always save, or a later crash re-sends already-sent alerts / repeats the rebalance next run
        with open(STATE + ".tmp", "w") as f:  # write-then-rename: a crash mid-write must not truncate state.json
            json.dump(state, f, indent=1)
        os.replace(STATE + ".tmp", STATE)


def run(state):
    now = dt.datetime.now(NY)
    today = now.date().isoformat()
    alt_data(state)
    is_open, to_close = market_clock(now)
    closing = to_close <= 30  # last 30 min of the session, 15:30 normally, 12:30 on half days
    if not FORCE and not is_open:
        print("market closed")
        return

    if AK and state.get("session_checked") != today:
        state["session_checked"] = today
        if msg := missed_rebalance(state, now.date()):
            discord(msg)

    state.setdefault("alerted", {})
    alerted = state["alerted"].setdefault(today, [])
    state["alerted"] = {today: alerted}  # keep only today's dedupe keys

    px = yf.download(UNIVERSE + [BENCH], start=(now - dt.timedelta(days=800)).date().isoformat(),
                     auto_adjust=True, progress=False, threads=False)
    raw = px["Close"].reindex(columns=UNIVERSE + [BENCH]).dropna(how="all")
    C = raw.ffill()  # a gap in today's partial row would blank that name's vol -> weight 0 -> full sell
    r = C / C.shift(1) - 1
    vol = r.iloc[:-1].tail(P["vol_win"]).std()
    msgs = []

    for s in UNIVERSE:
        z = r[s].iloc[-1] / vol[s] if vol[s] > 0 else np.nan
        if abs(z) > 2.5 and f"move:{s}" not in alerted:
            msgs.append(f"⚡ **{NAMES[s]} is {'up' if z > 0 else 'down'} {abs(r[s].iloc[-1]):.1%} today**, a big move for it (about {abs(z):.0f}x a normal day). Nothing to do, the bot rebalances near the close.")
            alerted.append(f"move:{s}")

    q = C[BENCH]
    if pd.isna(raw[BENCH].iloc[-1]) or q.notna().sum() < P["regime_ma"]:  # checked on the unfilled row (ffill hid a missing bar): a stale QQQ close must not set today's regime; the loop retries in minutes
        msgs.append("⚠️ Couldn't get today's market prices. The bot is waiting and will try again in a few minutes.")
        for m in msgs:
            discord(m)
        return
    regime = "risk-on" if q.iloc[-1] >= q.rolling(P["regime_ma"]).mean().iloc[-1] else "risk-off"
    if state.get("regime") and state["regime"] != regime:
        msgs.append(f"🚦 **The market's trend just turned {'up' if regime == 'risk-on' else 'down'}** (the Nasdaq crossed its 200-day average). No change to the plan: the bot stays fully invested either way.")
    state["regime"] = regime

    if (closing or FORCE) and state.get("rebalanced") != today:
        w = target_weights(C, LIVE).iloc[-1]
        order = w[UNIVERSE].sort_values(ascending=False).index
        mix = "\n".join(f"• {NAMES[s]} {w[s]:.0%}" for s in order if w[s] > 0)
        day = r[UNIVERSE].iloc[-1].dropna().sort_values()
        moves = "\n".join(f"• {NAMES[s]} {'up' if x > 0 else 'down'} {abs(x):.1%}" for s, x in
                          list(day.items())[:3] + [kv for kv in list(day.items())[-2:] if kv[1] > 0])
        trend = "up (Nasdaq above its 200-day average)" if regime == "risk-on" else "down (Nasdaq below its 200-day average)"
        summary = (f"📊 **Daily update, {now:%a %b %d}**\n\n"
                   f"📈 **Market trend:** {trend}\n\n"
                   f"🔍 **Biggest moves on the last trading day:**\n{moves}\n\n"
                   f"🎯 **Plan:** {w.sum():.0%} in big tech stocks, {1 - w.sum():.0%} in cash. Nothing for you to do, the bot trades it.\n{mix}")
        equity = None
        if AK:
            equity, orders = rebalance(w.to_dict(), {s for s in UNIVERSE if C[s].isna().all()}, C.iloc[-1].dropna().to_dict())
            summary = (summary.replace("\n\n📈", f"\n\n💰 **Paper account: ${equity:,.0f}**\n"
                                       f"{'Up' if equity >= START else 'Down'} {abs(equity / START - 1):.1%} since the $100,000 start\n\n📈", 1)
                       + "\n\n🧾 **Trades:**\n" + ("\n".join(f"• {plain(o)}" for o in orders) if orders else "No trades needed today."))
            if dd_msg := drawdown_alert(state, equity):
                msgs.append(dd_msg)
            if closing:  # one row per day at the close rebalance; track.py compares it with the backtest
                log_equity(today, equity, w.sum(), regime)
        msgs.append(summary[:1990])
        msgs.append(ask_link(now, equity, day, regime))
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
