"""Phidata adapter for GOAT SDK.

This adapter allows GOAT SDK tools to be used as Phidata toolkits, enabling
integration with Phidata's agent framework.

Example:
    ```python
    from goat_sdk import GoatSDK
    from goat_sdk.plugins.ERC20 import ERC20Plugin
    from goat_sdk.adapters.phidata import get_on_chain_toolkit
    from phidata.llm.openai import OpenAIChat
    from phidata.agent import Agent

    # Initialize SDK and plugin
    sdk = GoatSDK(
        private_key="your_private_key",
        provider_url="https://sepolia.mode.network"
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
        "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST'"
    )
    ```
"""

from .toolkit import GoatToolkit
from .adapter import get_on_chain_toolkit

__all__ = ["GoatToolkit", "get_on_chain_toolkit"]
