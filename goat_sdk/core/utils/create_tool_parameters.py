"""Utility for creating tool parameters."""
from typing import Dict, Any, Optional, Type, List, Union
from pydantic import BaseModel, create_model


def create_tool_parameters(
    name: str,
    description: str,
    version: str = "1.0.0",
    model: Optional[Type[BaseModel]] = None,
    additional_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a dictionary of tool parameters.
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        version: Version of the tool (default: "1.0.0")
        model: Optional Pydantic model for parameters
        additional_params: Optional additional parameters to include
        
    Returns:
        Dictionary containing tool metadata and parameter schema
    """
    parameters: Dict[str, Any] = {
        "properties": {},
        "required": []
    }
    
    if model:
        schema = model.model_json_schema()
        parameters["properties"].update(schema.get("properties", {}))
        parameters["required"].extend(schema.get("required", []))
        
    if additional_params:
        for param_name, param_info in additional_params.items():
            param_type = param_info.get("type", "any")
            param_desc = param_info.get("description", "")
            param_required = param_info.get("required", False)
            
            parameters["properties"][param_name] = {
                "type": param_type,
                "description": param_desc
            }
            
            if param_required:
                parameters["required"].append(param_name)
                
    return {
        "name": name,
        "description": description,
        "version": version,
        "parameters": parameters
    }
