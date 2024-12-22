"""Configuration for Jupiter plugin."""

import os
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class JupiterConfig(BaseModel):
    """Configuration for Jupiter plugin."""

    # API URLs
    api_url: HttpUrl = Field(
        default=os.getenv("JUPITER_API_URL", "https://quote-api.jup.ag/v6"),
        description="Jupiter API URL"
    )

    # Authentication
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("JUPITER_API_KEY"),
        description="API key for Jupiter API"
    )

    # Rate Limits
    max_retries: int = Field(
        default=int(os.getenv("JUPITER_MAX_RETRIES", "3")),
        description="Maximum number of retries for API calls",
        ge=0,
    )
    retry_delay: float = Field(
        default=float(os.getenv("JUPITER_RETRY_DELAY", "0.5")),
        description="Delay between retries in seconds",
        ge=0,
    )
    timeout: float = Field(
        default=float(os.getenv("JUPITER_TIMEOUT", "30.0")),
        description="Timeout for API calls in seconds",
        gt=0,
    )
    default_slippage_bps: int = Field(
        default=int(os.getenv("JUPITER_DEFAULT_SLIPPAGE_BPS", "50")),
        description="Default slippage in basis points",
        ge=0,
        le=10000,
    )

    # Retry Settings
    auto_retry_on_timeout: bool = Field(
        default=os.getenv("JUPITER_AUTO_RETRY_ON_TIMEOUT", "true").lower() == "true",
        description="Whether to automatically retry on timeout"
    )
    auto_retry_on_rate_limit: bool = Field(
        default=os.getenv("JUPITER_AUTO_RETRY_ON_RATE_LIMIT", "true").lower() == "true",
        description="Whether to automatically retry on rate limit"
    )

    # Compute Settings
    compute_unit_price_micro_lamports: Optional[int] = Field(
        default=os.getenv("JUPITER_COMPUTE_UNIT_PRICE") and int(os.getenv("JUPITER_COMPUTE_UNIT_PRICE")),
        description="Compute unit price in micro lamports",
        ge=0,
    )
    max_accounts_per_transaction: int = Field(
        default=int(os.getenv("JUPITER_MAX_ACCOUNTS_PER_TX", "64")),
        description="Maximum number of accounts per transaction",
        ge=1,
        le=256,
    )
    prefer_post_mint_version: bool = Field(
        default=os.getenv("JUPITER_PREFER_POST_MINT", "true").lower() == "true",
        description="Whether to prefer post mint version for token accounts"
    )

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True 