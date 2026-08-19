from pathlib import Path

import pytest

from arthashree.strategy import Strategy, TargetAllocation
from arthashree.strategy_registry import StrategyRegistry, RunCard
from arthashree.risk_engine import DefaultRiskEngine
from arthashree.events import OrderEvent


class DummyStrategy(Strategy):
    name = "dummy"

    def generate_target(self, context):
        # Simple: return long with weight if price > 0
        return TargetAllocation(direction="long", weight=float(context.get("weight", 0.1)))


def test_strategy_registry_execute():
    reg = StrategyRegistry()
    reg.register("dummy", DummyStrategy)
    run_card = RunCard(strategy="dummy", symbol="SAMPLE", params={"weight": 0.2})
    allocation = reg.execute(run_card)
    assert allocation.direction == "long"
    assert abs(allocation.weight - 0.2) < 1e-6


def test_default_risk_engine_approve_and_reject():
    engine = DefaultRiskEngine()
    # portfolio with equity and no current daily loss
    portfolio = {"equity": 100000.0, "daily_loss": 0.0}

    # create an order with payload stop_price
    order = OrderEvent(timestamp=None, symbol="SAMPLE", direction="long", quantity=100, price=100.0, payload={"stop_price": 95.0})

    decision = engine.approve(order, portfolio)
    assert decision.approved is True

    # request too large quantity -> reject
    large_order = OrderEvent(timestamp=None, symbol="SAMPLE", direction="long", quantity=10000, price=100.0, payload={"stop_price": 95.0})
    decision2 = engine.approve(large_order, portfolio)
    assert decision2.approved is False

    # daily loss limit test
    engine2 = DefaultRiskEngine(daily_loss_limit=0.001)  # allow only 100
    decision3 = engine2.approve(order, portfolio)
    assert decision3.approved is False

    # missing stop price -> reject
    bad_order = OrderEvent(timestamp=None, symbol="SAMPLE", direction="long", quantity=10, price=100.0)
    decision4 = engine.approve(bad_order, portfolio)
    assert decision4.approved is False
