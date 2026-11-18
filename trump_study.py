"""Do Trump's Truth Social posts predict these stocks' returns? Writes reports/trump_results.md.

Posts: trumpstruth.org archive (2025-01-20 onward), cached in data/trump_posts.csv (--refresh to refetch).
Returns start at the first daily price after each post (see entry_points). Per topic and ticker, post entries vs
all other entries: impact (|move|), drift (mean move) and extra reversal, HAC t, Holm over all tests.
"""
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

from candles import holm
from model import BENCH, UNIVERSE

CACHE = "data/trump_posts.csv"
FEED = "https://www.trumpstruth.org/feed"
START = pd.Timestamp("2025-01-20")
PLACEBOS = 300
MIN_SESSIONS = 250
rng = np.random.default_rng(7)

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
    else:
        raise RuntimeError(f"trumpstruth.org feed unreachable or rate-limited for {a.date()}..{b.date()}")
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


EARLY_CLOSE = {"2025-07-03", "2025-11-28", "2025-12-24", "2026-11-27", "2026-12-24"}  # NYSE 13:00 ET closes
# ponytail: hardcoded half-days; extend the set when the sample runs past 2026.


def entry_points(ts, sessions):
    """Map each post (naive ET) to the first daily price printed AFTER it: (session, "open"|"close").
    Before 09:30 on a session -> that open; during the session -> that close; after the close, weekend or
    holiday -> next session's open. Posts after the last available session -> NaT (dropped)."""
    day = ts.dt.normalize()
    mins = (ts.dt.hour * 60 + ts.dt.minute).values
    close_min = np.where(day.dt.strftime("%Y-%m-%d").isin(EARLY_CLOSE), 13 * 60, 16 * 60)
    is_session = day.isin(sessions).values
    pre = is_session & (mins < 9 * 60 + 30)
    intra = is_session & ~pre & (mins < close_min)
    pos = sessions.searchsorted(day.values, side="left")  # same day if it is a session, else the next one
    pos = np.where(is_session & ~pre & ~intra, pos + 1, pos)  # after the close -> next session
    ok = pos < len(sessions)
    sess = pd.Series(pd.NaT, index=ts.index, dtype="datetime64[ns]")
    sess[ok] = sessions[pos[ok]]
    return pd.DataFrame({"session": sess, "kind": np.where(intra, "close", "open")}, index=ts.index)


def load_ohlc():
    import yfinance as yf
    d = yf.download(UNIVERSE + [BENCH], start=START - pd.Timedelta(days=150), auto_adjust=True,
                    progress=False, threads=False)
    O, C = (d[k].reindex(columns=UNIVERSE + [BENCH]) for k in ("Open", "Close"))
    now = pd.Timestamp.now(tz="America/New_York")
    if now.hour < 17:  # today's bar may still be live
        today = now.normalize().tz_localize(None)
        O, C = O[O.index < today], C[C.index < today]
    return O, C


def panel(O, C, vol, tk, h, sessions):
    """Two rows per session (entry at the open, entry at the close): vol-normalised h-session forward return from
    the entry price, and the move from the prior close up to the entry price."""
    o, c = O[tk], C[tk]
    fo = pd.DataFrame({"fwd": c.shift(-(h - 1)) / o - 1, "pre": o / c.shift(1) - 1, "kind": "open"})
    fc = pd.DataFrame({"fwd": c.shift(-h) / c - 1, "pre": c / c.shift(1) - 1, "kind": "close"})
    df = pd.concat([fo, fc]).rename_axis("session").reset_index()
    v = df.session.map(vol[tk])
    df["fwd"], df["pre"] = df.fwd / v, df.pre / v
    df = df[df.session.isin(sessions)].dropna()
    return df.sort_values(["session", "kind"], ascending=[True, False]).reset_index(drop=True)


def main():
    posts = load_posts()
    O, C = load_ohlc()
    empty = [tk for tk in C if C[tk].loc[START:].isna().all()]  # e.g. ANT: not listed yet, yfinance has nothing
    sessions = C.index[C.index >= START]
    posts = posts[posts.ts >= START].join(entry_points(posts.ts, sessions)).dropna(subset=["session"])
    vol = (C / C.shift(1) - 1).rolling(60).std().shift(1)  # known before the session opens

    rows = []
    for topic, (pat, tickers) in TOPICS.items():
        hit = posts[posts.text.fillna("").str.contains(pat, flags=re.I, regex=True)]
        ev = set(zip(hit.session, hit.kind))  # several posts at one entry point = one event
        for tk in tickers:
            if tk in empty:
                continue
            row = dict(Topic=topic, Ticker=tk, posts=len(hit))
            for h in (1, 5):
                d = panel(O, C, vol, tk, h, sessions)
                is_ev = np.array([k in ev for k in zip(d.session, d.kind)], dtype=float)
                is_close = (d.kind == "close").values
                if is_ev.sum() < 10 or (~is_close).sum() < MIN_SESSIONS:  # short history -> placebo null degenerate
                    break
                coefs = lambda e: effects(d.fwd.values, d.pre.values, is_close.astype(float), e)
                actual = coefs(is_ev)
                # Placebo: shift the event dates circularly (within open and within close rows), keeping how posts
                # cluster in time (e.g. April 2025); the sd of placebo effects is the SE. HAC sandwich SEs badly
                # understate the noise when only ~10-50 rows are events.
                n = (~is_close).sum()
                placebo = []
                for k in rng.integers(20, n - 20, PLACEBOS):
                    e = is_ev.copy()
                    for m in (is_close, ~is_close):
                        e[m] = np.roll(is_ev[m], k)
                    placebo.append(coefs(e))
                z = (actual - np.mean(placebo, 0)) / np.std(placebo, 0)
                if h == 1:  # 1. impact: are moves after posts bigger than normal?
                    a = np.abs(d.fwd.values)
                    row.update(events=int(is_ev.sum()), event_share=is_ev.mean(),
                               abs_move_ratio=a[is_ev == 1].mean() / a[is_ev == 0].mean(), z_impact=z[0])
                row[f"drift_{h}d"], row[f"z_drift_{h}d"] = actual[1], z[1]
                row[f"extra_rev_{h}d"], row[f"z_rev_{h}d"] = actual[2], z[2]
            else:
                rows.append(row)
    df = pd.DataFrame(rows)
    tcols = ["z_impact", "z_drift_1d", "z_drift_5d", "z_rev_1d", "z_rev_5d"]
    p = df[tcols].map(lambda t: 2 * (1 - NormalDist().cdf(abs(t))))
    adj = pd.DataFrame(holm(p.values.ravel()).reshape(p.shape), columns=tcols, index=df.index)  # Holm over ALL tests
    df["min_p_holm"] = adj.min(axis=1)
    df["passes"] = [", ".join(c[2:] for c in tcols if adj.at[i, c] < 0.05) for i in df.index]
    sig = df[df.passes != ""]

    kinds = posts.kind.value_counts()
    capped = int((posts.ts.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC").dt.date.value_counts() >= 100).sum())
    out = [
        "# Trump posts vs these stocks\n",
        f"{len(posts):,} Truth Social posts {posts.ts.min().date()} to {posts.ts.max().date()} (trumpstruth.org; text = "
        f"RSS title, so video/image-only posts carry no text). Prices: yfinance adjusted daily open/close, "
        f"{sessions[0].date()} to {sessions[-1].date()}.\n",
        "## Method\n",
        "- **Timing.** Every return starts at the first daily price printed *after* the post: before 09:30 ET -> that "
        "session's open; during the session -> that session's close (13:00 on half-days); after the close, weekends, "
        f"holidays -> next session's open. Entry mix: {kinds.get('open', 0):,} posts at an open, "
        f"{kinds.get('close', 0):,} at a close. Nothing is measured from a close before the post, so the immediate "
        "intraday reaction is deliberately not counted: this is what a daily-bar trader could actually capture.",
        "- **Events.** Posts on a topic that share an entry point count once (`events`). `event_share` = fraction of "
        "all entry points (2 per session) that are events. Baseline = every other entry point, with an open/close "
        "dummy so overnight-vs-intraday drift doesn't leak in.",
        "- **Returns** are divided by the stock's 60-day daily vol up to the previous close (no lookahead).",
        f"- **Tests** (OLS; z = effect vs {PLACEBOS} placebos that shift the same event dates by a random 20+ "
        "sessions, so clustering of posts in volatile weeks and overlapping 5-day windows are kept in the null): `impact` = extra |1-session move| after "
        "posts (`abs_move_ratio` 1.2 = moves 20% bigger); `drift_hd` = extra mean h-session return after posts, in "
        "vol units; `extra_rev_hd` = extra slope of the h-session return on the move from the prior close to the "
        "entry price (negative = moves reverse more than usual after posts, the 'fade the post' trade).",
        f"- **Multiple testing:** Holm over all {p.size} p-values (valid under the heavy dependence between topics "
        "and tickers). `passes` lists tests with Holm-adjusted p < 0.05.",
        f"- **Data gap:** the feed returns at most 100 posts per request and has no paging; on {capped} UTC days with "
        "100+ posts (reposting sprees) only the latest 100 are kept, so a few earlier posts on those days are missing.",
        f"- Skipped, no price data: {', '.join(empty) or 'none'}. Pairs with fewer than 10 events, or tickers with "
        f"under {MIN_SESSIONS} sessions of prices (SPCX, IPO 2026-06: too short for a placebo null), dropped.\n",
        "## Results\n",
        df.round(3).to_markdown(index=False),
        "\n## Verdict\n",
    ]
    if sig.empty:
        out.append(f"No topic/ticker pair passes any test after Holm correction ({p.size} tests; smallest adjusted "
                   f"p = {df.min_p_holm.min():.2f}). Measured from the first price after the post on daily bars, "
                   "Trump's posts on these topics do not predict the size, direction or reversal of these stocks' moves.")
    else:
        out.append("Pairs passing Holm-corrected p < 0.05:\n")
        out.append(sig[["Topic", "Ticker", "events", "passes", "abs_move_ratio", "drift_1d", "drift_5d",
                        "extra_rev_1d", "extra_rev_5d", "min_p_holm"]].round(3).to_markdown(index=False))
    with open("reports/trump_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def effects(fwd, pre, is_close, ev):
    """Post-entry effects vs other entries, all with an open/close-entry dummy:
    impact = extra |fwd|, drift = extra mean fwd, extra reversal = extra slope of fwd on pre."""
    ols = lambda y, X: np.linalg.lstsq(np.column_stack([np.ones(len(y)), X]), y, rcond=None)[0][-1]
    return np.array([
        ols(np.abs(fwd), np.column_stack([is_close, ev])),
        ols(fwd, np.column_stack([is_close, ev])),
        ols(fwd, np.column_stack([is_close, ev, pre, pre * is_close, pre * ev])),
    ])


def selftest():
    s = pd.DatetimeIndex(["2025-04-04", "2025-04-07", "2025-11-28", "2025-12-01"])  # Fri, Mon, half-day Fri, Mon
    ts = pd.Series(pd.to_datetime(["2025-04-04 09:29", "2025-04-04 09:30", "2025-04-04 16:00", "2025-04-05 12:00",
                                   "2025-11-28 13:30", "2025-12-01 17:00"]))
    got = entry_points(ts, s)
    assert list(got.session.dt.strftime("%m-%d")[:5]) == ["04-04", "04-04", "04-07", "04-07", "12-01"], got
    assert list(got.kind[:5]) == ["open", "close", "open", "open", "open"], got
    assert got.session.isna().iloc[5]  # after the last session: dropped, not clamped to it


if __name__ == "__main__":
    selftest()
    main()
