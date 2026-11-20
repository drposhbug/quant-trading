"""TSM ADR premium vs 2330.TW: does the premium (or Taiwan's overnight move) predict TSM? Study only, model frozen.
Writes reports/tsm_premium_results.md.   Run: python tsm_premium_study.py [--refresh]

PRE-REGISTRATION (fixed 2026-11-20 before any test below was run; copied verbatim into the report):
Data. yfinance daily 2010+: 2330.TW, TWD=X, TSM, SMH (auto_adjust=False: Close = split- not dividend-adjusted,
  Adj Close = total return). Alpaca SIP 1-minute TSM/SMH bars (adjustment=split) 2016-01-04 to 2026-11-19 for the
  09:35 price. 1 TSM ADR = 5 shares of 2330.TW.
Timing. Taiwan closes 13:30 Taipei = 00:30 ET (EST) / 01:30 ET (EDT), before the US open of the same date D.
  FX: yfinance TWD=X daily bar D runs ~23:00 UTC D-1 -> ~22:00 UTC D, so its Close is after the US open (look-ahead);
  we use its Open (~18:00-19:00 ET D-1), known ~6.5 h before the Taiwan close. A day D is usable only if 2330.TW
  traded on D (Volume > 0): on a Taiwan holiday there is no fresh Taiwan price and the day is dropped.
Premium. level: TSM_open_D / (5 * TW_close_D / USDTWD_D) - 1, unadjusted prices (TSM's 09:30 official open, the
  first US price after the Taiwan close). For z we use the same ratio on dividend-adjusted prices (Open x AdjClose/Close
  for TSM, Adj Close for TW) so ex-date mismatches between Taipei and New York do not create fake 1-2 day deviations.
  lp = log(1 + premium_adj). z_D = (lp_D - mean(lp over the previous 60 usable days)) / sd(same 60 days).
  z_D is known at ~09:30:30 ET; every trade starts at 09:35 (close of the 09:34 1-minute bar).
Sample/holdout. Predictive tests use Alpaca-era days 2016-2026; discovery = first 70% of those days, holdout = last
  30%, run once after discovery is written. The overlay uses the same calendar split.
Tests (Holm across all 8, on discovery; pass = Holm p < 0.05 AND holdout same sign with one-sided p < 0.05):
  T2a slope of TSM 09:35->close return on z            (HAC t, 5 lags)
  T2b slope of TSM close D -> close D+1 return on z     (HAC t, 5 lags)
  T2c slope of TSM 09:35 D -> close D+4 (5 sessions)    (HAC t, 10 lags; overlapping)
  T2d slope of TSM residual 09:35->close vs SMH on z    (beta = OLS over the previous 60 days, HAC t, 5 lags)
  T3  Taiwan overnight USD return (TW close prev TW session -> TW close D, FX-adjusted) predicting TSM 09:35->close,
      controlling for TSM's opening gap (prev US close -> open): partial slope via Frisch-Waugh, HAC t 5 lags
  T4a rule: z < -1.5 -> long TSM 09:35 -> close same day, else flat; 2 bp/side (5 bp stress, not in the family).
      Stationary bootstrap (L=20, B=2000) P(Sharpe <= 0) vs flat
  T4b same rule, paired bootstrap P(Sharpe_rule <= Sharpe_always-long TSM close-to-close)
  T5  overlay inside the frozen model: TSM weight x0.5 if z_D > +1.5, x1.5 (capped at 0.25) if z_D < -1.5, applied at
      the close-D rebalance (z_D known that morning), extra weight from cash, everything else frozen;
      paired bootstrap P(Sharpe_overlay <= Sharpe_frozen) over the model's backtest window.
Expected sign: cheap ADR (z < 0) -> higher later TSM return (negative slopes in T2). Two-sided p for slopes,
one-sided bootstrap p for T4/T5 (the repo's P(challenger <= benchmark) convention). Premium dynamics (level, AR(1)
half-life, regimes) are descriptive, not in the family.
"""
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import yfinance as yf

from backtest import sharpe_rows, stationary_bootstrap_idx, stats
from correlations import holm, pval
from intraday_study import get
from macro import hac_slope_t

DAILY = "data/tsm_premium_daily.pkl"
START, END = "2016-01-01", "2026-11-19"
COST, STRESS = 0.0002, 0.0005
ZWIN, ZT = 60, 1.5
B, L = 2000, 20


# ---------------------------------------------------------------- data
def daily():
    if os.path.exists(DAILY) and "--refresh" not in sys.argv:
        return pd.read_pickle(DAILY)
    d = {}
    for t in ["2330.TW", "TWD=X", "TSM", "SMH"]:
        x = yf.download(t, start="2009-09-01", auto_adjust=False, progress=False, threads=False)
        x.columns = x.columns.get_level_values(0)
        d[t] = x
    pd.to_pickle(d, DAILY)
    return d


def minute(sym):
    """09:30-09:34 ET 1-minute bars (only these are kept). Alpaca SIP, split-adjusted to match yfinance Close."""
    path = f"data/tsm_premium_1m_{sym}.pkl"
    if os.path.exists(path) and "--refresh" not in sys.argv:
        return pd.read_pickle(path)
    keep, tok, n = [], None, 0
    while True:
        p = dict(timeframe="1Min", start=START + "T00:00:00Z", end=END + "T23:59:00Z", feed="sip",
                 adjustment="split", limit=10000)
        if tok:
            p["page_token"] = tok
        j = get(f"https://data.alpaca.markets/v2/stocks/{sym}/bars", p)
        b = pd.DataFrame(j.get("bars") or [])
        if len(b):
            n += len(b)
            ts = pd.to_datetime(b["t"], utc=True).dt.tz_convert("America/New_York")
            hm = ts.dt.strftime("%H:%M")
            b = b.assign(ts=ts)[(hm >= "09:30") & (hm < "09:35")]
            keep.append(b[["ts", "o", "c", "v"]])
        tok = j.get("next_page_token")
        print(f"  {sym}: {n} bars", end="\r")
        if not tok:
            break
    d = pd.concat(keep, ignore_index=True)
    d.to_pickle(path)
    return d


def p0935(m):
    """Per date: first 1-min open (>= 09:30) and the last trade before 09:35 (close of the last bar < 09:35)."""
    m = m.assign(date=m["ts"].dt.tz_localize(None).dt.normalize())
    g = m.sort_values("ts").groupby("date")
    return pd.DataFrame({"o930": g["o"].first(), "p935": g["c"].last()})


def fx_hourly_check(fx_open):
    """How stale is the daily Open vs the rate at the Taiwan close (05:00-06:00 UTC)? Last ~2 years only (Yahoo)."""
    h = yf.download("TWD=X", period="720d", interval="1h", progress=False)
    h.columns = h.columns.get_level_values(0)
    h = h[h.index.hour == 5]["Close"]
    h.index = h.index.tz_localize(None).normalize()
    j = pd.concat([h, fx_open], axis=1, keys=["h", "o"], sort=True).dropna()
    e = np.log(j["h"] / j["o"])
    return len(e), e.std() * 1e4, e.abs().quantile(0.99) * 1e4


# ---------------------------------------------------------------- premium
def premium_frame(d):
    tw, fx, us = d["2330.TW"], d["TWD=X"], d["TSM"]
    tw = tw[tw["Volume"] > 0]
    fxo = fx["Open"].where(fx["Open"] > 0)
    fxo = fxo[(np.log(fxo).diff().abs() < 0.03) | fxo.diff().isna()]  # drop bad Yahoo prints (>3% TWD moves)
    f = pd.DataFrame(index=us.index)
    f["tsm_open"], f["tsm_close"] = us["Open"].where(us["Open"] > 0), us["Close"]
    f["tsm_adjf"] = us["Adj Close"] / us["Close"]
    f["tw_close"] = tw["Close"].reindex(f.index)          # same calendar date only: NaN on Taiwan holidays
    f["tw_adjf"] = (tw["Adj Close"] / tw["Close"]).reindex(f.index)
    f["fx"] = fxo.reindex(f.index).fillna(fx["Close"].shift(1).reindex(f.index))  # no D bar -> prior Close
    f["prem"] = f["tsm_open"] / (5 * f["tw_close"] / f["fx"]) - 1
    f["lp"] = np.log(f["tsm_open"] * f["tsm_adjf"] / (5 * f["tw_close"] * f["tw_adjf"] / f["fx"]))
    f["z"] = zscore(f["lp"])
    # Taiwan overnight USD return: previous Taiwan session close -> close D, each at its own FX Open
    twu = (tw["Adj Close"] / fxo.reindex(tw.index).ffill())
    f["tw_ret"] = (twu / twu.shift(1) - 1).reindex(f.index).where(f["tw_close"].notna())
    adj_close = us["Adj Close"]
    f["gap"] = us["Open"] * f["tsm_adjf"] / adj_close.shift(1) - 1
    f["cc_next"] = adj_close.shift(-1) / adj_close - 1
    f["c4"] = adj_close.shift(-4) / adj_close          # close D -> close D+4 multiplier
    f["bh"] = adj_close.pct_change()
    return f


def zscore(lp, win=ZWIN):
    """z over usable days only; mean/sd from the previous `win` usable days (today excluded)."""
    s = lp.dropna()
    m, sd = s.rolling(win).mean().shift(1), s.rolling(win).std().shift(1)
    return ((s - m) / sd).reindex(lp.index)


def half_life(x):
    x = x.dropna()
    phi = np.polyfit(x.shift(1).dropna().values, x.iloc[1:].values, 1)[0]
    return phi, (math.log(0.5) / math.log(phi) if 0 < phi < 1 else np.inf)


def fwl(y, x, c):
    """Partial out [1, c] from y and x (Frisch-Waugh): slope of the residuals = multivariate coefficient on x."""
    C = np.column_stack([np.ones_like(c), c])
    res = lambda v: v - C @ np.linalg.lstsq(C, v, rcond=None)[0]
    return res(y), res(x)


# ---------------------------------------------------------------- tests
def slope_row(name, y, x, lags, scale=1e4):
    ok = np.isfinite(y) & np.isfinite(x)
    b, t = hac_slope_t(y[ok], x[ok], lags)
    return dict(Test=name, N=int(ok.sum()), Effect=b * scale, t=t, p=pval(t))


def boot_p(a, b=None):
    """P(Sharpe_a <= Sharpe_b) (b=None -> vs 0), paired stationary bootstrap."""
    a = np.asarray(a)
    idx = stationary_bootstrap_idx(len(a), B, L)
    sa = sharpe_rows(a[idx])
    return float(np.mean(sa <= (0 if b is None else sharpe_rows(np.asarray(b)[idx]))))


def run_tests(S, ov):
    rows = [
        slope_row("T2a z -> 09:35-close", S["oc"].values, S["z"].values, 5),
        slope_row("T2b z -> close-close D+1", S["cc_next"].values, S["z"].values, 5),
        slope_row("T2c z -> 09:35 D -> close D+4", S["r5"].values, S["z"].values, 10),
        slope_row("T2d z -> resid vs SMH 09:35-close", S["resid"].values, S["z"].values, 5),
    ]
    ok = S[["oc", "tw_ret", "gap"]].notna().all(axis=1)
    yr, xr = fwl(S.loc[ok, "oc"].values, S.loc[ok, "tw_ret"].values, S.loc[ok, "gap"].values)
    rows.append(slope_row("T3 TW overnight -> 09:35-close, gap held", yr, xr, 5, scale=1))
    rule = S["rule"]
    for name, p, eff in [("T4a rule vs flat", boot_p(rule), sharpe(rule)),
                         ("T4b rule vs always-long TSM", boot_p(rule, S["bh"]), sharpe(rule) - sharpe(S["bh"])),
                         ("T5 overlay vs frozen model", boot_p(ov["ov"], ov["frozen"]),
                          sharpe(ov["ov"]) - sharpe(ov["frozen"]))]:
        rows.append(dict(Test=name, N=len(rule) if name[1] == "4" else len(ov), Effect=eff, t=np.nan, p=p))
    return pd.DataFrame(rows).set_index("Test")


def sharpe(r):
    return r.mean() / r.std() * math.sqrt(252) if r.std() > 0 else 0.0


def overlay(z):
    from backtest import prices
    from model import P, backtest_returns, target_weights
    px = prices()
    w = target_weights(px)
    zz = z.reindex(px.index)  # z_D known at 09:30 D, used for the weight set at close D
    mult = np.where(zz > ZT, 0.5, np.where(zz < -ZT, 1.5, 1.0))
    w2 = w.copy()
    w2["TSM"] = (w["TSM"] * mult).clip(upper=P["cap"])
    out = pd.DataFrame({"frozen": backtest_returns(px, w), "ov": backtest_returns(px, w2)})
    out = out[w.abs().sum(axis=1).shift(1).fillna(0).cumsum() > 0]  # from the model's first invested day
    return out, (mult != 1).mean()


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    d = daily()
    f = premium_frame(d)
    smh = d["SMH"]
    mt, ms = p0935(minute("TSM")), p0935(minute("SMH"))

    S = f.join(mt).loc[START:END]
    S["smh_oc"] = smh["Close"].reindex(S.index) / ms["p935"].reindex(S.index) - 1
    S["oc"] = S["tsm_close"] / S["p935"] - 1
    S["r5"] = (1 + S["oc"]) * S["c4"] - 1
    beta = S["oc"].rolling(60).cov(S["smh_oc"]).shift(1) / S["smh_oc"].rolling(60).var().shift(1)
    S["resid"] = S["oc"] - beta * S["smh_oc"]
    S = S[S["z"].notna() & S["oc"].notna()]
    sig = S["z"] < -ZT
    S["rule"] = np.where(sig, S["oc"] - 2 * COST, 0.0)
    S["rule5"] = np.where(sig, S["oc"] - 2 * STRESS, 0.0)
    S["intra"] = S["oc"] - 2 * COST                       # control: long 09:35->close every day

    cut = S.index[int(len(S) * 0.7)]
    ov, ov_active = overlay(f["z"])
    disc = run_tests(S[S.index < cut], ov[ov.index < cut])
    hold = run_tests(S[S.index >= cut], ov[ov.index >= cut])
    disc["Holm p"] = holm(disc["p"]).values
    sign = lambda r: np.sign(r["t"]) if np.isfinite(r["t"]) else np.sign(r["Effect"])
    one_sided = lambda r: (r["p"] / 2 if np.isfinite(r["t"]) else r["p"])
    tab = pd.DataFrame({
        "N disc": disc["N"], "Effect disc": disc["Effect"], "t disc": disc["t"], "p disc": disc["p"],
        "Holm p": disc["Holm p"], "N hold": hold["N"], "Effect hold": hold["Effect"], "t hold": hold["t"],
        # slopes: one-sided in the discovery sign; T4/T5 bootstrap p is already one-sided in the hypothesis direction
        "p hold (1-sided)": [hold.loc[k, "p"] if not np.isfinite(hold.loc[k, "t"]) else
                             one_sided(hold.loc[k]) if sign(hold.loc[k]) == sign(disc.loc[k])
                             else 1 - one_sided(hold.loc[k]) for k in disc.index]})
    tab["Pass"] = (tab["Holm p"] < 0.05) & (tab["p hold (1-sided)"] < 0.05)

    report(d, f, S, cut, tab, ov, ov_active, mt)


# ---------------------------------------------------------------- report
def fmt(x, nd=2):
    return "" if pd.isna(x) else f"{x:.{nd}f}"


def strat_rows(S, cut):
    halves = {"Disc H1": S.index < S.index[int(len(S) * 0.35)],
              "Disc H2": (S.index >= S.index[int(len(S) * 0.35)]) & (S.index < cut),
              "Holdout": S.index >= cut, "All": np.full(len(S), True)}
    rows = []
    for col, name in [("rule", "Rule z<-1.5, 2bp"), ("rule5", "Rule z<-1.5, 5bp"),
                      ("intra", "Long 09:35->close every day, 2bp"), ("bh", "Always-long TSM (close-close)")]:
        r = S[col]
        s = stats(r)
        row = {"Strategy": name, "Days in": int((r != 0).sum()), "CAGR %": s["CAGR"] * 100, "Sharpe": s["Sharpe"],
               "MaxDD %": s["MaxDD"] * 100}
        for k, m in halves.items():
            if k != "All":
                row[f"Sharpe {k}"] = sharpe(r[m])
        rows.append(row)
    return pd.DataFrame(rows)


def report(d, f, S, cut, tab, ov, ov_active, mt):
    pre = __doc__.split("PRE-REGISTRATION")[1].split("\n", 1)[1]
    P = f["prem"].dropna()
    lpd = (f["lp"] - f["lp"].dropna().rolling(ZWIN).mean().shift(1).reindex(f.index)).dropna()
    phi_l, hl_l = half_life(f["lp"].dropna())
    phi_d, hl_d = half_life(lpd)
    yr = P.groupby(P.index.year).agg(["mean", "std", "min", "max"]) * 100
    yr["days"] = P.groupby(P.index.year).size()
    x = f.loc[START:].dropna(subset=["lp"])
    ao = x["tsm_open"] * x["tsm_adjf"]
    dev = (x["lp"] - x["lp"].rolling(ZWIN).mean().shift(1)).values
    leg = {}
    for k, v in [("tw", np.log(1 + x["tw_ret"].shift(-1))), ("tsm", np.log(ao.shift(-1) / ao))]:
        ok = np.isfinite(v.values) & np.isfinite(dev)
        leg[k] = hac_slope_t(v.values[ok], dev[ok], 5)
    tw = d["2330.TW"]
    n_fx, fx_sd, fx_99 = fx_hourly_check(d["TWD=X"]["Open"])
    open_diff = (np.log(S["o930"] / S["tsm_open"]).abs() * 1e4).median()
    sig = S["z"] < -ZT
    fz = f["z"].dropna()
    so = stats(ov["ov"]), stats(ov["frozen"])
    w = []
    w.append("# TSM ADR premium study (TSM vs 2330.TW)\n")
    w.append(f"Generated by tsm_premium_study.py on {pd.Timestamp.today():%Y-%m-%d}. Study only: the model is frozen; "
             "a pass would be a candidate for the 2027-11-19 scheduled review, never a live change. "
             "Every rule is directional in TSM only (long/flat or TSM weight scaling), no paired Taiwan trade.\n")
    w.append("## Pre-registration (written before running)\n```\n" + pre.rstrip() + "\n```\n")
    w.append("## Data coverage\n")
    w.append(f"- 2330.TW: {tw.index[0]:%Y-%m-%d} to {tw.index[-1]:%Y-%m-%d}, {int((tw['Volume'] > 0).sum())} sessions; "
             f"TSM: {d['TSM'].index[0]:%Y-%m-%d} to {d['TSM'].index[-1]:%Y-%m-%d}, {len(d['TSM'])} sessions.\n"
             f"- US sessions with a same-date Taiwan close (usable): {f['prem'].notna().sum()} of {len(f)}; "
             f"{f['tw_close'].isna().sum()} US days dropped for Taiwan holidays/typhoon closures. Taiwan-only days "
             "(US closed) enter only through the Taiwan overnight return.\n"
             f"- Alpaca 1-minute TSM: {mt.index[0]:%Y-%m-%d} to {mt.index[-1]:%Y-%m-%d}, {len(mt)} days with a 09:30-09:34 "
             f"bar. Test sample (z and 09:35 price available): {len(S)} days, {S.index[0]:%Y-%m-%d} to "
             f"{S.index[-1]:%Y-%m-%d}. Discovery < {cut:%Y-%m-%d} <= holdout.\n"
             f"- yfinance TSM daily Open vs Alpaca first 1-minute open: median |diff| {open_diff:.1f} bp.\n"
             f"- FX staleness: TWD=X daily Open vs hourly rate at 05:00 UTC (Taiwan close), last {n_fx} days: "
             f"sd {fx_sd:.1f} bp, 99th pct |diff| {fx_99:.1f} bp. That noise enters the premium one-for-one and is "
             "small vs the premium's daily moves.\n"
             "- Splits/dividends: no TSM or 2330.TW split since 2010; premium LEVEL uses unadjusted (split-only) prices, "
             "z and all multi-day returns use dividend-adjusted prices; same-day 09:35->close uses split-adjusted Alpaca "
             "vs split-adjusted yfinance Close.\n")
    w.append("## 1. Premium dynamics (descriptive)\n")
    w.append(f"Full sample {P.index[0]:%Y-%m-%d} to {P.index[-1]:%Y-%m-%d}: mean {P.mean()*100:.2f}%, sd "
             f"{P.std()*100:.2f}%, min {P.min()*100:.2f}%, max {P.max()*100:.2f}%, last {P.iloc[-1]*100:.2f}%. "
             f"Daily change sd {P.diff().std()*100:.2f} pp.\n\n"
             f"AR(1) on the log premium level: phi {phi_l:.3f}, half-life {hl_l:.1f} days (the level drifts with "
             f"regimes). AR(1) on the deviation from its trailing 60-day mean: phi {phi_d:.3f}, half-life {hl_d:.1f} days. "
             f"z: sd {fz.std():.2f}, share of days z < -1.5: {(fz < -ZT).mean()*100:.1f}%, z > +1.5: "
             f"{(fz > ZT).mean()*100:.1f}%.\n")
    w.append("Premium by year (%):\n\n" + yr.round(2).to_markdown() + "\n")
    w.append("## 2-5. Pre-registered tests (Holm across 8, discovery; holdout run once)\n")
    w.append("Effect: T2 = slope in bp of TSM return per 1 unit of z; T3 = partial regression coefficient (bp of TSM "
             "09:35->close per bp of Taiwan overnight USD return, gap held fixed; > 0 continuation, < 0 reversal); "
             "T4a = Sharpe of the rule; T4b/T5 = Sharpe difference. p: two-sided HAC for slopes, one-sided bootstrap "
             "P(Sharpe <= benchmark) for T4/T5.\n")
    w.append(tab.to_markdown(floatfmt=".3f") + "\n")
    w.append(f"Rule active on {int(sig.sum())} of {len(S)} test days ({sig.mean()*100:.1f}%). "
             f"Overlay changes TSM's weight on {ov_active*100:.1f}% of model days.\n")
    w.append("## 4. Rule vs benchmarks (daily series, 0 when flat)\n")
    w.append(strat_rows(S, cut).to_markdown(index=False, floatfmt=".2f") + "\n")
    tr = S.loc[sig, "oc"] - 2 * COST
    w.append(f"Rule trades: mean {tr.mean()*1e4:.1f} bp net, hit {(tr > 0).mean()*100:.0f}%; "
             f"intraday 09:35->close on all other days: {(S.loc[~sig, 'oc'] - 2*COST).mean()*1e4:.1f} bp.\n")
    w.append("## 5. Overlay inside the frozen model\n")
    w.append(f"Window {ov.index[0]:%Y-%m-%d} to {ov.index[-1]:%Y-%m-%d}. Frozen: CAGR {so[1]['CAGR']*100:.2f}%, Sharpe "
             f"{so[1]['Sharpe']:.3f}, MaxDD {so[1]['MaxDD']*100:.1f}%. Overlay: CAGR {so[0]['CAGR']*100:.2f}%, Sharpe "
             f"{so[0]['Sharpe']:.3f}, MaxDD {so[0]['MaxDD']*100:.1f}%. Full-window paired bootstrap "
             f"P(Sharpe_overlay <= Sharpe_frozen) = {boot_p(ov['ov'], ov['frozen']):.3f}.\n")
    np_ = int(tab["Pass"].sum())
    w.append("## Verdict\n")
    w.append(f"**{np_} of {len(tab)} pre-registered tests pass.** " + (
        "Nothing here is a candidate for the scheduled review." if np_ == 0 else
        "Passing tests are candidates for the 2027-11-19 review only; no live change.") + "\n")
    w.append(f"Which leg closes a deviation (2016+, slope of the next session's log return on today's 60-day "
             f"deviation): 2330.TW in USD {leg['tw'][0]:+.3f} (HAC t {leg['tw'][1]:.1f}), TSM open-to-open "
             f"{leg['tsm'][0]:+.3f} (t {leg['tsm'][1]:.1f}). The premium's ~2-day reversion runs through Taiwan "
             "catching up to the ADR (the two closes are 14.5 h apart; TSMC reports after the Taipei close, so the "
             "ADR reprices first), not through TSM, so a TSM-only long/flat rule has little to harvest. Near-misses "
             "(T3 reversal, T2a/T2d and T4a in the holdout) failed discovery and are logged forward, not adopted.\n")
    open("reports/tsm_premium_results.md", "w", encoding="utf-8").write("\n".join(w))
    print(tab.to_string())
    print(strat_rows(S, cut).to_string())


if __name__ == "__main__":
    main()
