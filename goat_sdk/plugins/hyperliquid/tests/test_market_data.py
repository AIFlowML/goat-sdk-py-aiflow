"""Tests for market data methods."""

import pytest
from decimal import Decimal
import asyncio

from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.models import (
    Market, MarketSummary
)
from goat_sdk.plugins.hyperliquid.types.market import (
    OrderbookResponse, TradeInfo, OrderbookLevel
)
from goat_sdk.plugins.hyperliquid.types.order import OrderSide

pytestmark = pytest.mark.asyncio

async def test_get_markets(plugin: HyperliquidPlugin):
    """Test getting all markets."""
    markets = await plugin.get_markets(testnet=True)
    assert isinstance(markets, list)
    assert len(markets) > 0
    
    btc_market = next(m for m in markets if m.name == "BTC")
    assert btc_market.base_currency == "BTC"
    assert btc_market.quote_currency == "USD"
    assert btc_market.price > 0
    assert btc_market.index_price > 0
    assert btc_market.open_interest >= 0
    assert btc_market.volume_24h >= 0
    assert btc_market.is_active is True

async def test_get_market_summary(plugin: HyperliquidPlugin):
    """Test getting market summary."""
    summary = await plugin.get_market_summary("BTC", testnet=True)
    assert isinstance(summary, MarketSummary)
    assert summary.coin == "BTC"
    assert summary.price > 0
    assert summary.index_price > 0
    assert summary.open_interest >= 0
    assert summary.volume_24h >= 0
    assert summary.funding_rate is not None

async def test_get_orderbook(plugin: HyperliquidPlugin):
    """Test getting orderbook."""
    orderbook = await plugin.get_orderbook("BTC", testnet=True)
    assert isinstance(orderbook, OrderbookResponse)
    assert orderbook.coin == "BTC"
    assert len(orderbook.bids) > 0
    assert len(orderbook.asks) > 0
    assert isinstance(orderbook.bids[0], OrderbookLevel)
    assert isinstance(orderbook.asks[0], OrderbookLevel)
    assert orderbook.bids[0].price > 0
    assert orderbook.bids[0].size > 0
    assert orderbook.asks[0].price > 0
    assert orderbook.asks[0].size > 0

async def test_get_recent_trades(plugin: HyperliquidPlugin):
    """Test getting recent trades."""
    trades = await plugin.get_recent_trades("BTC", testnet=True)
    assert isinstance(trades, list)
    assert len(trades) > 0
    assert isinstance(trades[0], TradeInfo)
    assert trades[0].coin == "BTC"
    assert trades[0].price > 0
    assert trades[0].size > 0
    assert trades[0].side in [OrderSide.BUY, OrderSide.SELL]
    assert trades[0].timestamp > 0