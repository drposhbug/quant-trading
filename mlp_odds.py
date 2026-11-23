"""A small neural network that keeps learning which stocks to hold more of. Writes reports/mlp_odds.md.
Run: python mlp_odds.py

The owner's ask (2026-11-23): "an MLP so it learns from its mistakes". Written before the first run.
Model: one hidden layer of 16 tanh units, squared error + L2, Adam, early stopping on the most recent 20% of its
training days; 3 seeds averaged. Plain numpy, no new dependency.
Inputs per stock per day, all known at that close: the stock's return over 5/21/63/126/252 sessions and its 5-session
return left over after QQQ, each divided by its 60-day volatility; distance from its 200-day average and from its
one-year high; 60-day volatility; 5-day over 60-day volatility; 60-day beta to QQQ. Each is a z-score across the names
that day. Plus three market inputs (QQQ's 21-session return, distance from its 200-day average, 20-day volatility),
standardised on past data only.
Target: the stock's return over the next 21 sessions minus the average of the names that day.
Learning from its mistakes: it is refitted every 21 sessions on every day whose 21-session outcome is by then known,
so each refit includes its latest errors. First fit after 500 sessions. Trained separately on each list, so the
end-2014 test contains no hindsight.
Use: the live tilt mechanics (x2 top third, x0.5 bottom third, same gross and caps) with the network's forecast as the score.
Decision (same bar as mini_trend_odds.py): replace the live tilt only if, on the end-2014 list, P(arm grows faster than
the current live book) >= 0.90 over the whole window AND > 0.5 in each half, AND >= 0.5 on the shipped list.
Reported, not deciding: the arm against the untilted book, and the rank IC of the forecasts (did it order the stocks).
"""
import numpy as np
import pandas as pd

from backtest import prices
from growth_odds import LIVE, odds
from mini_trend_odds import tilt
from model import BENCH, P, backtest_returns, names_of, target_weights
from monitor import tilted
from universe_study import TECH10_2014, load_extra

FIRST, EVERY, FWD, SEEDS = 500, 21, 21, (0, 1, 2)
NAME = "mlp: a neural network refitted every month"


def _loss_grad(p, X, y, l2):
    W1, b1, w2, b2 = p
    H = np.tanh(X @ W1 + b1)
    e = (H @ w2 + b2 - y) / len(y)
    dH = np.outer(e, w2) * (1 - H * H)
    loss = 0.5 * len(y) * (e @ e) + 0.5 * l2 * ((W1 * W1).sum() + w2 @ w2)
    return loss, [X.T @ dH + l2 * W1, dH.sum(axis=0), H.T @ e + l2 * w2, np.array(e.sum())]


def predict(p, X):
    return np.tanh(X @ p[0] + p[1]) @ p[2] + p[3]


def fit(X, y, seed, hidden=16, l2=1e-3, lr=1e-3, epochs=60, batch=1024, patience=5):
    """Rows must be in date order: the last 20% (the most recent days) decide when to stop."""
    rng, cut = np.random.default_rng(seed), int(len(y) * 0.8)
    p = [rng.normal(0, 1 / np.sqrt(X.shape[1]), (X.shape[1], hidden)), np.zeros(hidden), rng.normal(0, 1 / np.sqrt(hidden), hidden), np.array(0.0)]
    m, v, t = [np.zeros_like(a) for a in p], [np.zeros_like(a) for a in p], 0
    best, best_p, bad = np.inf, [a.copy() for a in p], 0
    for _ in range(epochs):
        order = rng.permutation(cut)
        for k in range(0, cut, batch):
            idx = order[k:k + batch]
            g = _loss_grad(p, X[idx], y[idx], l2)[1]
            t += 1
            for j in range(4):  # Adam
                m[j] = 0.9 * m[j] + 0.1 * g[j]
                v[j] = 0.999 * v[j] + 0.001 * g[j] ** 2
                p[j] = p[j] - lr * (m[j] / (1 - 0.9 ** t)) / (np.sqrt(v[j] / (1 - 0.999 ** t)) + 1e-8)
        val = np.mean((predict(p, X[cut:]) - y[cut:]) ** 2)
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
    y = sig + rng.normal(size=6000)
    out = predict(fit(X[:5000], y[:5000], 0, lr=3e-3), X[5000:])
    assert np.corrcoef(out, sig[5000:])[0, 1] > 0.6, "the network should learn a planted non-linear pattern"


def features(px):
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
    return X


def walk_forward(px):
    """Forecast score [date x name]: each block of EVERY sessions uses a network fitted on outcomes known by then."""
    X = features(px)
    c = px[names_of(px)].ffill()
    fwd = c.shift(-FWD) / c - 1
    y = fwd.sub(fwd.mean(axis=1), axis=0).stack(future_stack=True).reindex(X.index)
    d0, dates = X.index.get_level_values(0), px.index
    good, known = X.notna().all(axis=1).values, y.notna().values
    pred = pd.Series(np.nan, index=X.index)
    for i in range(FIRST, len(dates), EVERY):
        tr = good & known & (d0 <= dates[i - FWD])  # the last training day's 21-session outcome is known at close i
        te = good & (d0 >= dates[i]) & (d0 < dates[i + EVERY] if i + EVERY < len(dates) else True)
        if tr.sum() < 500 or not te.any():
            continue
        Xt, yt = X.values[tr], y.values[tr] / y.values[tr].std()
        pred[te] = np.mean([predict(fit(Xt, yt, s), X.values[te]) for s in SEEDS], axis=0)
    return pred.unstack().reindex(index=px.index, columns=names_of(px)), y.unstack()


def main():
    _check()
    px = prices()
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    a, b = features(px14.iloc[:-250]), features(px14)  # no lookahead: inputs at a date do not change when later prices are added
    assert np.allclose(a.values, b.loc[a.index].values, equal_nan=True), "lookahead in the inputs"

    rows = {}
    for uni, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        score, y = walk_forward(data)
        first = score.dropna(how="all").index[0]
        arm = backtest_returns(data, tilt(data, score)).loc[first:]
        cur = backtest_returns(data, tilted(data)).loc[first:]
        plain = backtest_returns(data, target_weights(data, LIVE)).loc[first:]
        mid, o = arm.index[len(arm) // 2], odds(arm, cur)
        p = lambda x, z: odds(x, z)["P(arm grows faster)"]
        ic = score.loc[first::FWD].corrwith(y.reindex(score.index).loc[first::FWD], axis=1, method="spearman").dropna()
        rows[f"{NAME} | {uni}"] = {"P vs live": o["P(arm grows faster)"], "P 1st half": p(arm[:mid], cur[:mid]), "P 2nd half": p(arm[mid:], cur[mid:]),
                                   "P vs untilted": p(arm, plain), "CAGR arm": o["CAGR arm"], "CAGR live": o["CAGR base"],
                                   "MaxDD arm": o["MaxDD arm"], "MaxDD live": o["MaxDD base"], "rank IC": ic.mean(),
                                   "IC t": ic.mean() / ic.std() * np.sqrt(len(ic)), "from": first.date()}
    t = pd.DataFrame(rows).T
    d, s = t.iloc[0], t.iloc[1]
    ok = {NAME: d["P vs live"]} if d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5 else {}
    out = ["# A neural network that refits every month: decision odds, 2026-11-23\n",
           "Rules written in mlp_odds.py before the run. 'live' = the current book (long-trend tilt).\n", t.to_markdown(floatfmt=".3f"),
           f"\n- Decision: {'replace the live tilt with the network' if ok else '**the live tilt stays**: the network does not clear the bar'}"]
    with open("reports/mlp_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    main()
