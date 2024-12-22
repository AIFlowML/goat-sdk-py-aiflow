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
     
     Path: goat_sdk/plugins/hyperliquid/utils.py
"""

"""Order types for Hyperliquid API."""

from enum import Enum
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class OrderSide(str, Enum):
    """Order side."""
    BUY = "B"
    SELL = "S"

class OrderType(str, Enum):
    """Order type."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    POST_ONLY = "POST_ONLY"
    IOC = "IOC"
    FOK = "FOK"

class OrderStatus(str, Enum):
    """Order status."""
    NEW = "NEW"
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"

class OrderRequest(BaseModel):
    """Order request."""
    coin: str
    side: OrderSide
    type: OrderType
    size: Decimal
    price: Optional[Decimal] = None
    reduce_only: bool = False
    post_only: bool = False
    client_id: Optional[str] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class OrderResponse(BaseModel):
    """Order response."""
    id: str
    client_id: Optional[str] = None
    coin: str
    size: Optional[Decimal] = None
    price: Optional[Decimal] = None
    side: Optional[OrderSide] = None
    type: Optional[OrderType] = None
    status: OrderStatus
    filled_size: Optional[Decimal] = None
    remaining_size: Optional[Decimal] = None
    average_fill_price: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    created_at: int
    updated_at: Optional[int] = None
    reduce_only: bool = False
    post_only: bool = False
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class OrderResult(BaseModel):
    """Order result."""
    success: bool
    order: Optional[OrderResponse] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(frozen=True, extra="forbid") 