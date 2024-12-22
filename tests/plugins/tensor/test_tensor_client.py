"""Tests for Tensor client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction as TransactionInstruction
from solders.keypair import Keypair
from solders.hash import Hash
from solders.pubkey import Pubkey

from goat_sdk.plugins.tensor.client import TensorClient
from goat_sdk.plugins.tensor.config import TensorConfig
from goat_sdk.plugins.tensor.types import (
    NFTInfo,
    BuyListingTransactionResponse,
    GetNFTInfoRequest,
    GetBuyListingTransactionRequest,
    LastSale,
    Listing,
    TransactionData,
    TransactionResponse,
)


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
    client.get_address = MagicMock(return_value=client.public_key)
    client.get_connection = MagicMock(return_value=MagicMock(endpoint_url="https://api.mainnet-beta.solana.com"))
    return client


@pytest.fixture
def mock_nft_info():
    """Create mock NFT info."""
    return NFTInfo(
        onchain_id="0x" + "22" * 32,
        attributes=[],
        image_uri="https://example.com/image.png",
        last_sale=LastSale(
            price="1000000000",
            price_unit="lamports",
        ),
        metadata_uri="https://example.com/metadata.json",
        name="Test NFT",
        rarity_rank_tt=1,
        rarity_rank_tt_stat=1,
        rarity_rank_hrtt=1,
        rarity_rank_stat=1,
        sell_royalty_fee_bps=500,
        token_edition="1",
        token_standard="NonFungible",
        hidden=False,
        compressed=False,
        verified_collection="0x" + "33" * 32,
        owner="0x" + "44" * 32,
        inscription=None,
        token_program="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        metadata_program="metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
        transfer_hook_program=None,
        listing_normalized_price="1000000000",
        hybrid_amount=None,
        listing=Listing(
            price="1000000000",
            tx_id="0x" + "55" * 32,
            seller="0x" + "44" * 32,
            source="tensor",
        ),
        slug_display="test-nft",
        coll_id="0x" + "33" * 32,
        coll_name="Test Collection",
        num_mints=1000,
    )


@pytest.fixture
def mock_buy_listing_transaction_response():
    """Create mock buy listing transaction response."""
    return BuyListingTransactionResponse(
        txs=[
            TransactionResponse(
                tx=TransactionData(
                    type="Buffer",
                    data=[0, 1, 2, 3, 4, 5],
                ),
                tx_v0=TransactionData(
                    type="Buffer",
                    data=[0, 1, 2, 3, 4, 5],
                ),
            ),
        ],
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

    request = GetNFTInfoRequest(mint_hash="0x" + "22" * 32)
    nft_info = await client.get_nft_info(request)

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

    request = GetNFTInfoRequest(mint_hash="0x" + "22" * 32)
    with pytest.raises(Exception, match="Failed to get NFT info: Invalid mint hash"):
        await client.get_nft_info(request)


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
    mock_instruction = TransactionInstruction(
        program_id=Pubkey.default(),
        accounts=[],
        data=bytes([0]),
    )
    mock_message = Message.new_with_blockhash(
        [mock_instruction],
        Pubkey.default(),
        Hash([0] * 32),
    )
    mock_transaction = Transaction.new_unsigned(mock_message)
    mock_instructions = [mock_instruction]

    with patch("goat_sdk.plugins.tensor.utils.transaction.deserialize_tx_response_to_instructions", 
              return_value=(mock_transaction, mock_instructions)):
        request = GetBuyListingTransactionRequest(mint_hash="0x" + "22" * 32)
        result = await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            request=request,
        )

        assert isinstance(result["transaction"], Transaction)
        assert len(result["instructions"]) == len(mock_instructions)
        assert len(result["instructions"]) > 0
        assert hasattr(result["instructions"][0], "data")
        assert hasattr(result["instructions"][0], "program_id")


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

    request = GetBuyListingTransactionRequest(mint_hash="0x" + "22" * 32)
    with pytest.raises(Exception, match="Failed to get buy listing transaction: Invalid transaction"):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            request=request,
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
    
    request = GetNFTInfoRequest(mint_hash="0x" + "22" * 32)
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client.get_nft_info(request)


@pytest.mark.asyncio
async def test_get_buy_listing_transaction_not_initialized(mock_wallet_client):
    """Test get_buy_listing_transaction without initializing client."""
    client = TensorClient()
    
    request = GetBuyListingTransactionRequest(mint_hash="0x" + "22" * 32)
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            request=request,
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

    request = GetBuyListingTransactionRequest(mint_hash="0x" + "22" * 32)
    with pytest.raises(Exception, match="No listing found for"):
        await client.get_buy_listing_transaction(
            wallet_client=mock_wallet_client,
            request=request,
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

    request = GetNFTInfoRequest(mint_hash="0x" + "22" * 32)
    async with client:
        with pytest.raises(Exception, match="Failed to get NFT info: Network error"):
            await client.get_nft_info(request) 