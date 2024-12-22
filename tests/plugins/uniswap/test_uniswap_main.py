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

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from web3 import Web3

from goat_sdk.plugins.uniswap.types import (
    UniswapPluginConfig, UniswapVersion, PoolFee, TokenInfo, 
    PoolInfo, SwapRoute, Position, PositionFees
)
from goat_sdk.plugins.uniswap.advanced_security import TokenSecurityChecker
from goat_sdk.plugins.uniswap.uniswap_service import UniswapService

# Fixtures
@pytest.fixture
async def mock_web3():
    with patch('web3.Web3') as MockWeb3:
        mock_instance = MockWeb3.return_value
        mock_instance.eth.get_code = AsyncMock(return_value=b'')
        mock_instance.eth.get_storage_at = AsyncMock(return_value=b'')
        yield mock_instance

@pytest.fixture
async def token_security_checker(mock_web3):
    return TokenSecurityChecker(web3=mock_web3)

@pytest.fixture
async def uniswap_service(mock_web3):
    """Create a UniswapService instance for testing."""
    config = {
        "version": UniswapVersion.V3,
        "router_address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "factory_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "quoter_address": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
        "position_manager_address": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "default_slippage": Decimal("0.005"),
        "default_deadline_minutes": 20,
        "max_hops": 3,
        "supported_fee_tiers": None
    }
    
    # Create the config object first
    config_obj = UniswapPluginConfig(**config)
    
    # Initialize service with proper parameters
    service = await UniswapService.create(config=config_obj, web3=mock_web3)
    return service

# Uniswap Types Tests
def test_uniswap_plugin_config_defaults():
    config = UniswapPluginConfig(
        version=UniswapVersion.V3,
        router_address='0xRouter',
        factory_address='0xFactory'
    )
    assert config.version == UniswapVersion.V3
    assert config.router_address == '0xRouter'
    assert config.factory_address == '0xFactory'
    assert config.default_slippage == Decimal('0.005')
    assert config.default_deadline_minutes == 20
    assert config.max_hops == 3

def test_token_info_initialization():
    token = TokenInfo(
        address='0xToken',
        symbol='TKN',
        name='Token',
        decimals=18,
        chain_id=1
    )
    assert token.address == '0xToken'
    assert token.symbol == 'TKN'
    assert token.name == 'Token'
    assert token.decimals == 18
    assert token.chain_id == 1

def test_pool_info_initialization():
    token0 = TokenInfo(
        address='0xToken0',
        symbol='TKN0',
        name='Token0',
        decimals=18,
        chain_id=1
    )
    token1 = TokenInfo(
        address='0xToken1',
        symbol='TKN1',
        name='Token1',
        decimals=18,
        chain_id=1
    )
    pool = PoolInfo(
        address='0xPool',
        token0=token0,
        token1=token1,
        fee=PoolFee.LOW,
        liquidity=Decimal('1000'),
        token0_price=Decimal('1'),
        token1_price=Decimal('1')
    )
    assert pool.address == '0xPool'
    assert pool.token0 == token0
    assert pool.token1 == token1
    assert pool.fee == PoolFee.LOW

def test_swap_route_initialization():
    route = SwapRoute(
        path=['0xTokenA', '0xTokenB'],
        pools=['0xPoolA', '0xPoolB'],
        fees=[PoolFee.LOW, PoolFee.MEDIUM],
        input_amount=Decimal('10'),
        output_amount=Decimal('9.5'),
        price_impact=Decimal('0.05'),
        minimum_output=Decimal('9'),
        gas_estimate=21000
    )
    assert route.path == ['0xTokenA', '0xTokenB']
    assert route.pools == ['0xPoolA', '0xPoolB']
    assert route.fees == [PoolFee.LOW, PoolFee.MEDIUM]

# UniswapService Tests
@pytest.mark.asyncio
async def test_get_token_info(uniswap_service, mock_web3):
    mock_web3.eth.contract.return_value.functions.name.return_value.call.return_value = 'Test Token'
    mock_web3.eth.contract.return_value.functions.symbol.return_value.call.return_value = 'TEST'
    mock_web3.eth.contract.return_value.functions.decimals.return_value.call.return_value = 18
    
    token_info = await uniswap_service.get_token_info('0x1234567890123456789012345678901234567890')
    assert token_info.name == 'Test Token'
    assert token_info.symbol == 'TEST'
    assert token_info.decimals == 18

@pytest.mark.asyncio
async def test_get_pool_info_v3(uniswap_service, mock_web3):
    # Mock pool data
    pool_address = '0x3333333333333333333333333333333333333333'
    mock_web3.eth.contract.return_value.functions.token0.return_value.call.return_value = '0x1111111111111111111111111111111111111111'
    mock_web3.eth.contract.return_value.functions.token1.return_value.call.return_value = '0x2222222222222222222222222222222222222222'
    mock_web3.eth.contract.return_value.functions.fee.return_value.call.return_value = 3000
    mock_web3.eth.contract.return_value.functions.liquidity.return_value.call.return_value = 1000000
    mock_web3.eth.contract.return_value.functions.slot0.return_value.call.return_value = [2**96, 0, 0, 0, 0, 0, 0]
    
    pool_info = await uniswap_service.get_pool_info_v3(pool_address)
    
    # Check token addresses
    assert pool_info.token0.address == '0x1111111111111111111111111111111111111111'
    assert pool_info.token1.address == '0x2222222222222222222222222222222222222222'
    assert pool_info.fee == PoolFee.MEDIUM
    assert pool_info.liquidity == 1000000

@pytest.mark.asyncio
async def test_find_optimal_routes(uniswap_service, mock_web3):
    # Mock necessary contract calls
    mock_web3.eth.contract.return_value.functions.factory.return_value.call.return_value = uniswap_service.config.factory_address
    mock_web3.eth.contract.return_value.functions.pool.return_value.call.return_value = '0x4444444444444444444444444444444444444444'
    mock_web3.eth.contract.return_value.functions.quote.return_value.call.return_value = [10**18, 0]
    
    routes = await uniswap_service.find_optimal_routes(
        token_in='0x1111111111111111111111111111111111111111',
        token_out='0x2222222222222222222222222222222222222222',
        amount_in=Decimal('1.0')
    )
    assert len(routes) > 0
    assert isinstance(routes[0], SwapRoute)
    assert routes[0].input_amount == Decimal('1.0')
    assert routes[0].output_amount > 0

@pytest.mark.asyncio
async def test_calculate_price_impact(uniswap_service, mock_web3):
    # Mock pool data for price impact calculation
    mock_web3.eth.contract.return_value.functions.slot0.return_value.call.return_value = [2**96, 0, 0, 0, 0, 0, 0]
    mock_web3.eth.contract.return_value.functions.liquidity.return_value.call.return_value = 1000000
    
    price_impact = await uniswap_service.calculate_price_impact(
        token_in='0x1111111111111111111111111111111111111111',
        token_out='0x2222222222222222222222222222222222222222',
        amount_in=Decimal('1.0')
    )
    assert isinstance(price_impact, Decimal)
    assert price_impact >= 0

@pytest.mark.asyncio
async def test_simulate_swap(uniswap_service, mock_web3):
    # Mock data
    token_in = '0x1111111111111111111111111111111111111111'
    token_out = '0x2222222222222222222222222222222222222222'
    amount_in = Decimal('1.0')
    
    # Simulate swap
    result = await uniswap_service.simulate_swap(token_in, token_out, amount_in)
    
    # Verify the swap route properties
    assert isinstance(result, SwapRoute)
    assert result.path == [token_in, token_out]
    assert result.input_amount == amount_in
    assert result.output_amount == Decimal('0.95')  # Based on mock data
    assert result.price_impact == Decimal('0.05')

@pytest.mark.asyncio
async def test_monitor_mempool(uniswap_service, mock_web3):
    # Mock pending transactions
    mock_web3.eth.get_block.return_value = {
        'transactions': [
            '0x1111111111111111111111111111111111111111111111111111111111111111',
            '0x2222222222222222222222222222222222222222222222222222222222222222'
        ]
    }
    
    # Monitor mempool
    transactions = await uniswap_service.monitor_mempool()
    
    # Verify the transaction data structure
    assert isinstance(transactions, dict)
    assert 'swaps' in transactions
    assert 'liquidity_changes' in transactions
    assert isinstance(transactions['swaps'], list)
    assert isinstance(transactions['liquidity_changes'], list)

# Token Security Tests
@pytest.mark.asyncio
async def test_verify_token_no_code(token_security_checker):
    result, reason = await token_security_checker.verify_token('0x0000000000000000000000000000000000000000')
    assert not result
    assert reason == "No contract code found"

@pytest.mark.asyncio
async def test_verify_token_malicious_pattern(token_security_checker, mock_web3):
    mock_web3.eth.get_code = AsyncMock(return_value=b'\xde\xad\xbe\xef' + b'selfdestruct')
    mock_web3.eth.contract.return_value.functions.name.return_value.call.return_value = 'TestToken'
    mock_web3.eth.contract.return_value.functions.symbol.return_value.call.return_value = 'TT'
    mock_web3.eth.contract.return_value.functions.decimals.return_value.call.return_value = 18
    mock_web3.eth.contract.return_value.functions.totalSupply.return_value.call.return_value = 1000000
    with patch.object(TokenSecurityChecker, '_analyze_pattern_context', return_value=True):
        result, reason = await token_security_checker.verify_token('0x0000000000000000000000000000000000000000')
        assert not result
        assert "Malicious pattern detected" in reason

@pytest.mark.asyncio
async def test_is_proxy_contract(token_security_checker):
    code = bytes.fromhex('363d3d373d3d3d363d73')
    assert token_security_checker._is_proxy_contract(code)

@pytest.mark.asyncio
async def test_get_implementation_address(token_security_checker, mock_web3):
    mock_web3.eth.get_storage_at = AsyncMock(return_value=b'\x00' * 12 + bytes.fromhex('0000000000000000000000000000000000000001'))
    address = await token_security_checker._get_implementation_address('0x0000000000000000000000000000000000000000')
    assert address == Web3.to_checksum_address('0x0000000000000000000000000000000000000001')

@pytest.mark.asyncio
async def test_call_async(token_security_checker):
    async def sample_func():
        return 'test'
    result = await token_security_checker._call_async(sample_func)
    assert result == 'test'