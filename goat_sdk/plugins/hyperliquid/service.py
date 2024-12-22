"""Service for interacting with Hyperliquid API."""

import logging
import time
import ssl
from decimal import Decimal
from typing import Any, Dict, List, Optional

import aiohttp
import backoff

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
        """Initialize service.
        
        Args:
            api_key: API key
            api_secret: API secret
            testnet: Whether to use testnet
            session: Optional aiohttp session
            logger: Optional logger
            use_ssl: Whether to use SSL
            ssl_verify: Whether to verify SSL certificates
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        self.base_url = "https://api.hyperliquid-testnet.xyz" if testnet else "https://api.hyperliquid.xyz"
        self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws" if testnet else "wss://api.hyperliquid.xyz/ws"
        
        # Create SSL context based on settings
        if use_ssl:
            ssl_context = ssl.create_default_context()
            if not ssl_verify:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = False

        # Create connector with SSL settings
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = session or aiohttp.ClientSession(connector=connector)
        self.logger = logger or logging.getLogger(__name__)
        
        self.rate_limiters = {
            "default": RateLimiter(max_rate=10, time_period=1),  # 10 requests per second
            "order": RateLimiter(max_rate=5, time_period=1),     # 5 orders per second
            "market": RateLimiter(max_rate=2, time_period=1)     # 2 market data requests per second
        }
    
    async def close(self):
        """Close service connections."""
        if self.session and not self.session.closed:
            await self.session.close()
            
    async def _request(
        self,
        method: str,
        endpoint: str,
        auth_required: bool = False,
        rate_limit_type: str = "default",
        **kwargs
    ) -> Any:
        """Make an HTTP request with retries and rate limiting.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            auth_required: Whether authentication is required
            rate_limit_type: Rate limit type for this request
            **kwargs: Additional request arguments
            
        Returns:
            Response data
            
        Raises:
            RequestError: If request fails
        """
        try:
            # Apply rate limiting
            await self.rate_limiters[rate_limit_type].acquire()
            
            # Build URL
            url = f"{self.base_url}/{endpoint}"
            
            # Handle auth if required
            if auth_required and self.api_key:
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                kwargs["headers"]["Authorization"] = f"Bearer {self.api_key}"
            
            # Remove auth_required from kwargs since aiohttp doesn't accept it
            kwargs.pop("auth_required", None)
            
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise RequestError(
                        f"HTTP {response.status}: {error_text}",
                        status_code=response.status
                    )
                return await response.json()
                
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise RequestError(str(e))
            
    async def get_markets(self) -> List[MarketInfo]:
        """Get list of available markets.
        
        Returns:
            List of market info objects
        """
        # Get market metadata
        meta_response = await self._request(
            "POST",
            "info",
            json={"type": "metaAndAssetCtxs"},
            rate_limit_type="market"
        )
        markets = meta_response[0]["universe"]
        
        # Get market states
        state_response = await self._request(
            "POST",
            "info",
            json={"type": "allMids"},
            rate_limit_type="market"
        )
        
        # Combine metadata with states
        result = []
        for market in markets:
            name = market["name"]
            state = state_response.get(name)
            if state:
                result.append(MarketInfo(
                    coin=name,
                    price=Decimal(str(state)),
                    index_price=Decimal(str(state)),  # Using same value since index price not available
                    mark_price=Decimal(str(state)),   # Using same value since mark price not available
                    open_interest=Decimal("0"),       # Not available in this response
                    funding_rate=Decimal("0"),        # Not available in this response
                    volume_24h=Decimal("0"),          # Not available in this response
                    size_decimals=market.get("szDecimals", 0)
                ))
        return result
        
    async def get_market_summary(self, coin: str) -> MarketSummary:
        """Get market summary.
        
        Args:
            coin: Market symbol
            
        Returns:
            Market summary
        """
        response = await self._request(
            "POST",
            "info",
            json={"type": "allMids"},
            rate_limit_type="market"
        )
        
        # Find market data for requested coin
        price = response.get(coin)
        if not price:
            raise ValueError(f"Market not found: {coin}")
            
        return MarketSummary(
            coin=coin,
            price=Decimal(str(price)),
            volume_24h=Decimal("0"),  # Not available in this response
            open_interest=Decimal("0"), # Not available in this response
            funding_rate=Decimal("0")   # Not available in this response
        )
        
    async def get_orderbook(self, coin: str, depth: int = 100) -> OrderbookResponse:
        """Get orderbook.
        
        Args:
            coin: Market symbol
            depth: Orderbook depth
            
        Returns:
            Orderbook response
        """
        response = await self._request(
            "POST",
            "info",
            json={
                "type": "l2Book",
                "coin": coin,
                "depth": depth
            },
            rate_limit_type="market"
        )
        
        return OrderbookResponse(
            coin=coin,
            bids=[
                OrderbookLevel(
                    price=Decimal(str(level.get("px", "0"))),
                    size=Decimal(str(level.get("sz", "0")))
                )
                for level in response.get("levels", [[]])[0]
            ],
            asks=[
                OrderbookLevel(
                    price=Decimal(str(level.get("px", "0"))),
                    size=Decimal(str(level.get("sz", "0")))
                )
                for level in response.get("levels", [[], []])[1]
            ]
        )
        
    async def get_recent_trades(
        self,
        coin: str,
        limit: int = 100
    ) -> List[TradeInfo]:
        """Get recent trades.
        
        Args:
            coin: Market symbol
            limit: Number of trades to return
            
        Returns:
            List of trades
        """
        response = await self._request(
            "POST",
            "info",
            json={
                "type": "recentTrades",
                "coin": coin,
                "limit": limit
            },
            rate_limit_type="market"
        )
        
        return [
            TradeInfo(
                coin=coin,
                id=str(trade.get("tid", "")),
                price=Decimal(str(trade.get("px", "0"))),
                size=Decimal(str(trade.get("sz", "0"))),
                side=OrderSide.BUY if trade.get("side") == "B" else OrderSide.SELL,
                timestamp=trade.get("time", 0)
            )
            for trade in response
        ]
        
    async def create_order(self, request: OrderRequest) -> OrderResult:
        """Create a new order.
        
        Args:
            request: Order request
            
        Returns:
            Order result
        """
        try:
            response = await self._request(
                "POST",
                "trade",
                json={
                    "type": "order",
                    "coin": request.coin,
                    "side": request.side.value,
                    "orderType": request.type.value,
                    "size": str(request.size),
                    "price": str(request.price) if request.price else None,
                    "reduceOnly": request.reduce_only,
                    "postOnly": request.post_only,
                    "clientId": request.client_id
                },
                auth_required=True,
                rate_limit_type="order"
            )
            
            return OrderResult(
                success=True,
                order=OrderResponse(
                    id=response["orderId"],
                    client_id=request.client_id,
                    coin=request.coin,
                    size=request.size,
                    price=request.price,
                    side=request.side,
                    type=request.type,
                    status=OrderStatus.NEW,
                    reduce_only=request.reduce_only,
                    post_only=request.post_only,
                    created_at=int(time.time() * 1000)
                )
            )
            
        except Exception as e:
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
            response = await self._request(
                "POST",
                "trade",
                json={
                    "type": "cancel",
                    "coin": coin,
                    "orderId": order_id
                },
                auth_required=True,
                rate_limit_type="order"
            )
            
            return OrderResult(
                success=True,
                order=OrderResponse(
                    id=order_id,
                    coin=coin,
                    status=OrderStatus.CANCELLED,
                    created_at=int(time.time() * 1000)
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