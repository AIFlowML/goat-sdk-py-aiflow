# Phidata Adapter for GOAT SDK

This adapter enables seamless integration between GOAT SDK tools and Phidata's agent framework.

## Features

- Convert GOAT SDK tools to Phidata toolkits
- Dynamic tool registration
- Full async/await support
- Proper error handling
- Type safety with Pydantic models
- Comprehensive test coverage

## Installation

The adapter is included in the GOAT SDK package:

```bash
pip install goat-sdk
```

## Usage

### Basic Example

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.ERC20 import ERC20Plugin
from goat_sdk.adapters.phidata import get_on_chain_toolkit
from phi.llm.openai import OpenAIChat
from phi.agent import Agent

# Initialize SDK and plugin
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://sepolia.mode.network"
)
erc20_plugin = ERC20Plugin(sdk)

# Get Phidata toolkit
toolkit = await get_on_chain_toolkit(wallet=sdk, plugins=[erc20_plugin])

# Initialize Phidata agent
llm = OpenAIChat()
agent = Agent(
    name="blockchain_agent",
    llm=llm,
    toolkits=[toolkit],
    show_tool_calls=True
)

# Use the agent
response = await agent.run(
    "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST'"
)
```

### Custom Toolkit Integration

You can also create custom toolkits:

```python
from goat_sdk.adapters.phidata import GoatToolkit

# Create toolkit from GOAT SDK tools
toolkit = GoatToolkit([tool1, tool2])

# Use toolkit methods directly
result = await getattr(toolkit, f"execute_{tool1.name}")(param1="value1")
```

## Error Handling

The adapter provides graceful error handling:

```python
# Errors are caught and returned as messages
result = await toolkit.execute_tool(invalid_param="value")
if "Error executing" in result:
    print(f"Tool execution failed: {result}")
```

## Testing

Run the adapter tests:

```bash
pytest tests/adapters/test_phidata_adapter.py -v
```

## API Reference

### `get_on_chain_toolkit`

```python
async def get_on_chain_toolkit(
    wallet: WalletClientBase,
    plugins: List[any]
) -> Toolkit
```

Converts GOAT SDK tools from plugins into a Phidata toolkit.

### `GoatToolkit`

```python
class GoatToolkit(Toolkit):
    def __init__(self, tools: List[ToolBase])
    def _create_tool_executor(self, tool: ToolBase)
```

Wraps GOAT SDK tools as a Phidata toolkit.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request
