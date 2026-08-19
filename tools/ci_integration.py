from pathlib import Path
import json

from arthashree.data import normalize_raw
from arthashree.strategy_registry import StrategyRegistry, RunCard
from arthashree.strategy import Strategy, TargetAllocation
from arthashree.features import add_features
from arthashree.event_engine import EventBacktester


class CIExampleStrategy(Strategy):
    name = "ci_example"

    def generate_target(self, context):
        # go long with small weight if ATR present
        if context.get("atr", None) is not None:
            return TargetAllocation(direction="long", weight=0.001)
        return TargetAllocation(direction="flat", weight=0.0)


def main():
    repo_root = Path(__file__).parent
    artifacts = repo_root / "artifacts"
    artifacts.mkdir(exist_ok=True)

    # Normalize sample data
    raw = repo_root / "data" / "sample_ohlcv.csv"
    norm_dest = artifacts / "normalized"
    norm_dest.mkdir(parents=True, exist_ok=True)
    try:
        manifest = normalize_raw(raw, symbol="CI_SAMPLE", dest=norm_dest, overwrite=True)
    except Exception as e:
        print("Normalization failed:", e)
        raise

    # Prepare features and run event engine
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

    import pandas as pd
    df = pd.read_csv(norm_dest / "CI_SAMPLE.csv")
    # ensure date parsed and index set like load_ohlcv
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df = add_features(df, cfg)

    reg = StrategyRegistry()
    reg.register("ci_example", CIExampleStrategy)
    run_card = RunCard(strategy="ci_example", symbol="CI_SAMPLE", params={})

    engine = EventBacktester(df=df, cfg=cfg, strategy_registry=reg, run_card=run_card)
    engine.run_card_dir = str(artifacts / "run_cards")
    result = engine.run()

    summary_path = artifacts / "summary.json"
    summary = {"metrics": result.metrics(), "trades": result.trades.to_dict(orient="records")}
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print("Integration run complete. Artifacts in:", artifacts)


if __name__ == "__main__":
    main()
