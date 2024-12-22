"""
Uniswap Plugin implementation with enhanced features.
"""

import logging
import time
from typing import Dict, List, Optional, Union, ClassVar
from decimal import Decimal
from web3 import Web3

from ...core.classes.plugin_base import PluginBase
from ...core.decorators.tool import tool, Tool
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

# Set up logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
    handlers=[
        logging.FileHandler('logs/uniswap_plugin_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Performance metrics
OPERATION_TIMES = {}
ERROR_COUNTS = {}

def log_operation_time(operation: str, duration: float) -> None:
    """Log operation time for performance tracking."""
    if operation not in OPERATION_TIMES:
        OPERATION_TIMES[operation] = []
    OPERATION_TIMES[operation].append(duration)
    logger.debug(f"Operation timing - {operation}: {duration:.3f}s")

def log_error(operation: str, error: Exception) -> None:
    """Log error for tracking."""
    if operation not in ERROR_COUNTS:
        ERROR_COUNTS[operation] = {}
    error_type = type(error).__name__
    ERROR_COUNTS[operation][error_type] = ERROR_COUNTS[operation].get(error_type, 0) + 1
    logger.error(f"Error in {operation}: {error_type} - {str(error)}")

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

    # Tool method annotations
    swap_tokens: ClassVar[Tool]
    add_liquidity: ClassVar[Tool]
    remove_liquidity: ClassVar[Tool]
    collect_fees: ClassVar[Tool]
    get_position: ClassVar[Tool]
    get_positions: ClassVar[Tool]
    get_pool_info: ClassVar[Tool]
    get_token_info: ClassVar[Tool]
    get_quote: ClassVar[Tool]
    get_swap_route: ClassVar[Tool]
    quote_swap: ClassVar[Tool]

    def __init__(
        self,
        version: UniswapVersion,
        router_address: str,
        factory_address: str,
        quoter_address: Optional[str] = None,
        position_manager_address: Optional[str] = None,
        web3: Optional[Web3] = None,
    ):
        """Initialize UniswapPlugin with extensive logging."""
        operation = "initialization"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting UniswapPlugin initialization")
            logger.debug(f"[{operation}] Version: {version}")
            logger.debug(f"[{operation}] Router address: {router_address}")
            logger.debug(f"[{operation}] Factory address: {factory_address}")
            logger.debug(f"[{operation}] Quoter address: {quoter_address}")
            logger.debug(f"[{operation}] Position manager address: {position_manager_address}")
            
            super().__init__()
            
            if version == UniswapVersion.V3 and (not quoter_address or not position_manager_address):
                logger.error(f"[{operation}] Missing required V3 addresses")
                raise ValueError("V3 requires quoter and position manager addresses")

            config = UniswapPluginConfig(
                version=version,
                router_address=router_address,
                factory_address=factory_address,
                quoter_address=quoter_address,
                position_manager_address=position_manager_address,
            )
            logger.debug(f"[{operation}] Created config: {config}")

            self.web3 = web3 or Web3()
            logger.debug(f"[{operation}] Web3 instance: {self.web3}")
            
            self.service = UniswapService(config, self.web3)
            logger.debug(f"[{operation}] Created UniswapService instance")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] UniswapPlugin initialized successfully")
            
        except Exception as e:
            logger.error(f"[{operation}] Failed to initialize UniswapPlugin")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def swap_tokens(self, params: SwapParameters) -> str:
        """Execute a token swap with advanced features."""
        operation = "swap_tokens"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting token swap")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.swap_exact_tokens(params)
            logger.debug(f"[{operation}] Swap result: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Token swap completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Token swap failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def add_liquidity(self, params: AddLiquidityParameters) -> str:
        """Add liquidity to a pool with position optimization."""
        operation = "add_liquidity"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting liquidity addition")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.add_liquidity(params)
            logger.debug(f"[{operation}] Add liquidity result: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Liquidity addition completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Liquidity addition failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def remove_liquidity(self, params: RemoveLiquidityParameters) -> str:
        """Remove liquidity from a pool safely."""
        operation = "remove_liquidity"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting liquidity removal")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.remove_liquidity(params)
            logger.debug(f"[{operation}] Remove liquidity result: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Liquidity removal completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Liquidity removal failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def collect_fees(self, params: CollectFeesParameters) -> Dict[str, Decimal]:
        """Collect accumulated fees from a V3 position."""
        operation = "collect_fees"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting fee collection")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.collect_fees(params)
            logger.debug(f"[{operation}] Collected fees: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Fee collection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Fee collection failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def get_positions(self, params: PositionParameters) -> List[Position]:
        """Get detailed position information."""
        operation = "get_positions"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting position retrieval")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.get_positions(params)
            logger.debug(f"[{operation}] Retrieved positions: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Position retrieval completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Position retrieval failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def get_pool_info(self, token0: str, token1: str, fee: PoolFee) -> PoolInfo:
        """Get detailed pool information with analytics."""
        operation = "get_pool_info"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting pool info retrieval")
            logger.debug(f"[{operation}] Parameters: token0={token0}, token1={token1}, fee={fee}")
            
            result = await self.service.get_pool_info(token0, token1, fee)
            logger.debug(f"[{operation}] Pool info: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Pool info retrieval completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Pool info retrieval failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def get_token_info(self, token_address: str) -> TokenInfo:
        """Get detailed token information."""
        operation = "get_token_info"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting token info retrieval")
            logger.debug(f"[{operation}] Token address: {token_address}")
            
            result = await self.service.get_token_info(token_address)
            logger.debug(f"[{operation}] Token info: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Token info retrieval completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Token info retrieval failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise

    @tool
    async def quote_swap(self, params: QuoteParameters) -> List[SwapRoute]:
        """Get detailed swap quotes with multiple route options."""
        operation = "quote_swap"
        start_time = time.time()
        
        try:
            logger.info(f"[{operation}] Starting swap quote retrieval")
            logger.debug(f"[{operation}] Parameters: {params}")
            
            result = await self.service.quote_exact_input(params)
            logger.debug(f"[{operation}] Swap routes: {result}")
            
            duration = time.time() - start_time
            log_operation_time(operation, duration)
            
            logger.info(f"[{operation}] Swap quote retrieval completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[{operation}] Swap quote retrieval failed")
            logger.error(f"[{operation}] Error: {str(e)}")
            logger.error(f"[{operation}] Stack trace:", exc_info=True)
            log_error(operation, e)
            raise
