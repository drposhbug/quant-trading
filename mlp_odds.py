"""A small neural network that keeps learning which stocks to hold more of, the lab that tests changes to it, and
the forward record that scores it on days that had not happened when it made its forecast.
Run: python mlp_odds.py          official test (learn.py runs it monthly); writes reports/mlp_odds.md
     python mlp_odds.py --dev    lab: score the current VARIANT on the development years, print why it went wrong,
                                 log it to reports/mlp_lab_log.csv and print VERDICT: keep / revert / closed
     python mlp_odds.py --log --refresh   forward record: add today's forecast, score the days now 21 sessions old

The owner's asks (2026-11-23): "an MLP so it learns from its mistakes", "a Claude loop that fixes the code itself",
then "a scheduled Claude task for an ML that is actively learning".
Model: one hidden layer of tanh units, squared error + L2, Adam, early stopping on its most recent training days
(whole days, with a 21-session gap so no label overlaps); 3 seeds averaged. Plain numpy, no new dependency.
Inputs per stock per day, all known at that close, each a z-score across the names that day; market inputs are
standardised on past data only. Target: the stock's return over the next 21 sessions against the other names.
Learning from its mistakes: refitted every 21 sessions on every day whose outcome is by then known, so each refit
includes its latest errors. First fit after 500 sessions. Trained separately on each list, so the end-2014 test
contains no hindsight. Use: the live tilt mechanics (x2 top third, x0.5 bottom third) with the forecast as the score.

The lab, rule 2 (fixed 2026-11-23 after session 1 and a second review by Astra 6.2 and Grok, before any further
experiment; research_notes/mlp loop/round 2.md). Rule 1 and its three experiments stay in the log.
- Prices are frozen in lab/dev_prices.csv, which ends at DEV_END (2021-12-31). --dev reads nothing else: it needs
  no download and cannot see a later price. Every variant is scored on the same months and the same names.
- The experiments are the four written in lab/queue.md before any of them ran, in that order, one change each, in
  this file only, each with a new VARIANT name and VARIANT["judged_from"] set to the day it is run. One try per
  idea. --dev counts them and refuses a fifth (BUDGET): more tries on the same 71 months would only find noise.
  Only the owner can raise the budget, with a row in MATH.md's change log.
- The yardstick is the live book, not the previous network. A change is kept only if ALL hold on the end-2014 list:
  growth odds against the live book >= 0.90, above 0.5 in each half, and above 0.5 when any one year is left out
  (the official bar, applied to the development years); and its rank IC is above the live trend score's, also when
  any one stock or any one year is left out. Otherwise the code is reverted. The log keeps both outcomes.
- A kept variant becomes the challenger and is judged only on days after its own date. Nothing here touches the
  trading bot. Inputs must be built from the daily closes lists() returns, so the official test runs on GitHub.
Why rule 1 was replaced: it compared a change with the last kept network (rank IC +0.01, a third of a standard
error), so a copy of the trend score could pass and each keep raised the bar on noise; its leave-one-out test
compared a reduced sample with a full one; and a December 2021 forecast was scored with January 2022 prices.
Official bar: on the end-2014 list from VARIANT["judged_from"] on, with at least 252 sessions to judge (MIN_FWD),
P(arm grows faster than the live book) >= 0.90 and > 0.5 in each half of that window, and >= 0.5 on the shipped
list over the same window. Whole-window numbers are reported only.
The forward record (signals/mlp_forecasts.csv, signals/mlp_forward.csv) is where new evidence comes from: one dated
forecast per stock per day, scored 21 sessions later, never rewritten. Both reviewers put the honest wait at years,
not months: with a monthly rank IC noise near 0.34, a true IC of 0.05 needs about six years to show.
"""
import csv
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

import growth_odds
from backtest import prices
from growth_odds import LIVE, odds
from mini_trend_odds import tilt
from model import BENCH, P, backtest_returns, names_of, scores, target_weights
from monitor import tilted
from universe_study import TECH10_2014, load_extra

FIRST, EVERY, FWD, SEEDS = 500, 21, 21, (0, 1, 2)
DEV_END, LOG = "2021-12-31", "reports/mlp_lab_log.csv"
DEV_PX, GRID_START = "lab/dev_prices.csv", "2016-01-28"  # lists()[0] as downloaded 2026-11-23, cut at DEV_END; the first forecast day
RULE, BUDGET, BAR, MIN_FWD = "2", 4, 0.90, 252
FORECASTS, FORWARD = "signals/mlp_forecasts.csv", "signals/mlp_forward.csv"
NAME = "mlp: a neural network refitted every month"
VARIANT = {"name": "v1 baseline", "judged_from": "2022-01-01", "target": "relative", "hidden": 16, "l2": 1e-3,
           "inputs": ["r5", "r21", "r63", "r126", "r252", "rev5", "ma200", "high", "vol", "volratio", "beta", "q21", "q200", "qvol"]}


def _loss_grad(p, X, y, l2):
    W1, b1, w2, b2 = p
    H = np.tanh(X @ W1 + b1)
    e = (H @ w2 + b2 - y) / len(y)
    dH = np.outer(e, w2) * (1 - H * H)
    loss = 0.5 * len(y) * (e @ e) + 0.5 * l2 * ((W1 * W1).sum() + w2 @ w2)
    return loss, [X.T @ dH + l2 * W1, dH.sum(axis=0), H.T @ e + l2 * w2, np.array(e.sum())]


def predict(p, X):
    return np.tanh(X @ p[0] + p[1]) @ p[2] + p[3]


def fit(X, y, day, seed, hidden=16, l2=1e-3, lr=1e-3, epochs=60, batch=1024, patience=5):
    """day: session number of each row. The most recent 20% of days decide when to stop; training rows whose
    21-session outcome reaches into those days are left out."""
    rng, u = np.random.default_rng(seed), np.unique(day)
    cut = u[int(len(u) * 0.8)]
    Xv, yv, X, y = X[day > cut], y[day > cut], X[day <= cut - FWD], y[day <= cut - FWD]
    p = [rng.normal(0, 1 / np.sqrt(X.shape[1]), (X.shape[1], hidden)), np.zeros(hidden), rng.normal(0, 1 / np.sqrt(hidden), hidden), np.array(0.0)]
    m, v, t = [np.zeros_like(a) for a in p], [np.zeros_like(a) for a in p], 0
    best, best_p, bad = np.inf, [a.copy() for a in p], 0
    for _ in range(epochs):
        order = rng.permutation(len(y))
        for k in range(0, len(y), batch):
            idx = order[k:k + batch]
            g = _loss_grad(p, X[idx], y[idx], l2)[1]
            t += 1
            for j in range(4):  # Adam
                m[j] = 0.9 * m[j] + 0.1 * g[j]
                v[j] = 0.999 * v[j] + 0.001 * g[j] ** 2
                p[j] = p[j] - lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
        val = np.mean((predict(p, Xv) - yv) ** 2)
        if val < best - 1e-6:
            best, best_p, bad = val, [a.copy() for a in p], 0
        else:
            bad += 1
            if bad >= patience:
                break
    return best_p


def _check():
    rng = np.random.default_rng(1)
    X, y = rng.normal(size=(40, 5)), rng.normal(size=40)
    p = [rng.normal(size=(5, 3)), rng.normal(size=3), rng.normal(size=3), np.array(0.3)]
    g = _loss_grad(p, X, y, 0.01)[1]
    for j, ix in ((0, (2, 1)), (1, (0,)), (2, (2,)), (3, ())):  # analytic gradient = finite difference
        q = [a.copy() for a in p]
        q[j][ix] += 1e-6
        assert abs((_loss_grad(q, X, y, 0.01)[0] - _loss_grad(p, X, y, 0.01)[0]) / 1e-6 - g[j][ix]) < 1e-4, j
    X = rng.normal(size=(6000, 6))
    sig = np.tanh(2 * X[:, 0] * X[:, 1])  # a pattern no straight line can find
    y, day = sig + rng.normal(size=6000), np.arange(6000) // 10
    out = predict(fit(X[:5000], y[:5000], day[:5000], 0, lr=3e-3), X[5000:])
    assert np.corrcoef(out, sig[5000:])[0, 1] > 0.6, "the network should learn a planted non-linear pattern"


def features(px):
    """Every available input [(date, name) x input]; the network uses VARIANT['inputs']. Add new inputs here."""
    names = names_of(px)
    c, bench = px[names].ffill(), px[BENCH].ffill()
    lr, q = np.log(c).diff(), np.log(bench).diff()
    vol = lr.rolling(60).std()
    f = {f"r{h}": lr.rolling(h).sum() / (vol * np.sqrt(h)) for h in (5, 21, 63, 126, 252)}
    beta = pd.DataFrame({n: lr[n].rolling(60).cov(q) / q.rolling(60).var() for n in names})
    f["rev5"] = (lr - beta.shift(1).mul(q, axis=0)).rolling(5).sum() / (vol * np.sqrt(5))
    f["ma200"], f["high"] = c / c.rolling(200).mean() - 1, c / c.rolling(252, min_periods=60).max() - 1
    f["vol"], f["volratio"], f["beta"] = vol, lr.rolling(5).std() / vol, beta
    X = pd.concat({k: v.sub(v.mean(axis=1), axis=0).div(v.std(axis=1), axis=0).clip(-3, 3).stack(future_stack=True)
                   for k, v in f.items()}, axis=1)
    mkt = pd.DataFrame({"q21": q.rolling(21).sum(), "q200": bench / bench.rolling(200).mean() - 1, "qvol": q.rolling(20).std()})
    mkt = ((mkt - mkt.expanding(250).mean()) / mkt.expanding(250).std()).clip(-3, 3)  # past data only
    for k in mkt:
        X[k] = mkt[k].reindex(X.index.get_level_values(0)).values
    return X[VARIANT["inputs"]]


def target(px):
    c = px[names_of(px)].ffill()
    fwd = c.shift(-FWD) / c - 1
    return fwd.sub(fwd.mean(axis=1), axis=0)


def walk_forward(px, upto=None, last_only=False):
    """(forecast score, realised target), both [date x name]. Each block of EVERY sessions uses a network fitted on
    outcomes known by then. With `upto`, no forecast is made after that date. `last_only` fits the latest block alone:
    the same forecast for today as the full run gives, in seconds."""
    X, yw = features(px), target(px)
    y = yw.stack(future_stack=True).reindex(X.index)
    d0, dates = X.index.get_level_values(0), px.index
    day = dates.get_indexer(d0)
    good, known = X.notna().all(axis=1).values, y.notna().values
    pred = pd.Series(np.nan, index=X.index)
    for i in list(range(FIRST, len(dates), EVERY))[-1 if last_only else 0:]:
        if upto is not None and dates[i] > pd.Timestamp(upto):
            break
        tr = good & known & (day <= i - FWD)  # the last training day's 21-session outcome is known at close i
        te = good & (day >= i) & (day < i + EVERY) & ((d0 <= pd.Timestamp(upto)) if upto is not None else True)
        if tr.sum() < 500 or not te.any():
            continue
        Xt, yt = X.values[tr], y.values[tr] / y.values[tr].std()
        pred[te] = np.mean([predict(fit(Xt, yt, day[tr], s, hidden=VARIANT["hidden"], l2=VARIANT["l2"]), X.values[te]) for s in SEEDS], axis=0)
    return pred.unstack().reindex(index=px.index, columns=names_of(px)), yw


def lists():
    px = prices()
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    return px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]], px


def p_grow(a, b):
    growth_odds.rng = np.random.default_rng(7)  # same draws every call, so two variants are compared like for like
    return odds(a, b)


def rank_ic(score, y, a, b):
    return score.loc[a:b:FWD].corrwith(y.loc[a:b:FWD], axis=1, method="spearman").dropna()


def dev():
    """Lab: development years only, from the frozen price file. Prints the scores, where the network went wrong, and
    the verdict of rule 2 (docstring). The yardstick is the live book and its trend score, on the same days and names."""
    today = f"{dt.date.today()}"
    old = list(csv.DictReader(open(LOG))) if os.path.exists(LOG) else []
    used = [r for r in old if r.get("rule") == RULE]
    kept = [r for r in used if r["status"] == "kept"]
    if sum(r["status"] != "reference" for r in used) >= BUDGET:
        return print(f"VERDICT: closed (all {BUDGET} experiments on the development years are spent; only new days add evidence now)")
    if VARIANT["name"] in {r["variant"] for r in used}:
        return print("VERDICT: refused (this variant name is already in the log: one try per idea, a new name for a new idea)")
    if used and VARIANT["judged_from"] != today:
        return print(f"VERDICT: refused (set VARIANT['judged_from'] to today, {today}: a kept change is judged only on later days)")

    px14 = pd.read_csv(DEV_PX, index_col=0, parse_dates=True)  # frozen and cut at DEV_END: no download, no later price
    score, y = walk_forward(px14, upto=DEV_END)
    grid = px14.loc[GRID_START:].index[::FWD]
    grid = grid[y.loc[grid].notna().all(axis=1).values]  # the same months for every variant, outcomes inside the file
    s, t, yy = score.loc[grid], scores(px14, {**P, "w_trend": 1.0}).loc[grid], y.loc[grid]  # t: what the live tilt ranks by

    def ic(sc, drop=()):
        return sc.drop(columns=list(drop)).corrwith(yy.drop(columns=list(drop)), axis=1, method="spearman")

    ic_s, gain = ic(s), ic(s) - ic(t)
    full = not s.isna().any().any()
    # partial rank IC: the part of each day's forecast that the trend score does not explain, against the outcome
    part = ic(pd.DataFrame({d: s.loc[d] - np.polyval(np.polyfit(t.loc[d], s.loc[d], 1), t.loc[d]) for d in grid}).T).mean() if full else np.nan
    years = sorted(set(grid.year))
    gain_name = {n: (ic(s, [n]) - ic(t, [n])).mean() for n in s.columns}
    gain_year = {yr: gain[gain.index.year != yr].mean() for yr in years}
    arm, cur = (backtest_returns(px14, w).loc[GRID_START:] for w in (tilt(px14, score), tilted(px14)))
    pg = lambda x, z: p_grow(x, z)["P(arm grows faster)"]
    o, mid = p_grow(arm, cur), arm.index[len(arm) // 2]
    p, p1, p2 = o["P(arm grows faster)"], pg(arm[:mid], cur[:mid]), pg(arm[mid:], cur[mid:])
    p_year = {yr: pg(arm[arm.index.year != yr], cur[cur.index.year != yr]) for yr in years}
    worst = min(p_year, key=p_year.get)
    fails = [txt for txt, bad in (
        ("a forecast is missing in some months", not full),
        (f"growth odds against the live book are {p:.2f}, below {BAR:.2f}", not p >= BAR),
        (f"growth odds are not above 0.5 in each half ({p1:.2f}, {p2:.2f})", not min(p1, p2) > 0.5),
        (f"growth odds fall to {p_year[worst]:.2f} without {worst}", not p_year[worst] > 0.5),
        (f"its ranking is no better than the live trend score's (rank IC {ic_s.mean():+.3f} vs {ic(t).mean():+.3f})", not gain.mean() > 0),
        ("the ranking gain disappears without one stock or one year", not min(*gain_name.values(), *gain_year.values()) > 0),
        ("growth odds are not above the kept variant's", bool(kept) and not p > float(kept[-1]["p_vs_live"]))) if bad]
    status = "reference" if not used else "reverted" if fails else "kept"
    row = {"time": f"{dt.datetime.now():%Y-%m-%d %H:%M}", "variant": VARIANT["name"], "inputs": len(VARIANT["inputs"]),
           "ic": round(ic_s.mean(), 4), "ic_t": round(ic_s.mean() / ic_s.std() * np.sqrt(len(ic_s)), 2), "p_vs_live": round(p, 3),
           "cagr_arm": round(o["CAGR arm"], 4), "cagr_live": round(o["CAGR base"], 4), "ic_min_drop_name": "", "ic_min_drop_year": "",
           "status": status, "rule": RULE, "ic_live": round(ic(t).mean(), 4), "gain_min_drop_name": round(min(gain_name.values()), 4),
           "gain_min_drop_year": round(min(gain_year.values()), 4), "p_half1": round(p1, 3), "p_half2": round(p2, 3),
           "p_min_drop_year": round(p_year[worst], 3), "partial_ic": round(part, 4)}
    with open(LOG, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))  # rule 1's rows keep their columns and leave the new ones empty
        w.writeheader()
        w.writerows(old + [row])

    print(f"VARIANT {VARIANT['name']} | development years {grid[0].date()} to {DEV_END}, {len(grid)} months | end-2014 list")
    print(f"growth odds vs live {p:.2f} (halves {p1:.2f}, {p2:.2f}; lowest without one year {p_year[worst]:.2f}) | {row['cagr_arm']:.1%} a year vs live {row['cagr_live']:.1%}")
    print(f"rank IC {row['ic']:+.3f} (t {row['ic_t']}) vs the live trend score's {row['ic_live']:+.3f} | gain without one stock: lowest "
          f"{min(gain_name.values()):+.3f} (without {min(gain_name, key=gain_name.get)}) | without one year: lowest {min(gain_year.values()):+.3f}")
    print(f"partial rank IC {part:+.3f}: what the forecast adds once the trend score is taken out (0 or below = nothing)")
    print("IC by year, network then trend: " + ", ".join(f"{yr} {ic_s[ic_s.index.year == yr].mean():+.2f} {ic(t)[grid.year == yr].mean():+.2f}" for yr in years))
    right = n = 0
    for day in grid:  # pairs the network and the live trend order differently: who was right?
        a, b, r = s.loc[day].values, t.loc[day].values, yy.loc[day].values
        da, db, dr = np.sign(a[:, None] - a[None, :]), np.sign(b[:, None] - b[None, :]), np.sign(r[:, None] - r[None, :])
        m = np.triu(da * db < 0, 1)
        right, n = right + (da[m] == dr[m]).sum(), n + m.sum()
    print(f"when it disagreed with the live trend about two stocks, the network was right {right / max(n, 1):.0%} of the time ({n} pairs)")
    monthly = (1 + arm).resample("ME").prod() - (1 + cur).resample("ME").prod()
    for mth, gap in monthly.nsmallest(3).items():
        day = arm.loc[f"{mth:%Y-%m}"].index[0]
        fc, k = score.loc[:day].iloc[-2].dropna().sort_values(), max(1, score.shape[1] // 3)  # the forecast it traded on
        f = y.loc[fc.name]
        print(f"worst month {mth:%Y-%m} ({gap:+.1%} vs live): favoured {', '.join(fc.index[-k:])} (then {f[fc.index[-k:]].mean():+.1%} vs the group), "
              f"avoided {', '.join(fc.index[:k])} (then {f[fc.index[:k]].mean():+.1%})")
    left = BUDGET - sum(r["status"] != "reference" for r in used) - (status != "reference")
    why = "; ".join(fails) if fails else "every condition holds"
    print(f"VERDICT: {dict(reference='reference, the starting network', kept='keep', reverted='revert')[status]} ({why}) | experiments left: {left}")


def log_forward():
    """The forward record (.github/workflows/mlp_log.yml, once a day after the close). Appends today's forecast for
    both lists, then scores each logged day once its 21 sessions have passed. Rows are only ever added: a forecast is
    what the committed code said that day, whatever Yahoo or the code say later. A missed day stays missing."""
    now = pd.Timestamp.now("America/New_York")
    new, done, sha = [], [], os.environ.get("GITHUB_SHA", "")[:7]
    logged = pd.read_csv(FORECASTS, parse_dates=["date"]) if os.path.exists(FORECASTS) else pd.DataFrame(columns=["date", "list", "variant"])
    scored = pd.read_csv(FORWARD, parse_dates=["date"]) if os.path.exists(FORWARD) else pd.DataFrame(columns=["date", "list", "variant"])
    for uni, data in zip(("end-2014", "shipped"), lists()):
        if data.index[-1].date() == now.date() and now.hour < 16:
            data = data.iloc[:-1]  # the session is still open: its last price is not a close
        day, c = data.index[-1], data[names_of(data)].ffill()
        if not ((logged["date"] == day) & (logged["list"] == uni)).any():
            nn, tr = walk_forward(data, last_only=True)[0], scores(data, {**P, "w_trend": 1.0})
            wn, wt = tilt(data, nn).loc[day], tilted(data).loc[day]
            if nn.loc[day].notna().any():
                new += [{"date": day.date(), "list": uni, "variant": VARIANT["name"], "sha": sha, "name": n, "close": round(c.loc[day, n], 4),
                         "nn_score": round(nn.loc[day, n], 5), "nn_rank": nn.loc[day].rank()[n], "nn_weight": round(wn[n], 4),
                         "trend_score": round(tr.loc[day, n], 5), "trend_rank": tr.loc[day].rank()[n], "trend_weight": round(wt[n], 4)}
                        for n in c.columns]
        for (d, v), g in logged[logged["list"] == uni].groupby(["date", "variant"]):
            k = data.index.get_indexer([d])[0]
            if k < 0 or k + FWD >= len(data) or ((scored["date"] == d) & (scored["list"] == uni) & (scored["variant"] == v)).any():
                continue  # not yet 21 sessions old, or already scored
            g = g.set_index("name")
            out = (c.iloc[k + FWD] / c.iloc[k] - 1).reindex(g.index)
            done.append({"date": d.date(), "list": uni, "variant": v, "names": len(g), "scored_on": data.index[-1].date(),
                         "ic_nn": round(g["nn_score"].corr(out, method="spearman"), 4), "ic_trend": round(g["trend_score"].corr(out, method="spearman"), 4),
                         "ret_nn_book": round((g["nn_weight"] / g["nn_weight"].sum() * out).sum(), 5),
                         "ret_trend_book": round((g["trend_weight"] / g["trend_weight"].sum() * out).sum(), 5)})
    for path, rows in ((FORECASTS, new), (FORWARD, done)):
        if rows:
            os.makedirs("signals", exist_ok=True)
            pd.DataFrame(rows).to_csv(path, mode="a", header=not os.path.exists(path), index=False)
    print(f"forward record: {len(new)} forecast rows added, {len(done)} days scored")


def main():
    _check()
    px14, px = lists()
    a, b = features(px14.iloc[:-250]), features(px14)  # no lookahead: inputs at a date do not change when later prices are added
    assert np.allclose(a.values, b.loc[a.index].values, equal_nan=True), "lookahead in the inputs"

    rows, start = {}, pd.Timestamp(VARIANT["judged_from"])
    for uni, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        score, y = walk_forward(data)
        first = score.dropna(how="all").index[0]
        arm, cur = (backtest_returns(data, w).loc[first:] for w in (tilt(data, score), tilted(data)))
        plain = backtest_returns(data, target_weights(data, LIVE)).loc[first:]
        ja, jc = arm.loc[start:], cur.loc[start:]
        p = lambda x, z: p_grow(x, z)["P(arm grows faster)"]
        rows[f"{NAME} | {uni}"] = row = {"sessions judged": len(ja), "P vs live": np.nan, "P 1st half": np.nan, "P 2nd half": np.nan}
        if len(ja) >= MIN_FWD:  # fewer new days than that cannot tell skill from luck, and none at all cannot be scored
            mid, o, ic = ja.index[len(ja) // 2], p_grow(ja, jc), rank_ic(score, y, start, None)
            row.update({"P vs live": o["P(arm grows faster)"], "P 1st half": p(ja[:mid], jc[:mid]), "P 2nd half": p(ja[mid:], jc[mid:]),
                        "CAGR arm": o["CAGR arm"], "CAGR live": o["CAGR base"], "MaxDD arm": o["MaxDD arm"], "MaxDD live": o["MaxDD base"],
                        "rank IC": ic.mean(), "IC t": ic.mean() / ic.std() * np.sqrt(len(ic))})
        row.update({"whole window: P vs live": p(arm, cur), "whole window: P vs untilted": p(arm, plain)})
    t = pd.DataFrame(rows).T
    d, s = t.iloc[0], t.iloc[1]  # a comparison with NaN is False, so a variant with too few judged sessions cannot pass
    ok = {NAME: d["P vs live"]} if d["P vs live"] >= BAR and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5 else {}
    early = "" if d["sessions judged"] >= MIN_FWD else f" Too early to judge: {d['sessions judged']:.0f} of the {MIN_FWD} sessions needed."
    out = ["# A neural network that refits every month: decision odds\n",
           f"Rules in mlp_odds.py. Variant: {VARIANT['name']}. Judged from {VARIANT['judged_from']} on; 'live' = the current book (long-trend tilt).{early}\n",
           t.T.to_markdown(floatfmt=".3f"),
           f"\n- Decision: {'replace the live tilt with the network' if ok else '**the live tilt stays**: the network does not clear the bar'}"]
    with open("reports/mlp_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    dev() if "--dev" in sys.argv else log_forward() if "--log" in sys.argv else main()
