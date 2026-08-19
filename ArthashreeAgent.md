# Arthashree --- NSE + Zerodha/Kite Connect Backtest → Paper Trading → Controlled Live Deployment

**Project:** Arthashree\
**Document purpose:** Single operating specification for VS Code +
Claude Code / coding agent\
**Version:** 1.0\
**Prepared:** 2026-08-19\
**Primary market:** NSE India\
**Broker/execution API:** Zerodha Kite Connect\
**Implementation language:** Python\
**Status:** Research/backtest first. No live trading until every
deployment gate passes.

This operating spec is intentionally conservative. The technical architecture has been re-synthesized in [ArthashreeAgentv2.md](</Users/priyamac/Desktop/Athashree Quant v2/Arthashree_v0_1/ArthashreeAgentv2.md>) around the strongest ideas from GS Quant (deterministic data/backtest/risk foundations) and Vibe-Trading (research autopilot, validation, artifacting, and security boundaries).

------------------------------------------------------------------------

## 0. NON-NEGOTIABLE RULES

Claude Code / any coding agent working on Arthashree MUST follow these
rules.

1.  **Never claim a strategy is profitable without measured
    out-of-sample evidence.**
2.  **Never use future information in a feature, signal, portfolio
    decision, or execution simulation.**
3.  **Never silently repair suspicious market data.** Flag it,
    quarantine it, and report it.
4.  **Never use synthetic data as evidence of a real trading edge.**
    Synthetic data is only for pipeline/unit tests.
5.  **Every backtest must include transaction costs and realistic
    slippage assumptions.**
6.  **Every live order must pass a pre-trade risk gate.**
7.  **No martingale sizing.**
8.  **No averaging down unless a separately validated strategy
    explicitly defines it and the risk engine approves it. Default:
    prohibited.**
9.  **No discretionary override in the live execution path.**
10. **Secrets must never be committed to Git.**
11. **Never put `api_secret`, access tokens, TOTP secrets, broker
    passwords, or private keys into source code, logs, prompts,
    screenshots, or Git history.**
12. **Never place a live order during development, testing, backtesting,
    or paper-trading mode.**
13. **Default execution mode is `DISABLED` / `PAPER`.**
14. **Live trading requires an explicit configuration change plus all
    deployment gates passing.**
15. **If broker/exchange documentation conflicts with an assumption in
    this document, stop and verify the current official documentation
    before implementing.**

------------------------------------------------------------------------

# 1. SOURCE BASIS

Arthashree uses the two uploaded books as conceptual inputs, not as
proof that any particular indicator or strategy is profitable.

## 1.1 Trading in the Zone

The core ideas to convert into machine-enforced controls are:

-   trading is probabilistic;
-   the next outcome does not need to be known;
-   anything can happen;
-   each trade is an independent event;
-   risk should be defined before entering;
-   consistency and trust in a tested edge matter;
-   emotional decisions and rule-breaking damage execution.

The book explicitly says it does **not** provide a trading system; it
focuses on the mindset required to execute an edge. Arthashree therefore
translates the principles into engineering controls rather than
pretending the book itself supplies a profitable strategy.

Reference: uploaded `Trading_in_the_Zone.pdf`, including the
preface/objectives and attitude survey. The book states that the trader
should think in probabilities and trust a tested edge.

## 1.2 Trading for a Living

The book provides technical-analysis and trading/risk-management
material including:

-   trend and trading ranges;
-   moving averages;
-   MACD;
-   momentum;
-   RSI;
-   stochastic;
-   volume;
-   open interest;
-   Triple Screen;
-   stop-loss rules;
-   money management;
-   transaction costs;
-   the 2% risk rule;
-   warnings against martingale sizing.

Arthashree treats these as **research hypotheses**. No indicator is
accepted merely because it appears in the book.

The initial Arthashree risk setting is intentionally more conservative
than the historical 2% rule:

``` text
risk_per_trade = 1%
```

This is a project default, not a claim that 1% is optimal.

------------------------------------------------------------------------

# 2. CURRENT BROKER/EXCHANGE FACTS --- VERIFY BEFORE LIVE DEPLOYMENT

This section was checked against current official NSE/Zerodha/Kite
documentation during preparation.

## 2.1 Zerodha Kite Connect

Kite Connect provides APIs for:

-   order placement;
-   order modification/cancellation;
-   portfolio/positions;
-   historical candle data;
-   market quotes;
-   WebSocket live market data.

Official documentation:

-   https://kite.trade/docs/connect/v3/
-   https://kite.trade/docs/connect/v3/user/
-   https://kite.trade/docs/connect/v3/historical/
-   https://kite.trade/docs/connect/v3/orders/
-   https://kite.trade/docs/connect/v3/websocket/
-   https://kite.trade/docs/connect/v3/exceptions/

### Current pricing

Zerodha's current documentation lists:

-   **Personal:** free, but no live/historical market data through Kite
    Connect.
-   **Connect:** ₹500/month per API key, including real-time WebSocket
    data and historical candle data.

Verify current pricing before purchase:

https://zerodha.com/products/api/

https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis

Do not hard-code the price into software.

------------------------------------------------------------------------

# 3. EXACT ZERODHA/KITE CONNECT SETUP

## Step 1 --- Have an active Zerodha account

Kite Connect documentation lists an active Zerodha trading account and
2FA/TOTP as prerequisites.

Do not give the coding agent your Zerodha password.

------------------------------------------------------------------------

## Step 2 --- Subscribe to Kite Connect

For Arthashree's real-data research and live execution, the paid Connect
tier is the relevant tier because it includes historical candles and
WebSocket market data.

Current documented price: ₹500/month per API key.

Official support:

https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/how-do-i-sign-up-for-kite-connect

------------------------------------------------------------------------

## Step 3 --- Create the API application

Go to:

https://developers.kite.trade/

Create a new app.

Current Zerodha support instructions say to provide:

-   App Name
-   Zerodha Client ID
-   Redirect URL
-   optional Postback URL
-   Description

Example development redirect:

``` text
http://127.0.0.1:8000/kite/callback
```

Use an HTTPS production callback when appropriate.

After creation, Zerodha provides:

``` text
API_KEY
API_SECRET
```

Store these in environment variables or a secret manager.

Never commit them.

------------------------------------------------------------------------

# 4. KITE AUTHENTICATION FLOW

Kite Connect does not simply use a permanent API token.

The documented flow is:

``` text
Arthashree
   |
   | open login URL
   v
Kite Login
   |
   | successful login
   v
registered redirect URL
   |
   | request_token
   v
POST /session/token
   |
   | api_key + request_token + checksum
   v
access_token
   |
   v
Kite API
```

The checksum is:

``` text
SHA256(api_key + request_token + api_secret)
```

The access token is then used for subsequent API requests.

The documented access token expires at 6 AM on the next day unless
invalidated earlier.

Official documentation:

https://kite.trade/docs/connect/v3/user/

## Critical security rule

Do not expose:

``` text
API_SECRET
ACCESS_TOKEN
ZERODHA_PASSWORD
TOTP_SECRET
```

to Claude, GitHub, Git, logs, screenshots, or client-side code.

------------------------------------------------------------------------

# 5. KITE PYTHON SDK

Use the official Python client:

``` text
pykiteconnect
```

Official documentation:

https://kite.trade/docs/connect/v3/agent-setup/

The current official agent setup documentation recommends using `uv` and
gives:

``` bash
uv init arthashree
cd arthashree
uv add kiteconnect
```

If the existing project already uses `venv`/`pip`, do not unnecessarily
migrate it. Use the project's existing dependency management.

------------------------------------------------------------------------

# 6. KITE INSTRUMENT MASTER

Arthashree must not hard-code instrument tokens.

Use the broker instrument master and maintain a local normalized
instrument table.

Required fields should include, where available:

``` text
exchange
tradingsymbol
instrument_token
segment
instrument_type
expiry
strike
tick_size
lot_size
```

For example:

``` text
NSE:INFY
```

is a human-readable instrument identity, while the `instrument_token` is
used by the Kite market-data APIs/WebSocket.

The instrument master must be refreshed and versioned.

Recommended file:

``` text
data/reference/kite_instruments.csv
```

Recommended metadata:

``` text
data/reference/kite_instruments_metadata.json
```

Never assume an instrument token remains valid forever without checking
the current instrument master.

------------------------------------------------------------------------

# 7. NSE DATA STRATEGY

Arthashree should distinguish two data sources.

## Source A --- NSE official historical/EOD data

Use NSE data where the exchange source is required.

NSE's historical reports currently expose:

-   security-wise price/volume archives;
-   historical index data;
-   contract-wise price/volume data for equity derivatives;
-   daily/monthly reports;
-   corporate-action-related information;
-   other exchange reports.

Official historical reports:

https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives

Official derivatives reports:

https://www.nseindia.com/all-reports-derivatives

NSE's current report pages also indicate that older F&O/common bhavcopy
formats were discontinued and UDiFF common bhavcopy formats are used for
current reporting. Do not build a new parser around a discontinued
format without checking the current report specification.

------------------------------------------------------------------------

## Source B --- Zerodha Kite historical candles

Kite Connect's historical candle API provides:

``` text
timestamp
open
high
low
close
volume
OI
```

depending on instrument/data availability.

Official documentation:

https://kite.trade/docs/connect/v3/historical/

The API uses:

``` text
GET /instruments/historical/:instrument_token/:interval
```

Supported intervals include minute, 3minute, 5minute and daily, with
additional intervals documented by Zerodha.

Use the broker data primarily for:

-   live/paper-trading feed;
-   instrument-specific research;
-   intraday historical data where permitted/available;
-   cross-checking data.

Do not assume that broker data alone is the same as a complete
institutional-grade historical dataset.

------------------------------------------------------------------------

# 8. NSE DATA LICENSING / USAGE

NSE distinguishes market-data products and has a data-sharing/usage
policy.

Official:

https://www.nseindia.com/static/market-data/nse-data-policy

NSE Data & Analytics provides EOD/historical, real-time and other
market-data products:

https://www.nseindia.com/static/nse-data-and-analytics/data-information-vending

For commercial redistribution, non-display use, large-scale data use, or
other institutional uses, confirm the applicable NSE data licence/terms.

Do not scrape NSE pages as a substitute for a licensed data feed when
the intended use requires a commercial/non-display data licence.

------------------------------------------------------------------------

# 9. WHAT DATA ARTHASHREE SHOULD COLLECT

For initial research:

``` text
NIFTY 50
NIFTY NEXT 50
NIFTY BANK
selected liquid NSE equities
```

Do not start with thousands of securities.

Start with a controlled universe.

Recommended v1 universe:

``` text
NIFTY 50 constituents
```

But the constituent list must be point-in-time correct.

## Critical survivorship-bias rule

Do NOT backtest today's NIFTY 50 constituent list over a 10-year
history.

Instead maintain:

``` text
effective_from
effective_to
symbol
```

for index membership.

Otherwise delisted/removed companies disappear from the historical
universe and the backtest becomes biased.

------------------------------------------------------------------------

# 10. CORPORATE ACTIONS

For equity strategies, data must correctly handle:

-   splits;
-   bonuses;
-   dividends where relevant;
-   symbol changes;
-   mergers;
-   delistings;
-   corporate restructuring.

Do not blindly apply an adjustment to OHLC without understanding whether
the adjustment is appropriate for the strategy.

Store raw and normalized data separately:

``` text
data/raw/
data/normalized/
data/reference/
```

------------------------------------------------------------------------

# 11. ARTHASHREE ARCHITECTURE

``` text
                 ┌───────────────────────┐
                 │ NSE / Kite Data       │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Data Validation       │
                 │ + Corporate Actions  │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Feature Engine        │
                 │ EMA / ATR / RSI / MACD│
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Strategy Engine       │
                 │ Signal + Probability  │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Risk Engine           │
                 │ Position sizing       │
                 │ Exposure / drawdown   │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Portfolio Engine      │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Execution Simulator   │
                 │ Slippage + Costs      │
                 └──────────┬────────────┘
                            │
              ┌─────────────┴─────────────┐
              v                           v
       ┌─────────────┐             ┌─────────────┐
       │ Backtest    │             │ Paper Trade │
       └──────┬──────┘             └──────┬──────┘
              │                           │
              └─────────────┬─────────────┘
                            v
                 ┌───────────────────────┐
                 │ Validation / Research │
                 │ Walk-forward          │
                 │ Monte Carlo           │
                 │ Robustness             │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Deployment Gate       │
                 └──────────┬────────────┘
                            │
                            v
                 ┌───────────────────────┐
                 │ Kite Execution        │
                 │ CONTROLLED LIVE       │
                 └───────────────────────┘
```

------------------------------------------------------------------------

# 12. REPOSITORY STRUCTURE

Use this structure:

``` text
Arthashree/
│
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── config/
│   ├── research.yaml
│   ├── backtest.yaml
│   ├── paper.yaml
│   └── live.yaml
│
├── src/
│   └── arthashree/
│       ├── __init__.py
│       │
│       ├── data/
│       │   ├── nse.py
│       │   ├── kite.py
│       │   ├── instruments.py
│       │   ├── corporate_actions.py
│       │   └── validation.py
│       │
│       ├── features/
│       │   ├── trend.py
│       │   ├── momentum.py
│       │   ├── volatility.py
│       │   └── volume.py
│       │
│       ├── strategies/
│       │   ├── base.py
│       │   ├── triple_screen.py
│       │   └── registry.py
│       │
│       ├── portfolio/
│       │   ├── position_sizing.py
│       │   ├── exposure.py
│       │   └── portfolio.py
│       │
│       ├── risk/
│       │   ├── limits.py
│       │   ├── drawdown.py
│       │   └── pretrade.py
│       │
│       ├── execution/
│       │   ├── simulator.py
│       │   ├── paper.py
│       │   └── kite_live.py
│       │
│       ├── validation/
│       │   ├── walk_forward.py
│       │   ├── monte_carlo.py
│       │   ├── robustness.py
│       │   └── leakage.py
│       │
│       ├── reporting/
│       │   ├── metrics.py
│       │   ├── trades.py
│       │   └── reports.py
│       │
│       └── cli.py
│
├── tests/
│
├── data/
│   ├── raw/
│   ├── normalized/
│   ├── reference/
│   └── cache/
│
├── experiments/
│
├── reports/
│
├── logs/
│
└── scripts/
```

------------------------------------------------------------------------

# 13. ENVIRONMENT VARIABLES

Create:

``` text
.env.example
```

with:

``` text
KITE_API_KEY=
KITE_API_SECRET=
KITE_ACCESS_TOKEN=
KITE_REDIRECT_URL=
KITE_POSTBACK_URL=

ARTHASHREE_MODE=PAPER

ARTHASHREE_INITIAL_CAPITAL=1000000
ARTHASHREE_RISK_PER_TRADE=0.01
ARTHASHREE_MAX_DAILY_LOSS=0.02
ARTHASHREE_MAX_DRAWDOWN=0.10

ARTHASHREE_LOG_LEVEL=INFO
```

Do NOT put actual secrets in `.env.example`.

Actual `.env` must be ignored by Git:

``` gitignore
.env
*.secret
secrets/
```

------------------------------------------------------------------------

# 14. INITIAL STRATEGY HYPOTHESIS

Arthashree v0.1 uses:

``` text
triple_screen_trend_pullback
```

This is a research hypothesis derived from concepts appearing in the
uploaded material.

## Higher timeframe

Weekly:

``` text
close > EMA(26)
EMA(26) slope > 0
```

## Daily trend

``` text
close > EMA(50)
```

## Momentum

``` text
MACD histogram > 0
```

## Pullback/re-entry

``` text
RSI(14) previously <= 50
AND current RSI > 50
```

## Entry

Only when all conditions are true.

## Initial stop

``` text
stop = entry - 2 * ATR(14)
```

## Initial target

``` text
target = entry + 2R
```

where:

``` text
R = entry - stop
```

## Risk

``` text
risk_per_trade = 1% of current equity
```

This is a starting hypothesis.

It is NOT approved for live trading until validated.

------------------------------------------------------------------------

# 15. POSITION SIZING

For a long trade:

``` text
risk_budget = equity × risk_fraction

risk_per_share = entry_price - stop_price

quantity_by_risk =
    floor(risk_budget / risk_per_share)
```

Then apply additional constraints:

``` text
quantity =
min(
    quantity_by_risk,
    quantity_by_capital,
    quantity_by_liquidity,
    quantity_by_exchange_rules,
    quantity_by_portfolio_limit
)
```

For F&O:

``` text
quantity must be a valid multiple of lot_size
```

Never silently round a quantity upward.

If the calculated quantity is zero:

``` text
NO TRADE
```

------------------------------------------------------------------------

# 16. RISK CONTROLS

Minimum controls:

``` text
max risk per trade
max total open risk
max position notional
max sector exposure
max instrument exposure
max daily loss
max weekly loss
max portfolio drawdown
max consecutive losses
max number of trades per day
max order quantity
max order value
```

Example initial research settings:

``` yaml
risk_per_trade: 0.01
max_daily_loss: 0.02
max_portfolio_drawdown: 0.10
max_open_positions: 10
```

These values are research defaults and must be validated/tuned through
research.

------------------------------------------------------------------------

# 17. HARD RISK STOP

If:

``` text
daily_loss >= max_daily_loss
```

then:

``` text
disable new entries
```

If:

``` text
drawdown >= max_portfolio_drawdown
```

then:

``` text
disable new entries
require manual review
```

The system must not automatically increase risk after losses.

------------------------------------------------------------------------

# 18. NO MARTINGALE

Explicitly prohibited:

``` text
loss → double position
loss → double again
loss → double again
```

Trading for a Living specifically discusses the danger of martingale
sizing and the risk of increasing trade size after losses.

Arthashree must never implement:

``` python
next_size = previous_size * 2
```

as a recovery mechanism.

------------------------------------------------------------------------

# 19. BACKTEST EXECUTION MODEL

A backtest must model:

``` text
signal time
order submission time
fill time
fill price
slippage
commission
quantity
partial fills where appropriate
stop/target interaction
position state
cash
margin
```

Never assume:

``` text
signal at close
+
fill at same close
```

unless the strategy explicitly uses information available before that
close and the execution model proves that fill assumption is valid.

For the initial daily strategy:

``` text
signal evaluated at today's completed bar
entry occurs at next bar open
```

This prevents a common look-ahead error.

------------------------------------------------------------------------

# 20. STOP/TARGET SAME-BAR RULE

If both stop and target are touched within one OHLC bar and the exact
intrabar path is unknown:

Default conservative rule:

``` text
STOP TAKES PRIORITY
```

Do not assume the profitable target was reached first.

For higher-fidelity intraday backtesting, use lower-timeframe/tick data
to reconstruct the sequence.

------------------------------------------------------------------------

# 21. TRANSACTION COST MODEL

At minimum:

``` text
brokerage
exchange transaction charges
GST
SEBI charges
stamp duty
STT
slippage
```

The exact current charges depend on instrument, product, exchange and
regulatory schedule.

Do NOT hard-code today's charges permanently.

Create:

``` text
config/costs/
```

and version the assumptions.

For live reconciliation, compare simulated costs with actual broker
contract notes/trades.

------------------------------------------------------------------------

# 22. KITE HISTORICAL DATA PIPELINE

Implement:

``` text
KiteInstrumentLoader
        ↓
instrument_token resolution
        ↓
HistoricalDownloader
        ↓
raw parquet/csv
        ↓
schema validation
        ↓
duplicate check
        ↓
timestamp normalization
        ↓
OHLC consistency check
        ↓
corporate-action treatment
        ↓
normalized dataset
```

Each download must record:

``` text
source
instrument_token
exchange
symbol
interval
start
end
download_time
API version
data hash
```

------------------------------------------------------------------------

# 23. KITE LIVE MARKET DATA

For live/paper mode use the Kite WebSocket.

Official documentation:

https://kite.trade/docs/connect/v3/websocket/

The current documentation says a single WebSocket connection can
subscribe to up to 3000 instruments, with up to 3 WebSocket connections
per API key.

Do not design the system around the assumption that these limits will
never change. Make them configurable.

Preferred modes:

``` text
LTP
QUOTE
FULL
```

Use `FULL` only where market-depth information is actually required.

------------------------------------------------------------------------

# 24. ORDER EXECUTION THROUGH KITE

Kite's order API supports placing, modifying and cancelling orders.

Official:

https://kite.trade/docs/connect/v3/orders/

The documented order endpoint is:

``` text
POST /orders/:variety
```

Important:

**Successful API order placement does NOT mean the order was executed.**

After receiving an `order_id`, Arthashree must query/order-stream the
order state and reconcile fills.

Track:

``` text
order_id
exchange_order_id
status
average_price
filled_quantity
pending_quantity
cancelled_quantity
exchange_timestamp
```

For partially filled orders, reconcile individual trades.

------------------------------------------------------------------------

# 25. ORDER STATE MACHINE

Implement:

``` text
CREATED
   ↓
RISK_APPROVED
   ↓
SUBMITTED
   ↓
OPEN
   ↓
PARTIALLY_FILLED
   ↓
COMPLETE
```

Alternative exits:

``` text
OPEN → CANCELLED
OPEN → REJECTED
OPEN → EXPIRED
```

Never treat:

``` text
SUBMITTED
```

as:

``` text
FILLED
```

------------------------------------------------------------------------

# 26. LIVE EXECUTION SAFETY

The live execution module must have:

``` text
LIVE_TRADING_ENABLED=false
```

by default.

A live order should require:

``` text
mode == LIVE
AND
live_trading_enabled == true
AND
risk_gate == PASS
AND
strategy_version == approved version
AND
data_health == PASS
AND
broker_session == HEALTHY
AND
clock_health == PASS
AND
position_reconciliation == PASS
AND
daily_loss_limit == PASS
```

If any condition fails:

``` text
NO ORDER
```

------------------------------------------------------------------------

# 27. ZERODHA / NSE RETAIL ALGO OPERATING REQUIREMENTS

This area is critical and must be treated as current regulatory
infrastructure, not optional engineering.

NSE issued the retail-algo operating framework in 2025 and subsequent
updates/corrigenda.

Relevant official NSE material includes:

-   NSE/INVG/67858 dated May 5, 2025
-   NSE/INVG/69255 dated July 22, 2025
-   NSE/INVG/69289 dated July 24, 2025
-   subsequent NSE updates/FAQs

Official NSE FAQ:

https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf

The FAQ states that client APIs are treated as Algo orders and require
appropriate tagging, including cases within the 10 orders-per-second
threshold.

Therefore:

**Do not design Arthashree assuming "I place fewer than 10 orders/sec,
so this is just a normal API."**

The broker/exchange handling and tagging requirements still apply.

------------------------------------------------------------------------

# 28. STATIC IP

Current NSE/Zerodha operating guidance requires a static IP for a
tech-savvy retail investor using API order access.

Zerodha's developer guidance has stated that the static IP applies to
API order traffic and that a fixed cloud/VPS setup can be used.

Before enabling live execution:

1.  Obtain a stable public IPv4 address.
2.  Host the live execution service on that machine/server.
3.  Register/whitelist the required IP in the current Zerodha developer
    interface.
4.  Confirm the registration is active.
5.  Send API order requests only from the registered network.
6.  Keep a backup static IP where supported/appropriate.
7.  Do not run live order placement from random laptop/mobile networks.

Official Zerodha developer discussion:

https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types

Important:

**The exact UI/location for static-IP registration can change.**

Claude must inspect the current Zerodha developer console and current
official Zerodha documentation before giving a user an exact
click-by-click instruction.

Do not invent a menu name if the current console differs.

------------------------------------------------------------------------

# 29. ORDER RATE LIMIT

Current Kite documentation states:

``` text
Order placement: 10 requests/second
```

It also documents:

``` text
400 orders/minute
5000 orders/day per user/API key
```

and order modification limits.

Official:

https://kite.trade/docs/connect/v3/exceptions/

For Arthashree:

``` text
internal_order_rate_limit < broker_limit
```

Example safety setting:

``` yaml
max_orders_per_second: 5
```

This gives internal headroom.

Do not design a strategy that intentionally operates near the broker
hard limit.

------------------------------------------------------------------------

# 30. MARKET ORDERS --- DO NOT ASSUME THEY ARE ALLOWED

Current NSE retail-algo FAQ states that algorithmic market orders are
not permitted.

Therefore the live execution design must NOT assume that:

``` text
MARKET
```

is a safe/default order type for algo execution.

The system should prefer a validated order policy such as:

``` text
LIMIT
```

and implement exchange/broker-specific handling.

Before live deployment, Claude must verify the current permitted order
types for the exact segment/product being traded.

Do not hard-code "market order is allowed" anywhere in Arthashree.

------------------------------------------------------------------------

# 31. PAPER TRADING

Do not assume Zerodha provides a production-equivalent paper-trading
account.

The safest Arthashree paper mode is an internal simulator:

``` text
Kite live market data
       ↓
Signal engine
       ↓
Risk engine
       ↓
PAPER EXECUTION ENGINE
       ↓
Simulated fills
       ↓
Portfolio
       ↓
P&L
```

No order is sent to Zerodha.

Paper mode should record:

``` text
signal timestamp
expected order
simulated fill
simulated slippage
simulated costs
position
stop
target
P&L
```

The paper engine must behave as similarly as possible to the live
engine.

------------------------------------------------------------------------

# 32. PAPER → LIVE PARITY

There should be one execution interface:

``` python
class ExecutionBroker:
    def submit_order(...)
    def modify_order(...)
    def cancel_order(...)
    def get_order(...)
    def get_positions(...)
    def get_trades(...)
```

Implement:

``` text
PaperExecutionBroker
KiteExecutionBroker
```

The strategy should not know which broker it is using.

This is essential.

------------------------------------------------------------------------

# 33. BACKTEST VALIDATION GATES

A strategy cannot move from research to paper simply because:

``` text
CAGR is high
```

Required gates:

## Gate A --- Data quality

PASS only if:

-   no unexpected duplicates;
-   timestamps valid;
-   OHLC relationships valid;
-   corporate-action handling verified;
-   no unexplained gaps;
-   instrument mapping verified.

## Gate B --- Look-ahead

PASS only if:

-   all features use information available at decision time;
-   no future bars are joined;
-   no future index membership is used;
-   no future corporate-action knowledge leaks into features;
-   train/validation/test boundaries are respected.

## Gate C --- Cost realism

PASS only if:

-   commissions modeled;
-   exchange/regulatory charges modeled;
-   slippage modeled;
-   liquidity constraints modeled.

## Gate D --- Out-of-sample

PASS only if performance survives:

``` text
TRAIN
VALIDATION
TEST
```

with chronological ordering.

## Gate E --- Walk-forward

Example:

``` text
Train: 2018–2021
Validate: 2022
Test: 2023

Train: 2019–2022
Validate: 2023
Test: 2024

Train: 2020–2023
Validate: 2024
Test: 2025
```

Use actual available dates and avoid overlapping leakage.

## Gate F --- Robustness

Test:

``` text
slippage +25%
slippage +50%
cost +25%
cost +50%
entry delay
exit delay
parameter perturbation
trade removal
regime segmentation
```

## Gate G --- Monte Carlo

Randomize trade sequences and/or relevant return characteristics.

Report:

``` text
median CAGR
5th percentile CAGR
95th percentile CAGR
median max drawdown
95th percentile max drawdown
probability of ruin
```

Do not confuse Monte Carlo confidence intervals with statistical proof
of future profitability.

------------------------------------------------------------------------

# 34. PERFORMANCE METRICS

Every strategy report must contain:

``` text
total return
CAGR
annualized volatility
Sharpe
Sortino
max drawdown
Calmar
profit factor
win rate
average win
average loss
expectancy
number of trades
average holding period
turnover
commission
slippage
gross P&L
net P&L
```

Also report:

``` text
best month
worst month
best trade
worst trade
largest losing streak
largest winning streak
time to recovery
```

------------------------------------------------------------------------

# 35. STRATEGY EXPECTANCY

For a strategy:

``` text
expectancy =
(win_rate × average_win)
-
(loss_rate × average_loss)
```

Calculate both:

``` text
gross expectancy
net expectancy
```

Net expectancy is the important figure.

------------------------------------------------------------------------

# 36. NO SINGLE-METRIC OPTIMIZATION

Never optimize only for:

``` text
CAGR
```

or:

``` text
Sharpe
```

or:

``` text
win rate
```

A strategy with:

``` text
90% win rate
```

can still lose money.

A strategy with:

``` text
40% win rate
```

can potentially be profitable if its winners are sufficiently larger
than its losers.

The system should optimize for robust multi-dimensional performance.

------------------------------------------------------------------------

# 37. EXPERIMENT TRACKING

Every experiment must create:

``` text
experiment_id
timestamp
git_commit
dataset_hash
strategy_version
config_hash
training_period
validation_period
test_period
cost_model_version
results
```

Example:

``` text
experiments/
└── EXP-2026-0001/
    ├── config.yaml
    ├── metrics.json
    ├── trades.csv
    ├── equity.csv
    ├── notes.md
    └── dataset_manifest.json
```

------------------------------------------------------------------------

# 38. CLAUDE CODE OPERATING MODE

Claude should act as:

``` text
Senior Quant Research Engineer
+
Risk Engineer
+
Python Engineer
+
Execution Engineer
+
QA Engineer
```

It must not act as a market guru.

It must prove assumptions with tests.

------------------------------------------------------------------------

# 39. CLAUDE CODE FIRST COMMANDS

Open VS Code terminal.

Go to the repository:

``` bash
cd /path/to/Arthashree
```

Create/activate environment according to the existing project.

If using `uv`:

``` bash
uv sync
```

If using standard Python virtualenv:

``` bash
python -m venv .venv
```

macOS/Linux:

``` bash
source .venv/bin/activate
```

Windows:

``` powershell
.venv\Scripts\Activate.ps1
```

Then:

``` bash
pytest -q
```

Do not continue if existing tests fail without understanding why.

------------------------------------------------------------------------

# 40. FIRST CLAUDE CODE TASK

Give Claude this instruction:

``` text
Read CLAUDE.md and ARTHASHREE_NSE_ZERODHA_AGENT.md completely before modifying code.

You are the senior engineering agent for the Arthashree systematic trading project.

Your job is to implement the system incrementally.

Do NOT jump to live trading.

First inspect:
1. repository structure
2. existing code
3. existing tests
4. current configuration
5. git status
6. Python version
7. installed dependencies

Then create a short implementation plan.

Do not rewrite completed modules unnecessarily.

For every change:
- explain the purpose
- implement the smallest correct change
- add/update tests
- run tests
- report failures
- do not hide warnings
- do not invent broker/exchange behaviour

Priority order:
1. data validation
2. instrument master
3. NSE/Kite data ingestion
4. feature engine
5. strategy engine
6. risk engine
7. backtest engine
8. transaction-cost model
9. walk-forward validation
10. Monte Carlo/robustness
11. reporting
12. paper trading
13. Kite authentication
14. live broker adapter
15. deployment/risk gates

Never enable live order placement during this task.
```

------------------------------------------------------------------------

# 41. CLAUDE CODE BACKTEST COMMAND

After implementation, the intended command should be similar to:

``` bash
python -m arthashree.cli backtest \
  --config config/backtest.yaml \
  --data data/normalized/nifty50.parquet
```

And:

``` bash
python -m arthashree.cli validate \
  --config config/backtest.yaml \
  --data data/normalized/nifty50.parquet
```

The exact CLI may differ based on the repository. Claude must use the
actual implemented CLI rather than inventing commands.

------------------------------------------------------------------------

# 42. DATA DOWNLOAD COMMAND

The final implementation should provide something similar to:

``` bash
python -m arthashree.cli download-kite \
  --symbol INFY \
  --exchange NSE \
  --interval day \
  --from 2015-01-01 \
  --to 2026-08-18
```

For NSE historical files:

``` bash
python -m arthashree.cli ingest-nse \
  --input data/raw/nse/ \
  --output data/normalized/
```

These are target commands. Claude must implement and document the exact
final CLI.

------------------------------------------------------------------------

# 43. PAPER MODE COMMAND

Target:

``` bash
python -m arthashree.cli paper \
  --config config/paper.yaml
```

Required behaviour:

``` text
connect market data
+
calculate signals
+
run risk engine
+
simulate orders
+
record paper fills
+
record P&L
```

Absolutely no broker order placement.

------------------------------------------------------------------------

# 44. LIVE MODE COMMAND

Target:

``` bash
python -m arthashree.cli live \
  --config config/live.yaml
```

But this command must fail unless:

``` text
LIVE_TRADING_ENABLED=true
```

and all deployment gates pass.

Example:

``` text
ERROR:
Live trading disabled.
Set LIVE_TRADING_ENABLED=true only after deployment checklist approval.
```

------------------------------------------------------------------------

# 45. LIVE DEPLOYMENT ARCHITECTURE

Recommended:

``` text
                Internet
                   |
                   v
        ┌────────────────────┐
        │ Static-IP Server   │
        │ AWS/GCP/VPS/etc.   │
        └─────────┬──────────┘
                  |
       ┌──────────┴──────────┐
       v                     v
Market Data             Execution API
WebSocket               Kite Connect
       |                     |
       └──────────┬──────────┘
                  v
          Arthashree Engine
                  |
       ┌──────────┼──────────┐
       v          v          v
     Risk      Portfolio   Monitoring
```

Use a fixed/static public IP for the order-execution host as required by
the current broker/exchange operating framework.

------------------------------------------------------------------------

# 46. CLOUD DEPLOYMENT

Do not deploy live execution on:

``` text
AWS Lambda
random serverless function
changing residential IP
laptop hotspot
```

unless the architecture demonstrably satisfies the current
broker/exchange requirements.

Prefer:

``` text
VM
+
static public IP
+
Docker
+
persistent process
+
monitoring
```

For example:

``` text
AWS EC2
Elastic/static public IP
Docker
PostgreSQL
Redis optional
Prometheus/Grafana optional
```

But the choice of cloud provider is not mandatory.

------------------------------------------------------------------------

# 47. DOCKER

Target:

``` text
docker compose up -d
```

Services:

``` text
arthashree-engine
postgres
redis        # optional
prometheus   # optional
grafana      # optional
```

Do not expose the database publicly.

------------------------------------------------------------------------

# 48. MONITORING

Monitor:

``` text
engine heartbeat
Kite connection
WebSocket connection
last market tick
order latency
order rejects
order fills
position mismatch
cash mismatch
daily P&L
drawdown
risk utilization
CPU
RAM
disk
network
```

If the engine loses market data:

``` text
STOP NEW ORDERS
```

If broker reconciliation fails:

``` text
STOP NEW ORDERS
```

If position mismatch occurs:

``` text
STOP NEW ORDERS
```

If risk state is unknown:

``` text
STOP NEW ORDERS
```

------------------------------------------------------------------------

# 49. KILL SWITCH

Arthashree must have:

``` text
global_kill_switch
```

The kill switch must:

1.  stop new order submissions;
2.  cancel eligible pending orders according to configured policy;
3.  record the reason;
4.  notify the operator;
5.  preserve logs;
6.  require explicit recovery.

Do not automatically restart trading after an unknown state.

------------------------------------------------------------------------

# 50. POSITION RECONCILIATION

At startup and periodically:

``` text
strategy positions
        vs
broker positions
```

must match.

If:

``` text
strategy_qty != broker_qty
```

then:

``` text
TRADING HALT
```

The system must not blindly trade its way back to the expected position.

------------------------------------------------------------------------

# 51. DAILY STARTUP CHECKLIST

Before market:

``` text
[ ] server healthy
[ ] static IP correct
[ ] Kite authentication valid
[ ] instrument master current
[ ] market calendar loaded
[ ] strategy version approved
[ ] configuration hash verified
[ ] data feed connected
[ ] account funds available
[ ] broker positions reconciled
[ ] no unexpected open orders
[ ] risk limits loaded
[ ] daily loss reset correctly
[ ] kill switch operational
[ ] monitoring operational
```

Only then:

``` text
READY_FOR_TRADING
```

------------------------------------------------------------------------

# 52. DAILY SHUTDOWN CHECKLIST

After market:

``` text
[ ] all orders reconciled
[ ] all fills downloaded
[ ] positions reconciled
[ ] P&L reconciled
[ ] transaction costs recorded
[ ] strategy logs archived
[ ] errors reviewed
[ ] data stored
[ ] experiment/run ID stored
```

------------------------------------------------------------------------

# 53. GO-LIVE GATES

Arthashree can move from paper to live only when:

``` text
GATE 1  Data quality                    PASS
GATE 2  Look-ahead tests                PASS
GATE 3  Backtest                        PASS
GATE 4  Out-of-sample                  PASS
GATE 5  Walk-forward                   PASS
GATE 6  Monte Carlo                    PASS
GATE 7  Cost sensitivity               PASS
GATE 8  Stress testing                 PASS
GATE 9  Paper trading                  PASS
GATE 10 Broker reconciliation           PASS
GATE 11 Static IP / API compliance      PASS
GATE 12 Risk controls                   PASS
GATE 13 Monitoring                      PASS
GATE 14 Kill switch                    PASS
GATE 15 Disaster recovery               PASS
```

If one gate fails:

``` text
NO LIVE TRADING
```

------------------------------------------------------------------------

# 54. FIRST LIVE DEPLOYMENT

Do NOT start with the full capital allocation.

Use a controlled deployment:

``` text
Phase 1:
minimum practical size

Phase 2:
stable paper/live comparison

Phase 3:
small capital

Phase 4:
increase only after predefined evidence
```

The increase must be rule-based, not emotional.

------------------------------------------------------------------------

# 55. STRATEGY VERSIONING

Every live order must contain internally:

``` text
strategy_name
strategy_version
config_version
git_commit
experiment_id
```

Example:

``` text
strategy_name = triple_screen_trend_pullback
strategy_version = 0.1.3
git_commit = abc1234
experiment_id = EXP-2026-0017
```

Do not modify strategy logic during a live trading session.

------------------------------------------------------------------------

# 56. CHANGE MANAGEMENT

Any change to:

``` text
signal
stop
target
position sizing
risk limit
instrument universe
execution logic
cost model
```

must create a new strategy/config version.

Example:

``` text
v0.1.0
v0.1.1
v0.2.0
```

Run the complete validation pipeline again.

------------------------------------------------------------------------

# 57. RESEARCH LOOP

Claude should repeatedly execute:

``` text
HYPOTHESIS
   ↓
IMPLEMENT
   ↓
UNIT TEST
   ↓
DATA TEST
   ↓
BACKTEST
   ↓
OUT-OF-SAMPLE
   ↓
WALK-FORWARD
   ↓
ROBUSTNESS
   ↓
PAPER
   ↓
REVIEW
   ↓
NEXT HYPOTHESIS
```

Not:

``` text
indicator
→ backtest
→ profit
→ live
```

------------------------------------------------------------------------

# 58. AI ROLE IN ARTHASHREE

AI should initially be used for:

``` text
research
feature discovery
code generation
test generation
data-quality analysis
regime classification
experiment analysis
anomaly detection
strategy comparison
documentation
```

AI should NOT directly override:

``` text
risk limits
position limits
kill switch
broker constraints
exchange rules
```

An AI-generated signal must pass the deterministic risk engine.

------------------------------------------------------------------------

# 59. PROBABILISTIC SIGNAL INTERFACE

Eventually strategies should return:

``` json
{
  "instrument": "NSE:INFY",
  "direction": "LONG",
  "probability": 0.61,
  "expected_return": 0.012,
  "expected_volatility": 0.018,
  "confidence": 0.72,
  "strategy_version": "0.2.0"
}
```

But probability values must be calibrated from historical data.

Never treat:

``` text
0.61
```

as a literal 61% future certainty unless calibration evidence supports
it.

------------------------------------------------------------------------

# 60. PORTFOLIO-LEVEL AI

Future Arthashree versions can combine:

``` text
technical signals
+
market regime
+
volatility
+
cross-sectional momentum
+
liquidity
+
macro features
+
options positioning
+
news/sentiment
```

But each addition requires:

``` text
data availability check
+
timestamp alignment
+
leakage test
+
incremental value test
```

------------------------------------------------------------------------

# 61. FEATURE LEAKAGE CHECK

Every feature must have:

``` text
feature_timestamp
information_available_timestamp
decision_timestamp
```

Requirement:

``` text
information_available_timestamp <= decision_timestamp
```

If not:

``` text
REJECT FEATURE
```

------------------------------------------------------------------------

# 62. DATA TIMESTAMP RULE

For an intraday strategy:

``` text
09:30 decision
```

must not use:

``` text
09:31 data
```

For daily strategy:

``` text
today's completed daily candle
```

may only be used if the decision happens after that candle is complete.

If trading at today's open:

``` text
today's close
```

is unavailable and must not be used.

------------------------------------------------------------------------

# 63. CURRENT ARTHASHREE V0.1 PACKAGE

The existing first implementation contains:

``` text
data loading
feature calculations
EMA
ATR
RSI
MACD
weekly trend filter
signal generation
position sizing
stop/target
slippage
commission
backtest
chronological validation
metrics
tests
```

The initial automated test suite passed:

``` text
4 tests passed
```

The synthetic demonstration produced zero trades and therefore provides
no evidence of profitability.

This is acceptable.

The next priority is real data.

------------------------------------------------------------------------

# 64. WHAT CLAUDE MUST BUILD NEXT

Priority 1:

``` text
NSE/Kite data ingestion
```

Priority 2:

``` text
instrument master
```

Priority 3:

``` text
point-in-time universe
```

Priority 4:

``` text
corporate-action pipeline
```

Priority 5:

``` text
real transaction-cost engine
```

Priority 6:

``` text
walk-forward engine
```

Priority 7:

``` text
Monte Carlo + robustness
```

Priority 8:

``` text
paper trading
```

Priority 9:

``` text
Kite authentication service
```

Priority 10:

``` text
Kite WebSocket
```

Priority 11:

``` text
Kite order adapter
```

Priority 12:

``` text
reconciliation
```

Priority 13:

``` text
static-IP deployment
```

Priority 14:

``` text
monitoring
```

Priority 15:

``` text
controlled live gate
```

------------------------------------------------------------------------

# 65. IMPORTANT: NO FAKE BACKTEST

Claude must never generate a statement such as:

``` text
Arthashree made 37% CAGR
```

unless the report clearly identifies:

``` text
dataset
date range
universe
strategy version
cost model
slippage model
train/test methodology
number of trades
out-of-sample result
```

The report must also say whether the result is:

``` text
IN-SAMPLE
OUT-OF-SAMPLE
WALK-FORWARD
PAPER
LIVE
```

------------------------------------------------------------------------

# 66. REQUIRED BACKTEST REPORT FORMAT

``` text
ARTHASHREE STRATEGY REPORT

Strategy:
Version:
Dataset:
Universe:
Period:

Train:
Validation:
Test:

Initial capital:
Final capital:
CAGR:
Max drawdown:
Sharpe:
Sortino:
Profit factor:
Win rate:
Expectancy:
Trades:

Gross P&L:
Commission:
Exchange charges:
Taxes:
Slippage:
Net P&L:

Walk-forward:
Monte Carlo:
Robustness:

Look-ahead test:
PASS/FAIL

Data quality:
PASS/FAIL

Decision:
RESEARCH ONLY / PAPER APPROVED / LIVE APPROVED
```

------------------------------------------------------------------------

# 67. BROKER FAILURE HANDLING

If Kite returns:

``` text
403
```

treat it as session/authentication failure and require
re-authentication.

If:

``` text
429
```

apply backoff/rate limiting.

If:

``` text
500/502/503/504
```

do not blindly retry order submission without reconciliation.

For order requests:

``` text
unknown outcome
```

must be treated as:

``` text
POTENTIAL ORDER EXISTS
```

Then query order state before retrying.

This prevents duplicate orders.

------------------------------------------------------------------------

# 68. ORDER IDEMPOTENCY

Before retrying an uncertain order:

``` text
check client-side order intent ID
check broker order book
check matching symbol
check transaction type
check quantity
check timestamp
```

Only retry when it is safe.

Never:

``` text
network error
→ send order again
```

without reconciliation.

------------------------------------------------------------------------

# 69. LOGGING

Every decision should log:

``` text
timestamp
instrument
strategy_version
features used
signal
probability
entry
stop
target
quantity
risk
portfolio exposure
decision
reason
```

For live:

``` text
order_id
broker response
fill
average price
status
```

Never log:

``` text
api_secret
access_token
password
TOTP
```

------------------------------------------------------------------------

# 70. AUDIT TRAIL

Use append-only event records:

``` text
SIGNAL_CREATED
RISK_APPROVED
RISK_REJECTED
ORDER_SUBMITTED
ORDER_ACK
ORDER_REJECTED
ORDER_PARTIAL_FILL
ORDER_FILLED
ORDER_CANCELLED
POSITION_UPDATED
KILL_SWITCH
SYSTEM_ERROR
```

Each event should include:

``` text
event_id
timestamp
run_id
strategy_version
git_commit
instrument
payload_hash
```

------------------------------------------------------------------------

# 71. RECOVERY

On restart:

``` text
load last system state
↓
connect Kite
↓
download current orders
↓
download current trades
↓
download positions
↓
reconcile
↓
verify risk
↓
only then resume
```

Never assume the process state before a crash is correct.

------------------------------------------------------------------------

# 72. FINAL AGENT PROMPT

Copy this prompt into Claude Code after placing this document in the
repository.

``` text
You are the lead engineering agent for Arthashree.

Read these files first:

1. CLAUDE.md
2. ARTHASHREE_NSE_ZERODHA_AGENT.md
3. README.md
4. existing source code
5. existing tests

Your job is to build Arthashree from research/backtest to paper trading and eventually controlled live execution through Zerodha Kite Connect for NSE.

The uploaded Trading in the Zone and Trading for a Living material is conceptual source material. Translate its principles into machine-enforceable engineering controls. Do not reproduce the books and do not claim that either book proves a profitable strategy.

Operating rules:

- Never claim profitability without out-of-sample evidence.
- Never use future information.
- Never use synthetic data as real performance evidence.
- Never hide failed tests.
- Never invent NSE or Zerodha API behaviour.
- Verify current official NSE/Zerodha documentation before implementing uncertain broker/exchange behaviour.
- Never expose API secrets.
- Never enable live trading automatically.
- Never bypass risk controls.
- Never use martingale sizing.
- Never average down by default.
- Treat broker order acknowledgement as different from execution.
- Reconcile orders and positions.
- Include realistic transaction costs and slippage.
- Keep backtest, paper and live execution behind the same ExecutionBroker interface.
- Live mode must default to disabled.

Build in this order:

PHASE 1 — Repository audit
- inspect code
- inspect tests
- inspect Python environment
- inspect git status
- create implementation plan

PHASE 2 — Data
- implement Kite instrument master
- implement NSE historical-data ingestion adapters
- implement Kite historical candle downloader
- implement schema validation
- implement timestamp validation
- implement duplicate detection
- implement corporate-action handling
- implement point-in-time universe support
- store raw and normalized data separately

PHASE 3 — Research
- implement EMA, ATR, RSI, MACD and other features as independent tested modules
- implement triple_screen_trend_pullback
- ensure no look-ahead
- implement configurable strategy registry

PHASE 4 — Backtest
- next-bar execution where appropriate
- realistic slippage
- commissions and regulatory costs
- position sizing
- stop/target logic
- partial-fill-aware execution abstraction
- portfolio accounting
- performance reports

PHASE 5 — Validation
- chronological train/validation/test
- walk-forward
- Monte Carlo
- parameter perturbation
- cost sensitivity
- slippage sensitivity
- regime analysis
- leakage tests

PHASE 6 — Paper
- live Kite market data
- internal paper execution
- simulated fills
- paper portfolio
- reconciliation
- monitoring

PHASE 7 — Broker
- implement secure Kite authentication
- implement token lifecycle
- implement WebSocket
- implement order adapter
- implement order-state reconciliation
- implement kill switch
- implement static-IP deployment configuration
- enforce broker/exchange rate limits
- enforce permitted order types

PHASE 8 — Deployment
- Docker
- static-IP server
- health checks
- monitoring
- audit trail
- startup reconciliation
- shutdown reconciliation
- disaster recovery

PHASE 9 — Live gate
Only after all validation gates pass:
- require explicit LIVE_TRADING_ENABLED=true
- require approved strategy version
- require approved config hash
- require data health
- require broker health
- require position reconciliation
- require risk health
- require static-IP/API compliance
- require monitoring
- require kill switch

For every coding iteration:

1. State what you will change.
2. Make the smallest correct change.
3. Add tests.
4. Run tests.
5. Show exact commands.
6. Report failures honestly.
7. Do not rewrite unrelated working code.
8. Record the next task.

At the end of each phase produce a report containing:

- implementation completed
- files changed
- tests run
- test result
- data assumptions
- broker assumptions
- known limitations
- security concerns
- next step

Do not move to live deployment because a backtest looks profitable.
Move only when the complete validation and operational gates pass.
```

------------------------------------------------------------------------

# 73. OFFICIAL REFERENCE LINKS

## NSE

Historical reports:

https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives

Derivatives reports:

https://www.nseindia.com/all-reports-derivatives

NSE data policy:

https://www.nseindia.com/static/market-data/nse-data-policy

NSE Data & Analytics:

https://www.nseindia.com/static/nse-data-and-analytics/data-information-vending

NSE retail algo FAQ:

https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf

## Zerodha / Kite

Kite Connect:

https://kite.trade/docs/connect/v3/

Authentication:

https://kite.trade/docs/connect/v3/user/

Historical candles:

https://kite.trade/docs/connect/v3/historical/

Orders:

https://kite.trade/docs/connect/v3/orders/

WebSocket:

https://kite.trade/docs/connect/v3/websocket/

Exceptions/rate limits:

https://kite.trade/docs/connect/v3/exceptions/

Official agent setup:

https://kite.trade/docs/connect/v3/agent-setup/

Zerodha API:

https://zerodha.com/products/api/

Kite Connect signup:

https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/how-do-i-sign-up-for-kite-connect

Kite Connect pricing:

https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis

Developer console:

https://developers.kite.trade/

------------------------------------------------------------------------

# 74. FINAL IMPLEMENTATION PRINCIPLE

Arthashree is not:

``` text
AI predicts price
→ buy
→ profit
```

Arthashree is:

``` text
DATA
 ↓
VALIDATION
 ↓
FEATURES
 ↓
PROBABILISTIC EDGE
 ↓
RISK
 ↓
PORTFOLIO
 ↓
EXECUTION
 ↓
VALIDATION
 ↓
PAPER
 ↓
CONTROLLED LIVE
 ↓
CONTINUOUS MONITORING
```

The objective is not to build the most complicated trading AI.

The objective is to build a system where:

``` text
every assumption is testable
every trade is explainable
every risk is bounded
every result is reproducible
every order is auditable
every failure is detectable
```

That is the engineering standard for Arthashree.
