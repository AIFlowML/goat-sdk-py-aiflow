"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /:::\____\        
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
     
     Path: examples/jupiter/get_usdc.py
"""

"""
Get USDC example using Jupiter.

This example demonstrates how to:
- Get a quote for swapping SOL to USDC
- Execute the swap to get USDC
- Handle slippage and price impact
"""

import asyncio
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.types import Network
from goat_sdk.core.types import ChainType
from goat_sdk.plugins.jupiter import JupiterPlugin

async def main():
    # Initialize SDK
    sdk = GoatSDK(
        private_key="0x" + "11" * 32,  # Replace with your private key (64 hex chars)
        network=Network.MAINNET,
        chain=ChainType.SOLANA
    )

    # Initialize Jupiter plugin
    jupiter = JupiterPlugin()

    # Token addresses (SOL -> USDC example)
    input_token = "So11111111111111111111111111111111111111112"   # SOL
    output_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC

    try:
        # Get quote for swapping 0.1 SOL to USDC
        quote = await jupiter.get_quote(
            input_mint=input_token,
            output_mint=output_token,
            amount="100000000",  # 0.1 SOL (9 decimals)
            slippage_bps=50    # 0.5% slippage
        )
        
        print(f"Quote received:")
        print(f"Input amount: {quote.in_amount} SOL")
        print(f"Output amount: {quote.out_amount} USDC")
        print(f"Price impact: {quote.price_impact_pct}%")

        # Execute the swap if price impact is acceptable
        if Decimal(quote.price_impact_pct) < 1.0:  # Less than 1% impact
            result = await jupiter.execute_swap(
                wallet_client=sdk.wallet_client,
                quote=quote
            )
            
            print(f"\nSwap executed:")
            print(f"Transaction hash: {result.transaction_hash}")
            print(f"Input amount: {result.input_amount} SOL")
            print(f"Output amount: {result.output_amount} USDC")
            print(f"Price impact: {result.price_impact}%")
        else:
            print(f"\nSwap aborted: Price impact too high ({quote.price_impact_pct}%)")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 