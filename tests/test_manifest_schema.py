import json
from pathlib import Path

from arthashree.data import read_manifest, normalize_raw
from arthashree.data.pipeline import validate_manifest_dict


def test_manifest_validates(tmp_path: Path):
    sample = Path("data/sample_ohlcv.csv")
    dest = tmp_path / "normalized"
    dest.mkdir()

    manifest = normalize_raw(sample, symbol="SCHEMA_TEST", dest=dest, overwrite=True)
    mf = read_manifest(dest / "SCHEMA_TEST.manifest.json")

    # ensure the manifest dict is valid per schema
    validate_manifest_dict(mf)

    # ensure essential fields
    assert mf["symbol"] == "SCHEMA_TEST"
    assert mf["row_count"] == manifest.row_count
