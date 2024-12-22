
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
     
     Path: examples/hyperliquid/basic_operations.py
"""
"""
Basic Hyperliquid operations example.

This example demonstrates how to:
- Get market data
- Read orderbook
- Place and cancel orders
"""

import asyncio
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.hyperliquid import HyperliquidPlugin

async def main():
    # Initialize SDK
    sdk = GoatSDK(
        private_key="your_private_key",  # Replace with your private key
        network=Network.MAINNET,
        chain=Chain.SOLANA
    )

    # Initialize Hyperliquid plugin
    hyperliquid = HyperliquidPlugin(sdk)

    try:
        # Get all markets
        markets = await hyperliquid.get_markets()
        print("\nAvailable markets:")
        for market in markets:
            print(f"- {market.name}: {market.base_token}/{market.quote_token}")

        # Get specific market (e.g., BTC-USDC)
        btc_market = next(m for m in markets if m.name == "BTC-USDC")
        
        # Get orderbook
        orderbook = await hyperliquid.get_orderbook(btc_market.address)
        print(f"\nOrderbook for {btc_market.name}:")
        print("Bids:")
        for bid in orderbook.bids[:5]:  # Show top 5 bids
            print(f"Price: {bid.price}, Size: {bid.size}")
        print("Asks:")
        for ask in orderbook.asks[:5]:  # Show top 5 asks
            print(f"Price: {ask.price}, Size: {ask.size}")

        # Get recent trades
        trades = await hyperliquid.get_recent_trades(btc_market.address)
        print(f"\nRecent trades for {btc_market.name}:")
        for trade in trades[:5]:  # Show last 5 trades
            print(f"Price: {trade.price}, Size: {trade.size}, Side: {trade.side}")

        # Place a limit order (example)
        """
        order = await hyperliquid.place_order(
            market=btc_market.address,
            side="buy",
            price=30000,  # Example price
            size=0.1,     # Example size
            type="limit"
        )
        print(f"\nPlaced order: {order.id}")

        # Cancel the order
        result = await hyperliquid.cancel_order(
            market=btc_market.address,
            order_id=order.id
        )
        print(f"Order cancelled: {result}")
        """

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 