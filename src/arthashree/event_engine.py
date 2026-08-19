from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .events import MarketEvent, SignalEvent, OrderEvent, FillEvent
from .strategy_registry import StrategyRegistry, RunCard
from .risk_engine import RiskEngine, DefaultRiskEngine
from .backtest import BacktestResult
from .logging_setup import get_logger
import time, os, json


@dataclass
class EventBacktester:
    df: pd.DataFrame
    cfg: dict
    strategy_registry: StrategyRegistry
    run_card: RunCard
    risk_engine: RiskEngine | None = None

    def run(self) -> BacktestResult:
        # Ensure risk engine and logger
        if self.risk_engine is None:
            self.risk_engine = DefaultRiskEngine()
        logger = get_logger("arthashree.event_engine", extra={"strategy": self.run_card.strategy, "symbol": self.run_card.symbol})
        logger.info({"evt": "run_start", "strategy": self.run_card.strategy, "symbol": self.run_card.symbol})

        equity = float(self.cfg.get("initial_capital", 1_000_000))
        cash = equity
        position = None
        eq_rows = []
        trades = []

        commission = self.cfg.get("commission_bps", 2.0) / 10000.0
        slippage = self.cfg.get("slippage_bps", 5.0) / 10000.0

        def current_daily_loss(trades_list):
            loss = 0.0
            for t in trades_list:
                pnl = float(t.get("pnl", 0.0))
                if pnl < 0:
                    loss += abs(pnl)
            return loss

        strategy = self.strategy_registry.create(self.run_card.strategy)

        for i, (dt, row) in enumerate(self.df.iterrows()):
            # Market event
            market_event = MarketEvent(timestamp=dt, payload=row.to_dict())

            # If we have an open position, check for exit
            if position:
                exit_price = None
                reason = None
                if row["low"] <= position["stop"]:
                    exit_price = position["stop"] * (1 - slippage)
                    reason = "stop"
                elif row["high"] >= position["target"]:
                    exit_price = position["target"] * (1 - slippage)
                    reason = "target"
                elif not bool(row.get("weekly_trend_ok", True)) or row["close"] < row.get("ema_fast", row["close"]):
                    exit_price = row["close"] * (1 - slippage)
                    reason = "trend_exit"
                elif i - position["entry_i"] >= self.cfg.get("max_bars_in_trade", 30):
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
                        "reason": reason,
                    })
                    position = None

            # Strategy decision when no open position
            if position is None:
                # Prepare context and ask strategy for a target
                context = {"symbol": self.run_card.symbol}
                context.update(self.run_card.params or {})
                context.update(self.cfg)
                strategy.prepare(context)
                target = strategy.generate_target(context)

                if target and target.direction in {"long", "short"} and target.weight > 0:
                    # Only consider entries when ATR is available to compute stops
                    if pd.notna(row.get("atr")) and row.get("atr", 0.0) > 0:
                        # Attempt entry at next bar open
                        if i + 1 < len(self.df):
                            next_open = self.df.iloc[i + 1]["open"]
                            entry_price = next_open * (1 + slippage)
                            stop = entry_price - self.cfg.get("atr_stop_multiple", 2.0) * row.get("atr", 0.0)
                            target_price = entry_price + self.cfg.get("reward_risk", 2.0) * (entry_price - stop)

                            # Compute size using risk engine / model
                            qty = 0
                            # Build order and portfolio snapshot
                            # quantity estimation: use RiskEngine via approve path
                            # use requested notional proportional to weight of equity
                            desired_notional = equity * float(target.weight)
                            # if price <=0, skip
                            if entry_price > 0:
                                qty = int(desired_notional // entry_price)

                            if qty > 0:
                                order = OrderEvent(timestamp=None, symbol=self.run_card.symbol, direction=target.direction, quantity=qty, price=entry_price, payload={"stop_price": stop})
                                portfolio = {"equity": cash, "daily_loss": current_daily_loss(trades), "open_positions": []}
                                # Log the attempted order
                                logger.info({"evt": "order_attempt", "order": {"symbol": self.run_card.symbol, "qty": qty, "price": entry_price}})
                                decision = self.risk_engine.approve(order, portfolio, {"stop_price": stop})
                                logger.info({"evt": "risk_decision", "decision": {"approved": decision.approved, "reason": decision.reason}})
                                if decision.approved:
                                    entry_value = qty * entry_price
                                    fee = entry_value * commission
                                    cash -= fee
                                    position = {
                                        "entry_dt": self.df.index[i + 1],
                                        "entry_i": i + 1,
                                        "entry": entry_price,
                                        "stop": stop,
                                        "target": target_price,
                                        "qty": qty,
                                    }
                                    logger.info({"evt": "order_filled", "entry": entry_price, "qty": qty})

            # MTM record
            mtm = cash
            if position:
                mtm += position["qty"] * row["close"]
            eq_rows.append({"date": dt, "equity": mtm})

        # Force close
        if position:
            dt = self.df.index[-1]
            exit_price = self.df.iloc[-1]["close"] * (1 - slippage)
            qty = position["qty"]
            entry_value = qty * position["entry"]
            exit_value = qty * exit_price
            fees = (entry_value + exit_value) * commission
            pnl = exit_value - entry_value - fees
            cash += exit_value - fees
            trades.append({"entry_date": position["entry_dt"], "exit_date": dt, "entry": position["entry"], "exit": exit_price, "qty": qty, "pnl": pnl, "reason": "final_close"})
            eq_rows[-1]["equity"] = cash

        equity_df = pd.DataFrame(eq_rows).set_index("date")
        trades_df = pd.DataFrame(trades)
        if trades_df.empty:
            trades_df = pd.DataFrame(columns=["entry_date", "exit_date", "entry", "exit", "qty", "pnl", "reason"])

        # Write run-card output if configured via self.cfg or attribute
        run_card_dir = getattr(self, "run_card_dir", None) or self.cfg.get("run_card_dir")
        if run_card_dir:
            os.makedirs(run_card_dir, exist_ok=True)
            ts = time.strftime("%Y%m%dT%H%M%S")
            out_path = os.path.join(run_card_dir, f"runcard-{self.run_card.strategy}-{ts}.json")
            summary = {
                "strategy": self.run_card.strategy,
                "symbol": self.run_card.symbol,
                "cfg": {k: self.cfg[k] for k in sorted(self.cfg) if k in ["initial_capital", "risk_per_trade", "max_position_notional_pct"]},
                "metrics": BacktestResult(equity_df, trades_df).metrics(),
                "trades": trades_df.to_dict(orient="records"),
            }
            open(out_path, "w").write(json.dumps(summary, indent=2, default=str))
            logger.info({"evt": "run_card_written", "path": out_path})

        logger.info({"evt": "run_end", "strategy": self.run_card.strategy, "symbol": self.run_card.symbol})
        return BacktestResult(equity_df, trades_df)
