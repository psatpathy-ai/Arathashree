from __future__ import annotations
import pandas as pd
import numpy as np
from .risk import position_size

class BacktestResult:
    def __init__(self, equity, trades):
        self.equity = equity
        self.trades = trades

    def metrics(self):
        eq = self.equity["equity"]
        ret = eq.pct_change().fillna(0)
        total = eq.iloc[-1] / eq.iloc[0] - 1
        days = max((eq.index[-1] - eq.index[0]).days, 1)
        cagr = (eq.iloc[-1] / eq.iloc[0]) ** (365.25 / days) - 1
        dd = eq / eq.cummax() - 1
        max_dd = dd.min()
        vol = ret.std() * np.sqrt(252)
        sharpe = (ret.mean() * 252 / vol) if vol > 0 else 0.0
        t = self.trades
        wins = t[t["pnl"] > 0]["pnl"] if len(t) else pd.Series(dtype=float)
        losses = t[t["pnl"] <= 0]["pnl"] if len(t) else pd.Series(dtype=float)
        win_rate = len(wins) / len(t) if len(t) else 0
        pf = wins.sum() / abs(losses.sum()) if len(losses) and losses.sum() != 0 else np.inf
        return {
            "initial_equity": float(eq.iloc[0]),
            "final_equity": float(eq.iloc[-1]),
            "total_return": float(total),
            "cagr": float(cagr),
            "max_drawdown": float(max_dd),
            "sharpe_daily": float(sharpe),
            "trades": int(len(t)),
            "win_rate": float(win_rate),
            "profit_factor": float(pf),
        }

from arthashree.risk_engine import DefaultRiskEngine
from arthashree.events import OrderEvent


def run_backtest(df, cfg, risk_engine: DefaultRiskEngine | None = None):
    """Simple event-loop backtest with optional risk_engine integration.

    If risk_engine is provided, it will be consulted before placing entries.
    When no risk_engine is supplied, create a DefaultRiskEngine whose internal
    RiskModel is seeded from the cfg values so pre-trade sizing logic matches
    the backtest configuration.
    """
    if risk_engine is None:
        # Seed risk model from cfg to keep sizing consistent with run_backtest
        from .risk import RiskModel, CostModel

        model = RiskModel(risk_per_trade=cfg.get("risk_per_trade", 0.01), max_position_notional_pct=cfg.get("max_position_notional_pct", 0.25))
        costs = CostModel(commission_bps=cfg.get("commission_bps", 5.0), slippage_bps=cfg.get("slippage_bps", 10.0))
        risk_engine = DefaultRiskEngine(model=model, costs=costs)

    equity = float(cfg["initial_capital"])
    cash = equity
    position = None
    eq_rows = []
    trades = []

    commission = cfg["commission_bps"] / 10000
    slippage = cfg["slippage_bps"] / 10000

    def current_daily_loss(trades_list):
        # sum of losses (positive number)
        loss = 0.0
        for t in trades_list:
            pnl = float(t.get("pnl", 0.0))
            if pnl < 0:
                loss += abs(pnl)
        return loss

    for i, (dt, row) in enumerate(df.iterrows()):
        if position:
            exit_price = None
            reason = None

            # Conservative OHLC ordering: stop gets priority when both stop and target
            # are touched in the same bar.
            if row["low"] <= position["stop"]:
                exit_price = position["stop"] * (1 - slippage)
                reason = "stop"
            elif row["high"] >= position["target"]:
                exit_price = position["target"] * (1 - slippage)
                reason = "target"
            elif not bool(row["weekly_trend_ok"]) or row["close"] < row["ema_fast"]:
                exit_price = row["close"] * (1 - slippage)
                reason = "trend_exit"
            elif i - position["entry_i"] >= cfg["max_bars_in_trade"]:
                exit_price = row["close"] * (1 - slippage)
                reason = "time_exit"

            if exit_price is not None:
                qty = position["qty"]
                entry_value = qty * position["entry"]
                exit_value = qty * exit_price
                fees = (entry_value + exit_value) * commission
                pnl = exit_value - entry_value - fees
                cash += exit_value - fees
                trades.append({
                    "entry_date": position["entry_dt"],
                    "exit_date": dt,
                    "entry": position["entry"],
                    "exit": exit_price,
                    "qty": qty,
                    "pnl": pnl,
                    "reason": reason
                })
                position = None

        if position is None and bool(row["signal"]) and pd.notna(row["atr"]):
            # Signal is evaluated on the close; entry occurs at next bar open.
            if i + 1 < len(df):
                next_open = df.iloc[i + 1]["open"]
                entry = next_open * (1 + slippage)
                stop = entry - cfg["atr_stop_multiple"] * row["atr"]
                target = entry + cfg["reward_risk"] * (entry - stop)
                qty = position_size(
                    cash, entry, stop, cfg["risk_per_trade"],
                    cfg["max_position_notional_pct"]
                )
                if qty > 0:
                    # Build a tentative order event and portfolio snapshot
                    order = OrderEvent(timestamp=None, symbol=None, direction="long", quantity=qty, price=entry, payload={"stop_price": stop})
                    portfolio = {
                        "equity": cash,
                        "daily_loss": current_daily_loss(trades),
                        "open_positions": [] if position is None else [{
                            "symbol": None,
                            "qty": position["qty"],
                            "entry": position["entry"],
                            "notional": position["qty"] * position["entry"]
                        }]
                    }
                    market = {"stop_price": stop}
                    decision = risk_engine.approve(order, portfolio, market)
                    if decision.approved:
                        entry_value = qty * entry
                        fee = entry_value * commission
                        cash -= fee
                        position = {
                            "entry_dt": df.index[i + 1],
                            "entry_i": i + 1,
                            "entry": entry,
                            "stop": stop,
                            "target": target,
                            "qty": qty
                        }

        mtm = cash
        if position:
            mtm += position["qty"] * row["close"]
        eq_rows.append({"date": dt, "equity": mtm})

    # Force-close any open position at final close.
    if position:
        dt = df.index[-1]
        exit_price = df.iloc[-1]["close"] * (1 - slippage)
        qty = position["qty"]
        entry_value = qty * position["entry"]
        exit_value = qty * exit_price
        fees = (entry_value + exit_value) * commission
        pnl = exit_value - entry_value - fees
        cash += exit_value - fees
        trades.append({
            "entry_date": position["entry_dt"],
            "exit_date": dt,
            "entry": position["entry"],
            "exit": exit_price,
            "qty": qty,
            "pnl": pnl,
            "reason": "final_close"
        })
        eq_rows[-1]["equity"] = cash

    equity_df = pd.DataFrame(eq_rows).set_index("date")
    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        trades_df = pd.DataFrame(columns=["entry_date","exit_date","entry","exit","qty","pnl","reason"])
    return BacktestResult(equity_df, trades_df)
