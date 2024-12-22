"""Tests for does_account_exist utility function."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from solders.pubkey import Pubkey as PublicKey
from base58 import b58decode

from goat_sdk.plugins.spl_token.utils.does_account_exist import does_account_exist
from goat_sdk.plugins.spl_token.exceptions import TokenAccountNotFoundError


@pytest.mark.asyncio
async def test_does_account_exist_true():
    """Test account exists case."""
    mock_connection = AsyncMock()
    mock_account_info = MagicMock()
    mock_account_info.value = True
    mock_connection.get_account_info = AsyncMock(return_value=mock_account_info)

    owner = PublicKey.from_string("11111111111111111111111111111111")
    mint = PublicKey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    account = await does_account_exist(mock_connection, owner, mint)
    assert account is not None


@pytest.mark.asyncio
async def test_does_account_exist_false():
    """Test account doesn't exist case."""
    mock_connection = AsyncMock()
    mock_account_info = MagicMock()
    mock_account_info.value = None
    mock_connection.get_account_info = AsyncMock(return_value=mock_account_info)

    owner = PublicKey.from_string("11111111111111111111111111111111")
    mint = PublicKey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    account = await does_account_exist(mock_connection, owner, mint)
    assert account is None


@pytest.mark.asyncio
async def test_does_account_exist_error():
    """Test error handling."""
    mock_connection = AsyncMock()
    mock_connection.get_account_info = AsyncMock(side_effect=Exception("RPC error"))
    mock_connection.get_token_accounts_by_owner = AsyncMock(return_value={"value": []})

    owner = PublicKey.from_string("11111111111111111111111111111111")
    mint = PublicKey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")

    account = await does_account_exist(mock_connection, owner, mint)
    assert account is None
