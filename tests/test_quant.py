import numpy as np
import pandas as pd

from arthashree.quant import (
    alpha,
    beta,
    correlation,
    covariance,
    log_returns,
    max_drawdown,
    rolling_volatility,
    sharpe_ratio,
    simple_returns,
    sortino_ratio,
    volatility,
    zscore,
)


def test_simple_returns_and_log_returns():
    prices = [100.0, 110.0, 121.0]
    ret = simple_returns(prices)
    assert list(ret.round(6)) == [0.0, 0.1, 0.1]
    assert np.isclose(log_returns(prices).iloc[1], np.log(1.1))


def test_volatility_and_sharpe_ratio():
    returns = pd.Series([0.01, 0.02, -0.01, 0.03, 0.00, 0.02])
    assert volatility(returns) > 0
    assert sharpe_ratio(returns) >= 0


def test_sortino_and_max_drawdown():
    equity = pd.Series([100.0, 110.0, 95.0, 105.0])
    assert sortino_ratio(equity) >= 0
    assert np.isclose(max_drawdown(equity), 0.13636363636363635)


def test_beta_alpha_correlation_covariance():
    p = pd.Series([0.01, 0.02, -0.01, 0.03])
    b = pd.Series([0.005, 0.015, -0.02, 0.025])
    assert abs(beta(p, b)) > 0
    assert abs(correlation(p, b)) > 0
    assert covariance(p, b) > 0
    assert abs(alpha(p, b)) >= 0


def test_rolling_volatility_and_zscore():
    values = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0, 15.0])
    rv = rolling_volatility(values, window=3)
    assert len(rv) == len(values)
    assert np.isfinite(rv.iloc[-1])
    zs = zscore(values)
    assert len(zs) == len(values)
    assert np.isfinite(zs.iloc[0])
