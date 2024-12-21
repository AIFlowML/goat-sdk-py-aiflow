# GOAT SDK Examples

This directory contains example applications demonstrating the usage of the GOAT SDK.

## Examples

### Mode Network Examples

1. **[Token Creation](mode/token_creation)**: Create and deploy ERC20 tokens on Mode Network
   - Basic token deployment
   - Token with custom parameters
   - Token with vesting schedule

2. **[Token Management](mode/token_management)**: Manage existing ERC20 tokens
   - Token transfers
   - Allowance management
   - Balance checking

3. **[DEX Integration](mode/dex_integration)**: Interact with decentralized exchanges
   - Uniswap integration
   - Liquidity provision
   - Token swaps

### Solana Examples

1. **[SPL Token](solana/spl_token)**: Create and manage SPL tokens
   - Token creation
   - Token minting
   - Token transfers

2. **[NFT Creation](solana/nft_creation)**: Create and manage NFTs
   - Basic NFT minting
   - Collection creation
   - Metadata management

## Running the Examples

Each example directory contains:
- README with specific instructions
- Requirements file
- Source code
- Configuration templates

### Prerequisites

- Python 3.11+
- GOAT SDK installed
- Network-specific requirements (e.g., Mode testnet tokens, Solana devnet tokens)

### General Setup

1. Clone the repository:
```bash
git clone https://github.com/goat-sdk/python-goat.git
cd python-goat
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Example-Specific Setup

Each example has its own README with specific setup instructions. Generally:

1. Navigate to example directory:
```bash
cd examples/[network]/[example]
```

2. Install example-specific dependencies:
```bash
pip install -r requirements.txt
```

3. Configure example:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the example:
```bash
python main.py
```

## Contributing

Feel free to contribute your own examples! Please follow our [contribution guidelines](../CONTRIBUTING.md).
