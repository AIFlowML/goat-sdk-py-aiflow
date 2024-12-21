"""Tests for Tensor client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from solana.transaction import Transaction, TransactionInstruction

from goat_sdk.plugins.tensor.client import TensorClient
from goat_sdk.plugins.tensor.config import TensorConfig
from goat_sdk.plugins.tensor.errors import (
    NFTInfoError,
    BuyListingError,
    TransactionError,
)


@pytest.mark.asyncio
async def test_get_nft_info(mock_nft_info):
    """Test get_nft_info method."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[mock_nft_info.model_dump(by_alias=True)])
    mock_session.get = AsyncMock(return_value=mock_response)
    client._session = mock_session

    nft_info = await client.get_nft_info(mint_hash="0x" + "22" * 32)

    assert nft_info.onchain_id == mock_nft_info.onchain_id
    assert nft_info.name == mock_nft_info.name
    assert nft_info.image_uri == mock_nft_info.image_uri
    assert nft_info.listing.price == mock_nft_info.listing.price


@pytest.mark.asyncio
async def test_get_nft_info_failure():
    """Test get_nft_info method failure case."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Invalid mint hash"})
    mock_session.get = AsyncMock(return_value=mock_response)
    client._session = mock_session

    with pytest.raises(Exception, match="Failed to get NFT info: Invalid mint hash"):
        await client.get_nft_info(mint_hash="0x" + "22" * 32)


@pytest.mark.asyncio
async def test_get_buy_listing_transaction(mock_wallet_client, mock_nft_info, mock_buy_listing_transaction_response):
    """Test get_buy_listing_transaction method."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    
    # Mock NFT info response
    mock_nft_response = AsyncMock()
    mock_nft_response.status = 200
    mock_nft_response.json = AsyncMock(return_value=[mock_nft_info.model_dump(by_alias=True)])
    
    # Mock buy listing response
    mock_buy_response = AsyncMock()
    mock_buy_response.status = 200
    mock_buy_response.json = AsyncMock(return_value=mock_buy_listing_transaction_response.model_dump(by_alias=True))
    
    mock_session.get = AsyncMock(side_effect=[mock_nft_response, mock_buy_response])
    client._session = mock_session

    # Mock transaction deserialization
    mock_transaction = Transaction()
    mock_transaction.recent_blockhash = "11111111111111111111111111111111"
    mock_instructions = [MagicMock(spec=TransactionInstruction)]

    with patch("goat_sdk.plugins.tensor.utils.transaction.deserialize_tx_response_to_instructions", 
              return_value=(mock_transaction, mock_instructions)):
        result = await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            mint_hash="0x" + "22" * 32,
        )

        assert isinstance(result["transaction"], Transaction)
        assert len(result["instructions"]) == len(mock_instructions)
        assert all(isinstance(instr, TransactionInstruction) for instr in result["instructions"])


@pytest.mark.asyncio
async def test_get_buy_listing_transaction_failure(mock_wallet_client, mock_nft_info):
    """Test get_buy_listing_transaction method failure case."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    
    # Mock NFT info response
    mock_nft_response = AsyncMock()
    mock_nft_response.status = 200
    mock_nft_response.json = AsyncMock(return_value=[mock_nft_info.model_dump(by_alias=True)])
    
    # Mock buy listing response
    mock_buy_response = AsyncMock()
    mock_buy_response.status = 400
    mock_buy_response.json = AsyncMock(return_value={"error": "Invalid transaction"})
    
    mock_session.get = AsyncMock(side_effect=[mock_nft_response, mock_buy_response])
    client._session = mock_session

    with pytest.raises(Exception, match="Failed to get buy listing transaction: Invalid transaction"):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            mint_hash="0x" + "22" * 32,
        )


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization without session."""
    client = TensorClient()
    assert client._session is None
    assert client.config is not None

    client = TensorClient(session=AsyncMock())
    assert client._session is not None


@pytest.mark.asyncio
async def test_context_manager():
    """Test client context manager."""
    client = TensorClient()
    assert client._session is None

    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.closed = False

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with client:
            assert client._session is not None

        assert client._session is None
        await mock_session.close.aclose()


@pytest.mark.asyncio
async def test_get_nft_info_not_initialized():
    """Test get_nft_info without initializing client."""
    client = TensorClient()
    
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client.get_nft_info(mint_hash="0x" + "22" * 32)


@pytest.mark.asyncio
async def test_get_buy_listing_transaction_not_initialized(mock_wallet_client):
    """Test get_buy_listing_transaction without initializing client."""
    client = TensorClient()
    
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            mint_hash="0x" + "22" * 32,
        )


@pytest.mark.asyncio
async def test_get_buy_listing_transaction_no_listing(mock_wallet_client, mock_nft_info):
    """Test get_buy_listing_transaction with no listing."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    
    # Mock NFT info response without listing
    nft_info = mock_nft_info.model_dump(by_alias=True)
    nft_info["listing"] = None
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=[nft_info])
    
    mock_session.get = AsyncMock(return_value=mock_response)
    client._session = mock_session

    with pytest.raises(Exception, match="No listing found for"):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            mint_hash="0x" + "22" * 32,
        )


@pytest.mark.asyncio
async def test_retry_on_network_error():
    """Test retry mechanism on network error."""
    client = TensorClient(config=TensorConfig(api_key="test_key"))
    mock_session = AsyncMock()
    
    # First call raises network error, second call succeeds
    mock_session.get = AsyncMock(side_effect=[
        aiohttp.ClientError("Network error"),
        AsyncMock(
            status=200,
            json=AsyncMock(return_value=[{
                "onchainId": "0x" + "22" * 32,
                "attributes": [],
                "name": "Test NFT",
            }]),
        ),
    ])
    client._session = mock_session

    async with client:
        with pytest.raises(Exception, match="Failed to get NFT info: Network error"):
            await client.get_nft_info(mint_hash="0x" + "22" * 32)