"""Tests for create_tool_parameters utility."""

import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from goat_sdk.core.utils.create_tool_parameters import create_tool_parameters

logger = logging.getLogger(__name__)


class TestParams(BaseModel):
    """Test parameter model."""
    name: str = Field(description="The name parameter")
    age: int = Field(default=0, description="The age parameter")


def test_create_parameters_no_model():
    """Test creating parameters with no model."""
    logger.info("Testing create_tool_parameters with no model")
    
    logger.debug("Creating parameters with basic tool info")
    result = create_tool_parameters(
        name="test_tool",
        description="A test tool",
        version="1.0.0"
    )
    logger.debug(f"Created parameters: {result}")
    
    # Verify basic tool info
    logger.debug("Verifying basic tool info")
    assert result["name"] == "test_tool"
    assert result["description"] == "A test tool"
    assert result["version"] == "1.0.0"
    
    # Verify parameter structure
    logger.debug("Verifying parameter structure")
    assert "parameters" in result
    assert "properties" in result["parameters"]
    assert "required" in result["parameters"]
    
    logger.info("No model test completed successfully")


def test_create_parameters_with_model():
    """Test creating parameters with a model."""
    logger.info("Testing create_tool_parameters with model")
    
    logger.debug("Creating parameters with TestParams model")
    result = create_tool_parameters(
        name="test_tool",
        description="A test tool",
        version="1.0.0",
        model=TestParams
    )
    logger.debug(f"Created parameters: {result}")
    
    # Verify basic tool info
    logger.debug("Verifying basic tool info")
    assert result["name"] == "test_tool"
    assert result["description"] == "A test tool"
    assert result["version"] == "1.0.0"
    
    # Verify parameter structure
    logger.debug("Verifying parameter structure")
    assert "parameters" in result
    assert "properties" in result["parameters"]
    
    # Verify model properties
    logger.debug("Verifying model properties")
    assert "name" in result["parameters"]["properties"]
    assert "age" in result["parameters"]["properties"]
    assert result["parameters"]["properties"]["name"]["description"] == "The name parameter"
    assert result["parameters"]["properties"]["age"]["description"] == "The age parameter"
    
    # Verify required fields
    logger.debug("Verifying required fields")
    assert "name" in result["parameters"]["required"]
    assert "age" not in result["parameters"]["required"]
    
    logger.info("Model test completed successfully")


def test_create_parameters_with_additional():
    """Test creating parameters with additional properties."""
    logger.info("Testing create_tool_parameters with additional properties")
    
    # Define additional parameters
    logger.debug("Defining additional parameters")
    additional_params: Dict[str, Any] = {
        "extra": {
            "type": "string",
            "description": "Extra parameter",
            "required": True
        }
    }
    logger.debug(f"Additional parameters: {additional_params}")
    
    # Create parameters
    logger.debug("Creating parameters with additional properties")
    result = create_tool_parameters(
        name="test_tool",
        description="A test tool",
        version="1.0.0",
        additional_params=additional_params
    )
    logger.debug(f"Created parameters: {result}")
    
    # Verify basic tool info
    logger.debug("Verifying basic tool info")
    assert result["name"] == "test_tool"
    assert result["description"] == "A test tool"
    assert result["version"] == "1.0.0"
    
    # Verify parameter structure
    logger.debug("Verifying parameter structure")
    assert "parameters" in result
    assert "properties" in result["parameters"]
    
    # Verify additional properties
    logger.debug("Verifying additional properties")
    assert "extra" in result["parameters"]["properties"]
    assert result["parameters"]["properties"]["extra"]["description"] == "Extra parameter"
    assert "extra" in result["parameters"]["required"]
    
    logger.info("Additional properties test completed successfully")
