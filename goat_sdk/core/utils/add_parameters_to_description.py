"""Utility for adding parameter descriptions to function docstrings."""
from typing import Dict, Any, Optional


def add_parameters_to_description(description: str, parameters: Optional[Dict[str, Any]] = None) -> str:
    """Add parameter descriptions to a function description.
    
    Args:
        description: Base function description
        parameters: Parameter schema dictionary
        
    Returns:
        Description with added parameter information
    """
    if parameters is None:
        return description
        
    if not parameters.get('properties'):
        return description + "\n\nParameters:"
        
    result = [description, "\nParameters:"]
    
    properties = parameters.get('properties', {})
    required = parameters.get('required', [])
    
    for name, schema in sorted(properties.items()):
        param_desc = schema.get('description', 'No description')
        param_type = schema.get('type', 'any')
        is_required = name in required
        
        param_line = f"{name}"
        if is_required:
            param_line += " (required)"
        param_line += f": {param_desc} (type: {param_type})"
        
        result.append(param_line)
        
    return "\n".join(result)
