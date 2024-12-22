# GOAT 🐐 in Python

Unofficial SDK to add blockchain tools to your AI agent written in Python, designed for Solana and Mode. 
Original repo: https://github.com/goat-sdk/goat

### Features

- **Multi-Chain Support**: Works seamless with Solana and Mode
- **Plugin Architecture**: Modular design for easy extensibility
- **AI Integration**: Built-in support for LangChain and LlamaIndex
- **Type Safety**: Full TypeScript-like typing with Pydantic
- **Async First**: Modern async/await design
- **Error Handling**: Comprehensive error types and handling

### Available Plugins

- **SPL Token Plugin**: Interact with SPL tokens on Solana and Mode networks
  - Token balance queries
  - Token transfers
  - Account existence checks
  - Token metadata retrieval
  - Base unit conversion utilities

- **Solana NFT Plugin**: Work with NFTs on the Solana blockchain
  - NFT metadata retrieval
  - NFT transfers
  - Collection queries
  - Ownership verification
  - Metadata updates

## Quick Start

#### Prerequisites

- Python 3.9 or higher
- Poetry 1.7 or higher

### Installation

#### 1. Using poetry (recommended)
```bash
poetry add GOAT-sdk-py

# Add plugins as needed
poetry add "GOAT-sdk-py[spl-token]"  # For SPL token support
poetry add "GOAT-sdk-py[solana-nft]" # For Solana NFT support
```

#### 2. Using pip

```bash
pip install GOAT-sdk-py
pip install "GOAT-sdk-py[spl-token]"  # For SPL token support
pip install "GOAT-sdk-py[solana-nft]" # For Solana NFT support
```

### Setup

```python
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.spl_token import SplTokenPlugin

# Initialize SDK
sdk = GoatSDK(
    private_key="your_private_key", 
    network=Network.MAINNET,
    chain=Chain.SOLANA
)

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

### Documentation

- [Getting Started](goat_sdk/docs/getting-started.md)
- [Plugin Guide](goat_sdk/docs/plugin-guide.md)
- [API Reference](goat_sdk/docs/api-reference.md)
- [Error Handling](goat_sdk/docs/error-handling.md)
- [AI Integration](goat_sdk/docs/ai-integration.md)

## Development

Contributions are welcome! Please feel free to submit a PR.
```bash
# Clone repository
git clone https://github.com/AIFlowML/GOAT-sdk-py.git
cd GOAT-sdk-py

# Install dependencies
poetry install

# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest tests/
```




### License

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.7%2B-blue)](https://python-poetry.org/)


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Author

**Igor Lessio**

email: ilessio.aimaster@gmail.com

### Disclaimer

This is an unofficial implementation of the GOAT SDK. It is not affiliated with, officially connected to, or endorsed by the official GOAT SDK team.

### Acknowledgments

Special thanks to Akhtar for the opportunity to create this SDK.
