"""Daily scorecard: one view of every paper sleeve, judged by the PRE-REGISTERED rules in MATH.md (Change control).

Read-only: sends no orders and changes no trading rule. "Learning" here means evidence accumulating against rules fixed
in advance, never retuning. A PASS only produces a Discord recommendation; real money is never allocated automatically.
A STOP is a recommendation too: this script does not halt any bot (the options bot already blocks entries at -10%).

Run: python scorecard.py   (prints the markdown view; posts the Discord report once per New York day)
"""
import datetime as dt
import json
import math
import os
import re
import sqlite3

import numpy as np
import pandas as pd
import yfinance as yf

import monitor
import options_earnings as oe
import track
from model import UNIVERSE

EQUITY_LOG, STOCK_STATE = monitor.EQUITY_LOG, monitor.STATE
OPT_TRADES, OPT_STATE = oe.TRADES, oe.STATE
SPORTS = "signals/sports_ledger.csv"
PM = "signals/prediction_markets.csv"
STATE = "scorecard_state.json"
FAV_DB = "betting/paper_favorites.sqlite3"  # favourites paper ledgers, written by the daily workflow; read-only here

# Pre-registered 2026-11-20, before any sleeve had data. Same text as the MATH.md table; change both or neither,
# and only at a scheduled review (a changed rule restarts that sleeve's n).
RULES = {
    "stocks": dict(name="Stock model (paper #1)", bench="frozen-model backtest over the same days (QQQ for context)",
                   min_n=250, unit="logged sessions",
                   test="TE <= 3%/yr, missed <= 5, mean fill shortfall <= 10 bp, no positions outside universe+SGOV",
                   stop="none automatic: -10%/-20% drawdown tiers are alerts; decide at the scheduled review"),
    "options": dict(name="Options iron fly (paper #2)", bench="0 (no trade)", min_n=120, unit="closed trades",
                    test="mean P&L/trade > 0 with t > 2, at the logged worst-case fills (natural - $0.05)",
                    stop="account equity -10% from peak"),
    "sports": dict(name="Sports paper bets", bench="market price (implied probability)", min_n=200,
                   unit="settled bets", test="ROI bootstrap 95% CI > 0 and ROI > 0 in both chronological halves",
                   stop="ROI < -10% after >= 100 settled bets"),
    "ipo": dict(name="Polymarket IPO brackets", bench="naive IPO price x 1.15", min_n=30, unit="resolved IPO events",
                test="bracket-implied CRPS lower than the naive baseline, paired sign test p < 0.05",
                stop="none (no money at risk)"),
    "tennis_fav": dict(name="Tennis favourites", bench="Polymarket ask + taker fee", min_n=300,
                       unit="settled heavy favs (ask 0.90-0.97, from 2026-11-20)",
                       test="mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both chronological halves",
                       stop="none (paper only)"),
    "sport_fav": dict(name="Soccer/NBA favourites", bench="Polymarket ask + taker fee", min_n=300,
                      unit="settled per group (soccer 0.80-0.95, NBA 0.85-0.97)",
                      test="per group: mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both halves",
                      stop="none (paper only)"),
    "other_fav": dict(name="Other-sports favourites (exploratory)", bench="Polymarket ask + taker fee", min_n=300,
                      unit="settled NFL/NHL/MLB favs (0.85-0.97)",
                      test="as Soccer/NBA; exploratory (no historical basis): a pass motivates a study, not money",
                      stop="none (paper only)"),
    "any_fav": dict(name="Any-category favourites", bench="Polymarket ask + taker fee", min_n=200,
                    unit="settled (0.90-0.97, 7-30 days out, objective resolution)",
                    test="mean ROI > 0, bootstrap 95% CI > 0, ROI > 0 in both chronological halves",
                    stop="none (paper only)"),
}
TE_MAX, MISSED_MAX, FILL_MAX_BP, OPT_DD_STOP, SPORTS_STOP_N, SPORTS_STOP_ROI = 0.03, 5, 10.0, -0.10, 100, -0.10


def verdict(n, min_n, passed, stop=False):
    """STOP beats everything; then nothing is judged before min_n; passed=None means no scorer yet."""
    if stop:
        return "STOP"
    if n < min_n:
        return "INSUFFICIENT_N"
    if passed is None:
        return "NOT_SCORED"
    return "PASS" if passed else "FAIL"


def max_drawdown(eq):
    eq = np.asarray(eq, float)
    return float((eq / np.maximum.accumulate(eq) - 1).min()) if len(eq) else None


def roi(pnl, stake):
    return float(np.sum(pnl) / np.sum(stake)) if np.sum(stake) > 0 else None


def bootstrap_roi(pnl, stake, b=2000, seed=0):
    """95% percentile CI of ROI = sum(pnl)/sum(stake), resampling bets i.i.d."""
    pnl, stake = np.asarray(pnl, float), np.asarray(stake, float)
    idx = np.random.default_rng(seed).integers(0, len(pnl), (b, len(pnl)))
    r = pnl[idx].sum(1) / stake[idx].sum(1)
    return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def tstat(x):
    x = np.asarray(x, float)
    sd = x.std(ddof=1) if len(x) > 1 else 0
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else None


def _json(path):
    return json.load(open(path)) if os.path.exists(path) else {}


# ---------------------------------------------------------------- sleeves
def fill_shortfall(start):
    """Mean signed bp of filled_avg_price vs that day's close (buys paying above / sells below the close = cost)."""
    orders, after = [], (start - pd.Timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    while True:
        page = monitor.alpaca("GET", "/orders", params={"status": "closed", "after": after, "limit": 500, "direction": "asc"})
        orders += [o for o in page if o.get("filled_avg_price") and o.get("filled_at")]
        if len(page) < 500:
            break
        after = page[-1]["submitted_at"]
    if not orders:
        return None, 0
    # unadjusted closes: dividend-adjusted history would shift older fills by the dividend (~10-30 bp)
    px = yf.download(sorted({o["symbol"] for o in orders}), start=(start - pd.Timedelta(days=5)).date().isoformat(),
                     auto_adjust=False, progress=False, threads=False)["Close"]
    bps = []
    for o in orders:
        day = pd.Timestamp(o["filled_at"]).tz_convert(monitor.NY).tz_localize(None).normalize()
        if day < start.normalize():  # only the frozen system's own rebalances: excludes the 2026-11-19 setup fills
            continue
        c = px[o["symbol"]].get(day) if o["symbol"] in px else None
        if c and c > 0:
            bps.append((1 if o["side"] == "buy" else -1) * (float(o["filled_avg_price"]) / c - 1) * 1e4)
    bps = [b for b in bps if abs(b) < 500]  # ponytail: drops split-day artefacts (split-adjusted close); fine for mega-caps
    return (float(np.mean(bps)) if bps else None), len(bps)


def stocks():
    log = (pd.read_csv(EQUITY_LOG, parse_dates=["date"]).set_index("date").sort_index() if os.path.exists(EQUITY_LOG)
           else pd.DataFrame(columns=["equity"]))
    missed = len(_json(STOCK_STATE).get("missed", []))
    equity = float(monitor.alpaca("GET", "/account")["equity"]) if monitor.AK else (float(log.equity.iloc[-1]) if len(log) else None)
    s = dict(n=len(log), equity=equity, missed=missed, ret=None, maxdd=None, qqq=None, model=None, te=None, fill=None,
             fills=0, stray=None)
    if len(log) and equity:
        s["ret"] = equity / float(log.equity.iloc[0]) - 1
        s["maxdd"] = max_drawdown(list(log.equity) + [equity])
    if len(log) >= 2:
        s.update({k: v for k, v in track.compare(log).items() if k in ("qqq", "model", "te")})
        if monitor.AK:
            s["fill"], s["fills"] = fill_shortfall(log.index[0])
    if monitor.AK:
        s["stray"] = sorted(p["symbol"] for p in monitor.alpaca("GET", "/positions")
                            if p["symbol"] not in UNIVERSE + [monitor.CASH_ETF])
    te = s["te"] if s["te"] is not None and not math.isnan(s["te"]) else None
    s["checks"] = {"TE": None if te is None else te <= TE_MAX, "missed": missed <= MISSED_MAX,
                   "fill": None if s["fill"] is None else s["fill"] <= FILL_MAX_BP,
                   "positions": None if s["stray"] is None else not s["stray"]}
    s["verdict"] = verdict(s["n"], RULES["stocks"]["min_n"], all(v is True for v in s["checks"].values()))
    return s


def options():
    tr = pd.read_csv(OPT_TRADES) if os.path.exists(OPT_TRADES) else pd.DataFrame(columns=["pnl"])
    pnl = tr.pnl.astype(float).to_numpy()
    st = _json(OPT_STATE)
    equity = float(oe.alpaca("GET", "/account")["equity"]) if oe.AK else None
    peak = max(st.get("peak_equity", equity), equity) if equity else None
    s = dict(n=len(pnl), equity=equity, dd=equity / peak - 1 if equity else None, open=len(st.get("spreads", {})),
             mean=float(pnl.mean()) if len(pnl) else None, t=tstat(pnl), hit=float((pnl > 0).mean()) if len(pnl) else None)
    s["verdict"] = verdict(s["n"], RULES["options"]["min_n"], bool(s["mean"] and s["mean"] > 0 and (s["t"] or 0) > 2),
                           stop=s["dd"] is not None and s["dd"] <= OPT_DD_STOP)
    return s


def _col(df, *names):
    return next((c for c in names if c in df.columns), None)


def _outcome(v):
    v = str(v).strip().lower()
    return 1.0 if v in ("1", "1.0", "true", "win", "won", "w", "yes") else 0.0 if v in ("0", "0.0", "false", "loss", "lost", "l", "no") else np.nan


def sports():
    if not os.path.exists(SPORTS):
        return dict(n=0, note="no ledger yet", verdict=verdict(0, RULES["sports"]["min_n"], None))
    # ponytail: column names guessed from sports.py's spec (built in parallel); add aliases here if it differs
    df = pd.read_csv(SPORTS)
    pnl_c, stake_c = _col(df, "pnl", "profit"), _col(df, "stake")
    pm_c = _col(df, "p_elo_home", "model_prob", "p_model", "model_p", "prob_model")
    pk_c = _col(df, "p_mkt_home", "market_prob", "p_market", "implied_prob", "market_price", "price")
    y_c = _col(df, "home_payout", "outcome", "won", "result", "y")
    stake = pd.to_numeric(df[stake_c], errors="coerce").fillna(0) if stake_c else pd.Series(0.0, index=df.index)
    pnl = pd.to_numeric(df[pnl_c], errors="coerce") if pnl_c else pd.Series(np.nan, index=df.index)
    bet = (stake > 0) & pnl.notna()
    p, k = pnl[bet].to_numpy(), stake[bet].to_numpy()
    s = dict(n=len(p), roi=roi(p, k), ci=None, halves=None, brier_model=None, brier_market=None, n_brier=0)
    if len(p) >= 2:
        s["ci"] = bootstrap_roi(p, k)
        h = len(p) // 2
        s["halves"] = (roi(p[:h], k[:h]), roi(p[h:], k[h:]))
    y = df[y_c].map(_outcome) if y_c else (pnl > 0).astype(float).where(bet & (pnl != 0))
    if pm_c and pk_c:
        mk = pd.to_numeric(df[pk_c], errors="coerce")
        mk = mk.where(mk <= 1, 1 / mk)  # decimal odds -> implied probability
        ok = y.notna() & df[pm_c].notna() & mk.notna()
        if ok.any():
            s["n_brier"] = int(ok.sum())
            s["brier_model"] = float(((df[pm_c][ok].astype(float) - y[ok]) ** 2).mean())
            s["brier_market"] = float(((mk[ok] - y[ok]) ** 2).mean())
    passed = bool(s["ci"] and s["ci"][0] > 0 and s["halves"] and all(x is not None and x > 0 for x in s["halves"]))
    s["verdict"] = verdict(s["n"], RULES["sports"]["min_n"], passed,
                           stop=s["n"] >= SPORTS_STOP_N and s["roi"] is not None and s["roi"] < SPORTS_STOP_ROI)
    return s


IPO_RE = r"\bipo\b.*\bclos|\bclos\w*\b.*\bipo\b|first[- ]day"


def ipo():
    """Day-one close bracket markets that have left the open-market snapshots (resolved, or fell out of the feed)."""
    if not os.path.exists(PM):
        return dict(n=0, markets=0, verdict=verdict(0, RULES["ipo"]["min_n"], None))
    d = pd.read_csv(PM, usecols=["ts_utc", "source", "market_id", "question"])
    latest = d.groupby("source").ts_utc.max()
    m = d[d.question.str.contains(IPO_RE, case=False, regex=True, na=False)]
    last = m.groupby("market_id").agg(ts=("ts_utc", "max"), q=("question", "first"), source=("source", "first"))
    gone = last[last.ts < last.source.map(latest)]
    # ponytail: one event = question with numbers/bracket words stripped; check by eye once a few events exist
    ev = gone.q.str.lower().str.replace(r"[\d$.,%]+[tbmk]?\b|\b(above|below|between|over|under|and|or more|less than)\b",
                                        "", regex=True).str.split().str.join(" ")
    n = ev.nunique()
    # the CRPS scorer needs frozen pre-open distributions + IPO prices; write it before n reaches min_n
    return dict(n=n, markets=len(gone), verdict=verdict(n, RULES["ipo"]["min_n"], None))


def _fav_pnl(sql, params=()):
    """Chronological pnl_per_dollar from the favourites ledger, opened read-only; [] if the file or table is missing."""
    if not os.path.exists(FAV_DB):
        return []
    conn = sqlite3.connect(f"file:{os.path.abspath(FAV_DB)}?mode=ro", uri=True)
    try:
        return [r[0] for r in conn.execute(sql, params)]
    except sqlite3.OperationalError:  # table not created yet
        return []
    finally:
        conn.close()


def fav_stats(pnl, min_n):
    """Flat-stake ledger: ROI per $1, bootstrap CI, halves; PASS needs n >= min_n, CI > 0 and both halves > 0."""
    p, k = np.asarray(pnl, float), np.ones(len(pnl))
    s = dict(n=len(p), roi=roi(p, k), ci=None, halves=None)
    if len(p) >= 2:
        s["ci"] = bootstrap_roi(p, k)
        h = len(p) // 2
        s["halves"] = (roi(p[:h], k[:h]), roi(p[h:], k[h:]))
    passed = bool(s["roi"] and s["roi"] > 0 and s["ci"] and s["ci"][0] > 0 and all(x > 0 for x in s["halves"]))
    s["verdict"] = verdict(s["n"], min_n, passed)
    return s


SETTLED = "status IN ('won','lost') ORDER BY logged_at, id"


def tennis_fav():
    return fav_stats(_fav_pnl("SELECT pnl_per_dollar FROM tennis_fav_trades WHERE entry_ask BETWEEN 0.90 AND 0.97 "
                              f"AND logged_at >= '2026-11-20' AND {SETTLED}"), RULES["tennis_fav"]["min_n"])


def sport_fav():
    g = {x: fav_stats(_fav_pnl(f"SELECT pnl_per_dollar FROM sport_fav_trades WHERE tour=? AND {SETTLED}", (x,)),
                      RULES["sport_fav"]["min_n"]) for x in ("soccer", "nba")}
    vs = [v["verdict"] for v in g.values()]
    v = "PASS" if "PASS" in vs else "FAIL" if all(x == "FAIL" for x in vs) else "INSUFFICIENT_N"
    return dict(n=max(x["n"] for x in g.values()), groups=g, verdict=v)  # n = the furthest-along group


def other_fav():
    return fav_stats(_fav_pnl(f"SELECT pnl_per_dollar FROM sport_fav_trades WHERE tour='other' AND {SETTLED}"),
                     RULES["other_fav"]["min_n"])


def any_fav():
    return fav_stats(_fav_pnl(f"SELECT pnl_per_dollar FROM any_fav_trades WHERE {SETTLED}"), RULES["any_fav"]["min_n"])


SLEEVES = {"stocks": stocks, "options": options, "sports": sports, "ipo": ipo,
           "tennis_fav": tennis_fav, "sport_fav": sport_fav, "other_fav": other_fav, "any_fav": any_fav}


def build():
    card = {"date": dt.datetime.now(monitor.NY).date().isoformat()}
    for k, f in SLEEVES.items():
        try:
            card[k] = f()
        except Exception as e:  # one dead feed must not kill the whole report; no secrets in these messages
            card[k] = dict(n=0, error=f"{type(e).__name__}: {str(e)[:80]}", verdict="ERROR")
    return card


# ---------------------------------------------------------------- rendering
def _p(x, sign=True):
    return "n/a" if x is None else f"{x:+.1%}" if sign else f"{x:.1%}"


def _ok(v):
    return "?" if v is None else "ok" if v else "FAIL"


def summary(k, s):
    if "error" in s:
        return f"error {s['error']}"
    if k == "stocks":
        c = s["checks"]
        eq = f"${s['equity']:,.0f}" if s["equity"] else "n/a"
        fill = "n/a" if s["fill"] is None else f"{s['fill']:+.1f}bp"
        return (f"{eq}, ret {_p(s['ret'])} vs QQQ {_p(s['qqq'])} (model {_p(s['model'])}), maxDD {_p(s['maxdd'])}; "
                f"TE {_p(s['te'], False)} {_ok(c['TE'])}, missed {s['missed']}/{MISSED_MAX} {_ok(c['missed'])}, "
                f"fill {fill} {_ok(c['fill'])}, positions {_ok(c['positions'])}")
    if k == "options":
        eq = f"${s['equity']:,.0f} (DD {_p(s['dd'])})" if s["equity"] else "equity n/a"
        mean = "n/a" if s["mean"] is None else f"${s['mean']:+,.0f}"
        t = "n/a" if s["t"] is None else f"{s['t']:.2f}"
        return f"{eq}, {s['open']} open; mean P&L {mean}, t {t}, hit {_p(s['hit'], False)}"
    if k == "sports":
        if "note" in s:
            return s["note"]
        ci = "n/a" if not s["ci"] else f"[{s['ci'][0]:+.1%}, {s['ci'][1]:+.1%}]"
        halves = "n/a" if not s["halves"] else "/".join(_p(x) for x in s["halves"])
        br = ("n/a" if s["brier_model"] is None else
              f"model {s['brier_model']:.3f} vs market {s['brier_market']:.3f} (n {s['n_brier']})")
        return f"ROI {_p(s['roi'])} CI {ci}, halves {halves}; Brier {br}"
    if k == "sport_fav":
        return "; ".join(f"{g} n {v['n']} {_fav_line(v)} {v['verdict']}" for g, v in s["groups"].items())
    if k in ("tennis_fav", "other_fav", "any_fav"):
        return _fav_line(s)
    return f"{s['markets']} resolved bracket markets; collecting data"


def _fav_line(s):
    if not s["n"]:
        return "no settled trades yet"
    ci = "n/a" if not s["ci"] else f"[{s['ci'][0]:+.1%}, {s['ci'][1]:+.1%}]"
    halves = "n/a" if not s["halves"] else "/".join(_p(x) for x in s["halves"])
    return f"ROI {_p(s['roi'])} CI {ci} halves {halves}"


def markdown(card):
    rows = [f"| {RULES[k]['name']} | {summary(k, card[k])} | {card[k]['n']}/{RULES[k]['min_n']} {RULES[k]['unit']} | "
            f"**{card[k]['verdict']}** |" for k in SLEEVES]
    rules = [f"| {r['name']} | {r['bench']} | {r['min_n']} {r['unit']} | {r['test']} | {r['stop']} |" for r in RULES.values()]
    return "\n".join([f"## Scorecard {card['date']}", "", "| Sleeve | Metrics | n / min | Verdict |", "|---|---|---|---|",
                      *rows, "", "| Experiment | Benchmark | Min n | Pass test | Stop |", "|---|---|---|---|---|", *rules])


STATUS = {"INSUFFICIENT_N": "too early to tell", "PASS": "✅ passed", "FAIL": "❌ failed", "STOP": "🛑 stop it",
          "NOT_SCORED": "not graded", "ERROR": "⚠️ error"}


def plain(k, s):
    """One plain-English line per experiment for Discord (the markdown report keeps the full numbers)."""
    if "error" in s:
        return "couldn't read its data today"
    if k == "stocks":
        if not s["equity"]:
            return "no account data"
        r = s["equity"] / 100_000 - 1
        return f"${s['equity']:,.0f}, {'up' if r >= 0 else 'down'} {abs(r):.1%} since the $100,000 start"
    if k == "options":
        return f"${s['equity']:,.0f}, {s['open']} trades open" if s["equity"] else "no account data"
    if k == "ipo":
        return f"{s['markets']} IPO bets finished; still collecting"
    if k == "sport_fav":
        return "; ".join(f"{g}: {_bets(v)}" for g, v in s["groups"].items())
    return _bets(s)


def _bets(s):
    if not s.get("n"):
        return s.get("note", "no finished bets yet")
    roi = s.get("roi")
    res = "result n/a" if roi is None else f"{'up' if roi >= 0 else 'down'} {abs(roi):.1%} so far"
    return f"{s['n']} finished bet{'s' * (s['n'] != 1)}, {res}"


def report(card):
    """One Discord message, <= 1900 chars."""
    lines = [f"📋 **Daily report card, {card['date']}** (all paper money, nothing real at risk)"]
    for k in SLEEVES:  # alerts first: the length cap truncates from the end
        if card[k]["verdict"] == "PASS":
            lines.append(f"✅ **{RULES[k]['name']} passed its pre-registered test.** Recommendation only: you decide "
                         f"whether to allocate real money. Nothing is allocated automatically.")
        elif card[k]["verdict"] == "STOP":
            lines.append(f"🛑 **{RULES[k]['name']} breached its loss limit** ({RULES[k]['stop']}). Recommend stopping it.")
    for k in SLEEVES:
        s = card[k]
        lines.append(f"**{RULES[k]['name']}**: {plain(k, s)}. {s['n']} of {RULES[k]['min_n']} needed "
                     f"before grading, {STATUS.get(s['verdict'], s['verdict'])}.")
    msg = "\n".join(lines)
    return msg if len(msg) <= 1900 else msg[:1897] + "..."


def main():
    card = build()
    print(markdown(card))
    st = _json(STATE)
    if st.get("last_report") == card["date"]:
        print("report already posted today")
        return
    if monitor.discord(report(card)) is True:  # True only after a successful post; no webhook -> printed, not marked
        st["last_report"] = card["date"]
        with open(STATE + ".tmp", "w") as f:
            json.dump(st, f, indent=1)
        os.replace(STATE + ".tmp", STATE)


if __name__ == "__main__":
    main()
