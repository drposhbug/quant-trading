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
                      r"starship|xai|ai\b|cpi|inflation|earnings", re.I)
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
