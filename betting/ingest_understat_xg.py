"""
Ingests Understat's expected-goals (xG) data for the Premier League and
attaches rolling xG features to the existing matches in the database
(run ingest_premier_league.py first).

Understat only covers 2014-15 onward, so older matches keep xg_* = NULL.

Features (all rolling averages over each team's last 5 matches, any
opponent/venue, computed strictly as-of before the match — no leakage):
  - xg_for_diff: home team's xG created minus away team's xG created.
    The core "who's actually creating better chances" signal, which is
    slower for bookmakers to fully price in than raw results.
  - xg_against_diff: home team's xG conceded minus away team's xG conceded
    (defensive equivalent).
  - xg_overperformance_diff: (goals scored - xG) rolling average, home
    minus away — captures finishing-quality "luck" that tends to regress
    toward the mean, a classic source of market mispricing.

Team names differ between Understat ("Manchester United") and
football-data.co.uk ("Man United") — reconciled via NAME_ALIASES below.

Usage:
    py ingest_understat_xg.py
"""

from collections import defaultdict, deque

from understatapi import UnderstatClient

from db import update_xg_features

SEASONS = [str(y) for y in range(2014, 2026)]
FORM_WINDOW = 5

NAME_ALIASES = {
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Newcastle United": "Newcastle",
    "Nottingham Forest": "Nott'm Forest",
    "Queens Park Rangers": "QPR",
    "West Bromwich Albion": "West Brom",
    "Wolverhampton Wanderers": "Wolves",
}


def alias(team):
    return NAME_ALIASES.get(team, team)


def fetch_all_matches():
    matches = []
    with UnderstatClient() as understat:
        for season in SEASONS:
            data = understat.league(league="EPL").get_match_data(season=season)
            for d in data:
                if not d.get("isResult"):
                    continue
                matches.append({
                    "date": d["datetime"][:10],
                    "home": alias(d["h"]["title"]),
                    "away": alias(d["a"]["title"]),
                    "home_xg": float(d["xG"]["h"]),
                    "away_xg": float(d["xG"]["a"]),
                    "home_goals": int(d["goals"]["h"]),
                    "away_goals": int(d["goals"]["a"]),
                })
    matches.sort(key=lambda m: m["date"])
    print(f"Fetched {len(matches)} matches with xG data from Understat "
          f"({matches[0]['date']} to {matches[-1]['date']}).")
    return matches


def compute_rolling_xg_features(matches):
    xg_for_hist = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
    xg_against_hist = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
    overperf_hist = defaultdict(lambda: deque(maxlen=FORM_WINDOW))

    rows = []
    for m in matches:
        home, away = m["home"], m["away"]

        def avg(d, key, default=0.0):
            vals = d[key]
            return (sum(vals) / len(vals)) if vals else default

        home_xg_for = avg(xg_for_hist, home)
        away_xg_for = avg(xg_for_hist, away)
        home_xg_against = avg(xg_against_hist, home)
        away_xg_against = avg(xg_against_hist, away)
        home_overperf = avg(overperf_hist, home)
        away_overperf = avg(overperf_hist, away)

        rows.append({
            "date": m["date"], "home_team": home, "away_team": away,
            "xg_for_diff": home_xg_for - away_xg_for,
            "xg_against_diff": home_xg_against - away_xg_against,
            "xg_overperformance_diff": home_overperf - away_overperf,
        })

        xg_for_hist[home].append(m["home_xg"])
        xg_for_hist[away].append(m["away_xg"])
        xg_against_hist[home].append(m["away_xg"])  # what home conceded = away's xG
        xg_against_hist[away].append(m["home_xg"])
        overperf_hist[home].append(m["home_goals"] - m["home_xg"])
        overperf_hist[away].append(m["away_goals"] - m["away_xg"])

    return rows


if __name__ == "__main__":
    matches = fetch_all_matches()
    rows = compute_rolling_xg_features(matches)
    n_updated = update_xg_features(rows)
    print(f"Updated {n_updated} matches in the database with rolling xG features "
          f"({len(rows) - n_updated} Understat matches had no matching row in the "
          f"database — likely a team-name alias gap, check NAME_ALIASES).")
