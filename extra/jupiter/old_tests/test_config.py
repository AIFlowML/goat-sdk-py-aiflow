"""Tests for Jupiter configuration."""

import pytest
from pydantic import ValidationError
import os

from goat_sdk.plugins.jupiter.config import JupiterConfig


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    monkeypatch.delenv("JUPITER_API_KEY", raising=False)
    monkeypatch.delenv("JUPITER_API_URL", raising=False)
    monkeypatch.delenv("JUPITER_MAX_RETRIES", raising=False)
    monkeypatch.delenv("JUPITER_RETRY_DELAY", raising=False)
    monkeypatch.delenv("JUPITER_TIMEOUT", raising=False)
    monkeypatch.delenv("JUPITER_DEFAULT_SLIPPAGE_BPS", raising=False)
    monkeypatch.delenv("JUPITER_AUTO_RETRY_ON_TIMEOUT", raising=False)
    monkeypatch.delenv("JUPITER_AUTO_RETRY_ON_RATE_LIMIT", raising=False)
    monkeypatch.delenv("JUPITER_COMPUTE_UNIT_PRICE", raising=False)
    monkeypatch.delenv("JUPITER_MAX_ACCOUNTS_PER_TX", raising=False)
    monkeypatch.delenv("JUPITER_PREFER_POST_MINT", raising=False)


def test_default_config():
    """Test default configuration values."""
    config = JupiterConfig()
    assert str(config.api_url) == "https://quote-api.jup.ag/v6"
    assert config.max_retries == 3
    assert config.retry_delay == 0.5
    assert config.timeout == 30.0
    assert config.default_slippage_bps == 50
    assert config.auto_retry_on_timeout is True
    assert config.auto_retry_on_rate_limit is True
    assert config.api_key is None
    assert config.compute_unit_price_micro_lamports == 1000
    assert config.max_accounts_per_transaction == 64
    assert config.prefer_post_mint_version is True


def test_custom_config():
    """Test custom configuration values."""
    config = JupiterConfig(
        api_url="https://test-api.jup.ag/v6",
        max_retries=5,
        retry_delay=1.0,
        timeout=60.0,
        default_slippage_bps=100,
        auto_retry_on_timeout=False,
        auto_retry_on_rate_limit=False,
        api_key="test_key",
        compute_unit_price_micro_lamports=1000,
        max_accounts_per_transaction=128,
        prefer_post_mint_version=False,
    )

    assert str(config.api_url) == "https://test-api.jup.ag/v6"
    assert config.max_retries == 5
    assert config.retry_delay == 1.0
    assert config.timeout == 60.0
    assert config.default_slippage_bps == 100
    assert config.auto_retry_on_timeout is False
    assert config.auto_retry_on_rate_limit is False
    assert config.api_key == "test_key"
    assert config.compute_unit_price_micro_lamports == 1000
    assert config.max_accounts_per_transaction == 128
    assert config.prefer_post_mint_version is False


def test_invalid_config():
    """Test configuration validation."""
    # Test invalid API URL
    with pytest.raises(ValidationError):
        JupiterConfig(api_url="not_a_url")

    # Test invalid retry values
    with pytest.raises(ValidationError):
        JupiterConfig(max_retries=-1)

    with pytest.raises(ValidationError):
        JupiterConfig(retry_delay=-0.5)

    # Test invalid timeout
    with pytest.raises(ValidationError):
        JupiterConfig(timeout=0)

    with pytest.raises(ValidationError):
        JupiterConfig(timeout=-1.0)

    # Test invalid slippage
    with pytest.raises(ValidationError):
        JupiterConfig(default_slippage_bps=-1)

    with pytest.raises(ValidationError):
        JupiterConfig(default_slippage_bps=10001)

    # Test invalid compute unit price
    with pytest.raises(ValidationError):
        JupiterConfig(compute_unit_price_micro_lamports=-1)

    # Test invalid max accounts
    with pytest.raises(ValidationError):
        JupiterConfig(max_accounts_per_transaction=0)

    with pytest.raises(ValidationError):
        JupiterConfig(max_accounts_per_transaction=257) 