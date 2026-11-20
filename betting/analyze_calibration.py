"""
Calibration Analysis — Polymarket price vs. an independent fair-value estimate
================================================================================
Routes fair-value estimation by market type:
  - "Win Group X" markets  -> ESPN live group standings (points + goal diff)
  - "Win the World Cup" (outright) markets -> LIVE FIFA ranking strength,
    converted to win probability via a softmax-style transform.

FIFA's rankings page renders its table via JavaScript, so a plain requests.get()
only ever sees an empty table skeleton. This version uses Playwright (a real
headless browser) to load the page, let the JS populate the table, then
extract the rendered HTML for parsing. Falls back to the GitHub CSV if
Playwright isn't installed or the scrape fails for any reason.
"""

import io
import math
import unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup

SPORT_FILTER = "World Cup"
SNAPSHOTS_FILE = "price_snapshots.csv"

FIFA_SOFTMAX_TEMP = 45.0
LONGSHOT_FAIR_VALUE_FLOOR = 0.01

# ---------------------------------------------------------------
# Name normalization + manual alias map
# ---------------------------------------------------------------
TEAM_ALIASES = {
    "korea republic": ["south korea"],
    "usa": ["united states", "us"],
    "ivory coast": ["cote d'ivoire", "côte d'ivoire"],
    "iran": ["ir iran"],
    "czechia": ["czech republic"],
    "north macedonia": ["macedonia"],
    "cabo verde": ["cape verde"],
    "curacao": ["curaçao"],
    "dr congo": ["congo dr", "democratic republic of congo"],
    "turkiye": ["turkey"],
}

def normalize(name: str) -> str:
    if not isinstance(name, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_only = ascii_only.lower().strip()
    for ch in ["'", ".", ","]:
        ascii_only = ascii_only.replace(ch, "")
    return " ".join(ascii_only.split())

def build_alias_lookup(table: dict) -> dict:
    lookup = {}
    for canonical in table:
        norm_canon = normalize(canonical)
        lookup[norm_canon] = canonical
        for alias in TEAM_ALIASES.get(norm_canon, []):
            lookup[normalize(alias)] = canonical
    return lookup

def match_team(question: str, table: dict, alias_lookup: dict):
    norm_q = normalize(question)
    matches = [(variant, canonical) for variant, canonical in alias_lookup.items()
               if variant and variant in norm_q]
    if not matches:
        return None, None
    variant, canonical = max(matches, key=lambda m: len(m[0]))
    return canonical, table[canonical]

# ---------------------------------------------------------------
# 1. Load your collected snapshots
# ---------------------------------------------------------------
def load_snapshots(filename=SNAPSHOTS_FILE):
    df = pd.read_csv(filename)
    df["pulled_at"] = pd.to_datetime(df["pulled_at"], unit="s", utc=True)
    return df

def filter_sport(df, keyword=SPORT_FILTER):
    return df[df["question"].str.contains(keyword, case=False, na=False)]

# ---------------------------------------------------------------
# 2. FIFA rankings (outright winner fair value)
# ---------------------------------------------------------------
FIFA_RANKING_CSV_URL = (
    "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/"
    "master/ranking_fifa_historical.csv"
)
FIFA_LIVE_URL = "https://inside.fifa.com/fifa-world-ranking/men"

def fetch_fifa_rankings_live_playwright(timeout_ms=30000):
    """
    Uses a real headless browser (Playwright/Chromium) to load the FIFA
    rankings page, wait for the JS-rendered table to populate, then parse
    the resulting HTML. Returns {team_name: points} or None.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed — run: py -m pip install playwright "
              "&& py -m playwright install chromium")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(FIFA_LIVE_URL, timeout=timeout_ms)
            # Wait for at least one populated row (a <td> inside the table body).
            try:
                page.wait_for_selector("table tbody tr td", timeout=timeout_ms)
            except Exception:
                print("Timed out waiting for FIFA table rows to render.")
                browser.close()
                return None
            html = page.content()
            browser.close()
    except Exception as e:
        print(f"Playwright scrape failed: {e}")
        return None

    try:
        tables = pd.read_html(io.StringIO(html))
    except Exception as e:
        print(f"read_html on rendered page failed: {e}")
        return None

    for t in tables:
        team_col = next((c for c in t.columns if "team" in str(c).lower()
                          or "country" in str(c).lower()), None)
        points_col = next((c for c in t.columns if "point" in str(c).lower()), None)
        if team_col is not None and points_col is not None and len(t) > 0:
            rankings = {}
            for _, row in t.iterrows():
                try:
                    team = str(row[team_col]).strip()
                    pts = float(str(row[points_col]).replace(",", ""))
                    rankings[team] = pts
                except (ValueError, TypeError):
                    continue
            if rankings:
                print(f"Scraped LIVE FIFA rankings via Playwright for {len(rankings)} teams.")
                return rankings
    print("Playwright rendered the page but no usable table was found.")
    return None

def fetch_fifa_rankings(timeout=15):
    """Fallback: GitHub CSV (can be stale — check the printed date)."""
    try:
        r = requests.get(FIFA_RANKING_CSV_URL, timeout=timeout)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        latest_date = df["date"].max()
        latest = df[df["date"] == latest_date]
        print(f"[FALLBACK] Loaded FIFA rankings CSV as of {latest_date} ({len(latest)} teams). "
              f"NOTE: may be stale — live scrape is preferred.")
        return dict(zip(latest["team"], latest["total_points"]))
    except Exception as e:
        print(f"FIFA ranking CSV fetch failed: {e}")
        return None

# Kept for backwards compatibility with monte_carlo_predictor.py's import.
def fetch_fifa_rankings_live():
    return fetch_fifa_rankings_live_playwright()

def fifa_points_to_win_probs(points_by_country: dict, temp=FIFA_SOFTMAX_TEMP) -> dict:
    clean = {c: p for c, p in points_by_country.items() if pd.notna(p)}
    if not clean:
        return {}
    max_pts = max(clean.values())
    exps = {c: math.exp((p - max_pts) / temp) for c, p in clean.items()}
    total = sum(exps.values())
    return {c: v / total for c, v in exps.items()}

def build_outright_fair_value_table(use_live_fifa_scraper=True):
    points = None
    source = None
    if use_live_fifa_scraper:
        points = fetch_fifa_rankings_live_playwright()
        source = "Playwright live scrape"
    if not points:
        points = fetch_fifa_rankings()
        source = "GitHub CSV fallback"
    if not points:
        print("WARNING: No FIFA ranking source available — outright markets will be skipped entirely.")
        return {}, {}
    probs = fifa_points_to_win_probs(points)
    print(f"Outright fair values built from {source} ({len(points)} teams).")
    return probs, points

# ---------------------------------------------------------------
# 3. ESPN live group standings (group-winner fair value)
# ---------------------------------------------------------------
ESPN_STANDINGS_URL = "https://site.api.espn.com/apis/v2/sports/soccer/fifa.world/standings"

def fetch_espn_world_cup_standings():
    try:
        r = requests.get(ESPN_STANDINGS_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        groups = data.get("children", [])
        if not groups:
            print("WARNING: ESPN response had no group data.")
            return None
        scores = {}
        for group in groups:
            entries = group.get("standings", {}).get("entries", [])
            for entry in entries:
                team_name = entry.get("team", {}).get("displayName")
                if not team_name:
                    continue
                stats = {s["name"]: s.get("value", 0) for s in entry.get("stats", [])}
                points = stats.get("points", 0)
                goal_diff = stats.get("pointDifferential", stats.get("goalDifferential", 0))
                scores[team_name] = max(points * 3 + goal_diff, 0.1)
        if not scores:
            print("WARNING: parsed zero teams from ESPN standings response.")
        return scores or None
    except Exception as e:
        print(f"ESPN standings fetch failed ({e}).")
        return None

def espn_scores_to_group_win_probs(scores: dict) -> dict:
    total = sum(scores.values())
    return {team: score / total for team, score in scores.items()}

# ---------------------------------------------------------------
# 4. Route by market type + build comparison
# ---------------------------------------------------------------
def is_group_winner_question(question: str) -> bool:
    return "win group" in question.lower()

def is_outright_winner_question(question: str) -> bool:
    q = question.lower()
    return "win the 2026 fifa world cup" in q or "win the world cup" in q

def build_comparison(df, outright_table, group_table, raw_fifa_points):
    latest = df.sort_values("pulled_at").groupby("question").tail(1).copy()

    outright_alias_lookup = build_alias_lookup(outright_table)
    group_alias_lookup = build_alias_lookup(group_table)

    matched_teams, fair_values, raw_points_used, sources = [], [], [], []
    outright_total, outright_matched = 0, 0
    group_total, group_matched = 0, 0

    for question in latest["question"]:
        if is_outright_winner_question(question):
            outright_total += 1
            team, fv = match_team(question, outright_table, outright_alias_lookup)
            if fv is not None:
                outright_matched += 1
            raw_pts = raw_fifa_points.get(team) if team else None
            matched_teams.append(team)
            fair_values.append(fv)
            raw_points_used.append(raw_pts)
            sources.append("FIFA/softmax" if fv is not None else None)
        elif is_group_winner_question(question):
            group_total += 1
            team, fv = match_team(question, group_table, group_alias_lookup)
            if fv is not None:
                group_matched += 1
            matched_teams.append(team)
            fair_values.append(fv)
            raw_points_used.append(None)
            sources.append("ESPN group" if fv is not None else None)
        else:
            matched_teams.append(None)
            fair_values.append(None)
            raw_points_used.append(None)
            sources.append(None)

    print(f"\nOutright markets: {outright_matched}/{outright_total} matched to a FIFA team.")
    print(f"Group-winner markets: {group_matched}/{group_total} matched to an ESPN team.")
    if outright_total > outright_matched or group_total > group_matched:
        print("Some markets did not match — check TEAM_ALIASES if you recognize the missing team names.")

    latest["matched_team"] = matched_teams
    latest["fair_value"] = fair_values
    latest["fifa_raw_points"] = raw_points_used
    latest["fair_value_source"] = sources

    unmatched = latest[latest["fair_value"].isna() &
                        (latest["question"].apply(lambda q: is_outright_winner_question(q) or is_group_winner_question(q)))]
    if len(unmatched):
        print("\nUnmatched market questions (consider adding aliases):")
        for q in unmatched["question"]:
            print(f"  - {q}")

    latest = latest.dropna(subset=["fair_value"])
    latest["divergence"] = latest["price"] - latest["fair_value"]
    latest["divergence_pct"] = (latest["divergence"] / latest["fair_value"]) * 100
    latest["longshot_unreliable_pct"] = latest["fair_value"] < LONGSHOT_FAIR_VALUE_FLOOR

    cols = ["question", "matched_team", "fair_value_source", "fifa_raw_points",
            "price", "fair_value", "divergence", "divergence_pct",
            "longshot_unreliable_pct", "pulled_at"]
    return latest[cols].sort_values("divergence", key=abs, ascending=False)

def price_trend(df, question_substring):
    subset = df[df["question"].str.contains(question_substring, case=False, na=False)]
    return subset[["pulled_at", "price"]].sort_values("pulled_at")

def print_fair_value_extremes(outright_probs: dict, n=5):
    if not outright_probs:
        return
    ranked = sorted(outright_probs.items(), key=lambda kv: kv[1], reverse=True)
    print(f"\nTop {n} outright fair values (sanity check):")
    for team, prob in ranked[:n]:
        print(f"  {team:20s} {prob:.4f}")
    print(f"Bottom {n} outright fair values:")
    for team, prob in ranked[-n:]:
        print(f"  {team:20s} {prob:.6f}")

# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
if __name__ == "__main__":
    df = load_snapshots()
    sport_df = filter_sport(df)
    print(f"Total snapshots for '{SPORT_FILTER}': {len(sport_df)}")
    print(f"Unique markets: {sport_df['question'].nunique()}")

    outright_table, raw_fifa_points = build_outright_fair_value_table(use_live_fifa_scraper=True)
    print_fair_value_extremes(outright_table)

    espn_scores = fetch_espn_world_cup_standings()
    group_table = espn_scores_to_group_win_probs(espn_scores) if espn_scores else {}
    if espn_scores:
        print(f"\nUsing LIVE ESPN group standings ({len(espn_scores)} teams) for group-winner markets.")

    comparison = build_comparison(sport_df, outright_table, group_table, raw_fifa_points)

    print("\n=== Team-match debug (outright markets) ===")
    debug_cols = ["question", "matched_team", "fifa_raw_points", "fair_value"]
    print(comparison[comparison["fair_value_source"] == "FIFA/softmax"][debug_cols].to_string(index=False))

    print("\n=== Biggest divergences from fair value (sorted by absolute divergence) ===")
    print(comparison.drop(columns=["fifa_raw_points", "fair_value_source"]).to_string(index=False))

    comparison.to_csv("comparison_output.csv", index=False)
    print("\nSaved full comparison table to comparison_output.csv")