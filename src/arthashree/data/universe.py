from __future__ import annotations

import pandas as pd


def constituents_on_date(membership: pd.DataFrame, date) -> list[str]:
    """Return only symbols active on the requested date."""
    required = {"symbol", "effective_from", "effective_to"}
    missing = required - set(membership.columns)
    if missing:
        raise ValueError(f"Universe membership missing columns: {sorted(missing)}")
    point = pd.Timestamp(date)
    start = pd.to_datetime(membership["effective_from"])
    end = pd.to_datetime(membership["effective_to"], errors="coerce")
    active = membership[start.le(point) & (end.isna() | end.ge(point))]
    return active["symbol"].astype(str).tolist()