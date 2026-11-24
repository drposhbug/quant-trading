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
   The crowd is counted too (the owner's point, 2026-11-23: many lucky-looking things at once may be one real thing
   nobody proved). Each day: how many of the 345 stand out one at a time (|t| above 2), beside how many the same
   re-signings give by luck. Far more than luck means something real is in there even where no single pattern
   clears the bar; the best-guess entry is the one that trades on it. Near-copies of one pattern count many times.
7. The verdict has two stages (changed 2026-11-23, before any call had come due and before the past record below
   had been computed, after the owner asked why wait 20 months when the past is all there).
   A. The past test, available the same day. Every 5th session from 2019 on, each entry's call is rebuilt with
      only what was known that day and checked against what followed (past()). Counting only calls that do not
      overlap, an entry passes on a board and horizon if it was right more often than a coin would be 19 times in
      20 and its average favoured-minus-avoided gap has t >= 2. The call rules above were committed (22e460e)
      before this record was computed. Its weak spots: the list is today's surviving companies, which flatters
      every entry a little; and six machine results are read on the market board (two entries, three horizons),
      so one narrow pass has about a 1 in 4 chance of being luck.
   B. New days confirm or contradict. Checked at 20, 40, 60... non-overlapping new calls: confirmed if right more
      often than a coin would be 19 times in 20 at that count. Earliest: a month at 1 session, five months at 5,
      twenty at 21. An entry that failed A is marked so whatever B shows early.
   Nothing here trades or touches the bot. An entry that passes A and is confirmed in B is worth a costed test.
8. Probabilities (PRULES, added 2026-11-23 before any call had come due). Every call carries the chance that it
   comes true, and each of the book's names the chance that it beats the typical stock (the median of the market
   list) over the horizon. They start from the entry's record on old days (A above; for the names, how often the
   stocks in each tenth of its ranking beat the typical one). That record is pulled toward 50% and counts for at
   most 100 calls (5,000 stock outcomes per tenth); every real result since is added on top, so the probabilities
   learn from what comes true. They are scored as well: the Brier score against a coin's 0.25, and how often each
   band of stated chance came true.
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
PROBS, PSCORED, PAST, PRULES = "signals/calls_probs.csv", "signals/calls_probs_scored.csv", "signals/calls_past.csv", "p1 2026-11-23"
STAND = "signals/calls_standouts.csv"
STEP, CAL0, CAP_CALLS, CAP_NAMES = 5, 904, 100, 5000  # old days: every 5th session from session 904 (WARM + two years of record)
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
    """(pattern names, today's z-score of every pattern [pattern x stock], daily rank IC [pattern x horizon x day],
    every pattern's z-scores on the old days used for the record [pattern x old day x stock], those days).
    A day's IC for horizon hz exists only once its outcome is known, hz sessions later."""
    ry = [(c.shift(-hz) / c - 1).rank(axis=1).values for hz in HORIZONS]
    grid = np.arange(CAL0, len(c), STEP)
    names, today, ic, zg = [], [], [], []
    for name, val in patterns(c, o, h, l, v, x, OUTSIDE):
        zc = z(val)
        r = zc.rank(axis=1).values
        names.append(name)
        today.append(zc.iloc[-1].values)
        zg.append(zc.values[grid].astype(np.float16))
        ic.append([rank_ic(r, y) for y in ry])
    return names, np.array(today), np.array(ic, dtype=np.float32), np.array(zg), grid


def believe(ic, hz, rng, last=None):
    """({entry: each pattern's vote}, the noise bar, each pattern's strength t) for one horizon. ic: [pattern x day]."""
    if last is None:
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
    lucky = np.abs(rng.choice([-1.0, 1.0], size=(FLIPS, nb)) @ bm.T / norm)  # what luck alone does to all 345 at once
    bar, crowd = np.quantile(lucky.max(1), 0.95), (lucky > SOFT).sum(1)
    vote = lambda cut: np.sign(t) * np.maximum(np.abs(t) - cut, 0) * (np.sign(recent) == np.sign(t))
    # the crowd: how many patterns stand out one at a time, beside how many luck gives (typically, and at most 19 times in 20)
    return {"machine": vote(bar), "guess": vote(SOFT)}, bar, t, (int((np.abs(t) > SOFT).sum()), float(np.median(crowd)), float(np.quantile(crowd, 0.95)))


def _check():
    ic = np.random.default_rng(5).normal(0, 0.1, size=(345, 2400)).astype(np.float32)
    ic[:, -21:] = np.nan
    ic[7] += 0.02   # a real, small pattern among 344 that know nothing: it must be the one that votes
    ic[19] += 0.02  # the same, but wrong lately: it must not vote
    ic[19, -273:] -= 0.06
    votes, bar, t, crowd = believe(ic, 21, np.random.default_rng(0))
    w, g = votes["machine"], votes["guess"]
    assert crowd[0] < 2 * crowd[2] and crowd[2] > 5, crowd  # 343 know nothing: the count of standouts is about what luck gives
    assert w[7] > 0 and w[19] == 0 and (w != 0).sum() <= 2 and 2.5 < bar < 4.5, (w[7], w[19], (w != 0).sum(), bar)
    assert g[7] > w[7] and g[19] == 0 and (g != 0).sum() < 40, (g != 0).sum()  # the best guess lets some luck in, by design
    r, y = np.random.default_rng(1).normal(size=(2, 50, 200))
    assert abs(np.nanmean(rank_ic(pd.DataFrame(y + r).rank(axis=1).values, pd.DataFrame(y).rank(axis=1).values)) - 0.69) < 0.03


def rank_names(w, zrow):
    """One score per stock from the voting patterns' z-scores. A stock is ranked only by the voters that can see it."""
    heard = (np.abs(w)[:, None] * ~np.isnan(zrow)).sum(0)
    return (w[:, None] * np.nan_to_num(zrow)).sum(0) / np.where(heard > 0, heard, np.nan)


def past(ic, zg, grid, c, names, mkt, book):
    """Each entry's record on old days: every STEP-th session the call is rebuilt with only what was known that day
    and checked against what followed. {(entry, horizon): market and book [calls, right]; hit and n per tenth of the
    market ranking (how many names beat the typical one; tenth 9 is the most favoured)}. mkt, book: column positions."""
    rec, trend = {}, (np.arange(len(names)) == names.index(TREND)).astype(float)
    for hi, hz in enumerate(HORIZONS):
        f = (c.shift(-hz) / c - 1).values
        for gi, d in enumerate(grid):
            if d + hz >= len(c):
                break
            votes = believe(ic[:, hi, :], hz, np.random.default_rng(0), last=d - hz)[0]  # ICs whose outcome was known at d
            votes["trend"] = trend
            for m, w in votes.items():
                nz = w != 0
                if not nz.any():
                    continue
                s = rank_names(w[nz], zg[nz, gi, :].astype(np.float32))
                r = rec.setdefault((m, hz), {"market": [0, 0], "book": [0, 0], "hit": np.zeros(10), "n": np.zeros(10), "log": {"market": [], "book": []}})
                for board, cols in (("market", mkt), ("book", book)):
                    ok = cols[~np.isnan(s[cols]) & ~np.isnan(f[d, cols])]
                    if len(ok) < 6:
                        continue
                    order = ok[np.argsort(-s[ok], kind="stable")]
                    k = len(order) // 3
                    gap = f[d, order[:k]].mean() - f[d, order[-k:]].mean()
                    r[board][0] += 1
                    r[board][1] += int(gap > 0)
                    r["log"][board].append((d, gap))
                    if board == "market":
                        tenth = np.minimum((np.arange(len(order))[::-1] * 10) // len(order), 9)
                        r["hit"] += np.bincount(tenth, weights=(f[d, order] > np.median(f[d, order])).astype(float), minlength=10)
                        r["n"] += np.bincount(tenth, minlength=10)
    return rec


def past_test(rec, day):
    """Stage A (docstring, 7): each entry's record on old days, counting only calls that do not overlap."""
    rows = []
    for (m, hz), r in rec.items():
        for board in ("market", "book"):
            keep, nxt = [], -1
            for d, gap in r["log"][board]:
                if d >= nxt:
                    keep.append(gap)
                    nxt = d + hz
            g = np.array(keep)
            if len(g) < 2:
                continue
            n, right, t = len(g), int((g > 0).sum()), g.mean() / (g.std(ddof=1) / np.sqrt(len(g)))
            lo, hi = binom.ppf([0.025, 0.975], n, 0.5).astype(int)
            rows.append({"as_of": day, "model": m, "horizon": hz, "board": board, "calls": n, "right": right, "coin": f"{lo} to {hi}",
                         "gap": round(float(g.mean()), 5), "t": round(float(t), 2), "passed": int(right > binom.ppf(0.95, n, 0.5) and t >= 2)})
    return rows


def chance(right, n, since=(0, 0), cap=CAP_CALLS, soft=10):
    """A probability from a past record, pulled toward 50% (as if `soft` more hits and `soft` more misses), counted
    for at most `cap` outcomes, then moved by the real results since then: (right, n)."""
    m = min(n, cap)
    return ((right + soft) / (n + 2 * soft) * m + since[0]) / (m + since[1]) if m + since[1] else 0.5


def score_due(calls, scored, c):
    """Rows for calls whose horizon has now passed: what favoured did against avoided, the rank IC, and for each
    tenth of the ranking how many names beat the typical one."""
    done, rows = set(zip(scored["date"], scored["horizon"], scored["model"], scored["board"], scored["rules"])), []
    for r in calls[calls["view"] == 1].itertuples():
        k = c.index.get_indexer([pd.Timestamp(r.date)])[0]
        if k < 0 or k + r.horizon >= len(c) or (r.date, r.horizon, r.model, r.board, r.rules) in done:
            continue
        order = r.order.split()
        ret, n3 = (c.iloc[k + r.horizon] / c.iloc[k] - 1).reindex(order), len(order) // 3
        fav, avo, ok = ret.iloc[:n3].mean(), ret.iloc[-n3:].mean(), ret.notna().values
        tenth = np.minimum((np.arange(len(order))[::-1] * 10) // len(order), 9)[ok]
        beat = (ret.values[ok] > np.nanmedian(ret.values)).astype(float)
        rows.append({"date": r.date, "horizon": r.horizon, "model": r.model, "board": r.board, "rules": r.rules,
                     "due": f"{c.index[k + r.horizon].date()}", "favoured": round(fav, 5), "avoided": round(avo, 5),
                     "ic": round(pd.Series(-np.arange(len(order), dtype=float), index=order).corr(ret, method="spearman"), 4),
                     "right": int(fav > avo), "dec_hit": " ".join(f"{v:.0f}" for v in np.bincount(tenth, weights=beat, minlength=10)),
                     "dec_n": " ".join(f"{v:.0f}" for v in np.bincount(tenth, minlength=10))})
    return rows


def score_names(probs, pscored, calls, c):
    """Rows for the book's stocks whose horizon has passed: did the stock beat the typical stock of the market list?"""
    done, rows, med = set(zip(pscored["date"], pscored["horizon"], pscored["model"], pscored["name"])), [], {}
    for r in probs[~probs["name"].str.startswith("*")].itertuples():
        k = c.index.get_indexer([pd.Timestamp(r.date)])[0]
        if k < 0 or k + r.horizon >= len(c) or (r.date, r.horizon, r.model, r.name) in done:
            continue
        ret, key = c.iloc[k + r.horizon] / c.iloc[k] - 1, (r.date, r.horizon)
        if key not in med:  # the typical stock: the median of the market list as ranked that day
            pool = calls[(calls["date"] == r.date) & (calls["horizon"] == r.horizon) & (calls["model"] == "trend") & (calls["board"] == "market")]["order"]
            med[key] = ret.reindex(pool.iloc[0].split()).median() if len(pool) else np.nan
        if pd.notna(ret.get(r.name, np.nan)) and pd.notna(med[key]):
            rows.append({"date": r.date, "horizon": r.horizon, "model": r.model, "name": r.name, "p": r.p,
                         "beat": int(ret[r.name] > med[key]), "due": f"{c.index[k + r.horizon].date()}"})
    return rows


def counted(scored, m, hz, board):
    """An entry's scored calls on one board that do not overlap (every hz-th)."""
    return scored[(scored["board"] == board) & (scored["horizon"] == hz) & (scored["model"] == m) & (scored["rules"] == RULES)].sort_values("date").iloc[::hz]


def report(calls, scored, beliefs, probs, pscored, old, stand):
    cur, pct, short = calls[calls["rules"] == RULES], lambda v: f"{v:+.2%}", {"machine": "sure", "guess": "best guess", "trend": "trend"}
    day = cur["date"].max()
    pr = probs[(probs["date"] == day) & (probs["rules"] == PRULES)].set_index(["horizon", "model", "name"])
    odds = lambda hz, m, name: f" **{pr.loc[(hz, m, name), 'p']:.0%} that favoured beats avoided**, {1 - pr.loc[(hz, m, name), 'p']:.0%} that it does not." if (hz, m, name) in pr.index else ""
    out = ["# Daily calls: what the machine predicted and what came true\n",
           f"Updated after the close on {day}. Rules \"{RULES}\", written in daily_calls.py before the first call. It never trades.\n",
           "Each day after the close the machine ranks about 500 stocks for three horizons. The top third is *favoured*, the "
           "bottom third *avoided*. When the horizon has passed, a call is **right** if favoured did better than avoided "
           "(before trading costs). There are three entries. **Sure**: only patterns whose record beats what the best of 345 "
           "reaches by luck; if there is none it says \"no view\". **Best guess**: every pattern that stands out one at a time, "
           "so some of its voters are luck. **Trend ranking**: a plain 12-month trend, the yardstick. "
           "Every call carries a probability, and the probabilities are checked too (last section). "
           "Being right more often than a coin is not yet a profit: trading costs come off, most of all on the next-session calls.\n",
           "## The fast answer: its record on the past\n",
           "Every fifth session since 2019 each entry's call was rebuilt with only what was known that day, then checked against what followed. "
           "Only calls that do not overlap are counted. \"A coin gets\" is the range pure luck lands in 19 times out of 20. An entry **passes** if it was "
           "right more often than a coin would be 19 times in 20 and its average gap is clearly above zero (t of 2 or more). Two cautions: the list is "
           "today's surviving companies, which flatters every entry a little, and several entries are tested, so a single narrow pass can be luck.\n",
           "| Board | Horizon | Who | Calls | Right | A coin gets | Favoured minus avoided | t | Past test |", "|---|---|---|---|---|---|---|---|---|"]
    ok = {(r.model, r.horizon, r.board): r.passed for r in old.itertuples()}
    for board in ("market", "book"):
        for hz in HORIZONS:
            for r in old[(old["board"] == board) & (old["horizon"] == hz)].set_index("model").reindex(list(WHO)).dropna(subset=["calls"]).itertuples():
                verdict = "yardstick" if r.Index == "trend" else "**passes**" if r.passed else "no better than a coin"
                out.append(f"| {board} | {WORDS[hz]} | {WHO[r.Index][4:]} | {r.calls:.0f} | {r.right:.0f} ({r.right / r.calls:.0%}) | {r.coin} | {pct(r.gap)} | {r.t:+.1f} | {verdict} |")
    out += ["\n## The tally on new days\n",
            "New days confirm or contradict the past. Only calls that do not overlap are counted, and an entry is checked at 20, 40, 60... calls.\n",
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
                cp = n // NEED * NEED  # the latest checkpoint reached
                says = "yardstick" if m == "trend" else f"too early: {n} of {NEED} calls" if not cp else "confirmed on new days" if k["right"].iloc[:cp].sum() > binom.ppf(0.95, cp, 0.5) else f"not confirmed at {cp} calls"
                if m != "trend" and not ok.get((m, hz, board), 0):
                    says += " (failed the past test)"
                out.append(f"| {board} | {WORDS[hz]} | {who} | {n} | {k['right'].sum()} | {lo} to {hi} | {pct((k['favoured'] - k['avoided']).mean())} | "
                           f"{k['ic'].mean():+.3f} | {a['right'].sum()} of {len(a)} | {says} |")
    quiet = cur[(cur["model"] == "machine") & (cur["board"] == "market") & (cur["view"] == 0)].groupby("horizon").size()
    days = cur["date"].nunique()
    out.append(f"\nDays logged: {days}. Days the sure entry had no view: " + ", ".join(f"{WORDS[hz]} {quiet.get(hz, 0)}" for hz in HORIZONS) + ".")

    out.append(f"\n## The calls made after the close on {day}\n")
    for hz in HORIZONS:
        out.append(f"### The {WORDS[hz]}\n")
        b = beliefs[(beliefs["date"] == day) & (beliefs["horizon"] == hz) & (beliefs["rules"] == RULES)]
        for r in stand[(stand["date"] == day) & (stand["horizon"] == hz)].itertuples():
            more = "More than luck: something real is in there, even where no single pattern proves it." if r.standouts > r.luck_high else "About what luck gives."
            out.append(f"- Patterns that stand out one at a time: **{r.standouts}** of 345. Luck alone usually gives about {r.luck_typical:.0f} and rarely more than {r.luck_high:.0f}. {more}")
        for m, who in WHO.items():
            row = {bd: cur[(cur["date"] == day) & (cur["horizon"] == hz) & (cur["model"] == m) & (cur["board"] == bd)] for bd in ("market", "book")}
            if row["market"].empty or not row["market"]["view"].iloc[0]:
                why = f"No pattern stood out from luck (the bar was {row['market']['bar'].iloc[0]:.2f})." if m == "machine" and not row["market"].empty else "Nothing to go on."
                out.append(f"- **{who}: no view.** {why}")
                continue
            o, ob = row["market"]["order"].iloc[0].split(), row["book"]["order"].iloc[0].split() if not row["book"].empty else []
            used = f" (from {row['market']['patterns'].iloc[0]} patterns that stand out one at a time; some of them are luck)" if m == "guess" else ""
            out.append(f"- **{who}**{used}, market: favours most {', '.join(o[:10])}; avoids most {', '.join(o[::-1][:10])}.{odds(hz, m, '*market')}")
            if ob:
                out.append(f"  In the book: favours {', '.join(ob[:len(ob) // 3])}; avoids {', '.join(ob[::-1][:len(ob) // 3])}.{odds(hz, m, '*book')}")
        if len(b):
            out.append(f"- What the machine is sure of ({len(b)} patterns cleared the bar of {b['bar'].iloc[0]:.2f}; strongest first):")
            out += [f"  - {r.pattern}: {r.direction} (strength {abs(r.strength):.1f})" for r in b.reindex(b["strength"].abs().sort_values(ascending=False).index).head(8).itertuples()]
        out.append("")

    stock = sorted(n for n in pr.index.get_level_values("name").unique() if not n.startswith("*"))
    if stock:
        cols = [(hz, m) for hz in HORIZONS for m in WHO]
        out += ["## The chance that each of the bot's stocks beats the typical stock\n",
                "\"Beats the typical stock\" means it does better than the middle stock of the market list over that horizon, so 50% is a coin. "
                "The columns are the horizon in sessions and the entry. These numbers stay close to 50% because that is what the record supports.\n",
                "| Stock | " + " | ".join(f"{hz}: {short[m]}" for hz, m in cols) + " |", "|---" * (len(cols) + 1) + "|"]
        out += [f"| {n} | " + " | ".join(f"{pr.loc[(hz, m, n), 'p']:.1%}" if (hz, m, n) in pr.index else "no view" for hz, m in cols) + " |" for n in stock]
        out.append("")

    out += ["## Where the probabilities come from\n",
            "Each starts from the entry's record on old days: every fifth session since 2019 the call was rebuilt with only what was known that day, "
            "and checked against what followed. That record is pulled toward 50% and counts for at most 100 calls; every real result since is added on top, "
            "so the probabilities learn from what comes true. The old-days record is on companies that still exist today, which flatters it a little.\n",
            "| Entry | Horizon | Board | Its record on old days | Real results since | Chance today |", "|---|---|---|---|---|---|"]
    for (hz, m, name), r in pr[pr.index.get_level_values("name").str.startswith("*")].iterrows():
        g = counted(scored, m, hz, name[1:])
        was = f"right in {r['past_right'] / r['past_n']:.0%} of {r['past_n']:.0f} calls" if r["past_n"] else "none"
        out.append(f"| {WHO[m][4:]} | {WORDS[hz]} | {name[1:]} | {was} | {g['right'].sum()} of {len(g)} | {r['p']:.0%} |")

    out.append("\n## Were the probabilities honest?\n")
    board = probs[probs["name"].str.startswith("*")].assign(board=lambda d: d["name"].str[1:])[["date", "horizon", "model", "board", "p"]]
    j = scored[scored["rules"] == RULES].merge(board, on=["date", "horizon", "model", "board"])
    if j.empty and pscored.empty:
        out.append("Nothing has come due yet. When it has: the Brier score (a coin that always says 50% scores 0.250, lower is better), and how often each band of stated chance came true.")
    for what, g, hit in (("Calls", j, "right"), ("Stocks", pscored, "beat")):
        if len(g):
            out += [f"**{what}**: {len(g)} scored, Brier score {((g['p'] - g[hit]) ** 2).mean():.4f} against a coin's 0.2500.\n",
                    "| Stated chance | How many | Came true |", "|---|---|---|"]
            band = pd.cut(g["p"], [0, 0.48, 0.5, 0.52, 0.55, 1], labels=["under 48%", "48 to 50%", "50 to 52%", "52 to 55%", "over 55%"])
            out += [f"| {k} | {len(a)} | {a[hit].mean():.0%} |" for k, a in g.groupby(band, observed=True)]
            out.append("")

    out += ["\n## What came due most recently\n", "| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |", "|---|---|---|---|---|---|---|---|"]
    for r in scored[scored["rules"] == RULES].sort_values(["due", "horizon", "board", "model"], ascending=[False, True, False, True]).head(36).itertuples():
        out.append(f"| {r.date} | {r.due} | {WORDS[r.horizon]} | {r.board} | {WHO[r.model][4:]} | {pct(r.favoured)} | {pct(r.avoided)} | {'right' if r.right else 'wrong'} |")
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def main():
    _check()
    uni = pd.read_csv(UNI)["ticker"].tolist()
    read = lambda p, cols: pd.read_csv(p, keep_default_na=False, na_values=[""]) if os.path.exists(p) else pd.DataFrame(columns=cols)
    cat = lambda old, rows: pd.concat([old, pd.DataFrame(rows)], ignore_index=True) if rows else old
    calls = read(CALLS, ["date", "horizon", "model", "board", "rules", "view", "patterns", "bar", "order"]).fillna({"order": ""})
    scored = read(SCORED, ["date", "horizon", "model", "board", "rules", "due", "favoured", "avoided", "ic", "right", "dec_hit", "dec_n"])
    beliefs = read(BELIEFS, ["date", "horizon", "rules", "pattern", "direction", "strength", "bar"])
    probs = read(PROBS, ["date", "horizon", "model", "name", "p", "past_right", "past_n", "rules"]).astype({"name": str})
    pscored = read(PSCORED, ["date", "horizon", "model", "name", "p", "beat", "due"])
    old = read(PAST, ["as_of", "model", "horizon", "board", "calls", "right", "coin", "gap", "t", "passed"])
    stand, snew = read(STAND, ["date", "horizon", "standouts", "luck_typical", "luck_high", "rules"]), []
    stocks = sorted(set(uni) | set(UNIVERSE) | {n for o in calls["order"] for n in o.split()})
    b = bars(sorted(set(stocks) | set(OUTSIDE)))
    now = pd.Timestamp.now("America/New_York")
    if b["c"].index[-1].date() == now.date() and now.hour < 16:
        b = {k: f.iloc[:-1] for k, f in b.items()}  # the session is still open: its last bar is not a close
    raw = {k: f.reindex(columns=stocks) for k, f in b.items()}
    c = raw["c"].ffill()
    day = f"{c.index[-1].date()}"

    due, pdue = score_due(calls, scored, c), score_names(probs, pscored, calls, c)
    scored, pscored = cat(scored, due), cat(pscored, pdue)
    new, found, pnew = [], [], []
    logged = ((calls["date"] == day) & (calls["rules"] == RULES)).any()
    if not logged or not ((probs["date"] == day) & (probs["rules"] == PRULES)).any():
        x = np.log(b["c"][list(OUTSIDE)].ffill()).diff()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            names, today, ic, zg, grid = learn(c, raw["o"] / raw["c"], raw["h"] / raw["c"], raw["l"] / raw["c"], raw["v"].replace(0, np.nan), x)
            at = {n: i for i, n in enumerate(stocks)}
            rec = past(ic, zg, grid, c, names, np.array([at[n] for n in uni]), np.array([at[n] for n in UNIVERSE]))
        old = pd.DataFrame(past_test(rec, day))
        old.to_csv(PAST, index=False)  # rewritten each day: it is a summary of old days, not a log of new ones
        live = c.iloc[-1].notna() & raw["c"].iloc[-5:].notna().any()  # a name with no bar in a week has stopped trading
        for hi, hz in enumerate(HORIZONS):
            votes, bar, t, crowd = believe(ic[:, hi, :], hz, np.random.default_rng(0))
            votes["trend"], sure = (np.arange(len(names)) == names.index(TREND)).astype(float), votes["machine"]
            if not ((stand["date"] == day) & (stand["horizon"] == hz)).any():
                snew.append({"date": day, "horizon": hz, "standouts": crowd[0], "luck_typical": round(crowd[1]), "luck_high": round(crowd[2]), "rules": RULES})
            if not logged:
                found += [{"date": day, "horizon": hz, "rules": RULES, "pattern": names[k], "direction": "higher is better" if sure[k] > 0 else "lower is better",
                           "strength": round(float(t[k]), 2), "bar": round(float(bar), 2)} for k in np.where(sure != 0)[0]]
            for m, w in votes.items():
                s, order = pd.Series(rank_names(w, today), index=stocks), {}
                for board, pool in (("market", uni), ("book", UNIVERSE)):
                    o = list(s.reindex([n for n in pool if live.get(n, False)]).dropna().sort_values(ascending=False, kind="stable").index)
                    order[board] = o if len(o) >= 6 and (w != 0).any() else []
                    if not logged:
                        new.append({"date": day, "horizon": hz, "model": m, "board": board, "rules": RULES, "view": int(bool(order[board])),
                                    "patterns": int((w != 0).sum()), "bar": round(float(bar), 2), "order": " ".join(order[board])})
                r = rec.get((m, hz))
                if r is None or not order["market"]:
                    continue
                row = lambda name, p, right, n: {"date": day, "horizon": hz, "model": m, "name": name, "p": round(float(p), 4),
                                                 "past_right": round(float(right), 1), "past_n": round(float(n), 1), "rules": PRULES}
                for board in ("market", "book"):  # the old-days calls are STEP sessions apart: longer horizons overlap, so they count for less
                    n, right, g = r[board][0] * min(1, STEP / hz), r[board][1] * min(1, STEP / hz), counted(scored, m, hz, board)
                    if order[board]:
                        pnew.append(row("*" + board, chance(right, n, (g["right"].sum(), len(g))), right, n))
                g, pool = counted(scored, m, hz, "market"), s.reindex(order["market"]).values
                fh, fn = (np.array([[float(v) for v in str(q).split()] for q in g[col]]).sum(0) if len(g) else np.zeros(10) for col in ("dec_hit", "dec_n"))
                for name in order["book"]:
                    k = min(int((pool < s[name]).mean() * 10), 9)  # which tenth of the market ranking the stock sits in today
                    pnew.append(row(name, chance(r["hit"][k], r["n"][k], (fh[k], fn[k]), CAP_NAMES, 50), r["hit"][k], r["n"][k]))
    for path, rows in ((SCORED, due), (PSCORED, pdue), (CALLS, new), (BELIEFS, found), (PROBS, pnew), (STAND, snew)):
        if rows:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pd.DataFrame(rows).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    report(cat(calls, new), scored, cat(beliefs, found), cat(probs, pnew), pscored, old, cat(stand, snew))
    print(f"daily calls for {day}: {len(new)} calls logged, {len(pnew)} probabilities, {len(due)} calls and {len(pdue)} stocks scored, {len(found)} trusted patterns")


if __name__ == "__main__":
    main()
