"""
Feature engineering for tennis — the analogue of nba_features.py / club_features.py.

Everything is computed strictly from matches that finished BEFORE the one being
predicted, and every rating is updated only after its features are read.

What differs from the team sports in this repo:

  1. SURFACE IS A SEPARATE SKILL, not a modifier. Clay and grass reward
     different games strongly enough that players carry genuinely different
     abilities across them, so each player holds a per-surface Elo alongside
     an overall one and the model gets both. A team-sport model has no
     equivalent — a basketball court is a basketball court.
  2. NO HOME ADVANTAGE. Neutral venues, so there is no intercept term standing
     in for one, and no home/away asymmetry anywhere. Players are ordered
     alphabetically (see ingest_tennis.py) purely to keep the label honest.
  3. RANKING IS A REAL FEATURE. Tennis has an official, continuously updated
     strength list; team sports do not. Rank enters as a LOG difference
     because the gap between #1 and #10 is a chasm and the gap between #210
     and #219 is nothing, which a raw difference would treat identically.
  4. HEAD-TO-HEAD IS MEANINGFUL. Individual matchups recur and styles genuinely
     match up badly, unlike club sides whose rosters turn over.

Elo does NOT reset between seasons: tennis runs a continuous calendar with no
offseason roster churn, so last year's rating is simply this year's starting
point — the opposite of the NBA treatment in nba_features.py, and for a
concrete reason rather than by preference.
"""

from collections import defaultdict, deque

import numpy as np

STARTING_ELO = 1500.0
K_FACTOR = 32.0             # higher than a team sport's: fewer matches per player
SURFACE_K = 32.0
FORM_WINDOW = 20
DEFAULT_RANK = 500.0        # unranked/missing: treat as deep outside the top 500

FEATURE_NAMES = ["elo_diff", "surface_elo_diff", "log_rank_diff",
                 "rank_pts_diff", "form_diff", "h2h_diff", "matches_played_diff"]


def _num(v, default):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    return default if not np.isfinite(f) else f


def compute_features(matches):
    """
    matches: chronologically sorted dicts from db.fetch_tennis_matches().
    Returns rows with FEATURE_NAMES added, plus the final rating state.
    """
    elo = defaultdict(lambda: STARTING_ELO)
    surface_elo = defaultdict(lambda: STARTING_ELO)
    form = defaultdict(lambda: deque(maxlen=FORM_WINDOW))
    h2h = defaultdict(lambda: [0, 0])       # (a, b) -> [a wins, b wins]
    played = defaultdict(int)

    rows = []
    for m in matches:
        p1, p2, surface = m["p1"], m["p2"], m.get("surface") or "Unknown"
        e1, e2 = elo[p1], elo[p2]
        s1, s2 = surface_elo[(p1, surface)], surface_elo[(p2, surface)]

        f1 = float(np.mean(form[p1])) if form[p1] else 0.5
        f2 = float(np.mean(form[p2])) if form[p2] else 0.5
        hh = h2h[(p1, p2)]

        r1 = max(_num(m.get("p1_rank"), DEFAULT_RANK), 1.0)
        r2 = max(_num(m.get("p2_rank"), DEFAULT_RANK), 1.0)

        rows.append({
            **m,
            # log rank: a rank difference means far more at the top of the list
            # than at the bottom. Sign is flipped because a LOWER rank number is
            # a BETTER player, so this stays positive when p1 is the stronger.
            "log_rank_diff": float(np.log(r2) - np.log(r1)),
            "elo_diff": e1 - e2,
            "surface_elo_diff": s1 - s2,
            "rank_pts_diff": _num(m.get("p1_pts"), 0.0) - _num(m.get("p2_pts"), 0.0),
            "form_diff": f1 - f2,
            "h2h_diff": float(hh[0] - hh[1]),
            "matches_played_diff": float(played[p1] - played[p2]),
        })

        # ---- update state AFTER reading features (no leakage) ----
        y = float(m["p1_won"])
        exp1 = 1.0 / (1.0 + 10 ** (-(e1 - e2) / 400.0))
        elo[p1] = e1 + K_FACTOR * (y - exp1)
        elo[p2] = e2 + K_FACTOR * ((1.0 - y) - (1.0 - exp1))

        sexp1 = 1.0 / (1.0 + 10 ** (-(s1 - s2) / 400.0))
        surface_elo[(p1, surface)] = s1 + SURFACE_K * (y - sexp1)
        surface_elo[(p2, surface)] = s2 + SURFACE_K * ((1.0 - y) - (1.0 - sexp1))

        form[p1].append(y)
        form[p2].append(1.0 - y)
        h2h[(p1, p2)][0 if y else 1] += 1
        h2h[(p2, p1)][1 if y else 0] += 1
        played[p1] += 1
        played[p2] += 1

    final_state = {
        "elo": dict(elo),
        "surface_elo": {f"{k[0]}|{k[1]}": v for k, v in surface_elo.items()},
        "form": {k: list(v) for k, v in form.items()},
        "matches_played": dict(played),
    }
    return rows, final_state
