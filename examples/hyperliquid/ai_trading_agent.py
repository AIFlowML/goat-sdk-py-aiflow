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
     
     Path: examples/hyperliquid/ai_trading_agent.py
"""

"""
Experimental AI Trading Agent for Hyperliquid.

⚠️ WARNING: This is an experimental example for educational purposes only.
DO NOT use with real funds. The AI's trading decisions are not financial advice.

This example demonstrates:
- Integration with LangChain
- Market data analysis with AI
- Basic trading strategy implementation
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.hyperliquid import HyperliquidPlugin
from goat_sdk.plugins.hyperliquid.types import Market, Trade

class AITradingAgent:
    def __init__(self, hyperliquid: HyperliquidPlugin, market_name: str):
        self.hyperliquid = hyperliquid
        self.market_name = market_name
        self.llm = ChatOpenAI(temperature=0)
        
        # Trading parameters
        self.min_confidence = 0.7
        self.position_size = 0.01  # 1% of available capital
        self.stop_loss_pct = 0.02  # 2% stop loss
        
    async def get_market_data(self) -> Dict[str, Any]:
        """Gather relevant market data for analysis."""
        markets = await self.hyperliquid.get_markets()
        market = next(m for m in markets if m.name == self.market_name)
        
        orderbook = await self.hyperliquid.get_orderbook(market.address)
        trades = await self.hyperliquid.get_recent_trades(market.address)
        
        return {
            "market": market.dict(),
            "orderbook": {
                "bids": [b.dict() for b in orderbook.bids[:10]],
                "asks": [a.dict() for a in orderbook.asks[:10]]
            },
            "recent_trades": [t.dict() for t in trades[:50]]
        }

    def analyze_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze market data and make trading decisions."""
        # Prepare market data summary for AI
        market_summary = (
            f"Market: {data['market']['name']}\n"
            f"Current bid: {data['orderbook']['bids'][0]['price']}\n"
            f"Current ask: {data['orderbook']['asks'][0]['price']}\n"
            f"Recent trades: {len(data['recent_trades'])} trades in last period\n"
        )

        # Ask AI to analyze the market
        messages = [
            SystemMessage(content="""
                You are a trading analysis AI. Analyze the market data and provide:
                1. Market trend (bullish/bearish/neutral)
                2. Confidence level (0-1)
                3. Suggested action (buy/sell/hold)
                4. Brief reasoning
                
                Respond in JSON format only.
            """),
            HumanMessage(content=f"Analyze this market data:\n{market_summary}")
        ]
        
        response = self.llm.predict_messages(messages)
        return json.loads(response.content)

    async def execute_trade(self, analysis: Dict[str, Any]) -> None:
        """Execute trade based on AI analysis if confidence is high enough."""
        if analysis["confidence"] < self.min_confidence:
            print(f"Confidence too low ({analysis['confidence']}), not trading")
            return

        markets = await self.hyperliquid.get_markets()
        market = next(m for m in markets if m.name == self.market_name)
        
        if analysis["action"] in ["buy", "sell"]:
            # Calculate position size and price
            orderbook = await self.hyperliquid.get_orderbook(market.address)
            current_price = (
                orderbook.asks[0].price if analysis["action"] == "buy"
                else orderbook.bids[0].price
            )
            
            # Place the order
            try:
                order = await self.hyperliquid.place_order(
                    market=market.address,
                    side=analysis["action"],
                    price=current_price,
                    size=self.position_size,
                    type="limit"
                )
                print(f"Placed {analysis['action']} order: {order.id}")
                
                # Place stop loss
                stop_price = (
                    current_price * (1 - self.stop_loss_pct) if analysis["action"] == "buy"
                    else current_price * (1 + self.stop_loss_pct)
                )
                stop_order = await self.hyperliquid.place_order(
                    market=market.address,
                    side="sell" if analysis["action"] == "buy" else "buy",
                    price=stop_price,
                    size=self.position_size,
                    type="stop_limit"
                )
                print(f"Placed stop loss order: {stop_order.id}")
                
            except Exception as e:
                print(f"Error placing orders: {str(e)}")

async def main():
    # Initialize SDK and plugin
    sdk = GoatSDK(
        private_key="your_private_key",  # Replace with your private key
        network=Network.MAINNET,
        chain=Chain.SOLANA
    )
    hyperliquid = HyperliquidPlugin(sdk)
    
    # Create AI trading agent for BTC-USDC market
    agent = AITradingAgent(hyperliquid, "BTC-USDC")
    
    try:
        # Main trading loop
        while True:
            # Gather market data
            print("\nGathering market data...")
            market_data = await agent.get_market_data()
            
            # Analyze with AI
            print("Analyzing market data with AI...")
            analysis = agent.analyze_market_data(market_data)
            print(f"\nAI Analysis:")
            print(f"Trend: {analysis['trend']}")
            print(f"Confidence: {analysis['confidence']}")
            print(f"Action: {analysis['action']}")
            print(f"Reasoning: {analysis['reasoning']}")
            
            # Execute trade if appropriate
            await agent.execute_trade(analysis)
            
            # Wait before next iteration
            await asyncio.sleep(60)  # 1 minute delay
            
    except KeyboardInterrupt:
        print("\nStopping trading bot...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 