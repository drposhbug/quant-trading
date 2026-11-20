"""Offline tests for sport_favorites.py (fakes for Gamma + CLOB, temp DB). Run: py test_sport_favorites.py"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone

import db
import sport_favorites as sf

NOW = datetime.now(timezone.utc)


def _gst(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S+00")


def soccer_event(slug, home_p, start, draw_p=0.10, away_p=0.05):
    def mk(mid, title, p):
        return {"id": mid, "sportsMarketType": "moneyline", "groupItemTitle": title, "closed": False,
                "outcomes": '["Yes", "No"]', "outcomePrices": json.dumps([str(p), str(1 - p)]),
                "clobTokenIds": json.dumps([f"{mid}-Y", f"{mid}-N"]), "gameStartTime": start}
    return {"slug": slug, "title": "Home vs. Away", "markets": [
        mk(f"{slug}-h", "Home FC", home_p), mk(f"{slug}-d", "Draw (Home FC vs. Away FC)", draw_p),
        mk(f"{slug}-a", "Away FC", away_p)]}


def nba_event(slug, fav_p, start):
    return {"slug": slug, "title": "Dogs vs. Favs", "markets": [
        {"id": f"{slug}-ml", "sportsMarketType": "moneyline", "groupItemTitle": None, "closed": False,
         "outcomes": '["Dogs", "Favs"]', "outcomePrices": json.dumps([str(1 - fav_p), str(fav_p)]),
         "clobTokenIds": json.dumps([f"{slug}-0", f"{slug}-1"]), "gameStartTime": start},
        {"id": f"{slug}-sp", "sportsMarketType": "spreads", "groupItemTitle": "Spread -9.5", "closed": False,
         "outcomes": '["Favs", "Dogs"]', "outcomePrices": '["0.96", "0.04"]',
         "clobTokenIds": json.dumps([f"{slug}-s0", f"{slug}-s1"]), "gameStartTime": start}]}


class Resp:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


def main():
    tmp = tempfile.mkdtemp()
    db.DB_PATH = os.path.join(tmp, "t.sqlite3")
    later = _gst(NOW + timedelta(hours=5))
    soon = _gst(NOW + timedelta(minutes=10))
    events = [
        soccer_event("epl-hom-awa-2026-11-21", 0.85, later),     # enters Home FC YES
        soccer_event("epl-low-awa-2026-11-21", 0.75, later),     # 0.75: below the frozen 0.80 floor
        soccer_event("epl-soo-awa-2026-11-21", 0.85, soon),      # < 30 min to start
        soccer_event("epl-unk-awa-2026-11-21", 0.85, None),      # unknown start
        soccer_event("isp-hom-awa-2026-11-21", 0.85, later),     # league not in the frozen list
        soccer_event("lal-gap-awa-2026-11-21", 0.85, later),     # gaping book
        soccer_event("bun-drw-awa-2026-11-21", 0.05, later, draw_p=0.85),  # draw priced high: never bought
        nba_event("nba-dog-fav-2026-11-21", 0.90, later),        # enters Favs
        nba_event("nba-mid-fav-2026-11-21", 0.80, later),        # 0.80: below NBA floor
        nba_event("nhl-dog-fav-2026-11-21", 0.93, later),        # exploratory group: enters
        nba_event("nfl-dog-fav-2026-11-21", 0.98, later),        # 0.98: above the 0.97 cap
    ]
    books = {"lal-gap-awa-2026-11-21-h-Y": (0.70, 0.86, 100, 100)}
    settled_events = {}

    def fake_get(url, params=None, **kw):
        if "slug" in (params or {}):
            return Resp(settled_events.get(params["slug"], []))
        return Resp(events if params.get("offset", 0) == 0 else [])

    def fake_book(token):
        if token in books:
            return books[token]
        p = next(float(json.loads(m["outcomePrices"])[i]) for e in events for m in e["markets"]
                 for i, t in enumerate(json.loads(m["clobTokenIds"])) if t == token)
        return (round(p - 0.01, 2), round(p + 0.01, 2), 100, 100)

    sf.requests.get = fake_get
    sf.public_book = fake_book

    # sanity on what the generic discovery filter keeps
    assert {e["slug"] for e in sf.game_events(NOW)} == {e["slug"] for e in events} - {"isp-hom-awa-2026-11-21"}

    sf.log_entries(quiet=True)
    conn = db.get_connection()
    rows = conn.execute("SELECT tour, league, player, token_id, entry_ask FROM sport_fav_trades ORDER BY id").fetchall()
    assert rows == [("soccer", "epl", "Home FC", "epl-hom-awa-2026-11-21-h-Y", 0.86),
                    ("nba", "nba", "Favs", "nba-dog-fav-2026-11-21-1", 0.91),
                    ("other", "nhl", "Favs", "nhl-dog-fav-2026-11-21-1", 0.94)], rows
    conn.close()

    # idempotent: a second pass enters nothing new
    sf.log_entries(quiet=True)
    conn = db.get_connection()
    assert conn.execute("SELECT COUNT(*) FROM sport_fav_trades").fetchone()[0] == 3
    conn.close()

    # settlement: soccer favourite wins, NBA favourite loses
    s = soccer_event("epl-hom-awa-2026-11-21", 1.0, later)
    s["markets"][0]["closed"] = True
    n = nba_event("nba-dog-fav-2026-11-21", 0.0, later)  # Favs resolved 0
    n["markets"][0]["closed"] = True
    settled_events.update({s["slug"]: [s], n["slug"]: [n]})
    sf.settle(quiet=True)
    conn = db.get_connection()
    res = dict(conn.execute("SELECT league, pnl_per_dollar FROM sport_fav_trades").fetchall())
    st = dict(conn.execute("SELECT league, status FROM sport_fav_trades").fetchall())
    conn.close()
    fee = 0.05 * 0.86 * 0.14
    assert st == {"epl": "won", "nba": "lost", "nhl": "open"}, st
    assert abs(res["epl"] - ((1 - 0.86) / 0.86 - fee / 0.86)) < 1e-9
    assert abs(res["nba"] - (-1 - 0.05 * 0.91 * 0.09 / 0.91)) < 1e-9

    # pass bar
    assert sf.group_stats([0.05] * 299 + [0.06])[-1] is True
    assert sf.group_stats([0.05] * 299)[-1] is False                     # n < 300
    assert sf.group_stats([-0.05] * 150 + [0.2] * 150)[-1] is False      # first half negative
    sf.report()
    print("test_sport_favorites: all passed")


if __name__ == "__main__":
    main()
