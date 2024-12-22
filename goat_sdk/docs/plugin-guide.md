# Plugin Guide

## Available Plugins

### SPL Token Plugin

The SPL Token Plugin provides functionality for interacting with SPL tokens on Solana and Mode networks.

```python
from goat_sdk.plugins.spl_token import SplTokenPlugin

# Initialize plugin
spl_plugin = SplTokenPlugin(sdk, chain=Chain.SOLANA)

# Get token balance
balance = await spl_plugin.get_token_balance(
    mint_address="...",
    owner_address="..."
)

# Transfer tokens
result = await spl_plugin.transfer_token(
    mint_address="...",
    from_address="...",
    to_address="...",
    amount=1000000  # in base units
)
```

#### Features

- Token balance queries
- Token transfers
- Account existence checks
- Token metadata retrieval
- Base unit conversion utilities

#### Configuration

```python
from goat_sdk.plugins.spl_token.types import SplTokenConfig

config = SplTokenConfig(
    commitment="confirmed",
    skip_preflight=False,
    retry_count=3
)

spl_plugin = SplTokenPlugin(sdk, chain=Chain.SOLANA, options=config)
```

### Solana NFT Plugin

The Solana NFT Plugin enables interaction with NFTs on the Solana blockchain.

```python
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin

# Initialize plugin
nft_plugin = SolanaNFTPlugin(sdk)

# Get NFT metadata
metadata = await nft_plugin.get_nft_metadata(
    mint_address="..."
)

# Transfer NFT
result = await nft_plugin.transfer_nft(
    mint_address="...",
    from_address="...",
    to_address="..."
)
```

#### Features

- NFT metadata retrieval
- NFT transfers
- Collection queries
- Ownership verification
- Metadata updates

#### Configuration

```python
from goat_sdk.plugins.solana_nft.types import NFTConfig

config = NFTConfig(
    metadata_program="...",  # Optional custom metadata program
    retry_count=3
)

nft_plugin = SolanaNFTPlugin(sdk, options=config)
```

## Plugin Development Guide

### Creating a New Plugin

1. Create a new directory under `goat_sdk/plugins/`
2. Implement the base Plugin class:

```python
from goat_sdk.core.plugin import Plugin
from goat_sdk.core.types import Chain

class MyPlugin(Plugin):
    def __init__(
        self,
        sdk: GoatSDK,
        chain: Chain = Chain.SOLANA,
        options: Optional[dict] = None
    ):
        super().__init__(sdk, chain, options)
        self.initialize()
    
    def initialize(self):
        # Setup plugin-specific resources
        pass
    
    async def cleanup(self):
        # Cleanup resources
        pass
```

3. Define plugin-specific types:

```python
from pydantic import BaseModel

class MyPluginConfig(BaseModel):
    retry_count: int = 3
    custom_option: str = "default"

class OperationParams(BaseModel):
    param1: str
    param2: int
```

4. Implement plugin methods:

```python
class MyPlugin(Plugin):
    async def my_operation(
        self,
        params: OperationParams
    ) -> OperationResult:
        # Validate parameters
        # Perform operation
        # Return results
        pass
```

### Adding AI Tools

1. Define tool parameters:

```python
class MyToolParams(BaseModel):
    param1: str = Field(..., description="First parameter")
    param2: int = Field(..., description="Second parameter")
```

2. Create tool function:

```python
async def my_tool_function(
    self,
    params: MyToolParams
) -> dict:
    result = await self.my_operation(params)
    return {"status": "success", "data": result}
```

3. Register tool:

```python
def get_tools(self) -> List[Tool]:
    return [
        Tool(
            name="my_tool",
            description="Performs my operation",
            function=self.my_tool_function,
            parameters=MyToolParams
        )
    ]
```

### Error Handling

1. Define plugin-specific exceptions:

```python
class MyPluginError(GoatSDKError):
    """Base exception for plugin errors."""
    pass

class OperationFailedError(MyPluginError):
    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"Operation {operation} failed: {reason}"
        )
```

2. Use error handling in methods:

```python
async def my_operation(self, params: OperationParams):
    try:
        # Attempt operation
        pass
    except NetworkError as e:
        raise MyPluginError(f"Network error: {str(e)}")
    except Exception as e:
        raise OperationFailedError(
            "my_operation",
            str(e)
        )
```

### Testing

1. Create test fixtures:

```python
@pytest.fixture
def my_plugin(sdk):
    return MyPlugin(sdk)

@pytest.fixture
def mock_connection(mocker):
    return mocker.patch("goat_sdk.core.connection.Connection")
```

2. Write test cases:

```python
async def test_my_operation(my_plugin, mock_connection):
    params = OperationParams(param1="test", param2=123)
    
    mock_connection.send.return_value = {
        "result": "success"
    }
    
    result = await my_plugin.my_operation(params)
    assert result.status == "success"
```

## Best Practices

1. **Configuration**
   - Use Pydantic models for config validation
   - Provide sensible defaults
   - Document all config options

2. **Error Handling**
   - Create plugin-specific exceptions
   - Provide detailed error messages
   - Handle network errors gracefully

3. **Testing**
   - Mock external dependencies
   - Test error cases
   - Use fixtures for common setup

4. **Documentation**
   - Document all public methods
   - Provide usage examples
   - Include type hints

5. **Performance**
   - Implement connection pooling
   - Cache frequently used data
   - Use batch operations when possible

## Examples

### Basic Plugin Usage

```python
# Initialize SDK
sdk = GoatSDK(
    private_key="...",
    network=Network.MAINNET
)

# Initialize plugin
my_plugin = MyPlugin(sdk)

# Use plugin
params = OperationParams(
    param1="test",
    param2=123
)

result = await my_plugin.my_operation(params)
```

### AI Integration

```python
# Get plugin tools
tools = my_plugin.get_tools()

# Create Langchain agent
agent = initialize_agent(
    tools=LangchainAdapter.create_tools(tools),
    llm=ChatOpenAI(),
    agent="chat-conversational-react-description",
    verbose=True
)

# Use agent
response = await agent.arun(
    "Perform my operation with param1=test and param2=123"
)
```

## Next Steps

- See [API Reference](./api-reference.md) for detailed method documentation
- Check [Examples](../examples/) for more usage examples
- Learn about [Error Handling](./error-handling.md)
