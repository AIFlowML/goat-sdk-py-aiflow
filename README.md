# GOAT SDK for Python 🐐

This is the official Python implementation of the GOAT SDK, providing a comprehensive toolkit for interacting with various blockchain networks and protocols. Built with Python's strong typing system and modern best practices, it offers a seamless experience for developers building blockchain applications.

## Features

- **Core SDK Functionality**
  - Chain-agnostic architecture
  - Comprehensive type system
  - Robust error handling
  - Async/await support

- **Plugin System**
  - ERC20 token support for Mode Network
  - SPL token support for Solana
  - NFT support (coming soon)
  - Extensible plugin architecture

- **Network Support**
  - Mode Network integration
  - Solana integration
  - Local development with Ganache
  - Easy network switching

- **Developer Experience**
  - Type hints throughout
  - Comprehensive documentation
  - Extensive test coverage
  - Example applications

## Installation

```bash
pip install goat-sdk
```

## Quick Start

### ERC20 Token Operations on Mode Network

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin, DeployTokenParams

# Initialize the SDK with Mode Network
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://sepolia.mode.network"
)

# Initialize ERC20 plugin
erc20 = ERC20Plugin(sdk)

# Deploy a new token
token = await erc20.deploy_token(DeployTokenParams(
    name="My Token",
    symbol="MTK",
    initial_supply=1000000
))

print(f"Token deployed at: {token.contract_address}")
```

### SPL Token Operations on Solana

```python
from goat_sdk.plugins.spl_token import SplTokenPlugin, MintTokenParams

# Initialize the SDK with Solana
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://api.devnet.solana.com"
)

# Initialize SPL Token plugin
spl = SplTokenPlugin(sdk)

# Mint new tokens
result = await spl.mint_token(MintTokenParams(
    amount=1000,
    recipient="recipient_address"
))

print(f"Tokens minted: {result.signature}")
```

## Development

### Setting Up the Environment

```bash
# Clone the repository
git clone https://github.com/goat-sdk/python-goat.git
cd python-goat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific plugin tests
pytest tests/plugins/ERC20
pytest tests/plugins/spl_token

# Run with coverage
pytest --cov=goat_sdk
```

## Project Structure

```
goat_sdk/
├── core/           # Core SDK functionality
│   ├── chain.py    # Chain definitions
│   └── types/      # Core type definitions
├── plugins/        # Plugin implementations
│   ├── ERC20/      # Mode Network ERC20 plugin
│   └── spl_token/  # Solana SPL Token plugin
├── docs/          # Documentation
└── tests/         # Test suite
```

## Documentation

- [Getting Started](https://github.com/goat-sdk/python-goat/tree/main/goat_sdk/docs/getting-started.md)
- [API Reference](https://github.com/goat-sdk/python-goat/tree/main/goat_sdk/docs/api-reference.md)
- [Plugin Guide](https://github.com/goat-sdk/python-goat/tree/main/goat_sdk/docs/plugin-guide.md)
- [Examples](https://github.com/goat-sdk/python-goat/tree/main/examples)

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/goat-sdk/python-goat/tree/main/CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
