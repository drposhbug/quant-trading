"""Monthly self-review: the bot re-tests its own rules on fresh prices and switches by bars fixed in advance.
Run: python learn.py   (.github/workflows/learn.yml runs it early each month; FORCE=1 repeats a month)

Written 2026-11-23. What it may change on its own, both already built into monitor.live_weights:
  exposure  fully invested <-> the original cut-loss engine. Fully invested stays while P(it grows faster) > 0.5 on
            BOTH ^NDX 1986+ and the end-2014 list (the 2026-11-22 rule, growth_odds.py).
  tilt      long-trend tilt on <-> off. On while P(tilted grows faster than untilted) >= 0.5 on the end-2014 list
            (tilt_odds.py).
A setting changes only after 3 monthly reviews in a row ask for the same change, so one odd month cannot flip the book.
Every other rule tested so far (equal weight, buying dips, short trends, the learning rule, five selling rules) is
re-tested against its own pre-registered bar. One that passes 3 reviews in a row is flagged on Discord for wiring in;
it is never switched on automatically, because its live code does not exist yet.
The bot cannot invent rules. New ideas still come from a person or a model session and enter through a test like these.
"""
import csv
import datetime as dt
import json
import os

import numpy as np

import exit_odds
import growth_odds
import mini_trend_odds
import tilt_odds
from monitor import CONFIG, DEFAULT, discord

STATE, LOG, NEED = "signals/learn_state.json", "signals/learn_log.csv", 3
TREND = "trend: heavier in what has been rising"
WORDS = {"exposure": {"full": "fully invested", "engine": "on the cut-loss rules"}, "tilt": {"long": "on", "none": "off"}}


def step(current, desired, streak, need=NEED):
    """(setting, streak) after one review: switch only when `need` reviews in a row ask for the same change."""
    if desired == current:
        return current, 0
    return (desired, 0) if streak + 1 >= need else (current, streak + 1)


def _check():
    assert step("long", "long", 2) == ("long", 0)   # agreement clears a pending switch
    assert step("long", "none", 0) == ("long", 1) and step("long", "none", 1) == ("long", 2)
    assert step("long", "none", 2) == ("none", 0)   # third review in a row switches


def _load(path, default):
    try:
        return {**default, **json.load(open(path))}
    except (OSError, ValueError):
        return dict(default)


def main():
    _check()
    today = dt.date.today()
    cfg, state = _load(CONFIG, DEFAULT), _load(STATE, {"streak": {}})
    if state.get("month") == f"{today:%Y-%m}" and os.environ.get("FORCE") != "1":
        return print("already reviewed this month")  # several cron days back each other up; only the first counts
    streak = state["streak"]

    def run(study):  # same seed as a stand-alone run, so a study's numbers do not depend on what ran before it
        growth_odds.rng = np.random.default_rng(7)
        return study.main()

    p_full = run(growth_odds)[1].filter(like="decides", axis=0)["P(arm grows faster)"]
    tt, tok = run(tilt_odds)
    p_tilt = tt.loc[f"{TREND} | end-2014 list (decides)", "P(arm grows faster)"]
    passing = sorted([n for n in tok if n != TREND] + list(run(mini_trend_odds)[1]) + list(run(exit_odds)[1]))

    want = {"exposure": "full" if (p_full > 0.5).all() else "engine", "tilt": "long" if p_tilt >= 0.5 else "none"}
    changed, pending = [], []
    for k, v in want.items():
        new, streak[k] = step(cfg[k], v, streak.get(k, 0))
        if new != cfg[k]:
            changed.append(f"{k} is now {WORDS[k][new]}")
        elif streak[k]:
            pending.append(f"{k}: review {streak[k]} of {NEED} asking to switch to {WORDS[k][v]}")
        cfg[k] = new
    for n in [k for k in streak if k.startswith("rule:") and k[5:] not in passing]:
        del streak[n]
    for n in passing:
        streak["rule:" + n] = streak.get("rule:" + n, 0) + 1
    ready = [n for n in passing if streak["rule:" + n] == NEED]

    os.makedirs("signals", exist_ok=True)
    for path, obj in ((CONFIG, cfg), (STATE, {"streak": streak, "month": f"{today:%Y-%m}"})):
        with open(path + ".tmp", "w") as f:  # write-then-rename: the trading bot reads CONFIG
            json.dump(obj, f, indent=1)
        os.replace(path + ".tmp", path)
    new_log = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new_log:
            w.writerow(["date", "exposure", "tilt", "p_full_min", "p_tilt", "passing", "changed"])
        w.writerow([today, cfg["exposure"], cfg["tilt"], round(float(p_full.min()), 3), round(float(p_tilt), 3), "; ".join(passing), "; ".join(changed)])

    discord(f"🧠 **Monthly self-check, {today:%b %d}**\nThe bot re-tested its own rules on fresh prices.\n\n"
            f"• **Fully invested vs the cut-loss rules:** fully invested made more money in {p_full.min():.0%} to {p_full.max():.0%} "
            f"of simulated histories. The account is **{WORDS['exposure'][cfg['exposure']]}**.\n"
            f"• **Trend tilt** (more in what has been rising for months): ahead in {p_tilt:.0%}. The tilt is **{WORDS['tilt'][cfg['tilt']]}**.\n"
            f"• **12 other rules re-tested** (equal weight, buying dips, short trends, selling rules): "
            + ("none passed." if not passing else "passed this month: " + ", ".join(passing) + ".") + "\n\n"
            + ("✅ **Changed:** " + "; ".join(changed) + "." if changed else "Nothing changed.")
            + ("\n⏳ " + "; ".join(pending) + "." if pending else "")
            + (f"\n🔔 Passed {NEED} reviews in a row and is ready to be built into the bot: " + ", ".join(ready) + "." if ready else ""))


if __name__ == "__main__":
    main()
