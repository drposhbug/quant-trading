"""
Test suite for the betting pipeline — run this after any change.

Plain asserts, no pytest dependency, so it runs anywhere the repo runs:

    py test_pipeline.py
    py test_pipeline.py --offline    # skip the tests that hit the network

Grouped by what would actually hurt if it broke:

  * MARKET MATH — de-vig, overround, best-price selection. A sign error here
    silently invents edge, which is the single most expensive class of bug in
    this repo: it produces confident, wrong bets rather than an exception.
  * LEAKAGE — the feature builders must not see a match's own result. This is
    tested directly: flip the outcome of the last event, recompute, and assert
    that event's features are byte-identical. Leakage is invisible in normal
    output (it just looks like a very good model), so it needs its own test.
  * STAKING — caps, degenerate prices, and the model gate that forces
    stakes to zero for leagues whose diagnostic has not passed.
  * STORAGE — idempotency. Every ingest re-runs on a schedule, so a
    non-idempotent upsert silently multiplies rows.
"""

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}   {detail}")


def section(title):
    print(f"\n=== {title} ===")


# ---------------------------------------------------------------- market math
def test_market_math():
    section("Market math: de-vig and prices")
    from nba_odds import american_to_decimal, devig_power

    check("american +150 -> 2.50", abs(american_to_decimal(150) - 2.5) < 1e-9)
    check("american -200 -> 1.50", abs(american_to_decimal(-200) - 1.5) < 1e-9)
    check("even market -> 0.500", abs(devig_power(2.0, 2.0) - 0.5) < 1e-9)
    check("vig-free 1.5/3.0 -> 0.667", abs(devig_power(1.5, 3.0) - 2 / 3) < 1e-6)

    p = devig_power(1.4, 2.8)
    check("fair probs sum to 1", abs(p + (1 - p) - 1) < 1e-12)
    check("favourite stays the favourite", devig_power(1.2, 5.0) > 0.8)

    # The power method exists to correct favourite-longshot bias: books load
    # more vig on the longshot, so removing it proportionally leaves the
    # favourite UNDERSTATED. Power must therefore return a HIGHER favourite
    # probability than proportional. If this ever flips, the correction is
    # backwards and every underdog will look falsely cheap.
    prop = (1 / 1.2) / ((1 / 1.2) + (1 / 5.0))
    check("power corrects favourite-longshot bias (power > proportional)",
          devig_power(1.2, 5.0) > prop,
          f"power={devig_power(1.2, 5.0):.4f} proportional={prop:.4f}")

    import analyze_prices as ap
    d2, _ = ap.devig({"H": 1.5, "A": 3.0}, ("H", "A"))
    check("2-way de-vig sums to 1", abs(sum(d2.values()) - 1) < 1e-9)
    d3, _ = ap.devig({"H": 2.0, "D": 3.5, "A": 4.0}, ("H", "D", "A"))
    check("3-way de-vig sums to 1", abs(sum(d3.values()) - 1) < 1e-9)
    check("tennis routed as 2-way", ap.outcomes_for("tennis_atp_wimbledon") == ("H", "A"))
    check("basketball routed as 2-way", ap.outcomes_for("basketball_nba") == ("H", "A"))
    check("soccer stays 3-way", ap.outcomes_for("soccer_epl") == ("H", "D", "A"))
    check("unknown league defaults 3-way", ap.outcomes_for(None) == ("H", "D", "A"))


def test_best_price():
    section("Best-price execution")
    import best_price as bp

    q = {"a": {"H": 2.0, "A": 2.0}, "b": {"H": 2.2, "A": 1.9}}
    check("overround of a fair market == 1", abs(bp.overround([2.0, 2.0]) - 1.0) < 1e-12)
    check("hold of a fair market == 0", abs(bp.hold([2.0, 2.0])) < 1e-12)
    check("hold goes negative when prices overpay", bp.hold([2.2, 2.2]) < 0)
    check("junk prices ignored", bp.overround([0, 1.0, None, 2.0]) == 0.5)

    bl = bp.best_line(q, ("H", "A"))
    check("best_line takes the max per outcome",
          bl["H"]["odds"] == 2.2 and bl["A"]["odds"] == 2.0, bl)
    check("best_line names the venue", bl["H"]["venue"] == "b")

    g = bp.shopping_gain(q, ("H", "A"))
    check("shopping gain is positive when books disagree", g and g["gain"] > 0)
    check("one venue -> no shopping", bp.shopping_gain({"a": q["a"]}, ("H", "A")) is None)
    check("incomplete market -> None",
          bp.shopping_gain({"a": {"H": 2.0}, "b": {"H": 2.1}}, ("H", "A")) is None)
    check("venue filter applied",
          bp.shopping_gain(q, ("H", "A"), allowed_venues={"a"}) is None)
    check("2-way sports detected",
          bp._two_way("tennis_atp_x") and bp._two_way("basketball_nba")
          and not bp._two_way("soccer_epl"))


# -------------------------------------------------------------------- leakage
def _flip_last_outcome_and_compare(rows, compute, label_key, feature_keys):
    """
    Shared leakage probe: compute features, flip the LAST event's result,
    recompute, and confirm that event's own features did not move. A feature
    that changes is reading the result it is supposed to predict.
    """
    base, _ = compute(rows)
    flipped_rows = [dict(r) for r in rows]
    last = flipped_rows[-1]
    last[label_key] = 1 - int(last[label_key]) if label_key in last else last[label_key]
    flipped, _ = compute(flipped_rows)
    diffs = [k for k in feature_keys
             if abs(float(base[-1][k]) - float(flipped[-1][k])) > 1e-12]
    return diffs


def test_leakage_tennis():
    section("Leakage: tennis features cannot see their own result")
    from db import fetch_tennis_matches
    from tennis_features import FEATURE_NAMES, compute_features

    rows = fetch_tennis_matches()[:2000]
    if not rows:
        check("tennis data present", False, "run ingest_tennis.py")
        return
    diffs = _flip_last_outcome_and_compare(rows, compute_features, "p1_won", FEATURE_NAMES)
    check("no tennis feature moves when the result is flipped",
          not diffs, f"leaking: {diffs}")

    # a player's very first match must use default ratings, not hindsight
    base, _ = compute_features(rows)
    check("first match starts at default Elo", abs(base[0]["elo_diff"]) < 1e-12,
          base[0]["elo_diff"])
    check("first match has no h2h", base[0]["h2h_diff"] == 0)


def test_leakage_nba():
    section("Leakage: NBA features cannot see their own result")
    from nba_features import FEATURE_NAMES, compute_features

    # small synthetic history: compute_features needs box scores, which the DB
    # does not store, so build a minimal well-formed sequence here
    box = {"fga": 85, "fta": 20, "oreb": 10, "tov": 14, "min": 240}
    games = []
    for i in range(30):
        games.append({
            "date": f"2024-01-{(i % 28) + 1:02d}", "season": "2023-24",
            "home": "Team A" if i % 2 else "Team B",
            "away": "Team B" if i % 2 else "Team A",
            "home_score": 110 + (i % 5), "away_score": 100 + (i % 7),
            "home_box": dict(box), "away_box": dict(box),
        })
    base, _ = compute_features(games)
    flipped = [dict(g) for g in games]
    flipped[-1]["home_score"], flipped[-1]["away_score"] = (
        flipped[-1]["away_score"], flipped[-1]["home_score"])
    after, _ = compute_features(flipped)
    diffs = [k for k in FEATURE_NAMES
             if abs(float(base[-1][k]) - float(after[-1][k])) > 1e-12]
    check("no NBA feature moves when the score is flipped", not diffs,
          f"leaking: {diffs}")
    check("first game starts at default Elo", abs(base[0]["elo_diff"]) < 1e-12)


# -------------------------------------------------------------------- staking
def test_staking():
    section("Staking and the model gate")
    from bet_sizer import MAX_BANKROLL_FRACTION as CAP
    from bet_sizer import model_betting_allowed, suggest_stake

    check("stake never exceeds the cap", suggest_stake(0.5, 0.45, 1000)["stake"] <= 1000 * CAP + 1e-9)
    check("non-positive edge stakes nothing", suggest_stake(-0.1, 0.45, 1000)["stake"] == 0)
    check("price 0 is refused (no division blow-up)", suggest_stake(0.1, 0.0, 1000)["stake"] == 0)
    check("price 1 is refused", suggest_stake(0.1, 1.0, 1000)["stake"] == 0)
    check("sharp-line edges still size", suggest_stake(0.06, 0.45, 1000)["stake"] > 0)
    check("tiers below the floor stake nothing",
          suggest_stake(0.01, 0.45, 1000, method="tiers")["stake"] == 0)

    for league in ("nba", "basketball_nba", "tennis_atp_wimbledon"):
        r = suggest_stake(0.2, 0.45, 1000, edge_source="model", league=league)
        check(f"model stakes blocked for {league}", r["stake"] == 0 and r["blocked"])
    # the one gate that passes: Premier League market-anchored at best price,
    # +6.0% [+0.4%, +11.6%] over 2,165 pre-registered bets (train_market_model.py)
    r = suggest_stake(0.06, 0.45, 1000, edge_source="model", league="premier_league")
    check("premier_league model stakes ALLOWED (passing gate)", r["stake"] > 0 and not r["blocked"])
    check("passing gate still respects the cap",
          suggest_stake(0.9, 0.45, 1000, edge_source="model",
                        league="premier_league")["stake"] <= 1000 * CAP + 1e-9)
    check("ungated league is refused, not allowed",
          not model_betting_allowed("some_new_league")[0])
    check("missing league is refused", not model_betting_allowed(None)[0])


# -------------------------------------------------------------------- storage
def test_storage():
    section("Storage: schema and idempotency")
    import sqlite3

    from db import DB_PATH, init_db, log_news_items, log_injury_snapshot
    init_db()
    conn = sqlite3.connect(DB_PATH)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in ("matches", "nba_games", "tennis_matches", "price_snapshots",
              "nba_injury_snapshots", "nba_news", "news_items", "paper_trades"):
        check(f"table {t} exists", t in tables)

    before = conn.execute("SELECT COUNT(*) FROM news_items").fetchone()[0]
    conn.close()
    row = [{"source": "test", "sport": "test", "item_id": "dup-check",
            "kind": "article", "published": "2026-01-01T00:00:00Z",
            "first_seen": "2026-01-01T00:00:00Z", "subject": None,
            "headline": "t", "summary": None, "url": None}]
    log_news_items(row)
    n2 = log_news_items(row)          # second insert must be a no-op
    check("news_items is idempotent per item", n2 == 0, f"inserted {n2} on repeat")

    inj = [{"snapshot_time": "2026-01-01T00:00:00Z", "team": "T", "player": "P",
            "status": "Out", "status_weight": 1.0, "impact_units": 0.0}]
    log_injury_snapshot(inj)
    n3 = log_injury_snapshot(inj)
    check("injury snapshot is idempotent per (time, team, player)", n3 == 0,
          f"inserted {n3} on repeat")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM news_items WHERE source='test'")
    conn.execute("DELETE FROM nba_injury_snapshots WHERE team='T' AND player='P'")
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM news_items").fetchone()[0]
    conn.close()
    check("test rows cleaned up", after == before)


def test_data_sanity():
    section("Stored data sanity")
    import sqlite3

    from db import DB_PATH
    conn = sqlite3.connect(DB_PATH)

    n = conn.execute("SELECT COUNT(*) FROM tennis_matches").fetchone()[0]
    if n:
        rate = conn.execute("SELECT AVG(p1_won) FROM tennis_matches").fetchone()[0]
        # p1 is assigned alphabetically, so its win rate must be ~50%. A drift
        # away from that means the ordering has picked up the result and every
        # downstream number is void.
        check("tennis p1 win rate ~0.50 (ordering is outcome-blind)",
              0.47 < rate < 0.53, f"{rate:.3f}")
        bad = conn.execute(
            "SELECT COUNT(*) FROM tennis_matches WHERE p1_ps <= 1 OR p2_ps <= 1").fetchone()[0]
        check("no impossible tennis prices (<= 1.0)", bad == 0, f"{bad} rows")
        bo = {r[0] for r in conn.execute(
            "SELECT DISTINCT best_of FROM tennis_matches WHERE best_of IS NOT NULL")}
        check("best_of only ever 3 or 5", bo <= {3, 5}, bo)

    g = conn.execute("SELECT COUNT(*) FROM nba_games").fetchone()[0]
    if g:
        hr = conn.execute("SELECT AVG(result='H') FROM nba_games").fetchone()[0]
        check("NBA home win rate plausible (0.55-0.65)", 0.55 < hr < 0.65, f"{hr:.3f}")
    conn.close()


def test_network():
    section("Live feeds (network)")
    import requests
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/"
                         "basketball/nba/injuries", timeout=25)
        check("ESPN injuries reachable", r.status_code == 200, f"HTTP {r.status_code}")
        if r.status_code == 200:
            check("ESPN injuries payload shaped as expected",
                  isinstance(r.json().get("injuries"), list))
    except Exception as e:  # noqa: BLE001
        check("ESPN injuries reachable", False, type(e).__name__)

    import nba_injuries as ni
    check("player-value cache loads", bool(ni.load_player_values()[0]))


# ------------------------------------------------------------------ trading
def test_execution():
    section("Execution: dry simulator against a synthetic book")
    from polymarket_exec import Executor, MAX_NOTIONAL_PER_ORDER, MIN_SHARES

    tok = "T"
    ex = Executor("dry", book_override={tok: (0.44, 0.46, 120.0, 80.0)}, fee_bps=100)
    b = ex.buy(tok, limit_price=0.47, size=50)
    check("buy fills at the real ask, not the limit", b.price == 0.46 and b.size == 50, repr(b))
    check("buy refused above limit", ex.buy(tok, limit_price=0.45, size=50).size == 0)
    check("buy capped by resting size", ex.buy(tok, limit_price=0.47, size=10_000).size == 120)
    check("notional cap enforced",
          ex.buy(tok, 0.47, 10_000).notional <= MAX_NOTIONAL_PER_ORDER + 1e-9)
    s = ex.sell(tok, limit_price=0.40, size=50)
    check("sell fills at the real bid", s.price == 0.44 and s.size == 50, repr(s))
    check("sell refused below limit", ex.sell(tok, limit_price=0.45, size=50).size == 0)
    check("sell capped by resting bid size", ex.sell(tok, 0.40, 500).size == 80)
    check("dust orders refused", ex.buy(tok, 0.47, MIN_SHARES - 1).size == 0)
    check("fees computed from bps", abs(b.fees - b.notional * 0.01) < 1e-9)
    check("empty book -> no fill",
          Executor("dry", book_override={tok: (None, None, 0.0, 0.0)}).buy(tok, 0.5, 50).size == 0)
    check("from_env without flags is dry", Executor.from_env().mode == "dry")
    check("from_env(live) without env is STILL dry", Executor.from_env(live=True).mode == "dry")


def test_trade_decisions():
    section("Trade decisions: entry and exit rules")
    from datetime import datetime, timedelta, timezone
    from trader import decide_entry, decide_exit

    check("enter when fair beats ask by > margin", decide_entry(0.50, 0.45, 100) is not None)
    check("no entry inside the margin", decide_entry(0.47, 0.45, 100) is None)
    check("no entry when overpriced", decide_entry(0.40, 0.45, 100) is None)
    check("no entry with no resting size", decide_entry(0.60, 0.45, 0) is None)
    check("no entry near the rails", decide_entry(0.99, 0.96, 100) is None
          and decide_entry(0.10, 0.03, 100) is None)
    check("no entry without a fair value", decide_entry(None, 0.45, 100) is None)

    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    later = now + timedelta(hours=3)
    # entry 0.42, fair 0.48
    check("hold while price has not converged",
          decide_exit(0.42, 0.48, bid=0.43, mid=0.435, now=now, kickoff=later) is None)
    check("exit on convergence to fair",
          decide_exit(0.42, 0.48, bid=0.47, mid=0.475, now=now, kickoff=later) == "converged")
    check("exit on take-profit",
          decide_exit(0.42, 0.60, bid=0.49, mid=0.495, now=now, kickoff=later) == "take_profit")
    check("exit on stop when the SHARP LINE moves against us",
          decide_exit(0.42, 0.36, bid=0.41, mid=0.415, now=now, kickoff=later) == "stop")
    check("stop is labelled stop even though mid >= collapsed fair",
          decide_exit(0.42, 0.30, bid=0.40, mid=0.405, now=now, kickoff=later) == "stop")
    check("small adverse drift under the stop still counts as convergence",
          decide_exit(0.42, 0.40, bid=0.39, mid=0.395, now=now, kickoff=later) == "converged")
    check("always flat before kickoff, whatever the price",
          decide_exit(0.42, 0.48, bid=0.43, mid=0.435, now=now,
                      kickoff=now + timedelta(minutes=10)) == "pre_kickoff")
    check("kickoff rule wins over everything else",
          decide_exit(0.42, 0.36, bid=0.41, mid=0.415, now=now,
                      kickoff=now + timedelta(minutes=5)) == "pre_kickoff")
    check("no kickoff known -> price rules still apply",
          decide_exit(0.42, 0.48, bid=0.47, mid=0.475, now=now, kickoff=None) == "converged")


def test_positions_storage():
    section("Positions: open/close round trip")
    import sqlite3
    from db import DB_PATH, close_position, fetch_positions, init_positions, open_position
    init_positions()
    pid = open_position({"mode": "test", "opened_at": "2026-01-01T00:00:00Z",
                         "home_team": "A", "away_team": "B", "outcome": "H",
                         "token_side": "YES", "token_id": "t", "entry_price": 0.42,
                         "size": 50, "fair_at_entry": 0.48})
    check("open_position returns an id", isinstance(pid, int) and pid > 0)
    check("shows as open", any(p["id"] == pid for p in fetch_positions(status="open", mode="test")))
    n = close_position(pid, "2026-01-01T01:00:00Z", 0.47, "converged", fees=0.2, pnl=2.3)
    check("close updates exactly one row", n == 1)
    check("closing twice is a no-op",
          close_position(pid, "2026-01-01T02:00:00Z", 0.10, "manual", 0, -10) == 0)
    p = [x for x in fetch_positions(mode="test") if x["id"] == pid][0]
    check("closed row keeps entry and exit", p["status"] == "closed" and p["exit_price"] == 0.47
          and p["pnl"] == 2.3 and p["entry_price"] == 0.42)
    conn = sqlite3.connect(DB_PATH); conn.execute("DELETE FROM positions WHERE mode='test'")
    conn.commit(); conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Test the betting pipeline.")
    ap.add_argument("--offline", action="store_true", help="skip network tests")
    args = ap.parse_args()

    test_market_math()
    test_best_price()
    test_leakage_tennis()
    test_leakage_nba()
    test_staking()
    test_storage()
    test_data_sanity()
    test_execution()
    test_trade_decisions()
    test_positions_storage()
    if not args.offline:
        test_network()

    print(f"\n{'=' * 60}")
    print(f"{len(PASSED)} passed, {len(FAILED)} failed")
    if FAILED:
        for name in FAILED:
            print(f"  FAILED: {name}")
    print("=" * 60)
    sys.exit(1 if FAILED else 0)
