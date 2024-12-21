# Jupiter Plugin Documentation

## Overview

The Jupiter plugin provides seamless integration with Jupiter Aggregator, the leading liquidity aggregator on Solana. It enables optimal token swaps by aggregating liquidity from multiple DEXs, ensuring the best prices and execution for trades.

## Features

- Best price routing across multiple DEXs
- Smart order routing
- Price impact analysis
- Slippage protection
- Route simulation
- Quote comparison
- Gas optimization
- MEV protection
- Token validation
- Real-time price updates
- Transaction monitoring
- Error handling

## Installation

The Jupiter plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.jupiter import JupiterPlugin

# Initialize the plugin
plugin = JupiterPlugin(
    rpc_url="https://api.mainnet-beta.solana.com",
    commitment="confirmed"
)
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Required: Solana RPC endpoint
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Required for transactions
SOLANA_PRIVATE_KEY=your_private_key

# Optional: Configuration
SOLANA_COMMITMENT=confirmed
JUPITER_SLIPPAGE_BPS=50  # 0.5%
JUPITER_PRIORITY_FEE=1000  # lamports
```

## Trading Operations

### Getting a Quote

Get swap quotes with multiple route options:

```python
from goat_sdk.plugins.jupiter.parameters import QuoteParameters
from decimal import Decimal

params = QuoteParameters(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",   # SOL
    amount=Decimal("100.0"),
    slippage_bps=50,  # 0.5%
    only_direct_routes=False
)

routes = await plugin.get_quote(params)
```

Response structure:
```python
{
    "routes": [
        {
            "in_amount": Decimal("100.0"),
            "out_amount": Decimal("1.234"),
            "price_impact_pct": Decimal("0.1"),
            "market_impact_pct": Decimal("0.05"),
            "minimum_out_amount": Decimal("1.228"),
            "route_plan": [
                {
                    "protocol": "Orca",
                    "percent": 100,
                    "input_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                    "output_mint": "So11111111111111111111111111111111111111112"
                }
            ],
            "priority_fee": 1000,
            "time_taken": 0.123
        },
        # ... more routes
    ],
    "best_route_index": 0
}
```

### Executing a Swap

Execute a token swap using the best route:

```python
from goat_sdk.plugins.jupiter.parameters import SwapParameters

params = SwapParameters(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",   # SOL
    amount=Decimal("100.0"),
    slippage_bps=50,  # 0.5%
    route_index=0,  # Use best route
    priority_fee=1000
)

result = await plugin.swap_tokens(params)
```

Response structure:
```python
{
    "signature": "transaction_signature",
    "input_amount": Decimal("100.0"),
    "output_amount": Decimal("1.234"),
    "price_impact_pct": Decimal("0.1"),
    "fee": {
        "amount": Decimal("0.001"),
        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    }
}
```

### Getting Token Information

Get detailed token information:

```python
token_info = await plugin.get_token_info("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
```

Response structure:
```python
{
    "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "symbol": "USDC",
    "name": "USD Coin",
    "decimals": 6,
    "logo_uri": "https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
    "coingecko_id": "usd-coin",
    "price_usd": Decimal("1.0")
}
```

### Getting Market Information

Get market information for a token pair:

```python
market_info = await plugin.get_market_info(
    base_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    quote_mint="So11111111111111111111111111111111111111112"
)
```

Response structure:
```python
{
    "base_mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "quote_mint": "So11111111111111111111111111111111111111112",
    "liquidity_usd": Decimal("1000000.0"),
    "volume_24h": Decimal("5000000.0"),
    "price": Decimal("0.0123"),
    "price_change_24h": Decimal("-2.5"),
    "protocols": ["Orca", "Raydium", "Serum"]
}
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
try:
    result = await plugin.swap_tokens(params)
except JupiterQuoteError as e:
    print(f"Quote error: {e}")
except JupiterSwapError as e:
    print(f"Swap error: {e}")
except JupiterRouteError as e:
    print(f"Route error: {e}")
except JupiterPriceError as e:
    print(f"Price error: {e}")
```

## Best Practices

1. **Trading Safety**
   - Always use appropriate slippage tolerance
   - Monitor price impact
   - Verify token addresses
   - Use MEV protection

2. **Performance Optimization**
   - Use priority fees during high congestion
   - Monitor network conditions
   - Implement proper retries
   - Cache token information

3. **Error Handling**
   - Implement proper error recovery
   - Monitor transaction status
   - Handle network issues
   - Validate inputs thoroughly

4. **Security**
   - Verify token contracts
   - Use secure RPC endpoints
   - Monitor for suspicious activity
   - Implement proper error handling

## Examples

### Advanced Swap Example

```python
async def execute_optimized_swap():
    plugin = JupiterPlugin(...)
    
    # Get quotes for the swap
    quote_params = QuoteParameters(
        input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        output_mint="So11111111111111111111111111111111111111112",   # SOL
        amount=Decimal("100.0"),
        slippage_bps=50
    )
    
    quotes = await plugin.get_quote(quote_params)
    
    # Check price impact
    best_route = quotes["routes"][quotes["best_route_index"]]
    if best_route["price_impact_pct"] > Decimal("1.0"):
        raise Exception("Price impact too high")
    
    # Execute swap with the best route
    swap_params = SwapParameters(
        input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        output_mint="So11111111111111111111111111111111111111112",
        amount=Decimal("100.0"),
        slippage_bps=50,
        route_index=quotes["best_route_index"],
        priority_fee=1000
    )
    
    result = await plugin.swap_tokens(swap_params)
    return result
```

### Market Analysis Example

```python
async def analyze_market():
    plugin = JupiterPlugin(...)
    
    # Get token information
    usdc_info = await plugin.get_token_info(
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    )
    
    sol_info = await plugin.get_token_info(
        "So11111111111111111111111111111111111111112"
    )
    
    # Get market information
    market_info = await plugin.get_market_info(
        base_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        quote_mint="So11111111111111111111111111111111111111112"
    )
    
    # Get quotes for different amounts
    amounts = [Decimal("100.0"), Decimal("1000.0"), Decimal("10000.0")]
    quotes = []
    
    for amount in amounts:
        quote_params = QuoteParameters(
            input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            output_mint="So11111111111111111111111111111111111111112",
            amount=amount,
            slippage_bps=50
        )
        quotes.append(await plugin.get_quote(quote_params))
    
    return {
        "tokens": {
            "usdc": usdc_info,
            "sol": sol_info
        },
        "market": market_info,
        "quotes": quotes
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Quote Issues**
   - Verify token addresses
   - Check token balances
   - Monitor network status
   - Handle rate limits

2. **Swap Issues**
   - Verify account balances
   - Check slippage settings
   - Monitor transaction status
   - Handle failed transactions

3. **Route Issues**
   - Check liquidity availability
   - Monitor price impact
   - Verify route validity
   - Handle timeout errors

4. **Network Issues**
   - Use reliable RPC endpoints
   - Monitor network congestion
   - Handle transaction timeouts
   - Implement proper retries

## API Reference

For complete API documentation, see:
- [Jupiter API Documentation](https://docs.jup.ag/) 