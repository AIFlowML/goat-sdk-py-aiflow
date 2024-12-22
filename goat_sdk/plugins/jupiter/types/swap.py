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
     
     Path: goat_sdk/plugins/jupiter/types/swap.py
"""

"""Swap types for Jupiter plugin."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .quote import QuoteResponse


class SwapRequest(BaseModel):
    """Request for a swap operation."""

    model_config = ConfigDict(populate_by_name=True)

    user_public_key: str = Field(..., alias="userPublicKey", description="The user's public key")
    quote_response: QuoteResponse = Field(..., alias="quoteResponse", description="The quote response")
    dynamic_compute_unit_limit: bool = Field(True, alias="dynamicComputeUnitLimit", description="Whether to use dynamic compute unit limit")
    prioritization_fee_lamports: str = Field("auto", alias="prioritizationFeeLamports", description="The prioritization fee in lamports")

    @field_validator("user_public_key")
    def validate_public_key(cls, v: str) -> str:
        """Validate public key format."""
        if not v.startswith("0x"):
            raise ValueError("Public key must start with '0x'")
        if len(v) != 66:  # 0x + 64 hex chars
            raise ValueError("Public key must be 32 bytes (64 hex characters)")
        try:
            int(v[2:], 16)
        except ValueError:
            raise ValueError("Public key must be a valid hex string")
        return v

    @field_validator("prioritization_fee_lamports")
    def validate_prioritization_fee(cls, v: str) -> str:
        """Validate prioritization fee."""
        if v != "auto":
            try:
                fee = int(v)
                if fee < 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Prioritization fee must be 'auto' or a non-negative integer")
        return v


class SwapResponse(BaseModel):
    """Response from a swap operation."""

    model_config = ConfigDict(populate_by_name=True)

    swap_transaction: str = Field(..., alias="swapTransaction", description="The base64 encoded swap transaction")
    address_lookup_tables: List[str] = Field(..., alias="addressLookupTables", description="The address lookup tables")


class SwapResult(BaseModel):
    """Result of a swap operation."""

    model_config = ConfigDict(populate_by_name=True)

    transaction_hash: str = Field(..., alias="transactionHash", description="The transaction hash")
    input_amount: str = Field(..., alias="inputAmount", description="The input amount")
    output_amount: str = Field(..., alias="outputAmount", description="The output amount")
    price_impact: str = Field(..., alias="priceImpact", description="The price impact percentage")
    fee_amount: str = Field(..., alias="feeAmount", description="The fee amount")
    platform_fee: Optional[str] = Field(None, alias="platformFee", description="The platform fee")
    route_plan: List[dict] = Field(..., alias="routePlan", description="The route plan")

    @field_validator("transaction_hash")
    def validate_transaction_hash(cls, v: str) -> str:
        """Validate transaction hash format."""
        if not v.startswith("0x"):
            raise ValueError("Transaction hash must start with '0x'")
        if len(v) != 66:  # 0x + 64 hex chars
            raise ValueError("Transaction hash must be 32 bytes (64 hex characters)")
        try:
            int(v[2:], 16)
        except ValueError:
            raise ValueError("Transaction hash must be a valid hex string")
        return v

    @field_validator("input_amount", "output_amount", "fee_amount")
    def validate_amount(cls, v: str) -> str:
        """Validate amount is a valid integer string."""
        try:
            int(v)
        except ValueError:
            raise ValueError("Amount must be a valid integer string")
        return v

    @field_validator("platform_fee")
    def validate_platform_fee(cls, v: Optional[str]) -> Optional[str]:
        """Validate platform fee if present."""
        if v is not None:
            try:
                int(v)
            except ValueError:
                raise ValueError("Platform fee must be a valid integer string")
        return v