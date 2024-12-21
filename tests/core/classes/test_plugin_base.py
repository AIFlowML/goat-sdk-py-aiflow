"""Tests for the PluginBase class."""

import pytest
from typing import Any, Dict, Optional

from goat_sdk.core.classes.plugin_base import PluginBase
from goat_sdk.core.classes.tool_base import ToolBase

class MockTool(ToolBase):
    """Mock tool for testing."""
    def execute(self) -> None:
        """Mock execute method."""
        pass

class MockPlugin(PluginBase):
    """Mock plugin for testing."""
    def initialize(self, params: Optional[Dict[str, Any]] = None) -> None:
        """Mock initialize method."""
        self.params = params or {}
        
    def validate(self) -> None:
        """Mock validate method."""
        if self.params.get("invalid"):
            raise ValueError("Invalid configuration")

def test_plugin_name():
    """Test that plugin name is correctly generated."""
    plugin = MockPlugin()
    assert plugin.name == "mock_plugin"

def test_plugin_initialization():
    """Test plugin initialization."""
    # Test with no parameters
    plugin = MockPlugin.create()
    assert plugin._initialized
    assert plugin.params == {}
    
    # Test with parameters
    params = {"key": "value"}
    plugin = MockPlugin.create(params)
    assert plugin._initialized
    assert plugin.params == params
    
    # Test with invalid parameters
    with pytest.raises(ValueError):
        MockPlugin.create({"invalid": True})

def test_tool_registration():
    """Test tool registration and unregistration."""
    plugin = MockPlugin.create()
    
    # Test registering a tool
    plugin.register_tool(MockTool)
    assert MockTool in plugin.tools
    assert len(plugin.tools) == 1
    
    # Test registering the same tool again
    with pytest.raises(ValueError):
        plugin.register_tool(MockTool)
    assert len(plugin.tools) == 1
    
    # Test unregistering a tool
    plugin.unregister_tool(MockTool)
    assert MockTool not in plugin.tools
    assert len(plugin.tools) == 0
    
    # Test unregistering a tool that's not registered
    with pytest.raises(ValueError):
        plugin.unregister_tool(MockTool)

def test_get_tools():
    """Test getting tools from the plugin."""
    plugin = MockPlugin()
    
    # Test getting tools before initialization
    with pytest.raises(ValueError):
        plugin.get_tools()
    
    # Test getting tools after initialization
    plugin.initialize()
    plugin.validate()
    plugin._initialized = True
    plugin.register_tool(MockTool)
    
    tools = plugin.get_tools()
    assert len(tools) == 1
    assert MockTool in tools
