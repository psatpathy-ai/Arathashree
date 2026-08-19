from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Event:
    timestamp: datetime
    kind: str = "event"
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketEvent(Event):
    kind: str = "market"


@dataclass
class SignalEvent(Event):
    kind: str = "signal"
    signal: Any = None


@dataclass
class OrderEvent(Event):
    kind: str = "order"
    symbol: Optional[str] = None
    direction: str = "flat"
    quantity: int = 0
    price: float | None = None


@dataclass
class FillEvent(Event):
    kind: str = "fill"
    order: OrderEvent | None = None
    filled_quantity: int = 0
    fill_price: float | None = None


@dataclass
class RiskEvent(Event):
    kind: str = "risk"
    reason: str = "ok"


@dataclass
class PortfolioEvent(Event):
    kind: str = "portfolio"
    allocation: Dict[str, float] = field(default_factory=dict)


@dataclass
class TimerEvent(Event):
    kind: str = "timer"
    interval: str = "1D"
