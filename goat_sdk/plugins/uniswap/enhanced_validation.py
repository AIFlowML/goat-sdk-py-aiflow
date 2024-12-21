"""
Enhanced validation for Uniswap operations.
"""

from typing import Dict, List, Optional, Union, Any
from decimal import Decimal
from datetime import datetime, timedelta
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    constr,
    conint,
    condecimal,
    AnyHttpUrl,
    SecretStr,
    EmailStr,
    GetCoreSchemaHandler,
)
from pydantic_core import CoreSchema, core_schema
from eth_utils import (
    is_address,
    is_hex,
    to_checksum_address,
    to_wei,
    from_wei,
)

class EnhancedEthereumAddress(str):
    """Enhanced Ethereum address validation."""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(),
            ]),
            serialization=core_schema.str_schema(),
        )

    @classmethod
    def validate(cls, value: str) -> 'EnhancedEthereumAddress':
        if not isinstance(value, str):
            raise TypeError("string required")
            
        # Check basic address format
        if not is_address(value):
            raise ValueError("invalid ethereum address")
            
        # Check for zero address
        if value.lower() == "0x0000000000000000000000000000000000000000":
            raise ValueError("zero address not allowed")
            
        # Check for common contract addresses
        common_contracts = {
            "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",
            "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
            # Add more known contracts
        }
        
        addr = value.lower()
        if addr in common_contracts:
            # You might want to handle known contracts differently
            pass
            
        return cls(to_checksum_address(value))

class EnhancedTokenAmount(BaseModel):
    """Enhanced token amount validation."""
    
    amount: condecimal(gt=Decimal(0)) = Field(
        ...,
        description="Token amount"
    )
    decimals: conint(ge=0, le=18) = Field(
        ...,
        description="Token decimals"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal, info) -> Decimal:
        # Check reasonable bounds
        if v > Decimal("1e36"):
            raise ValueError("amount too large")
            
        # Check decimal places
        decimal_places = abs(v.as_tuple().exponent)
        if "decimals" in info.data and decimal_places > info.data["decimals"]:
            raise ValueError(f"amount has too many decimal places for token decimals {info.data['decimals']}")
            
        return v

    @model_validator(mode='after')
    def validate_total(self) -> 'EnhancedTokenAmount':
        amount = self.amount
        decimals = self.decimals
        
        if amount and decimals:
            # Convert to wei for validation
            try:
                wei_value = int(amount * Decimal(10) ** decimals)
                if wei_value < 1:
                    raise ValueError("amount too small")
                if wei_value > 2**256 - 1:
                    raise ValueError("amount exceeds uint256")
            except Exception as e:
                raise ValueError(f"invalid amount conversion: {str(e)}")
                
        return self

class EnhancedGasSettings(BaseModel):
    """Enhanced gas settings validation."""
    
    max_fee_per_gas: Optional[condecimal(gt=Decimal(0))] = Field(
        None,
        description="Maximum fee per gas in wei"
    )
    max_priority_fee_per_gas: Optional[condecimal(gt=Decimal(0))] = Field(
        None,
        description="Maximum priority fee per gas in wei"
    )
    gas_limit: Optional[conint(gt=21000)] = Field(
        None,
        description="Gas limit for the transaction"
    )
    
    @model_validator(mode='after')
    def validate_gas_settings(self) -> 'EnhancedGasSettings':
        if self.max_fee_per_gas is not None and self.max_priority_fee_per_gas is not None:
            if self.max_fee_per_gas < self.max_priority_fee_per_gas:
                raise ValueError("max_fee_per_gas must be >= max_priority_fee_per_gas")
        return self

class EnhancedSlippageSettings(BaseModel):
    """Enhanced slippage settings validation."""
    
    slippage_tolerance: condecimal(gt=Decimal(0), lt=Decimal(100)) = Field(
        ...,
        description="Slippage tolerance percentage"
    )
    min_output_amount: Optional[EnhancedTokenAmount] = Field(
        None,
        description="Minimum output amount"
    )
    deadline: Optional[datetime] = Field(
        None,
        description="Transaction deadline"
    )
    
    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.utcnow()
            if v <= now:
                raise ValueError("deadline must be in the future")
            if v > now + timedelta(hours=24):
                raise ValueError("deadline cannot be more than 24 hours in the future")
        return v

class EnhancedRouteValidation(BaseModel):
    """Enhanced route validation."""
    
    path: List[EnhancedEthereumAddress] = Field(
        ...,
        min_length=2,
        description="Token path for the swap"
    )
    pools: List[EnhancedEthereumAddress] = Field(
        ...,
        min_length=1,
        description="Pool addresses for the swap"
    )
    
    @model_validator(mode='after')
    def validate_route(self) -> 'EnhancedRouteValidation':
        # Validate path and pools length relationship
        if len(self.pools) != len(self.path) - 1:
            raise ValueError("number of pools must be equal to number of tokens - 1")
            
        # Check for duplicate tokens in path
        if len(set(self.path)) != len(self.path):
            raise ValueError("duplicate tokens in path")
            
        # Check for duplicate pools
        if len(set(self.pools)) != len(self.pools):
            raise ValueError("duplicate pools in route")
            
        return self

class EnhancedSwapValidation(BaseModel):
    """Enhanced swap validation."""
    
    token_in: EnhancedEthereumAddress = Field(
        ...,
        description="Input token address"
    )
    token_out: EnhancedEthereumAddress = Field(
        ...,
        description="Output token address"
    )
    amount_in: EnhancedTokenAmount = Field(
        ...,
        description="Input amount"
    )
    route: EnhancedRouteValidation = Field(
        ...,
        description="Swap route"
    )
    slippage: EnhancedSlippageSettings = Field(
        ...,
        description="Slippage settings"
    )
    gas: Optional[EnhancedGasSettings] = Field(
        None,
        description="Gas settings"
    )
    
    @model_validator(mode='after')
    def validate_swap(self) -> 'EnhancedSwapValidation':
        # Validate token_in and token_out match route
        if self.token_in != self.route.path[0]:
            raise ValueError("token_in must match first token in route")
        if self.token_out != self.route.path[-1]:
            raise ValueError("token_out must match last token in route")
            
        # Additional route-specific validations
        if len(self.route.path) > 4:
            raise ValueError("route cannot have more than 4 hops")
            
        return self
