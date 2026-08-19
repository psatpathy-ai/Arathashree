# PHASE 2 Architecture

## Purpose

This architecture describes the next evolutionary step for Arthashree: a modular research and trading platform that remains deterministic, measure-based, and safe.

The key design choice is to separate the platform into two domains:

1. Quant core: deterministic, data-driven, risk-governed, backtest-friendly
2. AI research layer: hypothesis generation, strategy discovery, validation, attribution, and reporting

The AI proposes. The engine validates. The risk engine approves. The execution service acts.

## Platform structure

```text
ARTHASHREE
│
├── Data Platform
│   ├── Market Data
│   │   ├── OHLCV data
│   │   ├── market snapshots
│   │   ├── instrument metadata
│   │   └── alternative data
│   ├── Historical Data
│   │   ├── raw snapshots
│   │   ├── normalized tables
│   │   └── manifest metadata
│   ├── Fundamental Data
│   │   ├── corporate actions
│   │   ├── balance sheet / fundamentals
│   │   └── factor metadata
│   ├── Options Data
│   │   ├── option chains
│   │   ├── Greeks
│   │   └── implied volatility
│   └── Alternative Data
│       └── external research feeds
│
├── Quant Engine
│   ├── Statistics
│   │   ├── returns
│   │   ├── volatility
│   │   ├── Sharpe
│   │   ├── Sortino
│   │   └── drawdown
│   ├── Factors
│   │   ├── trend
│   │   ├── momentum
│   │   ├── volatility
│   │   └── cross-sectional factors
│   ├── Technical Analytics
│   │   ├── EMA / SMA / MACD / RSI
│   │   ├── rolling stats
│   │   └── regime detection
│   ├── Options Analytics
│   │   ├── option pricing
│   │   ├── Greeks
│   │   └── implied vol models
│   └── Portfolio Analytics
│       ├── weights
│       ├── exposure
│       ├── attribution
│       └── turnover
│
├── Strategy Engine
│   ├── Strategy Interface
│   ├── Signal Engine
│   ├── Alpha Models
│   ├── Factor Registry
│   └── Strategy Registry
│
├── Backtesting
│   ├── Event Engine
│   ├── Execution Simulation
│   ├── Slippage
│   ├── Transaction Costs
│   ├── Position Accounting
│   └── Performance Attribution
│
├── Portfolio
│   ├── Position Management
│   ├── Portfolio Construction
│   ├── Optimization
│   ├── Rebalancing
│   └── Exposure & Concentration Limits
│
├── Risk Engine
│   ├── Position Risk
│   ├── Portfolio Risk
│   ├── VaR
│   ├── Stress Testing
│   ├── Drawdown
│   ├── Daily Loss Limits
│   └── Risk Alerting
│
├── AI Layer
│   ├── Research Agent
│   ├── Strategy Agent
│   ├── Signal Agent
│   ├── Risk Agent
│   ├── Portfolio Agent
│   └── Critic Agent
│
├── Execution
│   ├── Broker Interface
│   ├── Paper Broker
│   ├── Order Management
│   ├── Fill Logic
│   ├── Execution Algorithms
│   └── Transaction Cost Model
│
├── Monitoring
│   ├── Metrics
│   ├── Logs
│   ├── Alerts
│   └── Audit Trail
│
├── Testing
│   ├── Unit Tests
│   ├── Integration Tests
│   ├── Quant Validation
│   ├── Backtest Regression
│   └── Performance Tests
│
└── Reproducibility
    ├── Run cards
    ├── Config hash
    ├── Data manifest
    ├── Strategy versioning
    └── Dependency locks
```

## Core domain contracts

### 1. Data source abstraction

```python
class MarketDataSource:
    def get_bar(self, symbol, timestamp, interval):
        ...

    def get_bars(self, symbol, start, end, interval):
        ...

    def get_snapshot(self, symbol, timestamp):
        ...
```

This is required to keep trading logic independent from medium/provider details.

### 2. Simulation clock

```python
class SimulationClock:
    current: datetime

    def assert_not_lookahead(self, requested_time):
        ...
```

This is a determinism boundary and should remain central to the platform.

### 3. Strategy target contract

```python
class Strategy:
    def generate_target(self, context):
        ...
```

The strategy produces a target or signal, not direct broker orders.

### 4. Risk approval contract

```python
class RiskEngine:
    def approve(self, order, portfolio, market):
        ...
```

Risk is an independent authority. AI cannot bypass it.

### 5. Backtest event contract

```text
MarketEvent -> Strategy -> Signal -> Risk -> Order -> Fill -> Portfolio
```

This is the foundation for future event-driven execution.

## Architecture principles

1. Determinism before flexibility.
2. Data quality before strategy quality.
3. Risk before execution.
4. Research before deployment.
5. Reproducibility before publication.
6. Auditability before automation.
7. Simple modules before clever abstractions.

## Phase 2 implementation order

The project should not implement every component at once. It should add layers in stable increments.

The first priority is a shared quant engine, then data abstraction, then strategy and risk contracts.

## Operational boundaries

### Research-only systems

- hypothesis generation;
- feature exploration;
- signal experimentation;
- report generation.

### Risk-governed systems

- position sizing;
- daily loss and exposure checks;
- stop-trading triggers;
- live execution approval.

### Execution systems

- broker adapters;
- order placement and cancellation;
- fill processing;
- reconciliation.

AI research can generate proposals, but only the deterministic engine can approve or reject them.

## Implementation stance

Arthashree should evolve incrementally with small, testable modules rather than a large rewrite. The architecture should be strong enough for future growth without requiring a complete replacement later.
