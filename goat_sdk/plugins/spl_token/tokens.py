"""Token definitions for SPL tokens."""

from typing import List
from .models import Token, SolanaNetwork


# Default SPL tokens
SPL_TOKENS: List[Token] = [
    Token(
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            SolanaNetwork.DEVNET: "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        },
        mode_config={
            "transfer_fee": 0.001,  # 0.1% fee for Mode transfers
            "min_transfer": 0.01,   # Minimum transfer amount
        }
    ),
    Token(
        symbol="USDT",
        name="Tether USD",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
            SolanaNetwork.DEVNET: "DUSTawucrTsGU8hcqRdHDCbuYhCPADMLM2VcCb8VnFnQ",
        },
        mode_config={
            "transfer_fee": 0.001,
            "min_transfer": 0.01,
        }
    ),
    Token(
        symbol="SOL",
        name="Solana",
        decimals=9,
        mint_addresses={
            SolanaNetwork.MAINNET: "So11111111111111111111111111111111111111112",
            SolanaNetwork.DEVNET: "So11111111111111111111111111111111111111112",
            SolanaNetwork.TESTNET: "So11111111111111111111111111111111111111112",
        },
        mode_config={
            "transfer_fee": 0.0005,  # 0.05% fee for SOL transfers
            "min_transfer": 0.001,   # Minimum transfer amount
        }
    ),
]
