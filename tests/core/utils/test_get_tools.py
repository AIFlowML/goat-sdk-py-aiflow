"""Tests for get_tools utility."""

import pytest
import logging
from pydantic import BaseModel

from goat_sdk.core.decorators.tool import Tool
from goat_sdk.core.utils.get_tools import get_tools

logger = logging.getLogger(__name__)


class TestParams(BaseModel):
    """Test parameters model."""
    value: str


class ToolTestClass:
    """Test class with tools."""
    
    @Tool(description="Test tool")
    async def test_tool(self, params: TestParams) -> str:
        """Test tool method."""
        logger.debug(f"Executing test_tool with params: {params}")
        return f"test_{params.value}"
    
    @Tool(description="Another test tool")
    async def another_test_tool(self, params: TestParams) -> str:
        """Another test tool method."""
        logger.debug(f"Executing another_test_tool with params: {params}")
        return f"another_{params.value}"
    
    def not_a_tool(self) -> str:
        """Not a tool method."""
        logger.debug("Executing not_a_tool method")
        return "not_a_tool"


def test_get_tools():
    """Test get_tools function."""
    logger.info("Testing get_tools function")
    
    logger.debug("Creating test class instance")
    test_class = ToolTestClass()
    
    logger.debug("Getting tools from test class")
    tools = get_tools(test_class)
    
    logger.debug(f"Found {len(tools)} tools")
    assert len(tools) == 2
    
    tool_names = [tool["name"] for tool in tools]
    logger.debug(f"Tool names: {tool_names}")
    
    # Verify tool names
    logger.debug("Verifying tool names")
    assert "test_tool" in tool_names
    assert "another_test_tool" in tool_names
    assert "not_a_tool" not in tool_names
    logger.debug("Tool names verified")
    
    # Test tool metadata
    logger.debug("Testing tool metadata")
    
    # Verify test_tool
    logger.debug("Verifying test_tool metadata")
    test_tool = next(tool for tool in tools if tool["name"] == "test_tool")
    assert test_tool["description"] == "Test tool"
    assert "parameters" in test_tool
    logger.debug(f"test_tool metadata verified: {test_tool}")
    
    # Verify another_test_tool
    logger.debug("Verifying another_test_tool metadata")
    another_test_tool = next(tool for tool in tools if tool["name"] == "another_test_tool")
    assert another_test_tool["description"] == "Another test tool"
    assert "parameters" in another_test_tool
    logger.debug(f"another_test_tool metadata verified: {another_test_tool}")
    
    logger.info("get_tools test completed successfully")
