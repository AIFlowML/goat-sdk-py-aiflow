# Python Trading SDK 🐐

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.7%2B-blue)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

> A powerful Python SDK for integrating blockchain capabilities into AI agents, with first-class support for Solana and Mode networks.

## ✨ Highlights

- 🌐 **Multi-Chain Architecture** - Seamless integration with Solana and Mode networks
- 🧩 **Plugin System** - Extensible design for easy feature additions
- 🤖 **AI-First Design** - Built-in support for LangChain and LlamaIndex
- 📝 **Type Safety** - Comprehensive typing with Pydantic
- ⚡ **Modern Async** - Built on async/await patterns
- 🛡️ **Robust Error Handling** - Detailed error types and recovery strategies

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Poetry 1.7+ (recommended) or pip

### Installation

**Using Poetry (Recommended)**
```bash
# Core SDK
poetry add GOAT-sdk-py

# Optional Plugins
poetry add "GOAT-sdk-py[spl-token]"    # SPL Token support
poetry add "GOAT-sdk-py[solana-nft]"   # Solana NFT support
```

**Using pip**
```bash
# Core SDK
pip install GOAT-sdk-py

# Optional Plugins
pip install "GOAT-sdk-py[spl-token]"    # SPL Token support
pip install "GOAT-sdk-py[solana-nft]"   # Solana NFT support
```

### Basic Usage

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

# Set up SPL Token plugin
spl = SplTokenPlugin(sdk)

# Query token balance
balance = await spl.get_token_balance(
    mint_address="your_token_mint",
    owner_address="your_wallet"
)

# Transfer tokens
tx = await spl.transfer_token(
    mint_address="token_mint",
    to_address="recipient",
    amount=1000000  # in base units
)
```

## 🧩 Available Plugins

### SPL Token Plugin
Comprehensive toolkit for SPL token operations:
- 💰 Balance queries and transfers
- ✅ Account validation
- 📊 Metadata retrieval
- 🔄 Unit conversion utilities

### Solana NFT Plugin
Complete NFT management capabilities:
- 🖼️ Metadata handling
- 📤 Transfer operations
- 🗂️ Collection management
- ✨ Ownership verification
- 📝 Metadata updates

## 📚 Documentation

- [Getting Started Guide](goat_sdk/docs/getting-started.md)
- [Plugin Development](goat_sdk/docs/plugin-guide.md)
- [API Reference](goat_sdk/docs/api-reference.md)
- [Error Handling](goat_sdk/docs/error-handling.md)
- [AI Integration Guide](goat_sdk/docs/ai-integration.md)

## 🛠️ Development

We welcome contributions! Here's how to get started:

```bash
# Clone the repository
git clone https://github.com/AIFlowML/GOAT-sdk-py.git
cd GOAT-sdk-py

# Install dependencies
poetry install

# Add development dependencies
poetry install --with dev

# Run test suite
poetry run pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Lead Developer**
- Igor Lessio ([@ilessio](https://github.com/ilessio))
- Email: ilessio.aimaster@gmail.com

## ⚠️ Disclaimer

This is an unofficial SDK implementation. It is not affiliated with, officially connected to, or endorsed by any official SDK team.

## 🙏 Acknowledgments

Special thanks to:
- Akhtar for the opportunity to create this SDK
- The Hyperliquid team for their excellent Python SDK
- All our contributors

## 📚 Citations

If you use this SDK in your research or project, please cite:

```bibtex
@misc{hyperliquid-python-sdk,
  author = {Hyperliquid},
  title = {SDK for Hyperliquid API trading with Python},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/hyperliquid-dex/hyperliquid-python-sdk}}
}
```

---

<div align="center">
Made with ❤️ by Igor Lessio
</div>