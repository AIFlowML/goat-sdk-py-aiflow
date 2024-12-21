"""Phidata toolkit implementation for GOAT SDK."""

from typing import List, Dict, Any, Callable, Awaitable
from phidata.core.toolkit import Toolkit
from goat_sdk.core.classes.tool_base import ToolBase

class GoatToolkit(Toolkit):
    """Phidata toolkit wrapper for GOAT SDK tools.
    
    This class wraps GOAT SDK tools as a Phidata toolkit, making them compatible
    with Phidata's agent framework. It handles tool registration, parameter
    validation, and async execution.

    Args:
        tools (List[ToolBase]): List of GOAT SDK tools to wrap

    Example:
        ```python
        goat_tools = [tool1, tool2]
        toolkit = GoatToolkit(goat_tools)
        agent = Agent(toolkits=[toolkit])
        ```
    """
    
    def __init__(self, tools: List[ToolBase]):
        """Initialize the toolkit.
        
        Args:
            tools: List of GOAT SDK tools to wrap
        """
        super().__init__(name="goat_toolkit")
        self.tools = tools
        
        # Register all tools
        for tool in tools:
            executor = self._create_tool_executor(tool)
            setattr(self, f"execute_{tool.name}", executor)
            self.register(executor)
    
    def _create_tool_executor(self, tool: ToolBase) -> Callable[..., Awaitable[str]]:
        """Create a tool executor function.
        
        This method creates a function that wraps a GOAT SDK tool's execute method,
        handling parameter passing and error handling.
        
        Args:
            tool: The GOAT SDK tool to create an executor for
            
        Returns:
            An async function that executes the tool
        """
        async def executor(**kwargs: Dict[str, Any]) -> str:
            """Execute the tool with given parameters.
            
            Args:
                **kwargs: Tool parameters as keyword arguments
                
            Returns:
                Tool execution result as a string, or error message if execution fails
            """
            try:
                result = await tool.execute(kwargs)
                return str(result)
            except Exception as e:
                return f"Error executing {tool.name}: {str(e)}"
        
        # Set function metadata
        executor.__name__ = f"execute_{tool.name}"
        executor.__doc__ = tool.description
        
        return executor
