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

"""Tests for market data methods."""
import pytest
from decimal import Decimal
import asyncio

from goat_sdk.plugins.hyperliquid.plugin import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.types.market import (
    MarketInfo, MarketSummary, OrderbookResponse, OrderbookLevel, TradeInfo
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

async def test_get_market_summary(plugin: HyperliquidPlugin):
    """Test getting market summary."""
    summary = await plugin.get_market_summary("BTC", testnet=True)
    assert isinstance(summary, MarketSummary)
    assert summary.coin == "BTC"
    assert isinstance(summary.price, Decimal)
    assert isinstance(summary.volume_24h, Decimal)
    assert isinstance(summary.open_interest, Decimal)
    assert isinstance(summary.funding_rate, Decimal)
    assert summary.price > 0
    assert summary.volume_24h >= 0
    assert summary.open_interest >= 0

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