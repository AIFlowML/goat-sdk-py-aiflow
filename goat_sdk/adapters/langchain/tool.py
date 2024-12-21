"""Langchain tool implementation for GOAT SDK."""

from typing import Dict, Any
from langchain.tools import BaseTool
from goat_sdk.core.classes.tool_base import ToolBase

class GoatTool(BaseTool):
    """Langchain tool wrapper for GOAT SDK tools.
    
    This class wraps a GOAT SDK tool as a Langchain tool, making it compatible
    with Langchain's agent framework. It handles parameter validation and
    async execution.

    Args:
        tool (ToolBase): The GOAT SDK tool to wrap

    Example:
        ```python
        goat_tool = ToolBase(name="my_tool", description="A tool")
        langchain_tool = GoatTool(goat_tool)
        ```
    """
    
    def __init__(self, tool: ToolBase):
        """Initialize the tool.
        
        Args:
            tool: The GOAT SDK tool to wrap
        """
        self.tool = tool
        super().__init__(
            name=tool.name,
            description=tool.description,
            func=self._execute,
            args_schema=tool.parameters
        )
    
    async def _execute(self, **kwargs: Dict[str, Any]) -> str:
        """Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool parameters as keyword arguments
            
        Returns:
            Tool execution result as a string
            
        Raises:
            Exception: If tool execution fails
        """
        try:
            result = await self.tool.execute(kwargs)
            return str(result)
        except Exception as e:
            raise ValueError(f"Tool execution failed: {str(e)}")
            
    def _run(self, *args: Any, **kwargs: Any) -> str:
        """Synchronous execution method required by Langchain.
        
        This method raises an error as all GOAT SDK tools are async.
        """
        raise NotImplementedError("GOAT SDK tools only support async execution")
        
    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Async execution method for Langchain.
        
        Args:
            *args: Positional arguments (not used)
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        return await self._execute(**kwargs)
