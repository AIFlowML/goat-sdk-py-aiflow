"""
Parameter definitions for Uniswap plugin operations.
"""

from typing import Optional, List, Union
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta

from .types import UniswapVersion, PoolFee, TokenInfo

class SwapParameters(BaseModel):
    """Parameters for token swaps."""
    token_in: str = Field(..., description="Address of input token")
    token_out: str = Field(..., description="Address of output token")
    amount_in: Decimal = Field(..., description="Amount of input token")
    recipient: Optional[str] = Field(None, description="Recipient address, defaults to sender")
    slippage_tolerance: Optional[Decimal] = Field(
        Decimal("0.005"),
        description="Maximum acceptable slippage, e.g. 0.005 for 0.5%"
    )
    deadline_minutes: Optional[int] = Field(
        20,
        description="Minutes until the transaction expires"
    )
    max_hops: Optional[int] = Field(3, description="Maximum number of hops in route")
    fee_tiers: Optional[List[PoolFee]] = Field(
        None,
        description="Specific fee tiers to use (V3 only)"
    )

    @validator("slippage_tolerance")
    def validate_slippage(cls, v):
        if v <= 0 or v >= 1:
            raise ValueError("Slippage must be between 0 and 1")
        return v

class AddLiquidityParameters(BaseModel):
    """Parameters for adding liquidity."""
    token0: str = Field(..., description="Address of first token")
    token1: str = Field(..., description="Address of second token")
    amount0: Decimal = Field(..., description="Amount of first token")
    amount1: Decimal = Field(..., description="Amount of second token")
    fee_tier: PoolFee = Field(..., description="Fee tier for the pool")
    recipient: Optional[str] = Field(None, description="Recipient of LP tokens")
    slippage_tolerance: Optional[Decimal] = Field(
        Decimal("0.005"),
        description="Maximum acceptable slippage"
    )
    deadline_minutes: Optional[int] = Field(
        20,
        description="Minutes until the transaction expires"
    )
    # V3 specific parameters
    tick_lower: Optional[int] = Field(None, description="Lower tick bound (V3)")
    tick_upper: Optional[int] = Field(None, description="Upper tick bound (V3)")

class RemoveLiquidityParameters(BaseModel):
    """Parameters for removing liquidity."""
    token0: str = Field(..., description="Address of first token")
    token1: str = Field(..., description="Address of second token")
    liquidity_amount: Decimal = Field(..., description="Amount of liquidity to remove")
    recipient: Optional[str] = Field(None, description="Recipient of tokens")
    slippage_tolerance: Optional[Decimal] = Field(
        Decimal("0.005"),
        description="Maximum acceptable slippage"
    )
    deadline_minutes: Optional[int] = Field(
        20,
        description="Minutes until the transaction expires"
    )
    # V3 specific
    token_id: Optional[int] = Field(None, description="NFT position token ID (V3)")

class CollectFeesParameters(BaseModel):
    """Parameters for collecting fees."""
    token_id: int = Field(..., description="NFT position token ID (V3)")
    recipient: Optional[str] = Field(None, description="Recipient of collected fees")

class PositionParameters(BaseModel):
    """Parameters for querying positions."""
    owner: str = Field(..., description="Address of position owner")
    token_id: Optional[int] = Field(None, description="Specific position token ID")
    pool_address: Optional[str] = Field(None, description="Specific pool address")

class QuoteParameters(BaseModel):
    """Parameters for price quotes."""
    token_in: str = Field(..., description="Address of input token")
    token_out: str = Field(..., description="Address of output token")
    amount: Decimal = Field(..., description="Amount to quote")
    fee_tiers: Optional[List[PoolFee]] = Field(
        None,
        description="Specific fee tiers to check"
    )
    max_hops: Optional[int] = Field(3, description="Maximum route length")
