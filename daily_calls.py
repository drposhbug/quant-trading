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
2. The 332 patterns of discover_odds.patterns() (15 outside series here; the first pattern-finder had 16 and
   345). No multiplied pairs.
3. A noise bar instead of a top ten ("shrink, don't crown"). For each horizon a pattern's daily rank IC is averaged in
   blocks (21 sessions; 5 for the shorter horizons) and its strength is t = sum of blocks / sqrt(sum of squares). The
   bar is what the best of all 332 reaches by luck: the 95th percentile, over 500 random re-signings of the blocks, of
   the largest |t|. A pattern votes with weight |t| - bar in the direction it earned, and not at all if its latest 252
   known sessions point the other way. If nothing clears the bar the machine says NO VIEW. That is an answer.
   A second entry, "best guess", is logged beside it so there is a call to watch every day: the same vote with the
   bar lowered to 2 (SOFT), which a pattern clears one time in twenty by luck alone, so with 332 patterns some of
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
   nobody proved). Each day: how many of the 332 stand out one at a time (|t| above 2), beside how many the same
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
   B. New days confirm or contradict, by a running evidence score that may be read after every call
      (evidence(): the likelihood of "right more often than a coin", averaged over every hit rate above 50%,
      against a coin). Luck alone takes it to 20 at most 1 time in 20, however often one looks. Confirmed at 20.
      Typical wait: about 160 non-overlapping calls if the true hit rate is 60%, 800 at 55%, 2,400 at 53%. It
      replaces checks at 20, 40, 60 calls, which could not confirm anything much below 60%. An entry that failed
      A is marked so whatever B shows early.
   Nothing here trades or touches the bot. An entry that passes A and is confirmed in B is worth a costed test.
8. Probabilities (PRULES, added 2026-11-23 before any call had come due). Every call carries the chance that it
   comes true, and each of the book's names the chance that it beats the typical stock (the median of the market
   list) over the horizon. They start from the entry's record on old days (A above; for the names, how often the
   stocks in each tenth of its ranking beat the typical one). That record is pulled toward 50% and counts for at
   most 100 calls (5,000 stock outcomes per tenth); every real result since is added on top, so the probabilities
   learn from what comes true. They are scored as well: the Brier score against a coin's 0.25, and how often each
   band of stated chance came true.
9. The clock (RULES v3, 2026-11-23, before any call had been scored). A call made after the close cannot be traded
   at that close. Every outcome, in learning, in the past test and on new days, now runs from the next session's
   open to the close hz sessions after the call (ahead()). Found the same night by two routes. The trend's whole
   one-session edge sits in the overnight step that an after-close call misses: +2.8 bp a night (t 2.5) against
   -2.2 bp in the daytime, on about 500 names since 2017. And Astra's first-principles review named the execution
   clock as the first thing to fix (research_notes/Smarter machine 2026-11-23/). The v2 calls logged for
   2026-11-23 are kept in the files and are never scored.
10. Rules v4 (2026-11-23, written before its past test was run; from the research round in "reports/Making the
   machine smarter (2026-11-23).md" and Grok's attack on it).
   - The list: every company that was in the index on the day, dead ones included, when the dated membership
     files exist (wide_universe.py). A call made just before a company's last bar exits at that last price.
   - Shared moves are taken out of both the patterns and the outcomes they are learned on: within each day, each
     sector's average and the part that goes with market beta (strip). A stock's sector is the sector fund it has
     moved with most over the last 252 sessions, market taken out; its beta is over the same window (groups).
     Style is left in: taking it out would take out the trend itself. Calls are still judged on real returns.
   - One learner replaces "sure" and "best guess" (believe). It speaks only if the whole crowd of price patterns
     beats luck: Q = the sum of their t squared against the same sum under re-signing, 95th percentile. It then
     weights them by (S + gI)^-1 m, so near-copies share one weight. The trend ranking stays as the yardstick;
     "calm" is the trend standing aside while its own bet is wilder than usual (wild).
   - Information entries, each one idea fixed in advance and judged on its own, never through the learner:
     busy/quiet month (21 sessions), earnings surprise (21), profitability (21), about to report (5). An entry
     whose data file is missing is not logged. Their definitions are in the info_ functions.
   - Judged as in 7: the past test from the next open, then new days by the evidence score. Ten machine results
     are read on the market board in the past test, so about four readings in ten would show one narrow pass by
     luck alone. A pass needs a wide margin, or confirmation on new days.
Priors written before the first call. Grok: about 20% that it shows real skill at 21 sessions on a wide list, 12% at 5,
under 10% at 1, each lower after trading costs. A logged, unedited "nothing there" is the most likely useful result.
"""
import itertools
import os
import time
import warnings

import numpy as np
import pandas as pd
import requests
from scipy.special import betainc, betaln
from scipy.stats import binom

from discover_odds import patterns, z
from model import UNIVERSE

RULES = "v4 2026-11-23"
UNI, CALLS, SCORED, BELIEFS, REPORT = "lab/universe.csv", "signals/calls.csv", "signals/calls_scored.csv", "signals/calls_beliefs.csv", "reports/daily_calls.md"
PROBS, PSCORED, PAST, PRULES = "signals/calls_probs.csv", "signals/calls_probs_scored.csv", "signals/calls_past.csv", "p3 2026-11-23"
STAND = "signals/calls_standouts.csv"
STEP, CAL0, CAP_CALLS, CAP_NAMES = 5, 904, 100, 5000  # old days: every 5th session from session 904 (WARM + two years of record)
HORIZONS, START, MIN_NAMES, WARM, FLIPS, RECENT, NEED, PASS, SOFT = (21, 5, 1), "2016-01-01", 100, 400, 500, 252, 20, 15, 2.0
EARN, FUND = "lab/earnings.csv", "lab/fundamentals.csv"
SECTORS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC"]  # the sector funds used to tell sectors apart
ENTRY_H = {"learner": (21, 5, 1), "trend": (21, 5, 1), "calm": (21, 5, 1), "busy": (21,), "surprise": (21,), "profit": (21,), "soon": (5,)}
BOOK = ("learner", "trend", "calm")  # the entries that also rank the bot's own names
WHO = {"learner": "The learner", "trend": "The trend ranking", "calm": "The trend on calm days", "busy": "Busy month, quiet month",
       "surprise": "Earnings surprise", "soon": "About to report", "profit": "Profitability"}
SHORT = {"learner": "learner", "trend": "trend ranking", "calm": "trend, calm days", "busy": "busy/quiet month", "surprise": "earnings surprise",
         "soon": "about to report", "profit": "profitability"}
WHAT = {"learner": "all the price patterns combined, with near-copies sharing one weight. It speaks only when the whole crowd of patterns beats luck; otherwise \"no view\".",
        "trend": "a plain 12-month trend. The yardstick.",
        "calm": "the same trend, standing aside while its own bet has been wilder than usual.",
        "busy": "last month's winners keep going if they traded unusually heavily, and turn back if they were quiet.",
        "surprise": "stocks that beat the earnings forecast at their latest report, for 63 sessions after it.",
        "soon": "stocks due to report earnings within about a week.",
        "profit": "companies with more gross profit per dollar of assets, as first reported."}
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


def ahead(c, op, hz):
    """What a call can actually earn, [day x stock]: bought at the next session's open, the first price after an
    after-close call, and held to the close hz sessions after the call. A missing open falls back to the close."""
    return c.shift(-hz) / op.shift(-1).fillna(c) - 1


def evidence(k, n):
    """How strongly k right calls out of n speak for "right more often than a coin" (docstring, 7B): 1 is nothing,
    20 confirms. 2^(n+1) B(k+1, n-k+1) I_1/2(n-k+1, k+1), the average over every hit rate above 50% of the likelihood
    against a coin. Under a coin it is a fair bet at every step, so it ever reaches 20 at most 1 time in 20."""
    return float(np.exp((n + 1) * np.log(2) + betaln(k + 1, n - k + 1)) * betainc(n - k + 1, k + 1, 0.5))


def groups(c, spy, funds, win=252, every=21):
    """Point in time, for every day and stock: its market beta, and its sector, taken as the sector fund it has moved
    with most over the last 252 sessions once the market is taken out. Refreshed every 21 sessions; a day uses the
    latest refresh at or before it. No outside labels, so it also works for companies that no longer exist."""
    r, m, f = np.log(c).diff().values, np.log(spy).diff().values, np.log(funds).diff().values
    beta, sec = np.full(r.shape, np.nan, dtype=np.float32), np.full(r.shape, -1, dtype=np.int8)
    for d in range(win, len(r), every):
        days = ~np.isnan(m[d - win + 1:d + 1])
        R, M, F = r[d - win + 1:d + 1][days], m[d - win + 1:d + 1][days], f[d - win + 1:d + 1][days]
        ok, use = (~np.isnan(R)).sum(0) >= win // 2, ~np.isnan(F).any(0)  # stocks with half a window; funds alive throughout
        R, M, F = np.nan_to_num(R), M - M.mean(), F[:, use]
        res = R - (R * M[:, None]).sum(0) / (M ** 2).sum() * M[:, None]
        res, fr = res - res.mean(0), F - (F * M[:, None]).sum(0) / (M ** 2).sum() * M[:, None]
        fr = fr - fr.mean(0)
        corr = res.T @ fr / (np.sqrt((res ** 2).sum(0))[:, None] * np.sqrt((fr ** 2).sum(0))[None, :] + 1e-12)
        hi = min(d + every, len(r))
        beta[d:hi] = np.where(ok, (R * M[:, None]).sum(0) / (M ** 2).sum(), np.nan)
        sec[d:hi] = np.where(ok, np.where(use)[0][corr.argmax(1)], -1)
    return beta, sec


def strip(y, beta, sec):
    """What is left of y [day x stock] once the market and the sectors are taken out: within each day, y minus its
    sector's average, then minus the part that goes with market beta (beta also measured against its sector)."""
    ok = ~np.isnan(y) & (sec >= 0) & ~np.isnan(beta)
    yt, bt = np.where(ok, y, 0.0).astype(float), np.where(ok, beta, 0.0).astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        for s in range(int(sec.max()) + 1):
            m = ok & (sec == s)
            n = m.sum(1, keepdims=True)
            yt -= np.where(m, np.nan_to_num((yt * m).sum(1, keepdims=True) / n), 0.0)
            bt -= np.where(m, np.nan_to_num((bt * m).sum(1, keepdims=True) / n), 0.0)
        slope = np.nan_to_num((yt * bt).sum(1, keepdims=True) / (bt * bt).sum(1, keepdims=True))
    return np.where(ok, yt - slope * bt, np.nan)


def info_busy(c, v):
    """Last month's return, kept for the stocks that traded unusually heavily and reversed for the quiet ones."""
    act = ((c * v).rolling(21).mean() / (c * v).rolling(252).mean()).rank(axis=1, pct=True)
    zr = z(c / c.shift(21) - 1)
    return (zr.where(act > 2 / 3, 0.0) - zr.where(act <= 1 / 3, 0.0)).where(c.notna())


def info_earnings(c):
    """(latest earnings surprise, about to report) [day x stock] from lab/earnings.csv, or (None, None) without it.
    A surprise counts from the announcement day if it came before the open, otherwise from the next session, for 63
    sessions. "About to report": last year's announcement of the same quarter plus 364 days falls in the next 7 days."""
    if not os.path.exists(EARN):
        return None, None
    e = pd.read_csv(EARN, parse_dates=["date"]).sort_values("date")
    e = e[e["ticker"].isin(c.columns) & (e["date"] <= c.index[-1])]
    col = {n: i for i, n in enumerate(c.columns)}
    sur, soon = np.full(c.shape, np.nan), np.zeros(c.shape)
    first = c.index.searchsorted(e["date"]) + (e["when"] != "before").astype(int).values
    for p, tk, s in zip(first, e["ticker"], pd.to_numeric(e["surprise_pct"], errors="coerce")):
        if p < len(c) and pd.notna(s):
            sur[p:p + 63, col[tk]] = np.clip(s, -100, 100)
    lo, hi = c.index.searchsorted(e["date"] + pd.Timedelta(days=357)), c.index.searchsorted(e["date"] + pd.Timedelta(days=364))
    for a, b, tk in zip(lo, hi, e["ticker"]):
        soon[a:b, col[tk]] = 1.0
    live = c.notna()
    return pd.DataFrame(sur, index=c.index, columns=c.columns).where(live), pd.DataFrame(soon, index=c.index, columns=c.columns).where(live)


def info_profit(c):
    """Gross profit over assets as first reported, usable from the session after the filing date; or None."""
    if not os.path.exists(FUND):
        return None
    f = pd.read_csv(FUND, parse_dates=["filed"]).dropna(subset=["gp_assets"]).sort_values("filed")
    f = f[f["ticker"].isin(c.columns)]
    col, g = {n: i for i, n in enumerate(c.columns)}, np.full(c.shape, np.nan)
    for p, tk, val in zip(c.index.searchsorted(f["filed"], side="right"), f["ticker"], f["gp_assets"]):
        g[p:p + 400, col[tk]] = val  # a report older than about 19 months is no longer used
    return pd.DataFrame(g, index=c.index, columns=c.columns).where(c.notna())


def learn(c, o, h, l, v, x, op, beta, sec, member, extra):
    """(names, today's score of every pattern [pattern x stock], daily rank IC [pattern x horizon x day], scores on
    the old days [pattern x old day x stock], those days). Patterns and outcomes both have the market and the sectors
    taken out (strip), and only companies in the index that day are ranked. `extra` holds the information entries;
    they are scored like patterns but are not part of the learner."""
    keep = member.values if member is not None else np.ones(c.shape, dtype=bool)
    ry = [pd.DataFrame(strip(np.where(keep, ahead(c, op, hz).values, np.nan), beta, sec)).rank(axis=1).values for hz in HORIZONS]
    grid = np.arange(CAL0, len(c), STEP)
    names, today, ic, zg = [], [], [], []
    for name, val in itertools.chain(patterns(c, o, h, l, v, x, OUTSIDE), extra.items()):
        zc = z(val)
        if name in extra:
            zc = zc.fillna(0.0).where(c.notna())  # a stock with no information is neutral, not missing
        zs = strip(np.where(keep, zc.values, np.nan), beta, sec)
        zs = zs / np.nanstd(zs, axis=1, keepdims=True)
        r = pd.DataFrame(zs).rank(axis=1).values
        names.append(name)
        today.append(zs[-1])
        zg.append(zs[grid].astype(np.float16))
        ic.append([rank_ic(r, y) for y in ry])
    return names, np.array(today), np.array(ic, dtype=np.float32), np.array(zg), grid


def believe(ic, hz, rng, core, last=None):
    """(the learner's weight on every pattern, the crowd test, each pattern's strength t) for one horizon.
    ic: [pattern x day]; only the first `core` rows (the price patterns) belong to the learner.
    The crowd test: Q = the sum of every pattern's t squared, beside what the same sum reaches when the blocks are
    re-signed at random (all patterns together). The learner speaks only if Q beats luck's 95th percentile. Its
    weights are then (S + g I)^-1 m: m the patterns' mean block ICs, S their covariance across blocks, g the average
    variance. Near-copies share one weight instead of voting many times."""
    if last is None:
        last = np.where(~np.isnan(ic).all(0))[0][-1]  # the latest day whose outcome is known
    size = max(hz, 5)
    nb = (last + 1 - WARM) // size
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        bm = np.nan_to_num(np.nanmean(ic[:, last + 1 - nb * size:last + 1].reshape(len(ic), nb, size), 2)).astype(float)
    norm = np.sqrt((bm ** 2).sum(1))
    norm[norm == 0] = np.inf
    t = bm.sum(1) / norm
    lucky = (rng.choice([-1.0, 1.0], size=(FLIPS, nb)) @ bm[:core].T / norm[:core]) ** 2
    q, luck, count = float((t[:core] ** 2).sum()), lucky.sum(1), (lucky > SOFT ** 2).sum(1)
    w = np.zeros(len(ic))
    if q > np.quantile(luck, 0.95):
        cov = np.cov(bm[:core])
        w[:core] = np.linalg.solve(cov + np.trace(cov) / core * np.eye(core), bm[:core].mean(1))
    crowd = {"q": q, "q_luck": float(np.quantile(luck, 0.95)), "standouts": int((np.abs(t[:core]) > SOFT).sum()),
             "luck_typical": float(np.median(count)), "luck_high": float(np.quantile(count, 0.95))}
    return w, crowd, t


def wild(ic1, last):
    """Has the trend's own bet been wilder than usual? Its next-session rank IC over the last 126 known sessions,
    against the median of that same measure over the last 504."""
    s = pd.Series(ic1[:last + 1]).rolling(126).std()
    return bool(s.iloc[-1] > s.iloc[-504:].median())


def votes(ic, names, hz, rng, last=None):
    """{entry: weight on every pattern} for one horizon, plus the crowd test and the strengths."""
    core, hi = len(names) - sum(n in ENTRY_H for n in names), HORIZONS.index(hz)
    w, crowd, t = believe(ic[:, hi, :], hz, rng, core, last)
    one = lambda n: (np.arange(len(names)) == names.index(n)).astype(float)
    known = (np.where(~np.isnan(ic[:, HORIZONS.index(1), :]).all(0))[0][-1] if last is None else last + hz - 1)
    out = {"learner": w, "trend": one(TREND), "calm": one(TREND) * (not wild(ic[names.index(TREND), HORIZONS.index(1), :], known))}
    out.update({n: one(n) for n in names[core:]})
    return {m: v for m, v in out.items() if hz in ENTRY_H[m]}, crowd, t


def _check():
    rng = np.random.default_rng(5)
    ic = rng.normal(0, 0.1, size=(60, 2400)).astype(np.float32)
    ic[:, -21:] = np.nan
    w, crowd, t = believe(ic, 21, np.random.default_rng(0), 60)
    assert not w.any() and crowd["q"] < crowd["q_luck"], "sixty patterns that know nothing must leave the learner silent"
    ic[7] += 0.03
    alone = believe(ic, 21, np.random.default_rng(0), 60)[0]
    assert alone[7] > 3 * np.abs(np.delete(alone, 7)).max(), "one real pattern among sixty must dominate"
    ic[8] = ic[7] + rng.normal(0, 0.01, size=2400).astype(np.float32)  # the same pattern again, as a near-copy
    w = believe(ic, 21, np.random.default_rng(0), 60)[0]
    assert 0 < max(w[7], w[8]) < 0.8 * alone[7] and w[7] + w[8] > 0.8 * alone[7], "a near-copy must share the weight, not double it"
    r, y = np.random.default_rng(1).normal(size=(2, 50, 200))
    assert abs(np.nanmean(rank_ic(pd.DataFrame(y + r).rank(axis=1).values, pd.DataFrame(y).rank(axis=1).values)) - 0.69) < 0.03
    g = np.random.default_rng(2)  # strip: a sector effect and a market-beta effect must vanish, a stock's own part must stay
    sec, beta, own = np.repeat(np.arange(5), 40)[None, :].repeat(3, 0), g.normal(1, 0.3, size=(3, 200)), g.normal(size=(3, 200))
    y = own + 5 * g.normal(size=(3, 5)).repeat(40, 1) + 3 * g.normal(size=(3, 1)) * beta
    out = strip(y, beta, sec.astype(np.int8))
    assert np.corrcoef(out.ravel(), own.ravel())[0, 1] > 0.97 and abs(out.mean()) < 1e-9
    assert abs(evidence(76, 124) - 5.3) < 0.05


def rank_names(w, zrow):
    """One score per stock from the voting patterns' scores. A stock is ranked only by the voters that can see it."""
    heard = (np.abs(w)[:, None] * ~np.isnan(zrow)).sum(0)
    return (w[:, None] * np.nan_to_num(zrow)).sum(0) / np.where(heard > 0, heard, np.nan)


def past(ic, zg, grid, c, op, names, member, uni, book):
    """Each entry's record on old days: every STEP-th session the call is rebuilt with only what was known that day
    and checked against what followed, from the next open (ahead). The market board ranks the companies that were in
    the index that day. {(entry, horizon): market and book [calls, right]; hit and n per tenth of the market ranking;
    log of (day, gap)}."""
    rec = {}
    for hz in HORIZONS:
        f = ahead(c, op, hz).values
        for gi, d in enumerate(grid):
            if d + hz >= len(c):
                break
            vt = votes(ic, names, hz, np.random.default_rng(0), last=d - hz)[0]  # ICs whose outcome was known at d
            for m, w in vt.items():
                nz = w != 0
                if not nz.any():
                    continue
                s = rank_names(w[nz], zg[nz, gi, :].astype(np.float32))
                r = rec.setdefault((m, hz), {"market": [0, 0], "book": [0, 0], "hit": np.zeros(10), "n": np.zeros(10), "log": {"market": [], "book": []}})
                for board, cols in (("market", np.where(member.values[d])[0] if member is not None else uni), ("book", book)):
                    if board == "book" and m not in BOOK:
                        continue
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
                         "gap": round(float(g.mean()), 5), "t": round(float(t), 2), "passed": int(right > binom.ppf(0.95, n, 0.5) and t >= 2),
                         "worst5": round(float(np.sort(g)[:max(1, n // 20)].mean()), 5)})
    return rows


def chance(right, n, since=(0, 0), cap=CAP_CALLS, soft=10):
    """A probability from a past record, pulled toward 50% (as if `soft` more hits and `soft` more misses), counted
    for at most `cap` outcomes, then moved by the real results since then: (right, n)."""
    m = min(n, cap)
    return ((right + soft) / (n + 2 * soft) * m + since[0]) / (m + since[1]) if m + since[1] else 0.5


def score_due(calls, scored, c, op):
    """Rows for calls whose horizon has now passed: what favoured did against avoided from the next open, the rank
    IC, and for each tenth of the ranking how many names beat the typical one."""
    done, rows = set(zip(scored["date"], scored["horizon"], scored["model"], scored["board"], scored["rules"])), []
    for r in calls[(calls["view"] == 1) & (calls["rules"] == RULES)].itertuples():
        k = c.index.get_indexer([pd.Timestamp(r.date)])[0]
        if k < 0 or k + r.horizon >= len(c) or (r.date, r.horizon, r.model, r.board, r.rules) in done:
            continue
        order = r.order.split()
        ret, n3 = (c.iloc[k + r.horizon] / op.iloc[k + 1].fillna(c.iloc[k]) - 1).reindex(order), len(order) // 3
        fav, avo, ok = ret.iloc[:n3].mean(), ret.iloc[-n3:].mean(), ret.notna().values
        tenth = np.minimum((np.arange(len(order))[::-1] * 10) // len(order), 9)[ok]
        beat = (ret.values[ok] > np.nanmedian(ret.values)).astype(float)
        rows.append({"date": r.date, "horizon": r.horizon, "model": r.model, "board": r.board, "rules": r.rules,
                     "due": f"{c.index[k + r.horizon].date()}", "favoured": round(fav, 5), "avoided": round(avo, 5),
                     "ic": round(pd.Series(-np.arange(len(order), dtype=float), index=order).corr(ret, method="spearman"), 4),
                     "right": int(fav > avo), "dec_hit": " ".join(f"{x:.0f}" for x in np.bincount(tenth, weights=beat, minlength=10)),
                     "dec_n": " ".join(f"{x:.0f}" for x in np.bincount(tenth, minlength=10))})
    return rows


def score_names(probs, pscored, calls, c, op):
    """Rows for the book's stocks whose horizon has passed: did the stock beat the typical stock of the market list?"""
    done, rows, med = set(zip(pscored["date"], pscored["horizon"], pscored["model"], pscored["name"])), [], {}
    for r in probs[~probs["name"].str.startswith("*") & (probs["rules"] == PRULES)].itertuples():
        k = c.index.get_indexer([pd.Timestamp(r.date)])[0]
        if k < 0 or k + r.horizon >= len(c) or (r.date, r.horizon, r.model, r.name) in done:
            continue
        ret, key = c.iloc[k + r.horizon] / op.iloc[k + 1].fillna(c.iloc[k]) - 1, (r.date, r.horizon)
        if key not in med:  # the typical stock: the median of the market list as ranked that day
            pool = calls[(calls["date"] == r.date) & (calls["horizon"] == r.horizon) & (calls["model"] == "trend") & (calls["board"] == "market") & (calls["rules"] == RULES)]["order"]
            med[key] = ret.reindex(pool.iloc[0].split()).median() if len(pool) else np.nan
        if pd.notna(ret.get(r.name, np.nan)) and pd.notna(med[key]):
            rows.append({"date": r.date, "horizon": r.horizon, "model": r.model, "name": r.name, "p": r.p,
                         "beat": int(ret[r.name] > med[key]), "due": f"{c.index[k + r.horizon].date()}"})
    return rows


def counted(scored, m, hz, board):
    """An entry's scored calls on one board that do not overlap (every hz-th)."""
    return scored[(scored["board"] == board) & (scored["horizon"] == hz) & (scored["model"] == m) & (scored["rules"] == RULES)].sort_values("date").iloc[::hz]


def report(calls, scored, beliefs, probs, pscored, old, stand):
    cur, pct = calls[calls["rules"] == RULES], lambda x: f"{x:+.2%}"
    day = cur["date"].max()
    pr = probs[(probs["date"] == day) & (probs["rules"] == PRULES)].set_index(["horizon", "model", "name"])
    odds = lambda hz, m, name: f" **{pr.loc[(hz, m, name), 'p']:.0%} that favoured beats avoided**, {1 - pr.loc[(hz, m, name), 'p']:.0%} that it does not." if (hz, m, name) in pr.index else ""
    rows = [(board, hz, m) for board in ("market", "book") for hz in HORIZONS for m in WHO if hz in ENTRY_H[m] and (board == "market" or m in BOOK)]
    ok = {(r.model, r.horizon, r.board): r.passed for r in old.itertuples()}
    out = ["# Daily calls: what the machine predicted and what came true\n",
           f"Updated after the close on {day}. Rules \"{RULES}\", written in daily_calls.py before the first call. It never trades.\n",
           "Each day after the close the machine ranks the S&P 500 stocks for three horizons. The top third is *favoured*, the bottom third "
           "*avoided*. A call is **right** if favoured did better than avoided, measured from the next morning's open (the first price anyone "
           "could trade at) and before trading costs. Moves that the whole market or a whole sector made are taken out first, so a call is "
           "about what is particular to each stock.\n",
           "The entries:\n",
           *[f"- **{WHO[m]}**: {WHAT[m]}" for m in WHO if any(r[2] == m for r in rows)],
           "\n## The fast answer: each entry's record on the past\n",
           "Every fifth session since 2019 each call was rebuilt with only what was known that day, among the companies that were in the index "
           "that day (dead ones included), then checked against what followed. Only calls that do not overlap are counted. \"A coin gets\" is the "
           "range pure luck lands in 19 times out of 20. An entry **passes** if it was right more often than a coin would be 19 times in 20 and "
           "its average gap is clearly above zero (t of 2 or more). Several entries are read here, so one narrow pass can be luck.\n",
           "| Board | Horizon | Who | Calls | Right | A coin gets | Favoured minus avoided | t | Its worst 5% of calls | Past test |", "|---|---|---|---|---|---|---|---|---|---|"]
    for board, hz, m in rows:
        r = old[(old["board"] == board) & (old["horizon"] == hz) & (old["model"] == m)]
        if r.empty:
            out.append(f"| {board} | {WORDS[hz]} | {SHORT[m]} | 0 | | | | | | never had a view |")
            continue
        r = r.iloc[0]
        often = r["right"] > binom.ppf(0.95, r["calls"], 0.5)
        verdict = "yardstick" if m == "trend" else "**passes**" if r["passed"] else "right more often than a coin, but its gain is not clearly above zero: fails" if often else "no better than a coin"
        out.append(f"| {board} | {WORDS[hz]} | {SHORT[m]} | {r['calls']:.0f} | {r['right']:.0f} ({r['right'] / r['calls']:.0%}) | {r['coin']} | {pct(r['gap'])} | {r['t']:+.1f} | {pct(r['worst5'])} | {verdict} |")
    out += ["\n## The tally on new days\n",
            "New days confirm or contradict the past. Only calls that do not overlap are counted. \"Evidence\" starts at 1 and 20 confirms; "
            "it can be read every day without fooling ourselves, because luck alone reaches 20 at most 1 time in 20.\n",
            "| Board | Horizon | Who | Calls counted | Right | A coin gets | Favoured minus avoided | All calls, overlapping | Says |", "|---|---|---|---|---|---|---|---|---|"]
    for board, hz, m in rows:
        a = scored[(scored["board"] == board) & (scored["horizon"] == hz) & (scored["model"] == m) & (scored["rules"] == RULES)].sort_values("date")
        k = a.iloc[::hz]
        n = len(k)
        if n == 0:
            out.append(f"| {board} | {WORDS[hz]} | {SHORT[m]} | 0 | | | | | nothing has come due yet |")
            continue
        lo, hi = binom.ppf([0.025, 0.975], n, 0.5).astype(int)
        hits = k["right"].cumsum().values
        ev = max(evidence(int(hits[i]), i + 1) for i in range(n))  # the strongest it has been on any day so far
        says = "yardstick" if m == "trend" else f"confirmed on new days (evidence {ev:.0f})" if ev >= NEED else f"not yet: evidence {ev:.1f} of the {NEED} needed"
        if m != "trend" and not ok.get((m, hz, board), 0):
            says += " (failed the past test)"
        out.append(f"| {board} | {WORDS[hz]} | {SHORT[m]} | {n} | {k['right'].sum()} | {lo} to {hi} | {pct((k['favoured'] - k['avoided']).mean())} | {a['right'].sum()} of {len(a)} | {says} |")

    out.append(f"\n## The calls made after the close on {day}\n")
    for hz in HORIZONS:
        out.append(f"### The {WORDS[hz]}\n")
        for r in stand[(stand["date"] == day) & (stand["horizon"] == hz) & (stand["rules"] == RULES)].itertuples():
            more = "More than luck: something real is in there." if r.standouts > r.luck_high else "About what luck gives."
            out.append(f"- Patterns that stand out one at a time: **{r.standouts}** of the learner's. Luck alone usually gives about {r.luck_typical:.0f} and rarely more than {r.luck_high:.0f}. {more}")
        for m in WHO:
            if hz not in ENTRY_H[m]:
                continue
            row = {bd: cur[(cur["date"] == day) & (cur["horizon"] == hz) & (cur["model"] == m) & (cur["board"] == bd)] for bd in ("market", "book")}
            if row["market"].empty or not row["market"]["view"].iloc[0]:
                why = {"learner": "The whole crowd of patterns is no better than luck here.", "calm": "The trend's bet has been wilder than usual, so it stands aside."}.get(m, "Nothing to go on.")
                out.append(f"- **{WHO[m]}: no view.** {why}" if not row["market"].empty else f"- {WHO[m]}: not logged (its data was missing).")
                continue
            o, ob = row["market"]["order"].iloc[0].split(), row["book"]["order"].iloc[0].split() if not row["book"].empty else []
            out.append(f"- **{WHO[m]}**, market: favours most {', '.join(o[:10])}; avoids most {', '.join(o[::-1][:10])}.{odds(hz, m, '*market')}")
            if ob:
                out.append(f"  In the book: favours {', '.join(ob[:len(ob) // 3])}; avoids {', '.join(ob[::-1][:len(ob) // 3])}.{odds(hz, m, '*book')}")
        b = beliefs[(beliefs["date"] == day) & (beliefs["horizon"] == hz) & (beliefs["rules"] == RULES)]
        if len(b):
            out.append("- What the learner leans on most:")
            out += [f"  - {r.pattern}: {r.direction} (strength {abs(r.strength):.1f})" for r in b.itertuples()]
        out.append("")

    stock = sorted(n for n in pr.index.get_level_values("name").unique() if not n.startswith("*"))
    if stock:
        cols = [(hz, m) for hz in HORIZONS for m in BOOK if (hz, m) in set(zip(pr.index.get_level_values(0), pr.index.get_level_values(1)))]
        out += ["## The chance that each of the bot's stocks beats the typical stock\n",
                "\"Beats the typical stock\" means it does better than the middle stock of the index over that horizon, so 50% is a coin. "
                "The columns are the horizon in sessions and the entry. These numbers stay close to 50% because that is what the record supports.\n",
                "| Stock | " + " | ".join(f"{hz}: {SHORT[m]}" for hz, m in cols) + " |", "|---" * (len(cols) + 1) + "|"]
        out += [f"| {n} | " + " | ".join(f"{pr.loc[(hz, m, n), 'p']:.1%}" if (hz, m, n) in pr.index else "no view" for hz, m in cols) + " |" for n in stock]
        out.append("")

    out += ["## Where the probabilities come from\n",
            "Each starts from the entry's record on old days (above), pulled toward 50% and counted for at most 100 calls; every real result since "
            "is added on top, so the probabilities learn from what comes true.\n",
            "| Entry | Horizon | Board | Its record on old days | Real results since | Chance today |", "|---|---|---|---|---|---|"]
    for (hz, m, name), r in pr[pr.index.get_level_values("name").str.startswith("*")].iterrows():
        g = counted(scored, m, hz, name[1:])
        was = f"right in {r['past_right'] / r['past_n']:.0%} of {r['past_n']:.0f} calls" if r["past_n"] else "none"
        out.append(f"| {SHORT[m]} | {WORDS[hz]} | {name[1:]} | {was} | {g['right'].sum()} of {len(g)} | {r['p']:.0%} |")

    out.append("\n## Were the probabilities honest?\n")
    board = probs[probs["name"].str.startswith("*") & (probs["rules"] == PRULES)].assign(board=lambda d: d["name"].str[1:])[["date", "horizon", "model", "board", "p"]]
    j = scored[scored["rules"] == RULES].merge(board, on=["date", "horizon", "model", "board"])
    ps = pscored[pscored["date"].isin(probs[probs["rules"] == PRULES]["date"])] if len(pscored) else pscored
    if j.empty and ps.empty:
        out.append("Nothing has come due yet. When it has: the Brier score (a coin that always says 50% scores 0.250, lower is better), and how often each band of stated chance came true.")
    for what, g, hit in (("Calls", j, "right"), ("Stocks", ps, "beat")):
        if len(g):
            out += [f"**{what}**: {len(g)} scored, Brier score {((g['p'] - g[hit]) ** 2).mean():.4f} against a coin's 0.2500.\n",
                    "| Stated chance | How many | Came true |", "|---|---|---|"]
            band = pd.cut(g["p"], [0, 0.48, 0.5, 0.52, 0.55, 1], labels=["under 48%", "48 to 50%", "50 to 52%", "52 to 55%", "over 55%"])
            out += [f"| {k} | {len(a)} | {a[hit].mean():.0%} |" for k, a in g.groupby(band, observed=True)]
            out.append("")

    out += ["\n## What came due most recently\n", "| Call made | Came due | Horizon | Board | Who | Favoured | Avoided | Result |", "|---|---|---|---|---|---|---|---|"]
    for r in scored[scored["rules"] == RULES].sort_values(["due", "horizon", "board", "model"], ascending=[False, True, False, True]).head(40).itertuples():
        out.append(f"| {r.date} | {r.due} | {WORDS[r.horizon]} | {r.board} | {SHORT[r.model]} | {pct(r.favoured)} | {pct(r.avoided)} | {'right' if r.right else 'wrong'} |")
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


def panel():
    """(bars {o,h,l,c,v: [day x stock]}, membership [day x stock] or None, the market list today, outside closes).
    With the dated membership files (wide_universe.py) every company that was in the index since 2016 is loaded,
    dead ones included; without them, today's members only (lab/universe.csv), which flatters the past."""
    extra = sorted(set(OUTSIDE) | set(SECTORS))
    if os.path.exists("wide_universe.py") and os.path.exists("lab/universe_members.csv"):
        import wide_universe
        raw, member = wide_universe.load(START)
        add = bars(sorted(set(UNIVERSE) - set(raw["c"].columns)) + extra)
        raw = {k: f.join(add[k][[n for n in UNIVERSE if n not in f.columns]], how="left") for k, f in raw.items()}
        member = member.reindex(index=raw["c"].index, columns=raw["c"].columns).ffill().fillna(False).astype(bool)
        return raw, member, list(member.columns[member.iloc[-1].values]), add["c"][extra].reindex(raw["c"].index)
    uni = pd.read_csv(UNI)["ticker"].tolist()
    b = bars(sorted(set(uni) | set(UNIVERSE)) + extra)
    stocks = sorted(set(uni) | set(UNIVERSE))
    return {k: f.reindex(columns=stocks) for k, f in b.items()}, None, uni, b["c"][extra]


def main():
    _check()
    read = lambda p, cols: pd.read_csv(p, keep_default_na=False, na_values=[""]) if os.path.exists(p) else pd.DataFrame(columns=cols)
    cat = lambda a, rows: pd.concat([a, pd.DataFrame(rows)], ignore_index=True) if rows else a
    calls = read(CALLS, ["date", "horizon", "model", "board", "rules", "view", "patterns", "bar", "order"]).fillna({"order": ""})
    scored = read(SCORED, ["date", "horizon", "model", "board", "rules", "due", "favoured", "avoided", "ic", "right", "dec_hit", "dec_n"])
    beliefs = read(BELIEFS, ["date", "horizon", "rules", "pattern", "direction", "strength", "bar"])
    probs = read(PROBS, ["date", "horizon", "model", "name", "p", "past_right", "past_n", "rules"]).astype({"name": str})
    pscored = read(PSCORED, ["date", "horizon", "model", "name", "p", "beat", "due"])
    old = read(PAST, ["as_of", "model", "horizon", "board", "calls", "right", "coin", "gap", "t", "passed", "worst5"])
    stand, snew = read(STAND, ["date", "horizon", "standouts", "luck_typical", "luck_high", "rules"]), []
    raw, member, uni, outside = panel()
    now = pd.Timestamp.now("America/New_York")
    if raw["c"].index[-1].date() == now.date() and now.hour < 16:  # the session is still open: its last bar is not a close
        raw, outside = {k: f.iloc[:-1] for k, f in raw.items()}, outside.iloc[:-1]
        member = member.iloc[:-1] if member is not None else None
    stocks, info = list(raw["c"].columns), "not rebuilt on this run"
    c = raw["c"].ffill(limit=21)  # a company's last price stands for 21 sessions, so a call made just before it left exits there
    day = f"{c.index[-1].date()}"

    due, pdue = score_due(calls, scored, c, raw["o"]), score_names(probs, pscored, calls, c, raw["o"])
    scored, pscored = cat(scored, due), cat(pscored, pdue)
    new, found, pnew = [], [], []
    logged = ((calls["date"] == day) & (calls["rules"] == RULES)).any()
    if not logged or not ((probs["date"] == day) & (probs["rules"] == PRULES)).any():
        x = np.log(outside[list(OUTSIDE)].ffill()).diff()
        beta, sec = groups(c, outside["SPY"].ffill(), outside[SECTORS].ffill())
        sur, soon = info_earnings(c)
        extra = {k: f for k, f in (("busy", info_busy(c, raw["v"])), ("surprise", sur), ("soon", soon), ("profit", info_profit(c))) if f is not None}
        at = {n: i for i, n in enumerate(stocks)}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            names, today, ic, zg, grid = learn(c, raw["o"] / raw["c"], raw["h"] / raw["c"], raw["l"] / raw["c"], raw["v"].replace(0, np.nan), x,
                                               raw["o"], beta, sec, member, extra)
            rec = past(ic, zg, grid, c, raw["o"], names, member, np.array([at[n] for n in uni]), np.array([at[n] for n in UNIVERSE]))
        info = [n for n in names if n in ENTRY_H]
        old = pd.DataFrame(past_test(rec, day))
        old.to_csv(PAST, index=False)  # rewritten each day: it is a summary of old days, not a log of new ones
        base = {(r.model, r.horizon, r.board): (r.right, r.calls) for r in old.itertuples()}
        live = c.iloc[-1].notna() & raw["c"].iloc[-5:].notna().any()  # a name with no bar in a week has stopped trading
        for hz in HORIZONS:
            vt, crowd, t = votes(ic, names, hz, np.random.default_rng(0))
            if not ((stand["date"] == day) & (stand["horizon"] == hz) & (stand["rules"] == RULES)).any():
                snew.append({"date": day, "horizon": hz, "standouts": crowd["standouts"], "luck_typical": round(crowd["luck_typical"]), "luck_high": round(crowd["luck_high"]), "rules": RULES})
            lean = vt["learner"]
            if not logged and lean.any():
                found += [{"date": day, "horizon": hz, "rules": RULES, "pattern": names[k], "direction": "higher is better" if lean[k] > 0 else "lower is better",
                           "strength": round(float(t[k]), 2), "bar": round(float(crowd["q_luck"]), 1)} for k in np.argsort(-np.abs(lean))[:8]]
            for m, w in vt.items():
                s, order = pd.Series(rank_names(w, today), index=stocks), {}
                for board, pool in (("market", uni), ("book", UNIVERSE)):
                    if board == "book" and m not in BOOK:
                        continue
                    o = list(s.reindex([n for n in pool if live.get(n, False)]).dropna().sort_values(ascending=False, kind="stable").index)
                    order[board] = o if len(o) >= 6 and (w != 0).any() else []
                    if not logged:
                        new.append({"date": day, "horizon": hz, "model": m, "board": board, "rules": RULES, "view": int(bool(order[board])),
                                    "patterns": int((w != 0).sum()), "bar": round(float(crowd["q_luck"]), 1), "order": " ".join(order[board])})
                r = rec.get((m, hz))
                if r is None or not order["market"]:
                    continue
                row = lambda name, p, right, n: {"date": day, "horizon": hz, "model": m, "name": name, "p": round(float(p), 4),
                                                 "past_right": round(float(right), 1), "past_n": round(float(n), 1), "rules": PRULES}
                for board in order:  # from the old-days calls that do not overlap: the same record as the past test
                    (right, n), g = base.get((m, hz, board), (0, 0)), counted(scored, m, hz, board)
                    if order[board]:
                        pnew.append(row("*" + board, chance(right, n, (g["right"].sum(), len(g))), right, n))
                g, pool = counted(scored, m, hz, "market"), s.reindex(order["market"]).values
                fh, fn = (np.array([[float(q) for q in str(e).split()] for e in g[col]]).sum(0) if len(g) else np.zeros(10) for col in ("dec_hit", "dec_n"))
                for name in order.get("book", []):
                    k = min(int((pool < s[name]).mean() * 10), 9)  # which tenth of the market ranking the stock sits in today
                    pnew.append(row(name, chance(r["hit"][k], r["n"][k], (fh[k], fn[k]), CAP_NAMES, 50), r["hit"][k], r["n"][k]))
    for path, rows in ((SCORED, due), (PSCORED, pdue), (CALLS, new), (BELIEFS, found), (PROBS, pnew), (STAND, snew)):
        if rows:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pd.DataFrame(rows).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    report(cat(calls, new), scored, cat(beliefs, found), cat(probs, pnew), pscored, old, cat(stand, snew))
    print(f"daily calls for {day}: {len(new)} calls logged, {len(pnew)} probabilities, {len(due)} calls and {len(pdue)} stocks scored; "
          f"{len(stocks)} companies, membership by date: {member is not None}, information entries: {info}")


if __name__ == "__main__":
    main()
