"""Parameter classes for SPL Token Service."""

from typing import Optional
from pydantic import BaseModel, Field


class ModeConfig(BaseModel):
    """Mode-specific configuration."""

    retry_attempts: int = Field(default=3, description="Number of retry attempts for operations")
    retry_on_not_found: bool = Field(default=True, description="Retry if account not found")
    raise_on_error: bool = Field(default=True, description="Raise exceptions on errors")
    network_validation: bool = Field(default=True, description="Validate network support")
    min_transfer_validation: bool = Field(default=True, description="Validate minimum transfer amounts")


class GetTokenMintAddressBySymbolParameters(BaseModel):
    """Parameters for getting token mint address by symbol."""

    symbol: str = Field(..., description="Token symbol")
    mode_config: Optional[ModeConfig] = Field(
        default=None,
        description="Mode-specific configuration",
    )


class GetTokenBalanceByMintAddressParameters(BaseModel):
    """Parameters for getting token balance by mint address."""

    wallet_address: str = Field(..., description="Wallet address")
    mint_address: str = Field(..., description="Token mint address")
    mode_config: Optional[ModeConfig] = Field(
        default=None,
        description="Mode-specific configuration",
    )


class TransferTokenByMintAddressParameters(BaseModel):
    """Parameters for transferring tokens by mint address."""

    to: str = Field(..., description="Destination wallet address")
    mint_address: str = Field(..., description="Token mint address")
    amount: int = Field(..., description="Amount to transfer in base units")
    mode_config: Optional[ModeConfig] = Field(
        default=None,
        description="Mode-specific configuration",
    )


class ConvertToBaseUnitParameters(BaseModel):
    """Parameters for converting token amount to base units."""

    amount: float = Field(..., description="Amount to convert")
    decimals: int = Field(..., description="Token decimals")
    mode_config: Optional[ModeConfig] = Field(
        default=None,
        description="Mode-specific configuration",
    )
