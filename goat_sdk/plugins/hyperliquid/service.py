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

"""Service for interacting with Hyperliquid API."""

import json
import logging
import time
import ssl
import os
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
import backoff
from dotenv import load_dotenv

from .errors import RequestError
from .utils import RateLimiter
from .types.order import (
    OrderRequest, OrderResponse, OrderResult,
    OrderSide, OrderStatus, OrderType
)
from .types.market import (
    MarketInfo, MarketSummary, OrderbookResponse, OrderbookLevel,
    TradeInfo
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class HyperliquidService:
    """Service for interacting with Hyperliquid API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        logger: Optional[logging.Logger] = None,
        use_ssl: bool = True,
        ssl_verify: bool = True
    ):
        """Initialize service."""
        # Load from env if not provided
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_secret = api_secret or os.getenv("API_SECRET")
        self.testnet = testnet if testnet is not None else not os.getenv("MAINNET", "false").lower() == "true"
        self.eth_wallet = os.getenv("ETH_WALLET_ADDRESS")
        
        # Set base URLs based on testnet flag
        if self.testnet:
            self.base_url = "https://api.hyperliquid-testnet.xyz"
            self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws"
        else:
            self.base_url = "https://api.hyperliquid.xyz"
            self.ws_url = "wss://api.hyperliquid.xyz/ws"
        
        # Create SSL context based on settings
        if use_ssl:
            self.ssl_context = ssl.create_default_context()
            if not ssl_verify:
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = False

        # Create connector with SSL settings
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        
        self.session = session or aiohttp.ClientSession(connector=connector)
        self.logger = logger or logging.getLogger(__name__)
        
        self.rate_limiters = {
            "default": RateLimiter(max_rate=10, time_period=1),  # 10 requests per second
            "order": RateLimiter(max_rate=5, time_period=1),     # 5 orders per second
            "market": RateLimiter(max_rate=2, time_period=1)     # 2 market data requests per second
        }
        
    async def close(self):
        """Close service connections."""
        if self.session:
            await self.session.close()
            
    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        auth_required: bool = False,
        rate_limit_key: Optional[str] = None
    ) -> Dict:
        """Make a request to the API."""
        # Use testnet URL if specified
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "goat-sdk/1.0.0"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        # Apply rate limiting if specified
        if rate_limit_key and rate_limit_key in self.rate_limiters:
            await self.rate_limiters[rate_limit_key].acquire()
        
        # Use json parameter if provided, otherwise use data
        request_data = json if json is not None else data
        
        self.logger.debug(f"Making {method} request to {url}")
        self.logger.debug(f"Headers: {headers}")
        self.logger.debug(f"Request data: {request_data}")
        
        async with self.session.request(
            method,
            url,
            json=request_data,
            headers=headers,
            ssl=self.ssl_context
        ) as response:
            response_text = await response.text()
            self.logger.debug(f"Response status: {response.status}")
            self.logger.debug(f"Response text: {response_text}")
            
            if response.status != 200:
                error_msg = f"Request failed with status {response.status}: {response_text}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            try:
                return await response.json()
            except Exception as e:
                self.logger.error(f"Failed to parse JSON response: {response_text}")
                raise
            
    async def get_markets(self) -> List[MarketInfo]:
        """Get list of available markets."""
        meta_response = await self._request(
            "POST",
            "info",
            json={"type": "meta"},
            rate_limit_key="market"
        )
        
        # Get market states for prices
        state_response = await self._request(
            "POST",
            "info",
            json={"type": "allMids"},
            rate_limit_key="market"
        )
        
        markets = []
        for market in meta_response["universe"]:
            name = market["name"]
            price = Decimal(str(state_response.get(name, "0")))
            markets.append(MarketInfo(
                coin=name,
                price=price,
                index_price=price,  # Using mid price as fallback
                mark_price=price,   # Using mid price as fallback
                open_interest=Decimal("0"),  # TODO: Get from API
                funding_rate=Decimal("0"),   # TODO: Get from API
                volume_24h=Decimal("0"),     # TODO: Get from API
                size_decimals=market.get("szDecimals", 8)
            ))
            
        return markets
        
    async def get_market_summary(self, coin: str) -> MarketSummary:
        """Get market summary."""
        # Get meta data
        meta_response = await self._request(
            "POST",
            "info",
            json={"type": "meta"},
            rate_limit_key="market"
        )
        
        # Get current prices
        state_response = await self._request(
            "POST",
            "info",
            json={"type": "allMids"},
            rate_limit_key="market"
        )
        
        market = next((m for m in meta_response["universe"] if m["name"] == coin), None)
        if not market:
            raise ValueError(f"Market {coin} not found")
            
        price = Decimal(str(state_response.get(coin, "0")))
        
        return MarketSummary(
            coin=coin,
            price=price,
            index_price=price,  # Using mid price as fallback
            mark_price=price,   # Using mid price as fallback
            open_interest=Decimal(str(market.get("openInterest", "0"))),
            funding_rate=Decimal(str(market.get("fundingRate", "0"))),
            volume_24h=Decimal(str(market.get("volume24h", "0")))
        )
        
    async def get_orderbook(self, coin: str, depth: int = 100) -> OrderbookResponse:
        """Get orderbook."""
        response = await self._request(
            "POST",
            "info",
            json={
                "type": "l2Book",
                "coin": coin,
                "depth": depth
            },
            rate_limit_key="market"
        )
        
        # API returns levels array where index 0 is bids and index 1 is asks
        levels = response.get("levels", [[], []])
        bids = levels[0] if len(levels) > 0 else []
        asks = levels[1] if len(levels) > 1 else []
        
        return OrderbookResponse(
            coin=coin,
            bids=[
                OrderbookLevel(
                    price=Decimal(str(level["px"])),
                    size=Decimal(str(level["sz"]))
                )
                for level in bids
            ],
            asks=[
                OrderbookLevel(
                    price=Decimal(str(level["px"])),
                    size=Decimal(str(level["sz"]))
                )
                for level in asks
            ]
        )
        
    async def get_recent_trades(self, coin: str, limit: int = 100) -> List[TradeInfo]:
        """Get recent trades."""
        response = await self._request(
            "POST",
            "info",
            json={
                "type": "recentTrades",
                "coin": coin,
                "limit": limit
            },
            rate_limit_key="market"
        )
        
        return [
            TradeInfo(
                coin=coin,
                id=str(trade["tid"]),
                price=Decimal(str(trade["px"])),
                size=Decimal(str(trade["sz"])),
                side=OrderSide.BUY if trade["side"] == "B" else OrderSide.SELL,
                timestamp=int(trade["time"])
            )
            for trade in response
        ]
        
    async def approve_agent_wallet(self, agent_address: str, agent_name: str) -> bool:
        """Approve an agent wallet."""
        try:
            timestamp = int(time.time() * 1000)
            
            request_data = {
                "action": {
                    "type": "approveAgent",
                    "agentAddress": agent_address,
                    "agentName": agent_name,
                    "hyperliquidChain": "Testnet" if self.testnet else "Mainnet",
                    "signatureChainId": "0xa4b1",  # Arbitrum chain ID
                    "nonce": timestamp
                },
                "nonce": timestamp,
                "signature": {
                    "r": "0x...",  # TODO: Generate signature
                    "s": "0x...",
                    "v": 27
                }
            }
            
            self.logger.debug(f"Agent approval request: {request_data}")
            
            response = await self._request(
                "POST",
                "exchange",
                json=request_data,
                auth_required=True,
                rate_limit_key="agent"
            )
            
            self.logger.debug(f"Agent approval response: {response}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Agent approval failed: {str(e)}", exc_info=True)
            raise
        
    async def create_order(self, request: OrderRequest) -> OrderResult:
        """Create a new order."""
        try:
            self.logger.info(f"Creating order: {request}")
            
            # Convert order type to time-in-force
            tif = "Alo" if request.post_only else "Gtc"
            
            # Current timestamp in milliseconds
            timestamp = int(time.time() * 1000)
            
            # Construct order data
            order_data = {
                "action": {
                    "type": "order",
                    "orders": [{
                        "a": 0,  # BTC is index 0 in universe
                        "b": request.side == OrderSide.BUY,
                        "p": str(request.price) if request.price else None,
                        "s": str(request.size),
                        "r": request.reduce_only,
                        "t": {
                            "limit": {
                                "tif": tif
                            }
                        }
                    }],
                    "grouping": "na",
                    "hyperliquidChain": "Testnet" if self.testnet else "Mainnet",
                    "signatureChainId": "0xa4b1",  # Arbitrum chain ID
                    "time": timestamp
                },
                "nonce": timestamp,
                "signature": {
                    "r": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "s": "0x0000000000000000000000000000000000000000000000000000000000000000",
                    "v": 27
                }
            }
            
            self.logger.debug(f"Order request data: {order_data}")
            
            response = await self._request(
                "POST",
                "exchange",
                json=order_data,
                auth_required=True,
                rate_limit_key="order"
            )
            
            self.logger.debug(f"Order response: {response}")
            
            # Extract order ID from response
            order_id = response.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
            if not order_id:
                raise ValueError("Failed to get order ID from response")
            
            return OrderResult(
                success=True,
                order=OrderResponse(
                    id=str(order_id),
                    client_id=request.client_id,
                    coin=request.coin,
                    size=request.size,
                    price=request.price,
                    side=request.side,
                    type=request.type,
                    status=OrderStatus.NEW,
                    reduce_only=request.reduce_only,
                    post_only=request.post_only,
                    created_at=timestamp
                )
            )
            
        except Exception as e:
            self.logger.error(f"Order creation failed: {str(e)}", exc_info=True)
            return OrderResult(
                success=False,
                error=str(e)
            )
            
    async def cancel_order(self, coin: str, order_id: str) -> OrderResult:
        """Cancel an order.
        
        Args:
            coin: Market symbol
            order_id: Order ID
            
        Returns:
            Order result
        """
        try:
            timestamp = int(time.time() * 1000)
            
            response = await self._request(
                "POST",
                "exchange",
                json={
                    "action": {
                        "type": "cancel",
                        "cancels": [{
                            "a": 0,  # BTC is index 0 in universe
                            "o": int(order_id)
                        }],
                        "hyperliquidChain": "Testnet" if self.testnet else "Mainnet",
                        "signatureChainId": "0xa4b1",  # Arbitrum chain ID
                        "time": timestamp
                    },
                    "nonce": timestamp,
                    "signature": {
                        "r": "0x...",  # TODO: Generate signature
                        "s": "0x...",
                        "v": 27
                    }
                },
                auth_required=True,
                rate_limit_key="order"
            )
            
            # Check if cancel was successful
            status = response.get("response", {}).get("data", {}).get("statuses", [])[0]
            if status != "success":
                raise ValueError(f"Cancel failed with status: {status}")
            
            return OrderResult(
                success=True,
                order=OrderResponse(
                    id=order_id,
                    coin=coin,
                    status=OrderStatus.CANCELLED,
                    created_at=timestamp
                )
            )
            
        except Exception as e:
            return OrderResult(
                success=False,
                error=str(e)
            )
            
    async def cancel_all_orders(self, coin: Optional[str] = None) -> List[OrderResult]:
        """Cancel all orders.
        
        Args:
            coin: Optional market symbol to cancel orders for
            
        Returns:
            List of order results
        """
        try:
            response = await self._request(
                "POST",
                "trade",
                json={
                    "type": "cancelAll",
                    "coin": coin
                },
                auth_required=True,
                rate_limit_type="order"
            )
            
            return [
                OrderResult(
                    success=True,
                    order=OrderResponse(
                        id=order_id,
                        coin=coin,
                        status=OrderStatus.CANCELLED,
                        created_at=int(time.time() * 1000)
                    )
                )
                for order_id in response["cancelledOrderIds"]
            ]
            
        except Exception as e:
            return [OrderResult(success=False, error=str(e))]
            
    async def get_open_orders(self, coin: Optional[str] = None) -> List[OrderResponse]:
        """Get open orders.
        
        Args:
            coin: Optional market symbol to filter orders
            
        Returns:
            List of open orders
        """
        response = await self._request(
            "POST",
            "trade",
            json={
                "type": "openOrders",
                "coin": coin
            },
            auth_required=True,
            rate_limit_type="order"
        )
        
        return [
            OrderResponse(
                id=order["oid"],
                client_id=order.get("cloid"),
                coin=order["coin"],
                size=Decimal(str(order["sz"])),
                price=Decimal(str(order["px"])),
                side=OrderSide.BUY if order["side"] == "B" else OrderSide.SELL,
                type=OrderType(order["orderType"]),
                status=OrderStatus.OPEN,
                filled_size=Decimal(str(order.get("filledSz", "0"))),
                remaining_size=Decimal(str(order["remainingSz"])),
                average_fill_price=Decimal(str(order["avgPx"])) if order.get("avgPx") else None,
                fee=Decimal(str(order.get("fee", "0"))),
                created_at=order["timestamp"],
                updated_at=order["lastUpdate"],
                reduce_only=order.get("reduceOnly", False),
                post_only=order.get("postOnly", False)
            )
            for order in response
        ]
        
    async def get_order_history(
        self,
        coin: Optional[str] = None,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[OrderResponse]:
        """Get order history.
        
        Args:
            coin: Optional market symbol to filter orders
            limit: Number of orders to return
            start_time: Optional start time in milliseconds
            end_time: Optional end time in milliseconds
            
        Returns:
            List of orders
        """
        response = await self._request(
            "POST",
            "trade",
            json={
                "type": "orderHistory",
                "coin": coin,
                "limit": limit,
                "startTime": start_time,
                "endTime": end_time
            },
            auth_required=True,
            rate_limit_type="order"
        )
        
        return [
            OrderResponse(
                id=order["oid"],
                client_id=order.get("cloid"),
                coin=order["coin"],
                size=Decimal(str(order["sz"])),
                price=Decimal(str(order["px"])),
                side=OrderSide.BUY if order["side"] == "B" else OrderSide.SELL,
                type=OrderType(order["orderType"]),
                status=OrderStatus(order["status"]),
                filled_size=Decimal(str(order.get("filledSz", "0"))),
                remaining_size=Decimal(str(order["remainingSz"])),
                average_fill_price=Decimal(str(order["avgPx"])) if order.get("avgPx") else None,
                fee=Decimal(str(order.get("fee", "0"))),
                created_at=order["timestamp"],
                updated_at=order["lastUpdate"],
                reduce_only=order.get("reduceOnly", False),
                post_only=order.get("postOnly", False)
            )
            for order in response
        ]
        
    async def get_order_status(self, coin: str, order_id: str) -> OrderResponse:
        """Get order status.
        
        Args:
            coin: Market symbol
            order_id: Order ID
            
        Returns:
            Order response
        """
        response = await self._request(
            "POST",
            "trade",
            json={
                "type": "orderStatus",
                "coin": coin,
                "orderId": order_id
            },
            auth_required=True,
            rate_limit_type="order"
        )
        
        return OrderResponse(
            id=response["oid"],
            client_id=response.get("cloid"),
            coin=response["coin"],
            size=Decimal(str(response["sz"])),
            price=Decimal(str(response["px"])),
            side=OrderSide.BUY if response["side"] == "B" else OrderSide.SELL,
            type=OrderType(response["orderType"]),
            status=OrderStatus(response["status"]),
            filled_size=Decimal(str(response.get("filledSz", "0"))),
            remaining_size=Decimal(str(response["remainingSz"])),
            average_fill_price=Decimal(str(response["avgPx"])) if response.get("avgPx") else None,
            fee=Decimal(str(response.get("fee", "0"))),
            created_at=response["timestamp"],
            updated_at=response["lastUpdate"],
            reduce_only=response.get("reduceOnly", False),
            post_only=response.get("postOnly", False)
        )
