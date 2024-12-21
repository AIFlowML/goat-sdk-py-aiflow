"""Tests for order management methods."""

import pytest
from decimal import Decimal

from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.types.order import (
    OrderType, OrderSide, OrderStatus,
    OrderRequest, OrderResponse, OrderResult
)

pytestmark = pytest.mark.asyncio

async def test_create_order(plugin: HyperliquidPlugin):
    """Test creating a new order."""
    request = OrderRequest(
        coin="BTC",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        size=Decimal("0.001"),
        price=Decimal("40000")
    )
    result = await plugin.create_order(request, testnet=True)
    assert isinstance(result, OrderResult)
    assert result.success
    assert isinstance(result.order, OrderResponse)
    assert result.order.coin == "BTC"
    assert result.order.side == OrderSide.BUY
    assert result.order.type == OrderType.LIMIT
    assert result.order.size == Decimal("0.001")
    assert result.order.price == Decimal("40000")
    assert result.order.status in [OrderStatus.NEW, OrderStatus.OPEN]

async def test_cancel_order(plugin: HyperliquidPlugin):
    """Test canceling an order."""
    # First create an order
    request = OrderRequest(
        coin="BTC",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        size=Decimal("0.001"),
        price=Decimal("40000")
    )
    create_result = await plugin.create_order(request, testnet=True)
    assert create_result.success
    
    # Then cancel it
    cancel_result = await plugin.cancel_order("BTC", create_result.order.id, testnet=True)
    assert isinstance(cancel_result, OrderResult)
    assert cancel_result.success
    assert isinstance(cancel_result.order, OrderResponse)
    assert cancel_result.order.status == OrderStatus.CANCELED

async def test_cancel_all_orders(plugin: HyperliquidPlugin):
    """Test canceling all orders."""
    # First create a few orders
    for price in [40000, 41000, 42000]:
        request = OrderRequest(
            coin="BTC",
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            size=Decimal("0.001"),
            price=Decimal(str(price))
        )
        result = await plugin.create_order(request, testnet=True)
        assert result.success
    
    # Then cancel all
    results = await plugin.cancel_all_orders(testnet=True)
    assert isinstance(results, list)
    assert len(results) > 0
    for result in results:
        assert isinstance(result, OrderResult)
        assert result.success
        assert result.order.status == OrderStatus.CANCELED

async def test_get_open_orders(plugin: HyperliquidPlugin):
    """Test getting open orders."""
    # First create an order
    request = OrderRequest(
        coin="BTC",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        size=Decimal("0.001"),
        price=Decimal("40000")
    )
    create_result = await plugin.create_order(request, testnet=True)
    assert create_result.success
    
    # Then get open orders
    orders = await plugin.get_open_orders(testnet=True)
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert isinstance(orders[0], OrderResponse)
    assert orders[0].status == OrderStatus.OPEN

async def test_get_order_history(plugin: HyperliquidPlugin):
    """Test getting order history."""
    orders = await plugin.get_order_history(testnet=True)
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert isinstance(orders[0], OrderResponse)

async def test_get_order_status(plugin: HyperliquidPlugin):
    """Test getting order status."""
    # First create an order
    request = OrderRequest(
        coin="BTC",
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        size=Decimal("0.001"),
        price=Decimal("40000")
    )
    create_result = await plugin.create_order(request, testnet=True)
    assert create_result.success
    
    # Then get its status
    order = await plugin.get_order_status("BTC", create_result.order.id, testnet=True)
    assert isinstance(order, OrderResponse)
    assert order.id == create_result.order.id
    assert order.coin == "BTC"
    assert order.status in [OrderStatus.NEW, OrderStatus.OPEN] 