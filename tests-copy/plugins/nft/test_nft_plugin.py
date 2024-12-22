"""Tests for NFT plugin."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction
from goat_sdk.plugins.nft.plugin import NFTPlugin, TOKEN_PROGRAM_ID
from goat_sdk.plugins.nft.types import (
    TransferNFTParams, MintNFTParams, NFTMetadata, NFTInfo,
    BulkMintNFTParams, BulkTransferNFTParams, UpdateMetadataParams,
    QueryNFTsParams, Creator
)

@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = MagicMock()
    client.provider_url = "https://api.mainnet-beta.solana.com"
    client.get_address = MagicMock(return_value="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ")
    client.send_transaction = AsyncMock(return_value={"hash": "test_signature"})
    client.public_key = PublicKey("GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ")
    return client

@pytest.fixture
def plugin(mock_wallet_client):
    """Create NFT plugin."""
    return NFTPlugin(mock_wallet_client)

@pytest.fixture
def valid_nft_metadata():
    """Create valid NFT metadata for testing."""
    return NFTMetadata(
        name="Test NFT",
        symbol="TEST",
        description="A test NFT",
        image="https://test.uri/image.png",
        seller_fee_basis_points=500,
        attributes=[{"trait_type": "test", "value": "test"}],
        collection={"name": "Test Collection", "family": "Test"},
        creators=[
            Creator(
                address="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ",
                share=100,
                verified=True
            )
        ]
    )

class TestNFTPlugin:
    """Test cases for NFTPlugin using the new test infrastructure."""

    @pytest.fixture
    def nft_plugin(self, mock_wallet_client):
        """Create an NFTPlugin instance with mocked dependencies."""
        return NFTPlugin(mock_wallet_client)

    @pytest.mark.asyncio
    async def test_transfer_nft(self, nft_plugin):
        """Test NFT transfer."""
        params = TransferNFTParams(
            mint_address="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
            to_address="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
        )

        with patch.object(nft_plugin, '_create_transfer_instruction') as mock_create_ix:
            # Create a valid instruction for mocking
            mock_ix = TransactionInstruction(
                program_id=TOKEN_PROGRAM_ID,
                keys=[
                    {"pubkey": PublicKey(params.mint_address), "is_signer": False, "is_writable": True},
                    {"pubkey": PublicKey(params.to_address), "is_signer": False, "is_writable": True},
                    {"pubkey": mock_wallet_client.public_key, "is_signer": True, "is_writable": False}
                ],
                data=b"\x03"  # Transfer instruction
            )
            mock_create_ix.return_value = mock_ix
            
            result = await nft_plugin.transfer_nft(params)

            mock_create_ix.assert_called_once_with(
                PublicKey(params.mint_address),
                PublicKey(params.to_address)
            )
            mock_wallet_client.send_transaction.assert_called_once()
            assert isinstance(
                mock_wallet_client.send_transaction.call_args[0][0],
                Transaction
            )
            assert result == "test_signature"

    @pytest.mark.asyncio
    async def test_bulk_transfer_nft(self, nft_plugin):
        """Test bulk NFT transfer."""
        params = BulkTransferNFTParams(
            mint_addresses=[
                "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
                "GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
            ],
            to_address="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
        )

        with patch.object(nft_plugin, '_create_transfer_instruction') as mock_create_ix:
            mock_ix = TransactionInstruction(
                program_id=TOKEN_PROGRAM_ID,
                keys=[],
                data=b"\x03"
            )
            mock_create_ix.return_value = mock_ix
            
            result = await nft_plugin.bulk_transfer_nft(params)
            assert len(result) == 2
            assert all(sig == "test_signature" for sig in result)
            assert mock_create_ix.call_count == 2

    @pytest.mark.asyncio
    async def test_mint_nft(self, nft_plugin, valid_nft_metadata):
        """Test NFT minting."""
        params = MintNFTParams(
            metadata=valid_nft_metadata,
            is_mutable=True,
            max_supply=100,
            collection_mint="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
            verify_creators=True
        )

        with patch.object(nft_plugin, '_create_mint_account') as mock_create_mint, \
             patch.object(nft_plugin, '_create_metadata_account') as mock_create_metadata, \
             patch.object(nft_plugin, '_create_master_edition') as mock_create_master, \
             patch.object(nft_plugin, '_verify_collection') as mock_verify_collection, \
             patch.object(nft_plugin, '_verify_creator') as mock_verify_creator:
            
            mock_mint = MagicMock()
            mock_mint.public_key = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            mock_create_mint.return_value = mock_mint
            mock_create_metadata.return_value = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            
            result = await nft_plugin.mint_nft(params)
            
            assert isinstance(result, NFTInfo)
            assert result.mint_address == str(mock_mint.public_key)
            assert result.metadata_address == "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"
            assert result.update_authority == str(mock_wallet_client.public_key)
            assert result.metadata == valid_nft_metadata
            mock_verify_collection.assert_called_once()
            mock_verify_creator.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_mint_nft(self, nft_plugin, valid_nft_metadata):
        """Test bulk NFT minting."""
        params = BulkMintNFTParams(
            metadata_list=[valid_nft_metadata, valid_nft_metadata],
            is_mutable=True,
            collection_mint="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
            verify_creators=True
        )

        with patch.object(nft_plugin, '_create_mint_account') as mock_create_mint, \
             patch.object(nft_plugin, '_create_metadata_account') as mock_create_metadata, \
             patch.object(nft_plugin, '_create_master_edition') as mock_create_master:
            
            mock_mint = MagicMock()
            mock_mint.public_key = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            mock_create_mint.return_value = mock_mint
            mock_create_metadata.return_value = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            
            result = await nft_plugin.bulk_mint_nft(params)
            assert len(result) == 2
            assert all(isinstance(nft, NFTInfo) for nft in result)
            assert mock_create_mint.call_count == 2

    @pytest.mark.asyncio
    async def test_update_metadata(self, nft_plugin, valid_nft_metadata):
        """Test updating NFT metadata."""
        params = UpdateMetadataParams(
            mint_address="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
            metadata=valid_nft_metadata,
            is_mutable=True,
            update_authority="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
        )

        with patch.object(nft_plugin, '_create_update_metadata_instruction') as mock_create_ix, \
             patch.object(nft_plugin, '_get_metadata_address') as mock_get_metadata:
            
            mock_get_metadata.return_value = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            mock_ix = TransactionInstruction(
                program_id=TOKEN_PROGRAM_ID,
                keys=[],
                data=b"\x04"
            )
            mock_create_ix.return_value = mock_ix
            
            result = await nft_plugin.update_metadata(params)
            assert isinstance(result, NFTInfo)
            mock_create_ix.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_nft(self, nft_plugin):
        """Test getting NFT information."""
        mint_address = "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"
        
        with patch.object(nft_plugin.connection, 'get_account_info') as mock_get_account, \
             patch.object(nft_plugin, '_get_metadata_address') as mock_get_metadata:
            
            mock_get_account.return_value = {
                'result': {
                    'value': {
                        'data': [1, 'base64_encoded_data'],
                        'owner': str(PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"))
                    }
                }
            }
            mock_get_metadata.return_value = PublicKey("BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY")
            
            nft_info = await nft_plugin.get_nft(mint_address)
            assert nft_info.mint_address == mint_address
            mock_get_account.assert_called()

    @pytest.mark.asyncio
    async def test_get_nfts_by_owner(self, nft_plugin):
        """Test getting NFTs by owner."""
        owner_address = "GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
        
        with patch.object(nft_plugin.connection, 'get_token_accounts_by_owner') as mock_get_accounts, \
             patch.object(nft_plugin, 'get_nft') as mock_get_nft:
            
            mock_get_accounts.return_value = {
                'result': {
                    'value': [
                        {
                            'pubkey': 'account1',
                            'account': {
                                'data': {'parsed': {'info': {'mint': 'mint1'}}}
                            }
                        }
                    ]
                }
            }
            
            nfts = await nft_plugin.get_nfts_by_owner(owner_address)
            assert len(nfts) > 0
            mock_get_accounts.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_nfts(self, nft_plugin, valid_nft_metadata):
        """Test querying NFTs with filters."""
        params = QueryNFTsParams(
            owner="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ",
            collection="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
            creator="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ",
            attributes={"trait_type": "test", "value": "test"},
            page=1,
            limit=10
        )

        with patch.object(nft_plugin, 'get_nfts_by_owner') as mock_get_nfts:
            mock_get_nfts.return_value = [
                NFTInfo(
                    mint_address="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
                    metadata_address="metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s",
                    update_authority="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ",
                    metadata=valid_nft_metadata
                )
            ]
            
            result = await nft_plugin.query_nfts(params)
            assert len(result) == 1
            mock_get_nfts.assert_called_once()

def test_transfer_nft_params_validation():
    """Test NFT transfer parameters validation."""
    # Test valid parameters
    valid_params = TransferNFTParams(
        mint_address="BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY",
        to_address="GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"
    )
    assert valid_params.mint_address == "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"
    assert valid_params.to_address == "GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"

    # Test invalid parameters
    with pytest.raises(ValueError):
        TransferNFTParams(
            mint_address="invalid",
            to_address="invalid"
        )

def test_nft_metadata_validation(valid_nft_metadata):
    """Test NFT metadata validation."""
    # Test valid metadata
    assert valid_nft_metadata.name == "Test NFT"
    assert valid_nft_metadata.symbol == "TEST"
    assert valid_nft_metadata.seller_fee_basis_points == 500
    assert len(valid_nft_metadata.creators) == 1
    assert valid_nft_metadata.creators[0].share == 100

    # Test invalid metadata
    with pytest.raises(ValueError):
        NFTMetadata(
            name="",  # Empty name should fail
            symbol="TOOLONG",  # Symbol too long should fail
            description="Test description",
            image="",  # Empty image URL should fail
            seller_fee_basis_points=15000  # Value too high should fail
        )

@pytest.mark.asyncio
async def test_mint_nft_error_handling(plugin, valid_nft_metadata):
    """Test error handling during NFT minting."""
    params = MintNFTParams(
        metadata=valid_nft_metadata,
        is_mutable=True
    )

    with patch.object(plugin, '_create_mint_account', side_effect=Exception("Mint failed")):
        with pytest.raises(Exception) as exc_info:
            await plugin.mint_nft(params)
        assert str(exc_info.value) == "Mint failed"
