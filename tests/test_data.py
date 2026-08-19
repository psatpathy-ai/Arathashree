import json

import pandas as pd
import pytest

from arthashree.data.instruments import KiteInstrumentLoader
from arthashree.data.kite import KiteHistoricalDownloader
from arthashree.data.universe import constituents_on_date
from arthashree.data.validation import validate_ohlcv


def ohlcv_frame():
    return pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [1000, 1200],
        }
    )


def test_validation_rejects_duplicate_timestamps():
    frame = pd.concat([ohlcv_frame(), ohlcv_frame().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        validate_ohlcv(frame)


def test_instrument_loader_resolves_one_current_instrument(tmp_path):
    path = tmp_path / "instruments.csv"
    pd.DataFrame(
        [
            {
                "exchange": "NSE",
                "tradingsymbol": "INFY",
                "instrument_token": 408065,
                "segment": "NSE",
                "instrument_type": "EQ",
                "expiry": "",
                "strike": 0,
                "tick_size": 0.05,
                "lot_size": 1,
            }
        ]
    ).to_csv(path, index=False)
    instrument = KiteInstrumentLoader(path).resolve("nse", "infy")
    assert instrument["instrument_token"] == 408065


def test_universe_is_point_in_time():
    membership = pd.DataFrame(
        [
            {"symbol": "OLD", "effective_from": "2020-01-01", "effective_to": "2021-12-31"},
            {"symbol": "NEW", "effective_from": "2022-01-01", "effective_to": None},
        ]
    )
    assert constituents_on_date(membership, "2022-02-01") == ["NEW"]


class FakeKiteClient:
    def historical_data(self, token, start, end, interval, oi):
        assert (token, interval, oi) == (408065, "day", True)
        return [
            {"date": "2024-01-01", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000},
        ]


def test_kite_downloader_writes_metadata(tmp_path):
    instrument = {"exchange": "NSE", "tradingsymbol": "INFY", "instrument_token": 408065}
    frame, metadata = KiteHistoricalDownloader(FakeKiteClient(), tmp_path).download(
        instrument, "2024-01-01", "2024-01-02"
    )
    assert len(frame) == 1
    assert metadata["source"] == "zerodha_kite_historical"
    metadata_path = tmp_path / "raw" / "NSE_INFY_day.json"
    assert json.loads(metadata_path.read_text())["data_hash"] == metadata["data_hash"]