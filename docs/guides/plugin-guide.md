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

## Advanced Plugin Development

### Plugin Architecture Best Practices

1. **Service Layer Pattern**
```python
class MyPluginService:
    """Service layer for core business logic."""
    def __init__(self, config: MyPluginConfig):
        self.config = config
        
    async def process_operation(self, params: OperationParams):
        # Core business logic here
        pass

class MyPlugin(Plugin):
    def __init__(self, sdk: GoatSDK, options: Optional[MyPluginConfig] = None):
        super().__init__(sdk)
        self.service = MyPluginService(options or MyPluginConfig())
```

2. **Configuration Management**
```python
from pydantic import Field, validator

class MyPluginConfig(BaseModel):
    api_url: str = Field(..., description="API endpoint URL")
    retry_count: int = Field(3, ge=1, le=10)
    timeout: float = Field(30.0, gt=0)
    
    @validator("api_url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")
        return v
```

3. **State Management**
```python
from typing import Dict, Any
from contextlib import asynccontextmanager

class MyPlugin(Plugin):
    def __init__(self, sdk: GoatSDK):
        self._state: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        
    @asynccontextmanager
    async def managed_state(self):
        async with self._lock:
            try:
                yield self._state
            finally:
                # Cleanup if needed
                pass
```

### Advanced Error Handling

1. **Custom Error Types**
```python
from enum import Enum
from typing import Optional

class ErrorCode(Enum):
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT"

class MyPluginError(GoatSDKError):
    def __init__(
        self,
        message: str,
        code: ErrorCode,
        details: Optional[dict] = None
    ):
        super().__init__(message)
        self.code = code
        self.details = details or {}
```

2. **Error Recovery Patterns**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class MyPlugin(Plugin):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def resilient_operation(self, params: OperationParams):
        try:
            return await self.service.process_operation(params)
        except NetworkError as e:
            raise MyPluginError(
                message="Network operation failed",
                code=ErrorCode.NETWORK_ERROR,
                details={"original_error": str(e)}
            )
```

### Performance Optimization

1. **Caching**
```python
from cachetools import TTLCache
from functools import lru_cache

class MyPlugin(Plugin):
    def __init__(self, sdk: GoatSDK):
        self.cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes TTL
        
    @lru_cache(maxsize=32)
    def get_cached_data(self, key: str):
        return self.cache.get(key)
```

2. **Batch Processing**
```python
class MyPlugin(Plugin):
    async def batch_process(
        self,
        items: List[OperationParams],
        batch_size: int = 10
    ):
        results = []
        for batch in self._chunk_list(items, batch_size):
            batch_results = await asyncio.gather(
                *[self.process_item(item) for item in batch]
            )
            results.extend(batch_results)
        return results
    
    @staticmethod
    def _chunk_list(lst: List, n: int):
        return [lst[i:i + n] for i in range(0, len(lst), n)]
```

### Testing Strategies

1. **Integration Tests**
```python
@pytest.mark.integration
async def test_integration_flow(my_plugin):
    # Setup test data
    params = OperationParams(...)
    
    # Execute operation
    result = await my_plugin.process_operation(params)
    
    # Verify results
    assert result.status == "success"
    assert "data" in result
```

2. **Performance Tests**
```python
@pytest.mark.performance
async def test_performance(my_plugin, benchmark):
    params = OperationParams(...)
    
    def run_sync():
        asyncio.run(my_plugin.process_operation(params))
    
    # Run benchmark
    result = benchmark(run_sync)
    
    # Assert performance constraints
    assert result.stats.mean < 0.1  # 100ms max
```

### Documentation

1. **Type Hints and Docstrings**
```python
from typing import TypeVar, Generic

T = TypeVar("T")

class OperationResult(Generic[T]):
    """
    Generic operation result container.
    
    Args:
        data: The operation result data
        metadata: Optional metadata about the operation
    
    Raises:
        ValidationError: If the data doesn't match expected type
    """
    def __init__(
        self,
        data: T,
        metadata: Optional[dict] = None
    ) -> None:
        self.data = data
        self.metadata = metadata or {}
```

2. **Usage Examples**
```python
def get_examples(self) -> List[dict]:
    """Provide usage examples for AI tools."""
    return [
        {
            "description": "Basic operation",
            "code": '''
                result = await plugin.process_operation(
                    OperationParams(value="test")
                )
            '''
        }
    ]
```

### Monitoring and Observability

1. **Metrics Collection**
```python
from prometheus_client import Counter, Histogram

class MyPlugin(Plugin):
    def __init__(self, sdk: GoatSDK):
        self.operation_counter = Counter(
            "my_plugin_operations_total",
            "Total operations processed"
        )
        self.operation_duration = Histogram(
            "my_plugin_operation_duration_seconds",
            "Operation duration in seconds"
        )
```

2. **Logging**
```python
import logging
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)

class MyPlugin(Plugin):
    @contextmanager
    def log_operation(self, operation: str):
        start_time = time.time()
        logger.info(f"Starting {operation}")
        try:
            yield
        except Exception as e:
            logger.error(f"Error in {operation}: {e}")
            raise
        finally:
            duration = time.time() - start_time
            logger.info(f"Completed {operation} in {duration:.2f}s")
```

These advanced features and patterns will help you create robust, maintainable, and performant plugins for the GOAT SDK.
