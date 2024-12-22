"""Constants for SPL token operations."""

from enum import Enum


class SolanaNetwork(Enum):
    """Solana network enum."""
    MAINNET = "mainnet"
    DEVNET = "devnet"


# Token Program ID on Solana
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

# Associated Token Account Program ID
ASSOCIATED_TOKEN_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"

# Maximum retries for token operations
MAX_RETRIES = 3

# Default timeout for token operations (in seconds)
DEFAULT_TIMEOUT = 30

# Default decimals for SPL tokens
DEFAULT_DECIMALS = 9

# Maximum amount of tokens that can be transferred
MAX_TRANSFER_AMOUNT = 1_000_000_000 