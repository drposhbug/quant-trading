"""Options that like small moves, and selling at a target. Writes reports/options_small_moves.md.
Run: python options_small_moves.py

The owner (2026-11-23): "there's multiple ways to do options, those like small movement, selling it once it hits
the target etc". options_study.py only bought options and held them to the end. Written before the first run.
Index options priced from the volatility index of each day (S&P 500 with the VIX from 1990 decides; the Nasdaq-100
with the VXN from 2001 is read beside it), one new position every 21 sessions, 21 sessions to run, valued again at
every close. Each leg pays 3% for the spread. The volatility index is higher than at-the-money volatility and
options below the market cost more than options above it, so each leg gets its own multiple of the index, chosen
against the trade being tested: what is sold is priced low (call 0.85, put 1.00) and what is bought for protection
is priced high (put 1.25, call 0.85); the bought call of test 3 is priced at 0.90.
1. The small-move trade with a capped loss (an "iron condor"): sell a put 3% below the market and a call 3% above,
   buy a put 8% below and a call 8% above. It keeps the money received if the index ends within 3% either way and
   can lose at most 5% of the index less that money. Held to the end. Decides: the average return on the money at
   risk. It pays if that is above zero with t >= 3 and above zero in both halves.
2. The same trade managed: closed as soon as half of the money received has been earned, or as soon as the loss
   reaches twice the money received. Reading.
3. Buying a call and selling it at a target: sold as soon as it is worth 50% more than was paid, otherwise held to
   the end. Reading, beside holding the same call to the end.
These are model prices, not quotes. A pass means the trade is worth building properly and running in shadow.
"""
import math

import numpy as np
import pandas as pd
import yfinance as yf

from options_study import call, spaced

T, BUY, SELL = 21, 1.03, 0.97


def put(s, k, sigma, days):
    return call(s, k, sigma, days) - s + k


def condor(s, sig, days):
    """What the four legs are worth together (short the inner pair, long the outer pair), the entry level being 1."""
    return put(s, 0.97, sig, days) + call(s, 1.03, 0.85 * sig, days) - put(s, 0.92, 1.25 * sig, days) - call(s, 1.08, 0.85 * sig, days)


def run(s, sig, i):
    """Results of the three trades opened at row i: (condor held, condor managed, call with target, call held)."""
    path, vol = s[i:i + T + 1] / s[i], sig[i:i + T + 1]
    credit = condor(1.0, vol[0], T) * SELL
    risk = 0.05 - credit
    end = max(0.97 - path[-1], 0) - max(0.92 - path[-1], 0) + max(path[-1] - 1.03, 0) - max(path[-1] - 1.08, 0)
    held = managed = (credit - end) / risk
    for k in range(1, T):
        cost = condor(path[k], vol[k], T - k) * BUY
        if cost <= 0.5 * credit or cost >= 3 * credit:
            managed = (credit - cost) / risk
            break
    paid = call(1.0, 1.0, 0.9 * vol[0], T) * BUY
    c_held = c_target = max(path[-1] - 1, 0) / paid - 1
    for k in range(1, T):
        worth = call(path[k], 1.0, 0.9 * vol[k], T - k) * SELL
        if worth >= 1.5 * paid:
            c_target = worth / paid - 1
            break
    return held, managed, c_target, c_held


def summary(x):
    x = pd.Series(x)
    h = len(x) // 2
    return {"trades": len(x), "average return": x.mean(), "t": x.mean() / (x.std() / math.sqrt(len(x))), "1st half": x.iloc[:h].mean(), "2nd half": x.iloc[h:].mean(),
            "share that made money": (x > 0).mean(), "worst": x.min(), "best": x.max()}


def main():
    px = yf.download(["^GSPC", "^VIX", "^NDX", "^VXN"], start="1990-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    rows = {}
    for name, idx, vol in (("S&P 500", "^GSPC", "^VIX"), ("Nasdaq-100", "^NDX", "^VXN")):
        d = px[[idx, vol]].dropna()
        s, sig = d[idx].values, d[vol].values / 100
        res = np.array([run(s, sig, i) for i in spaced(range(1, len(s) - T - 1))])
        for j, lab in enumerate(("small-move trade, held to the end" + (" (decides)" if idx == "^GSPC" else ""), "small-move trade, managed (half the money earned, or stopped at twice)",
                                 "call, sold at +50% or held", "call, held to the end")):
            rows[f"{name}: {lab}"] = summary(res[:, j])
    t = pd.DataFrame(rows).T
    a = t.iloc[0]
    verdict = "the small-move trade pays" if a["t"] >= 3 and min(a["1st half"], a["2nd half"]) > 0 else "the small-move trade does not clear its bar"
    out = ["# Options that like small moves, and selling at a target\n",
           f"Rules written in options_small_moves.py before the run. Model prices from the volatility indexes, {px.index[0].date()} to {px.index[-1].date()}. "
           "For the small-move trade the return is on the money at risk (the most it can lose); for the calls, on the money paid.\n",
           t.to_markdown(floatfmt=".3f"), f"\n- Verdict: **{verdict}** (needs an average above zero with t of 3 or more, above zero in both halves)."]
    with open("reports/options_small_moves.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
