"""Point-in-time profitability from SEC XBRL company facts.

For every company in lab/universe.csv and every 10-Q / 10-K it filed since 2015,
this works out what its trailing-twelve-month profitability looked like ON THE
DAY THE REPORT WAS FILED, using only numbers that were public by that day and,
for each period, the value as FIRST reported (never a later restatement).

Source: https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
Needs only `requests`; no API key.

    import fundamentals_data as fd
    fd.update()          # refresh every company, rewrite lab/fundamentals.csv
    df = fd.load()       # read it back with parsed dates

Rows: ticker, cik, filed, period_end, form, revenue_ttm, gross_profit_ttm,
op_income_ttm, net_income_ttm, assets, equity, gp_assets, op_assets.

`filed` is a DATE (no time). Many reports come out after the close, so a
signal built from a row can only be traded from the next session's open.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import os
import re
import sys
import time
from datetime import date, timedelta
from html import unescape

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
UNIVERSE = os.path.join(ROOT, "lab", "universe.csv")
WIKI = os.path.join(ROOT, "data", "universe", "wiki_current.html")
CACHE = os.path.join(ROOT, "data", "fundamentals")
OUT = os.path.join(ROOT, "lab", "fundamentals.csv")

UA = {"User-Agent": "Mozilla/5.0 (research script)", "Accept-Encoding": "gzip, deflate"}
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{:010d}.json"
MIN_GAP = 0.25          # seconds between requests: at most 4 a second
MAX_AGE = 86400         # re-fetch a company's facts if the cache is older than a day
START = "2015-01-01"    # earliest filing date written out
ROW_FORMS = {"10-Q", "10-K", "10-KT", "10-QT"}   # amendments are not new rows

COLUMNS = ["ticker", "cik", "filed", "period_end", "form", "revenue_ttm",
           "gross_profit_ttm", "op_income_ttm", "net_income_ttm", "assets",
           "equity", "gp_assets", "op_assets"]

CONCEPTS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax",
                "RevenuesNetOfInterestExpense"],   # last: banks' total net revenue
    # the last one excludes depreciation, as Compustat's COGS (Novy-Marx's input) does
    "cost": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold",
             "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization"],
    "gross": ["GrossProfit"],
    "opinc": ["OperatingIncomeLoss"],
    "netinc": ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"],
    "assets": ["Assets"],
    "equity": ["StockholdersEquity",
               "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
}
# An insurer (managed care included) reports claims costs under one of these. When
# they are material (a period's figure at least 5% of trailing revenue), its "cost of
# revenue" tag covers only products sold, so revenue minus it is not a gross profit:
# gross profitability is left empty unless the company tags GrossProfit itself.
FINANCIAL_MARKERS = ["PolicyholderBenefitsAndClaimsIncurredNet", "BenefitsLossesAndExpenses",
                     "IncurredClaimsPropertyCasualtyAndLongDuration",
                     "PolicyholderBenefitsAndClaimsIncurredHealthCare"]
# A derived gross profit (revenue minus cost) below operating income by more than this
# share of revenue means the two tags do not cover the same business: left empty.
GP_BELOW_OP = 0.05

# Companies that moved their filings to a new CIK (for example a new holding company):
# the predecessor's facts are merged in so the history and the trailing sums carry on.
PREDECESSORS = {
    "XOM": [34088],                     # ExxonMobil Holdings Corp (2115436) since mid-2026
    "GOOG": [1288776], "GOOGL": [1288776],   # Google Inc. before Alphabet (Oct 2015)
}

FLOWS = ["revenue", "cost", "gross", "opinc", "netinc"]
INSTANTS = ["assets", "equity"]

TOL = 10                 # days of slack when matching period boundaries
Q_DAYS = (75, 105)       # a single quarter
Y_DAYS = (340, 380)      # a fiscal year (52/53-week years included)


# --------------------------------------------------------------------- fetching
_last_request = [0.0]


def _get(url: str, tries: int = 6) -> requests.Response:
    """GET with a polite rate limit and exponential backoff."""
    delay = 2.0
    for attempt in range(tries):
        wait = MIN_GAP - (time.time() - _last_request[0])
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.time()
        try:
            r = requests.get(url, headers=UA, timeout=60)
        except requests.RequestException as e:
            if attempt == tries - 1:
                raise
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code == 200 or r.status_code == 404:
            return r
        if r.status_code in (403,) and attempt >= 1:
            # the SEC refusing us: stop rather than hammer
            raise RuntimeError(f"SEC refused {url}: HTTP {r.status_code}: {r.text[:300]!r}")
        time.sleep(delay)
        delay *= 2
    r.raise_for_status()
    return r


def fetch_facts(cik: int, max_age: float = MAX_AGE, cache: str = CACHE) -> dict | None:
    """Company facts JSON for one CIK, from the cache if it is fresh enough."""
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, f"CIK{cik:010d}.json.gz")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    r = _get(FACTS_URL.format(cik))
    if r.status_code == 404:
        return None
    data = r.json()
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)
    return data


# ------------------------------------------------------------------ ticker map
def _norm(t: str) -> str:
    return t.strip().upper().replace("-", ".").replace("/", ".")


def wiki_ciks(path: str = WIKI) -> dict[str, int]:
    """Ticker -> CIK from the saved Wikipedia 'List of S&P 500 companies' page."""
    if not os.path.exists(path):
        return {}
    html = open(path, encoding="utf-8").read()
    m = re.search(r'<table[^>]*id="constituents".*?</table>', html, re.S)
    if not m:
        return {}
    table = m.group(0)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)
    out: dict[str, int] = {}
    header = None
    for row in rows:
        cells = re.findall(r"<t([hd])[^>]*>(.*?)</t[hd]>", row, re.S)
        text = [unescape(re.sub(r"<[^>]+>", "", c[1])).strip() for c in cells]
        if cells and all(c[0] == "h" for c in cells):
            header = [t.lower() for t in text]
            continue
        if not header or len(text) != len(header):
            continue
        try:
            sym = text[header.index("symbol")]
            cik = text[header.index("cik")]
        except ValueError:
            continue
        if sym and cik.isdigit():
            out[_norm(sym)] = int(cik)
    return out


def universe() -> list[str]:
    with open(UNIVERSE, newline="") as f:
        return [_norm(r["ticker"]) for r in csv.DictReader(f) if r.get("ticker")]


def cik_map(tickers: list[str] | None = None) -> tuple[dict[str, int], list[str]]:
    """Ticker -> CIK: the Wikipedia cache first, then CIKs already in lab/fundamentals.csv
    (so a CI job without the git-ignored data/ folder still knows them)."""
    tickers = tickers or universe()
    known: dict[str, int] = {}
    if os.path.exists(OUT):
        with open(OUT, newline="") as f:
            for r in csv.DictReader(f):
                if r.get("cik"):
                    known[_norm(r["ticker"])] = int(r["cik"])
    known.update(wiki_ciks())
    found = {t: known[t] for t in tickers if t in known}
    missing = [t for t in tickers if t not in known]
    return found, missing


# ------------------------------------------------------------- fact handling
def _d(s: str) -> date:
    return date.fromisoformat(s)


def _first_reported(facts: dict, concept: str) -> list[dict]:
    """All USD facts of one concept with each (start, end) collapsed to its
    earliest filing. Each item: start, end, val, filed, accn, form, and all
    later filings (to measure restatement)."""
    node = facts.get("us-gaap", {}).get(concept)
    if not node:
        return []
    items = node.get("units", {}).get("USD", [])
    by_key: dict[tuple, list] = {}
    for it in items:
        key = (it.get("start"), it["end"])
        by_key.setdefault(key, []).append(it)
    out = []
    for (s, e), lst in by_key.items():
        lst.sort(key=lambda x: (x["filed"], x["accn"]))
        out.append({"start": s, "end": e, "val": float(lst[0]["val"]),
                    "filed": lst[0]["filed"], "accn": lst[0]["accn"],
                    "history": [(x["filed"], float(x["val"]), x["accn"]) for x in lst]})
    return out


def _value_as_of(fact: dict, asof: str) -> float | None:
    """First-reported value, provided it was public by `asof` (earliest filing <= asof)."""
    return fact["val"] if fact["filed"] <= asof else None


class _Pool:
    """Duration or instant facts of one concept, known as of a date, first-reported values."""

    def __init__(self, facts: list[dict], asof: str):
        self.dur = []   # (start, end, days, val)
        self.inst = {}  # end -> val
        for f in facts:
            v = _value_as_of(f, asof)
            if v is None:
                continue
            if f["start"]:
                s, e = _d(f["start"]), _d(f["end"])
                self.dur.append((s, e, (e - s).days + 1, v))
            else:
                self.inst[_d(f["end"])] = v

    def find(self, start=None, end=None, days=None):
        """Facts whose start/end are within TOL days of those given and length in `days`."""
        res = []
        for s, e, n, v in self.dur:
            if end is not None and abs((e - end).days) > TOL:
                continue
            if start is not None and abs((s - start).days) > TOL:
                continue
            if days is not None and not (days[0] <= n <= days[1]):
                continue
            res.append((s, e, n, v))
        # closest match first
        res.sort(key=lambda x: (abs((x[1] - end).days) if end else 0) +
                 (abs((x[0] - start).days) if start else 0))
        return res


def _ttm(pool: _Pool, end: date) -> tuple[float | None, str]:
    """Trailing twelve months ending `end`. Returns (value, method or failure reason)."""
    # 1. a fiscal-year figure ending at `end` (a 10-K)
    exact = [x for x in pool.find(end=end, days=Y_DAYS) if abs((x[1] - end).days) <= 3]
    if exact:
        return exact[0][3], "annual"
    # 2. year-to-date + last fiscal year - same period a year earlier
    ytds = [x for x in pool.find(end=end) if x[2] < Y_DAYS[0] and abs((x[1] - end).days) <= 3]
    if not ytds:
        return None, "no flow for this period"
    reason = "no prior fiscal year"
    for s, e, n, v in sorted(ytds, key=lambda x: -x[2]):
        fy = pool.find(end=s - timedelta(days=1), days=Y_DAYS)
        if not fy:
            continue
        fs, fe, fn, fv = fy[0]
        prior = pool.find(start=fs, end=e - timedelta(days=fn), days=(n - TOL, n + TOL))
        if not prior:
            reason = "no prior-year comparable"
            continue
        return v + fv - prior[0][3], "ytd"
    # 3. four single quarters, each direct, or a difference of year-to-date figures,
    #    or (for a fourth quarter) the year minus the first nine months
    total, q_end = 0.0, end
    for _ in range(4):
        q = _quarter(pool, q_end)
        if q is None:
            return None, reason + "; quarters incomplete"
        total += q[0]
        q_end = q[1] - timedelta(days=1)
    return total, "quarters"


def _quarter(pool: _Pool, end: date):
    """(value, start) of the single quarter ending near `end`."""
    direct = pool.find(end=end, days=Q_DAYS)
    if direct:
        return direct[0][3], direct[0][0]
    for s, e, n, v in sorted(pool.find(end=end), key=lambda x: x[2]):
        if n <= Q_DAYS[1]:
            continue
        # shorter period with the same start, ending about a quarter earlier
        for s2, e2, n2, v2 in pool.find(start=s):
            gap = (e - e2).days
            if Q_DAYS[0] <= gap <= Q_DAYS[1]:
                return v - v2, e2 + timedelta(days=1)
    return None


def _filings(facts: dict) -> list[dict]:
    """Original 10-Q/10-K filings: accn, form, filed, period_end."""
    seen: dict[str, dict] = {}
    ends: dict[str, list] = {}
    for concepts in CONCEPTS.values():
        for c in concepts:
            node = facts.get("us-gaap", {}).get(c)
            if not node:
                continue
            for it in node.get("units", {}).get("USD", []):
                form = it.get("form", "")
                if form not in ROW_FORMS:
                    continue
                a = it["accn"]
                seen.setdefault(a, {"accn": a, "form": form, "filed": it["filed"],
                                    "fy": it.get("fy"), "fp": it.get("fp")})
                ends.setdefault(a, []).append(it["end"])
    out = []
    for a, f in seen.items():
        # period end: the latest end date the filing reports, but not after it was filed
        cand = [e for e in ends[a] if e <= f["filed"]]
        if not cand:
            continue
        f["period_end"] = max(cand)
        out.append(f)
    out.sort(key=lambda x: (x["filed"], x["accn"]))
    return out


def _pick(concept_facts: dict[str, list], accn: str, asof: str, end: date, kind: str,
          largest: bool = False):
    """Try the concept alternatives in order, preferring ones the filing itself uses
    for its own period. With `largest` (revenue), the names this filing uses are tried
    largest first: some companies tag only a component under one name and the total
    under another, and some change what a name covers from one year to the next.
    Returns (value, concept, method/failure)."""
    names = list(concept_facts)
    own: dict[str, float] = {}
    for c in names:
        for f in concept_facts[c]:
            if abs((_d(f["end"]) - end).days) > 3:
                continue
            for h in f["history"]:
                if h[2] == accn:
                    own[c] = max(own.get(c, -math.inf), abs(h[1]))
    used = [c for c in names if c in own]
    if largest:
        used.sort(key=lambda c: -own[c])
    order = used + [c for c in names if c not in used]
    why = "not tagged"
    for c in order:
        if not concept_facts[c]:
            continue
        pool = _Pool(concept_facts[c], asof)
        if kind == "flow":
            v, how = _ttm(pool, end)
            if v is not None and largest and v < 0:
                why = "negative trailing sum (a tag changed meaning or a restatement)"
                continue
            if v is not None:
                return v, c, how
            why = how
        else:
            hits = [k for k in pool.inst if abs((k - end).days) <= 3]
            if hits:
                return pool.inst[min(hits, key=lambda k: abs((k - end).days))], c, "instant"
            why = "no value at period end"
    # Last resort for flows: the company changed tags between years (common in 2018
    # when revenue moved to RevenueFromContractWithCustomer...), so the year-ago and
    # current figures sit under different names. Pool them, each period taking the
    # value of the highest-priority name that has it.
    if kind == "flow" and sum(1 for c in order if concept_facts[c]) > 1:
        merged, have = [], set()
        for c in order:
            for f in concept_facts[c]:
                if f["filed"] > asof:
                    continue
                key = (f["start"], f["end"])
                if key not in have:
                    have.add(key)
                    merged.append(f)
        v, how = _ttm(_Pool(merged, asof), end)
        if v is not None and not (largest and v < 0):
            return v, "merged", how
        if v is None:
            why = how
    return None, None, why


def _is_insurer(facts: dict, asof: str, end: date, revenue_ttm: float) -> bool:
    lo = (end - timedelta(days=400)).isoformat()
    hi = end.isoformat()
    for c in FINANCIAL_MARKERS:
        node = facts.get("us-gaap", {}).get(c)
        if not node:
            continue
        for it in node.get("units", {}).get("USD", []):
            if (it.get("start") and lo <= it["end"] <= hi and it["filed"] <= asof
                    and abs(it["val"]) >= 0.05 * abs(revenue_ttm)):
                return True
    return False


def merge_facts(parts: list[dict]) -> dict:
    """Combine the 'facts' of several CIKs (a company and its predecessors)."""
    out: dict = {}
    for p in parts:
        for tax, concepts in p.items():
            for c, node in concepts.items():
                dst = out.setdefault(tax, {}).setdefault(c, {"units": {}})
                for u, items in node.get("units", {}).items():
                    dst["units"].setdefault(u, []).extend(items)
    return out


def company_rows(ticker: str, cik: int, facts: dict, start: str = START):
    """Rows for one company plus a list of construction failures."""
    cf = {k: {c: _first_reported(facts, c) for c in v} for k, v in CONCEPTS.items()}
    rows, fails, seen = [], [], set()
    for f in _filings(facts):
        if f["filed"] < start:
            continue
        if (f["filed"], f["period_end"]) in seen:   # same report filed under two CIKs
            continue
        seen.add((f["filed"], f["period_end"]))
        end = _d(f["period_end"])
        vals, meth, used = {}, {}, {}
        for k in FLOWS:
            vals[k], used[k], meth[k] = _pick(cf[k], f["accn"], f["filed"], end, "flow",
                                        largest=(k in ("revenue", "cost")))
        for k in INSTANTS:
            vals[k], _, meth[k] = _pick(cf[k], f["accn"], f["filed"], end, "instant")
        gp, src = vals["gross"], "tagged"
        if gp is None:
            src = "none"
            if vals["revenue"] is not None and vals["cost"] is not None:
                rev = vals["revenue"]
                if _is_insurer(facts, f["filed"], end, rev):
                    src = "insurer"
                elif (vals["opinc"] is not None and
                      (rev - vals["cost"]) < vals["opinc"] - GP_BELOW_OP * abs(rev)):
                    src = "inconsistent"
                else:
                    gp, src = rev - vals["cost"], "derived"
        a = vals["assets"]
        row = {"ticker": ticker, "cik": cik, "filed": f["filed"], "period_end": f["period_end"],
               "form": f["form"], "revenue_ttm": vals["revenue"], "gross_profit_ttm": gp,
               "op_income_ttm": vals["opinc"], "net_income_ttm": vals["netinc"],
               "assets": a, "equity": vals["equity"],
               "gp_assets": gp / a if gp is not None and a else None,
               "op_assets": vals["opinc"] / a if vals["opinc"] is not None and a else None,
               "_gp_src": src, "_cost": vals["cost"], "_accn": f["accn"],
               "_rev_c": used["revenue"], "_rev_how": meth["revenue"]}
        rows.append(row)
        for k in FLOWS + INSTANTS:
            if vals[k] is None and meth[k] != "not tagged":
                fails.append({"ticker": ticker, "filed": f["filed"], "period_end": f["period_end"],
                              "form": f["form"], "item": k, "why": meth[k]})
    return rows, fails


# ------------------------------------------------------------------- top level
def _fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if isinstance(v, float):
        return f"{v:.6g}" if abs(v) < 100 else f"{v:.0f}"
    return str(v)


def update(tickers: list[str] | None = None, max_age: float = MAX_AGE, out: str = OUT,
           verbose: bool = True) -> dict:
    """Refresh every company and rewrite lab/fundamentals.csv. Returns a summary."""
    t0 = time.time()
    tickers = tickers or universe()
    found, missing = cik_map(tickers)
    rows, fails, nofacts, fetched_cache = [], [], [], {}
    for i, t in enumerate(tickers):
        if t not in found:
            continue
        cik = found[t]
        try:
            if cik not in fetched_cache:
                fetched_cache.clear()        # keep memory bounded; share classes sit side by side
                parts = [fetch_facts(c, max_age) for c in [cik] + PREDECESSORS.get(t, [])]
                parts = [p["facts"] for p in parts if p and "facts" in p]
                fetched_cache[cik] = merge_facts(parts) if len(parts) > 1 else (parts[0] if parts else None)
            facts = fetched_cache[cik]
        except RuntimeError:
            raise
        except Exception as e:  # one bad company should not stop the run
            nofacts.append((t, f"fetch error: {e}"))
            continue
        if not facts:
            nofacts.append((t, "no company facts"))
            continue
        r, fl = company_rows(t, cik, facts)
        rows += r
        fails += fl
        if verbose and (i % 25 == 0):
            print(f"{i+1}/{len(tickers)} {t} rows={len(r)} {time.time()-t0:.0f}s", flush=True)
    rows.sort(key=lambda r: (r["ticker"], r["filed"], r["period_end"]))
    tmp = out + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([_fmt(r[c]) for c in COLUMNS])
    os.replace(tmp, out)
    return {"rows": len(rows), "companies": len({r["ticker"] for r in rows}),
            "missing_cik": missing, "no_facts": nofacts, "failures": fails, "row_detail": rows,
            "seconds": time.time() - t0}


def load(path: str = OUT):
    """lab/fundamentals.csv as a DataFrame with parsed dates (needs pandas)."""
    import pandas as pd
    df = pd.read_csv(path, dtype={"ticker": str, "form": str})
    for c in ("filed", "period_end"):
        df[c] = pd.to_datetime(df[c])
    return df


if __name__ == "__main__":
    s = update()
    print(f"rows={s['rows']} companies={s['companies']} seconds={s['seconds']:.0f}")
    print("missing CIK:", s["missing_cik"])
    print("no facts:", s["no_facts"])
    sys.exit(0)
