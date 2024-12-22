"""Models for SPL Token Service."""

from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class SolanaNetwork(str, Enum):
    """Solana network types."""
    MAINNET = "mainnet"
    DEVNET = "devnet"
    TESTNET = "testnet"


class TokenType(str, Enum):
    """Token types."""
    FUNGIBLE = "fungible"
    NON_FUNGIBLE = "non-fungible"
    SEMI_FUNGIBLE = "semi-fungible"


class Token(BaseModel):
    """
    Token information model.

    Attributes:
        symbol: Token symbol (e.g., "USDC")
        name: Token name (e.g., "USD Coin")
        decimals: Number of decimal places
        mint_addresses: Mapping of network to mint address
        mode_config: Optional Mode-specific configuration
        token_type: Type of token (fungible, non-fungible, etc.)
    """
    symbol: str = Field(..., description="Token symbol")
    name: str = Field(..., description="Token name")
    decimals: int = Field(..., description="Number of decimal places")
    mint_addresses: Dict[str, str] = Field(..., description="Network to mint address mapping")
    mode_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Mode-specific configuration for the token"
    )
    token_type: TokenType = Field(
        TokenType.FUNGIBLE,
        description="Type of token"
    )


class TokenBalance(BaseModel):
    """
    Token balance information.

    Attributes:
        amount: Raw token amount
        decimals: Number of decimal places
        ui_amount: Human-readable token amount
    """
    amount: int = Field(..., description="Raw token amount")
    decimals: int = Field(..., description="Number of decimal places")
    ui_amount: float = Field(..., description="Human-readable token amount")


class TransferParams(BaseModel):
    """
    Parameters for token transfer operations.

    Attributes:
        to_address: Destination wallet address
        mint_address: Token mint address
        amount: Amount to transfer in base units
        mode_config: Optional Mode-specific configuration
    """
    to_address: str = Field(..., description="Destination wallet address")
    mint_address: str = Field(..., description="Token mint address")
    amount: int = Field(..., description="Amount to transfer in base units")
    mode_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Mode-specific configuration for the transfer"
    )
