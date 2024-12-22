"""Hyperliquid plugin implementation."""

import logging
from typing import List, Optional, Dict, Any

import aiohttp

from .service import HyperliquidService
from .types.order import (
    OrderRequest, OrderResponse, OrderResult,
    OrderSide, OrderStatus, OrderType
)
from .types.market import (
    MarketSummary, OrderbookResponse, OrderbookLevel,
    TradeInfo
)
from .config import HyperliquidConfig

class HyperliquidPlugin:
    """Plugin for interacting with Hyperliquid exchange."""
    
    def __init__(
        self,
        config: Optional[HyperliquidConfig] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize plugin.
        
        Args:
            config: Optional configuration object
            api_key: API key (overridden by config if provided)
            api_secret: API secret (overridden by config if provided)
            testnet: Whether to use testnet (overridden by config if provided)
            session: Optional aiohttp session
            logger: Optional logger
        """
        if config:
            self.api_key = config.api_key
            self.api_secret = config.api_secret
            self.testnet = config.testnet
            self.use_ssl = config.use_ssl
            self.ssl_verify = config.ssl_verify
        else:
            self.api_key = api_key
            self.api_secret = api_secret
            self.testnet = testnet
            self.use_ssl = True
            self.ssl_verify = True
            
        self.session = session
        self.logger = logger or logging.getLogger(__name__)
        
        self._services: Dict[bool, HyperliquidService] = {}
        
    def _get_service(self, testnet: bool = False) -> HyperliquidService:
        """Get service instance.
        
        Args:
            testnet: Whether to use testnet
            
        Returns:
            Service instance
        """
        if testnet not in self._services:
            self._services[testnet] = HyperliquidService(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=testnet,
                session=self.session,
                logger=self.logger,
                use_ssl=self.use_ssl,
                ssl_verify=self.ssl_verify
            )
        return self._services[testnet]
        
    async def close(self):
        """Close plugin connections."""
        for service in self._services.values():
            await service.close()
            
    # Market Data Methods
    async def get_markets(self, testnet: bool = False) -> List[str]:
        """Get list of available markets.
        
        Args:
            testnet: Whether to use testnet
            
        Returns:
            List of market symbols
        """
        service = self._get_service(testnet)
        return await service.get_markets()
        
    async def get_market_summary(
        self,
        coin: str,
        testnet: bool = False
    ) -> MarketSummary:
        """Get market summary.
        
        Args:
            coin: Market symbol
            testnet: Whether to use testnet
            
        Returns:
            Market summary
        """
        service = self._get_service(testnet)
        return await service.get_market_summary(coin)
        
    async def get_orderbook(
        self,
        coin: str,
        depth: int = 100,
        testnet: bool = False
    ) -> OrderbookResponse:
        """Get orderbook.
        
        Args:
            coin: Market symbol
            depth: Orderbook depth
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
        """Get recent trades.
        
        Args:
            coin: Market symbol
            limit: Number of trades to return
            testnet: Whether to use testnet
            
        Returns:
            List of trades
        """
        service = self._get_service(testnet)
        return await service.get_recent_trades(coin, limit)
        
    # Order Management Methods
    async def create_order(
        self,
        request: OrderRequest,
        testnet: bool = False
    ) -> OrderResult:
        """Create a new order.
        
        Args:
            request: Order request parameters
            testnet: Whether to use testnet
            
        Returns:
            Order result
        """
        service = self._get_service(testnet)
        return await service.create_order(request)
        
    async def cancel_order(
        self,
        coin: str,
        order_id: str,
        testnet: bool = False
    ) -> OrderResult:
        """Cancel an existing order.
        
        Args:
            coin: The coin symbol
            order_id: The order ID to cancel
            testnet: Whether to use testnet
            
        Returns:
            Order result
        """
        service = self._get_service(testnet)
        return await service.cancel_order(coin, order_id)
        
    async def cancel_all_orders(
        self,
        coin: Optional[str] = None,
        testnet: bool = False
    ) -> List[OrderResult]:
        """Cancel all open orders.
        
        Args:
            coin: Optional coin symbol to cancel orders for
            testnet: Whether to use testnet
            
        Returns:
            List of order results
        """
        service = self._get_service(testnet)
        return await service.cancel_all_orders(coin)
        
    async def get_open_orders(
        self,
        coin: Optional[str] = None,
        testnet: bool = False
    ) -> List[OrderResponse]:
        """Get all open orders.
        
        Args:
            coin: Optional coin symbol to filter orders
            testnet: Whether to use testnet
            
        Returns:
            List of open orders
        """
        service = self._get_service(testnet)
        return await service.get_open_orders(coin)
        
    async def get_order_history(
        self,
        coin: Optional[str] = None,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        testnet: bool = False
    ) -> List[OrderResponse]:
        """Get order history.
        
        Args:
            coin: Optional coin symbol to filter orders
            limit: Number of orders to return
            start_time: Optional start time in milliseconds
            end_time: Optional end time in milliseconds
            testnet: Whether to use testnet
            
        Returns:
            List of historical orders
        """
        service = self._get_service(testnet)
        return await service.get_order_history(
            coin=coin,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
    async def get_order_status(
        self,
        coin: str,
        order_id: str,
        testnet: bool = False
    ) -> OrderResponse:
        """Get status of a specific order.
        
        Args:
            coin: The coin symbol
            order_id: The order ID
            testnet: Whether to use testnet
            
        Returns:
            Order response
        """
        service = self._get_service(testnet)
        return await service.get_order_status(coin, order_id)