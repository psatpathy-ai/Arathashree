__version__ = "0.1.0"

from .clock import LookAheadError, SimulationClock
from .data_handler import DataHandler
from .events import (
    Event,
    FillEvent,
    MarketEvent,
    OrderEvent,
    PortfolioEvent,
    RiskEvent,
    SignalEvent,
    TimerEvent,
)
from .quant import (
    alpha,
    beta,
    correlation,
    covariance,
    log_returns,
    max_drawdown,
    rolling_mean,
    rolling_std,
    rolling_volatility,
    sharpe_ratio,
    simple_returns,
    sortino_ratio,
    volatility,
    zscore,
)
from .research import HypothesisStatus, ResearchHypothesis, RunCard
from .risk import CostModel, RiskModel, position_size
from .strategy import Strategy, TargetAllocation, generate_signals
from .strategy_registry import StrategyRegistry, RunCard
from .risk_engine import RiskEngine, DefaultRiskEngine, RiskDecision
