"""Can intraday trading of TSLA make money after costs? Writes reports/intraday_results.md.
Run: python intraday_study.py [--refresh]

Data: Alpaca SIP 5-minute bars (adjustment=all), 2016 onward, TSLA plus QQQ and NVDA as out-of-symbol checks.
Bar timestamps are bar START times (UTC). Regular session only; per-day open/close (half days included) come from
Alpaca's read-only /v2/calendar, so post-13:00 extended-hours bars on half days are dropped.
A signal computed from bar k (known at its close) trades at bar k+1's open or later.

Pre-registered strategies, one fixed parameterization each (no tuning):
  ORB long-only / ORB long-short: first 5-min bar direction -> enter at 2nd bar open, stop 10% of 14d ATR, exit at close.
  Intraday momentum: sign(prior close -> 10:00) -> hold the last 30 minutes in that direction.
  VWAP mean reversion: close > 2 sd (20-bar rolling sd of 5-min returns) below session VWAP -> buy next open,
      exit at the first touch of VWAP (limit at the VWAP known when the bar opens) or at the close. One trade/day.
  Gap fade: |open / prior close - 1| > 2% -> fade at the 09:35 open, exit at the close.
Costs: c per side (2 bp base, 5 bp stress), 1x notional. Pass = Holm p < 0.05 over all strategy x symbol x cost tests,
positive mean, same sign in 2016-2020 and 2021-2026, and positive net at 5 bp.
"""
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import requests

from backtest import sharpe_rows, stationary_bootstrap_idx, stats
from correlations import holm, pval

SYMS = ["TSLA", "QQQ", "NVDA"]
START, END = "2016-01-01", "2026-11-17"
COSTS = [0.0002, 0.0005]
STRATS = ["ORB long-only", "ORB long-short", "Intraday momentum (last 30m)", "VWAP mean reversion", "Gap fade"]


def keys():
    env = dict(os.environ)
    if os.path.exists(".env"):
        for line in open(".env"):
            k, _, v = line.strip().partition("=")
            env.setdefault(k, v.strip().strip("'\""))
    return {"APCA-API-KEY-ID": env["ALPACA_API_KEY"], "APCA-API-SECRET-KEY": env["ALPACA_SECRET_KEY"]}


def get(url, params):
    r = requests.get(url, params=params, headers=keys(), timeout=60)
    if r.status_code != 200:
        raise SystemExit(f"Alpaca {r.status_code} on {url}")  # never echo headers (keys)
    time.sleep(0.5)  # <= 120 req/min, well under the 200 limit
    return r.json()


def calendar():
    path = "data/intraday_calendar.pkl"
    if os.path.exists(path) and "--refresh" not in sys.argv:
        return pd.read_pickle(path)
    c = pd.DataFrame(get("https://paper-api.alpaca.markets/v2/calendar", {"start": START, "end": END}))
    c = c.set_index(pd.to_datetime(c["date"]))[["open", "close"]]
    c.to_pickle(path)
    return c


def bars(sym):
    path = f"data/intraday_{sym}.pkl"  # cache this script writes itself (data/ is gitignored)
    if os.path.exists(path) and "--refresh" not in sys.argv:
        return pd.read_pickle(path)
    rows, tok = [], None
    while True:
        p = dict(timeframe="5Min", start=START + "T00:00:00Z", end=END + "T23:59:00Z", feed="sip",
                 adjustment="all", limit=10000)
        if tok:
            p["page_token"] = tok
        j = get(f"https://data.alpaca.markets/v2/stocks/{sym}/bars", p)
        rows += j.get("bars") or []
        tok = j.get("next_page_token")
        print(f"  {sym}: {len(rows)} bars", end="\r")
        if not tok:
            break
    d = pd.DataFrame(rows).rename(columns=dict(t="ts", o="open", h="high", l="low", c="close", v="volume", vw="vw"))
    d["ts"] = pd.to_datetime(d["ts"], utc=True).dt.tz_convert("America/New_York")
    os.makedirs("data", exist_ok=True)
    d.to_pickle(path)
    return d


def sessions(d, cal):
    """Regular-session bars only: bar start in [calendar open, calendar close) on calendar days."""
    d = d.copy()
    d["date"] = d["ts"].dt.tz_localize(None).dt.normalize()
    hm = d["ts"].dt.strftime("%H:%M")
    c = cal.reindex(d["date"])
    keep = c["open"].notna().values & (hm.values >= c["open"].values) & (hm.values < c["close"].values)
    d = d[keep].reset_index(drop=True)
    d["hm"] = d["ts"].dt.strftime("%H:%M")
    # 5-min return within the session; first bar uses close/open so no overnight gap leaks into the sd
    first = d["date"] != d["date"].shift()
    d["ret"] = np.where(first, d["close"] / d["open"] - 1, d["close"] / d["close"].shift() - 1)
    d["sd20"] = d["ret"].rolling(20).std()
    return d


def trades(d, cal):
    """One row per session day: gross return of each strategy (signed, before costs), NaN = no trade."""
    out = []
    prevC, tr = np.nan, []
    for date, b in d.groupby("date", sort=True):
        o, h, l, c, hm = (b[k].to_numpy() for k in ("open", "high", "low", "close", "hm"))
        H, L, O, C = h.max(), l.min(), o[0], c[-1]
        ok = hm[0] == cal.loc[date, "open"] and len(b) >= 12 and hm[1] == "09:35"  # data-quality guard
        atr = np.mean(tr[-14:]) if len(tr) >= 14 else np.nan  # prior 14 sessions only
        row = dict(date=date, bh=C / prevC - 1, overnight=O / prevC - 1, intraday=C / O - 1)
        if ok and not np.isnan(prevC):
            # ORB: direction of bar 0 (09:30-09:35), known at 09:35 -> enter at bar 1 open
            dirn = np.sign(c[0] - o[0])
            if dirn != 0 and not np.isnan(atr):
                entry, stop = o[1], o[1] - dirn * 0.10 * atr
                ex = c[-1]
                for k in range(1, len(b)):
                    if dirn > 0 and l[k] <= stop:
                        ex = min(o[k], stop)
                        break
                    if dirn < 0 and h[k] >= stop:
                        ex = max(o[k], stop)
                        break
                g = dirn * (ex / entry - 1)
                row["ORB long-short"] = g
                row["ORB long-only"] = g if dirn > 0 else np.nan
            # Momentum: prior close -> 10:00 (close of the 09:55 bar); hold last 6 bars (15:30-16:00, or last 30m)
            i10 = np.flatnonzero(hm == "09:55")
            if len(i10) and len(b) >= 18:
                s = np.sign(c[i10[0]] / prevC - 1)
                if s != 0:
                    row["Intraday momentum (last 30m)"] = s * (c[-1] / o[-6] - 1)
            # VWAP mean reversion (long-only)
            v, vw = b["volume"].to_numpy(), b["vw"].to_numpy()
            vwap = np.cumsum(vw * v) / np.cumsum(v)
            sig = np.flatnonzero((c / vwap - 1 < -2 * b["sd20"].to_numpy())[:-1])
            if len(sig):
                k0 = sig[0] + 1
                entry, ex = o[k0], c[-1]
                for j in range(k0, len(b)):
                    if h[j] >= vwap[j - 1]:  # limit at the VWAP known when bar j opens
                        ex = max(o[j], vwap[j - 1])
                        break
                row["VWAP mean reversion"] = ex / entry - 1
            # Gap fade
            gap = O / prevC - 1
            if abs(gap) > 0.02:
                row["Gap fade"] = -np.sign(gap) * (c[-1] / o[1] - 1)
        tr.append(max(H - L, abs(H - prevC), abs(L - prevC)) if not np.isnan(prevC) else H - L)
        prevC = C
        out.append(row)
    return pd.DataFrame(out).set_index("date").iloc[15:]  # need 14d ATR history


def nw_t(x, lags=5):
    """Newey-West t-stat of the mean."""
    x = np.asarray(x, float)
    u, T = x - x.mean(), len(x)
    s = u @ u
    for lag in range(1, lags + 1):
        s += 2 * (1 - lag / (lags + 1)) * (u[lag:] @ u[:-lag])
    return x.mean() / math.sqrt(s / T**2)


def daily(g, cost, idx):
    """Net daily strategy return (0 on no-trade days) and per-trade net returns."""
    t = g.dropna() - 2 * cost
    return t.reindex(idx).fillna(0.0), t


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cal = calendar()
    T = {s: trades(sessions(bars(s), cal), cal) for s in SYMS}
    idx = T["TSLA"].index.intersection(T["QQQ"].index).intersection(T["NVDA"].index)
    yrs = len(idx) / 252
    half = idx < "2021-01-01"
    rows, series = [], {}
    for sym in SYMS:
        for st in STRATS:
            for cost in COSTS:
                r, t = daily(T[sym][st], cost, idx)
                series[(st, sym, cost)] = r
                tt = nw_t(r)
                s = stats(r)
                rows.append({
                    "Strategy": st, "Sym": sym, "Cost bp/side": cost * 1e4, "Trades": len(t),
                    "bp/trade": t.mean() * 1e4, "Hit %": (t > 0).mean() * 100, "Ann ret %": s["CAGR"] * 100,
                    "Sharpe": s["Sharpe"], "MaxDD %": s["MaxDD"] * 100, "Turnover x/yr": 2 * len(t) / yrs,
                    "t (NW5)": tt, "p": pval(tt), "bp/day 16-20": r[half].mean() * 1e4,
                    "bp/day 21-26": r[~half].mean() * 1e4})
    R = pd.DataFrame(rows)
    R["Holm p"] = holm(R["p"]).values
    pos5 = {(a, b): series[(a, b, 0.0005)].mean() > 0 for a in STRATS for b in SYMS}
    R["Pass"] = [(h < 0.05) and (t > 0) and (a > 0) and (b > 0) and pos5[(st, sym)]
                 for h, t, a, b, st, sym in zip(R["Holm p"], R["t (NW5)"], R["bp/day 16-20"], R["bp/day 21-26"],
                                                R["Strategy"], R["Sym"])]

    # Baselines (descriptive, not in the Holm family)
    base = []
    for sym in SYMS:
        for name, col, legs in [("Buy & hold (close-close)", "bh", 0), ("Overnight only (close->open)", "overnight", 2),
                                ("Intraday only (open->close)", "intraday", 2)]:
            for cost in ([0.0] if legs == 0 else COSTS):
                r = T[sym][col].reindex(idx).fillna(0) - legs * cost
                series[(name, sym, cost)] = r
                s, tt = stats(r), nw_t(r)
                base.append({"Baseline": name, "Sym": sym, "Cost bp/side": cost * 1e4, "Ann ret %": s["CAGR"] * 100,
                             "Sharpe": s["Sharpe"], "MaxDD %": s["MaxDD"] * 100, "t (NW5)": tt,
                             "bp/day 16-20": r[half].mean() * 1e4, "bp/day 21-26": r[~half].mean() * 1e4})
    B = pd.DataFrame(base)

    # Paired stationary bootstrap: P(Sharpe_strategy <= Sharpe_TSLA buy & hold), base cost
    bi = stationary_bootstrap_idx(len(idx), 2000)
    bh = series[("Buy & hold (close-close)", "TSLA", 0.0)].to_numpy()[bi]
    sb = sharpe_rows(bh)
    boot = []
    for (st, sym, cost), r in series.items():
        if cost != 0.0002:
            continue
        x = r.to_numpy()[bi]
        sx = sharpe_rows(x)
        sx = np.where(np.isfinite(sx), sx, -np.inf)
        boot.append({"Strategy": st, "Sym": sym, "Sharpe": stats(r)["Sharpe"],
                     "Sharpe 95% CI": f"{np.percentile(sx, 2.5):.2f} to {np.percentile(sx, 97.5):.2f}",
                     "P(Sharpe <= TSLA B&H)": (sx <= sb).mean()})
    BS = pd.DataFrame(boot)

    npass = int(R["Pass"].sum())
    f = lambda df: df.to_markdown(index=False, floatfmt=".2f")
    md = f"""# Intraday trading study (TSLA, with QQQ and NVDA as checks)

Generated by intraday_study.py on {pd.Timestamp.today():%Y-%m-%d}. Alpaca SIP 5-minute bars, {idx[0]:%Y-%m-%d} to
{idx[-1]:%Y-%m-%d}, {len(idx)} common sessions. Regular session only (calendar open/close, so half days end at 13:00).
Bar timestamps are bar starts; a signal from bar k trades at bar k+1's open or later. 1x notional, no leverage,
cost charged per side on entry and exit (2 bp base, 5 bp stress). Daily series are 0 on no-trade days.

**Pre-registered strategies** (fixed before results, no tuning): ORB = first 5-min bar direction, enter 09:35 open,
stop at 10% of the prior-14-session ATR (fill at the stop, or at the bar open if it gaps through), exit at the close.
Momentum = sign(prior close -> 10:00), hold the last 30 minutes. VWAP MR = close > 2 sd (20-bar 5-min return sd)
below session VWAP -> buy next open, exit at the VWAP touch (limit at the VWAP known at bar open) or the close; one
trade/day. Gap fade = |gap| > 2% -> fade at 09:35, exit at the close.

**Test:** Newey-West (5 lags) t on the daily net return; Holm over all {len(R)} strategy x symbol x cost tests.
Pass = Holm p < 0.05, positive, same sign in 2016-2020 and 2021-2026, and positive at 5 bp.
Turnover = traded notional / capital per year (2 sides per trade).

## Results

{f(R.drop(columns="p"))}

**{npass} of {len(R)} pass.**

## Baselines (descriptive, not in the Holm family)

{f(B)}

## Paired stationary bootstrap vs buy & hold TSLA (2 bp, 2,000 resamples, mean block 20 days)

{f(BS)}

## Caveats

- **Survivorship / selection:** TSLA was picked knowing it became one of the largest, most volatile stocks of the decade.
  Its buy & hold Sharpe is the bar here, and that bar is itself a lucky draw. Anything that "beats" it is suspect.
- **One stock, one decade:** intraday results on a single name hinge on a few hundred extreme days (TSLA's 2020 run,
  2022 drawdown). QQQ and NVDA are the out-of-symbol check; a real edge should show up on them too.
- **Execution:** fills assume the bar open / stop / VWAP level with a flat per-side cost. Real TSLA opens are
  wide and fast; stops in fast markets slip beyond the level. 2 bp/side is optimistic at 09:35, 5 bp is closer to
  realistic for market orders right after the open.
- **Adjusted prices** (adjustment=all) are used throughout; this does not affect intraday returns.
"""
    os.makedirs("reports", exist_ok=True)
    open("reports/intraday_results.md", "w", encoding="utf-8").write(md)
    pd.set_option("display.width", 250)
    print(R.drop(columns=["p"]).round(2).to_string())
    print(B.round(2).to_string())
    print(BS.to_string())
    print(f"{npass} of {len(R)} pass")


if __name__ == "__main__":
    main()
