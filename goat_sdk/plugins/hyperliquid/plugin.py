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
     
     Path: goat_sdk/plugins/hyperliquid/utils.py
"""

"""Hyperliquid plugin implementation."""

import logging
from typing import List, Optional, Dict, Any

import aiohttp
import time

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
from .types.agent import AgentApprovalRequest, AgentApprovalAction, AgentApprovalResponse

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
        # Initialize config from environment variables if not provided
        if config is None:
            config = HyperliquidConfig()
            
        # Override config with explicit parameters if provided
        if api_key is not None:
            config.api_key = api_key
        if api_secret is not None:
            config.api_secret = api_secret
        if testnet:
            config.testnet = testnet

        self.config = config
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
                api_key=self.config.api_key,
                api_secret=self.config.api_secret,
                testnet=testnet,
                session=self.session,
                logger=self.logger,
                use_ssl=self.config.use_ssl,
                ssl_verify=self.config.ssl_verify
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
        
    async def approve_agent_wallet(
        self,
        agent_address: str,
        agent_name: Optional[str] = None,
        chain_id: str = "0xa4b1"
    ) -> Dict[str, Any]:
        """Approve an API/Agent wallet for trading."""
        if not self.service:
            raise ValueError("Service not initialized")
            
        action = {
            "hyperliquidChain": "arbitrum_testnet" if self.service.testnet else "arbitrum",
            "signatureChainId": chain_id,
            "agentAddress": agent_address,
            "agentName": agent_name,
            "time": int(time.time() * 1000),
            "nonce": int(time.time() * 1000)
        }
        
        # Send request to the API
        response = await self.service._request(
            "POST",
            "exchange",
            data={"type": "approveAgent", "action": action}
        )
        return response