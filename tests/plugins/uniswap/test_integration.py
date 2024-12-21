"""
Integration tests for Uniswap plugin.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal
from web3 import Web3

from goat_sdk.plugins.uniswap.enhanced_validation import (
    EnhancedTokenAmount,
    EnhancedSlippageSettings,
    EnhancedGasSettings,
    EnhancedRouteValidation,
    EnhancedSwapValidation,
)
from goat_sdk.plugins.uniswap.uniswap_service import UniswapService

@pytest.fixture
def web3_mock():
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
def uniswap_service(web3_mock):
    return UniswapService(web3_mock)

@pytest.mark.asyncio
async def test_complete_swap_flow(uniswap_service, web3_mock):
    """Test complete swap flow."""
    # Mock contract interactions
    contract_mock = Mock()
    contract_mock.functions.factory.return_value.call = AsyncMock(return_value="0x1234")
    contract_mock.functions.token0.return_value.call = AsyncMock(return_value="0x5678")
    contract_mock.functions.token1.return_value.call = AsyncMock(return_value="0x9abc")
    contract_mock.functions.fee.return_value.call = AsyncMock(return_value=3000)
    contract_mock.functions.liquidity.return_value.call = AsyncMock(return_value=1000000)
    contract_mock.functions.slot0.return_value.call = AsyncMock(
        return_value=(1000000, 0, 0, 0, 0, 0, True)
    )
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        # Test swap execution
        amount_in = EnhancedTokenAmount(amount=Decimal("1.0"), decimals=18)
        slippage = EnhancedSlippageSettings(slippage_tolerance=Decimal("0.5"))
        gas = EnhancedGasSettings(
            max_fee_per_gas=Decimal("100"),
            max_priority_fee_per_gas=Decimal("2"),
            gas_limit=200000
        )
        route = EnhancedRouteValidation(
            path=["0x1234", "0x5678"],
            pools=["0x9abc"]
        )
        
        swap = EnhancedSwapValidation(
            token_in="0x1234",
            token_out="0x5678",
            amount_in=amount_in,
            route=route,
            slippage=slippage,
            gas=gas
        )
        
        result = await uniswap_service.execute_swap(swap)
        assert result is not None
        assert "txHash" in result

@pytest.mark.asyncio
async def test_multi_hop_swap(uniswap_service, web3_mock):
    """Test multi-hop swap."""
    # Mock contract interactions
    contract_mock = Mock()
    contract_mock.functions.factory.return_value.call = AsyncMock(return_value="0x1234")
    contract_mock.functions.token0.return_value.call = AsyncMock(return_value="0x5678")
    contract_mock.functions.token1.return_value.call = AsyncMock(return_value="0x9abc")
    contract_mock.functions.fee.return_value.call = AsyncMock(return_value=3000)
    contract_mock.functions.liquidity.return_value.call = AsyncMock(return_value=1000000)
    contract_mock.functions.slot0.return_value.call = AsyncMock(
        return_value=(1000000, 0, 0, 0, 0, 0, True)
    )
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        # Test multi-hop swap
        amount_in = EnhancedTokenAmount(amount=Decimal("1.0"), decimals=18)
        slippage = EnhancedSlippageSettings(slippage_tolerance=Decimal("0.5"))
        gas = EnhancedGasSettings(
            max_fee_per_gas=Decimal("100"),
            max_priority_fee_per_gas=Decimal("2"),
            gas_limit=300000
        )
        route = EnhancedRouteValidation(
            path=["0x1234", "0x5678", "0xdef0"],
            pools=["0x9abc", "0x1234"]
        )
        
        swap = EnhancedSwapValidation(
            token_in="0x1234",
            token_out="0xdef0",
            amount_in=amount_in,
            route=route,
            slippage=slippage,
            gas=gas
        )
        
        result = await uniswap_service.execute_swap(swap)
        assert result is not None
        assert "txHash" in result

@pytest.mark.asyncio
async def test_swap_with_price_impact_protection(uniswap_service, web3_mock):
    """Test swap with price impact protection."""
    # Mock contract interactions
    contract_mock = Mock()
    contract_mock.functions.factory.return_value.call = AsyncMock(return_value="0x1234")
    contract_mock.functions.token0.return_value.call = AsyncMock(return_value="0x5678")
    contract_mock.functions.token1.return_value.call = AsyncMock(return_value="0x9abc")
    contract_mock.functions.fee.return_value.call = AsyncMock(return_value=3000)
    contract_mock.functions.liquidity.return_value.call = AsyncMock(return_value=1000000)
    contract_mock.functions.slot0.return_value.call = AsyncMock(
        return_value=(1000000, 0, 0, 0, 0, 0, True)
    )
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        # Test swap with price impact protection
        amount_in = EnhancedTokenAmount(amount=Decimal("100.0"), decimals=18)
        slippage = EnhancedSlippageSettings(slippage_tolerance=Decimal("0.1"))
        gas = EnhancedGasSettings(
            max_fee_per_gas=Decimal("100"),
            max_priority_fee_per_gas=Decimal("2"),
            gas_limit=200000
        )
        route = EnhancedRouteValidation(
            path=["0x1234", "0x5678"],
            pools=["0x9abc"]
        )
        
        swap = EnhancedSwapValidation(
            token_in="0x1234",
            token_out="0x5678",
            amount_in=amount_in,
            route=route,
            slippage=slippage,
            gas=gas
        )
        
        # Should raise error due to high price impact
        with pytest.raises(ValueError, match="price impact too high"):
            await uniswap_service.execute_swap(swap)

@pytest.mark.asyncio
async def test_swap_with_mev_protection(uniswap_service, web3_mock):
    """Test swap with MEV protection."""
    # Mock contract interactions
    contract_mock = Mock()
    contract_mock.functions.factory.return_value.call = AsyncMock(return_value="0x1234")
    contract_mock.functions.token0.return_value.call = AsyncMock(return_value="0x5678")
    contract_mock.functions.token1.return_value.call = AsyncMock(return_value="0x9abc")
    contract_mock.functions.fee.return_value.call = AsyncMock(return_value=3000)
    contract_mock.functions.liquidity.return_value.call = AsyncMock(return_value=1000000)
    contract_mock.functions.slot0.return_value.call = AsyncMock(
        return_value=(1000000, 0, 0, 0, 0, 0, True)
    )
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        # Test swap with MEV protection
        amount_in = EnhancedTokenAmount(amount=Decimal("1.0"), decimals=18)
        slippage = EnhancedSlippageSettings(slippage_tolerance=Decimal("0.5"))
        gas = EnhancedGasSettings(
            max_fee_per_gas=Decimal("200"),  # Higher gas to outbid MEV bots
            max_priority_fee_per_gas=Decimal("5"),
            gas_limit=200000
        )
        route = EnhancedRouteValidation(
            path=["0x1234", "0x5678"],
            pools=["0x9abc"]
        )
        
        swap = EnhancedSwapValidation(
            token_in="0x1234",
            token_out="0x5678",
            amount_in=amount_in,
            route=route,
            slippage=slippage,
            gas=gas
        )
        
        result = await uniswap_service.execute_swap(swap)
        assert result is not None
        assert "txHash" in result

@pytest.mark.asyncio
async def test_gas_optimization(uniswap_service, web3_mock):
    """Test gas optimization."""
    # Mock gas price and priority fee
    web3_mock.eth.gas_price.return_value = 50 * 10**9  # 50 gwei
    web3_mock.eth.max_priority_fee.return_value = 2 * 10**9  # 2 gwei
    web3_mock.eth.fee_history.return_value = {
        "baseFeePerGas": [40 * 10**9],
        "reward": [[2 * 10**9]],
    }
    
    # Test gas optimization
    optimized_gas = await uniswap_service.optimize_gas_settings()
    assert isinstance(optimized_gas, EnhancedGasSettings)
    assert optimized_gas.max_fee_per_gas is not None
    assert optimized_gas.max_priority_fee_per_gas is not None

@pytest.mark.asyncio
async def test_error_handling(uniswap_service, web3_mock):
    """Test error handling."""
    # Mock contract error
    contract_mock = Mock()
    contract_mock.functions.factory.return_value.call.side_effect = Exception("Contract error")
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        # Test error handling
        amount_in = EnhancedTokenAmount(amount=Decimal("1.0"), decimals=18)
        slippage = EnhancedSlippageSettings(slippage_tolerance=Decimal("0.5"))
        gas = EnhancedGasSettings(
            max_fee_per_gas=Decimal("100"),
            max_priority_fee_per_gas=Decimal("2"),
            gas_limit=200000
        )
        route = EnhancedRouteValidation(
            path=["0x1234", "0x5678"],
            pools=["0x9abc"]
        )
        
        swap = EnhancedSwapValidation(
            token_in="0x1234",
            token_out="0x5678",
            amount_in=amount_in,
            route=route,
            slippage=slippage,
            gas=gas
        )
        
        with pytest.raises(Exception):
            await uniswap_service.execute_swap(swap)
