from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from .strategy import Strategy, TargetAllocation


@dataclass
class RunCard:
    strategy: str
    symbol: str
    params: Dict[str, Any] | None = None


from pathlib import Path
import json

class StrategyRegistry:
    """Registry for strategy classes and helpers to execute a run-card.

    Production-grade features:
    - register/unregister strategies by name
    - instantiate strategies with parameters
    - execute run-cards with a consistent context
    - simple persistence/catalog for registered strategies (JSON)
    - support for strategy metadata and versioning
    """

    def __init__(self):
        self._registry: Dict[str, Type[Strategy]] = {}
        self._meta: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, cls: Type[Strategy], *, version: str | None = None, description: str | None = None) -> None:
        if not issubclass(cls, Strategy):
            raise TypeError("Registered class must be a Strategy subclass")
        self._registry[name] = cls
        self._meta[name] = {
            "name": name,
            "version": version or getattr(cls, "version", None),
            "description": description or getattr(cls, "__doc__", ""),
        }

    def unregister(self, name: str) -> None:
        if name in self._registry:
            del self._registry[name]
        if name in self._meta:
            del self._meta[name]

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

    def metadata(self, name: str) -> Dict[str, Any] | None:
        return self._meta.get(name)

    def catalog(self) -> Dict[str, Dict[str, Any]]:
        """Return a shallow copy of the registry metadata for cataloging."""
        return dict(self._meta)

    def save_catalog(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.catalog(), indent=2, sort_keys=True))

    def load_catalog(self, path: str | Path) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        data = json.loads(p.read_text())
        # Only restore metadata; classes must be re-registered by code
        self._meta.update(data)
