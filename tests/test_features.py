import pandas as pd
import numpy as np
from arthashree.features import add_features

def make_df(n=400):
    idx = pd.bdate_range("2020-01-01", periods=n)
    close = 100 * np.exp(np.cumsum(np.random.default_rng(1).normal(0.0003, 0.01, n)))
    return pd.DataFrame({
        "open": close * 0.999,
        "high": close * 1.01,
        "low": close * 0.99,
        "close": close,
        "volume": 100000
    }, index=idx)

def test_features_no_future_columns():
    df = make_df()
    out = add_features(df, {
        "ema_fast":50,"ema_weekly":26,"atr_period":14,
        "rsi_period":14,"macd_fast":12,"macd_slow":26,"macd_signal":9
    })
    assert len(out) == len(df)
    assert "signal" in out
    assert out.index.equals(df.index)
