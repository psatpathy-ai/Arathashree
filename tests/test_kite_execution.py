from types import SimpleNamespace
from arthashree.integrations.kite_execution import KiteExecutionAdapter
from arthashree.execution import ExecutionResult


class MockClient:
    def place_order(self, symbol, qty, price, side):
        return {"status": "success", "filled_qty": qty, "avg_fill_price": price}


def test_kite_dry_run():
    adapter = KiteExecutionAdapter(client=None, run_live=False, commission_bps=2.0)
    order = SimpleNamespace(symbol='TEST', quantity=10, price=100.0, direction='buy')
    res = adapter.send_order(order, {})
    assert isinstance(res, ExecutionResult)
    assert res.filled
    assert res.filled_qty == 10


def test_kite_live_mode():
    adapter = KiteExecutionAdapter(client=MockClient(), run_live=True, commission_bps=2.0)
    order = SimpleNamespace(symbol='TEST', quantity=5, price=200.0, direction='buy')
    res = adapter.send_order(order, {})
    assert res.filled
    assert res.filled_qty == 5
    assert res.filled_price == 200.0
