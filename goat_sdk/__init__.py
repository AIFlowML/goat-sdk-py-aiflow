"""GOAT SDK - A Python SDK for DeFi protocols.

This is an unofficial implementation of the GOAT SDK, created by Igor Lessio.
It follows the same structure and rules as the official SDK but is maintained independently.
"""

from .plugin import Plugin, PluginConfig
from .types import Chain

__version__ = "0.1.0"
__author__ = "Igor Lessio"
__email__ = "ilessio.aimaster@gmail.com"
__license__ = "MIT"

__all__ = [
    "Plugin",
    "PluginConfig",
    "Chain",
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]
