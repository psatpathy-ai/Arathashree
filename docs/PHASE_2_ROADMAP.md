# PHASE 2 Roadmap

## Phase 2.1 — Core architecture and code quality

Objective:
- harden the existing foundation;
- establish shared domain contracts;
- improve code quality and quantitative utility.

Features:
- stable `clock` and `data_handler` contracts;
- strategy target API;
- cost and risk models;
- quant analytics primitives;
- unit tests and edge-case validation.

Files/modules involved:
- `src/arthashree/clock.py`
- `src/arthashree/data_handler.py`
- `src/arthashree/strategy.py`
- `src/arthashree/risk.py`
- `src/arthashree/__init__.py`
- `tests/test_architecture.py`

Dependencies:
- existing pandas/numpy stack only

Tests:
- unit tests for clock bounds;
- access control and look-ahead rejection;
- strategy target contract; risk calculation regression.

Acceptance criteria:
- no look-ahead in simulation paths;
- target-based strategy allocation works; risk model is explicit; tests pass.

Performance considerations:
- low; keep this domain-layer work lightweight.

Risks:
- too much abstraction too early; keep it minimal.

## Phase 2.2 — Quant analytics foundation

Objective:
- create an analytics library for deterministic metrics and exposures.

Features:
- returns, log returns, volatility, Sharpe, Sortino, drawdown, z-score, correlation, covariance, rolling stats.

Files/modules involved:
- `src/arthashree/quant.py`
- `tests/test_quant.py`

Dependencies:
- pandas, numpy

Acceptance criteria:
- functions are deterministic and tested numerically;
- edge cases handled; type hints and docstrings complete.

## Phase 2.3 — Market data abstraction

Objective:
- standardize market-data access and provenance.

Features:
- `MarketDataSource` interface;
- source implementations for NSE/Kite/Parquet/CSV;
- data manifest and metadata model.

## Phase 2.4 — Strategy framework

Objective:
- make strategy lifecycle explicit and comparable.

Features:
- strategy registry;
- benchmark comparisons;
- target allocations and signal explanation;
- multi-strategy instrument registry.

## Phase 2.5 — Professional backtesting

Objective:
- upgrade from a simple loop to a robust engine.

Features:
- event-driven engine;
- realistic fills; slippage; transaction cost; turnover; exposure metrics.

## Phase 2.6 — Portfolio construction

Objective:
- create portfolio-level position logic.

Features:
- position bookkeeping;
- target weights and rebalancing;
- concentration and exposure limits;
- attribution.

## Phase 2.7 — Risk engine

Objective:
- make risk independent from the AI layer.

Features:
- maximum position size;
- portfolio exposure; drawdown; volatility; daily loss;
- stop-trading conditions; alerts.

## Phase 2.8 — Options / derivatives analytics

Objective:
- prepare the platform for derivative research.

Features:
- option chain abstraction;
- Greeks; implied volatility; pricing primitives.

## Phase 2.9 — AI research agents

Objective:
- add bounded research agents and evaluation flows.

Features:
- hypothesis model;
- agent loop;
- strategy evaluation and risk explanation;
- run cards and artifact review.

## Phase 2.10 — Execution architecture

Objective:
- formalize execution and broker boundary.

Features:
- broker adapters;
- order management;
- paper trading and execution service;
- live gate approvals.

## Phase 2.11 — Monitoring and observability

Objective:
- provide structured logging and auditability.

Features:
- metrics emitter;
- event stream;
- alerting;
- artifact registry.

## Phase 2.12 — Full validation and performance optimization

Objective:
- complete the production-hardening pass.

Features:
- Monte Carlo + walk-forward validation;
- performance regression tests;
- profiling; dataset caching; vectorization; serialization cleanup.

## Execution principle

Each milestone should be implemented in small, testable increments. The project should never skip from diagnosis to a broad rewrite. Each milestone must pass tests and maintain backward compatibility.
