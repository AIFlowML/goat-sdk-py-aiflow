"""Order types for Hyperliquid API."""

from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class OrderType(str, Enum):
    """Order types supported by Hyperliquid."""
    LIMIT = "Limit"
    MARKET = "Market"
    STOP_LIMIT = "StopLimit"
    STOP_MARKET = "StopMarket"
    TAKE_PROFIT = "TakeProfit"
    TAKE_PROFIT_MARKET = "TakeProfitMarket"

class OrderSide(str, Enum):
    """Order side."""
    BUY = "Buy"
    SELL = "Sell"

class OrderStatus(str, Enum):
    """Order status."""
    OPEN = "Open"
    FILLED = "Filled"
    PARTIALLY_FILLED = "PartiallyFilled"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"
    REJECTED = "Rejected"

class OrderRequest(BaseModel):
    """Order request parameters."""
    coin: str
    size: float
    price: Optional[float] = None
    side: OrderSide
    type: OrderType
    reduce_only: bool = False
    post_only: bool = False
    client_id: Optional[str] = None
    trigger_price: Optional[float] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class OrderResponse(BaseModel):
    """Order response from API."""
    order_id: str
    client_id: Optional[str]
    coin: str
    size: float
    price: float
    side: OrderSide
    type: OrderType
    status: OrderStatus
    filled_size: float = 0
    remaining_size: float
    average_fill_price: Optional[float] = None
    fee: float = 0
    created_at: int
    updated_at: int
    reduce_only: bool
    post_only: bool
    trigger_price: Optional[float] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class OrderResult(BaseModel):
    """Result of an order operation."""
    success: bool
    order: Optional[OrderResponse] = None
    error: Optional[str] = None
    error_code: Optional[int] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid") 