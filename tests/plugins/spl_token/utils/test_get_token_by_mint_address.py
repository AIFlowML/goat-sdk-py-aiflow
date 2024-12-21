"""Tests for get_token_by_mint_address utility function."""

from goat_sdk.plugins.spl_token.utils.get_token_by_mint_address import get_token_by_mint_address
from goat_sdk.plugins.spl_token.models import Token


def test_get_token_by_mint_address_found():
    """Test getting token by mint address when token exists."""
    test_token = Token(
        symbol="TEST",
        name="Test Token",
        decimals=6,
        mint_addresses={
            "mainnet": "test_mint_address",
            "devnet": "test_devnet_address",
            "testnet": "test_testnet_address",
        }
    )

    # Test mainnet
    token = get_token_by_mint_address("test_mint_address", "mainnet")
    assert token is not None
    assert token.symbol == "TEST"
    assert token.decimals == 6
    assert token.mint_addresses["mainnet"] == "test_mint_address"

    # Test devnet
    token = get_token_by_mint_address("test_devnet_address", "devnet")
    assert token is not None
    assert token.symbol == "TEST"
    assert token.decimals == 6
    assert token.mint_addresses["devnet"] == "test_devnet_address"


def test_get_token_by_mint_address_not_found():
    """Test getting token by mint address when token doesn't exist."""
    token = get_token_by_mint_address("nonexistent_address", "mainnet")
    assert token is None


def test_get_token_by_mint_address_real_tokens():
    """Test getting real SPL tokens by mint address."""
    # Test USDC mainnet
    token = get_token_by_mint_address(
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "mainnet"
    )
    assert token is not None
    assert token.symbol == "USDC"
    assert token.decimals == 6
    assert token.mint_addresses["mainnet"] == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    # Test USDC devnet
    token = get_token_by_mint_address(
        "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU", "devnet"
    )
    assert token is not None
    assert token.symbol == "USDC"
    assert token.decimals == 6
    assert token.mint_addresses["devnet"] == "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
