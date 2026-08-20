"""CLI helper to fetch historicals via a Kite-like client and normalize them."""
from pathlib import Path
import argparse

from arthashree.integrations.kite_adapter import fetch_and_write
from arthashree.data.pipeline import normalize_raw


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', required=True)
    p.add_argument('--interval', default='day')
    p.add_argument('--from', dest='from_date', required=True)
    p.add_argument('--to', dest='to_date', required=True)
    p.add_argument('--dest', default='data/raw')
    p.add_argument('--overwrite', action='store_true')
    args = p.parse_args()

    # Caller must provide a real client in production; for local quick runs, we
    # expect a small mock client module 'kite_client' to be importable. This keeps
    # the tool testable without secrets.
    try:
        import kite_client as client_module
        client = client_module.Client()
    except Exception:
        client = None

    out = fetch_and_write(args.symbol, args.interval, args.from_date, args.to_date, Path(args.dest) / args.symbol, api_client=client, overwrite=args.overwrite)
    print('Wrote raw CSV to', out)
    # attempt normalization
    try:
        manifest = normalize_raw(out, symbol=args.symbol, dest=Path('data/normalized'), overwrite=args.overwrite)
        print('Normalized to', manifest)
    except Exception as e:
        print('Normalization skipped/failed:', e)


if __name__ == '__main__':
    main()
