from dataclasses import dataclass
from decimal import Decimal

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

@dataclass
class MarketSummary:
    """Market summary information."""
    coin: str
    price: float
    index_price: float
    open_interest: float
    volume_24h: float
    funding_rate: float 