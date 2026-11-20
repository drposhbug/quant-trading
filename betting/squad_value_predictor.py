"""
Squad Market Value World Cup Predictor
================================================================================
Uses each team's total squad market value (Transfermarkt, via planetfootball.com,
published July 1 2026) as the strength score — this reflects how good each
player is judged to be based on their CLUB performance (Premier League, La
Liga, etc.) and reputation, aggregated into one number per national team.

This is NOT group-stage results — no goals, points, or match outcomes from
the World Cup itself are used. It IS, however, published July 1 2026, a few
weeks into the tournament window, so treat it as "club-form-based" rather
than strictly pre-tournament — see caveat in chat.

Source: https://www.planetfootball.com/lists-and-rankings/world-cup-2026-every-squad-ranked-market-value
"""

import random
from collections import defaultdict

N_SIMULATIONS = 20000
ELO_SCALE = 1200.0  # retuned — squad values span 49 to 1520 (much wider than
                     # typical Elo gaps), so 400 made nearly every match a
                     # near-certainty. 1200 is a starting guess for sane
                     # separation; still needs backtesting, same as always.

# ---------------------------------------------------------------
# Squad market values in EUR millions (Transfermarkt, via planetfootball.com)
# ---------------------------------------------------------------
SQUAD_VALUES = {
    "France": 1520, "Sweden": 406.08,
    "South Africa": 49.25, "Canada": 198.65,
    "Netherlands": 754.2, "Morocco": 447.7,
    "Portugal": 1010, "Croatia": 387.3,
    "Spain": 1220, "Austria": 245.2,
    "United States": 385.6, "Bosnia and Herzegovina": 146.4,
    "Belgium": 547.5, "Senegal": 478.1,
    "Brazil": 928.2, "Japan": 270.85,
    "Ivory Coast": 522.1, "Norway": 589.9,
    "Mexico": 191.85, "Ecuador": 368.7,
    "England": 1360, "DR Congo": 143.9,
    "Argentina": 807.5, "Cape Verde": 49.25,
    "Australia": 77.45, "Egypt": 116.48,
    "Switzerland": 332.5, "Algeria": 256.9,
    "Colombia": 302.35, "Ghana": 234.5,
    "Germany": 947, "Paraguay": 153.65,
}

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

def simulate_match(a, b, strengths):
    p_a = win_probability(strengths[a], strengths[b])
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

def predict_full_bracket(matchups, strengths):
    round_names = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final"]
    rounds = []
    current = matchups
    round_idx = 0
    while True:
        winners, results = [], []
        for a, b in current:
            p_a = win_probability(strengths[a], strengths[b])
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
    print("PREDICTED BRACKET — squad market value only")
    print("=" * 60)
    for round_name, results in rounds:
        print(f"\n--- {round_name} ---")
        for a, b, winner, conf in results:
            print(f"  {a:25s} vs {b:25s} -> {winner:25s} ({conf:.0%} model confidence)")
    champion = rounds[-1][1][0][2]
    print(f"\nPredicted champion (favorite-advances model): {champion}")

if __name__ == "__main__":
    all_teams = [t for pair in ROUND_OF_32_MATCHUPS for t in pair]
    missing = [t for t in all_teams if t not in SQUAD_VALUES]
    if missing:
        print(f"ERROR: no squad value for: {missing}")
        raise SystemExit(1)

    print("Squad market values used (EUR millions):")
    for team, val in sorted(SQUAD_VALUES.items(), key=lambda kv: kv[1], reverse=True):
        if team in all_teams:
            print(f"  {team:25s} {val:.2f}")

    bracket_rounds = predict_full_bracket(ROUND_OF_32_MATCHUPS, SQUAD_VALUES)
    print_full_bracket(bracket_rounds)

    print(f"\nRunning {N_SIMULATIONS} simulations using ONLY squad market value...")
    results = run_monte_carlo(ROUND_OF_32_MATCHUPS, SQUAD_VALUES)

    print("\n=== Squad-value-based championship probabilities ===")
    for team, prob in sorted(results.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:25s} {prob:.4f}")