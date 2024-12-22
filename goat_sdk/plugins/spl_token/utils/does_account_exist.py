"""Utility function to check if a token account exists."""

import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
from base58 import b58encode
import asyncio

from goat_sdk.plugins.spl_token.utils.token_account import get_associated_token_address
from goat_sdk.plugins.spl_token.exceptions import TokenAccountNotFoundError

logger = logging.getLogger(__name__)

async def does_account_exist(
    connection_future,
    owner_pubkey: Pubkey,
    mint_pubkey: Pubkey,
    mode_config: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Check if a token account exists for the given owner and mint.
    
    Args:
        connection_future: Future that resolves to RPC connection
        owner_pubkey: Owner's public key
        mint_pubkey: Token mint public key
        mode_config: Optional configuration for Mode-specific behavior
            retry_on_not_found: Whether to retry if account not found
            retry_attempts: Number of retry attempts
            raise_on_error: Whether to raise exceptions
        
    Returns:
        Token account address if it exists, None otherwise
        
    Raises:
        TokenAccountNotFoundError: If raise_on_error is True and account not found
    """
    mode_config = mode_config or {}
    retry_on_not_found = mode_config.get('retry_on_not_found', False)
    retry_attempts = mode_config.get('retry_attempts', 2)
    raise_on_error = mode_config.get('raise_on_error', False)
    
    async def _check_account():
        try:
            logger.debug(f"Checking token account existence for owner: {owner_pubkey}, mint: {mint_pubkey}")
            
            # Get associated token address
            token_account = await get_associated_token_address(
                str(owner_pubkey),
                str(mint_pubkey)
            )
            logger.debug(f"Associated token address: {token_account}")
            
            # Check if account exists
            account_info = await connection_future.get_account_info(Pubkey.from_string(token_account))
            logger.debug(f"Account info response: {account_info}")
            
            # Handle both tuple response and mock response cases
            if isinstance(account_info, tuple):
                exists = account_info[0] is not None
            else:
                exists = getattr(account_info, 'value', None) is not None
                
            if exists:
                logger.info(f"Token account exists: {token_account}")
                return token_account
                
            logger.info(f"Token account does not exist: {token_account}")
            if raise_on_error:
                raise TokenAccountNotFoundError("Associated Token", str(owner_pubkey))
            return None
                
        except Exception as e:
            logger.error(f"Error checking account existence: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error attributes: {vars(e) if hasattr(e, '__dict__') else {}}")
            
            if raise_on_error:
                raise TokenAccountNotFoundError("Associated Token", str(owner_pubkey))
            
            # Fallback: try to find account through get_token_accounts_by_owner
            try:
                logger.debug("Attempting fallback through get_token_accounts_by_owner")
                accounts = await connection_future.get_token_accounts_by_owner(
                    owner_pubkey,
                    [{"mint": str(mint_pubkey)}]
                )
                logger.debug(f"Token accounts response: {accounts}")
                
                if accounts and accounts.get("value"):
                    token_account = accounts["value"][0]["pubkey"]
                    logger.info(f"Found token account through fallback: {token_account}")
                    return token_account
                    
                logger.info("No token account found through fallback")
                if raise_on_error:
                    raise TokenAccountNotFoundError("Associated Token", str(owner_pubkey))
                return None
                
            except Exception as fallback_error:
                logger.error(f"Fallback attempt failed: {str(fallback_error)}")
                logger.error(f"Fallback error type: {type(fallback_error)}")
                logger.error(f"Fallback error attributes: {vars(fallback_error) if hasattr(fallback_error, '__dict__') else {}}")
                if raise_on_error:
                    raise TokenAccountNotFoundError("Associated Token", str(owner_pubkey))
                return None

    # Initial attempt
    try:
        result = await _check_account()
        if result is not None or not retry_on_not_found:
            return result
            
        # Retry logic
        for attempt in range(retry_attempts):
            logger.debug(f"Retry attempt {attempt + 1} of {retry_attempts}")
            await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            result = await _check_account()
            if result is not None:
                return result
                
        return None
    except TokenAccountNotFoundError:
        if raise_on_error:
            raise
        return None
