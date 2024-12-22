# Getting Started with GOAT-sdk-py

## Overview

GOAT-sdk-py is an unofficial Python SDK for blockchain development, created by Igor Lessio. It provides a unified interface for interacting with various blockchain networks and protocols, with a focus on Solana and Mode networks.

## Features

- **Multi-Chain Support**: Work with Solana and Mode networks
- **Plugin Architecture**: Modular design for extensibility
- **AI Integration**: Built-in support for LangChain and LlamaIndex
- **Type Safety**: Full TypeScript-like typing with Pydantic
- **Async First**: Modern async/await design
- **Error Handling**: Comprehensive error types and handling

## Installation

### Prerequisites

- Python 3.9 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
# Create new project
poetry new my-blockchain-project
cd my-blockchain-project

# Add GOAT-sdk-py
poetry add GOAT-sdk-py

# Add plugins as needed
poetry add "GOAT-sdk-py[spl-token]"  # For SPL token support
poetry add "GOAT-sdk-py[solana-nft]" # For Solana NFT support
```

### Using pip

```bash
pip install GOAT-sdk-py
pip install "GOAT-sdk-py[spl-token]"  # For SPL token support
pip install "GOAT-sdk-py[solana-nft]" # For Solana NFT support
```

## Quick Start

### Basic Setup

```python
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain

# Initialize SDK
sdk = GoatSDK(
    private_key="your_private_key",  # or use mnemonic
    network=Network.MAINNET,
    chain=Chain.SOLANA
)
```

### Working with SPL Tokens

```python
from goat_sdk.plugins.spl_token import SplTokenPlugin

# Initialize plugin
spl = SplTokenPlugin(sdk)

# Get token balance
balance = await spl.get_token_balance(
    mint_address="your_token_mint",
    owner_address="your_wallet"
)

# Transfer tokens
result = await spl.transfer_token(
    mint_address="token_mint",
    to_address="recipient",
    amount=1000000  # in base units
)
```

### Working with NFTs

```python
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin

# Initialize plugin
nft = SolanaNFTPlugin(sdk)

# Get NFT metadata
metadata = await nft.get_nft_metadata(
    mint_address="nft_mint"
)

# Transfer NFT
result = await nft.transfer_nft(
    mint_address="nft_mint",
    to_address="recipient"
)
```

## Core Concepts

### SDK Configuration

The SDK can be configured with various options:

```python
from goat_sdk.core.types import ModeConfig

config = ModeConfig(
    retry_count=3,
    timeout=30,
    commitment="confirmed",
    skip_preflight=False
)

sdk = GoatSDK(
    private_key="your_private_key",
    network=Network.MAINNET,
    options=config
)
```

### Wallet Management

Multiple wallet options are supported:

```python
# Using private key
sdk = GoatSDK(private_key="your_private_key")

# Using mnemonic
sdk = GoatSDK(mnemonic="your twelve word mnemonic phrase")

# Using custom wallet
from your_wallet import CustomWallet
sdk = GoatSDK(wallet=CustomWallet())
```

### Network Configuration

```python
# Mainnet
sdk = GoatSDK(
    private_key="key",
    network=Network.MAINNET
)

# Testnet
sdk = GoatSDK(
    private_key="key",
    network=Network.TESTNET
)

# Custom RPC
sdk = GoatSDK(
    private_key="key",
    network=Network.MAINNET,
    rpc_url="https://your-rpc-endpoint.com"
)
```

### Plugin Configuration

Plugins can be configured with specific options:

```python
from goat_sdk.plugins.spl_token.types import SplTokenConfig

config = SplTokenConfig(
    commitment="confirmed",
    skip_preflight=False,
    retry_count=3
)

spl = SplTokenPlugin(
    sdk,
    chain=Chain.SOLANA,
    options=config
)
```

## Error Handling

The SDK provides comprehensive error types:

```python
from goat_sdk.exceptions import (
    GoatSDKError,
    NetworkError,
    WalletError,
    TokenError,
    NFTError
)

try:
    result = await spl.transfer_token(...)
except TokenError as e:
    if isinstance(e, InsufficientBalanceError):
        print(f"Not enough balance: {e.available} < {e.required}")
    elif isinstance(e, TokenAccountNotFoundError):
        print(f"Token account not found: {e.address}")
except NetworkError as e:
    print(f"Network error: {str(e)}")
except GoatSDKError as e:
    print(f"Other SDK error: {str(e)}")
```

## AI Integration

### LangChain Integration

```python
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from goat_sdk.adapters import LangchainAdapter

# Get tools from plugins
spl = SplTokenPlugin(sdk)
tools = spl.get_tools()

# Create agent
agent = initialize_agent(
    tools=LangchainAdapter.create_tools(tools),
    llm=ChatOpenAI(),
    agent="chat-conversational-react-description",
    verbose=True
)

# Use agent
response = await agent.arun(
    "Get the balance of my SPL token"
)
```

### LlamaIndex Integration

```python
from llama_index import GPTVectorStoreIndex
from goat_sdk.adapters import LlamaIndexAdapter

# Get tools from plugins
nft = SolanaNFTPlugin(sdk)
tools = nft.get_tools()

# Create index with tools
index = GPTVectorStoreIndex.from_tools(
    LlamaIndexAdapter.create_tools(tools)
)

# Query
response = index.query(
    "What NFTs do I own?"
)
```

## Examples

### Token Transfer Flow

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.spl_token import SplTokenPlugin
from goat_sdk.core.types import Network

async def transfer_tokens():
    # Initialize SDK
    sdk = GoatSDK(
        private_key="your_private_key",
        network=Network.MAINNET
    )
    
    # Initialize plugin
    spl = SplTokenPlugin(sdk)
    
    try:
        # Check sender balance
        balance = await spl.get_token_balance(
            mint_address="token_mint",
            owner_address="sender"
        )
        
        # Check if recipient has token account
        has_account = await spl.does_account_exist(
            owner_pubkey="recipient",
            mint_pubkey="token_mint"
        )
        
        # Transfer tokens
        result = await spl.transfer_token(
            mint_address="token_mint",
            to_address="recipient",
            amount=1000000
        )
        
        print(f"Transfer successful: {result.signature}")
        
    except Exception as e:
        print(f"Transfer failed: {str(e)}")
```

### NFT Metadata Query

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin

async def get_nft_info():
    # Initialize SDK and plugin
    sdk = GoatSDK(private_key="your_private_key")
    nft = SolanaNFTPlugin(sdk)
    
    try:
        # Get metadata
        metadata = await nft.get_nft_metadata(
            mint_address="nft_mint"
        )
        
        # Print info
        print(f"Name: {metadata.name}")
        print(f"Symbol: {metadata.symbol}")
        print(f"URI: {metadata.uri}")
        print(f"Attributes: {metadata.attributes}")
        
    except Exception as e:
        print(f"Failed to get NFT info: {str(e)}")
```

## Next Steps

- Check out the [Plugin Guide](./plugin-guide.md) for detailed plugin documentation
- See the [API Reference](./api-reference.md) for complete API details
- View more [Examples](../examples/) for additional usage scenarios
- Learn about [Error Handling](./error-handling.md)
- Explore [AI Integration](./ai-integration.md) capabilities
