"""A small neural network that keeps learning which stocks to hold more of, and the lab a Claude loop improves it in.
Run: python mlp_odds.py          official test (learn.py runs it monthly); writes reports/mlp_odds.md
     python mlp_odds.py --dev    lab: score the current VARIANT on development years only, print why it went wrong,
                                 log it to reports/mlp_lab_log.csv and print VERDICT: keep / revert

The owner's ask (2026-11-23): "an MLP so it learns from its mistakes", then "a Claude loop that fixes the code itself".
Model: one hidden layer of tanh units, squared error + L2, Adam, early stopping on its most recent training days
(whole days, with a 21-session gap so no label overlaps); 3 seeds averaged. Plain numpy, no new dependency.
Inputs per stock per day, all known at that close, each a z-score across the names that day; market inputs are
standardised on past data only. Target: the stock's return over the next 21 sessions against the other names.
Learning from its mistakes: refitted every 21 sessions on every day whose outcome is by then known, so each refit
includes its latest errors. First fit after 500 sessions. Trained separately on each list, so the end-2014 test
contains no hindsight. Use: the live tilt mechanics (x2 top third, x0.5 bottom third) with the forecast as the score.

The lab (rules fixed 2026-11-23 before the first experiment; Astra 6.2's review shaped them):
- Development years end 2021-12-31 (DEV_END). --dev never computes a forecast after that date. Later years are the lockbox.
- One change per experiment (inputs, target, training, architecture), in this file only, with a new VARIANT name.
- A change is kept only if ALL hold on the end-2014 list in the development years: rank IC at least 0.01 above the
  last kept variant; growth odds against the live book not lower by more than 0.02 (the simulation's own noise); and
  the rank IC stays above the last kept variant's when any one stock or any one year is left out. Otherwise the code
  is reverted. The log keeps both outcomes.
- A lab session is at most 5 experiments. Then the kept variant gets ONE lockbox verdict (the official run) and is
  frozen. The lockbox can be spent once: any later change must set VARIANT["judged_from"] to its own date and is
  judged only on data after it.
- Changes must run on GitHub (prices downloadable from Yahoo). Nothing here touches the trading bot.
Official bar (replaces the whole-window bar of the first run, because development years are now used for tuning):
on the end-2014 list from VARIANT["judged_from"] on, P(arm grows faster than the live book) >= 0.90 and > 0.5 in each
half of that window, and >= 0.5 on the shipped list over the same window. Whole-window numbers are reported only.
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


def walk_forward(px, upto=None):
    """(forecast score, realised target), both [date x name]. Each block of EVERY sessions uses a network fitted on
    outcomes known by then. With `upto`, no forecast is made after that date."""
    X, yw = features(px), target(px)
    y = yw.stack(future_stack=True).reindex(X.index)
    d0, dates = X.index.get_level_values(0), px.index
    day = dates.get_indexer(d0)
    good, known = X.notna().all(axis=1).values, y.notna().values
    pred = pd.Series(np.nan, index=X.index)
    for i in range(FIRST, len(dates), EVERY):
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
    """Lab: development years only. Prints the scores, where the network went wrong, and the verdict."""
    px14 = lists()[0]
    score, y = walk_forward(px14, upto=DEV_END)
    a = score.dropna(how="all").index[0]
    arm, cur = (backtest_returns(px14, w).loc[a:DEV_END] for w in (tilt(px14, score), tilted(px14)))
    o, ic = p_grow(arm, cur), rank_ic(score, y, a, DEV_END)
    drop_name = {n: rank_ic(score.drop(columns=n), y.drop(columns=n), a, DEV_END).mean() for n in score.columns}
    drop_year = {yr: ic[ic.index.year != yr].mean() for yr in sorted(set(ic.index.year))}
    row = {"time": f"{dt.datetime.now():%Y-%m-%d %H:%M}", "variant": VARIANT["name"], "inputs": len(VARIANT["inputs"]),
           "ic": round(ic.mean(), 4), "ic_t": round(ic.mean() / ic.std() * np.sqrt(len(ic)), 2), "p_vs_live": round(o["P(arm grows faster)"], 3),
           "cagr_arm": round(o["CAGR arm"], 4), "cagr_live": round(o["CAGR base"], 4),
           "ic_min_drop_name": round(min(drop_name.values()), 4), "ic_min_drop_year": round(min(drop_year.values()), 4)}
    old = list(csv.DictReader(open(LOG))) if os.path.exists(LOG) else []
    kept = [r for r in old if r["status"] == "kept"]
    if not kept:
        row["status"], why = "kept", "first run: this is the baseline"
    else:
        b_ic, b_p = float(kept[-1]["ic"]), float(kept[-1]["p_vs_live"])
        fails = [t for t, bad in ((f"rank IC {row['ic']:+.3f} is not 0.01 above {b_ic:+.3f}", row["ic"] < b_ic + 0.01),
                                  (f"growth odds {row['p_vs_live']:.2f} fell from {b_p:.2f}", row["p_vs_live"] < b_p - 0.02),
                                  ("the gain disappears when one stock or one year is left out", min(row["ic_min_drop_name"], row["ic_min_drop_year"]) <= b_ic)) if bad]
        row["status"], why = ("reverted", "; ".join(fails)) if fails else ("kept", "all three conditions hold")
    with open(LOG, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        w.writeheader()
        w.writerows(old + [row])

    print(f"VARIANT {VARIANT['name']} | development years {a.date()} to {DEV_END} | end-2014 list")
    print(f"rank IC {row['ic']:+.3f} (t {row['ic_t']}) | growth odds vs live {row['p_vs_live']:.2f} | {row['cagr_arm']:.1%} a year vs live {row['cagr_live']:.1%}")
    print(f"IC without one stock: lowest {min(drop_name.values()):+.3f} (without {min(drop_name, key=drop_name.get)}), highest {max(drop_name.values()):+.3f} (without {max(drop_name, key=drop_name.get)})")
    print("IC by year: " + ", ".join(f"{yr} {ic[ic.index.year == yr].mean():+.2f}" for yr in drop_year))
    tr = scores(px14, {**P, "w_trend": 1.0})
    right = n = 0
    for d in ic.index:  # pairs the network and the live trend order differently: who was right?
        s, t, r = score.loc[d].values, tr.loc[d].values, y.loc[d].values
        ds, dt_, dr = np.sign(s[:, None] - s[None, :]), np.sign(t[:, None] - t[None, :]), np.sign(r[:, None] - r[None, :])
        m = np.triu(ds * dt_ < 0, 1)
        right, n = right + (ds[m] == dr[m]).sum(), n + m.sum()
    print(f"when it disagreed with the live trend about two stocks, the network was right {right / max(n, 1):.0%} of the time ({n} pairs)")
    monthly = (1 + arm).resample("ME").prod() - (1 + cur).resample("ME").prod()
    for mth, gap in monthly.nsmallest(3).items():
        d = arm.loc[f"{mth:%Y-%m}"].index[0]
        s, k = score.loc[:d].iloc[-2].dropna().sort_values(), max(1, score.shape[1] // 3)  # the forecast it traded on
        f = y.loc[s.name]
        print(f"worst month {mth:%Y-%m} ({gap:+.1%} vs live): favoured {', '.join(s.index[-k:])} (then {f[s.index[-k:]].mean():+.1%} vs the group), "
              f"avoided {', '.join(s.index[:k])} (then {f[s.index[:k]].mean():+.1%})")
    print(f"VERDICT: {'keep' if row['status'] == 'kept' else 'revert'} ({why})")


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
        mid, o, ic = ja.index[len(ja) // 2], p_grow(ja, jc), rank_ic(score, y, start, None)
        p = lambda x, z: p_grow(x, z)["P(arm grows faster)"]
        rows[f"{NAME} | {uni}"] = {"P vs live": o["P(arm grows faster)"], "P 1st half": p(ja[:mid], jc[:mid]), "P 2nd half": p(ja[mid:], jc[mid:]),
                                   "CAGR arm": o["CAGR arm"], "CAGR live": o["CAGR base"], "MaxDD arm": o["MaxDD arm"], "MaxDD live": o["MaxDD base"],
                                   "rank IC": ic.mean(), "IC t": ic.mean() / ic.std() * np.sqrt(len(ic)),
                                   "whole window: P vs live": p(arm, cur), "whole window: P vs untilted": p(arm, plain)}
    t = pd.DataFrame(rows).T
    d, s = t.iloc[0], t.iloc[1]
    ok = {NAME: d["P vs live"]} if d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5 else {}
    out = ["# A neural network that refits every month: decision odds\n",
           f"Rules in mlp_odds.py. Variant: {VARIANT['name']}. Judged from {VARIANT['judged_from']} on; 'live' = the current book (long-trend tilt).\n",
           t.T.to_markdown(floatfmt=".3f"),
           f"\n- Decision: {'replace the live tilt with the network' if ok else '**the live tilt stays**: the network does not clear the bar'}"]
    with open("reports/mlp_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    dev() if "--dev" in sys.argv else main()
