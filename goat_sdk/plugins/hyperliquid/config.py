"""Configuration for Hyperliquid plugin."""

import os
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class HyperliquidConfig(BaseModel):
    """Configuration for Hyperliquid plugin."""

    # Network Settings
    testnet: bool = Field(
        default=False,
        description="Whether to use testnet"
    )

    # API URLs
    api_url: HttpUrl = Field(
        default=os.getenv("HYPERLIQUID_MAINNET_URL", "https://api.hyperliquid.xyz"),
        description="Base URL for Hyperliquid API"
    )
    testnet_api_url: HttpUrl = Field(
        default=os.getenv("HYPERLIQUID_TESTNET_URL", "https://api.hyperliquid-testnet.xyz"),
        description="Base URL for Hyperliquid testnet API"
    )
    ws_url: HttpUrl = Field(
        default=os.getenv("HYPERLIQUID_WS_MAINNET_URL", "wss://api.hyperliquid.xyz/ws"),
        description="WebSocket URL for Hyperliquid API"
    )
    testnet_ws_url: HttpUrl = Field(
        default=os.getenv("HYPERLIQUID_WS_TESTNET_URL", "wss://api.hyperliquid-testnet.xyz/ws"),
        description="WebSocket URL for Hyperliquid testnet API"
    )

    # Authentication
    api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("HYPERLIQUID_API_KEY"),
        description="API key for authentication"
    )
    api_secret: Optional[str] = Field(
        default_factory=lambda: os.getenv("HYPERLIQUID_API_SECRET"),
        description="API secret for authentication"
    )

    # Rate Limits
    market_data_rate_limit: int = Field(
        default=10,
        description="Rate limit for market data requests per second"
    )
    orders_rate_limit: int = Field(
        default=5,
        description="Rate limit for order requests per second"
    )
    account_rate_limit: int = Field(
        default=2,
        description="Rate limit for account requests per second"
    )

    # Connection Settings
    use_ssl: bool = Field(
        default=True,
        description="Whether to use SSL for connections"
    )
    ssl_verify: bool = Field(
        default=True,
        description="Whether to verify SSL certificates"
    )
    max_connections: int = Field(
        default=100,
        description="Maximum number of concurrent connections"
    )

    # Timeouts (in seconds)
    request_timeout: float = Field(
        default=30.0,
        description="Total request timeout"
    )
    connect_timeout: float = Field(
        default=10.0,
        description="Connection establishment timeout"
    )
    sock_connect_timeout: float = Field(
        default=10.0,
        description="Socket connection timeout"
    )
    sock_read_timeout: float = Field(
        default=10.0,
        description="Socket read timeout"
    )

    # WebSocket Settings
    ws_ping_interval: float = Field(
        default=20.0,
        description="WebSocket ping interval in seconds"
    )
    ws_ping_timeout: float = Field(
        default=10.0,
        description="WebSocket ping timeout in seconds"
    )
    ws_close_timeout: float = Field(
        default=10.0,
        description="WebSocket close timeout in seconds"
    )

    # Retry Settings
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    retry_delay: float = Field(
        default=1.0,
        description="Delay between retry attempts in seconds"
    )

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True
 