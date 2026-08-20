"""Execution adapter that wraps a Kite-like broker client.

This implementation is safe-by-default: unless run_live=True is passed, the
adapter operates in dry-run mode (does not submit real orders). It is written
so tests can mock the underlying client.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
from ..execution import ExecutionResult


@dataclass
class KiteExecutionAdapter:
    client: Any
    run_live: bool = False
    commission_bps: float = 2.0

    def send_order(self, order: Any, portfolio_snapshot: Dict[str, Any]) -> ExecutionResult:
        """Send an order to the broker client.

        If run_live is False, return a simulated fill (dry-run). If True,
        attempt to place the order via client.place_order(...) and return
        a real ExecutionResult constructed from the broker response.
        """
        qty = int(getattr(order, 'quantity', getattr(order, 'qty', 0)))
        price = float(getattr(order, 'price', getattr(order, 'px', 0.0)))
        notional = qty * price
        fees = notional * (float(self.commission_bps) / 10000.0)

        if not self.run_live:
            # Dry-run/paper: simulate an immediate fill
            return ExecutionResult(filled=True, filled_qty=qty, filled_price=price, fees=fees, info={"dry_run": True})

        # Live mode: call into the client (assumes client has place_order)
        resp = self.client.place_order(symbol=order.symbol, qty=qty, price=price, side=order.direction)
        # The exact mapping depends on the client's response format — keep tolerant
        filled = bool(resp.get('status') in ('success', 'filled', 'complete'))
        filled_qty = int(resp.get('filled_qty', qty if filled else 0))
        filled_price = float(resp.get('avg_fill_price', price if filled else 0.0))
        return ExecutionResult(filled=filled, filled_qty=filled_qty, filled_price=filled_price, fees=fees, info=resp)
