"""Survivorship-free S&P 500 panel (2016-01-04 on), rebuilt from Alpaca alone.

    from wide_universe import load, missing
    panel, member = load()          # panel = {"o","h","l","c","v": [day x id]}, member = bool [day x id]

Inputs, both committed:
  lab/universe_members.csv  id, member_from, member_to, open   one row per membership spell (trading days, inclusive).
                            open=1: still a member on the file's last date; such companies stay members after it.
  lab/universe_symbols.csv  id, symbol, use_from, use_to       the Alpaca symbol(s) whose bars make up the id's
                            history and the calendar dates each applies (inclusive; empty use_to = still running).
Prices come from daily_calls.bars() (Alpaca SIP, adjustment=all; it finds the data key itself).

The id is the company's latest ticker ("X@2016" = an earlier, different company that used X). Both files were
derived from universe_data.py's local build (data/universe/): its chains, Alpaca symbol choices and OVERRIDES,
reproduced exactly (see reports/wide_universe_quality.md). Rules carried over from that build:
  * bars with volume 0 are dropped (Alpaca keeps printing the last price after a delisting);
  * an id's prices span ~400 days before its first membership to 10 days after its last, nothing outside;
  * where an id switches symbol, earlier bars are rescaled so the levels join: exact when the old symbol also has a
    bar on the new symbol's first day, else that day's return is taken as 0%; across a hole longer than 10 days
    (Paramount 2022-02..2025-08, not in Alpaca) the levels are left as they are. o/h/l/c are multiplied by the
    factor and volume divided by it (dollar volume is kept).
  * rows of one id may overlap: a later row takes over from its first bar, the earlier one's extra bars only set
    the join; if a row's symbol has no bars at all in its range, the id's later symbols fill it (fallbacks()).
Not carried over (they need yfinance): pre-2016 prices, the 13 spin-off return patches, DOW's and Paramount's
yfinance fill. Failed companies end at their last trade, not at a delisting return (see the report).
"""
import contextlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
MEMBERS = ROOT / "lab" / "universe_members.csv"
SYMBOLS = ROOT / "lab" / "universe_symbols.csv"
GAP = pd.Timedelta(days=10)  # longer hole between two symbols: no rescale across it
_last = {}


def _files():
    m = pd.read_csv(MEMBERS, parse_dates=["member_from", "member_to"])
    s = pd.read_csv(SYMBOLS, parse_dates=["use_from", "use_to"])
    return m, s.sort_values(["id", "use_from"])


def _fetch(symbols):
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import daily_calls
    with contextlib.chdir(ROOT):  # bars() looks for its key in the environment, else in the repo folder
        return daily_calls.bars(list(symbols))


def assemble(raw, members, symbols, start="2016-01-01"):
    """(panel, member) from raw bars {o,h,l,c,v: [day x symbol]} and the two files (as DataFrames)."""
    days = raw["c"].index.sort_values() if len(raw["c"].columns) else pd.DatetimeIndex([])
    ok = raw["v"].reindex(days) > 0  # volume-0 bars are stale prints
    f = {k: raw[k].reindex(days).where(ok) for k in "ohlcv"}
    ids = sorted(set(members["id"]) | set(symbols["id"]))
    out = {k: {} for k in "ohlcv"}
    empty = pd.Series(np.nan, index=days)
    fallbacks = []
    for i, rows in symbols.groupby("id"):
        rows = list(rows.itertuples())
        segs = []
        for n, r in enumerate(rows):
            lo, hi = r.use_from, (r.use_to if pd.notna(r.use_to) else days[-1] if len(days) else r.use_from)
            inr = (days >= lo) & (days <= hi)
            # Alpaca sometimes moves a renamed company's whole history to its new symbol, after which the old symbol
            # returns nothing: then take this row's dates from the id's later symbols, in order.
            d = None
            for sym in dict.fromkeys([r.symbol] + [x.symbol for x in rows[n + 1:]]):
                if sym in f["c"].columns and f["c"][sym][inr].notna().any():
                    d = {k: f[k][sym].where(inr) for k in "ohlcv"}
                    if sym != r.symbol:
                        fallbacks.append((i, r.symbol, sym))
                    break
            segs.append((r.symbol, hi, d))
        fac, acc = 1.0, {k: empty.copy() for k in "ohlcv"}
        nxt = None  # first (day, close) of the later, already placed segment
        for sym, hi, d in reversed(segs):
            if d is None:
                continue
            c = d["c"].dropna()
            if not len(c):
                continue
            put = d["c"].notna()
            if nxt is not None:  # this row runs until the later row's first bar; join the levels there
                j, cj = nxt
                prev = c[c.index < j]
                if j in c.index:  # overlap bar: exact
                    fac = cj / c[j]
                elif len(prev) and j - prev.index[-1] <= GAP:  # adjacent: join-day return 0%
                    fac = cj / prev.iloc[-1]
                # else a long hole with no Alpaca source: levels left as they are
                put &= d["c"].index < j
                c = c[c.index < j]
                if not len(c):
                    continue
            for k in "ohlc":
                acc[k] = acc[k].where(~put, d[k] * fac)
            acc["v"] = acc["v"].where(~put, d["v"] / fac)
            nxt = (c.index[0], c.iloc[0] * fac)
        for k in "ohlcv":
            out[k][i] = acc[k]
    keep = days >= pd.Timestamp(start)  # cut only now, so joins before `start` still set the levels
    days = days[keep]
    panel = {k: pd.DataFrame(out[k], index=empty.index).reindex(index=days, columns=ids) for k in "ohlcv"}
    member = pd.DataFrame(False, index=days, columns=ids)
    for r in members.itertuples():
        hi = days[-1] if (r.open and len(days)) else r.member_to
        member.loc[(days >= r.member_from) & (days <= hi), r.id] = True
    _last["fallbacks"] = fallbacks
    return panel, member


def load(start="2016-01-01"):
    """(panel, member): panel = {"o","h","l","c","v": DataFrame[day x id]}, member = bool DataFrame[day x id].
    One call to daily_calls.bars() with every symbol (about 750, paginated 100 at a time by bars())."""
    m, s = _files()
    raw = _fetch(sorted(set(s["symbol"])))
    panel, member = assemble(raw, m, s, start)
    _last["panel"] = panel
    return panel, member


def fallbacks():
    """(id, symbol in the file, symbol used) for rows whose own symbol had no bars, from the last assemble()."""
    return list(_last.get("fallbacks", []))


def missing(panel=None):
    """Ids with no bars at all (all-empty columns) in `panel`, default the last load()."""
    p = panel if panel is not None else _last.get("panel")
    if p is None:
        raise RuntimeError("call load() first or pass a panel")
    return sorted(p["c"].columns[p["c"].isna().all()])


if __name__ == "__main__":
    import time
    t = time.time()
    panel, member = load()
    print(f"{panel['c'].shape[1]} ids, {panel['c'].index[0].date()}..{panel['c'].index[-1].date()}, "
          f"{int(member.iloc[-1].sum())} members on the last day, {time.time() - t:.0f}s")
    print("no bars:", ", ".join(missing()))
    if fallbacks():
        print("rows filled from a later symbol:", fallbacks())
