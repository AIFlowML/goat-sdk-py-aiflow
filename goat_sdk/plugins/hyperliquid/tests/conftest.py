"""Test configuration and fixtures for Hyperliquid plugin tests."""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
import os

from goat_sdk.plugins.hyperliquid.config import HyperliquidConfig
from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin

TEST_ADDRESS = "0xEfDaFA4Cc07BbF8421477db4E3Ce79C96Baf5465"

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-auth",
        action="store_true",
        default=False,
        help="Run tests that require authentication"
    )

@pytest.fixture
def config() -> HyperliquidConfig:
    """Create a test configuration."""
    return HyperliquidConfig(
        api_key=os.getenv("HYPERLIQUID_API_KEY"),
        api_secret=os.getenv("HYPERLIQUID_API_SECRET"),
        use_ssl=True,
        ssl_verify=False,
        market_data_rps=5,
        order_rps=2,
        account_rps=2
    )

@pytest_asyncio.fixture
async def plugin(config: HyperliquidConfig) -> HyperliquidPlugin:
    """Create a test plugin instance."""
    plugin = HyperliquidPlugin(config)
    yield plugin
    await plugin.close()

@pytest.fixture
def test_address() -> str:
    """Get test wallet address."""
    return TEST_ADDRESS 