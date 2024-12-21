"""Account types for Hyperliquid API."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class MarginInfo(BaseModel):
    """Margin information for an account."""
    initial_margin: float
    maintenance_margin: float
    margin_ratio: float
    liquidation_price: Optional[float] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class LeverageInfo(BaseModel):
    """Leverage information for a position."""
    current: float
    max: float
    used: float
    available: float
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class AccountPosition(BaseModel):
    """Position information for a specific market."""
    coin: str
    size: float
    entry_price: float
    mark_price: float
    liquidation_price: Optional[float] = None
    unrealized_pnl: float
    realized_pnl: float
    margin_used: float
    leverage: float
    side: str  # "Long" or "Short"
    last_updated_timestamp: int
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class AccountInfo(BaseModel):
    """Complete account information."""
    address: str
    equity: float
    free_collateral: float
    total_collateral: float
    margin_ratio: float
    maintenance_margin: float
    initial_margin: float
    unrealized_pnl: float
    realized_pnl: float
    positions: List[AccountPosition]
    margin_info: MarginInfo
    leverage_info: LeverageInfo
    last_updated_timestamp: int
    
    model_config = ConfigDict(frozen=True, extra="forbid") 