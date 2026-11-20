"""
Ingests NBA game history from the official NBA.com stats API (nba_api) into the
local SQLite DB (db.py, nba_games table), with engineered features from
nba_features.py.

nba_api returns one row PER TEAM PER GAME (so every game appears twice); the
MATCHUP string ('IND vs. CLE' = home, 'CLE @ IND' = away) is what disambiguates
home from away. fetch_all_games() merges those two rows back into a single
home/away record with both teams' box scores, which is also exactly the shape
nba_features.compute_features and train_nba_model.py need — so this module is
the single source of raw NBA games for the whole pipeline (the trainer imports
fetch_all_games rather than re-implementing the pull).

Usage:
    py ingest_nba.py                 # all DEFAULT_SEASONS, regular season + playoffs
    py ingest_nba.py --from 2015     # only seasons starting 2015-16 onward
"""

import argparse
import time

from nba_api.stats.endpoints import leaguegamefinder

from db import init_db, upsert_nba_games
from nba_features import compute_features

# NBA seasons are labelled by their starting year: '2023-24'. Elo/net-rating
# need a burn-in, so start well before the window you actually care about.
FIRST_SEASON_YEAR = 2008
LAST_SEASON_YEAR = 2025          # 2025-26 season (completed by mid-2026)
SEASON_TYPES = ["Regular Season", "Playoffs"]
REQUEST_PAUSE = 0.6              # be polite to stats.nba.com between calls
MAX_RETRIES = 3


def season_label(start_year):
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def _fetch_one(season, season_type):
    """One leaguegamefinder call, with retries — stats.nba.com times out a lot."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            gf = leaguegamefinder.LeagueGameFinder(
                season_nullable=season,
                season_type_nullable=season_type,
                league_id_nullable="00",   # 00 = NBA (excludes G-League/WNBA)
                timeout=60,
            )
            return gf.get_data_frames()[0]
        except Exception as e:  # noqa: BLE001 — network flakiness, just retry
            if attempt == MAX_RETRIES:
                print(f"  ! {season} {season_type}: giving up after {attempt} tries ({e})")
                return None
            time.sleep(REQUEST_PAUSE * attempt * 2)
    return None


def _merge_game_rows(df, season, season_type):
    """
    Collapse the two per-team rows of each game into one home/away record.
    Returns a list of game dicts (unsorted).
    """
    by_game = {}
    for r in df.to_dict("records"):
        matchup = r["MATCHUP"]
        is_home = "vs." in matchup   # '@' means the team is away
        box = {
            "pts": r["PTS"], "fga": r["FGA"], "fta": r["FTA"],
            "oreb": r["OREB"], "tov": r["TOV"], "min": r["MIN"] or 240,
        }
        slot = by_game.setdefault(r["GAME_ID"], {})
        slot["date"] = r["GAME_DATE"]
        slot["season"] = season
        slot["season_type"] = season_type
        if is_home:
            slot["home"] = r["TEAM_NAME"]
            slot["home_score"] = r["PTS"]
            slot["home_box"] = box
        else:
            slot["away"] = r["TEAM_NAME"]
            slot["away_score"] = r["PTS"]
            slot["away_box"] = box
        slot["game_id"] = r["GAME_ID"]

    # keep only games where BOTH sides were returned (a rare half-row is useless)
    return [g for g in by_game.values()
            if {"home", "away", "home_box", "away_box"} <= g.keys()]


def fetch_all_games(first_year=FIRST_SEASON_YEAR, last_year=LAST_SEASON_YEAR):
    """
    Pull every game across the season range, merged to one record per game and
    sorted chronologically (date, then game_id). This is the raw input to
    nba_features.compute_features.
    """
    games = []
    for year in range(first_year, last_year + 1):
        season = season_label(year)
        for stype in SEASON_TYPES:
            df = _fetch_one(season, stype)
            time.sleep(REQUEST_PAUSE)
            if df is None or df.empty:
                continue
            merged = _merge_game_rows(df, season, stype)
            games.extend(merged)
            print(f"  {season} {stype:<14} {len(merged)} games")
    games.sort(key=lambda g: (str(g["date"])[:10], g["game_id"]))
    print(f"Fetched {len(games)} NBA games ({season_label(first_year)} .. {season_label(last_year)}).")
    return games


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="from_year", type=int, default=FIRST_SEASON_YEAR,
                    help="first season START year to ingest (e.g. 2015 = 2015-16)")
    args = ap.parse_args()

    init_db()
    games = fetch_all_games(first_year=args.from_year)
    rows, _ = compute_features(games)

    db_rows = [{
        "league": "nba",
        "game_id": r["game_id"],
        "date": str(r["date"])[:10],
        "season": r["season"],
        "season_type": r["season_type"],
        "home_team": r["home"],
        "away_team": r["away"],
        "home_score": r["home_score"],
        "away_score": r["away_score"],
        "result": r["result"],
        "elo_diff": r["elo_diff"],
        "form_diff": r["form_diff"],
        "net_rating_diff": r["net_rating_diff"],
        "pace_diff": r["pace_diff"],
        "rest_diff": r["rest_diff"],
        "b2b_diff": r["b2b_diff"],
        "elo_form_interaction": r["elo_form_interaction"],
    } for r in rows]

    upsert_nba_games(db_rows)

    from db import get_connection
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM nba_games").fetchone()[0]
    home_wins = conn.execute("SELECT COUNT(*) FROM nba_games WHERE result = 'H'").fetchone()[0]
    conn.close()
    print(f"Stored {total} NBA games "
          f"(home win rate {home_wins / total:.3f} across all stored games).")
