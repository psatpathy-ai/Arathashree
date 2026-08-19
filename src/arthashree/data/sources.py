from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .validation import load_ohlcv


@dataclass(frozen=True)
class DataProvenance:
    source: str
    symbol: str
    timestamp: str
    dataset_version: str | None = None
    source_hash: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataManifest:
    source: str
    symbol: str
    interval: str = "day"
    start: str | None = None
    end: str | None = None
    row_count: int = 0
    columns: list[str] = field(default_factory=list)
    provenance: DataProvenance | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.provenance is not None:
            payload["provenance"] = self.provenance.to_dict()
        return payload


class MarketDataSource:
    """Common market-data access contract for price, factor, and market data sources."""

    def __init__(self, symbol: str, *, source: str, interval: str = "day"):
        self.symbol = symbol
        self.source = source
        self.interval = interval
        self._last_provenance: DataProvenance | None = None

    def describe(self) -> DataManifest:
        raise NotImplementedError

    def get_bar(self, timestamp: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.Series:
        raise NotImplementedError

    def get_bars(self, start: str | pd.Timestamp, end: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.DataFrame:
        raise NotImplementedError

    def get_snapshot(self, timestamp: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.Series:
        return self.get_bar(timestamp, columns=columns)

    @property
    def last_provenance(self) -> DataProvenance | None:
        return self._last_provenance

    def _build_provenance(self, data: pd.DataFrame, *, metadata: dict[str, Any] | None = None) -> DataProvenance:
        payload = data.to_csv(index=True).encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()
        self._last_provenance = DataProvenance(
            source=self.source,
            symbol=self.symbol,
            timestamp=datetime.now(timezone.utc).isoformat(),
            dataset_version=metadata.get("dataset_version") if metadata else None,
            source_hash=digest,
            metadata=metadata or {},
        )
        return self._last_provenance


class InMemoryDataSource(MarketDataSource):
    """A data source backed by a local DataFrame."""

    def __init__(self, frame: pd.DataFrame, symbol: str, *, source: str = "memory", interval: str = "day"):
        self.frame = frame.copy()
        self.frame = self.frame.sort_index()
        super().__init__(symbol, source=source, interval=interval)
        self._manifest = self._build_manifest()

    def _build_manifest(self) -> DataManifest:
        provenance = self._build_provenance(self.frame)
        return DataManifest(
            source=self.source,
            symbol=self.symbol,
            interval=self.interval,
            start=str(self.frame.index.min()) if len(self.frame) else None,
            end=str(self.frame.index.max()) if len(self.frame) else None,
            row_count=len(self.frame),
            columns=list(self.frame.columns),
            provenance=provenance,
        )

    def describe(self) -> DataManifest:
        return self._manifest

    def get_bar(self, timestamp: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.Series:
        ts = pd.Timestamp(timestamp)
        if ts not in self.frame.index:
            raise KeyError(f"No bar for {self.symbol} at {ts.isoformat()}")
        row = self.frame.loc[ts]
        if columns is not None:
            return row[columns]
        return row

    def get_bars(self, start: str | pd.Timestamp, end: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.DataFrame:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        subset = self.frame[(self.frame.index >= start_ts) & (self.frame.index <= end_ts)]
        if columns is not None:
            subset = subset[columns]
        return subset


class CSVDataSource(InMemoryDataSource):
    """A source backed by a CSV file containing OHLCV data."""

    def __init__(self, path: str | Path, symbol: str, *, source: str = "csv", interval: str = "day"):
        frame = load_ohlcv(path)
        super().__init__(frame, symbol, source=source, interval=interval)


class ParquetDataSource(InMemoryDataSource):
    """A source backed by a Parquet file. This is intentionally lightweight and compatibility-focused."""

    def __init__(self, path: str | Path, symbol: str, *, source: str = "parquet", interval: str = "day"):
        try:
            frame = pd.read_parquet(path)
        except Exception as exc:  # pragma: no cover - depends on optional parquet dependency
            raise ValueError(f"Parquet source could not be loaded: {exc}") from exc
        super().__init__(frame, symbol, source=source, interval=interval)


class CachedDataSource(MarketDataSource):
    """Simple read-through cache for repeated symbol and time-window lookups."""

    def __init__(self, source: MarketDataSource):
        super().__init__(source.symbol, source=source.source, interval=source.interval)
        self.source = source
        self._cache: dict[tuple[str, str], pd.DataFrame | pd.Series] = {}

    def describe(self) -> DataManifest:
        return self.source.describe()

    def get_bar(self, timestamp: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.Series:
        key = ("bar", str(pd.Timestamp(timestamp)))
        if key not in self._cache:
            self._cache[key] = self.source.get_bar(timestamp, columns=columns)
        value = self._cache[key]
        if columns is not None and isinstance(value, pd.DataFrame):
            return value[columns]
        return value

    def get_bars(self, start: str | pd.Timestamp, end: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.DataFrame:
        key = ("bars", f"{pd.Timestamp(start)}::{pd.Timestamp(end)}")
        if key not in self._cache:
            self._cache[key] = self.source.get_bars(start, end, columns=columns)
        value = self._cache[key]
        if isinstance(value, pd.DataFrame):
            return value
        return pd.DataFrame(value)

    def get_snapshot(self, timestamp: str | pd.Timestamp, *, columns: list[str] | None = None) -> pd.Series:
        return self.get_bar(timestamp, columns=columns)


def materialize_manifest(source: MarketDataSource, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = source.describe().to_dict()
    if extra:
        manifest.update(extra)
    return manifest


def write_manifest(path: str | Path, source: MarketDataSource, *, extra: dict[str, Any] | None = None) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(materialize_manifest(source, extra=extra), indent=2, sort_keys=True))
