"""Utility function to get tools from plugins."""

from typing import List, TypeVar, Any
from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.classes.tool_base import ToolBase

TWalletClient = TypeVar('TWalletClient', bound=WalletClientBase)

async def get_tools(
    wallet: TWalletClient,
    plugins: List[Any]
) -> List[ToolBase]:
    """Get tools from plugins.
    
    This function collects tools from all provided plugins.
    Each plugin's get_tools method is called with the wallet client.
    
    Args:
        wallet: Wallet client instance for blockchain interactions
        plugins: List of plugin instances
        
    Returns:
        List of tools from all plugins
        
    Example:
        ```python
        tools = await get_tools(wallet=sdk, plugins=[erc20_plugin])
        ```
    """
    tools: List[ToolBase] = []
    for plugin in plugins:
        plugin_tools = await plugin.get_tools()
        tools.extend(plugin_tools)
    return tools
