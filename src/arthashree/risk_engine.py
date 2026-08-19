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
    max_total_exposure_pct: float = 1.0  # fraction of equity allowed as total exposure
    max_concentration_pct: float = 0.5  # max fraction of equity in a single symbol
    margin_requirement: float = 0.25  # fraction of notional required as margin

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

        if entry_price is None or stop_price is None or not (entry_price > 0 and stop_price > 0):
            return RiskDecision(False, "missing/invalid price/stop to compute risk")

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

        # requested notional
        notional_req = qty_req * entry_price

        # notional per-position cap (existing behavior)
        max_notional = equity * self.model.max_position_notional_pct
        if notional_req > max_notional:
            return RiskDecision(False, "notional exceeds max position notional pct")

        # portfolio exposure checks
        open_positions = portfolio.get("open_positions", []) or []
        total_existing_exposure = sum(float(p.get("notional", 0.0)) for p in open_positions)
        total_exposure_after = total_existing_exposure + notional_req
        if total_exposure_after > equity * self.max_total_exposure_pct:
            return RiskDecision(False, "would exceed total exposure limit")

        # concentration check: find max exposure for any symbol after adding this
        symbol = getattr(order, "symbol", None) or (order.payload or {}).get("symbol")
        symbol = str(symbol) if symbol is not None else None
        exposure_by_symbol = {}
        for p in open_positions:
            sym = p.get("symbol")
            exposure_by_symbol[sym] = exposure_by_symbol.get(sym, 0.0) + float(p.get("notional", 0.0))
        if symbol:
            exposure_by_symbol[symbol] = exposure_by_symbol.get(symbol, 0.0) + notional_req
        max_symbol_exposure = max(exposure_by_symbol.values()) if exposure_by_symbol else 0.0
        if max_symbol_exposure > equity * self.max_concentration_pct:
            return RiskDecision(False, "would exceed concentration limit for a single symbol")

        # margin check: require available equity to cover margin for new notional
        required_margin = notional_req * self.margin_requirement
        available_equity = equity - total_existing_exposure * self.margin_requirement
        if available_equity < required_margin:
            return RiskDecision(False, "insufficient margin for requested position")

        # daily loss check
        projected_loss = qty_req * abs(entry_price - stop_price)
        current_daily_loss = float(portfolio.get("daily_loss", 0.0))
        max_daily_loss = equity * self.daily_loss_limit
        if (current_daily_loss + projected_loss) > max_daily_loss:
            return RiskDecision(False, "would exceed daily loss limit")

        # otherwise approve
        return RiskDecision(True, "ok")
