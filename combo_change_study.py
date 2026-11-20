"""Why did 'buy NO on every Kalshi combo at the first fill' flip negative in Oct-Nov 2026? + a leg-correlation model.
Writes reports/combo_change_results.md.  Run: python combo_change_study.py   (needs data/combo/combos.pkl from combo_study.py)
Extra cache: data/combo/leg_results.pkl (leg market results, GET /markets and /historical/markets?tickers=..., local only).

Part A (descriptive): per month, no-fee NO ROI r = (p - y)/(1 - p) splits exactly into
  pricing = (p - yhat)/(1 - p)  and  luck = (yhat - y)/(1 - p),
where yhat is a STABLE calibration model (logistic y ~ logit p + same-event + log legs) fitted once on combos filled
before 2026-08-01. Mix is separated by fixed weights: Oct-Nov within-cell ROI reweighted to the Oct 2025-Jul 2026 cell
shares (cell = category x legs bucket x same-event). Tests are day-clustered bootstraps, Holm-adjusted as one family.

Part B PRE-REGISTERED (fixed 2026-11-20 before any test-period score was computed):
  * leg types = (series, side); same-event leg pairs keyed by (typeA, typeB, relation), relation = same team / opposite
    team / n.a. (team read from the market-ticker suffix). Dependence = shrunk log-lift log(P(A&B) / P(A)P(B)) from leg
    outcomes of every same-event pair in combos filled before 2026-08-01 (pairs deduplicated), shrunk (m = 20 pseudo-
    pairs) toward the (sport, relation) pooled lift, which is shrunk toward 0.
  * model fair = clip(leg-mid product * exp(k * sum of pair log-lifts), 1e-4, 0.999); k by grid search (0..1.5) on
    log-loss of priced combos before 2026-08-01. Independent legs: plain product of leg mids.
  * test = priced combos filled 2026-08-01..2026-11-15. Scores: Brier / log-loss of model vs combo price vs leg product.
  * rule: buy NO when p - fair >= 0.04; buy YES when fair - p >= 0.04 (reported separately); fill at p, maker fee
    (0.035 q(1-q) from 2026-08-20), $1 flat; ROI with day-clustered 95% CI, by month and category.
"""
import os
import re

import numpy as np
import pandas as pd

import combo_study as C

D = C.D
TRAIN_END = pd.Timestamp("2026-08-01", tz="UTC")
EARLY = ("2025-10", "2026-07")   # reference "good" period (Sep 2025 has almost no sample)
LATE = ("2026-10", "2026-11")
EDGE, M_SHRINK = 0.04, 20.0
RES_CACHE = f"{D}/leg_results.pkl"  # local caches written only by combo_*.py, so read_pickle is safe


# Desk research 2026-11-20 (Kalshi API changelog docs.kalshi.com/changelog + press); not re-checked by the script.
PRODUCT_NOTES = [
    "## A2b. Kalshi product / fee changes Aug–Nov 2026 (docs.kalshi.com/changelog unless noted)", "",
    "- 2026-08-20: combo maker fee starts (0.5× multiplier, i.e. 0.035·q(1−q)); all-independent-NFL-leg combos exempt "
    "(KXMVECROSSCATEGORY0-SHARD1).",
    "- 2026-08-22: fee swap — a quoter executing against an order resting < 5 s pays maker fee, resting side pays taker; "
    "post-only kept, repeat crossers can be rate-limited.",
    "- 2026-09-03: finer combo ticks ($0.0001 below 1c / above 99c, $0.001 between) — makes tighter quoting possible.",
    "- 2026-09-10: `target_cost_excludes_fees` RFQ flag. 2026-09-17: new combos all on KXMVECROSSCATEGORY (football on "
    "…CROSSCATEGORY0); RFQ/quote actions count against shard-1 write budget (matches the series shift in A1(iii)).",
    "- 2026-10-01: `obscure_creator_id` (requester identity can be hidden from quoters — harder to screen sharp requesters).",
    "- 2026-10-19: cancelled crossing post-only quotes count toward quoting penalties. 2026-11-12: max 100 open RFQs per user.",
    "- Volume: record days 2026-10-10/11 (~$3.9B notional, parlays ~70%; cryptobriefing). As of 2026-11-03 parlay takers "
    "had lost ~$1.0B since Sep 2025 and makers netted ~$520M after ~$89M maker fees (cdcgaming / SCCG) — i.e. the house "
    "side was still profitable in aggregate. No source found naming new quoters entering or makers losing in Oct–Nov.", ""]


# ---------------- maths (tested in test_combo_change.py) ----------------
def logit(p):
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def fit_logistic(X, y, iters=50, ridge=1e-6):
    """Newton/IRLS logistic regression; y may be fractional. X gets an intercept column."""
    X = np.column_stack([np.ones(len(X)), X])
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-X @ b))
        W = mu * (1 - mu)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(len(b))
        step = np.linalg.solve(H, X.T @ (y - mu))
        b += step
        if np.abs(step).max() < 1e-10:
            break
    return b


def predict_logistic(b, X):
    return 1 / (1 + np.exp(-(np.column_stack([np.ones(len(X)), X]) @ b)))


def decompose(p, y, yhat):
    """No-fee NO ROI per combo and its exact split into pricing + luck."""
    p, y, yhat = map(np.asarray, (p, y, yhat))
    return (p - y) / (1 - p), (p - yhat) / (1 - p), (yhat - y) / (1 - p)


def boot_diff(a, da, b=None, db=None, B=4000, seed=0):
    """Mean of a (minus mean of b), 95% CI and two-sided p from resampling days within each group."""
    rng = np.random.default_rng(seed)

    def draws(r, d):
        r, d = np.asarray(r, float), np.asarray(d)
        u, inv = np.unique(d, return_inverse=True)
        s, n = np.bincount(inv, r), np.bincount(inv)
        idx = rng.integers(0, len(u), (B, len(u)))
        return s.sum() / n.sum(), s[idx].sum(1) / n[idx].sum(1)

    m, bs = draws(a, da)
    if b is not None:
        m2, bs2 = draws(b, db)
        m, bs = m - m2, bs - bs2
    p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
    return m, np.percentile(bs, 2.5), np.percentile(bs, 97.5), max(p, 1 / B)


def holm(ps):
    ps = np.asarray(ps, float)
    o = np.argsort(ps)
    adj, run = np.empty_like(ps), 0.0
    for i, j in enumerate(o):
        run = max(run, (len(ps) - i) * ps[j])
        adj[j] = min(1.0, run)
    return adj


def team_of(market_ticker, event_ticker):
    """'A'/'H' if the market suffix starts with the away/home team code of the game in the event ticker, else None.
    KXNFLPASSYDS-26NOV15NEDET-DETJGOFF16-175 -> game NEDET, suffix DETJGOFF16 -> 'H'."""
    parts = event_ticker.split("-")
    if len(parts) < 2 or not market_ticker.startswith(event_ticker + "-"):
        return None
    teams = re.sub(r"^\d{2}[A-Z]{3}\d{2}(\d{4})?", "", parts[1])
    suf = market_ticker[len(event_ticker) + 1:].split("-")[0]
    if len(teams) < 4:
        return None
    for L in (4, 3, 2):
        pre = suf[:L]
        if len(pre) < L or not pre.isalpha():
            continue
        a, h = teams.startswith(pre), teams.endswith(pre)
        if a != h:
            return "A" if a else "H"
    return None


def relation(la, lb):
    ta, tb = team_of(la["market_ticker"], la["event_ticker"]), team_of(lb["market_ticker"], lb["event_ticker"])
    return "na" if ta is None or tb is None else ("same" if ta == tb else "opp")


def ltype(l):
    return f"{l['event_ticker'].split('-')[0]}:{l['side']}"


def pair_key(la, lb):
    a, b = sorted([ltype(la), ltype(lb)])
    return a, b, relation(la, lb)


def game_id(l):
    s = l["event_ticker"].split("-", 1)[1] if "-" in l["event_ticker"] else l["event_ticker"]
    return s.split("-")[0]


def same_event_pairs(legs):
    by = {}
    for l in legs:
        by.setdefault(game_id(l), []).append(l)
    return [(g[i], g[j]) for g in by.values() for i in range(len(g)) for j in range(i + 1, len(g))]


def shrunk_loglift(n, sA, sB, s11, prior=0.0, m=M_SHRINK):
    """log P(A&B)/(P(A)P(B)) with P(A&B) shrunk by m pseudo-pairs toward P(A)P(B)*exp(prior)."""
    pA, pB = (sA + 1) / (n + 2), (sB + 1) / (n + 2)
    target = min(pA * pB * np.exp(prior), min(pA, pB))
    pAB = (s11 + m * target) / (n + m)
    return float(np.log(max(pAB, 1e-9) / (pA * pB)))


def lift_table(pairs):
    """pairs: DataFrame key, sport, rel, oA, oB (deduplicated). Returns (child dict, parent dict)."""
    g = pairs.assign(o11=pairs.oA * pairs.oB)
    par = {k: shrunk_loglift(len(x), x.oA.sum(), x.oB.sum(), x.o11.sum()) for k, x in g.groupby(["sport", "rel"])}
    ch = {}
    for k, x in g.groupby("key"):
        pk = (x.sport.iloc[0], x.rel.iloc[0])
        ch[k] = shrunk_loglift(len(x), x.oA.sum(), x.oB.sum(), x.o11.sum(), par.get(pk, 0.0))
    return ch, par


def combo_S(legs, ch, par):
    S = 0.0
    for la, lb in same_event_pairs(legs):
        k = pair_key(la, lb)
        S += ch.get(k, par.get((C.leg_cat(la["event_ticker"]), k[2]), 0.0))
    return S


def model_fair(prod, S, k):
    return np.clip(np.asarray(prod) * np.exp(k * np.asarray(S)), 1e-4, 0.999)


def logloss(f, y):
    f = np.clip(np.asarray(f, float), 1e-4, 1 - 1e-4)
    return -(y * np.log(f) + (1 - y) * np.log(1 - f))


def roi_yes(p, y, fee):
    return (y - p - fee) / (p + fee)


# ---------------- data ----------------
def leg_results(df):
    cache = pd.read_pickle(RES_CACHE) if os.path.exists(RES_CACHE) else {}
    tick = sorted({l["market_ticker"] for L in df.legs for l in L} - set(cache))
    print(f"leg results: {len(cache)} cached, {len(tick)} to fetch", flush=True)
    for ep in ("historical/markets", "markets"):
        todo = [t for t in tick if t not in cache]
        for i in range(0, len(todo), 80):
            try:
                ms = C.get(f"{C.KX}/{ep}", tickers=",".join(todo[i:i + 80]), limit=1000).get("markets", [])
            except Exception as e:
                print(f"  {ep} batch {i} failed: {e!s:.100}", flush=True)
                continue
            for m in ms:
                if m.get("status") in ("finalized", "settled"):
                    cache[m["ticker"]] = m.get("result")
            if i % 8000 == 0:
                pd.to_pickle(cache, RES_CACHE)
                print(f"  {ep} {i}/{len(todo)}", flush=True)
    pd.to_pickle(cache, RES_CACHE)
    return cache


def leg_out(l, res):
    r = res.get(l["market_ticker"])
    if r not in ("yes", "no"):
        return np.nan
    return float((r == "yes") == (l["side"] == "yes"))


def first_fill_split(df):
    """Trades in the first 2 s after the opening fill (several = the RFQ fill was split / several makers)."""
    w = pd.read_pickle(C.WIN_CACHE)
    out = {}
    for v in w.values():
        for r in v["rows"]:
            if r.get("settled") and r.get("trades"):
                t = [C.ts(x["created_time"]) for x in r["trades"]]
                out[r["m"]["ticker"]] = sum((x - t[0]).total_seconds() <= 2 for x in t)
    return df.ticker.map(out)


# ---------------- report helpers ----------------
def ci(m, lo, hi, s=100, u="%"):
    return f"{m * s:+.2f}{u} [{lo * s:+.2f}, {hi * s:+.2f}]"


def cat2(c):
    return c if c in ("NFL", "NBA", "MLB", "mixed", "soccer", "tennis", "NCAAF", "NCAAB", "crypto 15m") else "other"


def share_table(df, col, title, cats=None):
    t = pd.crosstab(df.mo, df[col], normalize="index")
    if cats is not None:
        t = t[[c for c in cats if c in t.columns]]
    L = [f"**{title}** (share of sampled combos by month)", "", "| month | " + " | ".join(map(str, t.columns)) + " |",
         "|---" * (len(t.columns) + 1) + "|"]
    for mo, r in t.iterrows():
        L.append(f"| {mo} | " + " | ".join(f"{v:.0%}" for v in r) + " |")
    return L + [""]


def rule_rows(g, col, label):
    if len(g) < 5:
        return f"| {label} | {len(g)} | – | – | – |"
    m, lo, hi = C.day_boot(g[col], g.day)
    return f"| {label} | {len(g)} | {g.day.nunique()} | {ci(m, lo, hi)} | {(g.y > 0).mean():.3f} |"


def main():
    df = pd.read_pickle(f"{D}/combos.pkl")
    df["mo"] = df.t0.dt.strftime("%Y-%m")
    df["c2"] = df.cat.map(cat2)
    df["coll2"] = np.where(df.series.str.contains("SPORTSMULTIGAME"), "SPORTSMULTIGAMEEXT",
                           np.where(df.series.str.startswith("KXMVECROSSCATEGORY"), "CROSSCATEGORY", "NFL/NBA single"))
    df["fee"] = df.r_maker - df.r_nofee
    df["split"] = first_fill_split(df)
    early = df.mo.between(*EARLY)
    late = df.mo.between(*LATE)
    train = df.t0 < TRAIN_END

    # ---- stable calibration model (fit once, pre-Aug) ----
    X = lambda d: np.column_stack([logit(d.p), d.same.astype(float), np.log(d.n_legs.clip(1))])
    b = fit_logistic(X(df[train]), df.y[train].to_numpy())
    df["yhat"] = predict_logistic(b, X(df))
    df["r0"], df["r_price"], df["r_luck"] = decompose(df.p, df.y, df.yhat)

    L = ["# Kalshi combos: why did 'be the house' flip in Oct–Nov 2026? And a leg-correlation model",
         f"Generated {pd.Timestamp.today():%Y-%m-%d} by `combo_change_study.py` from the `combo_study.py` sample "
         f"({len(df):,} settled combos, first fill = RFQ fill). Method and pre-registration: script docstring.", "",
         "## A1. Month-by-month decomposition of NO ROI (buy NO at first fill)", "",
         f"Stable model (fit on {train.sum():,} combos before 2026-08-01): logit E[y] = {b[0]:+.3f} {b[1]:+.3f}·logit p "
         f"{b[2]:+.3f}·same-event {b[3]:+.3f}·ln legs. No-fee ROI = pricing (p − ŷ)/(1−p) + luck (ŷ − y)/(1−p); "
         "maker ROI = no-fee + fee. Premium vs legs = p − product of leg mids (priced subset only).", "",
         "| month | n | mean p | ŷ (stable) | realised y | NO ROI maker | = pricing | + luck | + fee | "
         "luck p (y~Bern ŷ, indep.) | y vs p: p (indep.) | n priced | p − leg product (mean / median) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    rng = np.random.default_rng(1)
    sims = {}
    for mo, g in df.groupby("mo"):
        p, yh, y = g.p.to_numpy(), g.yhat.to_numpy(), g.y.to_numpy()
        obs = g.r_luck.mean()
        sim_l = ((yh - (rng.random((4000, len(g))) < yh)) / (1 - p)).mean(1)        # luck under the stable model
        sim_p = ((p - (rng.random((4000, len(g))) < p)) / (1 - p)).mean(1)         # ROI if outcomes ~ price
        pl, pp = (sim_l <= obs).mean(), (sim_p <= g.r0.mean()).mean()
        sims[mo] = (pl, pp)
        f = g.dropna(subset=["fair"])
        f = f[f.fair > 0]
        L.append(f"| {mo} | {len(g)} | {p.mean():.3f} | {yh.mean():.3f} | {y.mean():.3f} | {g.r_maker.mean() * 100:+.1f}% | "
                 f"{g.r_price.mean() * 100:+.1f}% | {obs * 100:+.1f}% | {g.fee.mean() * 100:+.2f}% | {pl:.3f} | {pp:.3f} | "
                 f"{len(f)} | {f.prem.mean() * 100:+.2f} / {f.prem.median() * 100:+.2f}pp |")
    L += ["", "'luck p' = one-sided probability of luck at least this bad if outcomes were independent Bernoulli(ŷ); "
          "'y vs p' = same for no-fee ROI if outcomes were Bernoulli(price) (price fair, no house edge). Combos on the "
          "same day share games, so these independent-draw p-values are too small; the day-clustered tests below are the "
          "ones that count.", ""]

    # ---- mix ----
    df["cell"] = df.c2 + "|" + df.lb.astype(str) + "|" + df.same.map({True: "same", False: "indep"})
    w_e = df[early].cell.value_counts(normalize=True)
    w_l = df[late].cell.value_counts(normalize=True)
    m_l = df[late].groupby("cell").r_maker.mean()
    m_e = df[early].groupby("cell").r_maker.mean()
    both = w_e.index.intersection(m_l.index)
    fixed_l = (w_e[both] * m_l[both]).sum() / w_e[both].sum()        # late within-cell ROI at early weights
    both2 = w_l.index.intersection(m_e.index)
    fixed_e = (w_l[both2] * m_e[both2]).sum() / w_l[both2].sum()      # early within-cell ROI at late weights
    act_e, act_l = df[early].r_maker.mean(), df[late].r_maker.mean()
    # same for the pricing / luck components
    comp = {}
    for col in ("r_price", "r_luck"):
        ml = df[late].groupby("cell")[col].mean()
        comp[col] = ((w_e[both] * ml[both]).sum() / w_e[both].sum(), df[late][col].mean(), df[early][col].mean())
    L += ["## A1(iii). Mix", "",
          f"Cells = category × legs bucket × same-event ({df.cell.nunique()} cells). Early = {EARLY[0]}..{EARLY[1]} "
          f"(n={early.sum()}), late = {LATE[0]}..{LATE[1]} (n={late.sum()}). Late cells absent early carry "
          f"{1 - w_l[w_l.index.intersection(w_e.index)].sum():.0%} of late combos.", "",
          "| quantity (NO ROI, maker fee) | value |", "|---|---|",
          f"| early actual | {act_e * 100:+.2f}% |", f"| late actual | {act_l * 100:+.2f}% |",
          f"| late within-cell ROI at EARLY mix (fixed weights) | {fixed_l * 100:+.2f}% |",
          f"| early within-cell ROI at LATE mix | {fixed_e * 100:+.2f}% |",
          f"| change explained by mix (late actual − late@early mix) | {(act_l - fixed_l) * 100:+.2f}pp |",
          f"| change within cells (late@early mix − early actual) | {(fixed_l - act_e) * 100:+.2f}pp |",
          f"| pricing component: early / late / late@early mix | {comp['r_price'][2] * 100:+.2f}% / "
          f"{comp['r_price'][1] * 100:+.2f}% / {comp['r_price'][0] * 100:+.2f}% |",
          f"| luck component: early / late / late@early mix | {comp['r_luck'][2] * 100:+.2f}% / "
          f"{comp['r_luck'][1] * 100:+.2f}% / {comp['r_luck'][0] * 100:+.2f}% |", ""]
    pb_lab = list(df.pb.cat.categories)
    L += share_table(df, "c2", "Category", ["NFL", "NCAAF", "NBA", "MLB", "NCAAB", "soccer", "tennis", "crypto 15m",
                                            "mixed", "other"])
    L += share_table(df, "lb", "Legs bucket", ["2", "3", "4–5", "6–8", "9–14", "15–+"])
    L += share_table(df, "pb", "First-fill YES price bucket", pb_lab)
    L += share_table(df.assign(se=df.same.map({True: "same-event", False: "independent"})), "se", "Same-event")
    L += share_table(df, "coll2", "Series")
    L += ["**Late (Oct–Nov) NO ROI (maker) by category vs early**", "",
          "| category | early n | early ROI | late n | late ROI | late YES rate | late ŷ | late luck |", "|---|---|---|---|---|---|---|---|"]
    for c in ["NFL", "NCAAF", "NBA", "MLB", "NCAAB", "soccer", "tennis", "crypto 15m", "mixed", "other"]:
        e, l = df[early & (df.c2 == c)], df[late & (df.c2 == c)]
        L.append(f"| {c} | {len(e)} | {e.r_maker.mean() * 100:+.1f}% | {len(l)} | {l.r_maker.mean() * 100:+.1f}% | "
                 f"{l.y.mean():.3f} | {l.yhat.mean():.3f} | {l.r_luck.mean() * 100:+.1f}% |")
    L.append("")
    # ---- Nov day concentration ----
    nov = df[df.mo == "2026-11"]
    dl = nov.groupby("day").agg(n=("y", "size"), ysum=("y", "sum"), yh=("yhat", "sum"), roi=("r_maker", "mean"))
    worst = dl.sort_values("roi").head(4)
    L += ["Nov 2026 worst days (NO ROI, maker): " + "; ".join(f"{d} n={r.n} hits {r.ysum:.0f} vs ŷ {r.yh:.1f} "
          f"ROI {r.roi * 100:+.0f}%" for d, r in worst.iterrows()) +
          f". Nov ex those 4 days: {nov[~nov.day.isin(worst.index)].r_maker.mean() * 100:+.2f}%.", ""]

    # ---- A2 competition ----
    L += ["## A2. Competition signals", "",
          "| month | median s creation→fill | p90 s | median fill contracts | p90 contracts | share split fill (>1 trade in 2 s) | "
          "sd of p − leg product (pp) | IQR (pp) | median p / leg product |", "|---|---|---|---|---|---|---|---|---|"]
    for mo, g in df.groupby("mo"):
        f = g.dropna(subset=["fair"])
        f = f[f.fair > 0]
        L.append(f"| {mo} | {g.lag.median():.0f} | {g.lag.quantile(.9):.0f} | {g['size'].median():.0f} | "
                 f"{g['size'].quantile(.9):.0f} | {(g.split > 1).mean():.1%} | {f.prem.std() * 100:.2f} | "
                 f"{(f.prem.quantile(.75) - f.prem.quantile(.25)) * 100:.2f} | {(f.p / f.fair).median():.3f} |")
    sl = df.assign(slow=df.lag > 120).groupby("mo")
    L += ["", "First fill > 120 s after creation (combo market reused / re-requested later), share and NO ROI maker fast vs "
          "slow: " + "; ".join(f"{mo} {g.slow.mean():.0%} ({g[~g.slow].r_maker.mean() * 100:+.1f}% / "
                               f"{g[g.slow].r_maker.mean() * 100:+.1f}%)" for mo, g in sl if g.slow.any()) + "."]
    L += ["", "Public trade prints carry no account or quoter ids, so the number of distinct counterparties is not "
          "inferable from this data. 'creation→fill' includes the requester's own confirm time, so it bounds rather "
          "than measures quoter speed.", ""]

    # ---- tests (Holm) ----
    T = []
    for mo in ("2026-10", "2026-11"):
        g = df[df.mo == mo]
        T.append((f"{mo} luck ≠ 0 (y vs stable ŷ)", *boot_diff(g.r_luck, g.day)))
    T.append(("late − early pricing component", *boot_diff(df[late].r_price, df[late].day, df[early].r_price, df[early].day)))
    fe, fl = df[early].dropna(subset=["prem"]), df[late].dropna(subset=["prem"])
    T.append(("late − early premium p − leg product", *boot_diff(fl.prem, fl.day, fe.prem, fe.day)))
    T.append(("late − early NO ROI maker", *boot_diff(df[late].r_maker, df[late].day, df[early].r_maker, df[early].day)))
    T.append(("late − early luck component", *boot_diff(df[late].r_luck, df[late].day, df[early].r_luck, df[early].day)))
    adj = holm([t[4] for t in T])
    L += ["## A1/A2 tests (day-clustered bootstrap, two-sided, Holm over these 6)", "",
          "| test | estimate [95% CI] | p | Holm p |", "|---|---|---|---|"]
    for t, a in zip(T, adj):
        s, u = (100, "pp") if "premium" in t[0] else (100, "%")
        L.append(f"| {t[0]} | {ci(t[1], t[2], t[3], s, u)} | {t[4]:.4f} | {a:.4f} |")
    L.append("")

    # ---------------- Part B ----------------
    res = leg_results(df)
    rows, seen = [], set()
    for legs in df[train].legs:
        for la, lb in same_event_pairs(legs):
            u = tuple(sorted([(la["market_ticker"], la["side"]), (lb["market_ticker"], lb["side"])]))
            if u in seen:
                continue
            seen.add(u)
            oA, oB = leg_out(la, res), leg_out(lb, res)
            if np.isnan(oA) or np.isnan(oB):
                continue
            k = pair_key(la, lb)
            if ltype(la) != k[0]:
                oA, oB = oB, oA
            rows.append(dict(key=k, sport=C.leg_cat(la["event_ticker"]), rel=k[2], oA=oA, oB=oB))
    pairs = pd.DataFrame(rows)
    ch, par = lift_table(pairs)
    df["S"] = [combo_S(l, ch, par) for l in df.legs]
    pr = df.dropna(subset=["fair"])
    pr = pr[pr.fair > 0].copy()
    tr, te = pr[pr.t0 < TRAIN_END], pr[pr.t0 >= TRAIN_END].copy()
    ks = np.round(np.arange(0, 1.51, 0.05), 2)
    ll = [logloss(model_fair(tr.fair, tr.S, k), tr.y).mean() for k in ks]
    k = float(ks[int(np.argmin(ll))])
    for d in (tr, te):
        d["model"] = model_fair(d.fair, d.S, k)
    top = pairs.assign(o11=pairs.oA * pairs.oB).groupby("key").agg(n=("oA", "size"), pA=("oA", "mean"), pB=("oB", "mean"),
                                                                    pAB=("o11", "mean"))
    top["lift"] = [np.exp(ch[i]) for i in top.index]
    top = top.sort_values("n", ascending=False).head(15)
    L += ["## B. Leg-correlation model (pre-registered; train < 2026-08-01, test 2026-08-01..11-15)", "",
          f"Training same-event leg pairs with both results known: {len(pairs):,} (deduplicated) across "
          f"{len(ch):,} type-pair keys; leg results fetched for {len(res):,} leg markets. Fitted k = {k} "
          f"(train log-loss {min(ll):.4f} vs {ll[0]:.4f} at k=0). Priced combos: train {len(tr)}, test {len(te)}.", "",
          "Most common pair keys (training): ", "", "| pair (typeA, typeB, team relation) | n | P(A) | P(B) | P(A&B) | shrunk lift |",
          "|---|---|---|---|---|---|"]
    for kk, r in top.iterrows():
        L.append(f"| {kk[0]} / {kk[1]} / {kk[2]} | {r.n} | {r.pA:.3f} | {r.pB:.3f} | {r.pAB:.3f} | {r.lift:.2f} |")
    L += ["", "**Test-period forecast scores** (lower is better; Δ vs combo price with day-clustered 95% CI)", "",
          "| subset | n | Brier price | Brier leg product | Brier model | Δ Brier model − price | log-loss price | "
          "log-loss product | log-loss model | Δ log-loss model − price |", "|---|---|---|---|---|---|---|---|---|---|"]
    for nm, g in [("all test", te), ("same-event", te[te.same]), ("independent", te[~te.same])] + \
                 [(m, g) for m, g in te.groupby("mo")]:
        br = {c: (g[c].clip(0, 1) - g.y) ** 2 for c in ("p", "fair", "model")}
        lo = {c: logloss(g[c], g.y) for c in ("p", "fair", "model")}
        db, dl_ = boot_diff(br["model"] - br["p"], g.day), boot_diff(lo["model"] - lo["p"], g.day)
        L.append(f"| {nm} | {len(g)} | {br['p'].mean():.4f} | {br['fair'].mean():.4f} | {br['model'].mean():.4f} | "
                 f"{db[0]:+.4f} [{db[1]:+.4f}, {db[2]:+.4f}] | {lo['p'].mean():.4f} | {lo['fair'].mean():.4f} | "
                 f"{lo['model'].mean():.4f} | {dl_[0]:+.4f} [{dl_[1]:+.4f}, {dl_[2]:+.4f}] |")
    L.append("")
    # rule
    te["fee_y"] = [C.maker_fee(p, t) for p, t in zip(te.p, te.t0)]
    te["r_yes"] = roi_yes(te.p, te.y, te.fee_y)
    te["r_yes_taker"] = [roi_yes(p, y, C.taker_fee_contract(p)) for p, y in zip(te.p, te.y)]
    no_, yes_ = te[te.p - te.model >= EDGE], te[te.model - te.p >= EDGE]
    tr_no = tr[tr.p - tr.model >= EDGE]
    tr_yes = tr[tr.model - tr.p >= EDGE].copy()
    tr_yes["r_yes"] = [roi_yes(p, y, C.maker_fee(p, t)) for p, y, t in zip(tr_yes.p, tr_yes.y, tr_yes.t0)]
    H = "| slice | n | days | mean ROI per $ [95% CI, day-clustered] | YES hit rate |\n|---|---|---|---|---|"
    L += [f"**Rule: buy NO when p − model ≥ {EDGE * 100:.0f}pp** (test period, maker fee)", "", H,
          rule_rows(no_, "r_maker", "TEST all (maker fee)"), rule_rows(no_, "r_taker", "TEST all (taker fee)"),
          rule_rows(no_, "r_nofee", "TEST all (no fee)")]
    L += [rule_rows(g, "r_maker", f"TEST {m}") for m, g in no_.groupby("mo")]
    L += [rule_rows(g, "r_maker", f"TEST {c}") for c, g in no_.groupby("c2")]
    L += [rule_rows(g, "r_maker", f"TEST same-event={s}") for s, g in no_.groupby("same")]
    L += [rule_rows(tr_no, "r_maker", "train (in-sample context only)"),
          rule_rows(te, "r_maker", "TEST benchmark: NO on every priced combo"), ""]
    L += [f"**Rule: buy YES when model − p ≥ {EDGE * 100:.0f}pp** (test period; as RFQ requester you would be the taker, "
          "so the taker row is the realistic one)", "", H,
          rule_rows(yes_, "r_yes", "TEST all (maker fee)"), rule_rows(yes_, "r_yes_taker", "TEST all (taker fee)")]
    L += [rule_rows(g, "r_yes", f"TEST {m}") for m, g in yes_.groupby("mo")]
    L += [rule_rows(g, "r_yes", f"TEST {c}") for c, g in yes_.groupby("c2")]
    L += [rule_rows(tr_yes, "r_yes", "train (in-sample context only)"), ""]
    # durable segments: NO ROI by category in each era (all combos), for the paper-test question
    L += ["## Durable-segment screen (NO at first fill, maker fee, all sampled combos)", "",
          "| segment | Oct25–Jul26 ROI [CI] | Aug–Sep26 ROI | Oct–Nov26 ROI [CI] | late n |", "|---|---|---|---|---|"]
    mid = df.mo.between("2026-08", "2026-09")
    segs = [(c, df.c2 == c) for c in ["NFL", "NCAAF", "NBA", "MLB", "soccer", "tennis", "mixed", "other"]] + \
           [("same-event", df.same), ("independent", ~df.same)] + \
           [(f"legs {x}", df.lb == x) for x in ["2", "3", "4–5", "6–8", "9–14", "15–+"]] + \
           [(f"price {x}", df.pb == x) for x in pb_lab]
    for nm, msk in segs:
        e, mm, l = df[early & msk], df[mid & msk], df[late & msk]
        if len(l) < 20:
            continue
        L.append(f"| {nm} | {ci(*C.day_boot(e.r_maker, e.day))} | {mm.r_maker.mean() * 100:+.2f}% | "
                 f"{ci(*C.day_boot(l.r_maker, l.day))} | {len(l)} |")
    L.append("")
    L += PRODUCT_NOTES
    with open("reports/combo_change_results.md", "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
