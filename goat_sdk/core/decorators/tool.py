"""Tool decorator for marking methods as tools."""
import functools
import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, Union

T = TypeVar("T", bound=Callable[..., Any])


class Tool:
    """Class representing a tool with metadata."""

    def __init__(self, description: str = "", name: Optional[str] = None):
        """Initialize a tool.
        
        Args:
            description: A description of what the tool does
            name: Optional override for the tool name
        """
        self.description = description
        self.name = name

    def __call__(self, func: T) -> T:
        """Make the Tool class callable as a decorator.
        
        Args:
            func: The function to decorate
            
        Returns:
            The decorated function
        """
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)
        
        wrapper.__tool__ = {
            "description": self.description,
            "name": self.name or func.__name__,
            "parameters": self._get_parameters(func)
        }
        return wrapper

    def _get_parameters(self, func: Callable) -> Dict[str, Any]:
        """Get the parameters of a function.
        
        Args:
            func: The function to get parameters from
            
        Returns:
            A dictionary containing parameter information
        """
        sig = inspect.signature(func)
        parameters = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            parameters[name] = {
                "type": str(param.annotation),
                "default": None if param.default == inspect.Parameter.empty else param.default
            }
        return parameters


def get_tool_metadata(func: Union[Callable, Any]) -> Optional[Dict[str, Any]]:
    """Get the tool metadata from a function.
    
    Args:
        func: The function to get metadata from
        
    Returns:
        A dictionary containing the tool metadata, or None if the function is not a tool
    """
    return getattr(func, "__tool__", None)


def tool(description: str = "", name: Optional[str] = None) -> Callable[[T], T]:
    """Decorator to mark a method as a tool.
    
    Args:
        description: A description of what the tool does
        name: Optional override for the tool name
        
    Returns:
        A decorator function
    """
    return Tool(description=description, name=name)
