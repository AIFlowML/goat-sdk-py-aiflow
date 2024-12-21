"""Test configuration for Hyperliquid plugin tests."""
import os
import pytest
from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.config import HyperliquidConfig

# Test configuration
os.environ["API_KEY"] = "your_api_key"
os.environ["API_SECRET"] = "your_api_secret"
os.environ["MAINNET"] = "false"
TEST_ADDRESS = "0xEfDaFA4Cc07BbF8421477db4E3Ce79C96Baf5465"

@pytest.fixture
def plugin() -> HyperliquidPlugin:
    """Create a HyperliquidPlugin instance for testing."""
    config = HyperliquidConfig(
        ssl_verify=False,  # Disable SSL verification for testing
        use_ssl=True,  # Still use SSL, just don't verify
        api_key="your_api_key",
        api_secret="your_api_secret"
    )
    return HyperliquidPlugin(config=config)

@pytest.fixture
def test_address() -> str:
    """Return test address."""
    return TEST_ADDRESS 