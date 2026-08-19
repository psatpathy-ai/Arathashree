from pathlib import Path

from arthashree.event_engine import EventBacktester
from arthashree.strategy_registry import StrategyRegistry, RunCard
from arthashree.strategy import Strategy, TargetAllocation
from arthashree.data import load_ohlcv
from arthashree.features import add_features


class SimpleLongStrategy(Strategy):
    name = "simple_long"

    def generate_target(self, context):
        # Always go long with 1% weight when ATR present
        return TargetAllocation(direction="long", weight=0.01)


def test_event_backtester_runs(tmp_path: Path):
    df = load_ohlcv(Path("data/sample_ohlcv.csv"))
    cfg = {
        "initial_capital": 100000,
        "risk_per_trade": 0.01,
        "max_position_notional_pct": 1.0,
        "commission_bps": 2.0,
        "slippage_bps": 5.0,
        "atr_period": 14,
        "atr_stop_multiple": 2.0,
        "reward_risk": 2.0,
        "ema_fast": 50,
        "ema_weekly": 26,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "rsi_period": 14,
        "max_bars_in_trade": 30,
    }
    df = add_features(df, cfg)

    reg = StrategyRegistry()
    reg.register("simple_long", SimpleLongStrategy)
    run_card = RunCard(strategy="simple_long", symbol="SAMPLE", params={})

    engine = EventBacktester(df=df, cfg=cfg, strategy_registry=reg, run_card=run_card)
    result = engine.run()

    # ensure engine produced a BacktestResult with equity and trades frame
    assert hasattr(result, "equity")
    assert hasattr(result, "trades")
    # trades may be zero if risk limits disallow; at least equity exists
    assert not result.equity.empty
