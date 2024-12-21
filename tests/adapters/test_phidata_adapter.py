"""Tests for the Phidata adapter."""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock

# Mock phidata module
class MockToolkit:
    def __init__(self, name="mock_toolkit"):
        self.name = name

    def add_function(self, name, func):
        setattr(self, name, func)

# Mock phidata.core.toolkit module
class MockPhidataCore:
    Toolkit = MockToolkit

import sys
sys.modules['phidata'] = MagicMock()
sys.modules['phidata.core'] = MockPhidataCore
sys.modules['phidata.core.toolkit'] = MagicMock(Toolkit=MockToolkit)

from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.adapters.phidata import get_on_chain_toolkit, GoatToolkit

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
async def test_goat_toolkit_creation(mock_tool):
    """Test creating a Phidata toolkit from GOAT SDK tools."""
    # Create toolkit
    toolkit = GoatToolkit([mock_tool])

    # Check toolkit properties
    assert isinstance(toolkit, MockToolkit)
    assert toolkit.name == "goat_toolkit"
    assert hasattr(toolkit, f"execute_{mock_tool.name}")

@pytest.mark.asyncio
async def test_goat_toolkit_execution(mock_tool):
    """Test executing a tool in the toolkit."""
    # Create toolkit
    toolkit = GoatToolkit([mock_tool])

    # Execute tool
    result = await getattr(toolkit, f"execute_{mock_tool.name}")(param1="test", param2=123)
    assert result == "Tool executed"
    mock_tool.execute.assert_called_once_with(param1="test", param2=123)

@pytest.mark.asyncio
async def test_get_on_chain_toolkit(mock_wallet, mock_tool):
    """Test getting Phidata toolkit from plugins."""
    # Create toolkit
    toolkit = await get_on_chain_toolkit(mock_wallet)

    # Check toolkit properties
    assert isinstance(toolkit, MockToolkit)
    assert toolkit.name == "goat_toolkit"

@pytest.mark.asyncio
async def test_toolkit_error_handling(mock_tool):
    """Test error handling in toolkit execution."""
    # Set up mock to raise error
    error_message = "Test error"
    mock_tool.execute.side_effect = Exception(error_message)

    # Create toolkit
    toolkit = GoatToolkit([mock_tool])

    # Execute tool and check error handling
    with pytest.raises(Exception, match=error_message):
        await getattr(toolkit, f"execute_{mock_tool.name}")()

@pytest.mark.asyncio
async def test_toolkit_multiple_tools(mock_tool):
    """Test toolkit with multiple tools."""
    # Create multiple mock tools
    tool1 = mock_tool
    tool2 = Mock(spec=ToolBase)
    tool2.name = "test_tool_2"
    tool2.description = "Another test tool"
    tool2.parameters = {"type": "object"}
    tool2.execute = AsyncMock(return_value="Tool 2 executed")

    # Create toolkit with multiple tools
    toolkit = GoatToolkit([tool1, tool2])

    # Check both tools are accessible
    assert hasattr(toolkit, f"execute_{tool1.name}")
    assert hasattr(toolkit, f"execute_{tool2.name}")

    # Execute both tools
    result1 = await getattr(toolkit, f"execute_{tool1.name}")()
    result2 = await getattr(toolkit, f"execute_{tool2.name}")()

    assert result1 == "Tool executed"
    assert result2 == "Tool 2 executed"

@pytest.mark.asyncio
async def test_toolkit_function_metadata(mock_tool):
    """Test that tool executor functions have correct metadata."""
    toolkit = GoatToolkit([mock_tool])
    
    # Get function
    func = getattr(toolkit, f"execute_{mock_tool.name}")
    
    # Check metadata
    assert func.__doc__ == mock_tool.description
    assert hasattr(func, "__parameters__")
    assert func.__parameters__ == mock_tool.parameters
