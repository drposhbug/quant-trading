"""Quarterly earnings announcements (date, before/after market, EPS, consensus, surprise, # estimates) since 2016.

Source: Nasdaq's public earnings calendar, one page per calendar date:
    https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD
No API key; only `requests`. Each day's raw JSON is cached under data/earnings/ (git-ignored); the tidy result,
filtered to the project's stock list, is written to lab/earnings.csv. Data quality notes and traps:
reports/earnings_data_quality.md (read it before using the file: after-close announcements are only tradable at the
next session, EPS is not split-adjusted, and the historical consensus may not be point-in-time).

    python earnings_data.py          # fetch what is missing, rewrite lab/earnings.csv, print a summary
    import earnings_data as ed; df = ed.load()
"""
from __future__ import annotations

import ast
import datetime as dt
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "data" / "earnings"
OUT = ROOT / "lab" / "earnings.csv"
URL = "https://api.nasdaq.com/api/calendar/earnings"
START = dt.date(2016, 1, 1)
AHEAD_DAYS = 30      # upcoming announcements wanted too
REFRESH_DAYS = 10    # recent pages change (EPS filled in, dates confirmed): always re-fetch these and the future
MIN_INTERVAL = 0.34  # seconds between requests: at most ~3 per second
MAX_TRIES = 6
MAX_CONSECUTIVE_FAILS = 8  # then stop the run instead of hammering a server that is refusing us
DUP_WINDOW_DAYS = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}
COLUMNS = ["date", "ticker", "when", "eps", "eps_forecast", "surprise_pct", "n_est", "fiscal_quarter"]
WHEN = {"time-pre-market": "before", "time-after-hours": "after"}


# ---------------------------------------------------------------- stock list
def _norm(sym: str) -> str:
    """Nasdaq writes class shares as BRK/B (sometimes BRK-B or BRK.B); the project list uses BRK.B."""
    return str(sym).strip().upper().replace("/", ".").replace("-", ".")


def _lists_from_source(path: Path, names: list[str]) -> dict[str, list[str]]:
    """Read list literals (and `A + B` concatenations of them) from a .py file without importing it
    (model.py imports yfinance, which the daily job does not need)."""
    if not path.exists():
        return {}
    env: dict[str, list[str]] = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            try:
                env[name] = list(ast.literal_eval(node.value))
                continue
            except (ValueError, TypeError, SyntaxError):
                pass
            if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                parts, ok, stack = [], True, [node.value]
                while stack:
                    v = stack.pop()
                    if isinstance(v, ast.BinOp) and isinstance(v.op, ast.Add):
                        stack += [v.right, v.left]
                    elif isinstance(v, ast.Name) and v.id in env:
                        parts += env[v.id]
                    else:
                        ok = False
                        break
                if ok:
                    env[name] = parts
    return {n: env[n] for n in names if n in env}


def default_tickers() -> list[str]:
    """lab/universe.csv (S&P 500) + model.UNIVERSE + universe_study.TECH10_2014, in dotted form (BRK.B)."""
    tick = set(pd.read_csv(ROOT / "lab" / "universe.csv")["ticker"].dropna().astype(str))
    for f, n in [("model.py", "UNIVERSE"), ("universe_study.py", "TECH10_2014")]:
        tick |= set(_lists_from_source(ROOT / f, [n]).get(n, []))
    return sorted({_norm(t) for t in tick})


# ---------------------------------------------------------------- fetching
_last_request = [0.0]


def _get(session: requests.Session, day: dt.date, tries: int = MAX_TRIES) -> dict:
    """One calendar page, politely: rate-limited, retried with exponential backoff (honours Retry-After on 429)."""
    err = None
    for attempt in range(tries):
        r = None
        wait = _last_request[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()
        try:
            r = session.get(URL, params={"date": day.isoformat()}, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, dict) and isinstance(j.get("data"), dict):
                    return j
                # a day with no announcements comes back as data=null with code 1002 "No record found": valid, empty
                codes = [m.get("code") for m in ((j.get("status") or {}).get("bCodeMessage") or [])
                         if isinstance(m, dict)] if isinstance(j, dict) else []
                if isinstance(j, dict) and j.get("data") is None and 1002 in codes:
                    j["data"] = {"rows": []}
                    return j
                err = f"unexpected body: {r.text[:200]!r}"
            else:
                err = f"HTTP {r.status_code}"
                if r.status_code == 429 and r.headers.get("Retry-After", "").isdigit():
                    time.sleep(min(int(r.headers["Retry-After"]), 300))
                    continue
                if r.status_code in (400, 401, 403, 404) and attempt >= 2:
                    break  # a refusal, not a hiccup: do not keep knocking
        except (requests.RequestException, ValueError) as e:
            err = f"{type(e).__name__}: {e}"
            if r is not None and "html" in r.headers.get("content-type", ""):
                err = "HTML page instead of JSON"
        if attempt == tries - 1:
            break
        time.sleep(min(2 ** attempt * 2, 120) * (1 + 0.25 * random.random()))
    raise RuntimeError(f"{day}: {err}")


def _weekdays(a: dt.date, b: dt.date):
    d = a
    while d <= b:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def _cache_file(day: dt.date) -> Path:
    return CACHE / f"{day.isoformat()}.json"


def _is_placeholder(f: Path) -> bool:
    try:
        return "_error" in json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True


def _write(day: dt.date, j: dict) -> None:
    j["_fetched_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    tmp = _cache_file(day).with_suffix(".tmp")
    tmp.write_text(json.dumps(j), encoding="utf-8")
    tmp.replace(_cache_file(day))


def _keep_known_time(day: dt.date, j: dict) -> None:
    """Nasdaq shows pre-market/after-hours only while a date is upcoming; once it passes, the page says
    'time-not-supplied'. Carry a time seen in an earlier fetch of the same page forward (marked _time_from_cache),
    so the daily job accumulates timing history from now on."""
    f = _cache_file(day)
    if not f.exists():
        return
    try:
        old = (json.loads(f.read_text(encoding="utf-8")).get("data") or {}).get("rows") or []
    except (OSError, ValueError):
        return
    known = {r.get("symbol"): r.get("time") for r in old if r.get("time") in WHEN}
    for r in (j.get("data") or {}).get("rows") or []:
        if r.get("time") not in WHEN and r.get("symbol") in known:
            r["time"] = known[r["symbol"]]
            r["_time_from_cache"] = True


def fetch(through: dt.date | None = None, verbose: bool = True) -> dict:
    """Download every weekday page not yet cached (plus the last REFRESH_DAYS and all future dates).

    A past page that keeps failing (e.g. 2026-02-19 serves an HTML page instead of JSON) is cached as an empty
    placeholder with an "_error" key, so it does not block or fail every later run; placeholders are retried once
    (single attempt, no backoff) on each run and replaced as soon as the page works. Only failures inside the
    refresh window count as hard failures (stats["failed"]); the rest are listed in stats["placeholders"]."""
    today = dt.date.today()
    through = through or today + dt.timedelta(days=AHEAD_DAYS)
    CACHE.mkdir(parents=True, exist_ok=True)
    refresh_from = today - dt.timedelta(days=REFRESH_DAYS)
    todo = []
    for d in _weekdays(START, through):
        f = _cache_file(d)
        if d >= refresh_from or not f.exists():
            todo.append((d, MAX_TRIES))
        elif _is_placeholder(f):
            todo.append((d, 1))
    stats = {"todo": len(todo), "fetched": 0, "failed": [], "placeholders": [], "seconds": 0.0}
    t0, fails = time.monotonic(), 0
    with requests.Session() as s:
        for i, (d, tries) in enumerate(todo, 1):
            try:
                j = _get(s, d, tries)
            except RuntimeError as e:
                if d < refresh_from:
                    stats["placeholders"].append(str(e))
                    if not _cache_file(d).exists() or _is_placeholder(_cache_file(d)):
                        _write(d, {"_error": str(e), "data": {"rows": []}})
                else:
                    stats["failed"].append(str(e))
                fails += 1
                if verbose:
                    print("  failed", e, flush=True)
                if fails >= MAX_CONSECUTIVE_FAILS:
                    print(f"  {fails} failures in a row: stopping; re-run later to resume", flush=True)
                    stats["failed"].append(f"stopped after {fails} consecutive failures")
                    break
                continue
            fails = 0
            _keep_known_time(d, j)
            _write(d, j)
            stats["fetched"] += 1
            if verbose and (i % 100 == 0 or i == len(todo)):
                print(f"  {i}/{len(todo)} pages ({d})  {time.monotonic() - t0:.0f}s", flush=True)
    stats["seconds"] = time.monotonic() - t0
    return stats


# ---------------------------------------------------------------- parsing
def _num(x) -> float:
    """'$1.90' -> 1.90, '($0.12)' -> -0.12, '-$0.12' -> -0.12, '1,234' -> 1234, 'N/A'/'' -> NaN."""
    if x is None:
        return np.nan
    s = str(x).strip()
    if not s or s.upper() in {"N/A", "NA", "--", "-", "NONE", "NULL"}:
        return np.nan
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("$", "").replace(",", "").replace("%", "").strip()
    if s.startswith("-"):
        neg, s = True, s[1:].strip()
    try:
        v = float(s)
    except ValueError:
        return np.nan
    return -v if neg else v


def _fiscal(x) -> str:
    """'Mar/2016' -> '2016-03' (month the fiscal quarter ends)."""
    try:
        return dt.datetime.strptime(str(x).strip(), "%b/%Y").strftime("%Y-%m")
    except ValueError:
        return ""


def parse_cache(tickers=None) -> pd.DataFrame:
    """All cached pages -> one row per (date, ticker) for the given tickers (default: default_tickers();
    pass tickers='all' for every symbol on the calendar)."""
    keep = None if (isinstance(tickers, str) and tickers == "all") else {_norm(t) for t in (tickers or default_tickers())}
    recs = []
    for f in sorted(CACHE.glob("????-??-??.json")):
        day = f.stem
        rows = (json.loads(f.read_text(encoding="utf-8")).get("data") or {}).get("rows") or []
        for r in rows:
            t = _norm(r.get("symbol", ""))
            if not t or (keep is not None and t not in keep):
                continue
            recs.append({
                "date": day, "ticker": t, "when": WHEN.get(r.get("time"), "unknown"),
                "eps": _num(r.get("eps")), "eps_forecast": _num(r.get("epsForecast")),
                "surprise_pct": _num(r.get("surprise")), "n_est": _num(r.get("noOfEsts")),
                "fiscal_quarter": _fiscal(r.get("fiscalQuarterEnding")),
            })
    df = pd.DataFrame(recs, columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"])
    return repair(df).sort_values(["ticker", "date"]).reset_index(drop=True)


def repair(df: pd.DataFrame) -> pd.DataFrame:
    """Two source defects, fixed conservatively:
    1. Junk rows whose fiscal quarter ended more than 200 days before the listed date (e.g. 2019-01-01 shows PANW
       and WDAY results for Apr/2012): dropped.
    2. A lost minus sign on eps or eps_forecast (e.g. TSLA 2017-08-02: eps -2.04, forecast '$2', surprise -2%).
       Nasdaq's own surprise_pct is consistent with the true signs, so a sign is flipped only when the given
       values miss the stated surprise by more than 1 point and flipping exactly one sign reproduces it within
       0.5 point."""
    fq = pd.to_datetime(df["fiscal_quarter"], format="%Y-%m", errors="coerce") + pd.offsets.MonthEnd(0)
    df = df[~((df["date"] - fq).dt.days > 200)].copy()

    def surp(a, f):
        return (a - f) / f.abs() * 100

    e, f, s = df["eps"], df["eps_forecast"], df["surprise_pct"]
    ok = e.notna() & f.notna() & s.notna() & (f != 0)
    bad = ok & ((surp(e, f) - s).abs() > 1)
    fix_e = bad & ((surp(-e, f) - s).abs() <= 0.5) & (e != 0)
    fix_f = bad & ~fix_e & ((surp(e, -f) - s).abs() <= 0.5)
    df.loc[fix_e, "eps"] = -e[fix_e]
    df.loc[fix_f, "eps_forecast"] = -f[fix_f]
    df.attrs["sign_fixes"] = int(fix_e.sum() + fix_f.sum())
    return df


def dedupe(df: pd.DataFrame, window_days: int = DUP_WINDOW_DAYS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Same ticker listed again within `window_days` (or on the same fiscal quarter twice): keep one row.
    Preference: the row that carries a reported EPS, then the one with a forecast, then known timing, then the
    later date. Returns (kept, dropped)."""
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    gap = df.groupby("ticker")["date"].diff().dt.days
    same_q = (df["fiscal_quarter"] != "") & (df["fiscal_quarter"] == df.groupby("ticker")["fiscal_quarter"].shift())
    new_cluster = gap.isna() | ((gap > window_days) & ~(same_q & (gap <= 45)))
    df["_c"] = new_cluster.cumsum()
    score = (df["eps"].notna() * 8 + df["eps_forecast"].notna() * 4 + (df["when"] != "unknown") * 2)
    df["_s"] = score
    df = df.sort_values(["_c", "_s", "date"])
    kept = df.groupby("_c").tail(1)
    dropped = df.drop(kept.index)
    clean = lambda x: x.drop(columns=["_c", "_s"]).sort_values(["date", "ticker"]).reset_index(drop=True)
    return clean(kept), clean(dropped)


def build(tickers=None, out: Path = OUT) -> pd.DataFrame:
    df, _ = dedupe(parse_cache(tickers))
    out.parent.mkdir(parents=True, exist_ok=True)
    df.assign(date=df["date"].dt.strftime("%Y-%m-%d")).to_csv(out, index=False, float_format="%.4g")
    return df


def update(through: dt.date | None = None, tickers=None, verbose: bool = True) -> dict:
    """Fetch what is missing (and refresh recent/future pages), then rewrite lab/earnings.csv."""
    if isinstance(through, str):
        through = dt.date.fromisoformat(through)
    stats = fetch(through, verbose=verbose)
    df = build(tickers)
    stats["rows"] = len(df)
    stats["tickers"] = df["ticker"].nunique()
    stats["first"], stats["last"] = (df["date"].min(), df["date"].max()) if len(df) else (None, None)
    return stats


def load(path: Path = OUT) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"ticker": str, "when": str, "fiscal_quarter": str}, keep_default_na=False,
                     na_values=[""])
    df["date"] = pd.to_datetime(df["date"])
    for c in ["eps", "eps_forecast", "surprise_pct", "n_est"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["n_est"] = df["n_est"].astype("Int64")
    df["fiscal_quarter"] = df["fiscal_quarter"].fillna("")
    return df


if __name__ == "__main__":
    s = update()
    print(f"pages fetched {s['fetched']}/{s['todo']} in {s['seconds']:.0f}s, failed {len(s['failed'])}, "
          f"past pages still unavailable {len(s['placeholders'])}")
    for e in (s["failed"] + s["placeholders"])[:10]:
        print("  ", e)
    print(f"{OUT.relative_to(ROOT)}: {s['rows']} rows, {s['tickers']} tickers, {s['first']:%Y-%m-%d} .. {s['last']:%Y-%m-%d}")
    today = pd.Timestamp(dt.date.today())
    up = load()
    up = up[up["date"] >= today].head(8)
    if len(up):
        print("next:", ", ".join(f"{r.ticker} {r.date:%m-%d} {r.when}" for r in up.itertuples()))
    if s["failed"]:
        raise SystemExit(1)
