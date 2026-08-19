from arthashree.risk_engine import DefaultRiskEngine
from arthashree.events import OrderEvent


def test_exposure_and_concentration_rejection():
    engine = DefaultRiskEngine(max_total_exposure_pct=0.2, max_concentration_pct=0.1)
    # Portfolio with existing exposure 15000
    portfolio = {"equity": 100000.0, "daily_loss": 0.0, "open_positions": [{"symbol":"A", "notional": 15000.0}]}
    # Order would add 20000 notional -> total 35000 > 20000 (0.2*100000)
    order = OrderEvent(timestamp=None, symbol="B", direction="long", quantity=200, price=100.0, payload={"stop_price": 95.0})
    decision = engine.approve(order, portfolio)
    assert decision.approved is False


def test_margin_requirement_rejection():
    engine = DefaultRiskEngine(margin_requirement=0.5)
    portfolio = {"equity": 10000.0, "daily_loss": 0.0, "open_positions": []}
    # Order with notional 50000 requires margin 25000, which exceeds equity
    order = OrderEvent(timestamp=None, symbol="C", direction="long", quantity=500, price=100.0, payload={"stop_price": 99.0})
    decision = engine.approve(order, portfolio)
    assert decision.approved is False
