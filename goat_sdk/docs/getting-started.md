# Getting Started with GOAT SDK

Welcome to the GOAT SDK for Python! This guide will help you get started with using the SDK in your Python projects.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### Installing the SDK

```bash
pip install goat-sdk
```

## Basic Usage

### Initializing the SDK

```python
from goat_sdk import GoatSDK

# For Mode Network
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://sepolia.mode.network"
)

# For Solana
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://api.devnet.solana.com"
)
```

### Using Plugins

The GOAT SDK uses a plugin system to provide functionality for different blockchain networks and protocols.

#### ERC20 Plugin (Mode Network)

```python
from goat_sdk.plugins.ERC20 import ERC20Plugin, DeployTokenParams

# Initialize plugin
erc20 = ERC20Plugin(sdk)

# Deploy a new token
token = await erc20.deploy_token(DeployTokenParams(
    name="My Token",
    symbol="MTK",
    initial_supply=1000000
))

# Transfer tokens
await erc20.transfer({
    "token_address": token.contract_address,
    "to_address": "recipient_address",
    "amount": 100
})
```

#### SPL Token Plugin (Solana)

```python
from goat_sdk.plugins.spl_token import SplTokenPlugin, MintTokenParams

# Initialize plugin
spl = SplTokenPlugin(sdk)

# Mint tokens
result = await spl.mint_token(MintTokenParams(
    amount=1000,
    recipient="recipient_address"
))
```

## Configuration

### Network Configuration

The SDK supports various networks:

```python
# Mode Network (Testnet)
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://sepolia.mode.network"
)

# Mode Network (Local Development)
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="http://localhost:8545"  # Ganache
)

# Solana (Devnet)
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://api.devnet.solana.com"
)
```

### Plugin Configuration

Each plugin can be configured with specific parameters:

```python
# ERC20 Plugin with custom gas settings
erc20 = ERC20Plugin(
    sdk,
    gas_limit=300000,
    gas_price_multiplier=1.2
)

# SPL Token Plugin with custom commitment
spl = SplTokenPlugin(
    sdk,
    commitment="confirmed"
)
```

## Error Handling

The SDK uses Python's exception system to handle errors:

```python
from goat_sdk.core.errors import GoatSDKError

try:
    result = await erc20.transfer({
        "token_address": "0x...",
        "to_address": "0x...",
        "amount": 100
    })
except GoatSDKError as e:
    print(f"Error: {e}")
```

## Next Steps

- Check out our [examples](../examples) for more detailed usage scenarios
- Read the [API Reference](api-reference.md) for detailed documentation
- Learn about [Plugin Development](plugin-guide.md) to create your own plugins
