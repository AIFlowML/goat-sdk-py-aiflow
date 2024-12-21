"""Jupiter client for interacting with Jupiter API."""

from typing import Any, Optional

import aiohttp
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from goat_sdk.core.classes import ModeClientBase
from goat_sdk.plugins.jupiter.config import JupiterConfig
from goat_sdk.plugins.jupiter.errors import QuoteError, SwapError
from goat_sdk.plugins.jupiter.types import (
    QuoteRequest,
    QuoteResponse,
    SwapMode,
    SwapRequest,
    SwapResponse,
    SwapResult,
)


class JupiterClient(ModeClientBase):
    """Client for interacting with Jupiter API."""

    def __init__(
        self,
        config: Optional[JupiterConfig] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """Initialize Jupiter client.

        Args:
            config: Jupiter configuration
            session: Optional aiohttp session
        """
        self.config = config or JupiterConfig()
        self._session = session
        self._headers = {"Content-Type": "application/json"}

    async def __aenter__(self) -> "JupiterClient":
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

    async def _get_quote_internal(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
        mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Internal method to get quote for token swap."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        request = QuoteRequest(
            inputMint=input_mint,
            outputMint=output_mint,
            amount=str(amount),
            slippageBps=slippage_bps,
            swapMode=mode.value,
            **kwargs,
        )

        response = await self._session.post(
            f"{self.config.api_url}/quote",
            json=request.model_dump(by_alias=True),
        )
        data = await response.json()

        if response.status != 200:
            error_message = data.get("error", "Unknown error")
            raise QuoteError(f"Failed to get quote: {error_message}")

        return QuoteResponse(**data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True,
    )
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
        mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Get quote for token swap."""
        try:
            return await self._get_quote_internal(
                input_mint,
                output_mint,
                amount,
                slippage_bps,
                mode,
                **kwargs,
            )
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Network error while getting quote: {str(e)}")
        except Exception as e:
            raise QuoteError(f"Failed to get quote: {str(e)}")

    async def _get_swap_transaction_internal(
        self,
        wallet_client: "WalletClient",  # type: ignore
        quote: QuoteResponse,
        **kwargs: Any,
    ) -> SwapResponse:
        """Internal method to get swap transaction."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        request = SwapRequest(
            userPublicKey=wallet_client.public_key,
            quoteResponse=quote.model_dump(by_alias=True),
            **kwargs,
        )

        response = await self._session.post(
            f"{self.config.api_url}/swap",
            json=request.model_dump(by_alias=True),
        )
        data = await response.json()

        if response.status != 200:
            error_message = data.get("error", "Unknown error")
            raise SwapError(f"Failed to get swap transaction: {error_message}")

        return SwapResponse(**data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True,
    )
    async def get_swap_transaction(
        self,
        wallet_client: "WalletClient",  # type: ignore
        quote: QuoteResponse,
        **kwargs: Any,
    ) -> SwapResponse:
        """Get swap transaction."""
        try:
            return await self._get_swap_transaction_internal(
                wallet_client,
                quote,
                **kwargs,
            )
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Network error while getting swap transaction: {str(e)}")
        except Exception as e:
            raise SwapError(f"Failed to get swap transaction: {str(e)}")

    async def execute_swap(
        self,
        wallet_client: "WalletClient",  # type: ignore
        quote: QuoteResponse,
        **kwargs: Any,
    ) -> SwapResult:
        """Execute swap transaction."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        swap_tx = await self.get_swap_transaction(wallet_client, quote, **kwargs)
        tx = await wallet_client.deserialize_transaction(swap_tx.swap_transaction)

        try:
            signature = await wallet_client.send_transaction(tx)
            return SwapResult(
                transaction_hash=signature,
                input_amount=quote.in_amount,
                output_amount=quote.out_amount,
                price_impact=quote.price_impact_pct,
                fee_amount=quote.route_plan[0].swap_info.fee_amount,
                route_plan=[step.model_dump(by_alias=True) for step in quote.route_plan],
            )
        except Exception as e:
            raise SwapError(f"Failed to send transaction: {str(e)}") 