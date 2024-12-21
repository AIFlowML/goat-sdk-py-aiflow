"""Tests for compressed NFT functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction

from goat_sdk.plugins.nft.plugin import NFTPlugin
from goat_sdk.plugins.nft.types import (
    CompressedNFTParams,
    TransferCompressedNFTParams,
    NFTMetadata,
    Creator,
)

# Valid base58 encoded public keys and asset IDs
MOCK_WALLET = "5MYGMMafYr7G3HymNRqvqyVQQZqYZH1vf8hYx1avJ8Jc"
MOCK_TREE = "7XB3WqaNQv7qQVvQjxhGrJPoiVzVXheeYNJk6F9kKQhB"
MOCK_ASSET_ID = "7XB3WqaNQv7qQVvQjxhGrJPoiVzVXheeYNJk6F9kKQhB"
MOCK_TO_ADDRESS = "9ZNTfG4NyQgxy2SWjSiQoUyBPEvXT2xo7fKc5hPYYJ7b"


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = PublicKey(MOCK_WALLET)
    client.provider_url = "https://api.mainnet-beta.solana.com"
    client.get_address = MagicMock(return_value=str(client.public_key))
    return client


@pytest.fixture
def mock_metadata():
    """Create mock NFT metadata."""
    return NFTMetadata(
        name="Test NFT",
        symbol="TEST",
        description="Test NFT description",
        seller_fee_basis_points=500,
        image="https://example.com/image.png",
        creators=[
            Creator(
                address=MOCK_WALLET,
                share=100,
                verified=True,
            )
        ],
    )


@pytest.mark.asyncio
async def test_mint_compressed_nft(mock_wallet_client, mock_metadata):
    """Test minting a compressed NFT."""
    plugin = NFTPlugin(mock_wallet_client)

    # Mock merkle tree creation
    mock_tree_address = PublicKey(MOCK_TREE)
    with patch.object(plugin, "_create_merkle_tree", return_value=mock_tree_address):
        # Mock mint instruction
        mock_instruction = MagicMock(spec=TransactionInstruction)
        with patch.object(plugin, "_create_compressed_mint_instruction", return_value=mock_instruction):
            # Mock transaction result
            mock_result = {"hash": "test_signature"}
            mock_wallet_client.send_transaction = AsyncMock(return_value=mock_result)

            # Mock leaf info
            mock_leaf_info = {
                "id": MOCK_ASSET_ID,
                "index": 0,
            }
            with patch.object(plugin, "_get_compressed_nft_leaf", return_value=mock_leaf_info):
                # Test mint
                params = CompressedNFTParams(
                    metadata=mock_metadata,
                    max_depth=14,
                    max_buffer_size=64,
                )
                result = await plugin.mint_compressed_nft(params)

                # Verify result
                assert result.asset_id == MOCK_ASSET_ID
                assert result.tree_address == str(mock_tree_address)
                assert result.leaf_index == 0
                assert result.metadata == mock_metadata
                assert result.owner == str(mock_wallet_client.public_key)


@pytest.mark.asyncio
async def test_mint_compressed_nft_with_existing_tree(mock_wallet_client, mock_metadata):
    """Test minting a compressed NFT with existing tree."""
    plugin = NFTPlugin(mock_wallet_client)

    # Mock mint instruction
    mock_instruction = MagicMock(spec=TransactionInstruction)
    with patch.object(plugin, "_create_compressed_mint_instruction", return_value=mock_instruction):
        # Mock transaction result
        mock_result = {"hash": "test_signature"}
        mock_wallet_client.send_transaction = AsyncMock(return_value=mock_result)

        # Mock leaf info
        mock_leaf_info = {
            "id": MOCK_ASSET_ID,
            "index": 0,
        }
        with patch.object(plugin, "_get_compressed_nft_leaf", return_value=mock_leaf_info):
            # Test mint with existing tree
            params = CompressedNFTParams(
                metadata=mock_metadata,
                tree_address=MOCK_TREE,
                max_depth=14,
                max_buffer_size=64,
            )
            result = await plugin.mint_compressed_nft(params)

            # Verify result
            assert result.asset_id == MOCK_ASSET_ID
            assert result.tree_address == params.tree_address
            assert result.leaf_index == 0
            assert result.metadata == mock_metadata
            assert result.owner == str(mock_wallet_client.public_key)


@pytest.mark.asyncio
async def test_transfer_compressed_nft(mock_wallet_client):
    """Test transferring a compressed NFT."""
    plugin = NFTPlugin(mock_wallet_client)

    # Mock asset proof
    mock_proof = {
        "root": "test_root",
        "proof": ["proof1", "proof2"],
    }
    with patch.object(plugin, "_get_asset_with_proof", return_value=mock_proof):
        # Mock transfer instruction
        mock_instruction = MagicMock(spec=TransactionInstruction)
        with patch.object(plugin, "_create_compressed_transfer_instruction", return_value=mock_instruction):
            # Mock transaction result
            mock_result = {"hash": "test_signature"}
            mock_wallet_client.send_transaction = AsyncMock(return_value=mock_result)

            # Test transfer
            params = TransferCompressedNFTParams(
                asset_id=MOCK_ASSET_ID,
                to_address=MOCK_TO_ADDRESS,
            )
            result = await plugin.transfer_compressed_nft(params)

            # Verify result
            assert result == "test_signature"


@pytest.mark.asyncio
async def test_mint_compressed_nft_failure(mock_wallet_client, mock_metadata):
    """Test failure when minting a compressed NFT."""
    plugin = NFTPlugin(mock_wallet_client)

    # Mock merkle tree creation failure
    with patch.object(plugin, "_create_merkle_tree", side_effect=Exception("Tree creation failed")):
        # Test mint failure
        params = CompressedNFTParams(
            metadata=mock_metadata,
            max_depth=14,
            max_buffer_size=64,
        )
        with pytest.raises(Exception, match="Tree creation failed"):
            await plugin.mint_compressed_nft(params)


@pytest.mark.asyncio
async def test_transfer_compressed_nft_failure(mock_wallet_client):
    """Test failure when transferring a compressed NFT."""
    plugin = NFTPlugin(mock_wallet_client)

    # Mock asset proof failure
    with patch.object(plugin, "_get_asset_with_proof", side_effect=Exception("Asset not found")):
        # Test transfer failure
        params = TransferCompressedNFTParams(
            asset_id=MOCK_ASSET_ID,
            to_address=MOCK_TO_ADDRESS,
        )
        with pytest.raises(Exception, match="Asset not found"):
            await plugin.transfer_compressed_nft(params) 