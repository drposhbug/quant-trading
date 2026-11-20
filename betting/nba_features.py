"""
Feature engineering for the NBA match-outcome model — the basketball analogue
of club_features.py. Same discipline as everywhere else in this repo: every
feature is computed strictly from information available BEFORE tip-off, so
there is no leakage from the game being predicted.

Why the signals differ from the soccer models:

  1. elo_diff — running Elo, NBA-tuned. Uses FiveThirtyEight's NBA margin-of-
     victory multiplier so a 30-point blowout moves ratings more than a
     buzzer-beater, but with the favorite-damping term that stops good teams'
     ratings from inflating just by beating bad teams badly.
  2. form_diff — each team's win% over its last FORM_WINDOW games (home minus
     away). Basketball's 82-game season makes short-window form meaningful.
  3. net_rating_diff — rolling net rating (points scored minus allowed per 100
     possessions) over the last FORM_WINDOW games. This is the single best
     box-score predictor of team strength; Elo only sees wins/losses and
     margin, net rating sees efficiency.
  4. rest_diff / b2b_diff — days of rest (home minus away) and back-to-back
     flags. Rest is a real, well-documented NBA edge that has no soccer
     equivalent: a team on the second night of a back-to-back, especially the
     road team, is measurably worse. b2b_diff = away_b2b - home_b2b so a
     positive value favors the home side (the away team is the tired one).
  5. elo_form_interaction — lets the model weight recent form differently
     depending on how far apart the two teams' baseline ratings are.

pace_diff (rolling possessions per 48) is computed and stored for analysis but
deliberately kept OUT of FEATURE_NAMES: pace predicts how many points get
scored, not who wins, so as a win-probability feature it's mostly noise.

Rolling form/net-rating/pace and rest all RESET at each season boundary
(rosters turn over and the months-long offseason make last season's last-5 and
"days since last game" meaningless), while Elo carries over with a regression
toward the mean — same split FiveThirtyEight uses.
"""

from collections import defaultdict, deque
from datetime import datetime

STARTING_ELO = 1500.0
K_FACTOR = 20.0
HOME_ADVANTAGE_ELO = 100.0   # added to the home side inside the Elo update's
                             # expected score only — the elo_diff FEATURE stays
                             # raw, since the classifier intercept learns home
                             # advantage at prediction time (same as soccer).
SEASON_REGRESSION = 0.25     # each season, ratings regress 25% toward 1500 —
                             # rosters churn, so last year's rating is a prior,
                             # not a fact.
FORM_WINDOW = 10
FORM_DEFAULT_WINPCT = 0.5
NET_RATING_DEFAULT = 0.0
DEFAULT_REST_DAYS = 3        # before a team's first tracked game of a season
MAX_REST_DAYS = 5            # cap: 5 days off and 12 days off play about the same


def mov_multiplier(margin, elo_diff_winner):
    """
    FiveThirtyEight's NBA margin-of-victory multiplier. The numerator rewards
    bigger wins (sub-linearly); the denominator's elo_diff_winner term damps
    the update when a heavy favorite wins big, which otherwise inflates strong
    teams' ratings without bound (autocorrelation correction).
    elo_diff_winner = winner's rating minus loser's, both including home edge.
    """
    return ((margin + 3.0) ** 0.8) / (7.5 + 0.006 * elo_diff_winner)


def _possessions(box):
    """
    Standard possession estimate: FGA - OREB + TOV + 0.44*FTA. One team's
    possession count for the game.
    """
    return box["fga"] - box["oreb"] + box["tov"] + 0.44 * box["fta"]


def _as_date(d):
    if isinstance(d, datetime):
        return d.date()
    return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()


def compute_features(games):
    """
    games: chronologically-sorted list of dicts with keys
        date, season, home, away, home_score, away_score,
        home_box, away_box   (each *_box: {fga, fta, oreb, tov, min})

    Returns (rows, final_state). rows are the input games with engineered
    features and a computed result (H/A) added; final_state holds the
    end-of-history Elo / form / net-rating / pace / last-game-date needed to
    predict a brand-new future game (see predict_features).
    """
    elo = {}
    form = defaultdict(lambda: deque(maxlen=FORM_WINDOW))          # 1.0 win / 0.0 loss
    net_hist = defaultdict(lambda: deque(maxlen=FORM_WINDOW))      # net rating per game
    pace_hist = defaultdict(lambda: deque(maxlen=FORM_WINDOW))     # possessions/48 per game
    last_played = {}                                              # team -> date of prior game

    current_season = games[0].get("season") if games else None

    def avg(hist, team, default):
        v = hist[team]
        return (sum(v) / len(v)) if v else default

    rows = []
    for g in games:
        home, away = g["home"], g["away"]
        season = g.get("season")
        game_date = _as_date(g["date"])

        if season is not None and season != current_season:
            # season boundary: regress Elo toward the mean, and wipe the
            # within-season rolling state (form/efficiency/rest) that doesn't
            # carry across an offseason.
            for team in elo:
                elo[team] += SEASON_REGRESSION * (STARTING_ELO - elo[team])
            form.clear()
            net_hist.clear()
            pace_hist.clear()
            last_played.clear()
            current_season = season

        home_elo = elo.get(home, STARTING_ELO)
        away_elo = elo.get(away, STARTING_ELO)
        elo_diff = home_elo - away_elo

        home_winpct = avg(form, home, FORM_DEFAULT_WINPCT)
        away_winpct = avg(form, away, FORM_DEFAULT_WINPCT)
        form_diff = home_winpct - away_winpct

        net_rating_diff = avg(net_hist, home, NET_RATING_DEFAULT) - avg(net_hist, away, NET_RATING_DEFAULT)
        pace_diff = avg(pace_hist, home, 0.0) - avg(pace_hist, away, 0.0) if (pace_hist[home] and pace_hist[away]) else 0.0

        home_rest = min((game_date - last_played[home]).days, MAX_REST_DAYS) if home in last_played else DEFAULT_REST_DAYS
        away_rest = min((game_date - last_played[away]).days, MAX_REST_DAYS) if away in last_played else DEFAULT_REST_DAYS
        rest_diff = home_rest - away_rest
        home_b2b = 1 if home_rest <= 1 else 0
        away_b2b = 1 if away_rest <= 1 else 0
        b2b_diff = away_b2b - home_b2b   # positive => away team is the tired one => helps home

        hs, as_ = g["home_score"], g["away_score"]
        result = "H" if hs > as_ else "A"   # no draws in the NBA

        rows.append({
            **g,
            "elo_diff": elo_diff,
            "form_diff": form_diff,
            "net_rating_diff": net_rating_diff,
            "pace_diff": pace_diff,
            "rest_diff": float(rest_diff),
            "b2b_diff": float(b2b_diff),
            "elo_form_interaction": elo_diff * form_diff,
            "result": result,
        })

        # ---- update state AFTER reading features (no leakage) ----
        actual_home = 1.0 if result == "H" else 0.0
        home_adj, away_adj = home_elo + HOME_ADVANTAGE_ELO, away_elo
        expected_home = 1.0 / (1.0 + 10 ** (-(home_adj - away_adj) / 400.0))
        elo_diff_winner = (home_adj - away_adj) if result == "H" else (away_adj - home_adj)
        k = K_FACTOR * mov_multiplier(abs(hs - as_), elo_diff_winner)
        elo[home] = home_elo + k * (actual_home - expected_home)
        elo[away] = away_elo + k * ((1 - actual_home) - (1 - expected_home))

        form[home].append(actual_home)
        form[away].append(1.0 - actual_home)

        hbox, abox = g["home_box"], g["away_box"]
        home_poss, away_poss = _possessions(hbox), _possessions(abox)
        if home_poss > 0 and away_poss > 0:
            home_ortg = 100.0 * hs / home_poss
            away_ortg = 100.0 * as_ / away_poss
            net_hist[home].append(home_ortg - away_ortg)
            net_hist[away].append(away_ortg - home_ortg)
            # pace = possessions scaled to 48 minutes (MIN is total team minutes,
            # ~240 in regulation, more in OT — so OT games don't look high-pace)
            pace_hist[home].append(48.0 * home_poss / (hbox["min"] / 5.0))
            pace_hist[away].append(48.0 * away_poss / (abox["min"] / 5.0))

        last_played[home] = game_date
        last_played[away] = game_date

    final_state = {
        "elo": elo,
        "form": {t: list(v) for t, v in form.items()},
        "net_rating": {t: list(v) for t, v in net_hist.items()},
        "pace": {t: list(v) for t, v in pace_hist.items()},
        "last_played": {t: d.isoformat() for t, d in last_played.items()},
        "season": current_season,
    }
    return rows, final_state


# pace_diff intentionally excluded — see module docstring.
FEATURE_NAMES = ["elo_diff", "form_diff", "net_rating_diff", "rest_diff",
                 "b2b_diff", "elo_form_interaction"]


def feature_vector(row):
    return [row[name] for name in FEATURE_NAMES]


def predict_features(home, away, final_state, home_rest=None, away_rest=None):
    """
    Builds the FEATURE_NAMES vector for a not-yet-played game from saved
    end-of-history state. rest args are optional: pass the real days of rest
    for each side if known (from the schedule), otherwise both default to a
    neutral DEFAULT_REST_DAYS with no back-to-back.
    """
    elo = final_state["elo"]
    form = final_state["form"]
    net = final_state["net_rating"]

    elo_diff = elo.get(home, STARTING_ELO) - elo.get(away, STARTING_ELO)

    def avg(d, team, default):
        v = d.get(team, [])
        return (sum(v) / len(v)) if v else default

    form_diff = avg(form, home, FORM_DEFAULT_WINPCT) - avg(form, away, FORM_DEFAULT_WINPCT)
    net_rating_diff = avg(net, home, NET_RATING_DEFAULT) - avg(net, away, NET_RATING_DEFAULT)

    h_rest = DEFAULT_REST_DAYS if home_rest is None else min(home_rest, MAX_REST_DAYS)
    a_rest = DEFAULT_REST_DAYS if away_rest is None else min(away_rest, MAX_REST_DAYS)
    rest_diff = float(h_rest - a_rest)
    b2b_diff = float((1 if a_rest <= 1 else 0) - (1 if h_rest <= 1 else 0))

    return [elo_diff, form_diff, net_rating_diff, rest_diff, b2b_diff, elo_diff * form_diff]
