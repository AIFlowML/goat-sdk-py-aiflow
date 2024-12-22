"""Tests for get_tools utility."""

from typing import Dict, Any
from pydantic import BaseModel
from goat_sdk.core.decorators import Tool
from goat_sdk.core.utils.get_tools import get_tools


class TestParams(BaseModel):
    """Test parameter model."""
    name: str


class ToolTestClass:
    """Test class with tools."""

    @Tool(description="Test tool")
    def test_tool(self, params: TestParams) -> Dict[str, Any]:
        """Test tool method."""
        return {"name": params.name}

    @Tool(description="Another test tool")
    def another_tool(self, params: TestParams) -> Dict[str, Any]:
        """Another test tool method."""
        return {"name": params.name}

    def not_a_tool(self) -> None:
        """Not a tool method."""
        pass

    @Tool(description="Private tool")
    def _private_tool(self, params: TestParams) -> Dict[str, Any]:
        """Private tool method."""
        return {"name": params.name}


def test_get_tools():
    """Test getting tools from a class."""
    tools = get_tools(ToolTestClass)
    assert len(tools) == 2
    assert any(t["name"] == "test_tool" for t in tools)
    assert any(t["name"] == "another_tool" for t in tools)
    assert not any(t["name"] == "_private_tool" for t in tools)


def test_get_tools_with_private():
    """Test getting tools including private methods."""
    tools = get_tools(ToolTestClass, include_private=True)
    assert len(tools) == 3
    assert any(t["name"] == "_private_tool" for t in tools)


def test_tool_metadata():
    """Test tool metadata structure."""
    tools = get_tools(ToolTestClass)
    tool = next(t for t in tools if t["name"] == "test_tool")
    assert "description" in tool
    assert "parameters" in tool
    assert tool["parameters"]["type"] == "object"
    assert "name" in tool["parameters"]["properties"]
