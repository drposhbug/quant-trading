"""Offline tests for any_favorites.py (fake Gamma + CLOB, temp DB). Run: py test_any_favorites.py"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone

import db
import any_favorites as af

NOW = datetime.now(timezone.utc)


def mk(mid, p_yes, days=14, vol=50_000, tags=("politics",), fee_type="politics_fees", rate=0.04,
       source="https://official.example.gov", desc="Resolves per the official results.", q=None):
    return {"id": mid, "slug": mid, "question": q or f"Will {mid} happen?", "closed": False,
            "endDate": (NOW + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"), "volumeNum": vol,
            "outcomes": '["Yes", "No"]', "outcomePrices": json.dumps([str(p_yes), str(round(1 - p_yes, 3))]),
            "clobTokenIds": json.dumps([f"{mid}-Y", f"{mid}-N"]), "tags": [{"slug": t} for t in tags],
            "feeType": fee_type, "feeSchedule": {"rate": rate} if rate is not None else None,
            "resolutionSource": source, "description": desc}


class Resp:
    def __init__(self, data, code=200):
        self.data, self.status_code = data, code

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


def main():
    db.DB_PATH = os.path.join(tempfile.mkdtemp(), "t.sqlite3")
    markets = [
        mk("yes-fav", 0.93),                                   # enters YES
        mk("no-fav", 0.05),                                    # enters NO (priced 0.95)
        mk("geo", 0.92, tags=("geopolitics",), rate=None),     # enters, fee 0 by category fallback
        mk("too-soon", 0.93, days=3),                          # < 7 days left
        mk("too-far", 0.93, days=45),                          # > 30 days left
        mk("thin", 0.93, vol=5_000),                           # volume < $10k
        mk("sport", 0.93, tags=("sports",), fee_type="sports_fees_v3"),
        mk("btc", 0.93, tags=("crypto",), fee_type="crypto_fees_v2"),
        mk("stock", 0.93, tags=("finance",), fee_type="finance_prices_fees", q="Will NVDA close above $200?"),
        mk("subj", 0.93, source="", desc="The primary resolution source for this market will be a consensus of "
                                         "credible reporting."),
        mk("nosrc", 0.93, source="", desc="Resolves Yes if it happens."),
        mk("wide", 0.93),                                      # spread 0.05 > 0.03
        mk("mid", 0.60),                                       # no side in range
    ]
    books = {"wide-Y": (0.89, 0.94, 100, 100)}
    resolved = {}

    def fake_get(url, params=None, **kw):
        if "/markets/" in url:
            mid = url.rsplit("/", 1)[1]
            return Resp(resolved.get(mid, {"closed": False}))
        return Resp(markets if (params or {}).get("offset", 0) == 0 else [])

    def fake_book(token):
        if token in books:
            return books[token]
        m = next(m for m in markets if token in m["clobTokenIds"])
        p = float(json.loads(m["outcomePrices"])[0 if token.endswith("-Y") else 1])
        return (round(p - 0.01, 3), round(p + 0.01, 3), 100, 100)

    af.requests.get = fake_get
    af.public_book = fake_book

    af.log_entries(quiet=True)
    af.log_entries(quiet=True)  # idempotent
    conn = db.get_connection()
    rows = conn.execute("SELECT market_id, side, entry_ask, fee_rate, category FROM any_fav_trades ORDER BY id").fetchall()
    assert rows == [("yes-fav", "Yes", 0.94, 0.04, "politics"), ("no-fav", "No", 0.96, 0.04, "politics"),
                    ("geo", "Yes", 0.93, 0.0, "geopolitics")], rows
    skips = dict(conn.execute("SELECT market_id, reason FROM any_fav_skips").fetchall())
    assert skips == {"subj": "subjective wording", "nosrc": "no official source named"}, skips
    conn.close()

    # settlement: YES favourite wins; NO favourite loses (YES resolved 1); geo still unresolved
    resolved["yes-fav"] = {"closed": True, "outcomePrices": '["1", "0"]'}
    resolved["no-fav"] = {"closed": True, "outcomePrices": '["1", "0"]'}
    resolved["geo"] = {"closed": True, "outcomePrices": '["0.6", "0.4"]'}  # closed, not final: stays open
    af.settle(quiet=True)
    conn = db.get_connection()
    got = {r[0]: (r[1], r[2]) for r in conn.execute("SELECT market_id, status, pnl_per_dollar FROM any_fav_trades")}
    conn.close()
    assert got["geo"] == ("open", None)
    assert got["yes-fav"][0] == "won" and abs(got["yes-fav"][1] - (0.06 / 0.94 - 0.04 * 0.94 * 0.06 / 0.94)) < 1e-9
    assert got["no-fav"][0] == "lost" and abs(got["no-fav"][1] - (-1 - 0.04 * 0.96 * 0.04 / 0.96)) < 1e-9
    af.report()
    print("test_any_favorites: all passed")


if __name__ == "__main__":
    main()
