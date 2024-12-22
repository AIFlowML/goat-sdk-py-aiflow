"""
Base test class for Tensor plugin tests.
"""
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from tests.base_test import BaseGoatTest

class TensorTestBase(BaseGoatTest):
    """Base test class for Tensor plugin tests with specific Tensor testing utilities."""

    def setup_tensor_pool(
        self,
        mock_contract_factory,
        address: str,
        nft_address: str,
        token_address: str,
        floor_price: int = 1000000000000000000,  # 1 ETH
        tvl: int = 100000000000000000000,  # 100 ETH
    ):
        """Helper to setup a Tensor pool contract mock."""
        return mock_contract_factory(
            address=address,
            custom_functions={
                "nftAddress": lambda: nft_address,
                "tokenAddress": lambda: token_address,
                "getFloorPrice": lambda: floor_price,
                "getTVL": lambda: tvl,
                "buy": lambda token_ids, max_price: True,
                "sell": lambda token_ids, min_price: True,
                "deposit": lambda amount: True,
                "withdraw": lambda amount: True,
            }
        )

    def setup_tensor_oracle(
        self,
        base_price: Decimal = Decimal("1.0"),
        volatility: Decimal = Decimal("0.1"),
    ):
        """Helper to setup a mock Tensor price oracle."""
        oracle = MagicMock()
        oracle.get_floor_price = AsyncMock(return_value=base_price)
        oracle.get_price_range = AsyncMock(
            return_value=(
                base_price * (1 - volatility),
                base_price * (1 + volatility)
            )
        )
        return oracle

    def setup_tensor_indexer(
        self,
        collections: List[Dict[str, Any]] = None,
        trades: List[Dict[str, Any]] = None,
    ):
        """Helper to setup a mock Tensor indexer service."""
        indexer = MagicMock()
        indexer.get_collections = AsyncMock(return_value=collections or [])
        indexer.get_recent_trades = AsyncMock(return_value=trades or [])
        indexer.get_collection_stats = AsyncMock(
            return_value={
                "floor_price": 1.0,
                "volume_24h": 100.0,
                "market_cap": 1000.0,
                "num_listings": 10,
            }
        )
        return indexer

    def create_mock_collection_data(
        self,
        name: str = "Test Collection",
        symbol: str = "TEST",
        address: str = "0x" + "1" * 40,
        verified: bool = True,
    ) -> Dict[str, Any]:
        """Create mock collection data."""
        return {
            "name": name,
            "symbol": symbol,
            "address": address,
            "verified": verified,
            "stats": {
                "floor_price": 1.0,
                "volume_24h": 100.0,
                "market_cap": 1000.0,
                "num_listings": 10,
            },
            "metadata": {
                "description": "A test collection",
                "image": "https://test.com/image.png",
                "external_url": "https://test.com",
            },
        }

    def create_mock_trade_data(
        self,
        token_id: int = 1,
        price: float = 1.0,
        seller: str = "0x" + "1" * 40,
        buyer: str = "0x" + "2" * 40,
        timestamp: int = 1640995200,  # 2022-01-01
    ) -> Dict[str, Any]:
        """Create mock trade data."""
        return {
            "token_id": token_id,
            "price": price,
            "seller": seller,
            "buyer": buyer,
            "timestamp": timestamp,
            "transaction_hash": "0x" + "a" * 64,
            "block_number": 1000000,
        }
