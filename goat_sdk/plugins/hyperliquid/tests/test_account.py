"""Tests for account management methods."""

import pytest
from typing import List
import asyncio

from ..plugin import HyperliquidPlugin
from ..types.account import (
    AccountInfo, AccountPosition, MarginInfo,
    LeverageInfo
)

pytestmark = pytest.mark.asyncio

@pytest.mark.skipif(
    not pytest.config.getoption("--run-auth"),
    reason="Requires authentication"
)
class TestAccountManagement:
    """Test account management methods."""
    
    async def test_get_account_info(self, plugin: HyperliquidPlugin, test_address: str):
        """Test getting account information."""
        info = await plugin.get_account_info(testnet=True)
        assert isinstance(info, AccountInfo)
        assert info.address.lower() == test_address.lower()
        assert info.equity >= 0
        assert info.free_collateral >= 0
        assert info.total_collateral >= 0
        assert info.margin_ratio >= 0
        assert isinstance(info.positions, list)
        
    async def test_get_positions(self, plugin: HyperliquidPlugin):
        """Test getting positions."""
        positions = await plugin.get_positions(testnet=True)
        assert isinstance(positions, list)
        
        # Test filtering by coin
        btc_positions = await plugin.get_positions("BTC", testnet=True)
        assert isinstance(btc_positions, list)
        assert all(pos.coin == "BTC" for pos in btc_positions)
        
        # Check position fields if any exist
        for position in positions:
            assert isinstance(position, AccountPosition)
            assert position.coin
            assert position.size is not None
            assert position.entry_price >= 0
            assert position.mark_price > 0
            assert position.side in ["Long", "Short"]
            
    async def test_get_margin_info(self, plugin: HyperliquidPlugin):
        """Test getting margin information."""
        # Get general margin info
        margin_info = await plugin.get_margin_info(testnet=True)
        assert isinstance(margin_info, MarginInfo)
        assert margin_info.initial_margin >= 0
        assert margin_info.maintenance_margin >= 0
        assert margin_info.margin_ratio >= 0
        
        # Get margin info for specific coin
        btc_margin = await plugin.get_margin_info("BTC", testnet=True)
        assert isinstance(btc_margin, MarginInfo)
        
    async def test_get_leverage_info(self, plugin: HyperliquidPlugin):
        """Test getting leverage information."""
        leverage_info = await plugin.get_leverage_info("BTC", testnet=True)
        assert isinstance(leverage_info, LeverageInfo)
        assert leverage_info.current >= 1
        assert leverage_info.max >= leverage_info.current
        assert leverage_info.used >= 0
        assert leverage_info.available >= 0
        
    async def test_set_leverage(self, plugin: HyperliquidPlugin):
        """Test setting leverage."""
        # Get current leverage info
        initial_info = await plugin.get_leverage_info("BTC", testnet=True)
        
        # Try to set to a new value
        new_leverage = min(initial_info.max, initial_info.current + 1)
        success = await plugin.set_leverage("BTC", new_leverage, testnet=True)
        assert success
        
        # Verify change
        updated_info = await plugin.get_leverage_info("BTC", testnet=True)
        assert updated_info.current == new_leverage
        
        # Reset to original
        await plugin.set_leverage("BTC", initial_info.current, testnet=True)
        
    async def test_get_funding_payments(self, plugin: HyperliquidPlugin):
        """Test getting funding payments."""
        # Get recent funding payments
        payments = await plugin.get_funding_payments(
            coin="BTC",
            limit=5,
            testnet=True
        )
        assert isinstance(payments, list)
        assert len(payments) <= 5
        
        # Check payment fields if any exist
        for payment in payments:
            assert isinstance(payment, dict)
            assert "timestamp" in payment
            assert "amount" in payment
            assert "rate" in payment
            
    async def test_get_transaction_history(self, plugin: HyperliquidPlugin):
        """Test getting transaction history."""
        # Get recent transactions
        transactions = await plugin.get_transaction_history(
            limit=5,
            testnet=True
        )
        assert isinstance(transactions, list)
        assert len(transactions) <= 5
        
        # Check transaction fields if any exist
        for tx in transactions:
            assert isinstance(tx, dict)
            assert "timestamp" in tx
            assert "type" in tx
            assert "amount" in tx