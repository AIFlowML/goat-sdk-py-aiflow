# Plugin Development Guide

This guide explains how to create custom plugins for the GOAT SDK.

## Plugin Architecture

The GOAT SDK uses a plugin system based on the `PluginBase` class. All plugins must inherit from this class and implement the required methods.

## Creating a Plugin

### Basic Structure

```python
from goat_sdk.core.classes.plugin_base import PluginBase
from pydantic import BaseModel

class MyPluginParams(BaseModel):
    param1: str
    param2: int

class MyPlugin(PluginBase):
    def __init__(self, sdk):
        super().__init__(name="my_plugin", tools=[self])
        self.sdk = sdk

    async def my_method(self, params: MyPluginParams):
        # Implementation
        pass
```

### Required Components

1. **Parameter Models**: Use Pydantic models for type safety
2. **Plugin Class**: Inherit from `PluginBase`
3. **Initialization**: Call `super().__init__()` with plugin name
4. **Methods**: Implement async methods for plugin functionality

## Example: Custom Token Plugin

```python
from goat_sdk.core.classes.plugin_base import PluginBase
from pydantic import BaseModel, Field
from web3 import Web3

class CustomTokenParams(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=11)
    decimals: int = Field(..., ge=0, le=18)

class CustomTokenPlugin(PluginBase):
    def __init__(self, sdk):
        super().__init__(name="custom_token", tools=[self])
        self.sdk = sdk
        self.w3 = Web3(Web3.HTTPProvider(sdk.provider_url))

    async def create_token(self, params: CustomTokenParams):
        # Implementation
        pass

    async def _validate_params(self, params: CustomTokenParams):
        # Validation logic
        pass
```

## Best Practices

### 1. Type Safety

- Use Pydantic models for all parameters
- Add field validation with descriptive errors
- Use type hints consistently

```python
from pydantic import BaseModel, Field, field_validator

class TransferParams(BaseModel):
    recipient: str = Field(..., description="Recipient address")
    amount: int = Field(..., gt=0, description="Amount to transfer")

    @field_validator("recipient")
    def validate_address(cls, v: str) -> str:
        if not Web3.is_address(v):
            raise ValueError("Invalid address")
        return Web3.to_checksum_address(v)
```

### 2. Error Handling

- Create specific error types
- Provide detailed error messages
- Handle network errors gracefully

```python
from goat_sdk.core.errors import GoatSDKError

class CustomPluginError(GoatSDKError):
    pass

try:
    result = await self._make_call()
except Exception as e:
    raise CustomPluginError(f"Operation failed: {str(e)}")
```

### 3. Async/Await

- Use async/await for network operations
- Handle concurrent operations properly
- Implement proper cleanup

```python
async def make_transaction(self, params):
    try:
        async with self._get_session() as session:
            result = await self._send_transaction(session, params)
            return result
    finally:
        await self._cleanup()
```

### 4. Documentation

- Add docstrings to all classes and methods
- Include example usage
- Document all parameters and return types

```python
class MyPlugin(PluginBase):
    """Custom plugin for token operations.

    Example:
        ```python
        plugin = MyPlugin(sdk)
        result = await plugin.my_method({"param1": "value"})
        ```
    """

    async def my_method(self, params: MyPluginParams):
        """Perform a custom operation.

        Args:
            params: Operation parameters

        Returns:
            TransactionResult: Result of the operation

        Raises:
            CustomPluginError: If the operation fails
        """
        pass
```

## Testing

### 1. Unit Tests

```python
import pytest
from unittest.mock import Mock

def test_plugin_initialization():
    sdk = Mock()
    plugin = MyPlugin(sdk)
    assert plugin.name == "my_plugin"

@pytest.mark.asyncio
async def test_my_method():
    sdk = Mock()
    plugin = MyPlugin(sdk)
    result = await plugin.my_method({"param1": "value"})
    assert result.status == "success"
```

### 2. Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_transaction():
    sdk = GoatSDK(
        private_key="test_key",
        provider_url="http://localhost:8545"
    )
    plugin = MyPlugin(sdk)
    result = await plugin.my_method({"param1": "value"})
    assert result.transaction_hash is not None
```

## Publishing

1. Add your plugin to the `goat_sdk/plugins` directory
2. Update the plugin registry
3. Add documentation
4. Add tests
5. Create a pull request

## Example Plugins

Check out these example plugins:
- [ERC20 Plugin](../plugins/ERC20)
- [SPL Token Plugin](../plugins/spl_token)
