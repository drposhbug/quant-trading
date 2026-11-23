"""Selling rules: can the book sell near the peak and end with more money? Writes reports/exit_odds.md.
Run: python exit_odds.py

The owner's ask (2026-11-23): "decide through the market so that you sell at the peak too".
Written before the first run. Same method as growth_odds.py / tilt_odds.py: P = share of 2,000 paired
stationary-bootstrap histories (L = 20) in which the arm's mean log return is higher. Every arm is the CURRENT live
book (monitor.tilted: inverse-vol, fully invested, long-trend tilt, 5 bp costs) with one selling rule per stock on
top. What is sold sits in T-bills (^IRX) until the rule lets it back in. All rules use closes only, known that day.
  stop 20%        out of a stock while it is more than 20% below its highest close of the past year; back in above that
  stop 10%        the same at 10%
  stretch trim    half weight while a stock is more than 25% above its 200-day average
  jump trim       half weight for 21 sessions after a one-day gain of 15% or more
  new-high trim   half weight while a stock is within 3% of its one-year high (the literal "sell at the peak")
Decision: add a selling rule to the live book only if, on the end-2014 list (names chosen without hindsight),
P(arm grows faster than the live book) >= 0.90 over the whole window AND > 0.5 in each half, AND >= 0.5 on the
shipped list. If several qualify, the highest whole-window P. Otherwise no selling rule is added.
Reported, not deciding: worst drawdown and Sharpe (what a selling rule buys if it does not buy growth), and what each
arm did from the 2026-10-06 peak to 2026-11-23.
"""
import numpy as np
import pandas as pd

from backtest import prices
from growth_odds import odds
from model import BENCH, P, backtest_returns, load_prices, names_of
from monitor import tilted
from universe_study import TECH10_2014, load_extra


def arms(px):
    w, c = tilted(px), px[names_of(px)].ffill()
    dd = c / c.rolling(252, min_periods=60).max() - 1
    stretch = c / c.rolling(200).mean() - 1
    jumped = (c.pct_change() >= 0.15).astype(float).rolling(21).max()
    return {"stop 20%": w.where(dd > -0.20, 0.0), "stop 10%": w.where(dd > -0.10, 0.0),
            "stretch trim": w * np.where(stretch > 0.25, 0.5, 1.0), "jump trim": w * np.where(jumped > 0, 0.5, 1.0),
            "new-high trim": w * np.where(dd > -0.03, 0.5, 1.0)}


def ret(px, w, rf):
    """Net daily return with T-bills on whatever is not in stocks."""
    return backtest_returns(px, w) + (1 - w.sum(axis=1)).shift(1).fillna(0) * rf.reindex(px.index).ffill().fillna(0)


def main():
    px = prices()
    start = px.index[P["trend_long"] + P["vol_win"]]
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    rf = extra["^IRX"].ffill() / 100 / 252
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    cut = px14.iloc[:-250]  # no lookahead: weights at a date do not change when later prices are added
    for name, w in arms(cut).items():
        assert np.allclose(w.iloc[-1], arms(px14)[name].loc[cut.index[-1]], atol=1e-9), f"lookahead in {name}"
        assert (w <= tilted(cut) + 1e-12).all().all(), f"{name} buys instead of only selling"

    rows = {}
    for uni, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        live = ret(data, tilted(data), rf).loc[start:]
        mid = live.index[len(live) // 2]
        for name, w in arms(data).items():
            a = ret(data, w, rf).loc[start:]
            o, p = odds(a, live), lambda x, y: odds(x, y)["P(arm grows faster)"]
            rows[(name, uni)] = {"P vs live": o["P(arm grows faster)"], "P 1st half": p(a[:mid], live[:mid]),
                                 "P 2nd half": p(a[mid:], live[mid:]), "CAGR arm": o["CAGR arm"], "CAGR live": o["CAGR base"],
                                 "MaxDD arm": o["MaxDD arm"], "MaxDD live": o["MaxDD base"], "Sharpe arm": o["Sharpe arm"],
                                 "Sharpe live": o["Sharpe base"], "avg invested": w.sum(axis=1).loc[start:].mean()}
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {u}" for a, u in t.index]
    ok = {}
    for name in dict.fromkeys(a for a, _ in rows):
        d, s = t.loc[f"{name} | end-2014 list (decides)"], t.loc[f"{name} | shipped list (reported)"]
        if d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5:
            ok[name] = d["P vs live"]
    verdict = f"add **{max(ok, key=ok.get)}** to the live book" if ok else "**no selling rule is added**: none clears the bar"

    now = load_prices(start="2024-06-01")  # fresh prices for the episode table (the backtest cache stops earlier)
    now = now[now.index <= "2026-11-23"]
    ep = lambda w: (1 + ret(now, w, rf).loc["2026-10-07":"2026-11-23"]).prod() - 1
    fall = lambda w: (1 + ret(now, w, rf).loc["2026-10-07":"2026-11-20"]).prod() - 1
    e = pd.DataFrame({k: {"6 Oct to 20 Nov (the fall)": fall(w), "6 Oct to 23 Nov (with the rebound)": ep(w),
                          "invested on 20 Nov": w.loc["2026-11-20"].sum()} for k, w in {"live book": tilted(now), **arms(now)}.items()}).T
    out = ["# Selling rules: decision odds, 2026-11-23\n", "Rules written in exit_odds.py before the run. 'live' = the current book.\n",
           t.to_markdown(floatfmt=".3f"), f"\n- Decision: {verdict}\n", "## This dip, shipped list (reported)\n", e.to_markdown(floatfmt=".3f")]
    with open("reports/exit_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    main()
