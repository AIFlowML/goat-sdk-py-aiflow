"""Utility function to get token info by mint address."""

import logging
from typing import List, Optional

from ..models import Token, SolanaNetwork
from ..exceptions import InvalidTokenAddressError

logger = logging.getLogger(__name__)


def get_token_by_mint_address(
    mint_address: str,
    network: SolanaNetwork,
    tokens: List[Token],
    mode_config: Optional[dict] = None,
) -> Optional[Token]:
    """Get token information by mint address.

    Args:
        mint_address: Token mint address to search for
        network: Network to search in
        tokens: List of available tokens
        mode_config: Optional Mode-specific configuration

    Returns:
        Token information if found, None otherwise
        
    Raises:
        InvalidTokenAddressError: If mint_address is None and raise_on_error is True
    """
    logger.debug(f"Looking up token with mint address: {mint_address} on network: {network}")
    
    if mint_address is None:
        logger.debug("None mint address provided")
        if mode_config and mode_config.get("raise_on_error"):
            raise InvalidTokenAddressError("Mint address cannot be None")
        return None
    
    if not mint_address:
        logger.debug("Empty mint address provided")
        return None
    
    try:
        for token in tokens:
            logger.debug(f"Checking token: {token.symbol}")
            logger.debug(f"Token mint addresses: {token.mint_addresses}")
            
            # Check if token is supported on the network
            if network not in token.mint_addresses:
                logger.debug(f"Token {token.symbol} not supported on network {network}")
                continue
            
            # Check if mint address matches
            token_mint = token.mint_addresses[network]
            if token_mint == mint_address:
                # Check Mode-specific validations
                if mode_config and mode_config.get("network_validation"):
                    # For Mode validation, we require the token to be supported on mainnet
                    if network != SolanaNetwork.MAINNET:
                        logger.debug(f"Token {token.symbol} lookup not allowed on {network} with Mode validation")
                        return None
                    # Check if token has Mode-specific attributes
                    if not hasattr(token, "mode_config"):
                        logger.debug(f"Token {token.symbol} does not have Mode configuration")
                        return None
                
                logger.debug(f"Found token {token.symbol} on network {network}")
                return token
        
        logger.debug(f"No token found with mint address: {mint_address}")
        return None
        
    except Exception as e:
        logger.error(f"Error looking up token: {str(e)}", exc_info=True)
        if mode_config and mode_config.get("raise_on_error"):
            raise
        return None
