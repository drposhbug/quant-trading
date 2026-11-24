"""Earnings as an event: the run-up, holding through the announcement, and the drift after the reaction.
Writes reports/earnings_event_results.md.   Run: python earnings_event_study.py

The owner (2026-11-23): "can you find some correlation on certain event days, like holding for earnings".
The project's first event study (events_study.py, 12 megacaps, about 510 announcements) tested the calendar days
(Fed days, turn of the month, pre-holiday: nothing) and left two earnings hints that were too few events to pass:
a run-up in the 5 sessions before (+0.49%, t 2.3) and a drift in the direction of the reaction (+0.71% over 20
sessions, t 2.4). Now there are about forty times as many events. Written before the first run.
- Events: every scheduled earnings date of today's S&P 500 companies since 2016 (lab/earnings.csv) for which the
  SEC has an earnings filing within a day (lab/filings_8k.csv, item 2.02). The filing's acceptance time fixes the
  reaction session: the same session if it became public before 16:00 New York, otherwise the next one.
- Every return is the stock's minus the average index member's over the same sessions.
    run-up        the 5 sessions ending at the close before the reaction session
    holding       from the close before the reaction session to its close: "holding for earnings"
    drift         from the open after the reaction session to the close 21 sessions later, in the direction of the
                  reaction (plus = the stock kept going the way it jumped)
- Events in the same earnings season share their luck, so each calendar quarter is one observation: the events
  of a quarter are averaged, and the t is taken over the quarters (about 43).
- Three deciding numbers. Each is real if its t is 3 or more with the same sign in both halves of the quarters;
  a hint at 2 or more. With three readings one hint is likely by luck.
- Read beside them: how big the reaction is against a normal day, and the same three numbers for the bot's names.
Limit: only companies still in the index today, so companies that fell out after bad results are missing.
"""
import math
import warnings

import numpy as np
import pandas as pd

import daily_calls as d
from model import UNIVERSE


def main():
    warnings.simplefilter("ignore")
    raw, member, uni, outside = d.panel()
    c, o = raw["c"].ffill(limit=21), raw["o"]
    m = member if member is not None else c.notna()
    idx = c.index
    f = pd.read_csv("lab/filings_8k.csv")
    f = f[(f["form"] == "8-K") & f["items"].astype(str).str.contains("2.02", regex=False) & f["ticker"].isin(c.columns)]
    t = pd.to_datetime(f["accepted_ny"].astype(str).str.slice(0, 19))
    pos = idx.searchsorted(t.dt.normalize())
    same = np.zeros(len(f), dtype=bool)
    ok = pos < len(idx)
    same[ok] = idx[pos[ok]] == t.dt.normalize()[ok].values
    f = f.assign(react=pos + (same & (t.dt.hour >= 16).values))
    filed = {k: np.sort(g["react"].values) for k, g in f.groupby("ticker")}
    e = pd.read_csv("lab/earnings.csv", parse_dates=["date"])
    e = e[e["ticker"].isin(filed) & (e["date"] <= idx[-1])]
    rows = []
    for tk, day in zip(e["ticker"], e["date"]):
        q, r = idx.searchsorted(day), filed[tk]
        j = np.searchsorted(r, q - 1)
        if j < len(r) and r[j] <= q + 1:
            rows.append((tk, int(r[j])))
    ev = pd.DataFrame(rows, columns=["ticker", "p"]).drop_duplicates()
    ev = ev[(ev["p"] > 70) & (ev["p"] < len(idx))]
    col = c.columns.get_indexer(ev["ticker"])
    p = ev["p"].values

    def excess(a, b):  # each stock's return from frame a to frame b (same rows), minus the average member's
        r = (b / a - 1).where(m)
        return r.sub(r.mean(axis=1), axis=0).values

    hold_m, run_m = excess(c.shift(1), c), excess(c.shift(6), c.shift(1))
    drift_m = excess(o.shift(-1), c.shift(-21))
    hold, run = hold_m[p, col], run_m[p, col]
    drift = np.sign(hold) * drift_m[p, col]
    normal = pd.DataFrame(hold_m, index=idx).rolling(60).std().shift(1).values[p, col]
    ev = ev.assign(run=run, hold=hold, drift=drift, size=np.abs(hold) / normal, quarter=idx[p].to_period("Q"), book=ev["ticker"].isin(UNIVERSE).values)

    def line(frame, name):
        qm = frame.groupby("quarter")[name].mean().dropna()
        h = len(qm) // 2
        return {"events": int(frame[name].notna().sum()), "quarters": len(qm), "average per event": frame[name].mean(), "t over quarters": qm.mean() / (qm.std() / math.sqrt(len(qm))),
                "1st half": qm.iloc[:h].mean(), "2nd half": qm.iloc[h:].mean(), "share above zero": (frame[name].dropna() > 0).mean()}

    labels = {"run": "run-up: 5 sessions before", "hold": "holding through the announcement", "drift": "drift: 21 sessions after, in the reaction's direction"}
    table = pd.DataFrame({f"{lab} | S&P 500": line(ev, k) for k, lab in labels.items()} | {f"{lab} | the bot's names": line(ev[ev["book"]], k) for k, lab in labels.items()}).T
    out = ["# Earnings as an event\n",
           f"Rules written in earnings_event_study.py before the run. {len(ev)} announcements of {ev['ticker'].nunique()} companies, {idx[p.min()].date()} to {idx[p.max()].date()}. "
           "Returns are the stock's minus the average index member's.\n", table.to_markdown(floatfmt=".4f"), ""]
    for k, lab in labels.items():
        r = table.loc[f"{lab} | S&P 500"]
        same_sign = r["1st half"] * r["2nd half"] > 0
        v = "real" if abs(r["t over quarters"]) >= 3 and same_sign else "a hint" if abs(r["t over quarters"]) >= 2 and same_sign else "no pattern"
        out.append(f"- **{lab}**: {v} ({r['average per event']:+.2%} an event, t {r['t over quarters']:+.1f}).")
    out.append(f"\n- Size of the reaction: on the reaction session a stock moved {ev['size'].median():.1f} times its normal daily move (typical event); "
               f"one event in ten moved more than {ev['size'].quantile(0.9):.1f} times. The typical move was {ev['hold'].abs().median():.1%} against the average stock, up {np.mean(ev['hold'].dropna() > 0):.0%} of the time.")
    with open("reports/earnings_event_results.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
