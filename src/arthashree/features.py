from __future__ import annotations
import numpy as np
import pandas as pd

def ema(s, n): return s.ewm(span=n, adjust=False, min_periods=n).mean()

def atr(df, n=14):
    prev = df["close"].shift(1)
    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev).abs(),
        (df["low"] - prev).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/n, adjust=False, min_periods=n).mean()

def rsi(s, n=14):
    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    avg_loss = loss.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(s, fast=12, slow=26, signal=9):
    line = ema(s, fast) - ema(s, slow)
    sig = ema(line, signal)
    return line, sig, line - sig

def add_features(df, cfg):
    out = df.copy()
    out["ema_fast"] = ema(out["close"], cfg["ema_fast"])
    out["atr"] = atr(out, cfg["atr_period"])
    out["rsi"] = rsi(out["close"], cfg["rsi_period"])
    out["macd"], out["macd_signal"], out["macd_hist"] = macd(
        out["close"], cfg["macd_fast"], cfg["macd_slow"], cfg["macd_signal"]
    )

    # Higher timeframe screen. Resampling uses only completed weekly bars.
    weekly = out[["open","high","low","close","volume"]].resample("W-FRI").agg({
        "open":"first", "high":"max", "low":"min", "close":"last", "volume":"sum"
    })
    weekly["wema"] = ema(weekly["close"], cfg["ema_weekly"])
    weekly["wema_slope"] = weekly["wema"].diff()
    weekly["trend_ok"] = (weekly["close"] > weekly["wema"]) & (weekly["wema_slope"] > 0)

    # Map the last completed weekly observation to daily rows.
    out["week_key"] = out.index.to_period("W-FRI")
    weekly["week_key"] = weekly.index.to_period("W-FRI")
    out = out.join(
        weekly[["trend_ok"]].rename(columns={"trend_ok":"weekly_trend_ok"}),
        on="week_key"
    )
    out["weekly_trend_ok"] = out["weekly_trend_ok"].shift(1)
    out["rsi_cross_up"] = (out["rsi"].shift(1) <= 50) & (out["rsi"] > 50)
    out["signal"] = (
        out["weekly_trend_ok"].fillna(False)
        & (out["close"] > out["ema_fast"])
        & (out["macd_hist"] > 0)
        & out["rsi_cross_up"].fillna(False)
    )
    return out.drop(columns=["week_key"])
