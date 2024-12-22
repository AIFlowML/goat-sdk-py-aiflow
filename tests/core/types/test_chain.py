"""Tests for chain types."""

import pytest
import logging
from pydantic import ValidationError

from goat_sdk.core.types.chain import (
    ChainType,
    SolanaChainConfig,
    EthereumChainConfig,
    ModeChainConfig,
    validateChainConfig
)

logger = logging.getLogger(__name__)


def test_chain_type_validation():
    """Test chain type validation."""
    logger.info("Testing chain type validation")
    
    # Test valid chain types
    logger.debug("Testing valid chain types")
    assert ChainType.SOLANA == "solana"
    assert ChainType.ETHEREUM == "ethereum"
    assert ChainType.MODE == "mode"
    logger.debug("Valid chain types verified")
    
    # Test invalid chain type
    logger.debug("Testing invalid chain type")
    with pytest.raises(ValueError) as exc_info:
        ChainType("invalid")
    assert "is not a valid ChainType" in str(exc_info.value)
    logger.debug(f"Invalid chain type error: {exc_info.value}")
    
    logger.info("Chain type validation tests completed successfully")


def test_solana_chain_config_validation():
    """Test Solana chain config validation."""
    logger.info("Testing Solana chain config validation")
    
    # Test valid Solana chain config
    logger.debug("Testing valid Solana chain config")
    config = SolanaChainConfig(
        type=ChainType.SOLANA,
        network="mainnet",
        rpc_url="https://api.mainnet-beta.solana.com",
        commitment="confirmed"
    )
    logger.debug(f"Created Solana config: {config}")
    
    assert config.type == ChainType.SOLANA
    assert config.network == "mainnet"
    assert config.rpc_url == "https://api.mainnet-beta.solana.com"
    assert config.commitment == "confirmed"
    logger.debug("Valid Solana config verified")
    
    # Test invalid chain type
    logger.debug("Testing invalid chain type for Solana config")
    with pytest.raises(ValidationError) as exc_info:
        SolanaChainConfig(type=ChainType.ETHEREUM)
    assert "Input should be <ChainType.SOLANA: 'solana'>" in str(exc_info.value)
    logger.debug(f"Invalid chain type error: {exc_info.value}")
    
    logger.info("Solana chain config validation tests completed successfully")


def test_ethereum_chain_config_validation():
    """Test Ethereum chain config validation."""
    logger.info("Testing Ethereum chain config validation")
    
    # Test valid Ethereum chain config
    logger.debug("Testing valid Ethereum chain config")
    config = EthereumChainConfig(
        type=ChainType.ETHEREUM,
        network="mainnet",
        rpc_url="https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
        chain_id=1,
        gas_limit=21000
    )
    logger.debug(f"Created Ethereum config: {config}")
    
    assert config.type == ChainType.ETHEREUM
    assert config.network == "mainnet"
    assert config.rpc_url == "https://mainnet.infura.io/v3/YOUR-PROJECT-ID"
    assert config.chain_id == 1
    assert config.gas_limit == 21000
    logger.debug("Valid Ethereum config verified")
    
    # Test invalid chain type
    logger.debug("Testing invalid chain type for Ethereum config")
    with pytest.raises(ValidationError) as exc_info:
        EthereumChainConfig(type=ChainType.SOLANA)
    assert "Input should be <ChainType.ETHEREUM: 'ethereum'>" in str(exc_info.value)
    logger.debug(f"Invalid chain type error: {exc_info.value}")
    
    logger.info("Ethereum chain config validation tests completed successfully")


def test_mode_chain_config_validation():
    """Test Mode chain config validation."""
    logger.info("Testing Mode chain config validation")
    
    # Test valid Mode chain config
    logger.debug("Testing valid Mode chain config")
    config = ModeChainConfig(
        type=ChainType.MODE,
        network="mainnet",
        rpc_url="https://mainnet.mode.network",
        chain_id=919,
        gas_limit=21000
    )
    logger.debug(f"Created Mode config: {config}")
    
    assert config.type == ChainType.MODE
    assert config.network == "mainnet"
    assert config.rpc_url == "https://mainnet.mode.network"
    assert config.chain_id == 919
    assert config.gas_limit == 21000
    logger.debug("Valid Mode config verified")
    
    # Test invalid chain type
    logger.debug("Testing invalid chain type for Mode config")
    with pytest.raises(ValidationError) as exc_info:
        ModeChainConfig(type=ChainType.SOLANA)
    assert "Input should be <ChainType.MODE: 'mode'>" in str(exc_info.value)
    logger.debug(f"Invalid chain type error: {exc_info.value}")
    
    logger.info("Mode chain config validation tests completed successfully")


def test_validate_chain_config():
    """Test chain config validation function."""
    logger.info("Testing chain config validation function")
    
    # Test valid Solana config
    logger.debug("Testing valid Solana config validation")
    solana_config = validateChainConfig({
        "type": "solana",
        "network": "mainnet",
        "rpc_url": "https://api.mainnet-beta.solana.com",
        "commitment": "confirmed"
    })
    logger.debug(f"Validated Solana config: {solana_config}")
    assert isinstance(solana_config, SolanaChainConfig)
    assert solana_config.type == ChainType.SOLANA
    
    # Test valid Ethereum config
    logger.debug("Testing valid Ethereum config validation")
    ethereum_config = validateChainConfig({
        "type": "ethereum",
        "network": "mainnet",
        "rpc_url": "https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
        "chain_id": 1,
        "gas_limit": 21000
    })
    logger.debug(f"Validated Ethereum config: {ethereum_config}")
    assert isinstance(ethereum_config, EthereumChainConfig)
    assert ethereum_config.type == ChainType.ETHEREUM
    
    # Test valid Mode config
    logger.debug("Testing valid Mode config validation")
    mode_config = validateChainConfig({
        "type": "mode",
        "network": "mainnet",
        "rpc_url": "https://mainnet.mode.network",
        "chain_id": 919,
        "gas_limit": 21000
    })
    logger.debug(f"Validated Mode config: {mode_config}")
    assert isinstance(mode_config, ModeChainConfig)
    assert mode_config.type == ChainType.MODE
    
    # Test invalid chain type
    logger.debug("Testing invalid chain type validation")
    with pytest.raises(ValueError) as exc_info:
        validateChainConfig({"type": "invalid"})
    assert "Invalid chain type: invalid" in str(exc_info.value)
    logger.debug(f"Invalid chain type error: {exc_info.value}")
    
    # Test missing chain type
    logger.debug("Testing missing chain type validation")
    with pytest.raises(ValueError) as exc_info:
        validateChainConfig({})
    assert "Chain type is required" in str(exc_info.value)
    logger.debug(f"Missing chain type error: {exc_info.value}")
    
    logger.info("Chain config validation tests completed successfully")
