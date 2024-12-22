"""Tool decorator for marking methods as tools."""
import functools
import inspect
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union, get_type_hints, Type
from pydantic import BaseModel, create_model, ValidationError

from goat_sdk.core.utils.create_tool_parameters import create_tool_parameters
from goat_sdk.core.classes.wallet_client_base import WalletClientBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Any])


class Tool:
    """Class representing a tool with metadata."""

    def __init__(self, description: str = "", name: Optional[str] = None, model: Optional[Type[BaseModel]] = None):
        """Initialize a tool.
        
        Args:
            description: A description of what the tool does
            name: Optional override for the tool name
            model: Optional Pydantic model for parameters
        """
        logger.debug(f"Initializing Tool with description='{description}', name='{name}', model={model}")
        self.description = description
        self.name = name
        self.model = model

    def __call__(self, func: T) -> T:
        """Make the Tool class callable as a decorator.
        
        Args:
            func: The function to decorate
            
        Returns:
            The decorated function
            
        Raises:
            ValueError: If the function is not async or has no parameters
        """
        logger.debug(f"Decorating function {func.__name__}")
        
        if not inspect.iscoroutinefunction(func):
            logger.error(f"Function {func.__name__} is not async")
            raise ValueError(f"Tool {func.__name__} must be an async function")
            
        # Check if function has parameters
        sig = inspect.signature(func)
        params = [p for p in sig.parameters.values() if p.name != "self"]
        logger.debug(f"Function {func.__name__} has parameters: {[p.name for p in params]}")
        
        if not params:
            logger.error(f"Function {func.__name__} has no parameters")
            raise ValueError(f"Tool {func.__name__} must have parameters")
            
        # Validate parameter types
        type_hints = get_type_hints(func)
        for param in params:
            param_type = type_hints.get(param.name, Any)
            if param_type != Any and not (
                inspect.isclass(param_type) and 
                issubclass(param_type, (BaseModel, WalletClientBase))
            ):
                logger.error(f"Parameter {param.name} has invalid type {param_type}")
                raise ValueError(f"Tool {func.__name__} parameters must be Pydantic models or wallet clients")
            
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.debug(f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
            
            # Get the first argument (self) if it exists
            instance = args[0] if args else None
            
            # If this is an instance method, validate wallet client
            if instance and hasattr(instance, 'wallet_client'):
                logger.debug(f"Validating wallet client for {func.__name__}")
                if not instance.wallet_client:
                    logger.error(f"Wallet client not set for {func.__name__}")
                    raise ValueError("Wallet client is required but not set")
            
            # Validate parameters against model if provided
            if self.model:
                logger.debug(f"Validating parameters against model {self.model.__name__}")
                try:
                    params = {k: v for k, v in kwargs.items() if k in self.model.model_fields}
                    logger.debug(f"Filtered parameters: {params}")
                    validated_params = self.model(**params)
                    kwargs.update(validated_params.model_dump())
                except ValidationError as e:
                    logger.error(f"Parameter validation failed for {func.__name__}: {str(e)}")
                    raise ValueError(f"Parameter validation failed: {str(e)}")
                    
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"Function {func.__name__} returned: {result}")
                return result
            except Exception as e:
                logger.error(f"Error executing {func.__name__}: {str(e)}")
                raise
        
        # Create tool metadata
        logger.debug(f"Creating metadata for {func.__name__}")
        tool_params = create_tool_parameters(
            name=self.name or func.__name__,
            description=self.description,
            model=self.model,
            additional_params=self._get_parameters(func)
        )
        
        wrapper.__tool__ = tool_params
        return wrapper

    def _get_parameters(self, func: Callable) -> Dict[str, Any]:
        """Get the parameters of a function.
        
        Args:
            func: The function to get parameters from
            
        Returns:
            A dictionary containing parameter information
        """
        logger.debug(f"Getting parameters for {func.__name__}")
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        parameters = {}
        
        for name, param in sig.parameters.items():
            if name == "self":
                continue
                
            param_type = type_hints.get(name, Any)
            default = None if param.default == inspect.Parameter.empty else param.default
            required = param.default == inspect.Parameter.empty
            
            parameters[name] = {
                "type": str(param_type),
                "description": "",  # Could be added via docstring parsing
                "required": required
            }
            
            if default is not None:
                parameters[name]["default"] = default
                
            logger.debug(f"Parameter {name}: type={param_type}, required={required}, default={default}")
            
        return parameters


def get_tool_metadata(func: Union[Callable, Any]) -> Optional[Dict[str, Any]]:
    """Get the tool metadata from a function.
    
    Args:
        func: The function to get metadata from
        
    Returns:
        A dictionary containing the tool metadata, or None if the function is not a tool
    """
    metadata = getattr(func, "__tool__", None)
    logger.debug(f"Getting metadata for {getattr(func, '__name__', func)}: {metadata}")
    return metadata


def tool(description: str = "", name: Optional[str] = None, model: Optional[Type[BaseModel]] = None) -> Callable[[T], T]:
    """Decorator to mark a method as a tool.
    
    Args:
        description: A description of what the tool does
        name: Optional override for the tool name
        model: Optional Pydantic model for parameters
        
    Returns:
        A decorator function
    """
    logger.debug(f"Creating tool decorator with description='{description}', name='{name}', model={model}")
    return Tool(description=description, name=name, model=model)
