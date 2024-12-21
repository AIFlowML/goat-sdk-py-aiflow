"""Utility function to get token info by mint address."""

import logging
from typing import Optional

from ..models import Token, SolanaNetwork
from ..tokens import SPL_TOKENS


logger = logging.getLogger(__name__)


def get_token_by_mint_address(
    mint_address: str,
    network: SolanaNetwork,
    mode_config: Optional[dict] = None,
) -> Optional[Token]:
    """
    Get token information by mint address.

    Args:
        mint_address: Token mint address
        network: Solana network
        mode_config: Optional Mode-specific configuration

    Returns:
        Token information if found, None otherwise
    """
    try:
        # Check if mint address is valid
        if not mint_address or not isinstance(mint_address, str):
            logger.warning("Invalid mint address provided")
            return None

        # Get token by mint address
        token = next(
            (
                token
                for token in SPL_TOKENS
                if token.mint_addresses.get(str(network)) == mint_address
            ),
            None,
        )

        # Apply Mode-specific validations if configured
        if token and mode_config:
            # Check if token is supported by Mode
            if not token.mode_config:
                logger.warning(f"Token {token.symbol} is not supported by Mode")
                return None

            # Check if token is enabled for the network
            if mode_config.get("network_validation") and network not in token.mint_addresses:
                logger.warning(f"Token {token.symbol} is not enabled for network {network}")
                return None

        return token

    except Exception as e:
        logger.error(f"Error getting token by mint address: {str(e)}")
        if mode_config and mode_config.get("raise_on_error"):
            raise
        return None
