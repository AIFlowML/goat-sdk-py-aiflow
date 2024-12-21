"""Base types for GOAT SDK."""

from enum import Enum

class Chain(str, Enum):
    """Supported blockchain networks."""
    ARBITRUM = "arbitrum"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    OPTIMISM = "optimism"
    BSC = "bsc" 