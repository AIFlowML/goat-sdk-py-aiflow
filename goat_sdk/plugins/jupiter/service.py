"""Jupiter service for token swaps."""

from typing import Any, Dict, List, Optional

from goat_sdk.core.wallet_client import ModeWalletClient
from goat_sdk.core.decorators.tool import tool as tool_decorator

from .client import JupiterClient
from .config import JupiterConfig
from .errors import QuoteError, SwapError
from .types import QuoteResponse, SwapMode, SwapResult


class JupiterService:
    """Service for interacting with Jupiter."""

    def __init__(self, config: Optional[JupiterConfig] = None) -> None:
        """Initialize Jupiter service.

        Args:
            config: Optional Jupiter configuration
        """
        self.config = config or JupiterConfig()
        self.client = JupiterClient(config=self.config)

    @tool_decorator(description="Get a quote for a swap on the Jupiter DEX")
    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: Optional[int] = None,
        mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Get quote for token swap.

        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to swap in base units
            slippage_bps: Slippage tolerance in basis points
            mode: Swap mode (ExactIn or ExactOut)
            **kwargs: Additional parameters for quote request

        Returns:
            Quote response with route information

        Raises:
            QuoteError: If quote request fails
        """
        async with self.client as client:
            return await client.get_quote(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                slippage_bps=slippage_bps,
                mode=mode,
                **kwargs,
            )

    @tool_decorator(description="Swap an SPL token for another token on the Jupiter DEX")
    async def swap_tokens(
        self,
        wallet_client: ModeWalletClient,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: Optional[int] = None,
        mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> SwapResult:
        """Swap tokens using Jupiter.

        Args:
            wallet_client: Mode wallet client
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to swap in base units
            slippage_bps: Slippage tolerance in basis points
            mode: Swap mode (ExactIn or ExactOut)
            **kwargs: Additional parameters for swap request

        Returns:
            Swap result with transaction details

        Raises:
            QuoteError: If quote request fails
            SwapError: If swap execution fails
        """
        async with self.client as client:
            # Get quote
            quote = await client.get_quote(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount,
                slippage_bps=slippage_bps,
                mode=mode,
                **kwargs,
            )

            # Execute swap
            return await client.execute_swap(
                wallet_client=wallet_client,
                quote=quote,
                **kwargs,
            ) 