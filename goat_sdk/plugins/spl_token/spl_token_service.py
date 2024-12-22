"""SPL Token Service implementation."""

import logging
import os
from base58 import b58decode

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
)

# Create separate handlers for service and test logs
service_handler = logging.FileHandler('logs/spl_token_service.log')
test_handler = logging.FileHandler('logs/spl_token_test.log')
transfer_flow_handler = logging.FileHandler('logs/test_full_token_transfer_flow.log')
console_handler = logging.StreamHandler()

# Set format for all handlers
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s')
service_handler.setFormatter(formatter)
test_handler.setFormatter(formatter)
transfer_flow_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Create separate loggers
logger = logging.getLogger('spl_token.service')
test_logger = logging.getLogger('spl_token.test')
transfer_flow_logger = logging.getLogger('spl_token.transfer_flow')

# Configure service logger
logger.setLevel(logging.DEBUG)
logger.addHandler(service_handler)
logger.addHandler(console_handler)

# Configure test logger
test_logger.setLevel(logging.DEBUG)
test_logger.addHandler(test_handler)
test_logger.addHandler(console_handler)

# Configure transfer flow logger - only log errors
transfer_flow_logger.setLevel(logging.ERROR)
transfer_flow_handler.setLevel(logging.ERROR)
transfer_flow_logger.addHandler(transfer_flow_handler)
transfer_flow_logger.addHandler(console_handler)

# Prevent log propagation to avoid duplicate logs
logger.propagate = False
test_logger.propagate = False
transfer_flow_logger.propagate = False

from typing import List, Optional, Dict, Any
from decimal import Decimal

from solders.pubkey import Pubkey as PublicKey
from solders.transaction import Transaction, TransactionError
from solders.commitment_config import CommitmentLevel
from solders.rpc.config import RpcTransactionConfig as TxOpts
from solders.system_program import transfer, TransferParams
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.hash import Hash

from goat_sdk.plugins.spl_token.models import Token, TokenBalance, SolanaNetwork
from goat_sdk.plugins.spl_token.parameters import (
    GetTokenMintAddressBySymbolParameters,
    GetTokenBalanceByMintAddressParameters,
    TransferTokenByMintAddressParameters,
    ConvertToBaseUnitParameters,
)
from goat_sdk.plugins.spl_token.exceptions import (
    TokenNotFoundError,
    TokenAccountNotFoundError,
    InsufficientBalanceError,
    TokenTransferError,
)
from goat_sdk.plugins.spl_token.utils import (
    does_account_exist,
    create_associated_token_account,
    log_error_details,
)
from goat_sdk.plugins.spl_token.monitoring import (
    monitor_mode_performance,
    with_retries,
    trace_operation,
)

# Constants
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

class SplTokenService:
    """Service for interacting with SPL tokens."""

    def __init__(
        self,
        network: SolanaNetwork = SolanaNetwork.MAINNET,
        tokens: List[Token] = None,
    ):
        """Initialize the SPL token service.

        Args:
            network: The Solana network to use
            tokens: List of supported tokens
        """
        logger.info(f"Initializing SPL Token Service on network: {network}")
        self.network = network
        self.tokens = tokens or []
        self.wallet_client = None
        logger.info(f"Loaded {len(self.tokens)} tokens")
        for token in self.tokens:
            logger.debug(f"Loaded token: {token.symbol} with mint addresses: {token.mint_addresses}")

    @monitor_mode_performance
    @with_retries("get_token_info_by_symbol")
    @trace_operation("get_token_info_by_symbol")
    async def get_token_info_by_symbol(
        self,
        parameters: GetTokenMintAddressBySymbolParameters,
    ) -> Token:
        """Get token info by symbol.

        Args:
            parameters: Parameters for getting token info

        Returns:
            Token info
        """
        operation = "get_token_info_by_symbol"
        logger.info(f"[{operation}] Starting operation")
        logger.debug(f"[{operation}] Input parameters: {parameters}")
        logger.debug(f"[{operation}] Current network: {self.network}")
        logger.debug(f"[{operation}] Service instance: {self}")
        logger.debug(f"[{operation}] Service instance attributes: {vars(self) if hasattr(self, '__dict__') else str(self)}")
        
        # Find matching token
        logger.debug(f"[{operation}] Step: Finding matching token")
        matching_token = None
        
        for token in self.tokens:
            logger.debug(f"[{operation}] Checking token: {token}")
            logger.debug(f"[{operation}] Token attributes: {vars(token) if hasattr(token, '__dict__') else str(token)}")
            if token.symbol == parameters.symbol:
                logger.debug(f"[{operation}] Found matching token: {token}")
                matching_token = token
                break
        
        if not matching_token:
            logger.error(f"[{operation}] Token not found with symbol: {parameters.symbol}")
            logger.error(f"[{operation}] Available tokens: {[t.symbol for t in self.tokens]}")
            logger.error(f"[{operation}] Token list state: {self.tokens}")
            logger.error(f"[{operation}] Service instance: {self}")
            logger.error(f"[{operation}] Service instance attributes: {vars(self) if hasattr(self, '__dict__') else str(self)}")
            raise TokenNotFoundError(parameters.symbol)
                
        # Check if token exists on current network
        logger.debug(f"[{operation}] Step: Validating token on network {self.network}")
        logger.debug(f"[{operation}] Token mint addresses: {matching_token.mint_addresses}")
        logger.debug(f"[{operation}] Token attributes: {vars(matching_token) if hasattr(matching_token, '__dict__') else str(matching_token)}")
        if self.network not in matching_token.mint_addresses:
            logger.error(f"[{operation}] Token {matching_token.symbol} not found on network {self.network}")
            logger.error(f"[{operation}] Available networks: {list(matching_token.mint_addresses.keys())}")
            logger.error(f"[{operation}] Token mint addresses: {matching_token.mint_addresses}")
            logger.error(f"[{operation}] Token attributes: {vars(matching_token) if hasattr(matching_token, '__dict__') else str(matching_token)}")
            raise TokenNotFoundError(matching_token.symbol)
        
        logger.info(f"[{operation}] Successfully found token {matching_token.symbol} on network {self.network}")
        logger.debug(f"[{operation}] Returning token: {matching_token}")
        logger.debug(f"[{operation}] Token attributes: {vars(matching_token) if hasattr(matching_token, '__dict__') else str(matching_token)}")
        return matching_token

    @monitor_mode_performance
    @with_retries("get_token_balance_by_mint_address")
    @trace_operation("get_token_balance_by_mint_address")
    async def get_token_balance_by_mint_address(
        self,
        wallet_client,
        parameters: GetTokenBalanceByMintAddressParameters,
    ) -> TokenBalance:
        """Get token balance by mint address.

        Args:
            wallet_client: Wallet client
            parameters: Parameters for getting token balance

        Returns:
            Token balance
        """
        operation = "get_token_balance_by_mint_address"
        logger.info(f"[{operation}] Starting operation")
        logger.debug(f"[{operation}] Input parameters: {parameters}")
        logger.debug(f"[{operation}] Wallet client: {wallet_client}")
        logger.debug(f"[{operation}] Wallet client attributes: {vars(wallet_client) if hasattr(wallet_client, '__dict__') else str(wallet_client)}")
        logger.debug(f"[{operation}] Current network: {self.network}")
        logger.debug(f"[{operation}] Service instance: {self}")
        logger.debug(f"[{operation}] Service instance attributes: {vars(self) if hasattr(self, '__dict__') else str(self)}")
        
        try:
            # Find token info
            logger.debug(f"[{operation}] Step: Finding token info")
            token = next(
                (t for t in self.tokens if t.mint_addresses.get(self.network) == parameters.mint_address),
                None,
            )
            logger.debug(f"[{operation}] Found token: {token}")
            if token:
                logger.debug(f"[{operation}] Token attributes: {vars(token) if hasattr(token, '__dict__') else str(token)}")
            
            if not token:
                logger.error(f"[{operation}] Token not found for mint address: {parameters.mint_address}")
                logger.error(f"[{operation}] Available tokens: {[t.symbol for t in self.tokens]}")
                logger.error(f"[{operation}] Token list state: {self.tokens}")
                raise TokenAccountNotFoundError(
                    account_type="Token",
                    address=parameters.wallet_address
                )

            # Find associated token account
            logger.debug(f"[{operation}] Step: Finding associated token account")
            logger.debug(f"[{operation}] Wallet address: {parameters.wallet_address}")
            logger.debug(f"[{operation}] Mint address: {parameters.mint_address}")
            token_account = await does_account_exist(
                await wallet_client.get_connection(),
                PublicKey(b58decode(parameters.wallet_address)),
                PublicKey(b58decode(parameters.mint_address)),
                parameters.mode_config
            )
            logger.debug(f"[{operation}] Token account lookup result: {token_account}")
            
            if not token_account:
                logger.error(f"[{operation}] Token account not found for address: {parameters.wallet_address}")
                logger.error(f"[{operation}] Mint address: {parameters.mint_address}")
                logger.error(f"[{operation}] Wallet client: {wallet_client}")
                raise TokenAccountNotFoundError(
                    account_type="Token",
                    address=parameters.wallet_address
                )

            # Get token account balance
            logger.debug(f"[{operation}] Step: Getting token account balance")
            logger.debug(f"[{operation}] Token account: {token_account}")
            connection = await wallet_client.get_connection()
            balance = await connection.get_token_account_balance(
                PublicKey(b58decode(token_account))
            )
            logger.debug(f"[{operation}] Balance response: {balance}")
            
            # Convert balance to UI amount
            logger.debug(f"[{operation}] Step: Converting balance to UI amount")
            ui_amount = float(balance["value"]["uiAmount"])
            logger.debug(f"[{operation}] UI amount: {ui_amount}")
            
            logger.info(f"[{operation}] Successfully retrieved token balance")
            logger.debug(f"[{operation}] Returning balance: {ui_amount}")
            return ui_amount
            
        except Exception as e:
            log_error_details(operation, e, "getting token balance")
            raise

    @monitor_mode_performance
    @with_retries("transfer_token_by_mint_address")
    @trace_operation("transfer_token_by_mint_address")
    async def transfer_token_by_mint_address(
        self,
        wallet_client,
        parameters: TransferTokenByMintAddressParameters,
    ) -> Transaction:
        """Transfer tokens by mint address.

        Args:
            wallet_client: Wallet client
            parameters: Parameters for transferring tokens

        Returns:
            Transaction
        """
        operation = "transfer_token_by_mint_address"
        logger.info(f"[{operation}] Starting operation")
        logger.debug(f"[{operation}] Input parameters: {parameters}")
        logger.debug(f"[{operation}] Wallet client: {wallet_client}")
        logger.debug(f"[{operation}] Current network: {self.network}")
        
        try:
            # Get source wallet address
            logger.debug(f"[{operation}] Step: Getting source wallet address")
            source_address = await wallet_client.get_wallet_address()
            logger.debug(f"[{operation}] Source address: {source_address}")
            
            # Check source token account exists
            logger.debug(f"[{operation}] Step: Checking source token account")
            source_token_account = await does_account_exist(
                wallet_client.get_connection(),
                PublicKey(b58decode(source_address)),
                PublicKey(b58decode(parameters.mint_address)),
                parameters.mode_config
            )
            logger.debug(f"[{operation}] Source token account: {source_token_account}")
            
            if not source_token_account:
                logger.error(f"[{operation}] Source token account not found")
                raise TokenAccountNotFoundError(
                    account_type="Source Token",
                    address=source_address
                )
                
            # Check destination token account exists
            logger.debug(f"[{operation}] Step: Checking destination token account")
            destination_token_account = await does_account_exist(
                wallet_client.get_connection(),
                PublicKey(b58decode(parameters.to)),
                PublicKey(b58decode(parameters.mint_address)),
                parameters.mode_config
            )
            logger.debug(f"[{operation}] Destination token account: {destination_token_account}")
            
            if not destination_token_account:
                logger.debug(f"[{operation}] Creating destination token account")
                # Create destination token account
                create_account_tx = await create_associated_token_account(
                    parameters.to,
                    parameters.mint_address,
                    source_address
                )
                logger.debug(f"[{operation}] Create account transaction: {create_account_tx}")
                
                # Sign and send transaction
                logger.debug(f"[{operation}] Signing and sending create account transaction")
                connection = await wallet_client.get_connection()
                blockhash = await connection.get_latest_blockhash()
                create_account_tx.recent_blockhash = blockhash[0]
                create_account_tx.sign(wallet_client.keypair)
                
                try:
                    await connection.send_transaction(
                        create_account_tx,
                        [wallet_client.keypair],
                        opts=TxOpts(skip_preflight=True)
                    )
                except Exception as e:
                    logger.error(f"[{operation}] Failed to create destination token account")
                    log_error_details(operation, e, "creating destination token account")
                    raise TokenTransferError("Failed to create destination token account")
                
                # Get created account address
                destination_token_account = await does_account_exist(
                    connection,
                    PublicKey(b58decode(parameters.to)),
                    PublicKey(b58decode(parameters.mint_address)),
                    parameters.mode_config
                )
                logger.debug(f"[{operation}] Created destination token account: {destination_token_account}")

            # Check source account balance
            logger.debug(f"[{operation}] Step: Checking source account balance")
            connection = await wallet_client.get_connection()
            balance = await connection.get_token_account_balance(
                PublicKey(b58decode(source_token_account))
            )
            logger.debug(f"[{operation}] Source balance: {balance}")
            
            current_balance = int(balance["value"]["amount"])
            if current_balance < parameters.amount:
                logger.error(f"[{operation}] Insufficient balance")
                logger.error(f"[{operation}] Current balance: {current_balance}")
                logger.error(f"[{operation}] Requested amount: {parameters.amount}")
                
                # Get token symbol
                token = next(
                    (t for t in self.tokens if t.mint_addresses.get(self.network) == parameters.mint_address),
                    None
                )
                token_symbol = token.symbol if token else "Unknown"
                
                raise InsufficientBalanceError(
                    required=parameters.amount,
                    available=current_balance,
                    token_symbol=token_symbol
                )
            
            # Create transfer instruction
            logger.debug(f"[{operation}] Step: Creating transfer instruction")
            transfer_ix = Instruction(
                program_id=PublicKey(b58decode(TOKEN_PROGRAM_ID)),
                accounts=[
                    AccountMeta(
                        pubkey=PublicKey(b58decode(source_token_account)),
                        is_signer=False,
                        is_writable=True
                    ),
                    AccountMeta(
                        pubkey=PublicKey(b58decode(destination_token_account)),
                        is_signer=False,
                        is_writable=True
                    ),
                    AccountMeta(
                        pubkey=PublicKey(b58decode(source_address)),
                        is_signer=True,
                        is_writable=False
                    )
                ],
                data=bytes([3]) + parameters.amount.to_bytes(8, "little")
            )
            logger.debug(f"[{operation}] Transfer instruction: {transfer_ix}")
            
            # Get recent blockhash
            logger.debug(f"[{operation}] Step: Getting recent blockhash")
            blockhash_response = await connection.get_latest_blockhash()
            logger.debug(f"[{operation}] Blockhash response: {blockhash_response}")

            # Create transaction
            logger.debug(f"[{operation}] Step: Creating transaction")
            message = Message.new_with_blockhash(
                [transfer_ix],
                wallet_client.keypair.pubkey(),
                Hash(b58decode(blockhash_response[0]))
            )

            transaction = Transaction.new_unsigned(message)
            transaction.sign([wallet_client.keypair], Hash(b58decode(blockhash_response[0])))

            logger.info(f"[{operation}] Successfully created transfer transaction")
            logger.debug(f"[{operation}] Returning transaction: {transaction}")
            return transaction
            
        except Exception as e:
            log_error_details(operation, e, "transferring tokens")
            raise

    @monitor_mode_performance
    @with_retries("convert_to_base_unit")
    @trace_operation("convert_to_base_unit")
    async def convert_to_base_unit(
        self,
        parameters: ConvertToBaseUnitParameters,
    ) -> int:
        """Convert token amount to base units."""
        operation = "convert_to_base_unit"
        logger.info(f"[{operation}] Starting operation")
        logger.debug(f"[{operation}] Input parameters: {parameters}")
        
        try:
            # Find token info
            token = next(
                (t for t in self.tokens if t.mint_addresses.get(self.network) == parameters.mint_address),
                None
            )
            
            if not token:
                logger.error(f"[{operation}] Token not found for mint address: {parameters.mint_address}")
                raise TokenNotFoundError(parameters.mint_address)
            
            # Convert to base units
            base_units = int(parameters.amount * (10 ** token.decimals))
            logger.debug(f"[{operation}] Converted {parameters.amount} to {base_units} base units")
            
            return base_units
            
        except Exception as e:
            log_error_details(operation, e, "converting to base units")
            raise

    async def cleanup(self) -> None:
        """Clean up service resources."""
        operation = "cleanup"
        logger.info(f"[{operation}] Starting cleanup")
        logger.debug(f"[{operation}] Service instance: {self}")
        logger.debug(f"[{operation}] Current network: {self.network}")
        logger.debug(f"[{operation}] Token list state: {self.tokens}")

    async def _get_token_symbol_by_mint_address(self, mint_address: str) -> str:
        """Get token symbol by mint address."""
        operation = "_get_token_symbol_by_mint_address"
        logger.debug(f"[{operation}] Looking up token symbol for mint address: {mint_address}")
        for token in self.tokens:
            logger.debug(f"[{operation}] Checking token: {token}")
            logger.debug(f"[{operation}] Token mint addresses: {token.mint_addresses}")
            if mint_address in token.mint_addresses.values():
                logger.debug(f"[{operation}] Found token symbol: {token.symbol}")
                return token.symbol
        logger.error(f"[{operation}] Token not found with mint address: {mint_address}")
        logger.error(f"[{operation}] Available tokens: {[t.symbol for t in self.tokens]}")
        logger.error(f"[{operation}] Token list state: {self.tokens}")
        raise TokenNotFoundError(f"Token not found with mint address: {mint_address}")
