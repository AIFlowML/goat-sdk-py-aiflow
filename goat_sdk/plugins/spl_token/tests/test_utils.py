"""Tests for SPL Token utility functions."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from dataclasses import dataclass

from goat_sdk.plugins.spl_token.utils import (
    get_token_info_by_symbol,
    get_tokens_for_network,
    get_token_by_mint_address,
    does_account_exist,
)
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork
from goat_sdk.plugins.spl_token.exceptions import TokenNotFoundError, InvalidTokenAddressError, TokenAccountNotFoundError


@dataclass
class MockAccountInfo:
    """Mock account info for testing."""
    value: MagicMock


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
    return client


@pytest.fixture
def test_tokens():
    """Create test tokens."""
    return [
        Token(
            symbol="SOL",
            name="Solana",
            decimals=9,
            mint_addresses={
                SolanaNetwork.MAINNET: "0x" + "22" * 32,
                SolanaNetwork.DEVNET: "0x" + "22" * 32,
            },
        ),
        Token(
            symbol="USDC",
            name="USD Coin",
            decimals=6,
            mint_addresses={
                SolanaNetwork.MAINNET: "0x" + "33" * 32,
            },
        ),
    ]


@pytest.mark.asyncio
async def test_get_token_info_by_symbol(test_tokens):
    """Test get_token_info_by_symbol function."""
    # Test successful case
    token = await get_token_info_by_symbol(test_tokens, "SOL")
    assert token.symbol == "SOL"
    assert token.decimals == 9

    # Test token not found
    with pytest.raises(TokenNotFoundError):
        await get_token_info_by_symbol(test_tokens, "INVALID")

    # Test network not supported
    with pytest.raises(TokenNotFoundError):
        await get_token_info_by_symbol(test_tokens, "USDC", network=SolanaNetwork.DEVNET)


def test_get_tokens_for_network(test_tokens):
    """Test get_tokens_for_network function."""
    # Test mainnet tokens
    mainnet_tokens = get_tokens_for_network(test_tokens, SolanaNetwork.MAINNET)
    assert len(mainnet_tokens) == 2
    assert all(SolanaNetwork.MAINNET in t.mint_addresses for t in mainnet_tokens)

    # Test devnet tokens
    devnet_tokens = get_tokens_for_network(test_tokens, SolanaNetwork.DEVNET)
    assert len(devnet_tokens) == 1
    assert all(SolanaNetwork.DEVNET in t.mint_addresses for t in devnet_tokens)


def test_get_token_by_mint_address(test_tokens):
    """Test get_token_by_mint_address function."""
    # Test successful case
    token = get_token_by_mint_address(test_tokens, "0x" + "22" * 32)
    assert token is not None
    assert token.symbol == "SOL"

    # Test token not found
    token = get_token_by_mint_address(test_tokens, "0x" + "44" * 32)
    assert token is None

    # Test network specific search
    token = get_token_by_mint_address(test_tokens, "0x" + "33" * 32, network=SolanaNetwork.MAINNET)
    assert token is not None
    assert token.symbol == "USDC"


@pytest.mark.asyncio
async def test_does_account_exist(mock_wallet_client):
    """Test does_account_exist function."""
    # Test account exists
    mock_value = MagicMock()
    mock_account_info = MockAccountInfo(value=mock_value)
    mock_wallet_client.connection.get_account_info.return_value = mock_account_info
    
    # Valid addresses in base58 format
    owner_address = "11111111111111111111111111111111"  # Valid base58 string
    mint_address = "22222222222222222222222222222222"  # Valid base58 string
    
    exists = await does_account_exist(mock_wallet_client, owner_address, mint_address)
    assert exists is not None
    
    # Test account does not exist
    mock_account_info = MockAccountInfo(value=None)
    mock_wallet_client.connection.get_account_info.return_value = mock_account_info
    
    exists = await does_account_exist(mock_wallet_client, owner_address, mint_address)
    assert exists is None
    
    # Test invalid owner address
    with pytest.raises(InvalidTokenAddressError):
        await does_account_exist(mock_wallet_client, "invalid", mint_address)
    
    # Test invalid mint address
    with pytest.raises(InvalidTokenAddressError):
        await does_account_exist(mock_wallet_client, owner_address, "invalid")
    
    # Test RPC error
    mock_wallet_client.connection.get_account_info.side_effect = Exception("RPC error")
    with pytest.raises(TokenAccountNotFoundError) as exc_info:
        await does_account_exist(mock_wallet_client, owner_address, mint_address)
    assert "RPC error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_does_account_exist_error():
    """Test does_account_exist error handling."""
    # Test with None wallet client
    with pytest.raises(TokenAccountNotFoundError) as exc_info:
        await does_account_exist(None, "11111111111111111111111111111111", "22222222222222222222222222222222")
    assert "wallet client" in str(exc_info.value).lower()
    
    # Test with invalid connection
    mock_wallet_client = AsyncMock()
    mock_wallet_client.get_connection.return_value = None
    with pytest.raises(TokenAccountNotFoundError) as exc_info:
        await does_account_exist(mock_wallet_client, "11111111111111111111111111111111", "22222222222222222222222222222222")
    assert "connection" in str(exc_info.value).lower() 