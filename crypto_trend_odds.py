"""Trading crypto with the slow trend rule: does it beat simply holding the coin? Writes reports/crypto_trend_odds.md.
Run: python crypto_trend_odds.py

The owner's ask (2026-11-23): "can you train to trade crypto or is it bad". Written before the first run.
What cannot be tested: whether Bitcoin will keep rising. Its past return is the largest of any asset of the last
decade, and a test that holds it "proves" only that. What can be tested is whether a rule adds anything to holding.
- Coins: Bitcoin (daily closes from 2014, Yahoo) and Ether (from 2017). Seven days a week.
- The rule, one version fixed in advance (the only kind of rule that held up anywhere in this project): hold the
  coin while its price is above its 200-day average, otherwise sit in cash. Checked once a day at the close; each
  switch costs 0.25% (a small account's crypto trading fee; stocks here cost 0.05%). Cash earns nothing.
- Decides: P(the rule ends with more money than holding the coin), by the project's paired bootstrap. The rule is
  worth having if P >= 0.75 on Bitcoin and >= 0.5 on Ether, and its worst fall is smaller on both.
- Readings: growth and worst fall of each; the same rule with a 100-day average; how closely Bitcoin moves with
  the Nasdaq-100; and what a 10% slice of rule-traded Bitcoin would have done to the bot's book since 2018. That
  last one is hindsight by construction and is labelled so.
- A pass means a sleeve in shadow (VERSIONS.md), not a trade.
"""
import numpy as np
import pandas as pd
import yfinance as yf

import growth_odds
from backtest import prices
from growth_odds import odds
from model import BENCH, backtest_returns
from monitor import tilted

FEE = 0.0025


def rule(px, n=200):
    """Daily return of: hold while the close is above its n-day average, else cash; a switch costs FEE."""
    on = (px > px.rolling(n).mean()).astype(float)
    return (on.shift(1) * px.pct_change() - on.diff().abs().fillna(0) * FEE).iloc[n:]


def facts(r, per_year=365):
    eq = (1 + r).cumprod()
    return {"growth a year": eq.iloc[-1] ** (per_year / len(r)) - 1, "worst fall": (eq / eq.cummax() - 1).min(), "share of days held": float((r != 0).mean())}


def main():
    px = yf.download(["BTC-USD", "ETH-USD", "QQQ"], start="2014-01-01", auto_adjust=True, progress=False, threads=False)["Close"]
    rows, ok, p = {}, [], lambda a, b: odds(a, b)["P(arm grows faster)"]
    for coin, bar in (("BTC-USD", 0.75), ("ETH-USD", 0.5)):
        c = px[coin].dropna()
        hold, r200, r100 = c.pct_change().iloc[200:], rule(c), rule(c, 100).loc[c.index[200]:]
        mid = hold.index[len(hold) // 2]
        growth_odds.rng = np.random.default_rng(7)
        P = p(r200, hold)
        rows[f"{coin}: holding"] = {"P vs holding": np.nan, "P 1st half": np.nan, "P 2nd half": np.nan, **facts(hold)}
        rows[f"{coin}: 200-day rule (decides)"] = {"P vs holding": P, "P 1st half": p(r200[:mid], hold[:mid]), "P 2nd half": p(r200[mid:], hold[mid:]), **facts(r200)}
        rows[f"{coin}: 100-day rule (reading)"] = {"P vs holding": p(r100, hold), "P 1st half": np.nan, "P 2nd half": np.nan, **facts(r100)}
        ok.append(P >= bar and facts(r200)["worst fall"] > facts(hold)["worst fall"])
    t = pd.DataFrame(rows).T
    wk = px[["BTC-USD", "QQQ"]].dropna().pct_change().loc["2018-01-01":]
    book_px = prices()
    book = backtest_returns(book_px, tilted(book_px)).loc["2018-10-01":]
    btc = px["BTC-USD"].dropna()
    btc_rule = (1 + rule(btc)).cumprod().reindex(book.index, method="ffill").pct_change().fillna(0)  # the rule's result from one market day to the next
    mix = 0.9 * book + 0.1 * btc_rule
    fb, fm = facts(book, 252), facts(mix, 252)
    out = ["# Trading crypto with the slow trend rule\n",
           f"Rules written in crypto_trend_odds.py before the run. Bitcoin {px['BTC-USD'].dropna().index[200].date()} and Ether {px['ETH-USD'].dropna().index[200].date()} to {px.index[-1].date()}. "
           "P = share of simulated histories in which the rule ends with more money than holding the coin.\n",
           t.to_markdown(floatfmt=".3f"),
           f"\n- Verdict: **{'the rule is worth having: a sleeve for shadow' if all(ok) else 'the rule does not clear its bar'}** (needs P of 0.75 on Bitcoin, 0.5 on Ether, and a smaller worst fall on both).",
           "\n## Readings\n",
           f"- Bitcoin against the Nasdaq-100 on market days since 2018: correlation {wk.corr().iloc[0, 1]:.2f}. It is partly the same bet as technology shares, and it trades on weekends when the bot cannot react.",
           f"- Hindsight, not evidence: the bot's book since 2018-10 grew {fb['growth a year']:.1%} a year with a worst fall of {fb['worst fall']:.0%}. With 10% of it in rule-traded Bitcoin: "
           f"{fm['growth a year']:.1%} a year, worst fall {fm['worst fall']:.0%}. Bitcoin's own rise over these years is the reason, and that rise is the thing no test can promise again."]
    with open("reports/crypto_trend_odds.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, all(ok)


if __name__ == "__main__":
    main()
