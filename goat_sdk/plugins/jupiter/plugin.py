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
"""Jupiter plugin implementation."""

from typing import Any

from goat_sdk.core.plugin_base import PluginBase
from goat_sdk.core.chain import Chain
from .service import JupiterService
from .types import QuoteRequest, QuoteResponse, SwapRequest, SwapResult, SwapMode


class JupiterPlugin(PluginBase):
    """Plugin for Jupiter DEX integration."""

    def __init__(self):
        """Initialize Jupiter plugin."""
        self.service = JupiterService()
        super().__init__(name="jupiter", tools=[self.service])

    def supports_chain(self, chain: Chain) -> bool:
        """Check if chain is supported.
        
        Args:
            chain: Chain to check
        
        Returns:
            True if chain is supported
        """
        return chain.type == "solana"

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: str,
        slippage_bps: int = 50,
        swap_mode: SwapMode = SwapMode.EXACT_IN,
        **kwargs: Any,
    ) -> QuoteResponse:
        """Get quote for token swap.

        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount of input tokens
            slippage_bps: Slippage tolerance in basis points
            swap_mode: Swap mode (ExactIn or ExactOut)
            **kwargs: Additional parameters for quote request

        Returns:
            Quote response with route information
        """
        request = QuoteRequest(
            inputMint=input_mint,
            outputMint=output_mint,
            amount=amount,
            slippageBps=slippage_bps,
            swapMode=swap_mode.value,
            **kwargs
        )
        return await self.service.get_quote(request)

    async def execute_swap(self, wallet_client: Any, quote: QuoteResponse, **kwargs: Any) -> SwapResult:
        """Execute token swap.

        Args:
            wallet_client: Wallet client for signing transaction
            quote: Quote response from get_quote
            **kwargs: Additional parameters for swap request

        Returns:
            Swap result with transaction details
        """
        request = SwapRequest(
            wallet_client=wallet_client,
            quote_request=quote,
            **kwargs
        )
        return await self.service.swap_tokens(request)


def jupiter() -> JupiterPlugin:
    """Create Jupiter plugin instance.
    
    Returns:
        Jupiter plugin instance
    """
    return JupiterPlugin() 