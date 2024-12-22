"""
Tests for the ERC20 plugin implementation.
"""

import pytest
import logging
from decimal import Decimal
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock
from web3 import Web3

from goat_sdk.plugins.ERC20.erc20_plugin import ERC20Plugin, ERC20PluginCtorParams
from goat_sdk.plugins.ERC20.mode_config import ModeNetwork
from goat_sdk.plugins.ERC20.types import (
    TokenInfo,
    TransferParameters,
    ApprovalParameters,
    GetTokenInfoParams,
    GetBalanceParams,
    TransferParams,
    ApproveParams,
    GetTokenAllowanceParams,
)
from tests.base_test import BaseGoatTest

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='test_results.txt'
)

class TestERC20Plugin(BaseGoatTest):
    """Test cases for ERC20Plugin."""

    # Test addresses
    TEST_TOKEN_ADDRESS = "0x" + "1" * 40  # Valid Ethereum address
    TEST_WALLET_ADDRESS = "0x" + "2" * 40  # Valid Ethereum address
    TEST_SPENDER_ADDRESS = "0x" + "3" * 40  # Valid Ethereum address

    @pytest.fixture
    def web3_mock(self):
        """Create a mock Web3 instance."""
        logger.info("Creating Web3 mock instance")
        mock = MagicMock()
        
        # Mock eth module
        eth_mock = MagicMock()
        eth_mock.chain_id = 919  # Mode Testnet chain ID
        eth_mock.get_transaction_count = AsyncMock(return_value=1)
        eth_mock.gas_price = 20_000_000_000  # 20 gwei
        logger.debug(f"Mocked eth module with chain_id: {eth_mock.chain_id}, gas_price: {eth_mock.gas_price}")
        
        # Mock contract creation
        def create_contract(address, abi):
            logger.debug(f"Creating mock contract for address: {address}")
            contract = MagicMock()
            
            # Create function mocks that return actual values
            name_func = MagicMock()
            name_func.call = lambda: "Test Token"
            
            symbol_func = MagicMock()
            symbol_func.call = lambda: "TEST"
            
            decimals_func = MagicMock()
            decimals_func.call = lambda: 18
            
            total_supply_func = MagicMock()
            total_supply_func.call = lambda: 1000000
            
            balance_func = MagicMock()
            balance_func.call = lambda: 500000
            
            allowance_func = MagicMock()
            allowance_func.call = lambda: 500000
            
            logger.debug("Set up mock contract functions with values:")
            logger.debug(f"  name: Test Token")
            logger.debug(f"  symbol: TEST")
            logger.debug(f"  decimals: 18")
            logger.debug(f"  total_supply: 1000000")
            logger.debug(f"  balance: 500000")
            logger.debug(f"  allowance: 500000")
            
            # Mock transfer function
            transfer_func = MagicMock()
            transfer_func.build_transaction = lambda tx_params: {
                'from': tx_params['from'],
                'nonce': tx_params['nonce'],
                'gasPrice': tx_params['gasPrice'],
                'gas': 100000,
                'to': address,
                'data': '0x',
                'value': 0
            }
            
            # Mock approve function
            approve_func = MagicMock()
            approve_func.build_transaction = lambda tx_params: {
                'from': tx_params['from'],
                'nonce': tx_params['nonce'],
                'gasPrice': tx_params['gasPrice'],
                'gas': 100000,
                'to': address,
                'data': '0x',
                'value': 0
            }
            
            # Set up functions
            functions = MagicMock()
            functions.name = MagicMock(return_value=name_func)
            functions.symbol = MagicMock(return_value=symbol_func)
            functions.decimals = MagicMock(return_value=decimals_func)
            functions.totalSupply = MagicMock(return_value=total_supply_func)
            functions.balanceOf = MagicMock(return_value=balance_func)
            functions.allowance = MagicMock(return_value=allowance_func)
            functions.transfer = MagicMock(return_value=transfer_func)
            functions.approve = MagicMock(return_value=approve_func)
            
            contract.functions = functions
            logger.debug("Successfully created mock contract")
            return contract
        
        eth_mock.contract = create_contract
        
        # Mock transaction sending
        async def mock_send_raw_transaction(raw_tx):
            logger.debug(f"Sending raw transaction: {raw_tx}")
            # Return a valid 32-byte transaction hash
            return '0x' + '1234' * 16
        eth_mock.send_raw_transaction = mock_send_raw_transaction
        
        # Mock transaction receipt
        receipt_mock = {
            'status': 1,
            'transactionHash': bytes.fromhex('1234' * 16)  # 32 bytes
        }
        async def mock_wait_for_transaction_receipt(tx_hash):
            logger.debug(f"Waiting for transaction receipt: {tx_hash}")
            logger.debug(f"Returning receipt: {receipt_mock}")
            return receipt_mock
        eth_mock.wait_for_transaction_receipt = mock_wait_for_transaction_receipt
        
        # Mock account signing
        def mock_sign_transaction(tx, private_key):
            logger.debug(f"Signing transaction: {tx}")
            result = MagicMock(raw_transaction='0x' + '1234' * 16)
            logger.debug(f"Signed transaction result: {result.raw_transaction}")
            return result
        
        account_mock = MagicMock()
        account_mock.sign_transaction = mock_sign_transaction
        eth_mock.account = account_mock
        
        # Set up eth module
        mock.eth = eth_mock
        
        logger.info("Successfully created Web3 mock instance")
        return mock

    @pytest.fixture
    def erc20_plugin(self, web3_mock):
        """Create an ERC20Plugin instance with mocked dependencies."""
        logger.info("Creating ERC20Plugin instance")
        
        # Use a valid 32-byte private key for testing
        test_private_key = "0x" + "1" * 64  # 32 bytes in hex
        params = ERC20PluginCtorParams(
            private_key=test_private_key,
            provider_url="https://sepolia.mode.network",
            network=ModeNetwork.TESTNET,
            tokens=None  # Use default tokens
        )
        logger.debug(f"Created ERC20PluginCtorParams with network: {params.network}")
        
        # Patch both Web3 and Account to avoid actual blockchain interactions
        with patch("goat_sdk.plugins.ERC20.erc20_plugin.Web3") as web3_class_mock, \
             patch("goat_sdk.plugins.ERC20.erc20_plugin.Account") as account_mock:
            # Setup Web3 mock
            web3_class_mock.return_value = web3_mock
            web3_class_mock.HTTPProvider = MagicMock()
            
            # Setup Account mock
            account_mock.from_key.return_value.address = self.TEST_WALLET_ADDRESS
            logger.debug(f"Mocked account address: {self.TEST_WALLET_ADDRESS}")
            
            plugin = ERC20Plugin(params)
            logger.info("ERC20Plugin instance created successfully")
            return plugin

    @pytest.mark.asyncio
    async def test_get_token_info(self, erc20_plugin):
        """Test token info fetching."""
        logger.info("\n=== Starting test_get_token_info ===")
        
        logger.info("Creating GetTokenInfoParams")
        params = GetTokenInfoParams(
            token_address=self.TEST_TOKEN_ADDRESS,
            address=self.TEST_WALLET_ADDRESS
        )
        logger.debug(f"Created params with token_address: {params.token_address}, address: {params.address}")
        
        logger.info("Calling get_token_info")
        token_info = await erc20_plugin.get_token_info(params)
        logger.debug(f"Received token info: {token_info}")
        
        # Verify the results
        assert token_info.name == "Test Token"
        assert token_info.symbol == "TEST"
        assert token_info.decimals == 18
        assert token_info.total_supply == 1000000
        assert token_info.balance == 500000
        logger.info("test_get_token_info completed successfully")

    @pytest.mark.asyncio
    async def test_get_balance(self, erc20_plugin):
        """Test balance fetching."""
        print("\n=== Starting test_get_balance ===")
        
        print("Creating GetBalanceParams")
        params = GetBalanceParams(
            token_address=self.TEST_TOKEN_ADDRESS,
            wallet_address=self.TEST_WALLET_ADDRESS
        )
        
        print("Calling get_balance")
        balance = await erc20_plugin.get_balance(params)
        
        # Verify the results
        assert balance == 500000  # Half of total supply as defined in web3_mock

    @pytest.mark.asyncio
    async def test_transfer(self, erc20_plugin):
        """Test token transfer."""
        logger.info("\n=== Starting test_transfer ===")
        
        logger.info("Creating TransferParams")
        transfer_params = TransferParams(
            token_address=self.TEST_TOKEN_ADDRESS,
            to_address=self.TEST_SPENDER_ADDRESS,
            amount=100_000_000_000_000_000_000  # 100 tokens in base units (18 decimals)
        )
        logger.debug(f"Created params: {transfer_params}")
        
        logger.info("Calling transfer")
        tx_hash = await erc20_plugin.transfer(transfer_params)
        logger.debug(f"Received transaction hash: {tx_hash}")
        
        # Verify the results
        assert tx_hash is not None
        logger.info("test_transfer completed successfully")

    @pytest.mark.asyncio
    async def test_approve(self, erc20_plugin):
        """Test token approval."""
        logger.info("\n=== Starting test_approve ===")
        
        logger.info("Creating ApproveParams")
        approval_params = ApproveParams(
            token_address=self.TEST_TOKEN_ADDRESS,
            spender_address=self.TEST_SPENDER_ADDRESS,
            amount=100_000_000_000_000_000_000  # 100 tokens in base units (18 decimals)
        )
        logger.debug(f"Created params: {approval_params}")
        
        logger.info("Calling approve")
        tx_hash = await erc20_plugin.approve(approval_params)
        logger.debug(f"Received transaction hash: {tx_hash}")
        
        # Verify the results
        assert tx_hash is not None
        logger.info("test_approve completed successfully")

    @pytest.mark.asyncio
    async def test_get_allowance(self, erc20_plugin):
        """Test allowance fetching."""
        logger.info("\n=== Starting test_get_allowance ===")
        
        logger.info("Creating GetTokenAllowanceParams")
        params = GetTokenAllowanceParams(
            token_address=self.TEST_TOKEN_ADDRESS,
            owner_address=self.TEST_WALLET_ADDRESS,
            spender_address=self.TEST_SPENDER_ADDRESS
        )
        logger.debug(f"Created params: {params}")
        
        logger.info("Calling get_token_allowance")
        allowance = await erc20_plugin.get_token_allowance(params)
        logger.debug(f"Received allowance: {allowance}")
        
        # Verify the results
        assert allowance == 500000  # Half of total supply as defined in web3_mock
        logger.info("test_get_allowance completed successfully")

    def setup_token_contract(self, mock_contract_factory, address, **kwargs):
        """Set up a mock token contract."""
        print(f"Setting up token contract with address: {address}")
        mock_contract = MagicMock()
        
        # Get values from kwargs with defaults
        name = kwargs.get('name', 'Test Token')
        symbol = kwargs.get('symbol', 'TEST')
        decimals = kwargs.get('decimals', 18)
        total_supply = kwargs.get('total_supply', 1000000)
        balance = total_supply // 2  # Half of total supply
        
        print(f"Setting up contract with values:")
        print(f"  name: {name}")
        print(f"  symbol: {symbol}")
        print(f"  decimals: {decimals}")
        print(f"  total_supply: {total_supply}")
        print(f"  balance: {balance}")
        
        # Create function mocks that return actual values
        name_func = MagicMock()
        name_func.call = lambda: name
        
        symbol_func = MagicMock()
        symbol_func.call = lambda: symbol
        
        decimals_func = MagicMock()
        decimals_func.call = lambda: decimals
        
        total_supply_func = MagicMock()
        total_supply_func.call = lambda: total_supply
        
        balance_func = MagicMock()
        balance_func.call = lambda: balance
        
        # Set up functions
        functions = MagicMock()
        functions.name = MagicMock(return_value=name_func)
        functions.symbol = MagicMock(return_value=symbol_func)
        functions.decimals = MagicMock(return_value=decimals_func)
        functions.totalSupply = MagicMock(return_value=total_supply_func)
        functions.balanceOf = MagicMock(return_value=balance_func)
        
        mock_contract.functions = functions
        
        return mock_contract
