# Arthashree v0.1 — Probabilistic Systematic Trading Research Engine

This is the first implementation milestone of the Arthashree project.

## Design principles

1. Every trade must have a defined entry, invalidation/stop, position size and exit logic.
2. No strategy is assumed profitable before out-of-sample validation.
3. The engine models commissions and slippage explicitly.
4. Signals are shifted so today's close cannot trade on information that was only known after today's close.
5. Risk is based on stop distance and equity, not conviction.
6. No martingale / averaging down.
7. Strategy research is separated from portfolio/risk/execution simulation.
8. Backtests must be reproducible from a config file.

The architecture translates principles from *Trading in the Zone* into machine-enforceable controls and uses technical-analysis/risk-management concepts from *Trading for a Living* as hypotheses, not guarantees.

## Current strategy hypothesis

`triple_screen_trend_pullback`:

- Higher-timeframe trend: weekly close above weekly EMA(26) and EMA slope positive.
- Daily trend: close above EMA(50).
- Momentum confirmation: daily MACD histogram > 0.
- Entry: RSI(14) crosses back above 50 after being below 50.
- Exit: ATR-based stop, 2R target, or trend failure.
- Risk: 1% of current equity per trade, with a configurable cap.
- One position at a time in v0.1.

This is deliberately simple. Complexity will only be added if walk-forward evidence justifies it.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m arthashree.cli backtest --data data/sample_ohlcv.csv --config config/default.json
python -m arthashree.cli validate --data data/sample_ohlcv.csv --config config/default.json
python -m pytest -q
```

This project targets Python 3.10+ and uses the repository's existing `pytest` setup from `pyproject.toml`.

## CI

The repository includes a GitHub Actions workflow that runs the test suite automatically on pushes and pull requests.

## Real NSE data

Use a point-in-time, adjusted or correctly corporate-action-treated OHLCV dataset. NSE provides historical index/security and derivatives data through its historical-data facilities.

Phase 1 data boundaries are now available under `arthashree.data`: local
OHLCV is strictly validated, Kite instruments resolve from a local master,
and passive NSE/Kite historical downloaders write raw data with metadata.
Downloaded data belongs in `data/raw/`; normalized research data belongs in
`data/normalized/`. No downloader places orders or enables live trading.

Expected CSV columns:

`date,open,high,low,close,volume`

Do not mix revised/future information into historical rows.

## Important

The included dataset is synthetic and is ONLY a pipeline smoke test. Its result must not be interpreted as evidence of a real trading edge.

The next milestone is to run this exact engine against real NIFTY 50/security data, then perform walk-forward and robustness testing.
