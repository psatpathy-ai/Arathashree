from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from .risk import RiskModel, CostModel
from .events import OrderEvent


@dataclass
class RiskDecision:
    approved: bool
    reason: str = "ok"


class RiskEngine:
    """Contract for risk approval engines.

    Implementations should provide `approve(order, portfolio, market)` returning a RiskDecision.
    """

    def approve(self, order: OrderEvent, portfolio: Dict[str, Any], market: Dict[str, Any] | None = None) -> RiskDecision:
        raise NotImplementedError


@dataclass
class DefaultRiskEngine(RiskEngine):
    model: RiskModel = RiskModel()
    costs: CostModel = CostModel()
    daily_loss_limit: float = 0.05  # fraction of equity

    def approve(self, order: OrderEvent, portfolio: Dict[str, Any], market: Dict[str, Any] | None = None) -> RiskDecision:
        # Basic checks
        if order is None:
            return RiskDecision(False, "no order")
        if portfolio is None:
            return RiskDecision(False, "no portfolio")

        equity = float(portfolio.get("equity", 0.0))
        if equity <= 0:
            return RiskDecision(False, "non-positive equity")

        entry_price = float(order.price) if order.price is not None else None
        stop_price = None
        # stop definition: prefer explicit payload, then market param
        if isinstance(order.payload, dict) and order.payload.get("stop_price") is not None:
            stop_price = float(order.payload.get("stop_price"))
        elif market and market.get("stop_price") is not None:
            stop_price = float(market.get("stop_price"))

        if entry_price is None or stop_price is None:
            return RiskDecision(False, "missing price/stop to compute risk")

        # Determine maximum allowed quantity by position sizing rules
        qty_allowed = int(self.model.position_size(equity, entry_price, stop_price))
        if qty_allowed <= 0:
            return RiskDecision(False, "position size computed as zero")

        # requested quantity
        qty_req = int(order.quantity)
        if qty_req <= 0:
            return RiskDecision(False, "non-positive quantity")

        if qty_req > qty_allowed:
            return RiskDecision(False, f"quantity {qty_req} exceeds allowed {qty_allowed}")

        # notional exposure check
        notional_after = qty_req * entry_price
        max_notional = equity * self.model.max_position_notional_pct
        if notional_after > max_notional:
            return RiskDecision(False, "notional exceeds max position notional pct")

        # daily loss check
        projected_loss = qty_req * abs(entry_price - stop_price)
        current_daily_loss = float(portfolio.get("daily_loss", 0.0))
        max_daily_loss = equity * self.daily_loss_limit
        if (current_daily_loss + projected_loss) > max_daily_loss:
            return RiskDecision(False, "would exceed daily loss limit")

        # otherwise approve
        return RiskDecision(True, "ok")
