"""Client for interacting with Tensor API."""

from typing import Any, Dict, List, Optional
import aiohttp
from solana.rpc.async_api import AsyncClient

from goat_sdk.core import ModeClientBase
from goat_sdk.core.decorators.tool import tool
from goat_sdk.plugins.tensor.config import TensorConfig
from goat_sdk.plugins.tensor.types import (
    NFTInfo,
    BuyListingTransactionResponse,
)
from goat_sdk.plugins.tensor.utils.transaction import deserialize_tx_response_to_instructions


class TensorClient(ModeClientBase):
    """Client for interacting with Tensor API."""

    def __init__(
        self,
        config: Optional[TensorConfig] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """Initialize Tensor client.

        Args:
            config: Tensor configuration
            session: Optional aiohttp session
        """
        self.config = config or TensorConfig(api_key="")
        self._session = session
        self._headers = {
            "Content-Type": "application/json",
            "x-tensor-api-key": self.config.api_key,
        }

    async def __aenter__(self) -> "TensorClient":
        """Enter async context."""
        if not self._session:
            self._session = aiohttp.ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context."""
        if self._session:
            try:
                await self._session.close()
            except Exception:
                pass
        self._session = None

    @tool(description="Get information about an NFT from the Tensor API")
    async def get_nft_info(self, mint_hash: str) -> NFTInfo:
        """Get information about an NFT.

        Args:
            mint_hash: The mint hash of the NFT

        Returns:
            NFT information

        Raises:
            RuntimeError: If client is not initialized
            Exception: If API request fails
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            response = await self._session.get(
                f"{self.config.api_url}/mint",
                params={"mints": mint_hash},
            )
            data = await response.json()

            if response.status != 200:
                error_message = data.get("error", "Unknown error")
                raise Exception(f"Failed to get NFT info: {error_message}")

            return NFTInfo(**(data[0]))
        except Exception as e:
            raise Exception(f"Failed to get NFT info: {str(e)}")

    @tool(description="Get a transaction to buy an NFT from a listing from the Tensor API")
    async def get_buy_listing_transaction(
        self,
        wallet_client: Any,
        mint_hash: str,
    ) -> Dict[str, Any]:
        """Get a transaction to buy an NFT from a listing.

        Args:
            wallet_client: The wallet client
            mint_hash: The mint hash of the NFT

        Returns:
            Transaction information

        Raises:
            RuntimeError: If client is not initialized
            Exception: If API request fails or no listing found
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        nft_info = await self.get_nft_info(mint_hash)

        price = nft_info.listing.price if nft_info.listing else None
        owner = nft_info.owner

        if not price or not owner:
            raise Exception(f"No listing found for {mint_hash}")

        params = {
            "buyer": wallet_client.get_address(),
            "mint": mint_hash,
            "owner": owner,
            "maxPrice": price,
            "blockhash": "11111111111111111111111111111111",
        }

        try:
            response = await self._session.get(
                f"{self.config.api_url}/tx/buy",
                params=params,
            )
            data = await response.json()

            if response.status != 200:
                error_message = data.get("error", "Unknown error")
                raise Exception(f"Failed to get buy listing transaction: {error_message}")

            tx_response = BuyListingTransactionResponse(**data)
            connection = AsyncClient(wallet_client.get_connection().endpoint_url)

            transaction, instructions = await deserialize_tx_response_to_instructions(
                connection,
                tx_response,
            )

            return {
                "transaction": transaction,
                "instructions": instructions,
            }
        except Exception as e:
            raise Exception(f"Failed to get buy listing transaction: {str(e)}") 