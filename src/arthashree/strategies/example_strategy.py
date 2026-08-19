from __future__ import annotations

from ..strategy import Strategy, TargetAllocation


class ExampleStrategy(Strategy):
    """A trivial example strategy used for tests and demos."""
    version = "0.1"

    def prepare(self, context: dict):
        # no stateful preparation required for the example
        self.symbol = context.get('symbol')

    def generate_target(self, context: dict) -> TargetAllocation:
        # simple long if close is higher than open
        if context.get('close', None) is not None and context.get('open', None) is not None:
            if context['close'] > context['open']:
                return TargetAllocation(direction='long', weight=0.01)
        return TargetAllocation(direction='flat', weight=0.0)


# helper constant for register_from_path default
STRATEGY_CLASS_NAME = 'ExampleStrategy'
