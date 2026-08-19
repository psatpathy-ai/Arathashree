# Data pipeline and manifests

This document describes the normalization pipeline used by Arthashree.

The normalize_raw function:

- Validates raw OHLCV with strict rules (no silent repairs).
- Writes a canonical normalized CSV under `data/normalized/<symbol>.csv`.
- Attempts to write a parquet file when the runtime supports it.
- Emits a manifest JSON containing provenance (SHA256 of the written dataset), row counts and column lists.

Usage example:

```python
from arthashree.data import normalize_raw

manifest = normalize_raw("data/raw/MYSYMBOL.csv", symbol="MYSYMBOL", dest="data/normalized")
print(manifest.to_dict())
```

Manifests are JSON documents with the following keys: source, symbol, interval, start, end, row_count, columns, provenance.
