"""SPL Token Plugin implementation."""

import logging
from typing import Dict, List, Optional, Type, Set
from dataclasses import dataclass

from goat_sdk.core.classes.plugin_base import PluginBase
from goat_sdk.core.classes.tool_base import ToolBase
from goat_sdk.plugins.spl_token.models import (
    Token,
    SolanaNetwork,
    TransferParams,
    TokenBalance
)
from goat_sdk.plugins.spl_token.utils import (
    get_token_info_by_symbol,
    get_tokens_for_network,
    get_token_by_mint_address,
    does_account_exist,
    get_associated_token_address,
    create_associated_token_account
)
from goat_sdk.plugins.spl_token.exceptions import (
    TokenNotFoundError,
    TokenAccountNotFoundError,
    InvalidTokenAddressError,
    InsufficientBalanceError,
    TransferError
)

logger = logging.getLogger(__name__)


@dataclass
class SplTokenPluginConfig:
    """Configuration for SPL Token Plugin."""
    network: SolanaNetwork = SolanaNetwork.MAINNET
    tokens: Optional[List[Token]] = None
    wallet_client: Optional[object] = None


class SplTokenPlugin(PluginBase):
    """Plugin for interacting with SPL tokens."""
    
    def __init__(
        self,
        network: SolanaNetwork = SolanaNetwork.MAINNET,
        tokens: Optional[List[Token]] = None,
        wallet_client: Optional[object] = None,
        **kwargs
    ):
        """Initialize SPL Token Plugin.

        Args:
            network: Solana network to use
            tokens: Optional list of tokens to use instead of default
            wallet_client: Wallet client for sending transactions
        """
        super().__init__(**kwargs)
        self._config = SplTokenPluginConfig(
            network=network,
            tokens=tokens,
            wallet_client=wallet_client
        )
        logger.info(f"Initialized SPL Token Plugin on network: {self.network}")
    
    @property
    def network(self) -> SolanaNetwork:
        """Get the current network."""
        return self._config.network
    
    @network.setter
    def network(self, value: SolanaNetwork) -> None:
        """Set the current network."""
        logger.debug(f"Setting network to: {value}")
        self._config.network = value
        logger.debug("Network updated")
    
    @property
    def tokens(self) -> List[Token]:
        """Get the current tokens."""
        return self._config.tokens or []
    
    @property
    def wallet_client(self) -> object:
        """Get the wallet client."""
        if not self._config.wallet_client:
            raise ValueError("No wallet client configured")
        return self._config.wallet_client
    
    def get_tools(self) -> Set[Type[ToolBase]]:
        """Get the tools provided by this plugin.

        Returns:
            Set of tool classes
        """
        logger.debug("Getting plugin tools")
        tools = {
            self.get_token_info_by_symbol,
            self.get_token_balance,
            self.transfer_token,
            self.convert_to_base_unit,
        }
        logger.debug(f"Retrieved {len(tools)} tools")
        return tools
    
    def get_tokens_for_network(self) -> List[Token]:
        """Get tokens available for the current network.

        Returns:
            List of tokens with mint addresses for the current network
        """
        return get_tokens_for_network(self.tokens, self.network)
    
    async def get_token_info_by_symbol(self, symbol: str) -> Token:
        """Get token information by symbol.

        Args:
            symbol: Token symbol to look up

        Returns:
            Token information

        Raises:
            TokenNotFoundError: If token is not found or not supported
        """
        return await get_token_info_by_symbol(self.tokens, symbol, self.network)
    
    async def get_token_balance(self, token_symbol: str) -> TokenBalance:
        """Get token balance for the current wallet.

        Args:
            token_symbol: Symbol of token to check balance for

        Returns:
            Token balance information

        Raises:
            TokenNotFoundError: If token is not found
            TokenAccountNotFoundError: If token account is not found
        """
        logger.debug(f"Getting balance for token: {token_symbol}")
        
        # Get token info
        token = await self.get_token_info_by_symbol(token_symbol)
        mint_address = token.mint_addresses[self.network]
        
        # Get wallet address
        wallet_address = await self.wallet_client.get_address()
        
        # Check if token account exists
        token_account = await does_account_exist(
            self.wallet_client,
            wallet_address,
            mint_address
        )
        
        if not token_account:
            logger.error(f"Token account not found for {token_symbol}")
            raise TokenAccountNotFoundError(
                account_type="Associated Token",
                address=f"{wallet_address}:{mint_address}"
            )
        
        # Get account info
        account_info = await self.wallet_client.get_token_accounts_by_owner(
            wallet_address,
            mint_address
        )
        
        if not account_info or not account_info["value"]:
            logger.error(f"No token account info found for {token_symbol}")
            raise TokenAccountNotFoundError(
                account_type="Associated Token",
                address=token_account
            )
        
        # Parse balance
        token_amount = account_info["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]
        amount = float(token_amount["uiAmount"])
        
        logger.debug(f"Retrieved balance: {amount} {token_symbol}")
        return TokenBalance(
            token_symbol=token_symbol,
            amount=amount,
            mint_address=mint_address,
            token_account=token_account
        )
    
    async def transfer_token(
        self,
        token_symbol: str,
        amount: float,
        recipient_address: str
    ) -> str:
        """Transfer tokens to a recipient.

        Args:
            token_symbol: Symbol of token to transfer
            amount: Amount of tokens to transfer
            recipient_address: Recipient's wallet address

        Returns:
            Transaction signature

        Raises:
            TokenNotFoundError: If token is not found
            TokenAccountNotFoundError: If token account is not found
            InsufficientBalanceError: If insufficient balance
            TransferError: If transfer fails
        """
        logger.debug(f"Transferring {amount} {token_symbol} to {recipient_address}")
        
        # Get token info
        token = await self.get_token_info_by_symbol(token_symbol)
        mint_address = token.mint_addresses[self.network]
        
        # Get wallet address
        wallet_address = await self.wallet_client.get_address()
        
        # Check sender's token account
        sender_token_account = await does_account_exist(
            self.wallet_client,
            wallet_address,
            mint_address
        )
        
        if not sender_token_account:
            logger.error(f"Sender's token account not found for {token_symbol}")
            raise TokenAccountNotFoundError(
                account_type="Associated Token",
                address=f"{wallet_address}:{mint_address}"
            )
        
        # Check recipient's token account
        recipient_token_account = await does_account_exist(
            self.wallet_client,
            recipient_address,
            mint_address
        )
        
        if not recipient_token_account:
            logger.debug(f"Creating token account for recipient: {recipient_address}")
            recipient_token_account = await create_associated_token_account(
                self.wallet_client,
                recipient_address,
                mint_address
            )
        
        # Check balance
        balance = await self.get_token_balance(token_symbol)
        if balance.amount < amount:
            logger.error(f"Insufficient balance. Required: {amount}, Available: {balance.amount}")
            raise InsufficientBalanceError(token_symbol, amount, balance.amount)
        
        # Convert amount to base units
        amount_base = self.convert_to_base_unit(amount, token.decimals)
        
        try:
            # Send transfer transaction
            signature = await self.wallet_client.send_transaction(
                self.wallet_client.create_transfer_instruction(
                    sender_token_account,
                    recipient_token_account,
                    amount_base
                )
            )
            logger.debug(f"Transfer successful. Signature: {signature}")
            return signature
            
        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}", exc_info=True)
            raise TransferError(token_symbol, amount, recipient_address, str(e)) from e
    
    def convert_to_base_unit(self, amount: float, decimals: int) -> int:
        """Convert token amount to base units.

        Args:
            amount: Token amount in decimal form
            decimals: Number of decimal places

        Returns:
            Amount in base units
        """
        return int(amount * (10 ** decimals))
