from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd

from .validation import validate_ohlcv


class NSEHistoricalDownloader:
    """Download an explicitly selected NSE CSV endpoint; no page scraping."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)

    def download(self, url: str, symbol: str, target_name: str) -> tuple[pd.DataFrame, dict]:
        request = Request(url, headers={"User-Agent": "Arthashree research data client"})
        with urlopen(request) as response:
            payload = response.read()
        frame = validate_ohlcv(pd.read_csv(pd.io.common.BytesIO(payload)))
        raw_path = self.output_dir / "raw" / target_name
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(payload)
        metadata = {
            "source": "nse_historical_endpoint",
            "symbol": symbol,
            "url": url,
            "download_time": datetime.now(timezone.utc).isoformat(),
            "data_hash": hashlib.sha256(payload).hexdigest(),
        }
        metadata_path = raw_path.with_suffix(".json")
        metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True))
        return frame, metadata