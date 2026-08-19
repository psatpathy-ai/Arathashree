from __future__ import annotations

from datetime import datetime


class LookAheadError(RuntimeError):
    """Raised when a strategy or data query requests a timestamp beyond the current simulation clock."""


class SimulationClock:
    """Deterministic clock for backtests and research simulations."""

    def __init__(self, current_time: datetime | str | None = None):
        self.current = self._coerce(current_time) if current_time is not None else None

    @staticmethod
    def _coerce(value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    def advance_to(self, new_time: datetime | str) -> datetime:
        next_time = self._coerce(new_time)
        if self.current is not None and next_time < self.current:
            raise ValueError(f"Simulation clock cannot move backwards: {next_time} < {self.current}")
        self.current = next_time
        return self.current

    def assert_not_lookahead(self, requested_time: datetime | str) -> None:
        requested = self._coerce(requested_time)
        if self.current is None:
            return
        if requested > self.current:
            raise LookAheadError(
                f"Requested time {requested.isoformat()} exceeds the simulation clock {self.current.isoformat()}"
            )

    @property
    def now(self) -> datetime:
        if self.current is None:
            raise ValueError("Simulation clock has not been initialized")
        return self.current
