from pathlib import Path

from arthashree.event_engine import EventBacktester
from arthashree.strategy_registry import StrategyRegistry, RunCard
from arthashree.strategy import Strategy, TargetAllocation
from arthashree.data import load_ohlcv
from arthashree.features import add_features


class SimpleLongStrategy(Strategy):
    name = "simple_long_log"

    def generate_target(self, context):
        return TargetAllocation(direction="long", weight=0.001)


def test_run_card_written(tmp_path: Path):
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
    reg.register("simple_long_log", SimpleLongStrategy)
    run_card = RunCard(strategy="simple_long_log", symbol="SAMPLE", params={})

    engine = EventBacktester(df=df, cfg=cfg, strategy_registry=reg, run_card=run_card)
    # configure run_card_dir to tmp_path
    engine.run_card_dir = str(tmp_path)
    result = engine.run()

    # find run card file
    files = list(Path(tmp_path).glob('runcard-*.json'))
    assert len(files) == 1
    data = files[0].read_text()
    assert 'strategy' in data and 'metrics' in data
