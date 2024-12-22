# ERC20 Plugin Documentation

## Overview

The ERC20 plugin provides a standardized interface for interacting with ERC20 tokens on Ethereum and EVM-compatible networks. This plugin enables token transfers, allowance management, and balance queries across multiple chains.

## Features

- Token balance queries
- Token transfers and approvals
- Allowance management
- Multi-chain support (Ethereum, Arbitrum, Polygon, etc.)
- Gas estimation and optimization
- Event monitoring (transfers, approvals)

## Installation

The ERC20 plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.erc20 import ERC20Plugin

# Initialize the plugin
plugin = ERC20Plugin(
    rpc_url="https://mainnet.infura.io/v3/your-project-id",
    chain_id=1  # Ethereum mainnet
)

# Optional: Configure for other networks
arbitrum_plugin = ERC20Plugin(
    rpc_url="https://arb1.arbitrum.io/rpc",
    chain_id=42161  # Arbitrum One
)
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Required: RPC endpoint
ERC20_RPC_URL=https://mainnet.infura.io/v3/your-project-id

# Optional: Chain ID (defaults to 1 for Ethereum mainnet)
ERC20_CHAIN_ID=1

# Required for transactions
ERC20_PRIVATE_KEY=your_private_key
```

## Token Operations

### Getting Token Information

Retrieve basic information about an ERC20 token:

```python
info = await plugin.get_token_info("0x123...")  # token address
```

Response structure:
```python
{
    "name": "USD Coin",
    "symbol": "USDC",
    "decimals": 6,
    "total_supply": Decimal("1000000000.000000"),
    "contract_address": "0x123..."
}
```

### Getting Token Balance

Check token balance for an address:

```python
balance = await plugin.get_balance(
    token_address="0x123...",
    wallet_address="0x456..."
)
```

Response structure:
```python
{
    "balance": Decimal("100.000000"),
    "raw_balance": 100000000,  # Raw value from contract
    "decimals": 6
}
```

### Getting Token Allowance

Check token allowance for a spender:

```python
allowance = await plugin.get_allowance(
    token_address="0x123...",
    owner_address="0x456...",
    spender_address="0x789..."
)
```

Response structure:
```python
{
    "allowance": Decimal("50.000000"),
    "raw_allowance": 50000000,  # Raw value from contract
    "decimals": 6
}
```

## Transaction Operations

### Token Transfer

Transfer tokens to another address:

```python
tx = await plugin.transfer(
    token_address="0x123...",
    to_address="0x456...",
    amount=Decimal("10.5"),
    gas_limit=100000,  # Optional
    gas_price=None,  # Optional, will use network default
    max_priority_fee=None  # Optional, for EIP-1559
)
```

Response structure:
```python
{
    "tx_hash": "0xabc...",
    "from_address": "0x789...",
    "to_address": "0x456...",
    "amount": Decimal("10.5"),
    "gas_used": 65000,
    "gas_price": 50000000000,
    "status": "success"
}
```

### Approve Spender

Approve an address to spend tokens:

```python
tx = await plugin.approve(
    token_address="0x123...",
    spender_address="0x456...",
    amount=Decimal("100.0"),
    gas_limit=60000  # Optional
)
```

Response structure:
```python
{
    "tx_hash": "0xdef...",
    "spender": "0x456...",
    "amount": Decimal("100.0"),
    "gas_used": 45000,
    "gas_price": 50000000000,
    "status": "success"
}
```

### Transfer From

Transfer tokens using an allowance:

```python
tx = await plugin.transfer_from(
    token_address="0x123...",
    from_address="0x456...",
    to_address="0x789...",
    amount=Decimal("5.0"),
    gas_limit=120000  # Optional
)
```

## Event Monitoring

### Monitoring Transfers

Listen for transfer events:

```python
async def handle_transfer(event):
    print(f"Transfer: {event['from']} -> {event['to']}: {event['amount']}")

await plugin.monitor_transfers(
    token_address="0x123...",
    callback=handle_transfer,
    from_block="latest"
)
```

### Monitoring Approvals

Listen for approval events:

```python
async def handle_approval(event):
    print(f"Approval: {event['owner']} -> {event['spender']}: {event['amount']}")

await plugin.monitor_approvals(
    token_address="0x123...",
    callback=handle_approval,
    from_block="latest"
)
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
from goat_sdk.plugins.erc20.exceptions import (
    ERC20ConnectionError,
    ERC20ContractError,
    ERC20InsufficientBalanceError,
    ERC20InsufficientAllowanceError,
    ERC20TransactionError
)

try:
    result = await plugin.transfer(...)
except ERC20InsufficientBalanceError as e:
    print(f"Insufficient balance: {e}")
except ERC20TransactionError as e:
    print(f"Transaction failed: {e}")
except ERC20ConnectionError as e:
    print(f"Connection error: {e}")
```

## Best Practices

1. **Gas Management**
   - Always estimate gas before transactions
   - Consider using EIP-1559 for better gas pricing
   - Monitor gas prices for optimal timing

2. **Security**
   - Never expose private keys
   - Verify token contracts before interaction
   - Use appropriate allowance amounts

3. **Transaction Management**
   - Always wait for transaction confirmations
   - Implement proper error handling
   - Monitor transaction status

4. **Network Selection**
   - Use appropriate RPC endpoints
   - Consider network congestion
   - Verify chain ID configuration

## Examples

### Basic Token Operations Example

```python
async def token_operations():
    plugin = ERC20Plugin(rpc_url="your_rpc_url")
    
    # Get token info
    token = await plugin.get_token_info("0x123...")
    
    # Check balance
    balance = await plugin.get_balance(
        token_address="0x123...",
        wallet_address="0x456..."
    )
    
    # Check allowance
    allowance = await plugin.get_allowance(
        token_address="0x123...",
        owner_address="0x456...",
        spender_address="0x789..."
    )
    
    return {
        "token": token,
        "balance": balance,
        "allowance": allowance
    }
```

### Transfer and Approval Example

```python
async def transfer_example():
    plugin = ERC20Plugin(
        rpc_url="your_rpc_url",
        private_key="your_private_key"
    )
    
    # Approve spender
    approve_tx = await plugin.approve(
        token_address="0x123...",
        spender_address="0x456...",
        amount=Decimal("100.0")
    )
    
    # Transfer tokens
    transfer_tx = await plugin.transfer(
        token_address="0x123...",
        to_address="0x789...",
        amount=Decimal("50.0")
    )
    
    return {
        "approve_tx": approve_tx,
        "transfer_tx": transfer_tx
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Transaction Failures**
   - Verify sufficient gas
   - Check token balance and allowance
   - Ensure correct network configuration

2. **RPC Issues**
   - Verify RPC endpoint is accessible
   - Check network status
   - Consider using alternative RPC providers

3. **Contract Interactions**
   - Verify contract addresses
   - Check token decimals
   - Ensure contract is not paused

4. **Gas Estimation**
   - Use appropriate gas limits
   - Monitor network congestion
   - Consider using gas price oracles

## API Reference

For complete API documentation, see the [ERC20 Token Standard](https://eips.ethereum.org/EIPS/eip-20). 