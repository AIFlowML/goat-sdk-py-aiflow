"""Utility function to get token info by symbol."""

from typing import Optional

from ..models import Token, SolanaNetwork
from ..tokens import SPL_TOKENS


def get_token_info_by_symbol(symbol: str, network: SolanaNetwork) -> Optional[Token]:
    """
    Get token information by symbol.

    Args:
        symbol: Token symbol
        network: Solana network

    Returns:
        Token information if found, None otherwise
    """
    return next(
        (
            token
            for token in SPL_TOKENS
            if token.symbol.lower() == symbol.lower()
            and network in token.mint_addresses
        ),
        None,
    )
