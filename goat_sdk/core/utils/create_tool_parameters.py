"""Utility for creating tool parameters."""
from typing import Dict, Any, Optional


def create_tool_parameters(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a dictionary of tool parameters.
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        parameters: Optional dictionary of parameters
        
    Returns:
        Dictionary containing tool metadata
    """
    return {
        "name": name,
        "description": description,
        "parameters": parameters or {}
    }
