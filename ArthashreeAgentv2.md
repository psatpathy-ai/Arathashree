# Arthashree Re-Architecture: strongest ideas only

This document replaces the earlier, broader notes with a cleaner architecture built around the strongest ideas from the GS Quant and Vibe-Trading references.

The design goal is not to clone either repository. It is to create a durable Arthashree architecture that is:

- research-first;
- deterministic in backtests;
- risk-governed before any execution;
- auditable and reproducible;
- safe with a live broker boundary.

---

## 1. Strongest ideas to keep

### From GS Quant

These are the hardest technical foundations:

- strict data abstraction through DataSource / DataManager patterns;
- explicit simulation clock and look-ahead rejection;
- deterministic backtest engine with event-driven execution flow;
- strategy interface separated from execution/portfolio logic;
- transaction-cost models and risk configuration as first-class concepts;
- clear domain layering: data, instruments, features, strategies, portfolio, risk, execution.

### From Vibe-Trading

These are the strongest research and operations ideas:

- AI research autopilot loop;
- hypothesis-driven experimentation;
- artifact-based run cards and provenance;
- validation modules (walk-forward, Monte Carlo, attribution, sensitivity);
- explicit security boundaries between research and execution;
- paper-trading and live-trading gates behind deterministic checks.

### From the trading discipline material

The non-negotiable operational rule is:

- treat trading as probabilistic, never as certainty;
- define risk before entry;
- model costs and slippage explicitly;
- reject future leakage;
- keep live trading behind a risk gate and execution service boundary.

---

## 2. Design principle

Arthashree should be built as a two-layer system:

- Quant core: deterministic, data-driven, reproducible, cost-aware.
- AI research layer: hypothesis generation, factor testing, strategy discovery, validation, reporting.

The AI proposes. The engine validates. The risk engine approves. The execution service acts.

This is the central architecture decision.

---

## 3. Target architecture

```text
                              ARTHASHREE
                                   |
                    +--------------+---------------+
                    |                              |
              QUANT CORE                    AI RESEARCH
                    |                              |
    +---------------+----------------+      +-------------------+
    |                                |      |                   |
    Data Layer                     Risk Layer   Research Agent     
    - MarketDataSource             - RiskModel   - Hypothesis       
    - DataHandler                 - CostModel   - Feature tests    
    - Clock/Time                 - PositionSizer - Strategy ideas  
    - Provenance                 - PreTradeGate    - Validation      
    - Cache/Parquet                         |     - Attribution     
    |                                |      - Run cards       
    v                                v      v                   |
    Feature/Alpha Layer          Execution Layer                        
    - Features                   - PaperBroker                                
    - Alpha Library              - LiveBroker (sealed)                        
    - Signal generation          - Broker adapter                              
    - Instrument mapping         - Execution service                            
    |                                |                                      |
    v                                v                                      |
    Strategy Layer                 Portfolio Layer                            
    - Strategy interface          - Position state                             
    - Target allocation           - PnL ledger                                  
    - Short/long logic            - Inventory                                  
    - Explainability             - Exposure limits                             
    |                                |                                      |
    +----------------+---------------+                                      |
                     |                                                      |
                     v                                                      |
            Backtest Engine                                                  |
            - event loop                                                   |
            - simulation clock                                              |
            - order/fill/portfolio pipeline                                 |
            - cost model                                                    |
            - validation and reporting                                       |
                     |
                     v
               Paper trading
                     |
                     v
              Risk gate
                     |
                     v
             Live execution (only if all gates pass)
```

---

## 4. Core package structure

```text
src/arthashree/
├── data/
│   ├── sources/
│   ├── manifests/
│   ├── cache/
│   ├── validation/
│   └── provenance.py
├── instruments/
│   ├── registry.py
│   ├── index.py
│   └── contract.py
├── features/
│   ├── base.py
│   ├── technical.py
│   ├── market.py
│   └── alpha_library/
├── strategies/
│   ├── base.py
│   ├── signal_strategy.py
│   ├── target_strategy.py
│   └── registry.py
├── portfolio/
│   ├── state.py
│   ├── allocation.py
│   ├── ledger.py
│   └── exposure.py
├── risk/
│   ├── models.py
│   ├── cost_model.py
│   ├── position_sizing.py
│   ├── pre_trade_gate.py
│   └── limits.py
├── execution/
│   ├── base.py
│   ├── paper.py
│   ├── broker_adapter.py
│   ├── order.py
│   ├── fill.py
│   └── service.py
├── backtest/
│   ├── event.py
│   ├── clock.py
│   ├── data_handler.py
│   ├── engine.py
│   ├── actions.py
│   └── report.py
├── validation/
│   ├── leakage.py
│   ├── walk_forward.py
│   ├── monte_carlo.py
│   ├── bootstrap.py
│   ├── attribution.py
│   └── sensitivity.py
├── research/
│   ├── hypothesis.py
│   ├── autopilot.py
│   ├── run_card.py
│   ├── registry.py
│   └── report.py
├── agents/
│   ├── research_agent.py
│   ├── strategy_agent.py
│   ├── validation_agent.py
│   ├── risk_agent.py
│   ├── execution_agent.py
│   └── critic_agent.py
├── security/
│   ├── sandbox.py
│   ├── env.py
│   ├── broker_boundaries.py
│   └── audit.py
├── reporting/
│   ├── metrics.py
│   ├── summary.py
│   └── artifact_store.py
├── config/
│   ├── default.yaml
│   ├── costs/
│   └── strategies/
└── cli.py
```

---

## 5. The strongest technical contracts

### 5.1 Data contract

Every source should conform to a common interface:

```python
class MarketDataSource:
    def get_bar(self, symbol, timestamp, interval):
        ...

    def get_bars(self, symbol, start, end, interval):
        ...

    def get_snapshot(self, symbol, timestamp):
        ...
```

Implementations:

- NSEDataSource
- KiteHistoricalSource
- KiteLiveSource
- ParquetDataSource
- DuckDBDataSource
- CachedDataSource

The strategy never decides where data came from. It only consumes a standard contract.

### 5.2 Clock and look-ahead protection

The simulation clock is mandatory.

```python
class SimulationClock:
    current: datetime

    def advance_to(self, timestamp):
        ...
```

The data handler must reject any request beyond the current simulation time:

```python
if requested_timestamp > clock.current:
    raise LookAheadError()
```

This is a hard line. No silent data-shift tricks. No convenience padding.

### 5.3 Event-driven backtest engine

Backtests should be based on events instead of a giant dataframe loop.

```text
MarketEvent -> Strategy -> SignalEvent -> RiskEngine -> OrderEvent -> ExecutionSimulator -> FillEvent -> Portfolio
```

The event engine makes it viable for:

- daily strategies;
- intraday strategies;
- multi-strategy research;
- paper trading;
- live execution paths using the same contracts.

### 5.4 Strategy contract

Every strategy should declare a target or decision, not directly place broker orders.

```python
class Strategy:
    name: str
    version: str

    def prepare(self, context):
        ...

    def generate_signal(self, context):
        ...

    def generate_target(self, context):
        ...

    def explain(self, context):
        ...
```

Outputs should be explicit, for example:

```text
NO_POSITION
LONG 25%
SHORT 10%
```

This keeps AI research and deterministic execution separate.

### 5.5 Risk and costs

Transaction costs and risk assumptions are part of the architecture, not optional add-ons:

- brokerage;
- STT;
- exchange charges;
- taxes;
- slippage;
- impact cost;
- borrow cost;
- capacity constraints.

The engine must include them in every backtest and paper simulation.

---

## 6. Research loop

The AI research layer should follow a clean autopilot loop:

```text
Hypothesis
    -> Research plan
    -> Feature selection
    -> Strategy prototype
    -> Backtest
    -> Validation
    -> Attribution
    -> Report
    -> Accept / Reject / Modify
```

This is the Vibe-Trading contribution and is worth keeping.

Every run should generate a run card containing:

```text
runs/
└── RUN-2026-000123/
    ├── config.json
    ├── hypothesis.json
    ├── dataset_manifest.json
    ├── strategy.py
    ├── metrics.json
    ├── trades.csv
    ├── equity.csv
    ├── validation.json
    ├── attribution.json
    ├── logs/
    └── report.md
```

No result is valid without a reproducible record of the run.

---

## 7. Validation stack

The validation layer should be first-class rather than ad hoc. At minimum:

- leakage checks;
- walk-forward analysis;
- Monte Carlo / bootstrap tests;
- regime sensitivity checks;
- parameter perturbation checks;
- cost and slippage stress tests;
- capacity and fill-rate checks;
- attribution analysis.

A result is not accepted because one metric looks good. It must hold up under stress and out-of-sample testing.

---

## 8. Security and execution boundaries

The AI research layer must never hold broker credentials. The live execution service does.

```text
Research Agent -> Strategy Proposal -> Risk Gate -> Execution Service -> Kite / Broker
```

Important rules:

- no direct broker access from agents;
- no live order in development or backtest modes;
- no secret material in code, logs, prompts, screenshots, or Git history;
- generated strategy code runs inside a restricted sandbox;
- paper trading is the default path.

---

## 9. Hard non-negotiables

These are the design rules the project should never violate.

1. No strategy is considered profitable without out-of-sample evidence.
2. No future information is allowed in features or simulation logic.
3. All backtests include realistic costs and slippage assumptions.
4. Missing market data must be explicit and must never be silently repaired.
5. Risk must be defined before entering a trade.
6. No martingale sizing or averaging-down by default.
7. Execution mode defaults to PAPER or DISABLED.
8. Live execution requires a deployment gate and a broker boundary.
9. Reproducibility is required for any research result.
10. The research agent can propose; the deterministic engine decides.

---

## 10. Re-architecture summary

The strongest architecture is therefore:

- GS Quant for the hard technical foundations: market abstraction, clock protection, event-driven backtesting, strategy interfaces, risk/cost modelling.
- Vibe-Trading for the research operating model: agent loop, run artifacts, validation discipline, research autopilot, security boundaries.
- Trading discipline for the governance model: risk-first behaviour, no look-ahead, no magical fixes, no live execution without gates.

The result is a system where AI helps discover edges, but deterministic engines and risk gates decide whether those ideas survive long enough to become real trading logic.

This is the architecture Arthashree should build around.
