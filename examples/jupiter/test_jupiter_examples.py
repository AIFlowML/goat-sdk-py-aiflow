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
     
     Path: examples/jupiter/test_jupiter_examples.py
"""

import pytest
import asyncio
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.core.types import ChainType, SolanaChainConfig
from goat_sdk.plugins.jupiter import JupiterPlugin

# Test constants
TEST_PRIVATE_KEY = "your_private_key"  # Replace with test private key
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_ADDRESS = "So11111111111111111111111111111111111111112"
AMOUNT_USDC = "1000000"  # 1 USDC (6 decimals)
SLIPPAGE = 50  # 0.5% slippage

@pytest.fixture
async def jupiter_setup():
    """Setup Jupiter plugin for testing"""
    chain_config = SolanaChainConfig(
        network="mainnet",
        rpc_url="https://api.mainnet-beta.solana.com"
    )
    sdk = GoatSDK(
        private_key=TEST_PRIVATE_KEY,
        chain_config=chain_config
    )
    jupiter = JupiterPlugin(sdk)
    return jupiter

@pytest.mark.asyncio
async def test_get_quote(jupiter_setup):
    """Test getting a quote for token swap"""
    jupiter = await jupiter_setup
    
    quote = await jupiter.get_quote(
        input_mint=USDC_ADDRESS,
        output_mint=SOL_ADDRESS,
        amount=AMOUNT_USDC,
        slippage_bps=SLIPPAGE
    )
    
    assert quote is not None
    assert float(quote.price_impact_pct) >= 0
    print(f"\nQuote received:")
    print(f"Input amount: {quote.in_amount}")
    print(f"Output amount: {quote.out_amount}")
    print(f"Price impact: {quote.price_impact_pct}%")

@pytest.mark.asyncio
async def test_execute_swap(jupiter_setup):
    """Test executing a token swap"""
    jupiter = await jupiter_setup
    
    # First get a quote
    quote = await jupiter.get_quote(
        input_mint=USDC_ADDRESS,
        output_mint=SOL_ADDRESS,
        amount=AMOUNT_USDC,
        slippage_bps=SLIPPAGE
    )
    
    # Execute swap if price impact is acceptable
    if Decimal(quote.price_impact_pct) < 1.0:
        result = await jupiter.execute_swap(
            wallet_client=jupiter.sdk.wallet_client,
            quote=quote
        )
        
        assert result is not None
        assert result.transaction_hash is not None
        print(f"\nSwap executed:")
        print(f"Transaction hash: {result.transaction_hash}")
        print(f"Input amount: {result.input_amount}")
        print(f"Output amount: {result.output_amount}")
        print(f"Price impact: {result.price_impact}%")
    else:
        pytest.skip("Skipped due to high price impact")

@pytest.mark.asyncio
async def test_get_quote_with_different_slippage(jupiter_setup):
    """Test getting quotes with different slippage values"""
    jupiter = await jupiter_setup
    
    slippage_values = [10, 25, 50, 100]  # 0.1%, 0.25%, 0.5%, 1%
    
    for slippage in slippage_values:
        quote = await jupiter.get_quote(
            input_mint=USDC_ADDRESS,
            output_mint=SOL_ADDRESS,
            amount=AMOUNT_USDC,
            slippage_bps=slippage
        )
        
        assert quote is not None
        print(f"\nQuote with {slippage/100}% slippage:")
        print(f"Input amount: {quote.in_amount}")
        print(f"Output amount: {quote.out_amount}")
        print(f"Price impact: {quote.price_impact_pct}%")

@pytest.mark.asyncio
async def test_get_quote_with_different_amounts(jupiter_setup):
    """Test getting quotes with different amounts"""
    jupiter = await jupiter_setup
    
    amounts = ["500000", "1000000", "2000000"]  # 0.5, 1, 2 USDC
    
    for amount in amounts:
        quote = await jupiter.get_quote(
            input_mint=USDC_ADDRESS,
            output_mint=SOL_ADDRESS,
            amount=amount,
            slippage_bps=SLIPPAGE
        )
        
        assert quote is not None
        print(f"\nQuote for {int(amount)/1000000} USDC:")
        print(f"Input amount: {quote.in_amount}")
        print(f"Output amount: {quote.out_amount}")
        print(f"Price impact: {quote.price_impact_pct}%")

@pytest.mark.asyncio
async def test_error_handling(jupiter_setup):
    """Test error handling with invalid parameters"""
    jupiter = await jupiter_setup
    
    # Test with invalid token address
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint="invalid_address",
            output_mint=SOL_ADDRESS,
            amount=AMOUNT_USDC,
            slippage_bps=SLIPPAGE
        )
    
    # Test with invalid amount
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint=USDC_ADDRESS,
            output_mint=SOL_ADDRESS,
            amount="invalid_amount",
            slippage_bps=SLIPPAGE
        )
    
    # Test with negative slippage
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint=USDC_ADDRESS,
            output_mint=SOL_ADDRESS,
            amount=AMOUNT_USDC,
            slippage_bps=-1
        )

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 