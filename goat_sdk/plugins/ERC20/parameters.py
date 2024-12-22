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
     
     Path: examples/hyperliquid/ai_trading_agent.py
"""


"""Parameter types for the ERC20 plugin."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from web3 import Web3


class ERC20PluginCtorParams(BaseModel):
    """Parameters for constructing an ERC20Plugin instance."""
    private_key: str = Field(
        ...,
        description="Private key for signing transactions"
    )
    provider_url: str = Field(
        ...,
        description="URL of the Mode network provider"
    )
    network: str = Field(
        default="testnet",
        description="Mode network to connect to (mainnet or testnet)"
    )


class GetTokenInfoParams(BaseModel):
    """Parameters for getting token information."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    address: Optional[str] = Field(
        None,
        description="Optional address to get balance for"
    )

    @field_validator('token_address', 'address')
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate Ethereum address."""
        if v is None:
            return None
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class GetBalanceParams(BaseModel):
    """Parameters for getting token balance."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    wallet_address: str = Field(
        ...,
        description="The wallet address to get balance for"
    )

    @field_validator('token_address', 'wallet_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class GetAllowanceParams(BaseModel):
    """Parameters for getting token allowance."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    owner_address: str = Field(
        ...,
        description="The address of the token owner"
    )
    spender_address: str = Field(
        ...,
        description="The address of the spender"
    )

    @field_validator('token_address', 'owner_address', 'spender_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class ApproveParams(BaseModel):
    """Parameters for approving token spending."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    spender_address: str = Field(
        ...,
        description="The address of the spender"
    )
    amount: int = Field(
        ...,
        description="The amount to approve in base units",
        gt=0
    )

    @field_validator('token_address', 'spender_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class TransferParams(BaseModel):
    """Parameters for transferring tokens."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    to_address: str = Field(
        ...,
        description="The recipient address"
    )
    amount: int = Field(
        ...,
        description="The amount to transfer in base units",
        gt=0
    )

    @field_validator('token_address', 'to_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class TransferFromParams(BaseModel):
    """Parameters for transferring tokens on behalf of another address."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    from_address: str = Field(
        ...,
        description="The address to transfer tokens from"
    )
    to_address: str = Field(
        ...,
        description="The address to transfer tokens to"
    )
    amount: int = Field(
        ...,
        description="The amount to transfer in base units",
        gt=0
    )

    @field_validator('token_address', 'from_address', 'to_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class DeployTokenParams(BaseModel):
    """Parameters for deploying a new token."""
    name: str = Field(
        ...,
        description="The name of the token",
        min_length=1,
        max_length=64
    )
    symbol: str = Field(
        ...,
        description="The symbol of the token",
        min_length=1,
        max_length=11
    )
    initial_supply: int = Field(
        ...,
        description="The initial supply of the token in base units",
        gt=0
    )

    @field_validator('symbol')
    def validate_symbol(cls, v: str) -> str:
        """Validate token symbol."""
        return v.upper()
