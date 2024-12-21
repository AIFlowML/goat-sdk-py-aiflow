# GOAT SDK Adapters

This directory contains adapters that allow GOAT SDK to be used with various AI frameworks and tools.

## Available Adapters

### Langchain Adapter

The Langchain adapter allows GOAT SDK tools to be used as Langchain tools. This enables seamless integration with Langchain agents and chains.

```python
from goat_sdk.adapters.langchain import get_on_chain_tools

# Get Langchain tools
tools = await get_on_chain_tools(wallet=wallet, plugins=[erc20_plugin])

# Use with Langchain
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
```

### Phidata Adapter

The Phidata adapter allows GOAT SDK tools to be used as Phidata toolkits. This enables integration with Phidata's agent framework.

```python
from goat_sdk.adapters.phidata import get_on_chain_toolkit

# Get Phidata toolkit
toolkit = await get_on_chain_toolkit(wallet=wallet, plugins=[erc20_plugin])

# Use with Phidata
agent = Agent(
    name="blockchain_agent",
    llm=llm,
    toolkits=[toolkit]
)
```

## Creating New Adapters

To create a new adapter:

1. Create a new directory under `adapters/`
2. Implement the adapter interface
3. Add appropriate type hints and documentation
4. Add tests under `tests/adapters/`

See existing adapters for reference implementations.
