"""Utility function to get token info by symbol."""

from typing import Optional, List

from ..models import Token, SolanaNetwork
from ..tokens import SPL_TOKENS


def get_token_info_by_symbol(symbol: str, network: SolanaNetwork, tokens: Optional[List[Token]] = None) -> Optional[Token]:
    """
    Get token information by symbol.

    Args:
        symbol: Token symbol
        network: Solana network
        tokens: Optional list of tokens to search through. If not provided, uses default SPL_TOKENS.

    Returns:
        Token information if found, None otherwise
    """
    token_list = tokens if tokens is not None else SPL_TOKENS
    matching_token = next(
        (token for token in token_list if token.symbol.upper() == symbol.upper()),
        None
    )
    
    if matching_token and network in matching_token.mint_addresses:
        return matching_token
    return None
