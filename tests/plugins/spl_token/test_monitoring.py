import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Optional
from prometheus_client import REGISTRY
from solders.rpc.responses import GetHealthResp, GetVersionResp
from solders.rpc import errors as rpc_errors

from goat_sdk.plugins.spl_token.monitoring import (
    NetworkValidationError,
    MinTransferValidationError,
    _validate_network,
    validate_minimum_transfer,
    monitor_mode_performance,
    monitor_mode_validation,
    trace_operation,
    with_retries,
)
from goat_sdk.plugins.spl_token.parameters import ModeConfig

@pytest.mark.asyncio
async def test_validate_network():
    """Test network validation functionality."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Test successful validation
    await _validate_network(mock_network, mode_config=ModeConfig())

@pytest.mark.asyncio
async def test_min_transfer_validation():
    """Test minimum transfer validation logic."""
    # Mock network object with minimum transfer limit
    mock_network = MagicMock()
    mock_network.min_transfer_amount = 1000

    # Test with amount below minimum
    with pytest.raises(MinTransferValidationError, match="Transfer amount 500 is below minimum 1000"):
        await validate_minimum_transfer(mock_network, 500)

    # Test with amount above minimum
    await validate_minimum_transfer(mock_network, 1500)

@pytest.mark.asyncio
async def test_trace_operation():
    """Test operation tracing."""
    # Mock function
    async def mock_func(*args, **kwargs):
        return "success"

    # Apply decorator
    decorated = trace_operation("test_operation")(mock_func)

    # Test successful execution
    result = await decorated(MagicMock(), mode_config=ModeConfig())
    assert result == "success"

@pytest.mark.asyncio
async def test_with_retries():
    """Test retry logic."""
    # Mock function that fails twice then succeeds
    mock_func = AsyncMock(side_effect=[Exception("Retry 1"), Exception("Retry 2"), "success"])

    # Apply decorator
    decorated = with_retries("test_operation", max_attempts=3)(mock_func)

    # Test successful retry
    result = await decorated(MagicMock(), mode_config=ModeConfig())
    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_monitor_mode_performance():
    """Test Mode performance monitoring."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Test successful monitoring
    await _validate_network(mock_network, mode_config=ModeConfig())

@pytest.mark.asyncio
async def test_error_monitoring():
    """Test error monitoring."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock function that raises an error
    async def mock_func(*args, **kwargs):
        raise Exception("Test error")

    # Apply decorator
    decorated = monitor_mode_performance(mock_func)

    # Test error case
    with pytest.raises(Exception, match="Test error"):
        await decorated(mock_network, mode_config=ModeConfig())

    # Check error metrics
    metric_value = REGISTRY.get_sample_value(
        "spl_token_operation_errors_total",
        {"operation": mock_func.__name__, "network": "testnet", "mode_enabled": "true"}
    )
    assert metric_value == 1

@pytest.mark.asyncio
async def test_mode_validation_metrics():
    """Test Mode validation metrics."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Test successful validation
    await _validate_network(mock_network, mode_config=ModeConfig())

    # Check validation metrics
    metric_value = REGISTRY.get_sample_value(
        "spl_token_validation_duration_seconds_count",
        {"validation_type": "_validate_network", "network": "testnet", "mode_enabled": "true"}
    )
    assert metric_value is not None

@pytest.mark.asyncio
async def test_mode_performance_metrics():
    """Test Mode performance metrics."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Create a test function with mode performance monitoring
    @monitor_mode_performance
    async def test_func(network: Any, mode_config: Optional[ModeConfig] = None) -> None:
        await _validate_network(network, mode_config=mode_config)

    # Test successful monitoring
    await test_func(mock_network, mode_config=ModeConfig())

    # Check performance metrics
    metric_value = REGISTRY.get_sample_value(
        "spl_token_operation_duration_seconds_sum",
        {"operation": "test_func", "network": "testnet", "mode_enabled": "true"}
    )
    assert metric_value is not None

@pytest.mark.asyncio
async def test_validate_network_success():
    """Test successful network validation."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Test successful validation
    await _validate_network(mock_network, mode_config=ModeConfig())

@pytest.mark.asyncio
async def test_validate_network_health_failure():
    """Test network validation with health check failure."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock failed health response
    mock_network.client.get_health.return_value = GetHealthResp("error")

    # Test failed validation
    with pytest.raises(NetworkValidationError, match="Network health check failed"):
        await _validate_network(mock_network, mode_config=ModeConfig())

@pytest.mark.asyncio
async def test_validate_network_version_failure():
    """Test network validation with version check failure."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful health response but failed version
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.side_effect = Exception("Version error")

    # Test failed validation
    with pytest.raises(NetworkValidationError, match="Network validation failed"):
        await _validate_network(mock_network, mode_config=ModeConfig())

@pytest.mark.asyncio
async def test_validate_minimum_transfer():
    """Test minimum transfer validation."""
    # Mock network object with minimum transfer limit
    mock_network = MagicMock()
    mock_network.min_transfer_amount = 1000

    # Test with amount below minimum
    with pytest.raises(MinTransferValidationError, match="Transfer amount 500 is below minimum 1000"):
        await validate_minimum_transfer(mock_network, 500)

    # Test with amount above minimum
    await validate_minimum_transfer(mock_network, 1500)

@pytest.mark.asyncio
async def test_monitor_mode_validation():
    """Test mode validation monitoring."""
    # Mock network object
    mock_network = MagicMock()
    mock_network.endpoint = "http://test-endpoint"
    mock_network.client = AsyncMock()
    mock_network.network = "testnet"

    # Mock successful responses
    mock_network.client.get_health.return_value = GetHealthResp("ok")
    mock_network.client.get_version.return_value = MagicMock(value={"solana_core": "1.14.0"})

    # Test successful validation
    await _validate_network(mock_network, mode_config=ModeConfig())

    # Check validation metrics
    metric_value = REGISTRY.get_sample_value(
        "spl_token_validation_duration_seconds_count",
        {"validation_type": "_validate_network", "network": "testnet", "mode_enabled": "true"}
    )
    assert metric_value is not None
