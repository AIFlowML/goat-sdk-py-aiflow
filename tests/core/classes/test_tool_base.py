"""Tests for the ToolBase class."""

import pytest
from typing import Any, Dict, Optional

from goat_sdk.core.classes.tool_base import ToolBase

class MockTool(ToolBase):
    """Mock tool for testing."""
    def execute(self) -> str:
        """Mock execute method."""
        return "executed"

class ValidatedTool(ToolBase):
    """Tool that validates its parameters."""
    def execute(self) -> str:
        """Mock execute method."""
        return "executed"
        
    def validate_parameters(self, params: Dict[str, Any]) -> None:
        """Validate that 'required' parameter is present."""
        if "required" not in params:
            raise ValueError("Missing required parameter")

def test_tool_name():
    """Test that tool name is correctly generated."""
    tool = MockTool()
    assert tool.name == "mock_tool"

def test_tool_description():
    """Test that tool description is correctly set."""
    tool = MockTool()
    assert tool.description == "Mock tool for testing."
    
    # Test tool with no docstring
    class NoDocTool(ToolBase):
        def execute(self) -> None:
            pass
            
    tool = NoDocTool()
    assert tool.description == ""

def test_tool_execution():
    """Test tool execution."""
    tool = MockTool.create()
    assert tool.execute() == "executed"

def test_parameter_validation():
    """Test parameter validation."""
    # Test with no parameters
    tool = ValidatedTool.create()
    assert tool.parameters == {}
    
    # Test with valid parameters
    params = {"required": True}
    tool = ValidatedTool.create(params)
    assert tool.parameters == params
    
    # Test with invalid parameters
    with pytest.raises(ValueError):
        ValidatedTool.create({"optional": True})
