# Hyperliquid Plugin Documentation

## Overview

The Hyperliquid plugin provides integration with the Hyperliquid perpetual DEX protocol, allowing you to interact with perpetual futures markets on the Arbitrum network. This plugin enables market data retrieval, order management, and account operations.

## Features

- Real-time market data access
- Order placement and management
- Account information and position tracking
- Support for all available trading pairs
- Testnet and mainnet support

## Installation

The Hyperliquid plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.hyperliquid import HyperliquidPlugin

# Initialize the plugin
plugin = HyperliquidPlugin()

# Optional: Configure for testnet
plugin.use_testnet = True
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Optional: Use testnet instead of mainnet
HYPERLIQUID_USE_TESTNET=true

# Required for trading operations
HYPERLIQUID_PRIVATE_KEY=your_private_key
```

## Market Data Operations

### Getting All Markets

Retrieve information about all available markets:

```python
markets = await plugin.get_markets()
```

Response structure:
```python
[
    {
        "coin": "BTC",
        "price": Decimal("50000.00"),
        "index_price": Decimal("50005.00"),
        "mark_price": Decimal("50002.50"),
        "open_interest": Decimal("100.50"),
        "funding_rate": Decimal("0.0001"),
        "volume_24h": Decimal("1000.00")
    },
    # ... other markets
]
```

### Getting Market Summary

Get detailed information about a specific market:

```python
summary = await plugin.get_market_summary("BTC")
```

Response structure:
```python
{
    "price": Decimal("50000.00"),
    "index_price": Decimal("50005.00"),
    "mark_price": Decimal("50002.50"),
    "open_interest": Decimal("100.50"),
    "funding_rate": Decimal("0.0001"),
    "volume_24h": Decimal("1000.00")
}
```

### Getting Orderbook

Retrieve the current orderbook for a market:

```python
orderbook = await plugin.get_orderbook("BTC")
```

Response structure:
```python
{
    "bids": [
        {"price": Decimal("49995.00"), "size": Decimal("1.5"), "count": 3},
        # ... more bids
    ],
    "asks": [
        {"price": Decimal("50005.00"), "size": Decimal("2.0"), "count": 2},
        # ... more asks
    ]
}
```

### Getting Recent Trades

Fetch recent trades for a market:

```python
trades = await plugin.get_recent_trades("BTC")
```

Response structure:
```python
[
    {
        "price": Decimal("50000.00"),
        "size": Decimal("0.1"),
        "side": "buy",
        "timestamp": 1639123456789,
        "hash": "0x123..."
    },
    # ... more trades
]
```

## Trading Operations

### Placing Orders

Place a new order:

```python
order = await plugin.place_order(
    market="BTC",
    side="buy",
    order_type="limit",
    size=Decimal("0.1"),
    price=Decimal("50000.00")
)
```

Available order types:
- `limit`: Standard limit order
- `market`: Market order
- `post_only`: Limit order that must be a maker
- `fill_or_kill`: Order must be filled completely or cancelled
- `immediate_or_cancel`: Order must be filled immediately (partial fills allowed)

### Cancelling Orders

Cancel a specific order:

```python
result = await plugin.cancel_order(order_id="123")
```

Cancel all orders for a market:

```python
result = await plugin.cancel_all_orders(market="BTC")
```

## Account Operations

### Getting Account Information

Retrieve account balances and positions:

```python
account = await plugin.get_account_info()
```

Response structure:
```python
{
    "collateral": Decimal("10000.00"),
    "positions": [
        {
            "market": "BTC",
            "size": Decimal("0.5"),
            "entry_price": Decimal("49000.00"),
            "liquidation_price": Decimal("45000.00"),
            "unrealized_pnl": Decimal("500.00")
        }
    ]
}
```

### Getting Open Orders

Fetch all open orders:

```python
orders = await plugin.get_open_orders()
```

Response structure:
```python
[
    {
        "id": "123",
        "market": "BTC",
        "side": "buy",
        "type": "limit",
        "size": Decimal("0.1"),
        "price": Decimal("50000.00"),
        "filled_size": Decimal("0.05"),
        "status": "open"
    }
]
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
from goat_sdk.plugins.hyperliquid.exceptions import (
    HyperliquidConnectionError,
    HyperliquidAuthenticationError,
    HyperliquidOrderError,
    HyperliquidValidationError
)

try:
    result = await plugin.place_order(...)
except HyperliquidOrderError as e:
    print(f"Order error: {e}")
except HyperliquidValidationError as e:
    print(f"Validation error: {e}")
except HyperliquidConnectionError as e:
    print(f"Connection error: {e}")
except HyperliquidAuthenticationError as e:
    print(f"Authentication error: {e}")
```

## Best Practices

1. **Connection Management**
   - Use the plugin within an async context manager
   - Handle connection errors appropriately
   - Implement reconnection logic for long-running applications

2. **Rate Limiting**
   - The plugin implements automatic rate limiting
   - Avoid excessive API calls
   - Use websocket connections for real-time data when possible

3. **Order Management**
   - Always verify order status after placement
   - Implement proper error handling
   - Use appropriate order types based on your needs

4. **Testing**
   - Use testnet for development and testing
   - Validate all operations before moving to mainnet
   - Implement proper logging for debugging

## Examples

### Basic Market Data Example

```python
async def get_market_info():
    plugin = HyperliquidPlugin(use_testnet=True)
    
    # Get all markets
    markets = await plugin.get_markets()
    
    # Get BTC market details
    btc_summary = await plugin.get_market_summary("BTC")
    
    # Get orderbook
    orderbook = await plugin.get_orderbook("BTC")
    
    # Get recent trades
    trades = await plugin.get_recent_trades("BTC")
    
    return {
        "markets": markets,
        "btc_summary": btc_summary,
        "orderbook": orderbook,
        "trades": trades
    }
```

### Basic Trading Example

```python
async def simple_trading():
    plugin = HyperliquidPlugin(
        private_key="your_private_key",
        use_testnet=True
    )
    
    # Place a limit order
    order = await plugin.place_order(
        market="BTC",
        side="buy",
        order_type="limit",
        size=Decimal("0.1"),
        price=Decimal("50000.00")
    )
    
    # Get order status
    status = await plugin.get_order_status(order["id"])
    
    # Cancel if not filled
    if status["status"] == "open":
        await plugin.cancel_order(order["id"])
    
    return status
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**
   - Verify network connectivity
   - Check if the API endpoint is accessible
   - Ensure SSL/TLS configuration is correct

2. **Authentication Errors**
   - Verify private key is correct
   - Check if the account has sufficient permissions
   - Ensure the API key is active

3. **Order Placement Failures**
   - Verify sufficient balance
   - Check order parameters
   - Ensure market is active and trading

4. **Rate Limiting**
   - Implement proper delays between requests
   - Use batch operations when possible
   - Monitor rate limit headers

## API Reference

For complete API documentation, see the [Hyperliquid API Reference](https://hyperliquid.gitbook.io/hyperliquid/). 