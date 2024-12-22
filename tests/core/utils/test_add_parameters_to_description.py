"""Tests for add_parameters_to_description utility."""

import logging
from goat_sdk.core.utils.add_parameters_to_description import add_parameters_to_description

logger = logging.getLogger(__name__)


def test_add_parameters_no_params():
    """Test adding parameters with no parameters provided."""
    logger.info("Testing add_parameters_to_description with no parameters")
    description = "Test description"
    logger.debug(f"Input description: {description}")
    
    result = add_parameters_to_description(description)
    logger.debug(f"Result: {result}")
    
    assert result == description
    logger.info("No parameters test completed successfully")


def test_add_parameters_empty_params():
    """Test adding parameters with empty parameters."""
    logger.info("Testing add_parameters_to_description with empty parameters")
    description = "Test description"
    parameters = {"properties": {}, "required": []}
    logger.debug(f"Input description: {description}")
    logger.debug(f"Input parameters: {parameters}")
    
    result = add_parameters_to_description(description, parameters)
    logger.debug(f"Result: {result}")
    
    assert result == description + "\n\nParameters:"
    logger.info("Empty parameters test completed successfully")


def test_add_parameters_with_params():
    """Test adding parameters with actual parameters."""
    logger.info("Testing add_parameters_to_description with actual parameters")
    description = "Test description"
    parameters = {
        "properties": {
            "name": {
                "type": "string",
                "description": "The name parameter"
            },
            "age": {
                "type": "integer",
                "description": "The age parameter"
            }
        },
        "required": ["name"]
    }
    logger.debug(f"Input description: {description}")
    logger.debug(f"Input parameters: {parameters}")
    
    result = add_parameters_to_description(description, parameters)
    logger.debug(f"Result: {result}")
    
    # Verify each component of the result
    logger.debug("Verifying result components")
    assert "Test description" in result
    logger.debug("Description verified")
    
    assert "Parameters:" in result
    logger.debug("Parameters header verified")
    
    assert "name (required): The name parameter (type: string)" in result
    logger.debug("Name parameter verified")
    
    assert "age: The age parameter (type: integer)" in result
    logger.debug("Age parameter verified")
    
    logger.info("Parameters with actual parameters test completed successfully")
