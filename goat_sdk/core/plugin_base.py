"""Base plugin class for Mode SDK."""

from typing import List, Any
from .chain import Chain


class PluginBase:
    """Base plugin class for Mode SDK."""

    def __init__(self, name: str, tools: List[Any]):
        """Initialize plugin.
        
        Args:
            name: Plugin name
            tools: List of tools provided by the plugin
        """
        self.name = name
        self.tools = tools

    def supports_chain(self, chain: Chain) -> bool:
        """Check if plugin supports chain.
        
        Args:
            chain: Chain to check
        
        Returns:
            True if chain is supported
        """
        return True 