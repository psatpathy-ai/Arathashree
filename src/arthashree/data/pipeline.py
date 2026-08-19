from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .sources import InMemoryDataSource, DataManifest, write_manifest, materialize_manifest, MarketDataSource
from .validation import load_ohlcv


def normalize_raw(path: str | Path, *, symbol: str | None = None, dest: str | Path = "data/normalized", overwrite: bool = False) -> DataManifest:
    """Normalize a raw OHLCV file into the normalized data directory and emit a manifest.

    This is a production-oriented normalization step that:
    - validates raw OHLCV using strict rules (no silent repairs)
    - writes a normalized CSV (and parquet when available)
    - emits a manifest JSON containing provenance and metadata

    Returns the generated DataManifest.
    """
    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Source path not found: {source_path}")

    frame = load_ohlcv(source_path)

    # Symbol inference
    if symbol is None:
        symbol = source_path.stem

    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Write canonical CSV
    csv_out = dest / f"{symbol}.csv"
    if csv_out.exists() and not overwrite:
        raise FileExistsError(f"Normalized CSV already exists: {csv_out}")
    frame.to_csv(csv_out, index=True)

    # Attempt parquet write if engine available; tolerate missing optional dependency
    parquet_out = dest / f"{symbol}.parquet"
    try:
        frame.to_parquet(parquet_out)
        wrote_parquet = True
    except Exception:
        wrote_parquet = False

    # Build a DataManifest using the in-memory source utility for consistent provenance
    src = InMemoryDataSource(frame, symbol, source=str(source_path), interval="day")
    manifest = src.describe()

    # Add write metadata
    extra = {
        "normalized_csv": str(csv_out),
        "normalized_parquet": str(parquet_out) if wrote_parquet else None,
    }

    # Write manifest to dest
    manifest_path = dest / f"{symbol}.manifest.json"
    write_manifest(manifest_path, src, extra=extra)

    # Return manifest dataclass for programmatic use
    return manifest


def read_manifest(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text())


def _load_manifest_schema() -> dict[str, Any]:
    schema_path = Path(__file__).parent / "manifest_schema.json"
    if not schema_path.exists():
        raise FileNotFoundError("Manifest schema not found")
    return json.loads(schema_path.read_text())


def validate_manifest_dict(manifest: dict[str, Any]) -> None:
    """Validate a manifest dict against the on-disk JSON Schema.

    Raises jsonschema.ValidationError on failure.
    """
    try:
        import jsonschema
    except Exception as exc:  # pragma: no cover - environment missing optional dep
        raise RuntimeError("jsonschema is required to validate manifests; install the 'jsonschema' package") from exc

    schema = _load_manifest_schema()
    jsonschema.validate(instance=manifest, schema=schema)


# Integrate validation into normalization: validate manifest before writing
_original_write_manifest = write_manifest

def _write_manifest_with_validation(path: str | Path, source: MarketDataSource, *, extra: dict[str, Any] | None = None) -> None:
    # materialize and validate
    manifest = materialize_manifest(source, extra=extra)
    validate_manifest_dict(manifest)
    # write to disk
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True))

# Replace the exported write_manifest with the validating variant
write_manifest = _write_manifest_with_validation
