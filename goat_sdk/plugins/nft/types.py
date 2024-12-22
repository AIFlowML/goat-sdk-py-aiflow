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

"""Type definitions for NFT plugin."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, constr

class Creator(BaseModel):
    """NFT creator information."""
    address: constr(min_length=32, max_length=44)
    share: int = Field(ge=0, le=100)
    verified: bool = False

    model_config = ConfigDict(frozen=True, extra="forbid")

class NFTMetadata(BaseModel):
    """NFT metadata following Metaplex standard."""
    name: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1, max_length=10)
    description: str = Field(default="")
    seller_fee_basis_points: int = Field(default=0, ge=0, le=10000)
    image: str = Field(..., min_length=1)
    animation_url: Optional[str] = None
    external_url: Optional[str] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    collection: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    creators: Optional[List[Creator]] = None

    model_config = ConfigDict(frozen=True, extra="forbid")

class NFTInfo(BaseModel):
    """NFT information."""
    mint_address: constr(min_length=32, max_length=44)
    metadata_address: constr(min_length=32, max_length=44)
    update_authority: constr(min_length=32, max_length=44)
    metadata: NFTMetadata
    owner: Optional[constr(min_length=32, max_length=44)] = None

    model_config = ConfigDict(frozen=True, extra="forbid")

class CompressedNFTInfo(BaseModel):
    """Compressed NFT information."""
    asset_id: str = Field(..., min_length=32)
    tree_address: constr(min_length=32, max_length=44)
    leaf_index: int = Field(..., ge=0)
    metadata: NFTMetadata
    owner: constr(min_length=32, max_length=44)

    model_config = ConfigDict(frozen=True, extra="forbid")

class MintNFTParams(BaseModel):
    """Parameters for minting an NFT."""
    metadata: NFTMetadata
    is_mutable: bool = True
    max_supply: Optional[int] = Field(default=None, ge=0)
    collection_mint: Optional[str] = None
    verify_creators: bool = False

    model_config = ConfigDict(frozen=True, extra="forbid")

class CompressedNFTParams(BaseModel):
    """Parameters for minting a compressed NFT."""
    metadata: NFTMetadata
    tree_address: Optional[str] = None
    max_depth: int = Field(default=14, ge=3, le=30)
    max_buffer_size: int = Field(default=64, ge=8, le=256)
    is_mutable: bool = True
    collection_mint: Optional[str] = None
    verify_creators: bool = False

    model_config = ConfigDict(frozen=True, extra="forbid")

class TransferNFTParams(BaseModel):
    """Parameters for transferring an NFT."""
    mint_address: constr(min_length=32, max_length=44) = Field(
        ...,
        description="The mint address of the NFT to transfer",
        examples=["BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"]
    )
    to_address: constr(min_length=32, max_length=44) = Field(
        ...,
        description="The recipient's address",
        examples=["GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"]
    )

    model_config = ConfigDict(frozen=True, extra="forbid")

class TransferCompressedNFTParams(BaseModel):
    """Parameters for transferring a compressed NFT."""
    asset_id: str = Field(
        ...,
        description="The asset ID of the compressed NFT to transfer",
        min_length=32
    )
    to_address: constr(min_length=32, max_length=44) = Field(
        ...,
        description="The recipient's address",
        examples=["GkXP89QxPPvQBhvYxKQq1yGgZ3CrBZod1pBAKnKXXGBJ"]
    )

    model_config = ConfigDict(frozen=True, extra="forbid")

class BulkMintNFTParams(BaseModel):
    """Parameters for bulk minting NFTs."""
    metadata_list: List[NFTMetadata]
    is_mutable: bool = True
    collection_mint: Optional[str] = None
    verify_creators: bool = False

    model_config = ConfigDict(frozen=True, extra="forbid")

class BulkTransferNFTParams(BaseModel):
    """Parameters for bulk transferring NFTs."""
    mint_addresses: List[str]
    to_address: constr(min_length=32, max_length=44)

    model_config = ConfigDict(frozen=True, extra="forbid")

class UpdateMetadataParams(BaseModel):
    """Parameters for updating NFT metadata."""
    mint_address: constr(min_length=32, max_length=44)
    metadata: NFTMetadata
    is_mutable: Optional[bool] = None
    update_authority: Optional[str] = None

    model_config = ConfigDict(frozen=True, extra="forbid")

class QueryNFTsParams(BaseModel):
    """Parameters for querying NFTs."""
    owner: Optional[str] = None
    collection: Optional[str] = None
    creator: Optional[str] = None
    update_authority: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=50)

    model_config = ConfigDict(frozen=True, extra="forbid")
