"""Earnings-announcement premium on the point-in-time S&P 500 (STUDY ONLY: the live model is frozen, MATH.md).
Writes reports/earnings_premium_results.md.  Run: python earnings_premium_study.py

Pre-registered (fixed before any result was seen; nothing below is tuned):
  Events   8-K Item 2.02 acceptance times (SEC EDGAR) per company; reaction day = same session if accepted before
           09:30 ET else next session; days 1-5 of Jan/Apr/Jul/Oct dropped (delivery reports); one event per 10 days
           (events_study.reaction_days).
  E        expected date = prior-year reaction day + 364 calendar days, rolled forward to a trading day. Known a year
           ahead, so no lookahead. Every past event spawns one expected date.
  Trade    buy at close of E-5 (trading days) if the company is an S&P member on the lagged list and has not already
           reported in the 25 sessions up to entry; sell at close of the first actual reaction day after entry, or
           at E+5 if none. Equal weight over held names, rebalanced daily; idle -> T-bill (^IRX/100/252).
  Costs    5 bp per side on turnover (stress 10 bp). Benchmark basket charged nothing.
  Primary  sleeve daily return minus equal-weight point-in-time S&P 500 basket, 2017-01-01 .. latest, Newey-West
           t (5 lags). PASS iff t > 3.0 AND same sign 2017-2021 vs 2022-2026 AND mean excess > 0 at 10 bp.
  Second.  per-trade residual vs 60d SPY beta (known at entry), by size tercile (trailing 60d dollar volume rank
           among members at entry). Reported, not selected on.
  Mix      80% frozen model (target_weights on the 12 names + T-bills on idle cash, as live) + 20% sleeve, daily
           rebalanced, vs 100% frozen model: paired stationary bootstrap P(mix Sharpe <= model), P(mix MaxDD worse);
           2017+ and 2016+.
  Data     daily returns clipped at +/-40%; -100% delisting return for SIVB/SBNY/FRC on the session after their
           last bar (only matters if held); a held name with no price that day earns 0 (acquisition at deal price).
"""
import collections
import json
import os
import time

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from backtest import prices, sharpe_rows, stationary_bootstrap_idx, stats
from correlations import pval
from events_study import UA, _filings, reaction_days, season_t
from model import target_weights
from universe_data import load_universe
from universe_study import cash_yield

D = "data/earnings_premium"
FAILED = ["SIVB", "SBNY", "FRC"]  # seizures: last bar overstates the outcome (universe_data_quality.md)
BAR, LAGS, CLIP = 3.0, 5, 0.40
PRE, POST, NOREPORT = 5, 5, 25


def _get(url, params=None):
    for k in range(5):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=30)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(2 * (k + 1))
    return None


# ---------------------------------------------------------------- company id -> SEC CIK(s)
# Hand fixes for ids where the press-release search below is ambiguous (short or reused tickers). Checked by
# company name only (the display name EDGAR returns), never against returns.
# Drops are a second company that merely mentions the ticker (acquirer, spin-off, peer); adds are ids the search
# missed, verified against data.sec.gov submissions names. SBNY filed with the FDIC, not the SEC: no events.
CIK_FIX = {"CHK": [895126], "DAY": [1725057], "DO": [949039], "KSU": [54480], "MAC": [912242], "PENN": [921738],
           "POM": [1135971], "SE": [1373835], "SNDK@2016": [1000180], "ZION": [109380], "JEF": [96223],
           "AABA": [1011006], "BBBY": [886158], "DISCK": [1437107], "FRC": [1132979], "GT": [42582],
           "HRS": [202058], "KDP@2018": [1418135], "KORS": [1530721], "LLTC": [791907], "M": [794367],
           "POOL": [945841], "RHI": [315213], "TWX": [1105705], "UAA": [1336917], "URBN": [912615],
           "WFM": [865436], "WYND": [1361658], "AMTM": [2011286]}


def ciks(ids, chains, current):
    """id -> list of CIKs. Current members: SEC company_tickers.json. Every id: EDGAR full-text search of 8-Ks for
    '"NYSE: SYM"' / '"Nasdaq: SYM"' inside the symbol's own date spell (press releases name their ticker);
    CIKs with >= 25% of hits and >= 5 hits are kept (catches predecessor CIKs after holding-company reorgs)."""
    p = f"{D}/ciks.json"
    if os.path.exists(p):
        out = json.load(open(p))
    else:
        out = {}
    tk = _get("https://www.sec.gov/files/company_tickers.json")
    tk = {v["ticker"].replace("-", "").replace(".", ""): v["cik_str"] for v in tk.values()}
    for n, i in enumerate(ids):
        if i in out:
            continue
        cand, names = collections.Counter(), {}
        for sym, a, b in chains[i]:
            lo = max(pd.Timestamp(a), pd.Timestamp("2014-01-01"))
            hi = min(pd.Timestamp(b) if b is not None else pd.Timestamp.today(), pd.Timestamp.today())
            if hi <= lo:
                continue
            for ex in ("NYSE", "Nasdaq"):
                r = _get("https://efts.sec.gov/LATEST/search-index",
                         dict(q=f'"{ex}: {sym}"', forms="8-K", dateRange="custom",
                              startdt=str(lo.date()), enddt=str(hi.date())))
                time.sleep(0.15)
                for h in (r or {}).get("hits", {}).get("hits", []):
                    c = int(h["_source"]["ciks"][0])
                    cand[c] += 1
                    names[c] = h["_source"]["display_names"][0]
        tot = sum(cand.values())
        fts = [c for c, k in cand.most_common() if k >= 5 and k >= 0.25 * tot]
        cur = [tk[i.split("@")[0].replace(".", "")]] if current.get(i) and i.split("@")[0].replace(".", "") in tk else []
        out[i] = dict(cur=cur, fts=fts, names={str(c): names[c] for c in fts}, tot=tot)
        if n % 25 == 0:
            json.dump(out, open(p, "w"), indent=0)
            print(f"ciks {n}/{len(ids)}", flush=True)
    json.dump(out, open(p, "w"), indent=0)
    res = {}
    for i, v in out.items():
        if i in CIK_FIX:
            res[i] = CIK_FIX[i]
        elif v["cur"]:  # current member: its own CIK + FTS CIKs that EDGAR lists under one of its symbols
            syms = {s for s, _, _ in chains[i]}
            res[i] = v["cur"] + [c for c in v["fts"] if c not in v["cur"] and
                                 any(f"({s}" in v["names"][str(c)] or f", {s}" in v["names"][str(c)] for s in syms)]
        else:
            res[i] = v["fts"]
    return res, out


def earnings_events(idmap, idx):
    """Item 2.02 8-K acceptance times for every CIK, cached; -> reaction days per id."""
    p = f"{D}/edgar_202.csv"
    have = pd.read_csv(p) if os.path.exists(p) else pd.DataFrame(columns=["cik", "ts"])
    done = set(pd.read_csv(f"{D}/ciks_done.csv").cik) if os.path.exists(f"{D}/ciks_done.csv") else set()
    todo = sorted({c for cs in idmap.values() for c in cs} - done)
    rows = []
    for n, c in enumerate(todo):
        try:
            f = _filings(c)
            f = f[(f.form == "8-K") & f["items"].str.contains("2.02", regex=False)]
            rows += [dict(cik=c, ts=t) for t in f.acceptanceDateTime]
            done.add(c)
        except Exception as e:  # noqa: BLE001 - one bad CIK should not stop the run; it is reported as missing
            print("fail", c, e)
        time.sleep(0.15)
        if n % 50 == 49 or n == len(todo) - 1:
            have = pd.concat([have, pd.DataFrame(rows, columns=["cik", "ts"])])
            rows = []
            have.to_csv(p, index=False)
            pd.DataFrame({"cik": sorted(done)}).to_csv(f"{D}/ciks_done.csv", index=False)
            print(f"filings {n + 1}/{len(todo)}", flush=True)
    have["ts"] = pd.to_datetime(have.ts, utc=True).dt.tz_convert("America/New_York")
    f = pd.DataFrame([(i, t) for i, cs in idmap.items() for c in cs for t in have.ts[have.cik == c]],
                     columns=["name", "ts"])
    return reaction_days(f, idx)


def dollar_volume(ids, chains, idx):
    bars = pd.read_pickle("data/universe/alpaca_bars.pkl")
    out = {}
    for i in ids:
        parts = []
        for sym, a, b in chains[i]:
            if sym in bars:
                x = bars[sym]
                x = (x.close * x.volume)[(x.index >= pd.Timestamp(a)) & ((b is None) | (x.index < pd.Timestamp(b or "2100")))]
                parts.append(x)
        if parts:
            s = pd.concat(parts)
            out[i] = s[~s.index.duplicated(keep="last")]
    return pd.DataFrame(out).reindex(index=idx, columns=ids).rolling(60, min_periods=40).mean()


def nw_mean_t(y, lags=LAGS):
    u = np.asarray(y, float) - np.mean(y)
    s2 = u @ u / len(u)
    for l in range(1, lags + 1):
        s2 += 2 * (1 - l / (lags + 1)) * (u[l:] @ u[:-l]) / len(u)
    return np.mean(y) / np.sqrt(s2 / len(u))


def maxdd_rows(x):
    eq = np.cumprod(1 + x, axis=1)
    return (eq / np.maximum.accumulate(eq, axis=1) - 1).min(axis=1)


def main():
    os.makedirs(D, exist_ok=True)
    px, mem = load_universe()
    idx = px.index
    chains = pd.read_pickle("data/universe/chains.pkl")
    ids = list(mem.columns[mem.loc["2016-01-01":].any()])
    px, mem = px[ids], mem[ids]
    memL = mem.shift(1, fill_value=False)  # list known at close t = yesterday's list

    idmap, raw = ciks(ids, chains, mem.iloc[-1].to_dict())
    ev = earnings_events(idmap, idx)

    # returns: clip, then explicit delisting returns
    r = px.pct_change(fill_method=None).clip(-CLIP, CLIP)
    for i in FAILED:
        last = px[i].last_valid_index()
        r.loc[idx[idx.get_loc(last) + 1], i] = -1.0
    R = r.values
    irx = yf.download("^IRX", start="2009-12-01", progress=False, auto_adjust=True)["Close"].squeeze()
    rf = (irx.reindex(idx).ffill().fillna(0) / 100 / 252)
    spy = pd.read_pickle("data/universe/alpaca_bars.pkl")["SPY"].close.reindex(idx).pct_change(fill_method=None)

    # trades
    pos = {d: k for k, d in enumerate(idx)}
    col = {i: k for k, i in enumerate(ids)}
    rx = {i: np.array(sorted(pos[d] for d in g.day)) for i, g in ev.groupby("name")}
    H = np.zeros((len(idx), len(ids)), bool)  # H[t, j]: name j earns its return on day t
    trades = []
    T = len(idx)
    for i, rp in rx.items():
        j = col[i]
        for k in rp:
            E = idx.searchsorted(idx[k] + pd.Timedelta(days=364))
            s = E - PRE
            if s >= T - 1 or s < 60:
                continue
            if not memL.values[s, j] or np.isnan(px.values[s, j]):
                continue
            if ((rp >= s - NOREPORT) & (rp <= s)).any():  # already reported this quarter: nothing to hold through
                continue
            after = rp[(rp > s) & (rp <= E + POST)]
            x = min(after[0] if len(after) else E + POST, T - 1)
            H[s + 1:x + 1, j] = True
            trades.append(dict(name=i, entry=idx[s], exit=idx[x], E=idx[min(E, T - 1)], hit=len(after) > 0, s=s, x=x))
    tr = pd.DataFrame(trades)

    n = H.sum(1)
    W = np.where(n[:, None] > 0, H / np.maximum(n, 1)[:, None], 0.0)
    gross = np.where(n > 0, np.nansum(np.where(H, np.nan_to_num(R), 0), 1) / np.maximum(n, 1), rf.values)
    turn = np.abs(np.diff(W, axis=0, prepend=0)).sum(1)  # weights for day t are set at close t-1: charged on day t
    sleeve = {c: pd.Series(gross - turn * c / 1e4, idx) for c in (5, 10)}
    B = memL.shift(1, fill_value=False).values  # basket for day t is chosen at close t-1 from the list known then
    basket = pd.Series(np.nanmean(np.where(B, R, np.nan), 1), idx)

    sl = slice("2017-01-01", None)
    ex = {c: (sleeve[c] - basket)[sl].dropna() for c in (5, 10)}
    e5 = ex[5]
    t_main = nw_mean_t(e5.values)
    h1, h2 = e5[:"2021-12-31"], e5["2022-01-01":]
    t1, t2 = nw_mean_t(h1.values), nw_mean_t(h2.values)
    t10 = nw_mean_t(ex[10].values)
    passed = t_main > BAR and np.sign(h1.mean()) == np.sign(h2.mean()) and ex[10].mean() > 0
    by_year = pd.DataFrame({"excess 5bp (%/yr)": e5.groupby(e5.index.year).mean() * 252 * 100,
                            "days invested": pd.Series(n > 0, idx)[sl].groupby(idx[idx >= "2017-01-01"].year).sum()})

    # secondary: per-trade residual vs 60d SPY beta known at entry, by size tercile
    dv = dollar_volume(ids, chains, idx)
    dvr = dv.where(memL).rank(axis=1, pct=True).values
    S = spy.values
    res = []
    for t in tr.itertuples():
        j = col[t.name]
        a, b = R[t.s - 59:t.s + 1, j], S[t.s - 59:t.s + 1]
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() < 40:
            continue
        beta = np.cov(a[ok], b[ok])[0, 1] / np.var(b[ok], ddof=1)
        ri, rs = np.nan_to_num(R[t.s + 1:t.x + 1, j]), np.nan_to_num(S[t.s + 1:t.x + 1])
        q = dvr[t.s, j]
        res.append(dict(day=t.exit, resid=np.prod(1 + ri) - 1 - beta * (np.prod(1 + rs) - 1),
                        size="small" if q <= 1 / 3 else "mid" if q <= 2 / 3 else "large" if q == q else "n/a"))
    res = pd.DataFrame(res)
    res = res[res.day >= "2017-01-01"]
    sec = []
    for g, d in [("all", res)] + [(k, res[res["size"] == k]) for k in ("small", "mid", "large")]:
        m, t, nq, m1, m2 = season_t(d.resid.values, d.day)
        sec.append({"group": g, "trades": len(d), "quarters": nq, "mean resid (bp/trade)": m * 1e4, "t (quarters, NW1)": t,
                    "1st half": m1 * 1e4, "2nd half": m2 * 1e4})
    sec = pd.DataFrame(sec)

    # mix test
    px12 = prices()
    model = cash_yield(px12, irx)[0]
    mix_rows = []
    for lab, start in [("2017-01-01 ..", "2017-01-01"), ("2016-01-04 ..", "2016-01-04")]:
        st = max(pd.Timestamp(start), px12.index[300])
        m_ = model.loc[st:]
        s_ = sleeve[5].reindex(m_.index).fillna(rf.reindex(m_.index).fillna(0))
        mix = 0.8 * m_ + 0.2 * s_
        bi = stationary_bootstrap_idx(len(m_), 2000)
        Sm, Sx = sharpe_rows(m_.values[bi]), sharpe_rows(mix.values[bi])
        Dm, Dx = maxdd_rows(m_.values[bi]), maxdd_rows(mix.values[bi])
        for name, x in [("100% frozen model", m_), ("80% model + 20% sleeve", mix)]:
            mix_rows.append(dict(window=f"{st.date()} .. {m_.index[-1].date()}", portfolio=name, **stats(x)))
        mix_rows[-1].update({"P(mix Sharpe <= model)": (Sx <= Sm).mean(), "P(mix MaxDD worse)": (Dx < Dm).mean()})
    mix_tab = pd.DataFrame(mix_rows)

    perf = pd.DataFrame({k: stats(v[sl].dropna()) for k, v in
                         [("Sleeve 5bp", sleeve[5]), ("Sleeve 10bp", sleeve[10]), ("EW S&P 500 basket", basket)]}).T
    hit = tr[tr.entry >= "2017-01-01"]
    noev = [i for i in ids if not idmap.get(i)]
    noev_member = [i for i in noev if mem.loc["2017-01-01":, i].any()]
    cnt_ev = ev[ev.day >= "2016-01-01"]
    verdict = "PASS" if passed else "FAIL"

    out = [
        "# Earnings-announcement premium, point-in-time S&P 500\n",
        f"Generated by earnings_premium_study.py on {idx[-1].date()}. **Study only**: the live model is frozen "
        "(MATH.md, Change control); nothing here changes it. Design fixed before the run (module docstring).\n",
        f"## Verdict: **{verdict}**\n",
        f"Primary test (one test): sleeve minus equal-weight point-in-time S&P 500, daily, {e5.index[0].date()} .. "
        f"{e5.index[-1].date()}, Newey-West t ({LAGS} lags). Bar: t > {BAR}, same sign in both halves, positive at 10 bp.\n",
        "| | mean excess (%/yr) | NW t |\n|---|---:|---:|",
        f"| Full, 5 bp | {e5.mean() * 252 * 100:.2f} | {t_main:.2f} |",
        f"| 2017-2021, 5 bp | {h1.mean() * 252 * 100:.2f} | {t1:.2f} |",
        f"| 2022-2026, 5 bp | {h2.mean() * 252 * 100:.2f} | {t2:.2f} |",
        f"| Full, 10 bp | {ex[10].mean() * 252 * 100:.2f} | {t10:.2f} |",
        f"\nt > {BAR}: {t_main > BAR}; same sign halves: {np.sign(h1.mean()) == np.sign(h2.mean())}; "
        f"positive at 10 bp: {ex[10].mean() > 0}.\n",
        "## Sleeve vs basket (2017+)\n",
        perf.to_markdown(floatfmt=".3f"),
        f"\nTrades entered 2017+: {len(hit)} ({hit.hit.mean() * 100:.0f}% saw an actual announcement inside "
        f"(E-5, E+5]); mean names held on invested days {n[(idx >= '2017-01-01') & (n > 0)].mean():.1f}; "
        f"invested on {(n[idx >= '2017-01-01'] > 0).mean() * 100:.0f}% of days. Median holding "
        f"{int((hit.x - hit.s).median())} sessions.\n",
        by_year.to_markdown(floatfmt=".2f"),
        "\n## Secondary (reported, not selected on): per-trade residual vs 60d SPY beta\n",
        "Residual = compounded holding-period return minus beta x SPY's, beta from the 60 sessions to entry. Size = "
        "trailing 60d dollar volume percentile among members at entry (market cap is not point-in-time). t: trades "
        "averaged per calendar quarter, Newey-West 1 lag over quarters (events_study.season_t). Costs not deducted.\n",
        sec.to_markdown(index=False, floatfmt=".2f"),
        "\n## Mix test: 80% frozen model + 20% sleeve vs 100% frozen model\n",
        "Frozen model = model.target_weights on the 12 names with idle cash in T-bills (as live). Daily rebalanced "
        "mix, sleeve at 5 bp; paired stationary bootstrap (2,000 paths, mean block 20 days).\n",
        mix_tab.to_markdown(index=False, floatfmt=".3f"),
        "\n## Events and data\n",
        f"- {len(ids)} company ids were S&P 500 members at some point from 2016; {len(ids) - len(noev)} mapped to at "
        f"least one SEC CIK; {len(cnt_ev)} Item 2.02 reaction days from 2016 on ({ev.name.nunique()} companies). "
        f"No CIK (no events, never traded): {len(noev_member)} ids that were members 2017+: "
        f"{', '.join(noev_member) or 'none'}.",
        "- CIK mapping: current members from SEC company_tickers.json; every id (and predecessor CIKs) via EDGAR "
        "full-text search for '\"NYSE: SYM\"' / '\"Nasdaq: SYM\"' in 8-Ks during the symbol's own date spell (a CIK "
        "needs >= 25% and >= 5 of the hits). Short or reused tickers can map wrongly or not at all; a wrong CIK "
        "adds unrelated filings, which mostly produce expected dates with no announcement (held 10 days, no earnings "
        "exposure) and dilute the sleeve toward the basket.",
        "- Expected dates need the prior-year event, so a company's first year in the data, and quarters it moved by "
        "more than ~5 sessions, are not traded or are held through no announcement.",
        "- Item 2.02 also covers pre-announcements and some non-earnings releases; 8-K acceptance can lag a press "
        "release (reaction day one session late; the trade then exits a day late, which still holds the release).",
        "- Returns: Alpaca adjusted closes (load_universe), clipped at +/-40%; -100% on the session after the last "
        "bar for SIVB/SBNY/FRC. Held names without a price that day earn 0. Unadjusted spin-offs of ex-members "
        "remain as clipped fake drops.",
        "- Costs: turnover x 5 bp (10 bp stress) on the equal-weight sleeve; daily drift rebalancing and the T-bill "
        "leg are free; the mix's rebalancing between model and sleeve is free. Benchmark basket is cost-free.",
        "- One test, pre-registered; the t > 3.0 bar reflects ~700 earlier tests in this project (Harvey-Liu-Zhu).",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/earnings_premium_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
