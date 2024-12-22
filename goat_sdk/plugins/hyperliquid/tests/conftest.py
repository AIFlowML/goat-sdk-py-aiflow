"""Test fixtures for Hyperliquid plugin."""

import os
import pytest
import aiohttp

from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin

@pytest.fixture
async def plugin():
    """Create a Hyperliquid plugin instance for testing."""
    api_key = os.getenv("HYPERLIQUID_API_KEY", "test_key")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET", "test_secret")
    
    plugin = HyperliquidPlugin(
        api_key=api_key,
        api_secret=api_secret,
        testnet=True
    )
    
    yield plugin
    
    await plugin.close()