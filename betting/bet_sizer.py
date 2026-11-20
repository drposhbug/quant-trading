"""
Bet sizing — converts an edge estimate into a suggested stake.

Two methods, both deliberately conservative:

  1. Fractional Kelly (default, 0.25x). For buying a Polymarket YES share at
     price p when your fair probability is q, full Kelly stakes a bankroll
     fraction f* = (q - p) / (1 - p). Full Kelly is only optimal if q is
     exactly right — and our q comes from a model whose log loss does NOT
     beat the market, so the edge estimate is noisy. Fractional Kelly
     (0.25x) keeps most of the growth while cutting drawdowns roughly 4x,
     and quarter-Kelly is what serious bettors actually run.

  2. Edge tiers — the simple ladder from the walk-forward result: the +6%
     ROI showed up at pre-registered thresholds around 4-8%, so full size
     only above 8% edge, scaling down to zero below 3%.

Both return DOLLAR stakes given a bankroll, and both are capped at
MAX_BANKROLL_FRACTION per bet regardless of method — a fat-finger edge
estimate (or a research hallucination) should never be able to bet 40% of
the roll on one match.

WHERE THE EDGE CAME FROM NOW MATTERS
--------------------------------------------------------------------------
Sizing multiplies expected value; it cannot create it. Staking a negative-EV
bet well only loses the money more smoothly. The diagnostics in this repo
established that the stats models are negative-EV against a closing line:

    nba_diagnose.py      model beaten in 13/13 seasons  (gap +0.0200)
    tennis_diagnose.py   model beaten in  3/3 years     (gap +0.0553)

and in both, the market was closer to the truth in EVERY outer disagreement
bucket — so the bets those models generate are losing bets by construction.
Measured on the NBA backtest, ROI was negative in all five edge buckets
(-1.3%, -5.2%, +2.1%, -1.7%, -1.0%): no weighting of those numbers is
positive, which is exactly the point.

So `edge_source` is now required to be honest about what produced the edge:

    'sharp_line'  the edge is Polymarket's price against a de-vigged sharp
                  book. This is the divergence trade, it does not depend on
                  out-predicting anyone, and it sizes normally.
    'model'       the edge came from one of this repo's stats models. Sized
                  to ZERO for any league whose model has not passed its
                  diagnostic gate — which is currently all of them.

Flip a league in MODEL_GATE only when its diagnostic actually prints a
passing verdict. That is the one switch that should ever turn model betting
back on.

Usage as a module:
    from bet_sizer import suggest_stake
    suggest_stake(edge=0.06, price=0.42, bankroll=1000)            # sharp-line
    suggest_stake(edge=0.06, price=0.42, bankroll=1000,
                  edge_source="model", league="nba")               # -> $0

Self-test:
    py bet_sizer.py
"""

MAX_BANKROLL_FRACTION = 0.05   # hard cap per bet, any method
KELLY_FRACTION = 0.25          # quarter-Kelly default

# (min_edge, fraction_of_full_size) — full size = MAX_BANKROLL_FRACTION
EDGE_TIERS = [
    (0.08, 1.00),
    (0.05, 0.50),
    (0.03, 0.25),
]

# Has this league's stats model beaten the closing line in its own diagnostic?
# `passed: False` forces model-derived stakes to zero. Update ONLY from a
# passing diagnostic run, and record what produced the verdict.
MODEL_GATE = {
    "nba": {"passed": False, "checked_by": "nba_diagnose.py",
            "note": "beaten by the closing line in 13/13 seasons, gap +0.0200"},
    "basketball_nba": {"passed": False, "checked_by": "nba_diagnose.py",
                       "note": "beaten by the closing line in 13/13 seasons, gap +0.0200"},
    "tennis": {"passed": False, "checked_by": "tennis_diagnose.py",
               "note": "beaten by the closing line in 3/3 years, gap +0.0553"},
    # The one passing result in the repo. The log-loss gate itself FAILS
    # (0.977 vs 0.959) -- the model does not out-predict the line -- but the
    # pre-registered, walk-forward, best-price bets clear zero: +6.0%, 90% CI
    # [+0.4%, +11.6%], P(ROI>0)=96% over 2,165 bets (commit 6d088be, re-run
    # 2026-09-09). The mechanism is dispersion capture, not prediction: the
    # model's biggest disagreements mark where books disagree most, and the
    # best price there pays. It only holds AT BEST PRICE -- at average odds it
    # is +0.9% with a CI spanning zero -- so a caller using this gate must be
    # executing best-of-book or on a venue that cannot limit winners.
    "premier_league": {"passed": True, "checked_by": "train_market_model.py",
                       "note": "market-anchored model at BEST PRICE: +6.0% "
                               "[+0.4%, +11.6%], 2165 bets; +0.9% (noise) at "
                               "average odds -- best-price execution required"},
}
# Leagues absent from MODEL_GATE have never been gated at all, which is not the
# same as passing. Model stakes are refused for them too.
UNGATED_NOTE = "no diagnostic has been run for this league"


def _gate_for(league):
    key = (league or "").lower()
    if key in MODEL_GATE:
        return MODEL_GATE[key]
    # tolerate Odds API style keys ('basketball_nba', 'tennis_atp_wimbledon').
    # Only the key-extends-known direction is safe: the reverse would let a
    # short or truncated league name match an unrelated gate.
    for known, gate in sorted(MODEL_GATE.items(), key=lambda kv: -len(kv[0])):
        if key.startswith(known):
            return gate
    return None


def model_betting_allowed(league):
    """-> (allowed, reason). Used by callers that size off a model probability."""
    gate = _gate_for(league)
    if gate is None:
        return False, f"{league or 'unknown league'}: {UNGATED_NOTE}"
    if not gate["passed"]:
        return False, f"{league}: {gate['note']} ({gate['checked_by']})"
    return True, f"{league}: model passed {gate['checked_by']}"


def kelly_fraction(edge, price):
    """
    Bankroll fraction for buying a binary YES share at `price` (0-1) with
    fair probability q = price + edge. f* = (q - p) / (1 - p), scaled by
    KELLY_FRACTION. Returns 0 for non-positive edge or unbettable prices.
    """
    if edge <= 0 or not (0 < price < 1):
        return 0.0
    q = min(price + edge, 0.999)
    full = (q - price) / (1.0 - price)
    return max(0.0, full * KELLY_FRACTION)


def tier_fraction(edge):
    """Bankroll fraction from the edge ladder (as a share of the per-bet cap)."""
    for min_edge, size in EDGE_TIERS:
        if edge >= min_edge:
            return MAX_BANKROLL_FRACTION * size
    return 0.0


def suggest_stake(edge, price, bankroll, method="kelly",
                  edge_source="sharp_line", league=None):
    """
    -> dict {stake, fraction, method, capped, blocked, reason}.

    edge = fair_prob - price (positive means the share is underpriced). Stake
    is in bankroll units (dollars), never exceeding MAX_BANKROLL_FRACTION.

    edge_source='model' stakes zero unless the league's model has passed its
    diagnostic gate — see the module docstring. The default 'sharp_line' keeps
    the Polymarket-vs-sharp-book divergence trade sizing normally, which is the
    only signal in this repo that has ever been worth acting on.
    """
    if edge_source == "model":
        allowed, reason = model_betting_allowed(league)
        if not allowed:
            return {"stake": 0.0, "fraction": 0.0, "method": method,
                    "capped": False, "blocked": True,
                    "reason": f"model-derived edge refused -- {reason}"}

    frac = kelly_fraction(edge, price) if method == "kelly" else tier_fraction(edge)
    capped = frac > MAX_BANKROLL_FRACTION
    frac = min(frac, MAX_BANKROLL_FRACTION)
    return {
        "stake": round(bankroll * frac, 2),
        "fraction": frac,
        "method": method,
        "capped": capped,
        "blocked": False,
        "reason": f"sized on {edge_source} edge",
    }


if __name__ == "__main__":
    print(f"Bankroll $1000, quarter-Kelly (cap {MAX_BANKROLL_FRACTION:.0%}/bet):")
    for edge in (0.02, 0.03, 0.05, 0.08, 0.12, 0.25):
        k = suggest_stake(edge, price=0.45, bankroll=1000)
        t = suggest_stake(edge, price=0.45, bankroll=1000, method="tiers")
        cap = " (capped)" if k["capped"] else ""
        print(f"  edge {edge:>4.0%} @ price 0.45:  kelly ${k['stake']:>6.2f}{cap}   "
              f"tiers ${t['stake']:>6.2f}")

    print("\nSame edges, but sourced from a stats model:")
    for league in ("nba", "tennis", "premier_league", "soccer_usa_mls"):
        r = suggest_stake(0.12, price=0.45, bankroll=1000,
                          edge_source="model", league=league)
        print(f"  {league:<16} ${r['stake']:>6.2f}  {r['reason']}")
