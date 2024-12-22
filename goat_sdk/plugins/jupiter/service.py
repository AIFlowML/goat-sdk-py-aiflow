"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /:::\____\        
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

"""Jupiter service for token swaps."""

from typing import Any, Dict, List, Optional

from goat_sdk.core.wallet_client import ModeWalletClient
from goat_sdk.core.decorators.tool import tool as tool_decorator

from .client import JupiterClient
from .config import JupiterConfig
from .errors import QuoteError, SwapError
from .types import QuoteRequest, QuoteResponse, SwapMode, SwapRequest, SwapResult


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
        request: QuoteRequest,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Get quote for token swap.

        Args:
            request: Quote request parameters
            **kwargs: Additional parameters for quote request

        Returns:
            Quote response with route information

        Raises:
            QuoteError: If quote request fails
        """
        async with self.client as client:
            # Convert string swap_mode to SwapMode enum
            if isinstance(request.swapMode, str):
                request.swapMode = SwapMode.EXACT_IN if request.swapMode == "ExactIn" else SwapMode.EXACT_OUT
            return await client.get_quote(
                input_mint=request.inputMint,
                output_mint=request.outputMint,
                amount=int(request.amount),
                slippage_bps=request.slippageBps,
                mode=request.swapMode,
                **kwargs,
            )

    @tool_decorator(description="Swap an SPL token for another token on the Jupiter DEX")
    async def swap_tokens(
        self,
        request: SwapRequest,
        **kwargs: Any,
    ) -> SwapResult:
        """Swap tokens using Jupiter.

        Args:
            request: Swap request parameters
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
                input_mint=request.quote_request.input_mint,
                output_mint=request.quote_request.output_mint,
                amount=request.quote_request.amount,
                slippage_bps=request.quote_request.slippage_bps,
                mode=request.quote_request.swap_mode,
                **kwargs,
            )

            # Execute swap
            return await client.execute_swap(
                wallet_client=request.wallet_client,
                quote=quote,
                **kwargs,
            ) 