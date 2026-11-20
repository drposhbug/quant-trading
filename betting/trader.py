"""
The trade: buy Polymarket when it strays from the sharp line, sell when it
comes back — and never hold through kickoff
================================================================================
This is the strategy the evidence in this repo actually supports, and it is
not a prediction strategy. Three measured facts shape it:

  1. The stats models lose to the closing line (NBA 0/13 seasons, tennis 0/3
     years). Trying to out-predict the market is not the edge.
  2. Execution IS an edge: best-price vs sharp-line was worth +2.9 to +3.5 ROI
     points, and the one passing backtest in the repo (Premier League, +6.0%,
     CI [+0.4%, +11.6%]) works by capturing price dispersion, not by knowing
     who wins.
  3. Polymarket tracked Pinnacle to within ~1c on the only sample so far --
     which means when it DOES stray, the sharp line is the better estimate and
     the stray is what you trade.

So: when Polymarket's ask is below the de-vigged sharp line by more than a
margin, buy. Then, crucially, EXIT WHEN THE PRICE CONVERGES -- take the move,
not the outcome. A share bought at 0.42 that the sharp book says is worth
0.48 has earned its edge the moment it trades at 0.48, regardless of who
wins. Holding to resolution would add a coin flip's variance for zero extra
expectation and would expose the position to everything that happens in the
game. Every position is also closed before kickoff no matter what, for the
same reason. This is the "sell before it wins" idea made explicit: profit is
the price move, and it is banked as soon as it exists.

Positions are always LONG a token: buying YES for an outcome, or buying NO
(which is what "selling YES" means on Polymarket when you hold none). Both
are the same trade -- a token priced below its fair value -- so the code
treats them identically with fair_no = 1 - fair_yes.

CADENCE, honestly: the sharp line comes from the last log_prices.py snapshot
(bounded by the Odds API budget), so it is minutes old; Polymarket's book is
read live each pass (free). That is a seconds-to-minutes loop, not a
sub-second one -- fast enough to catch a stray that persists, not fast enough
to race news. Entries are refused when the sharp line is older than
MAX_FAIR_AGE_MIN, because a stale fair value is not a fair value.

DRY FIRST. The default executor simulates fills against the live public
book. Run that for weeks and read --report before anything goes live; the
paper P&L is settled against real prices and real resting size.

Usage:
    py trader.py --once                     # one pass, dry (cron-friendly)
    py trader.py --loop 60                  # every 60s, dry
    py trader.py --report                   # positions and P&L
    py trader.py --loop 60 --live           # real orders (needs POLYMARKET_LIVE=1 + key)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

from analyze_prices import (consensus_fair, group_snapshots, load_snapshots,
                            outcomes_for, sharp_fair)
from bet_sizer import suggest_stake
from db import (close_position, fetch_positions, fetch_probes, init_exec_probes,
                init_positions, open_position, open_probe, update_probe)
from polymarket_exec import MIN_SHARES, Executor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- strategy parameters --------------------------------------------------
ENTRY_MARGIN = 0.03          # fair - ask must exceed this to buy (covers fees + spread)
MAX_SPREAD = 0.10            # refuse entries when bid/ask are quoted wider than this
MAX_DEPLOYED_FRACTION = 0.5  # stop entering once this share of bankroll is at risk
ADVERSE_STOP = 0.02          # exit if PM mid drops this far below entry while the sharp
                             # line has NOT moved: the market is fading us, not the line
EARLY_ENTRY_HOURS = 12       # beyond this, a single sharp print is not enough:
EARLY_MARGIN = 0.05          # ...require the consensus to agree at a wider gap
EARLY_STAKE_FRACTION = 0.5   # ...and take half size (early lines are the most stale)
EXIT_BAND = 0.01             # sell once the mid is within this of fair (converged)
TAKE_PROFIT = 0.06           # or once the bid is this far above entry
STOP = 0.05                  # or if the SHARP LINE moves this far against entry
EXIT_BEFORE_KICKOFF_MIN = 20 # always flat before the game starts
MAX_FAIR_AGE_MIN = 10        # refuse entries on a sharp line older than this. Was 90: with sharp odds refreshed
                             # ~3x/day, 245 dry trades bought a stale line (fair never moved, avg 'edge' 15.8%,
                             # 172 adverse exits, -$76). 10 min means few trades until odds refresh more often.
MAX_OPEN_POSITIONS = 20
SHARP_BOOK = "pinnacle"
FALLBACK_BOOKS = ["betonlineag", "lowvig", "bovada", "draftkings", "fanduel", "betmgm"]

TOKENS_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pm_tokens_cache.json")


def _utc_now():
    return datetime.now(timezone.utc)


def _iso(dt):
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse(iso):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------- decisions
# Pure functions: no I/O, so test_pipeline.py can drive them directly.

def decide_entry(fair_token, ask, ask_size, margin=ENTRY_MARGIN,
                 bid=None, max_spread=MAX_SPREAD):
    """
    -> edge (fair - ask) if this token is worth buying, else None.
    Requires a real ask with resting size; refuses prices near the rails
    (a 0.97 share has no room to converge, a 0.03 one is a lottery ticket),
    and refuses books quoted wider than max_spread when a bid exists -- a
    gaping spread means the exit will cost back much of the edge, and thin
    two-sided interest is where stale-quote "edges" live.
    """
    if fair_token is None or ask is None or not ask_size or ask_size < MIN_SHARES:
        return None
    if not (0.05 <= ask <= 0.95):
        return None
    if bid is not None and ask - bid > max_spread:
        return None
    edge = fair_token - ask
    return edge if edge > margin else None


def decide_exit(entry_price, fair_token, bid, mid, now, kickoff,
                exit_band=EXIT_BAND, take_profit=TAKE_PROFIT, stop=STOP,
                before_kickoff_min=EXIT_BEFORE_KICKOFF_MIN,
                fair_at_entry=None, adverse_stop=ADVERSE_STOP):
    """
    -> exit reason, or None to keep holding. Order matters:

      1. kickoff  -- unconditional, always first
      2. stop     -- the sharp line has moved against the entry. This must be
                     checked BEFORE convergence: once fair has fallen below the
                     price, "mid >= fair - band" is trivially true, and the
                     exit would be mislabeled a win. The sell is the same
                     either way; the label is what the report counts, and the
                     stop rate is the honest measure of how often the thesis
                     (that the stray converges) was wrong.
      3. adverse  -- the sharp line has NOT moved but the PM mid has dropped
                     through the entry anyway: the crowd is fading us while
                     our thesis price stands still. Requires a two-sided
                     quote, so spread noise on a one-sided book cannot fire it.
      4. converged / take-profit -- banking the move
    """
    if kickoff is not None and now >= kickoff - timedelta(minutes=before_kickoff_min):
        return "pre_kickoff"
    if fair_token is not None and fair_token <= entry_price - stop:
        return "stop"
    if (fair_token is not None and fair_at_entry is not None
            and abs(fair_token - fair_at_entry) < 0.01
            and bid is not None and mid is not None
            and mid <= entry_price - adverse_stop):
        return "adverse"
    if fair_token is not None and mid is not None and mid >= fair_token - exit_band:
        return "converged"
    if bid is not None and bid >= entry_price + take_profit:
        return "take_profit"
    return None


# ------------------------------------------------------------ token lookup
def _load_token_cache():
    try:
        with open(TOKENS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_token_cache(cache):
    with open(TOKENS_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f)


def resolve_tokens(home, away, commence, cache):
    """
    {outcome: {'yes': token_id, 'no': token_id}} for the fixture, via Gamma.
    Handles both market shapes (see parse_event_markets): soccer's grouped
    YES/NO binaries, and the US moneyline whose two outcomes ARE the teams --
    there the home token is YES-on-home and the away token is its complement.
    commence anchors the event date -- teams that meet twice a season would
    otherwise both resolve to the sooner meeting's market (and the cache key
    carries the date for the same reason). Cached on disk: token ids never
    change for a market, and Gamma search is the slowest call in the loop.
    Only non-empty results are cached, so a fixture PM has not listed yet is
    retried on the next pass instead of being remembered as unlisted forever.
    """
    key = f"{home}|{away}|{(commence or '')[:10]}"
    if key in cache:
        return cache[key]
    from odds_compare import gamma_find_event, norm, teams_match
    event = gamma_find_event(home, away, commence_time=commence)
    out = {}
    if event:
        for m in event.get("markets", []):
            label = m.get("groupItemTitle") or m.get("question", "")
            outcomes = m.get("outcomes", [])
            tokens = m.get("clobTokenIds", [])
            outcomes = json.loads(outcomes) if isinstance(outcomes, str) else outcomes
            tokens = json.loads(tokens) if isinstance(tokens, str) else tokens
            low = [o.lower() for o in outcomes]

            if "yes" in low and "no" in low:      # soccer-style binary market
                if "draw" in norm(label):
                    k = "D"
                elif teams_match(home, label):
                    k = "H"
                elif teams_match(away, label):
                    k = "A"
                else:
                    continue
                yi, ni = low.index("yes"), low.index("no")
                if yi < len(tokens) and ni < len(tokens):
                    out[k] = {"yes": tokens[yi], "no": tokens[ni]}
                continue

            # US-style moneyline: outcomes are the team names (skip spreads,
            # which share the shape but carry a group label / handicap)
            if len(outcomes) == 2 and len(tokens) == 2 and not m.get("groupItemTitle") \
                    and "spread" not in (m.get("question") or "").lower():
                hi = next((i for i, o in enumerate(outcomes) if teams_match(home, o)), None)
                ai = next((i for i, o in enumerate(outcomes) if teams_match(away, o)), None)
                if hi is not None and ai is not None and hi != ai:
                    out.setdefault("H", {"yes": tokens[hi], "no": tokens[ai]})
                    out.setdefault("A", {"yes": tokens[ai], "no": tokens[hi]})
    if out:
        cache[key] = out
        _save_token_cache(cache)
    return out


# ------------------------------------------------------------------ passes
def latest_fair_lines():
    """
    {fixture_key: (fair, sharp_book, snapshot_time, league, cons_fair)} from
    the most recent snapshot of each fixture that has a full sharp line.
    cons_fair is the sharp-set consensus (None below 2 quoting books) — logged
    on probes so --report can say which reference tracks the close better.
    """
    grouped, fixture_league = group_snapshots(load_snapshots())
    out = {}
    for fixture, snaps in grouped.items():
        if not snaps:
            continue
        t = max(snaps)
        league = fixture_league.get(fixture)
        outcomes = outcomes_for(league)
        fair, book = sharp_fair(snaps[t], outcomes, SHARP_BOOK, FALLBACK_BOOKS)
        if fair:
            cons, _ = consensus_fair(snaps[t], outcomes)
            out[fixture] = (fair, book, t, league, cons)
    return out


def manage_exits(ex, fairs, now, quiet=False):
    """Check every open position against the exit rules; sell when one fires."""
    closed = 0
    for pos in fetch_positions(status="open", mode=ex.mode):
        fixture = (pos["home_team"], pos["away_team"], pos["commence_time"])
        fair_yes = None
        if fixture in fairs:
            fair_yes = fairs[fixture][0].get(pos["outcome"])
        fair_token = None if fair_yes is None else (
            fair_yes if pos["token_side"] == "YES" else 1.0 - fair_yes)
        try:
            bid, ask, _, bid_size = ex.book(pos["token_id"])
        except Exception as e:  # noqa: BLE001 -- book read failed; try next pass
            if not quiet:
                print(f"  ! book read failed for position {pos['id']}: {type(e).__name__}")
            continue
        mid = (bid + ask) / 2 if (bid is not None and ask is not None) else bid
        reason = decide_exit(pos["entry_price"], fair_token, bid, mid, now,
                             _parse(pos["commence_time"]),
                             fair_at_entry=pos["fair_at_entry"])
        if not reason:
            continue
        if bid is None:
            if not quiet:
                print(f"  exit wanted ({reason}) on #{pos['id']} but no bid -- holding")
            continue
        fill = ex.sell(pos["token_id"], limit_price=bid, size=pos["size"])
        if fill.size <= 0:
            if not quiet:
                print(f"  exit wanted ({reason}) on #{pos['id']} but no fill at {bid:.3f}")
            continue
        fee_bps = ex.fee_bps(pos["token_id"])
        entry_fees = pos["entry_price"] * fill.size * fee_bps / 10_000.0
        fees = entry_fees + fill.fees
        pnl = (fill.price - pos["entry_price"]) * fill.size - fees
        close_position(pos["id"], _iso(now), fill.price, reason, fees, pnl,
                       exit_order_id=fill.order_id, fair_at_exit=fair_token)
        closed += 1
        if not quiet:
            print(f"  CLOSE #{pos['id']} {pos['home_team']} v {pos['away_team']} "
                  f"{pos['outcome']}/{pos['token_side']} {reason}: "
                  f"{pos['entry_price']:.3f} -> {fill.price:.3f} x{fill.size:.0f} "
                  f"pnl {pnl:+.2f}")
    return closed


def find_entries(ex, fairs, now, bankroll, token_cache, quiet=False):
    """Scan every fixture with a fresh sharp line for a token priced below fair."""
    open_pos = fetch_positions(status="open", mode=ex.mode)
    held = {(p["home_team"], p["away_team"], p["commence_time"], p["outcome"]) for p in open_pos}
    # token-level guard: in a 2-way market YES-on-home IS NO-on-away (same
    # token), and the same game can appear under both team orderings -- the
    # fixture-key guard alone bought the same token up to four times
    held_tokens = {p["token_id"] for p in open_pos if p["token_id"]}
    deployed = sum(p["entry_price"] * p["size"] for p in open_pos)
    room = MAX_OPEN_POSITIONS - len(open_pos)
    opened = 0
    for fixture, (fair, book, snap_t, league, cons) in fairs.items():
        if room <= 0:
            break
        # bankroll exposure cap: Kelly sizes each bet alone and knows nothing
        # about the other open ones -- without this, one pass can put most of
        # the bankroll at risk simultaneously
        if deployed >= MAX_DEPLOYED_FRACTION * bankroll:
            if not quiet:
                print(f"  exposure cap reached (${deployed:.0f} deployed) -- no more entries")
            break
        home, away, commence = fixture
        kickoff = _parse(commence)
        if kickoff and now >= kickoff - timedelta(minutes=EXIT_BEFORE_KICKOFF_MIN):
            continue                        # would have to exit immediately
        snap_dt = _parse(snap_t)
        if snap_dt is None or now - snap_dt > timedelta(minutes=MAX_FAIR_AGE_MIN):
            continue                        # stale sharp line: not a fair value
        try:
            tokens = resolve_tokens(home, away, commence, token_cache)
        except Exception as e:  # noqa: BLE001
            if not quiet:
                print(f"  ! token lookup failed {home} v {away}: {type(e).__name__}")
            continue
        for outcome, fair_yes in fair.items():
            if (home, away, commence, outcome) in held or outcome not in tokens:
                continue
            best = None
            for side, fair_token in (("YES", fair_yes), ("NO", 1.0 - fair_yes)):
                token_id = tokens[outcome][side.lower()]
                if token_id in held_tokens:
                    continue
                try:
                    bid, ask, ask_size, _ = ex.book(token_id)
                except Exception:  # noqa: BLE001
                    continue
                edge = decide_entry(fair_token, ask, ask_size, bid=bid)
                if edge is not None and (best is None or edge > best[0]):
                    best = (edge, side, token_id, ask, ask_size, fair_token, bid)
            if best is None:
                continue
            edge, side, token_id, ask, ask_size, fair_token, bid = best
            # shadow maker order for the taker-vs-maker ledger (never traded):
            # rest one tick above the bid, never crossing the ask
            maker_price = round(min((bid or 0.0) + 0.01, ask - 0.01), 2)
            cons_yes = cons.get(outcome) if cons else None
            cons_token = None if cons_yes is None else (
                cons_yes if side == "YES" else 1.0 - cons_yes)
            open_probe({
                "logged_at": _iso(now), "league": league, "commence_time": commence,
                "home_team": home, "away_team": away, "outcome": outcome,
                "token_side": side, "token_id": token_id, "fair_at_entry": fair_token,
                "fair_consensus": cons_token,
                "taker_price": ask, "taker_fee_bps": ex.fee_bps(token_id),
                "maker_price": maker_price if maker_price > 0 else None,
            })
            # early-entry gate: >12h out, one Pinnacle print is not a fair
            # value -- it is the book's resting overnight line. Demand the
            # sharp CONSENSUS agrees at a wider gap, and take half size.
            # (The probe above still logs the raw signal either way, so the
            # gate's cost/benefit is itself measured.)
            early = kickoff is not None and kickoff - now > timedelta(hours=EARLY_ENTRY_HOURS)
            if early:
                if cons_token is None or edge < EARLY_MARGIN \
                        or cons_token - ask < EARLY_MARGIN:
                    continue
            stake = suggest_stake(edge, ask, bankroll)["stake"]     # sharp-line edge
            if early:
                stake *= EARLY_STAKE_FRACTION
            size = min(stake / ask, ask_size)
            fill = ex.buy(token_id, limit_price=ask, size=size)
            if fill.size <= 0:
                continue
            pid = open_position({
                "mode": ex.mode, "opened_at": _iso(now), "league": league,
                "commence_time": commence, "home_team": home, "away_team": away,
                "outcome": outcome, "token_side": side, "token_id": token_id,
                "entry_price": fill.price, "size": fill.size,
                "fair_at_entry": fair_token, "sharp_book": book,
                "entry_order_id": fill.order_id,
            })
            held.add((home, away, commence, outcome))
            held_tokens.add(token_id)
            deployed += fill.notional
            room -= 1
            opened += 1
            if not quiet:
                print(f"  OPEN  #{pid} {home} v {away} {outcome}/{side} "
                      f"@ {fill.price:.3f} x{fill.size:.0f} (fair {fair_token:.3f}, "
                      f"edge {edge:+.3f}, ${fill.notional:.0f})")
    return opened


def manage_probes(ex, fairs, now):
    """
    Advance the taker-vs-maker shadow ledger. A resting maker order fills
    when the market trades down through its price (ask <= maker_price); it is
    cancelled when the sharp line falls to where the entry rule would no
    longer want it (a live maker would pull the quote). At kickoff-20min every
    probe is scored with the last observed mid and closed.
    """
    for pr in fetch_probes(status="open"):
        kickoff = _parse(pr["commence_time"])
        try:
            bid, ask, _, _ = ex.book(pr["token_id"])
        except Exception:  # noqa: BLE001 -- book read failed; next pass
            continue
        mid = (bid + ask) / 2 if (bid is not None and ask is not None) else (bid or ask)
        if kickoff is not None and now >= kickoff - timedelta(minutes=EXIT_BEFORE_KICKOFF_MIN):
            update_probe(pr["id"], status="closed", close_time=_iso(now), close_mid=mid)
            continue
        if pr["maker_state"] != "resting" or pr["maker_price"] is None:
            continue
        fixture = (pr["home_team"], pr["away_team"], pr["commence_time"])
        fair_yes = fairs[fixture][0].get(pr["outcome"]) if fixture in fairs else None
        fair_token = None if fair_yes is None else (
            fair_yes if pr["token_side"] == "YES" else 1.0 - fair_yes)
        if fair_token is not None and fair_token - pr["maker_price"] <= ENTRY_MARGIN / 2:
            update_probe(pr["id"], maker_state="cancelled")
        elif ask is not None and ask <= pr["maker_price"]:
            update_probe(pr["id"], maker_state="filled", maker_filled_at=_iso(now))


def settle_probes(now, quiet=False, max_lookups=25):
    """
    Score closed probes at RESOLUTION (token worth 1 or 0), settling the
    exit-at-convergence vs hold-to-settlement question with the same signals:
    close_mid scores strategy A (take the move), settle_price scores B (take
    the outcome). Resolution comes free from Gamma once the market closes.
    """
    import requests as _rq
    cutoff = _iso(now - timedelta(hours=4))     # let games finish + resolve
    done = 0
    for pr in fetch_probes(status="closed"):
        if pr.get("settle_price") is not None or (pr["commence_time"] or "9") > cutoff:
            continue
        if done >= max_lookups:                 # spread lookups across passes
            break
        try:
            r = _rq.get("https://gamma-api.polymarket.com/markets",
                        params={"clob_token_ids": pr["token_id"]}, timeout=15)
            markets = r.json() or []
        except (_rq.RequestException, ValueError):
            continue
        if isinstance(markets, dict):           # Gamma sometimes returns an error object, not a list:
            markets = markets.get("data") or []  # KeyError: 0 here used to abort the whole trading pass
        done += 1
        if not markets or not markets[0].get("closed"):
            continue
        m = markets[0]
        tokens = m.get("clobTokenIds", [])
        prices = m.get("outcomePrices", [])
        tokens = json.loads(tokens) if isinstance(tokens, str) else tokens
        prices = json.loads(prices) if isinstance(prices, str) else prices
        if pr["token_id"] not in tokens:
            continue
        try:
            settle = float(prices[tokens.index(pr["token_id"])])
        except (TypeError, ValueError, IndexError):
            continue
        update_probe(pr["id"], settle_price=settle, settled_at=_iso(now))
        if not quiet:
            print(f"  settled probe #{pr['id']} {pr['home_team']} v {pr['away_team']} "
                  f"{pr['outcome']}/{pr['token_side']} -> {settle:.0f}")


def run_pass(ex, bankroll, token_cache, quiet=False):
    now = _utc_now()
    fairs = latest_fair_lines()
    closed = manage_exits(ex, fairs, now, quiet)
    opened = find_entries(ex, fairs, now, bankroll, token_cache, quiet)
    manage_probes(ex, fairs, now)
    settle_probes(now, quiet)
    n_open = len(fetch_positions(status="open", mode=ex.mode))
    if not quiet:
        print(f"[{_iso(now)}] {ex.mode}: {len(fairs)} fixtures with a sharp line, "
              f"opened {opened}, closed {closed}, open {n_open}")
    return opened, closed


def report(mode=None):
    closed = fetch_positions(status="closed", mode=mode)
    open_ = fetch_positions(status="open", mode=mode)
    print(f"=== Positions ({mode or 'all modes'}) ===")
    print(f"open: {len(open_)}   closed: {len(closed)}")
    for p in open_:
        print(f"  #{p['id']:<4} {p['home_team']} v {p['away_team']} {p['outcome']}/{p['token_side']} "
              f"@ {p['entry_price']:.3f} x{p['size']:.0f}  fair {p['fair_at_entry']:.3f}  "
              f"since {p['opened_at']}")
    if not closed:
        return
    pnl = sum(p["pnl"] or 0 for p in closed)
    risked = sum(p["entry_price"] * p["size"] for p in closed)
    fees = sum(p["fees"] or 0 for p in closed)
    moves = [(p["exit_price"] - p["entry_price"]) for p in closed]
    wins = sum(1 for m in moves if m > 0)
    print(f"\nrealized pnl {pnl:+.2f} on {risked:.2f} risked = ROI {pnl / risked:+.2%} "
          f"(fees {fees:.2f})")
    print(f"price moved in our favour on {wins}/{len(closed)} exits")
    reasons = {}
    for p in closed:
        reasons.setdefault(p["exit_reason"], []).append(p["pnl"] or 0)
    for r, v in sorted(reasons.items()):
        print(f"  {r:<12} {len(v):>4}  pnl {sum(v):+.2f}")
    clv = [p["fair_at_exit"] - p["entry_price"] for p in closed if p["fair_at_exit"] is not None]
    if clv:
        print(f"mean (fair at exit - entry): {sum(clv) / len(clv):+.4f} per share "
              f"-- the CLV-style number; sustained positive here is the edge, "
              f"before pnl converges")

    # ---- taker vs maker (shadow ledger; nothing here was traded) ---------
    scored = [p for p in fetch_probes(status="closed") if p["close_mid"] is not None]
    if scored:
        taker = [p["close_mid"] - p["taker_price"]
                 - p["taker_price"] * (p["taker_fee_bps"] or 0) / 10_000.0
                 for p in scored]
        maker_fills = [p for p in scored if p["maker_state"] == "filled"]
        # unfilled maker = no trade = 0; that IS the cost of making
        maker = [(p["close_mid"] - p["maker_price"]) if p["maker_state"] == "filled" else 0.0
                 for p in scored]
        print(f"\n=== Taker vs maker execution ({len(scored)} scored signals) ===")
        print(f"taker: mean {sum(taker) / len(taker):+.4f}/share to close (fees included)")
        print(f"maker: mean {sum(maker) / len(maker):+.4f}/share to close "
              f"(filled {len(maker_fills)}/{len(scored)}; unfilled counts as 0)")
        if len(scored) >= 30:
            better = "MAKER" if sum(maker) > sum(taker) else "TAKER"
            print(f"verdict so far: {better} execution nets more per signal")
        else:
            print(f"collecting ({len(scored)}/30 before a verdict)")

        # which fair-line reference tracked the close better?
        both = [p for p in scored if p.get("fair_consensus") is not None
                and p["fair_at_entry"] is not None]
        if both:
            e_pin = sum(abs(p["close_mid"] - p["fair_at_entry"]) for p in both) / len(both)
            e_con = sum(abs(p["close_mid"] - p["fair_consensus"]) for p in both) / len(both)
            print(f"\nfair-line reference vs close ({len(both)} probes): "
                  f"pinnacle off by {e_pin:.4f}, sharp consensus off by {e_con:.4f}"
                  f"{'  -> consensus tracks closer' if e_con < e_pin else ''}")

        # A/B: take the move (exit at the pre-kickoff close) vs take the
        # outcome (hold the same entry to resolution). Same signals, same
        # entry price and fee -- only the exit differs.
        ab = [p for p in scored if p.get("settle_price") is not None]
        if ab:
            fee = lambda p: p["taker_price"] * (p["taker_fee_bps"] or 0) / 10_000.0
            a = [p["close_mid"] - p["taker_price"] - fee(p) for p in ab]
            b = [p["settle_price"] - p["taker_price"] - fee(p) for p in ab]
            print(f"\n=== A/B: exit-at-close vs hold-to-settlement ({len(ab)} settled signals) ===")
            print(f"A (take the move):    mean {sum(a) / len(a):+.4f}/share")
            print(f"B (take the outcome): mean {sum(b) / len(b):+.4f}/share")
            if len(ab) >= 30:
                print(f"verdict so far: {'HOLD TO SETTLEMENT' if sum(b) > sum(a) else 'EXIT AT CONVERGENCE'} "
                      f"nets more per signal")
            else:
                print(f"collecting ({len(ab)}/30 before a verdict)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Trade Polymarket toward the sharp line; exit on convergence or before kickoff.")
    ap.add_argument("--once", action="store_true", help="one pass then exit")
    ap.add_argument("--loop", type=int, metavar="SEC", help="repeat every SEC seconds")
    ap.add_argument("--live", action="store_true",
                    help="real orders (also needs POLYMARKET_LIVE=1 and POLYMARKET_PRIVATE_KEY)")
    ap.add_argument("--bankroll", type=float, default=1000.0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    except ImportError:
        pass

    init_positions()
    init_exec_probes()
    if args.report:
        report()
        raise SystemExit(0)
    if not (args.once or args.loop):
        ap.error("pass --once, --loop SEC, or --report")

    ex = Executor.from_env(live=args.live)
    cache = _load_token_cache()
    if args.loop:
        print(f"{ex.mode} loop every {args.loop}s (ctrl-C to stop)")
        try:
            while True:
                run_pass(ex, args.bankroll, cache, args.quiet)
                time.sleep(args.loop)
        except KeyboardInterrupt:
            print("\nstopped")
        report(ex.mode)
    else:
        run_pass(ex, args.bankroll, cache, args.quiet)
