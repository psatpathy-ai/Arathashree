# Kite integration (scaffold)

This document describes the scaffolded Kite integration. It is a safe-by-default implementation intended for local development and testing. Do not run in live mode without confirming required environment variables and safety policies.

Required environment variables for live runs:
- KITE_API_KEY
- KITE_API_SECRET
- KITE_ACCESS_TOKEN
- KITE_REFRESH_TOKEN

Dry-run mode:
- The adapter supports run_live=False to avoid placing real orders. This is the default in most CI and local runs.

Fetching historical data:
- Use the CLI helper tools/kite_fetch.py to fetch historical data into data/raw and normalize it to data/normalized.
- Example: python tools/kite_fetch.py --symbol TEST --from 2020-01-01 --to 2020-02-01 --dest data/raw --overwrite

Notes:
- A template kite client shim is available at src/arthashree/integrations/kite_client.py. It supports LOCAL_MOCK=1 for local testing using the sample CSV (tools/artifacts/normalized/CI_SAMPLE.csv).
- Implement full OAuth/token refresh and secure secret storage before running live. Do NOT commit credentials into the repo.

Security & secrets
- Local development: put secrets in a local .env file and load them into the environment (do NOT commit .env). Example .env contents:
  KITE_API_KEY=your_key_here
  KITE_API_SECRET=your_secret_here
  KITE_ACCESS_TOKEN=your_access_token
  KITE_REFRESH_TOKEN=your_refresh_token
- CI/GitHub Actions: store KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN, KITE_REFRESH_TOKEN as GitHub Secrets and reference them in workflow env or secrets.

LOCAL_MOCK usage
- To run integration locally without credentials, set LOCAL_MOCK=1 in your environment. The provided kite_client shim will then use the sample CSV and the code will run end-to-end in dry-run mode.

Example: run a local integration
- Export LOCAL_MOCK=1
- python tools/ci_integration.py

When ready for live:
- Replace the TODOs in src/arthashree/integrations/kite_client.py with real SDK calls (kiteconnect or direct REST).
- Keep run_live=False by default in the KiteExecutionAdapter until you have tested reconciliation and safety checks.
