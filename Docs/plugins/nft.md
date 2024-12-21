# NFT Plugin Documentation

## Overview

The NFT plugin provides a comprehensive interface for interacting with NFTs (Non-Fungible Tokens) across multiple blockchain networks. It supports both ERC-721 and ERC-1155 standards, offering features for minting, trading, querying, and managing NFT collections.

## Features

- Support for ERC-721 and ERC-1155 standards
- Multi-chain compatibility
- NFT minting and burning
- Collection management
- Metadata handling
- Ownership verification
- Transfer operations
- Batch operations
- Royalty management
- Event monitoring
- IPFS integration
- Marketplace integration

## Installation

The NFT plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.nft import NFTPlugin, NFTStandard

# Initialize for ERC-721
plugin = NFTPlugin(
    standard=NFTStandard.ERC721,
    contract_address="0x...",
    chain_id=1  # Ethereum Mainnet
)

# Initialize for ERC-1155
plugin = NFTPlugin(
    standard=NFTStandard.ERC1155,
    contract_address="0x...",
    chain_id=1
)
```

### Environment Variables

The following environment variables can be used to configure the plugin:

```bash
# Required: RPC endpoint for the target chain
ETH_RPC_URL=https://mainnet.infura.io/v3/your-project-id
POLYGON_RPC_URL=https://polygon-rpc.com
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc

# Required for transactions
PRIVATE_KEY=your_private_key

# Optional: IPFS configuration
IPFS_GATEWAY=https://ipfs.io/ipfs/
IPFS_API_KEY=your_ipfs_api_key

# Optional: Gas settings
GAS_PRICE_MULTIPLIER=1.1
MAX_GAS_PRICE=100  # in gwei
```

## NFT Operations

### Minting NFTs

Mint new NFTs with metadata:

```python
from goat_sdk.plugins.nft.parameters import MintParameters
from decimal import Decimal

params = MintParameters(
    recipient="0x...",  # Recipient address
    token_id=1,  # Optional for auto-increment
    uri="ipfs://...",  # Metadata URI
    amount=1,  # Required for ERC-1155
    royalty_percentage=Decimal("2.5"),  # Optional
    data=b"",  # Optional data for hooks
)

tx_hash = await plugin.mint_nft(params)
```

### Transferring NFTs

Transfer NFTs between addresses:

```python
from goat_sdk.plugins.nft.parameters import TransferParameters

params = TransferParameters(
    from_address="0x...",
    to_address="0x...",
    token_id=1,
    amount=1,  # Required for ERC-1155
    data=b"",  # Optional data for hooks
)

tx_hash = await plugin.transfer_nft(params)
```

### Burning NFTs

Burn NFTs:

```python
from goat_sdk.plugins.nft.parameters import BurnParameters

params = BurnParameters(
    token_id=1,
    amount=1,  # Required for ERC-1155
    from_address="0x..."  # Optional, defaults to owner
)

tx_hash = await plugin.burn_nft(params)
```

### Getting NFT Information

Get detailed NFT information:

```python
nft_info = await plugin.get_nft_info(token_id=1)
```

Response structure:
```python
{
    "token_id": 1,
    "owner": "0x...",
    "uri": "ipfs://...",
    "metadata": {
        "name": "NFT Name",
        "description": "NFT Description",
        "image": "ipfs://...",
        "attributes": [
            {
                "trait_type": "Color",
                "value": "Blue"
            }
        ]
    },
    "royalty_info": {
        "recipient": "0x...",
        "percentage": Decimal("2.5")
    },
    "total_supply": 1,  # For ERC-1155
    "approved": {
        "operator": "0x...",
        "approved": True
    }
}
```

### Getting Collection Information

Get information about the NFT collection:

```python
collection_info = await plugin.get_collection_info()
```

Response structure:
```python
{
    "name": "Collection Name",
    "symbol": "SYMBOL",
    "total_supply": 1000,
    "owner": "0x...",
    "base_uri": "ipfs://...",
    "contract_uri": "ipfs://...",
    "supported_interfaces": [
        "IERC721",
        "IERC721Metadata",
        "IERC721Enumerable"
    ],
    "royalty_info": {
        "recipient": "0x...",
        "percentage": Decimal("2.5")
    }
}
```

### Approving Operators

Approve operators for NFT management:

```python
from goat_sdk.plugins.nft.parameters import ApprovalParameters

params = ApprovalParameters(
    operator="0x...",
    approved=True,
    token_id=1  # Optional for ERC-721
)

tx_hash = await plugin.set_approval(params)
```

### Batch Operations

Perform batch operations for ERC-1155:

```python
from goat_sdk.plugins.nft.parameters import BatchTransferParameters

params = BatchTransferParameters(
    from_address="0x...",
    to_address="0x...",
    token_ids=[1, 2, 3],
    amounts=[1, 1, 1],
    data=b""  # Optional data for hooks
)

tx_hash = await plugin.batch_transfer(params)
```

## Metadata Management

### Setting Token URI

Set or update token URI:

```python
from goat_sdk.plugins.nft.parameters import URIParameters

params = URIParameters(
    token_id=1,
    uri="ipfs://..."
)

tx_hash = await plugin.set_token_uri(params)
```

### IPFS Integration

Upload metadata to IPFS:

```python
from goat_sdk.plugins.nft.parameters import IPFSParameters

params = IPFSParameters(
    metadata={
        "name": "NFT Name",
        "description": "NFT Description",
        "image": image_data,  # bytes or file path
        "attributes": [
            {
                "trait_type": "Color",
                "value": "Blue"
            }
        ]
    }
)

uri = await plugin.upload_to_ipfs(params)
```

## Event Monitoring

### Listening for Events

Monitor NFT events:

```python
from goat_sdk.plugins.nft.parameters import EventParameters

params = EventParameters(
    event_types=["Transfer", "Approval"],
    from_block="latest",
    to_block="latest",
    token_id=1  # Optional filter
)

async for event in plugin.listen_for_events(params):
    print(f"Event: {event}")
```

Event structure:
```python
{
    "event_type": "Transfer",
    "transaction_hash": "0x...",
    "block_number": 12345678,
    "from_address": "0x...",
    "to_address": "0x...",
    "token_id": 1,
    "amount": 1,  # For ERC-1155
    "data": b""  # Optional data
}
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
try:
    result = await plugin.mint_nft(params)
except NFTContractError as e:
    print(f"Contract error: {e}")
except NFTValidationError as e:
    print(f"Validation error: {e}")
except NFTMetadataError as e:
    print(f"Metadata error: {e}")
except NFTIPFSError as e:
    print(f"IPFS error: {e}")
```

## Best Practices

1. **Metadata Management**
   - Use IPFS for decentralized storage
   - Include comprehensive metadata
   - Follow metadata standards
   - Validate URIs before minting

2. **Gas Optimization**
   - Use batch operations when possible
   - Monitor gas prices
   - Implement proper retry logic
   - Consider transaction timing

3. **Security**
   - Verify ownership before operations
   - Implement proper access control
   - Monitor for suspicious activity
   - Handle approvals carefully

4. **Error Handling**
   - Implement proper error recovery
   - Validate inputs thoroughly
   - Monitor transaction status
   - Handle network issues

## Examples

### Complete Minting Example

```python
async def mint_nft_with_metadata():
    plugin = NFTPlugin(...)
    
    # Upload metadata to IPFS
    ipfs_params = IPFSParameters(
        metadata={
            "name": "Unique NFT",
            "description": "A unique digital asset",
            "image": "path/to/image.png",
            "attributes": [
                {
                    "trait_type": "Rarity",
                    "value": "Legendary"
                }
            ]
        }
    )
    
    uri = await plugin.upload_to_ipfs(ipfs_params)
    
    # Mint NFT
    mint_params = MintParameters(
        recipient="0x...",
        uri=uri,
        royalty_percentage=Decimal("2.5")
    )
    
    tx_hash = await plugin.mint_nft(mint_params)
    
    # Get NFT info
    nft_info = await plugin.get_nft_info(token_id=1)
    
    return {
        "transaction": tx_hash,
        "token_id": 1,
        "uri": uri,
        "info": nft_info
    }
```

### Collection Management Example

```python
async def manage_collection():
    plugin = NFTPlugin(...)
    
    # Get collection info
    collection = await plugin.get_collection_info()
    
    # Set approval for marketplace
    approval_params = ApprovalParameters(
        operator="0x...",  # Marketplace address
        approved=True
    )
    
    approval_tx = await plugin.set_approval(approval_params)
    
    # Transfer multiple NFTs
    batch_params = BatchTransferParameters(
        from_address="0x...",
        to_address="0x...",
        token_ids=[1, 2, 3],
        amounts=[1, 1, 1]
    )
    
    transfer_tx = await plugin.batch_transfer(batch_params)
    
    return {
        "collection": collection,
        "approval_tx": approval_tx,
        "transfer_tx": transfer_tx
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Minting Issues**
   - Verify contract ownership
   - Check gas settings
   - Validate metadata format
   - Handle IPFS upload errors

2. **Transfer Issues**
   - Verify token ownership
   - Check approvals
   - Monitor gas costs
   - Handle failed transactions

3. **Metadata Issues**
   - Verify IPFS connectivity
   - Check URI format
   - Validate metadata schema
   - Handle gateway timeouts

4. **Contract Issues**
   - Verify contract deployment
   - Check interface support
   - Monitor network status
   - Handle contract errors

## API Reference

For complete API documentation, see:
- [ERC-721 Standard](https://eips.ethereum.org/EIPS/eip-721)
- [ERC-1155 Standard](https://eips.ethereum.org/EIPS/eip-1155)
- [OpenSea Metadata Standards](https://docs.opensea.io/docs/metadata-standards)
- [IPFS Documentation](https://docs.ipfs.io/) 