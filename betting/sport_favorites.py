"""
Sport favourites forward test -- the favourite-longshot bias outside tennis
================================================================================
PRE-REGISTERED, rules frozen 2026-11-20 (before any trade was logged).

Basis (historical, best-available prices):
  * Soccer favourites 2005-2026 (7,980 matches) won more often than priced:
    80%+ favourites priced 83.2% won 88.7% (+4.1% ROI at best odds). The
    0.70-0.80 bucket LOST even at best odds (-1.4% ROI), so it is excluded:
    soccer entry range is 0.80-0.95.
  * NBA heavy favourites 2023-25 priced 91.3% won 94.0%.
  The edge only survives at best-available prices, so a typical bookmaker
  margin eats it; Polymarket's small taker fee is the relevant venue.

Frozen rules (one table, sport_fav_trades; `tour` holds the group):
  * Soccer group, leagues SOCCER_LEAGUES (EPL, La Liga, Bundesliga, Serie A,
    Ligue 1, MLS, Champions League -- PM match-event slug prefixes): buy the
    favourite's 'Will <team> win' YES token (never the draw) when its market
    price AND best ask are both 0.80-0.95.
  * NBA group: buy the moneyline favourite when price AND ask are 0.85-0.97.
  * Entry only on a coherent two-sided book (spread <= 0.05, ask within 0.05
    of the market price), strictly before game start: the market's
    gameStartTime must be known and >= 30 min away. First qualifying
    observation is the entry; one entry per token ever; hold to settlement;
    flat $100; taker fee = 0.05 * p * (1-p) per share.
  * EXPLORATORY group 'other' (NFL, NHL, MLB), pre-registered 2026-11-20
    with NO historical validation, reported separately: buy the moneyline
    favourite when price AND ask are 0.85-0.97, same entry/settlement rules.
    Its result can motivate a study; it cannot by itself justify money.
  * Pass bar, per group: >= 300 settled, mean ROI > 0 with bootstrap 95% CI
    > 0, same sign in both chronological halves.

Paper only: never places an order, never touches a private key.

Usage:
    py sport_favorites.py             # discover + enter + settle (cron-friendly)
    py sport_favorites.py --report
"""

import argparse
import json
import random
import re
import sys
from datetime import datetime, timedelta, timezone

import requests

from db import get_connection
from polymarket_exec import public_book

GAMMA_BASE = "https://gamma-api.polymarket.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 20
FROZEN = "2026-11-20"
# slug prefix -> Gamma tag (PM tags are inconsistent: some leagues tag by prefix, some by name)
LEAGUE_TAGS = {"epl": "EPL", "lal": "la-liga", "bun": "bundesliga", "sea": "sea", "fl1": "ligue-1",
               "mls": "mls", "ucl": "ucl", "nba": "nba", "nfl": "nfl", "nhl": "nhl", "mlb": "mlb"}
OTHER_LEAGUES = {"nfl", "nhl", "mlb"}  # exploratory group
SOCCER_LEAGUES = set(LEAGUE_TAGS) - {"nba"} - OTHER_LEAGUES
RANGES = {"soccer": (0.80, 0.95), "nba": (0.85, 0.97), "other": (0.85, 0.97)}
MIN_LEAD = timedelta(minutes=30)
LOOKAHEAD = timedelta(days=14)
FLAT_STAKE = 100.0
TAKER_FEE_RATE = 0.05
PASS_N = 300
GAME_SLUG = re.compile(r"^([a-z0-9]+)-.+-\d{4}-\d{2}-\d{2}$")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA = """
CREATE TABLE IF NOT EXISTS sport_fav_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,
    tour TEXT,                        -- group: 'soccer' / 'nba' / 'other' (exploratory)
    slug TEXT NOT NULL,
    title TEXT,
    match_date TEXT,                  -- market gameStartTime (UTC ISO)
    player TEXT NOT NULL,             -- the favourite team bought
    market_id TEXT,
    outcome_idx INTEGER,              -- our index in the market's outcome list
    token_id TEXT NOT NULL UNIQUE,    -- idempotency: one entry per token ever
    entry_ask REAL NOT NULL,
    fee_per_share REAL,
    status TEXT NOT NULL DEFAULT 'open',   -- 'open' / 'won' / 'lost' / 'void'
    settled_at TEXT,
    pnl_per_dollar REAL,              -- profit per $1 staked, net of fee
    league TEXT                       -- slug prefix: epl, lal, ..., nba
);
"""


def _utc_now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _jload(v):
    return json.loads(v) if isinstance(v, str) else (v or [])


def _group(league):
    if league == "nba":
        return "nba"
    return "soccer" if league in SOCCER_LEAGUES else "other" if league in OTHER_LEAGUES else None


def _start(market):
    s = market.get("gameStartTime")
    try:
        dt = datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc) if dt and dt.tzinfo is None else dt


def game_events(now):
    """Open game events in our leagues starting within LOOKAHEAD, via each league's Gamma tag."""
    out = []
    for league, tag in LEAGUE_TAGS.items():
        offset = 0
        while True:
            r = requests.get(f"{GAMMA_BASE}/events", headers=HEADERS, timeout=TIMEOUT, params={
                "tag_slug": tag, "closed": "false", "limit": 100, "offset": offset,
                "end_date_min": _iso(now), "end_date_max": _iso(now + LOOKAHEAD)})
            r.raise_for_status()
            batch = r.json() or []
            for e in batch:
                m = GAME_SLUG.match(e.get("slug") or "")
                if m and m.group(1) == league:
                    out.append(e)
            if len(batch) < 100 or offset >= 1000:
                break
            offset += 100
    return out


def candidates(ev, now):
    """(team, market, outcome_idx, token, market_price) the frozen rule would consider."""
    league = GAME_SLUG.match(ev["slug"]).group(1)
    lo, hi = RANGES[_group(league)]
    out = []
    for m in ev.get("markets", []):
        if m.get("closed") or m.get("sportsMarketType") != "moneyline":
            continue
        start = _start(m)
        if start is None or start - now < MIN_LEAD:
            continue
        outcomes, tokens = _jload(m.get("outcomes")), _jload(m.get("clobTokenIds"))
        prices = _jload(m.get("outcomePrices"))
        if not (len(outcomes) == len(tokens) == len(prices) == 2):
            continue
        if league not in SOCCER_LEAGUES:  # NBA / NFL / NHL / MLB: two team-name outcomes
            picks = [(outcomes[i], i) for i in (0, 1)]
        else:  # soccer: per-team 'win' market, YES side only, never the draw
            title = m.get("groupItemTitle") or ""
            if not title or title.lower().startswith("draw") or [o.lower() for o in outcomes] != ["yes", "no"]:
                continue
            picks = [(title, 0)]
        for team, i in picks:
            try:
                p = float(prices[i])
            except (TypeError, ValueError):
                continue
            if lo <= p <= hi:
                out.append((team, m, i, tokens[i], p))
    return out


def log_entries(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    now = _utc_now()
    entered = scanned = 0
    for ev in game_events(now):
        scanned += 1
        league = GAME_SLUG.match(ev["slug"]).group(1)
        group = _group(league)
        lo, hi = RANGES[group]
        for team, m, idx, token, p_mkt in candidates(ev, now):
            if conn.execute("SELECT 1 FROM sport_fav_trades WHERE token_id=?", (token,)).fetchone():
                continue
            try:
                bid, ask, _, _ = public_book(token)
            except requests.RequestException:
                continue
            if ask is None or bid is None or ask - bid > 0.05 or abs(ask - p_mkt) > 0.05:
                continue
            if not (lo <= ask <= hi):
                continue
            fee = TAKER_FEE_RATE * ask * (1 - ask)
            conn.execute(
                "INSERT OR IGNORE INTO sport_fav_trades (logged_at, tour, league, slug, title, match_date, "
                "player, market_id, outcome_idx, token_id, entry_ask, fee_per_share) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (_iso(now), group, league, ev["slug"], ev.get("title"), _iso(_start(m)), team,
                 str(m.get("id")), idx, token, ask, fee))
            entered += 1
            if not quiet:
                print(f"  ENTER [{league}] {team} @ {ask:.2f} (mkt {p_mkt:.3f}, start {_iso(_start(m))}) {ev['slug']}")
    conn.commit()
    conn.close()
    if not quiet:
        print(f"[{_iso(now)}] sport favourites: {scanned} games scanned, {entered} entered")


def settle(quiet=False):
    conn = get_connection()
    conn.executescript(SCHEMA)
    rows = conn.execute("SELECT id, slug, market_id, outcome_idx, entry_ask, fee_per_share "
                        "FROM sport_fav_trades WHERE status='open'").fetchall()
    settled = 0
    for pid, slug, market_id, idx, ask, fee in rows:
        try:
            r = requests.get(f"{GAMMA_BASE}/events", params={"slug": slug}, headers=HEADERS, timeout=TIMEOUT)
            evs = r.json() or []
        except (requests.RequestException, ValueError):
            continue
        if not evs:
            continue
        market = next((m for m in evs[0].get("markets", []) if str(m.get("id")) == str(market_id)), None)
        if market is None or not market.get("closed"):
            continue
        prices = _jload(market.get("outcomePrices"))
        try:
            p = float(prices[idx])
        except (TypeError, ValueError, IndexError):
            continue
        if p == 0.5:  # cancelled / 50-50 resolution: stake returned, excluded from scoring
            status, pnl = "void", 0.0
        else:
            won = p > 0.5
            status = "won" if won else "lost"
            pnl = ((1 - ask) / ask if won else -1.0) - fee / ask
        conn.execute("UPDATE sport_fav_trades SET status=?, settled_at=?, pnl_per_dollar=? WHERE id=?",
                     (status, _iso(_utc_now()), pnl, pid))
        settled += 1
    conn.commit()
    conn.close()
    if not quiet and settled:
        print(f"settled {settled} sport favourite(s)")


def group_stats(pnls, min_n=PASS_N):
    """n, mean, CI lo, CI hi, half1, half2, passed -- pnls in chronological order."""
    n = len(pnls)
    if not n:
        return None
    rng = random.Random(0)
    boots = sorted(sum(rng.choices(pnls, k=n)) / n for _ in range(2000))
    half = n // 2
    h1 = sum(pnls[:half]) / max(half, 1)
    h2 = sum(pnls[half:]) / max(n - half, 1)
    mean = sum(pnls) / n
    passed = n >= min_n and mean > 0 and boots[50] > 0 and h1 > 0 and h2 > 0
    return n, mean, boots[50], boots[1949], h1, h2, passed


def report():
    conn = get_connection()
    conn.executescript(SCHEMA)
    print(f"=== Sport favourites forward test (pre-registered {FROZEN}; "
          f"pass: n>={PASS_N}, mean ROI>0, 95% CI>0, both halves>0) ===")
    for group, (lo, hi) in RANGES.items():
        open_n = conn.execute("SELECT COUNT(*) FROM sport_fav_trades WHERE tour=? AND status='open'",
                              (group,)).fetchone()[0]
        rows = conn.execute("SELECT status, pnl_per_dollar FROM sport_fav_trades WHERE tour=? "
                            "AND status IN ('won','lost') ORDER BY logged_at, id", (group,)).fetchall()
        tag = " (EXPLORATORY: NFL/NHL/MLB, no historical basis)" if group == "other" else ""
        print(f"--- {group}{tag}: buy {lo:.2f}-{hi:.2f}, hold to settlement --- open {open_n}, settled {len(rows)}")
        s = group_stats([r[1] for r in rows])
        if s is None:
            continue
        n, mean, clo, chi, h1, h2, passed = s
        wins = sum(1 for r in rows if r[0] == "won")
        print(f"won {wins}/{n} ({wins / n:.1%}); mean ROI {mean:+.2%} (flat ${FLAT_STAKE:.0f} -> "
              f"{mean * FLAT_STAKE * n:+,.0f}); 95% CI {clo:+.2%}..{chi:+.2%}; halves {h1:+.2%} / {h2:+.2%}; "
              f"{'PASS' if passed else 'not passed'}")
    conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pre-registered PM soccer/NBA (+ exploratory NFL/NHL/MLB) favourites paper test.")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.report:
        report()
    else:
        log_entries(quiet=args.quiet)
        settle(quiet=args.quiet)
