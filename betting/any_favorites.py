"""
Any-category favourites forward test -- favourite-longshot bias off the sports pages
================================================================================
PRE-REGISTERED, rules frozen 2026-11-20 (before any trade was logged).

Basis: reports/pm_calibration.md (40,140 resolved Polymarket markets) --
favourites 7-30 days before resolution won +1.4-2.5% more than priced, gross;
the edge is gone at ~2c round-trip costs. So this only works if entry is at a
tight book and the fee is small; this test measures exactly that, forward.

Frozen rules (table any_fav_trades; skipped candidates in any_fav_skips):
  * Universe: open binary Polymarket markets in politics, economics, world
    events, culture, tech and other (e.g. weather). EXCLUDED: sports/esports
    (covered by tennis_/sport_favorites.py) and crypto / stock / commodity
    price markets (tags or feeType crypto*, sports*, finance_prices*,
    hit-price, up-or-down).
  * 7-30 days remaining to the market's endDate; lifetime volume >= $10k.
  * Buy the side priced 0.90-0.97, if its best ask is also 0.90-0.97, the ask
    is within 0.05 of the market price (mid), and the book spread <= 0.03.
  * Objective resolution only: the market's resolutionSource is set, or its
    description names an official publisher / official result. Markets that
    resolve on subjective wording ("consensus of credible reporting") or name
    no official source are skipped, with the reason logged to any_fav_skips.
  * Flat $100, hold to resolution, one entry per token ever.
  * Fee = rate * p * (1-p) per share, rate = the market's published
    feeSchedule rate when present, else by category: geopolitics 0, all
    else 0.04.
  * Caveat (not a rule change): legs of one event (one election, one AI
    leaderboard) are correlated, so the i.i.d. bootstrap CI is too narrow
    when many entries share an event; read the CI with that in mind.
  * Pass bar: >= 200 settled, mean ROI > 0 with bootstrap 95% CI > 0, both
    chronological halves > 0.

Paper only: never places an order, never touches a private key.

Usage:
    py any_favorites.py             # discover + enter + settle (cron-friendly)
    py any_favorites.py --report
"""

import argparse
import re
from datetime import datetime, timedelta, timezone

import requests

from db import get_connection
from polymarket_exec import public_book
from sport_favorites import GAMMA_BASE, HEADERS, TIMEOUT, FLAT_STAKE, _iso, _jload, _utc_now, group_stats

FROZEN = "2026-11-20"
LO, HI = 0.90, 0.97
MIN_DAYS, MAX_DAYS = 7, 30
MIN_VOLUME = 10_000
MAX_SPREAD, MAX_DRIFT = 0.03, 0.05
PASS_N = 200
EXCLUDE_TAGS = {"sports", "esports", "games", "crypto", "crypto-prices", "hit-price", "finance-updown",
                "pyth-finance", "up-or-down", "stocks", "commodities"}
EXCLUDE_FEE_TYPES = ("crypto", "sports", "finance_prices")
PRICE_Q = re.compile(r"up or down|price of|(above|below|hit|reach|close at) \$", re.I)
OFFICIAL = re.compile(r"official|according to (the )?\w|as (published|reported|announced) by|\.gov\b|bureau|"
                      r"commission|federal reserve|statistics|certif|\bhttps?://", re.I)
PRIMARY_CONSENSUS = re.compile(r"primary resolution source[^.]{0,40}consensus of credible report", re.I)
SUBJECTIVE = re.compile(r"consensus of credible report|sole discretion|widely reported", re.I)

SCHEMA = """
CREATE TABLE IF NOT EXISTS any_fav_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,
    category TEXT,
    slug TEXT,
    question TEXT,
    end_date TEXT,
    side TEXT NOT NULL,               -- outcome bought ('Yes' / 'No' / name)
    market_id TEXT NOT NULL,
    outcome_idx INTEGER,
    token_id TEXT NOT NULL UNIQUE,    -- idempotency: one entry per token ever
    entry_ask REAL NOT NULL,
    fee_rate REAL,
    fee_per_share REAL,
    volume REAL,
    status TEXT NOT NULL DEFAULT 'open',   -- 'open' / 'won' / 'lost' / 'void'
    settled_at TEXT,
    pnl_per_dollar REAL
);
CREATE TABLE IF NOT EXISTS any_fav_skips (
    token_id TEXT PRIMARY KEY,        -- first skip reason per price-qualifying token
    logged_at TEXT NOT NULL,
    market_id TEXT,
    question TEXT,
    reason TEXT NOT NULL
);
"""


def _tags(m):
    return {t.get("slug", "").lower() for t in (m.get("tags") or []) if isinstance(t, dict)}


def category(m):
    ft, tags = (m.get("feeType") or "").lower(), _tags(m)
    if "geopolitics" in tags:
        return "geopolitics"
    cats = ("politics", "economics", "tech", "culture", "weather")
    for c in cats:  # the published fee type is the cleaner label; tags are a fallback
        if ft.startswith(c):
            return c
    for c in cats:
        if c in tags:
            return c
    return "economics" if "economy" in tags or "finance" in tags else "other"


def fee_rate(m):
    try:
        return float((m.get("feeSchedule") or {})["rate"])
    except (KeyError, TypeError, ValueError):
        return 0.0 if category(m) == "geopolitics" else 0.04


def excluded(m):
    ft = (m.get("feeType") or "").lower()
    return bool(_tags(m) & EXCLUDE_TAGS) or ft.startswith(EXCLUDE_FEE_TYPES) or bool(PRICE_Q.search(m.get("question") or ""))


def objective_skip(m):
    """None if resolution is objective, else the skip reason."""
    if (m.get("resolutionSource") or "").strip():
        return None
    desc = m.get("description") or ""
    if PRIMARY_CONSENSUS.search(desc):
        return "subjective wording"
    if OFFICIAL.search(desc):
        return None
    return "subjective wording" if SUBJECTIVE.search(desc) else "no official source named"


def _end(m):
    try:
        return datetime.fromisoformat(str(m.get("endDate")).replace("Z", "+00:00"))
    except ValueError:
        return None


def open_markets(now):
    """Open markets ending in 7-30 days with volume >= $10k (Gamma /markets, tags included)."""
    out, offset = [], 0
    while True:
        r = requests.get(f"{GAMMA_BASE}/markets", headers=HEADERS, timeout=TIMEOUT, params={
            "closed": "false", "limit": 100, "offset": offset, "volume_num_min": MIN_VOLUME, "include_tag": "true",
            "end_date_min": _iso(now + timedelta(days=MIN_DAYS)), "end_date_max": _iso(now + timedelta(days=MAX_DAYS))})
        r.raise_for_status()
        batch = r.json() or []
        out += batch
        if len(batch) < 100 or offset >= 2000:  # ponytail: 2,100-market cap (Gamma rejects deeper offsets); ~535 today
            break
        offset += 100
    return out


def candidates(m, now):
    """(side, idx, token, price) for a 0.90-0.97 side passing the time/volume/universe rules, or []."""
    end = _end(m)
    if m.get("closed") or end is None or not (timedelta(days=MIN_DAYS) <= end - now <= timedelta(days=MAX_DAYS)):
        return []
    try:
        if float(m.get("volumeNum") or 0) < MIN_VOLUME:
            return []
    except (TypeError, ValueError):
        return []
    if excluded(m):
        return []
    outcomes, tokens, prices = _jload(m.get("outcomes")), _jload(m.get("clobTokenIds")), _jload(m.get("outcomePrices"))
    if not (len(outcomes) == len(tokens) == len(prices) == 2):
        return []
    out = []
    for i in (0, 1):
        try:
            p = float(prices[i])
        except (TypeError, ValueError):
            continue
        if LO <= p <= HI:
            out.append((outcomes[i], i, tokens[i], p))
    return out


def log_entries(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    now = _utc_now()
    scanned = entered = skipped = 0
    for m in open_markets(now):
        scanned += 1
        for side, idx, token, p_mkt in candidates(m, now):
            if conn.execute("SELECT 1 FROM any_fav_trades WHERE token_id=?", (token,)).fetchone():
                continue
            reason = objective_skip(m)
            if reason:
                skipped += conn.execute("INSERT OR IGNORE INTO any_fav_skips VALUES (?,?,?,?,?)",
                                        (token, _iso(now), str(m.get("id")), m.get("question"), reason)).rowcount
                continue
            try:
                bid, ask, _, _ = public_book(token)
            except requests.RequestException:
                continue
            if ask is None or bid is None or ask - bid > MAX_SPREAD + 1e-9 or abs(ask - p_mkt) > MAX_DRIFT:
                continue
            if not (LO <= ask <= HI):
                continue
            rate = fee_rate(m)
            conn.execute(
                "INSERT OR IGNORE INTO any_fav_trades (logged_at, category, slug, question, end_date, side, market_id, "
                "outcome_idx, token_id, entry_ask, fee_rate, fee_per_share, volume) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (_iso(now), category(m), m.get("slug"), m.get("question"), m.get("endDate"), side, str(m.get("id")),
                 idx, token, ask, rate, rate * ask * (1 - ask), float(m.get("volumeNum") or 0)))
            entered += 1
            if not quiet:
                print(f"  ENTER [{category(m)}] {side} @ {ask:.2f} (mkt {p_mkt:.3f}, fee {rate:.2f}, "
                      f"ends {str(m.get('endDate'))[:10]}) {(m.get('question') or '')[:80]}")
    conn.commit()
    conn.close()
    if not quiet:
        print(f"[{_iso(now)}] any favourites: {scanned} markets scanned, {entered} entered, {skipped} new skips logged")


def settle(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    rows = conn.execute("SELECT id, market_id, outcome_idx, entry_ask, fee_per_share FROM any_fav_trades "
                        "WHERE status='open'").fetchall()
    settled = 0
    for pid, market_id, idx, ask, fee in rows:
        try:
            r = requests.get(f"{GAMMA_BASE}/markets/{market_id}", headers=HEADERS, timeout=TIMEOUT)
            m = r.json() if r.status_code == 200 else None
        except (requests.RequestException, ValueError):
            continue
        if not m or not m.get("closed"):
            continue
        try:
            p = float(_jload(m.get("outcomePrices"))[idx])
        except (TypeError, ValueError, IndexError):
            continue
        if p == 0.5:
            status, pnl = "void", 0.0
        elif p >= 0.99 or p <= 0.01:  # only a final resolution; a closed-but-unresolved price is skipped
            won = p >= 0.99
            status, pnl = ("won" if won else "lost"), ((1 - ask) / ask if won else -1.0) - fee / ask
        else:
            continue
        conn.execute("UPDATE any_fav_trades SET status=?, settled_at=?, pnl_per_dollar=? WHERE id=?",
                     (status, _iso(_utc_now()), pnl, pid))
        settled += 1
    conn.commit()
    conn.close()
    if not quiet and settled:
        print(f"settled {settled} any-category favourite(s)")


def report():
    conn = get_connection()
    conn.executescript(SCHEMA)
    open_n = conn.execute("SELECT COUNT(*) FROM any_fav_trades WHERE status='open'").fetchone()[0]
    rows = conn.execute("SELECT status, pnl_per_dollar FROM any_fav_trades WHERE status IN ('won','lost') "
                        "ORDER BY logged_at, id").fetchall()
    skips = conn.execute("SELECT reason, COUNT(*) FROM any_fav_skips GROUP BY reason").fetchall()
    conn.close()
    print(f"=== Any-category favourites (pre-registered {FROZEN}; buy {LO:.2f}-{HI:.2f}, 7-30 days out; "
          f"pass: n>={PASS_N}, CI>0, both halves>0) ===")
    print(f"open {open_n}, settled {len(rows)}; skipped (not objective): {dict(skips) or 'none'}")
    s = group_stats([r[1] for r in rows], PASS_N)
    if s:
        n, mean, clo, chi, h1, h2, passed = s
        wins = sum(1 for r in rows if r[0] == "won")
        print(f"won {wins}/{n} ({wins / n:.1%}); mean ROI {mean:+.2%} (flat ${FLAT_STAKE:.0f} -> "
              f"{mean * FLAT_STAKE * n:+,.0f}); 95% CI {clo:+.2%}..{chi:+.2%}; halves {h1:+.2%} / {h2:+.2%}; "
              f"{'PASS' if passed else 'not passed'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pre-registered PM any-category favourites paper test.")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.report:
        report()
    else:
        log_entries(quiet=args.quiet)
        settle(quiet=args.quiet)
