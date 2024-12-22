"""Tests for the WalletClientBase class."""

import pytest
import logging
from unittest.mock import MagicMock
from pydantic import BaseModel, Field

from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.types.chain import ChainType

logger = logging.getLogger(__name__)


class TestWalletClient(WalletClientBase):
    """Test wallet client implementation."""
    provider_url: str = Field(default="http://localhost:8545")
    private_key: str = Field(default="0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    
    async def get_address(self) -> str:
        """Get wallet address."""
        logger.debug("Getting wallet address")
        return "test_address"
        
    async def get_chain(self) -> ChainType:
        """Get chain type."""
        logger.debug("Getting chain type")
        return ChainType.ETHEREUM
        
    async def balance_of(self, address: str) -> int:
        """Get balance of address."""
        logger.debug(f"Getting balance of address: {address}")
        return 100
        
    async def sign_message(self, message: str) -> str:
        """Sign a message."""
        logger.debug(f"Signing message: {message}")
        return f"signed_{message}"
        
    async def sign_transaction(self, transaction: dict) -> str:
        """Sign a transaction."""
        logger.debug(f"Signing transaction: {transaction}")
        return f"signed_tx_{transaction}"
        
    async def send_transaction(self, transaction: dict) -> str:
        """Send a transaction."""
        logger.debug(f"Sending transaction: {transaction}")
        return f"sent_tx_{transaction}"


@pytest.mark.asyncio
async def test_wallet_client_initialization():
    """Test wallet client initialization."""
    logger.info("Testing wallet client initialization")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    logger.debug("Verifying client configuration")
    assert client.provider_url == "http://localhost:8545"
    assert client.private_key == "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    
    logger.info("Wallet client initialization test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_get_address():
    """Test get_address method."""
    logger.info("Testing get_address method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    logger.debug("Getting wallet address")
    address = await client.get_address()
    
    logger.debug(f"Verifying address: {address}")
    assert address == "test_address"
    
    logger.info("get_address test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_get_chain():
    """Test get_chain method."""
    logger.info("Testing get_chain method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    logger.debug("Getting chain type")
    chain = await client.get_chain()
    
    logger.debug(f"Verifying chain type: {chain}")
    assert chain == ChainType.ETHEREUM
    
    logger.info("get_chain test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_balance_of():
    """Test balance_of method."""
    logger.info("Testing balance_of method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    logger.debug("Getting balance of test address")
    balance = await client.balance_of("test_address")
    
    logger.debug(f"Verifying balance: {balance}")
    assert balance == 100
    
    logger.info("balance_of test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_sign_message():
    """Test sign_message method."""
    logger.info("Testing sign_message method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    logger.debug("Signing test message")
    signature = await client.sign_message("test_message")
    
    logger.debug(f"Verifying signature: {signature}")
    assert signature == "signed_test_message"
    
    logger.info("sign_message test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_sign_transaction():
    """Test sign_transaction method."""
    logger.info("Testing sign_transaction method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    test_tx = {"test": "tx"}
    logger.debug(f"Signing test transaction: {test_tx}")
    signature = await client.sign_transaction(test_tx)
    
    logger.debug(f"Verifying signature: {signature}")
    assert signature == "signed_tx_{'test': 'tx'}"
    
    logger.info("sign_transaction test completed successfully")


@pytest.mark.asyncio
async def test_wallet_client_send_transaction():
    """Test send_transaction method."""
    logger.info("Testing send_transaction method")
    
    logger.debug("Creating test wallet client")
    client = TestWalletClient()
    
    test_tx = {"test": "tx"}
    logger.debug(f"Sending test transaction: {test_tx}")
    result = await client.send_transaction(test_tx)
    
    logger.debug(f"Verifying transaction result: {result}")
    assert result == "sent_tx_{'test': 'tx'}"
    
    logger.info("send_transaction test completed successfully")
