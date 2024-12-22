# GOAT-sdk-py 🐐

<div align="center">

![GOAT SDK Python](https://img.shields.io/badge/GOAT--SDK-Python-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-yellow?style=for-the-badge&logo=python)
![Poetry](https://img.shields.io/badge/Poetry-1.7+-purple?style=for-the-badge&logo=poetry)

Unleash the power of blockchain in your Python AI agents.

[Documentation](https://github.com/ilessio/GOAT-sdk-py/wiki) | [Examples](./examples) | [Contributing](./CONTRIBUTING.md)

*An unofficial Python implementation of the GOAT SDK, created by [Igor Lessio](mailto:ilessio.aimaster@gmail.com)*
</div>

## Overview 🌟

GOAT-sdk-py is a Python implementation of the Great Onchain Agent Toolkit (GOAT), designed to seamlessly integrate blockchain capabilities into your AI agents. While the official GOAT SDK focuses on TypeScript, this Python implementation brings the same powerful features to the Python ecosystem.

### Why GOAT-sdk-py? 🤔

- **Native Python Integration**: Built from the ground up for Python, following Pythonic principles
- **Async First**: Leverages Python's async/await for optimal performance
- **Type Safety**: Full type hints support with Pydantic v2
- **Framework Agnostic**: Works with any Python AI framework (LangChain, LlamaIndex, etc.)
- **Production Ready**: Comprehensive test coverage and error handling

## Installation 🛠️

GOAT-sdk-py uses Poetry for dependency management. Here's how to get started:

1. **Install Poetry** (if you haven't already):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install GOAT-sdk-py**:
```bash
# Create a new project
poetry new my-goat-project
cd my-goat-project

# Add GOAT-sdk-py
poetry add GOAT-sdk-py

# Install with specific plugins
poetry add "GOAT-sdk-py[solana,ethereum]"  # For Solana and Ethereum support
poetry add "GOAT-sdk-py[full]"             # For all plugins
```

3. **Activate the environment**:
```bash
poetry shell
```

## Available Plugins 🔌

GOAT-sdk-py comes with a growing collection of blockchain plugins:

### Core Plugins
| Plugin | Description | Networks | Features |
|--------|-------------|----------|-----------|
| `SPLToken` | Solana Token Operations | Solana | Token transfers, balance checks, account management |
| `ERC20` | EVM Token Operations | Mode, Ethereum | Token transfers, approvals, allowances |
| `SolanaNFT` | Solana NFT Operations | Solana | Mint, transfer, metadata management |
| `Uniswap` | DEX Integration | Ethereum | Swaps, liquidity, price checks |
| `TensorTrade` | NFT Trading | Solana | List, buy, sell NFTs |
| `Hyperliquid` | Perpetuals Trading | Hyperliquid | Trade, position management |

### Plugin Installation
```bash
# Install specific plugins
poetry add "GOAT-sdk-py[spl-token]"    # For Solana token operations
poetry add "GOAT-sdk-py[solana-nft]"   # For Solana NFT operations
poetry add "GOAT-sdk-py[erc20]"        # For ERC20 operations
poetry add "GOAT-sdk-py[uniswap]"      # For Uniswap integration
```

## Usage Examples 🎯

### Basic Token Operations

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.spl_token import SplTokenPlugin
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin

async def main():
    # Initialize SDK
    sdk = GoatSDK(
        private_key="your_private_key",
        network="mainnet"
    )

    # Initialize plugins
    spl = SplTokenPlugin(sdk)
    nft = SolanaNFTPlugin(sdk)

    # Check USDC balance
    balance = await spl.get_token_balance_by_mint_address(
        wallet_address="your_wallet",
        mint_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    )

    # Get NFT metadata
    nft_info = await nft.get_nft_metadata(
        mint_address="your_nft_mint_address"
    )
```

### AI Agent Integration with LangChain

```python
from langchain import OpenAI, LLMChain
from goat_sdk.adapters import LangchainAdapter
from goat_sdk.plugins import SplTokenPlugin, SolanaNFTPlugin, UniswapPlugin

async def create_crypto_agent():
    # Initialize SDK and plugins
    sdk = GoatSDK(private_key="your_private_key")
    
    # Get all tools
    tools = sdk.get_tools([
        SplTokenPlugin,
        SolanaNFTPlugin,
        UniswapPlugin
    ])

    # Create Langchain adapter
    goat_tools = LangchainAdapter.create_tools(tools)

    # Create agent
    llm = OpenAI(temperature=0)
    agent = LLMChain(
        llm=llm,
        tools=goat_tools,
        template="""
        You are a crypto trading assistant. Use the available tools to:
        1. Check token balances
        2. Execute trades
        3. Manage NFTs
        
        Human: {input}
        Assistant: Let me help you with that.
        """
    )

    return agent

# Use the agent
agent = await create_crypto_agent()
response = await agent.arun(
    "Check my USDC balance and list my Solana NFTs for sale on Tensor"
)
```

### Error Handling

```python
from goat_sdk.exceptions import InsufficientBalanceError, TokenAccountNotFoundError

try:
    await spl.transfer_token_by_mint_address(
        to="recipient_address",
        mint_address="token_mint",
        amount=1000000
    )
except InsufficientBalanceError as e:
    print(f"Not enough balance: {e.available} < {e.required}")
except TokenAccountNotFoundError as e:
    print(f"Token account not found: {e.address}")
```

## Architecture 🏗️

```
goat_sdk/
├── core/           # Core SDK functionality
│   ├── chain.py    # Chain definitions
│   └── types/      # Type system
├── plugins/        # Plugin implementations
│   ├── spl_token/  # Solana token operations
│   ├── solana_nft/ # Solana NFT operations
│   ├── ERC20/      # EVM token operations
│   ├── uniswap/    # Uniswap integration
│   ├── tensor/     # Tensor trading
│   └── hyperliquid/# Perpetuals trading
└── adapters/       # Framework adapters
    ├── langchain/  # LangChain integration
    └── llamaindex/ # LlamaIndex integration
```

## Contributing 🤝

Contributions are welcome! See our [Contributing Guide](./CONTRIBUTING.md) for details.

## Testing 🧪

```bash
# Install dev dependencies
poetry install --with test

# Run tests
poetry run pytest tests/

# Run specific plugin tests
poetry run pytest tests/plugins/spl_token/
poetry run pytest tests/plugins/solana_nft/
```

## Documentation 📚

Full documentation is available in our [Wiki](https://github.com/ilessio/GOAT-sdk-py/wiki):

- [Getting Started](https://github.com/ilessio/GOAT-sdk-py/wiki/Getting-Started)
- [Plugin Guide](https://github.com/ilessio/GOAT-sdk-py/wiki/Plugin-Guide)
- [AI Integration](https://github.com/ilessio/GOAT-sdk-py/wiki/AI-Integration)
- [API Reference](https://github.com/ilessio/GOAT-sdk-py/wiki/API-Reference)

## License 📄

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments 👏

This project is an unofficial Python implementation of the [GOAT SDK](https://github.com/goat-sdk/goat), bringing its capabilities to the Python ecosystem. Special thanks to the original GOAT SDK team for their innovative work.

---

<div align="center">
Made with 🐐 by Igor Lessio

[Star on GitHub](https://github.com/ilessio/GOAT-sdk-py) | [Report Bug](https://github.com/ilessio/GOAT-sdk-py/issues) | [Request Feature](https://github.com/ilessio/GOAT-sdk-py/issues)
</div>
