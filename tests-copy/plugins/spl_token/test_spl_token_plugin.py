"""Tests for SPL Token Plugin."""

import pytest
from unittest.mock import MagicMock

from goat_sdk.plugins.spl_token.spl_token_plugin import SplTokenPlugin
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork


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
def spl_token_plugin():
    """Create SPL token plugin instance for testing."""
    return SplTokenPlugin(
        network=SolanaNetwork.MAINNET,
        tokens=MOCK_TOKENS,
        mode_config={"retry_attempts": 3},
    )


def test_plugin_initialization(spl_token_plugin):
    """Test plugin initialization."""
    assert spl_token_plugin.network == SolanaNetwork.MAINNET
    assert len(spl_token_plugin.tokens) == 2
    assert spl_token_plugin.mode_config == {"retry_attempts": 3}


def test_get_tools(spl_token_plugin):
    """Test getting plugin tools."""
    tools = spl_token_plugin.get_tools()
    assert len(tools) == 4
    tool_names = [tool.__name__ for tool in tools]
    assert "get_token_info_by_symbol" in tool_names
    assert "get_token_balance_by_mint_address" in tool_names
    assert "transfer_token_by_mint_address" in tool_names
    assert "convert_to_base_unit" in tool_names


def test_get_tokens_for_network(spl_token_plugin):
    """Test getting tokens for current network."""
    # Test mainnet tokens
    mainnet_tokens = spl_token_plugin.get_tokens_for_network()
    assert len(mainnet_tokens) == 2
    assert all(SolanaNetwork.MAINNET in token.mint_addresses for token in mainnet_tokens)

    # Test devnet tokens
    spl_token_plugin.network = SolanaNetwork.DEVNET
    devnet_tokens = spl_token_plugin.get_tokens_for_network()
    assert len(devnet_tokens) == 2
    assert all(SolanaNetwork.DEVNET in token.mint_addresses for token in devnet_tokens)

    # Test testnet tokens (should be empty)
    spl_token_plugin.network = SolanaNetwork.TESTNET
    testnet_tokens = spl_token_plugin.get_tokens_for_network()
    assert len(testnet_tokens) == 0


def test_get_mode_config(spl_token_plugin):
    """Test getting Mode configuration."""
    config = spl_token_plugin.get_mode_config()
    assert config == {"retry_attempts": 3}

    # Test default config
    plugin = SplTokenPlugin()
    assert plugin.get_mode_config() == {}
