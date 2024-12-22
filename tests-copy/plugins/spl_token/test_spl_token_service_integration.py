"""Integration tests for SPL Token Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from solana.publickey import PublicKey

from goat_sdk.plugins.spl_token.spl_token_service import SplTokenService
from goat_sdk.plugins.spl_token.parameters import (
    GetTokenMintAddressBySymbolParameters,
    GetTokenBalanceByMintAddressParameters,
    TransferTokenByMintAddressParameters,
)
from goat_sdk.plugins.spl_token.exceptions import (
    TokenNotFoundError,
    TokenAccountNotFoundError,
    InvalidTokenAddressError,
    TokenTransferError,
)

# Test constants
MOCK_WALLET_ADDRESS = "5ZWj7a1f8tWkjBESHKgrLmXshuXxqeGWh9r9TE6aafPF"
MOCK_RECIPIENT_ADDRESS = "7WNkYJqgvr1HJtHqh6BV5sHn2HgXtjEeHJ5MhDRqMY9y"
USDC_MINT_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
MOCK_TOKEN_ACCOUNT = "HWHvQhFmJB6gPtB6oXNw8PNM5hUWAhUnE4GFsKe254xZ"
MOCK_DEST_TOKEN_ACCOUNT = "3uetDDizgTtadDHZzyy9BqxrjQcozMEkxzbKhfZF4tG3"


@pytest.fixture
def spl_token_service():
    """Create SPL token service instance for testing."""
    return SplTokenService(network="devnet")


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client for testing."""
    mock_client = AsyncMock()
    mock_client.get_address = AsyncMock(return_value=MOCK_WALLET_ADDRESS)
    
    # Create a mock connection with async methods
    mock_connection = AsyncMock()
    mock_connection.get_token_account_balance = AsyncMock()
    
    # Make get_connection return the mock connection directly
    mock_client.get_connection = MagicMock(return_value=mock_connection)
    
    return mock_client


@pytest.mark.asyncio
async def test_full_token_transfer_flow(spl_token_service, mock_wallet_client):
    """Test complete token transfer flow including account creation."""
    # Step 1: Get token info
    token_params = GetTokenMintAddressBySymbolParameters(symbol="USDC")
    token_info = await spl_token_service.get_token_info_by_symbol(token_params)
    assert token_info.symbol == "USDC"
    assert token_info.decimals == 6

    # Step 2: Check initial balance
    balance_params = GetTokenBalanceByMintAddressParameters(
        wallet_address=MOCK_WALLET_ADDRESS,
        mint_address=USDC_MINT_ADDRESS,
    )

    # Mock initial balance
    mock_balance = MagicMock()
    mock_balance.value = {"amount": 2000000, "decimals": 6, "uiAmount": 2.0}
    mock_wallet_client.get_connection().get_token_account_balance.return_value = mock_balance

    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist") as mock_exists:
        mock_exists.return_value = MOCK_TOKEN_ACCOUNT
        initial_balance = await spl_token_service.get_token_balance_by_mint_address(
            mock_wallet_client, balance_params
        )
    
    assert initial_balance["amount"] == 2000000
    assert initial_balance["uiAmount"] == 2.0

    # Step 3: Perform transfer
    transfer_params = TransferTokenByMintAddressParameters(
        to=MOCK_RECIPIENT_ADDRESS,
        mint_address=USDC_MINT_ADDRESS,
        amount=1000000,  # Transfer 1 USDC
    )

    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist") as mock_exists:
        mock_exists.side_effect = [
            MOCK_TOKEN_ACCOUNT,  # Source account exists
            None,  # Destination account doesn't exist
            MOCK_DEST_TOKEN_ACCOUNT,  # Destination account after creation
        ]

        # Mock transaction signature
        mock_wallet_client.send_transaction = AsyncMock(return_value="mock_signature")

        signature = await spl_token_service.transfer_token_by_mint_address(
            mock_wallet_client, transfer_params
        )
    
    assert signature == "mock_signature"

    # Step 4: Verify final balance
    mock_balance.value = {"amount": 1000000, "decimals": 6, "uiAmount": 1.0}
    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist") as mock_exists:
        mock_exists.return_value = MOCK_TOKEN_ACCOUNT
        final_balance = await spl_token_service.get_token_balance_by_mint_address(
            mock_wallet_client, balance_params
        )
    
    assert final_balance["amount"] == 1000000
    assert final_balance["uiAmount"] == 1.0


@pytest.mark.asyncio
async def test_transfer_error_handling(spl_token_service, mock_wallet_client):
    """Test error handling during token transfer."""
    # Test invalid mint address
    with pytest.raises(InvalidTokenAddressError):
        params = TransferTokenByMintAddressParameters(
            to=MOCK_RECIPIENT_ADDRESS,
            mint_address="invalid_mint",
            amount=1000000,
        )
        await spl_token_service.transfer_token_by_mint_address(mock_wallet_client, params)

    # Test non-existent source account
    with pytest.raises(TokenAccountNotFoundError):
        params = TransferTokenByMintAddressParameters(
            to=MOCK_RECIPIENT_ADDRESS,
            mint_address=USDC_MINT_ADDRESS,
            amount=1000000,
        )
        with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist") as mock_exists:
            mock_exists.return_value = None
            await spl_token_service.transfer_token_by_mint_address(mock_wallet_client, params)

    # Test failed transfer
    with pytest.raises(TokenTransferError):
        params = TransferTokenByMintAddressParameters(
            to=MOCK_RECIPIENT_ADDRESS,
            mint_address=USDC_MINT_ADDRESS,
            amount=1000000,
        )
        with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist") as mock_exists:
            mock_exists.return_value = MOCK_TOKEN_ACCOUNT
            mock_wallet_client.send_transaction = AsyncMock(side_effect=Exception("Network error"))
            await spl_token_service.transfer_token_by_mint_address(mock_wallet_client, params)


@pytest.mark.asyncio
async def test_token_info_error_handling(spl_token_service):
    """Test error handling for token info retrieval."""
    # Test non-existent token
    with pytest.raises(TokenNotFoundError):
        params = GetTokenMintAddressBySymbolParameters(symbol="NONEXISTENT")
        await spl_token_service.get_token_info_by_symbol(params)

    # Test invalid network
    service = SplTokenService(network="invalid_network")
    with pytest.raises(TokenNotFoundError):
        params = GetTokenMintAddressBySymbolParameters(symbol="USDC")
        await service.get_token_info_by_symbol(params)
