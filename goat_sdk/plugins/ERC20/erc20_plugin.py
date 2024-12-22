
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
     
     Path: examples/hyperliquid/ai_trading_agent.py
"""

"""ERC20 token plugin."""
import json
import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from dotenv import load_dotenv

from goat_sdk.core.plugin_base import PluginBase
from goat_sdk.core.chain import Chain
from .types import (
    DeployTokenParams,
    GetTokenInfoParams,
    GetBalanceParams,
    TransferParams,
    ApproveParams,
    TransferFromParams,
    TokenDeploymentResult,
    TokenInfoResult,
    TransactionResult,
    ConvertToBaseUnitParams,
    ConvertFromBaseUnitParams,
    GetTokenInfoBySymbolParams,
    GetTokenAllowanceParams
)
from .compile_contract import compile_contract
from .mode_config import ModeNetwork, get_mode_config
from .tokens import Token, get_token_by_symbol, DEFAULT_TOKENS

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Environment variables with defaults
MODE_PRIVATE_KEY = os.getenv("MODE_PRIVATE_KEY")
MODE_PROVIDER_URL = os.getenv("MODE_PROVIDER_URL", "https://sepolia.mode.network")
MODE_NETWORK = os.getenv("MODE_NETWORK", "testnet")
MODE_GAS_LIMIT = int(os.getenv("MODE_GAS_LIMIT", "300000"))
MODE_GAS_PRICE_BUFFER = float(os.getenv("MODE_GAS_PRICE_BUFFER", "1.2"))
MODE_MAX_RETRIES = int(os.getenv("MODE_MAX_RETRIES", "3"))
MODE_RETRY_DELAY = float(os.getenv("MODE_RETRY_DELAY", "1.0"))
MODE_CONFIRMATION_BLOCKS = int(os.getenv("MODE_CONFIRMATION_BLOCKS", "1"))
MODE_GAS_LIMIT_BUFFER = float(os.getenv("MODE_GAS_LIMIT_BUFFER", "1.2"))
MODE_PRIORITY_FEE = int(os.getenv("MODE_PRIORITY_FEE", "1000000000"))
MODE_TIMEOUT = float(os.getenv("MODE_TIMEOUT", "30.0"))


class ERC20PluginCtorParams(BaseModel):
    """Parameters for constructing an ERC20Plugin."""
    private_key: str = Field(
        ...,
        description="Private key for signing transactions"
    )
    provider_url: str = Field(
        ...,
        description="URL of the Mode network provider"
    )
    network: ModeNetwork = Field(
        default=ModeNetwork.TESTNET,
        description="Mode network to connect to"
    )
    tokens: Optional[List[Token]] = Field(
        default=None,
        description="Optional list of tokens to use. If not provided, uses default tokens"
    )


class ERC20Plugin(PluginBase):
    """Plugin for interacting with ERC20 tokens on Mode network."""

    def __init__(self, params: ERC20PluginCtorParams):
        """Initialize the plugin."""
        super().__init__(name="erc20", tools=[self])
        logger.info("Initializing ERC20Plugin")
        self.w3 = Web3(Web3.HTTPProvider(params.provider_url))
        self.account = Account.from_key(params.private_key)
        self.network = params.network
        self.mode_config = get_mode_config(params.network)
        self.tokens = params.tokens or DEFAULT_TOKENS
        logger.debug(f"Connected to network: {self.network.value}")
        logger.debug(f"Account address: {self.account.address}")

        # Load contract ABI and bytecode
        build_dir = Path(__file__).parent / "build"
        try:
            with open(build_dir / "TestToken.abi", "r", encoding="utf-8") as f:
                self.abi = json.load(f)
            with open(build_dir / "TestToken.bin", "r", encoding="utf-8") as f:
                self.bytecode = f.read()
            logger.debug("Loaded contract ABI and bytecode from files")
        except FileNotFoundError:
            # Compile contract if ABI and bytecode files don't exist
            logger.info("Contract files not found, compiling contract")
            self.abi, self.bytecode = compile_contract()

        # Get chain ID
        chain_id = self.w3.eth.chain_id
        chain = Chain(type="evm", chain_id=chain_id)
        if not self.supports_chain(chain):
            # For local testing, we'll allow non-Mode networks
            if chain_id not in [1337]:  # Ganache chain ID
                raise ValueError(f"Chain {chain_id} is not supported")
        logger.info(f"Successfully initialized ERC20Plugin on chain {chain_id}")

    def supports_chain(self) -> bool:
        """Check if the current chain is supported.
        
        Returns:
            True if the chain is supported (EVM-compatible), False otherwise.
        """
        try:
            # Check if chain supports EVM by attempting to get chain ID
            chain_id = self.w3.eth.chain_id
            # Mode network chain IDs
            supported_chain_ids = {
                34443,  # Mode Mainnet
                919,    # Mode Testnet
            }
            return chain_id in supported_chain_ids
        except Exception:
            return False

    def supports_chain(self, chain: Chain) -> bool:
        """Check if the plugin supports the given chain.
        
        Args:
            chain: Chain to check support for
            
        Returns:
            True if the chain is supported (Mode network), False otherwise
        """
        return (
            chain.type == "evm" and
            chain.chain_id in {
                34443,  # Mode Mainnet
                919,    # Mode Testnet
                1337,   # Ganache (for testing)
            }
        )

    def _validate_mode_network(self):
        """Validate that we're connected to the correct Mode network."""
        chain_id = self.w3.eth.chain_id
        # Skip validation for local testing
        if chain_id == 1337:  # Ganache
            return
        if chain_id != self.mode_config["chain_id"]:
            raise ValueError(
                f"Connected to wrong network. Expected Mode {self.network.value} "
                f"(chain_id: {self.mode_config['chain_id']}), but got chain_id: {chain_id}"
            )

    def _estimate_gas(self, transaction):
        """Estimate gas for a transaction with Mode-specific adjustments."""
        try:
            estimated_gas = self.w3.eth.estimate_gas(transaction)
            # Add 20% buffer for Mode network
            return int(estimated_gas * 1.2)
        except ContractLogicError as e:
            raise ValueError(f"Failed to estimate gas: {str(e)}")

    async def deploy_token(self, params: DeployTokenParams) -> TokenDeploymentResult:
        """Deploy a new ERC20 token on Mode network."""
        self._validate_mode_network()
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)

        # Build constructor transaction
        constructor_txn = contract.constructor(
            params.name,
            params.symbol,
            params.initial_supply
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': self.w3.eth.gas_price
        })

        # Estimate gas with Mode-specific adjustments
        constructor_txn['gas'] = self._estimate_gas(constructor_txn)

        try:
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(constructor_txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt['status'] != 1:
                raise ValueError("Token deployment failed")

            tx_hash_hex = f"0x{tx_receipt['transactionHash'].hex()}"
            return TokenDeploymentResult(
                contract_address=tx_receipt['contractAddress'],
                transaction_hash=tx_hash_hex,
                explorer_url=f"{self.mode_config['explorer_url']}/tx/{tx_hash_hex}"
            )
        except Exception as e:
            raise ValueError(f"Failed to deploy token on Mode network: {str(e)}")

    async def get_token_info(self, params: GetTokenInfoParams) -> TokenInfoResult:
        """Get information about a token."""
        logger.info(f"Getting token info for address: {params.token_address}")
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)

        try:
            # Get token info
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            total_supply = contract.functions.totalSupply().call()
            logger.debug(f"Retrieved token info - Name: {name}, Symbol: {symbol}, Decimals: {decimals}")

            # Get balance if address is provided
            balance = None
            if params.address:
                balance = contract.functions.balanceOf(params.address).call()
                logger.debug(f"Retrieved balance for {params.address}: {balance}")

            result = TokenInfoResult(
                name=name,
                symbol=symbol,
                decimals=decimals,
                total_supply=total_supply,
                balance=balance
            )
            logger.info("Successfully retrieved token info")
            return result
        except Exception as e:
            logger.error(f"Failed to get token info: {str(e)}")
            raise

    async def transfer(self, params: TransferParams) -> TransactionResult:
        """Transfer tokens to another address on Mode network."""
        logger.info(f"Transferring {params.amount} tokens to {params.to_address}")
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)

        try:
            # Build transfer transaction
            nonce = await self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            logger.debug(f"Building transaction - Nonce: {nonce}, Gas Price: {gas_price}")

            transfer_txn = contract.functions.transfer(
                params.to_address,
                params.amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gasPrice': gas_price
            })

            # Estimate gas with Mode-specific adjustments
            transfer_txn['gas'] = self._estimate_gas(transfer_txn)
            logger.debug(f"Estimated gas: {transfer_txn['gas']}")

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transfer_txn, self.account.key)
            logger.debug("Transaction signed")
            
            tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            logger.debug(f"Transaction sent with hash: {tx_hash}")
            
            tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.debug(f"Transaction receipt received: {tx_receipt}")

            if tx_receipt['status'] != 1:
                raise ValueError("Transfer failed")

            tx_hash_hex = tx_hash if isinstance(tx_hash, str) else f"0x{tx_hash.hex()}"
            result = TransactionResult(
                transaction_hash=tx_hash_hex,
                explorer_url=f"{self.mode_config['explorer_url']}/tx/{tx_hash_hex}"
            )
            logger.info("Transfer completed successfully")
            return result
        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}")
            raise ValueError(f"Failed to transfer tokens on Mode network: {str(e)}")

    async def approve(self, params: ApproveParams) -> TransactionResult:
        """Approve token spending on Mode network."""
        logger.info(f"Approving {params.amount} tokens for spender {params.spender_address}")
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)

        try:
            # Build approve transaction
            nonce = await self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            logger.debug(f"Building transaction - Nonce: {nonce}, Gas Price: {gas_price}")

            approve_txn = contract.functions.approve(
                params.spender_address,
                params.amount
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gasPrice': gas_price
            })

            # Estimate gas with Mode-specific adjustments
            approve_txn['gas'] = self._estimate_gas(approve_txn)
            logger.debug(f"Estimated gas: {approve_txn['gas']}")

            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(approve_txn, self.account.key)
            logger.debug("Transaction signed")
            
            tx_hash = await self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            logger.debug(f"Transaction sent with hash: {tx_hash}")
            
            tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
            logger.debug(f"Transaction receipt received: {tx_receipt}")

            if tx_receipt['status'] != 1:
                raise ValueError("Approve failed")

            tx_hash_hex = tx_hash if isinstance(tx_hash, str) else f"0x{tx_hash.hex()}"
            result = TransactionResult(
                transaction_hash=tx_hash_hex,
                explorer_url=f"{self.mode_config['explorer_url']}/tx/{tx_hash_hex}"
            )
            logger.info("Approval completed successfully")
            return result
        except Exception as e:
            logger.error(f"Approval failed: {str(e)}")
            raise ValueError(f"Failed to approve token spending on Mode network: {str(e)}")

    async def transfer_from(self, params: TransferFromParams) -> TransactionResult:
        """Transfer tokens on behalf of another address on Mode network."""
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)

        # Build transferFrom transaction
        transfer_from_txn = contract.functions.transferFrom(
            params.from_address,
            params.to_address,
            params.amount
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': self.w3.eth.gas_price
        })

        # Estimate gas with Mode-specific adjustments
        transfer_from_txn['gas'] = self._estimate_gas(transfer_from_txn)

        try:
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transfer_from_txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if tx_receipt['status'] != 1:
                raise ValueError("TransferFrom failed")

            tx_hash_hex = f"0x{tx_receipt['transactionHash'].hex()}"
            return TransactionResult(
                transaction_hash=tx_hash_hex,
                explorer_url=f"{self.mode_config['explorer_url']}/tx/{tx_hash_hex}"
            )
        except Exception as e:
            raise ValueError(f"Failed to transfer tokens on behalf of another address on Mode network: {str(e)}")

    async def get_balance(self, params: GetBalanceParams) -> int:
        """Get token balance for an address on Mode network."""
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)
        return contract.functions.balanceOf(params.wallet_address).call()

    async def get_token_info_by_symbol(self, params: GetTokenInfoBySymbolParams) -> TokenInfoResult:
        """Get token information by its symbol."""
        self._validate_mode_network()
        
        token = get_token_by_symbol(
            symbol=params.symbol,
            chain_id=self.mode_config["chain_id"],
            tokens=self.tokens
        )
        
        if not token:
            raise ValueError(f"Token with symbol {params.symbol} not found on Mode {self.network.value}")

        contract = self.w3.eth.contract(address=token.contract_address, abi=self.abi)
        total_supply = contract.functions.totalSupply().call()
        
        # Get balance if address is provided
        balance = None
        if params.address:
            balance = contract.functions.balanceOf(params.address).call()

        return TokenInfoResult(
            name=token.name,
            symbol=token.symbol,
            decimals=token.decimals,
            total_supply=total_supply,
            balance=balance,
            contract_address=token.contract_address
        )

    async def get_token_allowance(self, params: GetTokenAllowanceParams) -> int:
        """Get the allowance of tokens that a spender can spend on behalf of an owner."""
        logger.info(f"Getting allowance for owner {params.owner_address} and spender {params.spender_address}")
        self._validate_mode_network()
        contract = self.w3.eth.contract(address=params.token_address, abi=self.abi)

        try:
            allowance = contract.functions.allowance(
                params.owner_address,
                params.spender_address
            ).call()
            logger.debug(f"Retrieved allowance: {allowance}")
            return allowance
        except Exception as e:
            logger.error(f"Failed to get allowance: {str(e)}")
            raise ValueError(f"Failed to get allowance on Mode network: {str(e)}")

    def convert_to_base_unit(self, params: ConvertToBaseUnitParams) -> int:
        """Convert an amount from decimal units to base units (wei)."""
        try:
            base_unit = int(params.amount * (10 ** params.decimals))
            return base_unit
        except Exception as e:
            raise ValueError(f"Failed to convert to base unit: {str(e)}")

    def convert_from_base_unit(self, params: ConvertFromBaseUnitParams) -> float:
        """Convert an amount from base units (wei) to decimal units."""
        try:
            decimal_unit = params.amount / (10 ** params.decimals)
            return decimal_unit
        except Exception as e:
            raise ValueError(f"Failed to convert from base unit: {str(e)}")
