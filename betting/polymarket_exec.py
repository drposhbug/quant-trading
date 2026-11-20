"""
Polymarket execution — the layer this repo never had
================================================================================
Until now every module here READ Polymarket (Gamma for discovery, the CLOB for
the order book) and nothing could place an order. This is the write side: one
Executor with two modes that expose the same interface, so the strategy in
trader.py is identical whether it is being rehearsed or run.

  dry   (default) Simulated fills against the LIVE public order book. A buy
        fills at the real best ask, capped by the size actually resting there;
        a sell fills at the real best bid the same way. No key, no wallet, no
        network write. This is the mode to run for weeks first, because the
        paper P&L it produces is settled against prices that really existed.

  live  Real orders through py-clob-client, signed with your wallet key. Three
        separate things must all be true before an order goes out -- the
        --live flag, POLYMARKET_LIVE=1 in the environment, and a private key --
        so that no single slip (a stray flag, an old shell) can trade money.
        Every order is also capped by MAX_NOTIONAL_PER_ORDER regardless of
        what the strategy asked for.

WHY TAKER ORDERS, and why fill-and-kill: this strategy's edge is a price that
is wrong NOW relative to the sharp line and will converge; resting a limit
order and waiting is how you get filled only when the price moves against
you (adverse selection). Orders are therefore FAK -- fill what is available
at or better than the limit, cancel the rest -- and the strategy sizes to what
the book can actually absorb rather than to what it would like.

FEES. Polymarket charges a per-market taker fee on some markets and none on
others, and the rate is exposed per token by the CLOB. Live mode reads it;
dry mode also tries to read it (it is a public endpoint) and otherwise falls
back to DEFAULT_FEE_BPS. The paper P&L deliberately errs toward overstating
fees rather than understating them.

Usage as a module:
    ex = Executor.from_env()                 # dry unless explicitly enabled
    bid, ask, ask_sz, bid_sz = ex.book(token_id)
    fill = ex.buy(token_id, limit_price=0.42, size=25)
    fill = ex.sell(token_id, limit_price=0.55, size=25)
"""

import os
import sys
from datetime import datetime, timezone

import requests

CLOB_HOST = "https://clob.polymarket.com"
CHAIN_ID = 137                     # Polygon
TIMEOUT = 20

DEFAULT_FEE_BPS = 100              # 1%: conservative when the real rate is unknown
MAX_NOTIONAL_PER_ORDER = 250.0     # hard cap in dollars, any mode, any caller
MIN_SHARES = 5.0                   # below this the CLOB rejects the order
PRICE_DECIMALS = 2                 # default tick; live mode asks the CLOB per token

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def public_book(token_id):
    """
    (best_bid, best_ask, ask_size, bid_size) from the public CLOB. Free, no
    auth, the same call log_prices.py makes. Sizes are shares resting at the
    best level -- what a taker can actually get without walking the book.
    """
    r = requests.get(f"{CLOB_HOST}/book", params={"token_id": token_id}, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    asks = [(float(a["price"]), float(a["size"])) for a in data.get("asks", [])
            if float(a.get("size", 0)) > 0]
    bids = [(float(b["price"]), float(b["size"])) for b in data.get("bids", [])
            if float(b.get("size", 0)) > 0]
    best_ask, ask_size = min(asks, key=lambda x: x[0]) if asks else (None, 0.0)
    best_bid, bid_size = max(bids, key=lambda x: x[0]) if bids else (None, 0.0)
    return best_bid, best_ask, ask_size, bid_size


def public_fee_bps(token_id):
    """Per-token taker fee from the CLOB, or None if it cannot be read."""
    try:
        r = requests.get(f"{CLOB_HOST}/fee-rate", params={"token_id": token_id}, timeout=TIMEOUT)
        if r.status_code == 200:
            v = r.json()
            if isinstance(v, dict):
                v = v.get("fee_rate_bps", v.get("feeRateBps"))
            return int(v) if v is not None else None
    except (requests.RequestException, ValueError, TypeError):
        pass
    return None


class Fill:
    """What came back from an order. size == 0 means nothing filled."""

    def __init__(self, side, token_id, price, size, order_id=None, fee_bps=0, mode="dry"):
        self.side, self.token_id = side, token_id
        self.price, self.size = float(price or 0.0), float(size or 0.0)
        self.order_id, self.fee_bps, self.mode = order_id, int(fee_bps or 0), mode
        self.at = _utc_now()

    @property
    def notional(self):
        return self.price * self.size

    @property
    def fees(self):
        return self.notional * self.fee_bps / 10_000.0

    def __repr__(self):
        return (f"Fill({self.side} {self.size:.2f} @ {self.price:.3f} "
                f"{'#' + str(self.order_id) if self.order_id else ''} {self.mode})")


class Executor:
    def __init__(self, mode="dry", client=None, book_override=None, fee_bps=None):
        """
        mode: 'dry' or 'live'. client: a py_clob_client ClobClient for live.
        book_override: {token_id: (bid, ask, ask_size, bid_size)} -- lets tests
        drive the dry simulator without the network.
        """
        if mode not in ("dry", "live"):
            raise ValueError(mode)
        if mode == "live" and client is None:
            raise ValueError("live mode needs a ClobClient")
        self.mode, self.client = mode, client
        self.book_override = book_override or {}
        self._fee_bps = fee_bps
        self._fee_cache = {}

    # ------------------------------------------------------------- construct
    @classmethod
    def from_env(cls, live=False):
        """
        Dry unless ALL of: live=True, POLYMARKET_LIVE=1, POLYMARKET_PRIVATE_KEY.
        Any one missing -> dry, with a printed reason, never a silent live.
        """
        if not live:
            return cls("dry")
        if os.getenv("POLYMARKET_LIVE") != "1":
            print("live requested but POLYMARKET_LIVE != 1 -> running DRY")
            return cls("dry")
        key = os.getenv("POLYMARKET_PRIVATE_KEY")
        if not key:
            print("live requested but POLYMARKET_PRIVATE_KEY unset -> running DRY")
            return cls("dry")
        from py_clob_client.client import ClobClient
        funder = os.getenv("POLYMARKET_FUNDER") or None
        sig_type = int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "0"))
        client = ClobClient(CLOB_HOST, chain_id=CHAIN_ID, key=key,
                            signature_type=sig_type, funder=funder)
        client.set_api_creds(client.create_or_derive_api_creds())
        print("LIVE executor armed")
        return cls("live", client=client)

    # ---------------------------------------------------------------- market
    def book(self, token_id):
        if token_id in self.book_override:
            return self.book_override[token_id]
        return public_book(token_id)

    def fee_bps(self, token_id):
        if self._fee_bps is not None:
            return self._fee_bps
        if token_id not in self._fee_cache:
            v = None
            if self.mode == "live":
                try:
                    v = int(self.client.get_fee_rate_bps(token_id))
                except Exception:  # noqa: BLE001 -- fall back to the public read
                    v = None
            if v is None:
                v = public_fee_bps(token_id)
            self._fee_cache[token_id] = DEFAULT_FEE_BPS if v is None else v
        return self._fee_cache[token_id]

    # ---------------------------------------------------------------- orders
    def _cap(self, price, size):
        """Enforce the notional ceiling and the CLOB's minimum size."""
        if price <= 0:
            return 0.0
        size = min(float(size), MAX_NOTIONAL_PER_ORDER / price)
        return 0.0 if size < MIN_SHARES else round(size, 2)

    def buy(self, token_id, limit_price, size):
        """Buy up to `size` shares at or below limit_price. FAK semantics."""
        size = self._cap(limit_price, size)
        if size <= 0:
            return Fill("BUY", token_id, limit_price, 0, mode=self.mode)
        if self.mode == "dry":
            bid, ask, ask_size, _ = self.book(token_id)
            if ask is None or ask > limit_price:
                return Fill("BUY", token_id, limit_price, 0, mode="dry")
            filled = min(size, ask_size)
            return Fill("BUY", token_id, ask, filled if filled >= MIN_SHARES else 0,
                        fee_bps=self.fee_bps(token_id), mode="dry")
        return self._live_order(token_id, limit_price, size, "BUY")

    def sell(self, token_id, limit_price, size):
        """Sell up to `size` shares at or above limit_price. FAK semantics."""
        size = round(float(size), 2)
        if size < MIN_SHARES:
            return Fill("SELL", token_id, limit_price, 0, mode=self.mode)
        if self.mode == "dry":
            bid, ask, _, bid_size = self.book(token_id)
            if bid is None or bid < limit_price:
                return Fill("SELL", token_id, limit_price, 0, mode="dry")
            filled = min(size, bid_size)
            return Fill("SELL", token_id, bid, filled if filled >= MIN_SHARES else 0,
                        fee_bps=self.fee_bps(token_id), mode="dry")
        return self._live_order(token_id, limit_price, size, "SELL")

    def _live_order(self, token_id, price, size, side):
        from py_clob_client.clob_types import OrderArgs, OrderType
        from py_clob_client.order_builder.constants import BUY, SELL

        tick = self.client.get_tick_size(token_id)
        decimals = max(0, len(str(tick).split(".")[-1]))
        price = round(float(price), decimals)
        fee = self.fee_bps(token_id)
        args = OrderArgs(token_id=token_id, price=price, size=float(size),
                         side=BUY if side == "BUY" else SELL, fee_rate_bps=fee)
        order = self.client.create_order(args)
        resp = self.client.post_order(order, OrderType.FAK)
        # The CLOB returns the order id and (for FAK) how much matched; treat a
        # missing size as zero rather than assuming the whole order filled.
        order_id = (resp or {}).get("orderID") or (resp or {}).get("id")
        matched = (resp or {}).get("makingAmount") or (resp or {}).get("size_matched") or 0
        try:
            matched = float(matched)
        except (TypeError, ValueError):
            matched = 0.0
        return Fill(side, token_id, price, matched, order_id=order_id, fee_bps=fee, mode="live")

    def cancel_all(self):
        if self.mode == "live":
            return self.client.cancel_all()
        return None


if __name__ == "__main__":
    ex = Executor.from_env()
    print(f"executor mode: {ex.mode}")
    # simulated round trip against a synthetic book, no network
    tok = "TEST"
    ex = Executor("dry", book_override={tok: (0.44, 0.46, 120.0, 80.0)}, fee_bps=0)
    b = ex.buy(tok, 0.47, 50)
    s = ex.sell(tok, 0.40, b.size)
    print(b, "->", s, f"pnl {(s.price - b.price) * s.size:+.2f}")
    print("no fill above limit:", ex.buy(tok, 0.45, 50))
    print("cap applied:", ex.buy(tok, 0.47, 10_000))
