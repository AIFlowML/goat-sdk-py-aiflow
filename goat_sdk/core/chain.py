"""Chain type for Mode SDK."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class Chain(BaseModel):
    """Chain type for Mode SDK."""

    type: Literal["solana", "ethereum", "evm"] = Field(
        default="solana",
        description="Type of blockchain"
    )
    network: Literal["mainnet", "testnet", "devnet"] = Field(
        default="mainnet",
        description="Network type"
    )
    chain_id: Optional[int] = Field(
        default=None,
        description="Chain ID for EVM chains"
    )