"""Point-in-time short interest for the stock list in lab/universe.csv.

Source: FINRA Query API, dataset otcMarket/consolidatedShortInterest (no key needed).
    POST https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest
    body {"limit": 5000,
          "domainFilters":  [{"fieldName": "symbolCode", "values": [...tickers...]}],
          "compareFilters": [{"compareType": "equal", "fieldName": "settlementDate",
                              "fieldValue": "YYYY-MM-DD"}]}
    header Accept: application/json
The API has no publication-date field, so `published` comes from FINRA's own
"Short Interest Reporting Dates" schedule pages (read through the Internet
Archive, because www.finra.org refuses scripted requests), and where a period is
not in any schedule found, settlement date + 9 business days.

update() builds or extends lab/short_interest.csv; load() reads it.
Raw responses are cached under data/short_interest/ (git-ignored).
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pandas.tseries.holiday import USFederalHolidayCalendar

ROOT = Path(__file__).resolve().parent
UNIVERSE = ROOT / "lab" / "universe.csv"
OUT = ROOT / "lab" / "short_interest.csv"
CACHE = ROOT / "data" / "short_interest"

API = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
ANCHORS = ["AAPL", "MSFT", "SPY"]          # always present; used to list the periods
FALLBACK_BDAYS = 9
COLS = ["ticker", "settlement_date", "published", "short_interest", "avg_daily_volume",
        "days_to_cover", "published_source", "finra_symbol"]

# FINRA schedule pages, as they moved over the years, with archive dates to read.
# The live page is tried first; www.finra.org usually answers scripts with 403.
LIVE_SCHEDULE = "https://www.finra.org/filing-reporting/short-interest/short-interest-reporting-due-dates"
SCHEDULE_SNAPSHOTS = [
    ("http://www.finra.org/industry/short-interest/short-interest-reporting-due-dates",
     ["20170301", "20170701", "20171101", "20180115", "20180408", "20180801",
      "20181213", "20190401", "20190801"]),
    ("https://www.finra.org/filing-reporting/short-interest/short-interest-reporting-due-dates",
     ["20191116"]),
    ("https://www.finra.org/filing-reporting/short-interest",
     ["20191211", "20200307", "20200606"]),
    ("https://www.finra.org/filing-reporting/regulatory-filing-systems/short-interest",
     ["20200718", "20201103", "20210302", "20210701", "20211102", "20220317", "20220811",
      "20230127", "20230608", "20231003", "20240320", "20240808", "20241202", "20250321",
      "20250806", "20251103", "20260323", "20260717"]),
]
RECENT_SCHEDULE_URLS = [  # read at "now" through the archive in a daily update
    LIVE_SCHEDULE,
    "https://www.finra.org/filing-reporting/regulatory-filing-systems/short-interest",
]

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}

_session = requests.Session()
_last_call = [0.0]


def _log(msg: str) -> None:
    print(msg, flush=True)


# ---------------------------------------------------------------- HTTP

def _request(method: str, url: str, min_gap: float = 0.4, tries: int = 6, **kw) -> requests.Response:
    """Polite request: at most ~2.5 per second, retry with backoff on 429/5xx/network errors."""
    headers = {"User-Agent": UA, **kw.pop("headers", {})}
    for k in range(tries):
        wait = _last_call[0] + min_gap - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()
        try:
            r = _session.request(method, url, headers=headers, timeout=90, **kw)
        except requests.RequestException as e:
            err = repr(e)
        else:
            if r.status_code < 400 or r.status_code in (400, 401, 403, 404):
                return r
            err = f"HTTP {r.status_code}"
        time.sleep(min(60, 2 * 2 ** k))
    raise RuntimeError(f"{method} {url} failed after {tries} tries: {err}")


def _api(body: dict) -> list[dict]:
    """POST a query to the FINRA API, paging through offsets; returns all records."""
    out, offset = [], 0
    while True:
        b = {**body, "limit": 5000, "offset": offset}
        r = _request("POST", API, json=b, headers={"Accept": "application/json"})
        if r.status_code in (401, 403):
            raise RuntimeError(f"FINRA refused the request (HTTP {r.status_code}): {r.text[:300]}")
        if r.status_code == 400:
            raise RuntimeError(f"FINRA rejected the query: {r.text[:500]}")
        if r.status_code == 204 or not r.text.strip():
            return out
        page = r.json()
        out += page
        total = int(r.headers.get("record-total") or len(out))
        offset += 5000
        if offset >= total or not page:
            return out


def _cached_api(name: str, body: dict, refresh: bool = False) -> list[dict]:
    p = CACHE / "api" / f"{name}.json"
    if p.exists() and not refresh:
        saved = json.loads(p.read_text())
        if saved.get("request") == body:
            return saved["rows"]
    rows = _api(body)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"request": body, "fetched": datetime.now(timezone.utc).isoformat(), "rows": rows}))
    return rows


# ---------------------------------------------------------------- periods and rows

def finra_symbol(ticker: str) -> str:
    """BRK.B / BRK-B / BRK/B / 'BRK B' -> BRKB (FINRA drops the class separator)."""
    return re.sub(r"[.\-/ ]", "", str(ticker).upper())


def _periods(after: str | None = None) -> list[str]:
    body = {"domainFilters": [{"fieldName": "symbolCode", "values": ANCHORS}]}
    if after:
        body["compareFilters"] = [{"compareType": "greater", "fieldName": "settlementDate",
                                   "fieldValue": after}]
    rows = _api(body)
    return sorted({r["settlementDate"] for r in rows if not after or r["settlementDate"] > after})


def _period_rows(d: str, symbols: list[str]) -> list[dict]:
    body = {"domainFilters": [{"fieldName": "symbolCode", "values": sorted(symbols)}],
            "compareFilters": [{"compareType": "equal", "fieldName": "settlementDate", "fieldValue": d}]}
    return _cached_api(f"period_{d}", body)


def _symbol_rows(sym: str) -> list[dict]:
    body = {"compareFilters": [{"compareType": "equal", "fieldName": "symbolCode", "fieldValue": sym}]}
    return _cached_api(f"symbol_{sym}", body)


def _by_quantity(d: str, qty: int) -> list[dict]:
    body = {"compareFilters": [{"compareType": "equal", "fieldName": "settlementDate", "fieldValue": d},
                               {"compareType": "equal", "fieldName": "currentShortPositionQuantity",
                                "fieldValue": int(qty)}]}
    return _cached_api(f"qty_{d}_{int(qty)}", body)


def _frame(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=["symbolCode", "settlementDate", "issueName",
                                     "currentShortPositionQuantity", "previousShortPositionQuantity",
                                     "averageDailyVolumeQuantity", "daysToCoverQuantity"])
    return pd.DataFrame(rows).drop_duplicates(["symbolCode", "settlementDate"])


def _name_key(name) -> str:
    w = re.sub(r"[^a-z0-9 ]", " ", str(name).lower()).split()
    return w[0] if w else ""


def _qty(x) -> int:
    return 0 if x is None or pd.isna(x) else int(x)


def _current_segment(h: pd.DataFrame, periods: list[str]) -> tuple[pd.DataFrame, str | None]:
    """Keep only the latest security behind a ticker (META was an ETF before Meta Platforms;
    Chesapeake's pre-bankruptcy shares were cancelled).

    A break is where the previous position FINRA reports does not equal the last current
    position in the series AND something else changed: the issuer name's first word, the
    FINRA symbol, or the series skipped one or more periods."""
    h = h.sort_values("settlementDate").reset_index(drop=True)
    pos = {d: i for i, d in enumerate(periods)}
    for i in range(len(h) - 1, 0, -1):
        a, b = h.iloc[i - 1], h.iloc[i]
        skipped = pos.get(b.settlementDate, 0) - pos.get(a.settlementDate, 0) > 1
        changed = (_name_key(a.issueName) != _name_key(b.issueName)
                   or a.symbolCode != b.symbolCode or skipped)
        if changed and _qty(b.previousShortPositionQuantity) != _qty(a.currentShortPositionQuantity):
            return h.iloc[i:], f"{h.iloc[0].settlementDate}..{a.settlementDate} '{a.issueName}' ({a.symbolCode})"
    return h, None


def _fill_gaps(ticker: str, h: pd.DataFrame, periods: list[str], notes: dict) -> pd.DataFrame:
    """Periods missing inside a ticker's series (Fiserv traded as FI 2023-2025, then FISV again):
    look up the symbol the shares traded under, as for a rename, and insert those rows."""
    pos = {d: i for i, d in enumerate(periods)}
    h = h.sort_values("settlementDate").reset_index(drop=True)
    add = []
    for i in range(1, len(h)):
        a, b = h.iloc[i - 1], h.iloc[i]
        if pos.get(b.settlementDate, 0) - pos.get(a.settlementDate, 0) <= 1:
            continue
        other = _predecessor(b, periods)
        if not other or other == b.symbolCode:
            continue
        o = _frame(_symbol_rows(other))
        o = o[(o.settlementDate > a.settlementDate) & (o.settlementDate < b.settlementDate)]
        if len(o):
            add.append(o)
            notes.setdefault("gap_filled", []).append(
                f"{ticker}: {other} {o.settlementDate.min()}..{o.settlementDate.max()}")
    return pd.concat([h, *add], ignore_index=True) if add else h


def _predecessor(first: pd.Series, periods: list[str]) -> str | None:
    """Old symbol of a renamed company: the one row in the prior period whose current position
    equals the previous position FINRA reports on the first row under the new symbol."""
    prev = _qty(first.previousShortPositionQuantity)
    i = periods.index(first.settlementDate) if first.settlementDate in periods else 0
    if prev < 10_000 or i == 0:
        return None
    cands = [r for r in _by_quantity(periods[i - 1], prev) if r["symbolCode"] != first.symbolCode]
    return cands[0]["symbolCode"] if len(cands) == 1 else None


def _history(ticker: str, periods: list[str], notes: dict, use_symbol_query: bool) -> pd.DataFrame:
    """Full history for one ticker, cut to the current company and spliced across renames."""
    sym = finra_symbol(ticker)
    h = _frame(_symbol_rows(sym)) if use_symbol_query else None
    return _splice(ticker, h, periods, notes)


def _splice(ticker: str, h: pd.DataFrame, periods: list[str], notes: dict) -> pd.DataFrame:
    if h is None or h.empty:
        notes.setdefault("missing", []).append(ticker)
        return _frame([])
    h = _fill_gaps(ticker, h, periods, notes)
    h, dropped = _current_segment(h, periods)
    if dropped:
        notes.setdefault("reused_symbol", []).append(f"{ticker}: dropped rows of an earlier issuer {dropped}")
    chain = [h.iloc[0].symbolCode]
    extended = {finra_symbol(ticker)}  # its own earlier rows are already in h
    for _ in range(6):
        first = h.sort_values("settlementDate").iloc[0]
        if first.settlementDate <= periods[0]:
            break
        if first.symbolCode not in extended:
            # the series starts with rows put in by _fill_gaps: first take that symbol's own earlier rows
            extended.add(first.symbolCode)
            o = _frame(_symbol_rows(first.symbolCode))
            o = o[o.settlementDate < first.settlementDate]
            if len(o):
                o, _ = _current_segment(pd.concat([o, first.to_frame().T]), periods)
                o = o[o.settlementDate < first.settlementDate]
            if len(o):
                notes.setdefault("renamed", []).append(
                    f"{ticker}: {first.symbolCode} {o.settlementDate.min()}..{o.settlementDate.max()} (earlier rows)")
                h = pd.concat([o, h])
                continue
        old = _predecessor(first, periods)
        if not old or old in chain:
            break
        o = _frame(_symbol_rows(old))
        o = o[o.settlementDate < first.settlementDate]
        if o.empty:
            break
        o, _ = _current_segment(o, periods)
        notes.setdefault("renamed", []).append(
            f"{ticker}: {old} {o.settlementDate.min()}..{o.settlementDate.max()} -> {first.symbolCode}")
        chain.append(old)
        extended.add(old)
        h = pd.concat([o, h])
    return h


# ---------------------------------------------------------------- publication schedule

def _parse_schedule(html: str, source: str) -> list[dict]:
    out = []
    parts = re.split(r"(?is)<h\d[^>]*>\s*(\d{4})(?:&nbsp;|\s)+Short Interest Reporting Dates\s*</h\d>", html)
    for k in range(1, len(parts), 2):
        year, body = int(parts[k]), parts[k + 1]
        m = re.search(r"(?is)<table.*?</table>", body)
        if not m:
            continue
        table = m.group(0)
        head = [re.sub(r"<[^>]+>|&nbsp;|\d$", " ", x).strip()
                for x in re.findall(r"(?is)<th[^>]*>(.*?)</th>", table)]
        third = re.sub(r"\s+", " ", head[2]).strip() if len(head) >= 3 else "?"
        for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", table):
            cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", tr)
            if len(cells) < 3:
                continue
            md = []
            for c in cells[:3]:
                t = re.sub(r"<[^>]+>", " ", c).lower()
                mm = re.search(r"(january|february|march|april|may|june|july|august|september|"
                               r"october|november|december)\s+(\d{1,2})", t)
                md.append((MONTHS[mm.group(1)], int(mm.group(2))) if mm else None)
            if None in md:
                continue
            s = date(year, *md[0])
            due = date(year + (md[1][0] < md[0][0]), *md[1])
            pub = date(year + (md[2][0] < md[0][0]), *md[2])
            if not (2 <= (pub - s).days <= 25):
                continue
            out.append({"settlement_date": s.isoformat(), "due_date": due.isoformat(),
                        "published": pub.isoformat(), "column": third, "source": source})
    return out


def _archive(url: str, ts: str) -> tuple[str, str] | None:
    """Fetch the archived page nearest to ts; cached raw under data/short_interest/schedule/."""
    key = re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[1]) + "_" + ts
    p = CACHE / "schedule" / f"{key}.html"
    meta = p.with_suffix(".src")
    if p.exists() and meta.exists():
        return p.read_text(encoding="utf-8"), meta.read_text()
    try:
        r = _request("GET", f"https://web.archive.org/web/{ts}id_/{url}", min_gap=1.5)
    except RuntimeError as e:
        _log(f"  schedule snapshot unavailable: {url} @ {ts}: {e}")
        return None
    if r.status_code != 200:
        _log(f"  schedule snapshot unavailable: {url} @ {ts}: HTTP {r.status_code}")
        return None
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(r.text, encoding="utf-8")
    meta.write_text(r.url)
    return r.text, r.url


def schedule(full: bool = True) -> pd.DataFrame:
    """FINRA settlement / due / publication dates. Later snapshots override earlier ones."""
    rows, snaps = [], []
    if full:
        snaps += [(u, ts) for u, tss in SCHEDULE_SNAPSHOTS for ts in tss]
    now = datetime.now(timezone.utc).strftime("%Y%m%d")
    snaps += [(u, now) for u in RECENT_SCHEDULE_URLS]
    try:  # live page first; usually HTTP 403 for scripts
        r = _request("GET", LIVE_SCHEDULE, tries=1)
        if r.status_code == 200:
            rows += _parse_schedule(r.text, LIVE_SCHEDULE + " (live " + now + ")")
    except RuntimeError:
        pass
    for u, ts in snaps:
        got = _archive(u, ts)
        if got:
            rows += _parse_schedule(*got)
    if not rows:
        return pd.DataFrame(columns=["settlement_date", "due_date", "published", "column", "source", "n_sources", "conflict"])
    s = pd.DataFrame(rows)
    s["snap"] = s.source.str.extract(r"/web/(\d{8,14})", expand=False).fillna("99999999")
    s = s.sort_values(["settlement_date", "snap"])
    g = s.groupby("settlement_date")
    last = g.tail(1).set_index("settlement_date")
    last["n_sources"] = g.size()
    last["conflict"] = g.published.nunique() > 1
    (CACHE / "schedule").mkdir(parents=True, exist_ok=True)
    s.to_csv(CACHE / "schedule" / "parsed_all.csv", index=False)
    return last.reset_index()[["settlement_date", "due_date", "published", "column", "source", "n_sources", "conflict"]]


_BDAY = pd.offsets.CustomBusinessDay(calendar=USFederalHolidayCalendar())


def _fallback_published(d: str) -> str:
    return (pd.Timestamp(d) + FALLBACK_BDAYS * _BDAY).date().isoformat()


# ---------------------------------------------------------------- build

def _to_output(raw: pd.DataFrame, sched: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return pd.DataFrame(columns=COLS)
    df = pd.DataFrame({
        "ticker": raw["ticker"],
        "settlement_date": raw["settlementDate"],
        "short_interest": pd.to_numeric(raw["currentShortPositionQuantity"]).astype("Int64"),
        "avg_daily_volume": pd.to_numeric(raw["averageDailyVolumeQuantity"]).astype("Int64"),
        "days_to_cover": pd.to_numeric(raw["daysToCoverQuantity"]),
        "finra_symbol": raw["symbolCode"],
    })
    df.loc[df.avg_daily_volume.fillna(0) == 0, "days_to_cover"] = np.nan  # FINRA writes 0 for "unknown"
    pub = sched.set_index("settlement_date")["published"] if len(sched) else pd.Series(dtype=str)
    df["published"] = df.settlement_date.map(pub)
    df["published_source"] = "schedule"   # the API itself carries no dissemination date
    miss = df.published.isna()
    df.loc[miss, "published"] = df.loc[miss, "settlement_date"].map(_fallback_published)
    return df[COLS]


def update(full: bool = False) -> pd.DataFrame:
    """Build lab/short_interest.csv (full) or add the periods after its last settlement date."""
    t0 = time.time()
    tickers = pd.read_csv(UNIVERSE)["ticker"].dropna().astype(str).str.strip().unique().tolist()
    sym2tic = {finra_symbol(t): t for t in tickers}
    old = None if full or not OUT.exists() else load()
    notes: dict = {}

    if old is None or old.empty:
        periods = _periods()
        _log(f"full build: {len(periods)} periods {periods[0]}..{periods[-1]}, {len(tickers)} tickers")
        sched = schedule(full=True)
        parts = []
        for i, d in enumerate(periods):
            f = _frame(_period_rows(d, list(sym2tic)))
            f["ticker"] = f.symbolCode.map(sym2tic)
            parts.append(f)
            if (i + 1) % 25 == 0:
                _log(f"  {i + 1}/{len(periods)} periods")
        raw = pd.concat(parts, ignore_index=True)
        # one company per ticker: drop an earlier issuer of a reused symbol, splice renames
        fixed = []
        for t, h in raw.groupby("ticker"):
            fixed.append(_splice(t, h.drop(columns="ticker"), periods, notes).assign(ticker=t))
        notes["missing"] = sorted(set(tickers) - set(raw.ticker))
        raw = pd.concat(fixed, ignore_index=True)
        new = _to_output(raw, sched)
        out = new
    else:
        last = old.settlement_date.max()
        periods_new = _periods(after=last)
        sched = schedule(full=False) if periods_new else pd.DataFrame(columns=["settlement_date", "published"])
        parts = []
        for d in periods_new:
            f = _frame(_period_rows(d, list(sym2tic)))
            f["ticker"] = f.symbolCode.map(sym2tic)
            parts.append(f)
        # tickers that joined the list since the file was built: fetch their whole history
        added = sorted(set(tickers) - set(old.ticker))
        if added:
            periods = sorted(set(old.settlement_date) | set(periods_new))
            for t in added:
                h = _history(t, periods, notes, use_symbol_query=True)
                if not h.empty:
                    parts.append(h.assign(ticker=t))
            sched = schedule(full=True)
        raw = pd.concat(parts, ignore_index=True) if parts else _frame([]).assign(ticker=[])
        new = _to_output(raw, sched)
        out = pd.concat([old[COLS], new], ignore_index=True)
        _log(f"daily update: {len(periods_new)} new period(s) after {last}, {len(added)} new ticker(s)")

    out = (out.drop_duplicates(["ticker", "settlement_date"], keep="last")
              .sort_values(["ticker", "settlement_date"]).reset_index(drop=True))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    out.to_csv(tmp, index=False)
    tmp.replace(OUT)
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "last_run.json").write_text(json.dumps(
        {"full": old is None or old.empty, "seconds": round(time.time() - t0, 1),
         "rows_added": int(len(new)), "notes": notes}, indent=1, default=str))
    update.notes = notes
    update.seconds = time.time() - t0
    return out


def load() -> pd.DataFrame:
    """Read lab/short_interest.csv. Use `published`, not `settlement_date`, as the as-of date."""
    df = pd.read_csv(OUT, dtype={"ticker": str, "finra_symbol": str, "published_source": str})
    for c in ("short_interest", "avg_daily_volume"):
        df[c] = df[c].astype("Int64")
    return df


if __name__ == "__main__":
    out = update(full="--full" in sys.argv)
    lag = (pd.to_datetime(out.published) - pd.to_datetime(out.settlement_date)).dt.days
    print(f"rows {len(out):,}  tickers {out.ticker.nunique()}  settlement "
          f"{out.settlement_date.min()}..{out.settlement_date.max()}  "
          f"periods {out.settlement_date.nunique()}  latest published {out.published.max()}")
    print(f"lag settlement->published, calendar days: median {lag.median():.0f}, "
          f"range {lag.min()}..{lag.max()}  ({update.seconds:.0f}s)")
    for k, v in getattr(update, "notes", {}).items():
        if v:
            print(f"{k}: {len(v)}  " + "; ".join(map(str, v[:8])) + (" ..." if len(v) > 8 else ""))
