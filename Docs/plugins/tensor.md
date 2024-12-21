# Tensor Plugin Documentation

## Overview

The Tensor plugin provides seamless integration with Tensor Trade, the leading NFT marketplace on Solana. It enables NFT trading, listing management, collection analytics, and real-time market data access with advanced features for optimal NFT trading strategies.

## Features

- NFT trading and listing
- Collection analytics
- Real-time market data
- Price discovery
- Listing management
- Bid management
- Floor price tracking
- Rarity analysis
- Collection statistics
- Historical data
- Market trends
- Wallet analytics
- Trait analysis
- Event monitoring
- Bulk operations

## Installation

The Tensor plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.tensor import TensorPlugin

# Initialize the plugin
plugin = TensorPlugin(
    rpc_url="https://api.mainnet-beta.solana.com",
    commitment="confirmed"
)
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Required: Solana RPC endpoint
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Required for transactions
SOLANA_PRIVATE_KEY=your_private_key

# Optional: Configuration
SOLANA_COMMITMENT=confirmed
TENSOR_API_KEY=your_tensor_api_key
```

## Market Operations

### Getting Collection Information

Get detailed collection information:

```python
from goat_sdk.plugins.tensor.parameters import CollectionParameters

params = CollectionParameters(
    collection_address="collection_address",
    include_listings=True,
    include_bids=True
)

collection = await plugin.get_collection_info(params)
```

Response structure:
```python
{
    "address": "collection_address",
    "name": "Collection Name",
    "symbol": "SYMBOL",
    "description": "Collection description",
    "image": "https://...",
    "website": "https://...",
    "twitter": "@handle",
    "discord": "discord_url",
    "stats": {
        "floor_price": Decimal("10.5"),
        "listed_count": 100,
        "volume_24h": Decimal("1000.0"),
        "volume_total": Decimal("100000.0"),
        "market_cap": Decimal("1000000.0"),
        "holder_count": 500
    },
    "listings": [
        {
            "nft_address": "nft_address",
            "seller": "seller_address",
            "price": Decimal("10.5"),
            "expiry": 1234567890
        }
    ],
    "bids": [
        {
            "bidder": "bidder_address",
            "price": Decimal("10.0"),
            "expiry": 1234567890
        }
    ]
}
```

### Getting NFT Information

Get detailed NFT information:

```python
from goat_sdk.plugins.tensor.parameters import NFTParameters

params = NFTParameters(
    nft_address="nft_address",
    include_listings=True,
    include_bids=True,
    include_history=True
)

nft = await plugin.get_nft_info(params)
```

Response structure:
```python
{
    "address": "nft_address",
    "name": "NFT Name",
    "collection": "collection_address",
    "owner": "owner_address",
    "image": "https://...",
    "attributes": [
        {
            "trait_type": "Background",
            "value": "Blue"
        }
    ],
    "rarity_rank": 123,
    "rarity_score": 0.876,
    "listings": [
        {
            "seller": "seller_address",
            "price": Decimal("10.5"),
            "expiry": 1234567890
        }
    ],
    "bids": [
        {
            "bidder": "bidder_address",
            "price": Decimal("10.0"),
            "expiry": 1234567890
        }
    ],
    "history": [
        {
            "type": "SALE",
            "price": Decimal("9.5"),
            "from": "seller_address",
            "to": "buyer_address",
            "timestamp": 1234567890
        }
    ]
}
```

### Listing NFTs

List NFTs for sale:

```python
from goat_sdk.plugins.tensor.parameters import ListingParameters
from decimal import Decimal

params = ListingParameters(
    nft_address="nft_address",
    price=Decimal("10.5"),
    expiry_seconds=86400,  # 24 hours
    taker_address=None  # Optional specific buyer
)

result = await plugin.list_nft(params)
```

### Buying NFTs

Buy listed NFTs:

```python
from goat_sdk.plugins.tensor.parameters import BuyParameters

params = BuyParameters(
    nft_address="nft_address",
    listing_address="listing_address",
    max_price=Decimal("10.5")
)

result = await plugin.buy_nft(params)
```

### Placing Bids

Place bids on NFTs:

```python
from goat_sdk.plugins.tensor.parameters import BidParameters

params = BidParameters(
    nft_address="nft_address",
    price=Decimal("10.0"),
    expiry_seconds=3600,  # 1 hour
    allow_any_mint=True  # Accept any NFT from collection
)

result = await plugin.place_bid(params)
```

### Getting Market Analytics

Get market analytics for a collection:

```python
from goat_sdk.plugins.tensor.parameters import AnalyticsParameters

params = AnalyticsParameters(
    collection_address="collection_address",
    time_range="24h",
    include_trait_floor=True
)

analytics = await plugin.get_analytics(params)
```

Response structure:
```python
{
    "volume": {
        "last_24h": Decimal("1000.0"),
        "last_7d": Decimal("5000.0"),
        "last_30d": Decimal("20000.0")
    },
    "floor_price": {
        "current": Decimal("10.5"),
        "change_24h": Decimal("0.5"),
        "change_7d": Decimal("-1.0")
    },
    "listings": {
        "count": 100,
        "total_value": Decimal("1000.0"),
        "average_price": Decimal("10.0")
    },
    "trait_floor": {
        "Background": {
            "Blue": Decimal("12.0"),
            "Red": Decimal("10.5")
        }
    },
    "holder_distribution": {
        "1": 300,
        "2-5": 150,
        "6+": 50
    }
}
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
try:
    result = await plugin.buy_nft(params)
except TensorMarketError as e:
    print(f"Market error: {e}")
except TensorPriceError as e:
    print(f"Price error: {e}")
except TensorListingError as e:
    print(f"Listing error: {e}")
except TensorAPIError as e:
    print(f"API error: {e}")
```

## Best Practices

1. **Trading Safety**
   - Verify NFT authenticity
   - Check floor prices
   - Monitor market trends
   - Use price limits

2. **Performance Optimization**
   - Cache collection data
   - Batch operations
   - Monitor rate limits
   - Handle network issues

3. **Market Analysis**
   - Track floor prices
   - Monitor volume trends
   - Analyze trait rarity
   - Study holder patterns

4. **Security**
   - Verify transactions
   - Check listing details
   - Monitor wallet activity
   - Implement proper error handling

## Examples

### Trading Strategy Example

```python
async def execute_trading_strategy():
    plugin = TensorPlugin(...)
    
    # Get collection analytics
    analytics_params = AnalyticsParameters(
        collection_address="collection_address",
        time_range="24h",
        include_trait_floor=True
    )
    
    analytics = await plugin.get_analytics(analytics_params)
    
    # Find undervalued listings
    collection_params = CollectionParameters(
        collection_address="collection_address",
        include_listings=True
    )
    
    collection = await plugin.get_collection_info(collection_params)
    
    undervalued = [
        listing for listing in collection["listings"]
        if listing["price"] < analytics["floor_price"]["current"]
    ]
    
    # Buy undervalued NFTs
    for listing in undervalued:
        buy_params = BuyParameters(
            nft_address=listing["nft_address"],
            listing_address=listing["address"],
            max_price=listing["price"]
        )
        
        try:
            result = await plugin.buy_nft(buy_params)
            print(f"Bought NFT at {listing['price']}")
        except TensorPriceError:
            print("Price changed, skipping")
    
    return {
        "analytics": analytics,
        "purchases": len(undervalued)
    }
```

### Collection Analysis Example

```python
async def analyze_collection():
    plugin = TensorPlugin(...)
    
    # Get collection info
    collection_params = CollectionParameters(
        collection_address="collection_address",
        include_listings=True,
        include_bids=True
    )
    
    collection = await plugin.get_collection_info(collection_params)
    
    # Get market analytics
    analytics_params = AnalyticsParameters(
        collection_address="collection_address",
        time_range="7d",
        include_trait_floor=True
    )
    
    analytics = await plugin.get_analytics(analytics_params)
    
    # Analyze trait distribution
    trait_distribution = {}
    for listing in collection["listings"]:
        nft_params = NFTParameters(
            nft_address=listing["nft_address"],
            include_history=True
        )
        nft = await plugin.get_nft_info(nft_params)
        
        for trait in nft["attributes"]:
            trait_type = trait["trait_type"]
            trait_value = trait["value"]
            
            if trait_type not in trait_distribution:
                trait_distribution[trait_type] = {}
            
            if trait_value not in trait_distribution[trait_type]:
                trait_distribution[trait_type][trait_value] = 0
            
            trait_distribution[trait_type][trait_value] += 1
    
    return {
        "collection": collection,
        "analytics": analytics,
        "trait_distribution": trait_distribution
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Trading Issues**
   - Verify wallet balance
   - Check listing status
   - Monitor price changes
   - Handle failed transactions

2. **Market Data Issues**
   - Verify collection address
   - Check API status
   - Monitor rate limits
   - Handle stale data

3. **Listing Issues**
   - Verify NFT ownership
   - Check listing expiry
   - Monitor floor prices
   - Handle cancellations

4. **Network Issues**
   - Use reliable RPC endpoints
   - Monitor network status
   - Handle timeouts
   - Implement proper retries

## API Reference

For complete API documentation, see:
- [Tensor Trade API Documentation](https://docs.tensor.trade/)