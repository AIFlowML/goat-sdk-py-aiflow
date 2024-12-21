"""Jupiter plugin implementation."""

from goat_sdk.core.plugin_base import PluginBase
from goat_sdk.core.chain import Chain
from .service import JupiterService


class JupiterPlugin(PluginBase):
    """Plugin for Jupiter DEX integration."""

    def __init__(self):
        """Initialize Jupiter plugin."""
        service = JupiterService()
        super().__init__(name="jupiter", tools=[service])

    def supports_chain(self, chain: Chain) -> bool:
        """Check if chain is supported.
        
        Args:
            chain: Chain to check
        
        Returns:
            True if chain is supported
        """
        return chain.type == "solana"


def jupiter() -> JupiterPlugin:
    """Create Jupiter plugin instance.
    
    Returns:
        Jupiter plugin instance
    """
    return JupiterPlugin() 