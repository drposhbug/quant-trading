"""
Pre-Tournament World Cup Predictor
================================================================================
Unlike stats_only_predictor.py (which uses group-stage results — i.e. data
that only existed AFTER the tournament began), this version uses ONLY FIFA
ranking points from before the 2026 World Cup started. This is a genuine
"what would the model have predicted going in" test, comparable against
what actually happened in the group stage and knockout rounds.

Pulls from the same GitHub FIFA ranking CSV already used in
analyze_calibration.py, filtered to the latest date before June 2026 (the
tournament's start) so no in-tournament information leaks into the ratings.
"""

import io
import random
import pandas as pd
import requests
from collections import defaultdict

from external_factors_agent import load_adjustment

N_SIMULATIONS = 20000
ELO_SCALE = 400.0  # standard Elo scale — appropriate here since FIFA points
                    # span hundreds/thousands, unlike the small group-stage
                    # scores in stats_only_predictor.py. Still unvalidated —
                    # needs backtesting against real historical tournaments.

FIFA_RANKING_CSV_URL = (
    "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/"
    "master/ranking_fifa_historical.csv"
)
CUTOFF_DATE = "2026-06-01"  # World Cup 2026 kicked off in June — use the
                             # latest ranking snapshot strictly before this

# ---------------------------------------------------------------
# 1. Pull pre-tournament FIFA points (no in-tournament data used at all)
# ---------------------------------------------------------------
def fetch_pretournament_fifa_points(cutoff=CUTOFF_DATE, timeout=15):
    r = requests.get(FIFA_RANKING_CSV_URL, timeout=timeout)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df["date"] = pd.to_datetime(df["date"])
    before_cutoff = df[df["date"] < pd.Timestamp(cutoff)]
    if before_cutoff.empty:
        raise RuntimeError(f"No FIFA ranking data found before {cutoff} — "
                            f"check the CSV's date range.")
    latest_date = before_cutoff["date"].max()
    latest = before_cutoff[before_cutoff["date"] == latest_date]
    print(f"Using FIFA rankings from {latest_date.date()} "
          f"(last available snapshot before {cutoff}, {len(latest)} teams).")
    return dict(zip(latest["team"], latest["total_points"]))

# ---------------------------------------------------------------
# 2. Round of 32 bracket — same real matchups as before
# ---------------------------------------------------------------
ROUND_OF_32_MATCHUPS = [
    ("Germany", "Paraguay"),
    ("France", "Sweden"),
    ("South Africa", "Canada"),
    ("Netherlands", "Morocco"),
    ("Portugal", "Croatia"),
    ("Spain", "Austria"),
    ("United States", "Bosnia and Herzegovina"),
    ("Belgium", "Senegal"),
    ("Brazil", "Japan"),
    ("Ivory Coast", "Norway"),
    ("Mexico", "Ecuador"),
    ("England", "DR Congo"),
    ("Argentina", "Cape Verde"),
    ("Australia", "Egypt"),
    ("Switzerland", "Algeria"),
    ("Colombia", "Ghana"),
]

def win_probability(strength_a, strength_b):
    return 1.0 / (1.0 + 10 ** ((strength_b - strength_a) / ELO_SCALE))

def adjusted_win_probability(a, b, strengths):
    """
    Same as win_probability, but layers in any saved external-factors
    adjustment for this specific pairing (head-to-head history, altitude,
    injuries, etc. — see external_factors_agent.py). No-op if no report
    has been generated for (a, b).
    """
    p_a = win_probability(strengths[a], strengths[b])
    adj = load_adjustment(a, b)
    if adj:
        before = p_a
        p_a = min(0.99, max(0.01, p_a + adj))
        print(f"  [external factors] {a} vs {b}: base {before:.1%} -> "
              f"adjusted {p_a:.1%} ({adj:+.1%})")
    return p_a

def simulate_match(a, b, strengths):
    p_a = adjusted_win_probability(a, b, strengths)
    return a if random.random() < p_a else b

def simulate_tournament(bracket, strengths):
    round_winners = [simulate_match(a, b, strengths) for a, b in bracket]
    while len(round_winners) > 1:
        next_round = []
        for i in range(0, len(round_winners), 2):
            next_round.append(simulate_match(round_winners[i], round_winners[i + 1], strengths))
        round_winners = next_round
    return round_winners[0]

def run_monte_carlo(bracket, strengths, n_sims=N_SIMULATIONS):
    wins = defaultdict(int)
    for _ in range(n_sims):
        wins[simulate_tournament(bracket, strengths)] += 1
    return {team: count / n_sims for team, count in wins.items()}

# ---------------------------------------------------------------
# Name resolution — FIFA's CSV naming may not exactly match bracket names
# (e.g. "Bosnia and Herzegovina" vs "Bosnia-Herzegovina", "DR Congo" vs
# "Congo DR"). Fill in aliases here as you discover mismatches.
# ---------------------------------------------------------------
NAME_FIXES = {
    "Bosnia and Herzegovina": ["Bosnia-Herzegovina", "Bosnia & Herzegovina"],
    "DR Congo": ["Congo DR", "Democratic Republic of the Congo"],
    "USA": ["United States"],
    "Ivory Coast": ["Côte d'Ivoire", "Cote d'Ivoire"],
    "Cape Verde": ["Cabo Verde"],
}

def resolve_strengths_for_bracket(bracket, raw_points):
    all_teams = sorted({t for pair in bracket for t in pair})
    resolved = {}
    unresolved = []
    for team in all_teams:
        if team in raw_points:
            resolved[team] = raw_points[team]
            continue
        found = None
        for canonical, aliases in NAME_FIXES.items():
            if team == canonical or team in aliases:
                for candidate in [canonical] + aliases:
                    if candidate in raw_points:
                        found = raw_points[candidate]
                        break
            if found is not None:
                break
        if found is not None:
            resolved[team] = found
        else:
            unresolved.append(team)
    return resolved, unresolved

def predict_full_bracket(matchups, strengths):
    """
    Deterministic bracket walk: favorite advances every match. Shows the
    single most-likely path round by round, separate from the Monte Carlo
    championship odds which account for upset probability.
    """
    round_names = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final"]
    rounds = []
    current = matchups
    round_idx = 0
    while True:
        winners, results = [], []
        for a, b in current:
            p_a = adjusted_win_probability(a, b, strengths)
            winner = a if p_a >= 0.5 else b
            winners.append(winner)
            results.append((a, b, winner, p_a if winner == a else 1 - p_a))
        rounds.append((round_names[round_idx] if round_idx < len(round_names) else f"Round {round_idx}", results))
        if len(winners) == 1:
            break
        current = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
        round_idx += 1
    return rounds

def print_full_bracket(rounds):
    print("\n" + "=" * 60)
    print("PREDICTED BRACKET — pre-tournament FIFA rankings only")
    print("=" * 60)
    for round_name, results in rounds:
        print(f"\n--- {round_name} ---")
        for a, b, winner, conf in results:
            print(f"  {a:20s} vs {b:20s} -> {winner:20s} ({conf:.0%} model confidence)")
    champion = rounds[-1][1][0][2]
    print(f"\nPredicted champion (favorite-advances model): {champion}")


if __name__ == "__main__":
    raw_points = fetch_pretournament_fifa_points()
    strengths, unresolved = resolve_strengths_for_bracket(ROUND_OF_32_MATCHUPS, raw_points)

    if unresolved:
        print(f"\nERROR: could not find pre-tournament FIFA points for: {unresolved}")
        print("These teams' exact names don't match the CSV. Check the CSV's "
              "team-name spelling and add an alias to NAME_FIXES.")
        raise SystemExit(1)

    print("\nPre-tournament FIFA strength scores used:")
    for team, pts in sorted(strengths.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:25s} {pts:.2f}")

    print(f"\nRunning {N_SIMULATIONS} simulations using ONLY pre-tournament "
          f"FIFA rankings (no group-stage results)...")

    bracket_rounds = predict_full_bracket(ROUND_OF_32_MATCHUPS, strengths)
    print_full_bracket(bracket_rounds)

    results = run_monte_carlo(ROUND_OF_32_MATCHUPS, strengths)

    print("\n=== Pre-tournament championship probabilities ===")
    for team, prob in sorted(results.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:25s} {prob:.4f}")