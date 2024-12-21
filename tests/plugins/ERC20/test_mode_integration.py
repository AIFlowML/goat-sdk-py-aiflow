"""Mode network integration tests for ERC20 plugin."""

import os
import pytest
from web3 import Web3

from goat_sdk.plugins.ERC20 import (
    ERC20Plugin,
    ERC20PluginCtorParams,
    DeployTokenParams,
    GetTokenInfoParams,
    GetBalanceParams,
    TransferParams,
)


@pytest.fixture
def mode_testnet_config():
    """Mode testnet configuration."""
    return {
        "chain_id": 919,  # Mode Testnet Chain ID
        "rpc_url": "https://sepolia.mode.network",
    }


@pytest.fixture
def private_key():
    """Get private key from environment."""
    key = os.getenv("MODE_PRIVATE_KEY")
    if not key:
        pytest.skip("MODE_PRIVATE_KEY environment variable not set")
    return key


@pytest.fixture
def plugin(mode_testnet_config, private_key):
    """Create an ERC20Plugin instance for Mode testnet."""
    return ERC20Plugin(ERC20PluginCtorParams(
        chain_id=mode_testnet_config["chain_id"],
        rpc_url=mode_testnet_config["rpc_url"],
        private_key=private_key
    ))


@pytest.mark.asyncio
async def test_deploy_token_on_mode(plugin):
    """Test deploying a token on Mode testnet."""
    # Deploy new token
    deploy_params = DeployTokenParams(
        name="Mode Test Token",
        symbol="MTT",
        initial_supply=1000000
    )
    result = await plugin.deploy_token(deploy_params)
    
    assert result["status"] == 1  # Transaction successful
    assert Web3.is_address(result["contract_address"])
    
    # Verify token info
    info_params = GetTokenInfoParams(
        token_address=result["contract_address"]
    )
    token_info = await plugin.get_token_info(info_params)
    
    assert token_info["name"] == "Mode Test Token"
    assert token_info["symbol"] == "MTT"
    assert token_info["decimals"] == 18
    assert int(token_info["total_supply"]) == 1000000 * 10**18


@pytest.mark.asyncio
async def test_transfer_on_mode(plugin):
    """Test token transfer on Mode testnet."""
    # First deploy a token
    deploy_params = DeployTokenParams(
        name="Mode Transfer Test",
        symbol="MTX",
        initial_supply=1000000
    )
    deploy_result = await plugin.deploy_token(deploy_params)
    assert deploy_result["status"] == 1
    
    # Create a new account to transfer to
    recipient = Web3().eth.account.create()
    
    # Transfer some tokens
    transfer_params = TransferParams(
        token_address=deploy_result["contract_address"],
        recipient_address=recipient.address,
        amount=str(100 * 10**18)  # Transfer 100 tokens
    )
    transfer_result = await plugin.transfer(transfer_params)
    
    assert transfer_result["status"] == 1  # Transaction successful
    
    # Verify recipient balance
    balance_params = GetBalanceParams(
        token_address=deploy_result["contract_address"],
        wallet_address=recipient.address
    )
    balance = await plugin.get_balance(balance_params)
    assert int(balance) == 100 * 10**18
