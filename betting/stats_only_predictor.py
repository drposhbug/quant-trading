"""
Pure Stats-Based World Cup BRACKET Simulator (v2)
================================================================================
Difference from v1 (stats_only_predictor.py): this version simulates the
REAL tournament tree structure — Round of 32 -> Round of 16 -> Quarterfinals
-> Semifinals -> Final — rather than just flattening 32 teams into one long
list. Bracket position now genuinely matters: two strong teams on the same
side of the draw will eliminate each other early; two on opposite sides
only meet in the final (if at all).

WHAT YOU MUST DO BEFORE TRUSTING THE OUTPUT:
Replace ROUND_OF_32_MATCHUPS below with the real FIFA-assigned pairings.
Everything below that point (R16 onward) is DERIVED automatically from
whoever wins each R32 match — you don't need to hand-enter later rounds.
"""

import random
from collections import defaultdict

N_SIMULATIONS = 20000
ELO_SCALE = 40.0  # tuned by eye last round — revisit once you have real data to backtest against

# ---------------------------------------------------------------
# Group-stage strength scores: Points*3 + Goal Difference
# ---------------------------------------------------------------
STRENGTHS = {
    "Mexico": 33, "South Africa": 11,
    "Switzerland": 25, "Canada": 17,
    "Brazil": 27, "Morocco": 24,
    "United States": 22, "Australia": 12,
    "Germany": 24, "Ivory Coast": 20,
    "Netherlands": 27, "Japan": 19,
    "Belgium": 19, "Egypt": 17,
    "Spain": 26, "Cape Verde": 9,
    "France": 35, "Norway": 22,
    "Argentina": 34, "Austria": 12,
    "Colombia": 24, "Portugal": 20,
    "England": 25, "Croatia": 18,
    "Congo DR": 13, "Sweden": 12, "Algeria": 12, "Ecuador": 12,
    "South Korea": 11, "Bosnia-Herzegovina": 11, "Ghana": 10, "Iran": 9,
    "Paraguay": 7, "Senegal": 7,
}

# ---------------------------------------------------------------
# REAL Round of 32 matchups, confirmed from actual bracket screenshots.
# ---------------------------------------------------------------
ROUND_OF_32_MATCHUPS = [
    ("Germany", "Paraguay"),           # Match 0
    ("France", "Sweden"),              # Match 1
    ("South Africa", "Canada"),        # Match 2
    ("Netherlands", "Morocco"),        # Match 3
    ("Portugal", "Croatia"),           # Match 4
    ("Spain", "Austria"),              # Match 5
    ("United States", "Bosnia-Herzegovina"),  # Match 6
    ("Belgium", "Senegal"),            # Match 7
    ("Brazil", "Japan"),               # Match 8
    ("Ivory Coast", "Norway"),         # Match 9
    ("Mexico", "Ecuador"),             # Match 10
    ("England", "Congo DR"),           # Match 11
    ("Argentina", "Cape Verde"),       # Match 12
    ("Australia", "Egypt"),            # Match 13
    ("Switzerland", "Algeria"),        # Match 14
    ("Colombia", "Ghana"),             # Match 15
]

def win_probability(strength_a, strength_b):
    return 1.0 / (1.0 + 10 ** ((strength_b - strength_a) / ELO_SCALE))

def simulate_match(a, b):
    p_a = win_probability(STRENGTHS[a], STRENGTHS[b])
    return a if random.random() < p_a else b

def simulate_tournament():
    """
    Simulates R32 -> R16 -> QF -> SF -> Final by successively pairing up
    adjacent winners, exactly mirroring standard single-elimination bracket
    structure. Match 0 vs Match 1's winners meet, Match 2 vs 3's winners
    meet, etc. — this is what makes bracket position matter.
    """
    round_winners = [simulate_match(a, b) for a, b in ROUND_OF_32_MATCHUPS]
    while len(round_winners) > 1:
        next_round = []
        for i in range(0, len(round_winners), 2):
            next_round.append(simulate_match(round_winners[i], round_winners[i + 1]))
        round_winners = next_round
    return round_winners[0]

def run_monte_carlo(n_sims=N_SIMULATIONS):
    wins = defaultdict(int)
    for _ in range(n_sims):
        wins[simulate_tournament()] += 1
    return {team: count / n_sims for team, count in wins.items()}

def predict_full_bracket(matchups):
    """
    Deterministic bracket walk: at each match, the team with the higher
    win probability is projected to advance. This is NOT the same as the
    Monte Carlo championship odds above — it's "who does the model expect
    to win, round by round," ignoring the chance of upsets. Useful as a
    single readable bracket prediction rather than a probability table.
    """
    rounds = []
    current = matchups
    round_names = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final"]

    round_idx = 0
    while True:
        winners = []
        results = []
        for a, b in current:
            p_a = win_probability(STRENGTHS[a], STRENGTHS[b])
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
    print("PREDICTED BRACKET (favorite advances each round)")
    print("=" * 60)
    for round_name, results in rounds:
        print(f"\n--- {round_name} ---")
        for a, b, winner, conf in results:
            loser = b if winner == a else a
            print(f"  {a:20s} vs {b:20s} -> {winner:20s} ({conf:.0%} model confidence)")
    champion = rounds[-1][1][0][2]
    print(f"\nPredicted champion (favorite-advances model): {champion}")
    print("NOTE: this is the single most-likely path assuming no upsets — it is "
          "NOT the same as the Monte Carlo championship probabilities, which "
          "account for the chance of upsets at every round.")


def print_bracket_side(matchups):
    """Quick sanity view of who's on which side of the draw."""
    half = len(matchups) // 2
    print("Top half of draw:")
    for a, b in matchups[:half]:
        print(f"  {a} vs {b}")
    print("Bottom half of draw:")
    for a, b in matchups[half:]:
        print(f"  {a} vs {b}")

if __name__ == "__main__":
    all_teams = [t for pair in ROUND_OF_32_MATCHUPS for t in pair]
    missing = [t for t in all_teams if t not in STRENGTHS]
    if missing:
        print(f"ERROR: these teams have no strength score: {missing}")
        raise SystemExit(1)
    if len(all_teams) != 32 or len(set(all_teams)) != 32:
        print(f"WARNING: expected exactly 32 unique teams in the bracket, "
              f"found {len(all_teams)} entries / {len(set(all_teams))} unique.")

    print_bracket_side(ROUND_OF_32_MATCHUPS)

    bracket_rounds = predict_full_bracket(ROUND_OF_32_MATCHUPS)
    print_full_bracket(bracket_rounds)

    print(f"\nRunning {N_SIMULATIONS} full bracket simulations "
          f"(R32 -> R16 -> QF -> SF -> Final)...")
    results = run_monte_carlo()

    print("\n=== Bracket-aware championship probabilities ===")
    for team, prob in sorted(results.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  {team:20s} {prob:.4f}")