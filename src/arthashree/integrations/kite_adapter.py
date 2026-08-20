"""Kite Connect integration (historical fetch + streaming scaffold).

This module provides a small, testable adapter to fetch historical OHLCV
via Kite-like REST endpoints. It is written to be mockable for unit tests
(it does not call any real Kite APIs directly here).
"""
from __future__ import annotations
from typing import Optional
from pathlib import Path
import pandas as pd
import time


def fetch_historical(symbol: str, interval: str, start: str, end: str, limit: int = 1000, api_client: Optional[object] = None) -> pd.DataFrame:
    """Fetch historical OHLCV for symbol between start and end.

    api_client: optional HTTP client or wrapped Kite client. If None, this
    function raises — callers/tests should pass a mock client.

    Returns a DataFrame with columns: date, open, high, low, close, volume
    and the date column as datetime.
    """
    if api_client is None:
        raise RuntimeError("api_client is required for fetch_historical in production — pass a requests-like client or mock for tests")

    # The api_client should implement a method `historical(symbol, interval, from_date, to_date)`
    raw = api_client.historical(symbol, interval, start, end)
    # raw expected to be a list of dicts with keys date/open/high/low/close/volume
    df = pd.DataFrame(raw)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        # attempt common alternatives
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp'])
    cols = ['date', 'open', 'high', 'low', 'close', 'volume']
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols]
    return df


def fetch_and_write(symbol: str, interval: str, start: str, end: str, dest: Path, api_client: Optional[object] = None, overwrite: bool = False) -> Path:
    """Fetch historical data and write a normalized CSV into dest.

    Returns the path to the written CSV.
    """
    dest = Path(dest)
    # ensure destination directory exists (create the dir itself, not just its parent)
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{symbol}.csv"
    if out.exists() and not overwrite:
        return out

    df = fetch_historical(symbol, interval, start, end, api_client=api_client)
    # Normalize columns
    df = df.sort_values('date')
    df.to_csv(out, index=False)
    # simple throttle: sleep a tiny bit to avoid hammering real APIs when caller forgets
    time.sleep(0.1)
    return out
