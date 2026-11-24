"""Holding less of the names that magnify selloffs: does the book lose less? Writes reports/downside_beta_odds.md.
Run: python downside_beta_odds.py

Grok's "other lenses" review (2026-11-23, research_notes/Smarter machine 2026-11-23/9): the tests so far asked which
stocks do better; a different question is which stocks fall hardest when the market falls, which repeats (rank
correlation 0.40 between a stock's reaction on its last ten shock days and the next one). Written before the run.
- Downside sensitivity of a stock: over the last 252 sessions, using only the days the market (QQQ) fell more than
  1%, the stock's fall per 1% of market fall. Needs at least 15 such days. Known at each close.
- The amplifiers: the third of the book's names with the highest downside sensitivity that day.
- Every arm is the live book (monitor.tilted, 5 bp costs) with one rule on top; what is sold sits in T-bills.
    trim amplifiers after a shock   half weight in the amplifiers for 21 sessions after any market shock day
                                    (QQQ moving more than 2.5 of its normal daily moves either way)
    trim amplifiers always          half weight in the amplifiers at all times
    half after shock                half of everything for 21 sessions after a shock: tested already
                                    (news_stop_odds.py), repeated here on the same days as the yardstick
- Bars, the same two as news_stop_odds.py. 1: belongs in the live book only if P(arm grows faster) >= 0.90 on the
  end-2014 list, > 0.5 in each half, >= 0.5 on the shipped list. 2: loses less only if the worst fall is smaller
  on both lists; then it is a trade-off for the owner, reported with its cost in growth.
- The question this answers: does trimming only the amplifiers buy the same protection as halving everything,
  for less growth given up? That is judged by worst fall saved per point of yearly growth lost, on both lists.
"""
import numpy as np
import pandas as pd

import growth_odds
from daily_calls import bars
from growth_odds import odds
from model import BENCH, P, UNIVERSE, backtest_returns, names_of
from monitor import tilted
from news_stop_odds import signals, worst
from universe_study import TECH10_2014


def downside(px):
    """Each stock's fall per 1% of market fall on the market's down days of the last 252 sessions."""
    q, c = px[BENCH].ffill().pct_change(), px[names_of(px)].ffill().pct_change()
    qd = q.where(q < -0.01)
    num, den = c.mul(qd, axis=0).rolling(252, min_periods=15).sum(), (qd ** 2).rolling(252, min_periods=15).sum()
    return num.div(den, axis=0)


def main():
    names = sorted(set(UNIVERSE) | set(TECH10_2014))
    b = bars(names + [BENCH, "BIL"])
    rf = b["c"]["BIL"].ffill().pct_change().fillna(0)
    rows, p = {}, lambda x, y: odds(x, y)["P(arm grows faster)"]
    for uni, lst in {"end-2014 list (decides)": TECH10_2014, "shipped list (reported)": UNIVERSE}.items():
        cols = [n for n in lst if n in b["c"]] + [BENCH]
        px, op, vol = b["c"][cols], b["o"][cols], b["v"][[n for n in cols if n != BENCH]]
        w, rfx = tilted(px), rf.reindex(b["c"].index).fillna(0)
        cash = lambda wt: backtest_returns(px, wt) + (1 - wt.sum(axis=1)).shift(1).fillna(0) * rfx
        amp = downside(px).rank(axis=1, pct=True) > 2 / 3
        after = signals(px, op, vol)["any"].astype(float).rolling(21, min_periods=1).max() > 0
        wide = pd.DataFrame({k: after for k in w.columns})
        arms = {"live book": w, "trim amplifiers after a shock": w * np.where(amp & wide, 0.5, 1.0), "trim amplifiers always": w * np.where(amp, 0.5, 1.0),
                "half after shock": w * np.where(wide, 0.5, 1.0)}
        start = px.index[P["trend_long"] + P["vol_win"] + 126 + 252]
        live = cash(w).loc[start:]
        mid = live.index[len(live) // 2]
        for k, wt in arms.items():
            a = cash(wt).loc[start:]
            growth_odds.rng = np.random.default_rng(7)
            o = odds(a, live)
            rows[(k, uni)] = {"P vs live": np.nan if k == "live book" else o["P(arm grows faster)"], "P 1st half": np.nan if k == "live book" else p(a[:mid], live[:mid]),
                              "P 2nd half": np.nan if k == "live book" else p(a[mid:], live[mid:]), "growth a year": o["CAGR arm"], "worst fall": o["MaxDD arm"],
                              "worst session": worst(a, 1), "worst 21 sessions": worst(a, 21), "Sharpe": o["Sharpe arm"], "average invested": wt.sum(axis=1).loc[start:].mean()}
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {u}" for a, u in t.index]
    out, notes = ["# Holding less of the names that magnify selloffs\n", "Rules written in downside_beta_odds.py before the run. Alpaca daily bars; the same days as news_stop_odds.py.\n",
                  t.to_markdown(floatfmt=".3f"), ""], []
    for k in ("trim amplifiers after a shock", "trim amplifiers always", "half after shock"):
        d, s = t.loc[f"{k} | end-2014 list (decides)"], t.loc[f"{k} | shipped list (reported)"]
        l1, l2 = t.loc["live book | end-2014 list (decides)"], t.loc["live book | shipped list (reported)"]
        ok = d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5
        less = d["worst fall"] > l1["worst fall"] and s["worst fall"] > l2["worst fall"]
        saved, cost = (d["worst fall"] - l1["worst fall"], s["worst fall"] - l2["worst fall"]), (l1["growth a year"] - d["growth a year"], l2["growth a year"] - s["growth a year"])
        notes.append(f"- **{k}**: live book by the standing bar: {'yes' if ok else 'no'}. Loses less on both lists: {'yes' if less else 'no'} "
                     f"(worst fall smaller by {saved[0]:.1%} and {saved[1]:.1%}; growth a year lower by {cost[0]:.1%} and {cost[1]:.1%}).")
    with open("reports/downside_beta_odds.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out + notes) + "\n")
    print("\n".join(out + notes))


if __name__ == "__main__":
    main()
