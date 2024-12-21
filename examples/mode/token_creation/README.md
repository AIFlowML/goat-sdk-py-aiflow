# Token Creation Example

This example demonstrates how to create and deploy ERC20 tokens on the Mode Network using the GOAT SDK.

## Features

- Basic token deployment
- Token with custom parameters (name, symbol, supply)
- Token deployment with error handling
- Gas estimation and optimization

## Prerequisites

- Python 3.11+
- Mode testnet account with funds
- Mode testnet RPC URL

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
PRIVATE_KEY=your_private_key
MODE_RPC_URL=https://sepolia.mode.network
```

## Running the Example

1. Basic token deployment:
```bash
python deploy_token.py
```

2. Custom token deployment:
```bash
python deploy_custom_token.py --name "My Token" --symbol "MTK" --supply 1000000
```

## Code Walkthrough

### Basic Token Deployment

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin, DeployTokenParams

async def deploy_basic_token():
    # Initialize SDK
    sdk = GoatSDK(
        private_key=os.getenv("PRIVATE_KEY"),
        provider_url=os.getenv("MODE_RPC_URL")
    )

    # Initialize ERC20 plugin
    erc20 = ERC20Plugin(sdk)

    # Deploy token
    try:
        result = await erc20.deploy_token(DeployTokenParams(
            name="My Token",
            symbol="MTK",
            initial_supply=1000000
        ))
        print(f"Token deployed at: {result.contract_address}")
        print(f"Transaction: {result.explorer_url}")
    except Exception as e:
        print(f"Error: {e}")
```

### Custom Token Deployment

```python
async def deploy_custom_token(name: str, symbol: str, supply: int):
    sdk = GoatSDK(
        private_key=os.getenv("PRIVATE_KEY"),
        provider_url=os.getenv("MODE_RPC_URL")
    )
    erc20 = ERC20Plugin(sdk)

    try:
        result = await erc20.deploy_token(DeployTokenParams(
            name=name,
            symbol=symbol,
            initial_supply=supply
        ))
        return result
    except Exception as e:
        raise Exception(f"Token deployment failed: {e}")
```

## Error Handling

The example includes proper error handling for common issues:
- Network connection errors
- Insufficient funds
- Invalid parameters
- Failed transactions

## Gas Optimization

The SDK automatically:
- Estimates gas requirements
- Adds a 20% buffer for Mode network
- Retries failed transactions with adjusted gas

## Next Steps

1. Try deploying tokens with different parameters
2. Explore token management features
3. Integrate with other Mode network features
