"""Utility function to get tokens for a specific network."""

from typing import List

from ..models import Token, SolanaNetwork
from ..tokens import SPL_TOKENS


def get_tokens_for_network(network: SolanaNetwork) -> List[Token]:
    """
    Get tokens available for a specific network.

    Args:
        network: Solana network

    Returns:
        List of tokens with mint addresses for the network
    """
    return [
        token for token in SPL_TOKENS
        if network in token.mint_addresses
    ]
