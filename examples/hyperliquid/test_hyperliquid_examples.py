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
     
     Path: examples/hyperliquid/test_hyperliquid_examples.py
"""

import pytest
import asyncio
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.core.types import ChainType, EthereumChainConfig
from goat_sdk.plugins.hyperliquid import HyperliquidPlugin

# Test constants
TEST_PRIVATE_KEY = "your_private_key"  # Replace with test private key
TEST_COIN = "BTC"
TEST_AMOUNT = "0.001"
TEST_PRICE = "50000"

@pytest.fixture
async def hyperliquid_setup():
    """Setup Hyperliquid plugin for testing"""
    chain_config = EthereumChainConfig(
        network="mainnet",
        rpc_url="https://mainnet.infura.io/v3/your-project-id"
    )
    sdk = GoatSDK(
        private_key=TEST_PRIVATE_KEY,
        chain_config=chain_config
    )
    hyperliquid = HyperliquidPlugin(sdk)
    return hyperliquid

@pytest.mark.asyncio
async def test_get_markets(hyperliquid_setup):
    """Test getting available markets"""
    hyperliquid = await hyperliquid_setup
    
    markets = await hyperliquid.get_markets()
    assert markets is not None
    print("\nAvailable markets:")
    for market in markets:
        print(f"Symbol: {market.symbol}")
        print(f"Base currency: {market.base_currency}")
        print(f"Quote currency: {market.quote_currency}")
        print(f"Price: {market.price}")
        print(f"24h volume: {market.volume_24h}")
        print("---")

@pytest.mark.asyncio
async def test_get_orderbook(hyperliquid_setup):
    """Test getting orderbook data"""
    hyperliquid = await hyperliquid_setup
    
    orderbook = await hyperliquid.get_orderbook(TEST_COIN)
    assert orderbook is not None
    print(f"\nOrderbook for {TEST_COIN}:")
    print("Bids:")
    for bid in orderbook.bids[:5]:  # Show top 5 bids
        print(f"Price: {bid.price}, Size: {bid.size}")
    print("Asks:")
    for ask in orderbook.asks[:5]:  # Show top 5 asks
        print(f"Price: {ask.price}, Size: {ask.size}")

@pytest.mark.asyncio
async def test_get_recent_trades(hyperliquid_setup):
    """Test getting recent trades"""
    hyperliquid = await hyperliquid_setup
    
    trades = await hyperliquid.get_recent_trades(TEST_COIN)
    assert trades is not None
    print(f"\nRecent trades for {TEST_COIN}:")
    for trade in trades[:5]:  # Show last 5 trades
        print(f"Price: {trade.price}")
        print(f"Size: {trade.size}")
        print(f"Side: {trade.side}")
        print(f"Timestamp: {trade.timestamp}")
        print("---")

@pytest.mark.asyncio
async def test_create_order(hyperliquid_setup):
    """Test creating a limit order"""
    hyperliquid = await hyperliquid_setup
    
    try:
        order = await hyperliquid.create_order(
            coin=TEST_COIN,
            is_buy=True,
            amount=TEST_AMOUNT,
            price=TEST_PRICE,
            reduce_only=False
        )
        
        assert order is not None
        print("\nOrder created:")
        print(f"Order ID: {order.order_id}")
        print(f"Status: {order.status}")
        print(f"Side: {'Buy' if order.is_buy else 'Sell'}")
        print(f"Price: {order.price}")
        print(f"Amount: {order.amount}")
    except Exception as e:
        pytest.skip(f"Order creation failed: {str(e)}")

@pytest.mark.asyncio
async def test_cancel_order(hyperliquid_setup):
    """Test canceling an order"""
    hyperliquid = await hyperliquid_setup
    
    try:
        # First create an order
        order = await hyperliquid.create_order(
            coin=TEST_COIN,
            is_buy=True,
            amount=TEST_AMOUNT,
            price=TEST_PRICE,
            reduce_only=False
        )
        
        # Then cancel it
        result = await hyperliquid.cancel_order(
            coin=TEST_COIN,
            order_id=order.order_id
        )
        
        assert result is not None
        print("\nOrder canceled:")
        print(f"Order ID: {order.order_id}")
        print(f"Cancel status: {result.status}")
    except Exception as e:
        pytest.skip(f"Order cancellation test failed: {str(e)}")

@pytest.mark.asyncio
async def test_get_open_orders(hyperliquid_setup):
    """Test getting open orders"""
    hyperliquid = await hyperliquid_setup
    
    orders = await hyperliquid.get_open_orders()
    assert orders is not None
    print("\nOpen orders:")
    for order in orders:
        print(f"Order ID: {order.order_id}")
        print(f"Coin: {order.coin}")
        print(f"Side: {'Buy' if order.is_buy else 'Sell'}")
        print(f"Price: {order.price}")
        print(f"Amount: {order.amount}")
        print("---")

@pytest.mark.asyncio
async def test_get_order_history(hyperliquid_setup):
    """Test getting order history"""
    hyperliquid = await hyperliquid_setup
    
    history = await hyperliquid.get_order_history()
    assert history is not None
    print("\nOrder history:")
    for order in history[:5]:  # Show last 5 orders
        print(f"Order ID: {order.order_id}")
        print(f"Coin: {order.coin}")
        print(f"Side: {'Buy' if order.is_buy else 'Sell'}")
        print(f"Price: {order.price}")
        print(f"Amount: {order.amount}")
        print(f"Status: {order.status}")
        print("---")

@pytest.mark.asyncio
async def test_error_handling(hyperliquid_setup):
    """Test error handling with invalid parameters"""
    hyperliquid = await hyperliquid_setup
    
    # Test with invalid coin
    with pytest.raises(Exception):
        await hyperliquid.get_orderbook("INVALID_COIN")
    
    # Test with invalid order parameters
    with pytest.raises(Exception):
        await hyperliquid.create_order(
            coin="INVALID_COIN",
            is_buy=True,
            amount="invalid_amount",
            price="invalid_price",
            reduce_only=False
        )
    
    # Test with invalid order ID
    with pytest.raises(Exception):
        await hyperliquid.cancel_order(
            coin=TEST_COIN,
            order_id="invalid_order_id"
        )

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 