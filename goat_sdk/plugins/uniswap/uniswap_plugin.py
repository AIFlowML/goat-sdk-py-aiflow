"""
Uniswap Plugin implementation with enhanced features.
"""

from typing import Dict, List, Optional, Union
from decimal import Decimal
from web3 import Web3

from ...core.classes.plugin_base import PluginBase
from ...core.decorators.tool import tool
from .uniswap_service import UniswapService
from .parameters import (
    SwapParameters,
    AddLiquidityParameters,
    RemoveLiquidityParameters,
    CollectFeesParameters,
    PositionParameters,
    QuoteParameters,
)
from .types import (
    UniswapVersion,
    PoolFee,
    TokenInfo,
    PoolInfo,
    SwapRoute,
    Position,
    UniswapPluginConfig,
)

class UniswapPlugin(PluginBase):
    """
    Enhanced Uniswap plugin with support for both V2 and V3 protocols.
    Features:
    - Advanced routing and price optimization
    - MEV protection
    - Gas optimization
    - Position management
    - Analytics and monitoring
    """

    def __init__(
        self,
        version: UniswapVersion,
        router_address: str,
        factory_address: str,
        quoter_address: Optional[str] = None,
        position_manager_address: Optional[str] = None,
        web3: Optional[Web3] = None,
    ):
        super().__init__()
        
        if version == UniswapVersion.V3 and (not quoter_address or not position_manager_address):
            raise ValueError("V3 requires quoter and position manager addresses")

        config = UniswapPluginConfig(
            version=version,
            router_address=router_address,
            factory_address=factory_address,
            quoter_address=quoter_address,
            position_manager_address=position_manager_address,
        )

        self.web3 = web3 or Web3()
        self.service = UniswapService(config, self.web3)

    @tool
    async def swap_tokens(self, params: SwapParameters) -> str:
        """
        Execute a token swap with advanced features.

        Features:
        - Multi-path routing optimization
        - MEV protection
        - Gas optimization
        - Slippage protection
        """
        return await self.service.swap_exact_tokens(params)

    @tool
    async def add_liquidity(self, params: AddLiquidityParameters) -> str:
        """
        Add liquidity to a pool with position optimization.

        Features:
        - Automatic price range selection (V3)
        - Gas-efficient deposit
        - Position analysis
        """
        return await self.service.add_liquidity(params)

    @tool
    async def remove_liquidity(self, params: RemoveLiquidityParameters) -> str:
        """
        Remove liquidity from a pool safely.

        Features:
        - Slippage protection
        - Gas optimization
        - Position unwinding strategy
        """
        return await self.service.remove_liquidity(params)

    @tool
    async def collect_fees(self, params: CollectFeesParameters) -> Dict[str, Decimal]:
        """
        Collect accumulated fees from a V3 position.

        Features:
        - Auto-compound option
        - Gas optimization
        - Fee analysis
        """
        return await self.service.collect_fees(params)

    @tool
    async def get_positions(self, params: PositionParameters) -> List[Position]:
        """
        Get detailed position information.

        Features:
        - Historical performance
        - Impermanent loss calculation
        - Fee earnings analysis
        """
        return await self.service.get_positions(params)

    @tool
    async def get_pool_info(self, token0: str, token1: str, fee: PoolFee) -> PoolInfo:
        """
        Get detailed pool information with analytics.

        Features:
        - Liquidity depth analysis
        - Volume analytics
        - Price impact estimation
        """
        return await self.service.get_pool_info(token0, token1, fee)

    @tool
    async def get_token_info(self, token_address: str) -> TokenInfo:
        """
        Get detailed token information.

        Features:
        - Price feeds
        - Volume analytics
        - Security checks
        """
        return await self.service.get_token_info(token_address)

    @tool
    async def quote_swap(self, params: QuoteParameters) -> List[SwapRoute]:
        """
        Get detailed swap quotes with multiple route options.

        Features:
        - Multi-path routing
        - Gas cost estimation
        - Price impact analysis
        - MEV risk assessment
        """
        return await self.service.quote_exact_input(params)
