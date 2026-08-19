from __future__ import annotations

from typing import Any

import pandas as pd

from .clock import LookAheadError, SimulationClock


class DataHandler:
    """Time-aware data access layer for deterministic market simulations."""

    def __init__(self, data: pd.DataFrame, clock: SimulationClock | None = None):
        self.data = data.copy()
        self.clock = clock or SimulationClock(self.data.index.min())

    def _ensure_present(self, timestamp: pd.Timestamp | str) -> pd.Timestamp:
        ts = pd.Timestamp(timestamp)
        self.clock.assert_not_lookahead(ts)
        if ts not in self.data.index:
            idx = self.data.index.searchsorted(ts)
            if idx == 0:
                raise KeyError(f"No data available before {ts.isoformat()}")
            ts = self.data.index[idx - 1]
        return ts

    def get_data(self, timestamp: pd.Timestamp | str, columns: list[str] | None = None) -> pd.Series | pd.DataFrame:
        ts = self._ensure_present(timestamp)
        row = self.data.loc[ts]
        if columns is not None:
            row = row[columns]
        return row

    def get_bars(self, start: pd.Timestamp | str, end: pd.Timestamp | str) -> pd.DataFrame:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        self.clock.assert_not_lookahead(end_ts)
        mask = (self.data.index >= start_ts) & (self.data.index <= end_ts)
        return self.data.loc[mask]

    def get_snapshot(self, timestamp: pd.Timestamp | str) -> pd.Series:
        return self.get_data(timestamp)

    @property
    def latest_timestamp(self) -> pd.Timestamp:
        return self.data.index[-1]

    def advance_to(self, timestamp: pd.Timestamp | str) -> pd.Timestamp:
        ts = pd.Timestamp(timestamp)
        self.clock.advance_to(ts)
        return ts
