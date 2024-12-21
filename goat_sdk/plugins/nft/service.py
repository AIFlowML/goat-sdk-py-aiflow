"""NFT service implementation."""

from typing import Dict, Any
from goat_sdk.core.decorators import tool
from goat_sdk.core.utils.retry import with_retry
from goat_sdk.core.telemetry.middleware import trace_transaction
from metaplex.bubblegum import (
    get_asset_with_proof,
    create_transfer_instruction,
    BubblegumProgram
)
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.transaction import Transaction
from .types import TransferNFTParams

class NFTService:
    """Service for NFT operations."""

    @tool(
        description="Send an NFT from your wallet to another address",
        parameters={
            "type": "object",
            "properties": {
                "recipient_address": {
                    "type": "string",
                    "description": "The address to send the NFT to",
                    "examples": ["GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"]
                },
                "asset_id": {
                    "type": "string",
                    "description": "The asset ID of the NFT to send",
                    "examples": ["Ah2Nvmc4YzwqzqyFYV6UBfXZCWFk3YfEwGp4TJgqgM5x"]
                }
            },
            "required": ["recipient_address", "asset_id"]
        }
    )
    @with_retry()
    @trace_transaction("solana")
    async def transfer_nft(self, wallet_client: Any, params: Dict[str, Any]) -> str:
        """Transfer an NFT.
        
        Args:
            wallet_client: Solana wallet client
            params: Transfer parameters
            
        Returns:
            Transaction signature
        """
        # Validate parameters
        transfer_params = TransferNFTParams(**params)
        
        # Create connection
        connection = AsyncClient(wallet_client.provider_url)
        
        # Get asset with proof
        asset_with_proof = await get_asset_with_proof(
            connection,
            PublicKey(transfer_params.asset_id),
            truncate_canopy=True
        )
        
        # Create transfer instruction
        transfer_ix = create_transfer_instruction(
            BubblegumProgram.ID,
            asset_with_proof,
            PublicKey(wallet_client.get_address()),
            PublicKey(transfer_params.recipient_address)
        )
        
        # Send transaction
        transaction = Transaction().add(transfer_ix)
        result = await wallet_client.send_transaction(transaction)
        
        return result["hash"]
