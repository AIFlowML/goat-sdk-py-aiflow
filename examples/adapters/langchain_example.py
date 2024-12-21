"""Example of using GOAT SDK with Langchain."""

import os
import asyncio
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin
from goat_sdk.adapters.langchain import get_on_chain_tools

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

    # Get Langchain tools
    tools = await get_on_chain_tools(wallet=sdk, plugins=[erc20_plugin])

    # Initialize Langchain agent
    llm = ChatOpenAI(temperature=0)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Use the agent
    response = await agent.arun(
        "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST' and initial supply of 1000000"
    )
    print(f"\nAgent Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
