
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
"""Type definitions for ERC20 plugin."""
from typing import Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator
from eth_typing import ChecksumAddress
from web3 import Web3


class TokenInfo(TypedDict):
    """Token information."""
    name: str
    symbol: str
    decimals: int
    total_supply: int
    balance: Optional[int]
    contract_address: Optional[str]


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


class ApproveParams(BaseModel):
    """Parameters for approving token spending."""
    token_address: str = Field(
        ...,
        description="The contract address of the token"
    )
    spender_address: str = Field(
        ...,
        description="The address to approve for spending"
    )
    amount: int = Field(
        ...,
        description="The amount to approve in base units",
        ge=0
    )

    @field_validator('token_address', 'spender_address')
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
        description="The address to transfer from"
    )
    to_address: str = Field(
        ...,
        description="The address to transfer to"
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


class GetTokenInfoBySymbolParams(BaseModel):
    """Parameters for getting token information by symbol."""
    symbol: str = Field(
        ...,
        description="The symbol of the token",
        min_length=1,
        max_length=11
    )
    address: Optional[str] = Field(
        None,
        description="Optional address to get balance for"
    )

    @field_validator('symbol')
    def validate_symbol(cls, v: str) -> str:
        """Validate token symbol."""
        return v.upper()

    @field_validator('address')
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate Ethereum address."""
        if v is None:
            return None
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class GetTokenAllowanceParams(BaseModel):
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


class ConvertToBaseUnitParams(BaseModel):
    """Parameters for converting to base units."""
    amount: float = Field(
        ...,
        description="The amount in decimal units",
        gt=0
    )
    decimals: int = Field(
        ...,
        description="The number of decimals",
        ge=0,
        le=77  # Maximum safe decimals to prevent overflow
    )


class ConvertFromBaseUnitParams(BaseModel):
    """Parameters for converting from base units."""
    amount: int = Field(
        ...,
        description="The amount in base units",
        ge=0
    )
    decimals: int = Field(
        ...,
        description="The number of decimals",
        ge=0,
        le=77  # Maximum safe decimals to prevent overflow
    )


class TokenDeploymentResult(BaseModel):
    """Result of token deployment."""
    contract_address: str = Field(
        ...,
        description="The deployed contract address"
    )
    transaction_hash: str = Field(
        ...,
        description="The deployment transaction hash"
    )
    explorer_url: str = Field(
        ...,
        description="URL to view the transaction on Mode explorer"
    )

    @field_validator('contract_address')
    def validate_address(cls, v: str) -> str:
        """Validate Ethereum address."""
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)

    @field_validator('transaction_hash')
    def validate_hash(cls, v: str) -> str:
        """Validate transaction hash."""
        if not v.startswith('0x') or len(v) != 66:
            raise ValueError("Invalid transaction hash")
        return v.lower()


class TokenInfoResult(BaseModel):
    """Result of getting token information."""
    name: str = Field(
        ...,
        description="The name of the token"
    )
    symbol: str = Field(
        ...,
        description="The symbol of the token"
    )
    decimals: int = Field(
        ...,
        description="The number of decimals",
        ge=0,
        le=77
    )
    total_supply: int = Field(
        ...,
        description="The total supply in base units",
        ge=0
    )
    balance: Optional[int] = Field(
        None,
        description="The balance in base units if address was provided",
        ge=0
    )
    contract_address: Optional[str] = Field(
        None,
        description="The contract address of the token"
    )

    @field_validator('contract_address')
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate Ethereum address."""
        if v is None:
            return None
        if not Web3.is_address(v):
            raise ValueError("Invalid Ethereum address")
        return Web3.to_checksum_address(v)


class TransactionResult(BaseModel):
    """Result of a token transaction."""
    transaction_hash: str = Field(
        ...,
        description="The transaction hash"
    )
    explorer_url: str = Field(
        ...,
        description="URL to view the transaction on Mode explorer"
    )

    @field_validator('transaction_hash')
    def validate_hash(cls, v: str) -> str:
        """Validate transaction hash."""
        if not v.startswith('0x') or len(v) != 66:
            raise ValueError("Invalid transaction hash")
        return v.lower()


class TransferParameters(TypedDict):
    """Parameters for token transfer."""
    to_address: str
    amount: int
    token_address: str
    max_fee_per_gas: Optional[int]
    max_priority_fee_per_gas: Optional[int]
    gas_limit: Optional[int]


class ApprovalParameters(TypedDict):
    """Parameters for token approval."""
    spender_address: str
    amount: int
    token_address: str
    max_fee_per_gas: Optional[int]
    max_priority_fee_per_gas: Optional[int]
    gas_limit: Optional[int]
