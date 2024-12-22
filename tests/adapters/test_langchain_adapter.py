"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
     
     Path: examples/adapters/langchain_example.py
"""

"""Tests for the Langchain adapter example."""

import pytest
from unittest.mock import Mock, AsyncMock
from langchain.tools import Tool
from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.adapters.langchain import get_on_chain_tools, create_langchain_tool

@pytest.fixture
def mock_tool():
    """Create a mock GOAT SDK tool."""
    tool = Mock(spec=ToolBase)
    tool.name = "test_tool"
    tool.description = "A test tool"
    tool.execute = AsyncMock(return_value="Tool executed")
    return tool

@pytest.fixture
def mock_plugin():
    """Create a mock plugin."""
    plugin = Mock()
    plugin.get_tools = AsyncMock()
    return plugin

@pytest.mark.asyncio
async def test_tool_creation(mock_tool):
    """Test creating a Langchain tool from a GOAT SDK tool."""
    langchain_tool = create_langchain_tool(mock_tool)
    assert isinstance(langchain_tool, Tool)
    assert langchain_tool.name == "test_tool"
    assert langchain_tool.description == "A test tool"

@pytest.mark.asyncio
async def test_tool_execution(mock_tool):
    """Test executing a Langchain tool."""
    langchain_tool = create_langchain_tool(mock_tool)
    result = await langchain_tool.arun('{"param1": "test", "param2": 123}')
    assert result == "Tool executed"
    mock_tool.execute.assert_called_once_with({"param1": "test", "param2": 123})

@pytest.mark.asyncio
async def test_get_on_chain_tools(mock_plugin, mock_tool):
    """Test getting Langchain tools from plugins."""
    mock_plugin.get_tools.return_value = [mock_tool]
    tools = await get_on_chain_tools(plugins=[mock_plugin])
    assert len(tools) == 1
    assert isinstance(tools[0], Tool)
    assert tools[0].name == "test_tool"

@pytest.mark.asyncio
async def test_tool_error_handling(mock_tool):
    """Test error handling in tool execution."""
    mock_tool.execute = AsyncMock(side_effect=ValueError("Test error"))
    langchain_tool = create_langchain_tool(mock_tool)
    with pytest.raises(ValueError, match="Tool execution failed: Test error"):
        await langchain_tool.arun('{"param1": "test", "param2": 123}')

@pytest.mark.asyncio
async def test_sync_execution_not_supported(mock_tool):
    """Test that synchronous execution is not supported."""
    langchain_tool = create_langchain_tool(mock_tool)
    with pytest.raises(NotImplementedError, match="GOAT SDK tools only support async execution"):
        langchain_tool.run('{"param1": "test", "param2": 123}')

@pytest.mark.asyncio
async def test_async_execution(mock_tool):
    """Test async execution through Langchain's arun method."""
    langchain_tool = create_langchain_tool(mock_tool)
    result = await langchain_tool.arun('{"param1": "test", "param2": 123}')
    assert result == "Tool executed"
    mock_tool.execute.assert_called_once_with({"param1": "test", "param2": 123})
