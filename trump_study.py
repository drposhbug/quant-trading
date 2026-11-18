"""Do Trump's Truth Social posts move these stocks, and does the move reverse? Writes reports/trump_results.md.

Posts: trumpstruth.org archive (2025-01-20 onward), cached in data/trump_posts.csv.
Per topic, on days with a matching post vs all other days:
  1. Impact:   is |event-day return| bigger than normal?          (Welch t-test on |r| / 60d vol)
  2. Reversal: does the event-day move reverse over the next h days? (slope of fwd return on event-day return,
               compared with the same slope on non-event days; HAC t)
"""
import math
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from statistics import NormalDist

import numpy as np
import pandas as pd
import requests

from backtest import hac_alpha, prices
from model import BENCH, UNIVERSE

CACHE = "data/trump_posts.csv"
FEED = "https://www.trumpstruth.org/feed"
START = pd.Timestamp("2025-01-20")

TOPICS = {  # regex -> tickers it should move
    "Tariffs / trade": (r"tariff|trade deal|trade war|reciprocal|import tax|customs dut", UNIVERSE + [BENCH]),
    "China": (r"\bchina\b|chinese|\bxi\b|beijing", UNIVERSE + [BENCH]),
    "Chips / Nvidia / AI": (r"\bchips?\b|semiconductor|nvidia|jensen|\bai\b|artificial intelligence", ["NVDA", "MSFT", "GOOGL", "META", "AMZN"]),
    "Apple": (r"\bapple\b|iphone|tim cook", ["AAPL"]),
    "Musk / Tesla / SpaceX": (r"\belon\b|musk|tesla|spacex|starlink|\bev\b|electric vehicle", ["TSLA", "SPCX"]),
    "Fed / rates": (r"\bfed\b|federal reserve|powell|interest rate|rate cut", UNIVERSE + [BENCH]),
    "Stock market talk": (r"stock market|\bstocks\b|dow jones|\bdow\b|s&p|nasdaq|great time to buy", UNIVERSE + [BENCH]),
    "Big Tech names": (r"amazon|bezos|google|alphabet|microsoft|meta\b|facebook|zuckerberg", ["AMZN", "GOOGL", "MSFT", "META"]),
}


def fetch_window(a, b):
    for attempt in range(8):
        try:
            r = requests.get(FEED, params={"start_date": a.date().isoformat(), "end_date": b.date().isoformat()},
                             timeout=30, headers={"User-Agent": "quant-research-script"})
        except requests.ConnectionError:
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code != 429:
            break
        time.sleep(int(r.headers.get("Retry-After", 0) or 0) or 15 * (attempt + 1))
    r.raise_for_status()
    items = ET.fromstring(r.content).iter("item")
    return [(parsedate_to_datetime(i.findtext("pubDate")), i.findtext("link"), (i.findtext("title") or "")) for i in items]


def load_posts():
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_csv(CACHE, parse_dates=["ts"])
    import pickle
    part = "data/trump_posts.partial.pkl"  # resume point if the archive drops the connection
    rows, day = pickle.load(open(part, "rb")) if os.path.exists(part) else ([], START)
    os.makedirs("data", exist_ok=True)
    end = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
    while day <= end:
        b = day + pd.Timedelta(days=2)
        got = fetch_window(day, b)
        if len(got) >= 100:  # feed page cap hit: refetch day by day
            per_day = [fetch_window(day + pd.Timedelta(days=k), day + pd.Timedelta(days=k)) for k in range(3)]
            got = [p for d in per_day for p in d]
            if any(len(d) >= 100 for d in per_day):
                print(f"warning: a day in {day.date()}..{b.date()} has 100+ posts, may be truncated")
        rows += got
        print(f"{b.date()}: {len(rows)} posts", flush=True)
        day = b + pd.Timedelta(days=1)
        pickle.dump((rows, day), open(part, "wb"))
        time.sleep(2)  # be polite to a free archive
    df = pd.DataFrame(rows, columns=["ts", "link", "text"]).drop_duplicates("link")
    df["ts"] = pd.to_datetime(df.ts, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df.to_csv(CACHE, index=False)
    os.remove(part)
    return df


def event_days(ts, trading_days):
    """Map post time to the first close that could react: same day if before 16:00 ET on a trading day, else next."""
    d = ts.dt.normalize() + pd.to_timedelta((ts.dt.hour >= 16).astype(int), unit="D")
    pos = trading_days.searchsorted(d)
    return pd.Series(trading_days[np.minimum(pos, len(trading_days) - 1)], index=ts.index)


def main():
    posts = load_posts()
    px = prices().loc[START - pd.Timedelta(days=120):]
    r = px / px.shift(1) - 1
    vol = r.rolling(60).std().shift(1)
    days = px.index[px.index >= START]
    posts["day"] = event_days(posts.ts, px.index)

    rows = []
    for topic, (pat, tickers) in TOPICS.items():
        hit = posts[posts.text.str.contains(pat, flags=re.I, regex=True)]
        ev = set(hit.day)
        for tk in tickers:
            z = (r[tk] / vol[tk]).loc[days].dropna()
            is_ev = z.index.isin(ev)
            a, b = z[is_ev].abs(), z[~is_ev].abs()
            if len(a) < 10:
                continue
            t_imp = (a.mean() - b.mean()) / math.sqrt(a.var() / len(a) + b.var() / len(b))
            row = dict(Topic=topic, Ticker=tk, posts=len(hit), event_days=len(a),
                       abs_move_vs_normal=a.mean() / b.mean(), t_impact=t_imp)
            for h in (1, 5):
                fwd = (px[tk].shift(-h) / px[tk] - 1).loc[z.index]
                ok = fwd.notna()
                x = r[tk].loc[z.index]
                # interaction regression: fwd = a + b*x + c*x*event; c<0 means extra reversal after post days
                X = np.column_stack([x[ok], (x * is_ev)[ok]])
                _, slope_ev, t_ev = hac_slope(fwd[ok].values, X, lags=h)
                row[f"extra_reversal_{h}d"] = slope_ev
                row[f"t_{h}d"] = t_ev
            rows.append(row)
    df = pd.DataFrame(rows)
    p = lambda t: 2 * (1 - NormalDist().cdf(abs(t)))
    m = len(df) * 3
    df["impact_sig"] = df.t_impact.map(lambda t: p(t) * m < 0.05)  # Bonferroni over all tests
    df["reversal_sig"] = (df.t_1d.map(lambda t: p(t) * m < 0.05)) | (df.t_5d.map(lambda t: p(t) * m < 0.05))

    out = [
        "# Trump posts vs these stocks\n",
        f"{len(posts):,} Truth Social posts {posts.ts.min().date()} to {posts.ts.max().date()} (trumpstruth.org). "
        f"Daily closes; a post after 16:00 ET counts for the next session.\n",
        "- **abs_move_vs_normal**: average size of the move on post days ÷ on other days (vol-normalised). 1.3 = 30% bigger moves.",
        "- **extra_reversal_hd**: extra slope of the next-h-day return on the post-day return, beyond normal days. "
        "Negative = moves after posts reverse more than usual (the tradable 'fade the post' idea).",
        "- Bonferroni-corrected over all tests.\n",
        df.round(3).to_markdown(index=False),
        "\n## Verdict\n",
        f"Impact significant in {df.impact_sig.sum()} of {len(df)} topic/ticker pairs; "
        f"extra reversal significant in {df.reversal_sig.sum()} of {len(df)}.",
    ]
    with open("reports/trump_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def hac_slope(y, X, lags):
    """OLS y = a + X b with Newey-West SEs; returns (b0, b_last, t_last)."""
    Xc = np.column_stack([np.ones(len(y)), X])
    beta = np.linalg.lstsq(Xc, y, rcond=None)[0]
    u = y - Xc @ beta
    inv = np.linalg.inv(Xc.T @ Xc)
    S = (Xc * u[:, None]).T @ (Xc * u[:, None])
    for l in range(1, lags + 1):
        G = (Xc[l:] * u[l:, None]).T @ (Xc[:-l] * u[:-l, None])
        S += (1 - l / (lags + 1)) * (G + G.T)
    se = np.sqrt(np.diag(inv @ S @ inv))
    return beta[1], beta[-1], beta[-1] / se[-1]


if __name__ == "__main__":
    main()
