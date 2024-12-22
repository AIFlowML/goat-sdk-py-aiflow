"""Type definitions for Tensor plugin."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class GetNFTInfoRequest(BaseModel):
    """Request parameters for get_nft_info."""
    mint_hash: str = Field(description="The mint hash of the NFT")


class GetBuyListingTransactionRequest(BaseModel):
    """Request parameters for get_buy_listing_transaction."""
    mint_hash: str = Field(description="The mint hash of the NFT")


class LastSale(BaseModel):
    """Last sale information."""
    model_config = ConfigDict(populate_by_name=True)

    price: str
    price_unit: str = Field(alias="priceUnit")


class Listing(BaseModel):
    """NFT listing information."""
    model_config = ConfigDict(populate_by_name=True)

    price: str
    tx_id: str = Field(alias="txId")
    seller: str
    source: str


class NFTInfo(BaseModel):
    """NFT information from Tensor API."""
    model_config = ConfigDict(populate_by_name=True)

    onchain_id: str = Field(alias="onchainId")
    attributes: List[dict]
    image_uri: Optional[str] = Field(None, alias="imageUri")
    last_sale: Optional[LastSale] = Field(None, alias="lastSale")
    metadata_uri: Optional[str] = Field(None, alias="metadataUri")
    name: Optional[str] = None
    rarity_rank_tt: Optional[int] = Field(None, alias="rarityRankTT")
    rarity_rank_tt_stat: Optional[int] = Field(None, alias="rarityRankTTStat")
    rarity_rank_hrtt: Optional[int] = Field(None, alias="rarityRankHrtt")
    rarity_rank_stat: Optional[int] = Field(None, alias="rarityRankStat")
    sell_royalty_fee_bps: Optional[int] = Field(None, alias="sellRoyaltyFeeBPS")
    token_edition: Optional[str] = Field(None, alias="tokenEdition")
    token_standard: Optional[str] = Field(None, alias="tokenStandard")
    hidden: Optional[bool] = None
    compressed: Optional[bool] = None
    verified_collection: Optional[str] = Field(None, alias="verifiedCollection")
    owner: Optional[str] = None
    inscription: Optional[str] = None
    token_program: Optional[str] = Field(None, alias="tokenProgram")
    metadata_program: Optional[str] = Field(None, alias="metadataProgram")
    transfer_hook_program: Optional[str] = Field(None, alias="transferHookProgram")
    listing_normalized_price: Optional[str] = Field(None, alias="listingNormalizedPrice")
    hybrid_amount: Optional[str] = Field(None, alias="hybridAmount")
    listing: Optional[Listing] = None
    slug_display: Optional[str] = Field(None, alias="slugDisplay")
    coll_id: Optional[str] = Field(None, alias="collId")
    coll_name: Optional[str] = Field(None, alias="collName")
    num_mints: Optional[int] = Field(None, alias="numMints")


class TransactionData(BaseModel):
    """Transaction data."""
    model_config = ConfigDict(populate_by_name=True)

    type: str
    data: List[int]


class TransactionResponse(BaseModel):
    """Transaction response from Tensor API."""
    model_config = ConfigDict(populate_by_name=True)

    tx: TransactionData
    tx_v0: TransactionData = Field(alias="txV0")


class BuyListingTransactionResponse(BaseModel):
    """Buy listing transaction response."""
    model_config = ConfigDict(populate_by_name=True)

    txs: List[TransactionResponse] 