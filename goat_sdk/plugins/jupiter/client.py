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
        self._headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            self._headers["Authorization"] = f"Bearer {self.config.api_key}"

    async def __aenter__(self) -> "JupiterClient":
        """Enter async context."""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
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
        retry=retry_if_exception_type((aiohttp.ClientError, QuoteError)),
        reraise=True,
    )
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = None,
        mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Get quote for token swap.

        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount of input tokens
            slippage_bps: Slippage tolerance in basis points (optional)
            mode: Swap mode (ExactIn or ExactOut)
            **kwargs: Additional parameters for quote request

        Returns:
            Quote response with route information

        Raises:
            QuoteError: If quote request fails
        """
        if slippage_bps is None:
            slippage_bps = self.config.default_slippage_bps

        try:
            return await self._get_quote_internal(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                slippage_bps=slippage_bps,
                mode=mode,
                **kwargs,
            )
        except Exception as e:
            raise QuoteError(f"Failed to get quote: {str(e)}")

    def _get_retry_decorator(self):
        """Get retry decorator based on config."""
        return retry(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(multiplier=self.config.retry_delay),
            retry=retry_if_exception_type((aiohttp.ClientError, QuoteError)),
            reraise=True,
        )

    async def get_swap_transaction(
        self,
        wallet_client: Any,
        quote: QuoteResponse,
        **kwargs: Any,
    ) -> SwapResponse:
        """Get swap transaction for executing token swap.

        Args:
            wallet_client: Wallet client for signing transaction
            quote: Quote response from get_quote
            **kwargs: Additional parameters for swap request

        Returns:
            Swap response with transaction data

        Raises:
            SwapError: If swap request fails
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use async context manager.")

        request = SwapRequest(
            userPublicKey=wallet_client.public_key,
            quoteResponse=quote,
            computeUnitPriceMicroLamports=self.config.compute_unit_price_micro_lamports,
            preferPostMint=self.config.prefer_post_mint_version,
            maxAccounts=self.config.max_accounts_per_transaction,
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

    async def execute_swap(
        self,
        wallet_client: Any,
        quote: QuoteResponse,
        **kwargs: Any,
    ) -> SwapResult:
        """Execute token swap.

        Args:
            wallet_client: Wallet client for signing transaction
            quote: Quote response from get_quote
            **kwargs: Additional parameters for swap request

        Returns:
            Swap result with transaction details

        Raises:
            SwapError: If swap execution fails
        """
        try:
            # Get swap transaction
            swap_response = await self.get_swap_transaction(
                wallet_client=wallet_client,
                quote=quote,
                **kwargs,
            )

            # Sign and send transaction
            transaction_hash = await wallet_client.sign_and_send_transaction(
                swap_response.swap_transaction
            )

            # Return swap result
            return SwapResult(
                transaction_hash=transaction_hash,
                input_amount=quote.in_amount,
                output_amount=quote.out_amount,
                price_impact=quote.price_impact_pct,
                fee_amount=quote.route_plan[0].swap_info.fee_amount,
                route_plan=[step.model_dump(by_alias=True) for step in quote.route_plan],
            )
        except Exception as e:
            raise SwapError(f"Failed to execute swap: {str(e)}") 