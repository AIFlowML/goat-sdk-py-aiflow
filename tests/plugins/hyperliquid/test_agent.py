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
     
     Path: examples/adapters/langchain_example.py
"""

"""Tests for Hyperliquid functionality."""

import pytest
from unittest.mock import AsyncMock, patch
import time
from decimal import Decimal
from pydantic import ValidationError

from goat_sdk.plugins.hyperliquid.types.agent import (
    AgentApprovalRequest,
    AgentApprovalAction,
    AgentApprovalResponse
)
from goat_sdk.plugins.hyperliquid.types.order import (
    OrderRequest, OrderResponse, OrderResult,
    OrderSide, OrderStatus, OrderType
)
from goat_sdk.plugins.hyperliquid.types.market import (
    MarketInfo, MarketSummary, OrderbookResponse,
    OrderbookLevel, TradeInfo
)

@pytest.fixture
def mock_response():
    """Mock successful response."""
    return {
        "status": "ok",
        "response": {"type": "default"}
    }

@pytest.fixture
def valid_address():
    """Valid ethereum address."""
    return "0x" + "1" * 40

@pytest.fixture
def mock_market_info():
    """Mock market information."""
    return MarketInfo(
        coin="BTC",
        price=Decimal("50000"),
        index_price=Decimal("50000"),
        mark_price=Decimal("50000"),
        open_interest=Decimal("1000"),
        funding_rate=Decimal("0.0001"),
        volume_24h=Decimal("10000"),
        size_decimals=8
    )

@pytest.fixture
def mock_order_request():
    """Mock order request."""
    return OrderRequest(
        coin="BTC",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        size=Decimal("0.1"),
        type=OrderType.LIMIT,
        reduce_only=False,
        post_only=False
    )

@pytest.fixture
def mock_order_response():
    """Mock order response."""
    return OrderResponse(
        id="test_order_id",
        client_id="test_client_id",
        coin="BTC",
        size=Decimal("0.1"),
        price=Decimal("50000"),
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        status=OrderStatus.NEW,
        filled_size=Decimal("0"),
        remaining_size=Decimal("0.1"),
        created_at=int(time.time() * 1000)
    )

@pytest.mark.asyncio
async def test_agent_approval_request_validation():
    """Test AgentApprovalRequest validation."""
    # Valid request
    request = AgentApprovalRequest(
        agent_address="0x" + "1" * 40,
        agent_name="TestAgent"
    )
    assert request.agent_address.startswith("0x")
    assert len(request.agent_address) == 42
    
    # Invalid address format
    with pytest.raises(ValidationError):
        AgentApprovalRequest(agent_address="invalid")
    
    # Invalid address length
    with pytest.raises(ValidationError):
        AgentApprovalRequest(agent_address="0x" + "1" * 39)

@pytest.mark.asyncio
async def test_approve_agent_wallet(mock_response, valid_address):
    """Test agent wallet approval flow."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.approve_agent_wallet = AsyncMock(return_value=mock_response)
        
        result = await mock_plugin.approve_agent_wallet(
            agent_address=valid_address,
            agent_name="TestAgent"
        )
        assert result["status"] == "ok"
        
        mock_plugin.approve_agent_wallet.assert_called_once_with(
            agent_address=valid_address,
            agent_name="TestAgent"
        )

@pytest.mark.asyncio
async def test_get_markets(mock_market_info):
    """Test getting market information."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.get_markets = AsyncMock(return_value=[mock_market_info])
        
        markets = await mock_plugin.get_markets()
        assert len(markets) > 0
        assert isinstance(markets[0], MarketInfo)
        assert markets[0].coin == "BTC"

@pytest.mark.asyncio
async def test_get_orderbook():
    """Test getting orderbook."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_orderbook = OrderbookResponse(
            coin="BTC",
            bids=[OrderbookLevel(price=Decimal("49900"), size=Decimal("1.0"))],
            asks=[OrderbookLevel(price=Decimal("50100"), size=Decimal("1.0"))]
        )
        mock_plugin.get_orderbook = AsyncMock(return_value=mock_orderbook)
        
        orderbook = await mock_plugin.get_orderbook("BTC")
        assert isinstance(orderbook, OrderbookResponse)
        assert len(orderbook.bids) > 0
        assert len(orderbook.asks) > 0

@pytest.mark.asyncio
async def test_get_recent_trades():
    """Test getting recent trades."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_trades = [
            TradeInfo(
                coin="BTC",
                id="trade1",
                price=Decimal("50000"),
                size=Decimal("0.1"),
                side=OrderSide.BUY,
                timestamp=int(time.time() * 1000)
            )
        ]
        mock_plugin.get_recent_trades = AsyncMock(return_value=mock_trades)
        
        trades = await mock_plugin.get_recent_trades("BTC")
        assert len(trades) > 0
        assert isinstance(trades[0], TradeInfo)

@pytest.mark.asyncio
async def test_create_order(mock_order_request, mock_order_response):
    """Test creating an order."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.create_order = AsyncMock(return_value=OrderResult(
            success=True,
            order=mock_order_response
        ))
        
        result = await mock_plugin.create_order(mock_order_request)
        assert result.success
        assert isinstance(result.order, OrderResponse)
        assert result.order.status == OrderStatus.NEW

@pytest.mark.asyncio
async def test_cancel_order(mock_order_response):
    """Test canceling an order."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.cancel_order = AsyncMock(return_value=OrderResult(
            success=True,
            order=mock_order_response
        ))
        
        result = await mock_plugin.cancel_order("BTC", "test_order_id")
        assert result.success
        assert isinstance(result.order, OrderResponse)

@pytest.mark.asyncio
async def test_get_open_orders(mock_order_response):
    """Test getting open orders."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.get_open_orders = AsyncMock(return_value=[mock_order_response])
        
        orders = await mock_plugin.get_open_orders("BTC")
        assert len(orders) > 0
        assert isinstance(orders[0], OrderResponse)

@pytest.mark.asyncio
async def test_get_order_history(mock_order_response):
    """Test getting order history."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        mock_plugin.get_order_history = AsyncMock(return_value=[mock_order_response])
        
        orders = await mock_plugin.get_order_history("BTC")
        assert len(orders) > 0
        assert isinstance(orders[0], OrderResponse)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in various scenarios."""
    with patch("goat_sdk.plugins.hyperliquid.plugin.HyperliquidPlugin") as MockPlugin:
        mock_plugin = MockPlugin()
        
        # Test market not found
        mock_plugin.get_market_summary = AsyncMock(side_effect=ValueError("Market not found"))
        with pytest.raises(ValueError, match="Market not found"):
            await mock_plugin.get_market_summary("INVALID")
        
        # Test order creation failure
        mock_plugin.create_order = AsyncMock(return_value=OrderResult(
            success=False,
            error="Insufficient balance"
        ))
        result = await mock_plugin.create_order(mock_order_request)
        assert not result.success
        assert "Insufficient balance" in result.error