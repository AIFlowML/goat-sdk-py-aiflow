# Plugin Guide

This guide provides detailed information about the available plugins and how to use them effectively.

## Jupiter Plugin

The Jupiter plugin enables token swaps on Solana using the Jupiter aggregator.

### Setup
```python
from goat_sdk.plugins.jupiter import JupiterPlugin
from goat_sdk.core import WalletClient

# Initialize wallet client
wallet_client = WalletClient(private_key="your_private_key")

# Create Jupiter plugin instance
jupiter = JupiterPlugin(wallet_client)
```

### Getting a Quote
```python
# Get quote for swapping SOL to USDC
quote = await jupiter.get_quote(
    input_mint="So11111111111111111111111111111111111111112",  # SOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=1_000_000_000,  # 1 SOL (in lamports)
    slippage_bps=50,  # 0.5% slippage
)

print(f"Output amount: {quote.out_amount}")
print(f"Price impact: {quote.price_impact}%")
```

### Executing a Swap
```python
# Execute the swap using the quote
result = await jupiter.swap(quote)
print(f"Transaction signature: {result}")
```

## NFT Plugin

The NFT plugin provides functionality for minting and managing NFTs on Solana.

### Setup
```python
from goat_sdk.plugins.nft import NFTPlugin
from goat_sdk.plugins.nft.types import NFTMetadata, Creator

# Initialize NFT plugin
nft = NFTPlugin(wallet_client)
```

### Minting a Regular NFT
```python
# Create metadata
metadata = NFTMetadata(
    name="My NFT",
    symbol="MNFT",
    description="My first NFT on Solana",
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

# Mint NFT
result = await nft.mint(metadata)
print(f"NFT mint: {result.mint}")
print(f"Metadata: {result.metadata_address}")
```

### Minting a Compressed NFT
```python
from goat_sdk.plugins.nft.types import CompressedNFTParams

# Create parameters for compressed NFT
params = CompressedNFTParams(
    metadata=metadata,
    max_depth=14,
    max_buffer_size=64,
)

# Mint compressed NFT
result = await nft.mint_compressed_nft(params)
print(f"Asset ID: {result.asset_id}")
print(f"Tree address: {result.tree_address}")
```

### Transferring NFTs
```python
# Transfer regular NFT
await nft.transfer(
    mint="NFT_MINT_ADDRESS",
    to_address="RECIPIENT_ADDRESS",
)

# Transfer compressed NFT
await nft.transfer_compressed_nft(
    asset_id="ASSET_ID",
    to_address="RECIPIENT_ADDRESS",
)
```

## SPL Token Plugin

The SPL Token plugin handles token operations on Solana.

### Setup
```python
from goat_sdk.plugins.spl_token import SPLTokenPlugin

# Initialize SPL Token plugin
spl = SPLTokenPlugin(wallet_client)
```

### Token Operations
```python
# Create token account
account = await spl.create_account(
    mint="TOKEN_MINT_ADDRESS",
)

# Transfer tokens
await spl.transfer(
    mint="TOKEN_MINT_ADDRESS",
    to_address="RECIPIENT_ADDRESS",
    amount=1_000_000,  # Amount in smallest units
)

# Check balance
balance = await spl.get_balance(
    mint="TOKEN_MINT_ADDRESS",
)
print(f"Balance: {balance}")
```

## Tensor Plugin

The Tensor plugin enables NFT trading through the Tensor marketplace.

### Setup
```python
from goat_sdk.plugins.tensor import TensorPlugin
from goat_sdk.plugins.tensor.config import TensorConfig

# Create configuration
config = TensorConfig(
    api_key="your_tensor_api_key",
    api_url="https://api.tensor.so",
)

# Initialize Tensor plugin
tensor = TensorPlugin(wallet_client, config)
```

### NFT Operations
```python
# Get NFT information
nft_info = await tensor.get_nft_info(
    mint="NFT_MINT_ADDRESS",
)
print(f"NFT owner: {nft_info.owner}")
print(f"Last sale price: {nft_info.last_sale.price if nft_info.last_sale else 'N/A'}")

# Buy NFT from listing
transaction = await tensor.get_buy_listing_transaction(
    mint="NFT_MINT_ADDRESS",
)
result = await wallet_client.send_transaction(transaction)
print(f"Purchase transaction: {result}")
```

## Error Handling

All plugins include comprehensive error handling. Here's an example:

```python
from goat_sdk.core.errors import (
    QuoteError,
    TransactionError,
    NetworkError,
)

try:
    result = await jupiter.swap(quote)
except QuoteError as e:
    print(f"Failed to get quote: {e}")
except TransactionError as e:
    print(f"Transaction failed: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. Always use `async/await` with plugin methods
2. Handle errors appropriately using try/except blocks
3. Close plugin instances when done using async context managers
4. Set reasonable slippage values for swaps
5. Verify transaction results before proceeding
6. Use appropriate retry mechanisms for network operations
7. Keep API keys secure and never expose them in code

## Common Issues and Solutions

1. **Transaction Error: Invalid Blockhash**
   - Solution: Retry the transaction with a new blockhash
   - Use the retry mechanism built into the plugins

2. **Insufficient Balance**
   - Solution: Check balances before transactions
   - Include fees in calculations

3. **Network Timeouts**
   - Solution: Use appropriate timeout values
   - Implement retry logic with exponential backoff

4. **Invalid Public Keys**
   - Solution: Validate addresses before use
   - Use the PublicKey class for validation 