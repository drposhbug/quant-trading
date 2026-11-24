"""Meme stocks, crypto stocks and candles: is there a pattern there that the large companies do not have?
Writes reports/meme_crypto_results.md.   Run: python meme_crypto_study.py

The owner's ask (2026-11-23): "can you find correlation in those meme and crypto stocks and candles in these".
Everything tested so far was large companies, where prices are picked over by professionals. Stocks traded mostly
by small traders are where the published work finds more. Written before the first run. Four tests, one deciding
number each; anything else in the report is a reading.
The lists were chosen today from names known as meme or crypto stocks, which is hindsight: a name is on the list
because it became famous. Dead ones are kept where bars exist. A pattern found here is a lead to follow on new
days (shadow), never a result to trade on its own. Alpaca adjusted daily bars; a name needs 250 sessions.
1. Night against day. Each day, the list's average move from the last close to the open, and from the open to the
   close. Decides: the meme list's overnight mean. Real if t >= 3 and positive in both halves of the days. Read
   beside it: the same after 10 bp a night for trading in and out, and the crypto list.
2. After a spike. A meme stock closes up more than 15% on more than 3 times its normal volume. In at the next
   open, held 5 sessions, against the list's average (a basket of all such stocks; each day one observation).
   Decides: the basket's daily mean. Real if its t is 3 or more in size with the same sign in both halves:
   minus means spikes fade, plus means they keep going.
3. Crypto stocks and Bitcoin. Bitcoin trades all night and all weekend; the stocks do not. Decides: does Bitcoin's
   move from the stock market's close (16:00 New York) to 09:00 the next session predict what the crypto list
   does from the open to the close that day? The slope of one on the other; real if its t is 3 or more in size
   with the same sign in both halves. Read beside it: how tightly the two move together day to day, and how much
   of Bitcoin's overnight move is already in the opening price.
4. Candles. The 13 candle patterns and three holding periods of the earlier study on big technology stocks
   (candles.py), on both lists together, with that study's rule: a pattern counts only if it survives the
   correction for 39 tries (Holm, p < 0.05) and has the same sign before and after 2021. One change, because of
   what was learned since: the return is measured from the next open, the first price that can be traded.
"""
import math
import os
import warnings
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests

from candles import H, SPLIT, holm, patterns, test
from daily_calls import bars
from news_filing_study import held

MEME = ["GME", "AMC", "BB", "NOK", "KOSS", "BBBY", "EXPR", "PLTR", "HOOD", "SOFI", "RIVN", "LCID", "NKLA", "SPCE", "CVNA", "AFRM", "UPST", "DJT", "RDDT",
        "TLRY", "SNDL", "CLOV", "WISH", "MULN", "FFIE", "NIO", "PLUG", "DKNG", "OPEN", "BYND", "PTON", "SNAP", "RBLX"]
CRYPTO = ["COIN", "MSTR", "MARA", "RIOT", "CLSK", "HUT", "BITF", "CIFR", "HIVE", "BTBT", "WULF", "IREN", "CORZ", "GLXY", "SI", "BKKT", "CAN"]


def bitcoin():
    """Bitcoin's price at 16:00 and at 09:00 New York time on each date, from Alpaca's hourly bars (2021 on)."""
    key, sec = os.environ.get("ALPACA_API_KEY"), os.environ.get("ALPACA_SECRET_KEY")
    if not key and os.path.exists(".env"):
        env = dict(line.strip().split("=", 1) for line in open(".env") if "=" in line)
        key, sec = env["ALPACA_API_KEY"], env["ALPACA_SECRET_KEY"]
    rows, tok = [], None
    while True:
        q = dict(symbols="BTC/USD", timeframe="1Hour", start="2021-01-01", limit=10000)
        if tok:
            q["page_token"] = tok
        r = requests.get("https://data.alpaca.markets/v1beta3/crypto/us/bars", headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": sec}, params=q, timeout=60)
        r.raise_for_status()
        j = r.json()
        rows += (j.get("bars") or {}).get("BTC/USD", [])
        tok = j.get("next_page_token")
        if not tok:
            break
    b = pd.DataFrame(rows)
    t = pd.to_datetime(b["t"], utc=True).dt.tz_convert("America/New_York")
    at = lambda hour: pd.Series(b["c"].values, index=t)[t.dt.hour.values == hour - 1].rename(lambda x: x.tz_localize(None).normalize())  # the bar ending at `hour`
    return at(16), at(9)


def stats(x):
    x = x.dropna()
    half = len(x) // 2
    return {"days": len(x), "mean, bp": x.mean() * 1e4, "t": x.mean() / (x.std() / math.sqrt(len(x))), "1st half, bp": x.iloc[:half].mean() * 1e4,
            "2nd half, bp": x.iloc[half:].mean() * 1e4, "share of days up": (x > 0).mean()}


def main():
    warnings.simplefilter("ignore")
    b = bars(sorted(set(MEME + CRYPTO)))
    have = [n for n in b["c"].columns if b["c"][n].notna().sum() >= 250]
    meme, crypto = [n for n in MEME if n in have], [n for n in CRYPTO if n in have]
    O, Hh, L, C, V = (b[k][have] for k in "ohlcv")
    night, day = O / C.shift(1) - 1, C / O - 1
    out = ["# Meme stocks, crypto stocks and candles\n",
           f"Rules written in meme_crypto_study.py before the run. Meme list ({len(meme)}): {', '.join(meme)}. Crypto list ({len(crypto)}): {', '.join(crypto)}. "
           f"Not found or too short: {', '.join(n for n in MEME + CRYPTO if n not in have) or 'none'}. {C.index[0].date()} to {C.index[-1].date()}. bp = hundredths of a percent.\n"]

    # 1. night against day
    rows = {}
    for name, lst in (("meme", meme), ("crypto", crypto)):
        rows[f"{name}: overnight (close to open)"] = stats(night[lst].mean(axis=1))
        rows[f"{name}: overnight after 10 bp a night"] = stats(night[lst].mean(axis=1) - 0.0010)
        rows[f"{name}: daytime (open to close)"] = stats(day[lst].mean(axis=1))
    t1 = pd.DataFrame(rows).T
    r = t1.loc["meme: overnight (close to open)"]
    v1 = "real" if r["t"] >= 3 and r["1st half, bp"] > 0 and r["2nd half, bp"] > 0 else "no pattern"
    out += ["## 1. Night against day\n", t1.to_markdown(floatfmt=".2f"), f"\n- Verdict (meme list, overnight): **{v1}**.\n"]

    # 2. after a spike
    cc = C.pct_change()
    spike = ((cc > 0.15) & (V / V.rolling(60).mean().shift(1) > 3))[meme]
    first, later = (C / O - 1)[meme], cc[meme]
    rf, rl = first.sub(first.mean(axis=1), axis=0), later.sub(later.mean(axis=1), axis=0)
    sgn = pd.DataFrame(np.where(spike, 1.0, np.nan), index=spike.index, columns=spike.columns)
    s2 = stats(held(sgn, rf, rl, 5))
    week = (C.shift(-5) / O.shift(-1) - 1)[meme]
    per = week.sub(week.mean(axis=1), axis=0).where(spike).stack().dropna()
    v2 = "no pattern" if abs(s2["t"]) < 3 or s2["1st half, bp"] * s2["2nd half, bp"] <= 0 else "real: spikes fade" if s2["t"] < 0 else "real: spikes keep going"
    out += ["## 2. After a spike (up more than 15% on more than 3 times normal volume)\n",
            f"{int(spike.sum().sum())} spikes. In at the next open, 5 sessions, against the list's average: {s2['mean, bp']:+.0f} bp a day, t {s2['t']:+.1f} "
            f"(halves {s2['1st half, bp']:+.0f} and {s2['2nd half, bp']:+.0f}), {s2['days']} days. Per spike over the 5 sessions: {per.mean():+.1%}; it lagged the list {np.mean(per < 0):.0%} of the time.",
            f"\n- Verdict: **{v2}**.\n"]

    # 3. crypto stocks and Bitcoin
    p16, p09 = bitcoin()
    idx = C.index[C.index >= p16.index.min()]
    btc_night = (p09.reindex(idx) / p16.reindex(idx).shift(1) - 1)
    btc_full = p16.reindex(idx).pct_change()
    cday, cnight, cfull = day[crypto].mean(axis=1).reindex(idx), night[crypto].mean(axis=1).reindex(idx), cc[crypto].mean(axis=1).reindex(idx)

    def slope(x, y):
        d = pd.concat([x, y], axis=1).dropna()
        xv, yv = d.iloc[:, 0] - d.iloc[:, 0].mean(), d.iloc[:, 1] - d.iloc[:, 1].mean()
        bb = (xv * yv).sum() / (xv ** 2).sum()
        res = yv - bb * xv
        return bb, bb / math.sqrt((res ** 2).sum() / (len(d) - 2) / (xv ** 2).sum()), len(d)
    bb, tt, n = slope(btc_night, cday)
    h = len(idx) // 2
    b1, b2 = slope(btc_night.iloc[:h], cday.iloc[:h])[0], slope(btc_night.iloc[h:], cday.iloc[h:])[0]
    v3 = "no pattern" if abs(tt) < 3 or b1 * b2 <= 0 else "real: the stocks keep following Bitcoin during the day" if bb > 0 else "real: the stocks give back part of the opening move"
    mon = idx[idx.dayofweek == 0]
    out += ["## 3. Crypto stocks and Bitcoin\n",
            f"- They move together: the crypto list's daily move against Bitcoin's (16:00 to 16:00) has a correlation of {cfull.corr(btc_full):.2f}; for each 1% in Bitcoin the list moves {slope(btc_full, cfull)[0]:.2f}%.",
            f"- Bitcoin's overnight move is in the opening price: for each 1% Bitcoin moves between the close and 09:00, the list opens {slope(btc_night, cnight)[0]:.2f}% higher (correlation {btc_night.corr(cnight):.2f}).",
            f"- **The deciding number:** for each 1% Bitcoin moved overnight, the list then moved {bb:+.2f}% from its open to its close, t {tt:+.1f}, {n} days (halves {b1:+.2f} and {b2:+.2f}). After weekends only: {slope(btc_night.reindex(mon), cday.reindex(mon))[0]:+.2f}, t {slope(btc_night.reindex(mon), cday.reindex(mon))[1]:+.1f}.",
            f"\n- Verdict: **{v3}**.\n"]

    # 4. candles, the earlier study's rule, from the next open
    pats, rows = patterns(O, Hh, L, C), []
    for hh in H:
        fwd = C.shift(-hh) / O.shift(-1) - 1
        excess = fwd - fwd.mean()
        for name, m in pats.items():
            n_, mu, hit, t_ = test(excess, m)
            _, mu_a, _, _ = test(excess.loc[:SPLIT], m.loc[:SPLIT])
            _, mu_b, _, _ = test(excess.loc[SPLIT:], m.loc[SPLIT:])
            rows.append(dict(Pattern=name, h=hh, n=n_, excess_bp=mu * 1e4, hit=hit, t=t_, pre2021_bp=mu_a * 1e4, post2021_bp=mu_b * 1e4))
    df = pd.DataFrame(rows)
    df["p"] = [2 * (1 - NormalDist().cdf(abs(x))) if pd.notna(x) else 1.0 for x in df.t]
    df["p_holm"] = holm(df.p.values)
    df["stable"] = np.sign(df.pre2021_bp) == np.sign(df.post2021_bp)
    won = df[(df.p_holm < 0.05) & df.stable]
    out += ["## 4. Candles\n", f"{len(df)} tries (13 patterns, holding {', '.join(str(x) for x in H)} sessions), from the next open, both lists together. The strongest five by t:\n",
            df.reindex(df.t.abs().sort_values(ascending=False).index).head(5).round({"excess_bp": 0, "hit": 2, "t": 2, "pre2021_bp": 0, "post2021_bp": 0, "p": 4, "p_holm": 3}).to_markdown(index=False),
            f"\n- Verdict: **{len(won)} of {len(df)} candle patterns survive**" + (": " + ", ".join(f"{a} ({b} sessions)" for a, b in zip(won.Pattern, won.h)) if len(won) else ": no candle pattern here either") + ".\n"]
    with open("reports/meme_crypto_results.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
