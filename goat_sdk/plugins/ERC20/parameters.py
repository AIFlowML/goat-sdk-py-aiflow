"""Parameter types for the ERC20 plugin."""

from typing import Optional
from pydantic import BaseModel, Field


class ERC20PluginCtorParams(BaseModel):
    """Parameters for constructing an ERC20Plugin instance."""
    chain_id: int = Field(..., description="Chain ID of the network")
    rpc_url: str = Field(..., description="RPC URL for the network")
    private_key: Optional[str] = Field(None, description="Private key for transactions")


class GetTokenInfoParams(BaseModel):
    """Parameters for getting token information."""
    token_address: str = Field(..., description="Address of the token contract")


class GetBalanceParams(BaseModel):
    """Parameters for getting token balance."""
    token_address: str = Field(..., description="Address of the token contract")
    wallet_address: str = Field(..., description="Address to check balance for")


class GetAllowanceParams(BaseModel):
    """Parameters for getting token allowance."""
    token_address: str = Field(..., description="Address of the token contract")
    owner_address: str = Field(..., description="Address of the token owner")
    spender_address: str = Field(..., description="Address of the spender")


class ApproveParams(BaseModel):
    """Parameters for approving token spending."""
    token_address: str = Field(..., description="Address of the token contract")
    spender_address: str = Field(..., description="Address of the spender")
    amount: str = Field(..., description="Amount to approve")


class TransferParams(BaseModel):
    """Parameters for transferring tokens."""
    token_address: str = Field(..., description="Address of the token contract")
    recipient_address: str = Field(..., description="Address to transfer tokens to")
    amount: str = Field(..., description="Amount to transfer")


class TransferFromParams(BaseModel):
    """Parameters for transferring tokens on behalf of another address."""
    token_address: str = Field(..., description="Address of the token contract")
    sender_address: str = Field(..., description="Address to transfer tokens from")
    recipient_address: str = Field(..., description="Address to transfer tokens to")
    amount: str = Field(..., description="Amount to transfer")


class DeployTokenParams(BaseModel):
    """Parameters for deploying a new token contract."""
    name: str = Field(..., description="Name of the token")
    symbol: str = Field(..., description="Symbol of the token")
    initial_supply: int = Field(..., description="Initial supply of tokens")
    private_key: Optional[str] = Field(None, description="Private key for deployment")
