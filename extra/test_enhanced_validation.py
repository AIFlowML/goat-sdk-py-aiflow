"""
Tests for enhanced validation features.
"""

import pytest
from decimal import Decimal
from pydantic import ValidationError
from eth_utils import to_checksum_address

from goat_sdk.plugins.uniswap.enhanced_validation import (
    EnhancedEthereumAddress,
    EnhancedTokenAmount,
    EnhancedSlippageSettings,
    EnhancedGasSettings,
    EnhancedRouteValidation,
    EnhancedSwapValidation,
)

def test_ethereum_address_validation():
    """Test Ethereum address validation."""
    
    # Valid address
    valid_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    assert EnhancedEthereumAddress.validate(valid_address) == to_checksum_address(valid_address)
    
    # Invalid addresses
    with pytest.raises(ValueError):
        EnhancedEthereumAddress.validate("0x0000000000000000000000000000000000000000")
    
    with pytest.raises(ValueError):
        EnhancedEthereumAddress.validate("0xinvalid")
    
    with pytest.raises(TypeError):
        EnhancedEthereumAddress.validate(123)

def test_token_amount_validation():
    """Test token amount validation."""
    
    # Valid amount
    valid_amount = EnhancedTokenAmount(
        amount=Decimal("1.23"),
        decimals=18
    )
    assert valid_amount.amount == Decimal("1.23")
    assert valid_amount.decimals == 18
    
    # Invalid amounts
    with pytest.raises(ValidationError):
        EnhancedTokenAmount(amount=Decimal("0"), decimals=18)
    
    with pytest.raises(ValidationError):
        EnhancedTokenAmount(amount=Decimal("1e37"), decimals=18)
    
    with pytest.raises(ValidationError):
        EnhancedTokenAmount(amount=Decimal("1.23"), decimals=19)
    
    # Test decimal places validation
    with pytest.raises(ValidationError):
        EnhancedTokenAmount(amount=Decimal("1.23456"), decimals=4)

def test_slippage_settings_validation():
    """Test slippage settings validation."""
    
    # Valid settings
    valid_settings = EnhancedSlippageSettings(
        tolerance=Decimal("0.005"),
        deadline_minutes=20
    )
    assert valid_settings.tolerance == Decimal("0.005")
    assert valid_settings.deadline_minutes == 20
    
    # Invalid settings
    with pytest.raises(ValidationError):
        EnhancedSlippageSettings(tolerance=Decimal("0.0001"))  # Too low
    
    with pytest.raises(ValidationError):
        EnhancedSlippageSettings(tolerance=Decimal("0.2"))  # Too high
    
    with pytest.raises(ValidationError):
        EnhancedSlippageSettings(deadline_minutes=3)  # Too short
    
    with pytest.raises(ValidationError):
        EnhancedSlippageSettings(deadline_minutes=61)  # Too long

def test_gas_settings_validation():
    """Test gas settings validation."""
    
    # Valid settings
    valid_settings = EnhancedGasSettings(
        max_fee_per_gas=Decimal("100"),
        max_priority_fee_per_gas=Decimal("2"),
        gas_limit=200000
    )
    assert valid_settings.max_fee_per_gas == Decimal("100")
    assert valid_settings.max_priority_fee_per_gas == Decimal("2")
    assert valid_settings.gas_limit == 200000
    
    # Invalid settings
    with pytest.raises(ValidationError):
        EnhancedGasSettings(
            max_fee_per_gas=Decimal("1"),
            max_priority_fee_per_gas=Decimal("2")  # Priority fee > max fee
        )
    
    with pytest.raises(ValidationError):
        EnhancedGasSettings(
            max_fee_per_gas=Decimal("600")  # Too high
        )
    
    with pytest.raises(ValidationError):
        EnhancedGasSettings(
            gas_limit=20000  # Too low
        )

def test_route_validation():
    """Test route validation."""
    
    # Valid route
    valid_route = EnhancedRouteValidation(
        path=[
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        ],
        pools=[
            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        ],
        fees=[3000]
    )
    assert len(valid_route.path) == 2
    assert len(valid_route.pools) == 1
    assert len(valid_route.fees) == 1
    
    # Invalid routes
    with pytest.raises(ValidationError):
        EnhancedRouteValidation(
            path=[
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Only one token
            ],
            pools=[],
            fees=[]
        )
    
    with pytest.raises(ValidationError):
        EnhancedRouteValidation(
            path=[
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Duplicate token
            ],
            pools=[
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            ],
            fees=[3000]
        )
    
    # Test path length validation
    with pytest.raises(ValidationError):
        EnhancedRouteValidation(
            path=["0x742d35Cc6634C0532925a3b844Bc454e4438f44e"] * 5,  # Too long
            pools=["0x742d35Cc6634C0532925a3b844Bc454e4438f44e"] * 4,
            fees=[3000] * 4
        )

def test_swap_validation():
    """Test complete swap validation."""
    
    # Valid swap
    valid_swap = EnhancedSwapValidation(
        route=EnhancedRouteValidation(
            path=[
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "0x6B175474E89094C44Da98b954EedeAC495271d0F"
            ],
            pools=[
                "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            ],
            fees=[3000]
        ),
        token_amount=EnhancedTokenAmount(
            amount=Decimal("1.23"),
            decimals=18
        ),
        recipient="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    )
    assert valid_swap.route.path[0] == "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    
    # Test amount validation for multi-hop
    with pytest.raises(ValidationError):
        EnhancedSwapValidation(
            route=EnhancedRouteValidation(
                path=[
                    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                ],
                pools=[
                    "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                    "0x6B175474E89094C44Da98b954EedeAC495271d0F"
                ],
                fees=[3000, 3000]
            ),
            token_amount=EnhancedTokenAmount(
                amount=Decimal("2000000"),  # Too large for multi-hop
                decimals=18
            )
        )
