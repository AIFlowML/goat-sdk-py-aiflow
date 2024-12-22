"""Base class for all plugins in the GOAT SDK."""

from abc import ABC
from typing import List, Dict, Any, Optional, Type, Set, ClassVar
from pydantic import BaseModel, Field, model_validator, PrivateAttr, ConfigDict

from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.core.utils.snake_case import to_snake_case
from goat_sdk.core.decorators.tool import Tool


class PluginConfig(BaseModel):
    """Base configuration for all plugins."""
    name: str = Field(default="")
    description: str = Field(default="")
    version: str = Field(default="0.1.0")
    params: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra='allow')


class PluginBase(ABC, BaseModel):
    """Base class for all plugins.
    
    This class provides the basic structure that all plugins must follow.
    Each plugin should inherit from this class and implement its own
    functionality.
    
    Attributes:
        name: The name of the plugin
        description: A description of what the plugin does
        version: The plugin version
        tools: Set of tool classes registered with the plugin
        params: Plugin parameters
    """
    
    name: str = Field(default="")
    description: str = Field(default="")
    version: str = Field(default="0.1.0")
    tools: Set[Type[ToolBase]] = Field(default_factory=set)
    params: Dict[str, Any] = Field(default_factory=dict)
    
    # Private attributes
    _initialized: bool = PrivateAttr(default=False)
    _config: Optional[PluginConfig] = PrivateAttr(default=None)
    
    # Class variables
    CONFIG_CLASS: ClassVar[Type[PluginConfig]] = PluginConfig
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='allow'
    )
    
    def __init__(self, **data):
        """Initialize the plugin with default name from class name."""
        if 'name' not in data:
            data['name'] = to_snake_case(self.__class__.__name__)
        super().__init__(**data)
        self._initialized = False
        self._config = None
    
    @property
    def initialized(self) -> bool:
        """Get initialization status.
        
        Returns:
            True if plugin is initialized
        """
        return self._initialized
    
    @property
    def config(self) -> PluginConfig:
        """Get plugin configuration.
        
        Returns:
            Plugin configuration
            
        Raises:
            ValueError: If plugin is not initialized
        """
        if not self._initialized:
            raise ValueError("Plugin is not initialized")
        return self._config
    
    @classmethod
    def create(cls, params: Optional[Dict[str, Any]] = None) -> "PluginBase":
        """Factory method for creating plugin instances.
        
        Args:
            params: Optional parameters for plugin initialization
            
        Returns:
            New plugin instance
            
        Raises:
            ValueError: If initialization fails
        """
        instance = cls(params=params or {})
        instance.initialize(params)
        instance.validate()
        instance._initialized = True
        return instance
    
    def initialize(self, params: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin with parameters.
        
        Args:
            params: Optional parameters for initialization
        """
        config_data = {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'params': params or {}
        }
        self._config = self.CONFIG_CLASS(**config_data)
        self.params = params or {}
    
    @model_validator(mode='after')
    def validate_plugin(self) -> "PluginBase":
        """Validate plugin configuration.
        
        Returns:
            Self for chaining
            
        Raises:
            ValueError: If configuration is invalid
        """
        if self._config:
            # Validate version format
            version_parts = self._config.version.split('.')
            if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
                raise ValueError("Invalid version format. Must be in format: MAJOR.MINOR.PATCH")
        return self
    
    def register_tool(self, tool: Type[ToolBase]) -> None:
        """Register a tool with the plugin.
        
        Args:
            tool: Tool class to register
            
        Raises:
            ValueError: If tool is already registered or invalid
        """
        if not issubclass(tool, ToolBase):
            raise ValueError(f"{tool.__name__} must be a subclass of ToolBase")
            
        if tool in self.tools:
            raise ValueError(f"Tool {tool.__name__} is already registered")
            
        self.tools.add(tool)
    
    def unregister_tool(self, tool: Type[ToolBase]) -> None:
        """Unregister a tool from the plugin.
        
        Args:
            tool: Tool class to unregister
            
        Raises:
            ValueError: If tool is not registered
        """
        if tool not in self.tools:
            raise ValueError(f"Tool {tool.__name__} is not registered")
        self.tools.remove(tool)
    
    def get_tools(self) -> Set[Type[ToolBase]]:
        """Get all tools registered with the plugin.
        
        Returns:
            Set of registered tool classes
            
        Raises:
            ValueError: If plugin is not initialized
        """
        if not self._initialized:
            raise ValueError("Plugin is not initialized")
        return self.tools.copy()
    
    async def cleanup(self) -> None:
        """Clean up any resources used by the plugin."""
        self.tools.clear()
        self._config = None
        self._initialized = False
