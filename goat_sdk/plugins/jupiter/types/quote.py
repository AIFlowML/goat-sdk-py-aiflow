"""Quote types for Jupiter API."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SwapMode(str, Enum):
    """Swap mode enum."""

    EXACT_IN = "ExactIn"
    EXACT_OUT = "ExactOut"


class QuoteRequest(BaseModel):
    """Request for a quote."""

    model_config = ConfigDict(populate_by_name=True)

    input_mint: str = Field(..., alias="inputMint", description="The input token mint address")
    output_mint: str = Field(..., alias="outputMint", description="The output token mint address")
    amount: str = Field(..., description="The amount to swap")
    slippage_bps: int = Field(..., alias="slippageBps", description="The slippage tolerance in basis points")
    swap_mode: str = Field(..., alias="swapMode", description="The swap mode")

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

    @field_validator("swap_mode")
    def validate_swap_mode(cls, v: str) -> str:
        """Validate swap mode is valid."""
        if v not in [mode.value for mode in SwapMode]:
            raise ValueError(f"swap_mode must be one of {[mode.value for mode in SwapMode]}")
        return v


class SwapInfo(BaseModel):
    """Swap info for a route step."""

    model_config = ConfigDict(populate_by_name=True)

    amm_key: str = Field(..., alias="ammKey", description="The AMM key")
    label: str = Field(..., description="The AMM label")
    input_mint: str = Field(..., alias="inputMint", description="The input token mint address")
    output_mint: str = Field(..., alias="outputMint", description="The output token mint address")
    in_amount: str = Field(..., alias="inAmount", description="The input amount")
    out_amount: str = Field(..., alias="outAmount", description="The output amount")
    fee_amount: str = Field(..., alias="feeAmount", description="The fee amount")
    fee_mint: str = Field(..., alias="feeMint", description="The fee token mint address")

    @field_validator("in_amount", "out_amount", "fee_amount")
    def validate_amount(cls, v: str) -> str:
        """Validate amount is a valid integer string."""
        try:
            int(v)
        except ValueError:
            raise ValueError("Amount must be a valid integer string")
        return v


class PlatformFee(BaseModel):
    """Platform fee for a swap."""

    model_config = ConfigDict(populate_by_name=True)

    amount: str = Field(..., description="The fee amount")
    fee_mint: str = Field(..., alias="feeMint", description="The fee token mint address")
    fee_bps: int = Field(..., alias="feeBps", description="The fee basis points")

    @field_validator("amount")
    def validate_amount(cls, v: str) -> str:
        """Validate amount is a valid integer string."""
        try:
            int(v)
        except ValueError:
            raise ValueError("Amount must be a valid integer string")
        return v

    @field_validator("fee_bps")
    def validate_fee_bps(cls, v: int) -> int:
        """Validate fee_bps is between 0 and 10000."""
        if v < 0 or v > 10000:
            raise ValueError("fee_bps must be between 0 and 10000")
        return v


class RoutePlanStep(BaseModel):
    """Step in a route plan."""

    model_config = ConfigDict(populate_by_name=True)

    swap_info: SwapInfo = Field(..., alias="swapInfo", description="The swap information")
    percent: float = Field(..., description="The percentage of the swap amount to route through this step")

    @field_validator("percent")
    def validate_percent(cls, v: float) -> float:
        """Validate percent is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("percent must be between 0 and 100")
        return v


class QuoteResponse(BaseModel):
    """Response from quote request."""

    model_config = ConfigDict(populate_by_name=True)

    input_mint: str = Field(..., alias="inputMint", description="The input token mint address")
    in_amount: str = Field(..., alias="inAmount", description="The input amount")
    output_mint: str = Field(..., alias="outputMint", description="The output token mint address")
    out_amount: str = Field(..., alias="outAmount", description="The output amount")
    other_amount_threshold: str = Field(..., alias="otherAmountThreshold", description="The minimum output amount threshold")
    swap_mode: SwapMode = Field(..., alias="swapMode", description="The swap mode")
    slippage_bps: int = Field(..., alias="slippageBps", description="The slippage tolerance in basis points")
    price_impact_pct: str = Field(..., alias="priceImpactPct", description="The price impact percentage")
    route_plan: List[RoutePlanStep] = Field(..., alias="routePlan", description="The route plan steps")
    platform_fee: Optional[PlatformFee] = Field(None, alias="platformFee", description="The platform fee")
    context_slot: Optional[int] = Field(None, alias="contextSlot", description="The context slot")
    time_taken: Optional[float] = Field(None, alias="timeTaken", description="The time taken to compute the quote")

    @field_validator("in_amount", "out_amount", "other_amount_threshold")
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