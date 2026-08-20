from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Any


@dataclass
class ExecutionResult:
    filled: bool
    filled_qty: int
    filled_price: float
    fees: float
    info: Dict[str, Any] | None = None


class ExecutionAdapter(Protocol):
    """Protocol for execution adapters.

    Implementations should provide a send_order() method that attempts to
    execute an order and returns an ExecutionResult describing the fill.
    """

    def send_order(self, order: Any, portfolio_snapshot: Dict[str, Any]) -> ExecutionResult:
        ...


class PaperExecutionAdapter:
    """Simple paper execution adapter that simulates immediate fills at the
    requested price and calculates fees.
    """

    def __init__(self, commission_bps: float = 2.0):
        # commission_bps is in basis points (e.g., 2.0 = 2 bps)
        self.commission = float(commission_bps) / 10000.0

    def send_order(self, order: Any, portfolio_snapshot: Dict[str, Any]) -> ExecutionResult:
        # assume order has quantity and price
        qty = int(getattr(order, 'quantity', getattr(order, 'qty', 0)))
        price = float(getattr(order, 'price', getattr(order, 'px', 0.0)))
        notional = qty * price
        fees = notional * self.commission
        return ExecutionResult(filled=True, filled_qty=qty, filled_price=price, fees=fees, info={'simulated': True})
