"""Free alternative data: do insider filings (SEC Form 4), FINRA short interest, or TSMC monthly revenue predict returns?
Writes reports/altdata_results.md.  Run: python altdata_study.py [--refresh]

Each predictor is tested in one pre-specified form. Every date is the date the data became PUBLIC, mapped to the first
US close at which the model (close fills) could act on it. Pass = Holm p < 0.05 across ALL tests AND the same sign in
both halves (MATH.md §6). Passing predictors would then be tried as an overlay on the shipped model.
"""
import io
import os
import re
import sys
import time
import zipfile

import numpy as np
import pandas as pd
import requests

from backtest import prices, rank_ic
from correlations import holm, pval, resid
from macro import hac_slope_t
from model import AI_CHAIN, BENCH, names_of

SEC_UA = {"User-Agent": "quant-research-script admin@example.com"}  # SEC requires a descriptive UA; generic on purpose
CACHE = "data/altdata_{}.pkl"  # data/ is gitignored and written only by this script, so read_pickle is safe
REFRESH = "--refresh" in sys.argv

# Issuer CIKs, including predecessors (Google Inc. before the 2015 Alphabet reorg; Avago / Broadcom Ltd before 2018).
# TSM is a foreign private issuer: its insiders do not file Form 4, so it has no insider data.
CIKS = {320193: "AAPL", 1045810: "NVDA", 789019: "MSFT", 1652044: "GOOGL", 1288776: "GOOGL", 1018724: "AMZN",
        1730168: "AVGO", 1671933: "AVGO", 1441634: "AVGO", 1326801: "META", 1318605: "TSLA", 2488: "AMD",
        1341439: "ORCL", 1181412: "SPCX"}


def cached(name, fn):
    path = CACHE.format(name)
    if os.path.exists(path) and not REFRESH:
        return pd.read_pickle(path)
    out = fn()
    os.makedirs("data", exist_ok=True)
    out.to_pickle(path)
    return out


def sec_get(url):
    time.sleep(0.15)  # < 10 req/s
    r = requests.get(url, headers=SEC_UA, timeout=120)
    return r if r.status_code == 200 else None


# ---------------------------------------------------------------------------------------------- 1. insider filings
def fetch_insider():
    """One row per Form 4 from the SEC's quarterly 'Insider Transactions Data Sets' (parsed Form 3/4/5 XML),
    restricted to our issuers. Acceptance timestamps come from the issuers' EDGAR submissions JSON."""
    rd = lambda z, f: pd.read_csv(z.open(f), sep="\t", dtype=str, quoting=3, on_bad_lines="skip")
    rows = []
    for y in range(2014, pd.Timestamp.today().year + 1):
        for q in range(1, 5):
            r = sec_get(f"https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/{y}q{q}_form345.zip")
            if r is None:
                continue
            z = zipfile.ZipFile(io.BytesIO(r.content))
            sub = rd(z, "SUBMISSION.tsv")
            sub = sub[(sub.DOCUMENT_TYPE == "4") & sub.ISSUERCIK.astype(int).isin(CIKS)]
            acc = set(sub.ACCESSION_NUMBER)
            own = rd(z, "REPORTINGOWNER.tsv").query("ACCESSION_NUMBER in @acc")
            tr = rd(z, "NONDERIV_TRANS.tsv").query("ACCESSION_NUMBER in @acc")
            fn = rd(z, "FOOTNOTES.tsv").query("ACCESSION_NUMBER in @acc")
            offdir = own.groupby("ACCESSION_NUMBER").RPTOWNER_RELATIONSHIP.agg(
                lambda s: s.fillna("").str.contains("Director|Officer").any())
            codes = tr.groupby("ACCESSION_NUMBER").TRANS_CODE.agg(set)
            plan_txt = pd.concat([fn[["ACCESSION_NUMBER", "FOOTNOTE_TXT"]].rename(columns={"FOOTNOTE_TXT": "t"}),
                                  sub[["ACCESSION_NUMBER", "REMARKS"]].rename(columns={"REMARKS": "t"})])
            plan = plan_txt.groupby("ACCESSION_NUMBER").t.agg(
                lambda s: s.fillna("").str.contains(r"10b5-?1|10b-5-?1|10b5 ?- ?1", case=False).any())
            d = sub.set_index("ACCESSION_NUMBER")
            rows.append(pd.DataFrame({
                "ticker": d.ISSUERCIK.astype(int).map(CIKS), "filed": pd.to_datetime(d.FILING_DATE, format="%d-%b-%Y"),
                "offdir": offdir.reindex(d.index, fill_value=False),
                "P": codes.reindex(d.index).map(lambda c: isinstance(c, set) and "P" in c),
                "S": codes.reindex(d.index).map(lambda c: isinstance(c, set) and "S" in c),
                # 10b5-1 flag: checkbox (from Apr 2023) or a footnote/remark citing the rule. Filing-level, so a filing
                # with plan and non-plan sales counts as plan (conservative for "discretionary").
                "plan": d.get("AFF10B5ONE", pd.Series("0", index=d.index)).fillna("0").str.lower().isin(["1", "true"])
                        | plan.reindex(d.index, fill_value=False)}))
            print(f"insider {y}q{q}: {len(d)} Form 4s", flush=True)
    ins = pd.concat(rows)
    ins = ins[~ins.index.duplicated()]
    acc_t = {}
    for cik in CIKS:
        j = sec_get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()
        pages = [j["filings"]["recent"]] + [sec_get(f"https://data.sec.gov/submissions/{f['name']}").json()
                                            for f in j["filings"]["files"]]
        for p in pages:
            acc_t.update(zip(p["accessionNumber"], p["acceptanceDateTime"]))
    t = pd.to_datetime(ins.index.map(acc_t), utc=True)  # EDGAR's acceptanceDateTime is true UTC (checked vs index page)
    ins["accepted_et"] = t.tz_convert("America/New_York").tz_localize(None)
    return ins


def entry_dates(ts, days, cutoff_hour=16):
    """First close at which a timestamp is tradable: same day if a trading day and before 16:00 ET, else next session.
    Missing timestamps (date only) are treated as after-close, i.e. the next session (conservative)."""
    d = ts.dt.normalize()
    same = ts.dt.hour.lt(cutoff_hour) & d.isin(days) & ts.dt.hour.notna()
    pos = days.searchsorted(d, side="right")
    nxt = pd.Series([days[p] if p < len(days) else pd.NaT for p in pos], index=ts.index)
    return d.where(same, nxt)


def nw_mean_t(y, lags):
    """Mean of y with a Newey-West t-stat (handles overlap between nearby events at h > 1)."""
    u = y - y.mean()
    s = (u @ u + sum(2 * (1 - l / (lags + 1)) * (u[l:] @ u[:-l]) for l in range(1, lags + 1))) / len(y)
    return y.mean(), y.mean() / np.sqrt(s / len(y))


def event_tests(name, ev, res, horizons=(1, 5, 20)):
    """ev: DataFrame [ticker, entry]. Forward residual return from the entry close, averaged per date first
    (many filings land on the same day), then a NW t across dates."""
    out = []
    ev = ev.drop_duplicates()
    for h in horizons:
        fwd = res.rolling(h).sum().shift(-h)
        v = pd.Series([fwd.at[e, tk] if e in fwd.index else np.nan for tk, e in zip(ev.ticker, ev.entry)], index=ev.entry)
        g = v.dropna().groupby(level=0).mean().sort_index()
        if len(g) < 10:
            out.append(dict(Test=name, Horizon=f"{h}d", n=len(g), effect=np.nan, t=np.nan, p=np.nan, h1=np.nan, h2=np.nan))
            continue
        m, t = nw_mean_t(g.values, max(h - 1, 0))
        half = len(g) // 2
        out.append(dict(Test=name, Horizon=f"{h}d", n=len(g), effect=m * 1e4, t=t, p=pval(t),
                        h1=g.iloc[:half].mean() * 1e4, h2=g.iloc[half:].mean() * 1e4,
                        events=int(v.notna().sum())))
    return out


# ---------------------------------------------------------------------------------------------- 2. short interest
def fetch_short_interest(tickers):
    url = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
    rows = []
    for tk in tickers:
        body = {"limit": 5000, "compareFilters": [{"compareType": "EQUAL", "fieldName": "symbolCode", "fieldValue": tk}],
                "fields": ["settlementDate", "currentShortPositionQuantity", "previousShortPositionQuantity",
                           "daysToCoverQuantity"]}
        r = requests.post(url, json=body, headers={"Accept": "application/json"}, timeout=60)
        r.raise_for_status()
        d = pd.DataFrame(r.json() if r.text.strip() else [])
        if len(d):
            rows.append(d.assign(ticker=tk))
        time.sleep(0.5)
    d = pd.concat(rows)
    d["settlementDate"] = pd.to_datetime(d.settlementDate)
    return d.drop_duplicates(["ticker", "settlementDate"], keep="last")


# ---------------------------------------------------------------------------------------------- 3. TSMC revenue
def fetch_tsmc():
    """TSMC (2330) monthly consolidated revenue, NT$ thousands, from the TWSE MOPS monthly revenue tables."""
    rows = []
    for per in pd.period_range("2013-10", pd.Timestamp.today().to_period("M") - 1, freq="M"):
        url = f"https://mopsov.twse.com.tw/nas/t21/sii/t21sc03_{per.year - 1911}_{per.month}_0.html"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        time.sleep(1.0)
        if r.status_code != 200:
            continue
        m = re.search(r"<td align=center>2330</td><td align=left>[^<]*</td>"
                      r"<td nowrap>\s*([\d,]+)</td><td nowrap>\s*([\d,]+)</td><td nowrap>\s*([\d,]+)</td>",
                      r.content.decode("big5", errors="ignore"))
        if m:
            cur, _, ly = (float(x.replace(",", "")) for x in m.groups())
            rows.append(dict(month=per.to_timestamp(), revenue=cur, revenue_ly=ly))
            print(f"TSMC {per}: {cur:,.0f}", flush=True)
    return pd.DataFrame(rows).set_index("month")


# ---------------------------------------------------------------------------------------------- main
def main():
    px = prices()
    days = px.index
    names = [c for c in names_of(px) if px[c].notna().any()]
    rets = px.pct_change(fill_method=None)
    res = resid(rets[names + [BENCH]])
    rows, notes = [], []

    # 1. insider
    ins = cached("insider", fetch_insider)
    ins["entry"] = entry_dates(ins.accepted_et, days)
    ins.loc[ins.accepted_et.isna(), "entry"] = entry_dates(ins.loc[ins.accepted_et.isna(), "filed"] + pd.Timedelta(hours=23), days)
    od = ins[ins.offdir & ins.entry.notna()]
    buys = od[od.P][["ticker", "entry"]]
    sells = od[od.S & ~od.plan][["ticker", "entry"]]
    rows += event_tests("Insider open-market purchase (code P, officer/director)", buys, res)
    rows += event_tests("Insider discretionary sale (code S, not 10b5-1, officer/director)", sells, res)
    ins_counts = od.assign(buy=od.P, sale_disc=od.S & ~od.plan, sale_plan=od.S & od.plan).groupby("ticker")[
        ["buy", "sale_disc", "sale_plan"]].sum().astype(int)
    notes.append(f"Form 4s for our issuers: {len(ins)} ({ins.filed.min().date()} to {ins.filed.max().date()}); "
                 f"acceptance time found for {ins.accepted_et.notna().mean():.1%}.")

    # 2. short interest: FINRA publishes ~7 business days after settlement, after the close -> act at settlement + 8 sessions
    si = cached("short_interest", lambda: fetch_short_interest([n for n in names if n != "SPCX"] + ["SPCX"]))
    si = si[si.ticker.isin(names)]
    si["entry"] = [days[min(days.searchsorted(s) + 8, len(days) - 1)] for s in si.settlementDate]
    si["chg"] = si.currentShortPositionQuantity / si.previousShortPositionQuantity.replace(0, np.nan) - 1
    entries = sorted(si.entry.unique())
    cum = res.fillna(0).cumsum()
    fwd = (cum.reindex(entries).shift(-1) - cum.reindex(entries)).iloc[:-1]  # entry close -> next entry close
    fwd = fwd.where(res.notna().rolling(5).sum().reindex(fwd.index) > 0)
    for col, label in (("chg", "Short interest % change"), ("daysToCoverQuantity", "Days to cover")):
        sc = si.pivot_table(index="entry", columns="ticker", values=col).reindex(fwd.index)
        sc = sc.where(sc.notna().sum(axis=1) >= 5, axis=0)
        ic, t, n = rank_ic(sc, fwd[sc.columns])
        half = sc.index[len(sc) // 2]
        h1 = rank_ic(sc.loc[:half], fwd.loc[:half, sc.columns])[0]
        h2 = rank_ic(sc.loc[half:], fwd.loc[half:, sc.columns])[0]
        rows.append(dict(Test=f"{label} -> next-period residual (rank IC)", Horizon="~half month", n=n,
                         effect=ic, t=t, p=pval(t), h1=h1, h2=h2, events=n))
    notes.append(f"FINRA short interest: {si.settlementDate.min().date()} to {si.settlementDate.max().date()}, "
                 f"{si.ticker.nunique()} names.")

    # 3. TSMC: YoY growth surprise vs the prior 3 months' average YoY; released by the 10th of the next month
    ts = cached("tsmc", fetch_tsmc)
    yoy = ts.revenue / ts.revenue_ly - 1
    surprise = (yoy - yoy.shift(1).rolling(3).mean()).dropna()
    surprise = surprise[surprise.index.to_series().diff().dt.days.fillna(31).le(31)]  # no gaps inside the window
    rel = pd.Series(surprise.index + pd.DateOffset(months=1, days=9), index=surprise.index)  # the 10th of next month
    entry = pd.Series([days[p] if p < len(days) else pd.NaT for p in days.searchsorted(rel)], index=surprise.index)
    tgt = {**{n: rets[n] for n in ("TSM", "NVDA", "AVGO", "AMD")}, "AI-chain basket (EW)": rets[AI_CHAIN].mean(axis=1)}
    for tn, r in tgt.items():
        for h in (1, 5, 20):
            f = r.rolling(h).sum().shift(-h)
            d = pd.DataFrame({"x": surprise.values, "y": f.reindex(entry.values).values}, index=entry.values).dropna()
            xs = (d.x - d.x.mean()) / d.x.std()
            b, t = hac_slope_t(d.y.values, xs.values, lags=2)
            half = len(d) // 2
            b1 = hac_slope_t(d.y.values[:half], xs.values[:half], 2)[0]
            b2 = hac_slope_t(d.y.values[half:], xs.values[half:], 2)[0]
            rows.append(dict(Test=f"TSMC revenue surprise -> {tn} (bp per 1σ)", Horizon=f"{h}d", n=len(d),
                             effect=b * 1e4, t=t, p=pval(t), h1=b1 * 1e4, h2=b2 * 1e4, events=len(d)))
    notes.append(f"TSMC monthly revenue: {ts.index.min():%Y-%m} to {ts.index.max():%Y-%m} ({len(ts)} months).")

    tab = pd.DataFrame(rows)
    ok = tab.p.notna()
    tab.loc[ok, "Holm p"] = holm(tab.p[ok]).values
    tab["Pass"] = (tab["Holm p"] < 0.05) & (np.sign(tab.h1) == np.sign(tab.h2))

    tsmc_now = pd.DataFrame({"YoY": yoy, "surprise": yoy - yoy.shift(1).rolling(3).mean()}).tail(6)
    out = [
        f"# Alternative data: insiders, short interest, TSMC revenue\n\nGenerated by altdata_study.py on {days[-1].date()}. "
        f"{int(ok.sum())} tests, Holm-corrected across all of them; pass also needs the same sign in both halves.\n",
        "Effect units: insider rows = mean forward residual return (bp, vs rolling 60d QQQ beta); short interest rows = "
        "mean cross-sectional Spearman IC; TSMC rows = raw forward return in bp per 1σ of surprise. "
        "h1/h2 = the same effect in the first/second half of the sample. Insider n = distinct event dates "
        "(events = name-dates); short interest n = publication periods.\n",
        tab.drop(columns="p").to_markdown(index=False, floatfmt=".3f"),
        f"\n**{int(tab.Pass.sum())} of {int(ok.sum())} pass.**\n",
        "## Overlay test\n",
        "Nothing passed, so there is nothing to overlay on the shipped model." if not tab.Pass.any() else
        "SEE PASSING ROWS: overlay not yet built.",
        "\n## Insider event counts (officer/director Form 4s, by issuer)\n",
        ins_counts.to_markdown(),
        "\n## Latest TSMC readings\n",
        tsmc_now.to_markdown(floatfmt=".3f"),
        "\n## Data sources and timing\n",
        *[f"- {n}" for n in notes],
        "- Insider: SEC 'Insider Transactions Data Sets' (quarterly parsed Form 3/4/5, sec.gov/dera) + EDGAR submissions JSON "
        "for acceptance timestamps. Info date = acceptance time (ET); after 16:00 or a non-trading day -> next session's close. "
        "Officer/director = reporting-owner relationship contains Director or Officer. 10b5-1 = the Form 4 checkbox "
        "(from April 2023) or any footnote/remark citing Rule 10b5-1; earlier plans not mentioned in footnotes are "
        "misclassified as discretionary. TSM files no Form 4 (foreign private issuer).",
        "- Short interest: FINRA Query API `consolidatedShortInterest` (free, no key). History starts Dec-2017 for these names. "
        "Publication date is not in the data; FINRA disseminates ~7 business days after settlement, after the close, so the "
        "signal is used at the close of settlement + 8 sessions. Forward return = residual return to the next such close. "
        "Dates with fewer than 5 names are dropped. yfinance `Ticker.info` short fields are current-only and not used.",
        "- TSMC: TWSE MOPS monthly revenue tables (mopsov.twse.com.tw t21sc03, consolidated revenue, TWSE code 2330); "
        "investor.tsmc.com is behind a bot wall. Release date = the 10th of the following month (the legal deadline; TSMC "
        "releases on or before it in Taipei, i.e. before the US open), so the signal is used at the close of the first US "
        "session on/after the 10th. If TSMC released earlier, this is late, never early. The same-day reaction on the "
        "release day is deliberately not counted (not tradable at close fills).",
        "- One pre-specified form per predictor; no lookback or threshold tuning.",
    ]
    os.makedirs("reports", exist_ok=True)
    with open("reports/altdata_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
