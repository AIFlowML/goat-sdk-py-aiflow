"""Tests for the ToolBase class."""

import pytest
import logging
from typing import Any, Dict, Optional
from pydantic import Field

from goat_sdk.core.classes.tool_base import ToolBase

logger = logging.getLogger(__name__)


class MockTool(ToolBase):
    """Mock tool for testing."""
    name: str = Field(default="mock_tool")
    description: str = Field(default="Mock tool for testing")
    version: str = Field(default="1.0.0")
    
    async def execute(self, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Mock execute method."""
        logger.debug(f"Executing MockTool with parameters: {parameters}")
        return "executed"


class ValidatedTool(ToolBase):
    """Tool that validates its parameters."""
    name: str = Field(default="validated_tool")
    description: str = Field(default="Tool that validates its parameters")
    version: str = Field(default="1.0.0")
    
    async def execute(self, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Mock execute method."""
        logger.debug(f"Executing ValidatedTool with parameters: {parameters}")
        if parameters:
            logger.debug("Validating parameters")
            self.validate_parameters(parameters)
        return "executed"
        
    def validate_parameters(self, params: Dict[str, Any]) -> None:
        """Validate that 'required' parameter is present."""
        logger.debug(f"Validating parameters: {params}")
        if "required" not in params:
            logger.error("Missing required parameter")
            raise ValueError("Missing required parameter")
        logger.debug("Parameter validation successful")


@pytest.mark.asyncio
async def test_tool_name():
    """Test that tool name is correctly set."""
    logger.info("Testing tool name")
    tool = MockTool()
    logger.debug(f"Created tool with name: {tool.name}")
    assert tool.name == "mock_tool"
    logger.info("Tool name test completed successfully")


@pytest.mark.asyncio
async def test_tool_description():
    """Test that tool description is correctly set."""
    logger.info("Testing tool description")
    
    # Test tool with docstring
    tool = MockTool()
    logger.debug(f"Created tool with description: {tool.description}")
    assert tool.description == "Mock tool for testing"
    
    # Test tool with no docstring
    logger.debug("Testing tool with no docstring")
    class NoDocTool(ToolBase):
        name: str = Field(default="no_doc_tool")
        description: str = Field(default="")
        version: str = Field(default="1.0.0")
        
        async def execute(self, parameters: Optional[Dict[str, Any]] = None) -> None:
            logger.debug(f"Executing NoDocTool with parameters: {parameters}")
            pass
            
    tool = NoDocTool()
    logger.debug(f"Created NoDocTool with description: {tool.description}")
    assert tool.description == ""
    logger.info("Tool description tests completed successfully")


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""
    logger.info("Testing tool execution")
    tool = MockTool()
    logger.debug("Created MockTool for execution test")
    
    result = await tool.execute()
    logger.debug(f"Tool execution result: {result}")
    assert result == "executed"
    logger.info("Tool execution test completed successfully")


@pytest.mark.asyncio
async def test_parameter_validation():
    """Test parameter validation."""
    logger.info("Testing parameter validation")
    
    # Test with no parameters
    logger.debug("Testing execution with no parameters")
    tool = ValidatedTool()
    result = await tool.execute()
    logger.debug(f"Execution result (no parameters): {result}")
    assert result == "executed"
    
    # Test with valid parameters
    logger.debug("Testing execution with valid parameters")
    params = {"required": True}
    tool = ValidatedTool()
    result = await tool.execute(params)
    logger.debug(f"Execution result (valid parameters): {result}")
    assert result == "executed"
    
    # Test with invalid parameters
    logger.debug("Testing execution with invalid parameters")
    tool = ValidatedTool()
    with pytest.raises(ValueError):
        await tool.execute({"optional": True})
    logger.info("Parameter validation tests completed successfully")
