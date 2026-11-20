"""
Scheduled price logger — the measurement layer for trading Polymarket.

Every run takes ONE snapshot: for each upcoming Premier League fixture
listed on The Odds API, it records sportsbook decimal odds (DraftKings +
whichever books you request — include a sharp one like Pinnacle) and, when
Polymarket has the fixture listed, the live CLOB best bid / best ask /
ask depth for each of home/draw/away. Rows land in a price_snapshots
table in the same sports_data.sqlite3 as everything else.

Run it 2-4x per day via Task Scheduler (you already run collection jobs
this way). API budget: one Odds API request per run regardless of fixture
count, so 3x daily is ~90 of the free tier's 500/month. Polymarket reads
are free and unlimited.

After a few gameweeks, analyze_prices.py answers, from this table:
  - how often/large Polymarket diverges from the de-vigged sharp line
  - how often true cross-venue arbs appear
  - whether Polymarket lags the books after news (the speed edge)
  - paper-trade CLV for a "trade toward the sharp line" rule

Usage:
    py log_prices.py
    py log_prices.py --bookmakers draftkings,pinnacle,fanduel
"""

import argparse
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from db import get_connection
from odds_compare import (CLOB_BASE, ODDS_API_BASE, TIMEOUT,
                          gamma_find_event, parse_event_markets, teams_match)

# Defaults target what is in season and liquid on Polymarket: EPL, MLS,
# NBA (season opens late Oct; empty until then), NFL (the deepest PM sport),
# and MLB (pennant race + playoffs). The 2026 World Cup key is retired —
# the tournament ended in July. 2-way sports (NBA/NFL/MLB) share the H/A
# mapping in book_rows_for_event; no special-casing needed. Each sport is
# +1 Odds API credit per run: 5 sports x 3 runs/day = ~450 of the free
# 500/month, so add a 6th sport only after upgrading the plan or cutting
# to 2 runs/day. Tennis: The Odds API uses per-tournament keys that rotate
# (e.g. tennis_atp_us_open) — pass them in season via --sports rather than
# hardcoding one here that dies with the tournament.
# basketball_wnba holds the NBA's slot while its season is live (playoffs run
# Sep-Oct) and the NBA returns nothing; swap it back to basketball_nba when
# the NBA season opens in late October — same 2-way plumbing either way.
DEFAULT_SPORTS = ("soccer_epl,soccer_usa_mls,basketball_wnba,"
                  "americanfootball_nfl,baseball_mlb")

# Odds API billing: a bookmakers list of <=10 costs a flat 1 credit per call
# regardless of regions; region-based requests cost 1 credit PER REGION
# (us,us2,eu = 3x). So a curated 10-book list is the cheap mode:
# 1 credit x 3 sports x 3 runs/day = ~270/month of the free 500.
# Composition: pinnacle (the sharp benchmark) + betfair exchange + books
# verified to quote MLS (DK/Pinnacle don't).
DEFAULT_BOOKMAKERS = ("pinnacle,betfair_ex_eu,betonlineag,betmgm,draftkings,"
                      "fanduel,betrivers,ballybet,betanysports,betparx")

# US sports get their own 10 slots (same flat 1 credit): the MLS-niche books
# add nothing there, so their slots go to lowvig (near-Pinnacle prices, low
# margin -- directly better best-price) and diverse US retail books (soft
# quotes are where best-price value lives; July data: best-of-27-books beat
# US-accessible-only by ~4.4 points of hold).
US_SPORTS_BOOKMAKERS = ("pinnacle,lowvig,betonlineag,bovada,betfair_ex_eu,"
                        "draftkings,fanduel,betmgm,espnbet,hardrockbet")
SPORT_BOOKMAKERS = {
    "americanfootball": US_SPORTS_BOOKMAKERS,
    "baseball": US_SPORTS_BOOKMAKERS,
    "basketball": US_SPORTS_BOOKMAKERS,
    "icehockey": US_SPORTS_BOOKMAKERS,
}

SNAPSHOT_SCHEMA = """
CREATE TABLE IF NOT EXISTS price_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,      -- UTC ISO, same for every row in one run
    league TEXT NOT NULL,
    commence_time TEXT,               -- kickoff, UTC ISO (from The Odds API)
    home_team TEXT NOT NULL,          -- Odds API full names are canonical here
    away_team TEXT NOT NULL,
    outcome TEXT NOT NULL,            -- 'H' / 'D' / 'A'
    venue TEXT NOT NULL,              -- 'polymarket' or a bookmaker key
    price REAL,                       -- cost per $1 payout (PM best ask, or 1/odds)
    bid REAL,                         -- PM best bid (NULL for bookmakers)
    ask_size REAL,                    -- shares available at PM best ask
    decimal_odds REAL,                -- bookmaker decimal odds (NULL for PM)
    pm_event_slug TEXT,
    pm_token_id TEXT                  -- YES token for this outcome; what an order needs
);
CREATE INDEX IF NOT EXISTS idx_snap_fixture
    ON price_snapshots(home_team, away_team, commence_time);
CREATE INDEX IF NOT EXISTS idx_snap_time ON price_snapshots(snapshot_time);
"""


def init_snapshot_table():
    conn = get_connection()
    conn.executescript(SNAPSHOT_SCHEMA)
    # CREATE TABLE IF NOT EXISTS never adds columns to an existing table
    cols = {row[1] for row in conn.execute("PRAGMA table_info(price_snapshots)")}
    if "pm_token_id" not in cols:
        conn.execute("ALTER TABLE price_snapshots ADD COLUMN pm_token_id TEXT")
    conn.commit()
    conn.close()


def fetch_fixtures(sport, bookmakers):
    """
    One Odds API call: every upcoming fixture for `sport` with h2h odds.
    bookmakers=[] fetches ALL books in the regions — The Odds API charges by
    region, not bookmaker count, so filtering only loses coverage (it cost
    us every MLS sharp line: DK/Pinnacle don't quote MLS, other books do).
    """
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        raise SystemExit("Missing ODDS_API_KEY in .env")
    params = {"apiKey": api_key, "regions": "us,us2,eu",
              "markets": "h2h", "oddsFormat": "decimal"}
    if bookmakers:
        params["bookmakers"] = ",".join(bookmakers)
    r = requests.get(f"{ODDS_API_BASE}/sports/{sport}/odds", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json(), r.headers.get("x-requests-remaining")


def clob_book(token_id):
    """(best_bid, best_ask, ask_size) from the live Polymarket order book."""
    r = requests.get(f"{CLOB_BASE}/book", params={"token_id": token_id}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    asks = [(float(a["price"]), float(a["size"]))
            for a in data.get("asks", []) if float(a.get("size", 0)) > 0]
    bids = [(float(b["price"]), float(b["size"]))
            for b in data.get("bids", []) if float(b.get("size", 0)) > 0]
    best_ask, ask_size = min(asks, key=lambda x: x[0]) if asks else (None, None)
    best_bid = max(bids, key=lambda x: x[0])[0] if bids else None
    return best_bid, best_ask, ask_size


def book_rows_for_event(ev):
    """Map one Odds API event's bookmaker odds to (venue, outcome, odds) rows."""
    rows = []
    for bm in ev.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] != "h2h":
                continue
            for oc in mkt["outcomes"]:
                if oc["name"].lower() == "draw":
                    key = "D"
                elif teams_match(ev["home_team"], oc["name"]):
                    key = "H"
                elif teams_match(ev["away_team"], oc["name"]):
                    key = "A"
                else:
                    continue
                rows.append((bm["key"], key, float(oc["price"])))
    return rows


def polymarket_rows_for_event(ev):
    """(outcome, bid, ask, ask_size, yes_token_id) rows + slug, or [] if PM doesn't list it."""
    event = gamma_find_event(ev["home_team"], ev["away_team"],
                             commence_time=ev.get("commence_time"))
    if event is None:
        return [], None
    slug = event.get("slug")
    markets = parse_event_markets(event, ev["home_team"], ev["away_team"])
    rows = []
    for key, m in markets.items():
        bid = ask = size = None
        if m["yes_token_id"]:
            try:
                bid, ask, size = clob_book(m["yes_token_id"])
            except requests.RequestException:
                pass
        if ask is None:
            ask = m["gamma_price"]  # indicative fallback
        if ask is not None:
            rows.append((key, bid, ask, size, m["yes_token_id"]))
    return rows, slug


if __name__ == "__main__":
    load_dotenv(override=True)
    parser = argparse.ArgumentParser(description="Snapshot Polymarket + sportsbook prices for upcoming fixtures.")
    parser.add_argument("--bookmakers", default=DEFAULT_BOOKMAKERS,
                        help="Odds API bookmaker keys (<=10 = flat 1 credit/call; '' = all "
                             "books but bills per region, ~3x cost)")
    parser.add_argument("--sports", default=DEFAULT_SPORTS,
                        help="comma-separated Odds API sport keys; each costs 1 request per run")
    args = parser.parse_args()
    books = [b.strip() for b in args.bookmakers.split(",") if b.strip()]
    sports = [s.strip() for s in args.sports.split(",") if s.strip()]

    init_snapshot_table()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_db_rows = []
    for sport in sports:
        sport_books = books
        if args.bookmakers == DEFAULT_BOOKMAKERS:   # only override the default, never a CLI choice
            override = SPORT_BOOKMAKERS.get(sport.split("_")[0])
            if override:
                sport_books = [b.strip() for b in override.split(",")]
        try:
            fixtures, remaining = fetch_fixtures(sport, sport_books)
        except requests.RequestException as e:
            print(f"[{now}] {sport}: fetch failed ({e}) — skipping")
            continue
        print(f"[{now}] {sport}: {len(fixtures)} upcoming fixtures "
              f"(Odds API requests left: {remaining})")

        pm_listed = 0
        for ev in fixtures:
            base = (now, sport, ev.get("commence_time"), ev["home_team"], ev["away_team"])
            for venue, key, odds in book_rows_for_event(ev):
                all_db_rows.append(base + (key, venue, 1.0 / odds, None, None, odds, None, None))
            try:
                pm_rows, slug = polymarket_rows_for_event(ev)
            except requests.RequestException as e:
                print(f"  ! Polymarket fetch failed for {ev['home_team']} vs {ev['away_team']}: {e}")
                pm_rows, slug = [], None
            if pm_rows:
                pm_listed += 1
                for key, bid, ask, size, token_id in pm_rows:
                    all_db_rows.append(base + (key, "polymarket", ask, bid, size, None, slug, token_id))
        print(f"  {pm_listed}/{len(fixtures)} fixtures listed on Polymarket")

    conn = get_connection()
    conn.executemany(
        "INSERT INTO price_snapshots (snapshot_time, league, commence_time, home_team, away_team, "
        "outcome, venue, price, bid, ask_size, decimal_odds, pm_event_slug, pm_token_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", all_db_rows)
    conn.commit()
    conn.close()
    print(f"  stored {len(all_db_rows)} price rows total")
