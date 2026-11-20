"""
Same-instant Polymarket vs de-vigged Pinnacle study (pre-registered in reports/sharp_snapshot_results.md).

Reads a COPY of betting/sports_data.sqlite3 (data/sharp_snap_copy.sqlite3, never the original), settles every
Polymarket token from Gamma (cached in data/pm_settle_cache.json), then:
  1. calibration: Brier of Pinnacle fair vs PM mid/ask at the same snapshot
  2. rule: first pre-game snapshot with pinnacle_fair - pm_ask >= 3pp (5pp), $1 held to settlement, after fees
  3. CLV: does PM move toward Pinnacle by the last pre-game snapshot
  4. soft books: same rule on DraftKings / FanDuel prices (informational)

Usage: .venv/Scripts/python.exe sharp_snapshot_study.py
"""
import json
import os
import shutil
import sqlite3

import numpy as np
import pandas as pd
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DB = os.path.join(ROOT, "betting", "sports_data.sqlite3")
DB = os.path.join(ROOT, "data", "sharp_snap_copy.sqlite3")
SETTLE_CACHE = os.path.join(ROOT, "data", "pm_settle_cache.json")
REPORT = os.path.join(ROOT, "reports", "sharp_snapshot_results.md")
UA = {"User-Agent": "quant-research-monitor"}
GAMMA = "https://gamma-api.polymarket.com/markets"
FEE_SWITCH = "2026-07-10"
B = 2000
SOCCER = ("soccer_",)
LEAGUE_NAME = {"americanfootball_nfl": "NFL", "baseball_mlb": "MLB", "basketball_wnba": "WNBA",
               "basketball_nba": "NBA", "soccer_epl": "EPL", "soccer_usa_mls": "MLS",
               "soccer_fifa_world_cup": "World Cup"}
GAME = ["snapshot_time", "league", "home_team", "away_team", "commence_time"]


# ------------------------------------------------------------------ pure helpers (tested)
def devig(df):
    """Multiplicative de-vig of bookmaker rows (one venue) -> fair per row; incomplete outcome sets dropped."""
    df = df.copy()
    need = np.where(df.league.str.startswith(SOCCER), 3, 2)
    g = df.groupby(GAME)
    df["n_out"] = g.outcome.transform("nunique")
    df["fair"] = df.price / g.price.transform("sum")
    return df[df.n_out == need].drop(columns="n_out")


def fee_rate(entry_time, late_rate=0.05, early_rate=0.03):
    return np.where(pd.Series(entry_time).astype(str).str[:10].values < FEE_SWITCH, early_rate, late_rate)


def pm_pnl(ask, settle, slip=0.0, rate=0.05):
    """$1 stake bought at ask+slip with taker fee rate*q*(1-q) per share, held to settlement (1/0)."""
    q = np.clip(np.asarray(ask, float) + slip, 1e-6, 0.999)
    return np.asarray(settle, float) / (q + rate * q * (1 - q)) - 1


def first_edge(df, thr, key="pm_token_id", edge_col="edge"):
    """First row (by snapshot_time) per key where edge >= thr."""
    hit = df[df[edge_col] >= thr - 1e-12].sort_values("snapshot_time")
    return hit.groupby(key, as_index=False).first()


def parse_gamma(payload):
    """Gamma returns a list of markets, or occasionally a dict ({'data': [...]} or an error)."""
    if isinstance(payload, dict):
        payload = payload.get("data") or []
    out = {}
    for m in payload or []:
        toks = m.get("clobTokenIds") or []
        prices = m.get("outcomePrices") or []
        toks = json.loads(toks) if isinstance(toks, str) else toks
        prices = json.loads(prices) if isinstance(prices, str) else prices
        for i, t in enumerate(toks):
            try:
                p = float(prices[i])
            except (IndexError, TypeError, ValueError):
                p = None
            settle = p if (m.get("closed") and p in (0.0, 1.0)) else None
            out[t] = {"settle": settle, "closed": bool(m.get("closed")),
                      "gameStartTime": m.get("gameStartTime"), "uma": m.get("umaResolutionStatus")}
    return out


def boot_ci(pnl, days, b=B, seed=0):
    """Mean and 95% CI from resampling whole game days."""
    pnl, days = np.asarray(pnl, float), np.asarray(days)
    if len(pnl) == 0:
        return np.nan, np.nan, np.nan
    u, inv = np.unique(days, return_inverse=True)
    s = np.bincount(inv, pnl)
    n = np.bincount(inv)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(u), (b, len(u)))
    means = s[idx].sum(1) / n[idx].sum(1)
    return pnl.mean(), np.percentile(means, 2.5), np.percentile(means, 97.5)


# ------------------------------------------------------------------ data
def load():
    if not os.path.exists(DB):
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        shutil.copy(SRC_DB, DB)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    d = pd.read_sql("SELECT * FROM price_snapshots WHERE venue IN "
                    "('polymarket','pinnacle','draftkings','fanduel') AND league != 'premier_league'", con)
    con.close()
    return d


def settle_tokens(tokens):
    cache = json.load(open(SETTLE_CACHE)) if os.path.exists(SETTLE_CACHE) else {}
    todo = [t for t in tokens if t not in cache or cache[t].get("settle") is None]
    for i in range(0, len(todo), 20):
        chunk = todo[i:i + 20]
        got = {}
        try:
            for closed in ("true", "false"):   # Gamma hides closed markets unless asked
                r = requests.get(GAMMA, params=[("clob_token_ids", t) for t in chunk]
                                 + [("closed", closed), ("limit", 100)], headers=UA, timeout=30)
                got = {**parse_gamma(r.json()), **got}
        except (requests.RequestException, ValueError) as e:
            print("gamma fail", e)
            continue
        for t in chunk:
            cache[t] = got.get(t, {"settle": None, "closed": False, "gameStartTime": None, "uma": None})
        if i % 200 == 0:
            print(f"  gamma {i}/{len(todo)}")
            json.dump(cache, open(SETTLE_CACHE, "w"))
    json.dump(cache, open(SETTLE_CACHE, "w"))
    return cache


def to_utc(s):
    return pd.to_datetime(s, utc=True, errors="coerce", format="mixed")


def build(d):
    pm = d[(d.venue == "polymarket") & d.pm_token_id.notna() & d.ask_size.notna() & d.price.between(0, 1)].copy()
    pin = devig(d[d.venue == "pinnacle"])[GAME + ["outcome", "fair"]]
    cache = settle_tokens(sorted(pm.pm_token_id.unique()))
    pm["settle"] = pm.pm_token_id.map(lambda t: cache.get(t, {}).get("settle")).astype(float)
    pm["gst"] = to_utc(pm.pm_token_id.map(lambda t: cache.get(t, {}).get("gameStartTime")))
    st, ct = to_utc(pm.snapshot_time), to_utc(pm.commence_time)
    pm["pregame"] = (st < ct) & (pm.gst.isna() | (st < pm.gst))
    # integrity (added after inspecting the as-registered bets, see report): the Odds API event must be the game the
    # token belongs to (MLB series put one PM market on two events), and the PM outcome set must be complete and not
    # sum below 0.98 (LAFC-Galaxy: H token mapped to the wrong team at 0.19 vs Pinnacle 0.65)
    need = np.where(pm.league.str.startswith(SOCCER), 3, 2)
    g = pm.groupby(GAME)
    pm["integrity"] = ((pm.gst.isna() | ((ct - pm.gst).abs() <= pd.Timedelta(hours=3)))
                       & (g.outcome.transform("nunique") == need) & (g.price.transform("sum") >= 0.98))
    pm = pm.merge(pin, on=GAME + ["outcome"], how="left")
    pm["mid"] = np.where(pm.bid.notna(), (pm.bid + pm.price) / 2, pm.price)
    pm["edge"] = pm.fair - pm.price
    pm["day"] = pm.commence_time.str[:10]
    pm["L"] = pm.league.map(LEAGUE_NAME)
    return pm, cache


# ------------------------------------------------------------------ analysis
def fmt(x, pct=True, d=1):
    return "n/a" if pd.isna(x) else (f"{x * 100:+.{d}f}%" if pct else f"{x:.{d}f}")


def calibration(panel):
    rows = []
    last = panel.sort_values("snapshot_time").groupby("pm_token_id").tail(1)
    for label, df in (("all pre-game snapshots", panel), ("last pre-game snapshot", last)):
        for lg, g in list(df.groupby("L")) + [("Pooled", df)]:
            bp = (g.fair - g.settle) ** 2
            bm = (g["mid"] - g.settle) ** 2
            ba = (g.price - g.settle) ** 2
            m, lo, hi = boot_ci(bp - bm, g.day)
            rows.append(f"| {label} | {lg} | {len(g)} | {g.pm_token_id.nunique()} | {bp.mean():.4f} | "
                        f"{bm.mean():.4f} | {ba.mean():.4f} | {m:+.4f} [{lo:+.4f}, {hi:+.4f}] |")
    return ("| Sample | League | rows | tokens | Brier Pinnacle | Brier PM mid | Brier PM ask | "
            "Pin - PM mid (95% CI) |\n|---|---|---|---|---|---|---|---|\n" + "\n".join(rows))


def rule_row(name, bets, slip=0.0, rate=None):
    r = fee_rate(bets.snapshot_time) if rate is None else rate
    pnl = pm_pnl(bets.price, bets.settle, slip, r)
    m, lo, hi = boot_ci(pnl, bets.day)
    order = np.argsort(bets.snapshot_time.values, kind="stable")
    h = len(order) // 2
    h1, h2 = pnl[order[:h]].mean() if h else np.nan, pnl[order[h:]].mean() if h else np.nan
    ok = lo > 0 and h1 > 0 and h2 > 0
    return (f"| {name} | {len(bets)} | {bets.settle.mean() * 100:.1f}% | {bets.price.mean():.3f} | "
            f"{bets.fair.mean():.3f} | {fmt(m)} | [{fmt(lo)}, {fmt(hi)}] | {fmt(h1)} / {fmt(h2)} | "
            f"{'PASS' if ok else 'fail'} |"), m


HDR = ("| Sample | bets | hit rate | mean ask | mean Pinnacle fair | ROI per $ | 95% CI (game-day) | "
       "ROI 1st / 2nd half | Verdict |\n|---|---|---|---|---|---|---|---|---|\n")


def rule_tables(panel, raw_panel):
    out, store = [], {}
    for thr in (0.03, 0.05):
        bets = first_edge(panel, thr)
        store[thr] = bets
        rows = [rule_row(f"**Pooled, s=0, r=0.05 (primary)**" if thr == 0.03 else "Pooled, s=0, r=0.05",
                         bets)[0]]
        for s in (0.01, 0.02):
            rows.append(rule_row(f"Pooled, s={s * 100:.0f}c", bets, s)[0])
        rows.append(rule_row("Pooled, r=0.03 everywhere", bets, 0, 0.03)[0])
        rows.append(rule_row("Pooled, no fee, s=0 (gross)", bets, 0, 0.0)[0])
        rows.append(rule_row("Pooled, ask depth >= 100 shares", bets[bets.ask_size >= 100])[0])
        rows.append(rule_row("Pooled, ask 0.05-0.95", bets[bets.price.between(0.05, 0.95)])[0])
        rows.append(rule_row("As registered, no integrity filter", first_edge(raw_panel, thr))[0])
        for lg, g in bets.groupby("L"):
            rows.append(rule_row(lg, g)[0])
        out.append(f"### Edge >= {thr * 100:.0f}pp\n\n" + HDR + "\n".join(rows))
    return "\n\n".join(out), store


def exploratory(panel):
    """NOT pre-registered: smaller thresholds, and the same rule with a one-snapshot-stale Pinnacle line."""
    rows = []
    for thr in (0.01, 0.02):
        bets = first_edge(panel, thr)
        rows.append(rule_row(f"Same-instant, edge >= {thr * 100:.0f}pp", bets)[0])
        rows.append(rule_row(f"Same-instant, edge >= {thr * 100:.0f}pp, gross (no fee)", bets, 0, 0.0)[0])
    p = panel.sort_values("snapshot_time").copy()
    g = p.groupby("pm_token_id")
    p["fair_stale"] = g.fair.shift(1)
    p["lag_h"] = (to_utc(p.snapshot_time) - to_utc(g.snapshot_time.shift(1))).dt.total_seconds() / 3600
    p["edge_stale"] = p.fair_stale - p.price
    st = p[p.fair_stale.notna()]
    for thr in (0.03, 0.05):
        bets = first_edge(st, thr, edge_col="edge_stale")
        rows.append(rule_row(f"STALE Pinnacle (previous snapshot), edge >= {thr * 100:.0f}pp", bets)[0])
    note = (f"Stale line = Pinnacle from the token's previous snapshot (median lag {st.lag_h.median():.1f} h). "
            f"Rows with stale edge >= 3pp: {(st.edge_stale >= .03).mean() * 100:.1f}% vs same-instant "
            f"{(st.edge >= .03).mean() * 100:.1f}% on the same rows. 'mean Pinnacle fair' column shows the "
            f"same-instant fair for every row.")
    return HDR + "\n".join(rows) + "\n\n" + note


def clv(panel, bets):
    last = panel.sort_values("snapshot_time").groupby("pm_token_id").tail(1).set_index("pm_token_id")
    b = bets.set_index("pm_token_id").join(last[["snapshot_time", "mid", "price", "fair"]].add_suffix("_c"))
    b = b[b.snapshot_time_c > b.snapshot_time]
    if b.empty:
        return "no bets with a later pre-game snapshot", b
    gap0 = b.fair - b["mid"]
    gapc = b.fair_c - b.mid_c
    lines = [
        f"- bets with a later pre-game snapshot: {len(b)} (median {((to_utc(b.snapshot_time_c) - to_utc(b.snapshot_time)).dt.total_seconds() / 3600).median():.1f} h between entry and close)",
        f"- CLV = close mid - entry ask: mean {b.mid_c.sub(b.price).mean() * 100:+.2f}c, "
        f"beat the close (close mid > entry ask) {(b.mid_c > b.price).mean() * 100:.0f}%",
        f"- PM mid move entry->close (positive = toward Pinnacle's side): {b.mid_c.sub(b['mid']).mean() * 100:+.2f}c "
        f"(moved up in {(b.mid_c > b['mid']).mean() * 100:.0f}%)",
        f"- Pinnacle fair move entry->close (positive = Pinnacle firmed on the bet): {b.fair_c.sub(b.fair).mean() * 100:+.2f}c",
        f"- Pinnacle-minus-PM-mid gap: {gap0.mean() * 100:.2f}c at entry -> {gapc.mean() * 100:.2f}c at close "
        f"(share of gap closed {1 - gapc.mean() / gap0.mean():.0%})",
        f"- Exit-at-close instead of settlement (sell at close bid ~ close mid - half spread, no fee): "
        f"mean {((b.mid_c - (b.price_c - b.mid_c)) / b.price - 1).mean() * 100:+.2f}% per $ (fee on entry ignored)",
    ]
    return "\n".join(lines), b


def soft_books(d, panel, cache):
    tok = (panel[GAME[1:] + ["outcome", "pm_token_id"]].drop_duplicates(GAME[1:] + ["outcome"]))
    pin = devig(d[d.venue == "pinnacle"])[GAME + ["outcome", "fair"]]
    rows = []
    for book in ("draftkings", "fanduel"):
        bk = d[d.venue == book][GAME + ["outcome", "price", "decimal_odds"]].merge(pin, on=GAME + ["outcome"])
        bk = bk[to_utc(bk.snapshot_time) < to_utc(bk.commence_time)].merge(tok, on=GAME[1:] + ["outcome"])
        bk["settle"] = bk.pm_token_id.map(lambda t: cache.get(t, {}).get("settle")).astype(float)
        bk = bk[bk.settle.notna()]
        bk["edge"] = bk.fair - bk.price
        bk["day"] = bk.commence_time.str[:10]
        bk["L"] = bk.league.map(LEAGUE_NAME)
        bk["key"] = bk.pm_token_id
        for thr in (0.03, 0.05):
            bets = first_edge(bk, thr, key="key")
            pnl = bets.settle * bets.decimal_odds - 1
            m, lo, hi = boot_ci(pnl, bets.day)
            rows.append(f"| {book} | {thr * 100:.0f}pp | {len(bk.key.unique())} | {len(bets)} | "
                        f"{bets.settle.mean() * 100:.1f}% | {fmt(m)} | [{fmt(lo)}, {fmt(hi)}] | "
                        + ", ".join(f"{lg} {len(g)}: {fmt((g.settle * g.decimal_odds - 1).mean())}"
                                    for lg, g in bets.groupby("L")) + " |")
        rows.append(f"| {book} | (edge distribution) | | | | | | share of rows with edge >= 3pp: "
                    f"{(bk.edge >= 0.03).mean() * 100:.2f}%, median edge {bk.edge.median() * 100:+.2f}pp |")
    return ("| Book | threshold | outcomes priced | bets | hit rate | ROI per $ | 95% CI | by league |\n"
            "|---|---|---|---|---|---|---|---|\n" + "\n".join(rows))


def main():
    d = load()
    pm, cache = build(d)
    raw = d[d.venue == "polymarket"]
    raw_panel = pm[pm.pregame & pm.fair.notna() & pm.settle.notna()].copy()
    panel = raw_panel[raw_panel.integrity].copy()
    cov = (pm.assign(has_pin=pm.fair.notna(), resolved=pm.settle.notna())
           .groupby("L").agg(rows=("pm_token_id", "size"), tokens=("pm_token_id", "nunique"),
                             pregame=("pregame", "sum"), with_pinnacle=("has_pin", "sum"),
                             resolved_tokens=("pm_token_id", lambda t: sum(cache.get(x, {}).get("settle") is not None for x in set(t)))))
    usable = panel.groupby("L").agg(rows=("pm_token_id", "size"), tokens=("pm_token_id", "nunique"),
                                     games=("pm_event_slug", "nunique"), snapshots=("snapshot_time", "nunique"))
    spread = (panel.price - panel.bid)
    edge_desc = panel.edge.describe(percentiles=[.05, .5, .95])

    calib = calibration(panel)
    rules, store = rule_tables(panel, raw_panel)
    expl = exploratory(panel)
    clv_txt, _ = clv(panel, store[0.03])
    clv5, _ = clv(panel, store[0.05])
    clv1, _ = clv(panel, first_edge(panel, 0.01))
    soft = soft_books(d, panel, cache)

    old = open(REPORT, encoding="utf-8").read()
    prereg = old.split("## Results")[0]
    verdict = "\n## Verdict" + old.split("## Verdict", 1)[1] if "## Verdict" in old else ""   # hand-written, kept
    res = f"""## Results

Generated by `sharp_snapshot_study.py`. DB copy: `data/sharp_snap_copy.sqlite3`; settlements: `data/pm_settle_cache.json`.

### Coverage

Raw Polymarket rows {len(raw)}: {raw.pm_token_id.isna().sum()} without a token id (all 4 July World Cup games, unsettleable),
{raw.ask_size.isna().sum()} indicative (no book) rows dropped. Distinct snapshot times in the table:
{d.snapshot_time.nunique()}. Gamma settled {sum(v.get('settle') is not None for v in cache.values())} of {len(cache)} tokens
(0/1 only; the rest open, voided or not found).

All Polymarket rows by league (pregame = before commence_time and Gamma gameStartTime):

{cov.to_markdown()}

Pre-game, Pinnacle complete at the same snapshot, token settled: {len(raw_panel)} rows, {raw_panel.pm_token_id.nunique()} tokens.
Integrity filter (token's Gamma start within 3 h of the Odds API commence_time; complete PM outcome set; PM asks sum
>= 0.98) removes {len(raw_panel) - len(panel)} rows. Usable panel: {len(panel)} rows, {panel.pm_token_id.nunique()}
tokens, {panel.pm_event_slug.nunique()} games, {panel.snapshot_time.nunique()} snapshots, {panel.snapshot_time.min()} to {panel.snapshot_time.max()}.

{usable.to_markdown()}

PM spread (ask - bid) on the panel: median {spread.median() * 100:.1f}c, 90th pct {spread.quantile(.9) * 100:.1f}c.
Edge (Pinnacle fair - PM ask): 5th pct {edge_desc['5%'] * 100:+.1f}pp, median {edge_desc['50%'] * 100:+.1f}pp,
95th pct {edge_desc['95%'] * 100:+.1f}pp; rows with edge >= 3pp: {(panel.edge >= .03).mean() * 100:.1f}%, >= 5pp: {(panel.edge >= .05).mean() * 100:.1f}%.

### Calibration at the same instant (Brier, lower is better; negative difference = Pinnacle more accurate)

{calib}

### Rule results (first snapshot per token with edge >= threshold, $1 at the ask, held to settlement)

{rules}

### Exploratory (not pre-registered): lower thresholds and a stale Pinnacle line

{expl}

### Closing-line value, 3pp bets

{clv_txt}

### Closing-line value, 5pp bets

{clv5}

### Closing-line value, 1pp bets (exploratory)

{clv1}

### Soft books vs Pinnacle (informational; same snapshot, $1 at the book's odds, settled with the PM result)

{soft}

Soft books limit or ban winning accounts quickly and are legal only in states where each is licensed; a positive
number here would not be scalable money.
"""
    open(REPORT, "w", encoding="utf-8").write(prereg + res + verdict)
    print(res)


if __name__ == "__main__":
    main()
