"""Utility for adding parameters to tool descriptions."""
from typing import Dict, Any


def add_parameters_to_description(description: str, parameters: Dict[str, Any]) -> str:
    """Add parameters to a tool description.
    
    Args:
        description: The base description
        parameters: Dictionary of parameters and their values
        
    Returns:
        Description with parameters appended
    """
    if not parameters:
        return description

    param_str = ", ".join(f"{k}={v}" for k, v in parameters.items())
    return f"{description} (Parameters: {param_str})"
