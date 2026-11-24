"""Seeing the news and closing out: does the book lose less, and what does it cost? Writes reports/news_stop_odds.md.
Run: python news_stop_odds.py

The owner's ask (2026-11-23): "can you just minimize loss by seeing the news and closing out so it's not as bad".
Written before the first run. The bot cannot read a headline faster than the market does, so "seeing the news" is
measured the way the bot would see it: the market or a stock suddenly moving far more than its normal. "Normal" is
the standard deviation of the last 60 daily moves, known before the day. Every arm is the CURRENT live book
(monitor.tilted: inverse-vol, fully invested, long-trend tilt, 5 bp costs) with one rule on top. What is sold sits
in T-bills (BIL). Prices: Alpaca adjusted daily bars from 2016, so that opening prices are on the same basis.
  close stop        the market (QQQ) closes down more than 2.5 normal moves: out of everything at that close, back in
                    at the close 5 sessions later
  gap stop          the market opens more than 2 normal moves below its last close: out of everything at that open,
                    back in at the close 4 sessions after that day
  half after shock  the market moves more than 2.5 normal moves either way: half the book for the next 21 sessions
  stock stop        a stock falls more than 3 of its own normal moves against the market on more than twice its
                    normal volume: that stock is sold at that close, back in 5 sessions later
  tilt off, shock   for 21 sessions after any market shock the book keeps its stocks but drops the trend tilt
  tilt off, wild    the book drops the trend tilt while the tilt's own bet (tilted minus untilted return) has been
                    more volatile over the last 126 sessions than its median of the last 504
Two questions, two rules, both fixed here.
1. Does it belong in the live book? The standing bar for any change (exit_odds.py): on the end-2014 list, P(arm grows
   faster than the live book) >= 0.90 over the whole window and > 0.5 in each half, and >= 0.5 on the shipped list.
2. Does it lose less, and at what price? For every arm: worst fall from a peak, worst single session, worst 21
   sessions, and growth a year, beside the live book's. An arm that loses less but grows slower is reported as a
   trade-off for the owner to choose; it is not added on its own. An arm counts as "loses less" only if its worst
   fall is smaller on BOTH lists.
Reported, not deciding: how much of a market shock day's fall had already happened at the open, and what the market
did in the 5 sessions after each kind of stop fired.
"""
import numpy as np
import pandas as pd

import growth_odds
from daily_calls import bars
from growth_odds import LIVE, odds
from model import BENCH, P, UNIVERSE, backtest_returns, names_of, target_weights
from monitor import tilted
from universe_study import TECH10_2014

CASH = "BIL"


def signals(px, op, vol):
    """Everything the rules look at, each known at the moment named."""
    q = px[BENCH].ffill()
    r, sd = q.pct_change(), q.pct_change().rolling(60).std().shift(1)
    c = px[names_of(px)].ffill()
    rel = c.pct_change().sub(r, axis=0)
    rel_sd, vn = rel.rolling(60).std().shift(1), vol / vol.rolling(60).mean().shift(1)
    return {"down": r / sd < -2.5, "any": (r / sd).abs() > 2.5, "gap": (op[BENCH] / q.shift(1) - 1) / sd < -2.0,
            "stock": (rel / rel_sd < -3) & (vn > 2)}


def arms(px, op, vol, rf):
    """{arm: daily net return}. Weights set at a close earn from that close to the next."""
    s, w, plain, c = signals(px, op, vol), tilted(px), target_weights(px, LIVE), px[names_of(px)].ffill()
    held = lambda flag, n: flag.astype(float).rolling(n, min_periods=1).max() > 0  # true for n closes from the trigger
    swap = lambda off: w.where(~pd.DataFrame({k: off for k in w.columns}).fillna(False), plain)  # tilt dropped on those days
    rf = rf.reindex(px.index).fillna(0)
    cash = lambda wt: backtest_returns(px, wt) + (1 - wt.sum(axis=1)).shift(1).fillna(0) * rf
    live = cash(w)
    out = {"live book": live,
           "close stop": cash(w.mul((~held(s["down"], 5)).astype(float), axis=0)),
           "half after shock": cash(w.mul(np.where(held(s["any"], 21), 0.5, 1.0), axis=0)),
           "stock stop": cash(w.where(~held(s["stock"], 5), 0.0)),
           "tilt off, shock": cash(swap(held(s["any"], 21)))}
    bet = live - cash(plain)
    wild = bet.rolling(126).std() > bet.rolling(126).std().rolling(504, min_periods=252).median()
    out["tilt off, wild"] = cash(swap(wild))
    # gap stop: out at the open of the gap day, so that day earns only the step from the last close to the open
    g = held(s["gap"], 4)
    wg = w.mul((~g).astype(float), axis=0)
    night = (op[names_of(px)] / c.shift(1) - 1).fillna(0)
    day = c.pct_change().fillna(0)
    first = s["gap"] & ~g.shift(1, fill_value=False)  # the day the stop fires while still holding the book
    fix = ((w.shift(1).fillna(0) * (night - day)).sum(axis=1) + rf).where(first, 0.0)
    out["gap stop"] = cash(wg) + fix
    return out, s


def worst(r, n):
    return ((1 + r).rolling(n).apply(np.prod, raw=True) - 1).min() if n > 1 else r.min()


def main():
    names = sorted(set(UNIVERSE) | set(TECH10_2014))
    b = bars(names + [BENCH, CASH])
    rf = b["c"][CASH].ffill().pct_change().fillna(0)
    rows, facts, ok, less = {}, [], {}, {}
    p = lambda x, y: odds(x, y)["P(arm grows faster)"]
    for uni, lst in {"end-2014 list (decides)": TECH10_2014, "shipped list (reported)": UNIVERSE}.items():
        cols = [n for n in lst if n in b["c"]] + [BENCH]
        px, op, vol = b["c"][cols], b["o"][cols], b["v"][[n for n in cols if n != BENCH]]
        cut = len(px) - 250  # no lookahead: an arm's returns up to a date do not change when later prices are added
        early, late = arms(px.iloc[:cut], op.iloc[:cut], vol.iloc[:cut], rf)[0], arms(px, op, vol, rf)
        for k in early:
            assert np.allclose(early[k].iloc[:-1], late[0][k].iloc[:cut - 1], atol=1e-9, equal_nan=True), f"lookahead in {k}"
        ret, s = late
        start = px.index[P["trend_long"] + P["vol_win"] + 126 + 252]  # once the trend, the volatility and the "wild" median all have data
        live = ret["live book"].loc[start:]
        mid = live.index[len(live) // 2]
        for k, a in ret.items():
            a = a.loc[start:]
            growth_odds.rng = np.random.default_rng(7)
            o = odds(a, live)
            rows[(k, uni)] = {"P vs live": np.nan if k == "live book" else o["P(arm grows faster)"],
                              "P 1st half": np.nan if k == "live book" else p(a[:mid], live[:mid]),
                              "P 2nd half": np.nan if k == "live book" else p(a[mid:], live[mid:]),
                              "growth a year": o["CAGR arm"], "worst fall": o["MaxDD arm"], "worst session": worst(a, 1),
                              "worst 21 sessions": worst(a, 21), "Sharpe": o["Sharpe arm"]}
        if uni.startswith("end-2014"):
            q, o_, sig = px[BENCH].ffill(), op[BENCH], signals(px, op, vol)
            dn = sig["down"].loc[start:]
            dn = dn[dn].index
            full, gap = q.pct_change().loc[dn], (o_ / q.shift(1) - 1).loc[dn]
            nxt = lambda idx, h: (q.shift(-h) / q - 1).loc[idx].dropna()
            gp = sig["gap"].loc[start:]
            gp = gp[gp].index
            rest = (q / o_ - 1).loc[gp]
            facts += [f"- Market shock-down days since {start.date()}: {len(dn)}. On those days the market fell {full.mean():.1%} on average; "
                      f"{gap.mean() / full.mean():.0%} of that had already happened at the open, before any stop could act.",
                      f"- In the 5 sessions after a close stop fired, the market returned {nxt(dn, 5).mean():+.2%} on average and was up {np.mean(nxt(dn, 5) > 0):.0%} of the time "
                      f"(any 5 sessions: {(q.shift(-5) / q - 1).loc[start:].mean():+.2%}, up {np.mean((q.shift(-5) / q - 1).loc[start:].dropna() > 0):.0%}).",
                      f"- Gap-down opens: {len(gp)}. From that open to the same day's close the market returned {rest.mean():+.2%} on average and rose {np.mean(rest > 0):.0%} of the time.",
                      f"- Times each rule fired: close stop {len(dn)}, gap stop {len(gp)}, any-shock {int(sig['any'].loc[start:].sum())}, "
                      f"stock stop {int(sig['stock'].loc[start:].sum().sum())} stock-days."]
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {u}" for a, u in t.index]
    for k in dict.fromkeys(a for a, _ in rows if a != "live book"):
        d, sh = t.loc[f"{k} | end-2014 list (decides)"], t.loc[f"{k} | shipped list (reported)"]
        l1, l2 = t.loc["live book | end-2014 list (decides)"], t.loc["live book | shipped list (reported)"]
        if d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and sh["P vs live"] >= 0.5:
            ok[k] = d["P vs live"]
        if d["worst fall"] > l1["worst fall"] and sh["worst fall"] > l2["worst fall"]:
            less[k] = (l1["growth a year"] - d["growth a year"], d["worst fall"] - l1["worst fall"], l2["growth a year"] - sh["growth a year"], sh["worst fall"] - l2["worst fall"])
    out = ["# Seeing the news and closing out: does the book lose less?\n",
           "Rules written in news_stop_odds.py before the run. 'live book' is what the bot holds now. Alpaca daily bars from 2016.\n",
           t.to_markdown(floatfmt=".3f"), "",
           f"- **Does any rule belong in the live book?** {'Yes: **' + max(ok, key=ok.get) + '**' if ok else '**No.** None grows faster than the live book by the standing bar.'}",
           "- **Which lose less, and at what price?** " + ("None has a smaller worst fall on both lists." if not less else ""),
           *[f"  - **{k}**: worst fall smaller by {v[1]:.1%} (end-2014 list) and {v[3]:.1%} (shipped list); growth a year {'lower' if v[0] > 0 else 'higher'} by {abs(v[0]):.1%} and {'lower' if v[2] > 0 else 'higher'} by {abs(v[2]):.1%}."
             for k, v in less.items()],
           "\n## Why closing out on the news helps less than it feels like it should\n", *facts]
    with open("reports/news_stop_odds.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok, less


if __name__ == "__main__":
    main()
