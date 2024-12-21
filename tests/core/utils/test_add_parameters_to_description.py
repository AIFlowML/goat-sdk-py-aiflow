"""Tests for add_parameters_to_description utility."""

from goat_sdk.core.utils.add_parameters_to_description import add_parameters_to_description


def test_add_parameters_no_params():
    """Test adding parameters with no parameters provided."""
    description = "Test description"
    result = add_parameters_to_description(description)
    assert result == description


def test_add_parameters_empty_params():
    """Test adding parameters with empty parameters."""
    description = "Test description"
    parameters = {"properties": {}, "required": []}
    result = add_parameters_to_description(description, parameters)
    assert result == description + "\n\nParameters:"


def test_add_parameters_with_params():
    """Test adding parameters with actual parameters."""
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
    result = add_parameters_to_description(description, parameters)
    assert "Test description" in result
    assert "Parameters:" in result
    assert "name (required): The name parameter (type: string)" in result
    assert "age: The age parameter (type: integer)" in result
