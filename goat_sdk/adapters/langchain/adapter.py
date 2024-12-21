"""Langchain adapter implementation for GOAT SDK."""

from typing import List, TypeVar
from langchain.tools import Tool
from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.utils.get_tools import get_tools
from .tool import GoatTool

TWalletClient = TypeVar('TWalletClient', bound=WalletClientBase)

async def get_on_chain_tools(
    wallet: TWalletClient,
    plugins: List[any]
) -> List[Tool]:
    """Get Langchain tools from GOAT SDK plugins.
    
    This function converts GOAT SDK tools from the provided plugins into
    Langchain-compatible tools. Each tool maintains its original functionality
    while being usable within Langchain's framework.
    
    Args:
        wallet: Wallet client instance for blockchain interactions
        plugins: List of GOAT SDK plugin instances
        
    Returns:
        List of Langchain tools ready for use with agents
        
    Example:
        ```python
        tools = await get_on_chain_tools(wallet=sdk, plugins=[erc20_plugin])
        agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
        ```
    """
    goat_tools = await get_tools(wallet=wallet, plugins=plugins)
    return [GoatTool(tool) for tool in goat_tools]
