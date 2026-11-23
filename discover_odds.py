"""A machine that looks for its own patterns instead of being handed the textbook ones.
Run: python discover_odds.py --dev      its one test on the development years (lab rule 2, mlp_odds.py); prints what it found
     python discover_odds.py --log      forward record: today's forecast and the patterns it trusts today
     python discover_odds.py --freeze   rebuild lab/dev_raw.csv from Yahoo (done once, 2026-11-23)

The owner's ask (2026-11-23): "make it so that it looks for unique trends and makes its own correlations ... don't
just stick within the realms of what's known". The network in mlp_odds.py is handed 14 textbook inputs. This machine
is handed raw material and builds its own.

Everything below was fixed on 2026-11-23 before the machine was scored on any real outcome.
What it can see, all known at the close: each stock's open, high, low, close and volume; QQQ; and 15 outside series
(EXT: stocks at home and abroad, bonds, junk bonds, gold, oil, the dollar, three sectors, chips, the VIX, the 10-year
yield).
What it builds from that (candidates()): 345 patterns of its own, none preferred: trends over any window, with
or without the latest days, split into overnight and daytime moves; daily range, volume against its own normal, where
it closes in the day's range; the shape of its daily moves; distance from highs, lows and averages; volume against
price; how closely each stock moves with each outside series, how that is changing, and what is left of its return
once that series is taken out; how it moves with, leads and follows the other names. Then 600 random pairs of those
multiplied together (seeded), so it can find a pattern that only works in combination. 945 candidates in all.
How it chooses, every 21 sessions, from outcomes known by that day only (pick()): a candidate needs 250 days of
record; it must have pointed the same way in the first and the second half of what the machine has seen; candidates
are ranked by their weaker half; the best 10 are taken, skipping any that is a near-copy (|correlation| >= 0.7) of
one already taken. Each of the 10 gets one equal vote, in the direction it earned. The forecast is the sum of votes.
Learning from its mistakes: the choice is redone every 21 sessions, so a pattern that stops working is dropped.
Why a search over 945 candidates is still one honest test: the choosing happens inside the walk-forward. Only
forecasts for days the machine had not seen are scored, so its lucky finds have to keep working to count.
The test: lab rule 2 exactly as written in mlp_odds.py (growth odds against the live book >= 0.90, above 0.5 in
each half and with any year left out, rank IC above the trend score's with any stock or year left out), end-2014
list, development years, as the lab's fifth experiment (BUDGET raised from 4 to 5 for it; MATH.md change log). One
run. K, the 250, the 0.7, the windows and the candidate list are not tuned afterwards.
After the test, whatever the verdict: it logs a dated forecast after every close (signals/discover_*.csv). If kept,
it is a challenger judged from 2026-11-23 on by the network's official bar (252 sessions at least). If reverted, the
log is a shadow record only. It never touches the trading bot.
Prior, written before the run: under 10% that it is kept. With ten stocks and 71 months, most of what any search
finds is noise; the reviewers gave 5 to 10% for the whole lab (research_notes/mlp loop/round 2.md).
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

import mlp_odds
from mlp_odds import DEV_END, DEV_PX, EVERY, FIRST, FWD
from model import BENCH, names_of
from universe_study import TECH10_2014

RAW, K, MIN_DAYS, MIN_NAMES, TWIN, PAIRS = "lab/dev_raw.csv", 10, 250, 6, 0.7, 600
W = (5, 10, 21, 42, 63, 126, 252)
EXT = {"SPY": "US stocks", "IWM": "small US stocks", "EEM": "emerging-market stocks", "TLT": "long Treasury bonds",
       "IEF": "7-10 year Treasuries", "HYG": "junk bonds", "GLD": "gold", "USO": "oil", "UUP": "the dollar",
       "XLK": "the tech sector", "XLF": "banks", "XLE": "energy stocks", "SMH": "chip stocks", "^VIX": "the VIX",
       "^TNX": "the 10-year yield"}
VARIANT = {"name": "v4 the machine picks its own patterns", "judged_from": "2026-11-23", "inputs": []}
FOUND, HISTORY = [], []  # rows for the forward log; (day, [(pattern, direction)]) at every refit of the last run


def raw(px, frozen):
    """Open, high and low as ratios to the same day's close, volume, and the outside series, on px's days."""
    names = names_of(px)
    if frozen:
        d = pd.read_csv(RAW, index_col=0, parse_dates=True)
    else:
        import yfinance as yf
        y = yf.download(names + list(EXT), start="2014-01-01", auto_adjust=True, progress=False, threads=False)
        cl = y["Close"]
        d = pd.concat({"o": y["Open"] / cl, "h": y["High"] / cl, "l": y["Low"] / cl, "v": y["Volume"], "x": cl}, axis=1)
        d.columns = [f"{a}|{b}" for a, b in d.columns]
    d = d.reindex(px.index)
    part = lambda k, cols: d.reindex(columns=[f"{k}|{c}" for c in cols]).set_axis(list(cols), axis=1)
    return part("o", names), part("h", names), part("l", names), part("v", names).replace(0, np.nan), part("x", EXT).ffill()


def freeze():
    px = pd.read_csv(DEV_PX, index_col=0, parse_dates=True)
    d = pd.concat(dict(zip("ohlvx", raw(px, False))), axis=1)
    d.columns = [f"{a}|{b}" for a, b in d.columns]
    d.round(6).to_csv(RAW)
    print(d.shape, d.index[0].date(), d.index[-1].date(), "missing values:", int(d.isna().sum().sum()))


def z(v):
    v = v.replace([np.inf, -np.inf], np.nan)
    return v.sub(v.mean(axis=1), axis=0).div(v.std(axis=1), axis=0).clip(-3, 3)


def candidates(px, frozen=False):
    """(plain names, [candidate x day x stock] z-scores across the names). Every value is known at that day's close."""
    names = names_of(px)
    o, h, l, v, ext = raw(px, frozen)
    c = px[names].ffill()
    lr = np.log(c).diff()
    vol = lr.rolling(60).std()
    dv = np.log(v) - np.log(v).rolling(60).mean()
    pos = ((1 - l) / (h - l)).replace([np.inf, -np.inf], np.nan)
    x = np.log(ext.join(px[BENCH].ffill())).diff()
    skip = lambda b: f", leaving out the latest {b}" if b else ""
    f = {}
    for what, p in (("return", lr), ("overnight return", np.log(o) + lr), ("daytime return", -np.log(o))):
        for a in W:
            for b in (0, 5, 21):
                if b < a:
                    f[f"{what} over {a} sessions{skip(b)}"] = p.rolling(a - b).sum().shift(b) / (vol * np.sqrt(a - b))
    for what, p in (("daily range", np.log(h / l)), ("volume against its own normal", dv), ("where it closes in the day's range", pos)):
        for a in W:
            f[f"{what}, average of {a} sessions"] = p.rolling(a).mean()
        for a, b in ((5, 21), (5, 63), (21, 126), (21, 252), (63, 252)):
            f[f"{what}, last {a} sessions against the last {b}"] = p.rolling(a).mean() - p.rolling(b).mean()
    f["choppiness over 60 sessions"] = vol
    for a in (21, 63, 126, 252):
        r = lr.rolling(a)
        f[f"lopsidedness of its daily moves, {a} sessions"] = r.skew()
        f[f"biggest one-day gain in {a} sessions"] = r.max() / vol
        f[f"biggest one-day loss in {a} sessions"] = r.min() / vol
        f[f"share of up days, {a} sessions"] = (lr > 0).astype(float).where(lr.notna()).rolling(a).mean()
        f[f"size of its down days against its up days, {a} sessions"] = (lr.clip(upper=0) ** 2).rolling(a).mean() / (lr.clip(lower=0) ** 2).rolling(a).mean()
        f[f"one day's move repeating the next day, {a} sessions"] = r.corr(lr.shift(1))
        f[f"distance below its {a}-session high"] = c / c.rolling(a).max() - 1
        f[f"distance above its {a}-session low"] = c / c.rolling(a).min() - 1
        f[f"distance from its {a}-session average"] = c / c.rolling(a).mean() - 1
        if a < 252:
            f[f"choppiness, {a} sessions against the last 252"] = r.std() / lr.rolling(252).std()
    for a in (21, 63, 126):
        f[f"volume rising on its up days, {a} sessions"] = lr.rolling(a).corr(dv)
        f[f"return on its heavy-volume days, {a} sessions"] = (lr * dv).rolling(a).sum() / (vol * np.sqrt(a))
    for k, what in {**EXT, BENCH: "the Nasdaq 100"}.items():
        beta = lr.rolling(126).cov(x[k]).div(x[k].rolling(126).var(), axis=0).shift(1)
        res = lr - beta.mul(x[k], axis=0)
        for a in (63, 126, 252):
            f[f"how closely it moves with {what}, {a} sessions"] = lr.rolling(a).corr(x[k])
        f[f"moving more closely with {what} lately (63 sessions against 252)"] = lr.rolling(63).corr(x[k]) - lr.rolling(252).corr(x[k])
        f[f"sensitivity to {what}"] = beta
        for a, b in ((5, 0), (21, 0), (63, 0), (126, 21), (252, 21)):
            f[f"return beyond what {what} explains, {a} sessions{skip(b)}"] = res.rolling(a - b).sum().shift(b) / (res.rolling(60).std() * np.sqrt(a - b))
        for a in (21, 63, 126):
            f[f"sensitivity to {what} times its move over {a} sessions"] = beta.mul(x[k].rolling(a).sum(), axis=0)
    peers = pd.DataFrame({n: lr.drop(columns=n).mean(axis=1) for n in names})
    for a in (63, 252):
        f[f"how closely it moves with the other names, {a} sessions"] = lr.rolling(a).corr(peers)
    f["following the other names a day late, 126 sessions"] = lr.rolling(126).corr(peers.shift(1))
    f["the other names following it a day late, 126 sessions"] = peers.rolling(126).corr(lr.shift(1))

    f = {k: z(v[names]) for k, v in f.items()}
    base, rng = list(f), np.random.default_rng(0)
    pairs = set()
    while len(pairs) < PAIRS:
        i, j = sorted(rng.choice(len(base), 2, replace=False))
        pairs.add((int(i), int(j)))
    for i, j in sorted(pairs):
        f[f"[{base[i]}] together with [{base[j]}]"] = z(f[base[i]] * f[base[j]])
    return list(f), np.stack([v.values.astype(np.float32) for v in f.values()])


def daily_ic(Z, y):
    """[candidate x day] rank correlation, across the names, of a pattern with the outcome that followed."""
    out = np.full(Z.shape[:2], np.nan, dtype=np.float32)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for k in range(len(Z)):
            ok = ~np.isnan(Z[k]) & ~np.isnan(y)
            a, b = (pd.DataFrame(np.where(ok, m, np.nan)).rank(axis=1).values for m in (Z[k], y))
            a, b = a - np.nanmean(a, 1, keepdims=True), b - np.nanmean(b, 1, keepdims=True)
            ic = np.nansum(a * b, 1) / np.sqrt(np.nansum(a * a, 1) * np.nansum(b * b, 1))
            out[k] = np.where(ok.sum(1) >= MIN_NAMES, ic, np.nan)
    return out


def pick(ic, Z, last):
    """[(candidate, direction)]: the K patterns to trust, judged on days up to `last`, whose outcomes are known."""
    v = ic[:, :last + 1]
    ok = ~np.isnan(v)
    n = ok.sum(1)
    first = ok & (ok.cumsum(1) <= (n // 2)[:, None])
    flat = lambda k: np.nan_to_num(Z[k, :last + 1:5]).ravel()
    chosen = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        s1, s2 = (np.nanmean(np.where(m, v, np.nan), 1) / np.nanstd(np.where(m, v, np.nan), 1) for m in (first, ok & ~first))
        score = np.where((n >= MIN_DAYS) & (s1 * s2 > 0), np.minimum(np.abs(s1), np.abs(s2)), 0.0)
        for k in np.argsort(-score):
            if score[k] <= 0 or len(chosen) == K:
                break
            if all(abs(np.corrcoef(flat(k), flat(j))[0, 1]) < TWIN for j, _ in chosen):
                chosen.append((int(k), float(np.sign(s1[k]))))
    return chosen


def walk_forward(px, upto=None, last_only=False):
    """Same contract as mlp_odds.walk_forward: (forecast score, realised target), both [date x name]. With `upto`
    (the lab) it reads the frozen raw file, which ends at DEV_END; otherwise it downloads."""
    names = names_of(px)
    labels, Z = candidates(px, frozen=upto is not None)
    VARIANT["inputs"] = labels
    yw = mlp_odds.target(px)
    ic, have = daily_ic(Z, yw.values), px[names].ffill().notna().values
    pred, chosen = np.full(yw.shape, np.nan), []
    HISTORY.clear()
    for i in list(range(FIRST, len(px), EVERY))[-1 if last_only else 0:]:
        if upto is not None and px.index[i] > pd.Timestamp(upto):
            break
        chosen = pick(ic, Z, i - FWD)  # day i - FWD's 21-session outcome is known at close i
        if not chosen:
            continue
        blk = slice(i, i + EVERY)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            p = np.nanmean([s * Z[k, blk] for k, s in chosen], axis=0)
        pred[blk] = np.where(np.isnan(p) & have[blk], 0.0, p)  # a stock none of the ten can see today is neutral
        HISTORY.append((px.index[i].date(), [(labels[k], "higher is better" if s > 0 else "lower is better") for k, s in chosen]))
    if last_only and HISTORY:
        uni = "end-2014" if set(names) == set(TECH10_2014) else "shipped"
        FOUND.extend({"date": px.index[-1].date(), "list": uni, "pattern": a, "direction": b} for a, b in HISTORY[-1][1])
    return pd.DataFrame(pred, index=px.index, columns=names), yw


def _check():
    rng = np.random.default_rng(3)
    Z = rng.normal(size=(40, 1500, 10)).astype(np.float32)
    y = 0.25 * Z[7] - 0.25 * Z[19] + rng.normal(size=(1500, 10))
    ch = dict(pick(daily_ic(Z, y), Z, 1000))  # two planted patterns among 40: it must find both, each with its sign
    assert ch.get(7) == 1 and ch.get(19) == -1, ch
    vote = lambda c: np.mean([s * Z[k, 1001:] for k, s in c.items()], axis=0)[None]
    assert np.nanmean(daily_ic(vote(ch), y[1001:])) > 0.1, "planted patterns should keep working on days it had not seen"
    noise = rng.normal(size=(1500, 10))
    assert abs(np.nanmean(daily_ic(vote(dict(pick(daily_ic(Z, noise), Z, 1000))), noise[1001:]))) < 0.05, "pure noise must not look like skill"
    px = pd.read_csv(DEV_PX, index_col=0, parse_dates=True)
    (la, a), (lb, b) = candidates(px.iloc[:-250], True), candidates(px, True)
    assert la == lb and np.allclose(a, b[:, :a.shape[1]], equal_nan=True, atol=1e-4), "lookahead: a pattern changed when later days were added"
    return lb, b


def _as_lab():
    """mlp_odds's lab, official test and forward log, run on this machine instead of the network."""
    mlp_odds.VARIANT, mlp_odds.walk_forward = VARIANT, walk_forward
    mlp_odds.FORECASTS, mlp_odds.FORWARD = "signals/discover_forecasts.csv", "signals/discover_forward.csv"


if __name__ == "__main__":
    if "--freeze" in sys.argv:
        freeze()
    elif "--log" in sys.argv:
        _as_lab()
        mlp_odds.log_forward()
        if FOUND:  # the patterns behind today's forecast: what it believes now
            path = "signals/discover_found.csv"
            pd.DataFrame(FOUND).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    elif "--dev" in sys.argv:
        labels, _ = _check()
        print(f"{len(labels)} candidate patterns; checks passed (finds planted patterns, noise is not skill, no lookahead)")
        _as_lab()
        mlp_odds.dev()
        if HISTORY:
            sets = [{a for a, _ in s} for _, s in HISTORY]
            kept = np.mean([len(a & b) / max(len(b), 1) for a, b in zip(sets, sets[1:])])
            count = pd.Series([a for s in sets for a in s]).value_counts()
            print(f"\n{len(HISTORY)} refits. From one refit to the next it kept {kept:.0%} of its patterns. {len(count)} different patterns were used at some point.")
            print("Used most often:")
            for a, n in count.head(8).items():
                print(f"  {n} of {len(HISTORY)} refits: {a}")
            print(f"Trusted at the last refit ({HISTORY[-1][0]}):")
            for a, b in HISTORY[-1][1]:
                print(f"  {a} ({b})")
