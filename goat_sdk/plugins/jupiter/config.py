"""Configuration for Jupiter plugin."""

from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class JupiterConfig(BaseModel):
    """Configuration for Jupiter plugin."""

    api_url: HttpUrl = Field(
        "https://quote-api.jup.ag/v6",
        description="Jupiter API URL",
    )
    max_retries: int = Field(
        3,
        description="Maximum number of retries for API calls",
        ge=0,
    )
    retry_delay: float = Field(
        0.5,
        description="Delay between retries in seconds",
        ge=0,
    )
    timeout: float = Field(
        30.0,
        description="Timeout for API calls in seconds",
        gt=0,
    )
    default_slippage_bps: int = Field(
        50,
        description="Default slippage in basis points",
        ge=0,
        le=10000,
    )
    auto_retry_on_timeout: bool = Field(
        True,
        description="Whether to automatically retry on timeout",
    )
    auto_retry_on_rate_limit: bool = Field(
        True,
        description="Whether to automatically retry on rate limit",
    )
    api_key: Optional[str] = Field(
        None,
        description="API key for Jupiter API",
    )
    compute_unit_price_micro_lamports: Optional[int] = Field(
        None,
        description="Compute unit price in micro lamports",
        ge=0,
    )
    max_accounts_per_transaction: int = Field(
        64,
        description="Maximum number of accounts per transaction",
        ge=1,
        le=256,
    )
    prefer_post_mint_version: bool = Field(
        True,
        description="Whether to prefer post mint version for token accounts",
    ) 