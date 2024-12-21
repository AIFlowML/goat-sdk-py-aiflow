"""
Custom token deployment example using GOAT SDK.
"""
import os
import asyncio
import argparse
from dotenv import load_dotenv
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin, DeployTokenParams

# Load environment variables
load_dotenv()

async def deploy_custom_token(name: str, symbol: str, supply: int):
    """Deploy a custom ERC20 token with specified parameters."""
    # Initialize SDK with Mode Network
    sdk = GoatSDK(
        private_key=os.getenv("PRIVATE_KEY"),
        provider_url=os.getenv("MODE_RPC_URL")
    )

    # Initialize ERC20 plugin
    erc20 = ERC20Plugin(sdk)

    try:
        # Validate parameters
        if not name or not symbol or supply <= 0:
            raise ValueError("Invalid parameters. Name and symbol must not be empty, and supply must be positive.")

        # Deploy token with custom parameters
        print(f"\nDeploying token '{name}' ({symbol}) with supply {supply}...")
        result = await erc20.deploy_token(DeployTokenParams(
            name=name,
            symbol=symbol,
            initial_supply=supply
        ))

        # Print results
        print("\nToken Deployment Successful!")
        print("----------------------------")
        print(f"Token Name: {name}")
        print(f"Token Symbol: {symbol}")
        print(f"Initial Supply: {supply}")
        print(f"Contract Address: {result.contract_address}")
        print(f"Transaction Hash: {result.transaction_hash}")
        print(f"Explorer URL: {result.explorer_url}")

        return result

    except Exception as e:
        print("\nToken Deployment Failed!")
        print("------------------------")
        print(f"Error: {str(e)}")
        return None

def main():
    """Parse arguments and deploy token."""
    parser = argparse.ArgumentParser(description="Deploy a custom ERC20 token on Mode Network")
    parser.add_argument("--name", required=True, help="Token name")
    parser.add_argument("--symbol", required=True, help="Token symbol")
    parser.add_argument("--supply", type=int, required=True, help="Initial token supply")

    args = parser.parse_args()
    asyncio.run(deploy_custom_token(args.name, args.symbol, args.supply))

if __name__ == "__main__":
    main()
