"""Unified tests for SPL Token Service with common mocking strategy."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY
from solders.transaction import Transaction
from solana.rpc.commitment import Commitment
from base58 import b58decode

from goat_sdk.plugins.spl_token.exceptions import (
    TokenAccountNotFoundError,
    TokenTransferError,
    InsufficientBalanceError,
)
from goat_sdk.plugins.spl_token.spl_token_service import SplTokenService
from goat_sdk.plugins.spl_token.models import TokenType, Token, SolanaNetwork
from goat_sdk.plugins.spl_token.parameters import (
    GetTokenBalanceByMintAddressParameters,
    TransferTokenByMintAddressParameters,
)
from goat_sdk.plugins.spl_token.utils.constants import USDC_MINT_ADDRESS

import logging
import os
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "test_full_token_transfer_flow.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create a test keypair
TEST_KEYPAIR = Keypair()
TEST_OWNER_ADDRESS = str(TEST_KEYPAIR.pubkey())
TEST_MINT_ADDRESS = USDC_MINT_ADDRESS
TEST_TOKEN_ACCOUNT = "TFsLPaKALiXSRnm9LqT8mmRbcK3AfKpPd8pAxAqBFMN"
TEST_DESTINATION_ADDRESS = "HWHvQhFmJB6gPtB6oXNw8PNM5hUWAhUnE4GFsKe254xZ"
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

@pytest.fixture
def mock_wallet_client():
    """Create a mock wallet client."""
    mock = MagicMock()
    mock.get_connection = AsyncMock()
    mock.get_wallet_address = AsyncMock()
    mock.get_wallet_address.return_value = TEST_OWNER_ADDRESS
    mock.keypair = TEST_KEYPAIR
    return mock

@pytest.fixture
def mock_connection(mock_wallet_client):
    """Create a mock connection."""
    mock = AsyncMock()
    mock.get_token_account_balance = AsyncMock()
    mock.get_token_account_balance.return_value = {
        "context": {"slot": 1},
        "value": {"amount": "100000000", "decimals": 6, "uiAmount": 100.0, "uiAmountString": "100"},
    }
    mock.get_latest_blockhash = AsyncMock()
    mock.get_latest_blockhash.return_value = ("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi", 123)
    mock.send_transaction = AsyncMock()
    mock_wallet_client.get_connection.return_value = mock
    return mock

@pytest.fixture
def mock_insufficient_balance_connection(mock_wallet_client):
    """Create a mock connection with insufficient balance."""
    mock = AsyncMock()
    mock.get_token_account_balance = AsyncMock()
    mock.get_token_account_balance.return_value = {
        "context": {"slot": 1},
        "value": {"amount": "100000", "decimals": 6, "uiAmount": 0.1, "uiAmountString": "0.1"},
    }
    mock.get_latest_blockhash = AsyncMock()
    mock.get_latest_blockhash.return_value = ("4vJ9JU1bJJE96FWSJKvHsmmFADCg4gpZQff4P3bkLKi", 123)
    mock.send_transaction = AsyncMock()
    mock_wallet_client.get_connection.return_value = mock
    return mock

@pytest.fixture
def spl_token_service(mock_wallet_client):
    """Create an SPL Token Service instance."""
    tokens = [
        Token(
            name="USD Coin",
            symbol="USDC",
            decimals=6,
            mint_addresses={
                SolanaNetwork.DEVNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                SolanaNetwork.MAINNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            },
            logo_uri="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
            token_type=TokenType.FUNGIBLE,
        )
    ]
    service = SplTokenService(network=SolanaNetwork.MAINNET, tokens=tokens)
    service.wallet_client = mock_wallet_client
    return service

@pytest.mark.asyncio
async def test_get_token_balance_success(spl_token_service, mock_connection):
    """Test getting token balance successfully."""
    logger.info("Starting test_get_token_balance_success")
    
    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist", new_callable=AsyncMock) as mock_exists:
        mock_exists.return_value = TEST_TOKEN_ACCOUNT
        
        # Get token balance
        balance = await spl_token_service.get_token_balance_by_mint_address(
            wallet_client=spl_token_service.wallet_client,
            parameters=GetTokenBalanceByMintAddressParameters(
                wallet_address=TEST_OWNER_ADDRESS,
                mint_address=TEST_MINT_ADDRESS,
                token_symbol="USDC"
            )
        )
        
        assert balance == 100.0
        logger.info("test_get_token_balance_success completed")

@pytest.mark.asyncio
async def test_transfer_token_success(spl_token_service, mock_connection):
    """Test transferring tokens successfully."""
    logger.info("Starting test_transfer_token_success")
    
    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist", new_callable=AsyncMock) as mock_exists:
        mock_exists.return_value = TEST_TOKEN_ACCOUNT
        
        # Transfer tokens
        transaction = await spl_token_service.transfer_token_by_mint_address(
            wallet_client=spl_token_service.wallet_client,
            parameters=TransferTokenByMintAddressParameters(
                to=TEST_DESTINATION_ADDRESS,
                mint_address=TEST_MINT_ADDRESS,
                amount=10000000
            )
        )
        
        assert isinstance(transaction, Transaction)
        logger.info("test_transfer_token_success completed")

@pytest.mark.asyncio
async def test_transfer_insufficient_balance(spl_token_service, mock_insufficient_balance_connection):
    """Test transferring tokens with insufficient balance."""
    logger.info("Starting test_transfer_insufficient_balance")
    
    with patch("goat_sdk.plugins.spl_token.spl_token_service.does_account_exist", new_callable=AsyncMock) as mock_exists:
        mock_exists.return_value = TEST_TOKEN_ACCOUNT
        
        # Attempt to transfer more tokens than available
        with pytest.raises(InsufficientBalanceError) as exc_info:
            await spl_token_service.transfer_token_by_mint_address(
                wallet_client=spl_token_service.wallet_client,
                parameters=TransferTokenByMintAddressParameters(
                    to=TEST_DESTINATION_ADDRESS,
                    mint_address=TEST_MINT_ADDRESS,
                    amount=1000000000000  # More than available balance
                )
            )
        
        error = exc_info.value
        assert error.required == 1000000000000
        assert error.available == 100000
        assert error.token_symbol == "USDC"
        
        logger.info("test_transfer_insufficient_balance completed")

@pytest.mark.asyncio
async def test_account_not_found(spl_token_service):
    """Test handling non-existent token account."""
    logger.info("Starting test_account_not_found")
    mock_wallet_client = spl_token_service.wallet_client
    mock_connection = await mock_wallet_client.get_connection()
    
    # Mock empty token accounts response
    mock_connection.get_token_accounts_by_owner = AsyncMock(return_value={"value": []})
    mock_connection.get_account_info = AsyncMock(return_value=MagicMock(value=None))
    
    with pytest.raises(TokenAccountNotFoundError) as exc_info:
        await spl_token_service.get_token_balance_by_mint_address(
            wallet_client=spl_token_service.wallet_client,
            parameters=GetTokenBalanceByMintAddressParameters(
                wallet_address=TEST_OWNER_ADDRESS,
                mint_address=TEST_MINT_ADDRESS,
                token_symbol="USDC"
            )
        )
    logger.info(f"Got expected error: {exc_info.value}")