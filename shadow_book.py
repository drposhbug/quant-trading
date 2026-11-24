"""Candidate versions of the bot's book, run in shadow. Writes reports/shadow_versions.md.
Run: python shadow_book.py   (workflow mlp-log, every weekday after the close)

A candidate is a change to the bot's rule that has been tested on the past and not switched on. In shadow it makes
the same decisions it would make live, on each new day, and its result is kept beside the live book's. Nothing here
sends an order. Only sessions from START on count, so no candidate can borrow a good-looking past.
The numbers are computed from the rules and daily prices (5 bp costs, idle money in T-bills), not from the
account's fills; track.py compares the real account with the live rule.
Candidates (VERSIONS.md has their history and their results on the past):
  B2.2  half after a shock          half of every position for 21 sessions after the market (QQQ) moves more than
                                    2.5 of its normal daily moves either way (news_stop_odds.py)
  B2.3  trim amplifiers after shock half weight, for the same 21 sessions, only in the third of names that fall
                                    hardest on the market's down days (downside_beta_odds.py)
  C1.0  5% in Bitcoin               95% in the live book and 5% in Bitcoin, held; a choice about exposure that no
                                    test can settle (crypto_trend_odds.py), tracked so its effect is seen on new days
  B3.0  steady 1.25x                the live book with a quarter more, on borrowed money at the T-bill rate + 1.5%
                                    (managed_exposure_odds.py): the calculated risk that cleared its bars
Sleeves (separate small books, not changes to the bot's book; from meme_crypto_study.py, lists chosen with hindsight):
  S1.0  crypto stocks, nights only  bought at each close and sold at the next open, equal weights, 10 bp a night
  S2.0  meme stocks, nights only    the same on the meme list
A candidate goes live in one of two ways, both written down before the fact (VERSIONS.md): it passes the growth bar
in the monthly self-review three times running, or the owner chooses it as a risk setting.
"""
import numpy as np
import pandas as pd

from daily_calls import bars
from downside_beta_odds import downside
from managed_exposure_odds import financed
from meme_crypto_study import CRYPTO, MEME
from model import BENCH, UNIVERSE, backtest_returns
from monitor import tilted
from news_stop_odds import signals

START, HOLD = "2026-11-24", 21


def main():
    b = bars([n for n in UNIVERSE] + [BENCH, "BIL"])
    now = pd.Timestamp.now("America/New_York")
    if b["c"].index[-1].date() == now.date() and now.hour < 16:
        b = {k: f.iloc[:-1] for k, f in b.items()}  # the session is still open
    cols = [n for n in UNIVERSE if n in b["c"]] + [BENCH]
    px, op, vol = b["c"][cols], b["o"][cols], b["v"][[n for n in cols if n != BENCH]]
    rf = b["c"]["BIL"].ffill().pct_change().fillna(0)
    w = tilted(px)
    shock = signals(px, op, vol)["any"]
    after = shock.astype(float).rolling(HOLD, min_periods=1).max() > 0
    wide, amp = pd.DataFrame({k: after for k in w.columns}), downside(px).rank(axis=1, pct=True) > 2 / 3
    books = {"B2.1 live book (trend tilt, fully invested)": w, "B2.2 half after a shock": w * np.where(wide, 0.5, 1.0),
             "B2.3 trim amplifiers after a shock": w * np.where(amp & wide, 0.5, 1.0), "B3.0 steady 1.25x (borrowing a quarter)": w * 1.25}
    ret = {k: (backtest_returns(px, wt) + financed(wt.sum(axis=1), rf, 0.015)).loc[START:] for k, wt in books.items()}
    live = ret["B2.1 live book (trend tilt, fully invested)"]
    try:  # C1.0: 5% of the account in Bitcoin, simply held; the rest in the live book
        import yfinance as yf
        btc = yf.download("BTC-USD", start="2026-10-01", auto_adjust=True, progress=False, threads=False)["Close"].squeeze()
        ret["C1.0 the live book with 5% in Bitcoin (held)"] = 0.95 * live + 0.05 * btc.reindex(px.index, method="ffill").pct_change().reindex(live.index).fillna(0)
    except Exception as err:
        print(f"Bitcoin slice not tracked today: {err!r}")
    day, last = px.index[-1], shock[shock].index[-1] if shock.any() else None
    left = HOLD - (len(px.loc[last:]) - 1) if last is not None else 0
    state = (f"**In shock mode today: yes.** The latest market shock was {last.date()} ({px[BENCH].pct_change().loc[last]:+.1%}); the candidates hold less for {left} more session{'s' if left != 1 else ''}."
             if left > 0 else f"**In shock mode today: no.** The latest market shock was {last.date() if last is not None else 'never'}.")
    names = [n for n in w.columns if bool(amp.iloc[-1].get(n, False))]
    out = ["# Candidate versions of the bot, in shadow\n",
           f"Updated after the close on {day.date()}. Counting from {START}. Computed from the rules and daily prices, not from the account's fills. Nothing here trades.\n",
           state + f" The names that fall hardest when the market falls, as measured today: {', '.join(names) if names else 'not enough down days yet'}.\n"]
    if len(live) == 0:
        out.append(f"No session has been counted yet: the first is {START}.")
    else:
        dd = lambda r: ((1 + r).cumprod() / (1 + r).cumprod().cummax() - 1).min()
        out += ["| Version | Sessions | Return since the start | Against the live book | Worst fall | Worst session | Share invested today |", "|---|---|---|---|---|---|---|"]
        for k, r in ret.items():
            tot = (1 + r).prod() - 1
            out.append(f"| {k} | {len(r)} | {tot:+.2%} | {tot - ((1 + live).prod() - 1):+.2%} | {dd(r):.2%} | {r.min():+.2%} | {f'{books[k].iloc[-1].sum():.0%}' if k in books else '95% stocks, 5% Bitcoin'} |")
        out.append("\nA few weeks of this say almost nothing: the candidates differ from the live book only after shocks. Their record on the past is in VERSIONS.md.")
    s = bars(sorted(set(MEME + CRYPTO)))
    s = {k: f.loc[:day] for k, f in s.items()}
    ok = [n for n in s["c"].columns if s["c"][n].notna().sum() >= 250]
    night, full = s["o"][ok] / s["c"][ok].shift(1) - 1, s["c"][ok].pct_change()
    pick = lambda lst: [n for n in lst if n in ok]
    sleeves = {"S1.0 crypto stocks, nights only (after 10 bp a night)": night[pick(CRYPTO)].mean(axis=1) - 0.0010,
               "S2.0 meme stocks, nights only (after 10 bp a night)": night[pick(MEME)].mean(axis=1) - 0.0010,
               "for comparison: crypto stocks held day and night": full[pick(CRYPTO)].mean(axis=1),
               "for comparison: meme stocks held day and night": full[pick(MEME)].mean(axis=1)}
    out += ["\n## Sleeves in shadow: holding only overnight\n",
            "Separate small books, not part of the bot. On the past, meme and crypto stocks made their gains between the close and the next open and "
            "lost during the day (reports/meme_crypto_results.md). The lists were chosen with hindsight, so only these new days count.\n"]
    if len(live):
        out += ["| Sleeve | Sessions | Return since the start | Worst session |", "|---|---|---|---|"]
        out += [f"| {k} | {len(r.loc[START:].dropna())} | {(1 + r.loc[START:].dropna()).prod() - 1:+.2%} | {r.loc[START:].min():+.2%} |" for k, r in sleeves.items()]
    else:
        out.append(f"No session has been counted yet: the first is {START}.")
    out += ["\n## How a candidate becomes the bot's rule\n",
            "1. Growth: the monthly self-review (learn.py) re-tests it against the live book; three passes in a row flag it for switching on.",
            "2. Risk: the owner may choose a candidate that loses less but grows slower. That is a preference, not something a test can decide.",
            "Either way the change gets a version number and a line in VERSIONS.md, and the old version stays one switch away."]
    with open("reports/shadow_versions.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[:4]))


if __name__ == "__main__":
    main()
