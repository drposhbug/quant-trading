"""
SQLite storage for club match data — replaces re-fetching from
football-data.co.uk / American Soccer Analysis on every run.

One denormalized `matches` table rather than separate matches/team_stats/
head_to_head tables: every stat here (elo_diff, h2h_home_win_rate,
recent_form_diff, odds) is inherently a property of one specific match, not
a standalone entity worth joining against, so splitting it out would add
query complexity for no real benefit.

Injuries DO get their own tables (nba_injury_snapshots / nba_news, see
NBA_INJURY_SCHEMA), because unlike everything above they are per-PLAYER and
per-OBSERVATION, not per-match: a single game is preceded by many changing
injury reports, and which report was current at bet time is the whole point.
They are append-only snapshots for that reason — see nba_injuries.py. The
qualitative Grok/Gemini research in external_factors_reports/ still exists
alongside them and remains the only lineup signal for the soccer leagues.

Usage: import init_db(), then insert_matches()/fetch_matches_df() from
ingest scripts and trainers.
"""

import os
import sqlite3

# SPORTS_DB_PATH overrides (the cloud favourites ledger uses betting/paper_favorites.sqlite3)
DB_PATH = os.environ.get("SPORTS_DB_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sports_data.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league TEXT NOT NULL,
    date TEXT NOT NULL,
    season TEXT,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    result TEXT,              -- 'H' / 'D' / 'A'
    knockout INTEGER DEFAULT 0,

    -- engineered features, as-of just before this match (no leakage)
    elo_diff REAL,
    h2h_home_win_rate REAL,
    h2h_meetings INTEGER,
    recent_form_diff REAL,
    elo_form_interaction REAL,
    elo_h2h_interaction REAL,

    -- expected-goals features (Understat), only populated for 2014-25
    -- onward (Understat's coverage window); NULL elsewhere
    xg_for_diff REAL,
    xg_against_diff REAL,
    xg_overperformance_diff REAL,

    -- rolling shot-stat features (football-data.co.uk HS/HST columns,
    -- ~2000-01 onward); NULL for older seasons. Shots-on-target-based
    -- strength is a better forward-looking signal than raw results, and
    -- unlike xG it comes free in the CSVs already being ingested.
    shots_for_diff REAL,       -- last-5 avg shots taken, home minus away
    sot_for_diff REAL,         -- last-5 avg shots ON TARGET taken, home minus away
    sot_against_diff REAL,     -- last-5 avg shots on target CONCEDED, home minus away

    -- bookmaker odds (decimal), where available — used for ROI backtesting,
    -- not just accuracy/log-loss. odds_* = market average (the consensus
    -- fair line). odds_max_* = best price across all tracked books
    -- (football-data MaxH 2019+ / BbMxH before that) — what a line-shopping
    -- bettor actually gets paid, typically 3-6% above average.
    odds_home REAL,
    odds_draw REAL,
    odds_away REAL,
    odds_max_home REAL,
    odds_max_draw REAL,
    odds_max_away REAL,

    UNIQUE(league, date, home_team, away_team)
);
CREATE INDEX IF NOT EXISTS idx_matches_league_date ON matches(league, date);
"""


# NBA lives in its own table rather than the soccer `matches` table above.
# Basketball is a 2-way market (no draw — overtime settles ties), and its
# predictive signals are completely different (rest days, back-to-backs,
# rolling net rating / pace from the box score) with none of soccer's
# xG/shots/3-way-odds columns. Forcing both into one denormalized table would
# mean a dozen always-NULL columns on each side, so they stay separate.
# Downstream live code (log_prices/analyze_prices/paper_trades) keys on
# league + team names, so it doesn't care which table the history came from.
NBA_SCHEMA = """
CREATE TABLE IF NOT EXISTS nba_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    league TEXT NOT NULL DEFAULT 'nba',
    game_id TEXT NOT NULL,          -- nba_api GAME_ID (stable across seasons)
    date TEXT NOT NULL,             -- YYYY-MM-DD
    season TEXT,                    -- e.g. '2023-24'
    season_type TEXT,               -- 'Regular Season' / 'Playoffs'
    home_team TEXT NOT NULL,        -- full team name, e.g. 'Indiana Pacers'
    away_team TEXT NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    result TEXT,                    -- 'H' / 'A' (no draws in the NBA)

    -- engineered features, as-of just before tip-off (no leakage), see
    -- nba_features.py. home minus away where it reads as a difference.
    elo_diff REAL,
    form_diff REAL,                 -- last-N win% difference
    net_rating_diff REAL,           -- rolling last-N net rating (pts/100 poss)
    pace_diff REAL,                 -- rolling last-N pace (possessions/48)
    rest_diff REAL,                 -- days rest, home minus away (capped)
    b2b_diff REAL,                  -- away_back_to_back minus home_back_to_back
    elo_form_interaction REAL,

    UNIQUE(game_id, home_team, away_team)
);
CREATE INDEX IF NOT EXISTS idx_nba_league_date ON nba_games(league, date);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.executescript(NBA_SCHEMA)
    conn.executescript(NBA_INJURY_SCHEMA)
    conn.executescript(TENNIS_SCHEMA)
    conn.executescript(NEWS_SCHEMA)
    conn.executescript(POSITIONS_SCHEMA)
    _migrate(conn)
    conn.commit()
    conn.close()


def _migrate(conn):
    """
    CREATE TABLE IF NOT EXISTS does nothing when the table already exists,
    so new columns added to SCHEMA never reach an existing sports_data.sqlite3.
    This adds any missing columns in place — no need to delete the DB and
    re-ingest everything after pulling schema changes.
    """
    existing = {row[1] for row in conn.execute("PRAGMA table_info(matches)")}
    for col in ("shots_for_diff", "sot_for_diff", "sot_against_diff",
                "odds_max_home", "odds_max_draw", "odds_max_away"):
        if col not in existing:
            conn.execute(f"ALTER TABLE matches ADD COLUMN {col} REAL")
    # price_snapshots is created by log_prices.py, so it may not exist yet.
    # The token id is what trader.py needs to actually place an order; the
    # slug alone only identifies the event page.
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "price_snapshots" in tables:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(price_snapshots)")}
        if "pm_token_id" not in cols:
            conn.execute("ALTER TABLE price_snapshots ADD COLUMN pm_token_id TEXT")


def upsert_matches(rows):
    """
    rows: list of dicts matching the matches table columns (missing keys
    default to NULL). Idempotent on (league, date, home_team, away_team),
    so re-running an ingest script after a new gameweek is safe.

    Uses ON CONFLICT ... DO UPDATE (not INSERT OR REPLACE) deliberately:
    OR REPLACE deletes the whole old row and inserts a fresh one, which
    silently reset the xg_* columns to NULL every time the ingest re-ran.
    DO UPDATE only touches the columns this ingest owns, so features
    written by ingest_understat_xg.py survive.
    """
    if not rows:
        return 0
    columns = ["league", "date", "season", "home_team", "away_team", "home_score", "away_score",
               "result", "knockout", "elo_diff", "h2h_home_win_rate", "h2h_meetings",
               "recent_form_diff", "elo_form_interaction", "elo_h2h_interaction",
               "shots_for_diff", "sot_for_diff", "sot_against_diff",
               "odds_home", "odds_draw", "odds_away",
               "odds_max_home", "odds_max_draw", "odds_max_away"]
    key_columns = ("league", "date", "home_team", "away_team")
    update_columns = [c for c in columns if c not in key_columns]
    placeholders = ", ".join("?" for _ in columns)
    assignments = ", ".join(f"{c} = excluded.{c}" for c in update_columns)
    sql = (f"INSERT INTO matches ({', '.join(columns)}) VALUES ({placeholders}) "
           f"ON CONFLICT(league, date, home_team, away_team) DO UPDATE SET {assignments}")

    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in columns) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def update_xg_features(rows, league="premier_league"):
    """
    rows: list of dicts with date (YYYY-MM-DD), home_team, away_team,
    xg_for_diff, xg_against_diff, xg_overperformance_diff. Matches against
    existing rows on the date portion only (football-data.co.uk stores
    midnight timestamps, Understat stores real kickoff times, so exact
    datetime string equality won't line up).
    """
    conn = get_connection()
    n_updated = 0
    for r in rows:
        # exact date first; then +/-1 day — late kickoffs can land on different
        # calendar dates between Understat (kickoff datetime) and
        # football-data (listed match date)
        cur = conn.execute(
            "UPDATE matches SET xg_for_diff = ?, xg_against_diff = ?, xg_overperformance_diff = ? "
            "WHERE league = ? AND home_team = ? AND away_team = ? "
            "AND substr(date, 1, 10) BETWEEN date(?, '-1 day') AND date(?, '+1 day')",
            (r["xg_for_diff"], r["xg_against_diff"], r["xg_overperformance_diff"],
             league, r["home_team"], r["away_team"], r["date"], r["date"]),
        )
        n_updated += cur.rowcount
    conn.commit()
    conn.close()
    return n_updated


PAPER_TRADES_SCHEMA = """
CREATE TABLE IF NOT EXISTS paper_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,          -- UTC ISO, when the signal fired
    league TEXT NOT NULL,
    commence_time TEXT,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    outcome TEXT NOT NULL,            -- 'H' / 'D' / 'A'
    side TEXT NOT NULL,               -- 'buy_yes' / 'sell_yes'
    entry_price REAL NOT NULL,        -- PM ask (buy) or bid (sell) at signal time
    depth REAL,                       -- shares available at that price (fill realism)
    fair_prob REAL,                   -- de-vigged sharp-book probability
    model_prob REAL,                  -- model's probability (NULL if unavailable)
    edge REAL NOT NULL,               -- fair_prob - entry_price (sign-adjusted for side)
    suggested_stake REAL,             -- from bet_sizer at the configured bankroll
    UNIQUE(logged_at, home_team, away_team, outcome, side)
);
"""


def init_paper_trades():
    conn = get_connection()
    conn.executescript(PAPER_TRADES_SCHEMA)
    conn.commit()
    conn.close()


def log_paper_trades(rows):
    """rows: list of dicts matching paper_trades columns. Idempotent per signal."""
    if not rows:
        return 0
    cols = ["logged_at", "league", "commence_time", "home_team", "away_team",
            "outcome", "side", "entry_price", "depth", "fair_prob", "model_prob",
            "edge", "suggested_stake"]
    sql = (f"INSERT OR IGNORE INTO paper_trades ({', '.join(cols)}) "
           f"VALUES ({', '.join('?' for _ in cols)})")
    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in cols) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


NBA_COLUMNS = ["league", "game_id", "date", "season", "season_type",
               "home_team", "away_team", "home_score", "away_score", "result",
               "elo_diff", "form_diff", "net_rating_diff", "pace_diff",
               "rest_diff", "b2b_diff", "elo_form_interaction"]


def upsert_nba_games(rows):
    """
    rows: list of dicts matching nba_games columns (missing keys -> NULL).
    Idempotent on (game_id, home_team, away_team), so re-running the ingest
    after new games is safe. Same ON CONFLICT DO UPDATE pattern as
    upsert_matches so a re-run refreshes engineered features in place.
    """
    if not rows:
        return 0
    key_columns = ("game_id", "home_team", "away_team")
    update_columns = [c for c in NBA_COLUMNS if c not in key_columns]
    placeholders = ", ".join("?" for _ in NBA_COLUMNS)
    assignments = ", ".join(f"{c} = excluded.{c}" for c in update_columns)
    sql = (f"INSERT INTO nba_games ({', '.join(NBA_COLUMNS)}) VALUES ({placeholders}) "
           f"ON CONFLICT(game_id, home_team, away_team) DO UPDATE SET {assignments}")
    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in NBA_COLUMNS) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def fetch_nba_games(include_playoffs=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM nba_games"
    if not include_playoffs:
        query += " WHERE season_type = 'Regular Season'"
    query += " ORDER BY date, game_id"
    rows = [dict(r) for r in conn.execute(query).fetchall()]
    conn.close()
    return rows


def fetch_matches(league, exclude_knockout=True):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM matches WHERE league = ?"
    params = [league]
    if exclude_knockout:
        query += " AND knockout = 0"
    query += " ORDER BY date"
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print(f"Initialized database at {DB_PATH}")


# Injuries are stored as APPEND-ONLY SNAPSHOTS, not as a current-state table
# that gets overwritten. The reason is the same one that makes price_snapshots
# a log rather than a "latest price" row: to ever test whether injury news is
# worth money, you need to know what the report said BEFORE tip-off, not what
# it says now. A mutable table would silently overwrite exactly the history
# that makes the data useful, and by the time you noticed, it would be
# unrecoverable — ESPN publishes only the current report, with no archive.
#
# The player-value columns (pie/mpg/impact_units) are denormalized onto each
# row on purpose: a player's value drifts over a season, and the number that
# matters is what it was at snapshot time, not what a later lookup would say.
NBA_INJURY_SCHEMA = """
CREATE TABLE IF NOT EXISTS nba_injury_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_time TEXT NOT NULL,    -- UTC ISO, when we observed the report
    team TEXT NOT NULL,             -- nba_api full name, e.g. 'Boston Celtics'
    player TEXT NOT NULL,
    position TEXT,
    status TEXT,                    -- ESPN wording: 'Out', 'Day-To-Day', ...
    status_weight REAL,             -- P(misses the game), see nba_injuries.STATUS_WEIGHT
    injury_type TEXT,               -- 'Knee', 'Foot', ...
    detail TEXT,                    -- 'Soreness', 'Fracture', ...
    side TEXT,                      -- 'Left' / 'Right'
    return_date TEXT,               -- ESPN's estimate, may be NULL
    comment TEXT,                   -- short human-readable note
    report_date TEXT,               -- ESPN's timestamp ON THE ITEM (news age)
    pie REAL,                       -- Player Impact Estimate at snapshot time
    mpg REAL,                       -- minutes per game at snapshot time
    impact_units REAL,              -- (pie - replacement) * mpg, floored at 0
    value_season TEXT,              -- season the pie/mpg came from; older than the
                                    -- current one means the player missed a full
                                    -- season, which is itself signal

    UNIQUE(snapshot_time, team, player)
);
CREATE INDEX IF NOT EXISTS idx_nba_inj_team_time
    ON nba_injury_snapshots(team, snapshot_time);
CREATE INDEX IF NOT EXISTS idx_nba_inj_time
    ON nba_injury_snapshots(snapshot_time);

CREATE TABLE IF NOT EXISTS nba_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT,                -- ESPN article id; dedupe key
    published TEXT,                 -- UTC ISO, when ESPN published it
    headline TEXT NOT NULL,
    description TEXT,
    byline TEXT,
    url TEXT,
    fetched_at TEXT,                -- UTC ISO, when we pulled it

    UNIQUE(article_id)
);
CREATE INDEX IF NOT EXISTS idx_nba_news_published ON nba_news(published);
"""

INJURY_COLUMNS = ["snapshot_time", "team", "player", "position", "status",
                  "status_weight", "injury_type", "detail", "side",
                  "return_date", "comment", "report_date", "pie", "mpg",
                  "impact_units", "value_season"]

NEWS_COLUMNS = ["article_id", "published", "headline", "description",
                "byline", "url", "fetched_at"]


def init_nba_injuries():
    conn = get_connection()
    conn.executescript(NBA_INJURY_SCHEMA)
    conn.commit()
    conn.close()


def log_injury_snapshot(rows):
    """
    rows: list of dicts matching nba_injury_snapshots columns. INSERT OR IGNORE
    on (snapshot_time, team, player), so re-running the same snapshot is a
    no-op rather than a duplicate — but a LATER snapshot of the same player
    always lands as a new row, which is the point.
    """
    if not rows:
        return 0
    sql = (f"INSERT OR IGNORE INTO nba_injury_snapshots "
           f"({', '.join(INJURY_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in INJURY_COLUMNS)})")
    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in INJURY_COLUMNS) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def log_nba_news(rows):
    """rows: list of dicts matching nba_news columns. Idempotent per article."""
    if not rows:
        return 0
    sql = (f"INSERT OR IGNORE INTO nba_news ({', '.join(NEWS_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in NEWS_COLUMNS)})")
    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in NEWS_COLUMNS) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def fetch_injuries_as_of(as_of=None, team=None):
    """
    The report as it stood at a moment in time — the query the whole
    append-only design exists to make possible.

    For each player, returns the most recent snapshot row at or before `as_of`
    (UTC ISO string; None = latest available). Pass `team` to restrict to one
    club. Use this, never "the latest row overall", when reconstructing what
    was known before a game that has already been played.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    where, params = [], []
    if as_of:
        where.append("snapshot_time <= ?")
        params.append(as_of)
    if team:
        where.append("team = ?")
        params.append(team)
    clause = f"WHERE {' AND '.join(where)}" if where else ""
    # window function: rank each player's snapshots newest-first, keep rank 1
    sql = f"""
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY team, player ORDER BY snapshot_time DESC
            ) AS rn
            FROM nba_injury_snapshots {clause}
        ) WHERE rn = 1
        ORDER BY team, impact_units DESC
    """
    rows = [dict(r) for r in conn.execute(sql, params)]
    conn.close()
    for r in rows:
        r.pop("rn", None)
    return rows


# Tennis gets its own table for the same reason NBA does: the entities differ.
# A tennis row is PLAYER vs PLAYER on a SURFACE with no home side, and it
# carries three prices per player (sharp / best-of-book / market average),
# which is what makes the execution analysis in tennis_diagnose.py possible.
# Players are stored as p1/p2 ordered ALPHABETICALLY -- an outcome-independent
# rule -- with p1_won as the label, so nothing about the result can leak in
# through the column ordering.
TENNIS_SCHEMA = """
CREATE TABLE IF NOT EXISTS tennis_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour TEXT NOT NULL,             -- 'ATP' / 'WTA'
    date TEXT NOT NULL,             -- YYYY-MM-DD
    year INTEGER,
    tournament TEXT,
    surface TEXT,                   -- 'Hard' / 'Clay' / 'Grass'
    round TEXT,
    best_of INTEGER,
    comment TEXT,                   -- 'Completed' / 'Retired'

    p1 TEXT NOT NULL,               -- alphabetically first player
    p2 TEXT NOT NULL,
    p1_won INTEGER NOT NULL,        -- 1 if p1 won

    p1_rank REAL, p2_rank REAL,
    p1_pts REAL,  p2_pts REAL,

    -- decimal odds, already un-permuted to player identity
    p1_ps REAL,  p2_ps REAL,        -- Pinnacle (the sharp line)
    p1_max REAL, p2_max REAL,       -- best price across tracked books
    p1_avg REAL, p2_avg REAL,       -- market average

    UNIQUE(tour, date, p1, p2)
);
CREATE INDEX IF NOT EXISTS idx_tennis_date ON tennis_matches(date);
CREATE INDEX IF NOT EXISTS idx_tennis_tour_year ON tennis_matches(tour, year);
"""

TENNIS_COLUMNS = ["tour", "date", "year", "tournament", "surface", "round",
                  "best_of", "comment", "p1", "p2", "p1_won",
                  "p1_rank", "p2_rank", "p1_pts", "p2_pts",
                  "p1_ps", "p2_ps", "p1_max", "p2_max", "p1_avg", "p2_avg"]


def upsert_tennis_matches(rows):
    """rows: dicts matching tennis_matches columns. Idempotent per match."""
    if not rows:
        return 0
    key = ["tour", "date", "p1", "p2"]
    upd = [c for c in TENNIS_COLUMNS if c not in key]
    sql = (f"INSERT INTO tennis_matches ({', '.join(TENNIS_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in TENNIS_COLUMNS)}) "
           f"ON CONFLICT({', '.join(key)}) DO UPDATE SET "
           + ", ".join(f"{c}=excluded.{c}" for c in upd))
    conn = get_connection()
    conn.executemany(sql, [tuple(r.get(c) for c in TENNIS_COLUMNS) for r in rows])
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def fetch_tennis_matches(tour=None):
    """Chronological list of tennis matches, optionally one tour."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    sql = "SELECT * FROM tennis_matches"
    params = []
    if tour:
        sql += " WHERE tour = ?"
        params.append(tour)
    sql += " ORDER BY date, id"
    rows = [dict(r) for r in conn.execute(sql, params)]
    conn.close()
    return rows


# Generic news/wire items across sports and sources. Separate from nba_news
# (which is ESPN-NBA-specific and already in use) because the question this
# table answers is different: nba_news stores WHAT was said, this stores HOW
# FAST we heard it.
#
# first_seen is the whole point and is why this is INSERT OR IGNORE on
# (source, item_id): the first observation of an item must never be
# overwritten by a later poll, or the latency measurement destroys itself.
# published - first_seen is the feed's real lag, which is the number that
# decides whether a paid low-latency feed would buy anything.
NEWS_SCHEMA = """
CREATE TABLE IF NOT EXISTS news_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,           -- 'espn_news' / 'espn_injuries' / ...
    sport TEXT,                     -- 'nba', 'tennis', ...
    item_id TEXT NOT NULL,          -- stable id from the source
    kind TEXT,                      -- 'article' / 'injury'
    published TEXT,                 -- source's own timestamp (UTC ISO)
    first_seen TEXT NOT NULL,       -- when WE first observed it (UTC ISO)
    subject TEXT,                   -- player/team the item is about
    headline TEXT,
    summary TEXT,
    url TEXT,

    UNIQUE(source, item_id)
);
CREATE INDEX IF NOT EXISTS idx_news_items_seen ON news_items(first_seen);
CREATE INDEX IF NOT EXISTS idx_news_items_sport ON news_items(sport, first_seen);
"""

NEWS_ITEM_COLUMNS = ["source", "sport", "item_id", "kind", "published",
                     "first_seen", "subject", "headline", "summary", "url"]


def init_news_items():
    conn = get_connection()
    conn.executescript(NEWS_SCHEMA)
    conn.commit()
    conn.close()


def log_news_items(rows):
    """
    Append-only. Returns how many were NEW -- that count is the useful signal
    from a poll, since re-seeing an item is a no-op by design.
    """
    if not rows:
        return 0
    sql = (f"INSERT OR IGNORE INTO news_items ({', '.join(NEWS_ITEM_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in NEWS_ITEM_COLUMNS)})")
    conn = get_connection()
    before = conn.total_changes
    conn.executemany(sql, [tuple(r.get(c) for c in NEWS_ITEM_COLUMNS) for r in rows])
    conn.commit()
    n = conn.total_changes - before
    conn.close()
    return n


# Open and closed Polymarket positions, paper ('dry') or real ('live'). One row
# per position for its whole life -- entry fields written at open, exit fields
# at close -- because the P&L of a position is a property of the pair, and the
# exit is the part this strategy is built around: it takes profit when the
# price converges to the sharp line, or gets out before kickoff, rather than
# holding a coin-flip to resolution. Realized pnl is in dollars, after fees.
POSITIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL,               -- 'dry' (simulated fills) / 'live'
    opened_at TEXT NOT NULL,          -- UTC ISO
    league TEXT,
    commence_time TEXT,               -- kickoff, UTC ISO
    home_team TEXT,
    away_team TEXT,
    outcome TEXT,                     -- 'H' / 'D' / 'A' the market is about
    token_side TEXT NOT NULL,         -- 'YES' / 'NO' -- which token we are LONG
    token_id TEXT,
    entry_price REAL NOT NULL,        -- paid per $1 share
    size REAL NOT NULL,               -- shares
    fair_at_entry REAL,               -- sharp-line fair value OF THIS TOKEN
    sharp_book TEXT,
    entry_order_id TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    closed_at TEXT,
    exit_price REAL,
    exit_reason TEXT,                 -- 'converged' / 'take_profit' / 'stop' / 'pre_kickoff' / 'manual'
    exit_order_id TEXT,
    fair_at_exit REAL,
    fees REAL,
    pnl REAL
);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status, mode);
"""

POSITION_OPEN_COLUMNS = ["mode", "opened_at", "league", "commence_time", "home_team",
                         "away_team", "outcome", "token_side", "token_id",
                         "entry_price", "size", "fair_at_entry", "sharp_book",
                         "entry_order_id"]


def init_positions():
    conn = get_connection()
    conn.executescript(POSITIONS_SCHEMA)
    conn.commit()
    conn.close()


def open_position(row):
    """row: dict with POSITION_OPEN_COLUMNS. -> new position id."""
    sql = (f"INSERT INTO positions ({', '.join(POSITION_OPEN_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in POSITION_OPEN_COLUMNS)})")
    conn = get_connection()
    cur = conn.execute(sql, tuple(row.get(c) for c in POSITION_OPEN_COLUMNS))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def close_position(pid, closed_at, exit_price, exit_reason, fees, pnl,
                   exit_order_id=None, fair_at_exit=None):
    conn = get_connection()
    conn.execute(
        "UPDATE positions SET status='closed', closed_at=?, exit_price=?, exit_reason=?, "
        "exit_order_id=?, fair_at_exit=?, fees=?, pnl=? WHERE id=? AND status='open'",
        (closed_at, exit_price, exit_reason, exit_order_id, fair_at_exit, fees, pnl, pid))
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n


def fetch_positions(status=None, mode=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    where, params = [], []
    if status:
        where.append("status = ?"); params.append(status)
    if mode:
        where.append("mode = ?"); params.append(mode)
    clause = f"WHERE {' AND '.join(where)}" if where else ""
    rows = [dict(r) for r in conn.execute(
        f"SELECT * FROM positions {clause} ORDER BY opened_at", params)]
    conn.close()
    return rows


# --------------------------------------------------------------- exec probes
# One row per entry signal: what a TAKER would have paid (lift the ask, pay
# the fee) vs what a MAKER would have (rest at bid+tick, no fee, fill only if
# the market trades through). Scored against the last pre-kickoff mid, this
# settles the taker-vs-maker execution question with data instead of theory:
# the maker saves fee+spread but suffers adverse selection on which signals
# actually fill. Probes never place orders in any mode.

EXEC_PROBES_SCHEMA = """
CREATE TABLE IF NOT EXISTS exec_probes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT NOT NULL,          -- UTC ISO, when the signal fired
    league TEXT,
    commence_time TEXT,
    home_team TEXT,
    away_team TEXT,
    outcome TEXT,                     -- 'H' / 'D' / 'A'
    token_side TEXT,                  -- 'YES' / 'NO'
    token_id TEXT NOT NULL,
    fair_at_entry REAL,               -- sharp fair value OF THIS TOKEN
    taker_price REAL,                 -- best ask at signal time
    taker_fee_bps INTEGER,
    maker_price REAL,                 -- where the maker order would rest
    maker_state TEXT NOT NULL DEFAULT 'resting',  -- 'resting'/'filled'/'cancelled'
    maker_filled_at TEXT,
    close_time TEXT,
    close_mid REAL,                   -- last pre-kickoff PM mid (the score)
    status TEXT NOT NULL DEFAULT 'open'
);
CREATE INDEX IF NOT EXISTS idx_probes_status ON exec_probes(status);
"""

PROBE_OPEN_COLUMNS = ["logged_at", "league", "commence_time", "home_team",
                      "away_team", "outcome", "token_side", "token_id",
                      "fair_at_entry", "fair_consensus", "taker_price",
                      "taker_fee_bps", "maker_price"]


def init_exec_probes():
    conn = get_connection()
    conn.executescript(EXEC_PROBES_SCHEMA)
    # columns added after the table first shipped; migrate quietly
    for ddl in ("ALTER TABLE exec_probes ADD COLUMN fair_consensus REAL",
                "ALTER TABLE exec_probes ADD COLUMN settle_price REAL",
                "ALTER TABLE exec_probes ADD COLUMN settled_at TEXT"):
        try:
            conn.execute(ddl)
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()


def open_probe(row):
    """One probe per open signal per token; skips if one is already open."""
    conn = get_connection()
    dup = conn.execute("SELECT 1 FROM exec_probes WHERE token_id=? AND status='open'",
                       (row["token_id"],)).fetchone()
    if dup:
        conn.close()
        return None
    sql = (f"INSERT INTO exec_probes ({', '.join(PROBE_OPEN_COLUMNS)}) "
           f"VALUES ({', '.join('?' for _ in PROBE_OPEN_COLUMNS)})")
    cur = conn.execute(sql, tuple(row.get(c) for c in PROBE_OPEN_COLUMNS))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def fetch_probes(status=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    clause, params = ("WHERE status = ?", [status]) if status else ("", [])
    rows = [dict(r) for r in conn.execute(
        f"SELECT * FROM exec_probes {clause} ORDER BY logged_at", params)]
    conn.close()
    return rows


def update_probe(pid, **fields):
    if not fields:
        return 0
    sets = ", ".join(f"{k}=?" for k in fields)
    conn = get_connection()
    conn.execute(f"UPDATE exec_probes SET {sets} WHERE id=?",
                 (*fields.values(), pid))
    conn.commit()
    n = conn.total_changes
    conn.close()
    return n
