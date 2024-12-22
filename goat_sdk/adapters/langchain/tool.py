"""Example script showing how to use GOAT SDK tools with Langchain."""

import json
from typing import Dict, Any
from langchain.tools import Tool
from goat_sdk.core.classes.tool_base import ToolBase


def create_langchain_tool(tool: ToolBase) -> Tool:
    """Create a Langchain tool from a GOAT SDK tool.
    
    Example:
        ```python
        goat_tool = ToolBase(name="my_tool", description="A tool")
        langchain_tool = create_langchain_tool(goat_tool)
        ```
    """
    async def _execute(tool_input: str) -> str:
        """Execute the wrapped tool."""
        try:
            # Parse JSON input
            kwargs = json.loads(tool_input)
            result = await tool.execute(kwargs)
            return str(result)
        except json.JSONDecodeError:
            raise ValueError("Tool input must be a valid JSON string")
        except Exception as e:
            raise ValueError(f"Tool execution failed: {str(e)}")
            
    def _run(tool_input: str) -> str:
        """Sync execution is not supported."""
        raise NotImplementedError("GOAT SDK tools only support async execution")
        
    async def _arun(tool_input: str) -> str:
        """Run the tool asynchronously."""
        return await _execute(tool_input)
    
    return Tool(
        name=tool.name,
        description=tool.description,
        func=_run,
        coroutine=_arun
    )
