"""Tests for the PluginBase class."""

import pytest
import logging
from typing import Any, Dict, Optional

from goat_sdk.core.classes.plugin_base import PluginBase
from goat_sdk.core.classes.tool_base import ToolBase

logger = logging.getLogger(__name__)

class MockTool(ToolBase):
    """Mock tool for testing."""
    def execute(self) -> None:
        """Mock execute method."""
        logger.debug("Executing mock tool")
        pass

class MockPlugin(PluginBase):
    """Mock plugin for testing."""
    def initialize(self, params: Optional[Dict[str, Any]] = None) -> None:
        """Mock initialize method."""
        logger.debug(f"Initializing mock plugin with params: {params}")
        self.params = params or {}
        
    def validate(self) -> None:
        """Mock validate method."""
        logger.debug(f"Validating mock plugin with params: {self.params}")
        if self.params.get("invalid"):
            logger.error("Invalid configuration detected")
            raise ValueError("Invalid configuration")
        logger.debug("Plugin validation successful")

def test_plugin_name():
    """Test that plugin name is correctly generated."""
    logger.info("Testing plugin name generation")
    
    logger.debug("Creating mock plugin")
    plugin = MockPlugin()
    
    logger.debug(f"Verifying plugin name: {plugin.name}")
    assert plugin.name == "mock_plugin"
    
    logger.info("Plugin name test completed successfully")

def test_plugin_initialization():
    """Test plugin initialization."""
    logger.info("Testing plugin initialization")
    
    # Test with no parameters
    logger.debug("Testing initialization with no parameters")
    plugin = MockPlugin.create()
    assert plugin._initialized
    assert plugin.params == {}
    logger.debug("No parameters initialization verified")
    
    # Test with parameters
    logger.debug("Testing initialization with parameters")
    params = {"key": "value"}
    plugin = MockPlugin.create(params)
    assert plugin._initialized
    assert plugin.params == params
    logger.debug(f"Parameters initialization verified: {params}")
    
    # Test with invalid parameters
    logger.debug("Testing initialization with invalid parameters")
    with pytest.raises(ValueError):
        MockPlugin.create({"invalid": True})
    logger.debug("Invalid parameters test verified")
    
    logger.info("Plugin initialization tests completed successfully")

def test_tool_registration():
    """Test tool registration and unregistration."""
    logger.info("Testing tool registration and unregistration")
    
    logger.debug("Creating mock plugin")
    plugin = MockPlugin.create()
    
    # Test registering a tool
    logger.debug("Testing tool registration")
    plugin.register_tool(MockTool)
    assert MockTool in plugin.tools
    assert len(plugin.tools) == 1
    logger.debug("Tool registration verified")
    
    # Test registering the same tool again
    logger.debug("Testing duplicate tool registration")
    with pytest.raises(ValueError):
        plugin.register_tool(MockTool)
    assert len(plugin.tools) == 1
    logger.debug("Duplicate registration prevention verified")
    
    # Test unregistering a tool
    logger.debug("Testing tool unregistration")
    plugin.unregister_tool(MockTool)
    assert MockTool not in plugin.tools
    assert len(plugin.tools) == 0
    logger.debug("Tool unregistration verified")
    
    # Test unregistering a tool that's not registered
    logger.debug("Testing unregistration of non-registered tool")
    with pytest.raises(ValueError):
        plugin.unregister_tool(MockTool)
    logger.debug("Non-registered tool unregistration prevention verified")
    
    logger.info("Tool registration tests completed successfully")

def test_get_tools():
    """Test getting tools from the plugin."""
    logger.info("Testing get_tools functionality")
    
    logger.debug("Creating mock plugin")
    plugin = MockPlugin()
    
    # Test getting tools before initialization
    logger.debug("Testing get_tools before initialization")
    with pytest.raises(ValueError):
        plugin.get_tools()
    logger.debug("Pre-initialization check verified")
    
    # Test getting tools after initialization
    logger.debug("Testing get_tools after initialization")
    plugin.initialize()
    plugin.validate()
    plugin._initialized = True
    plugin.register_tool(MockTool)
    
    tools = plugin.get_tools()
    logger.debug(f"Retrieved {len(tools)} tools")
    assert len(tools) == 1
    assert MockTool in tools
    logger.debug("Tool retrieval verified")
    
    logger.info("get_tools tests completed successfully")
