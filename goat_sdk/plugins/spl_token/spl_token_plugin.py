"""SPL Token Plugin implementation."""

import logging
from typing import Dict, List, Optional, Any

from goat_sdk.core.classes.plugin_base import PluginBase
from goat_sdk.plugins.spl_token.models import Token, SolanaNetwork
from goat_sdk.plugins.spl_token.spl_token_service import SplTokenService
from goat_sdk.plugins.spl_token.tokens import SPL_TOKENS

logger = logging.getLogger(__name__)


class SplTokenPlugin(PluginBase):
    """Plugin for interacting with SPL tokens."""

    def __init__(
        self,
        network: SolanaNetwork = SolanaNetwork.MAINNET,
        tokens: Optional[List[Token]] = None,
        mode_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize SPL Token Plugin.

        Args:
            network: Solana network to use
            tokens: Optional list of tokens to use instead of default
            mode_config: Optional Mode-specific configuration
        """
        super().__init__()
        self.network = network
        self.tokens = tokens or SPL_TOKENS
        self.mode_config = mode_config or {}
        self.service = SplTokenService(network=network, tokens=self.tokens)
        logger.info(f"Initialized SPL Token Plugin on network: {network}")

    def get_tools(self) -> List[Any]:
        """Get the tools provided by this plugin.

        Returns:
            List of tool functions
        """
        return [
            self.service.get_token_info_by_symbol,
            self.service.get_token_balance_by_mint_address,
            self.service.transfer_token_by_mint_address,
            self.service.convert_to_base_unit,
        ]

    def get_tokens_for_network(self) -> List[Token]:
        """Get tokens available for the current network.

        Returns:
            List of tokens with mint addresses for the current network
        """
        return [
            token for token in self.tokens
            if self.network in token.mint_addresses
        ]

    def get_mode_config(self) -> Dict[str, Any]:
        """Get Mode-specific configuration.

        Returns:
            Mode configuration dictionary
        """
        return self.mode_config
