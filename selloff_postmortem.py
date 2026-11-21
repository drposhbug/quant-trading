"""Post-mortem of the Oct-Nov 2026 selloff. DESCRIPTIVE ONLY: nothing here is a test that can change the frozen model
(MATH.md change control). The variant rows are hindsight on one episode; the full-sample columns beside them show what
each variant costs or earns over the whole backtest. Run: python selloff_postmortem.py -> reports/selloff_postmortem_results.md
"""
import numpy as np
import pandas as pd

from backtest import stats
from leverage_study import ENG, frame, load
from model import BENCH, P, backtest_returns, load_prices, names_of, target_weights

OUT = "reports/selloff_postmortem_results.md"
PEAK, END = "2026-10-06", "2026-11-20"
HORIZONS = (21, 63, 126, 252)


def fast_drops(px, depth=-0.15, max_days=45):
    """First close at or below `depth` from the running peak, kept only if that peak was <= max_days sessions earlier.
    One event per peak: the next event needs a new high first. Returns [(peak_date, event_date)]."""
    peak = px.cummax()
    dd = px / peak - 1
    out, armed = [], True
    for i in range(len(px)):
        if dd.iloc[i] == 0:
            armed = True
        elif armed and dd.iloc[i] <= depth:
            armed = False  # one per peak, whether or not it was fast
            j = int(np.flatnonzero(px.values[: i + 1] == peak.iloc[i])[-1])
            if i - j <= max_days:
                out.append((px.index[j], px.index[i]))
    return out


def _check():
    s = pd.Series([100, 110, 90, 80, 120, 119, 100, 130.0], index=pd.date_range("2000-01-03", periods=8, freq="B"))
    ev = fast_drops(s, -0.15, 45)
    assert [(a.day, b.day) for a, b in ev] == [(4, 5), (7, 11)], ev  # 110->90 once (not again at 80), 120->100
    assert fast_drops(s, -0.15, 0) == []  # speed filter


def pct(x):
    return "-" if pd.isna(x) else f"{x:+.1%}"


def table(rows, cols):
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def episode(px):
    """Frozen model and hindsight variants: Oct 6 - Nov 20 episode vs the full backtest window."""
    names = names_of(px)
    r = px[names].ffill().pct_change()
    ew = r.where(px[names].notna()).mean(axis=1)
    arms = {
        "QQQ buy & hold": px[BENCH].pct_change(),
        "Equal-weight basket, fully invested": ew,
        "**Frozen model** (20% vol, halve below 200d)": backtest_returns(px, target_weights(px)),
        "No 200-day rule": backtest_returns(px, target_weights(px, {**P, "regime_scale": 1.0})),
        "Full exit below 200d": backtest_returns(px, target_weights(px, {**P, "regime_scale": 0.0})),
        "Vol target 15%": backtest_returns(px, target_weights(px, {**P, "vol_target": 0.15})),
        "Vol target 25%": backtest_returns(px, target_weights(px, {**P, "vol_target": 0.25})),
    }
    full_start = px.index[px.index >= "2015-03-31"][0]
    rows = []
    for k, x in arms.items():
        e = x[(x.index > PEAK) & (x.index <= END)]
        f = stats(x[x.index >= full_start].fillna(0))
        eq = (1 + e).cumprod()
        rows.append([k, pct(eq.iloc[-1] - 1), pct(min(0, (eq / eq.cummax().clip(lower=1) - 1).min())), pct(e.iloc[-2:].add(1).prod() - 1),
                     pct(f["CAGR"]), pct(f["MaxDD"]), f"{f['Sharpe']:.2f}"])
    return table(rows, ["Arm", "Oct 6 – Nov 20", "Worst drawdown in episode", "Nov 19–20", "Full-sample CAGR", "Full-sample MaxDD", "Sharpe"])


def exposure(px):
    w = target_weights(px)
    g = w.sum(axis=1)
    q = px[BENCH]
    d = pd.DataFrame({"QQQ vs peak": q / q.cummax() - 1, "QQQ vs 200d": q / q.rolling(200).mean() - 1, "Model gross": g,
                      "Semis (NVDA+AMD+AVGO+TSM)": w[["NVDA", "AMD", "AVGO", "TSM"]].sum(axis=1)})
    d = d[(d.index >= PEAK) & (d.index <= END)]
    keep = d.index[::5].union(d.index[d.index >= "2026-11-02"])  # every session in November: the 200-day crossings are day-by-day
    return table([[i.date()] + [f"{v:+.1%}" if c.startswith("QQQ") else f"{v:.0%}" for c, v in d.loc[i].items()] for i in keep],
                 ["Close", *d.columns]), g


def analogs(max_days=45):
    """^NDX since 1985: drops of >=15% from a peak within max_days sessions. What buy & hold and the frozen engine
    (run on the index) did next. Events with no completed 21-day forward window (the current one) are left out."""
    ndx = load()["px"]["^NDX"].dropna()
    f = frame(ndx)
    eng = (1 + backtest_returns(f, target_weights(f, ENG))).cumprod()
    rows, fw = [], {h: ([], []) for h in HORIZONS}
    for a, b in fast_drops(ndx, max_days=max_days):
        i = ndx.index.get_loc(b)
        if i < 260 or i + HORIZONS[0] >= len(ndx):
            continue  # engine warm-up
        later = ndx.iloc[i:]
        rec = later.index[later >= ndx.loc[a]]
        low = later.iloc[:253].min() / ndx.loc[b] - 1
        cells = []
        for h in HORIZONS:
            if i + h < len(ndx):
                x, y = ndx.iloc[i + h] / ndx.iloc[i] - 1, eng.iloc[i + h] / eng.iloc[i] - 1
                fw[h][0].append(x), fw[h][1].append(y)
                cells.append(f"{x:+.0%} / {y:+.0%}")
            else:
                cells.append("-")
        rows.append([a.date(), b.date(), len(ndx.loc[a:b]) - 1, pct(ndx.loc[b] / ndx.loc[a] - 1), pct(low),
                     f"{(rec[0] - a).days / 365.25:.1f}y" if len(rec) else "not yet", *cells])
    summ = [[f"{h}d", len(fw[h][0]), pct(np.median(fw[h][0])), f"{np.mean(np.array(fw[h][0]) > 0):.0%}", pct(min(fw[h][0])),
             pct(np.median(fw[h][1])), f"{np.mean(np.array(fw[h][1]) > 0):.0%}", pct(min(fw[h][1]))] for h in HORIZONS]
    return (table(rows, ["Peak", "−15% hit", "Sessions", "Drop at hit", "Further low within 1y", "Peak regained after",
                         *[f"+{h}d hold / engine" for h in HORIZONS]]),
            table(summ, ["Horizon", "n", "Hold median", "Hold % up", "Hold worst", "Engine median", "Engine % up", "Engine worst"]))


def shipped_after(px):
    """The shipped 12-name book after each QQQ -15% hit since 2015 (any speed). Hindsight universe: the names were picked
    knowing they won, so read the model-vs-basket gap, not the level."""
    names = names_of(px)
    r = px[names].ffill().pct_change()
    arms = {"QQQ": px[BENCH].pct_change(), "Equal-weight basket": r.where(px[names].notna()).mean(axis=1),
            "Frozen model": backtest_returns(px, target_weights(px))}
    eq = {k: (1 + v.fillna(0)).cumprod() for k, v in arms.items()}
    q = px[BENCH].dropna()
    rows = []
    for a, b in fast_drops(q[q.index >= "2015-03-31"], max_days=10**6):
        i = px.index.get_loc(b)
        if i + 126 >= len(px):
            continue
        cells = []
        for h in (63, 126, 252):
            cells.append(" / ".join(f"{eq[k].iloc[i + h] / eq[k].iloc[i] - 1:+.0%}" for k in arms) if i + h < len(px) else "-")
        g = target_weights(px).sum(axis=1)
        back = g.iloc[i:][g.iloc[i:] >= 0.8]
        rows.append([a.date(), b.date(), f"{g.iloc[i]:.0%}", f"{(back.index[0] - b).days} days" if len(back) else "not yet", *cells])
    return table(rows, ["QQQ peak", "-15% hit", "Model gross at hit", "Back above 80% gross after", "+63d QQQ / basket / model",
                        "+126d QQQ / basket / model", "+252d QQQ / basket / model"])


def main():
    _check()
    px = load_prices(start="2014-01-01")
    px = px[px.index <= END]
    ep = episode(px)
    ex, g = exposure(px)
    sh = shipped_after(px)
    ev, summ = analogs()
    _, summ_all = analogs(max_days=10**6)
    basket_1120 = px[names_of(px)].pct_change().loc[END]
    w = target_weights(px)
    miss = (0.46 - w.loc["2026-11-19"].sum()) * (w.loc["2026-11-19"] / w.loc["2026-11-19"].sum() * basket_1120).sum()
    open(OUT, "w", encoding="utf-8").write(f"""# Selloff post-mortem: Oct 6 – Nov 20, 2026

Generated by `selloff_postmortem.py`. Descriptive only. The variant rows are hindsight on a single episode and are
**not** evidence for changing the frozen model; read each against its full-sample columns.

## The model through the episode

{ep}

"Nov 19–20" is the two sessions the paper account was live. The account's own result was −5.0% (bought at the 11-19
open at ~46% gross; the 11-19 afternoon rebalance never ran).

## Exposure path

{ex}

Model gross at the 11-19 close: {g.loc['2026-11-19']:.0%}. The account held ~46% into Friday because Thursday's rebalance was
missed; on Friday's moves that cost about {miss:+.2%} of equity.

## This model after QQQ's earlier 15% drops (shipped universe, 2015–2026)

{sh}

The names were chosen knowing they won, so the levels flatter everything; the comparison between the columns is the
point. The model gives up part of each rebound in exchange for a smaller loss on the way down.

## What happened after similar drops (^NDX, 1985–2026)

Event: first close 15% or more below the running peak, reached within 45 sessions of that peak (this episode: QQQ −19.9%
in 33 sessions). One event per peak. "Engine" is the frozen risk engine run on the index itself (price only, cash earns 0).

{ev}

{summ}

Same event without the speed filter (adds slower declines such as 2008, 2018 and 2022):

{summ_all}

Small samples. In the fast-drop table the engine kept roughly half of the rebound in the V-shaped recoveries and lost
about a third as much as holding in 2000. Treat the medians as a description of history, not a forecast.
""")
    print(open(OUT, encoding="utf-8").read())


if __name__ == "__main__":
    main()
