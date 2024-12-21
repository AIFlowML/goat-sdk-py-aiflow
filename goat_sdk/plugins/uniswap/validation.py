"""
Enhanced parameter validation for Uniswap plugin.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from decimal import Decimal
from pydantic import (
    BaseModel,
    Field,
    validator,
    constr,
    conint,
    condecimal,
    AnyHttpUrl,
    SecretStr,
)
from eth_typing import Address, HexStr
from eth_utils import is_address, is_hex

class SwapType(str, Enum):
    EXACT_IN = "EXACT_IN"
    EXACT_OUT = "EXACT_OUT"

class Protocol(str, Enum):
    V2 = "V2"
    V3 = "V3"

class Routing(str, Enum):
    CLASSIC = "CLASSIC"
    SPLIT = "SPLIT"
    MEV_PROTECTED = "MEV_PROTECTED"

class SecurityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class EthereumAddress(str):
    """Custom type for Ethereum address validation."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        if not is_address(v):
            raise ValueError("invalid ethereum address")
        return v.lower()

class HexString(str):
    """Custom type for hex string validation."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        if not is_hex(v):
            raise ValueError("invalid hex string")
        return v.lower()

class TokenAmount(BaseModel):
    """Validated token amount with decimals."""
    amount: condecimal(gt=Decimal(0))
    decimals: conint(ge=0, le=18)
    
    @validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

class GasSettings(BaseModel):
    """Gas settings with validation."""
    max_fee_per_gas: Optional[condecimal(gt=Decimal(0))]
    max_priority_fee_per_gas: Optional[condecimal(gt=Decimal(0))]
    gas_limit: Optional[conint(gt=0)]
    
    @validator("gas_limit")
    def validate_gas_limit(cls, v):
        if v and v < 21000:
            raise ValueError("Gas limit too low")
        if v and v > 30000000:
            raise ValueError("Gas limit too high")
        return v

class SecuritySettings(BaseModel):
    """Security settings for swaps."""
    min_liquidity: condecimal(gt=Decimal(0)) = Field(
        default=Decimal("1000"),
        description="Minimum pool liquidity in USD"
    )
    max_price_impact: condecimal(gt=Decimal(0), lt=Decimal("1")) = Field(
        default=Decimal("0.05"),
        description="Maximum acceptable price impact (0-1)"
    )
    security_level: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM,
        description="Security level for MEV protection"
    )
    simulate_transaction: bool = Field(
        default=True,
        description="Whether to simulate transaction before sending"
    )
    check_verified_tokens: bool = Field(
        default=True,
        description="Whether to check if tokens are verified"
    )

class PermitData(BaseModel):
    """EIP-2612 permit data."""
    domain: Dict[str, Union[int, str]]
    types: Dict[str, List[Dict[str, str]]]
    primary_type: str
    message: Dict[str, Union[int, str, bool]]
    signature: Optional[HexString]

class Quote(BaseModel):
    """Detailed quote information."""
    chain_id: conint(gt=0)
    swapper: EthereumAddress
    input_token: EthereumAddress
    output_token: EthereumAddress
    input_amount: TokenAmount
    output_amount: TokenAmount
    slippage_tolerance: condecimal(gt=Decimal(0), lt=Decimal("1"))
    trade_type: SwapType
    route_addresses: List[EthereumAddress]
    route_fees: List[int]
    gas_estimate: conint(gt=0)
    gas_price_gwei: condecimal(gt=Decimal(0))
    price_impact: condecimal(ge=Decimal(0), lt=Decimal("1"))
    minimum_output: TokenAmount
    maximum_input: Optional[TokenAmount]
    block_number: conint(gt=0)
    quote_id: str = Field(min_length=1)
    
    @validator("route_addresses")
    def validate_route(cls, v):
        if len(v) < 2:
            raise ValueError("Route must have at least 2 addresses")
        return v

class SwapParameters(BaseModel):
    """Enhanced swap parameters."""
    quote: Quote
    permit_data: Optional[PermitData]
    security_settings: SecuritySettings = Field(default_factory=SecuritySettings)
    gas_settings: Optional[GasSettings]
    deadline_minutes: conint(gt=0) = Field(default=20)
    recipient: Optional[EthereumAddress]
    
    @validator("deadline_minutes")
    def validate_deadline(cls, v):
        if v > 60:
            raise ValueError("Deadline cannot be more than 60 minutes")
        return v

class SwapResponse(BaseModel):
    """Swap execution response."""
    transaction_hash: HexString
    input_token: EthereumAddress
    output_token: EthereumAddress
    input_amount: TokenAmount
    output_amount: TokenAmount
    gas_used: conint(gt=0)
    gas_price_gwei: condecimal(gt=Decimal(0))
    block_number: conint(gt=0)
    timestamp: int
    success: bool
    error_message: Optional[str]
