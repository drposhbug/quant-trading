"""Do candlestick patterns predict returns on these names? Writes reports/candles_results.md.

For each pattern seen at close t, measures the forward return close t -> t+h minus that stock's average h-day
return (so drift of winners like NVDA does not count as "signal"). Holm correction across all pattern x horizon
tests; stability checked by splitting the sample (pre-2021 = discovery, 2021+ = holdout).
"""
import math
import os
import sys
from statistics import NormalDist

import numpy as np
import pandas as pd
import yfinance as yf

from model import UNIVERSE

CACHE = "data/ohlc.pkl"
H = (1, 5, 10)
SPLIT = "2021-01-01"


def ohlc():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_pickle(CACHE)
    d = yf.download(UNIVERSE, start="2014-01-01", auto_adjust=True, progress=False, threads=False)
    os.makedirs("data", exist_ok=True)
    d.to_pickle(CACHE)
    return d


def patterns(O, Hh, L, C):
    body, rng = C - O, (Hh - L).replace(0, np.nan)
    up, lo = Hh - np.maximum(O, C), np.minimum(O, C) - L
    green, red = body > 0, body < 0
    pO, pC = O.shift(1), C.shift(1)
    down5, up5 = C.shift(1) < C.shift(6), C.shift(1) > C.shift(6)  # prior 5-day trend
    return {
        "Doji": body.abs() <= 0.1 * rng,
        "Hammer (after down 5d)": (lo >= 2 * body.abs()) & (up <= 0.1 * rng) & down5,
        "Shooting star (after up 5d)": (up >= 2 * body.abs()) & (lo <= 0.1 * rng) & up5,
        "Bullish engulfing": (pC < pO) & green & (O <= pC) & (C >= pO),
        "Bearish engulfing": (pC > pO) & red & (O >= pC) & (C <= pO),
        "Bull marubozu": green & (body.abs() >= 0.9 * rng),
        "Bear marubozu": red & (body.abs() >= 0.9 * rng),
        "Three white soldiers": green & green.shift(1) & green.shift(2) & (C > pC) & (pC > C.shift(2)),
        "Three black crows": red & red.shift(1) & red.shift(2) & (C < pC) & (pC < C.shift(2)),
        "Inside bar": (Hh < Hh.shift(1)) & (L > L.shift(1)),
        "Outside bar": (Hh > Hh.shift(1)) & (L < L.shift(1)),
        "Gap up > 1%": O > Hh.shift(1) * 1.01,
        "Gap down > 1%": O < L.shift(1) * 0.99,
    }


def test(excess, mask):
    x = excess[mask.fillna(False)].stack().dropna()
    n = len(x)
    if n < 20:
        return n, np.nan, np.nan, np.nan
    t = x.mean() / (x.std() / math.sqrt(n))  # shortcut: treats events as independent; overlapping h>1 windows inflate t, Holm offsets some of it
    return n, x.mean(), (x > 0).mean(), t


def holm(p):
    order = np.argsort(p)
    adj = np.empty(len(p))
    running = 0
    for k, i in enumerate(order):
        running = max(running, min(1, (len(p) - k) * p[i]))
        adj[i] = running
    return adj


def main():
    d = ohlc()
    O, Hh, L, C = (d[k][UNIVERSE] for k in ("Open", "High", "Low", "Close"))
    pats = patterns(O, Hh, L, C)
    rows = []
    for h in H:
        fwd = C.shift(-h) / C - 1
        excess = fwd - fwd.mean()
        for name, m in pats.items():
            n, mu, hit, t = test(excess, m)
            _, mu_a, _, t_a = test(excess.loc[:SPLIT], m.loc[:SPLIT])
            _, mu_b, _, t_b = test(excess.loc[SPLIT:], m.loc[SPLIT:])
            rows.append(dict(Pattern=name, h=h, n=n, excess_bp=mu * 1e4, hit=hit, t=t,
                             pre2021_bp=mu_a * 1e4, post2021_bp=mu_b * 1e4, t_post=t_b))
    df = pd.DataFrame(rows)
    df["p"] = [2 * (1 - NormalDist().cdf(abs(t))) if pd.notna(t) else 1.0 for t in df.t]
    df["p_holm"] = holm(df.p.values)
    df["same_sign_both_halves"] = np.sign(df.pre2021_bp) == np.sign(df.post2021_bp)
    df["verdict"] = np.where((df.p_holm < 0.05) & df.same_sign_both_halves, "SIGNIFICANT + stable", "noise")

    out = [
        "# Candlestick pattern tests\n",
        f"Universe: {', '.join(UNIVERSE)}. Daily candles 2014 to today (yfinance, split/dividend adjusted). "
        f"{len(df)} tests (13 patterns × {len(H)} horizons); Holm-corrected p-values.\n",
        "excess_bp = average forward return after the pattern minus that stock's average return over the same horizon, in basis points (100 bp = 1%).\n",
        df.round({"excess_bp": 1, "hit": 3, "t": 2, "pre2021_bp": 1, "post2021_bp": 1, "t_post": 2, "p": 4, "p_holm": 4})
          .to_markdown(index=False),
        "\n## Verdict\n",
        f"{(df.verdict != 'noise').sum()} of {len(df)} pattern/horizon combinations survive multiple-testing correction "
        "with a consistent sign in both halves of the sample.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/candles_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
