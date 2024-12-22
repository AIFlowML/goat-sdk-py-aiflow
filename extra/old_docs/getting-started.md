# Getting Started

This guide will help you get started with the GOAT SDK for Python.

## Installation

Install the SDK using pip:

```bash
pip install goat-sdk
```

Or install from source:

```bash
git clone https://github.com/mode-labs/goat-sdk-python.git
cd goat-sdk-python
pip install -e .
```

## Prerequisites

- Python 3.8 or higher
- A Solana wallet with some SOL for transactions
- (Optional) API keys for specific services (e.g., Tensor)

## Basic Setup

First, import the necessary components and initialize a wallet client:

```python
from goat_sdk.core import WalletClient
from goat_sdk.plugins.jupiter import JupiterPlugin
from goat_sdk.plugins.nft import NFTPlugin
from goat_sdk.plugins.spl_token import SPLTokenPlugin
from goat_sdk.plugins.tensor import TensorPlugin, TensorConfig

# Initialize wallet client
wallet_client = WalletClient(
    private_key="your_private_key",
    provider_url="https://api.mainnet-beta.solana.com",
)
```

## Quick Examples

### Token Swaps with Jupiter

```python
# Initialize Jupiter plugin
jupiter = JupiterPlugin(wallet_client)

# Swap 0.1 SOL for USDC
async def swap_sol_to_usdc():
    # Get quote
    quote = await jupiter.get_quote(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=100_000_000,  # 0.1 SOL
    )
    
    # Execute swap
    signature = await jupiter.swap(quote)
    print(f"Swap executed: {signature}")
```

### Minting NFTs

```python
# Initialize NFT plugin
nft = NFTPlugin(wallet_client)

# Mint a regular NFT
async def mint_nft():
    metadata = NFTMetadata(
        name="My First NFT",
        symbol="FIRST",
        description="A test NFT",
        seller_fee_basis_points=500,  # 5% royalty
        image="https://example.com/image.png",
        creators=[
            Creator(
                address=wallet_client.public_key,
                share=100,
                verified=True,
            )
        ],
    )
    
    result = await nft.mint(metadata)
    print(f"NFT minted: {result.mint}")
```

### Token Transfers

```python
# Initialize SPL Token plugin
spl = SPLTokenPlugin(wallet_client)

# Transfer USDC
async def transfer_usdc():
    # USDC amount (1 USDC = 1_000_000 units)
    amount = 1_000_000
    
    # Transfer to recipient
    signature = await spl.transfer(
        mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        to_address="recipient_address",
        amount=amount,
    )
    print(f"Transfer executed: {signature}")
```

### NFT Trading with Tensor

```python
# Initialize Tensor plugin
config = TensorConfig(
    api_key="your_tensor_api_key",
)
tensor = TensorPlugin(wallet_client, config)

# Buy an NFT
async def buy_nft():
    # Get NFT information
    nft_info = await tensor.get_nft_info(
        mint="nft_mint_address",
    )
    
    # Check if NFT is listed
    if nft_info.listings:
        # Get buy transaction
        transaction = await tensor.get_buy_listing_transaction(
            mint="nft_mint_address",
        )
        
        # Execute purchase
        signature = await wallet_client.send_transaction(transaction)
        print(f"NFT purchased: {signature}")
```

## Error Handling

Always use try/except blocks to handle potential errors:

```python
from goat_sdk.core.errors import (
    QuoteError,
    TransactionError,
    NetworkError,
    InsufficientBalanceError,
)

async def safe_swap():
    try:
        quote = await jupiter.get_quote(
            input_mint="So11111111111111111111111111111111111111112",
            output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            amount=100_000_000,
        )
        signature = await jupiter.swap(quote)
        print(f"Swap successful: {signature}")
        
    except QuoteError as e:
        print(f"Failed to get quote: {e}")
    except TransactionError as e:
        print(f"Transaction failed: {e}")
    except NetworkError as e:
        print(f"Network error: {e}")
    except InsufficientBalanceError as e:
        print(f"Insufficient balance: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Using Context Managers

For better resource management, use async context managers:

```python
async def perform_operations():
    async with JupiterPlugin(wallet_client) as jupiter:
        # Get quote
        quote = await jupiter.get_quote(...)
        
        # Execute swap
        signature = await jupiter.swap(quote)
```

## Best Practices

1. **Environment Variables**
   - Store sensitive information like private keys and API keys in environment variables
   - Use a `.env` file for local development

```python
import os
from dotenv import load_dotenv

load_dotenv()

wallet_client = WalletClient(
    private_key=os.getenv("SOLANA_PRIVATE_KEY"),
)

tensor = TensorPlugin(
    wallet_client,
    config=TensorConfig(
        api_key=os.getenv("TENSOR_API_KEY"),
    ),
)
```

2. **Transaction Confirmation**
   - Wait for transaction confirmations
   - Use appropriate commitment levels

```python
# High-value transactions
signature = await wallet_client.send_transaction(
    transaction,
    commitment="finalized",
)

# Regular transactions
signature = await wallet_client.send_transaction(
    transaction,
    commitment="confirmed",
)
```

3. **Rate Limiting**
   - Respect API rate limits
   - Use built-in retry mechanisms

```python
# Configure retry settings
jupiter = JupiterPlugin(
    wallet_client,
    retry_attempts=3,
    retry_delay=1.0,
)
```

4. **Resource Cleanup**
   - Always close connections properly
   - Use context managers

```python
async def main():
    async with (
        JupiterPlugin(wallet_client) as jupiter,
        TensorPlugin(wallet_client, config) as tensor,
    ):
        # Perform operations
        pass
```

## Next Steps

1. Read the [Plugin Guide](plugin-guide.md) for detailed plugin usage
2. Check the [API Reference](api-reference.md) for complete documentation
3. Join our [Discord](https://discord.gg/modelabs) for support
4. Follow us on [Twitter](https://twitter.com/modelabs) for updates 