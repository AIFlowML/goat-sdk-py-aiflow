
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

"""
Base test class for GOAT SDK tests.
Provides common functionality and fixtures for all plugin tests.
"""
import pytest
from typing import Optional, Dict, Any, Type
from unittest.mock import Mock, AsyncMock, MagicMock
from decimal import Decimal
from web3 import Web3
from solana.rpc.async_api import AsyncClient as SolanaClient
import asyncio

from goat_sdk.core.config import GoatConfig
from tests.test_helpers import (
    TransactionBuilder,
    EventSimulator,
    PriceSimulator,
    GasSimulator,
    NetworkSimulator,
)

class MockContractFunction:
    def __init__(self, return_value):
        self._return_value = return_value

    def call(self):
        return self._return_value

class AsyncContractFunction:
    def __init__(self, return_value):
        self._return_value = return_value

    async def __call__(self, *args, **kwargs):
        if asyncio.iscoroutine(self._return_value):
            return await self._return_value
        return self._return_value

    def call(self):
        if asyncio.iscoroutine(self._return_value):
            return self._return_value
        return self._return_value

class AsyncContractFunctions:
    def __init__(self, functions_dict):
        self._functions = functions_dict

    def __getattr__(self, name):
        if name in self._functions:
            return AsyncContractFunction(self._functions[name])
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class BaseGoatTest:
    """Base test class for all GOAT SDK tests."""
    
    @pytest.fixture
    def config(self):
        """Base configuration fixture."""
        return GoatConfig(
            eth_network="test",
            eth_rpc_url="http://localhost:8545",
            eth_private_key="1" * 64,
            test_mode=True
        )

    @pytest.fixture
    def mock_contract_factory(self):
        """Contract factory fixture."""
        def create_mock_contract(address: str, abi: list, **kwargs):
            mock_contract = MagicMock()
            
            # Create a dictionary of function names and their return values
            functions_dict = {}
            for item in abi:
                if item["type"] == "function":
                    func_name = item["name"]
                    functions_dict[func_name] = kwargs.get(func_name)

            # Create the AsyncContractFunctions instance
            mock_contract.functions = AsyncContractFunctions(functions_dict)
            mock_contract.address = address
            mock_contract.abi = abi
            return mock_contract
        return create_mock_contract

    @pytest.fixture
    def web3_mock(self, config, mock_contract_factory):
        """Web3 mock fixture."""
        mock = Mock(spec=Web3)
        mock.eth = MagicMock()
        mock.eth.chain_id = AsyncMock(return_value=1)  # Make chain_id async
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
        mock.provider_url = config.eth_rpc_url
        mock.private_key = config.eth_private_key

        # Add contract method
        mock.eth.contract = mock_contract_factory

        return mock

    @pytest.fixture
    def solana_mock(self):
        """Solana client mock fixture."""
        mock = AsyncMock(spec=SolanaClient)
        mock.get_account_info = AsyncMock()
        mock.get_balance = AsyncMock()
        mock.get_token_accounts_by_owner = AsyncMock()
        mock.get_minimum_balance_for_rent_exemption = AsyncMock()
        return mock

    @pytest.fixture
    def tx_builder(self):
        """Transaction builder fixture."""
        return TransactionBuilder()

    @pytest.fixture
    def event_sim(self):
        """Event simulator fixture."""
        return EventSimulator()

    @pytest.fixture
    def price_sim(self):
        """Price simulator fixture."""
        return PriceSimulator()

    @pytest.fixture
    def gas_sim(self):
        """Gas simulator fixture."""
        return GasSimulator()

    @pytest.fixture
    def network_sim(self):
        """Network simulator fixture."""
        return NetworkSimulator()

    def setup_token_contract(
        self,
        mock_contract_factory,
        address: str,
        name: str = "Test Token",
        symbol: str = "TEST",
        decimals: int = 18,
        total_supply: int = 1000000
    ):
        """Helper to setup a token contract mock."""
        return mock_contract_factory(
            address=address,
            abi=[
                {"type": "function", "name": "name", "outputs": [{"type": "string"}], "inputs": []},
                {"type": "function", "name": "symbol", "outputs": [{"type": "string"}], "inputs": []},
                {"type": "function", "name": "decimals", "outputs": [{"type": "uint8"}], "inputs": []},
                {"type": "function", "name": "totalSupply", "outputs": [{"type": "uint256"}], "inputs": []},
                {"type": "function", "name": "balanceOf", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}]},
                {"type": "function", "name": "allowance", "outputs": [{"type": "uint256"}], "inputs": [{"type": "address"}, {"type": "address"}]},
                {"type": "function", "name": "approve", "outputs": [{"type": "bool"}], "inputs": [{"type": "address"}, {"type": "uint256"}]},
                {"type": "function", "name": "transfer", "outputs": [{"type": "bool"}], "inputs": [{"type": "address"}, {"type": "uint256"}]},
                {"type": "function", "name": "transferFrom", "outputs": [{"type": "bool"}], "inputs": [{"type": "address"}, {"type": "address"}, {"type": "uint256"}]}
            ],
            name=name,
            symbol=symbol,
            decimals=decimals,
            totalSupply=total_supply,
            balanceOf=total_supply // 2,
            allowance=total_supply,
            approve=True,
            transfer=True,
            transferFrom=True
        )

    def setup_pool_contract(
        self,
        mock_contract_factory,
        address: str,
        token0: str,
        token1: str,
        fee: int = 3000,
        liquidity: int = 1000000,
        sqrt_price_x96: int = 2**96
    ):
        """Helper to setup a pool contract mock."""
        return mock_contract_factory(
            address=address,
            abi=[
                {"type": "function", "name": "token0", "outputs": [{"type": "address"}], "inputs": []},
                {"type": "function", "name": "token1", "outputs": [{"type": "address"}], "inputs": []},
                {"type": "function", "name": "fee", "outputs": [{"type": "uint24"}], "inputs": []},
                {"type": "function", "name": "liquidity", "outputs": [{"type": "uint128"}], "inputs": []},
                {"type": "function", "name": "slot0", "outputs": [{"type": "uint160"}, {"type": "int24"}, {"type": "uint16"}, {"type": "uint16"}, {"type": "uint16"}, {"type": "uint16"}, {"type": "bool"}], "inputs": []}
            ],
            token0=token0,
            token1=token1,
            fee=fee,
            liquidity=liquidity,
            slot0=(sqrt_price_x96, 0, 0, 0, 0, 0, True)
        )

    def setup_wallet_mock(
        self,
        mock_contract_factory,
        address: str = "0x" + "1" * 40,
        balance: int = 10**18
    ):
        """Helper to setup a wallet mock."""
        wallet = MagicMock()
        wallet.address = address
        wallet.get_balance = AsyncMock(return_value=balance)
        wallet.sign_transaction = AsyncMock()
        wallet.send_transaction = AsyncMock()
        return wallet

    async def assert_reversion(self, coroutine, error_type: Type[Exception]):
        """Helper to assert that a coroutine raises an expected error."""
        with pytest.raises(error_type):
            await coroutine

    def setup_network_conditions(
        self,
        network_sim: NetworkSimulator,
        latency: float = 0.1,
        failure_rate: float = 0.0
    ):
        """Helper to setup network conditions for testing."""
        network_sim.set_conditions(latency, failure_rate)
        return network_sim
