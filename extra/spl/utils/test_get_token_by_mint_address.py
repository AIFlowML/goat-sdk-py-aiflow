"""Tests for get_token_by_mint_address utility function."""

import pytest
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork, TokenType
from goat_sdk.plugins.spl_token.utils.get_token_by_mint_address import get_token_by_mint_address


def test_get_token_by_mint_address_found():
    """Test getting token by mint address when token exists."""
    test_token = Token(
        symbol="TEST",
        name="Test Token",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "TestMintAddress",
            SolanaNetwork.DEVNET: "TestMintAddress",
        },
        logo_uri="https://test.com/logo.png",
        token_type=TokenType.FUNGIBLE
    )

    tokens = [test_token]
    token = get_token_by_mint_address("TestMintAddress", SolanaNetwork.MAINNET, tokens)
    assert token is not None
    assert token.symbol == "TEST"
    assert token.mint_addresses[SolanaNetwork.MAINNET] == "TestMintAddress"


def test_get_token_by_mint_address_not_found():
    """Test getting token by mint address when token doesn't exist."""
    test_token = Token(
        symbol="TEST",
        name="Test Token",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "TestMintAddress",
            SolanaNetwork.DEVNET: "TestMintAddress",
        },
        logo_uri="https://test.com/logo.png",
        token_type=TokenType.FUNGIBLE
    )

    tokens = [test_token]
    token = get_token_by_mint_address("NonExistentMintAddress", SolanaNetwork.MAINNET, tokens)
    assert token is None


def test_get_token_by_mint_address_real_tokens():
    """Test getting token by mint address with real token data."""
    usdc_token = Token(
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            SolanaNetwork.DEVNET: "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        },
        logo_uri="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
        token_type=TokenType.FUNGIBLE
    )

    tokens = [usdc_token]
    token = get_token_by_mint_address("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", SolanaNetwork.MAINNET, tokens)
    assert token is not None
    assert token.symbol == "USDC"
    assert token.mint_addresses[SolanaNetwork.MAINNET] == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
