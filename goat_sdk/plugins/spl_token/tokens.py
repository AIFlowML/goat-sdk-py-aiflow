"""SPL token definitions."""

from typing import List

from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork, TokenType


SPL_TOKENS: List[Token] = [
    Token(
        name="USD Coin",
        symbol="USDC",
        decimals=6,
        mint_addresses={
            SolanaNetwork.MAINNET: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            SolanaNetwork.DEVNET: "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        },
        logo_uri="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/logo.png",
        token_type=TokenType.FUNGIBLE,
    ),
    Token(
        name="Solana",
        symbol="SOL",
        decimals=9,
        mint_addresses={
            SolanaNetwork.MAINNET: "So11111111111111111111111111111111111111112",
            SolanaNetwork.DEVNET: "So11111111111111111111111111111111111111112",
        },
        logo_uri="https://raw.githubusercontent.com/solana-labs/token-list/main/assets/mainnet/So11111111111111111111111111111111111111112/logo.png",
        token_type=TokenType.FUNGIBLE,
    ),
]
