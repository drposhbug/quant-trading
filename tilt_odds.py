"""When to go heavier into certain stocks, by the owner's growth criterion. Writes reports/tilt_odds.md.

Written 2026-11-23, before the first run, after the Huang rebound (NVDA +31% in a day; equal weight +8.6% against the
live book's +7.5%). Same method as growth_odds.py: P = share of 2,000 paired stationary-bootstrap histories (L = 20)
in which the arm's mean log return is higher. Base = the live book (inverse-vol, fully invested, caps, 5 bp costs).
Arms, each fully invested with the same caps and costs:
  ew     equal weight: heavier in the volatile names, lighter in the calm ones (sizing="ew")
  trend  heavier in what has been rising: live weight x2 for the top third of names by the model's own trend score
         (12-1 month and 3-month, model.scores with w_trend=1), x0.5 for the bottom third, renormalised to the same gross
  dip    heavier in what just fell: the same tilt on the model's 1-week reversal score (w_trend=0)
Decision: move the live book to an arm only if, on the end-2014 list (names chosen without hindsight),
P(arm grows faster) >= 0.80 over the whole window AND > 0.5 in each half of it, AND > 0.5 on the shipped list.
If several qualify, the one with the highest whole-window P. Otherwise no change.
Three arms are tried, so even 0.80 is weak evidence: a pass would move the paper book only. These are decision odds,
not significance tests.
"""
import numpy as np
import pandas as pd

from backtest import prices
from growth_odds import LIVE, odds
from model import BENCH, P, backtest_returns, target_weights
from monitor import tilted  # the live function, so the study and the bot cannot drift apart
from universe_study import TECH10_2014, load_extra


ARMS = {"ew: heavier in the volatile names": lambda px: target_weights(px, {**LIVE, "sizing": "ew"}),
        "trend: heavier in what has been rising": lambda px: tilted(px, 1.0),
        "dip: heavier in what just fell": lambda px: tilted(px, 0.0)}
KEEP = ["P(arm grows faster)", "CAGR arm", "CAGR base", "Sharpe arm", "Sharpe base", "MaxDD arm", "MaxDD base"]


def main():
    px = prices()
    start = px.index[P["trend_long"] + P["vol_win"]]
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    cut = px14.iloc[:-250]  # self-check: no arm's weights at a date change when later prices are added
    for name, f in ARMS.items():
        assert np.allclose(f(cut).iloc[-1], f(px14).loc[cut.index[-1]], atol=1e-9), f"lookahead in {name}"
        assert (f(px14).sum(axis=1) <= 1 + 1e-9).all(), f"leverage in {name}"

    rows = {}
    for uni, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        base = backtest_returns(data, target_weights(data, LIVE)).loc[start:]
        mid = base.index[len(base) // 2]
        for name, f in ARMS.items():
            arm = backtest_returns(data, f(data)).loc[start:]
            o = odds(arm, base)
            rows[(name, uni)] = {**{k: o[k] for k in KEEP},
                                 "P 1st half": odds(arm[:mid], base[:mid])["P(arm grows faster)"],
                                 "P 2nd half": odds(arm[mid:], base[mid:])["P(arm grows faster)"]}
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {u}" for a, u in t.index]
    ok = {}
    for name in ARMS:
        d, s = t.loc[f"{name} | end-2014 list (decides)"], t.loc[f"{name} | shipped list (reported)"]
        if d[KEEP[0]] >= 0.80 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s[KEEP[0]] > 0.5:
            ok[name] = d[KEEP[0]]
    verdict = f"move the live book to **{max(ok, key=ok.get)}**" if ok else "**no change**: no tilt clears the bar"
    out = ["# When to go heavier into certain stocks: decision odds, 2026-11-23\n",
           "Rules written in tilt_odds.py before the run. Base = the live book (inverse-vol, fully invested).\n",
           t.to_markdown(floatfmt=".3f"), f"\n- Decision: {verdict}"]
    with open("reports/tilt_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    main()
