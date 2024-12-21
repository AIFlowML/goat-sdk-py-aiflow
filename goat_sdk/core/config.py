"""
Core configuration management for GOAT SDK.
"""
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from decimal import Decimal

class NetworkConfig(BaseSettings):
    rpc_url: str
    chain_id: int
    private_key: str

    class Config:
        env_file = '.env'

class GoatConfig(BaseSettings):
    """
    Main configuration class for GOAT SDK.
    Handles all environment variables and provides validation.
    """
    # Network Configurations
    eth_network: str = Field("mainnet", env='ETH_NETWORK', description="Ethereum network to connect to")
    eth_rpc_url: str = Field(..., env='ETH_RPC_URL', description="Ethereum RPC URL")
    eth_private_key: str = Field(..., env='ETH_PRIVATE_KEY', description="Ethereum private key")
    
    mode_rpc_url: Optional[str] = Field(None, env='MODE_RPC_URL')
    mode_chain_id: int = Field(919, env='MODE_CHAIN_ID')
    mode_private_key: Optional[str] = Field(None, env='MODE_PRIVATE_KEY')
    
    solana_network: Optional[str] = Field(None, env='SOLANA_NETWORK')
    solana_rpc_url: Optional[str] = Field(None, env='SOLANA_RPC_URL')
    solana_private_key: Optional[str] = Field(None, env='SOLANA_PRIVATE_KEY')

    # API Keys
    etherscan_api_key: Optional[str] = Field(None, env='ETHERSCAN_API_KEY')
    solscan_api_key: Optional[str] = Field(None, env='SOLSCAN_API_KEY')

    # Security Settings
    max_slippage: Decimal = Field(Decimal('0.5'), env='MAX_SLIPPAGE')
    gas_multiplier: Decimal = Field(Decimal('1.1'), env='GAS_MULTIPLIER')
    mev_protection: bool = Field(True, env='MEV_PROTECTION')

    # Logging Configuration
    log_level: str = Field('INFO', env='LOG_LEVEL')
    log_file: str = Field('logs/goat.log', env='LOG_FILE')

    # Cache Settings
    cache_duration: int = Field(3600, env='CACHE_DURATION')
    redis_url: Optional[str] = Field(None, env='REDIS_URL')

    # Advanced Features
    enable_analytics: bool = Field(True, env='ENABLE_ANALYTICS')
    max_concurrent_requests: int = Field(10, env='MAX_CONCURRENT_REQUESTS')
    request_timeout: int = Field(30, env='REQUEST_TIMEOUT')

    # Development Settings
    debug_mode: bool = Field(False, env='DEBUG_MODE')
    test_mode: bool = Field(False, env='TEST_MODE')

    class Config:
        """Pydantic config."""
        env_prefix = "GOAT_"
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'

    @validator('eth_private_key', 'mode_private_key')
    def validate_private_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v.startswith('0x'):
            v = v[2:]
        if not all(c in '0123456789abcdefABCDEF' for c in v):
            raise ValueError('Private key must be hexadecimal')
        if len(v) != 64:
            raise ValueError('Private key must be 32 bytes (64 hex characters)')
        return v

    @validator('max_slippage', 'gas_multiplier')
    def validate_decimal(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    def get_network_config(self, network: str) -> NetworkConfig:
        """Get configuration for a specific network."""
        network_configs = {
            'ethereum': NetworkConfig(
                rpc_url=self.eth_rpc_url,
                chain_id=1,
                private_key=self.eth_private_key
            ),
            'mode': NetworkConfig(
                rpc_url=self.mode_rpc_url,
                chain_id=self.mode_chain_id,
                private_key=self.mode_private_key
            ) if self.mode_rpc_url else None,
            'solana': NetworkConfig(
                rpc_url=self.solana_rpc_url,
                chain_id=0,  # Solana doesn't use chain ID
                private_key=self.solana_private_key
            ) if self.solana_rpc_url else None
        }
        return network_configs.get(network.lower())

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary, excluding sensitive data."""
        config_dict = self.dict()
        # Remove sensitive data
        sensitive_fields = {'eth_private_key', 'mode_private_key', 'solana_private_key'}
        for field in sensitive_fields:
            if field in config_dict:
                config_dict[field] = '***'
        return config_dict

    @classmethod
    def load_from_env(cls) -> 'GoatConfig':
        """Load configuration from environment variables."""
        return cls()
