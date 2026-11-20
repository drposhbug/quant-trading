"""Pre-registered study: is the frozen risk engine at leverage L more reliable than buy & hold across 6 indices?
Pre-registration: top of reports/leverage_results.md. Writes that report. The live model is NOT changed.

Run: python leverage_study.py            (downloads to data/leverage_px.pkl on first run)
     python leverage_study.py --refresh
"""
import os
import sys

import numpy as np
import pandas as pd
import yfinance as yf

from backtest import pbo_cscv, prices, sharpe_rows, stationary_bootstrap_idx, stats
from model import BENCH, P, target_weights, backtest_returns

CACHE = "data/leverage_px.pkl"
OUT = "reports/leverage_results.md"
MARKETS = {"^GSPC": "1950-01-01", "^NDX": "1985-10-01", "^N225": "1965-01-01",
           "^GDAXI": "1988-01-01", "^FTSE": "1985-01-01", "^HSI": "1987-01-01"}
DIV = {"^GSPC": 0.030, "^NDX": 0.008, "^N225": 0.013, "^GDAXI": 0.0, "^FTSE": 0.038, "^HSI": 0.033}  # crude long-run avgs
LS = (1.0, 1.25, 1.5, 2.0)
BASE, STRESS = dict(spread=0.015, cost=5.0), dict(spread=0.03, cost=10.0)
WARM = 252
B = 2000
ENG = {**P, "cap": 1.0}  # one-asset engine: the 25% per-name cap is for a stock basket; at 25% one index can't reach 20% vol
EVENTS = {"2000": ("1999-07-01", "2000-12-31"), "2008": ("2007-01-01", "2008-08-31"),
          "2022": ("2021-07-01", "2022-03-31"), "Nikkei 1990": ("1989-01-01", "1990-03-31")}


VERDICT = """
## Verdict (written after the 2026-11-20 run; numbers above are deterministic, seeded)

**No L passes.** L = 1.5 comes closest: under base assumptions it beats buy & hold on both CAGR and MaxDD in 5 of 6
markets including the Nikkei (fails the FTSE), and its worst 10-year CAGR is better than holding on the Nikkei and the
S&P. But the pooled Sharpe test fails (P = 0.095), and under stress financing (T-bill + 3%) and 10 bp it wins in only
3 markets (S&P, Nasdaq, Hang Seng; on the Nikkei its CAGR drops below holding, 7.6% vs 7.8%). L = 1.25 fails (a)
(4 of 6) and passes (b) only in base (P = 0.044; 0.25 under stress).
L = 2.0 fails everything that involves the Nikkei: −86% MaxDD vs −77% for holding, 34 years underwater.
L = 1.0 has the best risk-adjusted numbers (pooled P = 0.011) and the smallest drawdowns everywhere, but lower CAGR
than holding in 5 of 6 markets: it is a safer way to hold, not a higher-return one.

What is robust: the engine's drawdown control is real at every L ≤ 1.5 across six markets and five decades
(and survives a 1-day regime lag and vol windows 20/120). What is not: turning that into *more return than holding*
needs leverage whose financing cost eats the gain outside a strong uptrend; the Nasdaq result is the best case.
"""


def load():
    # pickle is our own cache written below from yfinance/FRED, never downloaded as a pickle
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_pickle(CACHE)
    px = yf.download(list(MARKETS) + ["QLD", "SSO", "QQQ", "SPY", "^IRX"], start="1950-01-01",
                     auto_adjust=True, progress=False, threads=False)["Close"]
    tb3 = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS", index_col=0, parse_dates=True).iloc[:, 0]
    d = {"px": px, "tb3": tb3}
    os.makedirs("data", exist_ok=True)
    pd.to_pickle(d, CACHE)
    return d


def rf_daily(d, index):
    """^IRX (13-week bill, %), FRED TB3MS monthly before ^IRX starts (1960). Daily = annual / 252."""
    irx = d["px"]["^IRX"].dropna()
    s = pd.concat([d["tb3"][d["tb3"].index < irx.index[0]], irx]).sort_index()
    return s.reindex(s.index.union(index)).ffill().reindex(index).fillna(0) / 100 / 252


def run(px, w, rf, spread, cost, dy=0.0):
    """Daily net return: model.backtest_returns (price P&L - cost x turnover) + T-bill on idle cash - (T-bill + spread)
    on borrowed exposure + dividend yield x exposure. Exposure held over day t = gross weight set at close t-1."""
    r = backtest_returns(px, w, cost)
    ex = w.reindex(r.index).fillna(0).sum(axis=1).shift(1).fillna(0)
    return r + (1 - ex).clip(lower=0) * rf - (ex - 1).clip(lower=0) * (rf + spread / 252) + ex * dy / 252


def frame(s, lag=0):
    """Single-index engine input: the index is both the traded name and the regime benchmark (its own 200d MA)."""
    return pd.DataFrame({"IDX": s, BENCH: s.shift(lag)})


def const_w(px, k, start):
    return pd.DataFrame({"IDX": np.where(px.index >= start, k, 0.0)}, index=px.index)


def engine_w(px, L, start, p=ENG):
    w = target_weights(px, p) * L
    w.loc[w.index < start] = 0.0  # everyone enters from cash on the same day
    return w


def underwater_years(r):
    eq = (1 + r).cumprod()
    peak_date = eq.index.to_series().where(eq >= eq.cummax() * (1 - 1e-12)).ffill()
    return (eq.index.to_series() - peak_date).dt.days.max() / 365.25


def roll10(r):
    eq = (1 + r).cumprod()
    past = eq.reindex(eq.index - pd.DateOffset(years=10), method="ffill").values
    return pd.Series((eq.values / past) ** 0.1 - 1, index=eq.index).dropna()


def recovery(r, a, b):
    """Peak inside [a, b] -> years until equity first regains it (None = not yet), and the drawdown depth."""
    eq = (1 + r).cumprod()
    win = eq.loc[a:b]
    if len(win) == 0 or eq.index[0] > pd.Timestamp(a):
        return None
    pv = win.max()
    pd_ = win[win >= pv * (1 - 1e-12)].index[-1]  # last day at the peak
    after = eq.loc[pd_:].iloc[1:]
    back = after[after >= pv * (1 - 1e-12)]
    depth = (after.loc[:back.index[0]] if len(back) else after).min() / pv - 1
    return ((back.index[0] - pd_).days / 365.25 if len(back) else None), depth


def boot_paths(T, n, B_, L, rng):
    """Stationary-bootstrap index paths of length n drawn from a sample of length T (mean block L)."""
    idx = np.empty((B_, n), dtype=np.int64)
    idx[:, 0] = rng.integers(0, T, B_)
    for t in range(1, n):
        jump = rng.random(B_) < 1 / L
        idx[:, t] = np.where(jump, rng.integers(0, T, B_), (idx[:, t - 1] + 1) % T)
    return idx


def metrics(r, rf):
    s = stats(r)
    r10 = roll10(r)
    return dict(CAGR=s["CAGR"], Vol=s["Vol"], SharpeX=stats(r - rf)["Sharpe"], MaxDD=s["MaxDD"],
                UnderY=underwater_years(r), Worst10y=r10.min(), P10yLoss=(r10 < 0).mean())


def market(d, tk, spread, cost, dy, lag=0, vol_win=60, extra=True):
    """All arms for one index over the same evaluation days. Returns dict name -> daily returns, and rf."""
    s = d["px"][tk].dropna().loc[MARKETS[tk]:]
    px = frame(s, lag)
    start = px.index[WARM]
    rf = rf_daily(d, px.index)
    p = {**ENG, "vol_win": vol_win}
    R = {"Hold 1x": run(px, const_w(px, 1.0, start), rf, spread, cost, dy)}
    if extra:
        for k in (1.5, 2.0):
            R[f"Naive {k:g}x"] = run(px, const_w(px, k, start), rf, spread, cost, dy)
    for L in LS:
        R[f"Engine L={L}"] = run(px, engine_w(px, L, start, p), rf, spread, cost, dy)
    return {k: v.loc[start:] for k, v in R.items()}, rf.loc[start:]


def boot_sharpe_diff(R, rf, keys, rng_seed=0):
    """Paired stationary bootstrap (backtest.stationary_bootstrap_idx, L=20): per-draw excess Sharpe of each key minus
    hold's. Returns array (B, len(keys)). Chunked to bound memory."""
    X = np.column_stack([(R[k] - rf).values for k in ["Hold 1x"] + keys])
    out = []
    for _ in range(B // 200):
        idx = stationary_bootstrap_idx(len(X), 200)
        S = np.column_stack([sharpe_rows(X[:, j][idx]) for j in range(X.shape[1])])
        out.append(S[:, 1:] - S[:, :1])
    return np.vstack(out)


def criteria(res, boots):
    """res[tk] = metrics table (DataFrame), boots[tk] = (B, len(LS)) Sharpe diffs. Returns per-L pass dict."""
    out = {}
    pooled = np.mean([boots[tk] for tk in MARKETS], axis=0)
    for j, L in enumerate(LS):
        e = f"Engine L={L}"
        wins = {tk: bool(res[tk].loc[e, "CAGR"] > res[tk].loc["Hold 1x", "CAGR"]
                         and res[tk].loc[e, "MaxDD"] > res[tk].loc["Hold 1x", "MaxDD"]) for tk in MARKETS}
        a = sum(wins.values()) >= 5 and wins["^N225"]
        pb = float((pooled[:, j] <= 0).mean())
        c = all(res[tk].loc[e, "Worst10y"] >= res[tk].loc["Hold 1x", "Worst10y"] for tk in ("^N225", "^GSPC"))
        out[L] = dict(wins=wins, a=a, p=pb, b=pb < 0.05, c=c, all=a and pb < 0.05 and c)
    return out


def pct(x):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.1%}"


def fmt_table(df):
    t = df.copy()
    for c in ("CAGR", "Vol", "MaxDD", "Worst10y", "P10yLoss"):
        t[c] = t[c].map(pct)
    t["SharpeX"] = t["SharpeX"].map("{:.2f}".format)
    t["UnderY"] = t["UnderY"].map("{:.1f}".format)
    return t.rename(columns={"SharpeX": "Sharpe (ex T-bill)", "UnderY": "Longest underwater (y)",
                             "Worst10y": "Worst 10y CAGR", "P10yLoss": "Share of 10y windows < 0"}).to_markdown()


def main():
    d = load()
    rng = np.random.default_rng(11)
    L_md = []
    scen = {"base": (BASE, True), "stress": (STRESS, True), "price-only": (BASE, False)}
    res, boots, rets, rfs, crit = {}, {}, {}, {}, {}
    for sc, (cfg, divs) in scen.items():
        res[sc], boots[sc] = {}, {}
        for tk in MARKETS:
            R, rf = market(d, tk, cfg["spread"], cfg["cost"], DIV[tk] if divs else 0.0)
            res[sc][tk] = pd.DataFrame({k: metrics(v, rf) for k, v in R.items()}).T
            boots[sc][tk] = boot_sharpe_diff(R, rf, [f"Engine L={L}" for L in LS])
            if sc == "base":
                rets[tk], rfs[tk] = R, rf
            print(sc, tk, "done", flush=True)
        crit[sc] = criteria(res[sc], boots[sc])

    # ---- decision ----
    L_md += ["## Decision (pre-registered criteria)\n",
             "| L | (a) wins of 6 (CAGR>hold AND MaxDD better) | Nikkei win | (b) pooled P(Sharpe ≤ hold) | (c) worst 10y ≥ hold on N225 & GSPC | base pass | (d) stress: a / b (P) / c | **PASS** | price-only (a/b/c) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for L in LS:
        b_, s_, po = crit["base"][L], crit["stress"][L], crit["price-only"][L]
        yn = lambda x: "yes" if x else "no"
        L_md.append(f"| {L} | {sum(b_['wins'].values())} ({', '.join(t for t, w in b_['wins'].items() if w) or 'none'}) "
                    f"| {yn(b_['wins']['^N225'])} | {b_['p']:.3f} | {yn(b_['c'])} | {yn(b_['all'])} "
                    f"| {yn(s_['a'])} / {yn(s_['b'])} ({s_['p']:.3f}) / {yn(s_['c'])} "
                    f"| **{'PASS' if b_['all'] and s_['all'] else 'FAIL'}** "
                    f"| {yn(po['a'])}/{yn(po['b'])}/{yn(po['c'])} |")
    L_md.append("")

    # ---- per-market tables ----
    L_md.append("## Per-market results (base: T-bill + 1.5%, 5 bp, approx. dividends)\n")
    for tk in MARKETS:
        R = rets[tk]
        first = R["Hold 1x"].index[0].date()
        L_md += [f"### {tk} ({first} → {R['Hold 1x'].index[-1].date()}, dividend {DIV[tk]:.1%})\n",
                 fmt_table(res["base"][tk]), ""]
        L_md.append("Stress (T-bill + 3%, 10 bp): " + "; ".join(
            f"{k}: CAGR {pct(v['CAGR'])}, MaxDD {pct(v['MaxDD'])}"
            for k, v in res["stress"][tk].iterrows() if k.startswith("Engine") or k == "Hold 1x") + "\n")

    # ---- drawdown recoveries ----
    L_md += ["## Recovery time after each crash (years from the pre-crash peak back to it; depth in brackets)\n",
             "| Market | Event | " + " | ".join(rets["^GSPC"]) + " |", "|---|---|" + "---|" * len(rets["^GSPC"])]
    for tk in MARKETS:
        for ev, (a, b) in EVENTS.items():
            if (ev == "Nikkei 1990") != (tk == "^N225"):
                continue
            cells = []
            for k, r in rets[tk].items():
                x = recovery(r, a, b)
                cells.append("n/a" if x is None else f"{'not yet' if x[0] is None else f'{x[0]:.1f}'} ({x[1]:.0%})")
            if any(c != "n/a" for c in cells):
                L_md.append(f"| {tk} | {ev} | " + " | ".join(cells) + " |")
    L_md.append("")

    # ---- forward 10y paths ----
    keys = ["Hold 1x", "Naive 2x"] + [f"Engine L={L}" for L in LS]
    n10 = 2520
    TW = {k: [] for k in keys}
    for tk in MARKETS:
        X = np.column_stack([np.log1p(rets[tk][k].values) for k in keys])
        idx = boot_paths(len(X), n10, B, 250, rng)
        for j, k in enumerate(keys):
            TW[k].append(np.exp(X[:, j][idx].sum(axis=1)))
    L_md += ["## 10-year forward paths (stationary bootstrap, mean block 250 d, 2,000 paths per market, paired; "
             "pooled = all 6 markets equally weighted)\n",
             "| Arm | median terminal wealth | 5th pct | 95th pct | P(lose money over 10y) | P(beat hold on same path) |",
             "|---|---|---|---|---|---|"]
    hold_all = np.concatenate(TW["Hold 1x"])
    for k in keys:
        tw = np.concatenate(TW[k])
        L_md.append(f"| {k} | {np.median(tw):.2f}x | {np.percentile(tw, 5):.2f}x | {np.percentile(tw, 95):.2f}x "
                    f"| {(tw < 1).mean():.1%} | {'—' if k == 'Hold 1x' else f'{(tw > hold_all).mean():.1%}'} |")
    L_md += ["", "Per market, P(lose money over 10y) bootstrap (hold / L=1 / L=1.5 / L=2 / naive 2x): "]
    for i, tk in enumerate(MARKETS):
        L_md.append(f"- {tk}: " + " / ".join(f"{(TW[k][i] < 1).mean():.1%}" for k in
                                              ["Hold 1x", "Engine L=1.0", "Engine L=1.5", "Engine L=2.0", "Naive 2x"]))
    L_md.append("")

    # ---- sensitivity ----
    L_md += ["## Sensitivity (report only): CAGR / MaxDD, base costs\n",
             "| Market | Variant | Hold | L=1.0 | L=1.5 | L=2.0 |", "|---|---|---|---|---|---|"]
    pbo_rows = []
    for tk in MARKETS:
        M = []
        for name, kw in [("frozen (vol 60, regime same day)", {}), ("regime 1 day late", dict(lag=1)),
                         ("vol window 20", dict(vol_win=20)), ("vol window 120", dict(vol_win=120))]:
            R, rf = market(d, tk, BASE["spread"], BASE["cost"], DIV[tk], extra=False, **kw)
            cell = lambda k: f"{pct(stats(R[k])['CAGR'])} / {pct(stats(R[k])['MaxDD'])}"
            L_md.append(f"| {tk} | {name} | {cell('Hold 1x')} | {cell('Engine L=1.0')} | {cell('Engine L=1.5')} "
                        f"| {cell('Engine L=2.0')} |")
            M += [(R[f"Engine L={L}"] - rf).values for L in LS]
        pbo_rows.append(f"{tk} {pbo_cscv(np.column_stack(M)):.2f}")
    L_md += ["", "PBO (CSCV, S = 16) over the 16 engine variants (4 L × 4 settings) per market, excess returns: "
             + ", ".join(pbo_rows) + ". L mostly rescales the same bet, so this mainly says whether the choice"
             " among near-identical variants is stable.\n"]

    # ---- ETF check ----
    px = d["px"]
    etf = []
    for lev, und in (("QLD", "QQQ"), ("SSO", "SPY")):
        s = px[[lev, und]].dropna()
        rf = rf_daily(d, s.index)
        pe = pd.DataFrame({lev: s[lev], BENCH: s[und]})  # regime on the underlying, as the frozen model does
        pu = frame(s[und])
        start = s.index[WARM]
        R = {f"{lev} hold": run(pe, const_w(pu, 1.0, start).rename(columns={"IDX": lev}), rf, 0, 5),
             f"Synthetic 2x {und} (T-bill+1.5%, study model)": run(pu, const_w(pu, 2.0, start), rf, 0.015, 5),
             f"Synthetic 2x {und} (T-bill + 0.95% fee)": run(pu, const_w(pu, 2.0, start), rf, 0.0, 5)
             - (s.index >= start) * 0.0095 / 252,
             f"{und} hold": run(pu, const_w(pu, 1.0, start), rf, 0, 5)}
        for L in (1.5, 2.0):
            w = target_weights(pe, {**ENG, "vol_target": P["vol_target"] * L}) * 1.0  # 1 unit of 2x ETF = 2x economic
            w.loc[w.index < start] = 0
            R[f"{lev} inside engine (vol target {P['vol_target'] * L:.0%}, max 1 unit = 2x)"] = run(pe, w, rf, 0, 5)
            R[f"Engine L={L} on {und}, synthetic financing"] = run(pu, engine_w(pu, L, start), rf, 0.015, 5)
        R = {k: v.loc[start:] for k, v in R.items()}
        rr = rf.loc[start:]
        tab = pd.DataFrame({k: metrics(v, rr) for k, v in R.items()}).T
        etf.append(f"### {lev} vs synthetic 2x {und} ({start.date()} → {s.index[-1].date()})\n")
        etf.append(fmt_table(tab))
        real = R[f"{lev} hold"]
        for k in [k for k in R if k.startswith("Synthetic")]:
            td = stats(real)["CAGR"] - stats(R[k])["CAGR"]
            te = (real - R[k]).std() * np.sqrt(252)
            etf.append(f"\n- {lev} minus {k}: tracking difference {td:+.2%}/yr, tracking error {te:.2%}/yr")
        etf.append("")
    L_md += ["## Real 2x ETFs vs the synthetic leverage used above (report only)\n"] + etf

    # ---- shipped 12-name universe ----
    px12 = prices()
    start = px12.index[P["trend_long"] + P["vol_win"]]
    extra_irx = rf_daily(d, px12.index)
    w0 = target_weights(px12)
    pq = frame(px12[BENCH])
    R12 = {"QQQ hold": run(pq, const_w(pq, 1.0, start), extra_irx, 0, 5)}
    for L in (1.0, 1.5):
        w = w0 * L
        w.loc[w.index < start] = 0
        R12[f"Frozen model L={L}"] = run(px12, w, extra_irx, BASE["spread"], BASE["cost"])
        R12[f"Frozen model L={L}, stress"] = run(px12, w, extra_irx, STRESS["spread"], STRESS["cost"])
    R12 = {k: v.loc[start:] for k, v in R12.items()}
    rr = extra_irx.loc[start:]
    t12 = pd.DataFrame({k: metrics(v, rr) for k, v in R12.items()}).T
    idx = stationary_bootstrap_idx(len(rr), B)
    S = {k: sharpe_rows((v - rr).values[idx]) for k, v in R12.items()}
    dd = lambda x: ((c := np.cumprod(1 + x, axis=1)) / np.maximum.accumulate(c, axis=1) - 1).min(axis=1)
    p15 = (S["Frozen model L=1.5"] - S["Frozen model L=1.0"] <= 0).mean()
    pdd = (dd(R12["Frozen model L=1.5"].values[idx]) <= dd(R12["QQQ hold"].values[idx])).mean()
    L_md += [f"## Shipped 12-name universe ({start.date()} → {rr.index[-1].date()}, frozen P incl. 25% caps; "
             "T-bill on idle cash, T-bill + spread on borrowing)\n", fmt_table(t12), "",
             f"Paired bootstrap: P(Sharpe L=1.5 ≤ L=1.0) = {p15:.3f}; P(MaxDD L=1.5 worse than QQQ) = {pdd:.3f}. "
             "Selection bias (MATH.md §7) inflates both levels; only the L comparison is meaningful.\n"]

    with open(OUT, encoding="utf-8") as f:
        prereg = f.read().split("\n## Decision")[0].rstrip()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(prereg + "\n\n" + "\n".join(L_md) + "\n" + VERDICT)
    print("\n".join(L_md))


if __name__ == "__main__":
    main()
