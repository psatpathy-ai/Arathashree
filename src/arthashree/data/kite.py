from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .validation import validate_ohlcv


class KiteHistoricalDownloader:
    """Download Kite candles through an injected read-only client."""

    def __init__(self, client, output_dir: str | Path):
        self.client = client
        self.output_dir = Path(output_dir)

    def download(self, instrument: dict, start, end, interval="day") -> tuple[pd.DataFrame, dict]:
        candles = self.client.historical_data(
            instrument["instrument_token"], start, end, interval, oi=True
        )
        frame = pd.DataFrame(candles)
        if "date" not in frame:
            raise ValueError("Kite response requires a date column")
        frame = validate_ohlcv(frame.rename(columns={"oi": "open_interest"}))
        raw_path = self.output_dir / "raw" / f"{instrument['exchange']}_{instrument['tradingsymbol']}_{interval}.csv"
        metadata_path = self.output_dir / "raw" / f"{instrument['exchange']}_{instrument['tradingsymbol']}_{interval}.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(raw_path, index_label="date")
        metadata = self._metadata(instrument, interval, start, end, raw_path)
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
        return frame, metadata

    @staticmethod
    def _metadata(instrument, interval, start, end, path: Path) -> dict:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {
            "source": "zerodha_kite_historical",
            "instrument_token": int(instrument["instrument_token"]),
            "exchange": instrument["exchange"],
            "symbol": instrument["tradingsymbol"],
            "interval": interval,
            "start": str(start),
            "end": str(end),
            "download_time": datetime.now(timezone.utc).isoformat(),
            "data_hash": digest,
        }