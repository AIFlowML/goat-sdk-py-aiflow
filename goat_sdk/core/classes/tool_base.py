"""Base class for GOAT SDK tools."""

from typing import Dict, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from goat_sdk.core.decorators import Tool

class ToolBase(ABC, BaseModel):
    """Base class for all GOAT SDK tools.
    
    This class defines the interface that all tools must implement.
    Tools are used to interact with blockchain networks and perform
    specific operations.
    
    Attributes:
        name: The name of the tool
        description: A description of what the tool does
        parameters: JSON schema defining the tool's parameters
    """
    
    model_config = ConfigDict(ignored_types=(Tool,))
    
    name: str
    description: str
    parameters: Dict[str, Any]
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> str:
        """Execute the tool with the given parameters.
        
        Args:
            params: Dictionary of parameters for the tool
            
        Returns:
            Tool execution result as a string
            
        Raises:
            Exception: If tool execution fails
        """
        pass
