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