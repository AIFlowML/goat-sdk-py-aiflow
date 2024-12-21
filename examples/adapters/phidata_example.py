"""Example of using GOAT SDK with Phidata."""

import os
import asyncio
from dotenv import load_dotenv
from phi.llm.openai import OpenAIChat
from phi.agent import Agent
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin
from goat_sdk.adapters.phidata import get_on_chain_toolkit

# Load environment variables
load_dotenv()

async def main():
    """Run the example."""
    # Initialize SDK and plugin
    sdk = GoatSDK(
        private_key=os.getenv("PRIVATE_KEY"),
        provider_url=os.getenv("MODE_RPC_URL")
    )
    erc20_plugin = ERC20Plugin(sdk)

    # Get Phidata toolkit
    toolkit = await get_on_chain_toolkit(wallet=sdk, plugins=[erc20_plugin])

    # Initialize Phidata agent
    llm = OpenAIChat()
    agent = Agent(
        name="blockchain_agent",
        llm=llm,
        toolkits=[toolkit],
        show_tool_calls=True
    )

    # Use the agent
    response = await agent.run(
        "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST' and initial supply of 1000000"
    )
    print(f"\nAgent Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
