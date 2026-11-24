"""Every day it looks at the day, makes its calls, and later we see what came true.
Run: python daily_calls.py    after the close: score the calls that have come due, log today's calls, rewrite
                               reports/daily_calls.md   (workflow mlp-log, every weekday)

The owner's ask (2026-11-23), after the first pattern-finder failed its test: "why did it not pass ... fix it ... every
day it looks at the day, it should be able to predict outcomes, and then let's see what comes true".

Why the first one failed (discover_odds.py; checks run 2026-11-23 on its development years, and Grok's review in
research_notes/mlp loop/round 3.md):
- The ten patterns it trusted had a rank IC of +0.108 in their own past and +0.003 in the 21 sessions that followed.
- Handed shuffled outcomes (each stock given another stock's future) it "found" ten patterns that looked as good:
  score 0.214 against 0.228 for the real ones, and 30% of shuffles looked better. Its finds could not be told from luck.
- Cause: ten stocks. One day's ranking of ten names is nearly all noise, and the best ten of 945 tries on noise always
  look convincing. Its rule (same direction in two halves) lets half of all candidates through, and the 600 multiplied
  pairs were more tries: 73% of its picks.

What is different here. Fixed 2026-11-23 before the first call was logged (RULES). Any change to these rules gets a new
RULES name and its tally starts again at zero; the old tally is kept.
1. About 500 stocks instead of ten: the S&P 500 members of 2026-11-18 (lab/universe.csv, frozen: a name that stops
   trading drops out and is not replaced) plus the book's names. Alpaca's adjusted daily bars from 2016. The list is
   today's survivors, which biases what is learned from the past but not the score on days that have not happened.
2. The 345 patterns of discover_odds.patterns(). No multiplied pairs.
3. A noise bar instead of a top ten ("shrink, don't crown"). For each horizon a pattern's daily rank IC is averaged in
   blocks (21 sessions; 5 for the shorter horizons) and its strength is t = sum of blocks / sqrt(sum of squares). The
   bar is what the best of all 345 reaches by luck: the 95th percentile, over 500 random re-signings of the blocks, of
   the largest |t|. A pattern votes with weight |t| - bar in the direction it earned, and not at all if its latest 252
   known sessions point the other way. If nothing clears the bar the machine says NO VIEW. That is an answer.
   A second entry, "best guess", is logged beside it so there is a call to watch every day: the same vote with the
   bar lowered to 2 (SOFT), which a pattern clears one time in twenty by luck alone, so with 345 patterns some of
   its voters are always luck. Added after a dry run on 2026-11-23 showed the sure entry silent at 21 and 5 sessions
   and trusting only versions of the 12-month trend at 1; no outcome had been seen and no call logged.
4. Three horizons, each learned on its own outcomes: the next 21 sessions (the official board), the next 5 and the
   next 1 (side boards, for watching; a side board can never be promoted to official after it has been seen).
5. The call: the names ranked by the forecast; the top third is favoured, the bottom third avoided. Two boards: the
   market (the frozen list) and the book (the bot's names). A plain 12-month trend ranking is logged beside it on
   every board as the yardstick.
6. What came true: when a call's horizon has passed, favoured minus avoided (average return of each third, before
   trading costs) and the rank IC. A call is right when favoured beat avoided. The tally counts only calls that do not
   overlap (every 5th or 21st), each board and horizon on its own, beside what a coin would get.
7. No verdict before 20 non-overlapping calls on the official market board (about 20 months). Then, for each of the
   two entries: worth a real test if at least 15 of its 20 were right and its average rank IC is above the trend
   ranking's; otherwise it stays a shadow. Luck passes one entry about 1 time in 50, either of the two about 1 in 25.
   Nothing here trades or touches the bot.
Priors written before the first call. Grok: about 20% that it shows real skill at 21 sessions on a wide list, 12% at 5,
under 10% at 1, each lower after trading costs. A logged, unedited "nothing there" is the most likely useful result.
"""
import os
import time
import warnings

import numpy as np
import pandas as pd
import requests
from scipy.stats import binom

from discover_odds import patterns, z
from model import UNIVERSE

RULES = "v2 2026-11-23"
UNI, CALLS, SCORED, BELIEFS, REPORT = "lab/universe.csv", "signals/calls.csv", "signals/calls_scored.csv", "signals/calls_beliefs.csv", "reports/daily_calls.md"
HORIZONS, START, MIN_NAMES, WARM, FLIPS, RECENT, NEED, PASS, SOFT = (21, 5, 1), "2016-01-01", 100, 400, 500, 252, 20, 15, 2.0
WHO = {"machine": "The machine, sure", "guess": "The machine, best guess", "trend": "The trend ranking"}
TREND = "return over 252 sessions, leaving out the latest 21"
OUTSIDE = {"SPY": "US stocks", "IWM": "small US stocks", "EEM": "emerging-market stocks", "TLT": "long Treasury bonds",
           "IEF": "7-10 year Treasuries", "HYG": "junk bonds", "GLD": "gold", "USO": "oil", "UUP": "the dollar",
           "XLK": "the tech sector", "XLF": "banks", "XLE": "energy stocks", "SMH": "chip stocks", "VIXY": "the VIX",
           "QQQ": "the Nasdaq 100"}
WORDS = {21: "next 21 sessions (official)", 5: "next 5 sessions (side board)", 1: "next session (side board)"}


def bars(symbols):
    """{o, h, l, c, v: [day x symbol]} of Alpaca's adjusted daily bars. The data key comes from the environment (the
    GitHub job) or from .env on the owner's machine. Read-only: this file has no order code."""
    key, sec = os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET_KEY")
    if not key and os.path.exists(".env"):
        env = dict(line.strip().split("=", 1) for line in open(".env") if "=" in line)
        key, sec = env["ALPACA_API_KEY"], env["ALPACA_SECRET_KEY"]
    head, got = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}, {}
    for i in range(0, len(symbols), 100):
        tok = None
        while True:
            q = dict(symbols=",".join(symbols[i:i + 100]), timeframe="1Day", start=START, feed="sip", adjustment="all", limit=10000)
            if tok:
                q["page_token"] = tok
            for attempt in range(6):
                r = requests.get("https://data.alpaca.markets/v2/stocks/bars", headers=head, params=q, timeout=60)
                if r.status_code != 429:
                    break
                time.sleep(5 * (attempt + 1))
            r.raise_for_status()
            j = r.json()
            for s, b in (j.get("bars") or {}).items():
                got.setdefault(s, []).extend(b)
            tok = j.get("next_page_token")
            if not tok:
                break
    frames = {s: pd.DataFrame(b).assign(t=lambda d: pd.to_datetime(d["t"].str[:10])).set_index("t") for s, b in got.items()}
    return {k: pd.DataFrame({s: f[k] for s, f in frames.items()}).sort_index() for k in "ohlcv"}


def rank_ic(r, ry):
    """Per day: correlation across the names of a pattern's ranks with the outcome's ranks, where both exist."""
    ok = ~np.isnan(r) & ~np.isnan(ry)
    n = ok.sum(1)
    a, b = np.where(ok, r, 0.0), np.where(ok, ry, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        ma, mb = a.sum(1) / n, b.sum(1) / n
        ic = ((a * b).sum(1) / n - ma * mb) / np.sqrt(((a * a).sum(1) / n - ma ** 2) * ((b * b).sum(1) / n - mb ** 2))
    return np.where(n >= MIN_NAMES, ic, np.nan)


def learn(c, o, h, l, v, x):
    """(pattern names, today's z-score of every pattern [pattern x stock], daily rank IC [pattern x horizon x day]).
    A day's IC for horizon hz exists only once its outcome is known, hz sessions later."""
    ry = [(c.shift(-hz) / c - 1).rank(axis=1).values for hz in HORIZONS]
    names, today, ic = [], [], []
    for name, val in patterns(c, o, h, l, v, x, OUTSIDE):
        zc = z(val)
        r = zc.rank(axis=1).values
        names.append(name)
        today.append(zc.iloc[-1].values)
        ic.append([rank_ic(r, y) for y in ry])
    return names, np.array(today), np.array(ic, dtype=np.float32)


def believe(ic, hz, rng):
    """({entry: each pattern's vote}, the noise bar, each pattern's strength t) for one horizon. ic: [pattern x day]."""
    last = np.where(~np.isnan(ic).all(0))[0][-1]  # the latest day whose outcome is known
    size = max(hz, 5)
    nb = (last + 1 - WARM) // size
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        bm = np.nan_to_num(np.nanmean(ic[:, last + 1 - nb * size:last + 1].reshape(len(ic), nb, size), 2)).astype(float)
        recent = np.nanmean(ic[:, last + 1 - RECENT:last + 1], 1)
    norm = np.sqrt((bm ** 2).sum(1))
    norm[norm == 0] = np.inf
    t = bm.sum(1) / norm
    bar = np.quantile(np.abs(rng.choice([-1.0, 1.0], size=(FLIPS, nb)) @ bm.T / norm).max(1), 0.95)
    vote = lambda cut: np.sign(t) * np.maximum(np.abs(t) - cut, 0) * (np.sign(recent) == np.sign(t))
    return {"machine": vote(bar), "guess": vote(SOFT)}, bar, t


def _check():
    ic = np.random.default_rng(5).normal(0, 0.1, size=(345, 2400)).astype(np.float32)
    ic[:, -21:] = np.nan
    ic[7] += 0.02   # a real, small pattern among 344 that know nothing: it must be the one that votes
    ic[19] += 0.02  # the same, but wrong lately: it must not vote
    ic[19, -273:] -= 0.06
    votes, bar, t = believe(ic, 21, np.random.default_rng(0))
    w, g = votes["machine"], votes["guess"]
    assert w[7] > 0 and w[19] == 0 and (w != 0).sum() <= 2 and 2.5 < bar < 4.5, (w[7], w[19], (w != 0).sum(), bar)
    assert g[7] > w[7] and g[19] == 0 and (g != 0).sum() < 40, (g != 0).sum()  # the best guess lets some luck in, by design
    r, y = np.random.default_rng(1).normal(size=(2, 50, 200))
    assert abs(np.nanmean(rank_ic(pd.DataFrame(y + r).rank(axis=1).values, pd.DataFrame(y).rank(axis=1).values)) - 0.69) < 0.03


def score_due(calls, scored, c):
    """Rows for calls whose horizon has now passed: what favoured did against avoided, and the rank IC."""
    done, rows = set(zip(scored["date"], scored["horizon"], scored["model"], scored["board"], scored["rules"])), []
    for r in calls[calls["view"] == 1].itertuples():
        k = c.index.get_indexer([pd.Timestamp(r.date)])[0]
        if k < 0 or k + r.horizon >= len(c) or (r.date, r.horizon, r.model, r.board, r.rules) in done:
            continue
        order = r.order.split()
        ret, n3 = (c.iloc[k + r.horizon] / c.iloc[k] - 1).reindex(order), len(order) // 3
        fav, avo = ret.iloc[:n3].mean(), ret.iloc[-n3:].mean()
        rows.append({"date": r.date, "horizon": r.horizon, "model": r.model, "board": r.board, "rules": r.rules,
                     "due": f"{c.index[k + r.horizon].date()}", "favoured": round(fav, 5), "avoided": round(avo, 5),
                     "ic": round(pd.Series(-np.arange(len(order), dtype=float), index=order).corr(ret, method="spearman"), 4),
                     "right": int(fav > avo)})
    return rows


def report(calls, scored, beliefs):
    cur, pct = calls[calls["rules"] == RULES], lambda v: f"{v:+.2%}"
    day = cur["date"].max()
    out = ["# Daily calls: what the machine predicted and what came true\n",
           f"Updated after the close on {day}. Rules \"{RULES}\", written in daily_calls.py before the first call. It never trades.\n",
           "Each day after the close the machine ranks about 500 stocks for three horizons. The top third is *favoured*, the "
           "bottom third *avoided*. When the horizon has passed, a call is **right** if favoured did better than avoided "
           "(before trading costs). There are three entries. **Sure**: only patterns whose record beats what the best of 345 "
           "reaches by luck; if there is none it says \"no view\". **Best guess**: every pattern that stands out one at a time, "
           "so some of its voters are luck. **Trend ranking**: a plain 12-month trend, the yardstick. "
           "Being right more often than a coin is not yet a profit: trading costs come off, most of all on the next-session calls.\n",
           "## The tally\n",
           "Only calls that do not overlap are counted. \"A coin gets\" is the range pure luck lands in 19 times out of 20.\n",
           "| Board | Horizon | Who | Calls counted | Right | A coin gets | Favoured minus avoided | Rank IC | All calls, overlapping | Says |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for board in ("market", "book"):
        for hz in HORIZONS:
            g = {m: scored[(scored["board"] == board) & (scored["horizon"] == hz) & (scored["model"] == m) & (scored["rules"] == RULES)].sort_values("date") for m in WHO}
            for m, a in g.items():
                k, who = a.iloc[::hz], WHO[m][4:]
                n = len(k)
                if n == 0:
                    out.append(f"| {board} | {WORDS[hz]} | {who} | 0 | | | | | | nothing has come due yet |")
                    continue
                lo, hi = binom.ppf([0.025, 0.975], n, 0.5).astype(int)
                says = "side board: for watching only" if hz != 21 or board != "market" else "yardstick" if m == "trend" else f"too early: {n} of {NEED} calls"
                if says.startswith("too early") and n >= NEED:
                    good = k["right"].iloc[:NEED].sum() >= PASS and k["ic"].iloc[:NEED].mean() > g["trend"].iloc[::hz]["ic"].iloc[:NEED].mean()
                    says = "worth a real test" if good else "stays a shadow: not better than luck"
                out.append(f"| {board} | {WORDS[hz]} | {who} | {n} | {k['right'].sum()} | {lo} to {hi} | {pct((k['favoured'] - k['avoided']).mean())} | "
                           f"{k['ic'].mean():+.3f} | {a['right'].sum()} of {len(a)} | {says} |")
    quiet = cur[(cur["model"] == "machine") & (cur["board"] == "market") & (cur["view"] == 0)].groupby("horizon").size()
    days = cur["date"].nunique()
    out.append(f"\nDays logged: {days}. Days the machine had no view: " + ", ".join(f"{WORDS[hz]} {quiet.get(hz, 0)}" for hz in HORIZONS) + ".")

    out.append(f"\n## The calls made after the close on {day}\n")
    for hz in HORIZONS:
        out.append(f"### The {WORDS[hz]}\n")
        b = beliefs[(beliefs["date"] == day) & (beliefs["horizon"] == hz) & (beliefs["rules"] == RULES)]
        for m, who in WHO.items():
            row = {bd: cur[(cur["date"] == day) & (cur["horizon"] == hz) & (cur["model"] == m) & (cur["board"] == bd)] for bd in ("market", "book")}
            if row["market"].empty or not row["market"]["view"].iloc[0]:
                why = f"No pattern stood out from luck (the bar was {row['market']['bar'].iloc[0]:.2f})." if m == "machine" and not row["market"].empty else "Nothing to go on."
                out.append(f"- **{who}: no view.** {why}")
                continue
            o, ob = row["market"]["order"].iloc[0].split(), row["book"]["order"].iloc[0].split() if not row["book"].empty else []
            used = f" (from {row['market']['patterns'].iloc[0]} patterns that stand out one at a time; some of them are luck)" if m == "guess" else ""
            out.append(f"- **{who}**{used}, market: favours most {', '.join(o[:10])}; avoids most {', '.join(o[::-1][:10])}.")
            if ob:
                out.append(f"  In the book: favours {', '.join(ob[:len(ob) // 3])}; avoids {', '.join(ob[::-1][:len(ob) // 3])}.")
        if len(b):
            out.append(f"- What the machine is sure of ({len(b)} patterns cleared the bar of {b['bar'].iloc[0]:.2f}; strongest first):")
            out += [f"  - {r.pattern}: {r.direction} (strength {abs(r.strength):.1f})" for r in b.reindex(b["strength"].abs().sort_values(ascending=False).index).head(8).itertuples()]
        out.append("")

    out += ["## What came due most recently\n", "| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |", "|---|---|---|---|---|---|---|---|"]
    for r in scored[scored["rules"] == RULES].sort_values(["due", "horizon", "board", "model"], ascending=[False, True, False, True]).head(36).itertuples():
        out.append(f"| {r.date} | {r.due} | {WORDS[r.horizon]} | {r.board} | {r.model} | {pct(r.favoured)} | {pct(r.avoided)} | {'right' if r.right else 'wrong'} |")
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def main():
    _check()
    uni = pd.read_csv(UNI)["ticker"].tolist()
    read = lambda p, cols: pd.read_csv(p, keep_default_na=False, na_values=[""]) if os.path.exists(p) else pd.DataFrame(columns=cols)
    calls = read(CALLS, ["date", "horizon", "model", "board", "rules", "view", "patterns", "bar", "order"]).fillna({"order": ""})
    scored = read(SCORED, ["date", "horizon", "model", "board", "rules", "due", "favoured", "avoided", "ic", "right"])
    beliefs = read(BELIEFS, ["date", "horizon", "rules", "pattern", "direction", "strength", "bar"])
    stocks = sorted(set(uni) | set(UNIVERSE) | {n for o in calls["order"] for n in o.split()})
    b = bars(sorted(set(stocks) | set(OUTSIDE)))
    now = pd.Timestamp.now("America/New_York")
    if b["c"].index[-1].date() == now.date() and now.hour < 16:
        b = {k: f.iloc[:-1] for k, f in b.items()}  # the session is still open: its last bar is not a close
    raw = {k: f.reindex(columns=stocks) for k, f in b.items()}
    c = raw["c"].ffill()
    day = f"{c.index[-1].date()}"

    due = score_due(calls, scored, c)
    new, found = [], []
    if not ((calls["date"] == day) & (calls["rules"] == RULES)).any():
        x = np.log(b["c"][list(OUTSIDE)].ffill()).diff()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            names, today, ic = learn(c, raw["o"] / raw["c"], raw["h"] / raw["c"], raw["l"] / raw["c"], raw["v"].replace(0, np.nan), x)
        live = c.iloc[-1].notna() & raw["c"].iloc[-5:].notna().any()  # a name with no bar in a week has stopped trading
        for hi, hz in enumerate(HORIZONS):
            votes, bar, t = believe(ic[:, hi, :], hz, np.random.default_rng(0))
            votes["trend"] = (np.arange(len(names)) == names.index(TREND)).astype(float)
            seen, sure = ~np.isnan(today), votes["machine"]
            found += [{"date": day, "horizon": hz, "rules": RULES, "pattern": names[k], "direction": "higher is better" if sure[k] > 0 else "lower is better",
                       "strength": round(float(t[k]), 2), "bar": round(float(bar), 2)} for k in np.where(sure != 0)[0]]
            for m, w in votes.items():
                heard = (np.abs(w)[:, None] * seen).sum(0)  # a stock is ranked only by the voting patterns that can see it
                s = pd.Series((w[:, None] * np.nan_to_num(today)).sum(0) / np.where(heard > 0, heard, np.nan), index=stocks)
                for board, pool in (("market", uni), ("book", UNIVERSE)):
                    order = list(s.reindex([n for n in pool if live.get(n, False)]).dropna().sort_values(ascending=False, kind="stable").index)
                    view = int(len(order) >= 6 and (w != 0).any())
                    new.append({"date": day, "horizon": hz, "model": m, "board": board, "rules": RULES, "view": view,
                                "patterns": int((w != 0).sum()), "bar": round(float(bar), 2), "order": " ".join(order) if view else ""})
    for path, rows in ((SCORED, due), (CALLS, new), (BELIEFS, found)):
        if rows:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pd.DataFrame(rows).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    cat = lambda old, rows: pd.concat([old, pd.DataFrame(rows)], ignore_index=True) if rows else old
    report(cat(calls, new), cat(scored, due), cat(beliefs, found))
    print(f"daily calls for {day}: {len(new)} calls logged, {len(due)} scored, {len(found)} trusted patterns")


if __name__ == "__main__":
    main()
