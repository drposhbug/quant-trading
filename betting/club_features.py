"""
Shared feature engineering for club-level models. Used by both
train_club_model.py (Premier League) and train_mls_model.py (MLS) so the
same statistical signals are computed identically for both leagues.

Signals, all computed strictly from information before each match (no
leakage — same principle as everywhere else in this repo):

  1. elo_diff — running Elo rating difference (train_club_model.py's
     original signal).
  2. h2h_home_win_rate — this exact home team's historical win rate
     specifically when hosting this exact away team (the "have they beaten
     them at home before" signal). h2h_meetings is included alongside it so
     the model can learn to trust it more when there's more history behind
     it, and default to a neutral 0.5 on a first-ever meeting.
  3. recent_form_diff — each team's league points-per-game over its last 5
     matches (any opponent, any venue), home minus away.
  4. elo_form_interaction / elo_h2h_interaction — lets models capture that,
     e.g., recent form or head-to-head history might matter more/less
     depending on how close the two teams' Elo ratings are, rather than
     assuming each signal contributes independently.

Deliberately not included: an "injuries x home advantage" interaction.
That's only backtestable on the handful of matches actually researched via
external_factors_agent.py (a few dozen at most) — nowhere near enough rows
to fit an interaction term without just fitting noise. It stays a
post-hoc adjustment (see club_match_predict.py) instead of a trained
feature until there's enough labeled history to support it.
"""

from collections import defaultdict, deque

STARTING_ELO = 1500.0
PROMOTED_ELO = 1430.0        # clubs entering the league after season 1 start below average,
                             # not at it — a newly promoted side is not a league-average side
K_FACTOR = 20.0
HOME_ADVANTAGE_ELO = 65.0    # added to the home side inside the Elo *update's* expected score
                             # only — the elo_diff FEATURE stays raw, since the classifier's
                             # intercept already learns home advantage at prediction time.
                             # Without this, the update step systematically over-rewards
                             # home wins and the ratings drift.
SEASON_REGRESSION = 0.25     # at each season boundary, every rating regresses 25% toward
                             # 1500 — squads churn over a summer, and a club absent from the
                             # league decays toward the mean instead of freezing for years
FORM_WINDOW = 5
FORM_DEFAULT_PPG = 1.0  # ~league-average points per game before a team has any history


def mov_multiplier(margin):
    """
    Margin-of-victory K scaling (World Football Elo convention):
    win by 0-1 -> 1.0x, by 2 -> 1.5x, by 3 -> 1.75x, +0.125x per extra goal.
    A 4-0 result carries more information than a 1-0, so it moves ratings more.
    """
    if margin <= 1:
        return 1.0
    if margin == 2:
        return 1.5
    return 1.75 + (margin - 3) * 0.125


def compute_features(matches):
    """
    matches: chronologically-sorted list of dicts with keys
    date, home, away, home_score, away_score (plus any extra keys, which
    are passed through unchanged).

    Returns (rows, final_state) where rows are the input matches with
    engineered features and a computed "result" (H/D/A) added, and
    final_state holds the end-of-history Elo/H2H/form data needed to
    predict a brand-new future match.
    """
    elo = {}
    h2h = defaultdict(lambda: {"home_wins": 0, "meetings": 0})
    form = defaultdict(lambda: deque(maxlen=FORM_WINDOW))

    first_season = matches[0].get("season") if matches else None
    current_season = first_season

    rows = []
    for m in matches:
        home, away = m["home"], m["away"]

        season = m.get("season")
        if season is not None and season != current_season:
            # season boundary: regress every rating toward the mean.
            # Applies to absent (relegated) clubs too, so a side returning
            # after N seasons re-enters with a rating that has decayed toward
            # 1500 rather than a frozen years-old one.
            for team in elo:
                elo[team] += SEASON_REGRESSION * (STARTING_ELO - elo[team])
            current_season = season

        # in the very first season of the dataset everyone is unknown, so 1500
        # is the honest prior; after that, a club with no rating is a promoted
        # side and enters below league average
        default_elo = STARTING_ELO if (season is None or season == first_season) else PROMOTED_ELO
        home_elo = elo.get(home, default_elo)
        away_elo = elo.get(away, default_elo)
        elo_diff = home_elo - away_elo

        h2h_record = h2h[(home, away)]
        h2h_meetings = h2h_record["meetings"]
        h2h_home_win_rate = (h2h_record["home_wins"] / h2h_meetings) if h2h_meetings else 0.5

        home_form = form[home]
        away_form = form[away]
        home_form_ppg = (sum(home_form) / len(home_form)) if home_form else FORM_DEFAULT_PPG
        away_form_ppg = (sum(away_form) / len(away_form)) if away_form else FORM_DEFAULT_PPG
        recent_form_diff = home_form_ppg - away_form_ppg

        hs, as_ = m["home_score"], m["away_score"]
        result = "H" if hs > as_ else ("A" if as_ > hs else "D")

        rows.append({
            **m,
            "elo_diff": elo_diff,
            "h2h_home_win_rate": h2h_home_win_rate,
            "h2h_meetings": h2h_meetings,
            "recent_form_diff": recent_form_diff,
            "elo_form_interaction": elo_diff * recent_form_diff,
            "elo_h2h_interaction": elo_diff * (h2h_home_win_rate - 0.5),
            "result": result,
        })

        actual_home = {"H": 1.0, "A": 0.0}.get(result, 0.5)
        # home advantage lives here (update only), NOT in the elo_diff feature
        expected_home = 1.0 / (1.0 + 10 ** (-(elo_diff + HOME_ADVANTAGE_ELO) / 400.0))
        k = K_FACTOR * mov_multiplier(abs(hs - as_))
        elo[home] = home_elo + k * (actual_home - expected_home)
        elo[away] = away_elo + k * ((1 - actual_home) - (1 - expected_home))

        h2h_record["meetings"] += 1
        if result == "H":
            h2h_record["home_wins"] += 1

        home_pts = 3 if result == "H" else (1 if result == "D" else 0)
        away_pts = 3 if result == "A" else (1 if result == "D" else 0)
        form[home].append(home_pts)
        form[away].append(away_pts)

    final_state = {
        "elo": elo,
        "h2h": {f"{h}|||{a}": v for (h, a), v in h2h.items()},
        "form": {team: list(pts) for team, pts in form.items()},
    }
    return rows, final_state


FEATURE_NAMES = ["elo_diff", "h2h_home_win_rate", "h2h_meetings", "recent_form_diff",
                  "elo_form_interaction", "elo_h2h_interaction"]


def feature_vector(row):
    return [row[name] for name in FEATURE_NAMES]


def predict_features(home, away, final_state):
    """
    Builds the same feature vector for a brand-new (not-yet-played) match,
    using saved end-of-history state instead of walking through matches.
    """
    elo = final_state["elo"]
    h2h = final_state["h2h"]
    form = final_state["form"]

    # a club missing from saved state is a newcomer — same PROMOTED_ELO prior
    # the training walk uses, not the league-average 1500
    elo_diff = elo.get(home, PROMOTED_ELO) - elo.get(away, PROMOTED_ELO)

    h2h_record = h2h.get(f"{home}|||{away}", {"home_wins": 0, "meetings": 0})
    h2h_meetings = h2h_record["meetings"]
    h2h_home_win_rate = (h2h_record["home_wins"] / h2h_meetings) if h2h_meetings else 0.5

    home_form = form.get(home, [])
    away_form = form.get(away, [])
    home_form_ppg = (sum(home_form) / len(home_form)) if home_form else FORM_DEFAULT_PPG
    away_form_ppg = (sum(away_form) / len(away_form)) if away_form else FORM_DEFAULT_PPG
    recent_form_diff = home_form_ppg - away_form_ppg

    return [elo_diff, h2h_home_win_rate, h2h_meetings, recent_form_diff,
            elo_diff * recent_form_diff, elo_diff * (h2h_home_win_rate - 0.5)]
