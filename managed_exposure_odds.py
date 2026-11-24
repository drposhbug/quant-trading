"""Calculated risk: does borrowing modestly, and holding more in calm times than after shocks, grow faster?
Writes reports/managed_exposure_odds.md.   Run: python managed_exposure_odds.py

The owner (2026-11-23): "do whatever you think makes money ... the biggest money maker, but sometimes I would like
you to take calculated risk". By the growth criterion the hold-half-after-a-shock rule (B2.2) stays in shadow: it
grows slower. But it has a better return for its risk, and the one thing this project can predict is the size of
moves. A calculated risk would be to borrow a little in calm times and cut back after shocks. Written before the run.
- Exposure: a multiple of the current rule, known at each close. After a market shock (the market moving more than
  2.5 of its normal daily moves either way; normal = the 60 sessions before) it is at its lower value for 21 closes.
    steady 1.25x, steady 1.5x                       the same multiple always
    1.25x calm / 0.625x after a shock               B2.2 scaled by 1.25
    1.5x calm / 0.75x after a shock                 B2.2 scaled by 1.5
    1x calm / 0.5x after a shock                    B2.2 itself, for reference
- Two tests, as for the exposure decision already in force (growth_odds.py): the Nasdaq-100 index since 1986, held
  as it is (this includes 2000-2002 and 2008, which the recent years do not), and the end-2014 list with the live
  book (monitor.tilted). The shipped list is reported.
- Money: borrowed money costs the T-bill rate + 1.5% a year, idle money earns the T-bill rate, trading costs 5 bp.
  Stress case: T-bill + 3% and 10 bp. Exposure is rebalanced to its multiple every day, as a margin account would be.
- Growth bar: P(arm grows faster than 1x) >= 0.75 on BOTH the index since 1986 and the end-2014 list in the base
  case, AND >= 0.5 on both in the stress case.
- Calculated-risk bar: on the index since 1986 the arm's worst fall is at most 10 points deeper than holding at 1x.
  A risk whose worst case is not bounded is not a calculated one.
- An arm that clears both becomes candidate B3.0 in shadow and goes on the agenda of the 2026-12-12 review; nothing
  is switched on by this run. An arm that clears only the growth bar is reported as "grows faster, at a price".
Reading, not a bar: the steady multiple that would have grown fastest in each sample, to show how flat the top is.
"""
import numpy as np
import pandas as pd
import yfinance as yf

import growth_odds
from backtest import prices
from growth_odds import odds
from model import BENCH, P, backtest_returns
from monitor import tilted
from universe_study import TECH10_2014, load_extra

ARMS = {"steady 1.25x": (1.25, 1.25), "steady 1.5x": (1.5, 1.5), "1.25x calm / 0.625x after a shock": (1.25, 0.625),
        "1.5x calm / 0.75x after a shock": (1.5, 0.75), "1x calm / 0.5x after a shock (B2.2)": (1.0, 0.5)}
CASES = {"base": (0.015, 5.0), "stress": (0.03, 10.0)}


def exposure(r, calm, tight):
    """The multiple held from each close: `tight` for 21 closes from a shock day, else `calm`."""
    after = ((r / r.rolling(60).std().shift(1)).abs() > 2.5).astype(float).rolling(21, min_periods=1).max() > 0
    return pd.Series(np.where(after, tight, calm), index=r.index)


def financed(gross, rf, spread):
    """Daily cost of borrowing above 1x and income on what is idle below it; gross is what was held into the day."""
    g = gross.shift(1).fillna(1.0)
    return -(g - 1).clip(lower=0) * (rf + spread / 252) + (1 - g).clip(lower=0) * rf


def index_arm(r, rf, e, spread, bps):
    return (e.shift(1) * r - e.diff().abs().fillna(0) * bps / 1e4 + financed(e, rf, spread)).dropna()


def book_arm(px, w, rf, e, spread, bps):
    wt = w.mul(e, axis=0)
    return backtest_returns(px, wt, bps) + financed(wt.sum(axis=1), rf, spread)


def main():
    px = prices()
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    long = yf.download(["^NDX", "^IRX"], start="1985-01-01", auto_adjust=True, progress=False, threads=False)["Close"].dropna(subset=["^NDX"])
    rf_long, ndx = (long["^IRX"].ffill() / 100 / 252).fillna(0), long["^NDX"].pct_change()
    rf = rf_long.reindex(px.index).ffill().fillna(0)
    markets = {"Nasdaq-100 since 1986 (decides)": ("index", ndx.loc["1986-01-01":], rf_long), "end-2014 list (decides)": ("book", px14, rf),
               "shipped list (reported)": ("book", px, rf)}
    rows, kelly = {}, {}
    p = lambda a, b: odds(a, b)["P(arm grows faster)"]
    for name, (kind, data, r_f) in markets.items():
        if kind == "index":
            ones = pd.Series(1.0, index=data.index)
            run = lambda e, s, c, data=data, r_f=r_f: index_arm(data, r_f.reindex(data.index).fillna(0), e, s, c)
            shock_r, start = data, data.index[61]
        else:
            w = tilted(data)
            ones = pd.Series(1.0, index=data.index)
            run = lambda e, s, c, data=data, w=w, r_f=r_f: book_arm(data, w, r_f, e, s, c)
            shock_r, start = data[BENCH].ffill().pct_change(), data.index[P["trend_long"] + P["vol_win"]]
        base = {k: run(ones, *v).loc[start:] for k, v in CASES.items()}
        mid = base["base"].index[len(base["base"]) // 2]
        rows[("1x (the current rule)", name)] = {"P base": np.nan, "P 1st half": np.nan, "P 2nd half": np.nan, "P stress": np.nan,
                                                 **{k: v for k, v in odds(base["base"], base["base"]).items() if k in ("CAGR arm", "MaxDD arm")}}
        for arm, (calm, tight) in ARMS.items():
            e = exposure(shock_r, calm, tight)
            a = {k: run(e, *v).loc[start:] for k, v in CASES.items()}
            growth_odds.rng = np.random.default_rng(7)
            o = odds(a["base"], base["base"])
            rows[(arm, name)] = {"P base": o["P(arm grows faster)"], "P 1st half": p(a["base"][:mid], base["base"][:mid]), "P 2nd half": p(a["base"][mid:], base["base"][mid:]),
                                 "P stress": p(a["stress"], base["stress"]), "CAGR arm": o["CAGR arm"], "MaxDD arm": o["MaxDD arm"]}
        grid = np.arange(0.5, 3.01, 0.25)
        g = [odds(run(ones * L, *CASES["base"]).loc[start:], base["base"])["CAGR arm"] for L in grid]
        kelly[name] = (grid[int(np.argmax(g))], max(g), dict(zip(grid, g)))
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {m}" for a, m in t.index]
    out = ["# Calculated risk: borrowing modestly, and more in calm times than after shocks\n",
           "Rules written in managed_exposure_odds.py before the run. P = share of simulated histories in which the arm ends with more money than the current rule at 1x.\n",
           t.rename(columns={"CAGR arm": "growth a year", "MaxDD arm": "worst fall"}).to_markdown(floatfmt=".3f"), ""]
    ix, b14 = "Nasdaq-100 since 1986 (decides)", "end-2014 list (decides)"
    for arm in ARMS:
        a, b, one = t.loc[f"{arm} | {ix}"], t.loc[f"{arm} | {b14}"], t.loc[f"1x (the current rule) | {ix}"]
        grow = min(a["P base"], b["P base"]) >= 0.75 and min(a["P stress"], b["P stress"]) >= 0.5
        bounded = a["MaxDD arm"] >= one["MaxDD arm"] - 0.10
        verdict = "**clears both bars: candidate B3.0**" if grow and bounded else "grows faster, at a price (worst fall not bounded)" if grow else "does not clear the growth bar"
        out.append(f"- **{arm}**: {verdict}. Index since 1986: P {a['P base']:.2f} (stress {a['P stress']:.2f}), worst fall {a['MaxDD arm']:.0%} against {one['MaxDD arm']:.0%} at 1x. "
                   f"End-2014 list: P {b['P base']:.2f} (stress {b['P stress']:.2f}).")
    out.append("\n## Reading: the steady multiple that would have grown fastest (base costs)\n")
    for name, (best, gbest, curve) in kelly.items():
        out.append(f"- {name}: {best:.2f}x ({gbest:.1%} a year). " + ", ".join(f"{L:.2f}x {v:.1%}" for L, v in curve.items() if L in (0.5, 1.0, 1.25, 1.5, 2.0, 3.0)))
    with open("reports/managed_exposure_odds.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
