"""
Full Bracket Mock
================================================================================
Walks the World Cup bracket round by round, researching each round's actual
matchups with the external factors agent (Grok + Gemini) before predicting
winners — using only information available before that round's games (see
ROUND_CUTOFFS in external_factors_agent.py). Round of 32 pairings are the
real bracket; every round after that is whatever this model's own adjusted
predictions produce, not assumed knowledge of the real outcome.

Each new matchup costs ~2 paid API calls (Grok web search + Gemini). Reports
already saved in external_factors_reports/ are reused, not re-fetched. Use
--through to cap how far the walk goes — e.g. Round of 32 alone is 16
matchups; the full bracket (through Final) is 31.

Usage:
    py full_bracket_mock.py --through "Round of 32"
    py full_bracket_mock.py --through "Final"
"""

import argparse
import os

from pretournament_predictor import (
    ROUND_OF_32_MATCHUPS,
    adjusted_win_probability,
    fetch_pretournament_fifa_points,
    resolve_strengths_for_bracket,
)
from external_factors_agent import ROUND_CUTOFFS, get_matchup_report, has_report

ROUND_NAMES = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Final"]


def ensure_report(a, b, round_name):
    if has_report(a, b):
        return
    print(f"  researching {a} vs {b} ({round_name}, as of {ROUND_CUTOFFS.get(round_name)})...")
    get_matchup_report(a, b, context=round_name, as_of_date=ROUND_CUTOFFS.get(round_name))


def predict_bracket_with_research(matchups, strengths, through_round="Final"):
    through_idx = ROUND_NAMES.index(through_round)
    rounds = []
    current = matchups
    round_idx = 0
    while True:
        round_name = ROUND_NAMES[round_idx] if round_idx < len(ROUND_NAMES) else f"Round {round_idx}"
        winners, results = [], []
        for a, b in current:
            ensure_report(a, b, round_name)
            p_a = adjusted_win_probability(a, b, strengths)
            winner = a if p_a >= 0.5 else b
            winners.append(winner)
            results.append((a, b, winner, p_a if winner == a else 1 - p_a))
        rounds.append((round_name, results))
        if len(winners) == 1 or round_idx >= through_idx:
            break
        current = [(winners[i], winners[i + 1]) for i in range(0, len(winners), 2)]
        round_idx += 1
    return rounds


def print_bracket(rounds):
    print("\n" + "=" * 70)
    print("MOCK BRACKET — FIFA rankings + external-factors research per round")
    print("=" * 70)
    for round_name, results in rounds:
        print(f"\n--- {round_name} ---")
        for a, b, winner, conf in results:
            print(f"  {a:20s} vs {b:20s} -> {winner:20s} ({conf:.0%} model confidence)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mock the World Cup bracket with external-factors research per round."
    )
    parser.add_argument("--through", default="Round of 32", choices=ROUND_NAMES,
                         help="How far to walk the bracket (default: Round of 32 only).")
    args = parser.parse_args()

    for var in ("XAI_API_KEY", "GOOGLE_API_KEY"):
        if not os.getenv(var):
            raise SystemExit(f"Missing {var}. Copy .env.example to .env and fill it in.")

    raw_points = fetch_pretournament_fifa_points()
    strengths, unresolved = resolve_strengths_for_bracket(ROUND_OF_32_MATCHUPS, raw_points)
    if unresolved:
        raise SystemExit(f"Could not find pre-tournament FIFA points for: {unresolved}")

    bracket_rounds = predict_bracket_with_research(ROUND_OF_32_MATCHUPS, strengths, through_round=args.through)
    print_bracket(bracket_rounds)
