"""Tests for the Tool decorator."""

import pytest
from pydantic import BaseModel

from goat_sdk.core.classes.wallet_client_base import WalletClientBase
from goat_sdk.core.decorators.tool import Tool, get_tool_metadata


class AddParameters(BaseModel):
    """Test parameters model."""
    a: int
    b: int


class TestWalletClient(WalletClientBase):
    """Test wallet client."""
    pass


class TestToolService:
    """Test service class for Tool decorator."""
    
    @Tool(description="Adds two numbers")
    def add(self, params: AddParameters) -> int:
        """Add two numbers."""
        return params.a + params.b

    @Tool(description="Adds two numbers with wallet", name="add_with_wallet")
    def add_with_wallet(self, params: AddParameters, wallet: TestWalletClient) -> int:
        """Add two numbers with wallet client."""
        return params.a + params.b


def test_tool_decorator_basic():
    """Test basic Tool decorator functionality."""
    service = TestToolService()
    
    # Test method execution
    result = service.add(AddParameters(a=1, b=2))
    assert result == 3

    # Test metadata
    metadata = get_tool_metadata(TestToolService, "add")
    assert metadata is not None
    assert metadata.name == "add"
    assert metadata.description == "Adds two numbers"
    assert metadata.parameters.index == 0
    assert metadata.parameters.schema == AddParameters
    assert metadata.wallet_client is None


def test_tool_decorator_with_wallet():
    """Test Tool decorator with wallet client parameter."""
    service = TestToolService()
    
    # Test method execution
    result = service.add_with_wallet(
        AddParameters(a=1, b=2),
        TestWalletClient()
    )
    assert result == 3

    # Test metadata
    metadata = get_tool_metadata(TestToolService, "add_with_wallet")
    assert metadata is not None
    assert metadata.name == "add_with_wallet"
    assert metadata.description == "Adds two numbers with wallet"
    assert metadata.parameters.index == 0
    assert metadata.parameters.schema == AddParameters
    assert metadata.wallet_client is not None
    assert metadata.wallet_client.index == 1


def test_tool_decorator_validation():
    """Test Tool decorator parameter validation."""
    
    # Test missing parameters
    with pytest.raises(ValueError) as exc_info:
        class InvalidService1:
            @Tool(description="Invalid method")
            def invalid(self):
                pass
    assert "has no parameters" in str(exc_info.value)

    # Test too many parameters
    with pytest.raises(ValueError) as exc_info:
        class InvalidService2:
            @Tool(description="Invalid method")
            def invalid(self, p1: AddParameters, p2: TestWalletClient, p3: str):
                pass
    assert "has 3 parameters" in str(exc_info.value)

    # Test missing Pydantic model
    with pytest.raises(ValueError) as exc_info:
        class InvalidService3:
            @Tool(description="Invalid method")
            def invalid(self, param: str):
                pass
    assert "has no Pydantic model parameter" in str(exc_info.value)
