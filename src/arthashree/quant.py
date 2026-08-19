from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def _as_series(values: Iterable[float] | pd.Series | np.ndarray, *, name: str = "series") -> pd.Series:
    series = pd.Series(values)
    if series.empty:
        raise ValueError(f"{name} must not be empty")
    if not np.isfinite(series.to_numpy(dtype=float)).all():
        raise ValueError(f"{name} contains non-finite values")
    return series.rename(name)


def _as_return_series(values: Iterable[float] | pd.Series | np.ndarray, *, name: str = "returns") -> pd.Series:
    series = _as_series(values, name=name)
    if series.empty:
        return series

    if (series > 0).all() and len(series) > 1 and series.iloc[0] > 1:
        return series.pct_change().fillna(0.0)

    return series.fillna(0.0)


def simple_returns(values: Iterable[float] | pd.Series | np.ndarray) -> pd.Series:
    """Return period-over-period simple returns."""
    return _as_return_series(values, name="returns")


def log_returns(values: Iterable[float] | pd.Series | np.ndarray) -> pd.Series:
    """Return log returns for a price series."""
    series = _as_series(values, name="log_returns")
    if (series > 0).all() and len(series) > 1 and series.iloc[0] > 1:
        return np.log(series / series.shift(1)).fillna(0.0)
    return series.fillna(0.0)


def volatility(values: Iterable[float] | pd.Series | np.ndarray, *, annualization: int = 252) -> float:
    """Return annualized volatility from a return series."""
    ret = _as_return_series(values, name="volatility")
    if ret.empty or ret.std(ddof=1) == 0:
        return 0.0
    return float(ret.std(ddof=1) * np.sqrt(annualization))


def rolling_volatility(values: Iterable[float] | pd.Series | np.ndarray, window: int = 20, *, annualization: int = 252) -> pd.Series:
    """Compute rolling annualized volatility."""
    if window <= 0:
        raise ValueError("window must be positive")
    series = _as_series(values, name="rolling_volatility")
    ret = series.pct_change().fillna(0.0)
    return ret.rolling(window=window, min_periods=window).std() * np.sqrt(annualization)


def sharpe_ratio(values: Iterable[float] | pd.Series | np.ndarray, *, risk_free_rate: float = 0.0, annualization: int = 252) -> float:
    """Compute the Sharpe ratio from a return series."""
    ret = _as_return_series(values, name="returns")
    if ret.empty:
        return 0.0
    excess = ret - risk_free_rate / annualization
    denom = excess.std(ddof=1)
    if denom == 0:
        return 0.0
    return float(excess.mean() * np.sqrt(annualization) / denom)


def sortino_ratio(values: Iterable[float] | pd.Series | np.ndarray, *, risk_free_rate: float = 0.0, annualization: int = 252) -> float:
    """Compute the Sortino ratio using downside volatility only."""
    ret = _as_return_series(values, name="returns")
    if ret.empty:
        return 0.0
    downside = ret.where(ret < 0, 0.0)
    downside_vol = downside.std(ddof=1)
    if downside_vol == 0:
        return 0.0
    excess = ret - risk_free_rate / annualization
    return float(excess.mean() * np.sqrt(annualization) / downside_vol)


def max_drawdown(values: Iterable[float] | pd.Series | np.ndarray) -> float:
    """Return the maximum drawdown as a fractional loss."""
    series = _as_series(values, name="drawdown")
    if series.empty:
        return 0.0
    running_max = series.cummax()
    drawdown = 1.0 - (series / running_max)
    return float(drawdown.max())


def beta(portfolio_returns: Iterable[float] | pd.Series | np.ndarray, benchmark_returns: Iterable[float] | pd.Series | np.ndarray) -> float:
    """Return the beta of a portfolio versus a benchmark series."""
    p = _as_return_series(portfolio_returns, name="portfolio_returns")
    b = _as_return_series(benchmark_returns, name="benchmark_returns")
    if len(p) != len(b):
        raise ValueError("Portfolio and benchmark return series must have the same length")
    cov = np.cov(p.to_numpy(dtype=float), b.to_numpy(dtype=float), ddof=1)[0, 1]
    var = np.var(b.to_numpy(dtype=float), ddof=1)
    if var == 0:
        return 0.0
    return float(cov / var)


def alpha(portfolio_returns: Iterable[float] | pd.Series | np.ndarray, benchmark_returns: Iterable[float] | pd.Series | np.ndarray, *, risk_free_rate: float = 0.0) -> float:
    """Return Jensen alpha using mean excess returns."""
    p = _as_return_series(portfolio_returns, name="portfolio_returns")
    b = _as_return_series(benchmark_returns, name="benchmark_returns")
    if len(p) != len(b):
        raise ValueError("Portfolio and benchmark return series must have the same length")
    b = b.fillna(0.0)
    p = p.fillna(0.0)
    beta_value = beta(p, b)
    portfolio_excess = p.mean() - risk_free_rate
    benchmark_excess = b.mean() - risk_free_rate
    return float(portfolio_excess - beta_value * benchmark_excess)


def zscore(values: Iterable[float] | pd.Series | np.ndarray) -> pd.Series:
    """Return the z-score of a numeric series."""
    series = _as_series(values, name="zscore")
    mean = series.mean()
    std = series.std(ddof=1)
    if std == 0:
        return pd.Series(0.0, index=series.index, dtype=float)
    return (series - mean) / std


def correlation(a: Iterable[float] | pd.Series | np.ndarray, b: Iterable[float] | pd.Series | np.ndarray) -> float:
    """Return the Pearson correlation coefficient between two numeric series."""
    left = _as_series(a, name="a")
    right = _as_series(b, name="b")
    if len(left) != len(right):
        raise ValueError("Input series must have equal length")
    if left.std(ddof=1) == 0 or right.std(ddof=1) == 0:
        return 0.0
    return float(left.corr(right))


def covariance(a: Iterable[float] | pd.Series | np.ndarray, b: Iterable[float] | pd.Series | np.ndarray) -> float:
    """Return the covariance between two series."""
    left = _as_series(a, name="a")
    right = _as_series(b, name="b")
    if len(left) != len(right):
        raise ValueError("Input series must have equal length")
    return float(np.cov(left.to_numpy(dtype=float), right.to_numpy(dtype=float), ddof=1)[0, 1])


def rolling_mean(values: Iterable[float] | pd.Series | np.ndarray, window: int = 20) -> pd.Series:
    """Return rolling mean values."""
    if window <= 0:
        raise ValueError("window must be positive")
    return _as_series(values, name="rolling_mean").rolling(window=window, min_periods=window).mean()


def rolling_std(values: Iterable[float] | pd.Series | np.ndarray, window: int = 20) -> pd.Series:
    """Return rolling standard deviation values."""
    if window <= 0:
        raise ValueError("window must be positive")
    return _as_series(values, name="rolling_std").rolling(window=window, min_periods=window).std()
