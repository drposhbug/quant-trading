"""
News latency harness — decide whether a paid feed is worth buying, with data
================================================================================
The diagnostics established that the models' deficit against the closing line
is INFORMATION, not architecture: injuries, lineups, load management. The only
way to profit from information you don't have is to get it before the price
moves — so the question stops being "how good is my model" and becomes "how
fast do I hear things, and is that fast enough to matter".

That question has a number attached, and this measures it:

    latency = published - first_seen

`published` is the source's own timestamp; `first_seen` is when this repo first
observed the item. Their difference is the free feed's real lag. You cannot
sensibly decide whether to pay for a low-latency wire (X/Twitter API, a paid
injury feed) until you know what the free one already gives you, because the
value of paying is the DIFFERENCE between the two, not the speed of the paid
one in isolation.

WHAT MAKES THIS MEASUREMENT VALID: first_seen is written once and never
updated (INSERT OR IGNORE on (source, item_id)). A poller that overwrote it
would measure only the time since its last run and always look fast. That is
also why polling frequency matters here: an item can never be seen sooner than
your polling interval, so running this every 6 hours guarantees a ~3 hour
apparent latency that tells you nothing about the feed. Run it at the cadence
you would actually trade at.

WHAT THIS CANNOT TELL YOU, and where the honest limit is: the offseason has no
breaking news, so a measurement taken now mostly reports how old stale items
are. The latency figure is only meaningful once collected across active game
days, and the report labels its own sample size for that reason.

Sources are all free and key-less. An X/Twitter source would slot in as one
more entry in SOURCES — see the cost note in the README section of this
docstring before paying for one.

WHETHER A PAID FEED PAYS FOR ITSELF:

    monthly cost / (edge per bet x average stake) = bets per month needed

At a $200/month feed and $200 average stake, a 2% edge needs 500 bets a month
to break even on the subscription alone; a 5% edge needs 200. Judge a paid feed
against that arithmetic and against the measured free-feed latency, not against
how fast it sounds.

Usage:
    py news_watch.py                  # one poll, all sources
    py news_watch.py --sport nba      # one sport
    py news_watch.py --report         # latency stats from what has been collected
    py news_watch.py --loop 5 --for 60   # poll every 5 min for an hour
"""

import argparse
import statistics as st
import sys
import time
from datetime import datetime, timezone

import requests

from db import get_connection, init_news_items, log_news_items

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ESPN = "https://site.api.espn.com/apis/site/v2/sports"
TIMEOUT = 25

# sport key -> ESPN path. All free, no key. Add a sport here and it is polled.
SPORTS = {
    "nba": "basketball/nba",
    "nfl": "football/nfl",
    "mlb": "baseball/mlb",
    "nhl": "hockey/nhl",
    "wnba": "basketball/wnba",
    "ncaab": "basketball/mens-college-basketball",
}
# Sports whose ESPN feed also exposes an injuries endpoint.
INJURY_SPORTS = {"nba", "nfl", "mlb", "nhl", "wnba"}


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _hours_between(published, first_seen):
    try:
        a = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(first_seen).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if a.tzinfo is None:
        a = a.replace(tzinfo=timezone.utc)
    if b.tzinfo is None:
        b = b.replace(tzinfo=timezone.utc)
    return (b - a).total_seconds() / 3600.0


def fetch_news(sport):
    path = SPORTS[sport]
    r = requests.get(f"{ESPN}/{path}/news", params={"limit": 50}, timeout=TIMEOUT)
    if r.status_code != 200:
        return []
    seen = _utc_now()
    out = []
    for a in r.json().get("articles", []):
        links = a.get("links") or {}
        url = ((links.get("web") or {}).get("href")
               or ((links.get("api") or {}).get("news") or {}).get("href"))
        out.append({
            "source": "espn_news", "sport": sport,
            "item_id": str(a.get("id") or a.get("headline")),
            "kind": "article", "published": a.get("published"), "first_seen": seen,
            "subject": None, "headline": a.get("headline"),
            "summary": a.get("description"), "url": url,
        })
    return out


def fetch_injuries(sport):
    path = SPORTS[sport]
    r = requests.get(f"{ESPN}/{path}/injuries", timeout=TIMEOUT)
    if r.status_code != 200:
        return []
    seen = _utc_now()
    out = []
    for team in r.json().get("injuries", []):
        for item in team.get("injuries", []):
            athlete = item.get("athlete") or {}
            name = athlete.get("displayName")
            if not name:
                continue
            # ESPN reuses ids across updates; pair it with the status+date so a
            # CHANGED designation counts as a new item rather than being ignored
            # as a duplicate -- the status change is the tradeable event.
            iid = f"{item.get('id')}|{item.get('status')}|{str(item.get('date'))[:16]}"
            out.append({
                "source": "espn_injuries", "sport": sport, "item_id": iid,
                "kind": "injury", "published": item.get("date"), "first_seen": seen,
                "subject": f"{name} ({team.get('displayName')})",
                "headline": f"{name}: {item.get('status')}",
                "summary": item.get("shortComment"), "url": None,
            })
    return out


def poll(sports=None, quiet=False):
    sports = sports or list(SPORTS)
    init_news_items()
    total_new, total_seen = 0, 0
    for sport in sports:
        rows = fetch_news(sport)
        if sport in INJURY_SPORTS:
            rows += fetch_injuries(sport)
        if not rows:
            continue
        n = log_news_items(rows)
        total_new += n
        total_seen += len(rows)
        if not quiet and n:
            print(f"  {sport:<7} {n:>3} new / {len(rows):>3} seen")
    if not quiet:
        print(f"[{_utc_now()}] {total_new} new items ({total_seen} observed)")
    return total_new


def report():
    conn = get_connection()
    rows = conn.execute(
        "SELECT source, sport, kind, published, first_seen, headline "
        "FROM news_items WHERE published IS NOT NULL").fetchall()
    span = conn.execute(
        "SELECT MIN(first_seen), MAX(first_seen), COUNT(DISTINCT first_seen) "
        "FROM news_items").fetchone()
    conn.close()
    if not rows:
        print("No items collected yet -- run `py news_watch.py` a few times first.")
        return

    print(f"=== Feed latency (published -> first observed) ===")
    print(f"collection window: {span[0]} .. {span[1]}  ({span[2]} distinct polls)")
    if span[2] < 10:
        print("!! Too few polls to trust these numbers. An item cannot be seen sooner\n"
              "   than your polling interval, so a sparse schedule manufactures lag that\n"
              "   belongs to the poller, not the feed. Run --loop over active game days.")

    by_source = {}
    for source, sport, kind, published, first_seen, _ in rows:
        lag = _hours_between(published, first_seen)
        if lag is None or lag < 0:
            continue
        by_source.setdefault((source, sport), []).append(lag)

    print(f"\n{'source':>16} {'sport':>7} {'n':>5} {'median':>9} {'p10':>9} {'min':>9}")
    for (source, sport), lags in sorted(by_source.items()):
        lags.sort()
        p10 = lags[max(0, int(len(lags) * 0.10) - 1)]
        print(f"{source:>16} {sport:>7} {len(lags):>5} {st.median(lags):>8.1f}h "
              f"{p10:>8.1f}h {min(lags):>8.1f}h")

    fresh = sorted(l for lags in by_source.values() for l in lags)
    if fresh:
        print(f"\nFastest 10% of all items arrived within {fresh[max(0, int(len(fresh)*0.1)-1)]:.1f}h "
              f"of publication.")
        print("That p10 is the number to compare a paid feed against: a wire that beats\n"
              "the free one by less than the time it takes you to act is worth nothing.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Poll free news/injury feeds and measure their latency.")
    ap.add_argument("--sport", choices=sorted(SPORTS), help="only this sport")
    ap.add_argument("--report", action="store_true", help="latency stats, no polling")
    ap.add_argument("--loop", type=int, metavar="MIN",
                    help="poll every MIN minutes (needed for a real latency measurement)")
    ap.add_argument("--for", dest="duration", type=int, metavar="MIN",
                    help="with --loop, stop after this many minutes")
    args = ap.parse_args()

    if args.report:
        report()
        raise SystemExit(0)

    sports = [args.sport] if args.sport else None
    if not args.loop:
        poll(sports)
        raise SystemExit(0)

    deadline = time.time() + (args.duration or 0) * 60 if args.duration else None
    print(f"polling every {args.loop} min"
          f"{f' for {args.duration} min' if args.duration else ' (ctrl-C to stop)'}")
    try:
        while True:
            poll(sports)
            if deadline and time.time() >= deadline:
                break
            time.sleep(args.loop * 60)
    except KeyboardInterrupt:
        print("\nstopped")
    report()
