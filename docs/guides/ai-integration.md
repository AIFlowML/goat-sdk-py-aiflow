# AI Integration Guide

## Overview

GOAT-sdk-py provides seamless integration with popular AI frameworks like LangChain and LlamaIndex. This enables AI agents to interact with blockchain networks using natural language commands.

## Supported Frameworks

- **LangChain**: For building conversational agents
- **LlamaIndex**: For structured data querying
- **Custom Integration**: Support for custom AI frameworks

## LangChain Integration

### Basic Setup

```python
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from goat_sdk import GoatSDK
from goat_sdk.plugins.spl_token import SplTokenPlugin
from goat_sdk.adapters import LangchainAdapter

# Initialize SDK and plugin
sdk = GoatSDK(private_key="your_private_key")
spl = SplTokenPlugin(sdk)

# Get tools
tools = spl.get_tools()

# Create agent
agent = initialize_agent(
    tools=LangchainAdapter.create_tools(tools),
    llm=ChatOpenAI(),
    agent="chat-conversational-react-description",
    verbose=True
)
```

### Using the Agent

```python
# Simple queries
response = await agent.arun(
    "What's my token balance?"
)

# Complex operations
response = await agent.arun(
    "Transfer 1 SOL worth of tokens to address xyz"
)

# Multi-step tasks
response = await agent.arun("""
1. Check my token balance
2. If I have more than 100 tokens, transfer 50 to address xyz
3. Confirm the transfer was successful
""")
```

### Custom Tool Configuration

```python
from goat_sdk.core.tool import Tool
from pydantic import BaseModel, Field

# Define custom parameters
class CustomParams(BaseModel):
    amount: float = Field(..., description="Amount to transfer")
    recipient: str = Field(..., description="Recipient address")

# Create custom tool
async def custom_transfer(params: CustomParams) -> dict:
    result = await spl.transfer_token(
        amount=params.amount,
        to_address=params.recipient
    )
    return {"status": "success", "tx": result.signature}

# Register tool
custom_tool = Tool(
    name="custom_transfer",
    description="Transfer tokens to an address",
    function=custom_transfer,
    parameters=CustomParams
)

# Add to agent
agent = initialize_agent(
    tools=LangchainAdapter.create_tools([custom_tool]),
    llm=ChatOpenAI(),
    agent="chat-conversational-react-description"
)
```

## LlamaIndex Integration

### Basic Setup

```python
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
from goat_sdk import GoatSDK
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin
from goat_sdk.adapters import LlamaIndexAdapter

# Initialize SDK and plugin
sdk = GoatSDK(private_key="your_private_key")
nft = SolanaNFTPlugin(sdk)

# Get tools
tools = nft.get_tools()

# Create index with tools
index = GPTVectorStoreIndex.from_tools(
    LlamaIndexAdapter.create_tools(tools)
)
```

### Querying NFT Data

```python
# Simple queries
response = index.query(
    "What NFTs do I own?"
)

# Complex queries
response = index.query(
    "Find all my NFTs from collection xyz and their rarity scores"
)

# Analytical queries
response = index.query("""
Analyze my NFT portfolio:
1. Total number of NFTs
2. Distribution by collection
3. Estimated value in SOL
""")
```

### Custom Index Configuration

```python
from llama_index import ServiceContext
from llama_index.llms import OpenAI

# Configure service context
service_context = ServiceContext.from_defaults(
    llm=OpenAI(temperature=0, model="gpt-4")
)

# Create index with custom configuration
index = GPTVectorStoreIndex.from_tools(
    LlamaIndexAdapter.create_tools(tools),
    service_context=service_context
)
```

## Custom Framework Integration

### Tool Abstraction

```python
from goat_sdk.core.tool import Tool
from typing import List, Type

class CustomAdapter:
    @staticmethod
    def create_tools(tools: List[Tool]) -> List[dict]:
        """Convert SDK tools to custom format.
        
        Args:
            tools: List of SDK tools
            
        Returns:
            List[dict]: Tools in custom format
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "function": tool.function,
                "schema": tool.parameters.schema()
            }
            for tool in tools
        ]
```

### Integration Example

```python
from your_ai_framework import Agent
from goat_sdk import GoatSDK
from goat_sdk.plugins.spl_token import SplTokenPlugin

# Initialize SDK and plugin
sdk = GoatSDK(private_key="your_private_key")
spl = SplTokenPlugin(sdk)

# Get and convert tools
tools = CustomAdapter.create_tools(spl.get_tools())

# Create custom agent
agent = Agent(
    tools=tools,
    model="your-model"
)

# Use agent
response = await agent.run(
    "Your natural language command"
)
```

## Best Practices

### 1. Tool Design

- Keep tool descriptions clear and concise
- Use meaningful parameter names
- Include comprehensive parameter descriptions
- Handle errors gracefully

```python
class TransferParams(BaseModel):
    amount: float = Field(
        ...,
        description="Amount to transfer in decimal format",
        gt=0
    )
    recipient: str = Field(
        ...,
        description="Recipient wallet address (base58 encoded)"
    )
```

### 2. Error Handling

```python
async def safe_transfer(params: TransferParams) -> dict:
    try:
        result = await spl.transfer_token(...)
        return {"status": "success", "data": result}
    except InsufficientBalanceError as e:
        return {
            "status": "error",
            "error": f"Insufficient balance: {e.available} < {e.required}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### 3. Response Formatting

```python
async def get_balance(params: BalanceParams) -> dict:
    balance = await spl.get_token_balance(...)
    
    return {
        "status": "success",
        "data": {
            "balance": balance,
            "formatted": f"{balance:.2f} tokens",
            "timestamp": int(time.time())
        }
    }
```

### 4. Chain Management

```python
async def safe_operation(params: Params) -> dict:
    # Validate chain
    if self.sdk.chain != Chain.SOLANA:
        return {
            "status": "error",
            "error": "Operation only supported on Solana"
        }
    
    # Perform operation
    try:
        result = await self.operation(...)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

## Examples

### Multi-Plugin Agent

```python
from goat_sdk import GoatSDK
from goat_sdk.plugins.spl_token import SplTokenPlugin
from goat_sdk.plugins.solana_nft import SolanaNFTPlugin
from goat_sdk.adapters import LangchainAdapter

# Initialize SDK and plugins
sdk = GoatSDK(private_key="your_private_key")
spl = SplTokenPlugin(sdk)
nft = SolanaNFTPlugin(sdk)

# Combine tools
tools = [
    *spl.get_tools(),
    *nft.get_tools()
]

# Create agent
agent = initialize_agent(
    tools=LangchainAdapter.create_tools(tools),
    llm=ChatOpenAI(),
    agent="chat-conversational-react-description"
)

# Use agent for complex operations
response = await agent.arun("""
1. List all my NFTs
2. For each NFT worth more than 10 SOL:
   - Get its metadata
   - Check if I have enough SPL tokens
   - If yes, list it on the marketplace
3. Summarize the results
""")
```

### Custom Agent with Memory

```python
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor
from goat_sdk.adapters import LangchainAdapter

# Create memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create agent with memory
agent = initialize_agent(
    tools=LangchainAdapter.create_tools(tools),
    llm=ChatOpenAI(),
    memory=memory,
    agent="chat-conversational-react-description"
)

# Use agent with context
responses = []
responses.append(await agent.arun(
    "What's my token balance?"
))
responses.append(await agent.arun(
    "Transfer half of it to address xyz"
))
responses.append(await agent.arun(
    "Confirm the transfer was successful"
))
```

## Next Steps

- Explore the [Plugin Guide](./plugin-guide.md) for available tools
- Check [Examples](../examples/) for more usage scenarios
- Review [Error Handling](./error-handling.md) best practices
- See [API Reference](./api-reference.md) for detailed documentation 