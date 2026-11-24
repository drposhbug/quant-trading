"""After a stock opens far below its last close (bad news overnight), does it keep falling? Writes reports/news_gap_results.md.
Run: python news_gap_study.py

The owner's ask (2026-11-23): "test that", after a quick look showed stocks that opened more than 10% down losing a
further 1.2% over the next five sessions, on a list without the companies that died. Written before this run.
Why this is a different kind of test: a ranking of every stock every day cannot see information that touches a few
names on a few days (Grok's review). So this is an event test: only the stocks the event happened to, and only then.
- List: S&P 500 members on the day, dead companies included (wide_universe.py). Alpaca adjusted daily bars.
- Event: a member opens more than 10% below its previous close. Also read: more than 5% below, and more than 10% above.
- What is measured: the stock against the average index member, from that open (the first price anyone can trade
  at). A basket holds every stock whose event was in the last 5 sessions: the event day from open to close, the
  next 4 sessions close to close. Each day the basket's average return minus the average member's is one
  observation, so overlapping events do not inflate anything. Reported: the daily mean, its t, and the average
  total over the 5 sessions for one event.
- Verdict (the 10%-down event only; the others are readings): real if t <= -3 and the daily mean is negative in
  both halves of the days. Short of that, "a hint" if t <= -2 with the same sign in both halves, else "no pattern".
- If real or a hint, the use is tested on the bot's own book by the standing bars (news_stop_odds.py): the stock is
  sold at that open and bought back at the close 4 sessions later. Bar 1: P(grows faster than the live book) >= 0.90
  on the end-2014 list, > 0.5 in each half, >= 0.5 on the shipped list. Bar 2: loses less only if the worst fall is
  smaller on both lists. With megacaps such gaps are rare, so the count of events is reported beside the result.
Known flaw: a few spin-off days show as false drops in these bars (reports/wide_universe_quality.md); they dilute
the result toward zero.
"""
import warnings

import numpy as np
import pandas as pd

import daily_calls as d
import growth_odds
from growth_odds import odds
from model import BENCH, P, UNIVERSE, backtest_returns, names_of
from monitor import tilted
from universe_study import TECH10_2014

HOLD = 5


def basket(flag, first, later, hold=HOLD):
    """Daily return of the basket of stocks whose event was in the last `hold` sessions, as written in the docstring.
    flag: [day x stock] events; first, later: each stock's return against the average member on its event day
    (open to close) and on other days (close to close)."""
    on = flag.astype(float).rolling(hold, min_periods=1).max().astype(bool) & ~flag
    num = first.where(flag).sum(axis=1) + later.where(on).sum(axis=1)
    cnt = (flag & first.notna()).sum(axis=1) + (on & later.notna()).sum(axis=1)
    return (num / cnt)[cnt > 0]


def line(name, b, per_event):
    half = len(b) // 2
    return {"event": name, "events": int(per_event.notna().sum()), "days held": len(b), "daily mean, bp": b.mean() * 1e4,
            "t": b.mean() / (b.std() / np.sqrt(len(b))), "1st half, bp": b.iloc[:half].mean() * 1e4, "2nd half, bp": b.iloc[half:].mean() * 1e4,
            "5 sessions, per event": per_event.mean(), "fell further": (per_event < 0).mean()}


def main():
    warnings.simplefilter("ignore")
    raw, member, uni, outside = d.panel()
    c, o = raw["c"].ffill(limit=21), raw["o"]
    m = member if member is not None else c.notna()
    gap = (o / c.shift(1) - 1).where(m)
    first, later, week = (c / o - 1).where(m), c.pct_change().where(m), (c.shift(-(HOLD - 1)) / o - 1).where(m)
    rf, rl, rw = first.sub(first.mean(axis=1), axis=0), later.sub(later.mean(axis=1), axis=0), week.sub(week.mean(axis=1), axis=0)
    start = d.WARM
    rows = [line(name, basket(flag.iloc[start:], rf.iloc[start:], rl.iloc[start:]), rw.iloc[start:].where(flag.iloc[start:]).stack().dropna())
            for name, flag in (("opens more than 10% down", gap < -0.10), ("opens more than 5% down", gap < -0.05), ("opens more than 10% up", gap > 0.10))]
    t = pd.DataFrame(rows).set_index("event")
    r = t.iloc[0]
    same = r["1st half, bp"] < 0 and r["2nd half, bp"] < 0
    verdict = "real" if r["t"] <= -3 and same else "a hint" if r["t"] <= -2 and same else "no pattern"
    out = ["# After a stock opens far below its last close, does it keep falling?\n",
           f"Rules written in news_gap_study.py before the run. S&P 500 members by date, dead companies included, {c.index[start].date()} to {c.index[-1].date()}. "
           "Returns are against the average index member, from the open of the event day.\n",
           t.to_markdown(floatfmt=".2f"),
           f"\n- Verdict for the 10%-down event: **{verdict}** (real needs t of -3 or lower and a negative mean in both halves; a hint needs -2)."]

    if verdict != "no pattern":  # the use, on the bot's own book
        names = sorted(set(UNIVERSE) | set(TECH10_2014))
        b = d.bars(names + [BENCH, "BIL"])
        rfree, res = b["c"]["BIL"].ffill().pct_change().fillna(0), {}
        for uni_name, lst in {"end-2014 list (decides)": TECH10_2014, "shipped list (reported)": UNIVERSE}.items():
            cols = [n for n in lst if n in b["c"]] + [BENCH]
            px, op = b["c"][cols], b["o"][cols]
            cc, w = px[names_of(px)].ffill(), tilted(px)
            flag = (op[names_of(px)] / cc.shift(1) - 1) < -0.10
            out_ = flag.astype(float).rolling(HOLD - 1, min_periods=1).max().astype(bool)  # zero at closes t .. t+3, back at close t+4
            cash = lambda wt: backtest_returns(px, wt) + (1 - wt.sum(axis=1)).shift(1).fillna(0) * rfree.reindex(px.index).fillna(0)
            night, day = (op[names_of(px)] / cc.shift(1) - 1).fillna(0), cc.pct_change().fillna(0)
            held = w.shift(1).fillna(0).where(flag & ~out_.shift(1, fill_value=False), 0.0)  # what was still held when the stop fired
            arm = cash(w.where(~out_, 0.0)) + (held * (night - day)).sum(axis=1)  # that day the stock earns only the step to the open
            live = cash(w)
            s0 = px.index[P["trend_long"] + P["vol_win"] + 126 + 252]
            a, l = arm.loc[s0:], live.loc[s0:]
            mid = l.index[len(l) // 2]
            growth_odds.rng = np.random.default_rng(7)
            og = odds(a, l)
            p = lambda x, y: odds(x, y)["P(arm grows faster)"]
            res[uni_name] = {"times it fired": int(flag.loc[s0:].sum().sum()), "P vs live": og["P(arm grows faster)"], "P 1st half": p(a[:mid], l[:mid]), "P 2nd half": p(a[mid:], l[mid:]),
                             "growth a year": og["CAGR arm"], "live growth": og["CAGR base"], "worst fall": og["MaxDD arm"], "live worst fall": og["MaxDD base"]}
        u = pd.DataFrame(res).T
        dd, sh = u.iloc[0], u.iloc[1]
        ok = dd["P vs live"] >= 0.90 and dd["P 1st half"] > 0.5 and dd["P 2nd half"] > 0.5 and sh["P vs live"] >= 0.5
        less = dd["worst fall"] > dd["live worst fall"] and sh["worst fall"] > sh["live worst fall"]
        out += ["\n## The use on the bot's book: sell a stock at the open when it opens more than 10% down, back in 4 sessions later\n", u.to_markdown(floatfmt=".3f"),
                f"\n- Belongs in the live book by the standing bar: **{'yes' if ok else 'no'}**. Loses less on both lists: **{'yes' if less else 'no'}**."]
    with open("reports/news_gap_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
