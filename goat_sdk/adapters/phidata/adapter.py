"""Phidata adapter implementation for GOAT SDK."""

from typing import List, TypeVar
from phidata.core.toolkit import Toolkit
from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.utils.get_tools import get_tools
from .toolkit import GoatToolkit

TWalletClient = TypeVar('TWalletClient', bound=WalletClientBase)

async def get_on_chain_toolkit(
    wallet: TWalletClient,
    plugins: List[any]
) -> Toolkit:
    """Get Phidata toolkit from GOAT SDK plugins.
    
    This function converts GOAT SDK tools from the provided plugins into a
    Phidata-compatible toolkit. The toolkit maintains all tool functionality
    while being usable within Phidata's framework.
    
    Args:
        wallet: Wallet client instance for blockchain interactions
        plugins: List of GOAT SDK plugin instances
        
    Returns:
        Phidata toolkit ready for use with agents
        
    Example:
        ```python
        toolkit = await get_on_chain_toolkit(wallet=sdk, plugins=[erc20_plugin])
        agent = Agent(name="blockchain_agent", toolkits=[toolkit])
        ```
    """
    goat_tools = await get_tools(wallet=wallet, plugins=plugins)
    return GoatToolkit(goat_tools)
