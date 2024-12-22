# SPL Token Plugin Documentation

## Overview

The SPL Token plugin provides comprehensive integration with the Solana Program Library (SPL) Token program. It enables creation, management, and interaction with SPL tokens on the Solana blockchain, supporting both fungible and non-fungible tokens with advanced features for token operations and account management.

## Features

- Token creation and minting
- Account management
- Token transfers
- Freezing and thawing accounts
- Burning tokens
- Multisig authority
- Account closing
- Token metadata
- Associated token accounts
- Wrapped SOL operations
- Batch operations
- Account rent management
- Authority delegation
- Token program upgrades

## Installation

The SPL Token plugin is included in the GOAT SDK by default. No additional installation is required.

## Configuration

### Plugin Initialization

```python
from goat_sdk import Plugin
from goat_sdk.plugins.spl_token import SPLTokenPlugin

# Initialize the plugin
plugin = SPLTokenPlugin(
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
SPL_TOKEN_PROGRAM_ID=TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
```

## Token Operations

### Creating a Token

Create a new SPL token:

```python
from goat_sdk.plugins.spl_token.parameters import CreateTokenParameters
from decimal import Decimal

params = CreateTokenParameters(
    name="My Token",
    symbol="MTK",
    decimals=9,
    initial_supply=Decimal("1000000.0"),
    uri="https://example.com/token-metadata.json",
    is_mutable=True,
    freeze_authority=None  # Optional
)

result = await plugin.create_token(params)
```

Response structure:
```python
{
    "mint": "mint_address",
    "metadata": "metadata_address",
    "token_account": "token_account_address",
    "signature": "transaction_signature",
    "decimals": 9,
    "supply": Decimal("1000000.0")
}
```

### Minting Tokens

Mint additional tokens:

```python
from goat_sdk.plugins.spl_token.parameters import MintParameters

params = MintParameters(
    mint="mint_address",
    recipient="recipient_address",
    amount=Decimal("1000.0"),
    multisig=None  # Optional multisig authority
)

result = await plugin.mint_tokens(params)
```

### Transferring Tokens

Transfer tokens between accounts:

```python
from goat_sdk.plugins.spl_token.parameters import TransferParameters

params = TransferParameters(
    source="source_address",
    destination="destination_address",
    amount=Decimal("100.0"),
    mint="mint_address",
    create_associated_token_account=True,
    fund_recipient=True
)

result = await plugin.transfer_tokens(params)
```

### Burning Tokens

Burn tokens from an account:

```python
from goat_sdk.plugins.spl_token.parameters import BurnParameters

params = BurnParameters(
    account="token_account_address",
    mint="mint_address",
    amount=Decimal("50.0"),
    close_account=True  # Optional: close account after burning
)

result = await plugin.burn_tokens(params)
```

### Getting Account Information

Get token account information:

```python
account_info = await plugin.get_account_info("token_account_address")
```

Response structure:
```python
{
    "address": "token_account_address",
    "mint": "mint_address",
    "owner": "owner_address",
    "amount": Decimal("100.0"),
    "delegate": None,
    "delegated_amount": Decimal("0.0"),
    "is_initialized": True,
    "is_frozen": False,
    "is_native": False,
    "rent_exempt_reserve": None,
    "close_authority": None
}
```

### Getting Token Information

Get token mint information:

```python
token_info = await plugin.get_token_info("mint_address")
```

Response structure:
```python
{
    "address": "mint_address",
    "supply": Decimal("1000000.0"),
    "decimals": 9,
    "is_initialized": True,
    "freeze_authority": None,
    "mint_authority": "authority_address",
    "metadata": {
        "name": "My Token",
        "symbol": "MTK",
        "uri": "https://example.com/token-metadata.json",
        "is_mutable": True
    }
}
```

## Account Management

### Creating Token Accounts

Create a new token account:

```python
from goat_sdk.plugins.spl_token.parameters import CreateAccountParameters

params = CreateAccountParameters(
    mint="mint_address",
    owner="owner_address",
    is_associated=True,  # Use associated token account
    payer=None  # Optional custom payer
)

result = await plugin.create_account(params)
```

### Freezing Accounts

Freeze a token account:

```python
from goat_sdk.plugins.spl_token.parameters import FreezeParameters

params = FreezeParameters(
    account="token_account_address",
    mint="mint_address",
    authority="freeze_authority_address"
)

result = await plugin.freeze_account(params)
```

### Thawing Accounts

Thaw a frozen token account:

```python
from goat_sdk.plugins.spl_token.parameters import ThawParameters

params = ThawParameters(
    account="token_account_address",
    mint="mint_address",
    authority="freeze_authority_address"
)

result = await plugin.thaw_account(params)
```

### Closing Accounts

Close a token account:

```python
from goat_sdk.plugins.spl_token.parameters import CloseParameters

params = CloseParameters(
    account="token_account_address",
    destination="sol_destination_address",
    authority="owner_address"
)

result = await plugin.close_account(params)
```

## Authority Management

### Setting Authorities

Update token authorities:

```python
from goat_sdk.plugins.spl_token.parameters import SetAuthorityParameters
from goat_sdk.plugins.spl_token.types import AuthorityType

params = SetAuthorityParameters(
    mint="mint_address",
    current_authority="current_authority_address",
    new_authority="new_authority_address",
    authority_type=AuthorityType.MINT_TOKENS
)

result = await plugin.set_authority(params)
```

### Approving Delegation

Approve token delegation:

```python
from goat_sdk.plugins.spl_token.parameters import ApproveParameters

params = ApproveParameters(
    account="token_account_address",
    delegate="delegate_address",
    amount=Decimal("100.0"),
    owner=None  # Optional custom owner
)

result = await plugin.approve(params)
```

## Error Handling

The plugin uses custom exceptions for different error scenarios:

```python
try:
    result = await plugin.transfer_tokens(params)
except SPLTokenError as e:
    print(f"Token error: {e}")
except SPLAccountError as e:
    print(f"Account error: {e}")
except SPLAuthorityError as e:
    print(f"Authority error: {e}")
except SPLProgramError as e:
    print(f"Program error: {e}")
```

## Best Practices

1. **Account Management**
   - Use associated token accounts
   - Properly handle rent-exempt reserve
   - Close unused accounts
   - Monitor account balances

2. **Transaction Safety**
   - Verify token addresses
   - Check account ownership
   - Handle authority changes carefully
   - Implement proper error handling

3. **Performance Optimization**
   - Batch operations when possible
   - Reuse accounts when appropriate
   - Monitor network conditions
   - Handle rate limits

4. **Security**
   - Secure private keys
   - Verify program IDs
   - Monitor for suspicious activity
   - Implement proper access control

## Examples

### Token Creation and Distribution Example

```python
async def create_and_distribute_token():
    plugin = SPLTokenPlugin(...)
    
    # Create new token
    create_params = CreateTokenParameters(
        name="My Token",
        symbol="MTK",
        decimals=9,
        initial_supply=Decimal("1000000.0"),
        uri="https://example.com/token-metadata.json"
    )
    
    token = await plugin.create_token(create_params)
    
    # Distribute tokens to multiple recipients
    recipients = ["addr1", "addr2", "addr3"]
    amount_each = Decimal("1000.0")
    
    for recipient in recipients:
        transfer_params = TransferParameters(
            source=token["token_account"],
            destination=recipient,
            amount=amount_each,
            mint=token["mint"],
            create_associated_token_account=True
        )
        
        await plugin.transfer_tokens(transfer_params)
    
    return {
        "token": token,
        "distributions": len(recipients)
    }
```

### Account Management Example

```python
async def manage_token_accounts():
    plugin = SPLTokenPlugin(...)
    
    # Create token account
    create_params = CreateAccountParameters(
        mint="mint_address",
        owner="owner_address",
        is_associated=True
    )
    
    account = await plugin.create_account(create_params)
    
    # Approve delegation
    approve_params = ApproveParameters(
        account=account["address"],
        delegate="delegate_address",
        amount=Decimal("100.0")
    )
    
    delegation = await plugin.approve(approve_params)
    
    # Freeze account
    freeze_params = FreezeParameters(
        account=account["address"],
        mint="mint_address",
        authority="freeze_authority_address"
    )
    
    freeze = await plugin.freeze_account(freeze_params)
    
    return {
        "account": account,
        "delegation": delegation,
        "freeze": freeze
    }
```

## Support

For issues and feature requests, please:
1. Check the [troubleshooting guide](#troubleshooting)
2. Open an issue on the GitHub repository
3. Contact the development team

## Troubleshooting

Common issues and solutions:

1. **Account Issues**
   - Verify account existence
   - Check rent-exempt status
   - Monitor account balances
   - Handle account initialization

2. **Transaction Issues**
   - Verify authority permissions
   - Check token balances
   - Monitor network status
   - Handle failed transactions

3. **Authority Issues**
   - Verify authority ownership
   - Check delegation status
   - Monitor authority changes
   - Handle multisig operations

4. **Program Issues**
   - Verify program IDs
   - Check instruction data
   - Monitor program upgrades
   - Handle version compatibility

## API Reference

For complete API documentation, see:
- [SPL Token Program Documentation](https://spl.solana.com/token)
- [Solana Program Library Documentation](https://docs.solana.com/developing/runtime-facilities/programs#bpf-loader) 