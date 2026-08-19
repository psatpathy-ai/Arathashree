from __future__ import annotations
import argparse, json
from .data import load_ohlcv
from .features import add_features
from .backtest import run_backtest
from .validation import validate

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ["backtest", "validate"]:
        sp = sub.add_parser(name)
        sp.add_argument("--data", required=True)
        sp.add_argument("--config", required=True)

    args = p.parse_args()
    with open(args.config) as f:
        cfg = json.load(f)
    df = load_ohlcv(args.data)
    df = add_features(df, cfg)

    if args.cmd == "backtest":
        result = run_backtest(df, cfg)
        print(json.dumps(result.metrics(), indent=2))
        if len(result.trades):
            result.trades.to_csv("reports/trades.csv", index=False)
        result.equity.to_csv("reports/equity_curve.csv")
    else:
        print(json.dumps(validate(df, cfg), indent=2))

if __name__ == "__main__":
    main()
