"""Example script showing how to use GOAT SDK tools with Phidata."""

from typing import List, Dict, Any
from phidata.core.toolkit import Toolkit
from goat_sdk.core.classes.tool_base import ToolBase


def create_phidata_toolkit(tools: List[ToolBase]) -> Toolkit:
    """Create a Phidata toolkit from GOAT SDK tools.
    
    Example:
        ```python
        goat_tools = [tool1, tool2]
        toolkit = create_phidata_toolkit(goat_tools)
        agent = Agent(toolkits=[toolkit])
        ```
    """
    toolkit = Toolkit(name="goat_toolkit")
    
    for tool in tools:
        # Create a closure to capture the tool instance
        def create_executor(t: ToolBase):
            async def executor(**kwargs: Dict[str, Any]) -> str:
                """Execute the tool with given parameters."""
                try:
                    result = await t.execute(kwargs)
                    return str(result)
                except Exception as e:
                    return f"Error executing {t.name}: {str(e)}"
            
            # Set function metadata
            executor.__name__ = f"execute_{t.name}"
            executor.__doc__ = t.description
            executor.__parameters__ = t.parameters
            
            return executor
        
        # Add function to toolkit
        setattr(toolkit, f"execute_{tool.name}", create_executor(tool))
    
    return toolkit
