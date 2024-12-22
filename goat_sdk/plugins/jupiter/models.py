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
     
     Path: goat_sdk/plugins/hyperliquid/utils.py
"""

"""Models for Jupiter API."""

from pydantic import BaseModel, Field, field_validator, ConfigDict

from goat_sdk.core.wallet_client import ModeWalletClient
from .types import SwapMode


class QuoteRequest(BaseModel):
    """Request for a quote."""

    model_config = ConfigDict(populate_by_name=True)

    input_mint: str = Field(..., alias="inputMint", description="The input token mint address")
    output_mint: str = Field(..., alias="outputMint", description="The output token mint address")
    amount: str = Field(..., description="The amount to swap")
    slippage_bps: int = Field(..., alias="slippageBps", description="The slippage tolerance in basis points")
    swap_mode: SwapMode = Field(SwapMode.EXACT_IN, alias="swapMode", description="The swap mode")

    @field_validator("amount")
    def validate_amount(cls, v: str) -> str:
        """Validate amount is a valid integer string."""
        try:
            int(v)
        except ValueError:
            raise ValueError("Amount must be a valid integer string")
        return v

    @field_validator("slippage_bps")
    def validate_slippage_bps(cls, v: int) -> int:
        """Validate slippage_bps is between 0 and 10000."""
        if v < 0 or v > 10000:
            raise ValueError("slippage_bps must be between 0 and 10000")
        return v


class SwapRequest(BaseModel):
    """Request for a swap."""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    wallet_client: ModeWalletClient = Field(..., description="The wallet client to use for the swap")
    quote_request: QuoteRequest = Field(..., alias="quoteRequest", description="The quote request parameters") 