# Uniswap Plugin Documentation

## Overview

The Uniswap plugin provides comprehensive integration with Uniswap V2 and V3 protocols, enabling advanced trading, liquidity provision, and analytics. This plugin includes features for optimal routing, MEV protection, position management, and detailed analytics.

## Features

- Support for both Uniswap V2 and V3
- Advanced routing optimization
- MEV protection
- Gas optimization
- Position management
- Liquidity provision
- Fee collection
- Price analytics
- Multi-hop routing
- Slippage protection
- Pool analytics
- Token information

## Installation

The Uniswap plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.uniswap import UniswapPlugin, UniswapVersion

# Initialize for V3
plugin = UniswapPlugin(
    version=UniswapVersion.V3,
    router_address="0x...",
    factory_address="0x...",
    quoter_address="0x...",  # Required for V3
    position_manager_address="0x..."  # Required for V3
)

# Initialize for V2
plugin = UniswapPlugin(
    version=UniswapVersion.V2,
    router_address="0x...",
    factory_address="0x..."
)
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Required: Ethereum RPC endpoint
ETH_RPC_URL=https://mainnet.infura.io/v3/your-project-id

# Required for transactions
ETH_PRIVATE_KEY=your_private_key

# Optional: Gas price settings
GAS_PRICE_MULTIPLIER=1.1
MAX_GAS_PRICE=100  # in gwei
```

## Trading Operations

### Executing a Swap

Execute a token swap with advanced features:

```python
from goat_sdk.plugins.uniswap.parameters import SwapParameters
from decimal import Decimal

params = SwapParameters(
    token_in="0x...",  # Input token address
    token_out="0x...",  # Output token address
    amount_in=Decimal("1.0"),
    slippage_tolerance=Decimal("0.005"),  # 0.5%
    recipient="0x...",  # Optional recipient
    deadline_minutes=20,
    ensure_sufficient_allowance=True
)

tx_hash = await plugin.swap_tokens(params)
```

### Getting a Quote

Get detailed swap quotes with multiple route options:

```python
from goat_sdk.plugins.uniswap.parameters import QuoteParameters

params = QuoteParameters(
    token_in="0x...",
    token_out="0x...",
    amount_in=Decimal("1.0"),
    slippage_tolerance=Decimal("0.005")
)

routes = await plugin.quote_swap(params)
```

Response structure:
```python
[
    {
        "path": ["0x...", "0x..."],  # Token addresses in order
        "pools": ["0x..."],  # Pool addresses
        "fees": [PoolFee.MEDIUM],  # Fee tiers for V3
        "input_amount": Decimal("1.0"),
        "output_amount": Decimal("1234.56"),
        "price_impact": Decimal("0.001"),
        "minimum_output": Decimal("1228.38"),
        "gas_estimate": 150000
    },
    # ... more routes
]
```

## Liquidity Operations

### Adding Liquidity

Add liquidity to a pool with position optimization:

```python
from goat_sdk.plugins.uniswap.parameters import AddLiquidityParameters

params = AddLiquidityParameters(
    token0="0x...",
    token1="0x...",
    amount0=Decimal("1.0"),
    amount1=Decimal("1000.0"),
    fee_tier=PoolFee.MEDIUM,  # For V3
    tick_lower=None,  # Optional for V3
    tick_upper=None,  # Optional for V3
    ensure_sufficient_allowance=True
)

tx_hash = await plugin.add_liquidity(params)
```

### Removing Liquidity

Remove liquidity from a pool:

```python
from goat_sdk.plugins.uniswap.parameters import RemoveLiquidityParameters

params = RemoveLiquidityParameters(
    token0="0x...",
    token1="0x...",
    liquidity_percentage=Decimal("100.0"),  # Full withdrawal
    position_id=123,  # For V3
    recipient="0x..."  # Optional
)

tx_hash = await plugin.remove_liquidity(params)
```

### Collecting Fees

Collect accumulated fees from a V3 position:

```python
from goat_sdk.plugins.uniswap.parameters import CollectFeesParameters

params = CollectFeesParameters(
    position_id=123,
    recipient="0x...",  # Optional
    auto_compound=True  # Optional
)

fees = await plugin.collect_fees(params)
```

Response structure:
```python
{
    "token0": Decimal("0.1"),  # Amount of token0 collected
    "token1": Decimal("100.0")  # Amount of token1 collected
}
```

## Position Management

### Getting Position Information

Get detailed position information:

```python
from goat_sdk.plugins.uniswap.parameters import PositionParameters

params = PositionParameters(
    position_ids=[123, 456],  # Optional specific positions
    owner="0x..."  # Optional owner filter
)

positions = await plugin.get_positions(params)
```

Response structure:
```python
[
    {
        "token_id": 123,  # For V3 NFT positions
        "owner": "0x...",
        "pool": {
            "address": "0x...",
            "token0": {...},
            "token1": {...},
            "fee": PoolFee.MEDIUM,
            "liquidity": Decimal("1000000.0"),
            "token0_price": Decimal("1.0"),
            "token1_price": Decimal("1000.0")
        },
        "liquidity": Decimal("10000.0"),
        "token0_amount": Decimal("1.0"),
        "token1_amount": Decimal("1000.0"),
        "fee_tier": PoolFee.MEDIUM,
        "lower_tick": -100,  # For V3
        "upper_tick": 100,   # For V3
        "unclaimed_fees": {
            "token0": Decimal("0.1"),
            "token1": Decimal("100.0")
        }
    },
    # ... more positions
]
```

## Pool Operations

### Getting Pool Information

Get detailed pool information with analytics:

```python
pool_info = await plugin.get_pool_info(
    token0="0x...",
    token1="0x...",
    fee=PoolFee.MEDIUM
)
```

Response structure:
```python
{
    "address": "0x...",
    "token0": {
        "address": "0x...",
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "chain_id": 1,
        "price_usd": Decimal("1.0")
    },
    "token1": {
        "address": "0x...",
        "symbol": "WETH",
        "name": "Wrapped Ether",
        "decimals": 18,
        "chain_id": 1,
        "price_usd": Decimal("1800.0")
    },
    "fee": PoolFee.MEDIUM,
    "liquidity": Decimal("1000000.0"),
    "token0_price": Decimal("1.0"),
    "token1_price": Decimal("1800.0"),
    "sqrt_price_x96": 123456789,  # V3 only
    "tick": 123456,  # V3 only
    "tvl_usd": Decimal("1000000.0")
}
```

### Getting Token Information

Get detailed token information:

```python
token_info = await plugin.get_token_info("0x...")
```

Response structure:
```python
{
    "address": "0x...",
    "symbol": "USDC",
    "name": "USD Coin",
    "decimals": 6,
    "chain_id": 1,
    "logo_uri": "https://...",
    "price_usd": Decimal("1.0"),
    "verified": True
}
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
try:
    result = await plugin.swap_tokens(params)
except ContractCallError as e:
    print(f"Contract call failed: {e}")
except ContractValidationError as e:
    print(f"Validation failed: {e}")
except ContractExecutionError as e:
    print(f"Execution failed: {e}")
except ContractABIError as e:
    print(f"ABI error: {e}")
```

## Best Practices

1. **Trading Safety**
   - Always use appropriate slippage tolerance
   - Monitor price impact
   - Verify token addresses
   - Use MEV protection

2. **Gas Optimization**
   - Monitor gas prices
   - Use appropriate fee tiers
   - Batch operations when possible
   - Consider transaction timing

3. **Position Management**
   - Monitor position health
   - Collect fees regularly
   - Adjust ranges based on volatility
   - Consider impermanent loss

4. **Security**
   - Verify token contracts
   - Use secure RPC endpoints
   - Monitor for suspicious activity
   - Implement proper error handling

## Examples

### Advanced Swap Example

```python
async def execute_optimized_swap():
    plugin = UniswapPlugin(...)
    
    # Get quotes for multiple routes
    quote_params = QuoteParameters(
        token_in="0x...",
        token_out="0x...",
        amount_in=Decimal("1.0"),
        slippage_tolerance=Decimal("0.005")
    )
    
    routes = await plugin.quote_swap(quote_params)
    
    # Select best route
    best_route = routes[0]  # Routes are sorted by output amount
    
    # Execute swap
    swap_params = SwapParameters(
        token_in=best_route.path[0],
        token_out=best_route.path[-1],
        amount_in=best_route.input_amount,
        slippage_tolerance=Decimal("0.005"),
        ensure_sufficient_allowance=True
    )
    
    tx_hash = await plugin.swap_tokens(swap_params)
    return tx_hash
```

### Liquidity Management Example

```python
async def manage_liquidity_position():
    plugin = UniswapPlugin(...)
    
    # Add liquidity
    add_params = AddLiquidityParameters(
        token0="0x...",
        token1="0x...",
        amount0=Decimal("1.0"),
        amount1=Decimal("1000.0"),
        fee_tier=PoolFee.MEDIUM
    )
    
    position_tx = await plugin.add_liquidity(add_params)
    
    # Monitor position
    position_params = PositionParameters(owner="your_address")
    positions = await plugin.get_positions(position_params)
    
    # Collect fees if available
    for position in positions:
        if position.unclaimed_fees:
            collect_params = CollectFeesParameters(
                position_id=position.token_id,
                auto_compound=True
            )
            fees = await plugin.collect_fees(collect_params)
    
    return {
        "position_tx": position_tx,
        "positions": positions,
        "fees": fees
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Swap Issues**
   - Verify token allowance
   - Check slippage settings
   - Monitor gas prices
   - Handle failed transactions

2. **Liquidity Issues**
   - Verify token balances
   - Check price ranges
   - Monitor pool conditions
   - Handle position limits

3. **Fee Collection**
   - Verify position ownership
   - Check fee accumulation
   - Monitor gas costs
   - Handle collection timing

4. **Network Issues**
   - Use reliable RPC endpoints
   - Monitor network status
   - Handle transaction timeouts
   - Implement proper retries

## API Reference

For complete API documentation, see:
- [Uniswap V2 Documentation](https://docs.uniswap.org/protocol/V2/introduction)
- [Uniswap V3 Documentation](https://docs.uniswap.org/protocol/introduction)
