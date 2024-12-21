"""Base plugin interface for GOAT SDK."""

from typing import List
from pydantic import BaseModel

from .types import Chain

class PluginConfig(BaseModel):
    """Base configuration for plugins."""
    pass

class Plugin:
    """Base plugin interface."""
    
    def __init__(self):
        """Initialize the plugin."""
        pass
        
    @property
    def supported_chains(self) -> List[Chain]:
        """Get supported chains."""
        raise NotImplementedError
        
    async def close(self) -> None:
        """Close all connections."""
        pass 