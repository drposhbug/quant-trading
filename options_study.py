"""Options: are they cheap after a shock, and do calls work as leverage with a capped loss? Writes reports/options_results.md.
Run: python options_study.py

The owner (2026-11-23): "there's gotta be more for options ... if we got options Friday and today that would have
been huge". Written before the first run. Earlier the same day it was said that option prices could not be tested
before 2024. That was wrong for the index: the volatility indexes are computed from option prices (VIX for the S&P
500 from 1990, VXN for the Nasdaq-100 from 2001), so what index options cost on every past day is known.
Pricing: an at-the-money option with 21 sessions to run, valued by Black-Scholes at the volatility index of that
day, held to expiry, bought 3% above that value for the spread. The index somewhat overstates at-the-money
volatility, so this is a little unkind to buyers. Single stocks cannot be done this way: no free history.
1. Cheap after a shock? The project's one strong forecast is that moves stay large for a month after a shock (the
   index moving more than 2.5 of its normal daily moves). A straddle (a call and a put) pays when moves are large
   either way. Bought at the close of a shock day on the Nasdaq-100, one position at a time (the next purchase no
   sooner than 21 sessions later). Decides: the average return on the money paid. Options are too cheap after
   shocks if it is above zero with t >= 3 and above zero in both halves; too dear if below zero the same way.
   Read beside it: the same on every 21st day whatever the state, the S&P 500 with the VIX, and calls alone.
2. Calls as leverage with a capped loss. Each 21 sessions, 1% of the account buys at-the-money calls on the
   Nasdaq-100 and the other 99% holds the index. Decides: P(it ends with more money than just holding), by the
   project's bootstrap on the 21-session results. Worth having if P >= 0.75 and its worst fall is no more than 10
   points deeper than holding. Read beside it: 2% a month, and borrowing a quarter instead (version B3.0).
3. The owner's example, as a reading: a 21-session call on the Nasdaq-100 bought at Friday's close and valued at
   Monday's close, for 2026-11-20 and for every Friday of the last five years.
"""
import math

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm

import growth_odds
from growth_odds import odds

T, SPREAD = 21, 1.03


def call(s, k, sigma, days, r=0.0):
    """Black-Scholes value of a call; sigma a year, days in sessions."""
    t = np.maximum(days, 1e-9) / 252
    d1 = (np.log(s / k) + (r + sigma ** 2 / 2) * t) / (sigma * np.sqrt(t))
    return s * norm.cdf(d1) - k * np.exp(-r * t) * norm.cdf(d1 - sigma * np.sqrt(t))


def summary(x):
    x = pd.Series(x).dropna()
    h = len(x) // 2
    return {"trades": len(x), "average return on the money paid": x.mean(), "t": x.mean() / (x.std() / math.sqrt(len(x))), "1st half": x.iloc[:h].mean(), "2nd half": x.iloc[h:].mean(),
            "share that made money": (x > 0).mean(), "median": x.median()}


def spaced(days, gap=T):
    """From a list of row numbers, those at least `gap` apart, taken in order."""
    out, nxt = [], -1
    for d in days:
        if d >= nxt:
            out.append(d)
            nxt = d + gap
    return out


def main():
    px = yf.download(["^NDX", "^VXN", "^GSPC", "^VIX", "^IRX"], start="1990-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    rows, text = {}, []
    for name, idx, vol in (("Nasdaq-100", "^NDX", "^VXN"), ("S&P 500", "^GSPC", "^VIX")):
        d = px[[idx, vol]].dropna()
        s, sig = d[idx].values, d[vol].values / 100
        r = d[idx].pct_change()
        shock = ((r / r.rolling(60).std().shift(1)).abs() > 2.5).values
        end = np.arange(len(s)) + T
        ok = end < len(s)
        move = np.where(ok, s[np.minimum(end, len(s) - 1)] / s - 1, np.nan)
        c0 = call(1.0, 1.0, sig, T)
        strad, calls = np.abs(move) / (SPREAD * 2 * c0) - 1, np.maximum(move, 0) / (SPREAD * c0) - 1  # with no interest a put costs what the call does
        after, anyday = spaced([i for i in np.where(shock & ok)[0] if i > 60]), spaced([i for i in np.where(ok)[0] if i > 60])
        rows[f"{name}: straddle bought after a shock" + (" (decides)" if idx == "^NDX" else "")] = summary(strad[after])
        rows[f"{name}: straddle bought on any day"] = summary(strad[anyday])
        rows[f"{name}: call bought after a shock"] = summary(calls[after])
        rows[f"{name}: call bought on any day"] = summary(calls[anyday])
        if idx == "^NDX":
            ndx, first = d, d.index[61]
            # 2. calls as leverage: per 21 sessions, 99% in the index and 1% (or 2%) in calls
            m = move[anyday]
            hold = pd.Series(m, index=d.index[anyday])
            rf = (px["^IRX"].reindex(d.index).ffill().fillna(0).values / 100)[anyday] * T / 252
            arms = {"hold the index": hold, "99% index + 1% in calls each 21 sessions": 0.99 * (1 + hold) + 0.01 / (SPREAD * c0[anyday]) * np.maximum(m, 0) - 1,
                    "98% index + 2% in calls": 0.98 * (1 + hold) + 0.02 / (SPREAD * c0[anyday]) * np.maximum(m, 0) - 1,
                    "borrow a quarter (B3.0)": 1.25 * hold - 0.25 * (rf + 0.015 * T / 252)}
            lev = {}
            for k, a in arms.items():
                eq = (1 + a).cumprod()
                growth_odds.rng = np.random.default_rng(7)
                lev[k] = {"P vs holding": np.nan if k == "hold the index" else odds(a, hold)["P(arm grows faster)"], "growth a year": eq.iloc[-1] ** (252 / T / len(a)) - 1,
                          "worst fall (21-session steps)": (eq / eq.cummax() - 1).min(), "worst 21 sessions": a.min(), "best 21 sessions": a.max()}
            # 3. the owner's example: Friday's close to Monday's close
            wd = d.index.dayofweek
            fri = [i for i in range(len(d) - 1) if wd[i] == 4 and wd[i + 1] == 0 and d.index[i] >= d.index[-1] - pd.Timedelta(days=5 * 365)]
            one = lambda i: call(s[i + 1] / s[i], 1.0, sig[i + 1], T - 1) / (SPREAD * call(1.0, 1.0, sig[i], T)) - 1
            wk = pd.Series([one(i) for i in fri], index=d.index[fri])
            last = wk.index[-1]
            text = [f"- The last one, bought at the close on {last.date()} with the Nasdaq-100's volatility index at {sig[fri[-1]]:.0%}: the index moved {s[fri[-1] + 1] / s[fri[-1]] - 1:+.1%} by Monday's close and the call was worth {wk.iloc[-1]:+.0%} more.",
                    f"- The same purchase on each of the last {len(wk)} Fridays: on average {wk.mean():+.1%} by Monday's close; it lost money on {np.mean(wk < 0):.0%} of them; best {wk.max():+.0%}, worst {wk.min():+.0%}.",
                    f"- The three best: {', '.join(f'{i.date()} {v:+.0%}' for i, v in wk.nlargest(3).items())}. The three worst: {', '.join(f'{i.date()} {v:+.0%}' for i, v in wk.nsmallest(3).items())}."]
    t1, t2 = pd.DataFrame(rows).T, pd.DataFrame(lev).T
    a = t1.iloc[0]
    v1 = ("options are too cheap after a shock" if a["t"] >= 3 and min(a["1st half"], a["2nd half"]) > 0 else
          "options are too dear after a shock" if a["t"] <= -3 and max(a["1st half"], a["2nd half"]) < 0 else "no reliable mispricing after a shock")
    b, h = t2.loc["99% index + 1% in calls each 21 sessions"], t2.loc["hold the index"]
    v2 = "worth having: candidate for shadow" if b["P vs holding"] >= 0.75 and b["worst fall (21-session steps)"] >= h["worst fall (21-session steps)"] - 0.10 else "does not clear its bar"
    out = ["# Options: cheap after a shock? Calls as leverage with a capped loss?\n",
           f"Rules written in options_study.py before the run. Index options priced from the volatility indexes; Nasdaq-100 from {first.date()}, S&P 500 from 1990, to {px.index[-1].date()}.\n",
           "## 1. Buying options after a shock\n", t1.to_markdown(floatfmt=".3f"), f"\n- Verdict: **{v1}**.\n",
           "## 2. Calls as leverage with a capped loss (Nasdaq-100, steps of 21 sessions)\n", t2.to_markdown(floatfmt=".3f"), f"\n- Verdict for 1% a month in calls: **{v2}**.\n",
           "## 3. \"If we had bought options on Friday\"\n", *text]
    with open("reports/options_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
