"""Tests for the WalletClientBase class."""

import pytest
from typing import Dict
from typing_extensions import TypedDict

from goat_sdk.core.classes.wallet_client_base import (
    WalletClientBase,
    Balance,
    Signature,
    GetAddressParams,
    GetChainParams,
    SignMessageParams,
    BalanceOfParams,
    SignTransactionParams,
    SendTransactionParams,
)
from goat_sdk.core.types import Chain


class MockWalletClient(WalletClientBase):
    """Mock wallet client for testing."""

    provider_url: str = "http://localhost:8545"
    private_key: str = "0x" + "1" * 64
    mock_address: str = "mock_address"
    mock_chain: Chain = {"type": "solana"}

    def get_address(self, params: GetAddressParams) -> str:
        return self.mock_address

    def get_chain(self, params: GetChainParams) -> Chain:
        return self.mock_chain

    async def sign_message(self, params: SignMessageParams) -> Signature:
        return {"signature": f"signed_{params.message}"}

    async def balance_of(self, params: BalanceOfParams) -> Balance:
        return {
            "decimals": 9,
            "symbol": "SOL",
            "name": "Solana",
            "value": "1.5",
            "in_base_units": "1500000000"
        }
        
    async def sign_transaction(self, params: SignTransactionParams) -> str:
        return f"signed_{params.transaction}"
        
    async def send_transaction(self, params: SendTransactionParams) -> str:
        return f"sent_{params.transaction}"


@pytest.fixture
def wallet_client() -> MockWalletClient:
    """Create a mock wallet client for testing."""
    return MockWalletClient()


def test_get_address(wallet_client: MockWalletClient):
    """Test get_address method."""
    params = GetAddressParams()
    assert wallet_client.get_address(params) == "mock_address"


def test_get_chain(wallet_client: MockWalletClient):
    """Test get_chain method."""
    params = GetChainParams()
    assert wallet_client.get_chain(params) == {"type": "solana"}


@pytest.mark.asyncio
async def test_sign_message(wallet_client: MockWalletClient):
    """Test sign_message method."""
    params = SignMessageParams(message="test_message")
    signature = await wallet_client.sign_message(params)
    assert signature == {"signature": "signed_test_message"}


@pytest.mark.asyncio
async def test_balance_of(wallet_client: MockWalletClient):
    """Test balance_of method."""
    params = BalanceOfParams(address="test_address")
    balance = await wallet_client.balance_of(params)
    assert balance == {
        "decimals": 9,
        "symbol": "SOL",
        "name": "Solana",
        "value": "1.5",
        "in_base_units": "1500000000"
    }


def test_get_core_tools(wallet_client: MockWalletClient):
    """Test get_core_tools method."""
    tools = wallet_client.get_core_tools()
    assert len(tools) == 6
    tool_names = [tool["name"] for tool in tools]
    assert "get_address" in tool_names
    assert "get_chain" in tool_names
    assert "sign_message" in tool_names
    assert "balance_of" in tool_names
    assert "sign_transaction" in tool_names
    assert "send_transaction" in tool_names
