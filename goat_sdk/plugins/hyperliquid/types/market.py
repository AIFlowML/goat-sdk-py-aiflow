
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
"""Market data types for Hyperliquid API."""

from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from .order import OrderSide

class MarketInfo(BaseModel):
    """Market information."""
    coin: str
    price: Decimal
    index_price: Decimal = Field(alias="indexPrice")
    mark_price: Decimal = Field(alias="markPrice")
    open_interest: Decimal = Field(alias="openInterest", default=Decimal("0"))
    funding_rate: Decimal = Field(alias="fundingRate", default=Decimal("0"))
    volume_24h: Decimal = Field(alias="volume24h", default=Decimal("0"))
    size_decimals: int = Field(alias="sizeDecimals")
    
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

class MarketSummary(BaseModel):
    """Market summary information."""
    coin: str
    price: Decimal = Field(alias="markPx")
    index_price: Decimal = Field(alias="oraclePx")
    mark_price: Decimal = Field(alias="markPx")
    volume_24h: Decimal = Field(alias="dayNtlVlm", default=Decimal("0"))
    open_interest: Decimal = Field(alias="openInterest", default=Decimal("0"))
    funding_rate: Decimal = Field(alias="funding", default=Decimal("0"))
    
    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

class OrderbookLevel(BaseModel):
    """Single level in orderbook."""
    price: Decimal
    size: Decimal
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class OrderbookResponse(BaseModel):
    """Orderbook response."""
    coin: str
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    
    model_config = ConfigDict(frozen=True, extra="forbid")

class TradeInfo(BaseModel):
    """Trade information."""
    coin: str
    id: str
    price: Decimal
    size: Decimal
    side: OrderSide
    timestamp: int
    
    model_config = ConfigDict(frozen=True, extra="forbid")