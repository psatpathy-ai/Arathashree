"""Template Kite client shim.

This is a safe, local-friendly shim that provides the minimal interface used by
arthashree integrations: `historical(symbol, interval, from_date, to_date)` and
`place_order(...)` if needed by live adapters.

By default this shim refuses to make network calls unless the required
environment variables are set (KITE_API_KEY, etc.). For local development,
set LOCAL_MOCK=1 to return sample data from tools/artifacts/normalized/CI_SAMPLE.csv.

IMPLEMENTATION NOTE:
- Replace the placeholder code with calls to the official Kite SDK or REST API.
- Do not commit real credentials; use environment variables or a secrets store.
"""
from __future__ import annotations
from typing import List, Dict, Optional
from pathlib import Path
import os
import csv


class Client:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, access_token: Optional[str] = None):
        self.api_key = api_key or os.getenv('KITE_API_KEY')
        self.api_secret = api_secret or os.getenv('KITE_API_SECRET')
        self.access_token = access_token or os.getenv('KITE_ACCESS_TOKEN')
        self.local_mock = bool(os.getenv('LOCAL_MOCK'))

        # If local mock mode, no credentials required
        if not self.local_mock and (not self.api_key or not self.api_secret):
            # Keep the client constructible but mark as unauthorized for live calls
            self._live_enabled = False
        else:
            self._live_enabled = True

    def historical(self, symbol: str, interval: str, from_date: str, to_date: str) -> List[Dict]:
        """Return list of dicts with keys: date, open, high, low, close, volume.

        Local mock mode will read tools/artifacts/normalized/CI_SAMPLE.csv for quick
        local testing. Replace this implementation with real SDK calls for live runs.
        """
        if self.local_mock:
            sample = Path(__file__).parent.parent.parent / 'tools' / 'artifacts' / 'normalized' / 'CI_SAMPLE.csv'
            if not sample.exists():
                raise FileNotFoundError(f"Local mock enabled but sample CSV not found at {sample}")
            out = []
            with sample.open('r') as fh:
                reader = csv.DictReader(fh)
                for r in reader:
                    # return as strings/numbers similar to SDK
                    out.append({
                        'date': r.get('date'),
                        'open': float(r.get('open')) if r.get('open') else None,
                        'high': float(r.get('high')) if r.get('high') else None,
                        'low': float(r.get('low')) if r.get('low') else None,
                        'close': float(r.get('close')) if r.get('close') else None,
                        'volume': float(r.get('volume')) if r.get('volume') else None,
                    })
            return out

        if not self._live_enabled:
            raise RuntimeError("Kite client not configured for live mode. Set KITE_API_KEY/KITE_API_SECRET or enable LOCAL_MOCK.")

        # TODO: Implement real SDK interaction here. For example using `kiteconnect`:
        # from kiteconnect import KiteConnect
        # kc = KiteConnect(api_key=self.api_key)
        # kc.set_access_token(self.access_token)
        # return kc.historical_data(symbol, interval, from_date, to_date)
        raise NotImplementedError("Live Kite client not implemented. Replace kite_client.Client.historical with real SDK calls.")

    def place_order(self, symbol: str, qty: int, price: float, side: str) -> Dict:
        """Placeholder for order placement. Returns a dict-like response.

        Local mock mode returns a fake filled response. Replace with SDK call for live.
        """
        if self.local_mock:
            return {"status": "success", "filled_qty": qty, "avg_fill_price": price}

        if not self._live_enabled:
            raise RuntimeError("Kite client not configured for live mode. Set KITE_API_KEY/KITE_API_SECRET or enable LOCAL_MOCK.")

        # TODO: Implement real order placement via SDK.
        raise NotImplementedError("Live order placement not implemented. Implement using provider SDK and ensure safety checks.")
