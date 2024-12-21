"""Mode network configuration."""

from enum import Enum
from typing import Dict, Any


class ModeNetwork(str, Enum):
    """Mode network types."""
    MAINNET = "mainnet"
    TESTNET = "testnet"


def get_mode_config(network: ModeNetwork) -> Dict[str, Any]:
    """Get Mode network configuration.
    
    Args:
        network: Mode network type.
        
    Returns:
        Network configuration.
    """
    configs = {
        ModeNetwork.MAINNET: {
            "chain_id": 34443,
            "name": "Mode Mainnet",
            "rpc_url": "https://mainnet.mode.network",
            "explorer_url": "https://explorer.mode.network",
            "gas_limit": 2000000,
        },
        ModeNetwork.TESTNET: {
            "chain_id": 919,
            "name": "Mode Testnet",
            "rpc_url": "https://sepolia.mode.network",
            "explorer_url": "https://sepolia.explorer.mode.network",
            "gas_limit": 2000000,
        },
    }
    return configs[network]
