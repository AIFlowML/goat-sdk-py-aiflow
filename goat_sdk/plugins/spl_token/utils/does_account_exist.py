"""Utility function to check if a Solana account exists."""

import logging
from typing import Optional
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from spl.token.instructions import get_associated_token_address

from ..exceptions import TokenAccountNotFoundError

logger = logging.getLogger(__name__)


async def does_account_exist(
    connection: AsyncClient,
    owner: PublicKey,
    mint: PublicKey,
    mode_config: Optional[dict] = None,
) -> Optional[PublicKey]:
    """Check if a token account exists.
    
    Args:
        connection: Solana RPC connection
        owner: Account owner
        mint: Token mint address
        mode_config: Optional Mode-specific configuration
        
    Returns:
        Associated token account public key if exists, None otherwise
        
    Raises:
        TokenAccountNotFoundError: If there's an error checking account existence
    """
    try:
        # Get the associated token account address
        associated_token_address = get_associated_token_address(owner, mint)
        
        # Check if the account exists
        account_info = await connection.get_account_info(associated_token_address)
        
        # Apply Mode-specific retry logic if configured
        if not account_info.value and mode_config and mode_config.get("retry_on_not_found"):
            retry_attempts = mode_config.get("retry_attempts", 1)
            for _ in range(retry_attempts):
                logger.debug(f"Retrying account check for {associated_token_address}")
                account_info = await connection.get_account_info(associated_token_address)
                if account_info.value:
                    break
        
        return associated_token_address if account_info.value else None
        
    except Exception as e:
        logger.error(f"Failed to check account existence: {str(e)}")
        if mode_config and mode_config.get("raise_on_error"):
            raise TokenAccountNotFoundError(f"Failed to check account existence: {str(e)}")
        return None
