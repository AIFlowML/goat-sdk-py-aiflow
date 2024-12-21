"""Tests for does_account_exist utility function."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from solana.publickey import PublicKey

from goat_sdk.plugins.spl_token.utils.does_account_exist import does_account_exist


@pytest.mark.asyncio
async def test_does_account_exist_true():
    """Test account existence check when account exists."""
    mock_connection = AsyncMock()
    mock_account_info = MagicMock()
    mock_account_info.value = {"data": b"test_data"}
    mock_connection.get_account_info.return_value = mock_account_info

    account = PublicKey("11111111111111111111111111111111")
    result = await does_account_exist(mock_connection, account)

    assert result == account
    mock_connection.get_account_info.assert_called_once_with(account)


@pytest.mark.asyncio
async def test_does_account_exist_false():
    """Test account existence check when account doesn't exist."""
    mock_connection = AsyncMock()
    mock_account_info = MagicMock()
    mock_account_info.value = None
    mock_connection.get_account_info.return_value = mock_account_info

    account = PublicKey("11111111111111111111111111111111")
    result = await does_account_exist(mock_connection, account)

    assert result is None
    mock_connection.get_account_info.assert_called_once_with(account)


@pytest.mark.asyncio
async def test_does_account_exist_error():
    """Test account existence check when error occurs."""
    mock_connection = AsyncMock()
    mock_connection.get_account_info.side_effect = Exception("RPC error")

    account = PublicKey("11111111111111111111111111111111")
    result = await does_account_exist(mock_connection, account)

    assert result is None
    mock_connection.get_account_info.assert_called_once_with(account)
