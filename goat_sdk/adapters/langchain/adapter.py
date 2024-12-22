"""Example script showing how to get Langchain tools from GOAT SDK plugins."""

from typing import List
from langchain.tools import Tool
from .tool import create_langchain_tool


async def get_on_chain_tools(plugins: List[any]) -> List[Tool]:
    """Get Langchain tools from GOAT SDK plugins.
    
    Example:
        ```python
        tools = await get_on_chain_tools(plugins=[erc20_plugin])
        agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
        ```
    """
    all_tools = []
    for plugin in plugins:
        tools = await plugin.get_tools()
        all_tools.extend([create_langchain_tool(tool) for tool in tools])
    return all_tools
