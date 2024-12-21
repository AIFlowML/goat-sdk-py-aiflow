"""Utility functions for SPL token operations."""

from typing import List, Optional
from base58 import b58decode

from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork
from goat_sdk.plugins.spl_token.exceptions import TokenNotFoundError


async def get_token_info_by_symbol(
    tokens: List[Token],
    symbol: str,
    network: SolanaNetwork = SolanaNetwork.MAINNET,
) -> Token:
    """Get token information by symbol.

    Args:
        tokens: List of available tokens
        symbol: Token symbol to search for
        network: Network to search in (default: mainnet)

    Returns:
        Token information

    Raises:
        TokenNotFoundError: If token is not found or not supported on the network
    """
    for token in tokens:
        if token.symbol == symbol:
            if network not in token.mint_addresses:
                raise TokenNotFoundError(f"Token {symbol} not supported on {network}")
            return token
    raise TokenNotFoundError(f"Token {symbol} not found")


def get_tokens_for_network(
    tokens: List[Token],
    network: SolanaNetwork,
) -> List[Token]:
    """Get list of tokens available on a specific network.

    Args:
        tokens: List of available tokens
        network: Network to filter by

    Returns:
        List of tokens available on the network
    """
    return [token for token in tokens if network in token.mint_addresses]


def get_token_by_mint_address(
    tokens: List[Token],
    mint_address: str,
    network: Optional[SolanaNetwork] = None,
) -> Optional[Token]:
    """Get token information by mint address.

    Args:
        tokens: List of available tokens
        mint_address: Token mint address to search for
        network: Optional network to search in

    Returns:
        Token information if found, None otherwise
    """
    for token in tokens:
        if network:
            if network in token.mint_addresses and token.mint_addresses[network] == mint_address:
                return token
        else:
            for token_mint_address in token.mint_addresses.values():
                if token_mint_address == mint_address:
                    return token
    return None


async def does_account_exist(
    wallet_client,
    address: str,
) -> bool:
    """Check if a Solana account exists.

    Args:
        wallet_client: Wallet client instance
        address: Account address to check

    Returns:
        True if account exists, False otherwise
    """
    try:
        # Try to decode the address to validate it
        b58decode(address.replace("0x", ""))
        
        # Get account info
        account_info = await wallet_client.connection.get_account_info(address)
        return account_info.value is not None
    except Exception:
        return False
