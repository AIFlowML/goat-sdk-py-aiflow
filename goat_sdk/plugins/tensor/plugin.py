"""Tensor plugin for GOAT SDK."""

from typing import Optional

from goat_sdk.core.classes.plugin_base import PluginBase
from goat_sdk.plugins.tensor.client import TensorClient
from goat_sdk.plugins.tensor.config import TensorConfig


class TensorPlugin(PluginBase):
    """Tensor plugin for GOAT SDK."""

    def __init__(self, config: Optional[TensorConfig] = None) -> None:
        """Initialize Tensor plugin.

        Args:
            config: Tensor configuration
        """
        self.config = config or TensorConfig(api_key="")
        self.client = TensorClient(config=self.config)

    async def initialize(self) -> None:
        """Initialize plugin."""
        pass

    async def cleanup(self) -> None:
        """Clean up plugin."""
        pass 