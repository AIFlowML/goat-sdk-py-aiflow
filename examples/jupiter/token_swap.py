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
     
     Path: examples/jupiter/token_swap.py
"""

"""
Jupiter Token Swap example.

This example demonstrates how to:
- Get a quote for a token swap
- Execute a token swap
- Handle slippage and price impact
"""

import asyncio
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.jupiter import JupiterPlugin

async def main():
    # Initialize SDK
    sdk = GoatSDK(
        private_key="your_private_key",  # Replace with your private key
        network=Network.MAINNET,
        chain=Chain.SOLANA
    )

    # Initialize Jupiter plugin
    jupiter = JupiterPlugin(sdk)

    # Token addresses (USDC -> SOL example)
    input_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    output_token = "So11111111111111111111111111111111111111112"   # SOL

    try:
        # Get quote for swapping 1 USDC to SOL
        quote = await jupiter.get_quote(
            input_mint=input_token,
            output_mint=output_token,
            amount="1000000",  # 1 USDC (6 decimals)
            slippage_bps=50    # 0.5% slippage
        )
        
        print(f"Quote received:")
        print(f"Input amount: {quote.in_amount}")
        print(f"Output amount: {quote.out_amount}")
        print(f"Price impact: {quote.price_impact_pct}%")

        # Execute the swap if price impact is acceptable
        if Decimal(quote.price_impact_pct) < 1.0:  # Less than 1% impact
            result = await jupiter.execute_swap(
                wallet_client=sdk.wallet_client,
                quote=quote
            )
            
            print(f"\nSwap executed:")
            print(f"Transaction hash: {result.transaction_hash}")
            print(f"Input amount: {result.input_amount}")
            print(f"Output amount: {result.output_amount}")
            print(f"Price impact: {result.price_impact}%")
        else:
            print(f"\nSwap aborted: Price impact too high ({quote.price_impact_pct}%)")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 