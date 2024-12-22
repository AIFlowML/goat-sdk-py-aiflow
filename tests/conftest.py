"""
Global pytest configuration and fixtures for GOAT SDK.
"""
import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock
from decimal import Decimal
from web3 import Web3
from goat_sdk.core.config import GoatConfig
import asyncio

class MockProvider:
    """Base class for mock providers."""
    def __init__(self, chain_id: int = 1):
        self.chain_id = chain_id
        self.calls: list = []
        self.responses: Dict[str, Any] = {}

    def record_call(self, method: str, params: Any):
        """Record method call for testing."""
        self.calls.append({"method": method, "params": params})

    def set_response(self, method: str, response: Any):
        """Set mock response for method."""
        self.responses[method] = response

    def get_calls(self, method: Optional[str] = None) -> list:
        """Get recorded calls, optionally filtered by method."""
        if method:
            return [call for call in self.calls if call["method"] == method]
        return self.calls

@pytest.fixture
def mock_provider():
    """Fixture for mock provider."""
    return MockProvider()

@pytest.fixture
def mock_web3():
    """Fixture for mock Web3 instance."""
    mock = Mock(spec=Web3)
    mock.eth = MagicMock()
    mock.eth.chain_id = 1
    mock.eth.get_code = AsyncMock()
    mock.eth.get_storage_at = AsyncMock()
    mock.eth.get_transaction_receipt = AsyncMock()
    mock.eth.get_block = AsyncMock()
    mock.eth.get_transaction = AsyncMock()
    mock.eth.get_transaction_count = AsyncMock()
    mock.eth.estimate_gas = AsyncMock()
    mock.eth.gas_price = AsyncMock()
    mock.eth.max_priority_fee = AsyncMock()
    mock.eth.fee_history = AsyncMock()
    mock.eth.get_balance = AsyncMock()
    return mock

@pytest.fixture
def test_config():
    """Fixture for test configuration."""
    return GoatConfig(
        eth_network="test",
        eth_rpc_url="http://localhost:8545",
        eth_private_key="1" * 64,
        test_mode=True
    )

class MockContract:
    """Mock for Web3 contract."""
    def __init__(self, address: str, abi: list):
        self.address = address
        self.abi = abi
        self.functions = MagicMock()
        self.events = MagicMock()

@pytest.fixture
def mock_contract():
    """Fixture for mock contract."""
    def _create_contract(address: str, abi: list = None):
        return MockContract(address, abi or [])
    return _create_contract

@pytest.fixture
def mock_token_contract(mock_contract):
    """Fixture for mock ERC20 token contract."""
    contract = mock_contract("0x" + "1" * 40)
    contract.functions.name.return_value.call = AsyncMock(return_value="Test Token")
    contract.functions.symbol.return_value.call = AsyncMock(return_value="TEST")
    contract.functions.decimals.return_value.call = AsyncMock(return_value=18)
    contract.functions.totalSupply.return_value.call = AsyncMock(return_value=1000000)
    contract.functions.balanceOf.return_value.call = AsyncMock(return_value=100000)
    return contract

@pytest.fixture
def mock_pool_contract(mock_contract):
    """Fixture for mock Uniswap V3 pool contract."""
    contract = mock_contract("0x" + "2" * 40)
    contract.functions.token0.return_value.call = AsyncMock(return_value="0x" + "3" * 40)
    contract.functions.token1.return_value.call = AsyncMock(return_value="0x" + "4" * 40)
    contract.functions.fee.return_value.call = AsyncMock(return_value=3000)
    contract.functions.liquidity.return_value.call = AsyncMock(return_value=1000000)
    contract.functions.slot0.return_value.call = AsyncMock(
        return_value=(2**96, 0, 0, 0, 0, 0, True)
    )
    return contract

class TransactionTracker:
    """Helper class to track and verify transactions."""
    def __init__(self):
        self.transactions: list = []
        self.pending_nonce = 0

    def add_transaction(self, tx_hash: str, tx_data: Dict[str, Any]):
        """Record a transaction."""
        self.transactions.append({
            "hash": tx_hash,
            "data": tx_data,
            "nonce": self.pending_nonce
        })
        self.pending_nonce += 1

    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction by hash."""
        for tx in self.transactions:
            if tx["hash"] == tx_hash:
                return tx
        return None

@pytest.fixture
def tx_tracker():
    """Fixture for transaction tracker."""
    return TransactionTracker()

@pytest.fixture
def mock_gas_oracle():
    """Fixture for gas price oracle."""
    class MockGasOracle:
        def __init__(self):
            self.base_fee = 10 * 10**9  # 10 gwei
            self.priority_fee = 2 * 10**9  # 2 gwei

        async def get_gas_price(self) -> Dict[str, int]:
            return {
                "base_fee": self.base_fee,
                "priority_fee": self.priority_fee,
                "max_fee": self.base_fee * 2
            }

    return MockGasOracle()

@pytest.fixture
def mock_mempool():
    """Fixture for mempool monitoring."""
    class MockMempool:
        def __init__(self):
            self.pending_transactions: list = []

        def add_pending_transaction(self, tx_data: Dict[str, Any]):
            self.pending_transactions.append(tx_data)

        async def get_pending_transactions(self) -> list:
            return self.pending_transactions

    return MockMempool()

@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup fixture that runs after each test."""
    yield  # Let the test run
    
    try:
        # Get the current event loop
        loop = asyncio.get_running_loop()
        
        # Cancel all tasks except the current one
        tasks = [t for t in asyncio.all_tasks(loop=loop) 
                if t is not asyncio.current_task(loop=loop)]
        
        if tasks:
            # Cancel all tasks
            for task in tasks:
                task.cancel()
                
            # Wait for all tasks to complete with a timeout
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Wait a bit to ensure tasks are really done
            await asyncio.sleep(0.1)
    except RuntimeError:
        # No running event loop - that's fine
        pass

@pytest.fixture(autouse=True)
def reset_mocks(mock_provider, mock_web3, tx_tracker):
    """Reset all mocks before each test."""
    yield
    mock_provider.calls = []
    mock_provider.responses = {}
    mock_web3.eth.reset_mock()
    tx_tracker.transactions = []
    tx_tracker.pending_nonce = 0

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
