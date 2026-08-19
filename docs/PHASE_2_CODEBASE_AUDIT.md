# PHASE 2 Codebase Audit

## Executive summary

Arthashree is already a credible Phase 1 foundation for a research-first systematic trading engine. The codebase has the right instincts: it treats risk, data validation, and out-of-sample evaluation as first-class concerns. However, it is still a compact research prototype rather than a production-grade quantitative platform.

The most important gaps are not conceptual; they are structural:

- the quant layer is too thin and fragmented;
- the strategy contract is still simple and not strongly extensible;
- the backtest engine is functional but not yet a full event-driven engine;
- the portfolio/risk layer needs a clearer separation from AI-generated ideas;
- data provenance, execution boundaries, and reproducibility need stronger standardization;
- the architecture lacks a mature quant metrics library and operational observability.

## Current architecture

The project currently contains a small but coherent set of modules.

### Package layout

- `src/arthashree/__init__.py`
- `src/arthashree/backtest.py`
- `src/arthashree/cli.py`
- `src/arthashree/features.py`
- `src/arthashree/risk.py`
- `src/arthashree/strategy.py`
- `src/arthashree/validation.py`
- `src/arthashree/data/`
- `src/arthashree/clock.py`
- `src/arthashree/data_handler.py`
- `src/arthashree/events.py`
- `src/arthashree/research.py`

### Existing capabilities

- OHLCV validation with strict checks for duplicate timestamps, missing values, invalid ranges, and non-positive prices
- Feature generation for EMA, ATR, RSI, MACD and weekly trend screen
- Strategy signal generation for a simple trend-pullback hypothesis
- Backtest execution with risk sizing and transaction-cost assumptions
- Validation split into train/validation/test windows
- NSE and Kite historical data downloaders with metadata capture
- Basic instrument master loader
- Simulation clock and look-ahead protection
- Hypothesis and run-card model for research work

### Current strengths

- Clear focus on risk and no-look-ahead controls
- Data validation is explicitly strict and does not silently repair market data
- The project treats synthetic data as non-evidence and separate from real research
- Backtest configuration is approachable and reproducible
- The project already anticipates a broker boundary and research-vs-execution separation

## Missing capabilities

### Quantitative research infrastructure

- no reusable statistics/analytics module;
- no rolling factor analytics library;
- no factor registry or alpha library;
- no standard quant primitives shared across strategies and research.

### Market-data architecture

- data sources are not yet modeled as a common abstraction layer;
- no market metadata, data manifest, or source provenance standard beyond downloader metadata;
- no explicit missing-data policies or data quality states;
- no data cache partitioning and versioning model.

### Strategy framework

- strategy contract exists but is still too light;
- no strategy registry; no strategy lifecycle; no benchmark/comparison layer;
- no explicit portfolio target objects beyond basic allocation concepts.

### Backtesting

- event-driven engine is only partially introduced;
- portfolio accounting is still ad hoc;
- trade stats are limited compared with institutional requirements;
- no performance attribution or turnover/stress validation layer.

### Portfolio construction

- no portfolio optimizer or target-allocation engine;
- no exposure, beta, concentration, or risk budgeting layer;
- no order routing or execution simulation across multiple names.

### Risk management

- risk model exists in a basic form but not yet as a full platform engine;
- no maximum drawdown, daily loss limit, volatility limit, concentration limit, or stop-trading logic;
- no independent risk gate separated from strategy logic.

### Options / derivatives analytics

- no Greeks, implied volatility, theoretical pricing, or option chain abstraction.

### AI research layer

- AI concepts exist as model classes, but not yet as a controlled operational system;
- no sandbox or execution boundary beyond the documented principle;
- no tested agent-to-risk-governance flow.

### Execution architecture

- broker boundary is documented but not yet formalized as a service abstraction;
- no paper-execution and live-execution separation by interface;
- no order management, fill logic, or execution algorithms.

### Testing and validation

- tests exist but are limited and mostly smoke-like;
- no quant numerical validation suite;
- no backtest regression benchmark suite;
- no stress/parameter-perturbation framework.

### Observability

- no structured logging system;
- no metrics collection for runs;
- no audit trail, run metadata, or artifact registry beyond a few output files.

### Configuration and reproducibility

- config is lightweight but not yet standardized;
- no versioned cost model, dataset manifest standard, or strong run provenance model;
- no dedicated environment lock or run hash registry.

## Technical debt

- The codebase is still small enough to refactor safely, but some foundational modules are not yet organized around a single architecture vocabulary.
- The risk, strategy, and backtest layers still need a cleaner separation of responsibilities.
- There are overlapping concepts (signal, target, risk limit, execution) that should be formalized with a single domain model.
- The system is still close to a single-strategy prototype and needs productization in the next phase.

## Risks

- Research ideas may be accepted too quickly because the project does not yet have a broad validation stack.
- Strategy logic may overfit to synthetic or narrow test data.
- Execution assumptions are insufficiently formalized for real-market deployment.
- Data-source abstraction is still too immature for reliable multi-source research.
- AI-generated ideas may bypass deterministic checks without a stronger governance boundary.

## Recommended improvements

1. Build a reusable quant analytics module.
2. Formalize the data-source abstraction and provenance model.
3. Separate signal generation, target generation, risk approval, and execution.
4. Add event-driven backtesting and more realistic fill simulation.
5. Build a risk engine that is independent from strategy code.
6. Add a stronger configuration and run-card model.
7. Add an options analytics foundation before live expansion.
8. Standardize tests around numeric validation and known-answer fixtures.
9. Add observability at the run and strategy level.
10. Keep the AI research layer advisory and non-autonomous.

## Dependency issues

The project currently depends on a minimal stack: `pandas`, `numpy`, `PyYAML`, and pytest. This is appropriate for the current stage. The risk is not dependency bloat; it is architectural incompleteness. Phase 2 should avoid unnecessary external libraries unless a concrete need emerges.

## Testing gaps

- no module-level numeric test coverage for quant primitives;
- no explicit regression tests for risk limits and edge conditions;
- no integration tests for data sources and event engine;
- no benchmark-based validation for strategy changes.

## Performance bottlenecks

- repeated calculations on dataframe pipelines can become expensive;
- feature generation is not yet standardized across a registry;
- backtests still rely on ad hoc loops and are not yet engineered for scale;
- performance work should focus on vectorized operations and data reuse, not premature optimization.

## Security concerns

- broker credentials and live-execution boundaries must remain tightly controlled;
- generated strategy code must not have direct access to production credentials;
- the research agent should never bypass the risk gate or execution service.

## Phase 2 recommendation

The correct path is not a full rewrite. It is to strengthen the engine in layers:

1. quant primitives and shared analytics;
2. data abstraction and provenance;
3. strategy contract and target engine;
4. risk engine independence;
5. event-driven backtest and portfolio layer;
6. monitoring and reproducibility;
7. options analytics and controlled execution architecture.

This is the safest route to a production-grade research platform.
