"""Hyperliquid plugin implementation."""

import asyncio
from typing import Dict, List, Optional, Any, Union
from pydantic import ValidationError

from goat_sdk.plugin import Plugin, PluginConfig
from goat_sdk.types import Chain

from .config import HyperliquidConfig
from .service import HyperliquidService
from .types.order import (
    OrderType, OrderSide, OrderStatus,
    OrderRequest, OrderResponse, OrderResult
)
from .types.market import (
    MarketInfo, MarketSummary, OrderbookLevel,
    OrderbookResponse, TradeInfo
)
from .types.account import (
    AccountInfo, AccountPosition, MarginInfo,
    LeverageInfo
)

class HyperliquidPlugin(Plugin):
    """Plugin for interacting with Hyperliquid exchange."""
    
    def __init__(self, config: Optional[HyperliquidConfig] = None):
        """Initialize the plugin.
        
        Args:
            config: Optional configuration for the plugin
        """
        super().__init__()
        self.config = config or HyperliquidConfig()
        self._mainnet_service = None
        self._testnet_service = None
        
    @property
    def supported_chains(self) -> List[Chain]:
        """Get supported chains."""
        return [Chain.ARBITRUM]
        
    def _get_service(self, testnet: bool = False) -> HyperliquidService:
        """Get the appropriate service instance.
        
        Args:
            testnet: Whether to use testnet
            
        Returns:
            HyperliquidService instance
        """
        if testnet:
            if not self._testnet_service:
                self._testnet_service = HyperliquidService(self.config, testnet=True)
            return self._testnet_service
        else:
            if not self._mainnet_service:
                self._mainnet_service = HyperliquidService(self.config, testnet=False)
            return self._mainnet_service
            
    async def close(self) -> None:
        """Close all connections."""
        if self._mainnet_service:
            await self._mainnet_service.close()
            self._mainnet_service = None
            
        if self._testnet_service:
            await self._testnet_service.close()
            self._testnet_service = None
            
    # Market Data Methods
    async def get_markets(
        self,
        testnet: bool = False
    ) -> List[MarketInfo]:
        """Get information for all markets.
        
        Args:
            testnet: Whether to use testnet
            
        Returns:
            List of market information
        """
        service = self._get_service(testnet)
        return await service.get_markets()
        
    async def get_market_summary(
        self,
        coin: str,
        testnet: bool = False
    ) -> MarketSummary:
        """Get market summary for a specific coin.
        
        Args:
            coin: The coin symbol
            testnet: Whether to use testnet
            
        Returns:
            Market summary information
        """
        service = self._get_service(testnet)
        return await service.get_market_summary(coin)
        
    async def get_orderbook(
        self,
        coin: str,
        depth: int = 10,
        testnet: bool = False
    ) -> OrderbookResponse:
        """Get orderbook for a market.
        
        Args:
            coin: The coin symbol
            depth: Number of levels to return
            testnet: Whether to use testnet
            
        Returns:
            Orderbook response
        """
        service = self._get_service(testnet)
        return await service.get_orderbook(coin, depth)
        
    async def get_recent_trades(
        self,
        coin: str,
        limit: int = 100,
        testnet: bool = False
    ) -> List[TradeInfo]:
        """Get recent trades for a market.
        
        Args:
            coin: The coin symbol
            limit: Number of trades to return
            testnet: Whether to use testnet
            
        Returns:
            List of trades
        """
        service = self._get_service(testnet)
        return await service.get_recent_trades(coin, limit)
        
    async def subscribe_orderbook(
        self,
        coin: str,
        callback: callable,
        testnet: bool = False
    ) -> None:
        """Subscribe to orderbook updates.
        
        Args:
            coin: The coin symbol
            callback: Callback function for updates
            testnet: Whether to use testnet
        """
        service = self._get_service(testnet)
        await service.subscribe_orderbook(coin, callback)
        
    async def subscribe_trades(
        self,
        coin: str,
        callback: callable,
        testnet: bool = False
    ) -> None:
        """Subscribe to trade updates.
        
        Args:
            coin: The coin symbol
            callback: Callback function for updates
            testnet: Whether to use testnet
        """
        service = self._get_service(testnet)
        await service.subscribe_trades(coin, callback)
        
    async def unsubscribe(
        self,
        coin: str,
        channel: str,
        testnet: bool = False
    ) -> None:
        """Unsubscribe from updates.
        
        Args:
            coin: The coin symbol
            channel: Channel to unsubscribe from
            testnet: Whether to use testnet
        """
        service = self._get_service(testnet)
        await service.unsubscribe(coin, channel)