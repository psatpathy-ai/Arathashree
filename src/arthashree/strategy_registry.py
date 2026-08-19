from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from .strategy import Strategy, TargetAllocation


@dataclass
class RunCard:
    strategy: str
    symbol: str
    params: Dict[str, Any] | None = None


class StrategyRegistry:
    """Registry for strategy classes and helpers to execute a run-card.

    Production-grade features:
    - register/unregister strategies by name
    - instantiate strategies with parameters
    - execute run-cards with a consistent context
    """

    def __init__(self):
        self._registry: Dict[str, Type[Strategy]] = {}

    def register(self, name: str, cls: Type[Strategy]) -> None:
        if not issubclass(cls, Strategy):
            raise TypeError("Registered class must be a Strategy subclass")
        self._registry[name] = cls

    def unregister(self, name: str) -> None:
        if name in self._registry:
            del self._registry[name]

    def get(self, name: str) -> Type[Strategy] | None:
        return self._registry.get(name)

    def create(self, name: str, **kwargs) -> Strategy:
        cls = self.get(name)
        if cls is None:
            raise KeyError(f"Unknown strategy: {name}")
        return cls(**kwargs)

    def execute(self, run_card: RunCard, context: Dict[str, Any] | None = None) -> TargetAllocation:
        context = context.copy() if context else {}
        context.setdefault("symbol", run_card.symbol)
        context.update(run_card.params or {})
        strategy = self.create(run_card.strategy)
        strategy.prepare(context)
        return strategy.generate_target(context)

    def list(self) -> list[str]:
        return sorted(list(self._registry.keys()))
