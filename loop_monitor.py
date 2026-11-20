"""Run the monitor every few minutes for the rest of the trading day, inside ONE GitHub Actions job.

Why: GitHub's 5-minute cron is best-effort and on 2026-11-19 it fired no run between 09:30 and 16:00 ET, so the 15:30
rebalance was missed. Whichever hourly trigger fires first now starts this loop, which keeps running until the close
(jobs may last up to 6 h; triggers repeat through the day in case one is dropped). State is committed after every pass.
"""
import datetime as dt
import os
import subprocess
import sys
import time

import monitor

DEADLINE = time.time() + 5 * 3600 + 40 * 60  # stay under the 6 h job limit with time to save state


def sh(*cmd):
    return subprocess.run(list(cmd), check=False).returncode


def save_state():
    sh("git", "add", "state.json", "signals/")
    sh("git", "add", "options_state.json")  # separate add: a missing file must not abort the one above
    if sh("git", "diff", "--cached", "--quiet") != 0:
        sh("git", "commit", "-q", "-m", "monitor state")
        sh("git", "pull", "-q", "--rebase", "-X", "theirs")  # rebase keeps THIS run's state (the newest) on conflict
        sh("git", "push", "-q")


def one_pass():
    sh(sys.executable, "monitor.py")
    sh(sys.executable, "options_earnings.py")  # separate experiment; its failures never stop the loop
    save_state()


def main():
    if os.environ.get("FORCE") == "1":  # manual forced run: one pass, old behaviour
        one_pass()
        return
    while time.time() < DEADLINE:
        now = dt.datetime.now(monitor.NY)
        clock = monitor.alpaca("GET", "/clock")
        if not clock["is_open"]:
            if dt.datetime.fromisoformat(clock["next_open"]).date() != now.date():
                print("market closed for the day")
                one_pass()  # lets after-close bookkeeping (alerts, state) run once
                return
            sh(sys.executable, "monitor.py")  # before the open: monitor only snapshots prediction markets + posts, then
            save_state()                      # exits ("market closed") — gives a pre-open odds record for IPO days
            time.sleep(300)
            continue
        one_pass()
        to_close = (dt.datetime.fromisoformat(clock["next_close"]) - now).total_seconds() / 60
        time.sleep(120 if to_close <= 45 else 300)  # denser near the close so the rebalance window gets retries


if __name__ == "__main__":
    main()
