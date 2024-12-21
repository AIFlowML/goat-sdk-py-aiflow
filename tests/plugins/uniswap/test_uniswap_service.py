"""
Tests for the Uniswap service implementation.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, AsyncMock, MagicMock, mock_open

from goat_sdk.plugins.uniswap.enhanced_validation import (
    EnhancedTokenAmount,
    EnhancedSlippageSettings,
    EnhancedGasSettings,
    EnhancedRouteValidation,
    EnhancedSwapValidation,
)
from goat_sdk.plugins.uniswap.uniswap_service import UniswapService
from goat_sdk.plugins.uniswap.types import (
    TokenInfo,
    PoolInfo,
    SwapRoute,
    UniswapPluginConfig,
    UniswapVersion,
    PoolFee
)
from tests.base_test import BaseGoatTest


class TestUniswapService(BaseGoatTest):
    """Test cases for UniswapService."""

    @pytest.fixture
    def mock_abis(self):
        """Mock ABI files."""
        router_abi = [{"type": "function", "name": "swapExactTokensForTokens"}]
        factory_abi = [{"type": "function", "name": "createPair"}]
        quoter_abi = [{"type": "function", "name": "quote"}]
        position_manager_abi = [{"type": "function", "name": "positions"}]
        
        def mock_file_open(file_path, *args, **kwargs):
            if "router.json" in str(file_path):
                return mock_open(read_data=str(router_abi)).return_value
            elif "factory.json" in str(file_path):
                return mock_open(read_data=str(factory_abi)).return_value
            elif "quoter.json" in str(file_path):
                return mock_open(read_data=str(quoter_abi)).return_value
            elif "position_manager.json" in str(file_path):
                return mock_open(read_data=str(position_manager_abi)).return_value
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
            default_slippage=Decimal("0.005"),
            default_deadline_minutes=20,
            max_hops=3,
            supported_fee_tiers=[PoolFee.LOW, PoolFee.MEDIUM, PoolFee.HIGH]
        )

    @pytest.fixture
    def uniswap_service(self, web3_mock, uniswap_config, mock_abis):
        """Create a UniswapService instance with mocked dependencies."""
        with patch("builtins.open", mock_abis):
            return UniswapService(uniswap_config, web3_mock)

    def setup_token_contract(self, mock_contract_factory, token_address, name, symbol, decimals):
        return mock_contract_factory(
            token_address,
            [
                {"type": "function", "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"type": "function", "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"type": "function", "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
            ],
            name=name,
            symbol=symbol,
            decimals=decimals
        )

    def setup_pool_contract(self, mock_contract_factory, pool_address, token0, token1, fee, liquidity, sqrt_price_x96):
        return mock_contract_factory(
            pool_address,
            [
                {"type": "function", "name": "token0", "outputs": [{"name": "", "type": "address"}], "type": "function"},
                {"type": "function", "name": "token1", "outputs": [{"name": "", "type": "address"}], "type": "function"},
                {"type": "function", "name": "fee", "outputs": [{"name": "", "type": "uint24"}], "type": "function"},
                {"type": "function", "name": "liquidity", "outputs": [{"name": "", "type": "uint128"}], "type": "function"},
                {"type": "function", "name": "slot0", "outputs": [{"name": "sqrtPriceX96", "type": "uint160"}, {"name": "tick", "type": "int24"}, {"name": "observationIndex", "type": "uint16"}, {"name": "observationCardinality", "type": "uint16"}, {"name": "observationCardinalityNext", "type": "uint16"}, {"name": "feeProtocol", "type": "uint8"}, {"name": "unlocked", "type": "bool"}], "type": "function"}
            ],
            token0=token0,
            token1=token1,
            fee=fee,
            liquidity=liquidity,
            slot0=(sqrt_price_x96, 0, 0, 0, 0, 0, False)
        )

    @pytest.mark.asyncio
    async def test_get_token_info(self, uniswap_service, mock_contract_factory):
        """Test token info fetching."""
        token_address = "0x1234"
        name = "Test Token"
        symbol = "TEST"
        decimals = 18
        chain_id = 1  # Ethereum mainnet

        token = self.setup_token_contract(
            mock_contract_factory,
            token_address,
            name=name,
            symbol=symbol,
            decimals=decimals
        )

        # Create a coroutine for chain_id
        async def mock_chain_id():
            return chain_id

        with patch.object(uniswap_service.web3.eth, "contract", return_value=token):
            with patch.object(uniswap_service.web3.eth, "chain_id", new=mock_chain_id):
                token_info = await uniswap_service.get_token_info(token_address)
                assert token_info.name == name
                assert token_info.symbol == symbol
                assert token_info.decimals == decimals
                assert token_info.chain_id == chain_id

    @pytest.mark.asyncio
    async def test_get_pool_info_v3(self, uniswap_service, mock_contract_factory):
        """Test pool info fetching."""
        pool_address = "0x1234"
        token0_address = "0x5678"
        token1_address = "0x9012"
        fee = 3000
        liquidity = 1000000
        sqrt_price_x96 = 2**96
        chain_id = 1  # Ethereum mainnet

        # Create mock token contracts
        token0 = self.setup_token_contract(
            mock_contract_factory,
            token0_address,
            name="Token0",
            symbol="TKN0",
            decimals=18
        )
        token1 = self.setup_token_contract(
            mock_contract_factory,
            token1_address,
            name="Token1",
            symbol="TKN1",
            decimals=18
        )

        pool = self.setup_pool_contract(
            mock_contract_factory,
            pool_address,
            token0=token0_address,
            token1=token1_address,
            fee=fee,
            liquidity=liquidity,
            sqrt_price_x96=sqrt_price_x96
        )

        # Create a coroutine for chain_id
        async def mock_chain_id():
            return chain_id

        with patch.object(uniswap_service.web3.eth, "contract") as mock_contract:
            def contract_side_effect(address, *args, **kwargs):
                if address == pool_address:
                    return pool
                elif address == token0_address:
                    return token0
                elif address == token1_address:
                    return token1
                return None
            
            mock_contract.side_effect = contract_side_effect
            with patch.object(uniswap_service.web3.eth, "chain_id", new=mock_chain_id):
                pool_info = await uniswap_service.get_pool_info_v3(pool_address)
                assert isinstance(pool_info.token0, TokenInfo)
                assert isinstance(pool_info.token1, TokenInfo)
                assert pool_info.token0.address == token0_address
                assert pool_info.token1.address == token1_address
                assert pool_info.fee == fee
                assert pool_info.liquidity == liquidity
                assert pool_info.sqrt_price_x96 == sqrt_price_x96
                assert pool_info.token0_price == Decimal("1.0")  # Default price for testing
                assert pool_info.token1_price == Decimal("1.0")  # Default price for testing

    @pytest.mark.asyncio
    async def test_find_optimal_routes(self, uniswap_service):
        """Test route finding."""
        token_in = "0x1234"
        token_out = "0x5678"
        amount_in = Decimal("1.0")

        routes = await uniswap_service.find_optimal_routes(token_in, token_out, amount_in)
        assert len(routes) > 0
        assert all(isinstance(route, SwapRoute) for route in routes)

    @pytest.mark.asyncio
    async def test_simulate_swap(self, uniswap_service):
        """Test swap simulation."""
        route = SwapRoute(
            path=["0x1234", "0x5678"],
            pools=["0x9012"],
            amount_in=Decimal("1.0"),
            amount_out=Decimal("0.9"),
            gas_estimate=100000
        )

        result = await uniswap_service.simulate_swap([route])
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].amount_out == route.amount_out

    @pytest.mark.asyncio
    async def test_monitor_mempool(self, uniswap_service):
        """Test mempool monitoring."""
        token_address = "0x1234"
        
        # Mock transaction data
        tx = {
            "hash": "0xabcd",
            "to": uniswap_service.config.router_address,
            "value": 0,
            "input": "0x"  # Mock transaction input data
        }

        # Test monitoring
        result = await uniswap_service.monitor_mempool(token_address)
        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_price_impact_calculation(self, uniswap_service):
        """Test price impact calculation."""
        amount_in = Decimal("1.0")
        amount_out = Decimal("0.9")
        
        # Calculate price impact
        impact = await uniswap_service.calculate_price_impact(amount_in, amount_out)
        assert impact is not None
        assert isinstance(impact, Decimal)
        assert impact >= 0
