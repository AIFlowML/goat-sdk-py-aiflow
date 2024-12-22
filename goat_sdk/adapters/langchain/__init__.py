"""Langchain adapter for GOAT SDK.

This adapter allows GOAT SDK tools to be used as Langchain tools, enabling seamless
integration with Langchain agents and chains.

Example:
    ```python
    from goat_sdk import GoatSDK
    from goat_sdk.plugins.ERC20 import ERC20Plugin
    from goat_sdk.adapters.langchain import get_on_chain_tools
    from langchain.agents import AgentType, initialize_agent
    from langchain.chat_models import ChatOpenAI

    # Initialize SDK and plugin
    sdk = GoatSDK(
        private_key="your_private_key",
        provider_url="https://sepolia.mode.network"
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
        "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST'"
    )
    ```
"""

from .adapter import get_on_chain_tools
from .tool import create_langchain_tool

__all__ = ["get_on_chain_tools", "create_langchain_tool"]
