"""Pre-registered tests of the ranked retail-edge slate (reports/Market theories retail edge.md) against the frozen model.
Writes reports/retail_edge_results.md. model.py is NOT changed; nothing here trades.

Run: python retail_edge_tests.py            (downloads once to data/retail_edge.pkl)
     python retail_edge_tests.py --refresh
"""
PREREG = r"""
## Pre-registration (written 2026-11-20 before any of these tests was run; not edited after)

**Shared protocol (every test).** One change vs the frozen model (`model.py` P as of 2026-11-19). Both arms: signal at
close t, fill at close t+1 (weights shifted one session), 5 bp per side, ±1 pp per-name no-trade band (a name trades
only if |target − held| > 1% of NAV, or to exit a name whose target is 0), idle cash earns the 13-week T-bill (^IRX, the
SGOV proxy), every arm enters from cash on the same day. Windows: shipped universe and end-2014 top-10 US tech list
(universe_study.TECH10_2014), each from backtest.py's first full-signal date to the last cached close; H4 and H5 also
on the one-asset engine on ^NDX (leverage_study frame/ENG, 0.8%/yr dividend yield) from 1990-01-02. Paired stationary
bootstrap (L = 20, B = 2000, backtest.stationary_bootstrap_idx) on one pre-named metric; P = share of resamples in
which the challenger's metric is ≤ the benchmark's (for MaxDD: challenger's drawdown at least as deep).
A hypothesis's P is the **maximum** of its per-universe P's (it must win on all of them). Holm correction runs across
every hypothesis that produced a P at this review (skipped / moot / untested ones are excluded and listed). A
hypothesis ships only if Holm-adjusted P < 0.05 **and** all of its extra conditions hold. Gate failure = dead, no re-tune.

**H1 Tax-aware execution (taxable account).** Lot ledger for every arm: short-term ≤ 365 days; wash sale on any purchase
of the same ticker within 30 calendar days before or after a loss sale (incl. the model's own routine buys), disallowed
loss added to the replacement shares' basis with holding period tacked; losses net by character; $3,000/yr of net loss
offsets ordinary income (valued at 37%), rest carried forward by character. Rates (assumption: top bracket, no state):
short-term and interest 40.8%, long-term 23.8%. T-bill interest federally taxed, state-exempt (state = 0 here). Tax paid
from the account on the last session of each year (pro-rata sales if cash goes negative). Start from $100,000 cash.
Dividends are inside adjusted prices (taxed as gains, both arms alike).
Benchmark arm: frozen trades, FIFO lots. Challenger (one judged arm): (a) lot order on any sale: ST losses, LT losses,
LT gains, ST gains, highest basis first within each; (b) a per-name sale whose planned lots realise a net ST gain
trades only if the name is > 5 pp from target, other trades keep ±1 pp; (c) aggregate exposure changes (Σ target vs Σ
held differ by > 1 pp) execute the same session as a pro-rata scaling of every name; if that sale would need a gain lot
aged 335–365 days, it is deferred up to 30 sessions while total deferred ≤ 3% of NAV; (d) harvest: any lot (except
VGT) whose close is ≤ 90% of basis is sold; proceeds buy QQQ (VGT if the lot was QQQ or QQQ is quarantined); the
harvested ticker is not bought for 30 days (model buys go to the substitute); after that the substitute is swapped back
unless the swap realises a net ST gain > 0.5% of NAV. Execution decisions (bands, harvest, swap-back) use the fill-day
close, as the live monitor's band does.
Primary metric: after-tax liquidation CAGR (daily liquidation value = NAV − tax due if everything were sold at that
close; bootstrap on its daily returns). Pass: P < 0.05 on both universes; pre-tax tracking error (tax payments added
back) ≤ 2%/yr; challenger's after-tax CAGR > placebo's (protects lots aged 275–304 days instead) on both; zero-tax
control: with all rates 0, challenger ΔCAGR ≤ 0.5 × its taxed ΔCAGR on both (the gain must come from tax).
Not run: user's actual bracket (unknown) and the seeded-lots secondary.

**H2 Muni idle cash.** Every dollar the frozen model leaves in cash is held in SUB instead of T-bills (BIL, the SGOV
proxy over the whole window; SGOV starts 2020). Third arm: SHY (1–3y Treasury) as the duration control. Actual price and
distribution histories (unadjusted close + dividends), no extra fee deduction. Taxes applied daily: BIL/SHY distributions
40.8% federal, state-exempt; SUB distributions federal-exempt, state-taxable; cash-sleeve price changes taxed as ST
gains/losses (40.8% + state). Equity sleeve identical in all arms and left pre-tax. Judged at state tax 0%; 5% reported.
Metric: after-tax CAGR. Pass: P(SUB ≤ BIL) < 0.05 on both universes and SUB's after-tax CAGR > SHY arm's on both.

**H3 Month-end 60/40 rebalancing timing.** From each month-end close, w = 0.6·G_SPY / (0.6·G_SPY + 0.4·G_IEF), d = w − 0.6.
z = d at the 5th-to-last trading day (T−5) / std of the same-day d over the prior 36 months. Signal days T−5, T−4, T−3
(fills T−4, T−3, T−2; restored at T−1): z ≥ +1 → target × 0.8; z ≤ −1 → target × min(1.2, 1/Σtarget). Months at the
data's ragged end are skipped. Metric Sharpe. Extra: ΔSharpe > 0 on 2023-03-01 onward on both universes.

**H4 ±2% band on the QQQ 200-day halving.** Halve when QQQ closes < 0.98 × SMA200, restore when > 1.02 × SMA200, keep
the prior state in between. Metric Sharpe on shipped, end-2014 and ^NDX 1990–2026. After-tax CAGR under the H1 ledger
(FIFO, both arms) reported, not judged.

**H5 Faster re-entry after VIX ≥ 40.** ^VIX (yfinance; same series as VIXCLS). Episode start: first close where the
max VIX over the prior 63 sessions (incl. today) is ≥ 40 and today's VIX ≤ 0.6 × that max, with no episode in the prior
126 sessions. From that signal close, the 200-day halving is off for 126 sessions or until QQQ closes above its SMA200
(whichever first). Power rule: ≥ 6 episodes on ^NDX 1990–2026, else UNTESTED. Metric Sharpe on ^NDX and both
universes; extra: MaxDD no more than 3 pp worse than the benchmark on each. Per-episode table. Secondary (not judged):
Grok's rule, exposure = full basket (no vol target, no halving) while VIX ≤ 22 and its 126-session max ≥ 35.

**H6 Semiconductor-cluster cap.** Semis (GICS semis + equipment): shipped NVDA AVGO TSM AMD; end-2014 INTC QCOM.
Their share of the capped equity sleeve ≤ 40%, excess to the other names pro rata, caps re-applied (excess to cash),
then vol target and halving unchanged. Binding frequency measured first: if it binds on < 10% of window days on either
universe, H6 is MOOT (excluded from Holm). Metric MaxDD (P = P(challenger DD at least as deep)); extra: Sharpe point
estimate ≥ benchmark − 0.05. 2022 and Nov-2026 drawdowns reported. The 2000–02 end-1998 list is NOT run: free data lacks
delisted names (Lucent, Nortel, ...), so any run would be survivor-biased.

**H9 52-week-high tilt.** First trading day of each month: PTH = close / max close over 252 sessions; eligible names
ranked, base inverse-vol weight × (0.5 → 1.5 linear in rank, highest PTH = 1.5), held for the month; caps, vol target,
halving unchanged. Metric Sharpe.

**H11 Lazy Prices.** Skipped: SEC EDGAR's fair-access policy requires a User-Agent with contact details (a probe with a
generic UA got HTTP 403 "Undeclared Automated Tool"), which this task may not send.

**H12 4-week net liquidity (expected to fail).** NL = WALCL − WTREGEN − RRPONTSYD (FRED, $bn, Wednesday values), usable
from the Friday close after Thursday's release. When NL's 4-week change ≤ 0, target × 0.5 (stacks with the halving).
Metric Sharpe. Extra: the 13-week version's ΔSharpe has the same sign on both universes.

Skipped (per task): ranks 7, 8, 10, 13, 14.
"""
import math
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
import yfinance as yf

from backtest import prices, sharpe_rows, stationary_bootstrap_idx
from leverage_study import ENG, frame, load as load_lev, rf_daily
from model import BENCH, EVENT_CAPS, P, names_of, scores, target_weights
from universe_study import TECH10_2014

CACHE = "data/retail_edge.pkl"
OUT = "reports/retail_edge_results.md"
BAND, COST, B = 0.01, 5.0, 2000
NDX_DY = 0.008
RATES = dict(st=0.408, lt=0.238, ded=0.37)
ZERO = dict(st=0.0, lt=0.0, ded=0.0)
SEMIS = {"ship": ["NVDA", "AVGO", "TSM", "AMD"], "e2014": ["INTC", "QCOM"]}


# ---------------------------------------------------------------- data
def load():
    # pickle is our own cache written below from yfinance/FRED
    if os.path.exists(CACHE) and "--refresh" not in sys.argv:
        return pd.read_pickle(CACHE)
    ex = yf.download(["INTC", "CSCO", "IBM", "QCOM", "^IRX", "VGT", "SPY", "IEF", "^VIX"], start="1990-01-01",
                     auto_adjust=True, progress=False, threads=False)["Close"]
    funds = {}
    for t in ("SUB", "BIL", "SHY"):
        h = yf.Ticker(t).history(start="2007-01-01", auto_adjust=False)[["Close", "Dividends"]]
        h.index = h.index.tz_localize(None).normalize()
        funds[t] = h
    fred = {s: pd.to_numeric(pd.read_csv(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={s}",
                                         index_col=0, parse_dates=True).iloc[:, 0], errors="coerce")
            for s in ("WALCL", "WTREGEN", "RRPONTSYD")}
    d = dict(ex=ex, funds=funds, fred=fred)
    os.makedirs("data", exist_ok=True)
    pd.to_pickle(d, CACHE)
    return d


# ---------------------------------------------------------------- weights (frozen engine, decomposed)
def gate_frozen(px, p=P):
    q = px[BENCH].ffill()
    return pd.Series(np.where(q < q.rolling(p["regime_ma"]).mean(), p["regime_scale"], 1.0), index=px.index)


def gate_hyst(px, band=0.02, p=P):
    q = px[BENCH].ffill().values
    ma = pd.Series(q).rolling(p["regime_ma"]).mean().values
    off, g = False, np.ones(len(q))
    for t in range(len(q)):
        if not np.isnan(ma[t]):
            if not off and q[t] < (1 - band) * ma[t]:
                off = True
            elif off and q[t] > (1 + band) * ma[t]:
                off = False
        g[t] = p["regime_scale"] if off else 1.0
    return pd.Series(g, index=px.index)


def weights(px, p=P, mult=None, semis=None):
    """model.target_weights without the regime gate, with two optional single changes: a per-name multiplier on the
    inverse-vol base weights (H9) and a cluster cap (H6). Returns (vol-targeted weights, cluster-cap-binding flag)."""
    px = px.ffill()
    names = names_of(px)
    s = np.log(px).diff()[names]
    vol_a = s.rolling(p["vol_win"]).std() * np.sqrt(252)
    sc = scores(px, p)
    n = len(names)
    cov = (s.fillna(0).rolling(p["vol_win"]).cov() * 252).values.reshape(len(s), n, n)
    base = sc.notna().astype(float) / vol_a
    if mult is not None:
        base = base * mult.reindex(index=base.index, columns=names).fillna(1.0)
    caps = pd.Series({c: EVENT_CAPS.get(c, p["cap"]) for c in names})
    w = base.div(base.sum(axis=1), axis=0).fillna(0).clip(upper=caps, axis=1)
    bind = pd.Series(False, index=w.index)
    if semis:
        non = [c for c in names if c not in semis]
        S, N = w[semis].sum(axis=1), w[non].sum(axis=1)
        tot = S + N
        bind = S > 0.4 * tot + 1e-12
        excess = (S - 0.4 * tot).clip(lower=0).where(bind, 0)
        w[semis] = w[semis].mul(np.where(bind, 0.4 * tot / S.where(S > 0, 1), 1.0), axis=0)
        w[non] = w[non].mul(1 + excess / N.where(N > 0, np.inf), axis=0)
        w = w.clip(upper=caps, axis=1)
    W = w.values
    pv = np.sqrt(np.clip(np.einsum("ti,tij,tj->t", W, np.nan_to_num(cov), W), 0, None))
    scale = np.where(pv > 0, np.minimum(1.0, p["vol_target"] / np.where(pv > 0, pv, 1)), 1.0)
    return w.mul(scale, axis=0), bind


# ---------------------------------------------------------------- pre-tax simulator with the ±1 pp band
def sim(px, W, rf, band=BAND, cost=COST, dy=0.0):
    """W = weights held from close t (already lagged). Daily net returns incl. T-bill on idle cash, and the
    pre-trade exposure each day. band=0, rf=0 reproduces model.backtest_returns exactly."""
    names = names_of(px)
    pf = px.ffill()
    r = (pf[names] / pf[names].shift(1) - 1).fillna(0).values
    Wv = W.reindex(index=px.index, columns=names).fillna(0).values
    rfv = rf.reindex(px.index).fillna(0).values
    h = np.zeros(len(names))
    out, ex = np.zeros(len(px)), np.zeros(len(px))
    for t in range(len(px)):
        ex[t] = h.sum()
        port = h @ r[t] + (1 - ex[t]) * rfv[t] + ex[t] * dy / 252
        h = h * (1 + r[t]) / (1 + port)
        tgt = Wv[t]
        trade = (np.abs(tgt - h) > band) | ((tgt == 0) & (h > 0))
        new = np.where(trade, tgt, h)
        out[t] = port - np.abs(new - h).sum() * cost / 1e4
        h = new
    return pd.Series(out, index=px.index), pd.Series(ex, index=px.index)


def lagged(w, start):
    w = w.shift(1).fillna(0)
    w.loc[w.index < start] = 0.0
    return w


# ---------------------------------------------------------------- tax ledger
def tax_due(st, lt, intr, cf_st, cf_lt, r):
    """Annual tax (negative = refund against other income) and new carryforwards (positive loss amounts)."""
    s, l = st - cf_st, lt - cf_lt
    base = intr * r["st"]
    if s >= 0 and l >= 0:
        return base + s * r["st"] + l * r["lt"], 0.0, 0.0
    if s < 0 and l < 0:
        ds = min(3000.0, -s)
        dl = min(3000.0 - ds, -l)
        return base - (ds + dl) * r["ded"], -s - ds, -l - dl
    n = s + l
    if n >= 0:
        return base + n * (r["lt"] if s < 0 else r["st"]), 0.0, 0.0
    d = min(3000.0, -n)
    return base - d * r["ded"], (-n - d if s < 0 else 0.0), (-n - d if l < 0 else 0.0)


class Ledger:
    """Lots: [ticker, shares, basis/share (incl. cost), hold-date (tacked), buy-date, shares still usable as wash
    replacement]. Days are calendar ordinals. Pools are model names; a pool may hold substitute tickers (QQQ/VGT)."""

    def __init__(self, cash, rates, cost=COST / 1e4):
        self.cash, self.r, self.c = cash, rates, cost
        self.lots = defaultdict(list)
        self.pend = []  # loss sales still open to a later purchase: [tic, shares, loss/share, sale day, held days, char]
        self.real = {"st": 0.0, "lt": 0.0}
        self.cf = {"st": 0.0, "lt": 0.0}
        self.intr = 0.0
        self.px = {}

    def value(self, pool):
        return sum(l[1] * self.px[l[0]] for l in self.lots[pool])

    def nav(self):
        return self.cash + sum(self.value(p) for p in self.lots)

    def gain_ps(self, lot):
        return self.px[lot[0]] * (1 - self.c) - lot[2]

    @staticmethod
    def char(lot, day):
        return "st" if day - lot[3] <= 365 else "lt"

    def buy(self, pool, tic, dollars, day):
        if dollars <= 1e-9:
            return
        self.cash -= dollars
        p = self.px[tic] * (1 + self.c)
        sh = dollars / p
        self.pend = [x for x in self.pend if day - x[3] <= 30 and x[1] > 1e-12]
        for x in self.pend:  # purchase within 30 days AFTER a loss sale: disallow, move loss into basis, tack period
            if x[0] != tic or sh <= 1e-12:
                continue
            m = min(sh, x[1])
            x[1] -= m
            sh -= m
            self.real[x[5]] += m * x[2]
            self.lots[pool].append([tic, m, p + x[2], day - x[4], day, 0.0])
        if sh > 1e-12:
            self.lots[pool].append([tic, sh, p, day, day, sh])

    def sell(self, picks, day):
        """picks: [(lot, shares)]. Lots in this sale are never their own wash replacement."""
        selling = {id(l) for l, _ in picks}
        for lot, sh in picks:
            if sh <= 1e-12:
                continue
            g = sh * self.gain_ps(lot)
            ch, held = self.char(lot, day), day - lot[3]
            self.cash += sh * self.px[lot[0]] * (1 - self.c)
            lot[1] -= sh
            lot[5] = min(lot[5], lot[1])
            if g >= 0:
                self.real[ch] += g
                continue
            lps, rem = -g / sh, sh
            for pl in self.lots.values():  # purchases within 30 days BEFORE the sale
                for c in list(pl):
                    if rem <= 1e-12:
                        break
                    if c[0] != lot[0] or id(c) in selling or c[5] <= 1e-12 or not (day - 30 <= c[4] <= day):
                        continue
                    m = min(rem, c[5])
                    c[1] -= m
                    c[5] -= m
                    pl.append([c[0], m, c[2] + lps, c[3] - held, c[4], 0.0])
                    rem -= m
            self.real[ch] -= lps * rem
            if rem > 1e-12:
                self.pend.append([lot[0], rem, lps, day, held, ch])
        for k in self.lots:
            self.lots[k] = [l for l in self.lots[k] if l[1] > 1e-10]

    def order(self, pool, how, day):
        lots = self.lots[pool]
        if how == "fifo":
            return sorted(lots, key=lambda l: l[4])
        cat = lambda l: (0 if self.char(l, day) == "st" else 1) if self.gain_ps(l) < 0 else \
            (2 if self.char(l, day) == "lt" else 3)
        return sorted(lots, key=lambda l: (cat(l), -l[2]))

    def pick(self, pool, dollars, how, day, skip=()):
        picks, rem = [], dollars
        for l in self.order(pool, how, day):
            if rem <= 1e-9:
                break
            if id(l) in skip:
                continue
            p = self.px[l[0]]
            take = min(l[1], rem / p)
            picks.append((l, take))
            rem -= take * p
        return picks, max(rem, 0.0)

    def st_gain(self, picks, day):
        return sum(sh * self.gain_ps(l) for l, sh in picks if self.char(l, day) == "st")

    def liq_value(self, day):
        un = {"st": 0.0, "lt": 0.0}
        mv = 0.0
        for pl in self.lots.values():
            for l in pl:
                v = l[1] * self.px[l[0]] * (1 - self.c)
                mv += v
                un[self.char(l, day)] += v - l[1] * l[2]
        tax = tax_due(self.real["st"] + un["st"], self.real["lt"] + un["lt"], self.intr,
                      self.cf["st"], self.cf["lt"], self.r)[0]
        return self.cash + mv - tax

    def pay_tax(self):
        tax, self.cf["st"], self.cf["lt"] = tax_due(self.real["st"], self.real["lt"], self.intr,
                                                    self.cf["st"], self.cf["lt"], self.r)
        self.cash -= tax
        self.real = {"st": 0.0, "lt": 0.0}
        self.intr = 0.0
        return tax


def run_ledger(px, W, rf, start, arm="bench", rates=RATES, protect=(335, 365), sub_px=None):
    """arm: 'bench' (frozen trades, FIFO) or 'ch' (H1 challenger). Returns DataFrame of liquidation value, pre-tax
    NAV return, tax paid, and a stats dict."""
    names = names_of(px)
    pf = px.ffill()
    if sub_px is not None:
        pf = pd.concat([pf, sub_px.reindex(pf.index).ffill()], axis=1)
    dates = px.index[px.index >= start]
    Wv = W.reindex(index=dates, columns=names).fillna(0)
    rfv = rf.reindex(dates).fillna(0).values
    L = Ledger(1e5, rates)
    how = "fifo" if arm == "bench" else "tax"
    quar, defer0, swap_ok = {}, {}, {}
    rec = []
    n_harv = n_defer = 0
    years = dates.year
    prev_nav = 1e5
    for t, d in enumerate(dates):
        day = d.toordinal()
        row = pf.loc[d]
        L.px = {k: v for k, v in row.items() if not pd.isna(v)}
        if t:
            i = L.cash * rfv[t]
            L.cash += i
            L.intr += i
        nav = L.nav()
        tgt = Wv.loc[d]
        if arm == "ch":
            blocked = lambda tic: quar.get(tic, -1) >= day
            sub_for = lambda tic: next((s for s in ("QQQ", "VGT") if s != tic and not blocked(s)), None)
            # (d) harvest
            picks = [(l, l[1]) for pl in L.lots.values() for l in pl
                     if l[0] != "VGT" and L.px[l[0]] <= 0.9 * l[2]]
            if picks:
                by_pool = defaultdict(float)
                for pool, pl in L.lots.items():
                    ids = {id(l) for l in pl}
                    by_pool[pool] += sum(sh * L.px[l[0]] * (1 - L.c) for l, sh in picks if id(l) in ids)
                tics = {l[0] for l, _ in picks}
                L.sell(picks, day)
                n_harv += len(picks)
                for tic in tics:
                    quar[tic] = day + 30
                for pool, val in by_pool.items():
                    if val > 0 and (s := sub_for(pool)) is not None:
                        L.buy(pool, s, min(val, max(L.cash, 0)), day)
            # swap-back
            for pool in names:
                subs = [l for l in L.lots[pool] if l[0] != pool]
                if subs and not blocked(pool) and L.st_gain([(l, l[1]) for l in subs], day) <= 0.005 * nav:
                    c0 = L.cash
                    L.sell([(l, l[1]) for l in subs], day)
                    L.buy(pool, pool, L.cash - c0, day)
            buy_tic = lambda pool: pool if not blocked(pool) else sub_for(pool)
            # (c) aggregate exposure change
            H = {p_: L.value(p_) for p_ in names}
            Et, Ec = tgt.sum(), sum(H.values()) / nav
            if Ec > 0 and abs(Et - Ec) > BAND:
                f = Et / Ec
                if f < 1:
                    deferred = 0.0
                    for pool in names:
                        need = H[pool] * (1 - f)
                        if need <= 0:
                            continue
                        prot = {id(l) for l in L.lots[pool] if L.gain_ps(l) > 0
                                and protect[0] <= day - l[3] <= protect[1]}
                        picks, short = L.pick(pool, need, how, day, skip=prot)
                        if short > 1e-6 and prot and (defer0.get(pool) is None or t - defer0[pool] <= 30) \
                                and deferred + short <= 0.03 * nav:
                            defer0.setdefault(pool, t)
                            deferred += short
                            n_defer += 1
                        else:
                            defer0[pool] = None
                            picks, _ = L.pick(pool, need, how, day)
                        L.sell(picks, day)
                else:
                    amt = {p_: H[p_] * (f - 1) for p_ in names}
                    k = min(1.0, max(L.cash, 0) / max(sum(amt.values()), 1e-9))
                    for pool, a in amt.items():
                        if (s := buy_tic(pool)) is not None:
                            L.buy(pool, s, a * k, day)
            # (b) relative trades
            H = {p_: L.value(p_) for p_ in names}
            buys = {}
            for pool in names:
                dlt = tgt[pool] * nav - H[pool]
                if dlt < 0 and H[pool] > 0:
                    if tgt[pool] == 0:
                        L.sell([(l, l[1]) for l in L.lots[pool]], day)
                        continue
                    picks, _ = L.pick(pool, -dlt, how, day)
                    thr = 0.05 if L.st_gain(picks, day) > 0 else BAND
                    if -dlt > thr * nav:
                        L.sell(picks, day)
                elif dlt > BAND * nav:
                    buys[pool] = dlt
            k = min(1.0, max(L.cash, 0) / max(sum(buys.values()), 1e-9))
            for pool, a in buys.items():
                if (s := buy_tic(pool)) is not None:
                    L.buy(pool, s, a * k, day)
        else:
            H = {p_: L.value(p_) for p_ in names}
            buys = {}
            for pool in names:
                dlt = tgt[pool] * nav - H[pool]
                if H[pool] > 0 and tgt[pool] == 0:
                    L.sell([(l, l[1]) for l in L.lots[pool]], day)
                elif dlt < -BAND * nav:
                    L.sell(L.pick(pool, -dlt, how, day)[0], day)
                elif dlt > BAND * nav:
                    buys[pool] = dlt
            k = min(1.0, max(L.cash, 0) / max(sum(buys.values()), 1e-9))
            for pool, a in buys.items():
                L.buy(pool, pool, a * k, day)
        tax = 0.0
        if t < len(dates) - 1 and years[t + 1] != years[t]:
            tax = L.pay_tax()
            if L.cash < 0:
                H = {p_: L.value(p_) for p_ in L.lots}
                tot = sum(H.values())
                need = -L.cash / (1 - L.c)
                for pool, v in H.items():
                    if v > 0:
                        L.sell(L.pick(pool, need * v / tot, how, day)[0], day)
        nav_end = L.nav()
        rec.append((L.liq_value(day), (nav_end + tax) / prev_nav - 1, tax))
        prev_nav = nav_end
    df = pd.DataFrame(rec, index=dates, columns=["liq", "pre", "tax"])
    return df, dict(harvested_lots=n_harv, deferrals=n_defer, lots_end=sum(len(v) for v in L.lots.values()))


# ---------------------------------------------------------------- stats + bootstrap
def cagr(r):
    r = np.asarray(r)
    return float(np.exp(np.log1p(r).sum() * 252 / len(r)) - 1)


def maxdd(r):
    eq = np.cumprod(1 + np.asarray(r))
    return float((eq / np.maximum.accumulate(eq) - 1).min())


def summary(r):
    r = np.asarray(r)
    return dict(CAGR=cagr(r), Sharpe=float(r.mean() / r.std() * math.sqrt(252)), MaxDD=maxdd(r))


def _rows_cagr(x):
    return np.exp(np.log1p(x).sum(axis=1) * 252 / x.shape[1]) - 1


def _rows_dd(x):
    eq = np.cumprod(1 + x, axis=1)
    return (eq / np.maximum.accumulate(eq, axis=1) - 1).min(axis=1)


METRICS = {"Sharpe": sharpe_rows, "CAGR": _rows_cagr, "MaxDD": _rows_dd}


def boot_p(ch, bench, metric):
    """P(challenger metric <= benchmark metric) under a paired stationary bootstrap (MaxDD: <= means as deep or deeper)."""
    a, b = np.asarray(ch), np.asarray(bench)
    f, hits = METRICS[metric], 0
    for _ in range(B // 500):
        idx = stationary_bootstrap_idx(len(a), 500, 20)
        hits += int((f(a[idx]) <= f(b[idx])).sum())
    return hits / B


def holm(ps):
    keys = sorted(ps, key=ps.get)
    m, out, run = len(keys), {}, 0.0
    for k, key in enumerate(keys):
        run = max(run, min(1.0, (m - k) * ps[key]))
        out[key] = run
    return out


# ---------------------------------------------------------------- signals
def h3_mult(px, w, spy, ief):
    idx = spy.dropna().index.intersection(ief.dropna().index)
    s, i = spy.reindex(idx), ief.reindex(idx)
    per = idx.to_period("M")
    me = pd.Series(idx, index=idx).groupby(per).transform("last")  # month's last session
    rev = pd.Series(1, index=idx).groupby(per).cumsum()
    rev = rev.groupby(per).transform("max") - rev  # 0 = last trading day of the month
    prev_end = pd.Series(idx, index=idx).groupby(per).transform("first").map(
        lambda d: idx[idx.get_loc(d) - 1] if idx.get_loc(d) > 0 else pd.NaT)
    ok = prev_end.notna()
    gs = s / s.reindex(prev_end[ok].values).set_axis(idx[ok]).reindex(idx)
    gi = i / i.reindex(prev_end[ok].values).set_axis(idx[ok]).reindex(idx)
    dev = 0.6 * gs / (0.6 * gs + 0.4 * gi) - 0.6
    d5 = dev[rev == 5]
    d5.index = d5.index.to_period("M")
    z = d5 / d5.shift(1).rolling(36, min_periods=36).std()
    last_full = per[-1] if idx[-1] == me.iloc[-1] and idx[-1] < px.index[-1] else per[-1] - 1  # ragged end skipped
    mult = pd.Series(1.0, index=px.index)
    up = pd.Series(np.minimum(1.2, 1 / w.sum(axis=1).where(w.sum(axis=1) > 0, 1)), index=px.index)
    pr = pd.Series(rev.reindex(px.index).values, index=px.index)
    pp = px.index.to_period("M")
    zz = pd.Series(z.reindex(pp).values, index=px.index)
    on = pr.isin([5, 4, 3]) & (pd.Series(pp, index=px.index) <= last_full)
    mult[on & (zz >= 1)] = 0.8
    mult[on & (zz <= -1)] = up[on & (zz <= -1)]
    return mult, int((on & (zz >= 1)).sum() // 3), int((on & (zz <= -1)).sum() // 3)


def vix_episodes(vix):
    v = vix.dropna()
    mx = v.rolling(63, min_periods=1).max()
    starts, last = [], -10 ** 9
    for t in range(len(v)):
        if mx.iloc[t] >= 40 and v.iloc[t] <= 0.6 * mx.iloc[t] and t - last > 126:
            starts.append(v.index[t])
            last = t
    return starts, mx


def h5_gate(px, vix, p=P):
    g = gate_frozen(px, p)
    q = px[BENCH].ffill()
    above = (q > q.rolling(p["regime_ma"]).mean()).values
    starts, mx = vix_episodes(vix)
    starts = [d for d in starts if px.index[0] <= d <= px.index[-1]]
    gv = g.values.copy()
    ends = []
    for s in starts:
        t0 = px.index.searchsorted(s)
        t = t0
        while t < len(px) and t - t0 < 126 and not above[t]:
            gv[t] = 1.0
            t += 1
        ends.append(px.index[min(t, len(px) - 1)])
    return pd.Series(gv, index=px.index), list(zip(starts, ends)), mx


def grok_full(vix, idx):
    v = vix.reindex(idx).ffill()
    return (v <= 22) & (vix.dropna().rolling(126, min_periods=1).max().reindex(idx).ffill() >= 35)


def h9_mult(px, p=P):
    pf = px.ffill()
    names = names_of(px)
    elig = scores(pf, p).notna() & (np.log(pf[names]).diff().rolling(p["vol_win"]).std() > 0)
    pth = pf[names] / pf[names].rolling(252, min_periods=1).max()
    first = pd.Series(px.index, index=px.index).groupby(px.index.to_period("M")).transform("first") == px.index
    m = pd.DataFrame(np.nan, index=px.index, columns=names)
    for d in px.index[first.values]:
        e = elig.loc[d]
        n = int(e.sum())
        if n == 0:
            continue
        rk = pth.loc[d][e].rank(method="first")
        m.loc[d, :] = 1.0
        m.loc[d, rk.index] = 0.5 + (rk - 1) / (n - 1) if n > 1 else 1.0
    return m.ffill().fillna(1.0)


def nl_mult(idx, fred, weeks):
    wal = fred["WALCL"].dropna()
    tga = fred["WTREGEN"].reindex(wal.index)
    rrp = fred["RRPONTSYD"].reindex(fred["RRPONTSYD"].index.union(wal.index)).ffill().reindex(wal.index).fillna(0)
    nl = wal / 1000 - tga / 1000 - rrp
    ch = nl.diff(weeks)
    ch.index = ch.index + pd.Timedelta(days=2)  # Wednesday value, usable from Friday's close
    s = ch.reindex(ch.index.union(idx)).ffill().reindex(idx)
    return pd.Series(np.where(s <= 0, 0.5, 1.0), index=idx)


# ---------------------------------------------------------------- runner helpers
def universes(D):
    px = prices()
    ex = D["ex"]
    px14 = px.join(ex[["INTC", "CSCO", "IBM", "QCOM"]], how="left")[TECH10_2014 + [BENCH]]
    rf = (ex["^IRX"].reindex(px.index).ffill().fillna(0) / 100 / 252)
    start = px.index[P["trend_long"] + P["vol_win"]]
    return {"ship": px, "e2014": px14}, rf, start


def pre_arm(px, w, rf, start, dy=0.0):
    r, ex = sim(px, lagged(w, start), rf, dy=dy)
    return r.loc[start:], ex.loc[start:]


def fmt(x, pct=True, d=1):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else (f"{x:+.{d}%}" if pct else f"{x:.{d}f}")


def main():
    D = load()
    U, rf, start = universes(D)
    ex = D["ex"]
    res = {}       # hypothesis -> dict(P per universe, extra checks, rows)
    lines = []

    # frozen benchmark per universe (pre-tax, banded) and its decomposition check
    base = {}
    for u, px in U.items():
        wu, _ = weights(px)
        g = gate_frozen(px)
        assert np.allclose(wu.mul(g, axis=0).values, target_weights(px).values, atol=1e-12), u
        rb, exb = pre_arm(px, wu.mul(g, axis=0), rf, start)
        base[u] = dict(w=wu, g=g, r=rb, ex=exb)
    lev = load_lev()
    ndx = lev["px"]["^NDX"].dropna()
    pxn = frame(ndx)
    rfn = rf_daily(lev, pxn.index)
    startn = pxn.index[pxn.index.searchsorted(pd.Timestamp("1990-01-02"))]
    wn, _ = weights(pxn, ENG)
    gn = gate_frozen(pxn, ENG)
    assert np.allclose(wn.mul(gn, axis=0).values, target_weights(pxn, ENG).values, atol=1e-12)
    rbn, _ = pre_arm(pxn, wn.mul(gn, axis=0), rfn, startn, NDX_DY)

    def judge(h, arms, metric, extra=None):
        """arms: {universe: (challenger returns, benchmark returns)}"""
        rows = {}
        for u, (c, b) in arms.items():
            rows[u] = dict(ch=summary(c), b=summary(b), P=boot_p(c.values, b.values, metric))
        res[h] = dict(rows=rows, metric=metric, P=max(r["P"] for r in rows.values()), extra=extra or {})

    # ---------------- H1 tax-aware execution
    vgt = ex[["VGT"]]
    h1 = {}
    for u, px in U.items():
        W = lagged(base[u]["w"].mul(base[u]["g"], axis=0), start)
        out = {}
        for k, arm, rates, prot in (("bench", "bench", RATES, None), ("ch", "ch", RATES, (335, 365)),
                                    ("placebo", "ch", RATES, (275, 304)), ("bench0", "bench", ZERO, None),
                                    ("ch0", "ch", ZERO, (335, 365))):
            out[k] = run_ledger(px, W, rf, start, arm, rates, prot or (335, 365), vgt)
            print("H1", u, k, f"{cagr(out[k][0]['liq'].pct_change().fillna(0)):.4f}", out[k][1], flush=True)
        h1[u] = out
    arms, extra = {}, {}
    for u, out in h1.items():
        lr = {k: v[0]["liq"].pct_change().fillna(v[0]["liq"].iloc[0] / 1e5 - 1) for k, v in out.items()}
        arms[u] = (lr["ch"], lr["bench"])
        te = float((out["ch"][0]["pre"] - out["bench"][0]["pre"]).std() * math.sqrt(252))
        d_tax = cagr(lr["ch"]) - cagr(lr["bench"])
        d_zero = cagr(lr["ch0"]) - cagr(lr["bench0"])
        extra[u] = dict(TE=te, TE_ok=te <= 0.02, placebo=cagr(lr["placebo"]), placebo_ok=cagr(lr["ch"]) > cagr(lr["placebo"]),
                        d_tax=d_tax, d_zero=d_zero, zero_ok=d_zero <= 0.5 * d_tax,
                        pre_ch=cagr(out["ch"][0]["pre"]), pre_b=cagr(out["bench"][0]["pre"]),
                        tax_b=out["bench"][0]["tax"].sum(), tax_ch=out["ch"][0]["tax"].sum(),
                        stats={k: v[1] for k, v in out.items()})
    judge("H1", arms, "CAGR", extra)
    res["H1"]["ok"] = all(e["TE_ok"] and e["placebo_ok"] and e["zero_ok"] for e in extra.values())

    # ---------------- H2 muni idle cash
    f = D["funds"]

    def after_tax_cash(t, state):
        h = f[t]
        pr = (h["Close"] / h["Close"].shift(1) - 1).fillna(0)
        dv = (h["Dividends"] / h["Close"].shift(1)).fillna(0)
        td = state if t == "SUB" else RATES["st"]
        return pr * (1 - RATES["st"] - state) + dv * (1 - td)

    h2x = {}
    for state in (0.0, 0.05):
        arms = {}
        for u, px in U.items():
            r0, exu = pre_arm(px, base[u]["w"].mul(base[u]["g"], axis=0), rf * 0, start)
            idle = (1 - exu).clip(lower=0)
            cash = {t: after_tax_cash(t, state).reindex(r0.index).fillna(0) for t in ("SUB", "BIL", "SHY")}
            port = {t: r0 + idle * c for t, c in cash.items()}
            arms[u] = (port["SUB"], port["BIL"])
            h2x.setdefault(state, {})[u] = {t: cagr(v) for t, v in port.items()} | {"idle": float(idle.mean())}
        if state == 0.0:
            judge("H2", arms, "CAGR", h2x)
    res["H2"]["ok"] = all(v["SUB"] > v["SHY"] for v in h2x[0.0].values())
    res["H2"]["state5"] = {}
    for u in U:
        r0, exu = pre_arm(U[u], base[u]["w"].mul(base[u]["g"], axis=0), rf * 0, start)
        idle = (1 - exu).clip(lower=0)
        a = r0 + idle * after_tax_cash("SUB", 0.05).reindex(r0.index).fillna(0)
        b = r0 + idle * after_tax_cash("BIL", 0.05).reindex(r0.index).fillna(0)
        res["H2"]["state5"][u] = boot_p(a.values, b.values, "CAGR")

    # ---------------- H3 month-end rebalancing timing
    arms, extra = {}, {}
    for u, px in U.items():
        wf = base[u]["w"].mul(base[u]["g"], axis=0)
        m, nup, ndn = h3_mult(px, wf, ex["SPY"], ex["IEF"])
        c, _ = pre_arm(px, wf.mul(m, axis=0), rf, start)
        arms[u] = (c, base[u]["r"])
        post = slice("2023-03-01", None)
        ds = summary(c.loc[post])["Sharpe"] - summary(base[u]["r"].loc[post])["Sharpe"]
        extra[u] = dict(months_cut=nup, months_lift=ndn, dSharpe_post=ds, post_ok=ds > 0)
    judge("H3", arms, "Sharpe", extra)
    res["H3"]["ok"] = all(e["post_ok"] for e in extra.values())

    # ---------------- H4 hysteresis band on the 200-day halving
    arms, extra = {}, {}
    for u, px in U.items():
        gh = gate_hyst(px)
        wc = base[u]["w"].mul(gh, axis=0)
        c, _ = pre_arm(px, wc, rf, start)
        arms[u] = (c, base[u]["r"])
        sw = lambda g: int((g.loc[start:].diff().abs() > 0).sum())
        lb = run_ledger(px, lagged(base[u]["w"].mul(base[u]["g"], axis=0), start), rf, start)[0]["liq"]
        lc = run_ledger(px, lagged(wc, start), rf, start)[0]["liq"]
        extra[u] = dict(switch_b=sw(base[u]["g"]), switch_c=sw(gh),
                        at_b=cagr(lb.pct_change().fillna(0)), at_c=cagr(lc.pct_change().fillna(0)))
    ghn = gate_hyst(pxn, p=ENG)
    cn, _ = pre_arm(pxn, wn.mul(ghn, axis=0), rfn, startn, NDX_DY)
    arms["ndx"] = (cn, rbn)
    extra["ndx"] = dict(switch_b=int((gn.loc[startn:].diff().abs() > 0).sum()),
                        switch_c=int((ghn.loc[startn:].diff().abs() > 0).sum()))
    judge("H4", arms, "Sharpe", extra)
    res["H4"]["ok"] = True

    # ---------------- H5 faster re-entry after VIX>=40
    vix = ex["^VIX"]
    arms, extra = {}, {}
    gn5, eps_n, _ = h5_gate(pxn, vix, ENG)
    cn5, _ = pre_arm(pxn, wn.mul(gn5, axis=0), rfn, startn, NDX_DY)
    eps_n = [e for e in eps_n if e[0] >= startn]
    arms["ndx"] = (cn5, rbn)
    ep_rows = []
    for s, e in eps_n:
        t0 = cn5.index.searchsorted(s)
        win = slice(cn5.index[t0], cn5.index[min(t0 + 126, len(cn5) - 1)])
        ep_rows.append((s.date(), e.date(), float(vix.loc[:s].tail(63).max()),
                        float((1 + cn5.loc[win]).prod() - 1), float((1 + rbn.loc[win]).prod() - 1)))
    for u, px in U.items():
        g5, eps, _ = h5_gate(px, vix)
        c, _ = pre_arm(px, base[u]["w"].mul(g5, axis=0), rf, start)
        arms[u] = (c, base[u]["r"])
        extra[u] = dict(episodes=len([e for e in eps if e[0] >= start]))
    # Grok secondary
    grok = {}
    for u, px in U.items():
        full = grok_full(vix, px.index)
        w0 = target_weights(px, {**P, "vol_target": 9, "regime_scale": 1.0})
        wg = base[u]["w"].mul(base[u]["g"], axis=0).where(~full, w0, axis=0)
        grok[u] = summary(pre_arm(px, wg, rf, start)[0])
    fulln = grok_full(vix, pxn.index)
    wgn = wn.mul(gn, axis=0).copy()
    wgn.loc[fulln.values, "IDX"] = 1.0
    grok["ndx"] = summary(pre_arm(pxn, wgn, rfn, startn, NDX_DY)[0])
    judge("H5", arms, "Sharpe", extra)
    for u, r in res["H5"]["rows"].items():
        r["dd_ok"] = r["ch"]["MaxDD"] >= r["b"]["MaxDD"] - 0.03
    res["H5"]["ok"] = all(r["dd_ok"] for r in res["H5"]["rows"].values())
    res["H5"]["episodes_ndx"] = len(eps_n)
    res["H5"]["ep_rows"] = ep_rows
    res["H5"]["grok"] = grok
    if len(eps_n) < 6:
        res["H5"]["status"] = "UNTESTED"

    # ---------------- H6 semis cap
    arms, extra = {}, {}
    for u, px in U.items():
        wc, bind = weights(px, semis=SEMIS[u])
        freq = float(bind.loc[start:].mean())
        c, _ = pre_arm(px, wc.mul(base[u]["g"], axis=0), rf, start)
        arms[u] = (c, base[u]["r"])
        dd = lambda r, a, b: maxdd(r.loc[a:b].values)
        extra[u] = dict(bind=freq, dd2022=(dd(c, "2022-01-01", "2022-12-31"), dd(base[u]["r"], "2022-01-01", "2022-12-31")),
                        ddnov26=(dd(c, "2026-11-01", None), dd(base[u]["r"], "2026-11-01", None)))
    judge("H6", arms, "MaxDD", extra)
    for r in res["H6"]["rows"].values():
        r["sh_ok"] = r["ch"]["Sharpe"] >= r["b"]["Sharpe"] - 0.05
    res["H6"]["ok"] = all(r["sh_ok"] for r in res["H6"]["rows"].values())
    if any(e["bind"] < 0.10 for e in extra.values()):
        res["H6"]["status"] = "MOOT"

    # ---------------- H9 52-week-high tilt
    arms = {}
    for u, px in U.items():
        wc, _ = weights(px, mult=h9_mult(px))
        c, _ = pre_arm(px, wc.mul(base[u]["g"], axis=0), rf, start)
        arms[u] = (c, base[u]["r"])
    judge("H9", arms, "Sharpe")
    res["H9"]["ok"] = True

    # ---------------- H12 net liquidity
    arms, extra = {}, {}
    for u, px in U.items():
        wf = base[u]["w"].mul(base[u]["g"], axis=0)
        c, _ = pre_arm(px, wf.mul(nl_mult(px.index, D["fred"], 4), axis=0), rf, start)
        c13, _ = pre_arm(px, wf.mul(nl_mult(px.index, D["fred"], 13), axis=0), rf, start)
        arms[u] = (c, base[u]["r"])
        sb = summary(base[u]["r"])["Sharpe"]
        d4, d13 = summary(c)["Sharpe"] - sb, summary(c13)["Sharpe"] - sb
        extra[u] = dict(d4=d4, d13=d13, sign_ok=np.sign(d4) == np.sign(d13),
                        cut_share=float((nl_mult(px.index, D["fred"], 4).loc[start:] < 1).mean()))
    judge("H12", arms, "Sharpe", extra)
    res["H12"]["ok"] = all(e["sign_ok"] for e in extra.values())

    # ---------------- Holm + verdicts
    ps = {h: r["P"] for h, r in res.items() if r.get("status") is None}
    adj = holm(ps)
    for h, r in res.items():
        r["holm"] = adj.get(h)
        r["pass"] = r.get("status") is None and adj[h] < 0.05 and r["ok"]
    pd.to_pickle(res, "data/retail_edge_results.pkl")
    write_report(res, start, U, startn)


NAMES = {"H1": "Tax-aware execution (after-tax liquidation CAGR)", "H2": "Muni (SUB) idle cash vs T-bills (after-tax CAGR)",
         "H3": "Month-end 60/40 rebalancing timing", "H4": "±2% band on QQQ 200-day halving",
         "H5": "Faster re-entry after VIX≥40", "H6": "Semis-cluster cap ≤40% (metric MaxDD)",
         "H9": "52-week-high tilt", "H12": "4-week net-liquidity halving"}
UN = {"ship": "shipped", "e2014": "end-2014", "ndx": "^NDX 1990–"}


def write_report(res, start, U, startn):
    end = U["ship"].index[-1].date()
    L = ["# Retail-edge slate: pre-registered tests vs the frozen model", "",
         f"Generated by `retail_edge_tests.py`. Stock windows {start.date()} – {end}; ^NDX engine {startn.date()} – {end}. "
         f"Holm across {sum(1 for r in res.values() if r.get('status') is None)} hypotheses that produced a P.", "",
         VERDICT, "", "## Results", "",
         "| Test | Universe | Bench CAGR | Δ CAGR | Bench MaxDD | Ch MaxDD | Bench Sharpe | Ch Sharpe | P | Holm P | Pass |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for h, r in res.items():
        st = r.get("status")
        for u, x in r["rows"].items():
            L.append(f"| {h} {NAMES[h]} | {UN[u]} | {fmt(x['b']['CAGR'])} | {fmt(x['ch']['CAGR'] - x['b']['CAGR'], d=2)} | "
                     f"{fmt(x['b']['MaxDD'])} | {fmt(x['ch']['MaxDD'])} | {x['b']['Sharpe']:.3f} | {x['ch']['Sharpe']:.3f} | "
                     f"{x['P']:.3f} | {fmt(r['holm'], False, 3) if r['holm'] is not None else st} | "
                     f"{st or ('PASS' if r['pass'] else 'fail')} |")
    L += ["", "CAGR/MaxDD/Sharpe for H1 are on the after-tax liquidation value; for H2 on the after-tax portfolio "
          "(equity sleeve pre-tax in both arms, so only the delta is meaningful); all others pre-tax with T-bills on idle cash. "
          "P = P(challenger ≤ benchmark) on the pre-named metric (H6: P(challenger's MaxDD at least as deep)). "
          "Hypothesis P = max over its universes; Holm over hypotheses.", ""]
    e = res["H1"]["extra"]
    L += ["## H1 detail (taxable, top bracket, $100k start, no state tax)", "",
          "| Universe | After-tax Δ CAGR | Zero-tax Δ CAGR | Placebo after-tax CAGR | Pre-tax CAGR bench / ch | Pre-tax TE | Taxes paid bench / ch | Harvested lots | Deferrals |",
          "|---|---|---|---|---|---|---|---|---|"]
    for u, x in e.items():
        L.append(f"| {UN[u]} | {fmt(x['d_tax'], d=2)} | {fmt(x['d_zero'], d=2)} (ok={x['zero_ok']}) | {fmt(x['placebo'], d=2)} "
                 f"(ch beats={x['placebo_ok']}) | {fmt(x['pre_b'], d=2)} / {fmt(x['pre_ch'], d=2)} | {x['TE']:.2%} (ok={x['TE_ok']}) | "
                 f"${x['tax_b']:,.0f} / ${x['tax_ch']:,.0f} | {x['stats']['ch']['harvested_lots']} | {x['stats']['ch']['deferrals']} |")
    L += ["", "## H2 detail (after-tax CAGR of whole portfolio, equity pre-tax)", "",
          "| State tax | Universe | Mean idle cash | BIL | SUB | SHY |", "|---|---|---|---|---|---|"]
    for s, d in res["H2"]["extra"].items():
        for u, x in d.items():
            L.append(f"| {s:.0%} | {UN[u]} | {x['idle']:.1%} | {fmt(x['BIL'], d=2)} | {fmt(x['SUB'], d=2)} | {fmt(x['SHY'], d=2)} |")
    L.append(f"\nAt 5% state tax, P(SUB ≤ BIL): " + ", ".join(f"{UN[u]} {p:.3f}" for u, p in res["H2"]["state5"].items()))
    e = res["H3"]["extra"]
    L += ["", "## H3 detail", ""] + [f"- {UN[u]}: overlay cut exposure in {x['months_cut']} months, lifted in {x['months_lift']}; "
                                     f"ΔSharpe from 2023-03 = {x['dSharpe_post']:+.3f}" for u, x in e.items()]
    e = res["H4"]["extra"]
    L += ["", "## H4 detail", ""] + [f"- {UN[u]}: gate switches {x['switch_b']} (frozen) → {x['switch_c']} (band)"
                                     + (f"; after-tax CAGR under H1 FIFO ledger {fmt(x['at_b'], d=2)} → {fmt(x['at_c'], d=2)} (reported, not judged)"
                                        if "at_b" in x else "") for u, x in e.items()]
    r5 = res["H5"]
    L += ["", "## H5 detail", "", f"Qualifying episodes on ^NDX 1990–2026: **{r5['episodes_ndx']}** (power rule ≥ 6). "
          + "; ".join(f"{UN[u]}: {x['episodes']} in window" for u, x in r5["extra"].items()), "",
          "| Episode signal | Override ended | VIX 63d max | ^NDX engine, challenger 126-session return | benchmark |", "|---|---|---|---|---|"]
    L += [f"| {a} | {b} | {v:.1f} | {fmt(c)} | {fmt(d)} |" for a, b, v, c, d in r5["ep_rows"]]
    L += ["", "MaxDD condition (≤ 3 pp worse): " + ", ".join(f"{UN[u]} {x['dd_ok']}" for u, x in r5["rows"].items()), "",
          "Secondary, Grok's rule (not judged): " + "; ".join(
              f"{UN[u]} CAGR {fmt(x['CAGR'])}, Sharpe {x['Sharpe']:.3f}, MaxDD {fmt(x['MaxDD'])}" for u, x in r5["grok"].items())]
    e = res["H6"]["extra"]
    L += ["", "## H6 detail", ""] + [f"- {UN[u]}: cap binds on {x['bind']:.1%} of days; 2022 MaxDD ch {fmt(x['dd2022'][0])} vs "
                                     f"bench {fmt(x['dd2022'][1])}; Nov-2026 ch {fmt(x['ddnov26'][0])} vs bench {fmt(x['ddnov26'][1])}"
                                     for u, x in e.items()]
    L += ["- 2000–02 end-1998 list not run (survivor-only free data lacks Lucent, Nortel, etc.); one-asset ^NDX engine has no cluster to cap."]
    e = res["H12"]["extra"]
    L += ["", "## H12 detail", ""] + [f"- {UN[u]}: halving active {x['cut_share']:.0%} of days; ΔSharpe 4-wk {x['d4']:+.3f}, "
                                      f"13-wk {x['d13']:+.3f} (same sign: {x['sign_ok']})" for u, x in e.items()]
    L += ["", "## Not run", "", "- H11 Lazy Prices: SEC EDGAR requires a declared contact in the User-Agent (generic UA → HTTP 403).",
          "- Ranks 7, 8, 10, 13, 14: skipped per task scope.",
          "- H1 at the user's actual bracket and the seeded-lots secondary run: not run (bracket unknown).", "",
          CAVEATS, "", PREREG]
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote", OUT)


VERDICT = """## Verdict (written after the 2026-11-20 run; the numbers below are deterministic, seed 7)

**Nothing passes; propose no change to the frozen model.** Holm runs over 7 hypotheses (H11 skipped, H6 moot). The
smallest hypothesis-level P is 0.159 (H5), so every Holm P is 1.000. No test clears even its unadjusted bar on all universes.

- **H1, tax-aware execution: the mechanism is real, but this rule set gives most of it back.** Taxes paid fall 27%
  (shipped, $223k → $162k) and 37% (end-2014). After-tax liquidation CAGR rises +0.84 pp and +0.57 pp, inside the
  report's +0.2 to +0.8 pp expectation. It still fails on every count. P = 0.13 and 0.22. Pre-tax tracking error is
  2.05% and 2.58%, over the 2% bar. The rules cost about 1.4 pp/yr pre-tax: the zero-tax rerun shows −2.0 pp and
  −1.05 pp. The 4,400 harvests park single names in QQQ for 31 days, mostly right after a 10% dip, and these names then
  rebounded. The 5 pp band also lets weights drift. The placebo (275–304-day protection) lands within 0.1–0.3 pp of the
  challenger, so the 335–365-day deferral adds almost nothing. A leaner variant (no index swap, or harvest only lots
  with no pending repurchase) would be a new hypothesis for a scheduled review and counts as a new trial.
- **H5, VIX≥40 re-entry, comes closest pre-tax.** Point estimates are positive everywhere (+0.3 pp CAGR) and MaxDD is
  no worse. P = 0.054 (shipped), 0.083 (end-2014) and 0.159 (^NDX, 11 episodes). Most of the gain comes from two
  episodes, 2008-11 and 2025-04. That leaves it untestable within one review window, as the slate predicted.
- **H2, muni cash:** +0.13 to +0.14 pp after tax, P ≈ 0.26–0.34 (0.28–0.34 at 5% state tax). SUB beats the SHY
  duration control, but the edge is too small to separate from noise at a ~15–21% idle-cash share.
- **H3** (month-end timing): about zero (+0.15 pp shipped, −0.05 pp end-2014). After 2023-03, ΔSharpe is +0.004 and −0.025.
- **H4** (±2% band): it cuts gate switches from 61 to 25 (253 to 87 on ^NDX), but Sharpe is lower on the shipped
  universe and ^NDX, and after-tax CAGR is lower on the shipped universe.
- **H6** (semis cap): MOOT. The cap never binds, because inverse-vol keeps semis at a 37% maximum (mean 30%) of the
  shipped sleeve and a 24% maximum of the end-2014 sleeve.
- **H9** (52-week-high tilt): −1.1 pp shipped, flat end-2014. Fail.
- **H12** (net liquidity): fails as pre-registered. CAGR is −6.3 pp and −4.0 pp, the rule halves exposure on 49% of
  days, and the 13-week version flips sign.
"""
CAVEATS = """## Caveats (written after the run)

- Tax model: top federal bracket assumed (40.8% ST/interest, 23.8% LT), no state tax, and the $3,000 loss deduction
  valued at 37% (it assumes other ordinary income). $100k start; the $3,000 limit does not scale with account size.
  No AMT. Dividends sit inside adjusted prices, so they are taxed as gains at sale rather than yearly as qualified
  dividends, the same in both arms. A wash sale whose repurchase falls in the next calendar year is reversed in the
  repurchase year.
- QQQ/VGT are treated as not substantially identical to single names or to each other. The IRS has never ruled on
  ETF pairs.
- H1 (c) is implemented as a pro-rata scaling of every name when Σ target and Σ held differ by more than 1 pp. Band,
  harvest and swap-back decisions use the fill-day close, as the live monitor's band does.
- The H1 bootstrap resamples daily returns of the realised after-tax liquidation-value path. It does not re-run the lot
  ledger on each resample, so the tax path is taken as given.
- H2: BIL stands in for SGOV over the whole window. Cash-sleeve price changes are taxed as ST in the year they occur.
  The equity sleeve is pre-tax in all arms, so only the H2 delta is meaningful. Any SUB capital-gain distributions are
  treated as tax-exempt.
- Survivorship and hindsight: the shipped list was picked knowing the winners. The end-2014 list contains only names
  that still trade. The ^NDX engine is one asset (leverage_study ENG, cap 1.0) with an assumed 0.8%/yr dividend.
- Crisis tests rest on few events: 4 VIX episodes in the stock windows and 11 on ^NDX. The 2000–02 semis diagnostic was
  not possible on free data.
"""

if __name__ == "__main__":
    main()
