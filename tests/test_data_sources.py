from pathlib import Path

import pandas as pd

from arthashree.data import CSVDataSource, InMemoryDataSource, MarketDataSource, write_manifest


def make_frame():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [1000, 1100, 1200],
        },
        index=idx,
    )


def test_in_memory_data_source_works():
    source = InMemoryDataSource(make_frame(), "INFY", source="memory")
    bar = source.get_bar("2024-01-02")
    assert bar["close"] == 101.5
    bars = source.get_bars("2024-01-01", "2024-01-02")
    assert len(bars) == 2
    manifest = source.describe()
    assert manifest.row_count == 3
    assert manifest.provenance is not None
    assert manifest.provenance.source == "memory"


def test_csv_data_source_materializes_manifest(tmp_path):
    path = tmp_path / "ohlcv.csv"
    frame = make_frame().reset_index().rename(columns={"index": "date"})
    frame.to_csv(path, index=False)

    source = CSVDataSource(path, "INFY", source="csv")
    assert source.get_bar("2024-01-03")["close"] == 102.5
    manifest = source.describe()
    assert manifest.provenance is not None
    assert manifest.provenance.source_hash

    out = tmp_path / "manifest.json"
    write_manifest(out, source, extra={"strategy": "trend_follow"})
    payload = out.read_text()
    assert "strategy" in payload
    assert "provenance" in payload


def test_market_data_source_is_an_abstract_contract():
    class DummySource(MarketDataSource):
        def describe(self):
            return None

        def get_bar(self, timestamp, *, columns=None):
            return None

        def get_bars(self, start, end, *, columns=None):
            return None

    source = DummySource("TCS", source="dummy")
    assert source.symbol == "TCS"
    assert source.source == "dummy"
