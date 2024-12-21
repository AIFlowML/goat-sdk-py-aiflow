"""Decorators for Mode SDK."""

from typing import Any, Callable, Dict, Optional
from functools import wraps


def tool(description: str) -> Callable:
    """Decorator to mark a method as a tool.
    
    Args:
        description: Tool description
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)
        
        # Add tool metadata
        wrapper.__tool__ = {
            "description": description,
        }
        return wrapper
    return decorator 