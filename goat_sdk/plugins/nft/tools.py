
"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
      
     Path: goat_sdk/plugins/hyperliquid/utils.py
"""
"""Tools for NFT plugin."""

from typing import Dict, Any, List
from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.core.utils.retry import with_retry
from goat_sdk.core.telemetry.middleware import trace_transaction
from .types import MintNFTParams, TransferNFTParams, NFTInfo

class MintNFTTool(ToolBase):
    """Tool for minting NFTs."""
    
    name = "mint_nft"
    description = "Mint a new NFT on Solana"
    parameters = {
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "symbol": {"type": "string"},
                    "description": {"type": "string"},
                    "image": {"type": "string"},
                    "seller_fee_basis_points": {"type": "integer"},
                    "animation_url": {"type": "string", "optional": True},
                    "external_url": {"type": "string", "optional": True},
                    "attributes": {"type": "array", "optional": True},
                    "collection": {"type": "object", "optional": True},
                    "properties": {"type": "object", "optional": True}
                },
                "required": ["name", "symbol", "description", "image"]
            },
            "is_mutable": {"type": "boolean", "optional": True},
            "max_supply": {"type": "integer", "optional": True}
        },
        "required": ["metadata"]
    }

    @with_retry()
    @trace_transaction("solana")
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NFT minting.
        
        Args:
            params: Minting parameters
            
        Returns:
            NFT information
        """
        mint_params = MintNFTParams(**params)
        nft_info = await self.plugin.mint_nft(mint_params)
        return nft_info.dict()

class TransferNFTTool(ToolBase):
    """Tool for transferring NFTs."""
    
    name = "transfer_nft"
    description = "Transfer an NFT to another address"
    parameters = {
        "type": "object",
        "properties": {
            "mint_address": {"type": "string"},
            "to_address": {"type": "string"}
        },
        "required": ["mint_address", "to_address"]
    }

    @with_retry()
    @trace_transaction("solana")
    async def execute(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Execute NFT transfer.
        
        Args:
            params: Transfer parameters
            
        Returns:
            Transaction signature
        """
        transfer_params = TransferNFTParams(**params)
        signature = await self.plugin.transfer_nft(transfer_params)
        return {"signature": signature}

class GetNFTTool(ToolBase):
    """Tool for getting NFT information."""
    
    name = "get_nft"
    description = "Get information about an NFT"
    parameters = {
        "type": "object",
        "properties": {
            "mint_address": {"type": "string"}
        },
        "required": ["mint_address"]
    }

    @with_retry()
    @trace_transaction("solana")
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NFT info retrieval.
        
        Args:
            params: Query parameters
            
        Returns:
            NFT information
        """
        nft_info = await self.plugin.get_nft(params["mint_address"])
        return nft_info.dict()

class GetNFTsByOwnerTool(ToolBase):
    """Tool for getting NFTs by owner."""
    
    name = "get_nfts_by_owner"
    description = "Get all NFTs owned by an address"
    parameters = {
        "type": "object",
        "properties": {
            "owner_address": {"type": "string"}
        },
        "required": ["owner_address"]
    }

    @with_retry()
    @trace_transaction("solana")
    async def execute(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute NFT list retrieval.
        
        Args:
            params: Query parameters
            
        Returns:
            List of NFT information
        """
        nfts = await self.plugin.get_nfts_by_owner(params["owner_address"])
        return [nft.dict() for nft in nfts]
