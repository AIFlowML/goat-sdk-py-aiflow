"""Test fixtures for Tensor plugin."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from goat_sdk.plugins.tensor.config import TensorConfig
from goat_sdk.plugins.tensor.types import (
    NFTInfo,
    LastSale,
    Listing,
    TransactionData,
    TransactionResponse,
    BuyListingTransactionResponse,
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