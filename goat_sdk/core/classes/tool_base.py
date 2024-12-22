"""Base class for GOAT SDK tools."""

from typing import Dict, Any, Optional, Type, ClassVar, List, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field, model_validator, PrivateAttr, create_model
from goat_sdk.core.decorators.tool import Tool
from goat_sdk.core.utils.create_tool_parameters import create_tool_parameters


class ToolParameters(BaseModel):
    """Base class for tool parameters."""
    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
        validate_default=True
    )


class ToolMetadata(BaseModel):
    """Metadata for tool configuration."""
    name: str = Field(default="", validate_default=True)
    description: str = Field(default="", validate_default=True)
    version: str = Field(default="0.1.0", validate_default=True)
    is_async: bool = Field(default=True)
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra='allow',
        validate_assignment=True,
        validate_default=True
    )


class ToolBase(ABC, BaseModel):
    """Base class for all GOAT SDK tools.
    
    This class defines the interface that all tools must implement.
    Tools are used to interact with blockchain networks and perform
    specific operations.
    
    Attributes:
        name: The name of the tool
        description: A description of what the tool does
        version: The tool version
        parameters: Tool parameters model
    """
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        validate_default=True,
        extra='allow'
    )
    
    name: str = Field(default="", validate_default=True)
    description: str = Field(default="", validate_default=True)
    version: str = Field(default="0.1.0", validate_default=True)
    parameters: Optional[Union[ToolParameters, Dict[str, Any]]] = Field(default=None)
    
    # Private attributes
    _metadata: ToolMetadata = PrivateAttr(default=None)
    _parameters_model: Optional[Type[BaseModel]] = PrivateAttr(default=None)
    
    # Class variables
    PARAMETERS_CLASS: ClassVar[Type[ToolParameters]] = ToolParameters
    
    def __init__(self, **data):
        """Initialize the tool with metadata."""
        super().__init__(**data)
        
        # Create parameters model if needed
        if self.parameters and isinstance(self.parameters, dict):
            self._parameters_model = create_model(
                f"{self.__class__.__name__}Parameters",
                **{k: (Any, v) for k, v in self.parameters.items()}
            )
            self.parameters = self._parameters_model(**self.parameters)
        
        # Create tool metadata
        tool_params = create_tool_parameters(
            name=self.name,
            description=self.description,
            model=self._parameters_model or self.PARAMETERS_CLASS,
            additional_params=None
        )
        
        self._metadata = ToolMetadata(
            name=self.name,
            description=self.description,
            version=self.version,
            parameters_schema=tool_params["parameters"]
        )
    
    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata.
        
        Returns:
            Tool metadata
        """
        return self._metadata
    
    @classmethod
    def create(cls, parameters: Optional[Dict[str, Any]] = None) -> "ToolBase":
        """Factory method for creating tool instances.
        
        Args:
            parameters: Optional parameters for the tool
            
        Returns:
            New tool instance
            
        Raises:
            ValueError: If parameters are invalid
        """
        instance = cls()
        if parameters:
            if instance._parameters_model:
                params_model = instance._parameters_model(**parameters)
            else:
                params_model = instance.PARAMETERS_CLASS(**parameters)
            instance.parameters = params_model
        return instance
    
    @model_validator(mode='after')
    def validate_tool(self) -> "ToolBase":
        """Validate the tool configuration.
        
        Returns:
            Self if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.name:
            raise ValueError("Tool name cannot be empty")
            
        # Validate version format
        version_parts = self.version.split('.')
        if len(version_parts) != 3 or not all(part.isdigit() for part in version_parts):
            raise ValueError("Invalid version format. Must be in format: MAJOR.MINOR.PATCH")
            
        return self
    
    @abstractmethod
    async def execute(self, parameters: Optional[Dict[str, Any]] = None) -> Any:
        """Execute the tool asynchronously.
        
        Args:
            parameters: Optional parameters for execution
        
        Returns:
            Tool execution result
            
        Raises:
            Exception: If tool execution fails
        """
        pass
    
    async def cleanup(self) -> None:
        """Clean up any resources used by the tool."""
        self.parameters = None
        self._parameters_model = None
