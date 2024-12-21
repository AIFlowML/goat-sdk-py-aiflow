"""Tests for market data methods individually."""

import pytest
import aiohttp
import ssl
import json
from decimal import Decimal

pytestmark = pytest.mark.asyncio

async def test_get_markets():
    """Test getting all markets."""
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test endpoint
    url = "https://api.hyperliquid-testnet.xyz/info"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "goat-sdk/1.0.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("\nTesting get_markets...")
        try:
            # Get full market data
            async with session.post(url, json={"type": "metaAndAssetCtxs"}, ssl=ssl_context) as response:
                print(f"Markets Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Markets Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
                
                # Validate response structure
                assert isinstance(data, list)
                assert len(data) == 2  # [meta, assetCtxs]
                
                meta_data = data[0]
                asset_data = data[1]
                
                # Find BTC market in asset data
                btc_asset = next((a for a in asset_data if isinstance(a, dict) and all(k in a for k in ["funding", "openInterest", "markPx"])), None)
                assert btc_asset is not None
                
                # Validate required fields
                required_fields = [
                    "funding", "openInterest", "prevDayPx", "dayNtlVlm",
                    "premium", "oraclePx", "markPx", "midPx"
                ]
                for field in required_fields:
                    assert field in btc_asset, f"Missing field: {field}"
                
                # Validate data types
                assert isinstance(Decimal(str(btc_asset["markPx"])), Decimal)
                assert isinstance(Decimal(str(btc_asset["oraclePx"])), Decimal)
                assert isinstance(Decimal(str(btc_asset["midPx"])), Decimal)
                assert isinstance(Decimal(str(btc_asset["openInterest"])), Decimal)
                assert isinstance(Decimal(str(btc_asset["funding"])), Decimal)
                assert isinstance(Decimal(str(btc_asset["dayNtlVlm"])), Decimal)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            raise

async def test_get_market_summary():
    """Test getting market summary."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    url = "https://api.hyperliquid-testnet.xyz/info"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "goat-sdk/1.0.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("\nTesting get_market_summary for BTC...")
        try:
            async with session.post(url, json={"type": "metaAndAssetCtxs"}, ssl=ssl_context) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
                
                # Extract BTC summary
                meta_data = data[0]
                asset_data = data[1]
                
                # Find first market with required fields
                market = next((a for a in asset_data if isinstance(a, dict) and all(k in a for k in ["funding", "openInterest", "markPx"])), None)
                assert market is not None
                
                # Validate fields
                summary = {
                    "price": Decimal(str(market["midPx"])),
                    "index_price": Decimal(str(market["oraclePx"])),
                    "mark_price": Decimal(str(market["markPx"])),
                    "open_interest": Decimal(str(market["openInterest"])),
                    "funding_rate": Decimal(str(market["funding"])),
                    "volume_24h": Decimal(str(market["dayNtlVlm"]))
                }
                
                print(f"\nMarket Summary: {json.dumps(summary, default=str, indent=2)}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            raise

async def test_get_orderbook():
    """Test getting orderbook."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    url = "https://api.hyperliquid-testnet.xyz/info"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "goat-sdk/1.0.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("\nTesting get_orderbook for BTC...")
        try:
            async with session.post(url, json={"type": "l2Book", "coin": "BTC"}, ssl=ssl_context) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
                
                # Validate orderbook structure
                assert "levels" in data
                assert len(data["levels"]) == 2
                bids = data["levels"][0]
                asks = data["levels"][1]
                
                assert isinstance(bids, list)
                assert isinstance(asks, list)
                
                # Check first bid and ask if available
                if bids:
                    bid = bids[0]
                    required_fields = ["px", "sz", "n"]
                    assert all(field in bid for field in required_fields)
                    
                    # Validate types
                    assert isinstance(Decimal(str(bid["px"])), Decimal)  # price
                    assert isinstance(Decimal(str(bid["sz"])), Decimal)  # size
                    assert isinstance(bid["n"], int)  # number of orders
                    
                if asks:
                    ask = asks[0]
                    required_fields = ["px", "sz", "n"]
                    assert all(field in ask for field in required_fields)
                    
                    # Validate types
                    assert isinstance(Decimal(str(ask["px"])), Decimal)  # price
                    assert isinstance(Decimal(str(ask["sz"])), Decimal)  # size
                    assert isinstance(ask["n"], int)  # number of orders
                
        except Exception as e:
            print(f"Error: {str(e)}")
            raise

async def test_get_recent_trades():
    """Test getting recent trades."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    url = "https://api.hyperliquid-testnet.xyz/info"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "goat-sdk/1.0.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        print("\nTesting get_recent_trades for BTC...")
        try:
            async with session.post(url, json={"type": "recentTrades", "coin": "BTC"}, ssl=ssl_context) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
                
                # Validate trades structure
                assert isinstance(data, list)
                
                # Check first trade if available
                if data:
                    trade = data[0]
                    required_fields = ["px", "sz", "side", "time", "hash"]
                    assert all(field in trade for field in required_fields)
                    
                    # Validate types
                    assert isinstance(Decimal(str(trade["px"])), Decimal)  # price
                    assert isinstance(Decimal(str(trade["sz"])), Decimal)  # size
                    assert isinstance(trade["side"], str)  # side
                    assert isinstance(trade["time"], int)  # timestamp
                    assert isinstance(trade["hash"], str)  # transaction hash
                
        except Exception as e:
            print(f"Error: {str(e)}")
            raise 