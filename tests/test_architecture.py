from datetime import datetime

import pandas as pd
import pytest

from arthashree.clock import LookAheadError, SimulationClock
from arthashree.data_handler import DataHandler
from arthashree.events import MarketEvent, OrderEvent, SignalEvent
from arthashree.research import HypothesisStatus, ResearchHypothesis
from arthashree.risk import CostModel, RiskModel
from arthashree.strategy import Strategy, TargetAllocation


def test_simulation_clock_rejects_lookahead():
    clock = SimulationClock("2024-01-01T00:00:00")
    with pytest.raises(LookAheadError):
        clock.assert_not_lookahead("2024-01-01T00:00:01")


def test_data_handler_respects_clock():
    idx = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])
    df = pd.DataFrame({"close": [100.0, 101.0, 102.0]}, index=idx)
    clock = SimulationClock("2024-01-02")
    handler = DataHandler(df, clock=clock)

    assert handler.get_data("2024-01-02")["close"] == 101.0
    with pytest.raises(LookAheadError):
        handler.get_data("2024-01-03")


def test_strategy_target_contract_and_research_hypothesis():
    strat = Strategy(name="demo", version="1.0")
    target = strat.generate_target({"weight": 0.25})
    assert isinstance(target, TargetAllocation)
    assert target.direction == "long"
    assert target.weight == 0.25

    hypothesis = ResearchHypothesis(
        hypothesis_id="HYP-0001",
        title="Momentum breakout",
        universe="NIFTY50_PIT",
        frequency="1D",
        features=["close", "rsi_14"],
        entry_logic="rsi crosses above 50",
        exit_logic="ATR stop",
        risk_model="risk_per_trade = 1%",
        cost_model="nse_equity_v1",
        status=HypothesisStatus.PROPOSED,
    )
    assert hypothesis.status == HypothesisStatus.PROPOSED


def test_risk_and_event_models():
    risk = RiskModel(risk_per_trade=0.01)
    assert risk.position_size(100000, 100, 95) > 0

    cost = CostModel(commission_bps=5, slippage_bps=10)
    assert cost.estimate_trade_cost(100000) > 0

    event = SignalEvent(timestamp=datetime(2024, 1, 1), signal=True)
    order = OrderEvent(timestamp=datetime(2024, 1, 1), symbol="INFY", direction="buy", quantity=10, price=100.0)
    assert event.kind == "signal"
    assert order.direction == "buy"
