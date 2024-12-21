"""Base class for all plugins in the GOAT SDK."""

from abc import ABC


class PluginBase(ABC):
    """Base class for all plugins.
    
    This class provides the basic structure that all plugins must follow.
    Each plugin should inherit from this class and implement its own
    functionality.
    """

    def __init__(self):
        """Initialize the plugin."""
        pass

    async def cleanup(self):
        """Clean up any resources used by the plugin.
        
        This method should be called when the plugin is no longer needed.
        """
        pass
