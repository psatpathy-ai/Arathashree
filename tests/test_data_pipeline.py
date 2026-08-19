import json
from pathlib import Path

import pandas as pd

from arthashree.data import normalize_raw, read_manifest, load_ohlcv


def test_normalize_and_manifest(tmp_path: Path):
    sample = Path("data/sample_ohlcv.csv")
    assert sample.exists(), "sample data must exist in repo for this test"

    dest = tmp_path / "normalized"
    dest.mkdir()

    manifest = normalize_raw(sample, symbol="SAMPLE_TEST", dest=dest, overwrite=True)

    # manifest object should report row_count and columns
    assert manifest.row_count > 0
    assert set(["open", "high", "low", "close", "volume"]).issubset(set(manifest.columns))

    manifest_file = dest / "SAMPLE_TEST.manifest.json"
    assert manifest_file.exists()

    data = read_manifest(manifest_file)
    assert data["symbol"] == "SAMPLE_TEST"
    assert data["row_count"] == manifest.row_count

    # read the normalized CSV and compare row counts
    csv_path = dest / "SAMPLE_TEST.csv"
    assert csv_path.exists()
    df = load_ohlcv(csv_path)
    assert len(df) == manifest.row_count
