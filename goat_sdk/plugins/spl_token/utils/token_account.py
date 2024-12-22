"""Utility functions for SPL Token account operations."""

import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.transaction import Transaction
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT as SYSVAR_RENT_PUBKEY

from goat_sdk.plugins.spl_token.utils.constants import (
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
)

logger = logging.getLogger(__name__)

async def get_associated_token_address(
    owner_address: str,
    mint_address: str,
) -> str:
    """Get the associated token account address for a wallet and mint.

    Args:
        owner_address: Owner's wallet address
        mint_address: Token mint address

    Returns:
        Associated token account address
    """
    try:
        logger.debug(f"Getting associated token address for owner: {owner_address}, mint: {mint_address}")
        owner = Pubkey.from_string(owner_address)
        mint = Pubkey.from_string(mint_address)
        token_program_id = Pubkey.from_string(TOKEN_PROGRAM_ID)
        associated_token_program_id = Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID)

        seeds = [
            bytes(owner),
            bytes(token_program_id),
            bytes(mint),
        ]
        
        program_address, _ = Pubkey.find_program_address(
            seeds,
            associated_token_program_id,
        )
        
        logger.debug(f"Found associated token address: {program_address}")
        return str(program_address)
    except Exception as e:
        logger.error(f"Error getting associated token address: {str(e)}")
        raise

async def create_associated_token_account(
    owner_address: str,
    mint_address: str,
    payer_address: str,
) -> Transaction:
    """Create an associated token account transaction.

    Args:
        owner_address: Owner's wallet address
        mint_address: Token mint address
        payer_address: Address that will pay for the account creation

    Returns:
        Transaction to create the associated token account
    """
    try:
        logger.debug(f"Creating associated token account for owner: {owner_address}, mint: {mint_address}")
        owner = Pubkey.from_string(owner_address)
        mint = Pubkey.from_string(mint_address)
        payer = Pubkey.from_string(payer_address)
        token_program_id = Pubkey.from_string(TOKEN_PROGRAM_ID)
        associated_token_program_id = Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID)
        
        associated_token_address = await get_associated_token_address(owner_address, mint_address)
        associated_token_pubkey = Pubkey.from_string(associated_token_address)
        
        keys = [
            AccountMeta(payer, True, True),
            AccountMeta(associated_token_pubkey, False, True),
            AccountMeta(owner, False, False),
            AccountMeta(mint, False, False),
            AccountMeta(SYS_PROGRAM_ID, False, False),
            AccountMeta(token_program_id, False, False),
            AccountMeta(SYSVAR_RENT_PUBKEY, False, False),
        ]
        
        create_ix = Instruction(
            program_id=associated_token_program_id,
            accounts=keys,
            data=bytes([]),
        )
        
        transaction = Transaction()
        transaction.add(create_ix)
        
        logger.debug(f"Created transaction to create associated token account: {transaction}")
        return transaction
    except Exception as e:
        logger.error(f"Error creating associated token account transaction: {str(e)}")
        raise

async def get_token_account_balance(connection, token_account_address: str) -> Dict[str, Any]:
    """Get the balance of a token account.

    Args:
        connection: RPC connection
        token_account_address: Token account address

    Returns:
        Token account balance information
    """
    try:
        logger.debug(f"Getting token account balance for: {token_account_address}")
        token_account = Pubkey.from_string(token_account_address)
        balance = await connection.get_token_account_balance(token_account)
        logger.debug(f"Token account balance: {balance}")
        return balance
    except Exception as e:
        logger.error(f"Error getting token account balance: {str(e)}")
        raise

async def get_token_accounts_by_owner(
    connection,
    owner_address: str,
    mint_address: Optional[str] = None,
) -> Dict[str, Any]:
    """Get all token accounts owned by an address.

    Args:
        connection: RPC connection
        owner_address: Owner's wallet address
        mint_address: Optional token mint address to filter by

    Returns:
        List of token accounts
    """
    try:
        logger.debug(f"Getting token accounts for owner: {owner_address}")
        owner = Pubkey.from_string(owner_address)
        program_id = Pubkey.from_string(TOKEN_PROGRAM_ID)
        
        filters = [{"programId": str(program_id)}]
        if mint_address:
            mint = Pubkey.from_string(mint_address)
            filters.append({"mint": str(mint)})
        
        accounts = await connection.get_token_accounts_by_owner(owner, filters)
        logger.debug(f"Found token accounts: {accounts}")
        return accounts
    except Exception as e:
        logger.error(f"Error getting token accounts by owner: {str(e)}")
        raise

async def get_token_account_info(connection, token_account_address: str) -> Dict[str, Any]:
    """Get information about a token account.

    Args:
        connection: RPC connection
        token_account_address: Token account address

    Returns:
        Token account information
    """
    try:
        logger.debug(f"Getting token account info for: {token_account_address}")
        token_account = Pubkey.from_string(token_account_address)
        info = await connection.get_account_info(token_account)
        logger.debug(f"Token account info: {info}")
        return info
    except Exception as e:
        logger.error(f"Error getting token account info: {str(e)}")
        raise

def get_token_account_data(account_info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract token account data from account info.

    Args:
        account_info: Account info response

    Returns:
        Token account data
    """
    try:
        logger.debug("Extracting token account data")
        data = account_info["value"]["data"]["parsed"]["info"]
        logger.debug(f"Token account data: {data}")
        return data
    except Exception as e:
        logger.error(f"Error extracting token account data: {str(e)}")
        raise

def get_token_account_mint(account_data: Dict[str, Any]) -> str:
    """Get mint address from token account data.

    Args:
        account_data: Token account data

    Returns:
        Mint address
    """
    try:
        logger.debug("Getting mint address from token account data")
        mint = account_data["mint"]
        logger.debug(f"Mint address: {mint}")
        return mint
    except Exception as e:
        logger.error(f"Error getting mint address: {str(e)}")
        raise

def get_token_account_owner(account_data: Dict[str, Any]) -> str:
    """Get owner address from token account data.

    Args:
        account_data: Token account data

    Returns:
        Owner address
    """
    try:
        logger.debug("Getting owner address from token account data")
        owner = account_data["owner"]
        logger.debug(f"Owner address: {owner}")
        return owner
    except Exception as e:
        logger.error(f"Error getting owner address: {str(e)}")
        raise

def get_token_account_amount(account_data: Dict[str, Any]) -> str:
    """Get token amount from token account data.

    Args:
        account_data: Token account data

    Returns:
        Token amount as string
    """
    try:
        logger.debug("Getting token amount from token account data")
        amount = account_data["tokenAmount"]["amount"]
        logger.debug(f"Token amount: {amount}")
        return amount
    except Exception as e:
        logger.error(f"Error getting token amount: {str(e)}")
        raise

def get_token_account_decimals(account_data: Dict[str, Any]) -> int:
    """Get token decimals from token account data.

    Args:
        account_data: Token account data

    Returns:
        Token decimals
    """
    try:
        logger.debug("Getting token decimals from token account data")
        decimals = account_data["tokenAmount"]["decimals"]
        logger.debug(f"Token decimals: {decimals}")
        return decimals
    except Exception as e:
        logger.error(f"Error getting token decimals: {str(e)}")
        raise

def get_token_account_ui_amount(account_data: Dict[str, Any]) -> float:
    """Get token UI amount from token account data.

    Args:
        account_data: Token account data

    Returns:
        Token UI amount
    """
    try:
        logger.debug("Getting token UI amount from token account data")
        ui_amount = account_data["tokenAmount"]["uiAmount"]
        logger.debug(f"Token UI amount: {ui_amount}")
        return ui_amount
    except Exception as e:
        logger.error(f"Error getting token UI amount: {str(e)}")
        raise 