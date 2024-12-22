"""Utility function to get tokens for a specific network."""

from typing import List, Optional

from ..models import Token, SolanaNetwork
from ..tokens import SPL_TOKENS


def get_tokens_for_network(network: SolanaNetwork, tokens: Optional[List[Token]] = None) -> List[Token]:
    """
    Get tokens available for a specific network.

    Args:
        network: Solana network
        tokens: Optional list of tokens to filter. If not provided, uses default SPL_TOKENS.

    Returns:
        List of tokens with mint addresses for the network
    """
    token_list = tokens if tokens is not None else SPL_TOKENS
    return [
        token for token in token_list
        if network in token.mint_addresses
    ]
