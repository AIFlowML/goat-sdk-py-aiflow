# API Reference

## Core SDK

### GoatSDK

The main SDK class that provides the foundation for all blockchain interactions.

```python
class GoatSDK:
    def __init__(
        self,
        private_key: Optional[str] = None,
        mnemonic: Optional[str] = None,
        wallet: Optional[WalletBase] = None,
        network: Network = Network.MAINNET,
        chain: Chain = Chain.SOLANA,
        rpc_url: Optional[str] = None,
        options: Optional[dict] = None
    ):
        """Initialize the SDK.
        
        Args:
            private_key: Wallet private key
            mnemonic: Wallet mnemonic phrase
            wallet: Custom wallet implementation
            network: Network to connect to
            chain: Blockchain to use
            rpc_url: Custom RPC endpoint
            options: Additional configuration options
        """
```

#### Methods

1. **get_tools**
   ```python
   def get_tools(
       self,
       plugins: List[Type[Plugin]]
   ) -> List[Tool]:
       """Get tools from plugins for AI integration.
       
       Args:
           plugins: List of plugin classes to initialize
           
       Returns:
           List[Tool]: List of tools ready for AI framework integration
       """
   ```

2. **sign_transaction**
   ```python
   async def sign_transaction(
       self,
       transaction: Transaction
   ) -> SignedTransaction:
       """Sign a transaction.
       
       Args:
           transaction: Transaction to sign
           
       Returns:
           SignedTransaction: The signed transaction
           
       Raises:
           WalletError: If signing fails
       """
   ```

## Core Types

### Network

```python
from enum import Enum

class Network(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"
    LOCAL = "local"
```

### Chain

```python
class Chain(str, Enum):
    SOLANA = "solana"
    MODE = "mode"
    ETHEREUM = "ethereum"
```

### ModeConfig

```python
from pydantic import BaseModel

class ModeConfig(BaseModel):
    """Configuration for operation modes."""
    
    retry_count: int = 3
    timeout: int = 30
    commitment: str = "confirmed"
    skip_preflight: bool = False
```

## Plugin Base Classes

### Plugin

```python
class Plugin:
    def __init__(
        self,
        sdk: GoatSDK,
        chain: Chain,
        options: Optional[dict] = None
    ):
        """Initialize a plugin.
        
        Args:
            sdk: SDK instance
            chain: Blockchain this plugin works with
            options: Plugin-specific options
        """
```

### Tool

```python
class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Type[BaseModel]
    ):
        """Initialize a tool.
        
        Args:
            name: Tool name
            description: Tool description
            function: Async function to execute
            parameters: Pydantic model for parameters
        """
```

## Exceptions

### Base Exceptions

```python
class GoatSDKError(Exception):
    """Base exception for all SDK errors."""
    pass

class NetworkError(GoatSDKError):
    """Network-related errors."""
    pass

class WalletError(GoatSDKError):
    """Wallet-related errors."""
    pass
```

### Token Exceptions

```python
class TokenError(GoatSDKError):
    """Base exception for token operations."""
    pass

class InsufficientBalanceError(TokenError):
    def __init__(self, required: int, available: int, token_symbol: str):
        self.required = required
        self.available = available
        self.token_symbol = token_symbol
        super().__init__(
            f"Insufficient balance for transfer of {token_symbol}. "
            f"Required: {required}, Available: {available}"
        )

class TokenAccountNotFoundError(TokenError):
    def __init__(self, account_type: str, address: str):
        self.account_type = account_type
        self.address = address
        super().__init__(
            f"{account_type} token account not found for address: {address}"
        )
```

### NFT Exceptions

```python
class NFTError(GoatSDKError):
    """Base exception for NFT operations."""
    pass

class NFTNotFoundError(NFTError):
    def __init__(self, mint_address: str):
        self.mint_address = mint_address
        super().__init__(f"NFT not found: {mint_address}")

class MetadataError(NFTError):
    def __init__(self, mint_address: str, reason: str):
        self.mint_address = mint_address
        self.reason = reason
        super().__init__(
            f"Metadata error for NFT {mint_address}: {reason}"
        )
```

## Framework Adapters

### LangChain Adapter

```python
class LangchainAdapter:
    @staticmethod
    def create_tools(
        tools: List[Tool]
    ) -> List[LangchainTool]:
        """Convert SDK tools to Langchain tools.
        
        Args:
            tools: List of SDK tools
            
        Returns:
            List[LangchainTool]: Tools ready for Langchain use
        """
```

### LlamaIndex Adapter

```python
class LlamaIndexAdapter:
    @staticmethod
    def create_tools(
        tools: List[Tool]
    ) -> List[LlamaIndexTool]:
        """Convert SDK tools to LlamaIndex tools.
        
        Args:
            tools: List of SDK tools
            
        Returns:
            List[LlamaIndexTool]: Tools ready for LlamaIndex use
        """
```

## Utility Functions

### Conversion Utilities

```python
def to_base_units(
    amount: float,
    decimals: int
) -> int:
    """Convert decimal amount to base units.
    
    Args:
        amount: Amount in decimal format
        decimals: Token decimals
        
    Returns:
        int: Amount in base units
    """

def from_base_units(
    amount: int,
    decimals: int
) -> float:
    """Convert base units to decimal amount.
    
    Args:
        amount: Amount in base units
        decimals: Token decimals
        
    Returns:
        float: Amount in decimal format
    """
```

### Network Utilities

```python
async def get_network_time(
    connection: Connection
) -> int:
    """Get current network time.
    
    Args:
        connection: Network connection
        
    Returns:
        int: Current network timestamp
    """

async def wait_for_confirmation(
    connection: Connection,
    signature: str,
    timeout: int = 30
) -> bool:
    """Wait for transaction confirmation.
    
    Args:
        connection: Network connection
        signature: Transaction signature
        timeout: Maximum wait time in seconds
        
    Returns:
        bool: True if confirmed, False if timed out
        
    Raises:
        NetworkError: If transaction failed
    """
```

## Next Steps

- See [Plugin Guide](./plugin-guide.md) for plugin-specific APIs
- Check [Examples](../examples/) for usage examples
- Learn about [AI Integration](./ai-integration.md)
