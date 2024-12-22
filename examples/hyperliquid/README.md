# Hyperliquid Examples

⚠️ **DISCLAIMER**: These examples are experimental and not meant for production use. They are provided for educational purposes only and are still under development. Use at your own risk.

## Examples Overview

1. `basic_operations.py`: Basic market operations (get markets, orderbook, etc.)
2. `trading_bot.py`: Simple trading bot with basic strategy
3. `ai_trading_agent.py`: Experimental AI-powered trading agent

## AI Trading Agent

The AI trading agent is an experimental feature that demonstrates how to:
- Use LangChain integration with GOAT SDK
- Process market data with AI
- Make trading decisions based on AI analysis
- Execute trades through Hyperliquid

### ⚠️ Important Notes

1. This is an experimental feature and should NOT be used with real funds
2. The AI agent's decisions are not financial advice
3. The implementation is basic and meant for demonstration only
4. Significant improvements would be needed for production use

## Running the Examples

1. Set up your environment:
```bash
export HYPERLIQUID_PRIVATE_KEY="your_private_key"
```

2. Install dependencies:
```bash
pip install "goat-sdk[hyperliquid]"
pip install langchain openai  # For AI agent example
```

3. Run an example:
```bash
python examples/hyperliquid/basic_operations.py
```

## Development Status

These examples are under active development and may change significantly. Features may be incomplete or require additional work. 