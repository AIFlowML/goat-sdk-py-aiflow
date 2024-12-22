"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
     
     Path: examples/adapters/langchain_example.py
"""

"""Tests for the Tool decorator."""

import pytest
import logging
from pydantic import BaseModel, Field

from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.decorators.tool import Tool, get_tool_metadata
from goat_sdk.core.types.chain import ChainType

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AddParameters(BaseModel):
    """Test parameters model."""
    a: int
    b: int


class TestWalletClient(WalletClientBase):
    """Test wallet client."""
    provider_url: str = Field(default="http://localhost:8545")
    private_key: str = Field(default="0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    
    async def get_address(self) -> str:
        """Get wallet address."""
        return "test_address"
        
    async def get_chain(self) -> ChainType:
        """Get chain type."""
        return ChainType.ETHEREUM
        
    async def balance_of(self, address: str) -> int:
        """Get balance of address."""
        return 100
        
    async def sign_message(self, message: str) -> str:
        """Sign a message."""
        return f"signed_{message}"
        
    async def sign_transaction(self, transaction: dict) -> str:
        """Sign a transaction."""
        return f"signed_tx_{transaction}"
        
    async def send_transaction(self, transaction: dict) -> str:
        """Send a transaction."""
        return f"sent_tx_{transaction}"


class TestToolService:
    """Test service class for Tool decorator."""
    
    @Tool(description="Adds two numbers")
    async def add(self, params: AddParameters) -> int:
        """Add two numbers."""
        return params.a + params.b

    @Tool(description="Adds two numbers with wallet", name="add_with_wallet")
    async def add_with_wallet(self, params: AddParameters, wallet: TestWalletClient) -> int:
        """Add two numbers with wallet client."""
        return params.a + params.b


@pytest.mark.asyncio
async def test_tool_decorator_basic():
    """Test basic Tool decorator functionality."""
    logger.info("Starting test_tool_decorator_basic")
    service = TestToolService()
    
    # Test method execution
    logger.debug("Testing method execution")
    result = await service.add(AddParameters(a=1, b=2))
    assert result == 3

    # Test metadata
    logger.debug("Testing metadata")
    metadata = get_tool_metadata(service.add)
    assert metadata is not None
    assert metadata["name"] == "add"
    assert metadata["description"] == "Adds two numbers"
    assert "parameters" in metadata
    assert isinstance(metadata["parameters"], dict)
    logger.info("Completed test_tool_decorator_basic")


@pytest.mark.asyncio
async def test_tool_decorator_with_wallet():
    """Test Tool decorator with wallet client parameter."""
    logger.info("Starting test_tool_decorator_with_wallet")
    service = TestToolService()
    
    # Test method execution
    logger.debug("Testing method execution with wallet")
    result = await service.add_with_wallet(
        AddParameters(a=1, b=2),
        TestWalletClient()
    )
    assert result == 3

    # Test metadata
    logger.debug("Testing metadata")
    metadata = get_tool_metadata(service.add_with_wallet)
    assert metadata is not None
    assert metadata["name"] == "add_with_wallet"
    assert metadata["description"] == "Adds two numbers with wallet"
    assert "parameters" in metadata
    assert isinstance(metadata["parameters"], dict)
    logger.info("Completed test_tool_decorator_with_wallet")


@pytest.mark.asyncio
async def test_tool_decorator_validation():
    """Test Tool decorator parameter validation."""
    logger.info("Starting test_tool_decorator_validation")
    
    # Test missing parameters
    logger.debug("Testing function with no parameters")
    with pytest.raises(ValueError) as exc_info:
        logger.debug("Creating Tool instance")
        tool = Tool(description="Invalid method")
        logger.debug("Defining invalid function with no parameters")
        async def invalid():
            pass
        logger.debug("Applying Tool decorator")
        tool(invalid)
    assert "Tool invalid must have parameters" in str(exc_info.value)
    logger.debug(f"Caught expected ValueError: {exc_info.value}")

    # Test invalid parameter type
    logger.debug("Testing function with invalid parameter type")
    with pytest.raises(ValueError) as exc_info:
        logger.debug("Creating Tool instance")
        tool = Tool(description="Invalid method")
        logger.debug("Defining invalid function with str parameter")
        async def invalid(param: str):
            pass
        logger.debug("Applying Tool decorator")
        tool(invalid)
    assert "parameters must be Pydantic models or wallet clients" in str(exc_info.value)
    logger.debug(f"Caught expected ValueError: {exc_info.value}")
    logger.info("Completed test_tool_decorator_validation")
