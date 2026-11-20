"""
Tennis favorites forward test — the pre-registered Wimbledon follow-up
================================================================================
The Wimbledon 2026 retro found favorites priced 0.80-0.95 on Polymarket won
97.4% at resolution: +11% ROI net of taker fees (37/38, p~0.04). That bucket
was chosen AFTER looking, so the agreed plan was a pre-registered forward
paper test with the rule frozen in advance:

    buy any PM tennis match favorite whose best ask is 0.80-0.95 pre-play,
    flat stakes, hold to resolution. No discretion, no exits.

This module runs that test, free of charge: match discovery via Gamma's
tennis tag, entry prices from the public CLOB book, settlement from the
resolved market. It never places an order; the ledger is paper by design
until the forward sample says otherwise.

Distinct from trader.py on purpose: that strategy trades CONVERGENCE before
kickoff; this one holds THROUGH the match, because the retro showed tennis
mispricing pays at settlement (the pre-match price path is flat).

Usage:
    py tennis_favorites.py             # discover + enter + settle (cron-friendly)
    py tennis_favorites.py --report
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests

from db import get_connection
from polymarket_exec import public_book

GAMMA_BASE = "https://gamma-api.polymarket.com"
TIMEOUT = 20
ENTRY_LO, ENTRY_HI = 0.80, 0.95
FLAT_STAKE = 100.0                     # dollars per trade, flat by the rule
TAKER_FEE_RATE = 0.03                  # fee = rate * p * (1-p) per share
MATCH_SLUG = re.compile(r"^(atp|wta)-(?!doubles-).+-(\d{4}-\d{2}-\d{2})$")  # singles only, per the frozen rule
SKIP_WORDS = ("spread", "set", "total", "tiebreak", "games")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA = """
CREATE TABLE IF NOT EXISTS tennis_fav_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,
    tour TEXT,                        -- 'atp' / 'wta'
    slug TEXT NOT NULL,
    title TEXT,
    match_date TEXT,                  -- from the slug
    player TEXT NOT NULL,             -- the favorite bought
    market_id TEXT,
    outcome_idx INTEGER,              -- our index in the market's outcome list
    token_id TEXT NOT NULL UNIQUE,    -- idempotency: one entry per token ever
    entry_ask REAL NOT NULL,
    fee_per_share REAL,
    status TEXT NOT NULL DEFAULT 'open',   -- 'open' / 'won' / 'lost' / 'void'
    settled_at TEXT,
    pnl_per_dollar REAL               -- profit per $1 staked, net of fee
);
"""


def _utc_now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _jload(v):
    return json.loads(v) if isinstance(v, str) else (v or [])


def match_events():
    """Open Gamma tennis events that look like single matches, via the tag."""
    out, offset = [], 0
    while True:
        r = requests.get(f"{GAMMA_BASE}/events",
                         params={"tag_slug": "tennis", "closed": "false",
                                 "limit": 100, "offset": offset}, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json() or []
        out += [e for e in batch if MATCH_SLUG.match(e.get("slug") or "")]
        if len(batch) < 100 or offset >= 500:
            break
        offset += 100
    return out


def winner_market(event):
    """The match-winner market: two player-name outcomes, no line, no label."""
    for m in event.get("markets", []):
        outcomes = _jload(m.get("outcomes"))
        if len(outcomes) != 2 or m.get("groupItemTitle"):
            continue
        if any(w in (m.get("question") or "").lower() for w in SKIP_WORDS):
            continue
        if "yes" in [o.lower() for o in outcomes]:
            continue
        return m, outcomes
    return None, None


def log_entries(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    now = _utc_now()
    today = now.strftime("%Y-%m-%d")
    entered = scanned = 0
    for ev in match_events():
        slug = ev.get("slug") or ""
        mt = MATCH_SLUG.match(slug)
        tour, match_date = mt.group(1), mt.group(2)
        # strictly future match days only: Gamma's startDate is the LISTING
        # time (useless for play state), and a same-day match may already be
        # in progress by the time a run fires. PM lists tennis ~1 day out, so
        # tomorrow's card is visible today and entry is guaranteed pre-play.
        if match_date <= today:
            continue
        market, outcomes = winner_market(ev)
        if market is None:
            continue
        tokens = _jload(market.get("clobTokenIds"))
        gamma_prices = _jload(market.get("outcomePrices"))
        if len(tokens) != 2 or len(gamma_prices) != 2:
            continue
        scanned += 1
        for idx, (player, token) in enumerate(zip(outcomes, tokens)):
            # the player must BE the favorite by market price -- an ask alone
            # is not a price: fresh thin books quote junk asks on both sides
            # (both players "at 0.87"), and buying those is not the rule
            try:
                p_mkt = float(gamma_prices[idx])
            except (TypeError, ValueError):
                continue
            if not (ENTRY_LO <= p_mkt <= ENTRY_HI):
                continue
            dup = conn.execute("SELECT 1 FROM tennis_fav_trades WHERE token_id=?",
                               (token,)).fetchone()
            if dup:
                continue
            try:
                bid, ask, ask_size, _ = public_book(token)
            except requests.RequestException:
                continue
            # coherent two-sided quote near the market price, or no entry:
            # entry is at the ask, so a gaping or drifted book means the real
            # cost is not the price the rule selected on
            if ask is None or bid is None or ask - bid > 0.05 or abs(ask - p_mkt) > 0.05:
                continue
            if not (ENTRY_LO <= ask <= ENTRY_HI):
                continue
            fee = TAKER_FEE_RATE * ask * (1 - ask)
            conn.execute(
                "INSERT OR IGNORE INTO tennis_fav_trades (logged_at, tour, slug, title, "
                "match_date, player, market_id, outcome_idx, token_id, entry_ask, fee_per_share) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (_iso(now), tour, slug, ev.get("title"), match_date, player,
                 str(market.get("id")), idx, token, ask, fee))
            entered += 1
            if not quiet:
                print(f"  ENTER {player} @ {ask:.2f} ({slug})")
    conn.commit()
    conn.close()
    if not quiet:
        print(f"[{_iso(now)}] tennis favorites: {scanned} matches scanned, {entered} entered")


def settle(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.row_factory = None
    rows = conn.execute("SELECT id, slug, market_id, outcome_idx, entry_ask, fee_per_share "
                        "FROM tennis_fav_trades WHERE status='open'").fetchall()
    settled = 0
    for pid, slug, market_id, idx, ask, fee in rows:
        try:
            r = requests.get(f"{GAMMA_BASE}/events", params={"slug": slug}, timeout=TIMEOUT)
            evs = r.json() or []
        except (requests.RequestException, ValueError):
            continue
        if not evs:
            continue
        ev = evs[0]
        market = next((m for m in ev.get("markets", [])
                       if str(m.get("id")) == str(market_id)), None)
        if market is None or not market.get("closed"):
            continue
        prices = _jload(market.get("outcomePrices"))
        if len(prices) != 2:
            continue
        try:
            won = float(prices[idx]) > 0.5
        except (TypeError, ValueError):
            continue
        # per $1 staked at price `ask`: win pays (1-ask)/ask, loss pays -1;
        # taker fee per share prorated onto the stake
        pnl = ((1 - ask) / ask if won else -1.0) - fee / ask
        conn.execute("UPDATE tennis_fav_trades SET status=?, settled_at=?, pnl_per_dollar=? "
                     "WHERE id=?", ("won" if won else "lost", _iso(_utc_now()), pnl, pid))
        settled += 1
    conn.commit()
    conn.close()
    if not quiet and settled:
        print(f"settled {settled} favorite(s)")


def report():
    conn = get_connection()
    conn.executescript(SCHEMA)
    rows = conn.execute("SELECT status, pnl_per_dollar, entry_ask FROM tennis_fav_trades").fetchall()
    conn.close()
    done = [r for r in rows if r[0] in ("won", "lost")]
    open_ = [r for r in rows if r[0] == "open"]
    print(f"=== Tennis favorites forward test (rule frozen 2026-07: buy 0.80-0.95, "
          f"hold to resolution) ===")
    print(f"open: {len(open_)}   settled: {len(done)}")
    if not done:
        print("Benchmark from the Wimbledon retro: 37/38 won, +11% ROI. This forward "
              "sample is the number that decides whether that was real.")
        return
    wins = sum(1 for r in done if r[0] == "won")
    roi = sum(r[1] for r in done) / len(done)
    print(f"won {wins}/{len(done)} ({wins / len(done):.1%}); "
          f"mean ROI {roi:+.2%} per $1 staked (flat ${FLAT_STAKE:.0f}/trade -> "
          f"{roi * FLAT_STAKE * len(done):+,.0f} total)")
    print("Wimbledon retro benchmark: 97.4% won, +11% ROI. Sustained agreement "
          "across 100+ forward trades = go-live case; divergence = the retro was "
          "selection bias.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pre-registered PM tennis favorites paper test.")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.report:
        report()
    else:
        log_entries(quiet=args.quiet)
        settle(quiet=args.quiet)
