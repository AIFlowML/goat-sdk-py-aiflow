"""Example script showing how to get Phidata toolkit from GOAT SDK plugins."""

from typing import List
from phidata.core.toolkit import Toolkit
from .toolkit import create_phidata_toolkit


async def get_on_chain_toolkit(plugins: List[any]) -> Toolkit:
    """Get Phidata toolkit from GOAT SDK plugins.
    
    Example:
        ```python
        toolkit = await get_on_chain_toolkit(plugins=[erc20_plugin])
        agent = Agent(name="blockchain_agent", toolkits=[toolkit])
        ```
    """
    all_tools = []
    for plugin in plugins:
        tools = await plugin.get_tools()
        all_tools.extend(tools)
    return create_phidata_toolkit(all_tools)
