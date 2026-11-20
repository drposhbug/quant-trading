"""
Preflight — is this pipeline actually collecting anything?
================================================================================
Written because it wasn't. price_snapshots held 1,830 rows from two runs in a
single July afternoon and zero NBA rows, and the cause was invisible: there is
no .env, so ODDS_API_KEY is unset, so log_prices.py fetches nothing and the
daily job still exits quietly. Every downstream conclusion about Polymarket
divergence — the one edge in this repo that the diagnostics did not rule out —
depends on data that was never being written.

A collector that fails silently is worse than one that crashes, because it
looks like "no opportunities today" forever. This prints the state of every
input in one place: credentials, storage, collector freshness, the free feeds,
and which models are cleared to size a bet.

Exit code is 1 if anything is FAIL, so it can gate the daily job.

Usage:
    py check_setup.py
    py check_setup.py --quiet     # summary line only
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone

OK, WARN, FAIL = "OK", "WARN", "FAIL"
MARK = {OK: "[ OK ]", WARN: "[WARN]", FAIL: "[FAIL]"}

HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "sports_data.sqlite3")
ENV_FILE = os.path.join(HERE, ".env")

# key -> (what breaks without it, is it required for the core loop)
KEYS = {
    "ODDS_API_KEY": ("log_prices.py cannot fetch book odds -- the whole "
                     "Polymarket-vs-sharp-line scan goes dark", True),
    "XAI_API_KEY": ("external_factors_agent.py research is unavailable "
                    "(optional; --research only)", False),
    "GOOGLE_API_KEY": ("external_factors_agent.py cross-check is unavailable "
                       "(optional; --research only)", False),
    "POLYMARKET_PRIVATE_KEY": ("trader.py can only run DRY (simulated fills) -- "
                               "fine until paper results justify going live", False),
}

# table -> (what writes it, hours before the data is considered stale, time column)
COLLECTORS = {
    "price_snapshots": ("log_prices.py", 24, "snapshot_time"),
    "nba_injury_snapshots": ("nba_injuries.py --snapshot", 48, "snapshot_time"),
}

results = []


def record(status, label, detail=""):
    results.append((status, label, detail))
    return status


def _age_hours(iso):
    if not iso:
        return None
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - t).total_seconds() / 3600.0


def check_credentials():
    print("\n--- Credentials ---")
    if not os.path.exists(ENV_FILE):
        record(FAIL, ".env file", f"missing -- copy .env.example to .env and fill it in")
        print(f"{MARK[FAIL]} .env file missing at {ENV_FILE}")
        print("       cp .env.example .env   then paste your keys in")
    else:
        record(OK, ".env file", "present")
        print(f"{MARK[OK]} .env present")
        try:
            from dotenv import load_dotenv
            load_dotenv(ENV_FILE)
        except ImportError:
            print("       (python-dotenv not installed; relying on real env vars)")

    for key, (consequence, required) in KEYS.items():
        if os.getenv(key):
            record(OK, key, "set")
            print(f"{MARK[OK]} {key} set")
        else:
            status = FAIL if required else WARN
            record(status, key, consequence)
            print(f"{MARK[status]} {key} missing -- {consequence}")


def check_storage():
    print("\n--- Storage ---")
    if not os.path.exists(DB_FILE):
        record(FAIL, "database", "sports_data.sqlite3 missing -- run db.init_db()")
        print(f"{MARK[FAIL]} sports_data.sqlite3 missing")
        return
    conn = sqlite3.connect(DB_FILE)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    expected = ["matches", "nba_games", "tennis_matches", "price_snapshots",
                "nba_injury_snapshots", "nba_news", "news_items", "paper_trades",
                "positions"]
    for t in expected:
        if t not in tables:
            record(WARN, f"table {t}", "missing -- its ingest has never run")
            print(f"{MARK[WARN]} {t:<22} missing")
            continue
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        status = OK if n else WARN
        record(status, f"table {t}", f"{n} rows")
        print(f"{MARK[status]} {t:<22} {n:>8,} rows")
    conn.close()


def check_collectors():
    print("\n--- Collector freshness ---")
    if not os.path.exists(DB_FILE):
        return
    conn = sqlite3.connect(DB_FILE)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    for table, (writer, max_age, col) in COLLECTORS.items():
        if table not in tables:
            record(WARN, table, f"no table -- {writer} has never run")
            print(f"{MARK[WARN]} {table:<22} never run ({writer})")
            continue
        last = conn.execute(f"SELECT MAX({col}) FROM {table}").fetchone()[0]
        age = _age_hours(last)
        if age is None:
            record(FAIL, table, f"empty -- {writer} is not writing")
            print(f"{MARK[FAIL]} {table:<22} empty -- {writer} is not writing")
        elif age > max_age:
            record(FAIL, table, f"last write {age:.0f}h ago (stale > {max_age}h)")
            print(f"{MARK[FAIL]} {table:<22} last write {age:>6.0f}h ago "
                  f"-- stale, expected every {max_age}h ({writer})")
        else:
            record(OK, table, f"last write {age:.1f}h ago")
            print(f"{MARK[OK]} {table:<22} last write {age:>6.1f}h ago")
    conn.close()


def check_free_feeds():
    """The feeds that need no key. If these fail it is the network, not config."""
    print("\n--- Free data sources ---")
    import requests
    feeds = {
        "ESPN NBA injuries": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries",
        "ESPN NBA news": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news",
    }
    for name, url in feeds.items():
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                record(OK, name, "reachable")
                print(f"{MARK[OK]} {name:<22} reachable")
            else:
                record(WARN, name, f"HTTP {r.status_code}")
                print(f"{MARK[WARN]} {name:<22} HTTP {r.status_code}")
        except Exception as e:  # noqa: BLE001 -- a probe; any failure is just "down"
            record(WARN, name, type(e).__name__)
            print(f"{MARK[WARN]} {name:<22} {type(e).__name__}")


def check_odds_quota():
    key = os.getenv("ODDS_API_KEY")
    if not key:
        return
    print("\n--- Odds API quota ---")
    import requests
    try:
        # /v4/sports does not count against the quota
        r = requests.get("https://api.the-odds-api.com/v4/sports",
                         params={"apiKey": key}, timeout=20)
        if r.status_code != 200:
            record(FAIL, "Odds API", f"HTTP {r.status_code} -- key rejected?")
            print(f"{MARK[FAIL]} key rejected (HTTP {r.status_code})")
            return
        left = r.headers.get("x-requests-remaining")
        used = r.headers.get("x-requests-used")
        status = OK if (left is None or float(left) > 20) else WARN
        record(status, "Odds API", f"{left} requests remaining")
        print(f"{MARK[status]} key valid -- {left} remaining, {used} used")
    except Exception as e:  # noqa: BLE001
        record(WARN, "Odds API", type(e).__name__)
        print(f"{MARK[WARN]} could not reach the Odds API ({type(e).__name__})")


def check_model_gates():
    """Which models are cleared to size a bet. All failing is the expected state."""
    print("\n--- Model gates (bet_sizer) ---")
    from bet_sizer import MODEL_GATE
    for league, gate in MODEL_GATE.items():
        mark = MARK[OK] if gate["passed"] else MARK[WARN]
        state = "cleared to size" if gate["passed"] else "stakes forced to 0"
        print(f"{mark} {league:<18} {state:<20} {gate['note']}")
    print("       Model stakes are refused by design until a diagnostic passes;")
    print("       sharp-line (Polymarket divergence) sizing is unaffected.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Check that the data pipeline is actually running.")
    ap.add_argument("--quiet", action="store_true", help="summary line only")
    args = ap.parse_args()

    if not args.quiet:
        print("=" * 70)
        print("PREFLIGHT -- can this pipeline collect and act on data right now?")
        print("=" * 70)

    check_credentials()
    check_storage()
    check_collectors()
    check_free_feeds()
    check_odds_quota()
    if not args.quiet:
        check_model_gates()

    fails = [r for r in results if r[0] == FAIL]
    warns = [r for r in results if r[0] == WARN]
    print("\n" + "=" * 70)
    print(f"{len(fails)} FAIL, {len(warns)} WARN, "
          f"{len([r for r in results if r[0] == OK])} OK")
    if fails:
        print("\nBlocking problems, in the order they break things:")
        for _, label, detail in fails:
            print(f"  - {label}: {detail}")
    print("=" * 70)
    sys.exit(1 if fails else 0)
