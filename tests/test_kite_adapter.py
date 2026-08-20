import pandas as pd
from types import SimpleNamespace
from arthashree.integrations.kite_adapter import fetch_historical, fetch_and_write
from pathlib import Path


class MockClient:
    def historical(self, symbol, interval, start, end):
        # return 3 rows of simplistic OHLCV
        return [
            {"date": "2020-01-01", "open": 100, "high": 101, "low": 99, "close": 100.5, "volume": 1000},
            {"date": "2020-01-02", "open": 100.5, "high": 102, "low": 100, "close": 101.0, "volume": 1200},
            {"date": "2020-01-03", "open": 101.0, "high": 103, "low": 100.5, "close": 102.5, "volume": 1100},
        ]


def test_fetch_historical():
    client = MockClient()
    df = fetch_historical('TEST', 'day', '2020-01-01', '2020-01-03', api_client=client)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['date', 'open', 'high', 'low', 'close', 'volume']
    assert len(df) == 3


def test_fetch_and_write(tmp_path):
    client = MockClient()
    out_dir = tmp_path / 'out'
    out = fetch_and_write('TEST', 'day', '2020-01-01', '2020-01-03', out_dir / 'TEST', api_client=client, overwrite=True)
    # file written
    assert Path(out).exists()
    text = Path(out).read_text()
    assert '100.5' in text
