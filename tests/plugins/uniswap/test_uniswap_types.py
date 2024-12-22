import pytest
from decimal import Decimal
from goat_sdk.plugins.uniswap.types import (
    UniswapPluginConfig, UniswapVersion, PoolFee, TokenInfo, PoolInfo, SwapRoute, Position, PositionFees
)


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


def test_position_initialization():
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
    position = Position(
        token_id=1,
        owner='0xOwner',
        pool=pool,
        liquidity=Decimal('1000'),
        token0_amount=Decimal('500'),
        token1_amount=Decimal('500'),
        fee_tier=PoolFee.LOW
    )
    assert position.token_id == 1
    assert position.owner == '0xOwner'
    assert position.pool == pool


def test_position_fees_initialization():
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
    fees = PositionFees(
        token0_amount=Decimal('10'),
        token1_amount=Decimal('5'),
        token0_info=token0,
        token1_info=token1
    )
    assert fees.token0_amount == Decimal('10')
    assert fees.token1_amount == Decimal('5')
    assert fees.token0_info == token0
    assert fees.token1_info == token1
