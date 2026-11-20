"""
Ingests ATP + WTA match results WITH bookmaker odds into the local DB.

Source: tennis-data.co.uk, the tennis analogue of football-data.co.uk (which
ingest_premier_league.py already uses) — same idea, same shape: one row per
match, results plus a block of closing prices. It is the only free source that
carries odds; Jeff Sackmann's archives have far deeper history and richer
serve stats but no prices at all, and without prices none of this repo's
questions can be asked.

DATA-SOURCE FRAGILITY, read before trusting a re-run: tennis-data.co.uk was
returning 503 site-wide when this was written, so the loader reads a GitHub
mirror of its CSVs instead. That mirror covers 2021 to early 2024 only. If the
upstream site comes back, point BASE_URL at it for the full 2000-onward
history; the column layout is identical. Rows are cached into SQLite on first
run so the analysis stays reproducible even when both sources are down.

TWO THINGS THIS MODULE IS CAREFUL ABOUT:

  1. LEAKAGE. Source rows are winner/loser oriented — every column is named
     for the outcome (PSW is "Pinnacle Winner"). Storing them that way would
     hand any model the label. Players are therefore re-assigned to p1/p2
     ALPHABETICALLY, a rule that cannot know the result, and every paired
     column is un-permuted to follow player identity. Using the result to
     work out which pre-match price belonged to which player is legitimate;
     using it to choose the ordering would not be.

  2. MIXED DATE FORMATS. The men's files use d/m/Y and the women's ISO. Pandas
     locks onto one format per Series, so parsing after a concat silently
     coerces half the rows to NaT — it drops ~50% of the data without raising.
     Dates are parsed per file, before anything is combined.

Walkovers and cancellations are dropped (no match was played); retirements are
kept, because a retirement is a settled result that books pay out on.

Usage:
    py ingest_tennis.py
    py ingest_tennis.py --years 2022,2023
"""

import argparse
import io

import pandas as pd
import requests

from db import init_db, upsert_tennis_matches

BASE_URL = ("https://raw.githubusercontent.com/sitrucp/"
            "tennis_data_co_uk_echartsjs_viz/main/tennis_data_co_uk/")
YEARS = (2021, 2022, 2023, 2024)
TOURS = {"m": "ATP", "f": "WTA"}
PLAYED = ("Completed", "Retired")
TIMEOUT = 60


def _num(v):
    """CSV cell -> float or None; the odds columns carry blanks and junk."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(f) else f


def _odds(v):
    """
    Decimal odds, or None if the source value is impossible.

    A decimal price of 1.0 or below says a winning bet returns less than the
    stake, which cannot happen -- it is a typo in the archive (the 2022 French
    Open row lists Tsitsipas at 0.972 where the other books say ~1.03). Storing
    it would let an implied probability above 100% reach the de-vig, so it is
    dropped to NULL here rather than filtered by every consumer downstream.
    """
    f = _num(v)
    return None if f is None or f <= 1.0 else f


def fetch_year(year, tour_code):
    """One source file as a DataFrame, with dates already parsed."""
    url = f"{BASE_URL}{year}{tour_code}.csv"
    r = requests.get(url, timeout=TIMEOUT)
    if r.status_code != 200:
        print(f"  ! {year}{tour_code}: HTTP {r.status_code}, skipped")
        return None
    df = pd.read_csv(io.StringIO(r.text))
    # parse HERE, per file — see the module docstring
    df["dt"] = pd.to_datetime(df["Date"], errors="coerce",
                              format="mixed", dayfirst=True)
    # 'Best of' has a space, so itertuples exposes it as the POSITIONAL name
    # _9 -- which silently becomes a different column if the source ever
    # reorders. Rename it to a real identifier so the access is by name.
    if "Best of" in df.columns:
        df = df.rename(columns={"Best of": "best_of_col"})
    df["tour"] = TOURS[tour_code]
    df["year"] = year
    return df


def to_rows(df):
    """Source rows -> storage rows, alphabetically ordered and un-permuted."""
    out = []
    for r in df.itertuples():
        winner, loser = str(r.Winner).strip(), str(r.Loser).strip()
        if winner in ("", "nan") or loser in ("", "nan") or winner == loser:
            continue
        p1, p2 = sorted([winner, loser])
        p1_won = int(p1 == winner)

        def by_player(win_val, lose_val):
            """(winner's value, loser's value) -> (p1's value, p2's value)."""
            return (win_val, lose_val) if p1_won else (lose_val, win_val)

        p1_ps, p2_ps = by_player(_odds(r.PSW), _odds(r.PSL))
        p1_max, p2_max = by_player(_odds(r.MaxW), _odds(r.MaxL))
        p1_avg, p2_avg = by_player(_odds(r.AvgW), _odds(r.AvgL))
        p1_rank, p2_rank = by_player(_num(r.WRank), _num(r.LRank))
        p1_pts, p2_pts = by_player(_num(r.WPts), _num(r.LPts))

        out.append({
            "tour": r.tour, "date": r.dt.strftime("%Y-%m-%d"), "year": int(r.year),
            "tournament": getattr(r, "Tournament", None),
            "surface": getattr(r, "Surface", None),
            "round": getattr(r, "Round", None),
            "best_of": _num(getattr(r, "best_of_col", None)),
            "comment": r.Comment,
            "p1": p1, "p2": p2, "p1_won": p1_won,
            "p1_rank": p1_rank, "p2_rank": p2_rank,
            "p1_pts": p1_pts, "p2_pts": p2_pts,
            "p1_ps": p1_ps, "p2_ps": p2_ps,
            "p1_max": p1_max, "p2_max": p2_max,
            "p1_avg": p1_avg, "p2_avg": p2_avg,
        })
    return out


def fetch_all(years=YEARS):
    rows, dropped = [], 0
    for year in years:
        for code, tour in TOURS.items():
            df = fetch_year(year, code)
            if df is None or df.empty:
                continue
            before = len(df)
            df = df[df["dt"].notna() & df["Comment"].isin(PLAYED)]
            dropped += before - len(df)
            got = to_rows(df)
            rows.extend(got)
            print(f"  {year} {tour}: {len(got)} matches")
    print(f"Fetched {len(rows)} matches "
          f"({dropped} dropped: walkovers, cancellations, unparseable dates).")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ingest ATP/WTA results with closing odds.")
    ap.add_argument("--years", default=",".join(str(y) for y in YEARS),
                    help="comma-separated years to ingest")
    args = ap.parse_args()
    years = [int(y) for y in args.years.split(",")]

    init_db()
    rows = fetch_all(years)
    if not rows:
        raise SystemExit("Nothing ingested — the mirror may be unreachable.")
    upsert_tennis_matches(rows)

    from db import get_connection
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM tennis_matches").fetchone()[0]
    with_odds = conn.execute(
        "SELECT COUNT(*) FROM tennis_matches WHERE p1_ps IS NOT NULL").fetchone()[0]
    p1_rate = conn.execute("SELECT AVG(p1_won) FROM tennis_matches").fetchone()[0]
    conn.close()
    print(f"\nStored {total} matches; {with_odds} ({with_odds / total:.1%}) have a "
          f"Pinnacle price.")
    print(f"p1 (alphabetically first) won {p1_rate:.3f} -- must sit near 0.500, "
          f"or the ordering\nis picking up the result and every downstream number is void.")
