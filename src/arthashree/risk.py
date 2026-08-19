from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    """Explicit transaction cost assumptions for a given market and execution path."""

    commission_bps: float = 5.0
    slippage_bps: float = 10.0
    impact_bps: float = 5.0
    borrow_bps: float = 0.0

    def estimate_trade_cost(self, notional: float) -> float:
        total_bps = self.commission_bps + self.slippage_bps + self.impact_bps + self.borrow_bps
        return notional * total_bps / 10000.0


@dataclass(frozen=True)
class RiskModel:
    """Default pre-trade risk constraints for a strategy."""

    risk_per_trade: float = 0.01
    max_position_notional_pct: float = 0.25

    def position_size(self, equity: float, entry_price: float, stop_price: float) -> int:
        if equity <= 0 or entry_price <= 0 or stop_price <= 0:
            return 0
        risk_distance = abs(entry_price - stop_price)
        if risk_distance <= 0:
            return 0
        risk_budget = equity * self.risk_per_trade
        qty_risk = math.floor(risk_budget / risk_distance)
        qty_notional = math.floor((equity * self.max_position_notional_pct) / entry_price)
        return max(0, min(qty_risk, qty_notional))


def position_size(equity, entry, stop, risk_fraction, max_notional_pct=1.0):
    risk_per_unit = abs(entry - stop)
    if risk_per_unit <= 0:
        return 0
    risk_budget = equity * risk_fraction
    qty_risk = math.floor(risk_budget / risk_per_unit)
    qty_notional = math.floor((equity * max_notional_pct) / entry)
    return max(0, min(qty_risk, qty_notional))
