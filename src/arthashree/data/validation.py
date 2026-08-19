from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize an OHLCV frame without silently repairing it."""
    out = df.copy()
    out.columns = [str(column).strip().lower() for column in out.columns]
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="raise")
        out = out.set_index("date")
    if not isinstance(out.index, pd.DatetimeIndex):
        raise ValueError("OHLCV requires a DatetimeIndex or date column")
    missing = [column for column in REQUIRED_OHLCV_COLUMNS if column not in out]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if out.index.has_duplicates:
        raise ValueError("OHLCV contains duplicate timestamps")
    if not out.index.is_monotonic_increasing:
        raise ValueError("Timestamps must be sorted in ascending order")
    for column in REQUIRED_OHLCV_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    if out[REQUIRED_OHLCV_COLUMNS].isna().any().any():
        raise ValueError("OHLCV contains NaN/non-numeric values")
    if (out["high"] < out["low"]).any():
        raise ValueError("Found high < low")
    if ((out["open"] < out["low"]) | (out["open"] > out["high"])).any():
        raise ValueError("Found open outside high/low range")
    if ((out["close"] < out["low"]) | (out["close"] > out["high"])).any():
        raise ValueError("Found close outside high/low range")
    if (out[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("OHLC prices must be positive")
    if (out["volume"] < 0).any():
        raise ValueError("Volume cannot be negative")
    return out


def load_ohlcv(path: str | Path) -> pd.DataFrame:
    """Load a CSV and return validated datetime-indexed OHLCV data."""
    frame = pd.read_csv(path)
    return validate_ohlcv(frame)