from pathlib import Path

from arthashree.backtest import run_backtest
from arthashree.risk_engine import DefaultRiskEngine
from arthashree.data import load_ohlcv


def test_backtest_respects_risk_limit(tmp_path: Path):
    from arthashree.features import add_features
    df = load_ohlcv(Path('data/sample_ohlcv.csv'))
    cfg = {
        "initial_capital": 100000,
        "risk_per_trade": 0.01,
        "max_position_notional_pct": 1.0,
        "commission_bps": 2.0,
        "slippage_bps": 5.0,
        "atr_stop_multiple": 2.0,
        "reward_risk": 2.0,
        "ema_fast": 50,
        "ema_weekly": 26,
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9,
        "rsi_period": 14,
        "atr_period": 14,
        "max_bars_in_trade": 30,
    }
    df = add_features(df, cfg)
    # Very tight daily loss limit to force rejection of trades
    engine = DefaultRiskEngine(daily_loss_limit=0.0001)
    result = run_backtest(df, cfg, risk_engine=engine)
    # with extremely low daily loss limit, backtest should produce zero trades
    assert result.trades.empty or len(result.trades) == 0
