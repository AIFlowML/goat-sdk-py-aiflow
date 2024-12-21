# API Reference

## Core SDK

### GoatSDK

The main SDK class that provides the foundation for all plugin interactions.

```python
class GoatSDK:
    def __init__(
        private_key: str,
        provider_url: str,
        network: Optional[str] = None
    )
```

#### Parameters

- `private_key`: The private key for signing transactions
- `provider_url`: The URL of the network provider
- `network`: Optional network identifier

## Plugins

### ERC20Plugin

Plugin for interacting with ERC20 tokens on the Mode network.

#### Methods

##### `deploy_token`
```python
async def deploy_token(params: DeployTokenParams) -> TokenDeploymentResult
```

Deploy a new ERC20 token.

**Parameters:**
- `name`: Token name
- `symbol`: Token symbol
- `initial_supply`: Initial token supply in base units

**Returns:**
- `contract_address`: Deployed contract address
- `transaction_hash`: Deployment transaction hash
- `explorer_url`: URL to view the transaction

##### `transfer`
```python
async def transfer(params: TransferParams) -> TransactionResult
```

Transfer tokens to another address.

**Parameters:**
- `token_address`: Token contract address
- `to_address`: Recipient address
- `amount`: Amount to transfer in base units

**Returns:**
- `transaction_hash`: Transfer transaction hash
- `explorer_url`: URL to view the transaction

##### `approve`
```python
async def approve(params: ApproveParams) -> TransactionResult
```

Approve token spending.

**Parameters:**
- `token_address`: Token contract address
- `spender_address`: Address to approve
- `amount`: Amount to approve in base units

**Returns:**
- `transaction_hash`: Approval transaction hash
- `explorer_url`: URL to view the transaction

### SplTokenPlugin

Plugin for interacting with SPL tokens on Solana.

#### Methods

##### `mint_token`
```python
async def mint_token(params: MintTokenParams) -> MintResult
```

Mint new tokens.

**Parameters:**
- `amount`: Amount to mint
- `recipient`: Recipient address

**Returns:**
- `signature`: Transaction signature
- `explorer_url`: URL to view the transaction

## Types

### Chain
```python
class Chain:
    type: str  # "evm" or "solana"
    chain_id: Optional[int]  # For EVM chains
```

### TokenDeploymentResult
```python
class TokenDeploymentResult:
    contract_address: str
    transaction_hash: str
    explorer_url: str
```

### TransactionResult
```python
class TransactionResult:
    transaction_hash: str
    explorer_url: str
```

## Error Handling

### GoatSDKError
Base class for all SDK errors.

### NetworkError
Raised when there are network-related issues.

### ValidationError
Raised when input validation fails.

### TransactionError
Raised when a transaction fails.

## Utilities

### convert_to_base_unit
```python
def convert_to_base_unit(amount: float, decimals: int) -> int
```

Convert from decimal to base units.

### convert_from_base_unit
```python
def convert_from_base_unit(amount: int, decimals: int) -> float
```

Convert from base to decimal units.
