"""Tests for SPL Token utility functions."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from solana.publickey import PublicKey

from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork
from goat_sdk.plugins.spl_token.utils.get_token_info_by_symbol import get_token_info_by_symbol
from goat_sdk.plugins.spl_token.utils.get_tokens_for_network import get_tokens_for_network
from goat_sdk.plugins.spl_token.utils.does_account_exist import does_account_exist
from goat_sdk.plugins.spl_token.utils.get_token_by_mint_address import get_token_by_mint_address
from goat_sdk.plugins.spl_token.exceptions import TokenAccountNotFoundError

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


def test_get_token_info_by_symbol():
    """Test getting token info by symbol."""
    # Test existing token
    token = get_token_info_by_symbol("USDC", SolanaNetwork.MAINNET)
    assert token is not None
    assert token.symbol == "USDC"
    assert token.mint_addresses[SolanaNetwork.MAINNET] == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    assert token.mode_config["transfer_fee"] == 0.001

    # Test case insensitive
    token = get_token_info_by_symbol("usdc", SolanaNetwork.MAINNET)
    assert token is not None
    assert token.symbol == "USDC"

    # Test non-existent token
    token = get_token_info_by_symbol("NONEXISTENT", SolanaNetwork.MAINNET)
    assert token is None

    # Test token without network
    token = get_token_info_by_symbol("USDC", SolanaNetwork.TESTNET)
    assert token is None


def test_get_tokens_for_network():
    """Test getting tokens for network."""
    # Test mainnet tokens
    mainnet_tokens = get_tokens_for_network(SolanaNetwork.MAINNET)
    assert len(mainnet_tokens) == 2
    assert all(SolanaNetwork.MAINNET in token.mint_addresses for token in mainnet_tokens)

    # Test devnet tokens
    devnet_tokens = get_tokens_for_network(SolanaNetwork.DEVNET)
    assert len(devnet_tokens) == 2
    assert all(SolanaNetwork.DEVNET in token.mint_addresses for token in devnet_tokens)

    # Test testnet tokens (should be empty)
    testnet_tokens = get_tokens_for_network(SolanaNetwork.TESTNET)
    assert len(testnet_tokens) == 0


@pytest.mark.asyncio
async def test_does_account_exist():
    """Test checking if account exists."""
    # Mock connection and account info
    mock_connection = AsyncMock()
    mock_account_info = MagicMock()
    mock_connection.get_account_info.return_value = mock_account_info

    owner = PublicKey("5ZWj7a1f8tWkjBESHKgrLmXshuXxqeGWh9r9TE6aafPF")
    mint = PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    # Test account exists
    mock_account_info.value = True
    account = await does_account_exist(mock_connection, owner, mint)
    assert account is not None

    # Test account doesn't exist
    mock_account_info.value = None
    account = await does_account_exist(mock_connection, owner, mint)
    assert account is None

    # Test Mode retry logic
    mock_account_info.value = None
    mode_config = {"retry_on_not_found": True, "retry_attempts": 2}
    account = await does_account_exist(mock_connection, owner, mint, mode_config)
    assert mock_connection.get_account_info.call_count == 3  # Initial + 2 retries

    # Test Mode error handling
    mock_connection.get_account_info.side_effect = Exception("RPC error")
    mode_config = {"raise_on_error": True}
    with pytest.raises(TokenAccountNotFoundError):
        await does_account_exist(mock_connection, owner, mint, mode_config)

    # Test silent error handling
    mode_config = {"raise_on_error": False}
    account = await does_account_exist(mock_connection, owner, mint, mode_config)
    assert account is None


def test_get_token_by_mint_address():
    """Test getting token by mint address."""
    # Test existing token
    token = get_token_by_mint_address(
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        SolanaNetwork.MAINNET,
    )
    assert token is not None
    assert token.symbol == "USDC"
    assert token.mode_config["transfer_fee"] == 0.001

    # Test non-existent token
    token = get_token_by_mint_address(
        "NonExistentMintAddress",
        SolanaNetwork.MAINNET,
    )
    assert token is None

    # Test invalid mint address
    token = get_token_by_mint_address(
        "",  # Empty mint address
        SolanaNetwork.MAINNET,
    )
    assert token is None

    # Test Mode validation - token not supported by Mode
    token_without_mode = Token(
        symbol="TEST",
        name="Test Token",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "TestMintAddress",
        },
        mode_config=None,  # No Mode config
    )
    MOCK_TOKENS.append(token_without_mode)
    token = get_token_by_mint_address(
        "TestMintAddress",
        SolanaNetwork.MAINNET,
        mode_config={"network_validation": True},
    )
    assert token is None
    MOCK_TOKENS.remove(token_without_mode)

    # Test Mode network validation
    token = get_token_by_mint_address(
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        SolanaNetwork.TESTNET,  # Token not available on testnet
        mode_config={"network_validation": True},
    )
    assert token is None

    # Test Mode error handling
    with pytest.raises(Exception):
        get_token_by_mint_address(
            None,  # Invalid type
            SolanaNetwork.MAINNET,
            mode_config={"raise_on_error": True},
        )
