"""Tests for market data methods."""
import pytest
from decimal import Decimal
import asyncio

from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.types.market import (
    MarketInfo, MarketSummary, OrderbookResponse, TradeInfo
)
from goat_sdk.plugins.hyperliquid.types.order import OrderSide

pytestmark = pytest.mark.asyncio

async def test_get_markets(plugin: HyperliquidPlugin):
    """Test getting all markets."""
    markets = await plugin.get_markets(testnet=True)
    assert isinstance(markets, list)
    assert len(markets) > 0
    
    btc_market = next(m for m in markets if m.coin == "BTC")
    assert isinstance(btc_market, MarketInfo)
    assert btc_market.coin == "BTC"
    assert isinstance(btc_market.price, Decimal)
    assert isinstance(btc_market.index_price, Decimal)
    assert isinstance(btc_market.mark_price, Decimal)
    assert isinstance(btc_market.open_interest, Decimal)
    assert isinstance(btc_market.funding_rate, Decimal)
    assert isinstance(btc_market.volume_24h, Decimal)
    assert isinstance(btc_market.size_decimals, int)