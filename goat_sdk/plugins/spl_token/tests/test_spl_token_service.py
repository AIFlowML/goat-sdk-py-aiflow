"""Tests for SPL Token service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from goat_sdk.plugins.spl_token.spl_token_service import SplTokenService
from goat_sdk.plugins.spl_token.parameters import (
    GetTokenMintAddressBySymbolParameters,
    GetTokenBalanceByMintAddressParameters,
    TransferTokenByMintAddressParameters,
    ConvertToBaseUnitParameters,
)
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork


@dataclass
class MockAccountInfo:
    """Mock account info for testing."""
    value: MagicMock


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
    client.keypair = MagicMock()
    client.connection.get_latest_blockhash = AsyncMock(return_value="mock_blockhash")
    return client


@pytest.fixture
def spl_token_service():
    """Create SPL Token service."""
    tokens = [
        Token(
            symbol="SOL",
            name="Solana",
            decimals=9,
            mint_addresses={
                SolanaNetwork.MAINNET: "0x" + "22" * 32,  # Valid hex string
                SolanaNetwork.DEVNET: "0x" + "22" * 32,  # Valid hex string
            },
        )
    ]
    return SplTokenService(tokens=tokens)


@pytest.mark.asyncio
async def test_get_token_mint_address_by_symbol(spl_token_service):
    """Test get_token_mint_address_by_symbol method."""
    params = GetTokenMintAddressBySymbolParameters(symbol="SOL")
    result = await spl_token_service.get_token_mint_address_by_symbol(params)
    assert result == "0x" + "22" * 32


@pytest.mark.asyncio
async def test_get_token_balance_by_mint_address(spl_token_service, mock_wallet_client):
    """Test get_token_balance_by_mint_address method."""
    params = GetTokenBalanceByMintAddressParameters(
        mint_address="0x" + "22" * 32,
        wallet_address="0x" + "11" * 32,
    )
    
    mock_value = MagicMock()
    mock_value.lamports = 1000000
    mock_account_info = MockAccountInfo(value=mock_value)

    with patch.object(mock_wallet_client.connection, 'get_account_info') as mock_get_account:
        mock_get_account.return_value = mock_account_info
        result = await spl_token_service.get_token_balance_by_mint_address(
            wallet_client=mock_wallet_client,
            parameters=params
        )
        assert result.amount == 1000000


@pytest.mark.asyncio
async def test_transfer_token_by_mint_address(spl_token_service, mock_wallet_client):
    """Test transfer_token_by_mint_address method."""
    params = TransferTokenByMintAddressParameters(
        mint_address="0x" + "22" * 32,
        to="0x" + "33" * 32,  # Valid hex string for recipient
        amount=1000000,
    )
    
    mock_value = MagicMock()
    mock_value.lamports = 2000000
    mock_account_info = MockAccountInfo(value=mock_value)

    with patch.object(mock_wallet_client.connection, 'get_account_info') as mock_get_account:
        mock_get_account.return_value = mock_account_info
        mock_wallet_client.send_and_confirm_transaction.return_value = "mock_signature"
        
        result = await spl_token_service.transfer_token_by_mint_address(
            wallet_client=mock_wallet_client,
            parameters=params
        )
        assert result == "mock_signature"


def test_convert_to_base_unit(spl_token_service):
    """Test convert_to_base_unit method."""
    params = ConvertToBaseUnitParameters(
        amount=1.5,
        decimals=6,
    )
    result = spl_token_service.convert_to_base_unit(params)
    assert result == 1500000