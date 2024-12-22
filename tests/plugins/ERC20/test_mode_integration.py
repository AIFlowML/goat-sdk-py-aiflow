"""Integration tests for ERC20 plugin on Mode network."""

import os
import pytest
from web3 import Web3

from goat_sdk.plugins.ERC20 import ERC20Plugin, ERC20PluginCtorParams
from goat_sdk.plugins.ERC20.types import DeployTokenParams, TransferParams


def get_mode_env_vars():
    """Get Mode network environment variables."""
    mode_private_key = os.getenv("MODE_PRIVATE_KEY")
    mode_rpc_url = os.getenv("MODE_RPC_URL", "https://sepolia.mode.network")
    return mode_private_key, mode_rpc_url


def requires_mode_env_vars(func):
    """Decorator to skip tests if Mode environment variables are not set."""
    def wrapper(*args, **kwargs):
        mode_private_key, _ = get_mode_env_vars()
        if not mode_private_key:
            pytest.skip("MODE_PRIVATE_KEY environment variable not set")
        return func(*args, **kwargs)
    return wrapper


@pytest.mark.asyncio
@requires_mode_env_vars
async def test_deploy_token_on_mode():
    """Test deploying a token on Mode network."""
    mode_private_key, mode_rpc_url = get_mode_env_vars()

    # Initialize plugin
    plugin = ERC20Plugin(ERC20PluginCtorParams(
        private_key=mode_private_key,
        provider_url=mode_rpc_url,
        network="testnet"
    ))

    # Deploy token
    result = await plugin.deploy_token(DeployTokenParams(
        name="Test Token",
        symbol="TEST",
        initial_supply=1000000
    ))

    assert Web3.is_address(result.contract_address)
    assert result.transaction_hash.startswith("0x")
    assert "mode.network" in result.explorer_url


@pytest.mark.asyncio
@requires_mode_env_vars
async def test_transfer_on_mode():
    """Test transferring tokens on Mode network."""
    mode_private_key, mode_rpc_url = get_mode_env_vars()

    # Initialize plugin
    plugin = ERC20Plugin(ERC20PluginCtorParams(
        private_key=mode_private_key,
        provider_url=mode_rpc_url,
        network="testnet"
    ))

    # Deploy token first
    deploy_result = await plugin.deploy_token(DeployTokenParams(
        name="Test Token",
        symbol="TEST",
        initial_supply=1000000
    ))

    # Create a random recipient address
    recipient = Web3().eth.account.create().address

    # Transfer tokens
    transfer_result = await plugin.transfer(TransferParams(
        token_address=deploy_result.contract_address,
        to_address=recipient,
        amount=1000
    ))

    assert transfer_result.transaction_hash.startswith("0x")
    assert "mode.network" in transfer_result.explorer_url
