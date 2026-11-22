"""Live alt-data feeds used by monitor.py. Each function fails soft: a dead feed must never stop trading/alerts.

- Prediction markets: Polymarket + Kalshi keep little fine-grained history (~30 days at minute resolution), so we
  snapshot relevant markets every run into signals/prediction_markets.csv and build our own history for later study.
- Trump posts: trumpstruth.org RSS (free, minutes of lag). Matched to topics from trump_study.py.
"""
import csv
import datetime as dt
import json
import os
import re
import xml.etree.ElementTree as ET

import requests

from trump_study import FEED, TOPICS

PM_CSV = "signals/prediction_markets.csv"
RELEVANT = re.compile(r"tesla|spacex|musk|nvidia|apple|microsoft|google|alphabet|amazon|meta\b|largest company|"
                      r"fed\b|rate (cut|hike)|fomc|recession|tariff|china|trade deal|shutdown|s&p|nasdaq|robotaxi|"
                      r"starship|xai|ai\b|cpi|inflation|earnings|anthropic|openai|\bipo\b|initial public offering", re.I)
UA = {"User-Agent": "quant-research-monitor"}


def _get(url, **params):
    r = requests.get(url, params=params, headers=UA, timeout=20)
    r.raise_for_status()
    return r.json()


def snapshot_prediction_markets():
    """Append (time, source, id, question, yes_price, volume24h) for relevant open markets. Returns rows written."""
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    rows, errors = [], []
    try:
        for m in _get("https://gamma-api.polymarket.com/markets", closed="false", active="true", limit=500,
                      order="volume24hr", ascending="false"):
            q = m.get("question", "")
            if RELEVANT.search(q):
                yes = json.loads(m.get("outcomePrices") or "[null]")[0]
                rows.append([now, "polymarket", m.get("slug") or m.get("id"), q, yes, m.get("volume24hr")])
    except Exception as e:
        errors.append(f"polymarket: {e}")
    try:
        cursor = None
        for _ in range(5):  # up to 5,000 open markets
            d = _get("https://api.elections.kalshi.com/trade-api/v2/markets", status="open", limit=1000,
                     **({"cursor": cursor} if cursor else {}))
            for m in d.get("markets", []):
                q = f"{m.get('title', '')} {m.get('yes_sub_title', '')}".strip()
                if RELEVANT.search(q):
                    price = m.get("last_price_dollars") or (m.get("last_price") or 0) / 100
                    rows.append([now, "kalshi", m.get("ticker"), q, price, m.get("volume_24h")])
            cursor = d.get("cursor")
            if not cursor:
                break
    except Exception as e:
        errors.append(f"kalshi: {e}")
    if rows:
        os.makedirs("signals", exist_ok=True)
        new = not os.path.exists(PM_CSV)
        with open(PM_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts_utc", "source", "market_id", "question", "yes_price", "volume_24h"])
            w.writerows(rows)
    return len(rows), errors


def new_trump_posts(seen):
    """Posts not in `seen` (set of links) that match a market-moving topic: [(topics, tickers, text, link)]."""
    r = requests.get(FEED, headers=UA, timeout=20)
    r.raise_for_status()
    out = []
    for i in ET.fromstring(r.content).iter("item"):
        link, text = i.findtext("link"), i.findtext("title") or ""
        if link in seen:
            continue
        hits = [(t, tk) for t, (pat, tk) in TOPICS.items() if re.search(pat, text, re.I)]
        if hits:
            tickers = sorted({x for _, tks in hits for x in tks})
            out.append(([t for t, _ in hits], tickers, text, link))
    return out


# ---------------------------------------------------------------- Fed + meme-stock radar (added 2026-11-21)
FED_FEEDS = {"press": "https://www.federalreserve.gov/feeds/press_all.xml",
             "speech": "https://www.federalreserve.gov/feeds/speeches.xml"}
FED_PRESS = re.compile(r"FOMC|Open Market|monetary policy|federal funds|discount rate|interest rate|balance sheet|Beige Book", re.I)
FED_SPEECH = re.compile(r"monetary|economy|economic|outlook|inflation|labor|rates?\b|policy|financial stability", re.I)


def fed_relevant(kind, title):
    return bool((FED_PRESS if kind == "press" else FED_SPEECH).search(title))


def new_fed_items(seen):
    """[(kind, title, link)] for policy-relevant Fed press releases and speeches not in `seen`."""
    out = []
    for kind, url in FED_FEEDS.items():
        r = requests.get(url, headers=UA, timeout=20)
        r.raise_for_status()
        for i in ET.fromstring(r.content).iter("item"):
            title, link = (i.findtext("title") or "").strip(), i.findtext("link")
            if link not in seen and fed_relevant(kind, title):
                out.append((kind, title, link))
    return out


def surges(rows, trending, min_mentions=50, ratio=3):
    """Reddit mention spikes from ApeWisdom rows: >= min_mentions today and >= ratio x yesterday (floor 10)."""
    return [(x["ticker"], x["mentions"], x.get("mentions_24h_ago") or 0, x["rank"], x["ticker"] in trending)
            for x in rows if x["mentions"] >= min_mentions and x["mentions"] >= ratio * max(x.get("mentions_24h_ago") or 0, 10)]


def meme_surges():
    rows = _get("https://apewisdom.io/api/v1.0/filter/all-stocks/page/1")["results"]
    try:
        trending = {s["symbol"] for s in _get("https://api.stocktwits.com/api/2/trending/symbols.json")["symbols"]}
    except Exception:  # StockTwits is context only
        trending = set()
    return surges(rows, trending)
