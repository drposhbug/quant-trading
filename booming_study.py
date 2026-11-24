"""Buying what is booming, in and outside technology; and meme coins. Writes reports/booming_results.md.
Run: python booming_study.py

The owner's ask (2026-11-23): "what about other good stocks outside of tech ... analyze everything that's booming",
and "what about those meme coins". Written before the first run.
1. Booming stocks. Among the S&P 500 members of each day (dead companies included), the 30 with the strongest
   12-month trend (the trend used everywhere here: the last year's move leaving out the latest month, per unit of
   its volatility) are held in equal amounts and re-picked every 21 sessions, entered a day after the pick, 5 bp
   costs. Decides: P(that book ends with more money than the average index member held the same way). Buying
   what is booming pays if P >= 0.75 with more than 0.5 in each half. Read beside it: the same picking only among
   stocks outside technology (a stock's sector as in daily_calls.groups), growth and worst fall of each, the
   bot's own book over the same days, and the names that are booming today.
2. Meme coins: a reading only, no verdict. Dogecoin and Shiba Inu are the two that survived out of thousands, so
   their history is the history of two lottery winners. Shown: holding them, and the 200-day trend rule of
   crypto_trend_odds.py, to see what the rule would have done with the rise and the falls.
"""
import warnings

import numpy as np
import pandas as pd
import yfinance as yf

import daily_calls as d
import growth_odds
from backtest import prices
from crypto_trend_odds import facts, rule
from growth_odds import odds
from model import backtest_returns
from monitor import tilted

TOP, EVERY = 30, 21


def book(score, c):
    """Daily return of holding the TOP names by score in equal amounts, re-picked every EVERY sessions."""
    w = pd.DataFrame(0.0, index=c.index, columns=c.columns)
    for t in range(d.WARM, len(c) - 1, EVERY):
        pick = score.iloc[t].dropna().nlargest(TOP).index
        w.iloc[t + 1:t + 1 + EVERY, w.columns.get_indexer(pick)] = 1.0 / TOP
    r = c.pct_change().fillna(0)
    return ((w.shift(1) * r).sum(axis=1) - w.diff().abs().sum(axis=1).fillna(0) * 0.0005).iloc[d.WARM + 2:], w


def main():
    warnings.simplefilter("ignore")
    raw, member, uni, outside = d.panel()
    c = raw["c"].ffill(limit=21)
    m = member if member is not None else c.notna()
    lr = np.log(c).diff()
    score = (lr.rolling(231).sum().shift(21) / (lr.rolling(60).std() * np.sqrt(231))).where(m)
    beta, sec = d.groups(c, outside["SPY"].ffill(), outside[d.SECTORS].ffill())
    tech = pd.DataFrame(sec == d.SECTORS.index("XLK"), index=c.index, columns=c.columns)
    boom, wb = book(score, c)
    other, wo = book(score.where(~tech), c)
    avg = c.pct_change().where(m).mean(axis=1).reindex(boom.index).fillna(0)
    px = prices()
    bot = backtest_returns(px, tilted(px)).reindex(boom.index).dropna()
    mid = boom.index[len(boom) // 2]
    growth_odds.rng = np.random.default_rng(7)
    p = lambda a, b: odds(a, b)["P(arm grows faster)"]
    P, P1, P2 = p(boom, avg), p(boom[:mid], avg[:mid]), p(boom[mid:], avg[mid:])
    rows = {"the 30 strongest trends, any sector": {"P vs the average stock": P, **facts(boom, 252)}, "the 30 strongest trends outside technology": {"P vs the average stock": p(other, avg), **facts(other, 252)},
            "the average index member": {"P vs the average stock": np.nan, **facts(avg, 252)}, "the bot's book (12 technology names)": {"P vs the average stock": p(bot, avg.reindex(bot.index)), **facts(bot, 252)}}
    t = pd.DataFrame(rows).T.drop(columns="share of days held")
    verdict = "buying what is booming pays" if P >= 0.75 and min(P1, P2) > 0.5 else "buying what is booming has not paid more than holding the average stock"
    now = lambda w: ", ".join(w.columns[w.iloc[-1] > 0][:TOP])
    out = ["# Buying what is booming, in and outside technology; and meme coins\n",
           f"Rules written in booming_study.py before the run. S&P 500 members by date, {boom.index[0].date()} to {boom.index[-1].date()}.\n",
           t.to_markdown(floatfmt=".3f"),
           f"\n- Verdict: **{verdict}** (P {P:.2f}; halves {P1:.2f} and {P2:.2f}; needs 0.75 with both halves above 0.5).",
           f"- Booming today, any sector: {now(wb)}.", f"- Booming today, outside technology: {now(wo)}.",
           "\n## Meme coins (a reading; two survivors out of thousands)\n"]
    coins = yf.download(["DOGE-USD", "SHIB-USD"], start="2014-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    rows = {}
    for coin in coins:
        cc = coins[coin].dropna()
        hold, r200 = cc.pct_change().iloc[200:], rule(cc)
        rows[f"{coin}: holding"], rows[f"{coin}: 200-day rule"] = facts(hold), facts(r200)
        rows[f"{coin}: holding"]["from"] = rows[f"{coin}: 200-day rule"]["from"] = f"{hold.index[0].date()}"
    out.append(pd.DataFrame(rows).T.to_markdown(floatfmt=".3f"))
    with open("reports/booming_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
