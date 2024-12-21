"""Market types for Hyperliquid API."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from .enums import OrderSide

@dataclass
class MarketInfo:
    """Market information."""
    coin: str
    base_currency: str
    quote_currency: str
    price_decimals: int
    size_decimals: int
    min_order_size: Decimal
    max_order_size: Decimal
    price_step: Decimal
    size_step: Decimal
    maker_fee: Decimal
    taker_fee: Decimal
    funding_rate: Decimal
    open_interest: Decimal
    mark_price: Decimal
    index_price: Decimal
    volume_24h: Decimal
    
@dataclass
class MarketSummary:
    """Market summary."""
    coin: str
    last_price: Decimal
    bid: Decimal
    ask: Decimal
    volume_24h: Decimal
    open_interest: Decimal
    funding_rate: Decimal
    
@dataclass
class OrderbookLevel:
    """Orderbook price level."""
    price: Decimal
    size: Decimal
    num_orders: int
    
@dataclass
class OrderbookResponse:
    """Orderbook response."""
    coin: str
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    timestamp: int
    
@dataclass
class TradeInfo:
    """Trade information."""
    coin: str
    id: str
    price: Decimal
    size: Decimal
    side: OrderSide
    timestamp: int
    liquidation: bool
    
@dataclass
class Market:
    """Market information."""
    name: str
    base_currency: str
    quote_currency: str
    price_decimals: int
    size_decimals: int
    min_order_size: Decimal
    max_leverage: Decimal
    price: Decimal
    index_price: Decimal
    open_interest: Decimal
    funding_rate: Decimal
    volume_24h: Decimal
    is_active: bool