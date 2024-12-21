# Langchain Adapter for GOAT SDK

This adapter enables seamless integration between GOAT SDK tools and Langchain's agent framework.

## Features

- Convert GOAT SDK tools to Langchain tools
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
from goat_sdk.adapters.langchain import get_on_chain_tools
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI

# Initialize SDK and plugin
sdk = GoatSDK(
    private_key="your_private_key",
    provider_url="https://sepolia.mode.network"
)
erc20_plugin = ERC20Plugin(sdk)

# Get Langchain tools
tools = await get_on_chain_tools(wallet=sdk, plugins=[erc20_plugin])

# Initialize Langchain agent
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent
response = await agent.arun(
    "Deploy a new ERC20 token named 'Test Token' with symbol 'TEST'"
)
```

### Custom Tool Integration

You can also wrap individual GOAT SDK tools:

```python
from goat_sdk.adapters.langchain import GoatTool

# Create Langchain tool from GOAT SDK tool
tool = GoatTool(your_goat_tool)

# Use the tool directly
result = await tool._execute(param1="value1", param2="value2")
```

## Error Handling

The adapter provides proper error handling:

```python
try:
    result = await tool._execute(param1="value1")
except Exception as e:
    print(f"Tool execution failed: {e}")
```

## Testing

Run the adapter tests:

```bash
pytest tests/adapters/test_langchain_adapter.py -v
```

## API Reference

### `get_on_chain_tools`

```python
async def get_on_chain_tools(
    wallet: WalletClientBase,
    plugins: List[any]
) -> List[Tool]
```

Converts GOAT SDK tools from plugins into Langchain tools.

### `GoatTool`

```python
class GoatTool(BaseTool):
    def __init__(self, tool: ToolBase)
    async def _execute(self, **kwargs) -> str
```

Wraps a GOAT SDK tool as a Langchain tool.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request
