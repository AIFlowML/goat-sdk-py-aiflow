"""Wallet client for Mode SDK."""

from typing import Optional, Dict, Any, List
from .client_base import ModeClientBase


class ModeWalletClient(ModeClientBase):
    """Wallet client for Mode SDK."""

    def __init__(self, public_key: str):
        """Initialize wallet client.
        
        Args:
            public_key: Public key of the wallet
        """
        super().__init__()
        self.public_key = public_key

    def deserialize_transaction(self, transaction_data: bytes) -> Any:
        """Deserialize transaction data.
        
        Args:
            transaction_data: Raw transaction data
        
        Returns:
            Deserialized transaction
        """
        raise NotImplementedError

    async def send_transaction(
        self,
        transaction: Any,
        address_lookup_tables: Optional[List[str]] = None,
    ) -> str:
        """Send transaction.
        
        Args:
            transaction: Transaction to send
            address_lookup_tables: Optional address lookup tables
        
        Returns:
            Transaction signature
        """
        raise NotImplementedError 