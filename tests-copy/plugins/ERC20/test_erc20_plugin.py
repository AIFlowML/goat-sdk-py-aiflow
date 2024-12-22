"""
Tests for the ERC20 plugin implementation.
"""

import pytest
from decimal import Decimal
from unittest.mock import patch, AsyncMock

from goat_sdk.plugins.ERC20.erc20_plugin import ERC20Plugin
from goat_sdk.plugins.ERC20.types import (
    TokenInfo,
    TransferParameters,
    ApprovalParameters,
)
from tests.base_test import BaseGoatTest


class TestERC20Plugin(BaseGoatTest):
    """Test cases for ERC20Plugin."""

    @pytest.fixture
    def erc20_plugin(self, web3_mock, config):
        """Create an ERC20Plugin instance with mocked dependencies."""
        web3_mock.network = "ethereum"
        return ERC20Plugin(web3_mock)

    @pytest.mark.asyncio
    async def test_get_token_info(self, erc20_plugin, mock_contract_factory):
        """Test token info fetching."""
        token_address = "0x1234"
        mock_token = self.setup_token_contract(
            mock_contract_factory,
            token_address,
            name="Test Token",
            symbol="TEST",
            decimals=18
        )

        with patch("web3.eth.Contract", return_value=mock_token):
            token_info = await erc20_plugin.get_token_info(token_address)
            assert token_info.name == "Test Token"
            assert token_info.symbol == "TEST"
            assert token_info.decimals == 18

    @pytest.mark.asyncio
    async def test_get_balance(self, erc20_plugin, mock_contract_factory):
        """Test balance fetching."""
        token_address = "0x1234"
        wallet_address = "0x5678"
        mock_token = self.setup_token_contract(
            mock_contract_factory,
            token_address,
            total_supply=1000000
        )

        with patch("web3.eth.Contract", return_value=mock_token):
            balance = await erc20_plugin.get_balance(token_address, wallet_address)
            assert balance == 500000  # Half of total supply as defined in setup_token_contract

    @pytest.mark.asyncio
    async def test_transfer(self, erc20_plugin, mock_contract_factory, gas_sim):
        """Test token transfer."""
        token_address = "0x1234"
        to_address = "0x5678"
        amount = Decimal("100.0")

        # Setup gas simulation
        gas_sim.set_gas_price(20 * 10**9, 2 * 10**9)  # 20 gwei base, 2 gwei priority
        gas_sim.set_estimate("transfer", 65000)

        mock_token = self.setup_token_contract(
            mock_contract_factory,
            token_address
        )

        with patch("web3.eth.Contract", return_value=mock_token):
            transfer_params = TransferParameters(
                token_address=token_address,
                to_address=to_address,
                amount=amount,
                gas_limit=65000,
                max_fee_per_gas=Decimal("100"),
                max_priority_fee_per_gas=Decimal("2")
            )
            
            tx_hash = await erc20_plugin.transfer(transfer_params)
            assert tx_hash is not None

    @pytest.mark.asyncio
    async def test_approve(self, erc20_plugin, mock_contract_factory, gas_sim):
        """Test token approval."""
        token_address = "0x1234"
        spender_address = "0x5678"
        amount = Decimal("1000.0")

        # Setup gas simulation
        gas_sim.set_gas_price(20 * 10**9, 2 * 10**9)  # 20 gwei base, 2 gwei priority
        gas_sim.set_estimate("approve", 46000)

        mock_token = self.setup_token_contract(
            mock_contract_factory,
            token_address
        )

        with patch("web3.eth.Contract", return_value=mock_token):
            approval_params = ApprovalParameters(
                token_address=token_address,
                spender_address=spender_address,
                amount=amount,
                gas_limit=46000,
                max_fee_per_gas=Decimal("100"),
                max_priority_fee_per_gas=Decimal("2")
            )
            
            tx_hash = await erc20_plugin.approve(approval_params)
            assert tx_hash is not None

    @pytest.mark.asyncio
    async def test_get_allowance(self, erc20_plugin, mock_contract_factory):
        """Test allowance fetching."""
        token_address = "0x1234"
        owner_address = "0x5678"
        spender_address = "0x9abc"
        
        mock_token = self.setup_token_contract(
            mock_contract_factory,
            token_address,
            total_supply=1000000
        )

        with patch("web3.eth.Contract", return_value=mock_token):
            allowance = await erc20_plugin.get_allowance(
                token_address,
                owner_address,
                spender_address
            )
            assert allowance == 1000000  # Total supply as defined in setup_token_contract
