# Book → Machine Translation

## Trading in the Zone

The book explicitly says it is not a trading system; it is about the mindset required to execute an edge. Arthashree therefore converts the principles into controls rather than pretending the book itself proves a strategy.

| Principle | Arthashree implementation |
|---|---|
| You do not need to know the next outcome | Strategy outputs probability/edge statistics, never certainty |
| Anything can happen | Every position requires a predefined invalidation/stop |
| Every moment is unique | No copying of a previous trade outcome into the next decision |
| Define risk before entry | Position sizing is calculated before order creation |
| Avoid rationalization/hope | Exit rules are machine-enforced |
| Consistency | Same signal/risk logic for every eligible observation |
| Take responsibility | Every order is linked to a strategy version/config hash |
| Avoid random trading | No discretionary signal can bypass validation in production |

## Trading for a Living

The book supplies technical-analysis and risk-management hypotheses including moving averages, MACD, momentum/oscillators, Triple Screen, stops, commissions/slippage, and the 2% risk rule.

Arthashree starts more conservatively at 1% risk per trade. The 2% figure is treated as a historical rule/hypothesis, not a mandatory target.

The book also warns against martingale sizing and emphasizes accounting for commissions/slippage. These become hard constraints in the engine.

## Research rule

No indicator is accepted because a book recommends it. A component survives only if it adds robust out-of-sample evidence after costs and across market regimes.
