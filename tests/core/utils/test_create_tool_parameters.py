"""Tests for create_tool_parameters utility."""

from pydantic import BaseModel
from goat_sdk.core.utils.create_tool_parameters import create_tool_parameters


class TestParams(BaseModel):
    """Test parameter model."""
    name: str
    age: int = 0


def test_create_parameters_no_model():
    """Test creating parameters with no model."""
    result = create_tool_parameters()
    assert result == {
        "type": "object",
        "properties": {},
        "required": [],
    }


def test_create_parameters_with_model():
    """Test creating parameters with a model."""
    result = create_tool_parameters(TestParams)
    assert result["type"] == "object"
    assert "name" in result["properties"]
    assert "age" in result["properties"]
    assert "name" in result["required"]
    assert "age" not in result["required"]


def test_create_parameters_with_additional():
    """Test creating parameters with additional properties."""
    additional = {
        "extra": {
            "type": "string",
            "description": "Extra parameter"
        }
    }
    result = create_tool_parameters(TestParams, additional)
    assert "extra" in result["properties"]
    assert result["properties"]["extra"]["description"] == "Extra parameter"
