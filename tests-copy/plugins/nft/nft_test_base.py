"""
Base test class for NFT plugin tests.
"""
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock
from tests.base_test import BaseGoatTest

class NFTTestBase(BaseGoatTest):
    """Base test class for NFT plugin tests with specific NFT testing utilities."""

    def setup_nft_contract(
        self,
        mock_contract_factory,
        address: str,
        name: str = "Test NFT",
        symbol: str = "TNFT",
        base_uri: str = "https://api.test.com/token/",
        owner: str = "0x" + "1" * 40,
    ):
        """Helper to setup an NFT contract mock."""
        return mock_contract_factory(
            address=address,
            custom_functions={
                "name": lambda: name,
                "symbol": lambda: symbol,
                "baseURI": lambda: base_uri,
                "tokenURI": lambda token_id: f"{base_uri}{token_id}",
                "ownerOf": lambda token_id: owner,
                "balanceOf": lambda owner: 1,
                "approve": lambda to, token_id: True,
                "getApproved": lambda token_id: "0x" + "0" * 40,
                "setApprovalForAll": lambda operator, approved: True,
                "isApprovedForAll": lambda owner, operator: False,
                "transferFrom": lambda _from, to, token_id: True,
                "safeTransferFrom": lambda _from, to, token_id, data=b"": True,
                "mint": lambda to, token_id: True,
                "burn": lambda token_id: True,
            }
        )

    def setup_marketplace_contract(
        self,
        mock_contract_factory,
        address: str,
        listing_price: int = 1000000000000000000,  # 1 ETH
        platform_fee: int = 250,  # 2.5%
    ):
        """Helper to setup an NFT marketplace contract mock."""
        return mock_contract_factory(
            address=address,
            custom_functions={
                "getListingPrice": lambda: listing_price,
                "getPlatformFee": lambda: platform_fee,
                "createMarketItem": lambda nft, token_id, price: True,
                "createMarketSale": lambda nft, token_id: True,
                "fetchMarketItems": lambda: [],
                "fetchMyNFTs": lambda: [],
                "fetchItemsCreated": lambda: [],
            }
        )

    def setup_metadata_service(self, base_url: str = "https://api.test.com"):
        """Helper to setup a mock IPFS/metadata service."""
        service = MagicMock()
        service.upload_metadata = AsyncMock()
        service.upload_file = AsyncMock()
        service.get_metadata = AsyncMock()
        service.base_url = base_url
        return service

    def create_mock_nft_metadata(
        self,
        name: str = "Test NFT",
        description: str = "A test NFT",
        image: str = "https://test.com/image.png",
        attributes: list = None,
    ) -> Dict[str, Any]:
        """Create mock NFT metadata."""
        return {
            "name": name,
            "description": description,
            "image": image,
            "attributes": attributes or [
                {"trait_type": "Test Trait", "value": "Test Value"}
            ],
        }
