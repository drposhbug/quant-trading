"""
Historical NBA closing moneylines — the odds side of the betting backtest.

nba_api carries no betting prices, so ROI can't be measured from it alone. This
pulls per-game closing moneylines from a public, stable mirror (the kyleskom/
NBA-Machine-Learning-Sports-Betting repo's OddsData.sqlite, itself sourced from
sportsbookreviewsonline), which covers 2007-08 through the current season with
full team names that line up with nba_api's. The file is cached locally
(nba_closing_odds.sqlite) so the backtest is reproducible offline.

Public odds archives are messy — team names drift (LA vs Los Angeles Clippers)
and late tip-offs occasionally land on the previous calendar date versus
nba_api — so load_closing_ml() normalizes names and the caller joins on date
with a +/-1 day fallback (same tolerance ingest_understat_xg.py uses).

Usage (as a library):
    from nba_odds import load_closing_ml, american_to_decimal
"""

import os
import re
import sqlite3

import requests

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nba_closing_odds.sqlite")
ODDS_URL = ("https://raw.githubusercontent.com/kyleskom/"
            "NBA-Machine-Learning-Sports-Betting/master/Data/OddsData.sqlite")

# nba_api name -> odds-archive name, for the handful that differ. Everything
# else (including era-correct historical names like 'New Jersey Nets') already
# matches on both sides.
NAME_ALIASES = {
    "la clippers": "los angeles clippers",
}


def download_odds(force=False):
    """Fetch the odds SQLite to CACHE_PATH (skips if present unless force)."""
    if os.path.exists(CACHE_PATH) and not force:
        return CACHE_PATH
    r = requests.get(ODDS_URL, timeout=120)
    r.raise_for_status()
    with open(CACHE_PATH, "wb") as f:
        f.write(r.content)
    return CACHE_PATH


def american_to_decimal(ml):
    """American moneyline -> decimal odds. +150 -> 2.50, -200 -> 1.50."""
    ml = float(ml)
    return 1.0 + (ml / 100.0 if ml > 0 else 100.0 / abs(ml))


def devig_power(d_home, d_away, tol=1e-10, max_iter=60):
    """
    Strip the vig from a 2-way price and return the fair home-win probability.

    The obvious method — divide each raw implied probability by the overround —
    is the wrong one. It removes the same FRACTION from both sides, but books
    don't load vig evenly: the longshot carries more of it. Proportional
    de-vigging therefore leaves a residual favorite-longshot bias that shows up
    as fake edge on underdogs.

    The power method solves for the exponent k with (1/d_home)^k + (1/d_away)^k
    = 1, which takes proportionally more off the longshot and matches observed
    outcomes more closely. k > 1 always (both implied probs are < 1 and must be
    shrunk to sum to 1), so the bisection bracket starts at 0.5 for safety.
    """
    ih, ia = 1.0 / float(d_home), 1.0 / float(d_away)
    lo, hi = 0.5, 3.0
    for _ in range(max_iter):
        k = 0.5 * (lo + hi)
        s = ih ** k + ia ** k
        if s > 1.0:
            lo = k
        else:
            hi = k
        if abs(s - 1.0) < tol:
            break
    return ih ** (0.5 * (lo + hi))


def norm_team(name):
    n = re.sub(r"[^a-z0-9 ]", "", str(name).lower()).strip()
    n = re.sub(r"\s+", " ", n)
    return NAME_ALIASES.get(n, n)


def _season_table(conn, season):
    """
    Pick the best available odds table for a season. The repo keeps several
    variants; the cleaned '_new' table wins, then the plain 'odds_' table,
    then a bare season table (used for the most recent seasons).
    """
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for cand in (f"odds_{season}_new", f"odds_{season}", season):
        if cand in names:
            return cand
    return None


def load_closing_ml(seasons, cache_path=CACHE_PATH):
    """
    seasons: iterable of season labels ('2015-16', ...).
    Returns {(date_str, norm_home, norm_away): (ml_home, ml_away)} where
    date_str is 'YYYY-MM-DD'. Rows with missing/zero moneylines are skipped.
    """
    download_odds()
    conn = sqlite3.connect(cache_path)
    out = {}
    for season in seasons:
        table = _season_table(conn, season)
        if table is None:
            continue
        for date, home, away, ml_home, ml_away in conn.execute(
                f'SELECT Date, Home, Away, ML_Home, ML_Away FROM "{table}"'):
            if ml_home in (None, 0, "") or ml_away in (None, 0, ""):
                continue
            try:
                mlh, mla = float(ml_home), float(ml_away)
            except (TypeError, ValueError):
                continue
            if mlh == 0 or mla == 0:
                continue
            out[(str(date)[:10], norm_team(home), norm_team(away))] = (mlh, mla)
    conn.close()
    return out


if __name__ == "__main__":
    seasons = [f"{y}-{(y + 1) % 100:02d}" for y in range(2008, 2026)]
    ml = load_closing_ml(seasons)
    print(f"Loaded {len(ml)} games with closing moneylines "
          f"({seasons[0]} .. {seasons[-1]}).")
    sample = next(iter(ml.items()))
    print("sample:", sample, "-> decimal",
          tuple(round(american_to_decimal(x), 3) for x in sample[1]))
