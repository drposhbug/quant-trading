"""NFL + NBA Elo vs Polymarket game-winner markets: honest backtest + forward PAPER ledger. Never bets real money.

Run:  python sports.py backtest [--refresh]   -> reports/sports_results.md   (caches in data/sports/, gitignored)
      python sports.py daily                  -> run_daily(): appends/settles signals/sports_ledger.csv

Model (one pre-specified version per league, no tuning; FiveThirtyEight-style Elo):
  p_home = 1 / (1 + 10^(-(R_home + HFA - R_away)/400)), HFA = 0 at neutral sites.
  R += K * MOV_mult * (result - p);  K = 20 both leagues.
  NFL: HFA 48, MOV_mult = ln(|MOV|+1) * 2.2 / (0.001*dElo_w + 2.2)          (538 "How our NFL predictions work")
  NBA: HFA 100, MOV_mult = (|MOV|+3)^0.8 / (7.5 + 0.006*dElo_w)             (538 "How we calculate NBA Elo ratings")
  dElo_w = winner's pre-game Elo edge incl. home advantage (autocorrelation damping). New teams start at 1500.
  Each new season every rating is regressed 1/3 toward 1500 (538 used 1/3 for NFL, 1/4 for NBA; 1/3 both here as pre-set).
Walk-forward: all games on an ET calendar date are priced from ratings built only from games on earlier dates.

Data (free, no key): NFL results/kickoffs from nflverse games.csv (1999-); NBA from ESPN's public site API team
schedules (2014-15-), ~90 cached requests. Polymarket: gamma /markets/keyset (tag NBA 745 / NFL 450, moneyline),
slugs `{nba|nfl}-{away}-{home}-{ET date}`; CLOB prices-history (fidelity 60) for the 48h before start.

Market price = YES price of the home team at the last hourly point <= start - 2h, else the last point < start (never at or
after start). Betting rule (fixed in advance): bet 1 unit on Elo's side when |p_elo - p_mkt| > 5pp, paying
mid + COST (1.5c: half-spread + slippage, no historical book). Live ledger pays the actual best ask.
"""
import datetime as dt
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

UA = {"User-Agent": "quant-research-monitor"}
GAMMA, CLOB, ESPN = ("https://gamma-api.polymarket.com", "https://clob.polymarket.com",
                     "https://site.api.espn.com/apis/site/v2/sports/basketball/nba")
NFL_CSV = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"
DATA, LEDGER, REPORT = "data/sports", "signals/sports_ledger.csv", "reports/sports_results.md"
ELO = {"nfl": dict(k=20, hfa=48), "nba": dict(k=20, hfa=100)}
MEAN, REGRESS = 1500.0, 1 / 3
EDGE, COST, LEAD_H, LOOKAHEAD_H = 0.05, 0.015, 2, 48
TAG = {"nba": 745, "nfl": 450}
NY = "America/New_York"
NFL_NICK = dict(ARI="Cardinals", ATL="Falcons", BAL="Ravens", BUF="Bills", CAR="Panthers", CHI="Bears", CIN="Bengals",
                CLE="Browns", DAL="Cowboys", DEN="Broncos", DET="Lions", GB="Packers", HOU="Texans", IND="Colts",
                JAX="Jaguars", KC="Chiefs", LA="Rams", LAC="Chargers", LV="Raiders", MIA="Dolphins", MIN="Vikings",
                NE="Patriots", NO="Saints", NYG="Giants", NYJ="Jets", PHI="Eagles", PIT="Steelers", SEA="Seahawks",
                SF="49ers", TB="Buccaneers", TEN="Titans", WAS="Commanders", OAK="Raiders", SD="Chargers", STL="Rams")
PM_ALIAS = {"Twolves": "Timberwolves", "PHO": "Suns", "LAR": "Rams"}
LEDGER_COLS = ["logged_utc", "league", "slug", "game_start_utc", "home", "away", "p_elo_home", "p_mkt_home", "ask_home",
               "ask_away", "edge", "bet_team", "price", "stake", "settled_utc", "home_payout", "pnl"]


def get(url, **params):
    for i in range(6):
        r = requests.get(url, params=params, headers=UA, timeout=60)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(min(2 ** i, 30))
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


# ---------------- Elo ----------------
def win_prob(diff):
    return 1 / (1 + 10 ** (-diff / 400))


def mov_mult(league, mov, dw):
    if league == "nfl":
        return math.log(abs(mov) + 1) * 2.2 / (0.001 * dw + 2.2)
    return (abs(mov) + 3) ** 0.8 / (7.5 + 0.006 * dw)


def elo_update(rh, ra, hs, as_, league, neutral=False):
    """New (home, away) ratings after a final score."""
    c = ELO[league]
    diff = rh - ra + (0 if neutral else c["hfa"])
    p = win_prob(diff)
    s = 1.0 if hs > as_ else 0.0 if hs < as_ else 0.5
    dw = diff if hs > as_ else -diff if hs < as_ else 0.0
    shift = c["k"] * mov_mult(league, hs - as_, dw) * (s - p)
    return rh + shift, ra - shift


def walk_forward(games, league):
    """games: DataFrame [date, season, home, away, hs, as_, neutral] (done = hs notna). Returns (p_home Series, ratings).
    Every game on date d is priced with ratings from games on dates < d only."""
    r, season = {}, None
    p = pd.Series(np.nan, index=games.index)
    for d, g in games.sort_values("date", kind="stable").groupby("date", sort=True):
        if season is not None and g.season.iloc[0] != season:
            r = {t: MEAN + (x - MEAN) * (1 - REGRESS) for t, x in r.items()}
        season = g.season.iloc[0]
        for i, x in g.iterrows():
            p[i] = win_prob(r.get(x.home, MEAN) - r.get(x.away, MEAN) + (0 if x.neutral else ELO[league]["hfa"]))
        for _, x in g[g.hs.notna()].iterrows():
            r[x.home], r[x.away] = elo_update(r.get(x.home, MEAN), r.get(x.away, MEAN), x.hs, x.as_, league, x.neutral)
    return p, r


# ---------------- results data ----------------
def nfl_games(refresh=False):
    path = f"{DATA}/nfl_games.csv"
    if refresh or not os.path.exists(path):
        os.makedirs(DATA, exist_ok=True)
        r = requests.get(NFL_CSV, headers=UA, timeout=60)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    g = pd.read_csv(path)
    start = pd.to_datetime(g.gameday + " " + g.gametime.fillna("13:00")).dt.tz_localize(NY).dt.tz_convert("UTC")
    return pd.DataFrame(dict(date=g.gameday, season=g.season, home=g.home_team.map(NFL_NICK), away=g.away_team.map(NFL_NICK),
                             hs=g.home_score, as_=g.away_score, neutral=g.location.eq("Neutral"), start=start))


def nba_season_now(today=None):
    today = today or dt.date.today()
    return today.year + (today.month >= 8)  # ESPN labels a season by its end year


def nba_games(refresh=False):
    """ESPN team schedules (regular, post, play-in), 2014-15 to now. Past seasons cached forever; current refetched on refresh."""
    os.makedirs(DATA, exist_ok=True)
    teams = {t["team"]["id"]: t["team"]["shortDisplayName"]
             for t in get(f"{ESPN}/teams")["sports"][0]["leagues"][0]["teams"]}
    out, cur = [], nba_season_now()
    for season in range(2015, cur + 1):
        path = f"{DATA}/nba_{season}.csv"
        if os.path.exists(path) and not (refresh and season == cur):
            out.append(pd.read_csv(path))
            continue
        rows = {}
        for tid in teams:
            for st in (2, 3, 5):
                for e in get(f"{ESPN}/teams/{tid}/schedule", season=season, seasontype=st).get("events", []):
                    c = e["competitions"][0]
                    side = {k["homeAway"]: k for k in c["competitors"]}
                    sc = lambda k: (k.get("score") or {}).get("value") if isinstance(k.get("score"), dict) else k.get("score")
                    final = c["status"]["type"]["name"] == "STATUS_FINAL"
                    rows[e["id"]] = dict(id=e["id"], start=e["date"], season=season,
                                         home=teams.get(side["home"]["team"]["id"], side["home"]["team"]["shortDisplayName"]),
                                         away=teams.get(side["away"]["team"]["id"], side["away"]["team"]["shortDisplayName"]),
                                         hs=float(sc(side["home"])) if final else None,
                                         as_=float(sc(side["away"])) if final else None, neutral=bool(c.get("neutralSite")))
        df = pd.DataFrame(rows.values())
        df.to_csv(path, index=False)
        out.append(df)
    g = pd.concat(out, ignore_index=True)
    g["start"] = pd.to_datetime(g.start, utc=True)
    g["date"] = g.start.dt.tz_convert(NY).dt.strftime("%Y-%m-%d")
    return g[["date", "season", "home", "away", "hs", "as_", "neutral", "start"]]


def load_games(league, refresh=False):
    g = (nfl_games if league == "nfl" else nba_games)(refresh).dropna(subset=["home", "away"])
    g = g.sort_values("start").reset_index(drop=True)
    g["p_home"] = walk_forward(g, league)[0]
    return g


# ---------------- Polymarket ----------------
def pm_markets(league, closed):
    out, cur = [], None
    while True:
        d = get(f"{GAMMA}/markets/keyset", closed=str(closed).lower(), tag_id=TAG[league], limit=100,
                sports_market_types="moneyline", **({"after_cursor": cur} if cur else {}))
        out += d.get("markets", [])
        cur = d.get("next_cursor")
        if not cur or not d.get("markets"):
            return [m for m in out if re.fullmatch(rf"{league}-[a-z]+-[a-z]+-\d{{4}}-\d{{2}}-\d{{2}}(-moneyline)?", m["slug"])]


def match(markets, games, league):
    """[(market, game_index, home_is_outcome0)] by (team nicknames, ET date in slug). One market per game (max volume)."""
    idx = {(frozenset((h, a)), d): i for i, (h, a, d) in enumerate(zip(games.home, games.away, games.date))}
    best = {}
    for m in markets:
        teams = [PM_ALIAS.get(x.strip(), x.strip()) for x in json.loads(m["outcomes"])]
        date = re.search(r"\d{4}-\d{2}-\d{2}", m["slug"]).group()
        i = idx.get((frozenset(teams), date))
        if i is None or len(set(teams)) != 2:
            continue
        i = games.index[i]
        if i not in best or float(m.get("volumeNum") or 0) > float(best[i][0].get("volumeNum") or 0):
            best[i] = (m, i, teams[0] == games.home[i])
    return list(best.values())


def price_before(hist, start):
    """(price, t) at the last point <= start - LEAD_H (+60s: CLOB stamps hourly points at hh:00:02), else the last point
    < start; (nan, None) if none. hist: [(t_unix, p)]."""
    s = start.timestamp()
    pre = [x for x in hist if x[0] <= s - LEAD_H * 3600 + 60] or [x for x in hist if x[0] < s]
    return (pre[-1][1], pre[-1][0]) if pre else (np.nan, None)


def pm_history(tokens_starts, refresh=False):
    path = f"{DATA}/pm_prices.json"
    cache = json.load(open(path)) if os.path.exists(path) and not refresh else {}
    todo = [(t, s) for t, s in tokens_starts if t not in cache]

    def one(ts):
        t, s = ts
        b = int(s.timestamp())
        h = get(f"{CLOB}/prices-history", market=t, startTs=b - LOOKAHEAD_H * 3600, endTs=b, fidelity=60).get("history", [])
        return sorted((int(x["t"]), float(x["p"])) for x in h)
    try:
        with ThreadPoolExecutor(4) as ex:
            for (t, _), h in zip(todo, ex.map(one, todo)):
                cache[t] = h
    finally:
        json.dump(cache, open(path, "w"))
    return cache


# ---------------- scoring ----------------
def brier(p, y):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def logloss(p, y):
    p = np.clip(np.asarray(p, float), 1e-3, 1 - 1e-3)
    y = np.asarray(y, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def decide(p_elo_home, p_mkt_home, ask_home, ask_away):
    """(bet_team 'home'/'away'/'', price). Bet Elo's side when it disagrees with the market by more than EDGE."""
    e = p_elo_home - p_mkt_home
    if e > EDGE:
        return "home", ask_home
    if e < -EDGE:
        return "away", ask_away
    return "", np.nan


def bet_pnl(side, price, home_payout, stake=1.0):
    """Buy stake/price shares of `side`; each pays home_payout (home) or 1 - home_payout (away)."""
    pay = home_payout if side == "home" else 1 - home_payout
    return stake * (pay / price - 1)


def boot_roi(pnl, days, B=2000, seed=0):
    """95% CI of ROI per unit staked, resampling whole game days (bets on one day share news/injury shocks)."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(dict(p=pnl, d=days)).groupby("d").p.agg(["sum", "count"])
    s, c = df["sum"].values, df["count"].values
    k = rng.integers(0, len(df), (B, len(df)))
    roi = s[k].sum(1) / c[k].sum(1)
    return np.percentile(roi, [2.5, 97.5])


# ---------------- backtest ----------------
def build_matched(refresh=False):
    rows = []
    for lg in ("nfl", "nba"):
        games = load_games(lg, refresh)
        mpath = f"{DATA}/pm_{lg}_closed.json"
        if refresh or not os.path.exists(mpath):
            json.dump(pm_markets(lg, True), open(mpath, "w"))
        mk = json.load(open(mpath))
        pairs = [(m, i, h0) for m, i, h0 in match(mk, games, lg) if games.hs.notna()[i] and games.hs[i] != games.as_[i]]
        hist = pm_history([(json.loads(m["clobTokenIds"])[0], games.start[i]) for m, i, _ in pairs], refresh)
        print(f"{lg}: {len(mk)} closed moneyline markets, {len(pairs)} matched to decided games")
        for m, i, h0 in pairs:
            g = games.loc[i]
            p0, t = price_before(hist[json.loads(m["clobTokenIds"])[0]], g.start)
            if t is None:
                continue
            rows.append(dict(league=lg, season=g.season, date=g.date, start=g.start, slug=m["slug"], home=g.home, away=g.away,
                             y=float(g.hs > g.as_), p_elo=g.p_home, p_mkt=p0 if h0 else 1 - p0,
                             mins_before=(g.start.timestamp() - t) / 60, volume=float(m.get("volumeNum") or 0)))
    return pd.DataFrame(rows).sort_values("start").reset_index(drop=True)


def betting(df, cost=COST):
    b = df.assign(side=[decide(e, m, m + cost, 1 - m + cost)[0] for e, m in zip(df.p_elo, df.p_mkt)])
    b = b[b.side != ""].copy()
    b["price"] = np.where(b.side == "home", b.p_mkt + cost, 1 - b.p_mkt + cost)
    b["pnl"] = [bet_pnl(s, p, y) for s, p, y in zip(b.side, b.price, b.y)]
    b["win"] = b.pnl > 0
    return b


def roi_row(name, b):
    if len(b) < 2:
        return f"| {name} | {len(b)} | | | | | |"
    lo, hi = boot_roi(b.pnl.values, b.date.values)
    h = len(b) // 2
    r1, r2 = b.pnl.iloc[:h].mean(), b.pnl.iloc[h:].mean()
    ok = (lo > 0) and r1 > 0 and r2 > 0
    return (f"| {name} | {len(b)} | {b.win.mean():.1%} | {b.pnl.mean():+.1%} | [{lo:+.1%}, {hi:+.1%}] | "
            f"{r1:+.1%} / {r2:+.1%} | {'PASS' if ok else 'fail'} |")


def backtest(refresh=False):
    df = build_matched(refresh)
    df = df[df.p_mkt.between(0.0, 1.0) & df.p_elo.notna()]
    df["p_blend"] = (df.p_elo + df.p_mkt) / 2
    L = ["# NFL + NBA: Elo vs Polymarket game-winner markets",
         f"Generated by `python sports.py backtest` on {dt.date.today()}. Model and rule pre-specified in sports.py "
         "docstring (538-style Elo, no tuning). PAPER ONLY.", "",
         "## Coverage (matched, decided games with a pre-start price)", "",
         "| League | Season | n | median mins before start | median volume $ |", "|---|---|---|---|---|"]
    for (lg, s), g in df.groupby(["league", "season"]):
        L.append(f"| {lg.upper()} | {s} | {len(g)} | {g.mins_before.median():.0f} | {g.volume.median():,.0f} |")
    L += ["", "## Forecast accuracy (lower is better)", "",
          "| League | n | Brier Elo | Brier market | Brier 50/50 blend | LogLoss Elo | LogLoss market | LogLoss blend | "
          "P(Brier Elo <= market), day bootstrap |", "|---|---|---|---|---|---|---|---|---|"]
    rng = np.random.default_rng(1)
    for lg, g in [("NFL", df[df.league == "nfl"]), ("NBA", df[df.league == "nba"]), ("Pooled", df)]:
        d = ((g.p_elo - g.y) ** 2 - (g.p_mkt - g.y) ** 2).groupby(g.date).agg(["sum", "count"])
        k = rng.integers(0, len(d), (2000, len(d)))
        pb = np.mean(d["sum"].values[k].sum(1) <= 0)
        L.append(f"| {lg} | {len(g)} | {brier(g.p_elo, g.y):.4f} | {brier(g.p_mkt, g.y):.4f} | {brier(g.p_blend, g.y):.4f} | "
                 f"{logloss(g.p_elo, g.y):.4f} | {logloss(g.p_mkt, g.y):.4f} | {logloss(g.p_blend, g.y):.4f} | {pb:.3f} |")
    L += ["", "## Calibration (home-win probability, pooled)", "",
          "| Bin | n | mean p Elo | win rate (Elo bins) | n | mean p market | win rate (market bins) |",
          "|---|---|---|---|---|---|---|"]
    bins = np.linspace(0, 1, 11)
    for lo, hi in zip(bins[:-1], bins[1:]):
        e, m = df[(df.p_elo >= lo) & (df.p_elo < hi)], df[(df.p_mkt >= lo) & (df.p_mkt < hi)]
        f = lambda g, c: f"{len(g)} | {g[c].mean():.3f} | {g.y.mean():.3f}" if len(g) else "0 | | "
        L.append(f"| {lo:.1f}-{hi:.1f} | {f(e, 'p_elo')} | {f(m, 'p_mkt')} |")
    L += ["", f"## Betting rule: |p_elo - p_mkt| > {EDGE:.0%}, 1 unit on Elo's side at mid + cost", "",
          "ROI = mean P&L per 1-unit bet. CI: 2,000 bootstrap resamples of whole game days. Halves: first/second half of "
          "bets in time. Pass bar (repo standard): CI excludes 0 on the positive side and both halves positive.", "",
          "| Sample | bets | hit rate | ROI | 95% CI | ROI 1st / 2nd half | Verdict |", "|---|---|---|---|---|---|---|"]
    b = betting(df)
    for name, g in [("NFL", b[b.league == "nfl"]), ("NBA", b[b.league == "nba"]), ("**Pooled (primary)**", b)]:
        L.append(roi_row(name, g))
    for c in (0.0, 0.01, 0.02):
        L.append(roi_row(f"Pooled, cost {c * 100:.1f}c (sensitivity)", betting(df, c)))
    bb = betting(df)
    L += ["", f"Home bias: mean p_elo(home) {df.p_elo.mean():.3f}, mean market {df.p_mkt.mean():.3f}, actual home win rate "
          f"{df.y.mean():.3f}. Bets on the home side: {(bb.side == 'home').mean():.0%}.",
          "", f"Average |edge| on bets: {(bb.p_elo - bb.p_mkt).abs().mean():.1%}; share of bets on the underdog by market "
          f"price: {((bb.side == 'home') == (bb.p_mkt < 0.5)).mean():.0%}.", ""]
    verdict = roi_row("x", b).endswith("PASS |")
    L += ["## Verdict", "",
          ("The pre-specified Elo rule **passes** the repo bar on the pooled sample. Treat as a candidate only; it must "
           "repeat in the forward paper ledger before anything else." if verdict else
           "**Null result.** Plain Elo does not forecast better than Polymarket's pre-game price, and betting its "
           "disagreements does not clear the bar. The market already contains everything a results-only rating knows "
           "(and injuries, rest and lineups, which Elo does not). Most of Elo's 'edges' come from its pre-set "
           "home advantage (538's 48/100 points) being too large for today's leagues (see Home bias), so it mostly bets "
           "the home side. Re-fitting the home advantage on this sample would be tuning on the test set and is not done. "
           "Keep the forward ledger running only as a calibration record; do not bet."), "",
          "Caveats: no historical order book, so entry = hourly mid + fixed cost; the hourly point nearest start-2h can be "
          "stale in thin markets; NFL has few games per season; ties and cancelled markets dropped (NBA preseason, "
          "summer league, all-star and NFL preseason markets do not match a results row and are excluded)."]
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    df.to_csv(f"{DATA}/matched.csv", index=False)
    print("\n".join(L))
    return df


# ---------------- forward paper ledger ----------------
def read_ledger(path=LEDGER):
    if os.path.exists(path):
        return pd.read_csv(path, dtype={"bet_team": str, "settled_utc": str}, keep_default_na=False, na_values=[""])
    return pd.DataFrame(columns=LEDGER_COLS)


def log_candidates(ledger, cands, now):
    """Append one row per new market slug (decision locked at first sight, never rewritten)."""
    seen, new = set(ledger.slug), []
    for c in cands:
        if c["slug"] in seen:
            continue
        side, price = decide(c["p_elo_home"], c["p_mkt_home"], c["ask_home"], c["ask_away"])
        new.append({**c, "logged_utc": now.isoformat(timespec="seconds"), "edge": round(c["p_elo_home"] - c["p_mkt_home"], 4),
                    "bet_team": c[side] if side else "", "price": price, "stake": 1.0 if side else 0.0,
                    "settled_utc": "", "home_payout": np.nan, "pnl": np.nan})
        seen.add(c["slug"])
    return pd.concat([ledger, pd.DataFrame(new, columns=LEDGER_COLS)], ignore_index=True) if new else ledger


def settle(ledger, payouts, now):
    """payouts: slug -> resolved price of the HOME outcome (1, 0, or 0.5). Fills only unsettled rows."""
    ledger = ledger.copy()
    for i, x in ledger.iterrows():
        if (isinstance(x.settled_utc, str) and x.settled_utc) or x.slug not in payouts:
            continue
        hp = float(payouts[x.slug])
        side = "home" if x.bet_team == x.home else "away" if x.bet_team == x.away else ""
        ledger.loc[i, ["settled_utc", "home_payout", "pnl"]] = [now.isoformat(timespec="seconds"), hp,
                                                                bet_pnl(side, x.price, hp, x.stake) if side else 0.0]
    return ledger


def open_candidates(now):
    """Upcoming moneyline markets starting within LOOKAHEAD_H, with Elo and the live book (home perspective)."""
    out = []
    for lg in ("nfl", "nba"):
        games = load_games(lg, refresh=True)
        for m, i, h0 in match(pm_markets(lg, False), games, lg):
            g = games.loc[i]
            if not (now < g.start <= now + pd.Timedelta(hours=LOOKAHEAD_H)) or not m.get("acceptingOrders", True):
                continue
            bid, ask = float(m.get("bestBid") or 0), float(m.get("bestAsk") or 0)
            mid0 = (bid + ask) / 2 if 0 < bid <= ask < 1 else float(m.get("lastTradePrice") or np.nan)
            ask0 = ask if 0 < ask < 1 else mid0 + COST
            bid0 = bid if 0 < bid < 1 else mid0 - COST
            out.append(dict(league=lg, slug=m["slug"], game_start_utc=g.start.isoformat(), home=g.home, away=g.away,
                            p_elo_home=round(g.p_home, 4), p_mkt_home=mid0 if h0 else 1 - mid0,
                            ask_home=ask0 if h0 else 1 - bid0, ask_away=1 - bid0 if h0 else ask0))
    return [{k: round(v, 4) if isinstance(v, float) else v for k, v in c.items()} for c in out
            if c["p_mkt_home"] == c["p_mkt_home"]]


def home_payouts(ledger, now):
    """slug -> resolved price of the home outcome, for unsettled rows whose game started > 3h ago and has resolved."""
    due = ledger[(ledger.settled_utc.fillna("") == "") &
                 (pd.to_datetime(ledger.game_start_utc, utc=True) < now - pd.Timedelta(hours=3))]
    out = {}
    for _, x in due.iterrows():
        ms = get(f"{GAMMA}/markets", slug=x.slug)
        if ms and ms[0].get("closed") and ms[0].get("umaResolutionStatus") == "resolved":
            names = [PM_ALIAS.get(n.strip(), n.strip()) for n in json.loads(ms[0]["outcomes"])]
            out[x.slug] = float(json.loads(ms[0]["outcomePrices"])[names.index(x.home)])
    return out


def run_daily(path=LEDGER, now=None):
    """Idempotent: refresh results (Elo), log every new candidate within 48h, settle finished games. Returns ledger."""
    now = now or pd.Timestamp.now(tz="UTC")
    led = read_ledger(path)
    led = log_candidates(led, open_candidates(now), now)
    led = settle(led, home_payouts(led, now), now)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    led[LEDGER_COLS].to_csv(path, index=False)
    return led


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backtest"
    if cmd == "daily":
        led = run_daily()
        print(f"{len(led)} ledger rows; {int((led.stake > 0).sum())} paper bets; settled P&L {led.pnl.fillna(0).sum():+.2f}u")
    else:
        backtest("--refresh" in sys.argv)
