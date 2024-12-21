"""Tests for SPL Token Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from solana.publickey import PublicKey
from solana.rpc.commitment import Commitment
from solana.rpc.types import RPCResponse

from goat_sdk.plugins.spl_token.spl_token_service import SplTokenService
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork, TokenBalance
from goat_sdk.plugins.spl_token.parameters import (
    GetTokenMintAddressBySymbolParameters,
    GetTokenBalanceByMintAddressParameters,
    TransferTokenByMintAddressParameters,
    ConvertToBaseUnitParameters,
    ModeConfig,
)
from goat_sdk.plugins.spl_token.exceptions import (
    TokenNotFoundError,
    TokenAccountNotFoundError,
    InsufficientBalanceError,
    TokenTransferError,
)


# Mock tokens for testing
MOCK_TOKENS = [
    Token(
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            SolanaNetwork.DEVNET: "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        },
        mode_config={
            "transfer_fee": 0.001,
            "min_transfer": 0.01,
        }
    ),
    Token(
        symbol="SOL",
        name="Solana",
        decimals=9,
        mint_addresses={
            SolanaNetwork.MAINNET: "So11111111111111111111111111111111111111112",
            SolanaNetwork.DEVNET: "So11111111111111111111111111111111111111112",
        },
        mode_config={
            "transfer_fee": 0.0005,
            "min_transfer": 0.001,
        }
    ),
]


@pytest.fixture
def mode_config():
    """Create Mode configuration for testing."""
    return ModeConfig(
        retry_attempts=2,
        retry_on_not_found=True,
        raise_on_error=True,
        network_validation=True,
        min_transfer_validation=True,
    )


@pytest.fixture
def spl_token_service(mode_config):
    """Create SPL token service instance for testing."""
    return SplTokenService(
        network=SolanaNetwork.MAINNET,
        tokens=MOCK_TOKENS,
        mode_config=mode_config,
    )


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client for testing."""
    mock_client = AsyncMock()
    mock_client.public_key = "5ZWj7a1f8tWkjBESHKgrLmXshuXxqeGWh9r9TE6aafPF"
    mock_client.connection = AsyncMock()
    mock_client.send_and_confirm_transaction = AsyncMock(return_value="tx_signature")
    return mock_client


@pytest.mark.asyncio
async def test_get_token_info_by_symbol(spl_token_service):
    """Test getting token info by symbol."""
    # Test existing token
    token = await spl_token_service.get_token_info_by_symbol(
        GetTokenMintAddressBySymbolParameters(symbol="USDC"),
    )
    assert token is not None
    assert token.symbol == "USDC"
    assert token.mode_config["transfer_fee"] == 0.001

    # Test non-existent token
    with pytest.raises(TokenNotFoundError):
        await spl_token_service.get_token_info_by_symbol(
            GetTokenMintAddressBySymbolParameters(symbol="NONEXISTENT"),
        )

    # Test Mode network validation
    spl_token_service.network = SolanaNetwork.TESTNET
    with pytest.raises(TokenNotFoundError):
        await spl_token_service.get_token_info_by_symbol(
            GetTokenMintAddressBySymbolParameters(symbol="USDC"),
        )


@pytest.mark.asyncio
async def test_get_token_balance_by_mint_address(spl_token_service, mock_wallet_client):
    """Test getting token balance by mint address."""
    # Mock account info response
    mock_account_info = MagicMock()
    mock_account_info.value = MagicMock()
    mock_account_info.value.lamports = 1000000  # 1 USDC
    mock_wallet_client.connection.get_account_info.return_value = RPCResponse(
        mock_account_info,
        context=None,
    )

    # Test existing token account
    balance = await spl_token_service.get_token_balance_by_mint_address(
        mock_wallet_client,
        GetTokenBalanceByMintAddressParameters(
            wallet_address=mock_wallet_client.public_key,
            mint_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        ),
    )
    assert balance is not None
    assert balance.balance == 1000000
    assert balance.decimals == 6

    # Test account not found with Mode retry
    mock_wallet_client.connection.get_account_info.return_value = RPCResponse(
        MagicMock(value=None),
        context=None,
    )
    with pytest.raises(TokenAccountNotFoundError):
        await spl_token_service.get_token_balance_by_mint_address(
            mock_wallet_client,
            GetTokenBalanceByMintAddressParameters(
                wallet_address=mock_wallet_client.public_key,
                mint_address="NonExistentMintAddress",
            ),
        )
    assert mock_wallet_client.connection.get_account_info.call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_transfer_token_by_mint_address(spl_token_service, mock_wallet_client):
    """Test transferring tokens by mint address."""
    # Mock balance check
    mock_account_info = MagicMock()
    mock_account_info.value = MagicMock()
    mock_account_info.value.lamports = 2000000  # 2 USDC
    mock_wallet_client.connection.get_account_info.return_value = RPCResponse(
        mock_account_info,
        context=None,
    )

    # Test successful transfer
    signature = await spl_token_service.transfer_token_by_mint_address(
        mock_wallet_client,
        TransferTokenByMintAddressParameters(
            to="7nYS5RkWxvWCDMjEXrTVfj4ChZX54xqvQUVxnUHNSY4U",
            mint_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            amount=1000000,  # 1 USDC
        ),
    )
    assert signature == "tx_signature"

    # Test transfer below minimum amount
    with pytest.raises(TokenTransferError, match="Amount below minimum transfer"):
        await spl_token_service.transfer_token_by_mint_address(
            mock_wallet_client,
            TransferTokenByMintAddressParameters(
                to="7nYS5RkWxvWCDMjEXrTVfj4ChZX54xqvQUVxnUHNSY4U",
                mint_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                amount=1000,  # 0.001 USDC (below minimum)
            ),
        )

    # Test insufficient balance
    mock_account_info.value.lamports = 500000  # 0.5 USDC
    with pytest.raises(InsufficientBalanceError):
        await spl_token_service.transfer_token_by_mint_address(
            mock_wallet_client,
            TransferTokenByMintAddressParameters(
                to="7nYS5RkWxvWCDMjEXrTVfj4ChZX54xqvQUVxnUHNSY4U",
                mint_address="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                amount=1000000,  # 1 USDC
            ),
        )


def test_convert_to_base_unit(spl_token_service):
    """Test converting token amount to base units."""
    # Test normal conversion
    amount = spl_token_service.convert_to_base_unit(
        ConvertToBaseUnitParameters(amount=1.5, decimals=6),
    )
    assert amount == 1500000

    # Test zero amount
    amount = spl_token_service.convert_to_base_unit(
        ConvertToBaseUnitParameters(amount=0, decimals=6),
    )
    assert amount == 0

    # Test large decimals
    amount = spl_token_service.convert_to_base_unit(
        ConvertToBaseUnitParameters(amount=0.000001, decimals=9),
    )
    assert amount == 1000

    # Test error handling
    with pytest.raises(Exception):
        spl_token_service.convert_to_base_unit(
            ConvertToBaseUnitParameters(amount="invalid", decimals=6),
        )
