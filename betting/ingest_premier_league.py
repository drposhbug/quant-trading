"""
Ingests Premier League history (football-data.co.uk) into the local SQLite
DB (db.py), including bookmaker odds where available — needed for the ROI
backtest in train_xgboost_model.py, since accuracy/log-loss alone don't
tell you whether a model would have actually made money.

Bookmaker odds coverage: B365 (Bet365) columns exist from the 2000s onward;
the cross-bookmaker Avg columns only start around 2012. Older seasons are
still ingested (for Elo/H2H/form history) with odds left NULL.

Usage:
    py ingest_premier_league.py
"""

import io
from collections import defaultdict, deque

import pandas as pd
import requests

from club_features import compute_features
from db import init_db, upsert_matches

LEAGUE_CODE = "E0"
LEAGUE_NAME = "premier_league"
SEASON_CODES = [f"{y % 100:02d}{(y + 1) % 100:02d}" for y in range(1993, 2026)]
BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"

ODDS_COLUMNS = ["AvgH", "AvgD", "AvgA", "B365H", "B365D", "B365A",
                "MaxH", "MaxD", "MaxA", "BbMxH", "BbMxD", "BbMxA",
                "BbAvH", "BbAvD", "BbAvA"]
# HS/AS = shots, HST/AST = shots on target; present in the CSVs from ~2000-01
# onward. Free extra signal already being downloaded and then thrown away.
SHOT_COLUMNS = ["HS", "AS", "HST", "AST"]
SHOT_FORM_WINDOW = 5


def fetch_season(season):
    url = BASE_URL.format(season=season, league=LEAGUE_CODE)
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return None
    df = pd.read_csv(io.StringIO(r.text), on_bad_lines="skip", engine="python")
    keep = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
    keep += [c for c in ODDS_COLUMNS + SHOT_COLUMNS if c in df.columns]
    df = df[keep].dropna(subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"])
    df["season"] = season
    return df


def add_rolling_shot_features(matches):
    """
    Adds shots_for_diff / sot_for_diff / sot_against_diff to each match dict
    in place: rolling averages over each team's last SHOT_FORM_WINDOW matches,
    computed strictly BEFORE the match (histories append after the features
    are read — same no-leakage pattern as compute_features and the xG ingest).
    Matches without shot data (pre-2000 seasons) get None and contribute
    nothing to the rolling windows.
    """
    shots_hist = defaultdict(lambda: deque(maxlen=SHOT_FORM_WINDOW))
    sot_hist = defaultdict(lambda: deque(maxlen=SHOT_FORM_WINDOW))
    sot_against_hist = defaultdict(lambda: deque(maxlen=SHOT_FORM_WINDOW))

    def avg(hist, team):
        vals = hist[team]
        return (sum(vals) / len(vals)) if vals else None

    for m in matches:
        home, away = m["home"], m["away"]

        h_shots, a_shots = avg(shots_hist, home), avg(shots_hist, away)
        h_sot, a_sot = avg(sot_hist, home), avg(sot_hist, away)
        h_sot_ag, a_sot_ag = avg(sot_against_hist, home), avg(sot_against_hist, away)

        m["shots_for_diff"] = (h_shots - a_shots) if (h_shots is not None and a_shots is not None) else None
        m["sot_for_diff"] = (h_sot - a_sot) if (h_sot is not None and a_sot is not None) else None
        m["sot_against_diff"] = (h_sot_ag - a_sot_ag) if (h_sot_ag is not None and a_sot_ag is not None) else None

        if m.get("hs") is not None and m.get("as") is not None:
            shots_hist[home].append(m["hs"])
            shots_hist[away].append(m["as"])
        if m.get("hst") is not None and m.get("ast") is not None:
            sot_hist[home].append(m["hst"])
            sot_hist[away].append(m["ast"])
            sot_against_hist[home].append(m["ast"])  # what home conceded = away's SOT
            sot_against_hist[away].append(m["hst"])


def fetch_all_seasons():
    frames = [df for s in SEASON_CODES if (df := fetch_season(s)) is not None and len(df)]
    all_matches = pd.concat(frames, ignore_index=True)
    all_matches["Date"] = pd.to_datetime(all_matches["Date"], dayfirst=True, format="mixed")
    all_matches = all_matches.sort_values("Date").reset_index(drop=True)
    print(f"Fetched {len(all_matches)} Premier League matches "
          f"({all_matches['Date'].min().date()} to {all_matches['Date'].max().date()}).")
    return all_matches


def first_valid(*vals):
    """
    First value that is a real number. Plain `a or b` is wrong here because
    pandas fills missing cells with NaN, and NaN is TRUTHY in Python — so
    `NaN or b365` returned NaN and the Bet365 fallback never fired, storing
    NULL odds for rows where B365 odds actually existed.
    """
    for v in vals:
        if v is not None and pd.notna(v):
            return float(v)
    return None


if __name__ == "__main__":
    init_db()

    df = fetch_all_seasons()
    matches = []
    for m in df.to_dict("records"):
        row = {"date": m["Date"], "season": m["season"], "home": m["HomeTeam"], "away": m["AwayTeam"],
               "home_score": m["FTHG"], "away_score": m["FTAG"]}
        # prefer cross-bookmaker average odds (Avg new-era, BbAv pre-2019);
        # fall back to Bet365 alone
        row["odds_home"] = first_valid(m.get("AvgH"), m.get("BbAvH"), m.get("B365H"))
        row["odds_draw"] = first_valid(m.get("AvgD"), m.get("BbAvD"), m.get("B365D"))
        row["odds_away"] = first_valid(m.get("AvgA"), m.get("BbAvA"), m.get("B365A"))
        # best price across all tracked books (Max new-era, BbMx pre-2019) —
        # the payout a line-shopping bettor actually gets
        row["odds_max_home"] = first_valid(m.get("MaxH"), m.get("BbMxH"))
        row["odds_max_draw"] = first_valid(m.get("MaxD"), m.get("BbMxD"))
        row["odds_max_away"] = first_valid(m.get("MaxA"), m.get("BbMxA"))
        row["hs"] = first_valid(m.get("HS"))
        row["as"] = first_valid(m.get("AS"))
        row["hst"] = first_valid(m.get("HST"))
        row["ast"] = first_valid(m.get("AST"))
        matches.append(row)

    add_rolling_shot_features(matches)
    rows, final_state = compute_features(matches)

    db_rows = [{
        "league": LEAGUE_NAME,
        "date": str(r["date"]),
        "season": r["season"],
        "home_team": r["home"],
        "away_team": r["away"],
        "home_score": r["home_score"],
        "away_score": r["away_score"],
        "result": r["result"],
        "knockout": 0,
        "elo_diff": r["elo_diff"],
        "h2h_home_win_rate": r["h2h_home_win_rate"],
        "h2h_meetings": r["h2h_meetings"],
        "recent_form_diff": r["recent_form_diff"],
        "elo_form_interaction": r["elo_form_interaction"],
        "elo_h2h_interaction": r["elo_h2h_interaction"],
        "shots_for_diff": r.get("shots_for_diff"),
        "sot_for_diff": r.get("sot_for_diff"),
        "sot_against_diff": r.get("sot_against_diff"),
        "odds_home": r.get("odds_home"),
        "odds_draw": r.get("odds_draw"),
        "odds_away": r.get("odds_away"),
        "odds_max_home": r.get("odds_max_home"),
        "odds_max_draw": r.get("odds_max_draw"),
        "odds_max_away": r.get("odds_max_away"),
    } for r in rows]

    upsert_matches(db_rows)

    from db import get_connection
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM matches WHERE league = ?", (LEAGUE_NAME,)).fetchone()[0]
    with_odds = conn.execute(
        "SELECT COUNT(*) FROM matches WHERE league = ? AND odds_home IS NOT NULL", (LEAGUE_NAME,)
    ).fetchone()[0]
    conn.close()
    print(f"Stored {total} matches in the database "
          f"({with_odds} with bookmaker odds, {total - with_odds} without — "
          f"older seasons predate football-data.co.uk's odds columns).")
