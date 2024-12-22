"""Tests for the Langchain adapter."""

import pytest
from unittest.mock import Mock, AsyncMock
from langchain.tools import BaseTool
from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.adapters.langchain import get_on_chain_tools, GoatTool

@pytest.fixture
def mock_tool():
    """Create a mock GOAT SDK tool."""
    tool = Mock(spec=ToolBase)
    tool.name = "test_tool"
    tool.description = "A test tool"
    tool.parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        }
    }
    tool.execute = AsyncMock(return_value="Tool executed")
    return tool

@pytest.fixture
def mock_wallet():
    """Create a mock wallet client."""
    wallet = Mock(spec=WalletClientBase)
    wallet.provider_url = "https://test.network"
    wallet.private_key = "0x123"
    return wallet

@pytest.mark.asyncio
async def test_goat_tool_creation(mock_tool):
    """Test creating a Langchain tool from a GOAT SDK tool."""
    # Create GoatTool
    langchain_tool = GoatTool(mock_tool)

    # Check tool properties
    assert isinstance(langchain_tool, BaseTool)
    assert langchain_tool.name == "test_tool"
    assert langchain_tool.description == "A test tool"
    assert langchain_tool.args_schema == mock_tool.parameters

@pytest.mark.asyncio
async def test_goat_tool_execution(mock_tool):
    """Test executing a Langchain tool."""
    # Create GoatTool
    langchain_tool = GoatTool(mock_tool)

    # Execute tool
    result = await langchain_tool._execute(param1="test", param2=123)

    # Check execution
    assert result == "Tool executed"
    mock_tool.execute.assert_called_once_with({"param1": "test", "param2": 123})

@pytest.mark.asyncio
async def test_get_on_chain_tools(mock_wallet, mock_tool):
    """Test getting Langchain tools from plugins."""
    # Create mock plugin
    mock_plugin = Mock()
    mock_plugin.get_tools = AsyncMock(return_value=[mock_tool])

    # Get tools
    tools = await get_on_chain_tools(wallet=mock_wallet, plugins=[mock_plugin])

    # Check tools
    assert len(tools) == 1
    assert isinstance(tools[0], GoatTool)
    assert tools[0].name == "test_tool"

@pytest.mark.asyncio
async def test_tool_error_handling(mock_tool):
    """Test error handling in tool execution."""
    # Make tool raise an error
    mock_tool.execute = AsyncMock(side_effect=ValueError("Test error"))

    # Create GoatTool
    langchain_tool = GoatTool(mock_tool)

    # Execute tool and check error handling
    with pytest.raises(ValueError, match="Tool execution failed: Test error"):
        await langchain_tool._execute(param1="test", param2=123)

@pytest.mark.asyncio
async def test_sync_execution_not_supported(mock_tool):
    """Test that synchronous execution is not supported."""
    # Create GoatTool
    langchain_tool = GoatTool(mock_tool)

    # Check that sync execution raises error
    with pytest.raises(NotImplementedError, match="GOAT SDK tools only support async execution"):
        langchain_tool._run(param1="test", param2=123)

@pytest.mark.asyncio
async def test_async_execution(mock_tool):
    """Test async execution through Langchain's _arun method."""
    # Create GoatTool
    langchain_tool = GoatTool(mock_tool)

    # Execute tool through _arun
    result = await langchain_tool._arun(param1="test", param2=123)

    # Check execution
    assert result == "Tool executed"
    mock_tool.execute.assert_called_once_with({"param1": "test", "param2": 123})
