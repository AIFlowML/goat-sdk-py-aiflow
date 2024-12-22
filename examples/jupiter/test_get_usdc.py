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
     
     Path: examples/jupiter/test_get_usdc.py
"""

"""Tests for getting USDC using Jupiter."""

import pytest
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.types import Network
from goat_sdk.core.types import ChainType
from goat_sdk.plugins.jupiter import JupiterPlugin

# Constants for testing
TEST_PRIVATE_KEY = "0x" + "11" * 32  # Test private key (64 hex chars)
SOL_ADDRESS = "So11111111111111111111111111111111111111112"
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
AMOUNT_SOL = "100000000"  # 0.1 SOL
SLIPPAGE = 50  # 0.5%

@pytest.fixture
def jupiter_setup():
    """Set up Jupiter plugin for testing."""
    sdk = GoatSDK(
        private_key=TEST_PRIVATE_KEY,
        network=Network.MAINNET,
        chain=ChainType.SOLANA
    )
    jupiter = JupiterPlugin()
    return jupiter

@pytest.mark.asyncio
async def test_get_quote_for_usdc(jupiter_setup):
    """Test getting a quote for SOL to USDC swap."""
    jupiter = jupiter_setup
    
    quote = await jupiter.get_quote(
        input_mint=SOL_ADDRESS,
        output_mint=USDC_ADDRESS,
        amount=AMOUNT_SOL,
        slippage_bps=SLIPPAGE
    )
    
    assert quote is not None
    assert quote.input_mint == SOL_ADDRESS
    assert quote.output_mint == USDC_ADDRESS
    assert quote.in_amount == AMOUNT_SOL
    assert quote.slippage_bps == SLIPPAGE
    assert float(quote.price_impact_pct) >= 0
    
    print(f"\nQuote received:")
    print(f"Input amount: {quote.in_amount} SOL")
    print(f"Output amount: {quote.out_amount} USDC")
    print(f"Price impact: {quote.price_impact_pct}%")

@pytest.mark.asyncio
async def test_execute_swap_for_usdc(jupiter_setup):
    """Test executing a SOL to USDC swap."""
    jupiter = jupiter_setup
    
    # First get a quote
    quote = await jupiter.get_quote(
        input_mint=SOL_ADDRESS,
        output_mint=USDC_ADDRESS,
        amount=AMOUNT_SOL,
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
        print(f"Input amount: {result.input_amount} SOL")
        print(f"Output amount: {result.output_amount} USDC")
        print(f"Price impact: {result.price_impact}%")
    else:
        pytest.skip("Skipped due to high price impact")

@pytest.mark.asyncio
async def test_get_quote_with_different_amounts(jupiter_setup):
    """Test getting quotes with different SOL amounts."""
    jupiter = jupiter_setup
    
    amounts = ["50000000", "100000000", "200000000"]  # 0.05, 0.1, 0.2 SOL
    
    for amount in amounts:
        quote = await jupiter.get_quote(
            input_mint=SOL_ADDRESS,
            output_mint=USDC_ADDRESS,
            amount=amount,
            slippage_bps=SLIPPAGE
        )
        
        assert quote is not None
        print(f"\nQuote for {int(amount)/1000000000} SOL:")
        print(f"Input amount: {quote.in_amount} SOL")
        print(f"Output amount: {quote.out_amount} USDC")
        print(f"Price impact: {quote.price_impact_pct}%")

@pytest.mark.asyncio
async def test_error_handling(jupiter_setup):
    """Test error handling with invalid parameters."""
    jupiter = jupiter_setup
    
    # Test with invalid token address
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint="invalid_address",
            output_mint=USDC_ADDRESS,
            amount=AMOUNT_SOL,
            slippage_bps=SLIPPAGE
        )
    
    # Test with invalid amount
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint=SOL_ADDRESS,
            output_mint=USDC_ADDRESS,
            amount="invalid_amount",
            slippage_bps=SLIPPAGE
        )
    
    # Test with negative slippage
    with pytest.raises(Exception):
        await jupiter.get_quote(
            input_mint=SOL_ADDRESS,
            output_mint=USDC_ADDRESS,
            amount=AMOUNT_SOL,
            slippage_bps=-1
        ) 