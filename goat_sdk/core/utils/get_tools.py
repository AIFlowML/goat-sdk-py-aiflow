"""Utility for getting tool instances from a class."""
from typing import List, Any, Dict
from inspect import getmembers, ismethod
from goat_sdk.core.classes.tool_base import ToolBase


def get_tools(instance: Any) -> List[Dict[str, Any]]:
    """Get all tool instances from a class instance.
    
    Args:
        instance: Class instance to get tools from
        
    Returns:
        List of tool dictionaries with name, description, and parameters
    """
    tools = []
    
    # Get all methods that are marked as tools
    for name, method in getmembers(instance, predicate=ismethod):
        if hasattr(method, '__tool__'):
            tool_metadata = method.__tool__
            tools.append(tool_metadata)
    
    return tools
