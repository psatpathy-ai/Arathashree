from __future__ import annotations
import pandas as pd
import numpy as np
from .backtest import run_backtest

def chronological_split(df, train=0.6, validation=0.2):
    n = len(df)
    a = int(n * train)
    b = int(n * (train + validation))
    return df.iloc[:a], df.iloc[a:b], df.iloc[b:]

from .risk_engine import DefaultRiskEngine

def validate(df, cfg):
    train, val, test = chronological_split(df)
    engine = DefaultRiskEngine()
    return {
        "train": run_backtest(train, cfg, risk_engine=engine).metrics(),
        "validation": run_backtest(val, cfg, risk_engine=engine).metrics(),
        "test": run_backtest(test, cfg, risk_engine=engine).metrics(),
    }
