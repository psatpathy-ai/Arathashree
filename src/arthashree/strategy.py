from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TargetAllocation:
    direction: str
    weight: float
    symbol: str | None = None

    def __post_init__(self):
        if self.direction not in {"long", "short", "flat"}:
            raise ValueError(f"Unsupported target direction: {self.direction}")

    def __str__(self) -> str:
        return f"{self.direction.upper()} {self.weight:.2%}" if self.direction != "flat" else "FLAT"


class Strategy:
    """Base contract for a systematic strategy.

    Strategies should generate a target allocation rather than placing broker orders directly.
    """

    name: str = "base_strategy"
    version: str = "0.1.0"

    def __init__(self, name: str | None = None, version: str | None = None):
        self.name = name or self.name
        self.version = version or self.version

    def prepare(self, context: dict[str, Any]) -> None:
        return None

    def generate_signal(self, context: dict[str, Any]) -> Any:
        return None

    def generate_target(self, context: dict[str, Any]) -> TargetAllocation:
        weight = float(context.get("weight", 0.0))
        direction = str(context.get("direction", "long" if weight > 0 else "flat")).lower()
        if direction not in {"long", "short", "flat"}:
            direction = "flat"
        if direction == "flat":
            weight = 0.0
        return TargetAllocation(direction=direction, weight=abs(weight))

    def explain(self, context: dict[str, Any]) -> dict[str, Any]:
        return {"strategy": self.name, "version": self.version, "target": str(self.generate_target(context))}


def generate_signals(df: pd.DataFrame) -> pd.Series:
    return df["signal"].astype(bool)
