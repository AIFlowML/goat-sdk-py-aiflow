"""Chain type definitions."""

from enum import Enum
from typing import Literal, Union
from pydantic import BaseModel, Field


class ChainType(str, Enum):
    """Supported blockchain types."""
    SOLANA = "solana"
    ETHEREUM = "ethereum"
    MODE = "mode"


class ChainConfig(BaseModel):
    """Base chain configuration."""
    type: ChainType = Field(...)
    network: str = Field(default="mainnet")
    rpc_url: str = Field(default="")
    
    class Config:
        use_enum_values = True


class SolanaChainConfig(ChainConfig):
    """Solana chain configuration."""
    type: Literal[ChainType.SOLANA] = Field(default=ChainType.SOLANA)
    commitment: str = Field(default="confirmed")


class EthereumChainConfig(ChainConfig):
    """Ethereum chain configuration."""
    type: Literal[ChainType.ETHEREUM] = Field(default=ChainType.ETHEREUM)
    chain_id: int = Field(default=1)
    gas_limit: int = Field(default=21000)


class ModeChainConfig(ChainConfig):
    """Mode chain configuration."""
    type: Literal[ChainType.MODE] = Field(default=ChainType.MODE)
    chain_id: int = Field(default=919)
    gas_limit: int = Field(default=21000)


# Type alias for any supported chain config
ChainConfigType = Union[SolanaChainConfig, EthereumChainConfig, ModeChainConfig]


def validateChainConfig(config: dict) -> ChainConfigType:
    """Validate and create a chain configuration.
    
    Args:
        config: Chain configuration dictionary
        
    Returns:
        Validated chain configuration
        
    Raises:
        ValueError: If chain type is invalid
    """
    chain_type = config.get("type")
    if not chain_type:
        raise ValueError("Chain type is required")
        
    try:
        chain_type = ChainType(chain_type)
    except ValueError:
        raise ValueError(f"Invalid chain type: {chain_type}")
        
    config_classes = {
        ChainType.SOLANA: SolanaChainConfig,
        ChainType.ETHEREUM: EthereumChainConfig,
        ChainType.MODE: ModeChainConfig
    }
    
    config_class = config_classes.get(chain_type)
    if not config_class:
        raise ValueError(f"Unsupported chain type: {chain_type}")
        
    return config_class(**config)
