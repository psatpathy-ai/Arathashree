# PHASE 2 Reference Analysis

## Executive summary

The strongest ideas for Arthashree come from combining two different models:

- GS Quant contributes the deterministic technical foundation for market data, portfolio/risk abstractions, and professional quant-engine architecture.
- Vibe-Trading contributes the research workflow, agent loop, validation culture, and operational boundaries required for an AI-assisted platform.

The right strategy is not to reproduce either project. It is to adopt the parts that improve Arthashree’s ability to become a disciplined, risk-aware, research-first platform.

## Capability comparison table

| Capability | GS Quant | Vibe-Trading | Arthashree Current | Arthashree Recommendation |
|---|---|---|---|---|
| Market data | Strong data abstraction, instrument and market modeling | Multi-source research and data loaders | Basic validated OHLCV + downloaders | ADAPT: add source abstraction and provenance |
| Quant analytics | Strong finance/statistics layering | Alpha/factor libraries, validation loops | Minimal core metrics | ADOPT: build shared quant-primitives module |
| Pricing | Strong finance and derivative modeling | Limited compared with institutional pricing stacks | Not yet present | BUILD OURSELVES: start with options basics only |
| Portfolio analytics | Portfolio/instrument/risk concepts | Portfolio and attribution concepts | Weak | ADOPT: add portfolio state and exposure model |
| Risk | Professional risk and product abstractions | Risk boundaries and paper/live separation | Basic size calc and config | ADOPT: formal risk engine + risk gate |
| Strategy framework | Systematic strategy concepts | Agent-hypothesis-to-strategy loop | Basic signal function | ADAPT: target-based strategy contract |
| Backtesting | Deterministic, event-driven engine patterns | Research autopilot + validation | Single-loop backtest | ADOPT: event engine + validation stack |
| AI agents | Not primarily an agent framework | Strong agent/research architecture | Basic doc-level concept | ADAPT: constrained research agents |
| Research workflow | More product/quant platform than workflow | Research autopilot + report cards | Basic validation function | ADOPT: hypothesis → backtest → validation → report |
| Execution | Professional interfaces expected | Broker boundary and safety controls | Not yet formalized | ADAPT: paper/live broker abstraction |
| Configuration | Typed and layered config patterns | Run cards and experiment configs | JSON config, basic defaults | ADOPT: versioned configs and manifests |
| Testing | Strong quant-engine discipline | Validation and Monte Carlo tests | Basic smoke tests | ADOPT: regression + numerical tests |
| Observability | Less visible in public docs | Run cards, logs, artifacts | Minimal | ADOPT: structured run metadata and artifact store |
| Extensibility | Domain decomposition | Modular tool/skill/plugin pattern | Small but modular in growth stage | ADAPT: modular packages and registries |

## GS Quant analysis

### What is valuable

- clean domain layering across data, markets, instruments, analytics, strategies, and risk;
- idea that the strategy layer should not talk directly to market data or broker systems;
- concept of deterministic simulation and time-aware data handling;
- strong separation between client-facing API and research/backtest engine;
- cost models and transaction assumptions are explicit and operationally relevant;
- portfolio and risk abstractions are built around real finance concepts.

### Which parts fit Arthashree

- strict data abstraction;
- clock and look-ahead prevention;
- event-driven backtests;
- strategy contract and target generation;
- cost and slippage modelling;
- market/instrument domain separation.

### Which parts to ignore or not copy

- proprietary platform integration and Goldman Sachs internal APIs;
- any derivative-specific infrastructure whose economics do not yet matter to Arthashree;
- large institutional tooling that would overcomplicate a small research codebase.

### Recommendation

ADOPT the architecture patterns. DO NOT copy the implementation.

## Vibe-Trading analysis

### What is valuable

- research-agent loop; hypothesis-driven development;
- run-card artifact generation and provenance;
- explicit validation workflows; Monte Carlo/bootstrap/walk-forward patterns;
- isolation of research from live execution;
- paper/live safety boundaries;
- factor-alpha library discipline with attribution and capacity awareness.

### Which parts fit Arthashree

- research autopilot design;
- hypothesis objects and experiment metadata;
- artifact-based reproducibility;
- validation modules for sensitivity and attribution;
- security boundary between AI and broker execution.

### Which parts to ignore or not copy

- excessive factor zoo without regime and multiple-testing discipline;
- large, generated alpha library without controlled validation;
- any pattern that grants unrestricted execution power to AI agents.

### Recommendation

ADAPT the operating model, but keep AI research advisory and bounded.

## Arthashree current state

Arthashree already has several good foundations:

- strict data validation no silent repairs;
- signal and risk construct; 
- configuration-driven run definitions;
- basic validation split and backtest metrics;
- initial data downloader abstractions;
- time-aware clock and look-ahead tests.

This means the project is not starting from zero. It is ready for the next layer: a reusable quant engine, tighter execution/risk separation, and a stronger platform architecture.

## Decision framework

For each concept we ask:

> Does this improve Arthashree?

- If yes, implement it in a minimal, domain-aligned way.
- If partially useful, adapt it to match Arthashree’s simpler architecture.
- If not useful, ignore it.

## Recommended Phase 2 stance

### ADOPT

- explicit simulation clock;
- event-driven backtest flows;
- strategy target contract;
- risk and cost configuration;
- run cards and run manifests;
- validation modules and walk-forward discipline;
- broker separation and live/paper gating.

### ADAPT

- factor and alpha library management;
- portfolio exposure and attribution framework;
- multi-engine market architecture;
- AI research workflow models.

### BUILD OURSELVES

- options analytics foundation;
- internal quant metrics library;
- execution service abstraction;
- risk engine and gateway logic;
- observability and audit trail tooling.

### IGNORE

- wholesale copying of any repo;
- proprietary internal APIs;
- the assumption that higher model complexity equals better performance;
- unrestricted autonomous trading by AI.

## Final recommendation

The proper architectural synthesis is:

- GS Quant for deterministic quant-engine structure;
- Vibe-Trading for research workflow and AI safety boundaries;
- Arthashree for the domain-specific NSE / Zerodha direction and conservative risk stance.

This combination is the right basis for a disciplined research platform.
