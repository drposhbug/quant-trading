"""
Blended Predictor: Pre-Tournament FIFA Ranking + Squad Market Value
================================================================================
Combines two independent pre-tournament signals into one strength score:
  1. FIFA ranking points (reputation/results-based, from before the WC)
  2. Squad market value (club-form/talent-based, Transfermarkt)

Neither signal uses any 2026 World Cup match data — this stays a genuine
"what would you have predicted going in" model, just using two inputs
instead of one.

Blending method: each metric is min-max normalized to a 0-100 scale (so
FIFA points and EUR millions become comparable), then averaged with equal
weight. Change BLEND_WEIGHT below to weigh one signal more than the other.
"""

import random
from collections import defaultdict

N_SIMULATIONS = 20000
ELO_SCALE = 60.0  # retuned after test run — 25 was too aggressive (near-100%
                   # confidence in most matches), same tuning caveat as always

# Weight given to FIFA ranking vs squad value (must sum to 1.0)
BLEND_WEIGHT_FIFA = 0.5
BLEND_WEIGHT_SQUAD = 0.5

# ---------------------------------------------------------------
# Pre-tournament FIFA ranking points (from pretournament_predictor.py's
# last successful run — Sept 2024 CSV snapshot, same known staleness caveat)
# ---------------------------------------------------------------
FIFA_POINTS = {
    "Argentina": 1889.02, "France": 1851.92, "Spain": 1836.42, "England": 1817.28,
    "Brazil": 1772.02, "Belgium": 1768.14, "Netherlands": 1759.95, "Portugal": 1752.14,
    "Colombia": 1738.72, "Croatia": 1699.60, "Germany": 1692.19, "Morocco": 1676.14,
    "Switzerland": 1641.00, "Japan": 1639.60, "Mexico": 1635.66, "United States": 1632.19,
    "Senegal": 1620.87, "Austria": 1580.37, "Australia": 1544.30, "Ecuador": 1535.43,
    "Sweden": 1528.18, "Egypt": 1515.64, "Ivory Coast": 1509.12, "Canada": 1502.31,
    "Algeria": 1486.03, "Norway": 1472.16, "Paraguay": 1423.98, "DR Congo": 1416.91,
    "South Africa": 1415.07, "Cape Verde": 1379.17, "Ghana": 1360.43,
    "Bosnia and Herzegovina": 1332.39,
}

# ---------------------------------------------------------------
# Squad market values in EUR millions (Transfermarkt, via planetfootball.com)
# ---------------------------------------------------------------
SQUAD_VALUES = {
    "France": 1520, "Sweden": 406.08, "South Africa": 49.25, "Canada": 198.65,
    "Netherlands": 754.2, "Morocco": 447.7, "Portugal": 1010, "Croatia": 387.3,
    "Spain": 1220, "Austria": 245.2, "United States": 385.6,
    "Bosnia and Herzegovina": 146.4, "Belgium": 547.5, "Senegal": 478.1,
    "Brazil": 928.2, "Japan": 270.85, "Ivory Coast": 522.1, "Norway": 589.9,
    "Mexico": 191.85, "Ecuador": 368.7, "England": 1360, "DR Congo": 143.9,
    "Argentina": 807.5, "Cape Verde": 49.25, "Australia": 77.45, "Egypt": 116.48,
    "Switzerland": 332.5, "Algeria": 256.9, "Colombia": 302.35, "Ghana": 234.5,
    "Germany": 947, "Paraguay": 153.65,
}

ROUND_OF_32_MATCHUPS = [
    ("Germany", "Paraguay"), ("France", "Sweden"),
    ("South Africa", "Canada"), ("Netherlands", "Morocco"),
    ("Portugal", "Croatia"), ("Spain", "Austria"),
    ("United States", "Bosnia and Herzegovina"), ("Belgium", "Senegal"),
    ("Brazil", "Japan"), ("Ivory Coast", "Norway"),
    ("Mexico", "Ecuador"), ("England", "DR Congo"),
    ("Argentina", "Cape Verde"), ("Australia", "Egypt"),
    ("Switzerland", "Algeria"), ("Colombia", "Ghana"),
]

def min_max_normalize(values: dict) -> dict:
    lo, hi = min(values.values()), max(values.values())
    span = hi - lo if hi != lo else 1.0
    return {team: 100 * (val - lo) / span for team, val in values.items()}

def build_blended_strengths():
    fifa_norm = min_max_normalize(FIFA_POINTS)
    squad_norm = min_max_normalize(SQUAD_VALUES)
    all_teams = set(fifa_norm) | set(squad_norm)
    blended = {}
    for team in all_teams:
        f = fifa_norm.get(team)
        s = squad_norm.get(team)
        if f is None or s is None:
            continue
        blended[team] = BLEND_WEIGHT_FIFA * f + BLEND_WEIGHT_SQUAD * s
    return blended, fifa_norm, squad_norm

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

def illustrative_scoreline(conf, winner, loser):
    """
    NOT a real goals model — just produces a plausible-looking result so the
    bracket reads like real scorelines. Carries no statistical meaning
    beyond the win probability itself. Two outcome types:
      - Decisive: winner wins outright in regulation, margin scales with
        how lopsided the confidence is (now uncapped up to 4 goals, not 2).
      - Draw + penalties: closer matches (confidence nearer 50%) have a
        chance of finishing level after 90 minutes, with the model's
        predicted winner going through on penalties — mirroring how real
        knockout draws get resolved.
    """
    closeness = 1 - abs(conf - 0.5) * 2  # 1.0 = coin flip, 0.0 = near-certain
    draw_chance = 0.22 * closeness       # up to ~22% draw chance for tossups

    if random.random() < draw_chance:
        reg_goals = random.choice([0, 1, 2])
        pens_winner = random.randint(3, 5)
        pens_loser = random.randint(0, pens_winner - 1)
        return f"{winner} {reg_goals}-{reg_goals} {loser} ({winner} wins {pens_winner}-{pens_loser} on penalties)"

    margin = max(1, round((conf - 0.5) * 8))  # widened — was *4, capped at 2 max
    margin = min(margin, 4)
    loser_goals = random.choice([0, 1]) if margin <= 2 else 0
    winner_goals = loser_goals + margin
    return f"{winner} {winner_goals}-{loser_goals} {loser}"

def print_full_bracket(rounds):
    print("\n" + "=" * 60)
    print("PREDICTED BRACKET — blended (FIFA ranking + squad value)")
    print("(Scorelines are illustrative only — not a real goals model)")
    print("=" * 60)
    for round_name, results in rounds:
        print(f"\n--- {round_name} ---")
        for a, b, winner, conf in results:
            loser = b if winner == a else a
            line = illustrative_scoreline(conf, winner, loser)
            print(f"  {a:20s} vs {b:20s} -> {line} ({conf:.0%} model confidence)")
    champion = rounds[-1][1][0][2]
    print(f"\nPredicted champion (favorite-advances model): {champion}")

if __name__ == "__main__":
    blended, fifa_norm, squad_norm = build_blended_strengths()

    all_teams = [t for pair in ROUND_OF_32_MATCHUPS for t in pair]
    missing = [t for t in all_teams if t not in blended]
    if missing:
        print(f"ERROR: no blended strength for: {missing}")
        raise SystemExit(1)

    print(f"Blend weights: FIFA ranking {BLEND_WEIGHT_FIFA:.0%}, "
          f"squad value {BLEND_WEIGHT_SQUAD:.0%}\n")
    print(f"{'Team':25s} {'FIFA norm':>10s} {'Squad norm':>11s} {'Blended':>9s}")
    for team in sorted(all_teams, key=lambda t: blended[t], reverse=True):
        print(f"{team:25s} {fifa_norm[team]:10.1f} {squad_norm[team]:11.1f} {blended[team]:9.1f}")

    bracket_rounds = predict_full_bracket(ROUND_OF_32_MATCHUPS, blended)
    print_full_bracket(bracket_rounds)

    print(f"\nRunning {N_SIMULATIONS} simulations using the blended strength score...")
    results = run_monte_carlo(ROUND_OF_32_MATCHUPS, blended)

    print("\n=== Blended championship probabilities ===")
    for team, prob in sorted(results.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:25s} {prob:.4f}")