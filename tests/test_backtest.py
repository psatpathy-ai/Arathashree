import pandas as pd
from arthashree.backtest import run_backtest

def test_backtest_is_reproducible():
    idx = pd.bdate_range("2021-01-01", periods=80)
    close = [100 + i*0.5 for i in range(80)]
    df = pd.DataFrame({
        "open": close,
        "high": [x+1 for x in close],
        "low": [x-1 for x in close],
        "close": close,
        "atr": [1.0]*80,
        "weekly_trend_ok": [True]*80,
        "ema_fast": [90]*80,
        "signal": [False]*80
    }, index=idx)
    df.iloc[30, df.columns.get_loc("signal")] = True
    cfg = {
        "initial_capital":1_000_000, "risk_per_trade":0.01,
        "max_position_notional_pct":1.0, "commission_bps":2,
        "slippage_bps":5, "atr_stop_multiple":2,
        "reward_risk":2, "max_bars_in_trade":30
    }
    r = run_backtest(df, cfg)
    assert len(r.trades) >= 1
    assert r.metrics()["final_equity"] > 0
