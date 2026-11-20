"""
NBA injury report + news — the information the closing line has and a box
score does not
================================================================================
nba_diagnose.py measured exactly why the stats model loses to the closing
line: a steady ~0.020 nats of log loss that no amount of feature engineering
touched (opponent-adjusted ratings, multi-window margin, schedule density and
gradient boosting between them closed 3% of it). The gap is not architecture.
It is information — who is playing. A star ruled out moves an NBA line several
points, and nba_features.py cannot see that at any level of sophistication,
because it only ever sees what already happened on the floor.

This module supplies the missing input, from two free, key-less ESPN feeds:

  * the injury report — per player: status, body part, ESPN's return estimate
    and the reporter's note
  * the league news wire — headlines, for the trades and load-management
    stories that precede a formal injury designation

WHY THIS CANNOT RETROACTIVELY FIX THE BACKTEST. ESPN publishes the CURRENT
report only; there is no historical archive to pull. So this cannot be joined
to the 15,226 games already in the DB, and running it today does not improve
any number nba_diagnose.py prints. What it does is start accumulating the
history that would — one append-only snapshot per run, the same design and for
the same reason as log_prices.py. After a few months of the season there is a
real per-game injury record, and the honest test becomes possible: re-run the
diagnostic with injury features added and see whether the 0.020 gap moves.
Until then this is a live decision aid and a data-collection job, not a
validated model input, and it is deliberately NOT wired into nba_predict.py's
probability — see the note on IMPACT_TO_POINTS below.

HOW A PLAYER'S ABSENCE IS SCORED. A list of names is useless without knowing
who matters: "Out" for a 12th man is worth nothing, "Out" for an MVP is worth
5+ points. Each injured player is valued by

    impact_units = max(0, PIE - REPLACEMENT_PIE) * MPG

PIE (Player Impact Estimate, from nba_api) is the share of a game's measurable
events a player accounts for; a league-average starter sits near 0.10. Netting
off REPLACEMENT_PIE matters because a player's absence costs only what he
provides ABOVE the bench player who takes his minutes, not his gross
production. Multiplying by minutes scales that rate by exposure. Statuses
short of "Out" are weighted by their probability of actually missing
(STATUS_WEIGHT), so a questionable star and a ruled-out role player don't
count the same.

Usage:
    py nba_injuries.py                          # today's report, worst-hit teams first
    py nba_injuries.py --team "Boston Celtics"  # one team, with the reporters' notes
    py nba_injuries.py --news                   # the news wire
    py nba_injuries.py --matchup "Boston Celtics" "New York Knicks"
    py nba_injuries.py --snapshot               # log to the DB (for run_daily.bat)
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from statistics import NormalDist

import requests

from db import fetch_injuries_as_of, init_nba_injuries, log_injury_snapshot, log_nba_news

# NBA rosters are full of names the Windows console's cp1252 codepage cannot
# encode (Jokic, Doncic, Sengun). Without this, printing the report dies with
# UnicodeEncodeError on the first accented name.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
INJURIES_URL = f"{ESPN_BASE}/injuries"
NEWS_URL = f"{ESPN_BASE}/news"
TIMEOUT = 25

VALUES_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "nba_player_values.json")
VALUES_MAX_AGE_DAYS = 3     # PIE/MPG drift slowly; no need to re-pull every run
SEASONS_TO_SCAN = 3         # how far back to look for a player's last real season
MIN_GP_FOR_VALUE = 10       # below this, a season's PIE/MPG is small-sample noise

# P(this player actually misses the game), by ESPN's status wording. These are
# the standard readings of the designations, not fitted values — with no
# historical report archive there is nothing yet to fit them on. 'Day-To-Day'
# is ESPN's catch-all and resolves to playing far more often than not, hence
# the low weight.
STATUS_WEIGHT = {
    "out": 1.00,
    "suspension": 1.00,
    "suspended": 1.00,
    "injured reserve": 1.00,
    "doubtful": 0.75,
    "questionable": 0.50,
    "day-to-day": 0.30,
    "game-time decision": 0.50,
    "probable": 0.10,
    "active": 0.00,
}
DEFAULT_STATUS_WEIGHT = 0.30

# A rotation-level replacement's PIE. League average across all players is ~0.10
# by construction; the bench player who absorbs the minutes is a little below
# that, so a star's absence is charged only the difference.
REPLACEMENT_PIE = 0.075

# UNVALIDATED PRIOR — the one number here not grounded in measured data.
# Anchored on the well-established rule of thumb that a superstar's absence
# moves an NBA line by ~5 points: a 36-mpg player at 0.20 PIE scores
# (0.20 - 0.075) * 36 = 4.5 impact units, so ~1.1 points per unit. Treat it as
# an order-of-magnitude scale, and refit it against real snapshots once a few
# months of history exist. This is exactly why the derived win-probability
# number is reported for a human to read and NOT fed into nba_predict.py:
# an unvalidated constant driving an automated edge calculation is how the
# fake edges that nba_diagnose.py found get manufactured in the first place.
IMPACT_TO_POINTS = 1.1

# SD of an NBA game's final margin around the spread, ~12 points. Converts a
# points swing into a win-probability swing via the normal CDF.
MARGIN_SD = 12.0

# ESPN team naming vs nba_api's. Full display names agree everywhere except
# the Clippers; abbreviations disagree for six teams.
ESPN_TEAM_ALIASES = {"LA Clippers": "Los Angeles Clippers"}
ESPN_ABBR_ALIASES = {"GS": "GSW", "NO": "NOP", "NY": "NYK",
                     "SA": "SAS", "UTAH": "UTA", "WSH": "WAS"}


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def norm_player(name):
    """
    Match ESPN's spelling to nba_api's. Strips accents (the two sources
    disagree on Jokic/Jokic), punctuation, and generational suffixes, which
    they render as 'Jr.' vs 'Jr' vs nothing.
    """
    n = unicodedata.normalize("NFKD", str(name))
    n = "".join(c for c in n if not unicodedata.combining(c)).lower()
    n = re.sub(r"[^a-z ]", " ", n)
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def status_weight(status):
    return STATUS_WEIGHT.get(str(status or "").strip().lower(), DEFAULT_STATUS_WEIGHT)


# --------------------------------------------------------------------------
# player value
# --------------------------------------------------------------------------

def _fetch_player_stats(seasons_back=SEASONS_TO_SCAN):
    """
    Per-player advanced stats for several recent seasons, newest first.

    Scanning MORE THAN ONE season is not belt-and-braces, it is required for
    correctness. A player who missed all of last season has no row in it — and
    the players who missed a full season are, overwhelmingly, stars recovering
    from major injuries. Looking at the newest season alone therefore scores
    exactly the highest-value names on the injury report (Haliburton, Lillard,
    Irving, VanVleet in the 2026 offseason report) at zero, silently, which is
    the worst possible failure mode for this module: it reports a returning
    star's absence as costless.

    Also handles the offseason, when the current season label is simply empty.
    Returns [(season_label, DataFrame), ...] newest first.
    """
    from nba_api.stats.endpoints import leaguedashplayerstats

    today = datetime.now(timezone.utc)
    start_year = today.year if today.month >= 10 else today.year - 1
    frames = []
    for back in range(0, seasons_back + 2):
        if len(frames) >= seasons_back:
            break
        year = start_year - back
        season = f"{year}-{(year + 1) % 100:02d}"
        try:
            df = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season, season_type_all_star="Regular Season",
                measure_type_detailed_defense="Advanced", timeout=60,
            ).get_data_frames()[0]
        except Exception as e:  # noqa: BLE001 — stats.nba.com is flaky; try the prior season
            print(f"  ! player stats for {season} failed ({type(e).__name__}); trying earlier")
            continue
        if not df.empty:
            frames.append((season, df))
    if not frames:
        raise SystemExit("Could not fetch player stats from nba_api for any recent season.")
    return frames


def load_player_values(refresh=False):
    """
    {normalized name: {'pie', 'mpg', 'gp', 'team', 'name'}}, cached to disk.
    MIN from the Advanced endpoint is already per-game, not a season total.
    """
    if not refresh and os.path.exists(VALUES_CACHE):
        try:
            with open(VALUES_CACHE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            age = (datetime.now(timezone.utc)
                   - datetime.fromisoformat(cached["fetched_at"])).days
            if age <= VALUES_MAX_AGE_DAYS:
                return cached["players"], cached["season"]
        except (ValueError, KeyError):
            pass   # corrupt or old-format cache — just re-pull

    frames = _fetch_player_stats()
    newest_season = frames[0][0]
    players = {}
    # newest season first, and never overwrite: the first (most recent) season
    # in which a player logged real minutes wins.
    for season, df in frames:
        for r in df.to_dict("records"):
            key = norm_player(r["PLAYER_NAME"])
            if not key or key in players:
                continue
            if float(r.get("GP") or 0) < MIN_GP_FOR_VALUE:
                continue
            players[key] = {
                "name": r["PLAYER_NAME"],
                "team": r.get("TEAM_ABBREVIATION"),
                "gp": float(r.get("GP") or 0),
                "mpg": float(r.get("MIN") or 0),
                "pie": float(r.get("PIE") or 0),
                "season": season,
            }
    with open(VALUES_CACHE, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": datetime.now(timezone.utc).isoformat(),
                   "season": newest_season, "players": players}, f)
    stale = sum(1 for v in players.values() if v["season"] != newest_season)
    print(f"  cached {len(players)} player values "
          f"({newest_season} for {len(players) - stale}, earlier seasons for {stale})")
    return players, newest_season


def impact_units(pie, mpg):
    """Value lost per game when this player sits, above a replacement's."""
    if not pie or not mpg:
        return 0.0
    return max(0.0, float(pie) - REPLACEMENT_PIE) * float(mpg)


# --------------------------------------------------------------------------
# ESPN feeds
# --------------------------------------------------------------------------

def fetch_injuries(values=None):
    """
    The current league-wide injury report as a flat list of dicts, ready for
    log_injury_snapshot(). Players nba_api has no stats for (two-way call-ups,
    rookies before their debut) still get a row, with pie/mpg NULL and zero
    impact — the report should show them even when they can't be scored.
    """
    if values is None:
        values, _ = load_player_values()
    payload = requests.get(INJURIES_URL, timeout=TIMEOUT).json()
    snapshot_time = _utc_now()

    rows = []
    for team_block in payload.get("injuries", []):
        raw_team = team_block.get("displayName") or ""
        team = ESPN_TEAM_ALIASES.get(raw_team, raw_team)
        for item in team_block.get("injuries", []):
            athlete = item.get("athlete") or {}
            name = athlete.get("displayName")
            if not name:
                continue
            details = item.get("details") or {}
            val = values.get(norm_player(name), {})
            pie, mpg = val.get("pie"), val.get("mpg")
            rows.append({
                "snapshot_time": snapshot_time,
                "team": team,
                "player": name,
                "position": (athlete.get("position") or {}).get("abbreviation"),
                "status": item.get("status"),
                "status_weight": status_weight(item.get("status")),
                "injury_type": details.get("type"),
                "detail": details.get("detail"),
                "side": details.get("side"),
                "return_date": details.get("returnDate"),
                "comment": item.get("shortComment"),
                "report_date": item.get("date"),
                "pie": pie,
                "mpg": mpg,
                "impact_units": impact_units(pie, mpg),
                "value_season": val.get("season"),
            })
    return rows


def fetch_news(limit=25):
    """Recent NBA headlines from ESPN's wire, newest first."""
    payload = requests.get(NEWS_URL, params={"limit": limit}, timeout=TIMEOUT).json()
    fetched_at = _utc_now()
    rows = []
    for a in payload.get("articles", []):
        links = a.get("links") or {}
        url = ((links.get("web") or {}).get("href")
               or ((links.get("api") or {}).get("news") or {}).get("href"))
        rows.append({
            "article_id": str(a.get("id") or a.get("dataSourceIdentifier") or a.get("headline")),
            "published": a.get("published"),
            "headline": a.get("headline"),
            "description": a.get("description"),
            "byline": a.get("byline"),
            "url": url,
            "fetched_at": fetched_at,
        })
    return rows


# --------------------------------------------------------------------------
# aggregation
# --------------------------------------------------------------------------

def team_burden(rows):
    """
    {team: {'expected_units', 'players', 'out'}} — expected_units is the
    impact-weighted sum over the roster, discounted by each status's
    probability of actually missing.
    """
    burden = {}
    for r in rows:
        slot = burden.setdefault(r["team"], {"expected_units": 0.0, "players": [], "out": 0})
        slot["expected_units"] += (r.get("impact_units") or 0.0) * (r.get("status_weight") or 0.0)
        slot["players"].append(r)
        if (r.get("status_weight") or 0) >= 1.0:
            slot["out"] += 1
    for slot in burden.values():
        slot["players"].sort(key=lambda x: -((x.get("impact_units") or 0.0)
                                             * (x.get("status_weight") or 0.0)))
    return burden


def units_to_points(units):
    return units * IMPACT_TO_POINTS


def points_to_win_prob_delta(points):
    """
    A points swing -> a home win-probability swing, via the normal CDF around
    a pick'em. Near 0 this is ~3.3%/point, and it correctly flattens out at
    the extremes rather than running past 100% the way a linear rule does.
    """
    return NormalDist(0.0, MARGIN_SD).cdf(points) - 0.5


def matchup_effect(home_team, away_team, burden):
    """
    Net effect of the two injury reports on the HOME side, as points and as
    win probability. Positive favors the home team (i.e. the away team is the
    more depleted one).
    """
    h = burden.get(home_team, {}).get("expected_units", 0.0)
    a = burden.get(away_team, {}).get("expected_units", 0.0)
    points = units_to_points(a - h)
    return {"home_units": h, "away_units": a, "points": points,
            "win_prob_delta": points_to_win_prob_delta(points)}


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def _fmt_player(r):
    weighted = (r.get("impact_units") or 0.0) * (r.get("status_weight") or 0.0)
    label = r["player"] + (f" ({r['position']})" if r.get("position") else "")
    what = " ".join(x for x in (r.get("side"), r.get("injury_type"), r.get("detail")) if x)
    ret = f", back ~{r['return_date'][:10]}" if r.get("return_date") else ""
    mpg = f"{r['mpg']:.0f}mpg" if r.get("mpg") else "no stats"
    pie = f"{r['pie']:.3f} PIE" if r.get("pie") else "-"
    # a value from an older season means the player missed a full year; say so
    # rather than presenting a two-year-old PIE as current
    src = f" [{r['value_season']}]" if r.get("value_season") else ""
    return (f"    {label:<28} {str(r.get('status') or ''):<13} "
            f"{what or 'unspecified':<24} {mpg:>8} {pie:>10}{src:>10} "
            f"{weighted:>6.2f}u{ret}")


def print_report(rows, top=10):
    burden = team_burden(rows)
    ranked = sorted(burden.items(), key=lambda kv: -kv[1]["expected_units"])
    print(f"\n=== Injury burden by team ({len(rows)} listings, {len(burden)} teams) ===")
    print(f"{'team':<26} {'exp. units':>10} {'~points':>8} {'ruled out':>10} {'listed':>7}")
    for team, slot in ranked[:top]:
        print(f"{team:<26} {slot['expected_units']:>10.2f} "
              f"{units_to_points(slot['expected_units']):>8.1f} "
              f"{slot['out']:>10} {len(slot['players']):>7}")
    print("\n'exp. units' discounts each listing by its chance of actually missing.")
    print(f"'~points' applies IMPACT_TO_POINTS={IMPACT_TO_POINTS}, an unvalidated prior "
          f"-- read it as a\nrough scale, not a number to bet.")


def print_team(rows, team):
    matching = [r for r in rows if r["team"].lower() == team.lower()]
    if not matching:
        print(f"No listings for '{team}'. Teams currently reporting:")
        for t in sorted({r["team"] for r in rows}):
            print(f"  {t}")
        return
    slot = team_burden(matching)[matching[0]["team"]]
    print(f"\n=== {matching[0]['team']} -- {len(matching)} listed, "
          f"{slot['expected_units']:.2f} expected units "
          f"(~{units_to_points(slot['expected_units']):.1f} pts) ===")
    for r in slot["players"]:
        print(_fmt_player(r))
        if r.get("comment"):
            print(f"        {r['comment']}")


def print_news(rows):
    print(f"\n=== NBA news wire ({len(rows)} articles) ===")
    for a in rows:
        when = (a.get("published") or "")[:16].replace("T", " ")
        print(f"\n  [{when}] {a.get('headline')}")
        if a.get("description"):
            print(f"    {a['description']}")
        if a.get("url"):
            print(f"    {a['url']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="NBA injury report and news wire (ESPN), with per-player impact scoring.")
    ap.add_argument("--team", help="show one team's full report with reporters' notes")
    ap.add_argument("--matchup", nargs=2, metavar=("HOME", "AWAY"),
                    help="net injury effect on the home side for one game")
    ap.add_argument("--news", action="store_true", help="show the news wire")
    ap.add_argument("--snapshot", action="store_true",
                    help="append the report + news to the DB (idempotent per run)")
    ap.add_argument("--refresh-values", action="store_true",
                    help="re-pull player PIE/MPG from nba_api, ignoring the cache")
    ap.add_argument("--top", type=int, default=10, help="teams to list in the summary")
    args = ap.parse_args()

    if args.news and not (args.snapshot or args.team or args.matchup):
        print_news(fetch_news())
        raise SystemExit(0)

    values, season = load_player_values(refresh=args.refresh_values)
    rows = fetch_injuries(values)
    if not rows:
        raise SystemExit("ESPN returned no injury listings (normal deep in the offseason).")
    print(f"Fetched {len(rows)} injury listings; player values from {season}.")

    if args.matchup:
        home, away = args.matchup
        eff = matchup_effect(home, away, team_burden(rows))
        print(f"\n=== {away} at {home} ===")
        print(f"  {home:<26} {eff['home_units']:>6.2f} expected units missing")
        print(f"  {away:<26} {eff['away_units']:>6.2f} expected units missing")
        print(f"\n  Net effect on the home side: {eff['points']:+.1f} points, "
              f"{eff['win_prob_delta']:+.1%} win probability.")
        print("  Unvalidated scale (see IMPACT_TO_POINTS) -- a prompt to check the "
              "line yourself,\n  not an edge. Compare it against how far the market "
              "has already moved.")
    elif args.team:
        print_team(rows, args.team)
    else:
        print_report(rows, top=args.top)

    if args.news:
        print_news(fetch_news())

    if args.snapshot:
        init_nba_injuries()
        n_inj = log_injury_snapshot(rows)
        n_news = log_nba_news(fetch_news())
        print(f"\nSnapshot logged: {n_inj} injury rows, {n_news} new articles.")
        print(f"({len({r['team'] for r in rows})} teams at {rows[0]['snapshot_time']}. "
              f"Read history back with db.fetch_injuries_as_of().)")
