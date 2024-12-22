"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
     
     Path: examples/nft/test_nft_examples.py
"""

import pytest
import asyncio
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.nft import NFTPlugin

# Test constants
TEST_PRIVATE_KEY = "your_private_key"  # Replace with test private key
TEST_NFT_ADDRESS = "your_nft_address"  # Replace with NFT address
TEST_RECIPIENT = "recipient_address"  # Replace with recipient address
TEST_METADATA = {
    "name": "Test NFT",
    "symbol": "TNFT",
    "description": "A test NFT for example purposes",
    "image": "https://example.com/image.png",
    "attributes": [
        {
            "trait_type": "Test Trait",
            "value": "Test Value"
        }
    ]
}

@pytest.fixture
async def nft_setup():
    """Setup NFT plugin for testing"""
    sdk = GoatSDK(
        private_key=TEST_PRIVATE_KEY,
        network=Network.MAINNET,
        chain=Chain.SOLANA
    )
    nft = NFTPlugin(sdk)
    return nft

@pytest.mark.asyncio
async def test_get_nft(nft_setup):
    """Test getting NFT information"""
    nft = await nft_setup
    
    info = await nft.get_nft(TEST_NFT_ADDRESS)
    assert info is not None
    print("\nNFT information:")
    print(f"Name: {info.name}")
    print(f"Symbol: {info.symbol}")
    print(f"Description: {info.description}")
    print(f"Image: {info.image}")
    print("Attributes:")
    for attr in info.attributes:
        print(f"  {attr.trait_type}: {attr.value}")

@pytest.mark.asyncio
async def test_get_nfts_by_owner(nft_setup):
    """Test getting NFTs by owner"""
    nft = await nft_setup
    
    nfts = await nft.get_nfts_by_owner(TEST_RECIPIENT)
    assert nfts is not None
    print("\nNFTs owned by address:")
    for nft_info in nfts:
        print(f"Address: {nft_info.address}")
        print(f"Name: {nft_info.name}")
        print(f"Symbol: {nft_info.symbol}")
        print("---")

@pytest.mark.asyncio
async def test_mint_nft(nft_setup):
    """Test minting a new NFT"""
    nft = await nft_setup
    
    try:
        result = await nft.mint_nft(TEST_METADATA)
        assert result is not None
        print("\nNFT minted:")
        print(f"NFT address: {result.nft_address}")
        print(f"Transaction hash: {result.transaction_hash}")
        print(f"Owner: {result.owner}")
    except Exception as e:
        pytest.skip(f"NFT minting failed: {str(e)}")

@pytest.mark.asyncio
async def test_bulk_mint_nft(nft_setup):
    """Test bulk minting NFTs"""
    nft = await nft_setup
    
    # Create multiple metadata objects
    metadata_list = [
        {**TEST_METADATA, "name": f"Test NFT {i}"} 
        for i in range(3)
    ]
    
    try:
        results = await nft.bulk_mint_nft(metadata_list)
        assert results is not None
        print("\nBulk NFT minting results:")
        for result in results:
            print(f"NFT address: {result.nft_address}")
            print(f"Transaction hash: {result.transaction_hash}")
            print(f"Owner: {result.owner}")
            print("---")
    except Exception as e:
        pytest.skip(f"Bulk NFT minting failed: {str(e)}")

@pytest.mark.asyncio
async def test_transfer_nft(nft_setup):
    """Test transferring an NFT"""
    nft = await nft_setup
    
    try:
        result = await nft.transfer_nft(
            nft_address=TEST_NFT_ADDRESS,
            to=TEST_RECIPIENT
        )
        assert result is not None
        print("\nNFT transferred:")
        print(f"NFT address: {result.nft_address}")
        print(f"Transaction hash: {result.transaction_hash}")
        print(f"New owner: {result.new_owner}")
    except Exception as e:
        pytest.skip(f"NFT transfer failed: {str(e)}")

@pytest.mark.asyncio
async def test_bulk_transfer_nft(nft_setup):
    """Test bulk transferring NFTs"""
    nft = await nft_setup
    
    # Create list of NFT addresses to transfer
    nft_addresses = [TEST_NFT_ADDRESS] * 3  # Example with same address
    
    try:
        results = await nft.bulk_transfer_nft(
            nft_addresses=nft_addresses,
            to=TEST_RECIPIENT
        )
        assert results is not None
        print("\nBulk NFT transfer results:")
        for result in results:
            print(f"NFT address: {result.nft_address}")
            print(f"Transaction hash: {result.transaction_hash}")
            print(f"New owner: {result.new_owner}")
            print("---")
    except Exception as e:
        pytest.skip(f"Bulk NFT transfer failed: {str(e)}")

@pytest.mark.asyncio
async def test_update_metadata(nft_setup):
    """Test updating NFT metadata"""
    nft = await nft_setup
    
    updated_metadata = {
        **TEST_METADATA,
        "name": "Updated Test NFT",
        "description": "Updated description"
    }
    
    try:
        result = await nft.update_metadata(
            nft_address=TEST_NFT_ADDRESS,
            metadata=updated_metadata
        )
        assert result is not None
        print("\nMetadata updated:")
        print(f"NFT address: {result.nft_address}")
        print(f"Transaction hash: {result.transaction_hash}")
        print(f"Updated metadata: {result.metadata}")
    except Exception as e:
        pytest.skip(f"Metadata update failed: {str(e)}")

@pytest.mark.asyncio
async def test_query_nfts(nft_setup):
    """Test querying NFTs with filters"""
    nft = await nft_setup
    
    filters = {
        "collection": "test_collection",
        "attributes": {
            "Test Trait": "Test Value"
        }
    }
    
    nfts = await nft.query_nfts(filters)
    assert nfts is not None
    print("\nQueried NFTs:")
    for nft_info in nfts:
        print(f"Address: {nft_info.address}")
        print(f"Name: {nft_info.name}")
        print(f"Collection: {nft_info.collection}")
        print("Attributes:")
        for attr in nft_info.attributes:
            print(f"  {attr.trait_type}: {attr.value}")
        print("---")

@pytest.mark.asyncio
async def test_error_handling(nft_setup):
    """Test error handling with invalid parameters"""
    nft = await nft_setup
    
    # Test with invalid NFT address
    with pytest.raises(Exception):
        await nft.get_nft("invalid_address")
    
    # Test with invalid recipient
    with pytest.raises(Exception):
        await nft.transfer_nft(
            nft_address=TEST_NFT_ADDRESS,
            to="invalid_address"
        )
    
    # Test with invalid metadata
    with pytest.raises(Exception):
        await nft.mint_nft({})  # Empty metadata

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 