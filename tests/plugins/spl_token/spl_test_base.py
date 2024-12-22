"""
Base test class for SPL Token plugin tests.
"""
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock
from solders.pubkey import Pubkey as PublicKey
from tests.base_test import BaseGoatTest

class SPLTestBase(BaseGoatTest):
    """Base test class for SPL Token plugin tests with Solana-specific utilities."""

    def setup_token_account(
        self,
        mint_address: str,
        owner_address: str,
        balance: int = 1000000,
        decimals: int = 6,
    ):
        """Helper to setup a mock SPL token account."""
        account = MagicMock()
        account.data = MagicMock()
        account.data.parsed = {
            "info": {
                "mint": mint_address,
                "owner": owner_address,
                "tokenAmount": {
                    "amount": str(balance),
                    "decimals": decimals,
                    "uiAmount": balance / (10 ** decimals),
                },
            },
            "type": "account",
        }
        return account

    def setup_token_mint(
        self,
        mint_address: str,
        decimals: int = 6,
        freeze_authority: str = None,
        mint_authority: str = None,
    ):
        """Helper to setup a mock SPL token mint account."""
        mint = MagicMock()
        mint.data = MagicMock()
        mint.data.parsed = {
            "info": {
                "decimals": decimals,
                "freezeAuthority": freeze_authority,
                "mintAuthority": mint_authority,
                "isInitialized": True,
                "supply": "0",
            },
            "type": "mint",
        }
        return mint

    def setup_solana_transaction(
        self,
        recent_blockhash: str = "GHtXQBsoZHVnNFa9YhXQqHzznzZqG6Ck6V6xGK4NUWsh",
        fee_payer: str = None,
    ):
        """Helper to setup a mock Solana transaction."""
        tx = MagicMock()
        tx.recent_blockhash = recent_blockhash
        tx.fee_payer = PublicKey(fee_payer) if fee_payer else None
        tx.signatures = []
        tx.compile = AsyncMock()
        tx.sign = AsyncMock()
        return tx

    def setup_solana_wallet(
        self,
        public_key: str = None,
        balance: int = 1000000000,  # 1 SOL
    ):
        """Helper to setup a mock Solana wallet."""
        wallet = MagicMock()
        wallet.public_key = PublicKey(public_key) if public_key else PublicKey(1)
        wallet.sign_transaction = AsyncMock()
        wallet.sign_all_transactions = AsyncMock()
        return wallet

    def create_mock_token_info(
        self,
        symbol: str = "TEST",
        name: str = "Test Token",
        decimals: int = 6,
        mint_addresses: Dict[str, str] = None,
        mode_config: Dict[str, Any] = None,
    ):
        """Create mock token information."""
        return {
            "symbol": symbol,
            "name": name,
            "decimals": decimals,
            "mint_addresses": mint_addresses or {
                "mainnet": "11111111111111111111111111111111",
                "devnet": "11111111111111111111111111111111",
            },
            "mode_config": mode_config or {
                "transfer_fee": 0.001,
                "min_transfer": 0.01,
            },
        }
