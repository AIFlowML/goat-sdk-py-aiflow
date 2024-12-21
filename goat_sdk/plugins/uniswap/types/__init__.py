"""
Type definitions for the Uniswap plugin.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Union
from decimal import Decimal
from enum import Enum

class UniswapVersion(Enum):
    V2 = "v2"
    V3 = "v3"

class PoolFee(Enum):
    LOWEST = 100    # 0.01%
    LOW = 500       # 0.05%
    MEDIUM = 3000   # 0.3%
    HIGH = 10000    # 1%

@dataclass
class UniswapPluginConfig:
    """Configuration for the Uniswap plugin."""
    version: UniswapVersion
    router_address: str
    factory_address: str
    quoter_address: Optional[str] = None  # Required for V3
    position_manager_address: Optional[str] = None  # Required for V3
    default_slippage: Decimal = Decimal("0.005")  # 0.5%
    default_deadline_minutes: int = 20
    max_hops: int = 3
    supported_fee_tiers: List[PoolFee] = None

@dataclass
class TokenInfo:
    """Detailed token information."""
    address: str
    symbol: str
    name: str
    decimals: int
    chain_id: int
    logo_uri: Optional[str] = None
    price_usd: Optional[Decimal] = None
    verified: bool = False

@dataclass
class PoolInfo:
    """Liquidity pool information."""
    address: str
    token0: TokenInfo
    token1: TokenInfo
    fee: PoolFee
    liquidity: Decimal
    token0_price: Decimal
    token1_price: Decimal
    sqrt_price_x96: Optional[int] = None  # V3 only
    tick: Optional[int] = None  # V3 only
    tvl_usd: Optional[Decimal] = None

@dataclass
class SwapRoute:
    """Detailed swap route information."""
    path: List[str]  # Token addresses in order
    pools: List[str]  # Pool addresses in order
    fees: List[PoolFee]  # Fee tiers for V3
    input_amount: Decimal
    output_amount: Decimal
    price_impact: Decimal
    minimum_output: Decimal
    gas_estimate: int

@dataclass
class Position:
    """Liquidity position information."""
    token_id: Optional[int]  # For V3 NFT positions
    owner: str
    pool: PoolInfo
    liquidity: Decimal
    token0_amount: Decimal
    token1_amount: Decimal
    fee_tier: PoolFee
    lower_tick: Optional[int] = None  # For V3
    upper_tick: Optional[int] = None  # For V3
    unclaimed_fees: Optional[Dict[str, Decimal]] = None

@dataclass
class PositionFees:
    """Unclaimed fees for a position."""
    token0_amount: Decimal
    token1_amount: Decimal
    token0_info: TokenInfo
    token1_info: TokenInfo
    last_collected_timestamp: Optional[int] = None
