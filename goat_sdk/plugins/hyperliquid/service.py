"""Service layer for Hyperliquid API interactions."""

import asyncio
import hmac
import hashlib
import time
import json
import ssl
from typing import Dict, List, Optional, Any, Union, Callable
import aiohttp
from aiohttp import ClientTimeout, ClientSession, TCPConnector
from websockets.exceptions import WebSocketException
from decimal import Decimal
import logging
import backoff

from .config import HyperliquidConfig
from .types.order import (
    OrderType, OrderSide, OrderStatus,
    OrderRequest, OrderResponse, OrderResult
)
from .models import (
    Market, MarketSummary
)
from .types.market import (
    OrderbookLevel, OrderbookResponse, TradeInfo
)
from .types.account import (
    AccountInfo, AccountPosition, MarginInfo,
    LeverageInfo
)

logger = logging.getLogger(__name__)

class HyperliquidService:
    """Service for interacting with Hyperliquid API."""
    
    def __init__(self, config: Optional[HyperliquidConfig] = None, testnet: bool = True):
        """Initialize the service.
        
        Args:
            config: Optional configuration
            testnet: Whether to use testnet
        """
        self.config = config or HyperliquidConfig()
        self.testnet = testnet
        base_domain = "api.hyperliquid-testnet.xyz" if testnet else "api.hyperliquid.xyz"
        self.base_url = f"https://{base_domain}/info"  # For market data
        self.trade_url = f"https://{base_domain}/trade"  # For trading operations
        
        # Setup SSL context
        if self.config.use_ssl:
            self.ssl_context = ssl.create_default_context()
            if not self.config.ssl_verify:
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = False
        
        # Setup session
        self.session = None
        self.ws = None
        self._setup_session()
        
        # Rate limiting setup
        self._market_data_semaphore = asyncio.Semaphore(self.config.market_data_rate_limit)
        self._orders_semaphore = asyncio.Semaphore(self.config.orders_rate_limit)
        self._account_semaphore = asyncio.Semaphore(self.config.account_rate_limit)
        
        # WebSocket subscriptions
        self._ws_task = None
        self._orderbook_callbacks = {}
        self._trade_callbacks = {}
        
    def _setup_session(self) -> None:
        """Setup HTTP session with retry logic."""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(
                total=self.config.request_timeout,
                connect=self.config.connect_timeout,
                sock_connect=self.config.sock_connect_timeout,
                sock_read=self.config.sock_read_timeout
            )
            connector = TCPConnector(
                ssl=self.ssl_context,
                limit=self.config.max_connections,
                ttl_dns_cache=300,
                force_close=False,
                enable_cleanup_closed=True
            )
            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'GOAT-SDK/1.0',
                    'Accept': 'application/json'
                }
            )
            
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        is_trade: bool = False,
        **kwargs
    ) -> Any:
        """Make HTTP request with retries.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            is_trade: Whether this is a trading operation
            **kwargs: Additional arguments for request
            
        Returns:
            Parsed response data
            
        Raises:
            aiohttp.ClientError: If request fails after retries
        """
        if self.session is None or self.session.closed:
            self._setup_session()
            
        url = self.trade_url if is_trade else self.base_url
        if endpoint:
            url = f"{url}{endpoint}"
            
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
            
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError),
        max_tries=3,
        max_time=30
    )
    async def _read_response(self, response: aiohttp.ClientResponse) -> Any:
        """Read and parse response with retries.
        
        Args:
            response: API response
            
        Returns:
            Parsed response data
            
        Raises:
            aiohttp.ClientError: If reading response fails
        """
        try:
            data = await response.json()
            return data
        except Exception as e:
            logger.error(f"Error reading response: {str(e)}")
            raise
        
    def _generate_signature(
        self,
        endpoint: str,
        timestamp: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate signature for authenticated requests."""
        message = f"{endpoint}{timestamp}"
        if data:
            message += json.dumps(data, sort_keys=True)
        return hmac.new(
            self.config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
    async def close(self) -> None:
        """Close all connections."""
        if self.session:
            await self.session.close()
            self.session = None
            
        await self._cleanup_websocket()
            
    async def _cleanup_websocket(self) -> None:
        """Clean up WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.ws = None
            
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None
            
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    # Market Data Methods
    async def get_markets(self, testnet: bool = False) -> List[Market]:
        """Get all markets."""
        try:
            data = await self._request(
                method="POST",
                endpoint="",  # Base URL already includes /info
                json={"type": "metaAndAssetCtxs"}
            )
            
            markets = []
            if isinstance(data, list) and len(data) >= 2:
                # First element contains universe (metadata), second contains market data
                universe = data[0].get("universe", [])
                market_data = data[1]
                
                # Create a map of coin to metadata for easier lookup
                metadata_map = {
                    asset["name"]: asset
                    for asset in universe
                }
                
                # Process each market
                for i, market_info in enumerate(market_data):
                    try:
                        # Get metadata for this market
                        coin = list(metadata_map.keys())[i]
                        metadata = metadata_map[coin]
                        
                        market = Market(
                            name=coin,
                            base_currency=coin,
                            quote_currency="USD",
                            price_decimals=metadata.get("szDecimals", 8),
                            size_decimals=metadata.get("szDecimals", 8),
                            min_order_size=Decimal("0.0001"),  # Default value
                            max_leverage=Decimal(str(metadata.get("maxLeverage", "1"))),
                            price=Decimal(str(market_info.get("markPx", "0"))),
                            index_price=Decimal(str(market_info.get("oraclePx", "0"))),
                            open_interest=Decimal(str(market_info.get("openInterest", "0"))),
                            funding_rate=Decimal(str(market_info.get("funding", "0"))),
                            volume_24h=Decimal(str(market_info.get("dayNtlVlm", "0"))),
                            is_active=True
                        )
                        markets.append(market)
                    except (KeyError, ValueError, IndexError) as e:
                        logger.warning(f"Error processing market {i}: {str(e)}")
                        continue
                        
            return markets
        except Exception as e:
            logger.error(f"Error getting markets: {str(e)}")
            raise
        
    async def get_market_summary(self, coin: str) -> MarketSummary:
        """Get market summary for a coin.
        
        Args:
            coin: Market symbol (e.g. "BTC")
            
        Returns:
            Market summary information
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        try:
            # Get market metadata for funding rate and other info
            meta_data = await self._request(
                method="POST",
                endpoint="",  # Base URL already includes /info
                json={"type": "metaAndAssetCtxs"}
            )

            if not isinstance(meta_data, list) or len(meta_data) < 2:
                raise ValueError("Invalid response format from API")

            # Find market data for the requested coin
            market_data = None
            for i, market in enumerate(meta_data[1]):
                if meta_data[0]["universe"][i]["name"] == coin:
                    market_data = market
                    break

            if not market_data:
                raise ValueError(f"Market {coin} not found")

            return MarketSummary(
                coin=coin,
                price=float(market_data.get("markPx", 0)),
                index_price=float(market_data.get("oraclePx", 0)),
                open_interest=float(market_data.get("openInterest", 0)),
                volume_24h=float(market_data.get("dayNtlVlm", 0)),
                funding_rate=float(market_data.get("funding", 0))
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching market summary: {str(e)}")
            raise
        
    async def get_orderbook(
        self,
        coin: str,
        depth: int = 10
    ) -> OrderbookResponse:
        """Get orderbook for a market.
        
        Args:
            coin: Market symbol (e.g. "BTC")
            depth: Number of levels to return
            
        Returns:
            Orderbook data
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        try:
            data = await self._request(
                method="POST",
                endpoint="",  # Base URL already includes /info
                json={"type": "l2Book", "coin": coin}
            )
            
            bids = []
            asks = []
            
            if "levels" in data and len(data["levels"]) >= 2:
                # First array is bids
                for bid in data["levels"][0][:depth]:
                    bids.append(OrderbookLevel(
                        price=Decimal(str(bid["px"])),
                        size=Decimal(str(bid["sz"])),
                        num_orders=bid["n"]
                    ))
                    
                # Second array is asks
                for ask in data["levels"][1][:depth]:
                    asks.append(OrderbookLevel(
                        price=Decimal(str(ask["px"])),
                        size=Decimal(str(ask["sz"])),
                        num_orders=ask["n"]
                    ))
                    
            return OrderbookResponse(
                coin=coin,
                bids=bids,
                asks=asks,
                timestamp=data.get("time", int(time.time() * 1000))
            )
            
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching orderbook: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching orderbook: {str(e)}")
            raise
            
    async def get_recent_trades(
        self,
        coin: str,
        limit: int = 100
    ) -> List[TradeInfo]:
        """Get recent trades for a market.
        
        Args:
            coin: Market symbol (e.g. "BTC")
            limit: Number of trades to return
            
        Returns:
            List of recent trades
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        try:
            data = await self._request(
                method="POST",
                endpoint="",  # Base URL already includes /info
                json={"type": "recentTrades", "coin": coin}
            )
            
            trades = []
            for trade in data[:limit]:
                trades.append(TradeInfo(
                    coin=coin,
                    id=str(trade.get("tid", "")),
                    price=Decimal(str(trade["px"])),
                    size=Decimal(str(trade["sz"])),
                    side=OrderSide.BUY if trade.get("side") == "B" else OrderSide.SELL,
                    timestamp=trade.get("time", int(time.time() * 1000)),
                    liquidation=trade.get("liquidation", False)
                ))
                
            return trades
            
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching recent trades: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching recent trades: {str(e)}")
            raise
        
    # WebSocket Methods for Market Data
    async def _connect_websocket(self) -> None:
        """Connect to WebSocket if not already connected."""
        if self.ws is None:
            self.ws = await websockets.connect(
                self.config.testnet_ws_url if self.testnet else self.config.ws_url,
                ssl=self.ssl_context
            )
            self._ws_task = asyncio.create_task(self._handle_ws_messages())

    async def _handle_ws_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            while True:
                message = await self.ws.recv()
                if message == "Websocket connection established.":
                    continue
                    
                data = json.loads(message)
                channel = data.get("channel")
                
                if channel == "l2Book":
                    coin = data["data"]["coin"]
                    if coin in self._orderbook_callbacks:
                        await self._orderbook_callbacks[coin](data["data"])
                elif channel == "trades":
                    trades = data["data"]
                    if trades and trades[0]["coin"] in self._trade_callbacks:
                        await self._trade_callbacks[trades[0]["coin"]](trades)
                elif channel == "pong":
                    continue
                    
        except WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
            await self._cleanup_websocket()
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._cleanup_websocket()

    async def subscribe_orderbook(
        self,
        coin: str,
        callback: callable
    ) -> None:
        """Subscribe to orderbook updates for a specific coin."""
        await self._connect_websocket()
        self._orderbook_callbacks[coin] = callback
        await self.ws.send(json.dumps({
            "method": "subscribe",
            "subscription": {
                "type": "l2Book",
                "coin": coin
            }
        }))
        
    async def subscribe_trades(
        self,
        coin: str,
        callback: callable
    ) -> None:
        """Subscribe to trade updates for a specific coin."""
        await self._connect_websocket()
        self._trade_callbacks[coin] = callback
        await self.ws.send(json.dumps({
            "method": "subscribe",
            "subscription": {
                "type": "trades",
                "coin": coin
            }
        }))
        
    async def unsubscribe(
        self,
        coin: str,
        channel: str
    ) -> None:
        """Unsubscribe from a specific channel for a coin."""
        if self.ws:
            await self.ws.send(json.dumps({
                "method": "unsubscribe",
                "subscription": {
                    "type": channel,
                    "coin": coin
                }
            }))
            if channel == "l2Book":
                self._orderbook_callbacks.pop(coin, None)
            elif channel == "trades":
                self._trade_callbacks.pop(coin, None)
        
    # Order Management Methods
    async def create_order(
        self,
        request: OrderRequest
    ) -> OrderResult:
        """Create a new order.
        
        Args:
            request: Order request parameters
            
        Returns:
            Order result
        """
        data = {
            "type": "placeOrder",
            "coin": request.coin,
            "side": "B" if request.side == OrderSide.BUY else "S",
            "sz": str(request.size),
            "px": str(request.price),
            "orderType": request.type.value.lower()
        }
        
        try:
            response = await self._request(
                method="POST",
                endpoint="",
                json=data,
                is_trade=True,
                auth_required=True,
                rate_limit_type="order"
            )
            
            return OrderResult(
                success=True,
                order=OrderResponse(**response["order"])
            )
            
        except Exception as e:
            return OrderResult(
                success=False,
                error=str(e),
                error_code=getattr(e, "status", None)
            )
            
    async def cancel_order(
        self,
        coin: str,
        order_id: str
    ) -> OrderResult:
        """Cancel an existing order.
        
        Args:
            coin: The coin symbol
            order_id: The order ID to cancel
            
        Returns:
            Order result
        """
        try:
            response = await self._request(
                method="POST",
                endpoint="",
                json={
                    "type": "cancelOrder",
                    "coin": coin,
                    "oid": order_id
                },
                is_trade=True,
                auth_required=True,
                rate_limit_type="order"
            )
            
            return OrderResult(
                success=True,
                order=OrderResponse(**response["order"])
            )
            
        except Exception as e:
            return OrderResult(
                success=False,
                error=str(e),
                error_code=getattr(e, "status", None)
            )
            
    async def cancel_all_orders(
        self,
        coin: Optional[str] = None
    ) -> List[OrderResult]:
        """Cancel all open orders.
        
        Args:
            coin: Optional coin symbol to cancel orders for
            
        Returns:
            List of order results
        """
        try:
            data = {"type": "cancelAllOrders"}
            if coin:
                data["coin"] = coin
                
            response = await self._request(
                method="POST",
                endpoint="",
                json=data,
                is_trade=True,
                auth_required=True,
                rate_limit_type="order"
            )
            
            return [
                OrderResult(
                    success=True,
                    order=OrderResponse(**order)
                )
                for order in response["orders"]
            ]
            
        except Exception as e:
            return [OrderResult(
                success=False,
                error=str(e),
                error_code=getattr(e, "status", None)
            )]
            
    async def get_open_orders(
        self,
        coin: Optional[str] = None
    ) -> List[OrderResponse]:
        """Get all open orders.
        
        Args:
            coin: Optional coin symbol to filter orders
            
        Returns:
            List of open orders
        """
        data = {"type": "openOrders"}
        if coin:
            data["coin"] = coin
            
        response = await self._request(
            method="POST",
            endpoint="",
            json=data,
            is_trade=True,
            auth_required=True,
            rate_limit_type="order"
        )
        
        return [OrderResponse(**order) for order in response["orders"]]
        
    async def get_order_history(
        self,
        coin: Optional[str] = None,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[OrderResponse]:
        """Get order history.
        
        Args:
            coin: Optional coin symbol to filter orders
            limit: Number of orders to return
            start_time: Optional start time in milliseconds
            end_time: Optional end time in milliseconds
            
        Returns:
            List of historical orders
        """
        data = {
            "type": "orderHistory",
            "limit": limit
        }
        if coin:
            data["coin"] = coin
        if start_time:
            data["startTime"] = start_time
        if end_time:
            data["endTime"] = end_time
            
        response = await self._request(
            method="POST",
            endpoint="",
            json=data,
            is_trade=True,
            auth_required=True,
            rate_limit_type="order"
        )
        
        return [OrderResponse(**order) for order in response["orders"]]
        
    async def get_order_status(
        self,
        coin: str,
        order_id: str
    ) -> OrderResponse:
        """Get status of a specific order.
        
        Args:
            coin: The coin symbol
            order_id: The order ID
            
        Returns:
            Order response
        """
        response = await self._request(
            method="POST",
            endpoint="",
            json={
                "type": "orderStatus",
                "coin": coin,
                "oid": order_id
            },
            is_trade=True,
            auth_required=True,
            rate_limit_type="order"
        )
        
        return OrderResponse(**response["order"])
        
    # Account Management Methods
    async def get_account_info(self) -> AccountInfo:
        """Get account information.
        
        Returns:
            Account information
        """
        response = await self._request(
            method="GET",
            endpoint="/account/info",
            auth_required=True,
            rate_limit_type="account"
        )
        return AccountInfo(**response)
        
    async def get_positions(
        self,
        coin: Optional[str] = None
    ) -> List[AccountPosition]:
        """Get account positions.
        
        Args:
            coin: Optional coin symbol to filter positions
            
        Returns:
            List of positions
        """
        endpoint = "/account/positions"
        if coin:
            endpoint += f"/{coin}"
            
        response = await self._request(
            method="GET",
            endpoint=endpoint,
            auth_required=True,
            rate_limit_type="account"
        )
        return [AccountPosition(**position) for position in response["positions"]]
        
    async def get_margin_info(
        self,
        coin: Optional[str] = None
    ) -> MarginInfo:
        """Get margin information.
        
        Args:
            coin: Optional coin symbol for specific market margin info
            
        Returns:
            Margin information
        """
        endpoint = "/account/margin"
        if coin:
            endpoint += f"/{coin}"
            
        response = await self._request(
            method="GET",
            endpoint=endpoint,
            auth_required=True,
            rate_limit_type="account"
        )
        return MarginInfo(**response)
        
    async def get_leverage_info(
        self,
        coin: str
    ) -> LeverageInfo:
        """Get leverage information for a specific market.
        
        Args:
            coin: The coin symbol
            
        Returns:
            Leverage information
        """
        response = await self._request(
            method="GET",
            endpoint=f"/account/leverage/{coin}",
            auth_required=True,
            rate_limit_type="account"
        )
        return LeverageInfo(**response)
        
    async def set_leverage(
        self,
        coin: str,
        leverage: float
    ) -> bool:
        """Set leverage for a specific market.
        
        Args:
            coin: The coin symbol
            leverage: The desired leverage value
            
        Returns:
            True if successful
        """
        try:
            await self._request(
                method="POST",
                endpoint=f"/account/leverage/{coin}",
                data={"leverage": leverage},
                auth_required=True,
                rate_limit_type="account"
            )
            return True
            
        except Exception:
            return False
            
    async def get_funding_payments(
        self,
        coin: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get funding payment history.
        
        Args:
            coin: Optional coin symbol to filter payments
            start_time: Optional start time in milliseconds
            end_time: Optional end time in milliseconds
            limit: Number of payments to return
            
        Returns:
            List of funding payments
        """
        endpoint = "/account/funding"
        if coin:
            endpoint += f"/{coin}"
            
        params = {"limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
            
        response = await self._request(
            method="GET",
            endpoint=endpoint,
            params=params,
            auth_required=True,
            rate_limit_type="account"
        )
        return response["payments"]
        
    async def get_transaction_history(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get transaction history.
        
        Args:
            start_time: Optional start time in milliseconds
            end_time: Optional end time in milliseconds
            limit: Number of transactions to return
            
        Returns:
            List of transactions
        """
        params = {"limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
            
        response = await self._request(
            method="GET",
            endpoint="/account/transactions",
            params=params,
            auth_required=True,
            rate_limit_type="account"
        )
        return response["transactions"]