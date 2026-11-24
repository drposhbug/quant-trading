"""Point-in-time company announcements: SEC Form 8-K and 8-K/A filings.

Source: https://data.sec.gov/submissions/CIK##########.json (free, no key).
  filings.recent  - parallel arrays for the latest ~1000 filings of the company
  filings.files   - older pages, fetched from https://data.sec.gov/submissions/<name>

Output: lab/filings_8k.csv, one row per 8-K or 8-K/A filed since 2016-01-01 by a
company in the stock list (lab/fundamentals.csv ticker/cik pairs):
  ticker, cik (the CIK that filed it), accession, form,
  accepted_ny  - the second the SEC accepted the filing, New York local time (ISO)
  filed        - the SEC filing date (filings accepted after 17:30 get the next day)
  after_close  - 1 if accepted at/after 16:00 New York time, or on a weekend or an
                 NYSE holiday (act on it the next session), else 0
  items        - item codes joined by ';', as the SEC lists them (9.01 = exhibits only)

acceptanceDateTime is real UTC (the 'Z' is honest): Apple's results releases at
16:30 New York time show as 20:30Z in summer and 21:30Z in winter.

update(): with no CSV, a full build (main file plus every older page that reaches
2016). With a CSV, the daily path: one request per company (the main file only),
new 8-Ks merged in; a company new to the list, or with a new CIK, gets a full fetch.
Raw JSON is cached under data/filings/ (git-ignored) but the daily path does not
need the cache.
"""
from __future__ import annotations

import datetime as dt
import gzip
import json
import os
import time

import numpy as np
import pandas as pd
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "lab", "filings_8k.csv")
LIST = os.path.join(ROOT, "lab", "fundamentals.csv")
CACHE = os.path.join(ROOT, "data", "filings")

UA = {"User-Agent": "Mozilla/5.0 (research script)", "Accept-Encoding": "gzip, deflate"}
MAIN_URL = "https://data.sec.gov/submissions/CIK{:010d}.json"
PAGE_URL = "https://data.sec.gov/submissions/{}"
MIN_GAP = 0.27            # seconds between requests (under ~4 a second)
START = "2016-01-01"
FORMS = ("8-K", "8-K/A")
NY = "America/New_York"

COLUMNS = ["ticker", "cik", "accession", "form", "accepted_ny", "filed", "after_close", "items"]

# As in fundamentals_data.py: companies whose history sits partly under an older CIK
# (a new holding company or redomicile). A predecessor's 8-Ks are kept only up to the
# successor's first 8-K (afterwards the old CIK is a subsidiary filing its own news).
# Each was checked against the SEC: name, and 8-Ks ending as the successor's begin.
PREDECESSORS = {
    "XOM": [34088],                          # ExxonMobil Holdings Corp (2115436) since mid-2026
    "GOOG": [1288776], "GOOGL": [1288776],   # Google Inc. before Alphabet (Oct 2015)
    "DIS": [1001039],                        # TWDC Enterprises 18 (old Disney) to 2019-03
    "BLK": [1364742],                        # BlackRock Finance (old BlackRock) to 2024-10
    "CI": [701221],                          # Cigna Holding Co (old Cigna) to 2018-12
    "AVGO": [1649338, 1441634],              # Broadcom Pte / Avago to 2018-04
    "APA": [6769],                           # Apache Corp before APA Corp (2021-03)
    "MRVL": [1058057],                       # Marvell Technology Group (Bermuda) to 2021-04
    "BG": [1144519],                         # Bunge Ltd to 2023-11
    "TPL": [97517],                          # Texas Pacific Land Trust to 2021-01
    "APO": [1411494],                        # Apollo Asset Management (old Apollo) to 2022
    "STE": [1624899],                        # STERIS Ltd (UK plc) to 2019-03
    "LIN": [884905],                         # Praxair (now 'Linde Inc') to 2018-10
}


# --------------------------------------------------------------------- fetching
_last = [0.0]
_count = [0]


def _get(url: str, tries: int = 6) -> requests.Response:
    """GET with a polite rate limit and exponential backoff; stops if the SEC refuses."""
    delay = 2.0
    for attempt in range(tries):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        _count[0] += 1
        try:
            r = requests.get(url, headers=UA, timeout=60)
        except requests.RequestException:
            if attempt == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code in (200, 404):
            return r
        if r.status_code == 403 and attempt >= 1:
            raise RuntimeError(f"SEC refused {url}: HTTP 403: {r.text[:300]!r}")
        time.sleep(delay)
        delay *= 2
    r.raise_for_status()
    return r


def _save(obj: dict, name: str) -> None:
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name + ".gz")
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, path)


def fetch_main(cik: int) -> dict | None:
    r = _get(MAIN_URL.format(cik))
    if r.status_code == 404:
        return None
    d = r.json()
    _save(d, f"CIK{cik:010d}.json")
    return d


def fetch_page(name: str) -> dict | None:
    r = _get(PAGE_URL.format(name))
    if r.status_code == 404:
        return None
    d = r.json()
    _save(d, name)
    return d


# -------------------------------------------------------------- NYSE calendar
def _easter(y: int) -> dt.date:
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(y, month, day)


def _nth_weekday(y: int, month: int, weekday: int, n: int) -> dt.date:
    d = dt.date(y, month, 1)
    d += dt.timedelta((weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_weekday(y: int, month: int, weekday: int) -> dt.date:
    d = dt.date(y + (month == 12), month % 12 + 1, 1) - dt.timedelta(1)
    return d - dt.timedelta((d.weekday() - weekday) % 7)


def _observed(d: dt.date) -> dt.date:
    if d.weekday() == 5:
        return d - dt.timedelta(1)
    if d.weekday() == 6:
        return d + dt.timedelta(1)
    return d


def nyse_holidays(y0: int = 2015, y1: int | None = None) -> set[dt.date]:
    """Full-day NYSE closures (rules plus the special closures since 2016)."""
    y1 = y1 or dt.date.today().year + 1
    out = set()
    for y in range(y0, y1 + 1):
        ny = dt.date(y, 1, 1)
        if ny.weekday() != 5:                 # a Saturday New Year is not observed on Friday
            out.add(_observed(ny))
        out.add(_nth_weekday(y, 1, 0, 3))     # Martin Luther King Jr. Day
        out.add(_nth_weekday(y, 2, 0, 3))     # Presidents' Day
        out.add(_easter(y) - dt.timedelta(2))  # Good Friday
        out.add(_last_weekday(y, 5, 0))       # Memorial Day
        if y >= 2022:
            out.add(_observed(dt.date(y, 6, 19)))   # Juneteenth
        out.add(_observed(dt.date(y, 7, 4)))
        out.add(_nth_weekday(y, 9, 0, 1))     # Labor Day
        out.add(_nth_weekday(y, 11, 3, 4))    # Thanksgiving
        out.add(_observed(dt.date(y, 12, 25)))
    out |= {dt.date(2018, 12, 5), dt.date(2025, 1, 9)}   # national days of mourning
    return out


_HOL = nyse_holidays()


# ------------------------------------------------------------------- parsing
def _arrays_to_rows(block: dict, ticker: str, cik: int) -> list[dict]:
    forms = block.get("form", [])
    n = len(forms)
    items = block.get("items", [""] * n)
    rows = []
    for i in range(n):
        if forms[i] not in FORMS or block["filingDate"][i] < START:
            continue
        it = items[i] if i < len(items) and items[i] is not None else ""
        rows.append({"ticker": ticker, "cik": cik, "accession": block["accessionNumber"][i],
                     "form": forms[i], "accepted_utc": block["acceptanceDateTime"][i],
                     "filed": block["filingDate"][i],
                     "items": ";".join(x.strip() for x in str(it).split(",") if x.strip())})
    return rows


def _finish(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(rows)
    t = pd.to_datetime(df.pop("accepted_utc"), utc=True).dt.tz_convert(NY)
    d = t.dt.date
    closed = (t.dt.day_of_week >= 5) | d.isin(_HOL)
    late = t.dt.hour >= 16
    df["after_close"] = (closed | late).astype(int)
    df["accepted_ny"] = t.map(lambda x: x.isoformat())
    return df[COLUMNS]


def company_rows(ticker: str, cik: int, full: bool) -> tuple[list[dict], str | None]:
    """8-K rows of one company. full=True: its CIK and predecessors, every page.
    full=False (daily): the current CIK's main file only."""
    rows, err = [], None
    for c in [cik] + (PREDECESSORS.get(ticker, []) if full else []):
        try:
            d = fetch_main(c)
        except RuntimeError:
            raise
        except Exception as e:              # network failure for this company: report it
            err = f"CIK {c}: {e}"
            continue
        if d is None:
            err = f"CIK {c}: 404"
            continue
        rows += _arrays_to_rows(d["filings"]["recent"], ticker, c)
        if full:
            for f in d["filings"].get("files", []):
                if f.get("filingTo", "9999") < START:
                    continue                  # page ends before 2016: nothing we keep
                p = fetch_page(f["name"])
                if p is not None:
                    rows += _arrays_to_rows(p, ticker, c)
    own = [r["accepted_utc"] for r in rows if r["cik"] == cik]
    if own and len({r["cik"] for r in rows}) > 1:
        first = min(own)
        rows = [r for r in rows if r["cik"] == cik or r["accepted_utc"] < first]
    return rows, err


def stock_list() -> pd.DataFrame:
    s = pd.read_csv(LIST, usecols=["ticker", "cik"]).drop_duplicates()
    return s.sort_values("ticker").reset_index(drop=True)


def _write(df: pd.DataFrame) -> None:
    df = df.drop_duplicates(["ticker", "accession"], keep="last")
    df = df.sort_values(["accepted_ny", "ticker", "accession"]).reset_index(drop=True)
    tmp = OUT + ".tmp"
    df.to_csv(tmp, index=False)
    os.replace(tmp, OUT)


def update(full: bool | None = None, verbose: bool = True) -> dict:
    """Build or refresh lab/filings_8k.csv. full=None: full build only if the CSV is missing."""
    t0, n0 = time.time(), _count[0]
    stocks = stock_list()
    old = None
    if full is None:
        full = not os.path.exists(OUT)
    if not full:
        old = pd.read_csv(OUT, dtype={"items": str, "accession": str}, keep_default_na=False)
    known = set() if old is None else set(zip(old["ticker"], old["cik"].astype(int)))
    known_t = set() if old is None else set(old["ticker"])
    rows, fails, fulls = [], [], []
    for k, (t, c) in enumerate(zip(stocks["ticker"], stocks["cik"].astype(int))):
        need_full = full or t not in known_t or (t, c) not in known
        if need_full and not full:
            fulls.append(t)
        r, err = company_rows(t, c, need_full)
        if err:
            fails.append(f"{t}: {err}")
        rows += r
        if verbose and (k + 1) % 50 == 0:
            print(f"  {k + 1}/{len(stocks)} companies, {_count[0] - n0} requests, "
                  f"{time.time() - t0:.0f}s", flush=True)
    new = _finish(rows)
    if old is not None:
        keys = set(zip(old["ticker"], old["accession"]))
        added = sum((a, b) not in keys for a, b in zip(new["ticker"], new["accession"]))
        df = pd.concat([old[COLUMNS], new], ignore_index=True)
    else:
        added = len(new)
        df = new
    df = df[df["ticker"].isin(set(stocks["ticker"]))]
    _write(df)
    out = {"mode": "full" if full else "daily", "rows": len(df.drop_duplicates(["ticker", "accession"])),
           "companies": int(df["ticker"].nunique()), "new_rows": int(added),
           "requests": _count[0] - n0, "seconds": round(time.time() - t0, 1),
           "full_fetch_companies": fulls, "failures": fails}
    return out


def load(path: str = OUT) -> pd.DataFrame:
    """The 8-K table, accepted_ny as New York datetimes and items as a string."""
    df = pd.read_csv(path, dtype={"items": str, "accession": str}, keep_default_na=False)
    df["accepted_ny"] = pd.to_datetime(df["accepted_ny"], utc=True).dt.tz_convert(NY)
    df["filed"] = pd.to_datetime(df["filed"])
    return df


if __name__ == "__main__":
    s = update()
    print(f"{s['mode']} update: {s['rows']} filings, {s['companies']} companies, "
          f"{s['new_rows']} new, {s['requests']} requests, {s['seconds']}s")
    if s["full_fetch_companies"]:
        print("full fetch for new/changed companies:", s["full_fetch_companies"])
    if s["failures"]:
        print("failures:", s["failures"])
