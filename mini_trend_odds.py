"""Mini trends: should the book lean on short trends, or learn which trend length is working? Writes
reports/mini_trend_odds.md. Run: python mini_trend_odds.py

The owner's idea (2026-11-23): the market is getting less logical, so follow short trends and learn to capitalise.
Written before the first run. Same method as growth_odds.py / tilt_odds.py: P = share of 2,000 paired
stationary-bootstrap histories (L = 20) in which the arm's mean log return is higher. Every arm is the live book
(inverse-vol, fully invested, caps, 5 bp costs) with the same tilt mechanics as monitor.tilted: x2 for the top third of
names by a score, x0.5 for the bottom third, same gross. Only the score changes:
  mini 5 / 10 / 21 / 63-day   the stock's return over that many sessions, divided by its 60-day volatility
  learn                       each day use whichever of {5-day, 21-day, 63-day, the live long trend} made the most money
                              over the previous 126 sessions (after costs, known at that close); the live trend before then
Compared with the CURRENT live book (monitor.tilted, the long trend added earlier today), since an arm would replace it.
Decision: replace the live tilt only if, on the end-2014 list (names chosen without hindsight), P(arm grows faster
than the current live book) >= 0.90 over the whole window AND > 0.5 in each half, AND >= 0.5 on the shipped list.
If several qualify, the highest whole-window P. Otherwise the live tilt stays.
The bar is 0.90, not 0.80, because five more arms are tried on top of this morning's three.
Reported, not deciding: the last three years alone (the owner's "now"), and each arm against the untilted book.
"""
import numpy as np
import pandas as pd

from backtest import prices
from growth_odds import LIVE, odds
from model import BENCH, EVENT_CAPS, P, backtest_returns, names_of, scores, target_weights
from monitor import tilted
from universe_study import TECH10_2014, load_extra


def tilt(px, score):
    """monitor.tilted with any score (main() checks it reproduces the live function on the live score)."""
    w = target_weights(px, LIVE)
    rank = score.where(w > 0).rank(axis=1, pct=True)
    t = w * np.select([rank > 2 / 3, rank <= 1 / 3], [2.0, 0.5], 1.0)
    caps = pd.Series({c: EVENT_CAPS.get(c, P["cap"]) for c in w.columns})
    return t.div(t.sum(axis=1), axis=0).mul(w.sum(axis=1), axis=0).fillna(0).clip(upper=caps, axis=1)


def mini(px, h):
    lr = np.log(px[names_of(px)]).diff()
    return lr.rolling(h).sum() / (lr.rolling(P["vol_win"]).std() * np.sqrt(h))


def learn(px, cands, default):
    """Each day hold the candidate book that earned most over the previous 126 sessions (returns through that close)."""
    tr = pd.DataFrame({k: np.log1p(backtest_returns(px, w)) for k, w in cands.items()}).rolling(126).sum()
    best = tr.fillna(-np.inf).idxmax(axis=1).where(tr.notna().all(axis=1), default)
    return sum(w.mul((best == k).astype(float), axis=0) for k, w in cands.items()), best


def books(px):
    b = {f"mini {h}-day": tilt(px, mini(px, h)) for h in (5, 10, 21, 63)}
    cands = {"5-day": b["mini 5-day"], "21-day": b["mini 21-day"], "63-day": b["mini 63-day"], "long": tilted(px)}
    b["learn"], best = learn(px, cands, "long")
    return b, best


def main():
    px = prices()
    start = px.index[P["trend_long"] + P["vol_win"]]
    extra = load_extra(sorted(set(TECH10_2014) - set(px.columns)))
    px14 = px.join(extra.drop(columns="^IRX"), how="left")[TECH10_2014 + [BENCH]]
    assert np.allclose(tilt(px14, scores(px14, {**P, "w_trend": 1.0})), tilted(px14)), "tilt() differs from the live function"
    cut = px14.iloc[:-250]  # no lookahead: weights at a date do not change when later prices are added
    for name, w in books(cut)[0].items():
        assert np.allclose(w.iloc[-1], books(px14)[0][name].loc[cut.index[-1]], atol=1e-9), f"lookahead in {name}"

    rows, picks = {}, {}
    for uni, data in {"end-2014 list (decides)": px14, "shipped list (reported)": px}.items():
        cur = backtest_returns(data, tilted(data)).loc[start:]
        plain = backtest_returns(data, target_weights(data, LIVE)).loc[start:]
        mid, recent = cur.index[len(cur) // 2], cur.index[-756]
        b, best = books(data)
        picks[uni] = best.loc[start:].value_counts(normalize=True)
        for name, w in b.items():
            arm = backtest_returns(data, w).loc[start:]
            o = odds(arm, cur)
            p = lambda a, c: odds(a, c)["P(arm grows faster)"]
            rows[(name, uni)] = {"P vs live": o["P(arm grows faster)"], "P 1st half": p(arm[:mid], cur[:mid]),
                                 "P 2nd half": p(arm[mid:], cur[mid:]), "P last 3 yrs": p(arm[recent:], cur[recent:]),
                                 "P vs untilted": p(arm, plain), "CAGR arm": o["CAGR arm"], "CAGR live": o["CAGR base"],
                                 "MaxDD arm": o["MaxDD arm"], "MaxDD live": o["MaxDD base"],
                                 "turnover/yr": (w - w.shift()).abs().sum(axis=1).loc[start:].mean() * 126}
    t = pd.DataFrame(rows).T
    t.index = [f"{a} | {u}" for a, u in t.index]
    ok = {}
    for name in dict.fromkeys(a for a, _ in rows):
        d, s = t.loc[f"{name} | end-2014 list (decides)"], t.loc[f"{name} | shipped list (reported)"]
        if d["P vs live"] >= 0.90 and d["P 1st half"] > 0.5 and d["P 2nd half"] > 0.5 and s["P vs live"] >= 0.5:
            ok[name] = d["P vs live"]
    verdict = f"replace the live tilt with **{max(ok, key=ok.get)}**" if ok else "**the live tilt stays**: no arm clears the bar"
    out = ["# Mini trends and a learning rule: decision odds, 2026-11-23\n",
           "Rules written in mini_trend_odds.py before the run. 'live' = the current book (long-trend tilt).\n",
           t.to_markdown(floatfmt=".3f"), f"\n- Decision: {verdict}",
           "- Share of days the learning rule held each trend length: " + "; ".join(
               f"{u.split(' (')[0]}: " + ", ".join(f"{k} {v:.0%}" for k, v in s.items()) for u, s in picks.items())]
    with open("reports/mini_trend_odds.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    return t, ok


if __name__ == "__main__":
    main()
