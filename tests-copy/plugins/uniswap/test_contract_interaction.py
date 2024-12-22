"""
Tests for contract interaction handling in UniswapService.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock, mock_open
from web3.exceptions import ContractLogicError, TransactionNotFound
from web3.types import Wei

from goat_sdk.plugins.uniswap.uniswap_service import (
    UniswapService,
    ContractCallError,
    ContractValidationError,
    ContractExecutionError,
    ContractABIError,
)
from goat_sdk.plugins.uniswap.types import (
    UniswapPluginConfig,
    UniswapVersion,
    PoolFee
)
from tests.base_test import BaseGoatTest


@pytest.mark.asyncio
class TestContractInteraction(BaseGoatTest):
    """Test cases for contract interaction handling."""

    @pytest.fixture
    def mock_abis(self):
        """Mock ABI files."""
        router_abi = [{"type": "function", "name": "swapExactTokensForTokens"}]
        factory_abi = [{"type": "function", "name": "createPair"}]
        quoter_abi = [{"type": "function", "name": "quote"}]
        
        def mock_file_open(file_path, *args, **kwargs):
            if "router.json" in str(file_path):
                return mock_open(read_data=str(router_abi)).return_value
            elif "factory.json" in str(file_path):
                return mock_open(read_data=str(factory_abi)).return_value
            elif "quoter.json" in str(file_path):
                return mock_open(read_data=str(quoter_abi)).return_value
            return mock_open().return_value
        
        return mock_file_open

    @pytest.fixture
    def uniswap_config(self):
        """Create a mock Uniswap config."""
        return UniswapPluginConfig(
            version=UniswapVersion.V3,
            router_address="0x1234",
            factory_address="0x5678",
            quoter_address="0x9012",
            default_slippage=0.005,
            default_deadline_minutes=20,
            max_hops=3,
            supported_fee_tiers=[PoolFee.LOW, PoolFee.MEDIUM, PoolFee.HIGH]
        )

    @pytest.fixture
    async def uniswap_service(self, web3_mock, uniswap_config, mock_abis):
        """Create a UniswapService instance with mocked dependencies."""
        with patch("builtins.open", mock_abis):
            service = await UniswapService.create(uniswap_config, web3_mock)
            return service

    async def test_contract_call_success(self, uniswap_service, mock_contract_factory):
        """Test successful contract call."""
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=100
        )

        result = await uniswap_service._call_contract(
            mock_contract,
            "testFunction",
            validation_func=lambda x: x == 100
        )
        assert result == 100

    async def test_contract_call_retry_success(self, uniswap_service, mock_contract_factory):
        """Test contract call succeeds after retries."""
        mock_function = AsyncMock()
        mock_function.call.side_effect = [
            TransactionNotFound("Not found"),
            TransactionNotFound("Not found"),
            100
        ]
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        result = await uniswap_service._call_contract(
            mock_contract,
            "testFunction"
        )
        assert result == 100
        assert mock_function.call.call_count == 3

    async def test_contract_call_validation_error(self, uniswap_service, mock_contract_factory):
        """Test contract call fails validation."""
        mock_function = AsyncMock()
        mock_function.call.return_value = 100
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        with pytest.raises(ContractCallError):
            await uniswap_service._call_contract(
                mock_contract,
                "testFunction",
                validation_func=lambda x: x == 200
            )

    async def test_contract_call_execution_error(self, uniswap_service, mock_contract_factory):
        """Test contract call execution error."""
        mock_function = AsyncMock()
        mock_function.call.side_effect = ContractLogicError("revert: execution failed")
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        with pytest.raises(ContractExecutionError):
            await uniswap_service._call_contract(
                mock_contract,
                "testFunction"
            )

    async def test_contract_call_max_retries_exceeded(self, uniswap_service, mock_contract_factory):
        """Test contract call fails after max retries."""
        mock_function = AsyncMock()
        mock_function.call.side_effect = TransactionNotFound("Not found")
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        with pytest.raises(ContractCallError):
            await uniswap_service._call_contract(
                mock_contract,
                "testFunction"
            )

    async def test_contract_validation_success(self, uniswap_service, mock_contract_factory):
        """Test successful contract validation."""
        mock_name = AsyncMock()
        mock_name.call.return_value = "Test Contract"
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "name"}],
            name=mock_name
        )

        await uniswap_service._validate_and_cache_contract(mock_contract, "0x1234")
        mock_name.call.assert_called_once()

    async def test_contract_validation_failure(self, uniswap_service, mock_contract_factory):
        """Test contract validation failure."""
        mock_name = AsyncMock()
        mock_name.call.side_effect = ContractLogicError("revert: not deployed")
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "name"}],
            name=mock_name
        )

        with pytest.raises(ContractValidationError):
            await uniswap_service._validate_and_cache_contract(mock_contract, "0x1234")

    async def test_abi_loading_fallback(self, uniswap_service):
        """Test ABI loading with fallback to minimal ABI."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            abi = await uniswap_service._load_abi("erc20.json")
            assert any(func.get("name") == "transfer" for func in abi)

    async def test_contract_call_with_args(self, uniswap_service, mock_contract_factory):
        """Test contract call with arguments."""
        mock_function = AsyncMock()
        mock_function.call.return_value = 100
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        result = await uniswap_service._call_contract(
            mock_contract,
            "testFunction",
            10,  # arg1
            20   # arg2
        )
        assert result == 100
        mock_function.call.assert_called_once()

    async def test_contract_call_with_kwargs(self, uniswap_service, mock_contract_factory):
        """Test contract call with keyword arguments."""
        mock_function = AsyncMock()
        mock_function.call.return_value = 100
        mock_contract = mock_contract_factory(
            "0x1234",
            [{"type": "function", "name": "testFunction", "outputs": [{"type": "uint256"}]}],
            testFunction=mock_function
        )

        result = await uniswap_service._call_contract(
            mock_contract,
            "testFunction",
            param1=10,
            param2=20
        )
        assert result == 100
        mock_function.call.assert_called_once()
