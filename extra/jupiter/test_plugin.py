"""Tests for Jupiter plugin."""

import pytest
from unittest.mock import MagicMock

from goat_sdk.core.chain import Chain
from goat_sdk.plugins.jupiter.plugin import jupiter, JupiterPlugin
from goat_sdk.plugins.jupiter.service import JupiterService


def test_plugin_initialization():
    """Test plugin initialization."""
    plugin = jupiter()
    assert isinstance(plugin, JupiterPlugin)
    assert plugin.name == "jupiter"
    assert len(plugin.tools) == 1
    assert isinstance(plugin.tools[0], JupiterService)


def test_supports_chain():
    """Test chain support check."""
    plugin = jupiter()

    # Test Solana chain support
    solana_chain = Chain(type="solana", network="mainnet")
    assert plugin.supports_chain(solana_chain) is True

    # Test other chains
    ethereum_chain = Chain(type="ethereum", network="mainnet")
    assert plugin.supports_chain(ethereum_chain) is False


def test_plugin_tools():
    """Test plugin tools registration."""
    plugin = jupiter()
    service = plugin.tools[0]

    # Verify tool decorators are applied
    assert hasattr(service.get_quote, "__tool__")
    assert hasattr(service.swap_tokens, "__tool__")

    # Check tool metadata
    assert service.get_quote.__tool__["description"] == "Get a quote for a swap on the Jupiter DEX"
    assert service.swap_tokens.__tool__["description"] == "Swap an SPL token for another token on the Jupiter DEX" 