from __future__ import annotations

from pathlib import Path

import pandas as pd

INSTRUMENT_COLUMNS = [
    "exchange", "tradingsymbol", "instrument_token", "segment",
    "instrument_type", "expiry", "strike", "tick_size", "lot_size",
]


class KiteInstrumentLoader:
    """Load and resolve the current Kite instrument master from a local file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        frame = pd.read_csv(self.path)
        frame.columns = [str(column).strip().lower() for column in frame.columns]
        missing = [column for column in INSTRUMENT_COLUMNS if column not in frame]
        if missing:
            raise ValueError(f"Instrument master missing columns: {missing}")
        if frame["instrument_token"].duplicated().any():
            raise ValueError("Instrument master contains duplicate instrument tokens")
        return frame[INSTRUMENT_COLUMNS].copy()

    def resolve(self, exchange: str, tradingsymbol: str) -> dict:
        matches = self.load()
        matches = matches[
            (matches["exchange"].str.upper() == exchange.upper())
            & (matches["tradingsymbol"].str.upper() == tradingsymbol.upper())
        ]
        if len(matches) != 1:
            raise LookupError(f"Expected one instrument for {exchange}:{tradingsymbol}, found {len(matches)}")
        return matches.iloc[0].to_dict()